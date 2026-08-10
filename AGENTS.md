本目录是用户自己的 Obsidian 研究阅读库。细则见下文。默认只维护功能文件，不新增面向用户的说明文档，除非用户明确要求。

流程草案、访谈记录和临时决策稿默认属于本地过程材料，放在 `local-archive/` 等已忽略目录，不提交到远端；远端只同步 AGENTS、模板、脚本和必要配置。

以后在本目录内处理论文 PDF 或文献阅读稿时，遵守这些约定：

- 默认任务路由采用渐进式披露，先按用户动词判断所需上下文，不要每次重读所有模板和脚本：`入库` 只处理元数据、重复检测、文献笔记、PDF 链接和地图维护；`抽图` 只处理本地图片目录与 `index.md`；`精读` 才读取论文全文、图表、公式并生成完整精读稿；`入库并精读` 才串联两段流程；用户说`解析`、`放入库中进行解析`、`抓下来解析`时，默认等同于`入库并精读`，必须生成并回填完整中英混读精读稿。
- 用户只说“入库”时，不生成精读稿，不做 AI 逐图视觉分析；为提速优先使用 `setting/scripts/ingest_paper_pdf.py --defer-images` 保留图片索引占位，只有用户明确要求抽图、精读，或精读正文需要图表时，再运行 `setting/scripts/extract_paper_images.py`。
- 用户说“精读”时，不压缩论文阅读深度：必须读取足够完整的 PDF 正文、章节结构、公式、表格和图题；若图片索引不存在或只是延后占位，先补跑图片抽取，再把精选图片嵌入对应讲解段落。
- 生成精读稿的脚本入口是 `python setting/scripts/generate_reading_draft.py --all --overwrite` 或 `python setting/scripts/generate_reading_draft.py papers/@citekey.md --overwrite`；默认输出旧版中英双语标准的 `papers/bilingual/<stem>_中英混读.md`，并写入文献笔记 `reading` 字段。生成后必须运行 `python setting/scripts/check_paper_map.py --sync-reading-markers`，确保 `reading` 字段、精读稿文件和地图 `⌛` 标记一致。
- 元数据默认只优先使用 arXiv / OpenAlex 等结构化来源；网络不可用时可从 PDF 推断，但必须降低 `metadata_confidence` 并说明来源。只有目标路径缺失、重复文献处理、地图分类轴不明确、或会覆盖已有非空字段时，才向用户追问。
- 不联动 Zotero，不生成 Zotero URI，不依赖 Citations 插件。
- 每篇文献可以有一个本地 PDF、一个精读稿 Markdown 和一个本地图片目录；文献笔记通过 `pdf`、`reading`、`images`、`image_index` 字段链接它们。`reading` 是唯一状态源：填写有效双链且文件存在后，才算“已有精读稿”。
- 文献元数据字段保留 `arxiv`、`metadata_source`、`metadata_confidence`；自动导入或补全时必须标明来源与置信度。联网查找可用时优先 arXiv / OpenAlex 等结构化来源；仅从 PDF 文本推断出的元数据要降低置信度，不要伪装成已确认事实。
- 处理 arXiv 论文图片时，默认先尝试 arXiv source package；source 不可用、无图或解析失败时，再从 PDF 用本地工具回退抽取，保存到 `papers/images/<pdf-stem>/`，并生成 `index.md`。不要默认让 AI 逐图视觉分析，除非用户明确要求。
- 用户提到使用精读稿或解析流程时，只生成完整中英混读稿 `<stem>_中英混读.md`。不要默认生成“表达与逻辑审查”文件，也不要插入审查标注，除非用户明确要求。
- 中英混读稿要保留论文结构、公式、表格、图题和关键英文术语，中文解释为主，英文术语以 `English（中文）` 形式保留。
- 中英混读稿默认写成“完整论文讲解稿”，不是短摘要。除非用户明确要求精简，否则要逐节覆盖论文的主要 section/subsection，解释每节的目的、关键论点、方法机制、假设、证据和与全文主线的关系。
- 中英混读稿顶部必须包含 `核心词汇速查`、`摘要`、`论文主线` 和 `贡献与结论对照`；正文必须覆盖 `结构地图`、按原文 section 展开的精读、`方法细节`、`实验设置、数据集、基线、指标`、`主要结果、消融或对比`、`图表、公式与表格线索`、`主张-证据-边界矩阵`、`局限与可追问点`、`与当前库的连接`、`精读路线 / 为什么需要回看`。原论文没有的栏目可以用简短说明标记，不要凭空补造。
- `一句话总结` 可以是一句话，也可以是两句话；必须让读者快速知道作者到底想做什么：是在反驳、证明、构造、提出、测量、解释还是综述什么，以及为什么要做、产出或支持了什么方法/模型/框架/系统/结论。
- 每个原文 section 下用自然语言说明本节如何推进全文论证，并在 `关键证据 / 图表 / 公式` 中列出最关键的 Figure/Table/Equation；重点解释它支撑哪条主张、证据含义是什么、读者应注意什么边界。
- 公式要尽量保留并解释变量含义、直观含义和使用位置；表格要尽量转成 Markdown 或保留关键行列、指标和数值结论；图题和图号要保留，正文要解释重要图在证明什么。
- 精读稿不要在顶部堆叠图片索引或批量预览图；完整图片清单放在独立 `papers/images/<pdf-stem>/index.md`，正文只把精选图片嵌入到对应的设计、方法、实验或应用讲解段落中。
- 增加、删除或重命名 `papers/@*.md` 文献笔记时，必须同步维护根目录 `论文地图.md` 的 `## 快速索引`；地图只保留 `#map/... :: [[@citekey|短名]] · ...` 分类线索行，不维护「书架」或 `问题 -> 方法钩子 -> 回看理由` 长条目（这些内容写在各文献笔记里）。尚未链接精读稿的文献，在快速索引短名前保留 `⌛` 标记；可用 `python setting/scripts/check_paper_map.py --sync-reading-markers` 按 `reading` 字段自动同步。完成或新增精读稿后，更新文献笔记 `reading` 与 checklist，并运行 `python setting/scripts/check_paper_map.py`，确认地图覆盖、精读稿标记与 `reading` 字段一致。`## 精读稿状态` 由 Dataview 自动汇总，不需手写清单。
- 不替用户强行设计正文文件夹结构；脚本和模板应保持可配置、可移动。
- 功能入口：`.obsidian/` 是 Obsidian 配置，`setting/js/research.js` 是 Dataview/CustomJS 汇总逻辑，`setting/templates/template-folder/` 是 Templater 模板，`setting/templater-scripts/` 是 OpenAlex/ROR 生成脚本，`setting/scripts/` 是本地批处理脚本。

Git 同步策略：

- 默认只提交仓库级配置、模板、脚本、校验逻辑和空目录占位。
- 同步策略只区分「体积」：小体积文本笔记进 Git——文献笔记 `papers/@*.md`、中英混读精读稿 `papers/bilingual/*.md`、`论文地图.md`、`setting/` 配置、`AGENTS.md`；大文件保持本地化不入库——PDF `papers/pdfs/`、图片 `papers/images/`。笔记里指向 PDF/图片的链接在远端仅作占位。规则由 `.gitignore` 落地，并用 `python setting/scripts/check_git_sync_policy.py` 校验（同时扫描 GitHub token 等密钥，防误提交）。
- 图片不入库意味着全新 clone / 换机器后本地会缺图，精读稿里的图片嵌入会显示为坏链。用 `python setting/scripts/rehydrate_images.py` 按各笔记 `arxiv` 字段从 arXiv source 确定性重抽补齐；抽取沿用 source 原始文件名，能精确复现精读稿引用的图名。`--check` 只报告缺图并以非零码退出（可作换机 / 提交前校验），`--force` / `--clean` 强制重建，无 `arxiv` 字段的论文需手动拷贝图片。
- 同理，PDF（`papers/pdfs/`）不入库意味着换机器 / 全新 clone 后本地会缺原文，笔记 `pdf::` 链接指向空文件。用 `python setting/scripts/rehydrate_pdfs.py` 按各笔记 `arxiv`（优先）或 `url`（支持 GitHub `/blob/`→raw、arXiv `/abs/`→`/pdf/`、直链 `.pdf`）确定性重下到 `pdf::` 期望的文件名；`--check` 只报缺失并以非零码退出（可作换机 / 提交前校验），`--force` 强制重下，无 `arxiv`/`url` 来源的论文需手动拷贝。
- `.obsidian/workspace*.json` 属于个人窗口布局和最近文件状态，不提交。
- `.obsidian/plugins/*/main.js`、`styles.css` 和主题 CSS 属于可重新安装的插件/主题载荷，不提交；Git 只保留插件启用列表、manifest 和 data 配置。
- 若确实需要同步少量精选笔记，先显式调整 `.gitignore`，不要直接用 `git add -f papers/...` 绕过策略。
- 提交前可运行 `python setting/scripts/check_git_sync_policy.py`，检查是否误追踪论文内容、大文件或 GitHub token 形态的密钥。
