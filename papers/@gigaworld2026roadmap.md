---
tags:
  - paper
status: unread
aliases:
  - "GigaWorld-1: A Roadmap to World Models for Robot Policy Evaluation"
year: 2026
title: "GigaWorld-1: A Roadmap to World Models for Robot Policy Evaluation"
doi: 
arxiv: 
url: "https://github.com/open-gigaai/giga-world-1/blob/main/assets/GigaWorld-1.pdf"
venue: 
openalex: 
metadata_source: github_pdf
metadata_confidence: medium
pdf: "[[papers/pdfs/gigaworld2026roadmap.pdf]]"
reading: "[[papers/bilingual/gigaworld2026roadmap_中英混读.md]]"
images: "papers/images/gigaworld2026roadmap/"
image_index: "[[papers/images/gigaworld2026roadmap/index.md]]"
authors:
  - "[[Open GigaAI]]"
institutions:
topics:
---

# GigaWorld-1: A Roadmap to World Models for Robot Policy Evaluation

- [ ] PDF:: [[papers/pdfs/gigaworld2026roadmap.pdf]]
- [ ] 元数据:: source=github_pdf, confidence=medium
- [x] 精读稿:: [[papers/bilingual/gigaworld2026roadmap_中英混读.md]]
- [ ] 地图维护:: 已加入 [[论文地图]] 快速索引后，运行 `python setting/scripts/check_paper_map.py --sync-reading-markers`
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

Technical report and open-source release around GigaWorld-1, providing training, inference, data processing, checkpoint conversion, and LoRA merge workflows for robot world models and robot policy evaluation. Note: the GitHub README names the report GigaWorld-1, while the downloaded PDF metadata currently contains the title GigaBrain-0: A World Model-Powered Vision-Language-Action Model.

## 一句话定位

GigaWorld-1 是一个围绕机器人 world model 与策略评估的技术报告和开源工程发布，重点在于把训练、推理、数据处理、checkpoint 转换、LoRA 合并和评测生态组织成可复用流程。

## 方法 / 对象

- 对象：robot world models、robot policy evaluation、WMBench/WorldModel Track 相关评测与开源模型流程。
- 方法线索：README 强调 Nano/Pro 权重、Stage-1 训练、Stage-2 DMD distillation、i2v/t2v 推理、LeRobot 风格数据处理、Qwen3-VL captions、Depth Anything V2 等工程组件。
- 元数据注意：GitHub README 标题为 `GigaWorld-1: A Roadmap to World Models for Robot Policy Evaluation`；当前 PDF metadata 中出现 `GigaBrain-0: A World Model-Powered Vision-Language-Action Model`，后续精读时需要核对 PDF 正文标题页。

## 证据

- GitHub README 显示 2026-07 已发布 technical report PDF、部分训练/推理/数据处理/模型工具、部分权重和 toy data。
- 论文/报告与项目页、Hugging Face、ModelScope、WMBench leaderboard 绑定，说明它更像“模型 + benchmark + 工具链”的发布，而不是单一算法论文。

## 局限

- 当前 metadata_confidence 设为 medium，因为 PDF 元数据和 README 标题存在不一致。
- README 中多个组件仍标记为 Beta 或 Coming Soon；报告中的实证覆盖、评测协议和与其他 world model/VLA 系统的公平比较需要精读正文后确认。

## 我的阅读笔记

- 后续优先追问：GigaWorld-1 的 policy evaluation 到底评估什么失败模式？它与 Qwen-RobotWorld、Orca、Tactile-WAM 的 world model 范式差异是什么？

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
