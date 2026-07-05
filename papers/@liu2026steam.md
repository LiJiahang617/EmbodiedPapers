---
tags:
  - paper
status: unread
aliases:
  - "STEAM: Self-Supervised Temporal Ensemble Advantage Modeling for Real-World Robot Learning"
year: 2026
title: "STEAM: Self-Supervised Temporal Ensemble Advantage Modeling for Real-World Robot Learning"
doi: 
arxiv: "2606.29834"
url: "https://arxiv.org/abs/2606.29834"
venue: "arXiv"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/liu2026steam.pdf]]"
reading: "[[papers/bilingual/liu2026steam_中英混读.md]]"
images: "papers/images/liu2026steam/"
image_index: "[[papers/images/liu2026steam/index.md]]"
authors:
  - "[[Zhihao Liu]]"
  - "[[Qiuyi Gu]]"
  - "[[Yitao Wang]]"
  - "[[Dongming Qiao]]"
  - "[[Yixian Zhang]]"
  - "[[Shuaihang Chen]]"
  - "[[Liangzhi Shi]]"
  - "[[Tianxing Zhou]]"
  - "[[Zefang Huang]]"
  - "[[Kang Chen]]"
  - "[[Zhen Guo]]"
  - "[[Quanlu Zhang]]"
  - "[[Jincheng Yu]]"
  - "[[Xiaodan Liang]]"
  - "[[Guoliang Fan]]"
  - "[[Yu Wang]]"
  - "[[Feng Gao]]"
  - "[[Xinlei Chen]]"
  - "[[Chao Yu]]"
institutions:
topics:
---

# STEAM: Self-Supervised Temporal Ensemble Advantage Modeling for Real-World Robot Learning

- [ ] PDF:: [[papers/pdfs/liu2026steam.pdf]]
- [ ] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/liu2026steam_中英混读.md]]
- [ ] 地图维护:: 已加入 [[论文地图]] 快速索引后，运行 `python setting/scripts/check_paper_map.py --sync-reading-markers`
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

Real-world robot learning increasingly relies on heterogeneous data, but demonstrations and rollouts often mix useful progress with stalls, corrections, and suboptimal behavior. Effective policy learning therefore requires frame-level advantages that distinguish reliable local progress from failures and regressions. We propose Self-supervised Temporal Ensemble Advantage Modeling (STEAM), a label-free method that learns such advantages from expert demonstrations. STEAM trains an ensemble of temporal-offset predictors on frame pairs within expert trajectories, using the normalized temporal offset between two frames as a self-supervised signal. Each predictor maps a frame pair to a distribution over temporal offsets, which is converted into a scalar advantage. STEAM then takes the minimum advantage across the ensemble to score mixed-quality rollout data conservatively. Across real-world bimanual towel folding, chip checkout, cola restocking, and single-arm pick-and-place tasks, STEAM identifies stalls, failures, and recoveries. When combined with CFGRL, STEAM further improves policy success rate by 59%, 54.3%, 23% and 16.2% over baselines, respectively.

## 一句话定位

STEAM 用 self-supervised temporal ensemble advantage modeling 给真实机器人轨迹打 frame-level advantage，区分有效进展、停滞、恢复和失败。

## 方法 / 对象

- 对象：真实机器人学习中的 heterogeneous demonstrations 和 mixed-quality rollouts。
- 方法：在 expert trajectories 的 frame pairs 上训练 temporal-offset predictors，用归一化时间偏移作为自监督信号。
- Advantage 构造：每个 predictor 将 frame pair 映射为 temporal offset distribution，再转成 scalar advantage；ensemble 取 minimum 以保守评分 mixed-quality rollout data。

## 证据

- 摘要列出 real-world bimanual towel folding、chip checkout、cola restocking、single-arm pick-and-place。
- 与 CFGRL 结合后，摘要报告 policy success rate 相对 baselines 分别提升 59%、54.3%、23%、16.2%。

## 局限

- 方法依赖 expert demonstrations 中“时间前进约等于任务进展”的假设；非单调、多阶段回退或需要反复调整的任务可能更复杂。
- 取 ensemble minimum 更保守，但可能压低有效探索片段；需要看 threshold/aggregation 的敏感性。

## 我的阅读笔记

- 和 WARP-RM 很接近：二者都把时间结构转成 progress/reward 信号；STEAM 更强调 ensemble conservative advantage，WARP-RM 更强调 time-warp augmentation 和 relative progress。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
