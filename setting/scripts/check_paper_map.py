#!/usr/bin/env python3
"""Check paper map coverage, structure, and reading-draft markers."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


LINK_RE = re.compile(r"\[\[([^\]#|]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]")
HEADING_RE = re.compile(r"^## (.+)$", re.MULTILINE)
QUICK_INDEX_LINE_RE = re.compile(r"^- (#map/[^\s]+) :: (.+)$")
REQUIRED_SECTIONS = {"快速索引"}
OPTIONAL_SECTIONS = {"精读稿状态"}
ALLOWED_SECTIONS = REQUIRED_SECTIONS | OPTIONAL_SECTIONS
FORBIDDEN_SECTIONS = {"研究域书架"}
READING_MARKER = "⌛"
READING_FIELD_RE = re.compile(r"^reading:[ \t]*(.*)$", re.MULTILINE)
WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--map",
        default="论文地图.md",
        help="paper map path relative to the vault root",
    )
    parser.add_argument(
        "--sync-reading-markers",
        action="store_true",
        help="sync ⌛ markers in the quick index with each paper's reading field",
    )
    parser.add_argument(
        "--list-pending",
        action="store_true",
        help="print pending reading draft paths; default output is compact",
    )
    parser.add_argument(
        "--max-pending",
        type=int,
        default=20,
        help="maximum pending paths to print with --list-pending; 0 means all",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    paper_dir = root / "papers"
    map_path = root / args.map

    if not paper_dir.exists():
        print(f"Missing paper directory: {paper_dir}", file=sys.stderr)
        return 2

    if not map_path.exists():
        print(f"Missing paper map: {map_path}", file=sys.stderr)
        return 2

    papers = {path.stem: path for path in paper_dir.glob("@*.md")}
    map_text = map_path.read_text(encoding="utf-8")
    reading_status = {
        stem: has_reading_note(path, root) for stem, path in papers.items()
    }

    if args.sync_reading_markers:
        synced_text, changed = sync_reading_markers(map_text, reading_status)
        if changed:
            map_path.write_text(synced_text, encoding="utf-8")
            map_text = synced_text
            print("Synced reading markers in paper map quick index.")

    linked = {
        normalize_link(match.group(1))
        for match in LINK_RE.finditer(map_text)
    }
    linked_papers = {name for name in linked if name.startswith("@")}

    missing = sorted(set(papers) - linked_papers)
    stale = sorted(linked_papers - set(papers))
    structure_errors = check_map_structure(map_text)
    marker_errors = check_reading_markers(map_text, reading_status)

    with_reading = sum(1 for value in reading_status.values() if value)
    without_reading = sorted(
        stem for stem, value in reading_status.items() if not value
    )

    if structure_errors:
        print("Paper map structure errors:")
        for message in structure_errors:
            print(f"  - {message}")

    if marker_errors:
        print("Reading marker errors:")
        for message in marker_errors:
            print(f"  - {message}")

    if missing:
        print("Missing from paper map:")
        for name in missing:
            print(f"  - {papers[name].relative_to(root).as_posix()}")

    if stale:
        print("Paper map links without matching papers/@*.md note:")
        for name in stale:
            print(f"  - {name}")

    print(
        f"Reading coverage: {with_reading}/{len(papers)} linked; "
        f"{len(without_reading)} pending."
    )
    if without_reading:
        if not args.list_pending:
            print("Pending reading drafts hidden; use --list-pending to print paths.")
        else:
            print("Pending reading drafts:")
            pending_limit = len(without_reading) if args.max_pending <= 0 else args.max_pending
            for name in without_reading[:pending_limit]:
                print(f"  - {papers[name].relative_to(root).as_posix()}")
            remaining = len(without_reading) - pending_limit
            if remaining > 0:
                print(f"  ... {remaining} more hidden; use --max-pending 0 to print all.")

    if structure_errors or marker_errors or missing or stale:
        return 1

    print(f"Paper map OK: {len(papers)}/{len(papers)} canonical paper notes covered.")
    return 0


def check_map_structure(map_text: str) -> list[str]:
    errors: list[str] = []
    sections = [match.group(1).strip() for match in HEADING_RE.finditer(map_text)]

    for required in REQUIRED_SECTIONS:
        if required not in sections:
            errors.append(f'missing required section "## {required}"')

    unexpected = [name for name in sections if name not in ALLOWED_SECTIONS]
    if unexpected:
        errors.append(
            "paper map contains unsupported sections; "
            f"allowed: {', '.join(sorted(ALLOWED_SECTIONS))}; "
            f"found: {', '.join(unexpected)}"
        )

    for forbidden in FORBIDDEN_SECTIONS:
        if forbidden in map_text:
            errors.append(f'forbidden section "## {forbidden}" is no longer supported')

    return errors


def check_reading_markers(map_text: str, reading_status: dict[str, bool]) -> list[str]:
    errors: list[str] = []
    quick_index = extract_quick_index_section(map_text)

    for line in quick_index.splitlines():
        if not line.strip().startswith("- #map/"):
            continue
        for citekey, display in parse_quick_index_links(line):
            if not citekey.startswith("@"):
                continue
            if citekey not in reading_status:
                continue
            marked = display_has_marker(display)
            has_reading = reading_status[citekey]
            if not has_reading and not marked:
                errors.append(
                    f"{citekey} is missing reading link; "
                    f'quick index display should start with "{READING_MARKER} "'
                )
            if has_reading and marked:
                errors.append(
                    f"{citekey} already has reading link; "
                    f'remove "{READING_MARKER} " from quick index display'
                )
    return errors


def sync_reading_markers(map_text: str, reading_status: dict[str, bool]) -> tuple[str, bool]:
    lines = map_text.splitlines()
    changed = False
    in_quick_index = False

    for index, line in enumerate(lines):
        if line.startswith("## "):
            in_quick_index = line == "## 快速索引"
            continue
        if not in_quick_index or not line.strip().startswith("- #map/"):
            continue

        new_line, line_changed = sync_quick_index_line(line, reading_status)
        if line_changed:
            lines[index] = new_line
            changed = True

    return "\n".join(lines) + ("\n" if map_text.endswith("\n") else ""), changed


def sync_quick_index_line(line: str, reading_status: dict[str, bool]) -> tuple[str, bool]:
    match = QUICK_INDEX_LINE_RE.match(line)
    if not match:
        return line, False

    axis, tail = match.group(1), match.group(2)
    changed = False

    def replace_link(link_match: re.Match[str]) -> str:
        nonlocal changed
        raw_target = link_match.group(1)
        citekey = normalize_link(raw_target)
        display = link_match.group(2)
        if not citekey.startswith("@"):
            return link_match.group(0)

        current_display = display if display is not None else citekey
        new_display = apply_marker(current_display, reading_status.get(citekey, False))
        if new_display != current_display:
            changed = True
        if display is None and new_display == citekey:
            return f"[[{raw_target}]]"
        return f"[[{raw_target}|{new_display}]]"

    new_tail = LINK_RE.sub(replace_link, tail)
    return f"- {axis} :: {new_tail}", changed


def parse_quick_index_links(line: str) -> list[tuple[str, str]]:
    match = QUICK_INDEX_LINE_RE.match(line)
    if not match:
        return []
    return [
        (normalize_link(item.group(1)), item.group(2) or normalize_link(item.group(1)))
        for item in LINK_RE.finditer(match.group(2))
    ]


def extract_quick_index_section(map_text: str) -> str:
    lines = map_text.splitlines()
    collected: list[str] = []
    in_quick_index = False

    for line in lines:
        if line.startswith("## "):
            if line == "## 快速索引":
                in_quick_index = True
                continue
            if in_quick_index:
                break
            continue
        if in_quick_index:
            collected.append(line)

    return "\n".join(collected)


def has_reading_note(paper_path: Path, root: Path) -> bool:
    text = paper_path.read_text(encoding="utf-8")
    match = READING_FIELD_RE.search(text)
    if not match:
        return False

    raw = match.group(1).strip().strip('"').strip("'")
    if not raw:
        return False

    wiki = WIKI_LINK_RE.search(raw)
    target = wiki.group(1).split("|")[0].strip() if wiki else raw
    target = target.replace("\\", "/")
    candidates = [
        root / target,
        root / f"{target}.md",
        root / "papers" / target,
        root / "papers" / f"{target}.md",
    ]
    return any(path.exists() for path in candidates)


def display_has_marker(display: str) -> bool:
    return strip_marker(display) != display


def strip_marker(display: str) -> str:
    value = display.strip()
    prefix = f"{READING_MARKER} "
    if value.startswith(prefix):
        return value[len(prefix) :]
    return value


def apply_marker(display: str, has_reading: bool) -> str:
    label = strip_marker(display)
    if has_reading:
        return label
    return f"{READING_MARKER} {label}"


def normalize_link(link: str) -> str:
    value = link.strip().replace("\\", "/")
    if value.endswith(".md"):
        value = value[:-3]
    return value.rsplit("/", 1)[-1]


if __name__ == "__main__":
    raise SystemExit(main())
