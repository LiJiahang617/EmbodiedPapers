---
tags:
  - paper
status: unread
aliases:
  - "WARP-RM: A Warp-Augmented Relative Progress Reward Model for Data Curation"
year: 2026
title: "WARP-RM: A Warp-Augmented Relative Progress Reward Model for Data Curation"
doi: 
arxiv: "2606.28320"
url: "https://arxiv.org/abs/2606.28320"
venue: "arXiv"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/yu2026warp-rm.pdf]]"
reading: "[[papers/bilingual/yu2026warp-rm_中英混读.md]]"
images: "papers/images/yu2026warp-rm/"
image_index: "[[papers/images/yu2026warp-rm/index.md]]"
authors:
  - "[[Justin Yu]]"
  - "[[Andrew Goldberg]]"
  - "[[Kavish Kondap]]"
  - "[[Karim El-Refai]]"
  - "[[Ethan Ransing]]"
  - "[[Qianzhong Chen]]"
  - "[[Mac Schwager]]"
  - "[[Fred Shentu]]"
  - "[[Philipp Wu]]"
  - "[[Ken Goldberg]]"
institutions:
topics:
---

# WARP-RM: A Warp-Augmented Relative Progress Reward Model for Data Curation

- [ ] PDF:: [[papers/pdfs/yu2026warp-rm.pdf]]
- [ ] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/yu2026warp-rm_中英混读.md]]
- [ ] 地图维护:: 已加入 [[论文地图]] 快速索引后，运行 `python setting/scripts/check_paper_map.py --sync-reading-markers`
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

Scaling imitation learning requires large datasets, yet human teleoperation inevitably produces mixed-quality demonstrations containing hesitations and recoveries. Prior frame-level progress reward models supervise on absolute temporal progress proxies that suffer from label noise, or require costly human annotations to define subtask boundaries. We present WARP (Warp-Augmented Relative Progress), a novel fully self-supervised algorithm for learning dense, signed relative progress magnitudes directly from successful demonstrations. WARP generates per-frame progress targets via time-warp augmentations of demonstrations (variable playback speeds and reversals) and we train WARP-RM to predict the normalized elapsed time between input frames. Aggregating these predictions across overlapping windows yields a dense frame-level progress signal. We then introduce WARP-BC, which leverages these scalar reward estimates to upweight high-advantage action chunks during behavior cloning, where chunk-level advantage is obtained by aggregating per-frame rewards. We evaluate our approach on a physical bimanual robot system performing a long-horizon deformable object manipulation task: folding T-shirts from a random crumpled start. To evaluate policy robustness against suboptimal data, we construct training datasets of varying quality using episode length as a proxy for teleoperation sub-optimality. As the dataset is widened to admit more inefficiencies, WARP-BC maintains a 19/20 success rate compared to vanilla BC's collapse to 2/20, improving throughput by up to 18x.

## 一句话定位

WARP-RM 用 time-warp augmentation 从成功演示中自监督学习 dense relative progress reward，用于数据筛选和加权 behavior cloning。

## 方法 / 对象

- 对象：teleoperation 中含有 hesitation、recovery、mixed-quality 的 demonstration data。
- 方法：通过 variable playback speeds 和 reversals 生成 time-warp augmentations，并训练模型预测 input frames 之间的 normalized elapsed time。
- 应用：overlapping windows 聚合成 frame-level progress signal；WARP-BC 用 reward estimates 给 high-advantage action chunks 更高权重。

## 证据

- 摘要报告在真实 bimanual robot 的 long-horizon deformable object manipulation 中评估，具体任务是 folding T-shirts。
- 关键证据应包括 reward 与人工 progress 的相关性、WARP-BC 成功率、对不同 teleop 质量的鲁棒性。

## 局限

- 主要从 successful demonstrations 学 relative progress，失败轨迹和探索数据如何纳入需要看正文。
- Time-warp/reversal 假设可能不适合强接触、多阶段循环或存在必要回退的任务。

## 我的阅读笔记

- 和 STEAM 对照时重点看：WARP-RM 的 signed relative progress 是否比 STEAM 的 conservative ensemble advantage 更适合 data curation。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
