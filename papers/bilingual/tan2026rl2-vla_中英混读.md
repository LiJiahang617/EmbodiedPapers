---
tags:
  - bilingual-reading
  - deep-reading
source_pdf: "[[papers/pdfs/tan2026rl2-vla.pdf]]"
paper: "[[@tan2026rl2-vla]]"
images: "papers/images/tan2026rl2-vla/"
image_index: "[[papers/images/tan2026rl2-vla/index.md]]"
created: 2026-09-01
source_version: "arXiv 2607.26991v2, 2026-07-30"
reading_standard: "full bilingual reading"
---

# RL$^2$-VLA: Adaptive RL Latent Compositional Steering with Test-Time Scaling for Vision-Language-Action Models

paper:: [[@tan2026rl2-vla]]
pdf:: [[papers/pdfs/tan2026rl2-vla.pdf]]
images:: [[papers/images/tan2026rl2-vla/index.md]]
reading:: [[papers/bilingual/tan2026rl2-vla_中英混读.md]]

## 核心词汇速查

| English | 中文 | 在本文中的含义 |
| --- | --- | --- |
| VLA | 视觉-语言-动作模型 | 根据观测和语言指令生成机器人动作的基础策略 |
| inference-time steering | 推理时引导 | 不改主模型参数，在动作生成过程中改变候选分布 |
| test-time scaling | 测试时扩展 | 用更多计算、样本或不同条件换取更高的选择质量 |
| OOD | 分布外 | 指令、物体、背景、干扰物或环境偏离训练分布 |
| VLA latent $e_t$ | VLA 内部潜变量 | 从 action expert 隐藏状态聚合出的 RL 条件，保留任务和动作上下文 |
| flow matching | 流匹配 | 用 velocity field 将噪声逐步积分成动作轨迹 |
| QAM | Q-learning with Adjoint Matching | 训练 flow policy 的离线 RL 方法，避免直接穿过多步流反传 |
| compositional steering | 组合引导 | 将 VLA 和 RL 两个 velocity field 按权重混合 |
| SAFE | 失败检测器 | 读取 latent 序列并预测当前 rollout 是否会失败 |
| conformal prediction, CP | 保序预测 | 从成功 rollout 校准时间变化的失败分数上界 |
| action verifier | 动作验证器 | 给候选动作打分并选出执行者 |
| NRMSE | 归一化均方根误差 | scaling law 中衡量候选动作与 ground-truth action 距离的指标 |

## 摘要

### 原文摘要

> Despite the impressive visuomotor capabilities enabled by Vision-Language-Action models, their performance often degrades on challenging and out-of-domain tasks. Recent test-time steering and scaling methods improve performance without extensive data collection and retraining, but action samples often remain concentrated around similar behaviors and therefore inherit correlated failure modes. Moreover, existing methods apply the same intervention strategy at every timestep, regardless of whether the base policy is already likely to succeed. We introduce RL$^2$, an adaptive inference-time steering framework that leverages Reinforcement Learning on VLA Latents. A lightweight offline RL policy is conditioned on latents extracted from the VLA action expert, and its flow velocity is composed with the frozen VLA during inference. SAFE and conformal prediction activate this composition only when failure is predicted.

### 中文解读

作者抓住了 test-time scaling 的两个缺口。重复采样和 language rephrase 仍然来自同一 VLA，候选容易共享失败模式。另一个缺口是统一干预，每个时间步都引入扰动，成功状态也可能被改坏。RL$^2$ 的答案是把多样性来源换成独立训练的 latent-conditioned offline RL policy，再让 failure detector 决定干预时机。

论文的证据链分成两层。BridgeV2 validation 上的 scaling law 用 oracle verifier 研究候选数量、动作误差和状态类型的关系。SIMPLER、PolaRiS 和 PiperX 则检验这种关系能否在闭环任务中转化为成功率。前一层解释为什么 adaptive 有必要，后一层才是部署层面的结果。

## 论文主线

可以把整篇论文压缩成一条条件分支。

```text
冻结 VLA 的 action expert
        ↓ 提取 latent e_t
轻量 offline RL policy  π_RL(a | e_t)
        ↓ 提供不同于示范主模态的 velocity
SAFE LSTM + CP 判断当前是否可能失败
        ├─ 成功可能性高，保留 Repeated / Rephrase 的 VLA 候选
        └─ 失败可能性高，混合 VLA velocity 与 RL velocity
        ↓
RoboMonkey 或 CoVer verifier 选候选并执行
```

说到底，论文的研究问题不是「RL 能否替代 VLA」，而是「在什么状态下，额外的 RL 多样性值得支付」。因此组合方式、触发器和 verifier 是一个系统，不能只看 RL policy 单点精度。

## 贡献与结论对照

| 论文主张 | 方法位置 | 证据 | 仍然受限的地方 |
| --- | --- | --- | --- |
| VLA 候选在失败时存在相关模式 | Introduction、Scaling Law | failure tuple 上 Repeated、Rephrase 的误差下降慢，RL$^2$ 的幂律指数为 $-0.1081$ | tuple 由 ground-truth action 离线筛出，非在线标签 |
| latent-conditioned offline RL 能提供有用多样性 | Method、RL latent ablation | RL 高于 BC，latent RL 明显高于 raw observation 版本 | RL 与 BC 的增益幅度有限，未证明所有任务都能越过示范分布 |
| 组合引导应按失败状态启用 | SAFE、CP、Ablation | SAFE 在 $π_0$ OOD prompt 上 60.3%，Always 为 57.8%；PolaRiS 上 42.7% 对 33.8% | CP $α$ 需要任务级选择，触发误差会改变候选分布 |
| 框架可跨 VLA、verifier 和 benchmark | Experiments | OpenVLA、$π_0$、$π_{0.5}$，RoboMonkey、CoVer，SIMPLER、PolaRiS 和 PiperX | 真机 SAFE 需重新采 rollout，模块并非零校准成本 |

## 结构地图

| 原文 section | 这一节推进什么 | 关键线索 |
| --- | --- | --- |
| I Introduction | 定义相关失败、说明人类式自适应的直觉并提出两个问题 | diversity 应在 uncertainty 高时增加 |
| II Related Works | 将本文放入 IL/RL、inference-time steering、TTS 和 adaptive inference | RL$^2$ 选择 latent RL，而非调温度或改大 VLM |
| III Preliminaries | 给出 imitation learning、RL 和 classifier guidance 背景 | flow velocity 可被外部 guidance 改写 |
| IV Inference-Time Scaling Law | 将 success/failure 分开并拟合 $e\approx ak^b$ | 状态决定多样性是否有利 |
| V Method | 训练 RL latent policy，组合 velocity，SAFE 触发，verifier 选动作 | 主 VLA 冻结，推理时插入模块 |
| VI Experiments | 仿真、消融、扩展性、延迟、定性和真机 | 结果覆盖 prompt、environment 与本体变化 |
| VII Conclusion | 总结贡献并承认 steering、检测器和 verifier 的边界 | 未来方向是更强 guidance 与更稳触发 |

## 按原文 section 精读

### 1. Introduction

#### 本节在全文中的任务

引言先把 VLA 的 OOD 退化放在 deployment 场景中，再区分两类已有办法。discrete action selection 依靠多候选和外部 verifier，优点是保留原策略先验，缺点是候选都可能来自同一失败模式。differentiable steering 能越过原分布，代价是依赖物理 grounding 不稳定的 VLM 或误差累积的 world model。TTS 进一步增加样本，却没有改变这个相关性问题。

作者用一个简短的人类类比把设计目标说清楚。桌面空旷时人会直接抓杯子，杯子被遮挡时才换方向或先清障。这里的关键不是让每次动作都更随机，而是把多样性和不确定性绑定。论文随后提出两个问题，如何 steer，以及 when to steer。

#### 方法回应

如何 steer 的回答是 latent-conditioned offline RL policy 和 velocity composition。when to steer 的回答是 SAFE failure score 加 CP band。这个分解让后面的 scaling law 不只是结果图，而是触发机制的设计依据。

![[papers/images/tan2026rl2-vla/iid_vs_ood_concepts_draft_stretched_v5_vector.png|760]]

图题 `Types of In-domain and OOD Tasks` 把语言指令和任务环境两个 shift 放在一起。它支持的是问题动机，不是 RL$^2$ 的因果证据。图中引用的外部数字来自其他工作，不能当作本论文 benchmark 的基线。

#### 阅读判断

引言最有价值的地方是把「多样性」从普遍良药改成状态条件变量。后文若只报平均成功率，就无法检验这个判断，因此作者安排了 success/failure 分组的 NRMSE 实验。

### 2. Related Works

#### Imitation vs Reinforcement Learning for VLAs

行为克隆在大规模 offline demonstrations 上学习 $π_\beta$，因此拥有强的动作先验，却受示范覆盖限制。端到端 RL 可以探索高价值行为，但更新完整 VLA 需要高算力和稳定的优化。RL$^2$ 选择中间位置，冻结 foundation VLA，只训练小的 RL head，利用 RL 改变候选分布而不承担重训主模型的成本。

#### Inference-Time Steering 与 Test-Time Scaling

RoboMonkey、CoVer 等方法从候选中选动作，DynaGuide、VLS 等方法在生成过程中加入 guidance。Repeated 与 Rephrase 分别扩大同一指令下的样本数和语言条件多样性。RL$^2$ 的新增点不在于又一个 verifier，而在于把独立 offline RL 产生的行为先验接入同一候选生成过程。

#### Adaptive Inference for VLAs

已有工作会根据不确定性、动作一致性或 deliberation 需求动态增加计算。RL$^2$ 采用 failure-centric 视角，不调整同一 policy 的 temperature，而是用 SAFE 预测失败并切换到另一种 steering source。这个选择也带来新的依赖，SAFE 的跨任务和跨本体校准必须可靠。

### 3. Preliminaries

#### Imitation learning 与 RL 目标

数据 tuple 写成 $(o_i,a_i,\ell_i)$，VLA 预测长度为 $H$ 的 action chunk，并最大化

$$
\max_\theta \mathbb{E}_{(a_{t:t+H},o_t,\ell_t)\sim\mathcal D}
\left[\log \pi_\theta(a_{t:t+H}\mid o_t,\ell_t)\right].
$$

RL 则在 POMDP 中最大化折扣回报

$$
R=\mathbb E\left[\sum_{t=1}^{T}\gamma^{t-1}r^t\right].
$$

这两个目标对应全文的互补关系。IL 贡献稳定的行为先验，RL 贡献可离开 dominant demonstration modes 的候选。

#### Classifier guidance for flow matching

流匹配 policy 以 velocity field $v(o,a,\ell,k)$ 将噪声动作轨迹运输到可行动作。外部 guidance $g$ 可写成

$$
\hat v=v(o_t,a_{t:t+T},\ell_t,k)+\lambda g(o_t,a_{t:t+T},\ell_t).
$$

RL$^2$ 不需要一个可微的语言评分器，而是让 RL policy 的 velocity 充当 guidance。这样做的假设是 latent 中已经包含足够的状态和任务信息。

### 4. Inference-Time Scaling Law

#### 实验构造

作者在 BridgeV2 validation tuples $(s,a^*,I)$ 上运行 $π_0$，按 base action 的 NRMSE 选出最高的 1024 个 failure tuples 和最低的 1024 个 success tuples。NRMSE 为

$$
\mathrm{NRMSE}=\sqrt{\frac1N\sum_{i=1}^{N}
\left(\frac{a_i-a_i^*}{\max_T a_i-\min_T a_i^*}\right)^2}.
$$

这里 $N$ 是 flatten 后的动作维度，$T$ 是用于归一化的 tuple 集合。作者随后比较 Repeated、Rephrase、RBF、独立 RL、Concat、Residual、RLT 和 RL$^2$。

#### 结果与解释

![[papers/images/tan2026rl2-vla/nrmse_scaling_plots_v6.png|760]]

图题 `Test-time Scaling Laws` 的核心观察是，误差随样本数大致服从 $e\approx ak^b$，但 $a,b$ 在两种状态下不能混读。

| tuple 集合 | 方法 | $a$ | $b$ | 读法 |
| --- | --- | ---: | ---: | --- |
| failure | Repeated | 0.4099 | -0.0438 | 同一 policy 的重复样本下降慢 |
| failure | Rephrase | 0.4073 | -0.0829 | 语言改写带来有限多样性 |
| failure | RBF | 0.4147 | -0.0988 | 早期排斥提高分散度 |
| failure | RL$^2$ | 0.3983 | -0.1081 | 失败状态下下降最快 |
| success | Rephrase | 0.0385 | -0.3243 | 成功状态的低误差基线 |
| success | RL$^2$ | 0.0468 | -0.3250 | 指数相近但误差起点更高 |

failure 上，RL$^2$ 的较低 $a$ 和更负 $b$ 表明候选既多样又保留质量。success 上，VLA 已经接近 ground truth，额外 RL 扰动把部分好动作推远，所以 RL$^2$ 反而不如 Rephrase。这个结果支撑 adaptive，而不是证明 RL$^2$ 在所有状态都更强。

#### 证据边界

这个分析使用 ground-truth action 和 oracle verifier。它适合回答候选分布的潜在上限，不等同真实部署里的 failure detector。作者把这一点作为设计动机，却没有给出 oracle 到 SAFE 的严格校准转移定理。

### 5. Method

#### 5.1 RL Latent Policy Training

作者先把每个 BridgeV2 或 DROID tuple 送进冻结 VLA，保存 action expert latent，得到 $(o,a,\ell,e)$ 数据。latent aggregation 沿 token、horizon 和 diffusion 维度采用 first、last、mean 或 concat，具体选择在 validation 上确定。

直接穿过多步 flow matching 对 critic 反传会数值不稳。QAM 用 adjoint state $\tilde g_t$ 做 step-wise matching。终点条件为

$$
\tilde g_1=-\tau\nabla_{a_1}Q(s,a_1),
$$

反向 ODE 为

$$
d\tilde g_t=-\nabla_{a_t}[2f_\beta(s,a_t,t)-a_t/t]\tilde g_t\,dt.
$$

actor velocity $f_\theta$ 最小化

$$
\mathcal L_{AM}=\mathbb E\int_0^1
\left\|\frac{2(f_\theta-f_\beta)}{\sigma_t}+\sigma_t\tilde g_t\right\|_2^2dt,
\qquad \sigma_t=\sqrt{2(1-t)/t}.
$$

QAM 的固定点是行为正则化分布

$$
\pi(a\mid s)\propto\pi_\beta(a\mid s)\exp(\tau Q(s,a)).
$$

直觉上，$π_\beta$ 防止离开示范支持集太远，$Q$ 将概率质量推向高回报区域，$τ$ 控制偏离幅度。论文的 RL 对 BC 消融只改变训练方式，未改变这套组合接口。

训练规模为 $π_0$ latent 在 BridgeV2 上 500k steps、约 4.5 小时，$π_{0.5}$ latent 在 DROID 上 1M steps、约 9 小时，均用两张 L40。QAM 主要超参是 batch 256、$γ=0.99$、学习率 $3\times10^{-4}$、10 个 critic、10 个 flow steps；horizon 分别为 4 和 15，$τ$ 分别为 0.1 和 0.02。

#### 5.2 Compositional Steering

对 flow-matching VLA，作者在每一个 flow step 混合两套 velocity。

$$
v_{comp}=w v_{VLA}+(1-w)v_{RL},
\qquad w\sim\mathcal N(0.5,0.25),\quad w\in[0,1].
$$

每个样本可以取不同的 $w$，因此候选同时受到 VLA prior 和 RL diversity 影响。$w$ 越大越贴近示范，越小越偏向 RL policy。这个权重是采样规则，不是通过在线奖励逐样本优化的控制量。

OpenVLA 是 autoregressive action head，不能直接混合 flow velocity。作者采用 Gaussian perturbation，把 VLA 和 RL action samples 等量混合拟合高斯，再从中重采样。两种 VLA 的 steering 运算因此并不完全同构，跨模型比较要保留这个差异。

![[papers/images/tan2026rl2-vla/architecture_draft_v9.png|760]]

图题 `RL$^2$ Framework` 显示了 latent 提取、RL guidance、SAFE 分支和 verifier 的顺序。flow 模型走 velocity composition，OpenVLA 走 Gaussian perturbation，这个旁注是理解复现实验的关键。

#### 5.3 Failure Detection for Adaptive Steering

SAFE 使用 LSTM 读取到当前为止的 latent 序列，输出

$$
s_t=f_\psi(e_{0:t})\in[0,1].
$$

作者为每个任务采集三种 seed、每种 100 个 rollout，按 60% 和 40% 分训练与验证。BCE 在所有时间步累积。对验证集中的成功 rollout，CP 构造单侧 band

$$
C_\alpha=\{[{-\infty},\mu_t+h_t]\}_{t=1}^{T}.
$$

当 $s_t>\delta_t=\mu_t+h_t$ 时启动组合引导，否则回到 base VLA 的 Repeated 或 Rephrase 候选。成功 rollout 在置信度 $1-\alpha$ 下不应越过 band，这是减少误触发的约束，不是保证失败一定被抓到。

不同任务的最佳 $α$ 不同。作者从 0.05 到 0.50 扫描，用 balanced accuracy

$$
\mathrm{BalAcc}(\alpha)=\tfrac12(\mathrm{TPR}(\alpha)+\mathrm{TNR}(\alpha))
$$

选 top-3，再做实际任务评估。该 heuristic 可获得最多约 88.5% 的最大性能收益，但仍需要新任务的 validation rollout。

#### 5.4 Action Verification 与算法流程

给定候选 $\hat A_t=\{\hat a_t^n\}_{n=1}^{N}$，verifier 输出

$$
r_t^n=\mathcal V_\theta(o_t,\hat a_t^n,\ell_t),
\qquad \hat a_t^*=\hat a_t^{\arg\max_n r_t^n}.
$$

RoboMonkey 使用 preference learning，CoVer 使用 contrastive learning。两者都被当作 reward model，但它们对视觉、语言和动作轨迹的偏好并不相同，因此 verifier 是系统假设的一部分。

部署循环可以读成下面的伪代码。

```text
e_t ← action-expert latent
s_t ← SAFE(e_0:t)
if s_t > CP band:
    sample w and noise actions
    integrate v_comp = w v_VLA + (1-w) v_RL
else:
    sample base-VLA candidates
score every candidate with verifier
execute highest-scoring action
```

### 6. Experiments

#### 6.1 设置、数据集、基线与指标

| 场景 | 基础 VLA | RL steering | verifier | 任务与 shift |
| --- | --- | --- | --- | --- |
| SIMPLER in-domain | OpenVLA | V-GPS CQL | RoboMonkey | 4 个 BridgeV2 标准任务 |
| SIMPLER OOD prompt | $π_0$ | QAM | CoVer | 4 个已知任务加 red-team prompt |
| SIMPLER OOD environment | $π_0$ | QAM | CoVer | orange juice、换背景、distractor、tape measure、toy dinosaur |
| PolaRiS OOD prompt | $π_{0.5}$ | QAM | CoVer | Move Latte Cup、Tape into Container、Pan Cleaning |
| PiperX real world | $π_0$ | QAM | CoVer | 2 个 OOD prompt 和 2 个 OOD environment |

OpenVLA 按 RoboMonkey 协议先由 9 个动作样本拟合高斯，再重采样 32 个。$π_0$ 和 $π_{0.5}$ 按 CoVer 协议使用 8 个 rephrases、每个 5 个 action samples。每个实验 50 次，报告三个 seed 的均值和标准差。指标主要是 success rate，PolaRiS 另报 progress rate。

#### 6.2 SIMPLER 与 PolaRiS 主要结果

##### OpenVLA，SIMPLER in-domain

| Task | Vanilla | Repeated | Compose-Always | Compose-Adaptive |
| --- | ---: | ---: | ---: | ---: |
| Eggplant in Basket | 53.3 | 75.3 | 80.7 | 77.3 |
| Stack Cubes | 33.3 | 42.7 | 27.3 | 44.0 |
| Spoon on Towel | 43.3 | 27.3 | 30.0 | 46.7 |
| Carrot on Plate | 17.3 | 15.3 | 19.3 | 22.7 |
| Average | 36.8 | 40.2 | 39.3 | 47.7 |

adaptive 相对 Repeated 平均提升 7.5 个百分点，Stack Cubes 和 Spoon on Towel 的收益最大。Eggplant 上 Compose-Always 高于 adaptive，说明成功状态的保护有时会牺牲一部分可用 steering。

![[papers/images/tan2026rl2-vla/openvla_simpler_main_results_IID_v4.png|700]]

##### $π_0$，SIMPLER OOD prompt

| Task | Vanilla | Rephrase | Compose-Always | Compose-Adaptive |
| --- | ---: | ---: | ---: | ---: |
| Eggplant in Basket | 74.0 | 90.7 | 91.3 | 93.3 |
| Stack Cubes | 13.3 | 28.7 | 38.7 | 40.7 |
| Spoon on Towel | 24.7 | 36.0 | 50.7 | 50.7 |
| Carrot on Plate | 48.7 | 45.3 | 50.7 | 56.7 |
| Average | 40.2 | 50.2 | 57.8 | 60.4 |

adaptive 相对 Rephrase 提升 10.2 个百分点，最高单任务增益是 Carrot on Plate 的 11.4 个百分点。论文正文把平均提升写作 10.1，项目页数组四舍五入后得到 10.2，阅读时应以表中精确均值为准。

![[papers/images/tan2026rl2-vla/pi0_simpler_main_results_IID_v4.png|700]]

##### $π_0$，SIMPLER OOD environment

| Task | Vanilla | Rephrase | Compose-Always | Compose-Adaptive |
| --- | ---: | ---: | ---: | ---: |
| Orange Juice on Plate | 31.3 | 35.3 | 41.3 | 43.3 |
| Spoon on Towel (Google) | 46.0 | 44.7 | 54.0 | 59.3 |
| Tape Measure in Basket | 18.7 | 52.0 | 44.7 | 59.3 |
| Toy Dinosaur on Towel | 48.0 | 49.3 | 46.0 | 53.3 |
| Average | 36.0 | 45.3 | 46.5 | 53.8 |

adaptive 相对 Rephrase 提升 8.5 个百分点。Tape Measure 的 Always 低于 Rephrase，而 adaptive 反超，正好体现触发器避免无条件扰动的价值。

![[papers/images/tan2026rl2-vla/pi0_simpler_main_results_OOD_v4.png|700]]

##### $π_{0.5}$，PolaRiS OOD prompt

| Task | 指标 | Vanilla | Rephrase | Compose-Always | Compose-Adaptive |
| --- | --- | ---: | ---: | ---: | ---: |
| Move Latte Cup | Success | 18.7 | 48.7 | 55.3 | 66.0 |
| Tape into Container | Success | 12.7 | 22.0 | 22.0 | 28.7 |
| Pan Cleaning | Success | 11.5 | 24.7 | 24.0 | 33.3 |
| Average | Success | 14.3 | 31.8 | 33.8 | 42.7 |
| Average | Progress | 40.0 | 55.2 | 55.8 | 63.0 |

adaptive 的平均 success 比 Rephrase 高 10.9 个百分点，progress 高 7.8 个百分点。Move Latte Cup 的 success 提升 17.3 个百分点，是论文报告的最高 task-wise gain。

#### 6.3 消融实验

| 消融问题 | 对照 | 结果 | 解释 |
| --- | --- | --- | --- |
| RL 是否优于 BC | $π_0$，RL / BC | 57.8 / 55.8 | RL 增加约 2.0 个百分点 |
| RL 是否优于 BC | $π_{0.5}$，RL / BC | 33.8 / 29.7 | RL 增加约 4.1 个百分点 |
| latent 是否关键 | OpenVLA latent / raw observation | 39.3 / 0.5 | raw observation 的 V-GPS 版本几乎失效 |
| 触发器 | SAFE / CoVer / Always，$π_0$ OOD prompt | 60.3 / 57.8 / 57.8 | SAFE 的分数更能分开成功与失败 |
| 触发器 | SAFE / CoVer / Always，$π_{0.5}$ | 42.7 / 39.8 / 33.8 | 自适应在长时程 PolaRiS 更重要 |

raw observation 结果不能简单解读成「所有视觉 encoder 都不行」。QAM 原本更适合 proprioceptive input，作者无法在 BridgeV2 上成功训练 raw-observation QAM，因此改用 OpenVLA 和 V-GPS CQL。这里同时改变了 backbone 与 RL 算法，归因要保守。

#### 6.4 样本扩展、延迟与定性分析

在 $π_0$ OOD prompt 上，8 rephrases $×$ 5 samples 的 success 是 adaptive 60.3%、Always 57.8%、Rephrase 50.2%。固定 40 个样本时，单 prompt 扩样本到 40 的结果是 47.3%、43.7%、42.0%。单样本则为 44.5%、39.2%、40.2%。数量和条件多样性叠加后 RL$^2$ 最占优势，最高相对基线提升约 18.7 个百分点。

在 RTX 5090 上，batch 128 时 $π_0$ forward 为 3093 ms，CoVer 为 145 ms，QAM 为 48 ms，SAFE 为 2 ms。H100 上对应值为 698、45、25 和 1 ms。额外模块轻，但 verifier 和 VLA forward 仍是主要成本。

![[papers/images/tan2026rl2-vla/scaling_rephrase_and_samples_plot_v4.png|700]]

![[papers/images/tan2026rl2-vla/RL2_visualization_cover_samples_v3.png|760]]

定性图中，失败状态的 Rephrase 候选常朝错误 distractor 或远离任务物体，导致来回摆动。组合引导把更多样本推向任务物体，再由 CoVer 选取其中一个。PCA heatmap 也显示 steering 后分布更接近 ground-truth action，但这仍是动作空间的可视化，不是闭环成功的单独证明。

#### 6.5 PiperX 真机

作者用与 $π_0$ 仿真相同的模型权重、QAM 和 CoVer，在 PiperX 加 Realsense D405 上测试。SAFE 不能直接从仿真迁移到真机，因此重新收集四个 in-domain 任务的 rollout 做训练和 CP calibration。每个任务每 seed 10 次，三个 seed 共 120 次。

| 场景 | Vanilla | Rephrase | Compose-Always | Compose-Adaptive |
| --- | ---: | ---: | ---: | ---: |
| OOD prompt，Carrot on Plate | 13.3 | 36.7 | 40.0 | 63.3 |
| OOD prompt，Cube in Toolbox | 3.3 | 40.0 | 50.0 | 50.0 |
| OOD prompt 平均 | 8.3 | 38.4 | 45.0 | 56.7 |
| OOD environment，Tape in Toolbox | 16.7 | 36.7 | 33.3 | 53.3 |
| OOD environment，Screwdriver in Toolbox | 6.7 | 16.7 | 20.0 | 33.3 |
| OOD environment 平均 | 11.7 | 26.7 | 26.7 | 43.3 |

adaptive 相对 Rephrase 的两组平均增益分别是 18.3 和 16.6 个百分点，合并后约 17.5。项目页 headline 写 19.5，这与正文表格不一致，可能来自不同聚合或版本。不能把两个数字混成单一结论。

![[papers/images/tan2026rl2-vla/real_robot_tape_in_toolbox_safe_viz_v6.png|760]]

Tape in Toolbox 的示意体现了触发时机。Rephrase 能抓住 tape，却常撞 toolbox 边缘。Always 过早改变接近动作。Adaptive 先沿用准确的 VLA 接近轨迹，SAFE 发现潜在失败后才提高搬运高度。

### 7. Conclusion

论文结论是一个模块化部署主张。轻量 offline RL 在 latent 上训练即可改变候选分布，success/failure scaling law 给出何时引导的依据，SAFE 和 CP 把引导变成条件开关，多个 VLA、verifier、仿真和真机实验显示这条链能工作。

作者承认三类后续问题。steering function 尚未与大型 VLM/VLA differentiable guidance 正面对比。CP $α$ 仍要额外 validation，未来希望直接用更大规模 offline data 训练 failure detector。verifier 假定过强，后续可把 verifier 与 RL steering policy 联合训练。

## 方法细节汇总

| 组件 | 输入 | 输出 | 训练或推理时机 | 关键超参 |
| --- | --- | --- | --- | --- |
| VLA action expert | observation、language | base velocity 或 action | 预训练后冻结 | $π_0$、$π_{0.5}$、OpenVLA |
| latent aggregation | hidden tensor $E$ | $e_t$ | 离线预处理和部署 | first、last、mean、concat |
| QAM policy | $e_t$、noisy action、flow time | $v_{RL}$ | 离线 RL | batch 256、10 critics、10 flow steps |
| composition | $v_{VLA}$、$v_{RL}$、$w$ | $v_{comp}$ | 失败预测时推理 | $μ_w=0.5$、$σ_w=0.25$ |
| SAFE | $e_{0:t}$ | $s_t$ | rollout 训练和逐步推理 | LSTM、BCE |
| CP | successful validation scores | $δ_t$ | 每任务校准 | $α$ 0.05 到 0.50 |
| verifier | observation、candidate、instruction | candidate score | 每次候选选择 | RoboMonkey 或 CoVer |

## 实验设置、数据集、基线、指标

论文覆盖的任务数量是 4 个 SIMPLER in-domain、4 个 SIMPLER OOD prompt、4 个 SIMPLER OOD environment、3 个 PolaRiS OOD prompt 和 4 个 PiperX 真机任务。OOD environment 的变化包括新物体、背景和 distractor，不等同于目标任务从未出现过。主指标是闭环 success rate，PolaRiS 同时使用 progress rate，scaling law 使用 NRMSE 和 oracle selection。

基线的比较关系应这样读。Vanilla 测 base VLA，Repeated 或 Rephrase 测同一 VLA 的 test-time scaling，Compose-Always 测组合引导但去掉 adaptive，Compose-Adaptive 才是完整 RL$^2$。这套排列把「多样性来源」和「触发时机」分开了。

## 主要结果、消融或对比

最稳定的方向是完整 adaptive 方法在 OOD prompt 和 OOD environment 上都高于 Rephrase。最能说明机制的反例是部分 in-domain task 上 Compose-Always 高于 adaptive，或者 success tuple 上 RL$^2$ 的 scaling 起点更差。论文没有掩盖这些反例，而是用它们解释为什么要做 state-conditional steering。

## 图表、公式与表格线索

| 图表 | 读图重点 | 证据级别 |
| --- | --- | --- |
| Fig. 1 poster overview | 失败时 steering、成功时保留 VLA 的总览 | 设计示意 |
| Fig. 2 IID/OOD concepts | 语言和环境 shift 的动机 | 外部引用的背景数字 |
| Fig. 4 scaling plots | success 与 failure 的不同幂律 | oracle 离线诊断 |
| Fig. 5 architecture | latent、QAM、SAFE、verifier 的数据流 | 方法结构 |
| Fig. 6–8 benchmark plots | OpenVLA、$π_0$、PolaRiS 的成功率 | 闭环仿真结果 |
| Fig. 9 scaling samples | 样本数和 rephrase 数的交互 | 扩展性实验 |
| Fig. 10 alpha heuristic | balanced accuracy 选 CP $α$ | 校准策略 |
| Fig. 11–12 qualitative | 错误候选如何被推向任务物体 | 定性解释 |
| Fig. 13–15 real robot | tape、screwdriver 等失败恢复 | 真机闭环结果 |
| Eq. NRMSE | 定义 failure/success tuple | 数据筛选规则 |
| Eq. QAM | 行为正则化 RL flow policy | 训练目标 |
| Eq. composition | VLA 与 RL velocity 的混合 | 推理机制 |
| Eq. CP | 时间变化的触发上界 | 自适应开关 |

## 主张-证据-边界矩阵

| 主张 | 直接证据 | 证据边界 |
| --- | --- | --- |
| RL$^2$ 可提升 OOD prompt 成功率 | $π_0$ 40.2 → 60.4，PolaRiS 31.8 → 42.7 | 任务多为 VLA 已见的操作，变化主要在 prompt 或场景 |
| 自适应优于 Always | OOD environment 53.8 对 46.5，PolaRiS 42.7 对 33.8 | SAFE 需要任务级训练和 CP 校准 |
| latent 比 raw observation 更适合 steering | OpenVLA 39.3 对 0.5 | 对照同时更换了 QAM/V-GPS 设定，不能单独归因表示 |
| RL 比 BC 有增益 | $π_0$ +2.0，$π_{0.5}$ +4.1 | 增益中等，未给出示范外行为的质量分布 |
| 真机可迁移 | PiperX 两组平均 56.7 和 43.3 | SAFE 重新采样训练，真实规模小，项目页和正文数字不一致 |
| scaling law 支持状态条件引导 | failure 与 success 的拟合曲线方向相反 | oracle verifier 和 ground-truth action 不可在线获得 |

## 局限与可追问点

这里需要把作者自述和外部审阅分开。作者承认缺少大型 differentiable steering 对照、CP $α$ 选择仍需额外评估、verifier 假定较强。阅读时还应追问以下问题。

- SAFE 的 CP band 在新本体、新摄像机和新任务上是否保持 coverage。真机实验重新收集 rollout，回答不了跨域校准能否复用。
- verifier 的 ranking error 是否偏向某一类动作。若 CoVer 更喜欢视觉上平滑但物理上错误的轨迹，RL$^2$ 的候选多样性可能被错误选择抵消。
- 失败 tuple 按 base NRMSE 极端分位数构造，是否代表自然发生的失败，而不是人为挑出的最难样本。
- composition weight $w$ 的高斯分布只使用一个均值和方差，尚未报告不同权重分布的敏感度。
- offline RL 的高价值行为是否真的在示范支持集外，还是只是在 latent 条件下重排已有动作模式。
- 真机表格的 17.5 与项目页的 19.5 如何由同一批 rollout 聚合得到。引用时应保留版本和口径。

说真的，这篇工作的工程价值高于它的理论新颖度。它把 latent、RL、failure detector 和 verifier 接成了可替换接口，适合做系统级消融；但每个接口都带有数据或校准成本，不能把「冻结 VLA」理解成零额外准备。

## 与当前库的连接

RL$^2$ 与 [[@pan2026vla-corrector-lightweight-detect]] 都在推理阶段处理失败，但前者改变候选分布，后者更接近检测后纠正。与 [[@qian2026wam-rl]] 的联系在于都把 RL 放在 world-action 或 action generation 的后端，差异是 RL$^2$ 不更新主 VLA，也不依赖在线环境回报。与 [[@feng2026wam-ttt]] 和 [[@zhou2026zero-wam]] 的人类视频接口不同，RL$^2$ 的 task condition 仍是 VLA 原有语言和观测，新增信息来自内部 latent 与离线 RL。

两篇同日阅读的论文不在一个尺度上。RL$^2$ 解决已有任务在 prompt、物体和环境 shift 下如何恢复，Zero-WAM 解决没有目标任务机器人示范时如何从 human video 得到 task specification。一个是 inference-time candidate control，一个是 training-time interface and model design。

## 精读路线 / 为什么需要回看

回看时可以沿四个问题走。先看 Fig. 4 和 NRMSE 定义，确认 success/failure 是怎样构造的。再看 QAM 和 composition，弄清多样性来自哪里。然后读 SAFE、CP 和 alpha heuristic，判断触发器有没有把 scaling law 变成可部署规则。最后重算四组 benchmark 的平均值，并对照真机表格和项目页，避免把 17.5 与 19.5 当成同一个数字。

如果要复现，优先记录 VLA latent 的抽取位置、aggregation 方式、RL policy horizon、verifier 版本和 CP 校准数据。少掉其中任何一项，结果都可能从「自适应 steering」变成另一种候选采样基线。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
