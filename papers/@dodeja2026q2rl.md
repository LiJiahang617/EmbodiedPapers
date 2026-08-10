---
tags:
  - paper
status: unread
aliases:
  - Q2RL
  - "When Life Gives You BC, Make Q-functions: Extracting Q-values from Behavior Cloning for On-Robot Reinforcement Learning"
year: 2026
title: "When Life Gives You BC, Make Q-functions: Extracting Q-values from Behavior Cloning for On-Robot Reinforcement Learning"
doi:
arxiv: "2605.05172v3"
url: "https://arxiv.org/abs/2605.05172"
venue: "Robotics: Science and Systems (RSS) 2026"
project: "https://q2rl.rai-inst.com/"
code: "https://github.com/rai-opensource/q2rl"
pdf_url: "https://arxiv.org/pdf/2605.05172v3"
openalex:
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/2605.05172v3.pdf]]"
reading: "[[papers/bilingual/dodeja2026q2rl_中英混读.md]]"
images: "papers/images/2605.05172v3/"
image_index: "[[papers/images/2605.05172v3/index.md]]"
authors:
  - "[[Lakshita Dodeja]]"
  - "[[Ondrej Biza]]"
  - "[[Shivam Vats]]"
  - "[[Stephen Hart]]"
  - "[[Stefanie Tellex]]"
  - "[[Robin Walters]]"
  - "[[Karl Schmeckpeper]]"
  - "[[Thomas Weng]]"
institutions:
  - "[[Robotics and AI Institute]]"
  - "[[Brown University]]"
  - "[[Northeastern University]]"
topics:
  - behavior cloning
  - offline-to-online reinforcement learning
  - on-robot reinforcement learning
  - Q-estimation
  - Q-gating
  - sample-efficient robot learning
  - contact-rich manipulation
  - Soft Actor-Critic
---

# When Life Gives You BC, Make Q-functions: Extracting Q-values from Behavior Cloning for On-Robot Reinforcement Learning

- [x] PDF:: [[papers/pdfs/2605.05172v3.pdf]]
- [x] 元数据:: source=arxiv, confidence=high；RSS 2026 与机构由论文 v3 / 项目页核对
- [x] 项目页:: [q2rl.rai-inst.com](https://q2rl.rai-inst.com/)
- [x] 代码:: [rai-opensource/q2rl](https://github.com/rai-opensource/q2rl)
- [x] 精读稿:: [[papers/bilingual/dodeja2026q2rl_中英混读.md]]
- [x] 图片索引:: [[papers/images/2605.05172v3/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，并通过 `python setting/scripts/check_paper_map.py`
- [ ] 阅读状态:: unread

related:: [[behavior cloning]], [[offline-to-online reinforcement learning]], [[on-robot reinforcement learning]], [[Soft Actor-Critic]], [[@deng2026e2hil]], [[@luo2024precise-dexterous-robotic-manipulation]], [[@intelligence2025pi06-vla-that-learns]]
affiliation:: [[Robotics and AI Institute]], [[Brown University]], [[Northeastern University]]

## Abstract

Behavior Cloning (BC) has emerged as a highly effective paradigm for robot learning. However, BC lacks a self-guided mechanism for online improvement after demonstrations have been collected. Existing offline-to-online learning methods often cause policies to replace previously learned good actions due to a distribution mismatch between offline data and online learning. In this work, we propose Q2RL, Q-Estimation and Q-Gating from BC for Reinforcement Learning, an algorithm for efficient offline-to-online learning. Our method consists of two parts: (1) Q-Estimation extracts a Q-function from a BC policy using a few interaction steps with the environment, followed by online RL with (2) Q-Gating, which switches between BC and RL policy actions based on their respective Q-values to collect samples for RL policy training. Across manipulation tasks from D4RL and robomimic benchmarks, Q2RL outperforms SOTA offline-to-online learning baselines on success rate and time to convergence. Q2RL is efficient enough to be applied in an on-robot RL setting, learning robust policies for contact-rich and high precision manipulation tasks such as pipe assembly and kitting, in 1-2 hours of online interaction, achieving success rates of up to 100% and up to 3.75x improvement against the original BC policy. Code and video are available at https://pages.rai-inst.com/q2rl_website/

## 一句话定位

Q2RL 把一个只会模仿、无法自我改进的黑盒 BC policy 转成在线 RL 的起点：先借少量 BC rollout、动作对数似然与策略熵估出 $\hat Q_{\mathrm{BC}}$，再用冻结的 BC critic 与可学习的 RL critic 做 Q-Gating，在保留好动作和探索更优动作之间逐状态选择。

## 方法 / 对象

- 对象：已有成功示范训练出的 Gaussian / GMM-RNN BC policy，在线阶段可获得稀疏成功奖励与环境交互，但不一定能访问原始示范数据。
- Q-Estimation：在 Boltzmann / soft-optimality 假设下使用 $\hat Q_{\mathrm{BC}}=\hat V_{\mathrm{BC}}+\alpha\log\pi_{\mathrm{BC}}+\alpha\mathcal H[\pi_{\mathrm{BC}}]$；$\hat V$ 来自少量 BC 在线 rollout 的 Monte Carlo return。
- Q-Gating：复制两份估计 critic；$\hat Q_{\mathrm{BC}}$ 冻结作 BC 锚点，$Q_{\mathrm{RL}}$ 由其初始化后随 SAC 更新，每步比较各自策略候选动作的各自 Q 值并执行较大者。
- 稳定项：RL actor 还带辅助 BC loss；仿真评 D4RL / robomimic，真机评 1–2 mm 公差插入、Pipe Assembly 与发生任务分布迁移的 Kitting。

## 证据

- 无原始训练数据的 robomimic 设置最能体现差异：Q2RL 在 Lift-State / Can-State / Square-State 最终约为 1.00 / 0.82 / 0.76，IBRL、CQL、CalQL、WSRL 基本为 0；Can-Image 最终约 0.63，高于 BC 0.45。
- D4RL 上 Kitchen 最终 $0.91\pm0.01$（BC 0.69），Pen $0.93\pm0.03$（BC 0.90）；Door 为 $0.87\pm0.08$，低于 WSRL 1.0，但作者指出 WSRL 利用了不具真机可行性的 simulator exploit。
- 真机每法每任务 20 次：Peg 0.70→1.00，Pipe 0.20→0.75（3.75×），Kitting-Modified 0.35→0.70（2×）；IBRL 在后两项为 0。
- 消融显示 Q-Gating 是核心；25 次 Q-Estimation rollout 已有竞争力；从 10%–75% 不同初始 BC 成功率都能改进；非 soft-optimal 噪声策略会先掉点、随后恢复。

## 局限

- 理论身份依赖把 BC 看作相对于任务 $Q$ 的 Boltzmann policy；一般行为分布并不保证由真实环境回报的 $Q^{\pi_{\mathrm{BC}}}$ 诱导，少量稀疏奖励 rollout 也可能让 $\hat V$ 偏差很大。
- Gate 比较的是冻结 $\hat Q_{\mathrm{BC}}$ 与持续漂移的 $Q_{\mathrm{RL}}$，论文没有显式解决跨 critic 标度校准；错误乐观仍可能把门开给危险 RL 动作。
- 兼容性要求可计算 normalized action likelihood 与 entropy，当前只验证 Gaussian / GMM；diffusion、flow matching VLA 被明确留作未来工作。
- 真机结果只报告选出的最佳 checkpoint、每项 20 次，未给多随机种子/置信区间；成功奖励、终止与 reset 都有人参与，“安全”结论主要来自少数故障计数与定性观察。
- Kitting 的 Q-Estimation 用 Original 条件的 50 个 episode，在线 buffer 又以 Modified 条件 30 个 episode 初始化，不能把该任务解读成完全零先验在线适应。

## 我的阅读笔记

这篇最值得保留的不是“从 BC 得到一个精确的真实 Q”，而是一个实用的策略分工接口：把原策略当作不会随在线训练遗忘的 action proposer / safety anchor，把 RL 留给接触、精对准和分布迁移段。读结果时应把“Q-Estimation 的理论正确性”与“冻结参照 + 双候选门控的工程有效性”分开评价；实验更强地支持后者。

引用数字时要区分三种口径：3.75× 是 Pipe 的成功率 $0.20\rightarrow0.75$；“1–2 小时”是代表性收敛叙述，而实验选择的 checkpoint 最多训练 2.5 小时；D4RL Door 的最高成功率属于 WSRL，不属于 Q2RL。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
