module.exports = async function createPaperFromOpenAlex(tp) {
  const query = await tp.system.prompt("论文标题、DOI 或关键词 / OpenAlex search");
  if (!query) return "";

  const data = await getJson(tp, `https://api.openalex.org/works?search=${encodeURIComponent(query)}&per-page=8`);
  const results = (data.results ?? [])
    .sort((left, right) => (right.cited_by_count ?? 0) - (left.cited_by_count ?? 0));
  if (results.length === 0) return `> 未在 OpenAlex 找到 "${query}"。`;

  const choice = await tp.system.suggester(
    results.map(formatWorkChoice),
    results,
    false,
    "选择文献"
  );
  if (!choice) return "";

  const citeKey = await resolveCiteKey(tp, choice);
  if (!citeKey) return "> 已取消创建文献笔记。";
  await tp.file.rename(citeKey);

  const authors = unique((choice.authorships ?? []).map(item => item.author?.display_name).filter(Boolean));
  const institutions = unique(
    (choice.authorships ?? [])
      .flatMap(item => item.institutions ?? [])
      .map(item => item.display_name)
      .filter(Boolean)
  );
  const venue = choice.primary_location?.source?.display_name ?? choice.host_venue?.display_name ?? "";
  const abstract = invertAbstract(choice.abstract_inverted_index);
  const arxiv = extractArxivId(choice);
  const metadataConfidence = choice.doi || arxiv ? "high" : "medium";

  return `---
tags:
  - paper
status: unread
aliases:
  - ${yamlString(choice.title)}
year: ${choice.publication_year ?? ""}
title: ${yamlString(choice.title)}
doi: ${yamlString(choice.doi)}
arxiv: ${yamlString(arxiv)}
url: ${yamlString(choice.id)}
venue: ${yamlString(venue)}
openalex: ${yamlString(choice.id)}
metadata_source: openalex
metadata_confidence: ${metadataConfidence}
pdf:
reading:
images:
image_index:
authors:
${yamlWikiList(authors)}
institutions:
${yamlWikiList(institutions)}
topics:
${yamlList((choice.topics ?? []).slice(0, 6).map(item => item.display_name))}
---

# ${choice.title}

- [ ] PDF:: 
- [ ] 元数据:: source=openalex, confidence=${metadataConfidence}
- [ ] 精读稿:: 待整理
- [ ] 地图维护:: 在 [[论文地图]] 的快速索引中加入本篇，并运行 \`python setting/scripts/check_paper_map.py --sync-reading-markers\`
- [ ] 阅读状态:: unread

related:: 
affiliation:: ${institutions.map(value => `[[${value}]]`).join(", ")}

## Abstract

${abstract}

## 一句话定位


## 方法 / 对象


## 证据


## 局限


## 我的阅读笔记


\`\`\`dataviewjs
const {Research} = customJS
Research.topic(dv)
\`\`\`
`;
};

async function getJson(tp, url) {
  const request = globalThis.requestUrl ?? tp.obsidian?.requestUrl;
  if (!request) throw new Error("Obsidian requestUrl is unavailable.");
  const response = await request({ url, method: "GET", headers: { Accept: "application/json" } });
  return response.json ?? JSON.parse(response.text);
}

function formatWorkChoice(work) {
  const venue = work.primary_location?.source?.display_name ?? work.host_venue?.display_name ?? "-";
  return `${work.publication_year ?? "-"} | ${work.title} | ${venue} | cites ${work.cited_by_count ?? 0}`;
}

async function resolveCiteKey(tp, work) {
  let citeKey = buildCiteKey(work);
  for (let attempt = 0; attempt < 3; attempt += 1) {
    const conflict = findCiteKeyFile(tp, citeKey);
    if (!conflict) return citeKey;

    const manual = await tp.system.prompt(
      `citekey 已存在：${citeKey}\n冲突文件：${conflict.path ?? conflict.name ?? "unknown"}\n请输入新的 citekey：`,
      citeKey
    );
    if (!manual) return "";
    citeKey = normalizeCiteKey(manual);
  }
  return citeKey;
}

function findCiteKeyFile(tp, citeKey) {
  if (tp.file?.find_tfile) {
    const found = tp.file.find_tfile(citeKey) ?? tp.file.find_tfile(`${citeKey}.md`);
    if (found) return found;
  }

  const app = globalThis.app ?? tp.app;
  const linked = app?.metadataCache?.getFirstLinkpathDest?.(citeKey, "");
  if (linked) return linked;

  const files = app?.vault?.getMarkdownFiles?.() ?? [];
  return files.find(file => file.basename === citeKey) ?? null;
}

function buildCiteKey(work) {
  const firstAuthor = work.authorships?.[0]?.author?.display_name ?? "paper";
  const family = slugPart(firstAuthor.trim().split(/\s+/).at(-1) ?? "paper") || "paper";
  const year = work.publication_year ?? "yyyy";
  const titleSlug = buildTitleSlug(work.title ?? "untitled");
  return normalizeCiteKey(`@${family}${year}${titleSlug}`);
}

function buildTitleSlug(title) {
  const words = String(title)
    .toLowerCase()
    .replace(/['’]/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .split(/\s+/)
    .filter(word => word && !TITLE_STOP_WORDS.has(word) && !/^\d+$/.test(word));

  const selected = [];
  for (const word of words) {
    if (!selected.includes(word)) selected.push(word);
    if (selected.length >= 4) break;
  }

  return selected.join("-") || "paper";
}

function normalizeCiteKey(value) {
  let raw = String(value ?? "").trim().replace(/\.md$/i, "");
  if (!raw.startsWith("@")) raw = `@${raw}`;
  return raw
    .toLowerCase()
    .replace(/[\\/:*?"<>|#^[\]\s]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$|^@-/g, match => match.startsWith("@") ? "@" : "");
}

function slugPart(value) {
  return String(value ?? "")
    .toLowerCase()
    .replace(/['’]/g, "")
    .replace(/[^a-z0-9]+/g, "");
}

function extractArxivId(work) {
  const values = [
    work.ids?.arxiv,
    work.primary_location?.landing_page_url,
    work.primary_location?.pdf_url,
    ...(work.locations ?? []).flatMap(location => [location.landing_page_url, location.pdf_url]),
  ].filter(Boolean);

  for (const value of values) {
    const match = String(value).match(/(?:arxiv\.org\/(?:abs|pdf)\/)?(\d{4}\.\d{4,5})(?:v\d+)?/i);
    if (match) return match[1];
  }
  return "";
}

function invertAbstract(index) {
  if (!index) return "";
  const words = [];
  for (const [word, positions] of Object.entries(index)) {
    for (const position of positions) words[position] = word;
  }
  return words.join(" ");
}

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function yamlString(value) {
  return value ? JSON.stringify(String(value)) : "";
}

function yamlList(values) {
  if (!values || values.length === 0) return "";
  return values.map(value => `  - ${yamlString(value)}`).join("\n");
}

function yamlWikiList(values) {
  if (!values || values.length === 0) return "";
  return values.map(value => `  - "[[${String(value).replaceAll('"', '\\"')}]]"`).join("\n");
}

const TITLE_STOP_WORDS = new Set([
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
]);
