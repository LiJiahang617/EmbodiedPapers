---
tags:
  - paper
status: unread
aliases:
  - "Tactile-WAM: Touch-Aware World Action Model with Tactile Asymmetric Attention"
year: 2026
title: "Tactile-WAM: Touch-Aware World Action Model with Tactile Asymmetric Attention"
doi: 
arxiv: "2606.26663"
url: "https://arxiv.org/abs/2606.26663"
venue: "arXiv"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/wu2026tactile-wam.pdf]]"
reading: "[[papers/bilingual/wu2026tactile-wam_中英混读.md]]"
images: "papers/images/wu2026tactile-wam/"
image_index: "[[papers/images/wu2026tactile-wam/index.md]]"
authors:
  - "[[Siyu Wu]]"
  - "[[Linjing You]]"
  - "[[Junjie Zhu]]"
  - "[[Yaozu Liu]]"
  - "[[Changhao Zhang]]"
  - "[[Jian Liu]]"
  - "[[Weiqiang Wang]]"
  - "[[Qi Li]]"
  - "[[Jituo Li]]"
  - "[[Hengshuang Zhao]]"
institutions:
topics:
---

# Tactile-WAM: Touch-Aware World Action Model with Tactile Asymmetric Attention

- [ ] PDF:: [[papers/pdfs/wu2026tactile-wam.pdf]]
- [ ] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/wu2026tactile-wam_中英混读.md]]
- [ ] 地图维护:: 已加入 [[论文地图]] 快速索引后，运行 `python setting/scripts/check_paper_map.py --sync-reading-markers`
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

World Action Models (WAMs) generate actions together with predicted futures, offering a powerful interface for robot decision making. In contact-rich manipulation, however, visually plausible futures can be physically incomplete: insertion, assembly, search, and reorientation often depend on slip, jamming, contact normals, or small alignment errors that are weakly visible or hidden in RGB. A natural solution is to predict future tactile states, however, we identify tactile pollution, a failure mode where unconstrained tactile-token injection degrades video and action prediction by forcing a visual dynamics model to absorb sparse, local, event-driven contact signals. To address this, we propose Tactile-WAM, a touch-aware WAM with a Tactile Asymmetric Attention Mechanism (TAAM). TAAM combines a VideoClean mask, which blocks video-query access to tactile key/value tokens while preserving action-query access, with a touch-aware bias for action attention. The VideoClean mask protects visual prediction while keeping contact information available for action generation; the touch-aware bias is derived from predicted touch changes and modulates action attention to tactile tokens during denoising. On ManiFeel, Tactile-WAM improves the mean success rate by 38.9% overall and by 86% on contact-rich tasks.

## 一句话定位

Tactile-WAM 把 tactile prediction 接入 World Action Model，以解决接触丰富操作中“视觉未来看起来合理但物理接触状态不完整”的问题。

## 方法 / 对象

- 对象：insertion、assembly、search、reorientation 等依赖 slip、jamming、contact normals 或微小对齐误差的 contact-rich manipulation。
- 关键问题：直接注入 tactile tokens 会造成 tactile pollution，让视觉动力学模型被稀疏、局部、事件驱动的接触信号污染。
- 方法：Tactile Asymmetric Attention Mechanism (TAAM)，包含 VideoClean mask 和 touch-aware bias。
- VideoClean mask 阻止 video-query 访问 tactile key/value tokens，但保留 action-query 对触觉信息的访问；touch-aware bias 根据 predicted touch changes 调制 denoising 过程中的 action attention。

## 证据

- 摘要报告在 ManiFeel 上整体 mean success rate 提升 38.9%，在 contact-rich tasks 上提升 86%。
- 关键实验应看 tactile prediction、video/action prediction 是否分别提升，以及 TAAM 两个组件的 ablation。

## 局限

- 触觉传感器类型、触觉 token 构造方式和 ManiFeel 任务覆盖会决定泛化边界。
- 方法依赖未来触觉状态预测；如果触觉信号噪声大或接触事件稀少，touch-aware bias 的稳定性需要验证。

## 我的阅读笔记

- 可与 Qwen-RobotWorld/Orca 对照：它不是追求通用 world model，而是专门修补 RGB world/action model 在接触物理上的盲区。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
