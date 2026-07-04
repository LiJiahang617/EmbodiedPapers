#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate and link full reading drafts for local paper notes."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - environment check.
    PdfReader = None


FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
HEADING_RE = re.compile(r"^##+ .+$")
WIKI_LINK_RE = re.compile(r"\[\[([^\]#|]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]")
CAPTION_RE = re.compile(r"^(Fig\.|Figure|Table|Algorithm|Eq\.|Equation)\s*[\w.\-:]*\s*(.*)$", re.I)
SECTION_KEYWORDS = (
    "ABSTRACT",
    "INTRODUCTION",
    "RELATED WORK",
    "BACKGROUND",
    "PRELIMINARIES",
    "FORMULATION",
    "METHOD",
    "METHODS",
    "APPROACH",
    "MODEL",
    "ARCHITECTURE",
    "TRAINING",
    "DATA",
    "DATASET",
    "BENCHMARK",
    "EXPERIMENT",
    "EXPERIMENTS",
    "EVALUATION",
    "RESULT",
    "RESULTS",
    "DISCUSSION",
    "LIMITATION",
    "LIMITATIONS",
    "CONCLUSION",
    "CONCLUSIONS",
    "APPENDIX",
    "REFERENCES",
)


@dataclass
class PaperNote:
    path: Path
    citekey: str
    title: str
    pdf: Path
    pdf_link: str
    image_index_link: str
    images: str
    abstract: str
    positioning: str
    method: str
    evidence: str
    limitations: str
    notes: str


@dataclass
class PdfText:
    pages: int
    text: str


@dataclass
class Section:
    title: str
    text: str


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notes", nargs="*", help="paper note paths or citekeys")
    parser.add_argument("--all", action="store_true", help="generate drafts for all papers/@*.md notes")
    parser.add_argument("--overwrite", action="store_true", help="overwrite existing reading drafts")
    parser.add_argument("--max-sections", type=int, default=14, help="maximum sections to expand")
    args = parser.parse_args()

    if PdfReader is None:
        print("Missing dependency: pypdf. Install it before generating reading drafts.", file=sys.stderr)
        return 2

    root = Path(__file__).resolve().parents[2]
    note_paths = resolve_note_paths(root, args.notes, args.all)
    if not note_paths:
        print("No paper notes selected.", file=sys.stderr)
        return 2

    written = 0
    for note_path in note_paths:
        note = read_paper_note(root, note_path)
        pdf_text = extract_pdf_text(note.pdf)
        sections = detect_sections(pdf_text.text, args.max_sections)
        captions = extract_captions(pdf_text.text)
        reading_path = root / "papers" / "readings" / f"{note.citekey.lstrip('@')}_精读稿.md"

        if reading_path.exists() and not args.overwrite:
            print(f"Skip existing reading draft: {reading_path.relative_to(root)}")
            continue

        reading_text = build_reading_draft(note, pdf_text, sections, captions, reading_path, root)
        reading_path.parent.mkdir(parents=True, exist_ok=True)
        reading_path.write_text(reading_text, encoding="utf-8")
        update_paper_note(note.path, reading_path, root)
        written += 1
        print(f"Generated reading draft: {reading_path.relative_to(root)}")

    print(f"Done. Generated {written} reading draft(s).")
    return 0


def resolve_note_paths(root: Path, values: list[str], include_all: bool) -> list[Path]:
    if include_all:
        return sorted((root / "papers").glob("@*.md"))

    paths: list[Path] = []
    for value in values:
        raw = value.strip()
        if not raw:
            continue
        candidates = [
            root / raw,
            root / "papers" / raw,
            root / "papers" / f"{raw}.md",
        ]
        if not raw.startswith("@"):
            candidates.append(root / "papers" / f"@{raw}.md")
        for candidate in candidates:
            if candidate.exists():
                paths.append(candidate)
                break
        else:
            raise FileNotFoundError(f"Paper note not found: {value}")
    return paths


def read_paper_note(root: Path, note_path: Path) -> PaperNote:
    text = note_path.read_text(encoding="utf-8")
    fields = parse_frontmatter(text)
    citekey = note_path.stem
    title = fields.get("title") or first_heading(text) or citekey
    pdf_link = clean_link(fields.get("pdf", ""))
    if not pdf_link:
        raise ValueError(f"Missing pdf field: {note_path}")
    pdf_path = root / pdf_link
    if not pdf_path.exists():
        raise FileNotFoundError(f"Missing PDF for {note_path}: {pdf_path}")

    return PaperNote(
        path=note_path,
        citekey=citekey,
        title=strip_quotes(title),
        pdf=pdf_path,
        pdf_link=pdf_link,
        image_index_link=clean_link(fields.get("image_index", "")),
        images=strip_quotes(fields.get("images", "")),
        abstract=section_after(text, "Abstract"),
        positioning=section_after(text, "一句话定位"),
        method=section_after(text, "方法 / 对象"),
        evidence=section_after(text, "证据"),
        limitations=section_after(text, "局限"),
        notes=section_after(text, "我的阅读笔记"),
    )


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.search(text)
    if not match:
        return {}
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line or line.startswith(" ") or line.startswith("\t") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def clean_link(value: str) -> str:
    value = strip_quotes(value)
    wiki = WIKI_LINK_RE.search(value)
    if wiki:
        value = wiki.group(1).split("|", 1)[0].strip()
    if value.endswith(".md"):
        return value
    return value


def strip_quotes(value: str) -> str:
    return value.strip().strip('"').strip("'")


def section_after(text: str, heading: str) -> str:
    lines = text.splitlines()
    collected: list[str] = []
    in_section = False
    for line in lines:
        if line == f"## {heading}":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            collected.append(line)
    return "\n".join(collected).strip()


def extract_pdf_text(pdf_path: Path) -> PdfText:
    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        raw = page.extract_text() or ""
        pages.append(f"\n[Page {index}]\n{raw}")
    return PdfText(pages=len(reader.pages), text="\n".join(pages))


def detect_sections(text: str, max_sections: int) -> list[Section]:
    lines = text.splitlines()
    markers: list[tuple[int, str]] = []
    seen: set[str] = set()

    for index, line in enumerate(lines):
        title = normalize_heading(line)
        if not title:
            continue
        key = re.sub(r"\s+", " ", title.upper())
        if key in seen:
            continue
        seen.add(key)
        markers.append((index, title))

    if not markers:
        return [Section("全文正文线索", excerpt_text(text, 5000))]

    sections: list[Section] = []
    for pos, (start, title) in enumerate(markers):
        if title.upper().startswith("REFERENCES"):
            break
        end = markers[pos + 1][0] if pos + 1 < len(markers) else len(lines)
        body = "\n".join(lines[start + 1 : end]).strip()
        if body:
            sections.append(Section(title=title, text=body))
        if len(sections) >= max_sections:
            break
    return sections


def normalize_heading(line: str) -> str:
    value = " ".join(line.strip().split())
    if len(value) < 4 or len(value) > 120:
        return ""
    if value.startswith("[Page "):
        return ""
    if CAPTION_RE.match(value):
        return ""
    if re.search(r"@|https?://", value):
        return ""

    upper = value.upper().replace("–", "-")
    roman_match = re.match(r"^(?:[IVX]+\.?\s+)(.+)$", upper)
    if roman_match and any(roman_match.group(1).startswith(item) for item in SECTION_KEYWORDS):
        return value

    numeric_match = re.match(r"^\d+(?:\.\d+)*\.?\s+([A-Z][A-Za-z][^\n]{2,100})$", value)
    if numeric_match:
        return value

    letter_match = re.match(r"^[A-Z]\.\s+[A-Z][A-Za-z][^\n]{2,80}$", value)
    if letter_match and not value.endswith("."):
        return value

    appendix_match = re.match(r"^Appendix\s+[A-Z](?:[-–][A-Z])?\.?\s+[A-Z][A-Za-z][^\n]{2,80}$", value)
    if appendix_match and word_count(value) <= 10:
        return value

    if any(upper == item for item in SECTION_KEYWORDS):
        return value

    return ""


def extract_captions(text: str, limit: int = 24) -> list[str]:
    lines = [" ".join(line.strip().split()) for line in text.splitlines()]
    captions: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if CAPTION_RE.match(line):
            parts = [line]
            for extra in lines[index + 1 : index + 4]:
                if not extra or HEADING_RE.match(extra) or CAPTION_RE.match(extra):
                    break
                if len(extra) > 180:
                    break
                parts.append(extra)
            captions.append(" ".join(parts))
            if len(captions) >= limit:
                break
        index += 1
    return unique(captions)


def build_reading_draft(
    note: PaperNote,
    pdf_text: PdfText,
    sections: list[Section],
    captions: list[str],
    reading_path: Path,
    root: Path,
) -> str:
    rel_reading = reading_path.relative_to(root).as_posix()
    rel_pdf = note.pdf.relative_to(root).as_posix()
    title = note.title
    one_sentence = paragraph_or_fallback(
        note.positioning,
        f"本文围绕 `{title}` 展开，目标是解决摘要中提出的核心问题，并通过方法设计与实验结果支撑其主张。",
    )
    method = note.method or "- 待从正文继续细化方法模块。"
    evidence = note.evidence or "- 待从实验章节继续细化证据。"
    limitations = note.limitations or "- 待从 Discussion / Limitations 与实验边界继续确认。"
    notes = note.notes or "- 后续精读时补充个人判断。"

    nav_lines = "\n".join(
        f"- {idx}. {section.title}：{section_role(section.title)}"
        for idx, section in enumerate(sections, start=1)
    )
    claim_rows = build_claim_rows(method, evidence, limitations)
    caption_lines = "\n".join(f"- {caption}" for caption in captions[:12]) or "- 未从 PDF 文本中稳定抽取到 Figure/Table caption；需要时运行抽图或人工补图。"

    section_blocks = "\n\n".join(
        build_section_block(section, idx) for idx, section in enumerate(sections, start=1)
    )

    return f"""---
tags:
  - deep-reading
source_pdf: "[[{rel_pdf}]]"
paper: "[[{note.citekey}]]"
images: "{note.images}"
image_index: "[[{note.image_index_link}]]"
created: {date.today().isoformat()}
generator: "setting/scripts/generate_reading_draft.py"
extraction: "pypdf"
source_pages: {pdf_text.pages}
source_chars: {len(pdf_text.text)}
---

# {title} 精读稿

## 生成依据

- 文献笔记：[[{note.citekey}]]
- PDF：[[{rel_pdf}]]
- 正文抽取：pypdf，{pdf_text.pages} 页，约 {len(pdf_text.text)} 个字符
- 本稿按仓库精读标准生成：保留论文结构、公式/表格/图题线索和关键英文术语，中文解释为主。

## 一句话总结

{one_sentence}

## 论证链

研究对象 / 问题：
{block_quote(one_sentence)}

方法机制：
{method}

证据链：
{evidence}

适用边界：
{limitations}

## 主张-证据速览

{claim_rows}

## 章节导航

{nav_lines}

## 图表 / 公式线索

{caption_lines}

## 按原文 section 精读

{section_blocks}

## 主张-证据-边界矩阵

| 主张 / 结论 | 原文证据 | 证据位置 | 解释 | 边界 / 适用条件 |
| --- | --- | --- | --- | --- |
| 论文核心问题成立 | Abstract / Introduction 中给出问题动机 | 摘要、引言 | 先确认作者要解决的缺口是否真实存在 | 需要结合 Related Work 判断是否充分覆盖前人 |
| 方法设计支撑核心主张 | Method / Model / Architecture 章节给出机制 | 方法章节 | 看机制是否直接回应问题，而不是只增加模型复杂度 | 需要消融实验验证每个组件 |
| 实验支持有效性 | Experiments / Evaluation / Results 给出指标与对比 | 实验章节 | 看结果是否覆盖主任务、泛化任务和失败案例 | 注意数据规模、benchmark 设置和真实部署范围 |

## 局限与可追问点

### 作者承认或摘要暴露的局限

{limitations}

### 证据不能推出的结论

- 不能仅凭摘要或主结果断定方法在所有 robot embodiment、任务分布或真实硬件条件下都稳定有效。
- 若论文主要在特定 benchmark 上验证，需要谨慎外推到开放世界、长时程、多传感器噪声或不同 action space。
- 如果图表/公式抽取不完整，涉及具体数值、公式变量和图像细节的判断应回到 PDF 原文复核。

### 可继续追问的问题

{notes}

## 回看路线

1. 先读 `Abstract` 和 `Introduction`，确认问题定义、缺口和主张。
2. 再读方法章节，画出输入、表示、模型模块、训练目标和输出之间的因果链。
3. 最后读实验章节，优先核对主表、关键 ablation、失败案例和真实部署设置。
"""


def paragraph_or_fallback(value: str, fallback: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        return fallback
    return cleaned


def block_quote(value: str) -> str:
    lines = [line for line in value.strip().splitlines() if line.strip()]
    return "\n".join(f"> {line}" for line in lines) if lines else "> 待补充"


def build_claim_rows(method: str, evidence: str, limitations: str) -> str:
    method_one = compact_text(method, 180)
    evidence_one = compact_text(evidence, 180)
    limit_one = compact_text(limitations, 180)
    return "\n".join(
        [
            f"- 主张 1：方法机制能够回应论文核心问题。",
            f"  证据位置：Method / Model / Architecture；当前线索：{method_one}",
            f"  边界：{limit_one}",
            f"- 主张 2：实验结果支持方法相对 baseline 的收益。",
            f"  证据位置：Experiments / Evaluation / Results；当前线索：{evidence_one}",
            f"  边界：需要核对 benchmark、数据分布、真实部署和 ablation。"
        ]
    )


def build_section_block(section: Section, index: int) -> str:
    role = section_role(section.title)
    excerpt = excerpt_text(section.text, 1500)
    captions = extract_captions(section.text, limit=6)
    caption_lines = "\n".join(f"- {item}" for item in captions) or "- 本节未稳定抽取到 Figure/Table/Equation caption。"

    return f"""### {index}. {section.title}

#### 本节如何推进全文论证

{role}

#### 原文内容线索

{excerpt}

#### 关键证据 / 图表 / 公式

{caption_lines}
"""


def section_role(title: str) -> str:
    upper = title.upper()
    if "INTRODUCTION" in upper:
        return "引言负责定义任务、指出现有方法缺口，并把读者带到本文的核心主张。"
    if "RELATED" in upper or "BACKGROUND" in upper or "PRELIMINAR" in upper:
        return "这一节建立前人工作和技术背景，用来说明本文方法为什么有必要。"
    if any(key in upper for key in ["METHOD", "APPROACH", "MODEL", "ARCHITECTURE", "FORMULATION", "TRAINING"]):
        return "这一节给出方法机制，是判断论文贡献是否成立的主要位置。"
    if any(key in upper for key in ["EXPERIMENT", "EVALUATION", "RESULT", "BENCHMARK"]):
        return "这一节提供经验证据，需要重点核对指标、baseline、ablation 和真实部署设置。"
    if "DISCUSSION" in upper or "LIMITATION" in upper:
        return "这一节说明适用边界、失败模式或作者对结果的解释。"
    if "CONCLUSION" in upper:
        return "结论负责收束主张，并指出方法产出和后续方向。"
    if "APPENDIX" in upper:
        return "附录通常补充实现细节、额外实验、证明或更完整的图表。"
    return "本节补充论文主线中的一个环节，需要结合上下文判断其论证功能。"


def excerpt_text(text: str, limit: int) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return "- 未抽取到稳定正文。"
    sentences = re.split(r"(?<=[.!?。])\s+", cleaned)
    selected: list[str] = []
    total = 0
    for sentence in sentences:
        if not sentence:
            continue
        selected.append(sentence)
        total += len(sentence)
        if total >= limit:
            break
    value = " ".join(selected)
    if len(value) > limit:
        value = value[:limit].rstrip() + "..."
    return value


def compact_text(text: str, limit: int) -> str:
    value = re.sub(r"\s+", " ", text).strip()
    if not value:
        return "待补充"
    if len(value) <= limit:
        return value
    return value[:limit].rstrip() + "..."


def word_count(value: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+", value))


def unique(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result


def update_paper_note(note_path: Path, reading_path: Path, root: Path) -> None:
    rel_reading = reading_path.relative_to(root).as_posix()
    text = note_path.read_text(encoding="utf-8")
    text = set_frontmatter_field(text, "reading", f'"[[{rel_reading}]]"')
    text = re.sub(
        r"^- \[[ xX]\] 精读稿::.*$",
        f"- [x] 精读稿:: [[{rel_reading}]]",
        text,
        flags=re.M,
    )
    note_path.write_text(text, encoding="utf-8")


def set_frontmatter_field(text: str, key: str, value: str) -> str:
    match = FRONTMATTER_RE.search(text)
    if not match:
        return text
    frontmatter = match.group(1)
    pattern = re.compile(rf"^{re.escape(key)}:[ \t]*(.*)$", re.M)
    if pattern.search(frontmatter):
        frontmatter = pattern.sub(f"{key}: {value}", frontmatter)
    else:
        frontmatter = f"{frontmatter.rstrip()}\n{key}: {value}"
    return f"---\n{frontmatter}\n---{text[match.end():]}"


if __name__ == "__main__":
    sys.exit(main())
