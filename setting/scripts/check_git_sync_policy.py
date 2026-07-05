#!/usr/bin/env python3
"""Verify that Git-tracked content stays lightweight.

Sync policy: small text notes (paper notes ``papers/@*.md`` and bilingual
reading drafts ``papers/bilingual/*.md``) may be tracked, but heavy artifacts
(PDFs under ``papers/pdfs/`` and images under ``papers/images/``) must stay
local so the repository does not balloon as papers are added.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


DEFAULT_MAX_BYTES = 1_000_000
PLACEHOLDER = ".gitkeep"
LOCAL_LIBRARY_PREFIXES = ("papers/", "institutions/", "researchers/")
# Heavy artifacts that must never be tracked (kept local to avoid repo bloat).
BLOCKED_LIBRARY_DIRS = ("papers/pdfs/", "papers/images/")
BLOCKED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg",
    ".mp4", ".mov", ".zip", ".tar", ".gz",
}
SECRET_PATTERNS = {
    "GitHub classic token": re.compile(r"ghp_[A-Za-z0-9_]{36,}"),
    "GitHub fine-grained token": re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=int(os.environ.get("MAX_SYNC_FILE_BYTES", DEFAULT_MAX_BYTES)),
        help="maximum allowed size for a tracked file",
    )
    args = parser.parse_args()

    root = repo_root()
    tracked = git_tracked_files(root)
    errors: list[str] = []

    errors.extend(check_local_library_paths(tracked))
    errors.extend(check_file_sizes(root, tracked, args.max_bytes))
    errors.extend(check_secret_patterns(root, tracked))

    if errors:
        print("Git sync policy violations:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        f"Git sync policy OK: {len(tracked)} tracked files, "
        f"max file size <= {args.max_bytes} bytes."
    )
    return 0


def repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(result.stdout.strip())


def git_tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def check_local_library_paths(paths: list[str]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        if not path.startswith(LOCAL_LIBRARY_PREFIXES):
            continue
        if Path(path).name == PLACEHOLDER:
            continue
        # Text notes are allowed; only heavy PDF/image artifacts must stay local.
        if path.startswith(BLOCKED_LIBRARY_DIRS) or Path(path).suffix.lower() in BLOCKED_EXTENSIONS:
            errors.append(f"heavy library artifact must stay local (not tracked): {path}")
    return errors


def check_file_sizes(root: Path, paths: list[str], max_bytes: int) -> list[str]:
    errors: list[str] = []
    for path in paths:
        size = (root / path).stat().st_size
        if size > max_bytes:
            errors.append(f"tracked file exceeds {max_bytes} bytes: {path} ({size} bytes)")
    return errors


def check_secret_patterns(root: Path, paths: list[str]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        file_path = root / path
        if not is_text_file(file_path):
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{label} pattern found in tracked file: {path}")
    return errors


def is_text_file(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:4096]
    except OSError:
        return False
    return b"\0" not in chunk


if __name__ == "__main__":
    sys.exit(main())
