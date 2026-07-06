---
tags:
  - paper
status: unread
aliases:
  - ENPIRE
  - Physical Autoresearch
  - "ENPIRE: Agentic Robot Policy Self-Improvement in the Real World"
year: 2026
title: "ENPIRE: Agentic Robot Policy Self-Improvement in the Real World"
doi: "10.48550/arXiv.2606.19980"
url: "https://arxiv.org/abs/2606.19980"
venue: "arXiv preprint"
venue_short: "arXiv"
arxiv: "2606.19980v1"
arxiv_url: "https://arxiv.org/abs/2606.19980"
arxiv_doi: "10.48550/arXiv.2606.19980"
pdf_url: "https://arxiv.org/pdf/2606.19980v1"
website: "https://research.nvidia.com/labs/gear/enpire"
pdf: "[[papers/pdfs/ENPIRE.pdf]]"
reading: "[[papers/bilingual/xiao2026enpire_中英混读.md]]"
images: "papers/images/xiao2026enpire/"
image_index: "[[papers/images/xiao2026enpire/index.md]]"
map_axis: "具身智能/VLA/自改进与物理自动研究"
map_brief: "把真实机器人学习封装成 coding agent 可闭环操作的 EN-PI-R-E harness：自动 reset/verification、policy improvement、rollout、multi-agent evolution。"
map_role: "研究真实机器人 autoresearch、agentic policy self-improvement、机器人 fleet 资源利用和自动化实验闭环的入口。"
authors:
  - "[[Wenli Xiao]]"
  - "[[Jia Xie]]"
  - "[[Tonghe Zhang]]"
  - "[[Haotian Lin]]"
  - "[[Letian Max Fu]]"
  - "[[Haoru Xue]]"
  - "[[Jalen Lu]]"
  - "[[Yi Yang]]"
  - "[[Cunxi Dai]]"
  - "[[Zi Wang]]"
  - "[[Jimmy Wu]]"
  - "[[Guanzhi Wang]]"
  - "[[S. Shankar Sastry]]"
  - "[[Ken Goldberg]]"
  - "[[Linxi Jim Fan]]"
  - "[[Yuke Zhu]]"
  - "[[Guanya Shi]]"
institutions:
  - "[[NVIDIA]]"
  - "[[Carnegie Mellon University]]"
  - "[[University of California, Berkeley]]"
topics:
  - physical autoresearch
  - coding agents
  - robot policy self-improvement
  - real-world reinforcement learning
  - behavior cloning
  - code-as-policy
  - robot fleet
  - automated reset
  - automated verification
  - VLA
  - RoboCasa
---

# ENPIRE: Agentic Robot Policy Self-Improvement in the Real World

- [x] PDF:: [[papers/pdfs/ENPIRE.pdf]]
- [x] 项目页:: [research.nvidia.com/labs/gear/enpire](https://research.nvidia.com/labs/gear/enpire)
- [x] 精读稿:: [[papers/bilingual/xiao2026enpire_中英混读.md]]
- [x] 图片索引:: [[papers/images/xiao2026enpire/index.md]]
- [x] 论文地图:: [[论文地图]]
- [ ] 阅读状态:: unread

related:: [[coding agents]], [[robot policy learning]], [[physical autoresearch]], [[VLA]], [[@qian2026wam-rl]], [[@yu2026wm-dagger]], [[@qwen2026robotmanip]], [[@tang2026frs]], [[@xu2026egoguide]]
affiliation:: [[NVIDIA]], [[Carnegie Mellon University]], [[University of California, Berkeley]]

## 一句话问题

真实机器人策略学习的瓶颈不只是算法，而是人要不断 reset scene、跑 policy、验证结果、看日志和改训练代码；ENPIRE 把这套 physical feedback loop 封装成 coding agents 可操作的 harness，让 agent 在真实机器人 fleet 上做 policy self-improvement。

## 方法

- EN：Environment module。先由 coding agent 在少量人类反馈下构造自动 reset、自动 verification/reward、安全约束和 Gym-style APIs。
- PI：Policy Improvement module。agent 读文献、提出假设、改训练代码，在真实机器人自动反馈上 hill-climb success rate。
- R：Rollout module。支持单机器人或多机器人并行执行 policy，收集视频、proprioception、reward、日志和调试信息。
- E：Evolution module。多个 agent-robot workers 通过 Git 分支异步测试训练 recipe，cherry-pick / merge 成功想法。
- 资源指标：Mean Robot Utilization (MRU) 衡量机器人执行实验时间占比；Mean Token Utilization (MTU) 衡量 agent 团队 token 消耗速率；Tokens-to-Success 衡量 token 换成功策略的效率。
- 工具栈：SAM3 / BundleSDF / cuRobo / RealSense / FastAPI / Git / Viser / SERL-style async RL pipeline。

## 证据

- 真实机器人：8 个 bimanual YAM robot stations，每站有两只 6-DoF YAM 臂、1-DoF parallel-jaw gripper、RealSense 摄像头和 RTX 5090 工作站。
- 任务覆盖：Push-T、Pin Insertion、GPU Insertion、Zip Tie Cutting，强调接触、精度、恢复和真实世界 nondeterminism。
- 性能主张：frontier coding agents 可在真实 dexterous tasks 中自主把策略提升到约 99% success rate；pin insertion 中达到 50 consecutive successes / near-perfect success。
- 多 agent scaling：Push-T 从 1 到 8 agents 时，达到 1.0 normalized score 的时间约从 5 小时降到 2 小时；Pin insertion 从超过 1.5 小时降到约 40 分钟。
- 自动环境构造：zip-tie reward 用两视角 segmentation / geometric test，延迟优化到 150 ms 以内；pin insertion reward 融合 visual alignment、insertion depth 和 force estimates。
- 仿真：RoboCasa365 中，agent 通过 motion planning 和 detection tools 增强 GR00T VLA，并把 hover-before-grasp 策略迁移到真实剪刀剪扎带任务。

## 局限

- robot 和 GPU 资源仍未充分利用；agent 读日志、写代码、等待模型响应时机器人空闲，fleet 变大后 MRU 下降。
- token 成本随 fleet size 超线性增长；8-agent 更快成功，但 token-to-success 成本显著上升。
- EN 阶段仍需要一次性人类反馈来构造和验证自动 reset/reward；不是完全从零自发建立实验环境。
- 成功依赖可用工具 API 的质量，例如 SAM3 对小物体或歧义物体的 mask 失败会限制 generated scripts。
- 真实任务虽然多样，但仍在固定 station、固定任务族和高度工程化 safety / reset harness 内。
- 自动 reward/verification 可能与真正任务目标存在偏差，需要 held-out success/failure snapshots 和人类检查保证可靠。

## 我的阅读笔记

ENPIRE 的价值在于把“机器人实验循环”本身作为研究对象，而不是只提出一个新 policy。它把真实世界中最耗人的部分拆成可被 agent 调用和优化的接口：reset、verify、rollout、log、train、merge。这样 coding agent 不只是写代码，而是在真实硬件预算下做可重复的物理实验。

和 [[@qian2026wam-rl]]、[[@yu2026wm-dagger]] 相比，ENPIRE 更偏系统层。WAM-RL 研究 world model 和 actor 怎么在线 co-train；WM-DAgger 研究 world model 怎么补 recovery data；ENPIRE 研究谁来不断发起、执行、验证和改进这些策略实验。它可以被看作 VLA/RL 自改进方法的“物理实验操作系统”。

最值得回看的概念是 physical autoresearch。以往自动研究多在数字环境里运行，因为 trial 便宜；ENPIRE 把 trial 迁移到真实机器人，真正稀缺资源变成 robot-access budget、reset throughput、reward latency 和 token-to-success。这个视角对以后设计机器人自动学习平台很重要。

## 摘录

