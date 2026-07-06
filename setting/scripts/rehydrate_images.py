#!/usr/bin/env python3
"""Re-hydrate local paper images that notes/drafts reference but that are missing on disk.

Why this exists
---------------
The Git sync policy keeps PDFs (``papers/pdfs/``) and images (``papers/images/``)
LOCAL and out of Git, so a fresh clone / new machine gets the paper notes
(``papers/@*.md``) and bilingual reading drafts (``papers/bilingual/*.md``) but
NOT the images those drafts embed. The embeds then render as broken links.

Images are recoverable deterministically: ``extract_paper_images.py`` pulls each
paper's arXiv source package, which preserves the original figure filenames, so a
re-extraction reproduces exactly the filenames the drafts reference. This script
scans every note (+ its reading draft), finds the ``papers/images/<stem>/...``
embeds that are missing on disk, and re-extracts them per paper.

Usage
-----
  python setting/scripts/rehydrate_images.py             # fix every paper with missing images
  python setting/scripts/rehydrate_images.py --check     # report only; exit 1 if anything missing
  python setting/scripts/rehydrate_images.py @yu2026warp-rm liu2026steam   # only these papers
  python setting/scripts/rehydrate_images.py --force     # re-extract even if images already present
  python setting/scripts/rehydrate_images.py --clean     # wipe each target image dir before extracting
  python setting/scripts/rehydrate_images.py --dry-run   # show what would be extracted, do nothing

Exit code is non-zero if any referenced image is still missing at the end, so it
doubles as a pre-push / CI check for a machine's local asset completeness.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

IMAGE_REF = re.compile(r"papers/images/[^\]\)\n\"']+?\.(?:png|jpe?g|gif|webp|svg)", re.IGNORECASE)
EXTRACTOR = Path(__file__).resolve().parent / "extract_paper_images.py"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("notes", nargs="*", help="note paths or citekeys to limit to (default: all papers/@*.md)")
    parser.add_argument("--check", action="store_true", help="report missing images only; do not extract")
    parser.add_argument("--dry-run", action="store_true", help="show what would be extracted; do not run")
    parser.add_argument("--force", action="store_true", help="re-extract even if all images already present")
    parser.add_argument("--clean", action="store_true", help="remove each target image dir before extracting")
    args = parser.parse_args()

    root = repo_root()
    notes = resolve_notes(root, args.notes)
    if not notes:
        print("No matching paper notes found.")
        return 0

    scanned = extracted = 0
    unresolved: list[str] = []          # referenced images still missing after we finish
    no_arxiv: list[str] = []            # papers with missing images but no arXiv id to fix them

    for note in notes:
        info = parse_note(note, root)
        refs = collect_refs(note, info, root)
        if not refs:
            continue
        scanned += 1
        missing = [r for r in refs if not (root / r).exists()]

        if not missing and not args.force:
            continue

        rel = note.relative_to(root)
        if args.check:
            print(f"MISSING {len(missing):>2}  {rel}")
            for m in missing:
                print(f"           - {m}")
            unresolved.extend(missing)
            continue

        if not info.get("images"):
            print(f"SKIP  {rel}: {len(missing)} missing image(s) but no `images:` dir in frontmatter")
            unresolved.extend(missing)
            continue
        if not info.get("arxiv"):
            print(f"SKIP  {rel}: {len(missing)} missing image(s) but no `arxiv:` id (needs manual copy)")
            no_arxiv.append(str(rel))
            unresolved.extend(missing)
            continue

        out_dir = (root / info["images"]).resolve()
        why = "force" if not missing else f"{len(missing)} missing"
        print(f"EXTRACT {rel}  (arXiv {info['arxiv']} -> {info['images']}, {why})")
        if args.dry_run:
            continue

        if args.clean and out_dir.exists():
            shutil.rmtree(out_dir)
        ok = run_extractor(info["arxiv"], out_dir, root)
        extracted += 1
        still = [r for r in refs if not (root / r).exists()]
        if ok and not still:
            print(f"        -> OK, {len(refs)} referenced image(s) present")
        else:
            for m in still:
                print(f"        -> STILL MISSING: {m}  (not in arXiv source? hand-made figure)")
            unresolved.extend(still)

    print()
    print(f"Summary: scanned {scanned} paper(s) with image embeds; "
          f"{'would extract' if args.dry_run else 'extracted'} {extracted}; "
          f"{len(unresolved)} referenced image(s) still missing.")
    if no_arxiv:
        print("  No arXiv id (copy images manually): " + ", ".join(no_arxiv))
    return 1 if unresolved else 0


def repo_root() -> Path:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True, capture_output=True, text=True)
    return Path(out.stdout.strip())


def resolve_notes(root: Path, names: list[str]) -> list[Path]:
    if not names:
        return sorted((root / "papers").glob("@*.md"))
    notes: list[Path] = []
    for name in names:
        p = Path(name)
        if p.is_absolute() and p.exists():
            notes.append(p)
            continue
        cand = root / name
        if cand.exists():
            notes.append(cand)
            continue
        stem = name.lstrip("@")
        if stem.endswith(".md"):
            stem = stem[:-3]
        cand = root / "papers" / f"@{stem}.md"
        if cand.exists():
            notes.append(cand)
        else:
            print(f"WARN: no note found for '{name}'")
    return notes


def parse_note(note: Path, root: Path) -> dict:
    text = note.read_text(encoding="utf-8", errors="ignore")
    return {
        "arxiv": front_value(text, "arxiv"),
        "images": strip_dir(front_value(text, "images")),
        "reading": strip_link(front_value(text, "reading")),
    }


def front_value(text: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip('"').strip("'").strip() or None


def strip_link(value: str | None) -> str | None:
    if not value:
        return None
    return value.replace("[[", "").replace("]]", "").strip('"').strip("'").strip() or None


def strip_dir(value: str | None) -> str | None:
    value = strip_link(value)
    return value.rstrip("/") if value else None


def collect_refs(note: Path, info: dict, root: Path) -> list[str]:
    texts = [note.read_text(encoding="utf-8", errors="ignore")]
    if info.get("reading"):
        draft = root / info["reading"]
        if draft.exists():
            texts.append(draft.read_text(encoding="utf-8", errors="ignore"))
    refs: set[str] = set()
    for text in texts:
        for m in IMAGE_REF.findall(text):
            # ignore the auto-generated index preview and keep it to the paper's own dir when known
            if info.get("images") and not m.startswith(info["images"] + "/"):
                # still count it: a stray ref outside the declared dir is worth surfacing
                pass
            refs.add(m.strip())
    return sorted(refs)


def run_extractor(arxiv_id: str, out_dir: Path, root: Path) -> bool:
    try:
        proc = subprocess.run(
            [sys.executable, str(EXTRACTOR), arxiv_id, "--output-dir", str(out_dir)],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        print("        -> extractor timed out")
        return False
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout).strip().splitlines()[-3:]
        print("        -> extractor failed: " + " | ".join(tail))
        return False
    return True


if __name__ == "__main__":
    sys.exit(main())
