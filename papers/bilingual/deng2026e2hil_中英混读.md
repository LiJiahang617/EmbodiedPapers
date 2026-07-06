---
tags:
  - deep-reading
source_pdf: "[[papers/pdfs/2601.19969v1.pdf]]"
paper: "[[@deng2026e2hil]]"
images: "papers/images/2601.19969v1/"
image_index: "[[papers/images/2601.19969v1/index.md]]"
created: 2026-06-28
---

# E2HiL: Entropy-Guided Sample Selection for Efficient Real-World Human-in-the-Loop Reinforcement Learning

## 论文主线

这篇论文的主线是：真实机器人 Human-in-the-Loop Reinforcement Learning（人类在环强化学习，HiL-RL）确实能通过人工纠偏加速在线策略学习，但现有方法通常把 replay buffer（回放缓冲区）里的人工接管样本和机器人自探索样本近似一视同仁。问题不只是“人工样本贵”，而是不同样本对 policy entropy（策略熵）的影响非常不一样：有些样本会让策略过快走向低熵、低探索的 shortcut（捷径）状态，有些样本几乎不改变熵，只带来噪声或重复更新。E2HiL 的核心判断是，人工干预样本应该按其对 entropy dynamics（熵动态）的影响被主动筛选，而不是被随机均匀采样。

方法上，作者从 entropy-regularized RL（熵正则化强化学习）的 actor objective 出发，把单个样本对策略熵变化的影响近似写成 action log-probability（动作对数概率）与 soft advantage（软优势）相关项的 covariance（协方差）。E2HiL 先估计每个样本的 influence value（影响值）`c(s_t, a_t)`，再用 batch 内动态上下界 `[ell, u]` 保留中等影响样本，剪掉过大影响的 shortcut samples 和过小影响的 noisy samples。这样做的目标不是最大化熵，也不是简单压低熵，而是让熵稳定下降，避免过早 entropy collapse（熵塌缩），同时减少人工接管成本。

实验上，论文在 Lerobot SO-101 真实机器人平台上做四个 manipulation tasks（操作任务），与 HIL-SERL 对比。E2HiL 在平均 success rate（成功率）上从 41.8 提到 83.9，在 intervention rate（人工接管率）上从 44.0 降到 33.9。按表格数值，这是成功率增加 42.1 个百分点、接管率减少 10.1 个百分点；论文文字把它表述为 42.1% higher success rate 和 10.1% fewer interventions。最重要的证据不是单个数值，而是 entropy curve 更平滑、Touch-Cube 中能继续探索第二个位置，以及 covariance 估计和实际熵导数之间出现明显对应关系。

![[papers/images/2601.19969v1/teaser1130_page1.png|700]]

## 结构地图

| 原文位置 | 作者在这一部分做什么 | 与全文主线的关系 | 关键图表 / 公式 |
| --- | --- | --- | --- |
| Abstract / Fig. 1 | 提出 E2HiL 的问题、方法和总结果 | 用“熵稳定下降”统领样本筛选、成功率提升和人工成本降低 | Fig. 1 |
| I. Introduction | 说明真实机器人 RL、HiL-RL 和人工接管成本的矛盾 | 把问题从“需要更多人工纠偏”转成“如何筛选有信息量的纠偏样本” | Fig. 1, 贡献列表 |
| II. Related Work | 对比 real-world RL、HiL-RL 和 entropy-regularized RL | 说明本文不是新 RL backbone，而是 sample-level entropy regulation（样本级熵调控） | 无独立图表 |
| III. Methodology | 从 RLPD actor objective 推导样本对策略熵的影响，并给出 entropy-bounded selection | 全文核心机制：用 covariance-based influence function 选择训练样本 | Eq. 1-12, Algorithm 1, Fig. 2 |
| IV. Experiments | 在真实 SO-101 平台验证性能、熵动态估计、人工样本分布和被剪样本特征 | 证明筛样本既提升任务表现，也对应可解释的 entropy dynamics | Table I-II, Fig. 3-6 |
| V. Conclusion | 总结并指出未来扩展到 VLA、多任务真实 RL 和更可靠价值估计 | 给出方法边界和后续方向 | 无 |

## 按原文 section 精读

### Section 0. Abstract / Overview

#### 高层故事流

摘要先确认 HiL-RL 的优势：人工接管能帮助复杂真实机器人操作更快收敛。但它马上指出低 sample efficiency（样本效率低）会把人工成本放大，因为系统需要大量 human interventions（人工干预）才能达到可靠成功率。E2HiL 的切口是 active sample selection（主动样本选择）：不是让人少接管，而是让已经收集到的人工样本更有效地进入更新。

摘要中最关键的机制是“stable reduction of policy entropy”。作者认为，策略熵如果骤降，策略会过早固化在局部行为；如果熵变化太弱，则样本对学习几乎没有贡献。E2HiL 因此构造 influence functions（影响函数），用 action probabilities（动作概率）与 soft advantages（软优势）的 covariance 估计样本对 entropy dynamics 的贡献，再保留中等影响样本。这个摘要其实已经把论文的三段论说完：熵动态可测，样本可筛，真实机器人训练更省人工。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| HiL-RL 能加速真实机器人在线 RL，但人工成本高 | 建立现实动机 | Abstract 第 1-2 句 | 成本主要用 intervention rate 衡量，没有直接报告人时成本 |
| 稳定降低 policy entropy 能改善 exploration-exploitation trade-off | 给方法提供理论直觉 | Abstract 中段 | 这是经验和理论结合的假设，依赖 critic / advantage 估计质量 |
| covariance of action probabilities and soft advantages 估计影响函数 | 给出核心技术 | Abstract 中段 | PDF 正文的推导较短，完整推导放在项目页 |
| 四个真实任务平均成功率更高、接管率更低 | 给出总结果 | Abstract 末尾, Table I | 论文表述的百分比更接近百分点差值 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| 图 | Fig. 1 | 随机采样 HiL-RL 与 entropy-guided sampling 的概念对比、Touch-Cube 收敛曲线和平均性能 | E2HiL 试图避免早期 entropy collapse，在更少人工接管下保留探索能力 |
| 数值 | Abstract / Table I | success rate 41.8 -> 83.9，intervention rate 44.0 -> 33.9 | 主张“更高成功率、更少人工干预” |

### Section I. Introduction

#### 高层故事流

Introduction 从 robotic manipulation（机器人操作）的长期难点切入：手写控制器难以泛化，pre-trained imitation policies（预训练模仿策略）虽然强，但遇到 out-of-distribution states（分布外状态）仍会失败。纯仿真 RL 又有 sim-to-real gap（仿真到现实差距），所以真实机器人 RL 很自然。但真实环境中 RL 面临两个硬问题：sample efficiency 低、sparse rewards（稀疏奖励）难学。HiL-RL 用人工纠偏降低探索难度，但随着状态动作维度和任务时长增长，人工样本需求仍然很高。

作者把现有 HiL-RL 的关键缺口定义为：无法区分哪些 intervention samples（接管样本）真正 informative（有信息量）。如果所有样本都均匀采样，策略可能被极端样本快速拉向低熵行为，或者被大量重复/无效样本拖慢。Fig. 1 把这个问题具象化为 entropy dynamics 和 policy improvement 的 trade-off：HIL-SERL 这类随机采样方法可能早期熵骤降，导致策略只学到一个局部位置；E2HiL 保持更平稳的熵下降，因此后续还能探索并学到另一个位置。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 真实机器人 RL 避免 sim-to-real，但样本效率和稀疏奖励更难 | 说明为什么不能只靠在线 RL 暴力探索 | Introduction 前两段 | 论文没有提出新 reward design |
| HiL-RL 可用人工 corrective takeovers 加速学习 | 说明 baseline 范式 | Introduction 中段 | 人工接管本身仍然昂贵 |
| 现有 HiL-RL 不能判断接管样本是否 informative | 提出本文问题定义 | Introduction 中后段 | 这是假设和经验观察，后文用 covariance 分布验证 |
| LLM-RL 中熵骤降会导致 premature convergence，机器人 RL 也观察到类似模式 | 借鉴 entropy mechanism 的理论直觉 | Introduction 中段 | 语言模型 token-level 熵和机器人 action-level 熵不完全等价 |
| E2HiL 用 influence functions 和 entropy-bounded selection 剪掉 shortcut/noisy samples | 给出方法预告 | Introduction 末段 | 依赖 soft advantage 估计可靠 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| 图 | Fig. 1 | HiL-RL random sampling vs. E2HiL entropy-based sampling | 说明样本不是同质的，极端 entropy influence 样本应被剪掉 |
| 贡献列表 | Introduction 末尾 | E2HiL 框架、sample-induced entropy dynamics、四个真实任务验证 | 明确本文不是提出新机器人硬件，而是提出样本筛选机制 |

### Section II. Related Work

#### 高层故事流

Related Work 分两条线。第一条是 Real-world RL for Robotic Manipulation（真实机器人操作强化学习）。作者回顾 off-policy / model-based RL、offline pretraining、reward shaping、success classifiers、reset-free learning 等方向，但指出这些方法往往会增加训练时间或没有降低人工成本到足够实用的水平。HiL-RL，特别是 HIL-SERL，通过人工纠偏取得了真实操作的强效果，但它依然把接管样本近似均匀处理。

第二条是 Entropy-Regularized Reinforcement Learning（熵正则化强化学习）。SAC、MPO、RLPD 等已经把 entropy bonus 作为探索和稳定训练的重要组件，但它们通常在 objective 或 temperature level（温度系数层面）调熵，没有建模“单个样本”对熵的影响。作者借鉴 LLM-RL 中对 entropy collapse 的分析，强调 sample-level entropy regularization（样本级熵正则）在机器人 RL 中还没有被充分探索。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 真实机器人 RL 的困难包括 sample efficiency、sparse rewards、human intervention cost | 将本文放入真实机器人学习问题空间 | II-A | 这篇没有系统比较所有真实 RL 类方法 |
| HIL-SERL 代表强 HiL-RL baseline，但均匀处理干预样本 | 直接定位 baseline 缺口 | II-A | HIL-SERL 的实现细节会影响对比公平性 |
| SAC/MPO/RLPD 使用 entropy-regularized objectives | 说明熵不是新概念 | II-B | 这些方法多为全局或温度层面的熵控制 |
| LLM-RL 中 covariance-based regularizers 可缓解 entropy collapse | 给 E2HiL 的 covariance 机制提供前史 | II-B | action-level robot policies 与 token-level LLM policies 存在 domain-specific differences |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| 文献定位 | II-A | Real-world RL、reward shaping、reset-free learning、HIL-SERL | E2HiL 关注高人工成本下的在线真实机器人 HiL-RL |
| 文献定位 | II-B | SAC、MPO、RLPD、Clip-Higher、Clip-Cov、KL-Cov | E2HiL 的新意在 sample-level entropy influence，而非单纯加 entropy bonus |

### Section III. Methodology

#### 高层故事流

Methodology 是全文最重要的部分。作者先把真实机器人操作建模为 MDP：状态包括视觉和本体感知，动作是末端执行器运动，奖励给任务目标，折扣因子平衡短期和长期回报。训练上，它沿用 RLPD 思路，把 replay buffer 和 demonstration buffer 结合，critic 用 Bellman target 回归，actor 最大化 `Q - alpha log pi` 的熵正则目标。

E2HiL 的改动是给 actor update 加一个 binary indicator（0/1 指示函数）`I(s_t, a_t)`。如果样本对熵的影响过大或过小，它就不参与 actor gradient；如果影响适中，它才参与更新。这个 objective 把 sample selection 直接接到策略优化里，而不是事后过滤数据集。

推导部分从 entropy change approximation 开始。直观上，策略熵变化可以近似由 action log-probability 和 logit change 的 covariance 决定。再把 RLPD actor gradient 写成 soft advantage 形式，得到单个动作 logit 的变化与 `pi(a|s) A_soft(s,a)` 成正比。代回去后，样本对熵变化的关键量就是 `log pi(a|s)` 与 `pi(a|s) A_soft(s,a)` 的 covariance。作者把负学习率乘上估计 covariance 定义为 influence value `c(s_t, a_t)`，再用动态区间 `[ell, u]` 做 entropy-bounded sample selection。

![[papers/images/2601.19969v1/pipeline1130_page1.png|700]]

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 真实操作 RL 建模为 MDP `M={S,A,rho,P,r,gamma}` | 给公式和 RLPD 更新提供基础 | III-A | 状态、动作和奖励细节没有展开到复现实验级别 |
| critic loss `L_Q` 和 actor loss `L_pi` 采用 RLPD/SAC 风格 | 表明 E2HiL 建在已有 off-policy entropy-regularized RL 上 | Eq. 1-2 | 性能依赖 baseline 实现和 critic 稳定性 |
| `I(s_t,a_t)` 只让 entropy-consistent samples 进入 actor update | 把样本筛选变成优化目标的一部分 | Eq. 3, Eq. 12 | 只屏蔽 actor gradient，critic 更新仍按普通损失 |
| entropy change 近似为 covariance | 建立“样本影响可估计”的理论桥 | Eq. 4, Eq. 9 | 文中承认早期 Q 不准会导致估计偏差 |
| 动态上下界 `[ell,u]` 剪掉过大/过小 `|c|` | 实现 shortcut/noisy sample pruning | Eq. 11 | 具体 percentile 是启发式，实验中用 5th 和 90th |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| 公式 | Eq. 1 | `L_Q(phi)=E[(Q_phi(s_t,a_t)-y_hat_t)^2]` | critic 学习 bootstrapped Bellman target |
| 公式 | Eq. 2 | `L_pi(theta)=-E[Q_phi(s_t,a_t)-alpha log pi_theta(a_t|s_t)]` | actor 同时追求高价值和高熵探索 |
| 公式 | Eq. 3 | `L_E2HiL=-E[I(s_t,a_t)(Q-alpha log pi)]` | E2HiL 的核心是在 actor 更新前选择样本 |
| 公式 | Eq. 4 | `Delta H approx E[-Cov(log pi(a_t|s_t), Delta z_t)]` | 把 entropy dynamics 连接到 logit update |
| 公式 | Eq. 6-8 | `A_soft=g-V_pi`，`Delta z=eta pi A_soft` | 说明样本影响来自动作概率与软优势 |
| 公式 | Eq. 9-10 | `Delta H approx -eta Cov(log pi, pi A_soft)`，`c=-eta Cov_hat` | 定义样本 influence value |
| 公式 | Eq. 11-12 | `I=1[|c| in [ell,u]]`，masked actor objective | 保留中等影响样本，剪掉极端样本 |
| 算法 | Algorithm 1 | 收集人工/自探索样本，采样 replay/demo batch，更新 critic，估计 `c_i`，筛样本，更新 actor | 给出闭环训练流程 |
| 图 | Fig. 2 | sample collection、entropy dynamics estimation、entropy-bounded selection、online RL update | 展示 E2HiL 如何插入 HiL-RL 训练循环 |

关键公式解释：

$$
\mathcal{L}_Q(\phi)=
\mathbb{E}_{(s_t,a_t,r_t,s_{t+1})\sim \mathcal{D}}
\left[(Q_\phi(s_t,a_t)-\hat{y}_t)^2\right].
$$

这里 `Q_phi` 是 critic（价值函数），`\hat{y}_t` 是 bootstrapped Bellman target（自举贝尔曼目标）。它负责估计某状态动作的长期回报。

$$
\mathcal{L}_\pi(\theta)=-
\mathbb{E}_{(s_t,a_t)\sim \mathcal{D}}
\left[Q_\phi(s_t,a_t)-\alpha\log\pi_\theta(a_t|s_t)\right].
$$

`alpha` 是 adaptive temperature coefficient（自适应温度系数）。`Q` 项鼓励 exploitation（利用高价值动作），`-\log pi` 项鼓励保持 entropy（探索）。

$$
\Delta \mathcal{H}\approx
\mathbb{E}_{s_t\sim d_{\pi_\theta}}
\left[-\mathrm{Cov}_{a_t\sim\pi_\theta}
\left(\log\pi_\theta(a_t|s_t), \Delta z_t\right)\right].
$$

这一步是全文的理论支点：如果知道一次更新如何改变 action logits（动作 logit），就能近似知道它如何改变策略熵。

$$
A_{\mathrm{soft}}(s_t,a_t)
=Q_\phi(s_t,a_t)-\alpha\log\pi_\theta(a_t|s_t)-V_\pi(s_t),
$$

$$
V_\pi(s_t)=
\mathbb{E}_{a'_t\sim\pi_\theta}
\left[Q_\phi(s_t,a'_t)-\alpha\log\pi_\theta(a'_t|s_t)\right].
$$

`A_soft` 表示该动作相对当前策略平均 entropy-regularized value 的优势。如果一个高概率动作还有很大的 soft advantage，它会推动策略更确定，容易降低熵；如果低概率动作有优势，则可能增加探索。

$$
c(s_t,a_t)=-\eta \widehat{\mathrm{Cov}}(s_t,a_t),
\qquad
\mathbb{I}(s_t,a_t)=\mathbf{1}\left[|c(s_t,a_t)|\in[\ell,u]\right].
$$

`c` 是 stop-gradient signal（停止梯度信号），只用于筛选，不直接被反向传播优化。`ell` 和 `u` 是 batch-wise percentile bounds（批内分位数上下界）。

### Section IV. Experiments

#### 高层故事流

实验部分先介绍真实机器人设置。平台是 Lerobot SO-101 leader-follower system：follower 是 RL actor agent（执行策略的机器人），leader 是 human operator（人类操作者）用来做同构映射接管的设备。观测来自两个 RGB cameras，分辨率 `128 x 128`，30 Hz。每个任务先收集 10 条 real-world human demonstrations 初始化 demonstration buffer。

Baseline 是 HIL-SERL。它同样用人工 corrective interventions 和 RLPD entropy regularization，但没有按样本对 entropy dynamics 的影响进行筛选。指标包括 final success rate、average human intervention rate，以及 policy entropy curve。四个任务是 Touch Cube、Pick Cube、Pick & Place Cube、Stack Blocks，难度逐渐增加。

总体结果显示 E2HiL 在所有任务成功率都明显高于 HIL-SERL，接管率也都更低。Touch Cube case study 是最能说明机制的实验：如果策略早期因为 shortcut samples 熵塌缩，它可能只学会触碰一个位置；E2HiL 通过剪掉导致熵骤降的样本，保留了继续探索第二个位置的能力。论文中这段 case study 的代词描述略混乱，但结合图和上下文，应理解为 HIL-SERL 更容易在第二位置学习上变慢且人工成本更高，E2HiL 更稳定。

![[papers/images/2601.19969v1/real_robot_page1.png|500]]

![[papers/images/2601.19969v1/main1114.png|700]]

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| SO-101 leader-follower 平台和双 RGB 观测 | 说明是真实机器人在线 RL，而非纯仿真 | Fig. 3, IV-A | 任务规模仍较小，硬件和场景单一 |
| HIL-SERL 作为 baseline | 与 state-of-the-art HiL-RL 对比 | IV-A | 复现设置、超参和人工操作者差异会影响结果 |
| 四任务成功率平均 83.9 vs. 41.8 | 支持 E2HiL 提升任务表现 | Table I, Fig. 4 | 未报告多随机种子统计显著性 |
| 接管率平均 33.9 vs. 44.0 | 支持减少人工成本 | Table I | 接管率不是人力时长的完整度量 |
| covariance 与 `-Delta H` 有比例关系 | 验证 entropy influence 估计有意义 | Fig. 5 Left | 前 5k steps 偏差明显，作者归因于 critic Q 不准 |
| 人工接管样本集中在 covariance upper tail | 解释人工样本强影响但也高风险 | Fig. 5 Right, Table II | 强影响不一定等于好样本，因此需要上下界 |
| 被剪样本多来自人工接管，且常在 workspace 外或重复状态 | 解释 clipping 的实际含义 | Fig. 6 | 这个分析偏经验，未完全因果证明每类剪样本都负面 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| 图 | Fig. 3 | SO-101 leader-follower real-world setup | 说明实验不是仿真，人工可通过 leader robot 接管 |
| 表 | Table I | 四任务 success rate 和 intervention rate | E2HiL 平均成功率更高、接管率更低 |
| 图 | Fig. 4 | baseline comparison、entropy curves、success/intervention curves | E2HiL 熵动态更平滑，避免 premature entropy collapse |
| 图 | Fig. 5 | covariance vs. entropy derivative；intervention vs. exploration covariance | 支持 covariance 是样本熵影响的可用 proxy |
| 表 | Table II | covariance magnitude 分布 | 人工样本在 upper tail 中远强于 exploration samples |
| 图 | Fig. 6 | retained vs. clipped samples 在任务空间中的分布 | 被剪样本常是 workspace 外、冗余或低贡献状态 |

Table I 关键数值：

| 指标 | Method | Touch Cube | Pick Cube | Pick & Place Cube | Stack Blocks | Average |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Success Rate (%) ↑ | HIL-SERL | 55.4 | 40.0 | 36.1 | 35.7 | 41.8 |
| Success Rate (%) ↑ | E2HiL | 92.5 | 93.2 | 71.3 | 78.7 | 83.9 |
| Intervention Rate (%) ↓ | HIL-SERL | 42.6 | 39.9 | 41.4 | 52.1 | 44.0 |
| Intervention Rate (%) ↓ | E2HiL | 23.3 | 31.4 | 37.1 | 43.6 | 33.9 |

这张表最直接支持两个主张。第一，E2HiL 不是只降低人工干预而牺牲成功率，四个任务成功率都更高。第二，接管率下降幅度在简单任务更大，例如 Touch Cube 从 42.6 降到 23.3；在 Stack Blocks 这种更难任务上仍下降，但幅度较小，从 52.1 到 43.6。

![[papers/images/2601.19969v1/prediction1128_page1.png|600]]

Fig. 5 的左图是理论验证：batch-wise covariance 和 `-Delta H` 的曲线趋势相近，尤其在 `0-10k` 初始熵降低和 `10k-20k` 熵回升阶段。右图显示 human intervention samples 的 covariance amplitude 明显高于 self-exploration samples，这说明人工样本对策略更新更“有力”，但也意味着它们更可能造成过大熵变化。

Table II 关键数值：

| Subset | All Samples | Intervention Samples | Exploration Samples |
| --- | ---: | ---: | ---: |
| Top 2% | 269.9 | 368.1 | 5.56 |
| Top 5% | 127.0 | 180.2 | 2.7 |
| Top 10% | 67.3 | 98.6 | 1.5 |
| Top 20% | 34.2 | 51.1 | 0.8 |
| Top 50% | 13.8 | 20.6 | 0.3 |
| Low 20% | 0.001 | 0.002 | 0.0007 |
| Low 10% | 0.0005 | 0.0007 | 0.0003 |
| Low 5% | 0.0002 | 0.0003 | 0.0001 |
| Low 2% | 0.00008 | 0.0001 | 0.00006 |
| All | 6.9 | 10.3 | 0.2 |

这张表说明 intervention samples 的平均绝对 covariance 远高于 exploration samples。尤其在 Top 2% 中，人工样本达到 368.1，而 exploration samples 只有 5.56。这个分布支持 E2HiL 的设计：人工纠偏样本不能简单都保留，因为上尾极端样本既可能有价值，也可能导致 shortcut-style entropy collapse。

![[papers/images/2601.19969v1/Figure6_page1.png|700]]

Fig. 6 展示 retained samples 与 clipped samples 的空间分布。作者的解释是，被剪掉的大量样本来自 human interventions，其中许多在 robot effective manipulation region（机器人有效操作区域）之外，或是 workspace 内的冗余重复状态。这为 entropy-bounded clipping 提供了可解释性：它不仅防止过强样本把策略熵压塌，也减少 near-zero influence 的低多样性样本拖慢学习。

### Section V. Conclusion

#### 高层故事流

Conclusion 回到全文主张：E2HiL 是一个面向真实机器人 HiL-RL 的 sample-efficient framework（样本高效框架），关键是 entropy-guided sample selection（熵引导样本选择）。它通过 covariance-based influence functions 描述 sample-induced entropy dynamics，再用 entropy-bounded selection 剪掉 shortcut 和 noisy samples，从而保持稳定熵演化，并以更少人工干预完成更有效的策略更新。

未来方向有两条。第一，把 E2HiL 扩展到 scalable multi-task real-world RL（可扩展多任务真实机器人强化学习）和 Vision-Language-Action models（视觉语言动作模型，VLA）。第二，用更可靠的 value estimation（价值估计）改善 covariance estimation，因为当前方法的一个薄弱点就是 early-stage critic 不准会影响 `A_soft`，进而影响样本影响值。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| covariance-based influence functions 可识别 shortcut/noisy samples | 总结方法贡献 | V. Conclusion | 依赖 critic 质量和 action sampling 估计 |
| entropy-bounded selection 维持稳定 entropy evolution | 总结机制作用 | V. Conclusion | 稳定熵不等于所有任务中最优探索策略 |
| 多真实任务更高成功率、更少人工干预 | 总结实验证据 | Table I, Fig. 4 | 任务数、机器人形态和操作者范围有限 |
| 未来扩展到 VLA 和改进价值估计 | 指出研究路线 | V. Conclusion | 还没有在大规模 VLA/RL 后训练中验证 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| 总结 | Conclusion | E2HiL 通过样本级熵影响函数筛掉 shortcut/noisy samples | 方法主张闭合 |
| 未来工作 | Conclusion | multi-task real-world RL for VLA，reliable value estimation | 当前边界在可扩展性和估计稳定性 |

## 主张-证据-边界矩阵

| 主张 / 结论 | 原文证据 | 证据位置 | 解释 | 边界 / 适用条件 |
| --- | --- | --- | --- | --- |
| HiL-RL 中不是所有人工接管样本都同样有价值 | 人工样本 covariance amplitude 明显高于探索样本，且极端值集中在人工样本中 | Fig. 5 Right, Table II | 人工样本对策略熵影响更强，因此更需要筛选 | 强影响可能是有用纠偏，也可能是危险 shortcut，单靠来源不能判断 |
| 稳定的 entropy reduction 比快速 entropy collapse 更适合真实机器人在线学习 | Touch-Cube 中 E2HiL 熵下降更平滑，能继续探索第二位置；HIL-SERL 更早进入 suboptimal performance | Fig. 1, Fig. 4 | 熵曲线反映探索能力是否过早消失 | 熵只是 proxy，具体任务中成功还依赖 reward、critic 和动作空间 |
| covariance-based influence function 可以估计样本对 entropy dynamics 的影响 | batch-wise covariance 与 `-Delta H` 曲线有比例关系 | Fig. 5 Left | 理论推导和经验曲线互相支持 | 前 5k steps 偏差较大，作者承认 Q-value 不准会影响估计 |
| entropy-bounded sample selection 能提升成功率并降低人工接管率 | 四任务平均 success rate 83.9 vs. 41.8，intervention rate 33.9 vs. 44.0 | Table I | 筛掉过大/过小影响样本后，训练更稳定且更省人工 | 任务数量有限，缺少跨机器人和多操作者大规模统计 |
| 被剪样本确实有一部分是低质量或低贡献样本 | clipped samples 多在 workspace 外或冗余状态 | Fig. 6 | 空间分布给出机制解释 | 这是事后分析，不完全证明所有 clipped 样本都应被剪 |
| E2HiL 可作为 VLA 在线 RL 扩展方向 | 作者未来工作指向 multi-task real-world RL for VLA | Conclusion | 样本级熵筛选可能帮助大模型在线 RL 降低人工成本 | 本文实验不是 VLA backbone，不能直接外推到大规模模型 |

## 局限与可追问点

1. 任务规模和硬件范围有限。实验集中在 SO-101 平台和四个 cube/block 操作任务，能证明真实机器人可行性，但还不足以说明该方法在 dexterous hand（灵巧手）、长时程多阶段任务、接触丰富装配或移动操作中同样稳健。

2. 统计证据不够完整。论文报告了曲线和平均结果，但没有充分展示多随机种子、多操作者差异、置信区间或显著性检验。真实机器人 RL 成本高可以理解，但这会影响结果稳健性的判断。

3. covariance 估计依赖 critic 和 soft advantage。作者自己观察到前 5k steps 中 covariance 和熵导数有偏差，原因可能是 Q-value estimation 不准。也就是说，E2HiL 最需要筛样本的训练早期，恰好也是 value estimate 最不可靠的阶段。

4. `[ell,u]` 的分位数规则仍是启发式。论文实验中提到用 5th 和 90th percentiles，但没有系统分析不同阈值、不同任务阶段自适应策略或阈值对 human intervention usage 的敏感性。

5. actor-only masking 的影响边界需要更清楚。E2HiL 把样本从 actor update 中屏蔽，但这些样本如何影响 critic、demo buffer、replay buffer 长期组成，论文没有充分展开。被剪样本是否应从 critic 训练中降权，是后续可追问点。

6. “shortcut sample”和“noisy sample”的语义还比较经验化。本文用 extreme covariance values 来识别它们，Fig. 6 给了空间分布解释，但还没有一个独立标注或因果实验来证明这些样本一定导致熵塌缩或无效更新。

7. 与 VLA/RL 大模型训练的连接还是展望。论文动机借鉴 LLM-RL entropy dynamics，也在未来工作中提到 VLA，但当前策略和任务规模仍是传统真实机器人 RL 设置。若迁移到 VLA，需要重新验证 token/action entropy、连续动作分布和高维视觉语言状态下的 covariance 估计。

## 精读路线 / 为什么需要回看

第一遍先看 Fig. 1 和 Table I，抓住全文问题：E2HiL 不是减少人工接管入口，而是提高人工样本进入策略更新时的有效性。关键对比是随机均匀采样可能带来 early entropy collapse，而 E2HiL 试图保持稳定熵下降。

第二遍重点回看 Section III 的 Eq. 4 到 Eq. 12。这里要把变量关系顺清楚：`Delta H` 由 `Cov(log pi, Delta z)` 近似，`Delta z` 又由 `pi A_soft` 表示，因此 influence value `c(s,a)` 本质上是在估计样本推动策略熵变化的强度。理解这条链，才能判断方法是不是只是经验过滤。

第三遍看 Fig. 5 和 Table II。它们回答“为什么人工样本需要筛选”：人工干预样本确实更强地影响熵，但强影响不自动等于好影响。上尾样本可能导致 shortcut，下尾样本可能是 noisy/redundant，所以保留中间区间是本文的关键启发式。

第四遍看 Fig. 6 和局限。Fig. 6 给了一个很实用的解释：被剪样本不只是抽象的 covariance outliers，很多对应 workspace 外或重复状态。这对复现和扩展很重要，因为后续可以把 entropy influence 与 workspace constraints、state novelty、human correction type 结合起来。

如果要把这篇接到你的 embodied/VLA 阅读线里，最值得追问的是：E2HiL 的 sample-level entropy filtering 能否成为 VLA 在线 RL 后训练中的 human feedback budget allocator（人工反馈预算分配器）。也就是说，在大模型机器人策略里，不仅要问“什么时候人来接管”，还要问“哪些接管片段应该真正驱动 policy update”。
