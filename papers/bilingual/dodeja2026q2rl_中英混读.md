---
tags:
  - bilingual-reading
  - deep-reading
paper: "[[@dodeja2026q2rl]]"
source_pdf: "[[papers/pdfs/2605.05172v3.pdf]]"
images: "papers/images/2605.05172v3/"
image_index: "[[papers/images/2605.05172v3/index.md]]"
created: 2026-07-18
reading_mode: 生成式精读（逐节读原文 + 附录 + 读图）
---
![[Pasted image 20260719154731.png]]
# Q2RL：When Life Gives You BC, Make Q-functions

paper:: [[@dodeja2026q2rl]]
pdf:: [[papers/pdfs/2605.05172v3.pdf]]
images:: [[papers/images/2605.05172v3/index.md]]

> [!info] 版本与归属
> 本稿解析 arXiv `2605.05172v3`，正式发表 venue 为 **Robotics: Science and Systems (RSS) 2026**。作者来自 Robotics and AI Institute、Brown University 与 Northeastern University；Northeastern 对应 Robin Walters 的作者归属之一。

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| Behavior Cloning (BC) | 行为克隆 | 已有策略起点；能复现成功示范，却没有靠环境反馈继续自我改进的机制。 |
| offline-to-online RL | 离线到在线强化学习 | 先用离线数据得到初始能力，再靠在线交互提升；难点是上线初期会遗忘已学会的好动作。 |
| Q2RL | 从 BC 做 Q-Estimation 与 Q-Gating 的 RL | 全名是 **Q-Estimation and Q-Gating from BC for Reinforcement Learning**。 |
| Q-Estimation | Q 值估计 | 用少量 BC rollout 的 return、BC 动作 log-likelihood 与 entropy 构造 $\hat Q_{\mathrm{BC}}$。 |
| soft-optimality / Boltzmann assumption | 软最优 / 玻尔兹曼假设 | 把 BC 动作分布视为由某个任务 Q 经指数归一化诱导，是解析公式成立的关键假设。 |
| action likelihood | 动作似然 | 衡量某动作在 BC 分布下是否典型；进入 $\alpha\log\pi_{\mathrm{BC}}(a\mid s)$ 项。 |
| policy entropy | 策略熵 | 修正不同状态下动作分布的扩散程度；与 $V$ 一起确定 Q 的 state-dependent offset。 |
| Monte Carlo return | 蒙特卡洛回报 | 从少量在线 BC rollout 估 $V_{\mathrm{BC}}(s)$，因此需要在线奖励但不要求原始示范数据。 |
| Q-Initialization | Q 初始化 | 用 $\hat Q_{\mathrm{BC}}$ 监督初始化可学习的 $Q_{\mathrm{RL}}$；与“如何估出 Q”的 Q-Estimation 不同。 |
| Q-Gating | Q 门控 | 每一步分别由 BC、RL 提议动作，再用冻结 BC critic 与在线 RL critic 比分选择。 |
| frozen reference critic | 冻结参照 critic | $\hat Q_{\mathrm{BC}}$ 不随在线训练漂移，用来保住 BC 的好动作与初始行为。 |
| trainable RL critic | 可学习 RL critic | $Q_{\mathrm{RL}}$ 从 BC Q 初始化，随后随在线 SAC 更新，负责发现超越 BC 的动作。 |
| auxiliary BC loss | 辅助 BC 损失 | 约束 RL actor 不要过快偏离 BC 分布，真机安全与平滑性的一部分来源。 |
| replay-buffer seeding | replay buffer 示范预填充 | IBRL 等方法依赖原始数据稳定 critic；Q2RL 的卖点是即使拿不到示范也能启动。 |
| on-robot RL | 真机在线强化学习 | 交互成本、碰撞和磨损都是真实代价，因此初始成功率与安全探索比最终分数更重要。 |
| sparse success reward | 稀疏成功奖励 | 真机由人给成功/终止信号；Q2RL 不需要稠密 reward shaping，但仍需要可判定成功。 |

## 摘要

Behavior Cloning（行为克隆）在机器人学习里很实用：目标简单、只要成功示范就能训练，也容易得到一个非零成功率的初始策略。但 BC 的能力上限被数据锁死；遇到示范不足、光照/物体位置/控制器变化或接触误差时，它既会 covariate shift（协变量偏移），也不会自己试出更好动作。直接接 online RL 又有另一类风险：随机初始化的 critic 和 actor 可能在上线初期把 BC 已会的动作替换掉，真机上还会产生高冲击、不安全探索。

Q2RL 的回答是：**不要从原始示范重新学一个 offline Q，而从已经训练好的 BC policy 本身“提取”一个 Q 参照。** 作者先运行少量 BC 轨迹，用回报拟合 $V_{\mathrm{BC}}$；在把 BC 视为 Boltzmann policy 的假设下，再由 $V$、动作 log-probability 和策略 entropy 构造 $\hat Q_{\mathrm{BC}}$。在线阶段保留一份冻结的 $\hat Q_{\mathrm{BC}}$，同时从它初始化一份可学习 $Q_{\mathrm{RL}}$。BC 和 RL 每步各提一个动作，两个动作分别由各自 critic 估值，得分较高者被执行；收集到的 transition 再用于 SAC 更新 RL 分支。

论文的最强证据不是“任何任务都 SOTA”，而是三个更窄也更可信的结论：第一，在**拿不到 BC 原始训练数据**时，Q2RL 比依赖 replay seeding 的 IBRL / offline RL 稳得多；第二，门控确实能让 BC 负责已会的自由空间运动，让 RL 集中处理接触、精插入和分布迁移段；第三，在三项真机任务上，BC 成功率分别从 0.70/0.20/0.35 提到 1.00/0.75/0.70。其边界同样明确：Q 提取依赖 soft-optimality 与可计算 likelihood/entropy，真实实验规模小、使用最佳 checkpoint，且冻结/在线两个 critic 的长期标度校准没有被显式解决。

## 论文主线

![[papers/images/2605.05172v3/Q2RL_fig1_final.jpg|920]]

**Figure 1 / 方法总览。** 左侧 Q-Estimation 把一个 BC policy 拆成三类可用信息：少量 rollout 训练出的 $\hat V_{\mathrm{BC}}$、动作分布的 log-likelihood，以及 entropy；三者合成 $\hat Q_{\mathrm{BC}}$。中间把它复制成两条支路：雪花标记的 $\hat Q_{\mathrm{BC}}$ 永久冻结，火焰标记的 $Q_{\mathrm{RL}}$ 继续训练。右侧 Max gate 比较两条支路对各自候选动作的打分，执行胜者并把 reward 回流给 RL 分支。最右侧三类真机任务逐步增加难度：已抓持的 Peg Insertion、需要先抓再旋转对准的 Pipe Assembly、以及长时程且发生物体数量/位置迁移的 Kitting。

全文可以压成一条因果链：

1. **BC 有好起点但无改进机制；直接 online RL 会忘掉好起点。**
2. **只要 BC 给出 normalized density 与 entropy，少量在线 return 就能构造一个带任务尺度的 frozen Q anchor。**
3. **把“保留”与“探索”分给两个 critic / policy 候选，再逐状态门控，而不是让一个随机 critic 同时评两者。**
4. **如果机制成立，Q2RL 应该更快恢复 BC 水平、无示范数据也能启动，并在困难接触段逐渐选择 RL。**
5. **仿真、门控行为分析、消融和真机结果总体支持 3–4；但并未证明公式给出了无偏的真实 $Q^{\pi_{\mathrm{BC}}}$。**

## 贡献与结论对照

| 贡献 / 结论 | 方法位置 | 关键证据 | 应如何定性 |
| --- | --- | --- | --- |
| 从 BC policy 提取 $\hat Q_{\mathrm{BC}}$ | §IV-A，Eq.(4)–(8)，Appendix A | 25–100 个 rollout 即可启动；非 soft-optimal 噪声消融会先掉点但能恢复 | 是有用初始化/参照构造；不是一般条件下真实 Q 的无偏恢复证明。 |
| 冻结 BC Q + 在线 RL Q 的双 critic 门控 | §IV-B，Eq.(9)，Algorithm 1 | 去掉 Q-Gating 明显掉性能；BC/RL action ratio 随学习阶段变化 | 实验最扎实的机制贡献。 |
| 无需访问原始示范也能 BC→RL | §V-D、Appendix Table III/IV | robomimic no-data 中基线近零，Q2RL 全部超过 BC 或持续提升 | 在本文 Gaussian/GMM policy 与稀疏奖励设置下成立。 |
| 在困难段用 RL、简单段保留 BC | §V-E、Fig.5/7 | Pipe 中 BC 做抓取/初对准，RL 做插入；Kitting 中 RL 处理新位置抓放 | 是代表性 rollout 的定性解释，不是所有轨迹的严格分段规律。 |
| 真机 1–2 小时级改进 | §V-G、Fig.8、Appendix Table VI | Peg 1.00、Pipe 0.75、Kitting 0.70；系统约 13k action/h、44k learner step/h | 强真机信号，但选最佳 checkpoint，训练上限写明可到 2.5 h。 |
| 比 IBRL 更安全 | §V-G Safety、Appendix CalQL | IBRL Peg 出现 2 次 fault，stochastic CalQL 4 次，Q2RL 未观察到 | 只能视为小样本安全观察，不是系统性安全保证。 |

## 结构地图

| 原文位置 | 作者在做什么 | 与主线的关系 | 关键图表 / 公式 |
| --- | --- | --- | --- |
| §I Introduction | 把 BC 的 covariate shift、online RL 遗忘与真机危险探索并列成问题 | 定义“既保留又改进”的目标 | Fig.1；四点贡献 |
| §II Related Work | 对比 BC/offline RL、CalQL/WSRL、Residual RL/IBRL、SERL/HIL-SERL | 说明为何从已有 BC 本身估 Q、再双分支门控 | 无主公式 |
| §III Problem Formulation | 定义示范、任务分布迁移、MDP、$Q/V$ 与 Boltzmann policy | 给 Q-Estimation 建形式化接口 | Eq.(1)–(3) |
| §IV-A Q-Estimation | 推导 $Q=V+\alpha\log\pi+\alpha H$，说明 $V$/likelihood/entropy 如何获得 | 从黑盒 BC 构造可冻结的 value anchor | Eq.(4)–(8)；Appendix A 推导/GMM |
| §IV-B Q-Gating | 两份 critic、两候选动作、按各自 Q 取最大 | 把“保留 BC”与“在线改进”同时落实 | Algorithm 1；Eq.(9) |
| §IV-C Implementation | $\alpha=1$、SAC、auxiliary BC loss | 给真机稳定性加工程约束 | Appendix Table I/II |
| §V-A–D Simulation | D4RL + robomimic，有/无原始数据，state/image | 验证性能、收敛速度与 no-data 启动 | Fig.2–4；Appendix Table III/IV |
| §V-E Action Analysis | 看门控用了多少 BC/RL 动作 | 验证 gate 不是退化成固定混合 | Fig.5 |
| §V-F Ablations | 分离 Q-Gating 与 Q-Initialization | 找出实际贡献组件 | Fig.6；Appendix Fig.9–14 |
| §V-G Real World | Peg、Pipe、Kitting-Modified | 验证接触精度、长时程与分布迁移 | Fig.7/8；Appendix Table V–VII |
| §VI Conclusion | 总结兼容范围并承认生成式 policy 不适用 | 给出最主要方法边界 | diffusion / flow matching 留作未来 |
| Appendix A–D | 完整推导、超参、数值表、更多消融与真机细节 | 校准主文曲线、复现性与限制 | Table I–VII；Fig.9–15 |

## 按原文 section 精读

### 1. Introduction / 为什么“好 BC + 直接 RL”仍会坏掉

引言先承认 BC 的现实优势：监督目标简单，成功示范容易收集，能直接拟合 $\pi_{\mathrm{BC}}(a\mid s)$。但它没有 self-guided online improvement（自导在线改进）；训练数据覆盖不足或环境发生轻微变化时，错误会沿时间累积。这是传统 covariate shift，但论文把重点放在**已有一个不差的策略之后怎么办**。

作者把替代路线的代价排列得很清楚。Interactive imitation learning 能在线纠正，却持续需要专家；offline RL 能学 value，却通常需要包含正负/次优行为的较大数据集，而机器人 BC 数据往往只有少量成功示范；CalQL、WSRL 等 offline-to-online 方法可能在切到在线分布时 unlearn；从零开始的 RL 动作在真机上又意味着磨损和碰撞。

因此目标不是简单“让 RL 分数更高”，而是同时满足三个条件：**上线第一刻不丢 BC 能力、困难状态允许偏离 BC、最好不依赖第三方没有交付的原始训练集。** Q2RL 的四项贡献——Q-Estimation、Q-Gating、仿真比较、真机验证——逐一对应这三个条件。

### 2. Related Work / Q2RL 与相邻路线的差别

#### 2.1 Offline learning

CQL 用保守惩罚压低 OOD action 的 Q，适合较大、质量混合的离线数据，却容易产生 pessimistic bias；IQ-Learn 从示范直接学习 soft Q。Q2RL 的定位不同：它不从示范重训一个 policy/Q，而把**已经存在的 BC policy 当作黑盒**，只要求能查询 action density 与 entropy。

这一区分很重要。Q2RL 的优势来自“policy artifact 可用、dataset artifact 不可用”的部署现实；代价是兼容显式概率头比较容易，diffusion/flow policy 的 normalized likelihood 与 entropy 不好算。

#### 2.2 Offline-to-online 与 residual learning

CalQL 校准 conservative Q，WSRL 先用 offline policy rollout 预热 online buffer，RLPD 持续混采 offline/online buffer。Residual RL / Policy Decorator 则不替换 BC，而在动作上加受限 residual；它保持附近行为，却要调 residual scale，动作维度大或需要大幅修正时可能受限。

最接近 Q2RL 的 IBRL 也让 BC 与 RL 各提一个动作，再由 critic 选择；关键区别是 IBRL 的 critic 随机初始化，并依赖 demonstration seeding 先学会“BC 动作通常更好”。Q2RL 先估 $Q_{\mathrm{BC}}$，保留冻结副本，再让另一个 critic 在线变化。这一差异直接预言了 no-data 实验：没有 seeded buffer 时，IBRL 的随机动作可能被随机 critic 虚高估值，Q2RL 应该不至于从零崩掉。

#### 2.3 On-robot RL

SERL 提供异步 actor–learner 真机栈，HIL-SERL 加人类 intervention；Q2RL 沿用 SERL 类 SAC/异步基础设施，但不靠持续人工纠偏或额外稠密 reward。需要注意的是，真机仍由人给 success/termination 并协助 reset，因此是“无需持续动作干预”，不是完全无人系统。

### 3. Problem Formulation / 任务、奖励与假设

已有 $M$ 条成功示范：

$$
\mathcal D=\{\tau_j\}_{j=1}^M,\qquad
\tau_j=\{(o_{j,t},a_{j,t})\}_{t=1}^{T_j},
$$

它们训练出 $\pi_{\mathrm{BC}}$。训练任务 $\mathcal M_{\mathrm{train}}$ 与测试任务 $\mathcal M_{\mathrm{test}}$ 可以不同，但共享同一 success condition 并来自任务类 $\mathfrak M$。在线阶段可与测试环境交互，并获得稀疏奖励；目标是超过原 BC，而不是仅恢复它。

标准 action-value 定义为：

$$
Q_\pi(s,a)=\mathbb E_{\tau\sim\pi}
\left[\sum_{t=0}^{\infty}\gamma^t r(s_t,a_t)\mid s_0=s,a_0=a\right],
\qquad
V_\pi(s)=\mathbb E_{a\sim\pi}[Q_\pi(s,a)].
$$

作者随后使用 energy-based interpretation（能量模型解释）：令 $E=-Q$，便得到 Boltzmann policy

$$
\pi(a\mid s)\propto \exp\!\left(\frac{Q(s,a)}{\alpha}\right).
$$

到这里最需要保持警觉：任意正密度都能写成某种 energy 的指数形式，但那个 energy **不自动等于环境回报定义的真实 $Q^\pi$**。Q2RL 进一步用在线 return 给 state value 定标，实质上加入了一个 soft-optimality / reward-consistency 假设；论文的鲁棒性消融能说明假设偏离时方法未必立刻失效，却不能把近似升级成普遍定理。

### 4. Q2RL / 方法

#### 4.1 Q-Estimation / 从 policy distribution 构造 Q

假设 BC 近似满足：

$$
\pi_{\mathrm{BC}}(a\mid s)
\approx
\frac{\exp(Q_{\mathrm{BC}}(s,a)/\alpha)}
{\int_{\mathcal A}\exp(Q_{\mathrm{BC}}(s,a')/\alpha)\,da'}.
$$

记 partition function 为 $Z(s)$。由

$$
\log\pi_{\mathrm{BC}}(a\mid s)=\frac{1}{\alpha}Q_{\mathrm{BC}}(s,a)-\log Z(s)
$$

和 entropy 定义可得：

$$
\begin{aligned}
\mathcal H[\pi_{\mathrm{BC}}(\cdot\mid s)]
&=-\mathbb E_{a\sim\pi_{\mathrm{BC}}}\log\pi_{\mathrm{BC}}(a\mid s)\\
&=-\frac{1}{\alpha}V_{\mathrm{BC}}(s)+\log Z(s),
\end{aligned}
$$

因此

$$
\boxed{
\hat Q_{\mathrm{BC}}(s,a)=
\hat V_{\mathrm{BC}}(s)
+\alpha\log\pi_{\mathrm{BC}}(a\mid s)
+\alpha\mathcal H[\pi_{\mathrm{BC}}(\cdot\mid s)]
}.
$$

直觉上，$\hat V$ 给这个状态的任务价值基线，$\log\pi$ 让 BC 认为更典型的动作得分更高，entropy 项修正该状态下分布整体有多宽。对同一状态比较多个 BC 动作时，$V$ 与 $H$ 都是常数，动作排序实际由 log-likelihood 决定；而跨状态/与另一个 critic 比较时，return-based $V$ 才提供任务尺度。

$\hat V_{\mathrm{BC}}$ 来自少量 BC online rollout 的 Monte Carlo return，再训练一个 value estimator。正文公式把多个 episode 与时刻写得较简略，核心操作是用 rollout-to-go 回报监督 $V(s)$；这意味着在稀疏奖励、低成功率 BC 下，估计质量会强烈依赖 rollout 数与成功样本覆盖。

对 diagonal Gaussian，按通常概率论记号应为：

$$
\log\pi(a\mid s)
=-\frac12\sum_{i=1}^{d}
\left[rac{(a_i-\mu_i(s))^2}{\sigma_i^2(s)}
+\log(2\pi\sigma_i^2(s))\right],
$$

$$
\mathcal H[\pi(\cdot\mid s)]
=\frac12\sum_{i=1}^{d}\log(2\pi e\,\sigma_i^2(s)).
$$

> [!warning] 公式排版校准
> 论文 v3 正文 Eq.(7) 的 Gaussian log-probability 括号前未印出标准的负号，Eq.(8) 也省略了多维求和写法。按概率密度定义这应视作排版/记号问题；精读稿采用标准形式，但不能仅凭 PDF 推断代码是否同样出错。

对 GMM，密度为 $\pi(a\mid s)=\sum_i c_i\pi_i(a\mid s)$；entropy 没有同样简单的闭式，论文使用上界：

$$
\mathcal H[\pi]\leq \sum_i c_i\mathcal H[\pi_i]+\mathcal H(C).
$$

这让 robomimic 的 GMM-RNN BC 可以使用 Q2RL，但也引入额外近似。

#### 4.2 Q-Gating / 两个 critic 分别承担记忆与学习

估出 $\hat Q_{\mathrm{BC}}$ 后，作者初始化两份网络：

- $\hat Q_{\mathrm{BC}}$：冻结，只评价 $a_{\mathrm{BC}}\sim\pi_{\mathrm{BC}}(s)$；
- $Q_{\mathrm{RL}}$：先在相同 BC rollout 上监督拟合 $\hat Q_{\mathrm{BC}}$，随后作为 SAC critic 在线更新，只评价 $a_{\mathrm{RL}}\sim\pi_{\mathrm{RL}}(s)$。

门控规则是：

$$
a_t=
\begin{cases}
a_{\mathrm{BC}}, & \hat Q_{\mathrm{BC}}(s_t,a_{\mathrm{BC}})>Q_{\mathrm{RL}}(s_t,a_{\mathrm{RL}}),\\
a_{\mathrm{RL}}, & \text{otherwise}.
\end{cases}
$$

执行后的 $(s_t,a_t,r_t,s_{t+1})$ 进入 online replay buffer，RL actor/critic 用 off-policy SAC 更新。冻结支路的意义是“不会遗忘的参照”，可学习支路则能吸收 BC 与 RL 两类已执行动作的后果，最终在 BC 的困难状态提出更高值动作。

这个设计也留下一个值得复现时重点监控的问题：两个分数初始同源，但 $Q_{\mathrm{RL}}$ 之后随 bootstrapping、reward scale 与分布变化漂移，论文没有额外 cross-critic calibration。若 RL critic 整体变得过度乐观，Max gate 仍可能系统偏向 RL；auxiliary BC loss、初始化和真实数据共同缓解，却不是形式保证。

#### 4.3 Algorithm 1 / 一次完整运行

1. 给定预训练 $\pi_{\mathrm{BC}}$；先运行 $N$ 个环境步骤/rollout。
2. 用 return 拟合 $\hat V_{\mathrm{BC}}$，再由 likelihood + entropy 得 $\hat Q_{\mathrm{BC}}$。
3. 冻结一份 $\hat Q_{\mathrm{BC}}$，监督初始化 $Q_{\mathrm{RL}}$，初始化 $\pi_{\mathrm{RL}}$。
4. 每个在线时刻从两策略各采一个动作，按 Eq.(9) gate。
5. 收 reward、写 buffer、采 minibatch，用 SAC 更新 $Q_{\mathrm{RL}}$ 与 $\pi_{\mathrm{RL}}$。

#### 4.4 Implementation / 稳定训练的工程选择

作者固定 $\alpha=1$，RL 使用 SERL/WSRL 系的 SAC，critic ensemble 为 10、每次 subsample 2，UTD=4，$\gamma=0.99$，target update 0.005，replay size $2\times10^6$。state/image/real 的 actor-critic hidden size分别为 `[512,512,512]`、`[1024,1024]`、`[1024,1024]`；学习率 state 为 $3\times10^{-4}$，image/real 为 $10^{-4}$。

RL actor loss叠加辅助 BC loss，权重依任务为 0.1–0.3。论文没有在主方法段给出这项 loss 的完整公式，这会影响严格复现；从论证上看，它也是早期平滑/安全行为的共同原因，所以不能把所有收益只归因于 gate。

仿真通常用 RL policy mode 做候选动作；真机因随机性更强，从 Gaussian 分布采样。图像任务用 DrQ augmentation。reward 采用 WSRL 式线性变换 $\tilde r=ar+b$，大多数任务 $b=-1$ 形成每步代价，Adroit 例外。

### 5. Experiments / 证据链

#### 5.1 任务、观测、基线与指标

| 组别 | 任务 | 观测 / 特点 | 在线阶段是否用原始数据 |
| --- | --- | --- | --- |
| D4RL | Kitchen-Complete、Adroit Pen、Adroit Door | state；Kitchen 只有 19 条成功示范 | 否 |
| robomimic state | Lift、Can、Square | Franka；GMM-RNN BC | 分别评 with-data / no-data |
| robomimic image | Lift、Can | agent-view + wrist-view，统一可学习 CNN | 分别评 with-data / no-data |
| real robot | Peg、Pipe、Kitting-Modified | 双 RGB + EEF pose/gripper，10 Hz delta pose | 任务设置不同，详见后文 |

基线包括 CQL、CalQL、WSRL、RLPD、IBRL；附录再比 Policy Decorator residual RL 与真机 CalQL。仿真曲线用 5 seeds，每个评估点 20 trajectories，阴影为 95% confidence interval。主要指标是 task success；真机每个方法/任务评 20 次。

#### 5.2 D4RL / Q2RL 不等于所有任务最终第一

![[papers/images/2605.05172v3/d4rl.png|900]]

**Figure 3 / D4RL 曲线。** 黑线是 BC；蓝色虚线是 Q2RL 从 Q-Estimation 切到在线 Q-Gating 的位置。Kitchen 中 Q2RL（红）很快超过 BC，而只含成功示范的小数据让 offline RL 系列困难；Pen 的 BC 已近饱和，Q2RL主要是保持；Door 中 WSRL 最终分数最高，但其行为利用仿真漏洞。

| 300k env step 成功率 | BC | WSRL | CQL | CalQL | IBRL | Q2RL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Kitchen | 0.69 | $0.64\pm0.08$ | $0.06\pm0.08$ | $0.23\pm0.02$ | $0.50\pm0.15$ | **$0.91\pm0.01$** |
| Pen | 0.90 | **$0.98\pm0.01$** | $0.05\pm0.03$ | $0.93\pm0.03$ | **$0.95\pm0.05$** | **$0.93\pm0.03$** |
| Door | 0.50 | **1.00** | $0.31\pm0.33$ | $0.15\pm0.15$ | 0.00 | $0.87\pm0.08$ |

作者用 rollout 解释 Door：WSRL 学会不先抓门把、靠仿真可行但真机不现实的动作，Q2RL 仍按人类式抓把再开门。这提示 success metric 可能奖励 simulator exploit；不过也应诚实记录：**按该 benchmark 的标量指标，Door 最优确实不是 Q2RL。**

#### 5.3 robomimic with data / 与 IBRL 各有胜负

有原始训练数据填进 online buffer 时，IBRL 在 Lift/Square 可竞争甚至最终更高；Q2RL 的优势主要体现在更快恢复初始能力和较难的 Can：

| 最后评估点 | BC | RLPD | IBRL | Q2RL |
| --- | ---: | ---: | ---: | ---: |
| Lift-State (300k) | 0.58 | $0.99\pm0.01$ | $0.98\pm0.02$ | **1.00** |
| Can-State (500k) | 0.60 | 0.00 | $0.54\pm0.18$ | **$0.85\pm0.03$** |
| Square-State (500k) | 0.58 | 0.00 | **$0.94\pm0.01$** | $0.81\pm0.08$ |
| Lift-Image (200k) | 0.60 | 0.00 | **1.00** | **1.00** |
| Can-Image (500k) | 0.45 | 0.00 | $0.03\pm0.05$ | **$0.73\pm0.06$** |

论文指出原 IBRL 在 Can-Image 使用了更专门的 ViT 优化，而本比较统一用标准 CNN；这提高了架构公平性，但也意味着这里的数值不能直接当作对原论文最强配置的复现判决。

#### 5.4 robomimic without data / 最能支撑核心卖点

![[papers/images/2605.05172v3/rm_without_data_all.png|920]]

**Figure 4b / 无示范数据在线学习。** 黑线是 BC，红线 Q2RL 在蓝色虚线后迅速恢复并超过它；IBRL 等曲线基本贴零。原因与方法动机吻合：随机 critic 没见过示范时无法可靠比较 BC 与随机 RL 动作，Q2RL 已从 BC rollout 得到参照。

| 最后评估点 | BC | IBRL | Q2RL |
| --- | ---: | ---: | ---: |
| Lift-State (300k) | 0.58 | 0.00 | **1.00** |
| Can-State (550k) | 0.60 | 0.00 | **$0.82\pm0.10$** |
| Square-State (550k) | 0.58 | 0.00 | **$0.76\pm0.06$** |
| Lift-Image (200k) | 0.60 | $0.01\pm0.01$ | **$0.98\pm0.01$** |
| Can-Image (550k) | 0.45 | 0.00 | **$0.63\pm0.05$** |

这里的“without data”指 online RL 阶段不访问原始 BC training data；Q2RL 仍然要让 BC 在测试环境 rollout，并获得 reward 来估 $V$。它不是零交互、零奖励的 policy conversion。

#### 5.5 BC/RL action selection / gate 是否学会分工

Can-State、Square-State 中，Q2RL 在较少在线步骤内恢复 BC 水平，同时 BC 动作使用比例低于一半，说明它没有退化成“永远听 BC”。随着 $Q_{\mathrm{RL}}$ 改善，门控更常在简单运动段保留 BC、在 contact-rich 段用 RL。IBRL 使用的 BC 比例相近但成功率恢复更慢，而且比例较平，说明随机 critic 的选择没有形成同样有效的阶段分工。

这里应把“比例变化”当机制一致性证据，而不是最优性证明：相同 BC fraction 可以对应完全不同的状态选择质量；真正关键的是**在哪些状态切换**，论文主要靠代表性轨迹做定性展示。

#### 5.6 Ablations / 什么组件真正重要

- **Q-Gating 是关键。** No Q-Gating 让 BC/RL 候选都由同一在线 Q 评价，性能显著下降；冻结参照的作用得到直接支持。
- **Q-Initialization 不是主要分数来源。** 开 gate 后，从 $\hat Q_{\mathrm{BC}}$ 初始化与随机初始化最终相近；作者仍保留前者，因为它的早期分布更贴 BC，更适合真机。
- **25 个 rollout 已可竞争，主实验用 100。** 这支持样本效率，但没有说明更稀疏成功或更长任务所需的成功样本下限。
- **初始 BC 10%–75% 都能提升。** 说明方法不只适用于中等强 BC；但极低于 10% 或从未成功的 policy 没有覆盖。
- **非 soft-optimal policy。** 给 deterministic BC 加 Gaussian / uniform noise 会使 Q-Estimation 后初始成功率下降，online RL 能恢复；证明一定鲁棒性，但不是对任意多峰/强次优行为的保证。
- **Replay seeding。** Q2RL 对 seed fraction 不敏感，IBRL 强依赖它，正面支持 no-data 主张。
- **Policy Decorator。** Can 能恢复并小幅超过 BC，Square 恢复明显更慢，说明小 residual 对需大修正任务受限。

### 6. Real-world On-Robot RL / 真机

#### 6.1 平台、控制与人类参与

平台是 7-DoF Franka + Robotiq 2F-85 + compliant finray fingertips，工作区和腕部各一台 RealSense D405；输入为 EEF pose、gripper width 与两路 $84\times84$ RGB，输出 delta EEF pose 和必要时的 gripper command，由 Cartesian impedance controller 以 10 Hz 执行。actor 与 learner 通过 ZeroMQ 异步运行，约每小时执行 13k RL actions、44k learner steps。

> [!note] 硬件命名差异
> 主文写 “Franka Panda”，附录 Hardware 写 “Franka FR3”。精读时保留这一版本内不一致；不据此擅自认定具体机型。

每个任务的 success/termination 由人提供，reset 也有人协助，有时先用 SpaceMouse 把机械臂移到安全自由空间。因而 wall-clock 小时数含真实系统并行学习，但没有把人工 reset 成本排除。

#### 6.2 三个任务为何逐级变难

- **Peg Insertion**：peg 已抓在手中，初始 pose 随机；配合公差约 1–2 mm、插入深度约 50 mm。50 条 BC demo，episode 最长 200。
- **Pipe Assembly**：PVC 管从桌面开始，先抓、再旋转对准 plumbing fixture；公差约 1–2 mm、插入深度约 57 mm，平均步骤约为 Peg 两倍。100 条 BC demo。
- **Kitting-Modified**：两种零件各从一个 bin 取出并放进 tray，要完成两次 pick-place；BC 只在 Original（每 bin 一个、居中）上训练，测试时每 bin 两个且都移开中心。50 条 BC demo，episode 最长 500。

Kitting 的证据口径尤其要细读：BC 在 Original 为 0.95，到 Modified 掉至 0.35；Q2RL Q-Estimation 获得 50 个 Original episode，online buffer 又 seed 30 个 Modified episode，IBRL 同样 seed 30 个 Modified episode。因此它证明的是**在相同 shifted seed 下，冻结 BC Q + gate 比随机 critic 更能适应**，不是 Modified 条件完全零数据。

#### 6.3 真机结果

![[papers/images/2605.05172v3/real_world_results.png|860]]

**Figure 8 / 真机成功率。** 第一组 Peg 有 seeded data；第二组特意去掉 replay seed。Pipe 与 Kitting 的 IBRL 即使有 seed 仍为零，Q2RL 分别达到 0.75 与 0.70。每根柱对应 20 trials 的最佳 checkpoint。

| Task | BC | IBRL | Q2RL | Q2RL learner steps | 相对 BC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Peg Insertion | 0.70 | 0.95 | **1.00** | 60k | 1.43× |
| Pipe Assembly | 0.20 | 0.00 | **0.75** | 90k | **3.75×** |
| Kitting-Modified | 0.35 | 0.00 | **0.70** | 165k | 2.00× |

Peg no-data 的单独表中，Q2RL 为 1.00、IBRL 0、deterministic/stochastic CalQL 为 0.10/0.20，BC 为 0.70。作者最多训练 2.5 h、170k gradient steps / 80k environment steps，并选各方法的最佳 evaluated checkpoint；所以摘要的“1–2 h”应理解为代表性任务的在线学习量级，不应改写成所有最终结果都严格两小时以内。

#### 6.4 门控轨迹与安全观察

![[papers/images/2605.05172v3/combined_with_border.png|800]]

**Figure 7b / BC–RL 分工。** Pipe 中蓝色 BC 负责抓管和初始对齐，黄色 RL 负责高精度接触插入；Modified Kitting 中，BC 负责两 bin 间已有的移动，RL 负责新位置的抓取/放置与 recovery。作者明确说并非每条 rollout 都完全遵循这一模式，不能把颜色示意当硬编码状态机。

安全方面，IBRL Peg 训练中有 2 次过力导致 robot fault；Q2RL 未出现相同 fault。真机 stochastic CalQL 评估还有 4 次 high-jerk safety violation。这个结果和初始化、gate、auxiliary BC loss 的组合解释一致，但样本量小、没有统一 force/jerk 指标，最多支持“本文运行中观察到更平滑”，不能支持 certified safety（形式安全保证）。

### 7. Conclusion / 作者自己承认的边界

论文结论把 Q2RL 定位为从 BC 到 online RL 的转换器：不要求 BC 原数据，能在数小时内改善高精度接触任务。唯一明确写入结论的局限是必须获得 action likelihood 与 entropy；因此当前显式 Gaussian / GMM 可用，diffusion 与 flow matching policy 需要未来研究。

从全文证据还能补出更深的边界：它依赖在线 success reward、BC 至少偶尔能给出有用 rollout、两个 critic 的尺度不能严重失配，并用辅助 BC regularization 共同维持安全。换言之，Q2RL 是**有条件的强 warm start**，不是把任意 imitation policy 无损变成最优 RL critic。

## 方法细节

### 三个容易混淆的名字

| 名称 | 发生在何时 | 是否持续训练 | 作用 |
| --- | --- | --- | --- |
| Q-Estimation | online RL 前 | 先收 BC rollout，再拟合 | 构造 $\hat Q_{\mathrm{BC}}$ 的算法 |
| Q-Initialization | online RL 前 | 监督预训练 $Q_{\mathrm{RL}}$ | 让 RL critic 起点与 BC Q 同尺度 |
| Q-Gating | 每个在线动作时刻 | 全程使用 | 在 BC/RL 候选之间逐状态选择 |

### Frozen / learnable 两支路的数据流

$$
\pi_{\mathrm{BC}}
\xrightarrow[\log\pi,\,H]{\text{BC rollouts + returns}}
\hat Q_{\mathrm{BC}}
\begin{cases}
\longrightarrow \text{frozen BC scorer},\\
\longrightarrow Q_{\mathrm{RL}}^{(0)}\longrightarrow \text{online SAC critic}.
\end{cases}
$$

这个结构最重要的设计原则是：**不要让保存旧能力的量和吸收新证据的量是同一个参数对象。** 但决策时又必须比较两者，因此 calibration 是潜在薄弱点。

### 真机 reward / 时间口径

大多数任务稀疏成功 $r=1$，再变换为 $\tilde r=ar+b$；负 step bias 鼓励快完成。人给成功与终止，失败到 max length 截断。learner step 指一次 high-UTD update；UTD=4 时包含四次 critic update 和一次 actor update。表中的 Q2RL learner steps 也包含 Q-Estimation steps。

## 实验设置、数据集、基线、指标

| 维度 | 设定 |
| --- | --- |
| BC classes | Gaussian policy（D4RL）与 GMM-RNN + ImageNet-pretrained ResNet-10（真机/robomimic） |
| RL algorithm | SAC；image 用 DrQ；critic ensemble 10，subsample 2，UTD 4 |
| Simulation Q-estimation | D4RL 50 rollout；robomimic state/image 100；训练 20k step，Square 50k |
| Real Q-estimation | Peg 100、Pipe 100、Kitting 30（配置表）；Kitting 正文另说明 50 Original episode 与 30 shifted seed |
| Simulation evaluation | 每点 20 rollout × 5 seeds，95% CI |
| Real evaluation | 每方法每任务 20 trials，报告最佳 checkpoint |
| Baselines | CQL、CalQL、WSRL、RLPD、IBRL；附录 Policy Decorator、real CalQL |
| Primary metric | task success rate；另读 convergence speed、BC/RL action ratio、qualitative feasibility 与 safety faults |

## 主要结果、消融或对比

1. **最强定量结论**：no-data robomimic 五个 state/image 设置里，Q2RL 全部保住/超过 BC，IBRL 几乎全零。
2. **最强真机结论**：Pipe 从 0.20 到 0.75，是论文“3.75×”的准确口径；不是整体平均倍数。
3. **非全面 SOTA**：D4RL Door 是 WSRL 1.0 > Q2RL 0.87；with-data Square 是 IBRL 0.94 > Q2RL 0.81。
4. **核心消融**：Q-Gating 比 Q-Initialization 更决定最终表现；这说明冻结参照的持续存在比单纯 warm-start critic 更关键。
5. **安全不是单组件效果**：作者自己将平滑性归因于 BC loss + gate + Q initialization 的组合。

## 图表、公式与表格线索

| 线索 | 内容 | 阅读时抓什么 |
| --- | --- | --- |
| Fig.1 | Q-Estimation → frozen/trainable critics → Max gate | 全文最小方法闭环 |
| Algorithm 1 | 先估 Q，再逐步双候选、存 transition、SAC 更新 | 哪些量冻结、哪些量学习 |
| Eq.(6) | $\hat Q=\hat V+\alpha\log\pi+\alpha H$ | soft-optimality 假设与 state/action 两类项 |
| Eq.(9) | 两个 critic 对各自动作的 hard max | calibration 与过度乐观风险 |
| Fig.3 | D4RL | Kitchen 增益、Pen 饱和、Door simulator exploit |
| Fig.4a/b | robomimic with/without data | no-data 是区分 Q2RL 与 IBRL 的关键实验 |
| Fig.5 | BC action fraction + success | gate 是否学到状态相关分工 |
| Fig.6 | Q-init / Q-gating ablation | gate 是主要组件 |
| Fig.7 | 真机平台与彩色 action segment | 定性看 BC 简单段、RL 困难段 |
| Fig.8 / Table VI | 真机成功率与 learner steps | 20 trials、最佳 checkpoint、3.75× 口径 |
| Appendix Fig.9–14 | 假设、residual、seed、BC loss、rollout 数、BC 初始强度 | 结论适用区间 |
| Table I/II | BC loss 与 RL 超参 | 辅助约束不可忽略 |
| Table III/IV | 仿真精确数字 | 避免只凭平滑曲线读结论 |
| Table V–VII | 真机配置、结果、no-data CalQL | 人工参与、任务差异与安全边界 |

## 主张-证据-边界矩阵

| 主张 / 结论 | 原文证据 | 解释 | 边界 / 适用条件 |
| --- | --- | --- | --- |
| 能从 BC 提取可用 Q | Lemma + Eq.(6)，rollout ablation | policy density 给 action-relative energy，return 给 state value 尺度 | 依赖 Boltzmann / reward consistency；不保证等于一般 $Q^\pi$ |
| 无原示范也能稳定 online RL | Fig.4b、Table III/IV | 冻结 Q anchor 避免随机 critic 错评 BC | 仍需测试环境 rollout、reward、likelihood/entropy |
| Q-Gating 防止遗忘 | Fig.5/6 | 冻结支路持续保存旧策略评价 | 双 critic 标度可能随时间失配 |
| 能超越 BC | Kitchen、Can、真机三任务 | RL 在困难状态收集并学习更好动作 | Pen 增益小；Door/with-data Square 非最优 |
| 对分布迁移有效 | Kitting Original 0.95→Modified BC 0.35，Q2RL 0.70 | 在线分支补新物体位置/拥挤条件 | 有 Original Q-estimation 与 30 shifted seed；单一迁移类型 |
| 1–2 小时可真机学习 | 项目/主文叙述，系统吞吐与 steps | 异步 learner 使 wall-clock 可行 | 最高允许 2.5 h，人工 reset/success 未计成本 |
| 更安全平滑 | IBRL 2 faults、CalQL 4、Q2RL 0 | 行为锚定与 BC loss 符合预期 | 小样本定性，非安全证明，无 force/jerk 统一指标 |
| policy-class agnostic | 只需 likelihood + entropy | backbone 可黑盒，显式分布头易接 | diffusion/flow 默认不满足，当前仅 Gaussian/GMM 验证 |

## 局限与可追问点

1. **“提取 Q”究竟提取了什么？** 公式恒等地构造了与 policy density 一致的 energy，并用 Monte Carlo $V$ 定标；需要额外验证它是否满足 Bellman consistency、与真实 counterfactual action return 排序一致。
2. **双 critic 如何校准？** 可监测 $Q_{\mathrm{RL}}-\hat Q_{\mathrm{BC}}$ 的整体漂移，尝试 shared target、temperature calibration、uncertainty-aware gate 或保守 margin，而不只 hard max。
3. **低成功率与长时程怎么办？** 10% 初始成功已测，但零成功 BC、奖励极稀疏、需要先失败再恢复的任务没有覆盖；此时 $V$ 监督可能全相同。
4. **辅助 BC loss 的精确定义与贡献。** 主文缺完整公式；应独立报告 gate only、loss only、init only 及安全/性能 trade-off。
5. **hard gate 是否抖动？** 逐步 Max 可能在两个 critic 近似相等时频繁切换；可问是否需要 hysteresis、chunk-level gate 或 uncertainty threshold。
6. **真机统计强度。** 应报告多 training seeds、固定 checkpoint selection protocol、置信区间、碰撞力/jerk、人工 reset 时长。
7. **生成式 VLA 扩展。** diffusion/flow 可否用 score、ELBO/ODE likelihood、sample ranking 或 learned energy 近似 likelihood/entropy，是与当前 VLA 库连接最直接的研究方向。
8. **论文内记号/硬件一致性。** Gaussian log-probability 负号、Monte Carlo return 索引、Panda/FR3 名称均值得代码核对。

## 与当前库的连接

- 与 [[@luo2024precise-dexterous-robotic-manipulation|HIL-SERL]] / [[@deng2026e2hil|E2HiL]]：三者都解决真机在线 RL 的昂贵探索。HIL-SERL 用 human intervention，E2HiL 筛 intervention/exploration sample，Q2RL 则把已有 BC 变成冻结 action/value anchor；它们分别干预“谁来纠错”“哪些样本更新”“哪个候选动作执行”。
- 与 [[@intelligence2025pi06-vla-that-learns|π*0.6 / RECAP]]：RECAP 面向大 VLA 的经验强化学习自改进，Q2RL 面向显式概率 BC + SAC。Q2RL 的 likelihood/entropy 门槛正是迁移到 flow-matching VLA 时的主要障碍。
- 与 [[@yu2026wm-dagger|WM-DAgger]]：两者都保护已有强策略再做数据聚合/修复；WM-DAgger 让世界模型暴露失败并聚合修复数据，Q2RL 用双 Q 在线选择 BC/RL 动作。
- 与 [[@qian2026wam-rl|WAM-RL]]：WAM-RL 借世界动作模型做在线 RL 后训练，Q2RL 借 policy-derived Q 做门控；可比较 learned dynamics/value uncertainty 与 hard Q gate 的风险控制。
- 与 [[@wang2026wvm|WVM]]：WVM 从视频/世界模型得到轨迹价值，Q2RL 从 policy likelihood + online return 得 action value；两者都在问“现有生成/模仿模型能否派生一个 value interface”。
- 与 [[@yu2026warp-rm|WARP-RM]] / [[@liu2026steam|STEAM]]：后两者用进展/价值筛选已有数据，Q2RL 用 value 在执行时选动作。一个工作在 training data gate，一个工作在 online action gate。

## 精读路线 / 为什么需要回看

1. **先看 Fig.1 + Eq.(6)**：抓住从 policy distribution 到 frozen Q anchor 的最小闭环，并立刻标记 soft-optimality 假设。
2. **再看 Algorithm 1 + Eq.(9)**：分清 Q-Estimation、Q-Initialization、Q-Gating，确认两个 critic 各评谁、谁被冻结。
3. **优先读 Fig.4b**：no-data robomimic 是最直接支持论文独特卖点的实验。
4. **用 Table III/IV 校准曲线**：记住 Door 与 with-data Square 的反例，避免把“多数更好”写成“全部 SOTA”。
5. **最后看 Fig.7/8 + Appendix D**：理解 BC/RL 真机分工，同时核对 20 trials、最佳 checkpoint、2.5 h 上限、人类 reward/reset 与 Kitting seed。
6. **若要复现/扩展到 VLA**：回看 Appendix A 的推导、Gaussian/GMM entropy、Fig.9 soft-optimality 消融，并把 likelihood/entropy 与 critic calibration 列为第一批技术风险。
