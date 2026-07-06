---
tags:
  - bilingual-reading
paper: "[[@qian2026wam-rl]]"
source_pdf: "[[papers/pdfs/WAM-RL.pdf]]"
images: "papers/images/qian2026wam-rl/"
image_index: "[[papers/images/qian2026wam-rl/index.md]]"
created: 2026-06-25
---

# WAM-RL: World-Action Model Reinforcement Learning with Reconstruction Rewards and Online Video SFT

paper:: [[@qian2026wam-rl]]
pdf:: [[papers/pdfs/WAM-RL.pdf]]
images:: [[papers/images/qian2026wam-rl/index.md]]

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| World-Action Model, WAM / WA model | 世界-动作模型 | 把未来世界状态预测和动作生成耦合起来的机器人策略范式。 |
| world model | 世界模型 | 生成 imagined future observations，提供隐式规划和预测结构。 |
| action model / actor | 动作模型 / 执行器 | 把 world model 的 latent predictions 翻译成可执行动作。 |
| reinforcement learning, RL | 强化学习 | 让模型通过在线交互继续优化，而不是只依赖 expert trajectories。 |
| online video SFT | 在线视频监督微调 | 用交互中成功轨迹的 observation sequences 微调 world model。 |
| KL regularization | KL 正则 | 限制更新后 world model 的 latent feature distribution 不要偏离预训练模型太多。 |
| reconstruction-based reward | 基于重建的一致性奖励 | 比较 imagined trajectory 和真实执行 trajectory 的相似度，作为 actor RL 的 dense reward。 |
| dense reward | 稠密奖励 | 相比成功/失败 0/1 奖励，提供每段轨迹的连续优化信号。 |
| Flow Matching | 流匹配 | 视频生成和动作生成的基础生成建模框架。 |
| Flow-SDE | 流随机微分方程 | 给 flow-based policy 引入随机性和可计算 likelihood，使其能做 RL。 |
| LIBERO-Object | LIBERO 物体任务 | 本文的短/中程对象操作评测。 |
| RLBench Water Plants | RLBench 浇水任务 | 本文的长时程多步技能评测。 |
| recovery behavior | 恢复行为 | 失败后重新定位、再次抓取等纠偏动作，是 video SFT 希望让 world model 学到的内容。 |

## 论文主线

这篇论文的核心问题是：World-Action Models（WA/WAM）已经显示出比普通 VLA 更强的预测结构和泛化能力，但大多仍依赖 expert trajectories 做 supervised learning。这样训练出来的模型会被示范分布限制，缺少通过真实交互不断变好的能力。WAM-RL 想回答：能不能把 reinforcement learning 接入 WA 范式，而且不只是调 actor，还要让 world model 在线更新？

![[papers/images/qian2026wam-rl/page4_full.png|700]]

**Figure 1 / WAM-RL 总览。** 左边是以往 RL 方法：world model / VLM 固定，只优化 actor，用 sparse 0/1 reward，能力上限受固定表示限制。右边是 WAM-RL：world model 通过 successful trajectories 做 video SFT，并用 KL regularization 稳定 latent space；actor 则用 reconstruction reward 优化，让真实执行结果贴近 world model 的想象。

作者的核心观点是：WA model 的主要能力来自 world model，因为它捕捉未来视觉动态和隐式规划结构；actor 更像 translator，把 world model latent space 中的计划翻译成动作。因此短时程任务里 actor-only RL 可能能涨分，但长时程任务里 world model 的预测误差会累积，actor 不能靠自己修正错误预测。要提升长时程能力，必须让 world model 和 actor co-evolve（共同演化）。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| 首次把 RL 系统性引入 World-Action paradigm。 | Flow-SDE actor RL + online video SFT for world model。 | LIBERO 和 RLBench 结果。 | 概念贡献清楚，但实验规模偏小。 |
| WA 模型不能只优化 actor，world model 也要在线更新。 | successful rollouts 做 video SFT，KL 稳定 latent space。 | RLBench 上 actor-only 18%，Base 19%，WAM-RL 22%；Figure 3 recovery behavior。 | 长时程方向有支持，但数值提升还不大。 |
| reconstruction reward 能给 actor 更密集的优化信号。 | imagined future vs executed observation similarity。 | Pixel MSE 在 reward ablation 中最佳。 | 有效但仍是启发式 reward。 |
| reward discriminability 不等于优化效果。 | 比较 Pixel / Flow / DINO / V-JEPA2。 | Optical Flow 成功/失败区分更强，但 Pixel MSE 成功率更高。 | 这是本文最有意思的经验结论之一。 |
| KL regularization 可以稳定 world model online SFT。 | latent Gaussian approximation + KL 到 frozen pretrained model。 | 论文报告训练更稳定，但没有详细消融表。 | 合理但证据略弱。 |

## 摘要与核心贡献

摘要提出的矛盾是：Recent World-Action models 有很好的 generalization 和 data efficiency，但训练通常依赖 expert trajectories。这会造成两个限制：第一，策略只能在 demonstration distribution 内学细节，难以获得超出示范的 fine-grained manipulation skills；第二，模型不能通过 real-world interaction 持续改进。

WAM-RL 的回答是一个 joint optimization framework。World model 负责生成未来观测，actor 负责把预测转换成动作。训练时：

- world model 用 successful trajectories 做 online video self-supervised fine-tuning；
- KL regularization 防止 world model latent space 漂移导致 actor 失效；
- actor 用 reconstruction-based reward 做 RL，使真实执行轨迹和 imagined trajectory 一致。

作者的实验结论是：actor-only optimization 对短时程任务有帮助，但对长时程任务不够；联合优化 world model 和 actor 才能在 long-horizon settings 中更稳。

## 1. Introduction / 为什么 WA 模型需要 RL

WA models 和传统 VLA 的差别在于，它们不仅从图像/语言直接输出动作，还显式或隐式地建模未来世界状态。Future prediction（未来预测）为策略提供 predictive structure，这对 long-horizon decision making 是有益 inductive bias。

但当前 WA models 大多通过 supervised learning from expert trajectories 训练。这样会出现两个问题：

1. **能力被示范分布限制**：示范没有覆盖的微操作、失败边界、恢复行为，模型很难学到。
2. **不能在线自我改进**：真实执行时遇到新场景或错误，模型无法利用交互数据更新。

把 RL 加进去看似自然，但 WA 模型有特殊难点。普通 VLA RL 通常把视觉表示固定，只优化 action policy；WA 模型里 actor 深度依赖 world model latent space。如果 world model 在线变化，actor 的输入分布也会变，容易不稳定。反过来，如果 world model 完全固定，actor 的上限又被错误预测锁死。

因此 WAM-RL 的设计目标是：既让 world model 能适应在线轨迹，又不让 latent space 剧烈漂移；既优化 actor，又让 actor 的 reward 和 world model 的“想象”保持一致。

## 2. Related Work / 论文位置

### 2.1 World-Action Models

WA/WAM 路线从 video prediction policy、Unified World Models、Genie Envisioner、Cosmos Policy、LingBot-VA、DreamZero 等工作发展而来。共同思路是把未来视频预测和动作生成耦合起来，让机器人策略不只是“看图输出动作”，而是利用未来世界状态进行隐式规划。

本文尤其接近 Genie Envisioner-ACT / DreamZero：它把 WAM 看成 world model + actor 的组合，并追问这两部分如何通过在线交互继续提升。

### 2.2 Reinforcement Learning for VLA Models

VLA RL 后训练已经有很多方向，如 ConRFT、CO-RFT、ARFM、RIPT-VLA、SimpleVLA-RL、πRL、TwinRL-VLA、VLA-RFT、GR-RL、PLD 等。这些工作说明 RL 可以提升 VLA 的鲁棒性、探索和长时程能力。

WAM-RL 的差别是：它不只研究 policy side，而是明确研究 World-Action setting 中 world model 和 actor 的联合优化。也就是说，它把“世界模型是否应该一起 RL/后训练”变成中心问题。

## 3. Method / 方法细节

### 3.1 Flow Matching and Flow-SDE

Flow Matching 用一个 continuous-time vector field 把简单分布传输到数据分布。令 $x_0 \sim p_0(x)$ 是 Gaussian noise，$x_1 \sim p_{data}(x)$ 是视频或动作样本，模型学习：

$$
\frac{d x_t}{dt}=v_\theta(x_t,t)
$$

训练损失是：

$$
\mathcal{L}_{FM}
=
\mathbb{E}_{x_0,x_1,t}
\left[
\left\|v_\theta(x_t,t)-v^\*(x_t,t)\right\|^2
\right]
$$

普通 flow matching 是 deterministic generation，不天然适合 RL，因为没有 stochasticity，也难以计算 action likelihood。Flow-SDE 把 deterministic ODE 改成 stochastic differential equation：

$$
d x_t=v_\theta(x_t,t)dt+\sigma dW_t
$$

这样去噪过程就可以看成一串条件转移：

$$
p(x_{t-1}\mid x_t)=\mathcal{N}(x_{t-1};\mu_\theta(x_t,t),\sigma^2 I)
$$

动作序列 likelihood 可以分解为：

$$
\log \pi_\theta(a\mid s)=\sum_t \log p(x_{t-1}\mid x_t)
$$

于是就能用 policy gradient：

$$
\nabla_\theta J=
\mathbb{E}
\left[
\nabla_\theta \log \pi_\theta(a\mid s)A(s,a)
\right]
$$

这一节的作用是为 actor RL 提供数学接口：flow-based action model 通过 Flow-SDE 变成可做 RL 的随机策略。

### 3.2 Overall Framework

WAM-RL 建立在 WA paradigm 上。一个 policy 由两部分组成：

- world model：预测未来视觉/世界状态，提供隐式 planning；
- actor：消费 world model 的 latent features，把 imagined future 翻译成 actions。

作者认为 world model 是能力来源，actor 是 translator。因此优化目标也分两部分：

1. world model 用 online video SFT 从成功轨迹中学习更真实的 future prediction 和 recovery dynamics；
2. actor 用 reconstruction reward 学会让真实执行结果符合 world model 的 imagined plan。

### 3.3 Online Video SFT with KL Regularization

给定成功 rollout 中的 observation sequence $x_{1:T}$，world model 的视频训练目标是：

$$
\mathcal{L}_{video}
=
\mathbb{E}_{x_{1:T}}
\left[
\ell(f_\theta(x_{<t}),x_t)
\right]
$$

直观讲，就是让 world model 更擅长预测在线交互中真实出现过的成功轨迹。

但如果直接微调 world model，会导致 actor 输入的 latent feature distribution 改变。actor 原本学的是旧 world model 的 latent space，一旦 latent space 漂移，actor 会失效。为此作者构造 latent features 的 Gaussian approximation：

$$
p_\theta(z_t\mid x_{<t})=\mathcal{N}(z_t,\Sigma_\theta),
\quad
p_{old}(z_t\mid x_{<t})=\mathcal{N}(z_t^{old},\Sigma_{old})
$$

其中 $z_t=f_\theta(x_{<t})$，$z_t^{old}=f_{old}(x_{<t})$。当前 covariance $\Sigma_\theta$ 用 EMA 估计，old covariance 来自 frozen pretrained model。

KL 正则是：

$$
\mathcal{L}_{KL}
=
\mathbb{E}_t
\left[
D_{KL}
\left(
\mathcal{N}(z_t,\Sigma_\theta)
\|
\mathcal{N}(z_t^{old},\Sigma_{old})
\right)
\right]
$$

最终 world model loss：

$$
\mathcal{L}_{WM}
=
\mathcal{L}_{video}
+\lambda_{KL}\mathcal{L}_{KL}
$$

这个设计的直觉是：允许 world model 逐步适应在线数据，但不允许它突然改变 actor 所依赖的 latent geometry。

### 3.4 Action Model RL with Reconstruction-Based Reward

actor 的目标不是直接最大化任务 reward，而是让真实执行轨迹实现 world model 的 imagined future。设 world model 预测的未来观测是 $\hat{x}_{t+1:t+H}$，执行 actor 后真实环境给出的观测是 $x_{t+1:t+H}$，reward 定义为：

$$
r_t=\mathrm{sim}(\hat{x}_{t+1:t+H}, x_{t+1:t+H})
$$

这里 $\mathrm{sim}(\cdot,\cdot)$ 可以是多种相似度：

- Pixel MSE：低层像素重建误差；
- Optical Flow MSE：运动一致性；
- DINOv2 feature similarity：语义/视觉特征一致性；
- V-JEPA2 feature similarity：视频表征一致性。

actor 用 policy gradient 优化：

$$
\nabla_\phi J
=
\mathbb{E}
\left[
\nabla_\phi \log \pi_\phi(a_t\mid s_t)A_t
\right]
$$

这套 reward 的含义是：如果 actor 执行动作后真实世界演化和 world model 的想象一致，那么 actor 就更好地把 latent plan 翻译成了动作。

## 4. Experiment / 实验

### 4.1 Implementation Details

![[papers/images/qian2026wam-rl/page5_full.png|700]]

模型基于 Genie Envisioner-ACT architecture：world model 是 DiT-based video generator，actor 消费 world model 的 intermediate latent features 生成动作。实验使用 8 张 NVIDIA A800，训练 8 小时，采用 online RL + video fine-tuning 的混合设置。

评测基准：

- LIBERO-Object：object-centric manipulation tasks，关注组合泛化；
- RLBench Water Plants：多步机器人技能，长时程难度更高。

Baseline：

- Base：预训练 WA model，不做 RL；
- $\pi_{RL}$：actor-only reinforcement learning；
- Ours：world model + actor 联合优化。

### 4.2 Main Results

| Method | LIBERO-Object | RLBench Water Plants |
| --- | ---: | ---: |
| Base | 68% | 19% |
| $\pi_{RL}$ | 78% | 18% |
| Ours WAM-RL | 82% | 22% |

这个表要分任务读。LIBERO-Object 上，actor-only RL 从 68% 到 78%，说明短/中程对象操作中，只调 actor 已经能带来明显收益；WAM-RL 进一步到 82%，说明 world model SFT 还能补一点。

RLBench Water Plants 上，actor-only RL 从 19% 降到 18%，几乎没用；WAM-RL 到 22%。虽然绝对提升不大，但它支持作者的核心论点：长时程任务中，world model 的 prediction quality 限制了策略上限，只优化 actor 不足以解决累积预测错误。

### 4.3 Ablation Study on Reconstruction Loss

![[papers/images/qian2026wam-rl/page6_full.png|700]]

**Figure 2 / Table 2。** 左侧表格比较不同 reconstruction reward；下方柱状图显示成功/失败轨迹的 reward distribution。右侧 Figure 3 比较有无 video SFT 的恢复行为。

RLBench Water Plants 上 reward 消融：

| Method | Success Rate |
| --- | ---: |
| Base | 19% |
| $\pi_{RL}$ | 18% |
| Pixel MSE | 21% |
| Optical Flow MSE | 19% |
| DINO MSE | 16% |
| V-JEPA2 | 17% |

最有意思的是：Optical Flow 对 success / failure 的 reward separation 最大，但下游成功率不高；Pixel MSE 区分度弱一些，却成功率最好。作者的解释是，Pixel MSE 更贴近 world model 的训练目标，因此优化时更稳定，也会对 OOD actions 产生更直接的视觉偏差惩罚。

这说明 reward 的“判别力”不等于“可优化性”。在 world model + actor 这种耦合系统里，reward 需要和模型内部表示、训练目标对齐。

### 4.4 Ablation Study on Video SFT

Figure 3 展示 open-loop chunk 中是否出现 recovery。没有 video SFT 时，模型第一次 grasp fail 后继续沿错误轨迹走，最后进入 OOD。加入 video SFT 后，world model 会预测重新定位夹爪、再次抓取，最后成功。

这说明 online video SFT 的价值不是让图像更清晰，而是让 world model 学到 failure dynamics 和 corrective behavior。它开始不再默认执行完美，而是能想象“失败后如何修正”。

## 5. Conclusion / 结论与局限

WAM-RL 的结论是：World-Action models 的强化学习不应该只优化 actor。Actor-only RL 在短任务上可能有效，但长时程任务会受限于 world model 的预测质量。通过 reconstruction rewards 训练 actor，通过 online video SFT + KL regularization 训练 world model，二者可以 co-evolve，从而产生更稳的 recovery behavior。

论文也明确列出局限：

- KL regularization 保持稳定，但限制 world model 大幅适应新分布；
- reconstruction rewards 依赖预训练表征或手工相似度，成功/失败对比度有限；
- 当前 reward 还不够 task-aware；
- 需要更 scalable 的 world model adaptation 和更 discriminative 的 reward learning。

## 图表索引与讲解

| 图表 | 读图重点 | 关联问题 |
| --- | --- | --- |
| Figure 1 | 传统 RL 只优化 actor；WAM-RL 同时更新 world model 和 actor。 | 为什么 WA 模型 RL 不能只调动作头。 |
| Table 1 | LIBERO / RLBench 主结果。 | 联合优化相对 Base 和 actor-only RL 的收益。 |
| Figure 2 | 不同 reconstruction reward 的成功/失败分布。 | reward discriminability 和优化效果为什么不一致。 |
| Table 2 | Pixel / Flow / DINO / V-JEPA2 reward 消融。 | 哪种一致性信号更适合 actor RL。 |
| Figure 3 | 有无 video SFT 的 open-loop recovery 行为。 | world model 是否学到失败后的纠偏。 |

## 和你的论文库中其他条目的关系

- 对 [[@yu2026wm-dagger]]：WM-DAgger 离线用 world model 生成 recovery data，WAM-RL 在线用成功交互轨迹微调 world model。两者都强调 recovery dynamics 是世界模型进入机器人学习的关键。
- 对 [[@zhang2026contactworld]]：ContactWorld 关注 vision-tactile world model 如何支持 planning；WAM-RL 关注 world model 与 actor 如何通过 RL 后训练共同提升。
- 对 [[@tang2026frs]]：FRS 是在已有 flow policy 中做 action steering；WAM-RL 是在 WA 模型里通过 Flow-SDE 和 reconstruction reward 做 actor RL。
- 对 [[@qwen2026robotmanip]]：Qwen-RobotManip 解决大规模 VLA 数据对齐，WAM-RL 解决 WA 模型如何在线自我改进。未来可关注二者是否会合流：大规模预训练 + online WA/RL 后训练。

## 可追问点

1. 只用 successful rollouts 做 video SFT 是否会忽视失败轨迹中有价值的负样本？
2. Reconstruction reward 让执行贴近想象，但如果 world model 想错了，actor 是否会被错误想象牵引？
3. KL regularization 的强度如何设定？太强不适应，太弱 actor 输入分布崩。
4. Pixel MSE 为什么比 DINO/V-JEPA2 更有效？这是否只是因为任务视觉简单？
5. RLBench 只从 19% 到 22%，是否说明 world model online SFT 当前还很弱？
6. 如果加入触觉或状态 token，reconstruction reward 应该比较视觉、触觉还是 latent dynamics？

## 我的阅读笔记

这篇的价值在于把 WA 模型拆成了两个可优化对象：world model 和 actor。很多 VLA/VLM-RL 论文默认 backbone 或 world representation 是固定的，只优化动作头；WAM-RL 明确指出，对 World-Action Model 来说这种做法会遇到上限，因为 actor 的输入和规划来源就是 world model latent prediction。

但这篇目前更像一个方向性技术报告，而不是成熟 recipe。实验短，提升不算大，reward 设计仍粗。真正值得保留的是它的判断框架：如果一个机器人策略通过世界模型来想象未来，那么 RL 后训练要同时回答两个问题：世界模型是否变得更会想象失败和恢复，actor 是否更会把这个想象落到真实动作。

我会把它作为“WA/WAM 在线强化学习后训练”的入口。和 WM-DAgger 放在一起读，可以形成一条线：先用 world model 离线补 recovery data，再进一步让 world model 在在线交互中用成功轨迹更新自己。

