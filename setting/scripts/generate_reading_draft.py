#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate old-style bilingual full-reading drafts for local paper notes."""

from __future__ import annotations

import argparse
import collections
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
WIKI_LINK_RE = re.compile(r"\[\[([^\]#|]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]")
CAPTION_RE = re.compile(r"^(Fig\.|Figure|Table|Algorithm|Eq\.|Equation)\s*[\w.\-:]*\s*(.*)$", re.I)
READING_CHECK_RE = re.compile(r"^- \[[ xX]\] 精读稿::.*$", re.M)
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
# NUL and other C0/DEL control bytes plus U+FFFD leak in from some PDF font
# encodings; they are not matched by ``\s`` so they must be stripped explicitly,
# otherwise the generated Markdown is flagged as a binary file.
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f�]")
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
ACRONYM_STOPWORDS = {
    *SECTION_KEYWORDS,
    "PDF",
    "URL",
    "HTML",
    "HTTP",
    "HTTPS",
    "RGB",
    "IEEE",
    "ICRA",
    "RSS",
    "CVPR",
    "ICML",
    "ICLR",
    "NEURIPS",
    "APPENDIX",
    "SUPPLEMENTARY",
    "ACKNOWLEDGEMENTS",
    "ACKNOWLEDGMENTS",
}


TERM_BANK = [
    (r"\bworld model\b|\bWorld Model\b", "世界模型", "把状态转移、未来预测或环境动力学作为机器人决策的中间表示。"),
    (r"\bWorld Action Model\b|\bWAM\b", "世界动作模型", "同时预测未来状态和动作，让策略能看见动作可能造成的后果。"),
    (r"\bWorld Value Model\b|\bWVM\b", "世界价值模型", "用世界模型的时间/未来建模能力评估任务进展或数据质量。"),
    (r"\bvalue model\b", "价值模型", "给状态、轨迹片段或数据样本打分，指导数据筛选或策略学习。"),
    (r"\bVision-Language-Action\b|\bVLA\b", "视觉-语言-动作模型", "把视觉观测、语言指令和机器人动作统一到一个策略模型中。"),
    (r"\bChain-of-Thought\b|\bCoT\b|\bECoT\b", "具身思维链", "把场景理解、任务分解和动作规划显式写成训练监督或中间推理。"),
    (r"\btokenizer\b|\bTokenizer\b", "动作分词器", "把连续动作压缩或离散化成可与语言/视觉模型对齐的 token。"),
    (r"\bresidual quantization\b|\bResidual Quantization\b|\bSRQ\b", "残差量化", "用多层离散码逐步表示粗到细的动作信息。"),
    (r"\breward model\b|\bReward Model\b|\bRM\b", "奖励模型", "为轨迹或片段提供可优化的进展/质量信号。"),
    (r"\brelative progress\b|\btask progress\b", "相对进展", "判断两个时间点之间任务推进了多少。"),
    (r"\btemporal modeling\b|\btrajectory\b|\btrajectories\b", "时间/轨迹建模", "利用帧序列和历史上下文理解任务进展或未来结果。"),
    (r"\btime[- ]warp\b|\bwarp\b", "时间扭曲增强", "通过变速、反转或重排时间片段构造自监督进展标签。"),
    (r"\btactile\b|\btouch\b", "触觉/接触信号", "提供 RGB 难以看到的滑移、卡滞、接触法线和局部形变信息。"),
    (r"\btactile pollution\b", "触觉污染", "触觉 token 无约束注入时破坏视觉动力学或动作预测的失败模式。"),
    (r"\battention\b|\bAttention\b", "注意力机制", "决定视觉、触觉、动作、语言 token 之间如何相互读取信息。"),
    (r"\bspatial memory\b|\b3D spatial memory\b", "三维空间记忆", "为具身智能体保存物体、位置、地图和执行反馈。"),
    (r"\bAgentOS\b|\bagent\b", "具身智能体系统", "把语言指令、工具/技能调用、反馈和重规划组织成闭环执行。"),
    (r"\blatent\b|\blatents\b", "潜在表示", "模型内部用于压缩图像、动作、状态或未来预测的连续表示。"),
    (r"\bdiffusion\b|\bDiffusion\b", "扩散生成", "通过去噪过程生成视频、动作或未来状态。"),
    (r"\bbenchmark\b|\bBenchmark\b", "基准测试", "用统一任务、数据和指标比较模型能力。"),
    (r"\bablation\b|\bAblation\b", "消融实验", "移除或替换组件以验证每个设计是否真的贡献性能。"),
    (r"\bsuccess rate\b|\bSuccess Rate\b", "成功率", "机器人任务中最直接的结果指标，但需要结合任务难度和评估协议读。"),
]


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
    parser.add_argument("--overwrite", action="store_true", help="overwrite existing bilingual drafts")
    parser.add_argument(
        "--force",
        action="store_true",
        help="also overwrite hand-written drafts (frontmatter reading_mode); use with care",
    )
    parser.add_argument("--max-sections", type=int, default=18, help="maximum sections to expand")
    parser.add_argument(
        "--output-dir",
        default="papers/bilingual",
        help="output directory relative to the vault root",
    )
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
        result_lines = extract_result_lines(pdf_text.text)
        equation_lines = extract_equation_lines(pdf_text.text)
        output_dir = root / args.output_dir
        reading_path = output_dir / f"{note.citekey.lstrip('@')}_中英混读.md"

        if reading_path.exists():
            existing_fm = parse_frontmatter(reading_path.read_text(encoding="utf-8"))
            if "reading_mode" in existing_fm and not args.force:
                print(
                    "Skip hand-written draft (pass --force to overwrite): "
                    f"{reading_path.relative_to(root)}"
                )
                continue
            if not args.overwrite and not args.force:
                print(f"Skip existing bilingual draft: {reading_path.relative_to(root)}")
                continue

        reading_text = build_bilingual_draft(
            note=note,
            pdf_text=pdf_text,
            sections=sections,
            captions=captions,
            result_lines=result_lines,
            equation_lines=equation_lines,
            reading_path=reading_path,
            root=root,
        )
        reading_path.parent.mkdir(parents=True, exist_ok=True)
        reading_path.write_text(reading_text, encoding="utf-8")
        update_paper_note(note.path, reading_path, root)
        written += 1
        print(f"Generated bilingual draft: {reading_path.relative_to(root)}")

    print(f"Done. Generated {written} bilingual draft(s).")
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
    title = strip_quotes(fields.get("title") or first_heading(text) or citekey)
    pdf_link = clean_link(fields.get("pdf", ""))
    if not pdf_link:
        raise ValueError(f"Missing pdf field: {note_path}")
    pdf_path = root / pdf_link
    if not pdf_path.exists():
        raise FileNotFoundError(f"Missing PDF for {note_path}: {pdf_path}")

    return PaperNote(
        path=note_path,
        citekey=citekey,
        title=title,
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
        if not line or line.startswith((" ", "\t")) or ":" not in line:
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


def sanitize_pdf_text(raw: str) -> str:
    """Drop NUL/control bytes that some PDF fonts emit before any downstream use.

    ``clean_extracted_fragment`` collapses whitespace but ``\\x00`` is not a
    whitespace character, so it would otherwise survive all the way into the
    generated Markdown and mark the file as binary.
    """
    return CONTROL_CHARS_RE.sub("", raw)


def extract_pdf_text(pdf_path: Path) -> PdfText:
    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        raw = sanitize_pdf_text(page.extract_text() or "")
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
    value = clean_heading_title(value)
    if len(value) < 4 or len(value) > 120:
        return ""
    if value.startswith("[Page ") or CAPTION_RE.match(value) or re.search(r"@|https?://", value):
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


def clean_heading_title(value: str) -> str:
    value = re.sub(r"\bANDFORMULATION\b", "AND FORMULATION", value)
    value = re.sub(r"\bAND([A-Z][A-Z]{3,})\b", r"AND \1", value)
    return value


def extract_captions(text: str, limit: int = 36) -> list[str]:
    lines = [" ".join(line.strip().split()) for line in text.splitlines()]
    captions: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if CAPTION_RE.match(line):
            parts = [line]
            for extra in lines[index + 1 : index + 5]:
                if not extra or CAPTION_RE.match(extra):
                    break
                if len(extra) > 220 or looks_like_table_row(extra):
                    break
                parts.append(extra)
            captions.append(finalize_caption(tidy_caption(compact_text(" ".join(parts), 420))))
            if len(captions) >= limit:
                break
        index += 1
    return unique(captions)


def looks_like_table_row(line: str) -> bool:
    """True for grid/data rows so caption assembly stops before swallowing them."""
    tokens = line.split()
    if len(tokens) < 3:
        return False
    numeric = sum(1 for token in tokens if re.fullmatch(r"[+\-]?\d[\d.,%×xX↓↑/]*", token))
    return numeric >= 3 and numeric >= 0.4 * len(tokens)


def finalize_caption(text: str) -> str:
    """Keep only the leading title clause of a table caption.

    PDF table titles are rendered uppercase and glued in the text layer and are
    normally trailed by their numeric grid, which is noise in a reading draft.
    """
    if re.match(r"(?i)^(table|tab\.)\b", text):
        text = re.split(r"(?<=[.])\s+", text, maxsplit=1)[0]
    return text


def tidy_caption(text: str) -> str:
    """Re-insert spaces lost during PDF extraction without breaking real tokens.

    Conservative on purpose: it splits ``Figure3`` and ``450trials`` but keeps
    ``3D``/``6D`` (uppercase run) and hyphenated names such as ``GR-1`` intact.
    """
    value = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", text)        # Figure3 -> Figure 3
    value = re.sub(r"(?<=\d)(?=[a-z]{2,})", " ", value)      # 450trials -> 450 trials
    value = re.sub(r"(?<=[.,;:])(?=[A-Za-z])", " ", value)   # QUALITY.Metric -> QUALITY. Metric
    return re.sub(r"\s+", " ", value).strip()


def extract_result_lines(text: str, limit: int = 30) -> list[str]:
    patterns = re.compile(
        r"(\bSOTA\b|\bsuccess\b|\bimprov|\boutperform|\bbenchmark\b|\bablation\b|"
        r"\baccuracy\b|\bcorrelation\b|\bVOC\b|\bMSE\b|\bMAE\b|\bPSNR\b|"
        r"\b\d+(?:\.\d+)?%|\b\d+(?:,\d{3})+\b)",
        re.I,
    )
    lines = []
    for line in re.split(r"(?<=[.!?。])\s+|\n", text):
        cleaned = re.sub(r"\s+", " ", line).strip()
        if 40 <= len(cleaned) <= 360 and patterns.search(cleaned):
            lines.append(cleaned)
        if len(lines) >= limit:
            break
    return unique(lines)


def extract_equation_lines(text: str, limit: int = 16) -> list[str]:
    candidates = []
    for line in text.splitlines():
        cleaned = re.sub(r"\s+", " ", line).strip()
        if len(cleaned) < 8 or len(cleaned) > 220:
            continue
        if not is_probable_equation_line(cleaned):
            continue
        if re.search(r"[=∑∏≈→]|\\theta|\\math|pθ|L\(|arg\s*min|arg\s*max", cleaned):
            candidates.append(cleaned)
        if len(candidates) >= limit:
            break
    return unique(candidates)


def is_probable_equation_line(value: str) -> bool:
    if value.count("≤") + value.count("≥") > 0 and "=" not in value and "L(" not in value:
        return False
    if value.endswith((".", ",", ";")) and "=" not in value:
        return False
    if word_count(value) > 24 and "=" not in value:
        return False
    return bool(re.search(r"=|∑|∏|≈|→|\\theta|\\math|pθ|L\(|arg\s*min|arg\s*max", value))


def build_bilingual_draft(
    note: PaperNote,
    pdf_text: PdfText,
    sections: list[Section],
    captions: list[str],
    result_lines: list[str],
    equation_lines: list[str],
    reading_path: Path,
    root: Path,
) -> str:
    rel_pdf = note.pdf.relative_to(root).as_posix()
    rel_reading = reading_path.relative_to(root).as_posix()
    title = note.title
    terms = build_terms(note, pdf_text.text)
    selected_images = collect_image_embeds(note, root)
    intro = find_first_section(sections, "INTRODUCTION") or (sections[0] if sections else None)
    method_sections = filter_sections(sections, ("METHOD", "APPROACH", "MODEL", "ARCHITECTURE", "FORMULATION", "TRAINING", "Overview"))
    experiment_sections = filter_sections(sections, ("EXPERIMENT", "EVALUATION", "RESULT", "BENCHMARK", "Simulation", "Real-Robot"))

    return f"""---
tags:
  - bilingual-reading
  - deep-reading
source_pdf: "[[{rel_pdf}]]"
paper: "[[{note.citekey}]]"
images: "{note.images}"
image_index: "[[{note.image_index_link}]]"
created: {date.today().isoformat()}
generator: "setting/scripts/generate_reading_draft.py"
reading_standard: "fba534d bilingual full-reading"
extraction: "pypdf"
source_pages: {pdf_text.pages}
source_chars: {len(pdf_text.text)}
---

# {title}

paper:: [[{note.citekey}]]
pdf:: [[{rel_pdf}]]
images:: [[{note.image_index_link}]]
reading:: [[{rel_reading}]]

## 核心词汇速查

{format_terms_table(terms)}

## 摘要

{build_abstract_block(note)}

## 论文主线

{build_main_thread(note, intro)}

## 贡献与结论对照

{build_contribution_table(note, method_sections, experiment_sections, result_lines)}

## 结构地图

{build_structure_map(sections, captions)}

## 按原文 section 精读

{build_section_readings(sections)}

## 方法细节

{build_method_details(note, method_sections, equation_lines)}

## 实验设置、数据集、基线、指标

{build_experiment_details(experiment_sections, result_lines)}

## 主要结果、消融或对比

{build_results_block(captions, result_lines)}

## 图表、公式与表格线索

{build_artifact_block(captions, equation_lines, selected_images)}

## 主张-证据-边界矩阵

{build_claim_matrix(note, result_lines)}

## 局限与可追问点

{build_limitations(note)}

## 与当前库的连接

{build_library_connections(note)}

## 精读路线 / 为什么需要回看

1. 先读 `摘要` 和 `论文主线`，确认作者到底把哪个缺口定义为核心问题。
2. 再读 `方法细节` 和对应原文 section，检查输入、表示、训练目标、推理过程和模块依赖是否闭合。
3. 最后读 `实验设置、数据集、基线、指标` 与 `主要结果、消融或对比`，重点核对是否有真实机器人、跨任务、跨 embodiment、失败案例和 ablation。
4. 如果后续要写 related work，把 `贡献与结论对照` 和 `主张-证据-边界矩阵` 作为引用依据，不要只引用摘要结论。
"""


def build_terms(note: PaperNote, full_text: str) -> list[tuple[str, str, str]]:
    source = "\n".join([note.title, note.abstract, note.positioning, note.method, full_text[:8000]])
    terms: list[tuple[str, str, str]] = []
    seen: set[str] = set()

    for pattern, zh, role in TERM_BANK:
        match = re.search(pattern, source, re.I)
        if match:
            english = canonical_term(match.group(0))
            key = english.lower()
            if key in seen:
                continue
            seen.add(key)
            terms.append((english, zh, role))

    # Only surface acronyms that either come with an explicit in-text expansion
    # ("Full Name (ACR)") or recur often enough to be load-bearing. This keeps
    # one-off extraction noise (e.g. VOC) and glued PDF artifacts (e.g. BCFILTER)
    # out of the glossary.
    expansions = find_acronym_expansions(full_text)
    counts = collections.Counter(re.findall(r"\b[A-Z][A-Z0-9-]{2,}\b", source))
    for acronym, freq in counts.most_common():
        if len(terms) >= 14:
            break
        if not is_useful_acronym(acronym) or acronym.lower() in seen:
            continue
        expansion = expansions.get(acronym) or expansions.get(acronym.rstrip("s"))
        if expansion:
            english = f"{expansion}（{acronym}）"
            role = "论文用括号定义的专有缩写，此处已从上文完整写法还原；回看首次出现可核对精确定义。"
        elif freq >= 2 and len(acronym) <= 6:
            english = acronym
            role = "论文中多次出现的缩写，需结合首次出现位置确认完整含义和作用。"
        else:
            continue
        seen.add(acronym.lower())
        terms.append((english, "论文专有缩写", role))

    return terms[:14] or [
        ("paper-specific mechanism", "论文核心机制", "需要从方法章节确认输入、表示、训练目标和输出。"),
        ("benchmark / evaluation", "基准与评测", "需要从实验章节确认指标、数据和 baseline 是否支撑主张。"),
    ]


def find_acronym_expansions(text: str) -> dict[str, str]:
    """Map acronyms to their in-text expansion, e.g. WVM -> World Value Model.

    Only keeps a candidate when the acronym letters actually appear as the
    initials of the preceding phrase, which filters incidental parentheticals
    such as ``(Fig. 2)``.
    """
    expansions: dict[str, str] = {}
    # The separator allows any whitespace (PDF extraction often puts each word of
    # a defined phrase on its own line) so multi-line definitions like
    # "Tactile Asymmetric Attention Mechanism (TAAM)" are still recovered.
    pattern = re.compile(
        r"([A-Z][A-Za-z]+(?:[\s\-]+[A-Za-z][A-Za-z-]+){1,5})\s*\(\s*([A-Z][A-Za-z0-9-]{1,12})s?\s*\)"
    )
    for match in pattern.finditer(text):
        phrase = clean_extracted_fragment(match.group(1))
        acronym = match.group(2)
        if acronym in expansions:
            continue
        initials = "".join(word[0] for word in re.findall(r"[A-Za-z]+", phrase)).upper()
        letters = re.sub(r"[^A-Za-z]", "", acronym).upper()
        if len(letters) >= 2 and letters in initials:
            expansions[acronym] = compact_text(phrase, 60)
    return expansions


def is_useful_acronym(value: str) -> bool:
    if value.endswith("-") or value.startswith("-") or len(value) > 14:
        return False
    if value in ACRONYM_STOPWORDS or value.rstrip("S") in ACRONYM_STOPWORDS:
        return False
    if value.isdigit() or not re.search(r"[A-Z]", value):
        return False
    return True


def canonical_term(value: str) -> str:
    cleaned = clean_extracted_fragment(value)
    return cleaned if len(cleaned) > 2 else value


def format_terms_table(terms: list[tuple[str, str, str]]) -> str:
    rows = ["| English | 中文 | 在本文中的作用 |", "| --- | --- | --- |"]
    rows.extend(f"| {en} | {zh} | {role} |" for en, zh, role in terms)
    return "\n".join(rows)


def build_abstract_block(note: PaperNote) -> str:
    abstract = note.abstract or "原文摘要未从文献笔记中稳定提取，需要回到 PDF 摘要段核对。"
    positioning = note.positioning or "本文的核心定位需要结合 Introduction 与 Method 进一步确认。"
    return (
        f"{abstract}\n\n"
        f"中文解读：{positioning}\n\n"
        "这部分不是把摘要简单翻译成中文，而是先抓住作者的写作动作："
        "作者通常先指出现有方法在哪个环节失效，再提出一个机制、模型、数据集或系统，最后用 benchmark、真实机器人或 ablation 证明它确实补上了这个缺口。"
    )


def build_main_thread(note: PaperNote, intro: Section | None) -> str:
    intro_trace = build_intro_trace(intro) if intro else "未稳定识别 Introduction，需回到 PDF 开头确认问题铺垫。"
    method = note.method or "方法机制需要从 Method / Model / Architecture 章节继续细化。"
    evidence = note.evidence or "证据链需要从 Experiments / Evaluation / Results 章节继续细化。"
    return (
        "如果用一条线串起全文，可以这样读：\n\n"
        f"1. **问题入口**：{compact_text(note.positioning, 520) or '从 Introduction 回看作者如何定义失败模式、任务缺口和评价目标。'}\n"
        f"2. **方法钩子**：{compact_text(method, 680)}\n"
        f"3. **证据出口**：{compact_text(evidence, 680)}\n"
        f"4. **引言铺垫的读法**：\n{intro_trace}\n\n"
        "阅读时要盯住一个问题：作者的方法机制是否真的直接解决了引言中定义的失败模式，还是只是给同一问题换了更大的模型或更多的数据。"
    )


def build_intro_trace(intro: Section | None) -> str:
    if not intro:
        return "- 未稳定识别 Introduction。"
    points = split_key_points(intro.text, 6)
    if not points:
        return f"- {excerpt_text(intro.text, 520)}"
    lines = []
    for point, interp in interpret_points_deduped(points[:5], intro.title):
        lines.append(f"- {interp}\n  原文线索：`{compact_text(point, 180)}`")
    return "\n".join(lines)


def interpret_points_deduped(points: list[str], section_title: str) -> list[tuple[str, str]]:
    """Interpret each point, softening consecutive duplicates.

    ``interpret_point`` classifies a sentence into a handful of buckets, so a run
    of similar sentences would otherwise repeat the exact same gloss verbatim.
    """
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for point in points:
        interp = interpret_point(point, section_title)
        if interp in seen:
            interp = "（与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）"
        else:
            seen.add(interp)
        out.append((point, interp))
    return out


def build_contribution_table(
    note: PaperNote,
    method_sections: list[Section],
    experiment_sections: list[Section],
    result_lines: list[str],
) -> str:
    method_text = compact_text(note.method, 520) or compact_text(join_sections(method_sections), 520)
    experiment_text = compact_text(join_sections(experiment_sections), 520)
    result_text = compact_text(note.evidence, 520) or compact_text(" ".join(result_lines[:4]), 520)
    limitation_text = compact_text(note.limitations, 420)
    rows = [
        "| 贡献 / 结论 | 方法位置 | 证据 / 结论 |",
        "| --- | --- | --- |",
        f"| 定义核心问题 | Abstract / Introduction | {compact_text(note.positioning, 280)} |",
        f"| 提出主要方法或系统 | Method / Model / Architecture | {method_text or '需要从方法章节继续核对。'} |",
        f"| 通过实验验证主张 | Experiments / Evaluation / Results | {result_text or experiment_text or '需要从实验章节继续核对。'} |",
        f"| 暴露适用边界 | Discussion / Limitations / failure cases | {limitation_text or '需要回看作者是否承认失败案例、数据边界或部署限制。'} |",
    ]
    return "\n".join(rows)


def build_structure_map(sections: list[Section], captions: list[str]) -> str:
    rows = ["| 原文位置 | 作者在这一部分做什么 | 与全文主线的关系 | 关键图表 / 公式 |", "| --- | --- | --- | --- |"]
    for section in sections[:18]:
        related = related_artifacts(section.text, captions, limit=2)
        rows.append(
            f"| {section.title} | {section_role(section.title)} | {section_relation(section.title)} | {related or '待回看 PDF 图表'} |"
        )
    return "\n".join(rows)


def build_section_readings(sections: list[Section]) -> str:
    return "\n\n".join(build_section_block(index, section) for index, section in enumerate(sections[:18], start=1))


def build_section_block(index: int, section: Section) -> str:
    terms = section_terms(section.text)
    term_line = "、".join(terms) if terms else "本节术语需结合上下文回看。"
    captions = extract_captions(section.text, limit=5)
    caption_rows = build_artifact_rows(captions, extract_equation_lines(section.text, limit=5), section.title)
    points = split_key_points(section.text, 4)
    walkthrough = build_section_walkthrough(section, points, terms, captions)
    source_clues = build_source_clues(points, section.text)
    watch_points = build_watch_points(section, terms, captions)
    point_rows = "\n".join(
        f"| {compact_text(point, 180)} | {interp} | {section.title} | {boundary_for_point(point, section.title)} |"
        for point, interp in interpret_points_deduped(points, section.title)
    )
    if not point_rows:
        point_rows = "| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |"

    return f"""### {index}. {section.title}

#### 高层故事流

{section_role(section.title)} 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

{term_line}

#### 原文内容讲解

{walkthrough}

#### 关键原文线索

{source_clues}

#### 回看重点

{watch_points}

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
{point_rows}

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
{caption_rows}
"""


def build_section_walkthrough(
    section: Section,
    points: list[str],
    terms: list[str],
    captions: list[str],
) -> str:
    title = section.title
    lines = [
        f"这一节要按“{section_relation(title)}”来读。{section_role(title)}",
    ]

    if terms:
        lines.append(
            "术语上先抓住 "
            + "、".join(terms[:5])
            + "。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。"
        )

    if points:
        lines.append("可以把正文拆成下面几步：")
        for idx, (point, interp) in enumerate(interpret_points_deduped(points[:4], title), start=1):
            lines.append(f"{idx}. {interp}")
    else:
        lines.append("PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。")

    if captions:
        lines.append(
            "图表读法：本节出现的图题/表题应当放回对应段落看，重点确认它是在展示 architecture、data pipeline、main result 还是 ablation。"
        )

    return "\n\n".join(lines)


def build_source_clues(points: list[str], fallback_text: str) -> str:
    clues = points[:4] or split_key_points(fallback_text, 4)
    if not clues:
        return "- 未抽取到稳定原文线索。"
    return "\n".join(f"- `{compact_text(point, 220)}`" for point in clues)


def build_watch_points(section: Section, terms: list[str], captions: list[str]) -> str:
    title = section.title
    upper = title.upper()
    points: list[str] = []
    if "INTRODUCTION" in upper:
        points.append("缺口是否具体到可验证的失败模式，而不只是泛泛说现有方法不足。")
        points.append("作者给出的 motivating example 是否会在实验中被直接覆盖。")
    elif any(key in upper for key in ["METHOD", "MODEL", "APPROACH", "FORMULATION", "TRAINING", "OVERVIEW"]):
        points.append("输入、隐藏表示、训练目标和输出之间是否闭合。")
        points.append("每个新增模块是否有对应 ablation 或对照实验支撑。")
    elif any(key in upper for key in ["EXPERIMENT", "RESULT", "EVALUATION", "BENCHMARK", "SIMULATION", "REAL-ROBOT"]):
        points.append("数据集、baseline、指标和样本量是否足以支撑摘要中的强结论。")
        points.append("主结果之外是否有 failure cases、消融和真实机器人验证。")
    elif "DISCUSSION" in upper or "LIMITATION" in upper:
        points.append("作者承认的边界是否覆盖数据分布、模型规模、传感器/embodiment 和部署条件。")
    else:
        points.append("这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。")

    if terms:
        points.append(f"术语复查：{', '.join(terms[:4])} 在本节是否有明确变量、模块或实验定义。")
    if captions:
        points.append("图表复查：把图题/表题对应到正文 claim，确认图中数值或示意是否真的支撑该 claim。")
    return "\n".join(f"- {item}" for item in points)


def interpret_point(point: str, section_title: str) -> str:
    text = point.lower()
    upper_title = section_title.upper()
    if re.search(r"\b(we propose|we introduce|we present|we develop|we build)\b", text):
        return "这是本文的贡献声明：要看作者提出的是新模型、新数据、新训练目标、新评测，还是系统集成。"
    if re.search(r"\b(however|but|yet|challenge|limitation|fail|lack|insufficient|difficulty)\b", text):
        return "这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。"
    if re.search(r"\b(baseline|ablation|outperform|improve|success|sota|benchmark|evaluation|result)\b", text):
        return "这是证据线索：读的时候要核对 baseline、指标、任务覆盖和统计口径。"
    if re.search(r"\b(model|architecture|token|latent|attention|loss|training|denois|policy|reward|value)\b", text):
        return "这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。"
    if re.search(r"\b(dataset|data|trajectory|annotation|label|simulation|real[- ]robot)\b", text):
        return "这是数据或实验设置线索：重点看数据来源、标注协议、任务分布和真实部署边界。"
    if "INTRODUCTION" in upper_title:
        return "这句话在铺设论文问题入口：它帮助读者理解为什么这件事值得做。"
    if any(key in upper_title for key in ["METHOD", "MODEL", "APPROACH", "FORMULATION"]):
        return "这句话在补方法定义：它需要和公式、模块图或算法流程一起看。"
    if any(key in upper_title for key in ["EXPERIMENT", "RESULT", "EVALUATION"]):
        return "这句话在提供实验论证：它需要和表格、图和 baseline 对照读。"
    return "这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。"


def boundary_for_point(point: str, section_title: str) -> str:
    text = point.lower()
    if re.search(r"\b(improve|outperform|success|sota|state-of-the-art)\b", text):
        return "需要看提升是否来自公平 baseline、足够任务覆盖和同等数据/算力。"
    if re.search(r"\b(propose|introduce|present)\b", text):
        return "需要看新增设计是否有必要性证明，而不是只靠整体结果。"
    if re.search(r"\b(dataset|benchmark|annotation)\b", text):
        return "需要看数据分布、标注一致性和任务代表性。"
    if any(key in section_title.upper() for key in ["METHOD", "MODEL", "APPROACH"]):
        return "需要后续实验或 ablation 证明该机制不可替代。"
    return "注意是否被后续实验直接验证。"


def build_method_details(note: PaperNote, method_sections: list[Section], equation_lines: list[str]) -> str:
    method_text = note.method or compact_text(join_sections(method_sections), 1800)
    eq_block = "\n".join(f"- `{line}`" for line in equation_lines[:8]) or "- 未稳定抽取到公式；需要回看 PDF 中的数学定义。"
    return f"""方法部分要拆成四个问题读：

1. **输入是什么**：视觉、语言、动作、触觉、历史轨迹或环境状态分别如何进入模型。
2. **中间表示是什么**：token、latent、memory、value、reward、future state 或 action chunk 是否有明确语义。
3. **训练目标是什么**：监督信号来自人工标注、时间顺序、自监督、world model prediction、diffusion denoising 还是 behavior cloning。
4. **输出如何使用**：输出是 action、future video、value score、progress reward、skill graph，还是只作为下游模块的条件。

当前方法线索：

{method_text or '文献笔记中没有方法摘要，需从 Method 章节补读。'}

公式 / 数学定义线索：

{eq_block}
"""


def build_experiment_details(experiment_sections: list[Section], result_lines: list[str]) -> str:
    experiment_points = split_key_points(join_sections(experiment_sections), 8)
    experiment_text = "\n".join(
        f"- {interp} 原文线索：`{compact_text(point, 180)}`"
        for point, interp in interpret_points_deduped(experiment_points[:8], "Experiments")
    ) or "- 未稳定识别实验正文，需要回看 Experiments / Evaluation / Results 章节。"
    result_block = "\n".join(f"- {compact_text(line, 260)}" for line in result_lines[:12]) or "- 未稳定抽取到含指标的结果句，需要回看实验表格。"
    return f"""读实验时不要只看最终分数，要按 `数据集 -> baseline -> 指标 -> 主结果 -> 消融 -> 失败案例` 走。

实验正文线索：

{experiment_text}

指标 / 结果句线索：

{result_block}
"""


def build_results_block(captions: list[str], result_lines: list[str]) -> str:
    table_like = [item for item in captions if item.lower().startswith(("table", "figure", "fig."))]
    rows = ["| 证据类型 | 原文线索 | 读法 |", "| --- | --- | --- |"]
    for item in (table_like[:8] or captions[:8]):
        rows.append(f"| 图表/表格 | {compact_text(item, 260)} | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |")
    for line in result_lines[:6]:
        rows.append(f"| 结果句 | {compact_text(line, 260)} | 核对 baseline、样本量、任务覆盖和统计口径。 |")
    return "\n".join(rows)


def build_artifact_block(captions: list[str], equation_lines: list[str], selected_images: list[str]) -> str:
    caption_block = "\n".join(f"- {compact_text(item, 320)}" for item in captions[:16]) or "- 未稳定抽取到图题/表题。"
    equation_block = "\n".join(f"- `{compact_text(item, 220)}`" for item in equation_lines[:12]) or "- 未稳定抽取到公式行。"
    image_block = "\n".join(selected_images) or "- 本地图片索引当前没有可嵌入图片；需要图像级解释时可手动截图或补抽 source figures。"
    return f"""图表线索：

{caption_block}

本地精选图：

{image_block}

公式线索：

{equation_block}

这些线索不等于完整视觉理解。需要解释图中具体曲线、表格数值或失败案例时，应回到 PDF 原图或运行抽图脚本补全图片。"""


def collect_image_embeds(note: PaperNote, root: Path, limit: int = 8) -> list[str]:
    if not note.images:
        return []
    image_dir = root / note.images
    if not image_dir.exists():
        return []
    files = [
        path for path in image_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]
    files.sort(key=image_priority)
    embeds = []
    for path in files[:limit]:
        rel_path = path.relative_to(root).as_posix()
        embeds.append(f"![[{rel_path}|700]]")
    return embeds


def image_priority(path: Path) -> tuple[int, str]:
    name = path.name.lower()
    if name.startswith(("fig", "figure")):
        return (0, natural_sort_key(name))
    if any(token in name for token in ["overview", "architecture", "method", "pipeline", "result"]):
        return (1, natural_sort_key(name))
    return (2, natural_sort_key(name))


def natural_sort_key(value: str) -> str:
    return re.sub(r"\d+", lambda match: match.group(0).zfill(6), value)


def build_claim_matrix(note: PaperNote, result_lines: list[str]) -> str:
    evidence = compact_text(" ".join(result_lines[:4]) or note.evidence, 420)
    return "\n".join(
        [
            "| 主张 / 结论 | 原文证据 | 证据位置 | 解释 | 边界 / 适用条件 |",
            "| --- | --- | --- | --- | --- |",
            f"| 核心问题值得解决 | {compact_text(note.positioning, 260)} | Abstract / Introduction | 先确认作者的问题定义是否真实、具体、可检验 | 需要与 Related Work 对照，避免把已有工作重新包装成缺口 |",
            f"| 方法机制能回应问题 | {compact_text(note.method, 260)} | Method / Model | 看输入、表示、训练目标、输出是否形成闭环 | 需要 ablation 证明关键组件不可替代 |",
            f"| 实验支持有效性 | {evidence or '待回看实验表格'} | Experiments / Results | 看主结果是否覆盖任务、数据、baseline 和真实部署 | 指标可能只覆盖局部能力，不能直接外推到所有场景 |",
            f"| 方法存在边界 | {compact_text(note.limitations, 260)} | Limitations / Discussion / failure cases | 边界决定这篇论文什么时候值得引用、什么时候不能引用 | 如果作者未充分讨论，需要从失败案例和数据分布反推 |",
        ]
    )


def build_limitations(note: PaperNote) -> str:
    base = note.limitations or "- 文献笔记未记录明确局限，需要回看 Discussion、Limitations、Appendix 和失败案例。"
    return f"""{base}

额外需要追问：

- 数据是否覆盖足够多 embodiment、任务、传感器、场景和失败模式？
- Baseline 是否足够强，是否和本文方法使用了同等数据、模型规模和计算预算？
- 指标是否直接对应机器人最终成功率，还是只衡量 proxy signal？
- 真实机器人实验是否足够多，是否报告失败案例和部署约束？
"""


def build_library_connections(note: PaperNote) -> str:
    title = note.title.lower()
    if "tactile" in title or "touch" in title:
        return "- 连接触觉路线：可与 Tactile-WAM、GelSight/DTact 系列和触觉 foundation representation 论文一起读，重点比较传感器差异、触觉 token 表示和跨传感器泛化。"
    if "world" in title:
        return "- 连接世界模型路线：可与 GigaWorld-1、Qwen-RobotWorld、Orca、Fast LeWorldModel、WVM 对照，重点比较 future prediction、planning、value estimation 和 policy evaluation。"
    if "action" in title or "vla" in title or "robot" in title:
        return "- 连接 VLA/机器人策略路线：可与 ZR-0、X-Tokenizer、HoloAgent-0、STEAM/WARP-RM 对照，重点比较动作表示、推理监督、数据筛选和闭环执行。"
    return "- 可放入当前库的具身智能/机器人学习线索中，与 world model、VLA、触觉、reward/data curation 四条路线交叉比较。"


def build_artifact_rows(captions: list[str], equations: list[str], section_title: str) -> str:
    rows = []
    for item in captions[:4]:
        kind = item.split(" ", 1)[0]
        rows.append(f"| {kind} | {section_title} | {compact_text(item, 220)} | 支撑本节的方法、实验或定性解释。 |")
    for item in equations[:4]:
        rows.append(f"| Equation | {section_title} | `{compact_text(item, 180)}` | 定义变量关系、训练目标或推理过程。 |")
    return "\n".join(rows) or "| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |"


def section_terms(text: str) -> list[str]:
    terms = []
    for pattern, zh, _ in TERM_BANK:
        match = re.search(pattern, text, re.I)
        if match:
            terms.append(f"{canonical_term(match.group(0))}（{zh}）")
    return unique(terms)[:8]


def split_key_points(text: str, limit: int) -> list[str]:
    cleaned = clean_extracted_fragment(text)
    sentences = re.split(r"(?<=[.!?。])\s+", cleaned)
    points = [item for item in sentences if 50 <= len(item) <= 280]
    return points[:limit]


def find_first_section(sections: list[Section], keyword: str) -> Section | None:
    for section in sections:
        if keyword.upper() in section.title.upper():
            return section
    return None


def filter_sections(sections: list[Section], keywords: tuple[str, ...]) -> list[Section]:
    result = []
    for section in sections:
        haystack = section.title.upper()
        if any(keyword.upper() in haystack for keyword in keywords):
            result.append(section)
    return result


def join_sections(sections: list[Section]) -> str:
    return "\n\n".join(f"{section.title}\n{section.text}" for section in sections)


def section_role(title: str) -> str:
    upper = title.upper()
    if "INTRODUCTION" in upper:
        return "定义任务、指出现有方法缺口，并把读者带到本文的核心主张。"
    if "RELATED" in upper or "BACKGROUND" in upper or "PRELIMINAR" in upper:
        return "建立前人工作和技术背景，说明本文方法为什么有必要。"
    if any(key in upper for key in ["METHOD", "APPROACH", "MODEL", "ARCHITECTURE", "FORMULATION", "TRAINING", "OVERVIEW"]):
        return "给出方法机制，是判断论文贡献是否成立的主要位置。"
    if any(key in upper for key in ["EXPERIMENT", "EVALUATION", "RESULT", "BENCHMARK", "SIMULATION", "REAL-ROBOT"]):
        return "提供经验证据，需要重点核对指标、baseline、ablation 和真实部署设置。"
    if "DISCUSSION" in upper or "LIMITATION" in upper:
        return "说明适用边界、失败模式或作者对结果的解释。"
    if "CONCLUSION" in upper:
        return "收束主张，并指出方法产出和后续方向。"
    if "APPENDIX" in upper:
        return "补充实现细节、额外实验、证明或更完整的图表。"
    return "补充论文主线中的一个环节，需要结合上下文判断其论证功能。"


def section_relation(title: str) -> str:
    upper = title.upper()
    if "INTRODUCTION" in upper:
        return "回答为什么要做。"
    if any(key in upper for key in ["METHOD", "MODEL", "APPROACH", "FORMULATION", "TRAINING"]):
        return "回答怎么做。"
    if any(key in upper for key in ["EXPERIMENT", "RESULT", "EVALUATION", "BENCHMARK"]):
        return "回答是否有效。"
    if "CONCLUSION" in upper or "DISCUSSION" in upper:
        return "回答边界和意义。"
    return "为主线提供背景或细节支撑。"


def related_artifacts(section_text: str, captions: list[str], limit: int = 2) -> str:
    found = []
    for caption in captions:
        marker = caption.split(" ", 2)[:2]
        if marker and marker[0] in section_text:
            found.append(compact_text(caption, 120))
        if len(found) >= limit:
            break
    return "<br>".join(found)


def excerpt_text(text: str, limit: int) -> str:
    cleaned = clean_extracted_fragment(text)
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
    value = clean_extracted_fragment(str(text))
    if not value:
        return ""
    if len(value) <= limit:
        return value
    return value[:limit].rstrip() + "..."


def clean_extracted_fragment(text: str) -> str:
    value = CONTROL_CHARS_RE.sub("", str(text)).replace("\u00ad", "")
    replacements = [
        (r"\bW\s+AM(s?)\b", r"WAM\1"),
        (r"\bV\s+LA(s?)\b", r"VLA\1"),
        (r"\bV\s+LM(s?)\b", r"VLM\1"),
        (r"\bR\s+GB\b", r"RGB"),
        (r"\bD\s+MD\b", r"DMD"),
        (r"\bTA\s+AM\b", r"TAAM"),
        (r"\bVIDEO\s*CLEAN\b", r"VideoClean"),
    ]
    for pattern, repl in replacements:
        value = re.sub(pattern, repl, value)
    return re.sub(r"\s+", " ", value).strip()


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


def word_count(value: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+", value))


def update_paper_note(note_path: Path, reading_path: Path, root: Path) -> None:
    rel_reading = reading_path.relative_to(root).as_posix()
    text = note_path.read_text(encoding="utf-8")
    text = set_frontmatter_field(text, "reading", f'"[[{rel_reading}]]"')
    if READING_CHECK_RE.search(text):
        text = READING_CHECK_RE.sub(f"- [x] 精读稿:: [[{rel_reading}]]", text)
    else:
        text = text.replace("related::", f"- [x] 精读稿:: [[{rel_reading}]]\n\nrelated::")
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
