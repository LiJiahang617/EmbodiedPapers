---
tags:
  - paper
status: unread
aliases:
  - "DM0.5: An Open-World Foundation Model for General-Purpose Embodied Intelligence"
  - "DM0.5: 面向开放世界的通用具身智能基础模型"
  - DM0.5
year: 2026
title: "DM0.5: An Open-World Foundation Model for General-Purpose Embodied Intelligence"
doi: 
arxiv: 
url: "https://www.dexmal.com/blog/dm0.5"
venue: "Dexmal 原力灵机技术博客（非同行评审；无配套论文）"
openalex: 
metadata_source: "dexmal.com 官方博客正文（标题与技术内容逐字提取）；发布日期与作者名单博客未标注"
metadata_confidence: medium
pdf: "[[papers/pdfs/dexmal2026dm05.pdf]]"
reading: "[[papers/bilingual/dexmal2026dm05_中英混读.md]]"
images: "papers/images/dexmal2026dm05/"
image_index: "[[papers/images/dexmal2026dm05/index.md]]"
authors:
  - "[[Dexmal 原力灵机]]"
institutions:
  - "[[北京原力灵机智能科技有限公司]]"
topics:
---

# DM0.5: An Open-World Foundation Model for General-Purpose Embodied Intelligence

- [x] PDF:: [[papers/pdfs/dexmal2026dm05.pdf]]
- [x] 元数据:: source=官方博客正文, confidence=medium（标题/正文/数字均逐字取自主源；**发布日期与作者名单博客未给出**，勿当作已确认事实）
- [x] 精读稿:: [[papers/bilingual/dexmal2026dm05_中英混读.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，`#map/具身智能/VLA/开放世界长时记忆与具身推理`
- [ ] 阅读状态:: unread

related:: [[@jiang2026robottt]] · [[@intelligence2026pi07-steerable-generalist-robotic]] · [[@intelligence2025pi06-vla-that-learns]] · [[@liu2026last0-latent-spatio-temporal]] · [[@wu2026lingbot-vla2]] · [[@zhang2026lingbot-va2]] · [[@qwen2026robotmanip]] · [[@ye2026data-pyramid-embodied-manipulation]]
affiliation:: [[北京原力灵机智能科技有限公司]]（Dexmal）

## Abstract

> [!warning] 博客无正式 Abstract
> 以下为博客 Overview 小节的自述式总结（原文「DM0.5 的核心优势可以总结为 5 个方面」），非同行评审摘要。

DM0.5 是 Dexmal 在 DM0（2026 年 2 月发布的第一代原生具身基础模型）之上的迭代，目标是「走出实验室，走向开放世界」。架构上沿用 VLA：4B VLM 主干 + 680M Action Expert。相比 DM0，提升不来自单纯放大模型/数据，而来自四项系统性改造——长历史上下文建模（Context Abstraction Layer，最长 60s）、具身推理任务（Embodiment CoT，11 种自回归任务）、动作监督对齐（Trajectory Alignment Layer，动态规划做单调动作匹配）与数据清洗管线。自述五项核心优势：Zero-Shot 能力涌现、Fine-Tuning 高效可靠、长记忆（60s）、动作鲁棒（光照/视角/人为干扰）、多机型后训练迁移。报告成绩：LIBERO 99.0、RoboTwin2.0 93.5、RoboChallenge Table30 v2 Score 54.42（SR 43%），导航 R2R/RxR Val-Unseen 多数指标第一。

## 一句话定位

DM0.5 用 **60 秒历史视觉上下文（Context Abstraction）+ 11 种语言化具身推理任务（Embodiment CoT）+ DP 单调动作匹配（Trajectory Alignment）** 三件套，把 VLA 从「当前帧驱动的短程策略」推向「能记住任务进程、能被开放指令驱动、能在视角变化和人为干扰下续跑」的开放世界基础模型；同时把操作与导航塞进同一个模型。

## 方法 / 对象

- 骨架：4B VLM + 680M Action Expert，经 KV cache 相连；动作走 Flow Matching，默认 10 步去噪生成 50 步 action chunk（4090 10Hz / H100 20Hz）。
- Context Abstraction Layer：训练时从当前时刻往前采多个 history slot，每个 slot 经时间采样 + 空间抽样压成固定数量视觉 token；随机历史长度 + 历史增强，使模型能退化到「无历史」也可用。
- Embodiment CoT Tasks：11 种自回归任务，分任务规划 / 事件与环境预测 / 动作生成三类，与连续动作监督联合训练。
- Trajectory Alignment Layer：监督从「固定时间点对齐」改为「轨迹进展对齐」，为每个预测动作在真值轨迹上选锚点，要求严格单调，用动态规划最小化总匹配损失，并额外约束相邻锚点间的轨迹连续性。
- 数据：机器人操作（ALOHA / Galaxea R1 Lite / AgiBot G1 / Franka Panda / UR5 / ARX5 / Dexmal 自研双臂移动机器人）+ 具身导航 + 第一人称人类操作 + 通用多模态 VL 数据；五道清洗（异常值、静止帧、无价值动作、动作模式去重、错误标注重标）。

## 证据

- Zero-Shot：8 类动作原语 × 7 类语义约束，四组「模型 × 平台」对比（Franka 上 Pi0.5-Droid vs DM0.5-Droid；Dexmal-Mirror 上 DM0 vs DM0.5）。结果只以柱状图给出（本库已存图，无数值表）。
- Fine-tuning：Table30 v2（Generalist Setting，SR 43% / Score 54.42）、LIBERO（99.0 平均）、RoboTwin2.0（93.5 平均）、R2R/RxR 导航表。
- 长记忆：两个真机实验（拿杯擦桌复位 = 短程；看人类示范放电池 = 长程 >1min）。
- 鲁棒性：Franka 九组第三视角相机位姿配置 × 每组 10 次抓放，成功率 80%–100%。

## 局限

- **非同行评审的公司博客**：无 Abstract、无公式、无作者名单、无发布日期，Trajectory Alignment 的 DP 目标只有文字描述，无法复现。
- **Zero-Shot 结果没有数值表**，只有柱状图，且未给 trial 数、置信区间、任务清单；「显著优于」缺统计支撑。
- **无消融**：长历史、Embodiment CoT、Trajectory Alignment 三项改造对最终指标各自贡献多少，全文未拆分。
- 图表里 DM0.5 并非全面占优：Franka 上 `move` 与 Pi0.5-Droid 打平，`status` 约束维度反而低于 Pi0.5-Droid；R2R 的 SPL 也不是第一。博客正文的「绝大多数维度显著优于」口径掩盖了这几处。
- 各基准的对比方法是选择性列举，DM0.5 自身在 Table30 v2 的 43% SR 说明真机泛化仍远未饱和。

## 我的阅读笔记


```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
