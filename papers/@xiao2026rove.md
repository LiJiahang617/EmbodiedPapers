---
tags:
  - paper
status: unread
aliases:
  - "ROVE: Unlocking Human Interventions for Humanoid Manipulation via Reinforcement Learning"
year: 2026
title: "ROVE: Unlocking Human Interventions for Humanoid Manipulation via Reinforcement Learning"
doi: 
arxiv: "2606.17011"
url: "https://arxiv.org/abs/2606.17011"
venue: "arXiv preprint"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/xiao2026rove.pdf]]"
reading: "[[papers/bilingual/xiao2026rove_中英混读.md]]"
images: "papers/images/xiao2026rove/"
image_index: "[[papers/images/xiao2026rove/index.md]]"
authors:
  - "[[Wei Xiao]]"
  - "[[Weiliang Tang]]"
  - "[[Yuying Ge]]"
  - "[[Hui Zhou]]"
  - "[[Yao Mu]]"
  - "[[Li Zhang]]"
  - "[[Yixiao Ge]]"
institutions:
topics:
  - humanoid manipulation
  - vision-language-action model
  - reinforcement learning
  - human intervention
  - optimistic value estimation
  - cross-embodiment learning
---

# ROVE: Unlocking Human Interventions for Humanoid Manipulation via Reinforcement Learning

- [x] PDF:: [[papers/pdfs/xiao2026rove.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/xiao2026rove_中英混读.md]]
- [x] 地图维护:: [[论文地图]]
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

Human interventions provide crucial corrective signals for post-training Vision-Language-Action (VLA) models. However, enabling seamless humanoid interventions is a formidable systems challenge due to complex whole-body kinematics and dexterous-hand control. Consequently, the collected intervention trajectories are often suboptimal, and methods that rely on human interventions as expert supervision can absorb hesitant, inefficient, or even erroneous behaviors. To address both the system and algorithmic challenges, we propose ROVE, a reinforcement learning framework for humanoid VLA post-training with imperfect human interventions. First, ROVE introduces a human-in-the-loop pipeline capable of collecting deployment and intervention data for humanoid manipulation. Second, it utilizes Optimistic Value Estimation (OVE) to prioritize high-value behaviors from mixed-quality trajectories. To further robustify value estimation, we incorporate cross-embodiment human experience videos to provide rich supervision for long-tailed failure and recovery modes. The resulting critic yields informative advantage signals, steering the VLA actor to focus on high-value behaviors rather than indiscriminately imitating all actions. On challenging real-world contact-rich and fine-grained humanoid manipulation tasks, ROVE outperforms experience-learning baselines and consistently improves across multiple rollout-intervention iterations.

## 一句话定位

ROVE 把不完美的人类接管轨迹视为 mixed-quality experience，而不是逐动作专家示范；它用跨本体人类视频辅助训练 optimistic state-value critic，再以 advantage conditioning 从机器人 rollout、适应和恢复片段中筛出高价值动作，迭代后训练 humanoid VLA。

## 方法 / 对象

- 系统对象是 IRON-R01-1.11 humanoid，采用 50 维全身、本体与灵巧手状态/动作空间；任务是擦白板和把面包放入烤面包机。
- 每条接管轨迹拆成 autonomous rollout、adaptation 和 recovery。适应段包含人类重新对齐身体和手部的犹豫动作，不能直接当成最优动作监督。
- critic 学习状态价值 $V(s)$ 而非 $Q(s,a)$，因此机器人轨迹和没有同构动作空间的人类第一视角视频可进入同一训练目标。
- Optimistic Value Estimation（OVE）对 bootstrapped return 使用 expectile regression；$\tau>0.5$ 偏向数据内更优的恢复结局，但不查询 OOD 动作。
- actor 根据 critic 给出的二值 advantage 条件做微调；每轮按“收集 rollout/intervention → 更新 critic → 标注 advantage → 更新 actor”闭环迭代。
- 训练中对高维 proprioception 使用 dropout 和 Gaussian perturbation，减少策略记住脆弱关节姿态而忽略视觉任务进度。

## 证据

- 三轮 rollout-intervention 后，擦白板成功率从 45.0% 提升到 80.0%，面包入槽从 56.7% 提升到 86.7%。
- ROVE 在 demonstration-only 对比中优于普通 SFT，在 experience-learning 对比中平均优于 HG-DAgger、Filtered BC 和 RECAP。
- 每个任务额外收集 180 条第一视角 human experience videos，成功/失败各半；加入它们后 critic 对“只擦掉一部分”等伪进展的估值更低、更符合真实进度。
- OVE 比 Monte Carlo value curve 更能区分失败、恢复和重新推进；这使负 advantage 落在真正有害的动作区间。
- 擦白板的 value-label 消融：默认 $H=16$ 且在 adaptation 后施加失败边界为 80%；长 horizon $H=50$ 降到 65%；把惩罚提前到接管开始降到 50%。
- 数据规模：两任务分别从 225/220 条 demonstration 起步，三轮新增 82/71/79 和 97/69/104 episodes；接管时间占比为 25.50% 与 4.53%。

## 局限

- 只有两个真实世界任务和单一 humanoid 平台，尚不能证明对更长时程、多任务或不同本体普遍成立。
- 结果主要报告成功率，缺少跨操作者、不同 intervention latency 和更复杂安全约束的系统分析。
- OVE 会放大数据内高回报 continuation；错误的阶段边界会产生“乐观但错误”的标签，消融已显示其敏感性。
- 人类视频只为 critic 提供状态进展监督，无法直接验证跨本体价值对齐在更大 domain gap 下是否稳定。

## 我的阅读笔记

ROVE 的关键不是“用 RL 替代 imitation”，而是重新定义 intervention 的统计角色：接管说明当前位置可能失败，但接管后的每个动作并不都是专家动作。相较直接行为克隆，value-guided extraction 更适合处理 humanoid teleoperation 的犹豫、重对齐和误操作。

它和 [[@deng2026e2hil]]、[[@intelligence2025pi06-vla-that-learns]] 应并排阅读：共同问题是如何利用部署经验，区别在于 ROVE 用 state-value 统一机器人与人类跨本体经验，并显式针对 imperfect intervention。最值得继续追踪的是 OVE 是否能扩展到多任务共享 critic，以及能否用 uncertainty calibration 避免乐观估值放大错误恢复片段。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
