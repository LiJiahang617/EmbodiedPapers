---
tags:
  - paper
status: unread
aliases:
  - Ego-Pi
  - "Ego-Pi: VLA Fine-Tuning for Ego-Centric Human and Robot Data"
year: 2026
title: "Ego-Pi: VLA Fine-Tuning for Ego-Centric Human and Robot Data"
doi:
arxiv: "2606.08107v1"
url: "https://arxiv.org/abs/2606.08107"
venue: "CVPR 2026（扩展版）"
project: "https://egopipaper.github.io/"
pdf_url: "https://arxiv.org/pdf/2606.08107v1"
openalex:
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/2606.08107v1.pdf]]"
reading: "[[papers/bilingual/kim2026ego-pi_中英混读.md]]"
images: "papers/images/2606.08107v1/"
image_index: "[[papers/images/2606.08107v1/index.md]]"
authors:
  - "[[Ji Woong Kim]]"
  - "[[Ke Wang]]"
  - "[[Zipeng Fu]]"
  - "[[Sirui Chen]]"
  - "[[Cong Zhao]]"
  - "[[Jeff Lai]]"
  - "[[Chelsea Finn]]"
institutions:
  - "[[Stanford University]]"
  - "[[Meta]]"
topics:
  - vision-language-action
  - egocentric human demonstrations
  - cross-embodiment learning
  - humanoid manipulation
  - dexterous hands
  - task-semantic transfer
  - action interleaving
  - subtask prediction
  - pi0.5
---

# Ego-Pi: VLA Fine-Tuning for Ego-Centric Human and Robot Data

- [x] PDF:: [[papers/pdfs/2606.08107v1.pdf]]
- [x] 元数据:: source=arxiv, confidence=high；CVPR 扩展版与机构由论文 v1 / 项目页核对
- [x] 项目页:: [egopipaper.github.io](https://egopipaper.github.io/)
- [x] 精读稿:: [[papers/bilingual/kim2026ego-pi_中英混读.md]]
- [x] 图片索引:: [[papers/images/2606.08107v1/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，并通过 `python setting/scripts/check_paper_map.py`
- [ ] 阅读状态:: unread

related:: [[vision-language-action]], [[egocentric human data]], [[cross-embodiment]], [[dexterous manipulation]], [[@qwen2026robotmanip]], [[@paliwal2026do-i-dexterous-manipulation]], [[@intelligence2025pi06-vla-that-learns]], [[@wang2026vlk-learning-humanoid-loco]]
affiliation:: [[Stanford University]], [[Meta]]

## Abstract

Robotics faces a fundamental challenge of data scarcity. Unlike language or vision research, there is no internet-scale dataset for robotic manipulation. A promising path forward is to leverage egocentric human data, which can be collected more easily, with greater breadth, and at a larger scale. Towards this end, we investigate key design choices for learning across human and humanoid embodiments equipped with dexterous five-finger hands, using the $π_{0.5}$ model as a foundation. Our results show that human data enables robots to learn new task semantics and compose existing skills into novel behaviors without corresponding robot data. The paper website is here: https://egopipaper.github.io/

## 一句话定位

Ego-Pi 研究的不是“人类视频能否让机器人把已有任务做得更稳”，而是更强的 zero-robot-demo semantic transfer（零目标机器人示范语义迁移）：机器人只学低层原子技能，人类示范提供排序规则、技能先后关系与装箱规则，再由微调后的 $\pi_{0.5}$ 在灵巧双手人形机器人上组合执行。

## 方法 / 对象

- 基座：flow-matching VLA $\pi_{0.5}$，输入头部第一视角、左右腕相机、proprioception 与语言，输出 action chunk，并可先生成 subtask string。
- 高维动作适配：单手 Tesollo 动作为 wrist position 3D + rotation 6D + 20 joint angles，共 29D；双手 58D 超过基座单 token 32D，于是按左、右手交错放入两个 action token，保留预训练投影层但把有效双手 horizon 减半。
- 跨本体动作对齐：把 Manus / MANO 人手角度经逐关节 offset 与 scale 映到 robot-native joint space；避免用 fingertip IK 在高 DoF 手上产生自碰或非自然姿态。
- 视觉与语义辅助：可叠加按手指着色、深度感知遮挡的 skeleton overlay；更关键的是让 VLM 先预测 subtask，再让 action expert 出动作。
- 数据：每 batch 人/机器人各 50%；因人类数据无腕相机，机器人腕图 40% dropout。平台为 Galaxea R1 Pro，Tesollo 20-DoF 或 Inspire 6-DoF 双手。

## 证据

- Tomato Sorting：robot-only 40%，human+robot 92%；加 subtask+skeleton 仍 92%，说明简单排序语义主要由联合训练获得，overlay 没带来收益。
- Boxing（技能串联）：robot-only 20%，简单联合训练 27%，skeleton 版仅 7%；加入 subtask 后 Inspire 为 93%，subtask+skeleton 为 100%，Tesollo+subtask 为 67%。
- Packaging（规则顺序）：robot-only 10%，human+robot 90%。
- 数据规模很小但针对性强：human/robot 分别为 Tomato 89/150 条（13/60 min）、Boxing 60/144 条（5/21 min）、Packaging 96/185 条（11/27 min）。
- 腕相机消融只有定性结论：测试时拿掉 wrist views，番茄抓取明显不稳，说明训练时的人类无腕图并未让模型忽略机器人腕图。

## 局限

- “无目标任务机器人数据”不等于从人类数据学会全新低层技能：机器人已见过开盒、抓放、放盒、放玩偶等原子技能；人类数据主要教 stitching、precondition 和 ordering。
- 只覆盖固定视角、短时程、以 pick-and-place 为主的 3 个任务；没有移动操作、长时程恢复或人类独有低层灵巧技能迁移。
- 人类数据依赖 ZED mini、Manus glove 与 Quest controller 的同步动作标签和手工关节映射，不是从普通无标注互联网视频直接扩展；论文也没有数据规模曲线。
- 结果主要是单比例柱状图；论文未给多 seed、置信区间或统一评测协议。项目页可反推出 Sorting 40 次、Boxing 15 次、Packaging 10 次，后两项样本尤其小。
- interleaving 保住预训练 head 但把有效 bimanual horizon 减半；“直接扩 head 导致更高训练 loss”没有完整定量消融。
- skeleton overlay 实验没有正收益；手型比较也可能混入尺寸、关节数、状态维度和控制难度等混杂因素。

## 我的阅读笔记

Ego-Pi 最有价值的结论是把 human-to-robot transfer 拆成两层：低层 motor primitive 仍由机器人数据落地，人类数据负责提供更便宜的 task semantics。对 Boxing 而言，单纯把两域样本混在一起并不足以学习“先开盒、后放块”的 precondition；显式 subtask token 把这一离散状态机暴露给策略，成功率才从 27% 跳到 93%。因此这篇更像“语义编排迁移”论文，而不是低层 embodiment gap 已被解决的证明。

与大规模第一视角视频路线对照时要特别注明：这里的数据量只有分钟级，且动作由 glove/controller 标注，优势是因果对齐清楚、真机结论直接；代价是采集栈仍重、规模化主张尚未被实验验证。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
