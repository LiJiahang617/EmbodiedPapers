---
tags:
  - paper
  - cat/vla
  - cat/human-data
  - cat/data
  - cat/value-reward
status: unread
aliases:
  - "HIL-UMI: Bringing Human-in-the-Loop Post-Training of Vision-Language-Action Models to Universal Manipulation Interface"
year: 2026
title: "HIL-UMI: Bringing Human-in-the-Loop Post-Training of Vision-Language-Action Models to Universal Manipulation Interface"
doi: "10.48550/arXiv.2609.20659"
arxiv: "2609.20659v1"
url: "https://arxiv.org/abs/2609.20659"
venue:
openalex:
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/han2026hil-umi.pdf]]"
reading: "[[papers/bilingual/han2026hil-umi_中英混读.md]]"
images: "papers/images/han2026hil-umi/"
image_index: "[[papers/images/han2026hil-umi/index.md]]"
authors:
  - "[[Zimu Han]]"
  - "[[Yiming Zeng]]"
  - "[[Jiyao Zhang]]"
  - "[[Zihao Zhao]]"
  - "[[Yuanfei Wang]]"
  - "[[Yixiang Jin]]"
  - "[[Shiqi Li]]"
  - "[[Shuangben Chen]]"
  - "[[Wei Huang]]"
  - "[[Ruodai Li]]"
  - "[[Hui Shen]]"
  - "[[Hao Dong]]"
institutions:
  - "[[Peking University]]"
  - "[[PrimeBot]]"
  - "[[Xi'an Jiaotong University]]"
  - "[[JD Technology]]"
topics:
  - "VLA Post-Training"
  - "UMI"
  - "Human-in-the-Loop Learning"
  - "Advantage-Conditioned Behavioral Cloning"
---

# HIL-UMI: Bringing Human-in-the-Loop Post-Training of Vision-Language-Action Models to Universal Manipulation Interface

- [x] PDF:: [[papers/pdfs/han2026hil-umi.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/han2026hil-umi_中英混读.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，`#map/具身智能/VLA/无机器人采集与人在环后训练`
- [ ] 阅读状态:: unread

related:: [[@intelligence2025pi06-vla-that-learns]]、[[@luo2024precise-dexterous-robotic-manipulation]]、[[@murray2026flowdagger]]、[[@zhao2026urvc]]
affiliation:: Peking University、PrimeBot、Xi'an Jiaotong University、JD Technology
map_brief:: 用当前策略分歧与进度反馈引导手持 UMI 采集，再以 ACBC 迭代后训练
map_role:: 把模型指导的纠错采集移到人类示范流，比较其与真实机器人接管的效果和成本

## Abstract

Large-scale vision-language-action (VLA) models provide powerful priors for robot manipulation, yet adapting them to a specific deployment remains challenging. Supervised fine-tuning (SFT) on task-specific demonstrations provides a step toward deployment, but faces two persistent limitations: static data provide limited coverage of out-of-distribution states, and standard imitation objectives do not distinguish progressing behavior from less useful data. Interactive post-training can address these limitations, but typically requires repeated policy execution and human intervention on a physical robot. We introduce HIL-UMI, a policy-guided Universal Manipulation Interface (UMI) framework for robot-free human-in-the-loop VLA post-training. During handheld UMI demonstrations, HIL-UMI queries the current policy on the same observation stream without executing its predictions. The Energy Score compares the human action trajectory with policy inference and triggers collection when their discrepancy indicates an out-of-distribution region. In a separate feedback loop, low online advantage predictions identify essential segments for refining a progress-based advantage estimator. The updated estimator then guides advantage-conditioned behavioral cloning using a balanced mixture of base demonstrations and new policy data. This design preserves the iterative and policy-aware nature of human-in-the-loop learning while decoupling data collection from robot deployment. Experiments on four real-world tasks spanning long-horizon and precise manipulation show that HIL-UMI achieves consistent improvement over SFT and benefits from both targeted collection and advantage refinement. Moreover, HIL-UMI outperforms HG-DAgger on Clean Up Table with lower per-frame collection time, suggesting a scalable path for VLA post-training across operators and locations.

## 一句话定位

HIL-UMI 提出一种不执行机器人策略的数据采集与后训练系统。人类用手持 UMI 示范任务。人类动作与当前策略预测的轨迹分歧触发策略数据采集，进度模型给出的低进度估计触发进度数据采集；随后通过优势条件行为克隆更新 VLA，以降低真机纠错采集成本。

## 方法 / 对象

- 适配开源 $\pi_{0.5}$，用 10 个随机策略动作片段与人类片段计算 Energy Score（能量评分），保存分歧较大的子任务示范。
- 另收集进度模型低估进展的片段，以时间线性标签训练两观测相对进度估计器。
- 新旧数据按 0.5 / 0.5 混合；基础数据最高 30% 预测标为正优势，其余标负；新增策略片段全部标正，推理使用正标签提示。
- 采集设备为 OmniPicker、Meta Quest 3 与两台 RealSense；真实评估使用一台 Franka Panda。

作者单位由论文首页确认，包含 Peking University 的 Center on Frontier Computing Studies 和 National Key Laboratory for Multimedia Information Processing，以及 PrimeBot、Xi'an Jiaotong University、JD Technology。Zimu Han、Yiming Zeng、Jiyao Zhang 为共同一作，Jiyao Zhang 是项目负责人，Hao Dong 为通讯作者。

## 证据

- 四任务，每任务每个 checkpoint 评估 10 次，报告 0–100 的 Task Progress Score（任务进度分数）。基础示范为长时程任务每任务 50 条、精细任务每任务 80 条，三次后训练更新。
- Figure 5 曲线读数显示，完整方法最终四任务均值约 94.75，SFT 约 58，无优势变体约 88；完整方法的基础均值也已更高，约 62.25 对 44.25。
- Stack Cube 阈值表的选定设置 $(\tau_P,\tau_A)=(1.2,0.2)$，TPS 为 84、86、90、100。
- Clean Up Table 最终 TPS 约 96 对 HG-DAgger 的 91；每帧采集时间为 73.40 对 412.99 ms，时间比为 5.63×。
- 相对普通 UMI SFT，HIL-UMI 每帧采集更慢，四任务分别为 91.92、73.40、89.89、101.02 ms；收益在于所采数据带来更多任务进展。

## 局限

无机器人指采集不执行策略，评估仍需真机。模型查询的是人类示范状态，不能直接保证覆盖策略实际执行后的失败状态。进度模型使用时间代理，新增策略数据全为正标签；缺少独立进度误差评估、组件分项消融和失败案例分析。论文没有明确说明新增帧数是两条采集流程各自的数量，还是两者的合计数量。TPS 不是一般成功率，单机器人、四任务和 10 次试验不足以验证跨地点分布式扩展。

## 我的阅读笔记

完整讲解见 [[papers/bilingual/han2026hil-umi_中英混读.md]]，覆盖原文各节、17 个公式、四张表和六张图。回看时重点核对两类采集数据的用途、Equation 16 的标签规则，以及 Figure 5 的初始性能差异。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
