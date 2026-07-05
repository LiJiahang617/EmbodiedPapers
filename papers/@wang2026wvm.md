---
tags:
  - paper
status: unread
aliases:
  - "World Value Models for Robotic Manipulation"
year: 2026
title: "World Value Models for Robotic Manipulation"
doi: 
arxiv: "2606.24742"
url: "https://arxiv.org/abs/2606.24742"
venue: "arXiv"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/wang2026wvm.pdf]]"
reading: "[[papers/bilingual/wang2026wvm_中英混读.md]]"
images: "papers/images/wang2026wvm/"
image_index: "[[papers/images/wang2026wvm/index.md]]"
authors:
  - "[[Zhihao Wang]]"
  - "[[Jianxiong Li]]"
  - "[[Yu Cui]]"
  - "[[Yuan Gao]]"
  - "[[Xianyuan Zhan]]"
  - "[[Junzhi Yu]]"
  - "[[Xiao Ma]]"
institutions:
topics:
---

# World Value Models for Robotic Manipulation

- [ ] PDF:: [[papers/pdfs/wang2026wvm.pdf]]
- [ ] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/wang2026wvm_中英混读.md]]
- [ ] 地图维护:: 已加入 [[论文地图]] 快速索引后，运行 `python setting/scripts/check_paper_map.py --sync-reading-markers`
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

Generalist value models play a pivotal role in scaling robotic policy learning from large-scale, mixed-quality data. Mathematically, accurate value estimation demands deep temporal understanding, requiring models to both ground the current belief using historical context and plan over future outcomes. However, most existing robotic value models are built on Vision-Language Model (VLM) backbones that are pretrained primarily on static or temporally sparse visual observations, lacking the requisite temporal modeling capabilities for value estimation. Unlike VLMs, world models naturally excel at temporal modeling and future planning, making them ideal foundations for learning generalizable value functions. Driven by this insight, we marry world models with value estimation to construct a new generalist robotic value model, World Value Model (WVM), that offers accurate task progressions to assess data quality. On standard benchmarks, WVM delivers state-of-the-art (SOTA) Value-Order Correlation (VOC) results. Complementing standard evaluation suites that contains only expert data, we further introduce Suboptimal-Value-Bench, a multi-embodiment benchmark consisting of 800 suboptimal trajectories with high-fidelity, human-labeled frame annotations. Our evaluations show that WVM maintains its SOTA performance on Suboptimal-Value-Bench, establishing its robustness in handling both expert and suboptimal data. When deployed for policy learning, WVM improves manipulation performance across various policy extraction approaches in both simulated and real-world deployment, providing robust guidance for learning from mixed-quality data.

## 一句话定位

WVM 将 world model 的时间建模和未来规划能力用于 robotic value estimation，目标是在 mixed-quality data 中给出可泛化的任务进展/价值评分。

## 方法 / 对象

- 对象：大规模 mixed-quality robot data 下的 generalist value model，尤其关注 expert 与 suboptimal trajectories 中的 frame-level/task progression 评估。
- 核心动机：现有 robotic value models 多基于 VLM backbone，而 VLM 预训练通常偏静态或稀疏时间观测，不足以支撑准确 value estimation 所需的历史 grounding 和未来 planning。
- 方法主张：把 world models 与 value estimation 结合，构建 World Value Model (WVM)，输出 task progressions 来评估数据质量。

## 证据

- 摘要声称在标准 benchmarks 上取得 SOTA Value-Order Correlation (VOC)。
- 论文还提出 Suboptimal-Value-Bench，包含 800 条 multi-embodiment suboptimal trajectories 和高质量人工 frame annotations，用来评估模型处理非专家数据的鲁棒性。
- 部署层面，摘要称 WVM 在 simulated 和 real-world deployment 中均能提升多种 policy extraction approaches 的 manipulation performance。

## 局限

- WVM 的关键 claim 依赖 VOC 是否真实反映 policy learning 中的可用进展信号，需要精读指标定义和标注协议。
- Suboptimal-Value-Bench 规模为 800 trajectories，覆盖哪些 embodiment、任务类型和失败模式会决定泛化边界。
- 将 world model 用作 value estimator 时，模型是否受预测未来偏差影响，需要看 ablation 和错误案例。

## 我的阅读笔记

- 和 STEAM/WARP-RM 构成同一主题：三者都做 progress/value/reward for data curation；WVM 的差异是以 world model temporal/future modeling 作为 value backbone。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
