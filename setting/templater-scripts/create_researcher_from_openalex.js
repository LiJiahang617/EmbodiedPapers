module.exports = async function createResearcherFromOpenAlex(tp) {
  const name = await tp.system.prompt("研究人员姓名 / OpenAlex search");
  if (!name) return "";

  const data = await getJson(tp, `https://api.openalex.org/authors?search=${encodeURIComponent(name)}&per-page=8`);
  const results = data.results ?? [];
  if (results.length === 0) return `> 未在 OpenAlex 找到 "${name}"。`;

  const choice = await tp.system.suggester(
    results.map(formatAuthorChoice),
    results,
    false,
    "选择研究人员"
  );
  if (!choice) return "";

  const title = sanitizeTitle(choice.display_name ?? name);
  await tp.file.rename(title);

  const institutions = unique(
    (choice.last_known_institutions ?? []).map(item => item.display_name).filter(Boolean)
  );
  const topics = unique((choice.topics ?? []).slice(0, 8).map(item => item.display_name).filter(Boolean));
  const aliases = unique([...(choice.display_name_alternatives ?? []), ...(choice.raw_author_names ?? [])])
    .filter(alias => alias && alias !== choice.display_name && looksLikeSamePerson(alias, choice.display_name))
    .slice(0, 8);

  return `---
tags:
  - researcher
aliases:
${yamlList(aliases)}
homepage:
embed_url:
scholar: "https://scholar.google.com/citations?view_op=search_authors&mauthors=${encodeURIComponent(choice.display_name ?? name)}"
openalex: ${yamlString(choice.id)}
orcid: ${yamlString(choice.orcid)}
semantic_scholar: ${yamlString(`https://www.semanticscholar.org/search?q=${encodeURIComponent(choice.display_name ?? name)}&sort=relevance`)}
wikidata:
works_api_url: ${yamlString(choice.works_api_url)}
works_count: ${choice.works_count ?? ""}
cited_by_count: ${choice.cited_by_count ?? ""}
h_index: ${choice.summary_stats?.h_index ?? ""}
i10_index: ${choice.summary_stats?.i10_index ?? ""}
last_known_institutions:
${yamlWikiList(institutions)}
interests:
${yamlList(topics)}
---

# ${choice.display_name ?? name}

affiliation:: ${institutions.map(value => `[[${value}]]`).join(", ")}
label:: 

## 简介


## 代表性工作


\`\`\`dataviewjs
const {Research} = customJS
Research.researcher(dv)
\`\`\`
`;
};

async function getJson(tp, url) {
  const request = globalThis.requestUrl ?? tp.obsidian?.requestUrl;
  if (!request) throw new Error("Obsidian requestUrl is unavailable.");
  const response = await request({ url, method: "GET", headers: { Accept: "application/json" } });
  return response.json ?? JSON.parse(response.text);
}

function formatAuthorChoice(author) {
  const institution = author.last_known_institutions?.[0]?.display_name ?? "unknown institution";
  const hIndex = author.summary_stats?.h_index ?? "-";
  return `${author.display_name} | ${institution} | works ${author.works_count ?? 0} | cites ${author.cited_by_count ?? 0} | h ${hIndex}`;
}

function sanitizeTitle(value) {
  return String(value).replace(/[\\/:*?"<>|#^[\]]/g, " ").replace(/\s+/g, " ").trim();
}

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function looksLikeSamePerson(alias, displayName) {
  const displayTokens = normalizeName(displayName);
  const aliasText = normalizeName(alias).join(" ");
  if (displayTokens.length === 0 || !aliasText) return false;

  const familyName = displayTokens.at(-1);
  if (!aliasText.includes(familyName)) return false;
  if (displayTokens.length === 1) return true;

  return displayTokens
    .slice(0, -1)
    .some(token => aliasText.includes(token) || aliasText.includes(token[0]));
}

function normalizeName(value) {
  return String(value ?? "")
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim()
    .split(/\s+/)
    .filter(Boolean);
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
