---
tags:
  - paper
status: read
aliases:
  - "Precise and Dexterous Robotic Manipulation via"
year: 2024
title: "Precise and Dexterous Robotic Manipulation via"
doi: 
arxiv: "2410.21845v1"
url: "https://arxiv.org/abs/2410.21845"
venue: 
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/luo2024precise-dexterous-robotic-manipulation.pdf]]"
reading: "[[papers/bilingual/luo2024precise-dexterous-robotic-manipulation_中英混读.md]]"
images: "papers/images/luo2024precise-dexterous-robotic-manipulation/"
image_index: "[[papers/images/luo2024precise-dexterous-robotic-manipulation/index.md]]"
authors:
  - "[[Human-in-the-Loop Reinforcement Learning Jianlan Luo]]"
  - "[[Charles Xu]]"
  - "[[Jeffrey Wu]]"
  - "[[Computer Sciences]]"
  - "[[UC Berkeley]]"
institutions:
topics:
---

# Precise and Dexterous Robotic Manipulation via

- [x] PDF:: [[papers/pdfs/luo2024precise-dexterous-robotic-manipulation.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/luo2024precise-dexterous-robotic-manipulation_中英混读.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，`#map/具身智能/RL/真实机器人HiL`
- [x] 阅读状态:: read

related::
affiliation::

## Abstract

Reinforcement learning (RL) holds great promise for enabling autonomous acquisition of complex robotic manipulation skills, but realizing this potential in real-world settings has been challenging. We present a human-in-the-loop vision-based RL system that demonstrates impressive performance on a diverse set of dexterous manipulation tasks, including dynamic manipulation, precision assembly, and dual-arm coordination. Our approach integrates demonstrations and human corrections, efficient RL algorithms, and other system-level design choices to learn policies that achieve near-perfect success rates and fast cycle times within just 1 to 2.5 hours of training. We show that our method significantly outperforms imitation learning baselines and prior RL approaches, with an average 2x improvement in success rate and 1.8x faster execution. Through extensive experiments and analysis, we provide insights into the effectiveness of our approach, demonstrating how it learns robust, adaptive policies for both reactive and predictive control strategies. Our results suggest that RL can indeed learn a wide range of complex vision-based manipulation policies directly in the real world within practical training times. We hope this work will inspire a new generation of learned robotic manipulation techniques, benefiting both industrial applications and research advancements. Videos and code are available at our project website https://hil-serl.github.io/.

## 一句话定位

系统级整合（预训练视觉骨干+RLPD+二值奖励分类器+安全阻抗控制器+SpaceMouse 人在环纠正+离散 grasp critic），让真机视觉 RL 在 1–2.5 小时内以近乎 100% 成功率学会 timing belt/Jenga/双臂装配等极难灵巧任务。

## 方法 / 对象

actor/learner/replay-buffer 分布式异步；RLPD off-policy 等量采样 demo/在线数据；二值分类器稀疏奖励；相对末端本体状态（空间泛化+抗扰）；阻抗控制器保证探索安全；离散夹爪用 DQN grasp critic；训练中人用 SpaceMouse 随时接管纠偏（纠正入 demo+RL 双 buffer）。

## 证据

7 任务平均成功率 BC(HG-DAgger) 49.7%→100%、循环用时 1.8× 更快（Table 1a）；timing belt 2→100、Jenga 8→100。消融：去掉纠正平均 49、无 demo 无纠正 =0（Table 1b），证明人类纠正是难任务关键。

## 局限

每任务单独训练、依赖人工奖励分类器/复位/纠正（非全自主、非单策略多任务）；纠正质量依赖操作者；未评估跨物体/场景/本体泛化。详见精读稿矩阵。

## 我的阅读笔记


```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
