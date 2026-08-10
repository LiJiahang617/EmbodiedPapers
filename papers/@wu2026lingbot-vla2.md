---
tags:
  - paper
status: unread
aliases:
  - "From Foundation to Application: Improving VLA Models in Practice"
year: 2026
title: "From Foundation to Application: Improving VLA Models in Practice"
doi: 
arxiv: "2607.06403"
url: "https://arxiv.org/abs/2607.06403"
venue: 
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/wu2026lingbot-vla2.pdf]]"
reading: "[[papers/bilingual/wu2026lingbot-vla2_中英混读.md]]"
images: "papers/images/wu2026lingbot-vla2/"
image_index: "[[papers/images/wu2026lingbot-vla2/index.md]]"
authors:
  - "[[Wei Wu]]"
  - "[[Fangjing Wang]]"
  - "[[Fan Lu]]"
  - "[[He Sun]]"
  - "[[Shi Liu]]"
  - "[[Yunnan Wang]]"
  - "[[Yibin Yan]]"
  - "[[Yong Wang]]"
  - "[[Shuailei Ma]]"
  - "[[Xinyang Wang]]"
  - "[[Yibin Liu]]"
  - "[[Shuai Yang]]"
  - "[[Tianxiang Zhou]]"
  - "[[Kejia Zhang]]"
  - "[[Lei Zhou]]"
  - "[[Cheng Su]]"
  - "[[Nan Xue]]"
  - "[[Bin Tan]]"
  - "[[Han Zhang]]"
  - "[[Youchao Zhang]]"
  - "[[Fei Liao]]"
  - "[[Xing Zhu]]"
  - "[[Yujun Shen]]"
  - "[[Kecheng Zheng]]"
institutions:
topics:
---

# From Foundation to Application: Improving VLA Models in Practice

- [ ] PDF:: [[papers/pdfs/wu2026lingbot-vla2.pdf]]
- [ ] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/wu2026lingbot-vla2_中英混读.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引；精读稿生成后已同步阅读状态。
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

Despite recent progress of VLA foundation models, the disparity between laboratory conditions and real-world applications continues to impede their practical implementation. To bridge this gap, we present LingBot-VLA 2.0, which advances LingBot-VLA through improvements in three functional domains. (1) Generalization across tasks and embodiments. Compared to the previous version, we revamp the data processing pipeline and curate around 60,000 hours of data for pretraining, including 50,000 hours of robot trajectories spanning 20 robot configurations and 10,000 hours of egocentric human videos. (2) Expanded action space in addition to dual-arm hardware platforms. In particular, our system accommodates degrees of freedom for the heads, waists, mobile bases, and dexterous hands, thereby empowering the robots to tackle more complex tasks in practical scenarios. (3) Predictive dynamics modeling for improved temporal reasoning. Specifically, we formulate future prediction as a proxy task, facilitated by a video representation model for semantic priors and a depth estimation model for geometric cues. Evaluations on the GM-100 benchmark, conducted in a generalist setting, validate the beneficial impact of these proposed modifications. Furthermore, benefiting from the expanded pretraining data that covers whole-body degrees of freedom, LingBot-VLA-2.0 demonstrates strong cross-embodiment long-horizon mobile manipulation capability across the two robotic platforms.

## 一句话定位

LingBot-VLA 2.0 用 **60,000 小时跨本体数据 + 55 维统一动作空间 + MoE 动作专家 + 双查询未来表征蒸馏**，把 VLA 从双臂实验室操作扩展到含头、腰、底盘和灵巧手的实际机器人控制。

## 方法 / 对象

- 预训练数据：50,000 小时、20 种机器人本体的机器人轨迹，加 10,000 小时第一视角人类操作视频。
- 核心机制：异构动作填充到 55D canonical vector；action expert 使用 token-level loss-free MoE；通过 DINO-Video 与 LingBot-Depth 监督 current/future query，学习语义与几何的预测动力学。

## 证据

- GM-100 的九项双臂任务结果见 Table 5，移动操作的两项长时程任务见 Table 6；作者用进度分数和成功率报告。
- 消融 §6 分别验证数据规模、统一动作、MoE、视觉蒸馏及未来预测的作用；这些结果支撑“组合改进”而非单一模块归因。

## 局限

- 主要基准是 GM-100 与两个自建移动操作任务，跨实验室、跨物体分布与真实长期安全性的外推仍有限。
- 论文同时改变数据、架构和目标，虽有消融，但系统增益不能完全归因于任一组件。

## 我的阅读笔记


```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
