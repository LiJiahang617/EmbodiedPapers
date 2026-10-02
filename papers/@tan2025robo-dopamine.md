---
tags:
  - paper
  - process-reward
  - robotic-reinforcement-learning
status: unread
aliases:
  - "Robo-Dopamine: General Process Reward Modeling for High-Precision Robotic Manipulation"
  - "General Process Reward Modeling for Robotic Reinforcement Learning"
year: 2025
title: "Robo-Dopamine: General Process Reward Modeling for High-Precision Robotic Manipulation"
published_title: "General Process Reward Modeling for Robotic Reinforcement Learning"
doi: "10.48550/arXiv.2512.23703"
arxiv: "2512.23703v1"
url: "https://arxiv.org/abs/2512.23703"
project_url: "https://robo-dopamine.github.io/"
publication_url: "https://openaccess.thecvf.com/content/CVPR2026/html/Tan_General_Process_Reward_Modeling_for_Robotic_Reinforcement_Learning_CVPR_2026_paper.html"
code_url: "https://github.com/FlagOpen/Robo-Dopamine"
venue: "CVPR 2026"
openalex:
metadata_source: arxiv+cvf
metadata_confidence: high
pdf: "[[papers/pdfs/chen2025robo-dopamine.pdf]]"
reading: "[[papers/bilingual/tan2025robo-dopamine_中英混读.md]]"
images: "papers/images/chen2025robo-dopamine/"
image_index: "[[papers/images/chen2025robo-dopamine/index.md]]"
authors:
  - "[[Huajie Tan]]"
  - "[[Sixiang Chen]]"
  - "[[Yijie Xu]]"
  - "[[Zixiao Wang]]"
  - "[[Yuheng Ji]]"
  - "[[Cheng Chi]]"
  - "[[Yaoxu Lyu]]"
  - "[[Zhongxia Zhao]]"
  - "[[Xiansheng Chen]]"
  - "[[Peterson Co]]"
  - "[[Shaoxuan Xie]]"
  - "[[Guocai Yao]]"
  - "[[Pengwei Wang]]"
  - "[[Zhongyuan Wang]]"
  - "[[Shanghang Zhang]]"
institutions:
  - "[[Peking University]]"
  - "[[Beijing Academy of Artificial Intelligence]]"
  - "[[University of Sydney]]"
  - "[[Chinese Academy of Sciences]]"
topics:
  - process reward model
  - dense reward shaping
  - multi-view robot learning
  - policy-invariant reward shaping
  - one-shot adaptation
  - high-precision manipulation
map_axis: "具身智能/奖励模型/过程奖励与策略塑形"
map_brief: "用多视角step-aware GRM估计相对进度和回退，再以policy-invariant potential shaping接入仿真与真机RL，并用单条专家轨迹适配新任务的奖励尺度。"
map_role: "连接通用过程奖励、真机RL样本效率与PBRS理论的入口，也暴露代理完成阈值、线性进度监督和多视角硬件依赖。"
---

# Robo-Dopamine: General Process Reward Modeling for High-Precision Robotic Manipulation

- [x] PDF:: [[papers/pdfs/chen2025robo-dopamine.pdf]]
- [x] 元数据:: source=arxiv+cvf, confidence=high
- [x] 精读稿:: [[papers/bilingual/tan2025robo-dopamine_中英混读.md]]
- [x] 图片索引:: [[papers/images/chen2025robo-dopamine/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[process reward model]], [[dense reward shaping]], [[@yu2026warp-rm]], [[@wang2026wvm]], [[@chen2025sarm]], [[@luo2024precise-dexterous-robotic-manipulation]], [[@intelligence2025pi06-vla-that-learns]]
affiliation:: [[Peking University]], [[Beijing Academy of Artificial Intelligence]], [[University of Sydney]], [[Chinese Academy of Sciences]]

## Abstract

Robo-Dopamine 把真实机器人强化学习的奖励设计拆成两个层次。Dopamine-Reward 训练一个能处理同步多视角、细粒度相对进度和回退的 General Reward Model（GRM），Dopamine-RL 再把 GRM 的进度估计转成 policy-invariant dense reward。GRM 使用超过 3,400 小时视频、100K 以上轨迹和 350 个以上日常操作任务，原始 27.23M 帧经多视角扩增为约 35M 训练样本。论文报告 GRM-8B multi-view 在七套数据和三种采样密度上平均 VOC 为 0.96、0.96、0.94，三类真机 rollout 的完成判断准确率为 92.8%。在 10 个仿真任务和 8 个真机任务上，Dopamine-RL 分别达到 81.0% 和 95.2% 成功率，达到最终成功率 80% 所需 rollout 为 395 和 150。

## 一句话定位

这篇论文用 hop-based step-aware GRM 估计「前后状态离目标还近了多少」，用 incremental、forward-anchored、backward-anchored 三路融合抵抗漂移，再以 $r_{gold}+\gamma\Phi(s')-\Phi(s)$ 做 potential-based shaping，让密集信号帮助探索而不改变相对于代理奖励的最优动作排序。

## 方法 / 对象

- GRM 基于 RoboBrain 2.0 / Qwen2.5-VL，提供 3B 和 8B 版本。输入是任务文字、initial、goal 以及 BEFORE/AFTER 的同步多视角图像，输出量化到百分比 token 的 progress hop 或 regress hop。
- 轨迹先由人工多视角 keyframes 切成子任务，定义线性全局进度 $\Phi(s_i)=i/M$。hop 在前进时除以剩余到 goal 的距离，在回退时除以已经走过的距离，标签范围为 $[-1,1]$。
- 多视角进度融合把局部递推、初始锚定和目标锚定平均。可选 consistency-aware weighting 比较 forward 与 backward 的差异，在 OOD 状态下采取保守更新，降低 reward hacking 风险。
- 新任务只需一条 human expert trajectory 做 GRM 的 MSE SFT。真机策略侧使用 ConRFT、Cal-QL 和 human-in-the-loop，仍以 20–30 条 policy demonstrations 做安全初始化，这不等于整个系统只需一条示范。
- 最终奖励是 $r_{GRM}=r_{gold}+\gamma\Phi^*(s_{t+1})-\Phi^*(s_t)$，其中 $r_{gold}$ 在估计进度达到 $1-\delta$ 时自动置 1，论文默认 $\delta=0.05$。

## 证据

- **进度排序。** Table 1 的 GRM-8B multi-view 平均 VOC 在 Sparse、Medium、Dense 下分别为 0.96、0.96、0.94，基线 GVL 为 0.20、0.12、0.13，VLAC-2B 为 0.24、0.29、0.33。
- **完成判断。** Table 2 使用 stacking、folding、clearing 各 60 条 rollout，multi-view GRM-8B 正确 56、54、57 条，平均 92.8%，高于 GPT-5 的 83.9% 和 single-view GRM 的 83.9%。
- **策略学习。** Table 3 的 Dopamine-RL 在论文所称的 10 个仿真任务达到 81.0% 成功率、395 rollout，在 8 个真机任务达到 95.2%、150 rollout。这里的 rollout 数是达到最终成功率 80% 的样本效率指标，因此 150 对应的门槛约为 76%，不能严格读成 150 次后立刻达到 95.2%；正文把仿真任务来源写成 LIBERO 与 RoboTwin2.0，Appendix 具体展开的却是 LIBERO-Goal 10 tasks。
- **泛化。** Table 4 在 Insert Square、Circuit、Cap Pen 三个真机任务上比较 object、layout、background shift。Dopamine-RL 的平均相对下降为 19.3%、8.3%、15.8%，BC 为 57.1%、60.0%、50.0%。
- **消融。** Table 5 的完整框架平均成功率为 85.0%。去掉 fusion 后三路单独使用为 70.0%、65.7%、62.5%，去掉 policy-invariant shaping 为 41.3%，去掉 one-shot adaptation 为 63.2%。

## 局限

- hop 标签依赖人工 keyframe 切分与线性 $\Phi=i/M$，把专家轨迹采样点当作等间隔进度，不能自动表达每个子步骤的真实 salience。
- policy-invariant 证明假设 Markov state、无限时域、$\Phi$ 有界。有限 episode 会留下 $\gamma^T\Phi(s_T)$ 终端项，实际的 $\Phi^*$ 还含历史递推；因此严格不变性针对定义好的代理奖励，不自动等于真实任务成功目标。
- 自动 $r_{gold}$ 由 GRM 的 $\Phi\geq0.95$ 阈值触发。GRM 若在 OOD 状态产生高分，系统仍可能把估计误差固化成学习目标。
- multi-view 需要同步、标定的 wrist 与 third-person 相机。single-view 与 multi-view 的差距显示它很重要，也说明部署硬件和数据采集成本不能忽略。
- 主要 OOD 评测是已知任务的物体、布局和背景变化，不是完全未见任务。one-shot 适配节省的是 reward model 标注，真机策略仍有 20–30 条示范、HIL 和校准开销。
- 论文把 one-shot 适配写成 hop 的 MSE 目标，公开 fine-tuning 脚本则对 assistant 的 score token 使用 causal-LM cross-entropy。两者未必等价，复现时需要以具体数据处理和训练代码为准。
- 官方仓库提供 GRM 推理、评测、数据生成和微调，但没有完整公开论文中的 Dopamine-RL、ConRFT、PPO、ReinFlow 端到端训练代码，复现策略结果需要自行补齐。公开 HF benchmark 当前只有六类数据源，而 Table 1 列七类。

## 我的阅读笔记

说到底，Robo-Dopamine 的贡献不是又一个把视频打分的 VLM，而是把 reward model 的误差传播和 RL 的目标错位放在同一条设计链里。hop 归一化先把局部变化限制在可递推的区间，三路融合再分别利用局部、起点和终点参照，最后用 PBRS 形式接入 RL。只有这三层同时成立，GRM 的高 VOC 才有机会转成策略成功率。

最值得保留的判断是「one-shot」必须限定在 GRM adaptation。论文摘要容易让读者把 150 次 rollout 和一条 demonstration 读成端到端单示范学习，但 Appendix 的 ConRFT 设置明确保留了 20–30 条 policy demonstrations。奖励接口的低标注成本与策略初始化的示范成本是两条不同账本。

理论部分很有用，但不应把「policy-invariant」当成无条件安全证明。论文证明的是在代理奖励、Markov 假设和无限时域下，$\gamma\Phi(s')-\Phi(s)$ 的折扣和只产生初始状态偏移。附录的有界性归纳只直接覆盖 incremental 递推，forward/backward 锚定和三路平均在模型误差下未自动保证落在 $[0,1]$，论文也没有报告额外 clamp 或校准。真实系统的完成奖励由同一个 GRM 阈值产生，若 GRM 错判，保持最优策略只是在错误目标上保持。

我的保留意见集中在负反馈来源。训练 hop 主要来自专家轨迹内的反向配对和 zero-hop 采样，并非大量真实失败恢复轨迹。GRM 对 off-trajectory 状态的可靠性仍依赖多视角覆盖、random viewpoint dropout 和少量 corner-case 数据，不能仅凭 Table 1 的排序分数推断它已解决 reward hacking。

## 来源与版本核对

- 原论文与版本日期  [arXiv 2512.23703v1](https://arxiv.org/abs/2512.23703)，提交日期为 2025-12-29，PDF 含主文与补充材料。
- CVPR 正式版本  [CVF Open Access](https://openaccess.thecvf.com/content/CVPR2026/html/Tan_General_Process_Reward_Modeling_for_Robotic_Reinforcement_Learning_CVPR_2026_paper.html)，正式题名为 `General Process Reward Modeling for Robotic Reinforcement Learning`，方法仍称 Robo-Dopamine。
- 官方项目页  [Robo-Dopamine](https://robo-dopamine.github.io/)，页面将工作标为 CVPR 2026。
- 官方代码  [FlagOpen/Robo-Dopamine](https://github.com/FlagOpen/Robo-Dopamine)，用于 GRM 推理、数据生成、微调与评测；后续 GRM-2.0 preview 不与本文 v1 混写。
- 模型与基准入口  [Hugging Face collection](https://huggingface.co/collections/tanhuajie2001/robo-dopamine)。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
