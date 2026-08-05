---
tags:
  - paper
status: unread
aliases:
  - "Multisensory Continual Learning: Adapting Pretrained Visuomotor Policies to Force"
year: 2026
title: "Multisensory Continual Learning: Adapting Pretrained Visuomotor Policies to Force"
doi: 
arxiv: "2606.30988"
url: "https://arxiv.org/abs/2606.30988"
venue: "arXiv preprint"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/clark2026muse.pdf]]"
reading: "[[papers/bilingual/clark2026muse_中英混读.md]]"
images: "papers/images/clark2026muse/"
image_index: "[[papers/images/clark2026muse/index.md]]"
authors:
  - "[[Jaden Clark]]"
  - "[[Changhao Wang]]"
  - "[[Yihuai Gao]]"
  - "[[Seongheon Hong]]"
  - "[[Hojung Choi]]"
  - "[[Mark Cutkosky]]"
  - "[[Yifan Hou]]"
  - "[[Shuran Song]]"
institutions:
topics:
  - multisensory learning
  - continual learning
  - force-torque sensing
  - visuomotor policy
  - world model
  - experience replay
---

# Multisensory Continual Learning: Adapting Pretrained Visuomotor Policies to Force

- [x] PDF:: [[papers/pdfs/clark2026muse.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/clark2026muse_中英混读.md]]
- [x] 地图维护:: [[论文地图]]
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

Robot manipulation often relies on sensory feedback beyond vision, particularly in contact-rich settings where force, tactile, or audio signals reveal interaction states that are not directly observable from images. However, these modalities are often hardware- and task-specific, and large-scale multisensory robot datasets remain scarce. As a result, it is impractical to pretrain policies with every sensor they may encounter. We study multisensory continual learning: adapting a pretrained robot policy to new tasks with newly introduced modalities while preserving performance under the original sensor suite. We propose MultiSensory World Model (MuSe), which incorporates limited multisensory data into pretrained vision-only policies through multi-stage fusion, multisensory future prediction, and experience replay over pretraining data. We instantiate MuSe by augmenting a pretrained vision-only policy with force-torque sensing and evaluate it on real-world manipulation tasks. Our experiments show that MuSe performs strongly on contact-rich finetuning tasks while preserving, and in some cases improving, performance on the original pretraining tasks. These results suggest that a modest multisensory dataset can improve general robot capabilities beyond the finetuning distribution. Project website: https://jadenvc.github.io/multisensory-continual-learning/

## 一句话定位

MuSe 研究 multisensory continual learning：在不要求大规模多传感器预训练的前提下，用少量 force-torque 数据把一个 vision-only visuomotor policy 扩展为力觉策略，同时通过 multi-stage fusion、future prediction 和 experience replay 保住甚至提升原任务能力。

## 方法 / 对象

- 先在 21 个任务上只用视觉与动作预训练，再用 5 个不重叠的 contact-rich tasks、434 条带 F/T 的 episodes 微调。
- early fusion 把历史图像、本体状态和 F/T 编码到共享 token sequence；late fusion adapters 让新增模态影响 video/action prediction，同时减少对原视觉表示的破坏。
- 多任务 world-model objective 包括 video、dynamics、full dynamics、policy 和 inverse modes；共同预测 future video、action 及 F/T trajectory。
- 对没有 F/T 标签的 replayed pretraining samples 遮蔽 F/T input/loss，以 experience replay 抑制 catastrophic forgetting。
- 预测的 F/T 不只作 auxiliary loss，还用于 adaptive compliance：接触或力增大时降低刚度，改善擦拭和插入。

## 证据

- Forward transfer：MuSe 在 vase wiping、peg insertion、pick-and-place 上分别为 11.5/15、13/15、7.5/10；No F/T 为 5/15、9/15、7.5/10，scratch 为 8/15、6/15、5/10。
- Backward transfer：MuSe 在原训练分布的三组任务上为 12.5/15、10/15、6.5/10，优于 pretraining-only 的 8.5/15、8/15、5.5/10；去掉 replay 后前两项崩到 0.5/15 和 2/15。
- Adaptive compliance 消融：擦花瓶从 11.5/15 降到 8/15，插 peg 从 13/15 降到 11/15，说明预测力轨迹确实参与控制而非只正则化表示。
- 与同样带 replay 和 masked F/T supervision 的 Diffusion Policy 相比，MuSe 在未见力监督的预训练任务上 F/T prediction error 为 8.42，对方为 18.27；差异指向 future-image prediction 与 late fusion 的跨模态迁移作用。
- MuSe 在原任务上没有新增对应任务数据却取得 positive backward transfer，说明少量力觉微调可能改善通用接触表征，而非仅记住五个新任务。

## 局限

- 只实例化了 force-torque modality；对 tactile array、audio、event camera 等异构频率与空间结构的模态是否成立仍未知。
- 真实评估每项仅 10 或 15 trials，存在较大方差，且部分任务采用 0.5 success credit。
- Adaptive compliance 和 policy learning 同时变化，使最终成功率收益难完全归因于 representation learning；论文虽做关闭 compliance 消融，但控制接口仍是系统组成的一部分。
- Replay 依赖保留预训练数据，若原始大规模数据不可访问、隐私受限或持续增加，存储和采样成本会成为瓶颈。

## 我的阅读笔记

MuSe 最有价值的结论不是“力觉有用”，而是新增模态可以成为旧任务的补充监督。future video prediction 提供跨任务共享的视觉动力学锚点，F/T prediction 被迫与接触导致的视觉变化对齐，因此在从未给过力标签的旧任务上也能预测接触并提升控制。

这篇适合与 [[@wu2026tactile-wam]] 和 [[@park2026tactx-learning-shared-tactile]] 对照：前两者更关注触觉/世界动作表示，MuSe 则明确把问题定义成 continual adaptation 与 backward transfer。后续最关键的问题是能否把 replay 替换为参数高效或生成式记忆，以及不同传感器是否能共用一个可扩展的 modality adapter 接口。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
