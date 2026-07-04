module.exports = async function createInstitutionFromRor(tp) {
  const query = await tp.system.prompt("机构名称 / ROR search");
  if (!query) return "";

  const data = await searchRor(tp, query);
  const results = data.items ?? data.results ?? [];
  if (results.length === 0) return `> 未在 ROR 找到 "${query}"。`;

  const choice = await tp.system.suggester(
    results.map(formatInstitutionChoice),
    results,
    false,
    "选择机构"
  );
  if (!choice) return "";

  const displayName = getDisplayName(choice) ?? query;
  const title = sanitizeTitle(displayName);
  await tp.file.rename(title);

  const aliases = getAliases(choice).filter(alias => alias !== displayName).slice(0, 10);
  const website = getLink(choice, "website");
  const wikipedia = getLink(choice, "wikipedia");
  const wikidata = getExternalId(choice, "wikidata");
  const country = getCountry(choice);
  const city = getCity(choice);

  return `---
tags:
  - institution
  - 机构
aliases:
${yamlList(aliases)}
homepage: ${yamlString(website)}
embed_url: ${yamlString(website)}
ror: ${yamlString(choice.id)}
openalex:
wikidata: ${yamlString(wikidata ? `https://www.wikidata.org/wiki/${wikidata}` : "")}
wikipedia: ${yamlString(wikipedia)}
country: ${yamlString(country)}
city: ${yamlString(city)}
type:
${yamlList(choice.types ?? [])}
established: ${choice.established ?? ""}
---

# ${displayName}

## 简介


## 相关团队 / 研究方向


\`\`\`dataviewjs
const {Research} = customJS
Research.institution(dv)
\`\`\`
`;
};

async function searchRor(tp, query) {
  try {
    return await getJson(tp, `https://api.ror.org/v2/organizations?query=${encodeURIComponent(query)}`);
  } catch (_error) {
    return await getJson(tp, `https://api.ror.org/organizations?query=${encodeURIComponent(query)}`);
  }
}

async function getJson(tp, url) {
  const request = globalThis.requestUrl ?? tp.obsidian?.requestUrl;
  if (!request) throw new Error("Obsidian requestUrl is unavailable.");
  const response = await request({ url, method: "GET", headers: { Accept: "application/json" } });
  return response.json ?? JSON.parse(response.text);
}

function formatInstitutionChoice(item) {
  const name = getDisplayName(item) ?? "unknown";
  const country = getCountry(item) ?? "-";
  const city = getCity(item) ?? "-";
  const types = (item.types ?? []).join(", ") || "-";
  return `${name} | ${city}, ${country} | ${types}`;
}

function getDisplayName(item) {
  if (item.name) return item.name;
  return (item.names ?? []).find(name => (name.types ?? []).includes("ror_display"))?.value
    ?? item.names?.[0]?.value;
}

function getAliases(item) {
  if (item.aliases) return item.aliases;
  return (item.names ?? [])
    .filter(name => (name.types ?? []).includes("alias"))
    .map(name => name.value)
    .filter(Boolean);
}

function getLink(item, type) {
  const links = Array.isArray(item.links) ? item.links : [item.links].filter(Boolean);
  const link = links.find(value => value.type === type);
  if (typeof link === "string") return link;
  return link?.value;
}

function getExternalId(item, type) {
  const external = (item.external_ids ?? []).find(value => value.type === type);
  if (!external) return "";
  if (Array.isArray(external.all)) return external.preferred ?? external.all[0];
  return external.preferred ?? String(external.all ?? "").split(/\s+/)[0];
}

function getCountry(item) {
  return item.country?.country_name
    ?? item.locations?.[0]?.geonames_details?.country_name
    ?? item.locations?.[0]?.country?.country_name;
}

function getCity(item) {
  return item.locations?.[0]?.geonames_details?.name
    ?? item.locations?.[0]?.city;
}

function sanitizeTitle(value) {
  return String(value).replace(/[\\/:*?"<>|#^[\]]/g, " ").replace(/\s+/g, " ").trim();
}

function yamlString(value) {
  return value ? JSON.stringify(String(value)) : "";
}

function yamlList(values) {
  if (!values || values.length === 0) return "";
  return values.map(value => `  - ${yamlString(value)}`).join("\n");
}
