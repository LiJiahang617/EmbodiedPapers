---
tags:
  - paper
status: unread
aliases:
  - "RL$^2$-VLA: Adaptive RL Latent Compositional Steering with Test-Time Scaling for Vision-Language-Action Models"
year: 2026
title: "RL$^2$-VLA: Adaptive RL Latent Compositional Steering with Test-Time Scaling for Vision-Language-Action Models"
doi: "10.48550/arXiv.2607.26991"
arxiv: "2607.26991v2"
url: "https://arxiv.org/abs/2607.26991"
project_url: "https://rl2-vla.github.io"
code_url: "https://github.com/marmotlab/RL2-VLA"
venue: "arXiv preprint"
openalex:
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/tan2026rl2-vla.pdf]]"
reading: "[[papers/bilingual/tan2026rl2-vla_中英混读.md]]"
images: "papers/images/tan2026rl2-vla/"
image_index: "[[papers/images/tan2026rl2-vla/index.md]]"
map_axis: "具身智能/VLA/推理时RL组合引导与自适应缩放"
map_brief: "用冻结VLA的action-expert latent训练轻量离线RL策略，在失败被SAFE和保序校准检测到时组合两套flow velocity，给候选动作引入脱离主导失败模式的多样性。"
map_role: "检验VLA推理时扩展何时该增加多样性，以及latent、离线RL、失败检测和外部verifier如何组成模块化部署链。"
authors:
  - "[[Derek Ming Siang Tan]]"
  - "[[Shailesh Shailesh]]"
  - "[[Srikrishna Iyer]]"
  - "[[William Wei Jie Teo]]"
  - "[[Yuanliang Ju]]"
  - "[[Qiao Gu]]"
  - "[[Guillaume Sartoretti]]"
institutions:
  - "[[National University of Singapore]]"
  - "[[University of Toronto]]"
  - "[[Singapore Technologies Engineering]]"
topics:
  - VLA
  - inference-time steering
  - test-time scaling
  - offline RL
  - flow matching
  - failure detection
  - conformal prediction
---

# RL$^2$-VLA: Adaptive RL Latent Compositional Steering with Test-Time Scaling for Vision-Language-Action Models

- [x] PDF:: [[papers/pdfs/tan2026rl2-vla.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/tan2026rl2-vla_中英混读.md]]
- [x] 图片索引:: [[papers/images/tan2026rl2-vla/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[VLA]], [[inference-time steering]], [[offline reinforcement learning]], [[@pan2026vla-corrector-lightweight-detect]], [[@qian2026wam-rl]], [[@intelligence2026pi07-steerable-generalist-robotic]], [[@kwok2026scaling]]
affiliation:: [[National University of Singapore]], [[University of Toronto]], [[Singapore Technologies Engineering]]

## Abstract

RL$^2$ 面向预训练 VLA 在困难状态和 out-of-domain 场景中的相关失败。作者冻结原 VLA，只用同一份离线微调数据训练一个以 VLA 内部 latent 为条件的轻量 RL policy，再把它的 flow velocity 与 VLA velocity 组合，形成更分散的候选动作。作者通过按成功状态和失败状态拆开的 test-time scaling law 发现，多样性在失败状态更有用，在成功状态可能扰动本来已经正确的动作。因此系统用 SAFE 失败检测器和 conformal prediction 只在预测会失败的时间步启动组合引导，其他时间退回 Repeated 或 Rephrase 的基线采样。SIMPLER、PolaRiS 和 PiperX 真机结果支持这一策略，但证据依赖外部 verifier、离线 oracle 分析和小规模真机校准。

## 一句话定位

这篇论文不是重新训练一个更大的 VLA，而是在推理时给冻结 VLA 接上一个 latent-conditioned offline RL 分支，并让 SAFE 决定何时混入这支分布，从而在失败时产生能避开主导错误的候选动作，在成功时保留原策略的稳定性。

## 方法 / 对象

- 基础策略是 flow-matching VLA $π_0$ 或 $π_{0.5}$，OpenVLA 作为 autoregressive 对照。action expert 的隐藏表示聚合成 latent $e_t$。
- RL steering policy $π_{RL}(a\mid e_t)$ 用 Q-learning with Adjoint Matching（QAM）训练，目标分布是行为正则化的 $π(a\mid s)\propto\pi_\beta(a\mid s)\exp(\tau Q(s,a))$。
- flow-matching VLA 在每个积分步使用 $v_{comp}=w v_{VLA}+(1-w)v_{RL}$。$w$ 从均值 0.5、标准差 0.25 的高斯分布采样并裁剪到 $[0,1]$。
- SAFE 是输入 latent 序列的 LSTM failure detector。成功 rollout 的分数用一侧、随时间变化的 conformal band 校准，分数越过上界才触发 steering。
- 最终候选交给 RoboMonkey 或 CoVer verifier 选取要执行的动作。OpenVLA 没有 flow velocity，因此采用 VLA 与 RL 动作样本拟合高斯后再重采样的兼容实现。

## 证据

- OpenVLA 在 SIMPLER 原始任务上的平均成功率从 Repeated 的 40.2% 提升到 adaptive RL$^2$ 的 47.7%，最高单任务增益为 19.4 个百分点。
- $π_0$ 在 OOD prompt 的平均成功率为 Vanilla 40.2%、Rephrase 50.2%、Compose-Always 57.8%、Compose-Adaptive 60.4%。
- $π_0$ 在 OOD environment 的平均成功率为 36.0%、45.3%、46.5% 和 53.8%，adaptive 相对 Rephrase 提升 8.5 个百分点。
- PolaRiS 的 $π_{0.5}$ 在 OOD prompt 上，adaptive 的平均 success 为 42.7%，progress 为 63.0%，相对 Rephrase 分别提升 10.9 和 7.8 个百分点。Move Latte Cup 的 success 达到 66.0%，比 Rephrase 高 17.3 个百分点。
- PiperX 真机的 OOD prompt 平均成功率是 Vanilla 8.3%、Rephrase 38.4%、Compose-Always 45.0%、Compose-Adaptive 56.7%。OOD environment 平均为 11.7%、26.7%、26.7% 和 43.3%。论文正文报告 adaptive 相对 Rephrase 平均提升 17.5 个百分点，项目页 headline 报 19.5 个百分点，口径并不一致。
- 消融显示 RL 高于 BC，$π_0$ 为 57.8% 对 55.8%，$π_{0.5}$ 为 33.8% 对 29.7%。OpenVLA latent RL 为 39.3%，改用 raw observation 的版本只有 0.5%。
- SAFE 触发在 $π_0$ OOD prompt、OOD task 上分别达到 60.3% 和 53.8%，高于 CoVer 触发的 57.8% 和 50.3%，也高于 Always 的 57.8% 和 46.5%。
- BridgeV2 的 oracle scaling law 拟合为 $e\approx ak^b$。failure set 上 RL$^2$ 为 $a=0.3983,b=-0.1081$，优于 RBF 的 $0.4147,-0.0988$。success set 上 RL$^2$ 为 $0.0468,-0.3250$，反而落后于 Rephrase 的 $0.0385,-0.3243$，说明多样性有状态依赖。

## 局限

- scaling law 用 ground-truth action、NRMSE 和 oracle verifier 构造 failure/success tuple，不能直接替代真实部署中的失败标签。
- 主要 OOD 仍是已知任务的 prompt、物体、背景或 distractor shift，并非严格的 task-level unseen task。
- 系统假定 verifier 能可靠偏好正确候选。RoboMonkey 和 CoVer 的偏好误差会直接改变结果。
- SAFE 在仿真训练后不能直接迁移到真机，作者重新采集真机 rollout 做校准，部署成本因此高于表面上的即插即用。
- adaptive 触发依赖每个任务的 CP $α$ 选择。作者以 balanced accuracy 扫描 $α=0.05$ 到 0.50，并从 top-3 候选中再评估，仍需要额外试验。
- 论文没有和大型 VLM 或其他 VLA 的 differentiable steering 做直接对照，也没有充分证明 offline RL 能在示范分布外稳定地产生高价值行为。

## 我的阅读笔记

说到底，RL$^2$ 的关键不是把 RL policy 单独拿来执行，而是把它当作 VLA 的可控扰动源。VLA 提供大规模示范留下的行为先验，RL 分支负责把候选分布拉出主导模式，SAFE 再把这个代价只花在可能失败的时刻。这个分工比单纯增加采样数更有解释力。

值得画出来的是 success 与 failure 两组曲线方向相反。failure 上 RL$^2$ 的指数更陡，success 上却是较差的候选生成器。作者没有把一条平均曲线当成普遍规律，而是把状态条件写进 scaling law，这个实验问题意识很强。

说实话也不确定的是 oracle 分析到在线触发之间的距离。BridgeV2 中可以直接看 ground-truth action，真实机器人却只能依赖 SAFE 的内部表示和有限 rollout。论文证明了触发思路可行，还没有证明 CP band 在更换任务、相机或本体后仍然校准。

还在摸索的部分是 offline RL 的价值。RL 相对 BC 的增益在主实验中只有 2.0 到 4.1 个百分点，真正大的提升来自 latent 条件、组合方式和自适应开关。把所有收益归结为 RL 会高估这一个组件。

## 摘录

> When faced with uncertainty, humans actively broaden the diversity of alternatives they consider.

> The diversity induced by compositional steering is most useful when the base VLA is likely to fail.

> $\pi(a|s) \propto \pi_\beta(a|s) \exp(\tau Q(s,a))$

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
