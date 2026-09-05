---
tags:
  - paper
  - cat/agent
  - cat/self-evolving
status: unread
aliases:
  - Zetta
  - "Zetta ζ: An Efficient Closed-Loop Embodied Harness for Self-Evolving Physical Intelligence"
year: 2026
title: "Zetta ζ: An Efficient Closed-Loop Embodied Harness for Self-Evolving Physical Intelligence"
doi: "10.48550/arXiv.2608.16590"
arxiv: "2608.16590v1"
url: "https://arxiv.org/abs/2608.16590"
venue: "arXiv preprint"
venue_short: "arXiv"
arxiv_url: "https://arxiv.org/abs/2608.16590"
arxiv_doi: "10.48550/arXiv.2608.16590"
pdf_url: "https://arxiv.org/pdf/2608.16590v1"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/ding2026zetta.pdf]]"
reading: "[[papers/bilingual/ding2026zetta_中英混读.md]]"
images: "papers/images/ding2026zetta/"
image_index: "[[papers/images/ding2026zetta/index.md]]"
map_axis: "具身智能/智能体/闭环执行监督与技能自进化"
map_brief: "冻结 VLA 不动，让 LLM 智能体从失败 rollout 里进化出代码形态的运行时 critic 与恢复技能，三个时间尺度分离的循环实现闭环执行、因果诊断修复和验证门控入库，配 Z-Infra 基础设施把 rollout 吞吐提 20.6 倍。"
map_role: "研究不动策略权重、只进化执行监管层能把成功率推多远，以及具身自进化的 rollout 基础设施该长什么样的入口。"
authors:
  - "[[Xin Ding]]"
  - "[[Liang Mi]]"
  - "[[Mingzhe Huang]]"
  - "[[Zixuan Wang]]"
  - "[[Chao Zhang]]"
  - "[[Zixu Hao]]"
  - "[[Fu Chen]]"
  - "[[Xiangyu Li]]"
  - "[[Yikai Zheng]]"
  - "[[Yaoyu Guo]]"
  - "[[Weijun Wang]]"
  - "[[Kun Li]]"
  - "[[Hao Wu]]"
  - "[[Yunxin Liu]]"
  - "[[Ting Cao]]"
institutions:
  - "[[Tsinghua University]]"
  - "[[Z-Trans AI]]"
topics:
  - embodied agent harness
  - runtime critic
  - recovery skill
  - self-evolution
  - closed-loop execution
  - causal diagnosis
  - rollout infrastructure
  - frozen VLA
  - LIBERO-Pro
  - RoboCasa
---

# Zetta ζ: An Efficient Closed-Loop Embodied Harness for Self-Evolving Physical Intelligence

- [x] PDF:: [[papers/pdfs/ding2026zetta.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/ding2026zetta_中英混读.md]]
- [x] 图片索引:: [[papers/images/ding2026zetta/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[embodied agent harness]], [[runtime critic]], [[self-evolution]], [[@pan2026vla-corrector-lightweight-detect]], [[@xiao2026enpire]], [[@intelligence2025pi06-vla-that-learns]], [[@jiang2026robottt]], [[@xue2026worldsample]], [[@luo2024precise-dexterous-robotic-manipulation]], [[@deng2026e2hil]]
affiliation:: [[Tsinghua University]], [[Z-Trans AI]]

## Abstract

Embodied agents are increasingly used to close the gap left by end-to-end policy models. Yet the agentic path has not realized closed-loop learning in physical execution: existing harnesses remain largely open-loop, following fixed skills during rollout and reflecting only after an episode completes. Such post-hoc reflection cannot govern execution as it unfolds, because physical interaction requires decisions to track rapidly changing robot-environment states at a frequency beyond today's large agentic models. We present Zetta, a closed-loop embodied harness that evolves code-based runtime critics and recovery skills online while keeping the base policy frozen. Through three timescale-separated loops, Zetta provides action-frequency governance, rollout-level critic-recovery proposal, and validation-gated skill updates. Together with Z-Infra, a rollout infrastructure decoupling agent logic from heterogeneous execution resources, Zetta achieves state-of-the-art success on LIBERO-Pro and RoboCasa under our current rollout budget, reaching 90.8% and 93.6%, with an 11.1x inference speedup; success continues to scale with self-exploration experience; learned skills transfer zero-shot, and clear robotic "Aha Moments" emerge. These results show that closed-loop harness self-evolution opens a scaling path for reliable physical intelligence.

## 一句话定位

策略模型一个参数不动，把包在外面的执行框架（runtime critic、恢复技能、工具集）定义成进化对象，让 LLM 智能体从失败 rollout 里自动诊断根因、写代码补丁、验证入库，用高频代码监管加低频智能体进化实现闭环自进化，LIBERO-Pro Goal 平均从 34.5% 到 90.8%，RoboCasa 从 73.6% 到 93.6%。

## 方法 / 对象

- 治理结构，冻结的动作策略 $\pi$（π0.5 / GR00T N1.5）加冻结的 Orchestrator Agent 裁决，进化对象是 harness $H=\{C,R,\mathcal{T}\}$。
- critic 是代码形态高频监控函数，产出结构化提案 $P_t=\langle e_t,\hat\sigma_t\rangle$，只有提案权，干预须经裁决。
- 三循环，动作级 critic 监管、rollout 批级失败聚类与候选提案、迭代级验证门控技能入库。
- 诊断流水线，$m^*$ 首个缺失里程碑粗聚类，$t_{EOD}$ 最早可观测偏离细聚类，medoid seed 深挖，单视角接地协议，六层自顶向下因果诊断（评估/critic/状态/规划/恢复/参数），高层能修绝不动低层。
- 修复带 VLA 重入契约 $\Psi(s_t)$，失败证据清除且接触稳定才还权，防二次失败。
- 泛化阶段跨种子合并成版本化技能包（SKILL.md + tools/plans/params），历史回归 100% 加隔离集 $\Delta SR$ 双关，隔离集暴露新机制则种子降级换新集重验。
- Z-Infra，控制面加环境 worker 池加 rollout worker 池，MuJoCo 模板 fork 与 C++ 步进控制器实现进程内并行，π0.5 VLM 与动作专家双进程切分（延迟降 53%），prefix MLP W8A8 量化（1.18 到 1.32 倍无损加速），基于 Ray。

## 证据

- RoboCasa 18 任务宏平均 73.56% 到 93.56%（+20.00），全部任务提升；LIBERO-Pro 40 组任务对总体 32.00% 到 71.13%（+39.13），32 升 8 平。
- 摘要的 90.8% 是 LIBERO-Pro Goal (T) 92.5 与 (S) 89.0 的平均，LIBERO-10 只到 63.0 与 40.0，且 (T) 有两组 0.0 未解决。
- scaling，LIBERO-Pro Goal-T 31.0→67.5→89.5→92→92.5，RoboCasa 73.56→78.71→84.85→90.54→93.56，四轮单调上升未见饱和。
- 零样本迁移，PnP-Stove 技能迁到 Sink/Cabinet/Toaster 宏平均 64→84，TurnOffStove 技能迁到三个铰接任务 64→80，全部不做目标任务优化。
- 顿悟时刻，Wine bottle in bowl 10/15/95，Put cream cheese 0/5/90，Goal-T8 5/10/60，RoboCasa 三任务 88/88/94、76/76/94、82/82/96。
- 系统，吞吐 1.7 到 35.1 ep/min（20.6 倍），并发 16 时比 RPent 高 12.8 倍，延迟相对 RPent 降 91%（11.1 倍），基线并发 16 以上 OOM。

## 局限

- 全部在 MuJoCo 仿真。critic 监控的物体位姿、双指接触、抓取谓词在仿真里是特权状态，真机上每个信号都要靠估计，高频代码 critic 的可行性要重新论证，作者把真机列为未来工作。
- 进化智能体（诊断/修复/泛化）的模型身份、token 成本、每轮墙钟时间全文无数字，离线进化的真实开销无法与微调路线对比。
- 成功率表里只有纯 VLA 底座，没有任何其他 agent harness 的成功率对照，RPent 只比了延迟，SOTA 主张的成功率证据不完整。
- 上限受冻结策略加外部工具能力封顶，LIBERO-10 (T) 两组 0.0 与 (S) 40.0 的天花板是证据，作者自己也说 toward the frozen policy's capability ceiling。
- 无框架级组件消融（重入契约、诊断次序等），LIBERO-Pro 开发集 50% 的迭代停止门槛未解释。

## 我的阅读笔记

这篇最值得拿走的是架构层面那个分工，高频侧放进化出来的代码，低频侧放 LLM。闭环频率问题和大模型推理慢的矛盾被这一个分工化解掉，11.1 倍加速不是优化出来的，是 online 路径上根本没有 LLM。对照 RPent 每步调 API 的 392 秒起步延迟，这个设计选择的份量就出来了。

第二个值得记的是评测纪律。隔离测试集全程不可见、历史回归 100% 才放行、隔离集暴露新机制就种子降级换新集重验，这套协议在 agent 自进化的论文里少见地严格。同种子同 RNG 的相邻轮对照（Figure 13 的 Round 2/3）也做得干净。数字本身可以信，要小心的只是口径，90.8% 是 Goal 子集，完整宏平均 71.13%。

「顿悟时刻」这个包装我持保留态度，v1 定义为还在反复修改的中间态，突跳幅度有选点自由度。但它背后的论断说到点子上了，物理智能的可规模化单元是「识别出哪个状态变量必须被恢复」，抓取保持、接近几何这类变量是任务无关的，这才是零样本迁移 +20 点的真正原因。

我最大的保留意见在真机。critic 代码读的是仿真特权状态，真机上位姿估计与接触推断的噪声和延迟会直接打在 critic 的假阳假阴率上，而层级诊断第二层查的恰恰就是 critic 假阳假阴。这个循环在真机上会不会收敛，说实话也不确定，值得盯它们的后续工作。

## 摘录

> Physical tasks require decisions to be coupled to the current robot and environment state, often changing within a millisecond-level latency budget. Large agentic models cannot make decisions at this frequency in real-world systems.

> Adhering to the principle that "if high-level logic resolves the failure, never modify low-level parameters," ensures patches are applied at the minimal effective layer, preserving the foundation model's integrity.

> These discontinuous gains reflect the harness's improved ability to restore the required physical state for the frozen VLA.

> the scalable unit in our framework is not a task-specific trajectory, but a reusable mapping from observable physical failure states to robust recovery behaviors.

> this self-evolution scales task success toward the frozen policy's capability ceiling and transfers across tasks.

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
