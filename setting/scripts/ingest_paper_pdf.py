#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preview or ingest a paper PDF into this Research vault.

Default mode is a dry run. It identifies DOI/arXiv/title signals, checks
duplicates, proposes a citekey, PDF target, image index paths, and the note that
would be created. Use --apply to write files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover - allows metadata-only preview.
    fitz = None


DOI_RE = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", re.I)
ARXIV_RE = re.compile(r"(?:arxiv[:\s]*)?(?P<id>\d{4}\.\d{4,5})(?P<version>v\d+)?", re.I)
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
WIKI_LINK_RE = re.compile(r"\[\[([^\]#|]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]")
READING_MARKER = "⌛"
TITLE_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "based",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "toward",
    "towards",
    "using",
    "via",
    "with",
}


@dataclass
class Metadata:
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: str = ""
    doi: str = ""
    arxiv: str = ""
    venue: str = ""
    url: str = ""
    openalex: str = ""
    abstract: str = ""
    source: str = "pdf"
    confidence: str = "low"


@dataclass
class ExistingPaper:
    path: Path
    stem: str
    title: str = ""
    doi: str = ""
    arxiv: str = ""
    pdf: str = ""


@dataclass
class Duplicate:
    kind: str
    existing: ExistingPaper
    detail: str


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", help="PDF path to preview or ingest.")
    parser.add_argument("--vault", default=None, help="Vault root. Defaults to current directory or parent vault.")
    parser.add_argument("--apply", action="store_true", help="Write the proposed note/PDF/image index/map changes.")
    parser.add_argument("--lookup", action="store_true", help="Use arXiv/OpenAlex network lookups when identifiers are found.")
    parser.add_argument("--allow-duplicate", action="store_true", help="Allow creating a new note despite duplicate warnings.")
    parser.add_argument("--merge-note", default="", help="Existing @citekey note to update instead of creating a new one.")
    parser.add_argument("--overwrite-fields", action="store_true", help="When merging, overwrite non-empty frontmatter fields.")
    parser.add_argument("--citekey", default="", help="Manual citekey, e.g. @smith2024diffusion-policy.")
    parser.add_argument("--title", default="", help="Manual title override.")
    parser.add_argument("--author", action="append", default=[], help="Manual author. Can be repeated.")
    parser.add_argument("--year", default="", help="Manual year override.")
    parser.add_argument("--doi", default="", help="Manual DOI override.")
    parser.add_argument("--arxiv", default="", help="Manual arXiv id override.")
    parser.add_argument("--venue", default="", help="Manual venue override.")
    parser.add_argument("--metadata-source", default="", help="Manual metadata_source override.")
    parser.add_argument("--metadata-confidence", choices=["high", "medium", "low"], default="", help="Manual confidence.")
    parser.add_argument("--rename-pdf", action="store_true", help="Use citekey as the target PDF filename.")
    parser.add_argument("--skip-images", action="store_true", help="Do not run extract_paper_images.py on --apply.")
    parser.add_argument("--defer-images", action="store_true", help="Create an empty image index placeholder and skip extraction for now.")
    parser.add_argument("--map-axis", default="", help="Quick-index axis to update when creating a new note, e.g. #map/入口/综述坐标系.")
    parser.add_argument("--map-display", default="", help="Display label used in 论文地图 quick index.")
    parser.add_argument("--print-note", action="store_true", help="Print the full note body in dry-run output.")
    args = parser.parse_args()

    if args.skip_images and args.defer_images:
        print("Use only one of --skip-images or --defer-images.", file=sys.stderr)
        return 2

    vault = resolve_vault(Path(args.vault).expanduser() if args.vault else Path.cwd())
    pdf_path = resolve_pdf_path(Path(args.pdf).expanduser(), vault)
    if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
        print(f"Not a PDF file: {pdf_path}", file=sys.stderr)
        return 2

    metadata = collect_metadata(pdf_path, args)
    if args.lookup:
        metadata = enrich_metadata(metadata)
    apply_overrides(metadata, args)
    metadata.confidence = args.metadata_confidence or infer_confidence(metadata)
    metadata.source = args.metadata_source or infer_source(metadata)

    citekey = normalize_citekey(args.citekey or build_citekey(metadata))
    if citekey == "@paperyyyypaper":
        print("Could not build a meaningful citekey. Pass --citekey.", file=sys.stderr)
        return 2

    pdf_stem = citekey.lstrip("@") if args.rename_pdf else pdf_path.stem
    target_pdf = unique_path(vault / "papers" / "pdfs" / f"{pdf_stem}.pdf")
    if is_inside(pdf_path, vault / "papers" / "pdfs") and not args.rename_pdf:
        target_pdf = pdf_path

    images_dir = vault / "papers" / "images" / target_pdf.stem
    index_file = images_dir / "index.md"
    note_path = vault / "papers" / f"{citekey}.md"
    existing_papers = read_existing_papers(vault)
    duplicates = find_duplicates(pdf_path, metadata, existing_papers, vault)

    merge_path = find_note_path(args.merge_note, existing_papers, vault) if args.merge_note else None
    creating_new = merge_path is None

    if duplicates and not args.allow_duplicate and creating_new:
        print_preview(metadata, citekey, note_path, target_pdf, images_dir, index_file, duplicates, args)
        print("\nDuplicate candidates found. Choose one action:")
        print("  - merge into an existing note: --merge-note @citekey --apply")
        print("  - create anyway: --allow-duplicate --apply")
        print("  - cancel: run no --apply command")
        return 1 if args.apply else 0

    if args.apply and creating_new and note_path.exists():
        print(f"Paper note already exists: {note_path}", file=sys.stderr)
        return 1

    if args.apply and creating_new and not args.map_axis:
        print("Creating a new papers/@*.md note requires --map-axis so 论文地图 stays covered.", file=sys.stderr)
        return 2

    note_text = build_note(citekey, metadata, target_pdf, images_dir, index_file, vault)
    print_preview(metadata, citekey, note_path if creating_new else merge_path, target_pdf, images_dir, index_file, duplicates, args)
    if args.print_note:
        print("\n--- proposed note ---")
        print(note_text.rstrip())

    if not args.apply:
        print("\nDry run only. Re-run with --apply to write files.")
        return 0

    copy_pdf(pdf_path, target_pdf)
    if creating_new:
        note_path.write_text(note_text, encoding="utf-8")
        update_paper_map(vault / "论文地图.md", args.map_axis, citekey, args.map_display or display_title(metadata, citekey))
        print(f"Created note: {relative(note_path, vault)}")
    else:
        update_existing_note(merge_path, metadata, target_pdf, images_dir, index_file, args.overwrite_fields, vault)
        print(f"Updated note: {relative(merge_path, vault)}")

    if args.defer_images:
        write_deferred_image_index(index_file, images_dir, vault)
    elif not args.skip_images:
        run_image_extraction(vault, target_pdf, images_dir, index_file)

    print("Done.")
    return 0


def resolve_vault(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".obsidian").exists() or (candidate / "AGENTS.md").exists():
            return candidate
    return current


def resolve_pdf_path(path: Path, vault: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    if path.exists():
        return path.resolve()
    return (vault / path).resolve()


def collect_metadata(pdf_path: Path, args: argparse.Namespace) -> Metadata:
    text, pdf_title = extract_pdf_text_and_title(pdf_path)
    metadata = Metadata(title=pdf_title)
    metadata.doi = first_match(DOI_RE, text)
    metadata.arxiv = detect_arxiv(f"{pdf_path.name}\n{text}") or ""
    metadata.title = metadata.title or guess_title(text, pdf_path)
    metadata.authors = guess_authors(text, metadata.title)
    metadata.year = guess_year(text, metadata.arxiv)
    return metadata


def extract_pdf_text_and_title(pdf_path: Path) -> tuple[str, str]:
    chunks: list[str] = []
    title = ""
    if fitz is None:
        return extract_text_with_pdftotext(pdf_path), title

    try:
        doc = fitz.open(pdf_path)
    except Exception:
        return extract_text_with_pdftotext(pdf_path), title

    try:
        meta = doc.metadata or {}
        title = clean_pdf_title(meta.get("title") or "")
        for page_index in range(min(len(doc), 3)):
            chunks.append(doc[page_index].get_text("text") or "")
    finally:
        doc.close()

    return "\n".join(chunks), title


def extract_text_with_pdftotext(pdf_path: Path) -> str:
    executable = shutil.which("pdftotext")
    if not executable:
        return ""
    try:
        result = subprocess.run(
            [executable, "-f", "1", "-l", "3", str(pdf_path), "-"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except Exception:
        return ""
    return result.stdout if result.returncode == 0 else ""


def clean_pdf_title(value: str) -> str:
    value = " ".join(str(value).split())
    if not value or value.lower() in {"untitled", "microsoft word", "paper"}:
        return ""
    if value.lower().endswith(".docx") or value.lower().endswith(".doc"):
        return ""
    if ARXIV_RE.fullmatch(value) or re.fullmatch(r"[\w.-]+\.pdf", value, flags=re.I):
        return ""
    return value


def first_match(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    if not match:
        return ""
    value = match.group(1).rstrip(".,;)")
    return value


def detect_arxiv(text: str) -> str:
    match = ARXIV_RE.search(text)
    if not match:
        return ""
    return f"{match.group('id')}{match.group('version') or ''}"


def guess_title(text: str, pdf_path: Path) -> str:
    lines = [
        " ".join(line.strip().split())
        for line in text.splitlines()[:80]
        if line.strip()
    ]
    pre_abstract: list[str] = []
    for line in lines:
        if line.lower().startswith("abstract"):
            break
        pre_abstract.append(line)

    for line in pre_abstract:
        if is_title_candidate(line, strict=True):
            return line

    candidates: list[str] = []
    for line in lines:
        if is_title_candidate(line, strict=False):
            candidates.append(line)
        if len(candidates) >= 6:
            break

    if candidates:
        return max(candidates, key=lambda item: (score_title_candidate(item), -abs(len(item) - 70)))
    return pdf_path.stem.replace("_", " ").replace("-", " ")


def is_title_candidate(line: str, strict: bool) -> bool:
    lower = line.lower()
    if len(line) < 12 or len(line) > 160:
        return False
    if "arxiv" in lower or lower.startswith(("abstract", "keywords", "doi", "http")):
        return False
    if DOI_RE.search(line) or ARXIV_RE.search(line):
        return False
    if sum(char.isalpha() for char in line) < 8:
        return False
    if strict and re.search(r"[@,]|\b(university|department|institute|laboratory|abstract)\b", lower):
        return False
    return True


def score_title_candidate(value: str) -> int:
    words = re.findall(r"[A-Za-z0-9]+", value)
    return len([word for word in words if word.lower() not in TITLE_STOP_WORDS])


def guess_authors(text: str, title: str) -> list[str]:
    lines = [
        " ".join(line.strip().split())
        for line in text.splitlines()[:60]
        if line.strip()
    ]
    title_seen = False
    candidate_lines: list[str] = []
    for line in lines:
        lower = line.lower()
        if normalize_title(line) == normalize_title(title):
            title_seen = True
            continue
        if lower.startswith("abstract"):
            break
        if not title_seen:
            continue
        if "arxiv" in lower or DOI_RE.search(line):
            continue
        if re.search(r"\b(university|department|institute|laboratory|school|college|abstract)\b", lower):
            continue
        if len(line) > 180:
            continue
        candidate_lines.append(line)
        if len(candidate_lines) >= 3:
            break

    if not candidate_lines:
        return []

    raw = " ".join(candidate_lines)
    raw = re.sub(r"\S+@\S+", "", raw)
    raw = re.sub(r"[*†‡§]", "", raw)
    raw = re.sub(r"(?<=\D)\d+(?=\D|$)", "", raw)
    raw = raw.replace(" and ", ", ")
    parts = [part.strip(" ,.;") for part in raw.split(",")]
    authors = []
    for part in parts:
        part = re.sub(r"\s+", " ", part).strip()
        if not part or len(part.split()) < 2:
            continue
        if re.search(r"\b(university|department|institute|laboratory)\b", part, re.I):
            continue
        authors.append(part)
    return authors[:10]


def guess_year(text: str, arxiv: str) -> str:
    if arxiv:
        year = 2000 + int(arxiv[:2])
        return str(year)

    match = YEAR_RE.search(text)
    return match.group(1) if match else ""


def enrich_metadata(metadata: Metadata) -> Metadata:
    if metadata.arxiv:
        arxiv_metadata = lookup_arxiv(metadata.arxiv)
        metadata = merge_metadata(metadata, arxiv_metadata)
    if metadata.doi:
        openalex_metadata = lookup_openalex_by_doi(metadata.doi)
        metadata = merge_metadata(metadata, openalex_metadata)
    return metadata


def lookup_arxiv(arxiv_id: str) -> Metadata:
    base_id = re.sub(r"v\d+$", "", arxiv_id)
    url = f"https://export.arxiv.org/api/query?id_list={urllib.parse.quote(base_id)}"
    try:
        raw = urllib.request.urlopen(url, timeout=30).read()
    except Exception as exc:
        print(f"arXiv lookup failed: {exc}", file=sys.stderr)
        return Metadata()

    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(raw)
    entry = root.find("atom:entry", ns)
    if entry is None:
        return Metadata()

    published = entry.findtext("atom:published", default="", namespaces=ns)
    doi = entry.findtext("arxiv:doi", default="", namespaces=ns)
    return Metadata(
        title=" ".join(entry.findtext("atom:title", default="", namespaces=ns).split()),
        authors=[
            " ".join(author.findtext("atom:name", default="", namespaces=ns).split())
            for author in entry.findall("atom:author", ns)
        ],
        year=published[:4],
        doi=doi,
        arxiv=arxiv_id,
        url=f"https://arxiv.org/abs/{base_id}",
        abstract=" ".join(entry.findtext("atom:summary", default="", namespaces=ns).split()),
        source="arxiv",
        confidence="high",
    )


def lookup_openalex_by_doi(doi: str) -> Metadata:
    url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi, safe='')}"
    try:
        data = json.loads(urllib.request.urlopen(url, timeout=30).read().decode("utf-8"))
    except Exception as exc:
        print(f"OpenAlex lookup failed: {exc}", file=sys.stderr)
        return Metadata()

    venue = data.get("primary_location", {}).get("source", {}).get("display_name") or data.get("host_venue", {}).get("display_name") or ""
    authors = [
        item.get("author", {}).get("display_name", "")
        for item in data.get("authorships", [])
        if item.get("author", {}).get("display_name")
    ]
    return Metadata(
        title=data.get("title") or "",
        authors=authors,
        year=str(data.get("publication_year") or ""),
        doi=data.get("doi") or doi,
        venue=venue,
        url=data.get("id") or "",
        openalex=data.get("id") or "",
        source="openalex",
        confidence="high",
    )


def merge_metadata(base: Metadata, incoming: Metadata) -> Metadata:
    if not incoming.title and not incoming.doi and not incoming.arxiv:
        return base

    for field_name in ["title", "year", "doi", "arxiv", "venue", "url", "openalex", "abstract"]:
        if not getattr(base, field_name) and getattr(incoming, field_name):
            setattr(base, field_name, getattr(incoming, field_name))
    if not base.authors and incoming.authors:
        base.authors = incoming.authors
    if incoming.source != "pdf":
        base.source = incoming.source
    if incoming.confidence == "high":
        base.confidence = "high"
    return base


def apply_overrides(metadata: Metadata, args: argparse.Namespace) -> None:
    if args.title:
        metadata.title = args.title
    if args.author:
        metadata.authors = args.author
    if args.year:
        metadata.year = args.year
    if args.doi:
        metadata.doi = args.doi
    if args.arxiv:
        metadata.arxiv = args.arxiv
    if args.venue:
        metadata.venue = args.venue


def infer_source(metadata: Metadata) -> str:
    if metadata.source and metadata.source != "pdf":
        return metadata.source
    if metadata.arxiv:
        return "arxiv"
    if metadata.doi:
        return "doi"
    return "pdf"


def infer_confidence(metadata: Metadata) -> str:
    if metadata.confidence == "high":
        return "high"
    if (metadata.doi or metadata.arxiv) and metadata.title:
        return "medium"
    if metadata.title and metadata.year:
        return "medium"
    return "low"


def build_citekey(metadata: Metadata) -> str:
    first_author = metadata.authors[0] if metadata.authors else "paper"
    family = slug_part(first_author.split()[-1] if first_author.split() else first_author) or "paper"
    year = metadata.year or "yyyy"
    title_slug = build_title_slug(metadata.title or "paper")
    return f"@{family}{year}{title_slug}"


def build_title_slug(title: str) -> str:
    words = [
        word
        for word in re.sub(r"['’]", "", title.lower()).replace("-", " ").split()
        if word and word not in TITLE_STOP_WORDS
    ]
    cleaned: list[str] = []
    for word in words:
        token = re.sub(r"[^a-z0-9]+", "", word)
        if not token or token.isdigit() or token in cleaned:
            continue
        cleaned.append(token)
        if len(cleaned) >= 4:
            break
    return "-".join(cleaned) or "paper"


def slug_part(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def normalize_citekey(value: str) -> str:
    raw = str(value).strip().removesuffix(".md")
    if not raw.startswith("@"):
        raw = f"@{raw}"
    raw = raw.lower()
    raw = re.sub(r'[\\/:*?"<>|#^[\]\s]+', "-", raw)
    raw = re.sub(r"-+", "-", raw)
    raw = raw.replace("@-", "@").strip("-")
    return raw


def read_existing_papers(vault: Path) -> list[ExistingPaper]:
    papers: list[ExistingPaper] = []
    for path in sorted((vault / "papers").glob("@*.md")):
        fields = parse_frontmatter(path.read_text(encoding="utf-8"))
        papers.append(
            ExistingPaper(
                path=path,
                stem=path.stem,
                title=str(fields.get("title") or ""),
                doi=str(fields.get("doi") or ""),
                arxiv=str(fields.get("arxiv") or ""),
                pdf=str(fields.get("pdf") or ""),
            )
        )
    return papers


def parse_frontmatter(text: str) -> dict[str, object]:
    match = FRONTMATTER_RE.search(text)
    if not match:
        return {}

    fields: dict[str, object] = {}
    current_key = ""
    current_list: list[str] = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("  - ") and current_key:
            current_list.append(unquote_yaml(line[4:].strip()))
            fields[current_key] = current_list
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        current_list = []
        fields[key] = unquote_yaml(value)
    return fields


def unquote_yaml(value: str) -> str:
    value = value.strip()
    if value in {"", "null", "None"}:
        return ""
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def find_duplicates(pdf_path: Path, metadata: Metadata, existing: list[ExistingPaper], vault: Path) -> list[Duplicate]:
    duplicates: list[Duplicate] = []
    input_hash: str | None = None
    normalized_title = normalize_title(metadata.title)
    normalized_doi = normalize_doi(metadata.doi)
    normalized_arxiv = normalize_arxiv(metadata.arxiv)

    for paper in existing:
        if normalized_doi and normalize_doi(paper.doi) == normalized_doi:
            duplicates.append(Duplicate("doi", paper, normalized_doi))
            continue
        if normalized_arxiv and normalize_arxiv(paper.arxiv) == normalized_arxiv:
            duplicates.append(Duplicate("arxiv", paper, normalized_arxiv))
            continue
        if normalized_title and normalize_title(paper.title) == normalized_title:
            duplicates.append(Duplicate("title", paper, metadata.title))
            continue

        existing_pdf = resolve_obsidian_path(paper.pdf, vault)
        if existing_pdf and existing_pdf.exists():
            if input_hash is None:
                input_hash = file_hash(pdf_path)
            if file_hash(existing_pdf) == input_hash:
                duplicates.append(Duplicate("pdf-hash", paper, input_hash[:12]))

    return duplicates


def normalize_doi(value: str) -> str:
    return str(value).strip().lower().removeprefix("https://doi.org/").removeprefix("http://doi.org/").rstrip(".,;")


def normalize_arxiv(value: str) -> str:
    return re.sub(r"v\d+$", "", str(value).strip().lower().replace("arxiv:", ""))


def normalize_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def resolve_obsidian_path(value: str, vault: Path) -> Path | None:
    if not value:
        return None
    wiki = WIKI_LINK_RE.search(value)
    raw = wiki.group(1) if wiki else value
    raw = raw.strip().strip('"').strip("'").replace("\\", "/")
    if not raw:
        return None
    candidates = [vault / raw]
    if not raw.endswith(".pdf") and not raw.endswith(".md"):
        candidates.extend([vault / f"{raw}.pdf", vault / f"{raw}.md"])
    return next((path for path in candidates if path.exists()), candidates[0])


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_note_path(citekey: str, existing: list[ExistingPaper], vault: Path) -> Path | None:
    normalized = normalize_citekey(citekey)
    for paper in existing:
        if paper.stem == normalized:
            return paper.path
    candidate = vault / "papers" / f"{normalized}.md"
    return candidate if candidate.exists() else None


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    for index in range(2, 1000):
        candidate = path.with_name(f"{stem}-{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find unique path for {path}")


def is_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def build_note(citekey: str, metadata: Metadata, pdf_path: Path, images_dir: Path, index_file: Path, vault: Path) -> str:
    title = metadata.title or citekey
    authors_yaml = "\n".join(f'  - "[[{escape_yaml(author)}]]"' for author in metadata.authors)
    aliases = f"  - {yaml_string(title)}" if title else ""
    abstract = metadata.abstract.strip()
    return f"""---
tags:
  - paper
status: unread
aliases:
{aliases}
year: {metadata.year}
title: {yaml_string(title)}
doi: {yaml_string(metadata.doi)}
arxiv: {yaml_string(metadata.arxiv)}
url: {yaml_string(metadata.url)}
venue: {yaml_string(metadata.venue)}
openalex: {yaml_string(metadata.openalex)}
metadata_source: {metadata.source}
metadata_confidence: {metadata.confidence}
pdf: "[[{relative(pdf_path, vault)}]]"
reading:
images: "{relative(images_dir, vault)}/"
image_index: "[[{relative(index_file, vault)}]]"
authors:
{authors_yaml}
institutions:
topics:
---

# {title}

- [ ] PDF:: [[{relative(pdf_path, vault)}]]
- [ ] 元数据:: source={metadata.source}, confidence={metadata.confidence}
- [ ] 精读稿:: 待整理
- [ ] 地图维护:: 已加入 [[论文地图]] 快速索引后，运行 `python setting/scripts/check_paper_map.py --sync-reading-markers`
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

{abstract}

## 一句话定位


## 方法 / 对象


## 证据


## 局限


## 我的阅读笔记


```dataviewjs
const {{Research}} = customJS
Research.topic(dv)
```
"""


def yaml_string(value: str) -> str:
    return json.dumps(str(value), ensure_ascii=False) if value else ""


def escape_yaml(value: str) -> str:
    return str(value).replace('"', '\\"')


def relative(path: Path, vault: Path) -> str:
    try:
        return path.resolve().relative_to(vault.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def display_title(metadata: Metadata, citekey: str) -> str:
    title = metadata.title or citekey
    words = [word for word in re.split(r"\s+", title.strip()) if word]
    return " ".join(words[:5]) if words else citekey


def print_preview(
    metadata: Metadata,
    citekey: str,
    note_path: Path | None,
    target_pdf: Path,
    images_dir: Path,
    index_file: Path,
    duplicates: list[Duplicate],
    args: argparse.Namespace,
) -> None:
    vault = resolve_vault(Path(args.vault).expanduser() if args.vault else Path.cwd())
    print("Paper PDF ingest preview")
    print(f"  title: {metadata.title or '-'}")
    print(f"  authors: {', '.join(metadata.authors) if metadata.authors else '-'}")
    print(f"  year: {metadata.year or '-'}")
    print(f"  doi: {metadata.doi or '-'}")
    print(f"  arxiv: {metadata.arxiv or '-'}")
    print(f"  metadata: source={metadata.source}, confidence={metadata.confidence}")
    print(f"  citekey: {citekey}")
    print(f"  note: {relative(note_path, vault) if note_path else '-'}")
    print(f"  pdf: {relative(target_pdf, vault)}")
    print(f"  images: {relative(images_dir, vault)}/")
    print(f"  image_index: {relative(index_file, vault)}")
    print(f"  image_mode: {image_mode(args)}")
    print(f"  map_axis: {args.map_axis or '-'}")
    if duplicates:
        print("  duplicates:")
        for duplicate in duplicates:
            print(f"    - {duplicate.kind}: {relative(duplicate.existing.path, vault)} ({duplicate.detail})")
    else:
        print("  duplicates: none")


def image_mode(args: argparse.Namespace) -> str:
    if args.defer_images:
        return "defer"
    if args.skip_images:
        return "skip"
    return "extract"


def copy_pdf(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() == target.resolve():
        return
    shutil.copy2(source, target)
    print(f"Copied PDF: {target}")


def update_existing_note(
    note_path: Path | None,
    metadata: Metadata,
    pdf_path: Path,
    images_dir: Path,
    index_file: Path,
    overwrite: bool,
    vault: Path,
) -> None:
    if note_path is None:
        raise RuntimeError("--merge-note did not match an existing note")

    text = note_path.read_text(encoding="utf-8")
    replacements = {
        "title": yaml_string(metadata.title),
        "doi": yaml_string(metadata.doi),
        "arxiv": yaml_string(metadata.arxiv),
        "url": yaml_string(metadata.url),
        "venue": yaml_string(metadata.venue),
        "openalex": yaml_string(metadata.openalex),
        "metadata_source": metadata.source,
        "metadata_confidence": metadata.confidence,
        "pdf": f'"[[{relative(pdf_path, vault)}]]"',
        "images": f'"{relative(images_dir, vault)}/"',
        "image_index": f'"[[{relative(index_file, vault)}]]"',
    }
    for key, value in replacements.items():
        if value:
            text = set_frontmatter_field(text, key, value, overwrite)
    note_path.write_text(text, encoding="utf-8")


def set_frontmatter_field(text: str, key: str, value: str, overwrite: bool) -> str:
    match = FRONTMATTER_RE.search(text)
    if not match:
        return text
    frontmatter = match.group(1)
    pattern = re.compile(rf"^{re.escape(key)}:[ \t]*(.*)$", re.M)
    field_match = pattern.search(frontmatter)
    if field_match:
        current = field_match.group(1).strip()
        if current and not overwrite:
            return text
        frontmatter = pattern.sub(f"{key}: {value}", frontmatter)
    else:
        frontmatter = f"{frontmatter.rstrip()}\n{key}: {value}"
    return f"---\n{frontmatter}\n---{text[match.end():]}"


def update_paper_map(map_path: Path, axis: str, citekey: str, display: str) -> None:
    text = map_path.read_text(encoding="utf-8")
    link = f"[[{citekey}|{READING_MARKER} {display}]]"
    lines = text.splitlines()
    in_quick = False
    inserted = False
    quick_end = len(lines)

    for index, line in enumerate(lines):
        if line.startswith("## "):
            if line == "## 快速索引":
                in_quick = True
                continue
            if in_quick:
                quick_end = index
                break
        if in_quick and line.startswith(f"- {axis} ::"):
            if citekey not in line:
                lines[index] = f"{line} · {link}"
            inserted = True
            break

    if not inserted:
        lines.insert(quick_end, f"- {axis} :: {link}")

    map_path.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")
    print(f"Updated map: {map_path}")


def write_deferred_image_index(index_file: Path, images_dir: Path, vault: Path) -> None:
    images_dir.mkdir(parents=True, exist_ok=True)
    if index_file.exists():
        print(f"Image index already exists; left unchanged: {relative(index_file, vault)}")
        return

    index_file.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 图片索引",
        "",
        "总计：0 张图片",
        "",
        "> 图片抽取已延后。精读或需要图表讲解时，再运行 `setting/scripts/extract_paper_images.py` 生成完整索引。",
        "",
        "## 状态",
        "",
        f"- 图片目录：`{relative(images_dir, vault)}/`",
        "- 状态：deferred",
    ]
    index_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Deferred image index: {relative(index_file, vault)}")


def run_image_extraction(vault: Path, pdf_path: Path, images_dir: Path, index_file: Path) -> None:
    script = vault / "setting" / "scripts" / "extract_paper_images.py"
    command = [
        sys.executable,
        str(script),
        relative(pdf_path, vault),
        "--vault",
        str(vault),
        "--output-dir",
        str(images_dir),
        "--index-file",
        str(index_file),
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    raise SystemExit(main())
