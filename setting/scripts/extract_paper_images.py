#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract paper figures for this Obsidian vault.

Low-cost default:
1. Try arXiv source package first.
2. Convert source PDF figures to PNG.
3. Fall back to embedded PDF images when source figures are scarce or the paper is not arXiv.
4. Generate an Obsidian-ready image index with embeds.
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover - Poppler fallback handles local installs without PyMuPDF.
    fitz = None

try:
    import requests
except ImportError:  # pragma: no cover - urllib fallback is for minimal Python installs.
    requests = None
    import urllib.request


LOGGER = logging.getLogger("extract_paper_images")

FIGURE_DIR_NAMES = {"pics", "figures", "figure", "fig", "images", "image", "img"}
SOURCE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".pdf", ".eps"}
EMBED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".pdf"}
SKIP_NAME_RE = re.compile(r"(logo|icon|favicon|thumb|thumbnail|author|orcid)", re.I)
ARXIV_RE = re.compile(r"(?P<id>\d{4}\.\d{4,5})(?:v\d+)?", re.I)


@dataclass
class ImageRecord:
    filename: str
    path: Path
    source: str
    size: int
    ext: str
    page: int | None = None


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract paper images into Research/papers/images.")
    parser.add_argument("paper", help="Local PDF path or arXiv id, e.g. papers/pdfs/2209.13916v1.pdf")
    parser.add_argument("--vault", default=None, help="Vault root. Defaults to current directory when it looks like a vault.")
    parser.add_argument("--output-dir", default=None, help="Output image directory.")
    parser.add_argument("--index-file", default=None, help="Output index.md path.")
    parser.add_argument("--max-embeds", type=int, default=12, help="Number of images to include in the embed snippet.")
    parser.add_argument("--min-source-count", type=int, default=3, help="Fallback to PDF extraction below this source image count.")
    parser.add_argument("--min-dimension", type=int, default=120, help="Minimum width/height for PDF embedded images.")
    parser.add_argument("--min-bytes", type=int, default=8 * 1024, help="Minimum byte size for PDF embedded images.")
    parser.add_argument("--skip-arxiv-source", action="store_true", help="Skip arXiv source download and use the local PDF only.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    vault = resolve_vault(Path(args.vault).expanduser() if args.vault else Path.cwd())
    paper_input = Path(args.paper).expanduser()
    if not paper_input.is_absolute() and paper_input.exists():
        paper_input = paper_input.resolve()
    elif not paper_input.is_absolute() and (vault / paper_input).exists():
        paper_input = (vault / paper_input).resolve()

    pdf_path = paper_input if paper_input.exists() and paper_input.suffix.lower() == ".pdf" else None
    arxiv_id = detect_arxiv_id(str(paper_input))
    paper_stem = pdf_path.stem if pdf_path else (arxiv_id or sanitize_name(args.paper))

    output_dir = Path(args.output_dir).expanduser() if args.output_dir else vault / "papers" / "images" / paper_stem
    if not output_dir.is_absolute():
        output_dir = vault / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    index_file = Path(args.index_file).expanduser() if args.index_file else output_dir / "index.md"
    if not index_file.is_absolute():
        index_file = vault / index_file

    records: list[ImageRecord] = []
    with tempfile.TemporaryDirectory(prefix="paper-images-") as temp_name:
        temp_dir = Path(temp_name)

        if arxiv_id and not args.skip_arxiv_source and download_arxiv_source(arxiv_id, temp_dir):
            source_records = extract_from_source(temp_dir, output_dir)
            records.extend(source_records)
            LOGGER.info("arXiv source figures: %s", len(source_records))

        if pdf_path and len(records) < args.min_source_count:
            records.extend(
                extract_from_pdf(
                    pdf_path=pdf_path,
                    output_dir=output_dir,
                    min_dimension=args.min_dimension,
                    min_bytes=args.min_bytes,
                )
            )

    records = dedupe_records(records)
    write_index(index_file, records, vault, args.max_embeds)

    LOGGER.info("Extracted %s images", len(records))
    LOGGER.info("Image dir: %s", output_dir)
    LOGGER.info("Index: %s", index_file)
    for record in records:
        print(obsidian_path(record.path, vault))

    return 0


def resolve_vault(start: Path) -> Path:
    current = start.resolve()
    candidates = [current, *current.parents]
    for candidate in candidates:
        if (candidate / ".obsidian").exists() or (candidate / "AGENTS.md").exists():
            return candidate
    return current


def detect_arxiv_id(value: str) -> str | None:
    match = ARXIV_RE.search(value)
    return match.group("id") if match else None


def download_arxiv_source(arxiv_id: str, output_dir: Path) -> bool:
    url = f"https://arxiv.org/e-print/{arxiv_id}"
    archive_path = output_dir / f"{arxiv_id}.tar.gz"
    LOGGER.info("Downloading arXiv source: %s", url)

    try:
        if requests:
            response = requests.get(url, timeout=60)
            if response.status_code != 200 or not response.content:
                LOGGER.info("arXiv source unavailable: HTTP %s", response.status_code)
                return False
            archive_path.write_bytes(response.content)
        else:
            with urllib.request.urlopen(url, timeout=60) as response:  # type: ignore[name-defined]
                archive_path.write_bytes(response.read())

        with tarfile.open(archive_path, "r:*") as tar:
            members = list(safe_tar_members(tar, output_dir))
            try:
                tar.extractall(output_dir, members=members, filter="data")
            except TypeError:
                tar.extractall(output_dir, members=members)
        return True
    except Exception as exc:
        LOGGER.info("Could not use arXiv source: %s", exc)
        return False


def safe_tar_members(tar: tarfile.TarFile, output_dir: Path) -> Iterable[tarfile.TarInfo]:
    root = output_dir.resolve()
    for member in tar.getmembers():
        if member.issym() or member.islnk():
            continue
        target = (output_dir / member.name).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            continue
        yield member


def extract_from_source(source_dir: Path, output_dir: Path) -> list[ImageRecord]:
    records: list[ImageRecord] = []
    source_files = find_source_figure_files(source_dir)

    for source_file in source_files:
        ext = source_file.suffix.lower()
        if ext == ".pdf":
            records.extend(render_pdf_figure(source_file, output_dir, source="pdf-figure"))
        elif ext == ".eps":
            target = unique_output_path(output_dir / source_file.name)
            shutil.copy2(source_file, target)
            records.append(make_record(target, "arxiv-source"))
        else:
            target = unique_output_path(output_dir / source_file.name)
            shutil.copy2(source_file, target)
            records.append(make_record(target, "arxiv-source"))

    return records


def find_source_figure_files(source_dir: Path) -> list[Path]:
    figure_dirs = [
        path for path in source_dir.rglob("*")
        if path.is_dir() and path.name.lower() in FIGURE_DIR_NAMES
    ]

    files: list[Path] = []
    seen: set[Path] = set()
    search_roots = figure_dirs if figure_dirs else [source_dir]
    for root in search_roots:
        for path in root.rglob("*"):
            if not path.is_file() or path in seen:
                continue
            if path.suffix.lower() not in SOURCE_EXTENSIONS:
                continue
            if SKIP_NAME_RE.search(path.name):
                continue
            seen.add(path)
            files.append(path)

    return sorted(files, key=lambda item: natural_key(item.name))


def render_pdf_figure(pdf_file: Path, output_dir: Path, source: str) -> list[ImageRecord]:
    if fitz is None:
        return render_pdf_figure_with_pdftoppm(pdf_file, output_dir, source)

    records: list[ImageRecord] = []
    try:
        doc = fitz.open(pdf_file)
    except Exception as exc:
        LOGGER.info("Skip PDF figure %s: %s", pdf_file.name, exc)
        return records

    try:
        if len(doc) > 3:
            LOGGER.info("Skip likely full paper PDF: %s (%s pages)", pdf_file.name, len(doc))
            return records

        for page_index, page in enumerate(doc):
            pix = page.get_pixmap(dpi=180, alpha=False)
            filename = f"{sanitize_name(pdf_file.stem)}_page{page_index + 1}.png"
            target = unique_output_path(output_dir / filename)
            pix.save(target)
            records.append(make_record(target, source, page=page_index + 1))
    finally:
        doc.close()

    return records


def render_pdf_figure_with_pdftoppm(pdf_file: Path, output_dir: Path, source: str) -> list[ImageRecord]:
    executable = shutil.which("pdftoppm")
    if not executable:
        LOGGER.info("Skip PDF figure %s: PyMuPDF and pdftoppm are unavailable", pdf_file.name)
        return []

    page_count = pdf_page_count(pdf_file)
    if page_count is not None and page_count > 3:
        LOGGER.info("Skip likely full paper PDF: %s (%s pages)", pdf_file.name, page_count)
        return []

    prefix = output_dir / sanitize_name(pdf_file.stem)
    before = {path.resolve() for path in output_dir.glob(f"{prefix.name}-*.png")}
    try:
        subprocess.run(
            [executable, "-png", "-r", "180", "-f", "1", "-l", "3", str(pdf_file), str(prefix)],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception as exc:
        LOGGER.info("Skip PDF figure %s: %s", pdf_file.name, exc)
        return []

    records: list[ImageRecord] = []
    for path in sorted(output_dir.glob(f"{prefix.name}-*.png"), key=lambda item: natural_key(item.name)):
        if path.resolve() in before:
            continue
        records.append(make_record(path, source))
    return records


def extract_from_pdf(pdf_path: Path, output_dir: Path, min_dimension: int, min_bytes: int) -> list[ImageRecord]:
    if fitz is None:
        return extract_from_pdf_with_pdfimages(pdf_path, output_dir, min_bytes)

    records: list[ImageRecord] = []
    LOGGER.info("Falling back to embedded PDF images: %s", pdf_path)

    doc = fitz.open(pdf_path)
    try:
        for page_index in range(len(doc)):
            page = doc[page_index]
            for image_index, image_info in enumerate(page.get_images(full=True)):
                xref = image_info[0]
                try:
                    base_image = doc.extract_image(xref)
                except Exception as exc:
                    LOGGER.info("Skip image xref %s on page %s: %s", xref, page_index + 1, exc)
                    continue

                image_bytes = base_image.get("image")
                image_ext = base_image.get("ext", "png")
                width = int(base_image.get("width", 0) or 0)
                height = int(base_image.get("height", 0) or 0)
                if not image_bytes:
                    continue
                if len(image_bytes) < min_bytes or max(width, height) < min_dimension:
                    continue

                filename = f"page{page_index + 1}_fig{image_index + 1}.{image_ext}"
                target = unique_output_path(output_dir / filename)
                target.write_bytes(image_bytes)
                records.append(make_record(target, "pdf-extraction", page=page_index + 1))
    finally:
        doc.close()

    return records


def extract_from_pdf_with_pdfimages(pdf_path: Path, output_dir: Path, min_bytes: int) -> list[ImageRecord]:
    executable = shutil.which("pdfimages")
    if not executable:
        LOGGER.info("PyMuPDF and pdfimages are unavailable; writing an empty index.")
        return []

    LOGGER.info("Falling back to Poppler pdfimages: %s", pdf_path)
    prefix = output_dir / f"{sanitize_name(pdf_path.stem)}_img"
    before = {path.resolve() for path in output_dir.glob(f"{prefix.name}-*.*")}
    try:
        result = subprocess.run(
            [executable, "-png", "-p", str(pdf_path), str(prefix)],
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except Exception as exc:
        LOGGER.info("pdfimages failed: %s", exc)
        return []

    if result.returncode != 0:
        message = (result.stderr or result.stdout or "").strip()
        LOGGER.info("pdfimages failed: %s", message)
        return []

    records: list[ImageRecord] = []
    for path in sorted(output_dir.glob(f"{prefix.name}-*.*"), key=lambda item: natural_key(item.name)):
        if path.resolve() in before:
            continue
        if path.stat().st_size < min_bytes:
            try:
                path.unlink()
            except OSError:
                pass
            continue
        page = parse_pdfimages_page(path.name)
        records.append(make_record(path, "pdfimages", page=page))
    return records


def pdf_page_count(pdf_file: Path) -> int | None:
    executable = shutil.which("pdfinfo")
    if not executable:
        return None
    try:
        result = subprocess.run(
            [executable, str(pdf_file)],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    match = re.search(r"^Pages:\s+(\d+)", result.stdout, re.M)
    return int(match.group(1)) if match else None


def parse_pdfimages_page(filename: str) -> int | None:
    match = re.search(r"-(\d+)-\d+\.[^.]+$", filename)
    return int(match.group(1)) if match else None


def write_index(index_file: Path, records: list[ImageRecord], vault: Path, max_embeds: int) -> None:
    index_file.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# 图片索引", "", f"总计：{len(records)} 张图片", ""]

    if not records:
        lines.extend([
            "> 未自动抽取到可用图片。精读正文需要图表时，再按需截图或手动补图到本目录。",
            "",
        ])

    embeddable = [record for record in records if record.path.suffix.lower() in EMBED_EXTENSIONS]
    if embeddable:
        lines.extend(["## 可复制到精读稿", ""])
        for record in embeddable[:max_embeds]:
            lines.append(f"![[{obsidian_path(record.path, vault)}|700]]")
        if len(embeddable) > max_embeds:
            lines.append(f"\n> 还有 {len(embeddable) - max_embeds} 张图片未列入预览。")
        lines.append("")

    by_source: dict[str, list[ImageRecord]] = {}
    for record in records:
        by_source.setdefault(record.source, []).append(record)

    for source, source_records in by_source.items():
        lines.extend([f"## 来源：{source}", ""])
        lines.append("| 文件 | 路径 | 大小 | 页码 |")
        lines.append("| --- | --- | ---: | ---: |")
        for record in source_records:
            page = record.page if record.page is not None else ""
            lines.append(
                f"| {record.filename} | `{obsidian_path(record.path, vault)}` | {record.size / 1024:.1f} KB | {page} |"
            )
        lines.append("")

    index_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def make_record(path: Path, source: str, page: int | None = None) -> ImageRecord:
    return ImageRecord(
        filename=path.name,
        path=path,
        source=source,
        size=path.stat().st_size,
        ext=path.suffix.lstrip(".").lower(),
        page=page,
    )


def dedupe_records(records: list[ImageRecord]) -> list[ImageRecord]:
    deduped: list[ImageRecord] = []
    seen: set[tuple[int, str]] = set()
    for record in records:
        key = (record.size, file_hash(record.path))
        if key in seen:
            try:
                record.path.unlink()
            except OSError:
                pass
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unique_output_path(path: Path) -> Path:
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    for index in range(2, 1000):
        candidate = path.with_name(f"{stem}_{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not create a unique filename for {path}")


def obsidian_path(path: Path, vault: Path) -> str:
    try:
        return path.resolve().relative_to(vault.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def sanitize_name(value: str) -> str:
    return re.sub(r'[\\/:*?"<>|#^[\]\s]+', "_", str(value)).strip("_") or "paper"


def natural_key(value: str) -> list[object]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", value)]


if __name__ == "__main__":
    raise SystemExit(main())
