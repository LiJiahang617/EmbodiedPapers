#!/usr/bin/env python3
"""Re-hydrate local paper PDFs that notes reference but that are missing on disk.

Why this exists
---------------
The Git sync policy keeps PDFs (``papers/pdfs/``) and images (``papers/images/``)
LOCAL and out of Git, so a fresh clone / new machine gets the paper notes
(``papers/@*.md``) and bilingual reading drafts but NOT the source PDFs those
notes point to via their ``pdf:`` field. The link then resolves to nothing.

PDFs are recoverable deterministically from each note's own metadata: the ``arxiv``
id (re-downloaded from ``https://arxiv.org/pdf/<id>``) or, for non-arXiv papers,
the ``url`` field (GitHub ``/blob/`` links are rewritten to ``raw`` links; arXiv
``/abs/`` links to ``/pdf/``; direct ``*.pdf`` links used as-is). Each download is
written to the exact filename the note's ``pdf:`` field expects, so the note link
resolves afterwards. This mirrors ``rehydrate_images.py`` for images.

Usage
-----
  python setting/scripts/rehydrate_pdfs.py             # fetch every note's missing PDF
  python setting/scripts/rehydrate_pdfs.py --check     # report only; exit 1 if anything missing
  python setting/scripts/rehydrate_pdfs.py @li2026zr0 wu2026tactile-wam   # only these papers
  python setting/scripts/rehydrate_pdfs.py --force     # re-download even if the PDF is already present
  python setting/scripts/rehydrate_pdfs.py --dry-run   # show what would be downloaded, do nothing

Exit code is non-zero if any referenced PDF is still missing at the end, so it
doubles as a pre-push / new-machine check for a machine's local asset completeness.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    import requests
except ImportError:  # pragma: no cover - urllib fallback for minimal installs.
    requests = None
    import urllib.request

try:
    import fitz  # PyMuPDF; used only to validate the downloaded file opens.
except ImportError:  # pragma: no cover - validation degrades to magic-byte check.
    fitz = None

WIKI_LINK = re.compile(r"\[\[([^\]#|]+)")
ARXIV_ID = re.compile(r"^\d{4}\.\d{4,5}")
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("notes", nargs="*", help="note paths or citekeys to limit to (default: all papers/@*.md)")
    parser.add_argument("--check", action="store_true", help="report missing PDFs only; do not download")
    parser.add_argument("--dry-run", action="store_true", help="show what would be downloaded; do not fetch")
    parser.add_argument("--force", action="store_true", help="re-download even if the PDF is already present")
    parser.add_argument("--timeout", type=int, default=120, help="per-download timeout in seconds (default 120)")
    args = parser.parse_args()

    root = repo_root()
    notes = resolve_notes(root, args.notes)
    if not notes:
        print("No matching paper notes found.")
        return 0

    scanned = downloaded = 0
    unresolved: list[str] = []       # notes whose PDF is still missing after we finish
    no_source: list[str] = []        # notes with a missing PDF but no arxiv/url to fetch it

    for note in notes:
        info = parse_note(note)
        target = info.get("pdf")
        rel = note.relative_to(root)
        if not target:
            print(f"SKIP  {rel}: no `pdf:` field")
            continue
        scanned += 1
        dest = root / target
        present = dest.exists()

        if present and not args.force:
            continue

        if args.check:
            print(f"MISSING  {rel}  -> {target}")
            unresolved.append(target)
            continue

        url, kind = source_url(info)
        if not url:
            print(f"SKIP  {rel}: {target} missing but no usable `arxiv:`/`url:` source (needs manual copy)")
            no_source.append(str(rel))
            unresolved.append(target)
            continue

        why = "force" if present else "missing"
        print(f"FETCH {rel}  ({kind}: {url} -> {target}, {why})")
        if args.dry_run:
            continue

        ok, detail = download_pdf(url, dest, args.timeout)
        if ok:
            downloaded += 1
            print(f"        -> OK, {detail}")
        else:
            print(f"        -> FAILED: {detail}")
            unresolved.append(target)
        time.sleep(2)  # be polite to arXiv/GitHub between fetches (in-process sleep)

    print()
    print(f"Summary: scanned {scanned} note(s) with a pdf field; "
          f"{'would download' if args.dry_run else 'downloaded'} {downloaded}; "
          f"{len(unresolved)} referenced PDF(s) still missing.")
    if no_source:
        print("  No arxiv/url source (copy PDF manually): " + ", ".join(no_source))
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


def parse_note(note: Path) -> dict:
    text = note.read_text(encoding="utf-8", errors="ignore")
    return {
        "pdf": link_target(front_value(text, "pdf")),
        "arxiv": front_value(text, "arxiv"),
        "url": front_value(text, "url"),
    }


def front_value(text: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip('"').strip("'").strip() or None


def link_target(value: str | None) -> str | None:
    """Extract the path inside a ``[[papers/pdfs/x.pdf]]`` wiki link (or a bare path)."""
    if not value:
        return None
    m = WIKI_LINK.search(value)
    target = (m.group(1) if m else value).split("|", 1)[0].strip().strip('"').strip("'")
    return target or None


def source_url(info: dict) -> tuple[str | None, str | None]:
    """Pick a download URL from the note metadata. Prefer arXiv, then url."""
    arxiv = (info.get("arxiv") or "").strip()
    if ARXIV_ID.match(arxiv):
        base = re.sub(r"v\d+$", "", arxiv)
        return f"https://arxiv.org/pdf/{base}", "arxiv"

    url = (info.get("url") or "").strip()
    if url:
        if "arxiv.org/abs/" in url:
            return url.replace("/abs/", "/pdf/"), "arxiv-url"
        if "github.com" in url and "/blob/" in url:
            raw = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
            return raw, "github"
        if url.lower().endswith(".pdf"):
            return url, "url"
    return None, None


def download_pdf(url: str, dest: Path, timeout: int) -> tuple[bool, str]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        content = fetch_bytes(url, timeout)
    except Exception as exc:  # noqa: BLE001 - report any network/parse error verbatim
        return False, f"download error: {exc}"

    if not content or content[:5] != b"%PDF-":
        head = content[:12] if content else b""
        return False, f"not a PDF (got {len(content)}B, head={head!r}) — dead link or HTML error page?"

    # Write to a temp file next to the destination, validate, then atomically move.
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(dest.parent), suffix=".pdf.part", delete=False) as handle:
            handle.write(content)
            tmp = Path(handle.name)
        pages = None
        if fitz is not None:
            try:
                doc = fitz.open(tmp)
                pages = len(doc)
                doc.close()
            except Exception as exc:  # noqa: BLE001
                return False, f"downloaded file will not open as PDF: {exc}"
        tmp.replace(dest)
        tmp = None
        size_mb = dest.stat().st_size / 1e6
        return True, f"{size_mb:.1f} MB" + (f", {pages} pages" if pages is not None else "")
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()


def fetch_bytes(url: str, timeout: int) -> bytes:
    if requests is not None:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout, allow_redirects=True)
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}")
        return resp.content
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})  # type: ignore[name-defined]
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # type: ignore[name-defined]
        return resp.read()


if __name__ == "__main__":
    sys.exit(main())
