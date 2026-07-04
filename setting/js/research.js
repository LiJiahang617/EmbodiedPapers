class Research {
  CONFIG = {
    paperFolders: ["papers", "文献", "文献笔记", "Literature"],
    paperTags: ["paper", "文献"],
    maxPeopleInTable: 5,
    externalIframeHeight: 680,
  };

  paperPages(dv) {
    const pagesByPath = new Map();

    for (const folder of this.CONFIG.paperFolders) {
      for (const page of dv.pages(`"${folder}"`).array()) {
        pagesByPath.set(page.file.path, page);
      }
    }

    for (const tag of this.CONFIG.paperTags) {
      for (const page of dv.pages(`#${tag}`).array()) {
        pagesByPath.set(page.file.path, page);
      }
    }

    return dv
      .array(Array.from(pagesByPath.values()))
      .where(page => !this.hasTag(page, "graph-ignore"));
  }

  researcher(dv) {
    this.renderProfileSummary(dv, "researcher");
    this.renderExternalLinks(dv);
    this.renderLinkedPaperSection(dv, "参与文献");
    this.renderEmbed(dv, ["embed_url"]);
  }

  institution(dv) {
    this.renderProfileSummary(dv, "institution");
    this.renderExternalLinks(dv);
    this.renderLinkedPaperSection(dv, "相关文献");
    this.renderEmbed(dv, ["embed_url"]);
  }

  topic(dv, query = undefined) {
    const current = dv.current();
    const papers = this.paperPages(dv)
      .where(page => this.linksToCurrent(page, current, query))
      .sort(page => page.year ?? 0, "desc");

    this.renderPaperTable(dv, papers);
  }

  recentPapers(dv, days = 14) {
    const since = dv.date("now").minus({ days });
    const papers = this.paperPages(dv)
      .where(page => page.file.mtime > since)
      .sort(page => page.file.mtime, "desc");

    this.renderPaperTable(dv, papers);
  }

  missingReading(dv) {
    const papers = this.paperPages(dv)
      .where(page => !this.hasReadingLink(page))
      .sort(page => page.file.mtime, "desc");

    dv.table(
      ["Paper", "PDF", "Updated"],
      papers.map(page => [
        this.paperTitle(dv, page),
        this.formatField(page.pdf),
        this.date(page.file.mtime),
      ])
    );
  }

  metadataReview(dv) {
    const papers = this.paperPages(dv)
      .where(page => this.needsMetadataReview(page))
      .sort(page => page.file.mtime, "desc");
    const rows = papers.array ? papers.array() : Array.from(papers);

    dv.header(2, "元数据待确认");
    if (rows.length === 0) {
      dv.paragraph("所有文献笔记都有可用的元数据来源和置信度标记。");
      return;
    }

    dv.table(
      ["Paper", "Source", "Confidence", "DOI", "arXiv", "PDF", "Updated"],
      rows.map(page => [
        this.paperTitle(dv, page),
        page.metadata_source ?? "",
        page.metadata_confidence ?? "",
        page.doi ?? "",
        page.arxiv ?? "",
        this.formatField(page.pdf),
        this.date(page.file.mtime),
      ])
    );
  }

  paperMapReadingStatus(dv) {
    const content = String(dv.current()?.file?.content ?? "");
    const axes = this.parseQuickIndexAxes(content);
    const papers = this.paperPages(dv)
      .where(page => String(page.file?.name ?? "").startsWith("@"));
    const rows = papers.array ? papers.array() : Array.from(papers);
    const byName = new Map(rows.map(page => [page.file.name, page]));
    const pending = rows.filter(page => !this.hasReadingLink(page));
    const completed = rows.length - pending.length;

    dv.header(2, "精读稿覆盖");
    dv.paragraph(
      `已链接 ${completed}/${rows.length} 篇；待写 ${pending.length} 篇。快速索引中 \`⌛\` 表示待整理精读稿。`
    );

    const grouped = axes
      .map(([axis, citekeys]) => {
        const axisPending = citekeys
          .map(name => byName.get(name))
          .filter(page => page && !this.hasReadingLink(page));
        return [axis, axisPending];
      })
      .filter(([, axisPending]) => axisPending.length > 0);

    if (grouped.length > 0) {
      dv.header(3, "按线索分类的待写清单");
      for (const [axis, axisPending] of grouped) {
        dv.paragraph(`**${axis}**`);
        dv.list(
          axisPending.map(page =>
            dv.fileLink(page.file.path, false, page.aliases?.[0] ?? page.title ?? page.file.name)
          )
        );
      }
    }

    if (pending.length === 0) {
      dv.paragraph("全部文献笔记都已链接精读稿。");
      this.renderMetadataReviewSummary(dv, rows);
      return;
    }

    dv.header(3, "全部待写");
    dv.table(
      ["Paper", "Year", "PDF", "Updated"],
      pending
        .sort((left, right) => (right.year ?? 0) - (left.year ?? 0))
        .map(page => [
          this.paperTitle(dv, page),
          page.year ?? "",
          this.formatField(page.pdf),
          this.date(page.file.mtime),
        ])
    );

    this.renderMetadataReviewSummary(dv, rows);
  }

  paperMapCoverage(dv) {
    const current = dv.current();
    const linkedNames = new Set(
      this.asArray(current.file?.outlinks)
        .map(link => this.paperLinkName(link))
        .filter(value => value.startsWith("@"))
    );
    const papers = this.paperPages(dv)
      .where(page => String(page.file?.name ?? "").startsWith("@"))
      .sort(page => page.year ?? 0, "desc");
    const rows = papers.array ? papers.array() : Array.from(papers);
    const paperNames = new Set(rows.map(page => page.file.name));
    const missing = rows.filter(page => !linkedNames.has(page.file.name));
    const stale = Array.from(linkedNames)
      .filter(name => !paperNames.has(name))
      .sort();

    dv.header(2, "地图维护检查");

    if (missing.length === 0 && stale.length === 0) {
      dv.paragraph(`地图覆盖 ${rows.length}/${rows.length} 篇文献笔记。`);
      return;
    }

    dv.paragraph(`地图覆盖 ${rows.length - missing.length}/${rows.length} 篇文献笔记。`);

    if (missing.length > 0) {
      dv.header(3, "漏掉的文献");
      dv.list(missing.map(page => dv.fileLink(page.file.path, false, page.aliases?.[0] ?? page.title ?? page.file.name)));
    }

    if (stale.length > 0) {
      dv.header(3, "失效的地图链接");
      dv.list(stale);
    }
  }

  renderLinkedPaperSection(dv, heading) {
    const current = dv.current();
    const papers = this.paperPages(dv)
      .where(page => this.linksToCurrent(page, current))
      .sort(page => page.year ?? 0, "desc");

    dv.header(2, heading);
    this.renderPaperTable(dv, papers);
  }

  renderPaperTable(dv, papers) {
    const rows = papers.array ? papers.array() : Array.from(papers);

    if (rows.length === 0) {
      dv.paragraph("暂无匹配文献。");
      return;
    }

    dv.table(
      ["Paper", "Year", "Authors", "Venue", "PDF", "精读稿", "Images", "Status", "Updated"],
      rows.map(page => [
        this.paperTitle(dv, page),
        page.year ?? "",
        this.truncateList(page.authors ?? page.author),
        page.venue ?? page.container ?? page.publication ?? "",
        this.formatField(page.pdf),
        this.formatField(page.reading),
        this.formatField(page.image_index ?? page.images),
        page.status ?? "",
        this.date(page.file.mtime),
      ])
    );
  }

  paperTitle(dv, page) {
    const display = page.aliases?.[0] ?? page.alias ?? page.title ?? page.file.name;
    const prefix = this.rankBadge(page);
    return `${prefix}${dv.fileLink(page.file.path, false, display)}`;
  }

  rankBadge(page) {
    const tags = page.file?.etags ?? [];
    const tag = tags.find(value => /#?CCF\/[ABC]/i.test(String(value)));
    if (!tag) return "";

    const level = String(tag).match(/CCF\/([ABC])/i)?.[1]?.toUpperCase();
    const colors = { A: "#d9480f", B: "#e67700", C: "#2b8a3e" };
    return level
      ? `<span style="color:${colors[level]};font-weight:700;">[${level}]</span> `
      : "";
  }

  linksToCurrent(page, current, query = undefined) {
    if (query) {
      return this.linkValues(page).some(link => this.linkText(link).includes(query));
    }

    const currentPath = current.file?.path;
    const currentName = current.file?.name;
    return this.linkValues(page).some(link => {
      const value = this.linkText(link);
      return (
        link?.path === currentPath ||
        value === currentName ||
        value === `[[${currentName}]]` ||
        value.endsWith(`/${currentName}`)
      );
    });
  }

  linkValues(page) {
    const fields = [
      page.file?.outlinks,
      page.authors,
      page.author,
      page.institutions,
      page.institution,
      page.affiliation,
      page.related,
      page.topics,
    ];

    return fields.flatMap(value => this.asArray(value)).filter(Boolean);
  }

  renderProfileSummary(dv, kind) {
    const page = dv.current();
    const rows = kind === "researcher"
      ? [
          ["机构", page.last_known_institutions ?? page.affiliation],
          ["方向", page.interests],
          ["Works", page.works_count],
          ["Citations", page.cited_by_count],
          ["H-index", page.h_index],
          ["I10-index", page.i10_index],
        ]
      : [
          ["位置", [page.city, page.country].filter(Boolean).join(", ")],
          ["类型", page.type],
          ["成立", page.established],
        ];

    const visibleRows = rows
      .filter(([, value]) => this.hasValue(value))
      .map(([label, value]) => [label, this.formatField(value)]);

    if (visibleRows.length === 0) return;

    dv.header(2, "档案");
    dv.table(["字段", "内容"], visibleRows);
  }

  renderExternalLinks(dv) {
    const page = dv.current();
    const links = [
      ["Homepage", page.homepage],
      ["Google Scholar", page.scholar],
      ["OpenAlex", page.openalex],
      ["Semantic Scholar", page.semantic_scholar],
      ["ORCID", page.orcid],
      ["ROR", page.ror],
      ["Wikidata", page.wikidata],
      ["Wikipedia", page.wikipedia],
      ["Works API", page.works_api_url],
    ].filter(([, url]) => this.hasValue(url));

    if (links.length === 0) return;

    dv.header(2, "外部资料");
    dv.paragraph(links.map(([label, url]) => `[${label}](${this.firstValue(url)})`).join(" · "));
  }

  renderEmbed(dv, fields = ["embed_url"]) {
    const page = dv.current();
    const url = fields.map(field => this.firstValue(page[field])).find(Boolean);
    if (!url) return;

    dv.header(2, "外部页面");
    dv.el("iframe", "external profile", {
      attr: {
        width: "100%",
        height: String(this.CONFIG.externalIframeHeight),
        src: url,
        frameborder: "0",
      },
    });
  }

  truncateList(value) {
    const values = this.asArray(value);
    if (values.length <= this.CONFIG.maxPeopleInTable) return values;
    return [...values.slice(0, this.CONFIG.maxPeopleInTable), `+${values.length - this.CONFIG.maxPeopleInTable}`];
  }

  formatField(value) {
    if (!value) return "";
    if (Array.isArray(value)) return value.map(item => this.formatField(item));
    if (typeof value === "string" && /^https?:\/\//.test(value)) {
      return `[link](${value})`;
    }
    return value;
  }

  firstValue(value) {
    if (Array.isArray(value)) return value.find(item => this.hasValue(item));
    if (typeof value === "string") return value.trim();
    return value;
  }

  hasValue(value) {
    if (value === null || value === undefined) return false;
    if (Array.isArray(value)) return value.some(item => this.hasValue(item));
    if (typeof value === "string") return value.trim().length > 0;
    return true;
  }

  date(value) {
    if (!value) return "";
    return window.moment(value.toString()).format("YYYY-MM-DD");
  }

  hasTag(page, tagName) {
    const normalized = tagName.replace(/^#/, "");
    return (page.file?.etags ?? []).some(tag => String(tag).replace(/^#/, "") === normalized);
  }

  asArray(value) {
    if (!value) return [];
    return Array.isArray(value) ? value : [value];
  }

  linkText(link) {
    if (!link) return "";
    if (typeof link === "string") return link.replace(/^\[\[/, "").replace(/\]\]$/, "");
    return String(link.path ?? link.display ?? link);
  }

  paperLinkName(link) {
    const value = this.linkText(link)
      .replace(/#.*$/, "")
      .replace(/\.md$/, "");
    return value.split("/").at(-1) ?? "";
  }

  hasReadingLink(page) {
    return this.hasValue(page.reading);
  }

  needsMetadataReview(page) {
    const confidence = String(page.metadata_confidence ?? "").trim().toLowerCase();
    const source = String(page.metadata_source ?? "").trim().toLowerCase();
    if (!confidence || !source) return true;
    return confidence === "low";
  }

  renderMetadataReviewSummary(dv, rows) {
    const pending = rows.filter(page => this.needsMetadataReview(page));
    if (pending.length === 0) {
      return;
    }

    dv.header(3, "元数据待确认");
    dv.paragraph(
      `${pending.length} 篇文献缺少 \`metadata_source\` / \`metadata_confidence\`，或置信度为 low。`
    );
    dv.table(
      ["Paper", "Source", "Confidence", "DOI", "arXiv"],
      pending.map(page => [
        this.paperTitle(dv, page),
        page.metadata_source ?? "",
        page.metadata_confidence ?? "",
        page.doi ?? "",
        page.arxiv ?? "",
      ])
    );
  }

  parseQuickIndexAxes(content) {
    const axes = [];
    let inQuickIndex = false;

    for (const line of content.split(/\r?\n/)) {
      if (line.startsWith("## ")) {
        inQuickIndex = line.trim() === "## 快速索引";
        continue;
      }
      if (!inQuickIndex) continue;

      const match = line.match(/^- (#map\/\S+) :: (.+)$/);
      if (!match) continue;

      const citekeys = [...match[2].matchAll(/\[\[(@[^\]#|]+)/g)].map(item =>
        item[1].split("/").at(-1)
      );
      axes.push([match[1], citekeys]);
    }

    return axes;
  }
}
