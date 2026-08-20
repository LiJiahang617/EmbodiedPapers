# Claude Code 入口

**规则以本目录的 `AGENTS.md` 为准，动手前先完整读一遍。** 本文件只做三件事，指路、说环境、说新机器怎么起步，不复述规则，避免两份文档各改各的。

Codex 原生读 `AGENTS.md`，Claude Code 原生读本文件，两边指向同一份规则。

## 写中文内容必须过 skill

本库随附 `.claude/skills/stop-slop-zh/`，在仓库根目录打开 Claude Code 时会被自动发现。精读稿、文献笔记正文、`map_brief` / `map_role` 以及给用户的汇报文字，都要按它的规则写。

学术场景的分层裁决在 `.claude/skills/stop-slop-zh/references/academic-notes-profile.md`，一句话概括是骨架听 `AGENTS.md`、中文散文听 skill。

交付前跑一遍机器质检，命中不为 0 就返工。

```bash
python setting/scripts/check_zh_style.py papers/bilingual/<新稿>_中英混读.md
```

## 环境

`setting/scripts/` 下的脚本需要 Python 3.9 以上，依赖见 `setting/scripts/requirements.txt`。关键依赖是 PyMuPDF，缺了它入库和抽图脚本会静默产不出元数据和图片，所以动手前先验一下。

```bash
python -c "import fitz, requests; print('ok', fitz.__doc__)"
```

不要把解释器路径写死进任何文件。各机器的 Python 位置不同，用当前环境里能通过上面这条检测的那个。

## 新设备第一次使用

仓库只同步文本，PDF 和图片按策略留在本地，所以 clone 之后要补一次。

```bash
git clone https://github.com/LiJiahang617/EmbodiedPapers.git
cd EmbodiedPapers
pip install -r setting/scripts/requirements.txt

python setting/scripts/rehydrate_pdfs.py      # 按各笔记 arxiv / url 重下原文
python setting/scripts/rehydrate_images.py    # 按 arxiv source 重抽图片
python setting/scripts/check_paper_map.py     # 校验地图覆盖与 reading 字段
python setting/scripts/check_git_sync_policy.py
```

两个 rehydrate 脚本都靠 `arxiv` 字段工作，没有 arXiv 号的文献覆盖不到，需要按各自 `papers/images/<citekey>/index.md` 里的说明手动补。目前已知的例外是 [[@dyna2026dyna2]]，它是网页技术报告。

在仓库根目录打开 Claude Code，不要在外面再套一层目录，否则 `.claude/skills/` 不会被发现。
