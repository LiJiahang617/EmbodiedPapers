#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L1 scan for the stop-slop-zh academic-notes profile.

Counts banned punctuation and banned words in Chinese prose only. YAML
frontmatter, markdown tables, fenced code, math blocks, image embeds and
wikilinks are structural, so they are stripped before scanning.

Rules live in .claude/skills/stop-slop-zh/references/academic-notes-profile.md.

Usage:
    python setting/scripts/check_zh_style.py papers/bilingual/foo_中英混读.md
    python setting/scripts/check_zh_style.py --since 2026-08-16   # only newer drafts
    python setting/scripts/check_zh_style.py --all                # every draft and note
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

BANNED_WORDS = [
    "说白了", "本质上", "换句话说", "不可否认",
    "综上所述", "总的来说", "总而言之", "一言以蔽之",
    "值得注意的是", "不难发现", "让我们来看看", "接下来让我们",
    "需要指出的是", "显而易见", "毋庸置疑", "众所周知",
    "随着技术的不断进步", "意味着什么", "这意味着",
    "这说明了什么", "由此可见", "毫无疑问", "可以说",
    "那么问题来了", "答案可能出乎你的意料", "你可能会问", "这就引出了一个问题",
]

BANNED_PATTERNS = [
    (r"在当今.{0,10}的时代", "在当今...的时代"),
    (r"在这个.{0,10}的时代", "在这个...的时代"),
    (r"随着.{0,12}的快速发展", "随着...的快速发展"),
    (r"在.{0,12}的大背景下", "在...的大背景下"),
    (r"首先.{0,80}其次.{0,80}最后", "首先...其次...最后"),
    (r"第一[，,].{0,80}第二[，,].{0,80}第三[，,]", "第一...第二...第三"),
    (r"一方面.{0,120}另一方面", "一方面...另一方面"),
    (r"(?<![\w])事实上", "事实上"),
    (r"(?<![\w])实际上", "实际上"),
]


def repo_root() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(out)
    except Exception:
        current = Path.cwd().resolve()
        for candidate in [current, *current.parents]:
            if (candidate / "AGENTS.md").exists():
                return candidate
        return current


def strip_structure(text: str) -> list[tuple[int, str]]:
    """Return (lineno, prose) pairs with structural markup removed."""
    lines = text.split("\n")
    out: list[tuple[int, str]] = []
    in_front = in_code = in_math = False

    for i, raw in enumerate(lines, 1):
        line = raw
        if i == 1 and line.strip() == "---":
            in_front = True
            continue
        if in_front:
            if line.strip() == "---":
                in_front = False
            continue
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.strip().startswith("$$"):
            in_math = not in_math
            continue
        if in_math:
            continue
        if line.lstrip().startswith("|"):
            continue
        if line.strip().startswith("!["):
            continue
        line = re.sub(r"\$[^$\n]+\$", " ", line)
        line = re.sub(r"`[^`\n]+`", " ", line)
        line = re.sub(r"https?://\S+", " ", line)
        line = re.sub(r"\[\[[^\]]*\]\]", " ", line)
        line = re.sub(r"^[a-zA-Z_]+::", " ", line.strip())
        out.append((i, line))
    return out


def scan(path: Path, quiet: bool = False) -> int:
    body = strip_structure(path.read_text(encoding="utf-8"))
    hits: dict[str, list[str]] = {}

    def add(kind: str, lineno: int, frag: str) -> None:
        hits.setdefault(kind, []).append(f"L{lineno}: {frag}")

    for lineno, line in body:
        for m in re.finditer("：", line):
            add("冒号", lineno, line[max(0, m.start() - 18):m.start() + 6].strip())
        for m in re.finditer("——", line):
            add("破折号", lineno, line[max(0, m.start() - 18):m.start() + 6].strip())
        for m in re.finditer("[“”]", line):
            add("中文双引号", lineno, line[max(0, m.start() - 18):m.start() + 6].strip())
        for word in BANNED_WORDS:
            if word in line:
                add(f"禁用词 {word}", lineno, line.strip()[:60])
        for pattern, label in BANNED_PATTERNS:
            if re.search(pattern, line):
                add(f"禁用式 {label}", lineno, line.strip()[:60])

    total = sum(len(v) for v in hits.values())
    if total == 0 and quiet:
        return 0
    print(f"[{'PASS' if total == 0 else 'FAIL'}] {path.name}  命中 {total}")
    for kind, items in sorted(hits.items()):
        print(f"  - {kind}: {len(items)} 处")
        for item in items[:6]:
            print(f"      {item}")
        if len(items) > 6:
            print(f"      ... 另有 {len(items) - 6} 处")
    return total


def collect_targets(root: Path, args: argparse.Namespace) -> list[Path]:
    if args.paths:
        return [Path(p) for p in args.paths]
    targets = sorted((root / "papers" / "bilingual").glob("*.md"))
    if args.all:
        targets += sorted((root / "papers").glob("@*.md"))
    return targets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", help="Markdown files to scan. Defaults to papers/bilingual/*.md.")
    parser.add_argument("--all", action="store_true", help="Also scan papers/@*.md literature notes.")
    parser.add_argument("--quiet", action="store_true", help="Only print files that fail.")
    args = parser.parse_args()

    root = repo_root()
    targets = collect_targets(root, args)
    if not targets:
        print("没有找到可扫描的文件")
        return 0

    failed = 0
    for target in targets:
        if not target.exists():
            print(f"跳过（不存在）：{target}")
            continue
        if scan(target, quiet=args.quiet) > 0:
            failed += 1

    print(f"\n扫描 {len(targets)} 个文件，{failed} 个未通过。")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
