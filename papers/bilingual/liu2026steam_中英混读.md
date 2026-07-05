---
tags:
  - bilingual-reading
  - deep-reading
paper: "[[@liu2026steam]]"
source_pdf: "[[papers/pdfs/liu2026steam.pdf]]"
images: "papers/images/liu2026steam/"
image_index: "[[papers/images/liu2026steam/index.md]]"
created: 2026-07-05
reading_mode: 生成式精读（逐节读原文 + 读图）
---

# STEAM: Self-Supervised Temporal Ensemble Advantage Modeling for Real-World Robot Learning

paper:: [[@liu2026steam]]
pdf:: [[papers/pdfs/liu2026steam.pdf]]
images:: [[papers/images/liu2026steam/index.md]]

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| frame-level advantage | 帧级优势 | 本文靶心：给一条真实机器人轨迹的**每一帧**打一个标量分，区分“正在推进任务”的帧与“停滞/回退/失败”的帧，而非只给整条 episode 一个成/败标签。 |
| temporal offset $\Delta_{\tau_k}(i,j)=j-i$ | 时间偏移 | 自监督信号的来源：同一条 expert 轨迹里两帧的**帧序差**。正偏移=向前推进，负偏移（反向配对）=回退。全部可从轨迹本身读出，无需人工标注。 |
| trajectory-length normalization $L_{\max}/L_{\tau_k}$ | 轨迹长度归一化 | 把不同执行时长的轨迹拉到同一尺度：同样一个偏移，在短轨迹里算“大进展”、长轨迹里算“小进展”。这条归一化让 advantage **内在偏好执行效率**（短而利落的示范得分更高）。 |
| reversed frame pairs / pseudo-failure | 反向帧对 / 伪失败序列 | 本文巧思：**只用成功示范**，把它倒放当作负偏移样本，让模型无需任何真实失败演示就学会识别“回退运动”。 |
| distributional signed-bin predictor（$N$ bins） | 分布式带符号分箱预测器 | 不直接回归连续偏移（输出空间过大），而是把归一化偏移离散成 $N$ 个箱、预测一个 categorical 分布，再折算成标量 advantage。$N$ 越大，进展/回退的粒度越细。 |
| advantage lookahead $H$ | 优势前瞻步长 | 推断某帧 advantage 时固定用它 $H$ 帧后的未来帧作配对（Eq.4）。real-task 里 $H=32$（pick-and-place 用 16）。 |
| ensemble minimum / worst-of-$M$ | 集成取最小 / 最差-M 聚合 | 本文核心保守机制：训 $M$ 个独立随机初始化的预测器，最终 advantage 取**逐帧最小值**。成员在训练分布内一致、在 OOD 上发散——取最小即压制“过度自信的假阳性”。 |
| overestimation / OOD false positive | 过估计 / 分布外假阳性 | 本文要防的失败模式：单预测器在 rollout 的分布外状态上会自信地给出高 advantage，制造错误正样本、把策略带偏。 |
| optimality label $o_{k,i}$ + quantile threshold | 最优性标签 + 分位数阈值 | 把连续 advantage 二值化成 0/1 标签喂给 CFGRL。**按数据源分别设阈值**：expert 宽松（保留 top 80%）、non-expert 严格（保留 top 30%）。 |
| CFGRL (classifier-free guidance RL) | 无分类器引导强化学习 | 下游策略优化框架 [1]（库外）：把 optimality 标签当作 flow-matching 策略的条件，推理时朝 $o{=}1$ 外推，把动作生成引导向“高局部进展”样本。 |
| heterogeneous / mixed-quality data | 异质 / 混合质量数据 | 训练数据构成：expert demonstrations + autonomous rollouts + human corrections，同一条 episode 内质量会变（先推进后失败、先烂后被人救回）。 |
| BC / HG-DAgger / RECAP | 三个对照基线 | BC=只用 expert 的行为克隆；HG-DAgger [25]=加人类纠正干预；RECAP [5]=基于 VLM 的 value 估计（均库外），是本文最关键的“已有信号方法”对照。 |
| SigLIP-SO400M / Gemma-3-270M / $\pi_0$ | 视觉编码 / 语言骨干 / 策略骨干 | 每个 advantage 预测器 = SigLIP-SO400M 视觉编码 + Gemma-3-270M 语言骨干 + 任务专属头；策略骨干用 $\pi_0$ [24]（库外）经 CFGRL 集成。 |

## 论文主线

这篇论文的核心问题是：**真实机器人学习越来越依赖异质数据，但示范和 rollout 里“有用进展”与“停滞/纠正/次优行为”是混在同一条 episode 里的**。一条 rollout 可能先推进再失败；一条 human-intervention 轨迹可能先是糟糕的自主行为、后被人救回。于是**按整条轨迹过滤**（trajectory-level filtering）会误伤有用片段、也会漏留有害片段。作者把它精炼成一句话：

> **how can we assign fine-grained credit to distinguish task-advancing actions from stalled or regressive ones?**（如何做细粒度的 credit assignment，把“推进任务的动作”和“停滞/回退的动作”分开？）

作者把这个问题定式为 **frame-level advantage estimation（帧级优势估计）**。但在没有 dense reward 的真实机器人上估 advantage 很难，作者点名三个障碍：
1. **hand-crafted reward / 人工标注 / 跨轨迹标定** 需要大量外部监督，限制可扩展性；
2. **VLM-based reward/value** 需要广泛预训练，且当视觉-语言先验没有物理接地时，会给出**噪声帧级信号**；
3. 很多 progress estimator 假设一个**绝对或单调**的进展观，与“会临时回退、犯错后恢复、离开专家分布”的真实 rollout 不匹配。一旦把这种 learned reward/value 用到这些 **OOD rollout 状态**上，它会给不可靠的 transition 打高 advantage，制造 **false-positive 训练信号**，把策略优化引向误导性行为。

作者的关键转念是：**不给每帧一个绝对进展值，而用同一条 expert 轨迹内两帧的相对顺序**。这个相对信号只属于每条示范本身，绕开跨轨迹标定和人工设定的全局进展曲线；任意两帧的 normalized temporal offset 都能**直接从轨迹算出**，从而得到 dense 的成对进展监督——不需要人工 reward、人工标签或外部 value。

在此之上作者提出 **STEAM（Self-supervised Temporal Ensemble Advantage Modeling）**：在 expert frame pair 上训一个 temporal-offset 预测器的**集成**；每个预测器输出 temporal bins 上的分布，折算成反映 local temporal efficiency 的标量 advantage；用**成功轨迹的反向帧对**在没有失败演示的情况下暴露回退运动；对混合质量数据打分时**取集成最小值**以压制 OOD 上的过估计。得到的 STEAM advantage 再用来给 offline RL（CFGRL）挑高 advantage 帧做策略改进。

阅读时要盯住两句话：**（1）本文的监督完全来自 expert 轨迹的时间结构，一行人工标注都不用；（2）本文真正“抗噪”的机器是 ensemble-min（worst-of-M），它把“单模型在分布外的过度自信”从一句修辞变成了可被压制的可测现象。** 这两点共同构成 STEAM 相对 RECAP / VLM-based value 的差异化主张。（overview 图 Figure 1 与 framework 图 Figure 2 未在本地图集中提取，故不嵌入，仅据 caption 在下方图表索引里说明。）

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| 提出 label-free frame-level advantage estimation：用 expert 轨迹内 frame pair 的 normalized temporal offset 作 dense 自监督 target。 | §3.1，Eq.(1)(2)。 | Fig.4/Fig.5：advantage 曲线在 expert 高、rollout 略低、failure 掉零、human-correction 先掉后恢复。 | 概念干净、无需标注；但依赖“时间前进≈任务进展”的假设。 |
| STEAM 把分布式 temporal-offset 预测折算成标量 advantage，并用**保守集成聚合（取最小）**压制混合质量数据上的过估计。 | §3.2，Eq.(3)(4)(5)。 | Table 3：$M{=}1\to M{=}3$ 使成功率 72.7%→92.3%；Fig.11 定性证明。 | 消融直接支撑；是全文最扎实的一环。 |
| 在四个真实任务上验证：能定位 stall/failure/recovery，且配 CFGRL 大幅提升策略成功率。 | §3.3 + §4，Eq.(6)。 | Table 1：towel +59、chip +54.3、cola +23、pick +16.2 百分点（相对 BC）。 | 真实增益大；但增益幅度与任务 horizon / 数据构成强相关。 |

## 摘要与核心贡献

摘要提出的矛盾是：真实机器人学习越来越依赖 heterogeneous data，但示范与 rollout 常把“有用进展”与“停滞、纠正、次优行为”混在一起，因此有效的策略学习需要**帧级 advantage** 来区分“可靠的局部进展”与“失败/回退”。

STEAM 是一个 **label-free** 方法：在 expert 示范上训一个 **temporal-offset predictor 的集成**，用两帧之间的 normalized temporal offset 作自监督信号；每个预测器把 frame pair 映射成 temporal offset 上的分布、折算成标量 advantage；随后**取集成最小 advantage** 来保守地给混合质量 rollout 打分。在真实的双臂 towel folding、chip checkout、cola restocking 和单臂 pick-and-place 上，STEAM 能识别 stall / failure / recovery；配合 CFGRL 后，把策略成功率相对基线分别提升 **59%、54.3%、23%、16.2%**。

> 读原文才发现的口径细节：这四个提升数字是 Table 1 里 STEAM 相对 **BC** 的**百分点**提升——towel 92.3−33.3=59.0、chip 93.8−39.5=54.3、cola 75−52=23、pick 80−63.8=16.2。摘要写“over baselines”，但对齐的基线是 BC，且是“百分点”而非“相对提升”。引用时别写成“成功率相对提升 59%”。

作者把贡献列为三点：**（1）label-free 帧级 advantage 的问题定式**（normalized temporal offset 作 dense self-supervised target）；**（2）STEAM 本体**——分布式 offset 预测折算成标量 advantage + 保守集成聚合压过估计；**（3）四个真实任务上的验证**——定位 stall/failure/recovery，配 CFGRL 提升成功率。

## 按原文 section 逐节精读

### 1. Introduction / 为什么“帧级、相对、自监督”的 advantage 是对的方向

Introduction 的功能是把“混合质量数据”这个现实痛点，一路收敛到“帧级、相对顺序、自监督”这三个设计选择。作者先说 robot foundation model 依赖大量 expert 示范，但采集昂贵、真实数据常含混合质量行为（尤其 long-horizon）；近期方法 [5,6] 引入 non-expert 轨迹（rollout、human intervention、失败尝试）来拓宽 state-action 覆盖，但这些轨迹**同一 episode 内质量就会变**——于是轨迹级过滤两头不讨好。

接着把三条“为什么难”摆清楚（见上文主线）。**这一节的读法**：Introduction 没有停在“需要 reward/value”，而是把矛头对准“learned reward/value 在 OOD rollout 上会制造 false-positive”——后面 §3.2 的 ensemble-min 正是针对这句话设计的。可以逐一回勾：相对顺序→解决“绝对/单调进展”假设；自监督→解决“外部监督不可扩展”；ensemble-min→解决“OOD 假阳性”。

### 2. Related Work / STEAM 卡在哪两条线之间

作者把自己定位在两条线的交点：

- **Reward Models for Robot Manipulation**：现有工作从 human annotation [3,4]、hand-crafted reward [5,6]、foundation-model priors [7,13,14,15] 学 reward/value。STEAM 的差异是**直接预测 advantage**，而非从 learned reward/value 里恢复。最接近的是 **ARM [4]**（也估 frame pair 间的相对进展），但 ARM 依赖**人工标注数据训的分类器**，STEAM 则把 expert 示范的时间结构当自监督，**零人工标注**。
- **Temporal Structure as Supervision**：时间顺序是免费监督信号，长期用于自监督视频表示 [16-20]。机器人里通常把时间顺序转成 dense reward：**TimeRewarder [8]** 回归帧级 temporal offset 成 dense reward；**ReWiND [21]** 把成功视频倒放成失败样 reward 序列；**VLAC [9]** 用大 VLM critic 出带符号进展 delta。作者点名 **TimeRewarder 是最接近的 prior**——两者都利用 frame pair 间带符号 temporal offset，但 **STEAM 把它们当作 per-frame advantage 用于 offline 数据质量评估，而非 online RL 的 dense reward**。

**这一节读法**：把握两个“最接近但关键不同”——对 ARM 是“自监督 vs 人工标注”，对 TimeRewarder 是“离线数据质量评估 vs 在线 dense reward”。这也解释了为什么实验对照是 RECAP（value）而非 TimeRewarder（online reward）——STEAM 主张的是离线数据筛选这一使用场景。

### 3.1 Normalized Temporal Offset as Learning Target / 自监督 target 怎么来

训练数据**只来自 expert 示范**。作者的假设是：尽管偶有短暂 stall，expert 轨迹的内在时间前进可靠地指示任务推进，因此不需要 hand-crafted reward。对一条 expert episode $\tau_k=(f_{k,1},\dots,f_{k,L_{\tau_k}})$，定义两帧间的 temporal offset：

$$
\Delta_{\tau_k}(i,j)=\Delta(f_{k,i},f_{k,j})=j-i\tag{1}
$$

正偏移（帧配一个未来观测）监督**向前进展**；**反向 expert 轨迹**给出负偏移，制造 pseudo-failure 序列——让模型**仅从成功示范就学会回退行为**。这是全文最省数据的一步：不需要任何真实失败演示。

原始 offset 不能跨轨迹直接比（执行时长不同），于是按轨迹长度归一化：

$$
\tilde{\Delta}_{\tau_k}(i,j)=(j-i)\cdot\frac{L_{\max}}{L_{\tau_k}}\tag{2}
$$

$L_{\max}$ 是 expert episode 中的最大长度（或用高分位数降 outlier 敏感度）。这条归一化的深层作用是**把执行效率编进 target**：短而利落的示范被乘上 $>1$ 的因子、得到更高的进展尺度；慢的、次优的执行被相对压低——这直接决定了后面 advantage 会“奖励效率”。

### 3.2 Distributional Temporal Offset Predictor / 分箱预测 + 集成取最小

**Categorical 预测**：直接回归连续 offset 会有过大的输出空间，于是把 $\tilde{\Delta}_{\tau_k}(i,j)$ 约束在 $[-\tilde{\Delta}_{\max},\tilde{\Delta}_{\max}]$ 内、离散成 $N$ 个等距 bin，得到长度 $N$ 的 one-hot target $\tilde{\Delta}^{B}_{\tau_k}(i,j)$。预测器 $p_\theta(\Delta\mid f_{k,i},f_{k,j},\ell)$ 把 expert frame pair 与自然语言指令 $\ell$ 映到 $N$ 个 bin 上的 categorical 分布，用交叉熵训练：

$$
\mathcal{L}(\theta)=\mathbb{E}_{\tau_k,i,j}\Big[\,H\big(\tilde{\Delta}^{B}_{\tau_k}(i,j),\ p_\theta(\Delta\mid f_{k,i},f_{k,j},\ell)\big)\Big]\tag{3}
$$

**Advantage Modeling**：从 learned 分布导出标量 advantage，且只关注 temporal efficiency。对帧 $f_{k,i}$，用固定前瞻 $H$ 取未来帧 $f_{k,i+H}$ 做推断，把预测分布折成期望 bin 索引，再减去 ground-truth 量化 offset：

$$
A(f_{k,i};\theta)=\frac{2}{N}\Big[\,\mathbb{E}_{b\sim p_\theta(\cdot\mid f_{k,i},f_{k,i+H},\ell)}[b]-\tilde{\Delta}^{B}_{\tau_{\max}}(i,i+H)\Big]\tag{4}
$$

因为 $H$ 固定、$\tau_{\max}$ 指最长 episode，$\tilde{\Delta}^{B}_{\tau_{\max}}(i,i+H)$ 是一个**确定性 offset**（相当于用最长轨迹当参照）。归一化（Eq.2）让这个 advantage **内在偏好执行效率**：更短、更高效的 expert 示范得分更高，更慢/次优的被惩罚。

**Ensemble for Overestimation Control**：单个在 expert 上训的预测器，在 OOD rollout 样本上会**过度自信**，给出严重过估计的 advantage [22]，制造 false-positive 信号退化策略改进。对策是训 $M$ 个独立随机初始化的预测器 $\Theta=\{\theta_1,\dots,\theta_M\}$，最终 advantage 取**逐帧最小**：

$$
A_{\text{STEAM}}(f_{k,i};\Theta)=\min_{m=1,\dots,M}A(f_{k,i};\theta_m)\tag{5}
$$

作者的论证是：ensemble 成员在训练分布内趋于一致、在陌生状态空间发散；取最小=**惩罚高方差**，是针对 reward overoptimization（RLHF 常见问题 [23]）的稳健正则。它可能略降 recall，但压制 false positive——而后者对稳定策略优化更关键（§4.3 验证）。

### 3.3 Policy Training with $A_{\text{STEAM}}$ / advantage 如何变成策略监督

训练好集成后，$A_{\text{STEAM}}$ 作为异质训练数据（expert + rollout + human correction）的帧级 advantage 估计器。作者**把连续 advantage 二值化成 optimality label**，并且**按数据源分别做分位数阈值**（因为不同来源 advantage 分布不同）：

$$
o_{k,i}=\mathbb{1}\big[\,A_{\text{STEAM}}(f_{k,i};\Theta)\ge\delta_q\,\big]\tag{6}
$$

$\delta_q$ 是随数据源动态选取的 $q$-quantile 阈值。这个标签表示“该帧在 STEAM advantage 下是否代表高质量的局部进展”，随后作为 optimality 条件塞进 **CFGRL [1]**，引导策略偏向生成“高局部进展”样本的动作。

**这一节读法**：STEAM 本身不做策略优化，它是一个**离线数据打分器 + 二值筛选器**，真正改策略的是 CFGRL。所以“advantage 好不好”最终只能靠“下游策略成功率”来验证——这解释了为什么 §4 的核心证据是 Table 1 的成功率而非 advantage 的绝对精度。

## 方法细节

### CFGRL 集成的实现（Appendix A / Algorithm 2）

optimality 标签按 expert / non-expert **分别阈值**：

$$
o=\begin{cases}
\mathbb{1}\big[A_{\text{STEAM}}(f_{k,i};\Theta)\ge\varpi_q^{\text{exp}}\big], & f_{k,i}\in\mathcal{D}_{\text{exp}}\\[4pt]
\mathbb{1}\big[A_{\text{STEAM}}(f_{k,i};\Theta)\ge\varpi_q^{\text{non-exp}}\big], & f_{k,i}\in\mathcal{D}_{\text{nexp}}
\end{cases}\tag{7}
$$

标签条件化一个 flow-matching 策略 $v_\phi(a_t,t,s,o)$。训练时构造带噪动作插值并做 conditioning dropout：

$$
a_t=(1-t)a_0+t\,a\quad(a_0\sim\mathcal{N}(0,I),\ t\sim\mathcal{U}[0,1])\tag{8}
$$
$$
\mathcal{L}_\pi(\phi)=\mathbb{E}\big[\,\lVert v_\phi(a_t,t,s,\tilde{o})-(a-a_0)\rVert^2\big]\tag{9}
$$

其中以概率 $p_{\text{drop}}$ 把条件置空 $\tilde{o}=\varnothing$。推理时从纯噪声出发做 $T$ 步固定步长 Euler 积分（$\Delta t=1/T$），并朝高 optimality 标签外推：

$$
v_{\text{cfg}}(a_t,t,s)=v_\phi(a_t,t,s,\varnothing)+w\big[\,v_\phi(a_t,t,s,o{=}1)-v_\phi(a_t,t,s,\varnothing)\big]\tag{11}
$$

$w\ge1$ 是 guidance scale；$w>1$ 主动把生成动作推向 STEAM 判定为“高进展”的轨迹。**这是 STEAM advantage 真正作用于策略的唯一出口**：advantage → 二值标签 → CFG 外推方向。

### 关键超参（Appendix D / Table 4）

| Hyperparameter | Towel | Chip | Cola | Pick |
| --- | ---: | ---: | ---: | ---: |
| Maximum offset $k_{\max}$ | 32 | 32 | 32 | 16 |
| Number of bins $N$ | 32 | 32 | 32 | 16 |
| Ensemble size $M$ | 3 | 3 | 3 | 3 |
| Advantage lookahead $H$ | 32 | 32 | 32 | 16 |
| $\varpi_q^{\text{exp}}$（expert 保留） | 0.8 | 0.8 | 0.8 | 0.8 |
| $\varpi_q^{\text{non-exp}}$（non-expert 保留） | 0.3 | 0.3 | 0.3 | 0.3 |
| dropout $p_{\text{drop}}$ / guidance $w$ | 0.1 / 2.5 | 0.1 / 2.5 | 0.1 / 2.5 | 0.1 / 2.5 |
| lr / steps / batch | 5e-5 / 30k / 512 | 同 | 同 | 同 |

**一个值得记的设计**：对 expert 数据保留 top 80%（宽松，因为 expert 大多可信），对 non-expert（rollout+correction）只保留 top 30%（严格，因为混合质量风险高）。短 horizon 的 pick-and-place 把 $N/H/k_{\max}$ 都从 32 降到 16——因为它 episode 短，用不着那么细的分箱。

## 实验

### Setup / 基准、编码器、基线

- **四个真实任务**（Fig.3）：towel folding（5 stage，ARX 双臂）、chip checkout（8 stage，ARX 双臂）、cola restocking（4 stage，ARX 双臂，需主动避碰）、pick-and-place（2 stage，单 Franka 臂）。
- **模型**：每个 advantage 预测器 = SigLIP-SO400M 视觉编码 + Gemma-3-270M 语言骨干 + 任务专属预测头；策略骨干 = $\pi_0$ [24]，经 CFGRL 与 STEAM 集成。
- **基线三选**：**BC**（只用 expert）、**HG-DAgger [25]**（加人类纠正干预）、**RECAP [5]**（VLM-based value 估计）。为公平，RECAP 用**同一 CFGRL 骨干**、跑单次迭代；RECAP 与 STEAM 都用**全数据源**（expert + human correction + autonomous rollout）。
- **三个问题**：Q1 能否区分高/低质量帧？Q2 能否提升策略？Q3 设计选择如何影响性能？

### 数据集构成（Appendix C）

| 任务 | Expert | Autonomous rollouts | Human corrections | Stages / 平台 |
| --- | ---: | ---: | ---: | --- |
| Towel Folding | 240 | 125 | 20 | 5 / ARX 双臂 |
| Chip Checkout | 200 | 63 | 20 | 8 / ARX 双臂 |
| Cola Restocking | 89 | 49 | 27 | 4 / ARX 双臂 |
| Pick-and-Place | 50 | 594 | 0 | 2 / 单 Franka |

注意 pick-and-place **没有 human correction**，且 expert 只有 50 条、rollout 却有 594 条——这解释了它在数据消融里的反常表现（见下文 Fig.7）。

### Q1 主结果：STEAM 能区分“推进/停滞/失败/恢复”（§4.1）

作者用两类证据：
- **Fig.4（towel folding 四类 episode 的 advantage 曲线）**：expert 全程高、仅在必要 retry/微调处**短暂小幅下掉**；successful rollout 更低更抖（慢但仍有效）；failed rollout 进入失败态后**迅速掉到近零并卡住不恢复**；human correction **先像失败一样下掉、人接管后明显回升**。
- **Fig.5（帧级 $A_{\text{STEAM}}$ 概率密度）**：四任务一致——expert 强烈集中在 $+1$；successful rollout 系统性左移到更低正值；failed rollout 在 0 附近或以下出现显著峰；human correction 分布更宽（既含慢自主段的低正值、也含人接管后回升的高值）。
- **Fig.6（episode 级 advantage 求和）**：成功 episode 的累计 advantage 相当，failed rollout 被显著更低的求和清晰分开。有意思的细节：towel/chip 的累计 advantage（尤其失败样）高于 cola/pick——因为 towel/chip 的失败多发生在**中后段**（前期已积累正 advantage），而 cola/pick 的失败发生在**初始抓取**（几乎没机会积累）。这说明 STEAM 的累计量**在一定程度上也能在 episode 级区分成/败**。

### Q2 主结果：STEAM 提升策略性能（Table 1，§4.2）

指标：Succ.=平均成功率(%)，Score=平均完成的 sub-stage 数，Thr.=吞吐（成功 episode/小时）。

| Method | Towel Succ/Score/Thr | Chip Succ/Score/Thr | Cola Succ/Score/Thr | Pick Succ/Score/Thr |
| --- | --- | --- | --- | --- |
| BC | 33.3 / 3.3 / 42 | 39.5 / 4.6 / 16 | 52 / 2.4 / 71 | 63.8 / 1.5 / 230 |
| HG-DAgger | 40 / 3.7 / 48 | 53.3 / 6 / 22 | 58.3 / 2.6 / 84 | — |
| RECAP | 55.6 / 2.9 / 39 | 53.3 / 5.33 / 24 | 52.9 / 2.1 / 46 | 53.8 / 1.5 / 161 |
| **STEAM** | **92.3** / 4.9 / 58 | **93.8** / 7.5 / 48 | **75** / 3 / 90 | **80** / 1.8 / 254 |

**这张表要看三处**：
1. **成功率全面第一**：两个最难的 long-horizon 任务（towel、chip）STEAM 到 92.3%/93.8%，Score（4.9/7.5）逼近满 stage（5/8）。
2. **吞吐也涨**：towel 上 rollout 天生比 expert 慢，RECAP 没能滤掉慢帧、吞吐（39）反而**低于 BC（42）**；STEAM 剪掉停滞低质帧，吞吐升到 58。这是“advantage 偏好效率”那条归一化（Eq.2）的直接回报。
3. **RECAP 不总赢 BC**：cola（52.9 vs 52）、pick（53.8 vs 63.8）上 RECAP 甚至不如 BC——印证 introduction 说的“VLM-based value 在物理未接地时给噪声信号”。

**数据源消融（Fig.7）**：比较 BC / STEAM(Exp) / STEAM(Exp+Dagg) / STEAM(Full)：

| 任务 | BC | STEAM (Exp) | STEAM (Exp+Dagg) | STEAM (Full) |
| --- | ---: | ---: | ---: | ---: |
| Towel Folding | 33.3 | 69.2 | 81.8 | 92.3 |
| Chip Checkout | 39.5 | 72.7 | 80.0 | 93.8 |
| Cola Restocking | 52.0 | 61.5 | 66.7 | 75.0 |
| Pick-and-Place | 63.8 | 55.0 | —（无 correction） | 80.0 |

- towel/chip/cola：**只用 expert（STEAM Exp）就已超 BC**（如 towel 33.3→69.2），说明 STEAM 能从 expert 里**挑出最关键的 task-advancing 片段**。
- **pick-and-place 反常**：STEAM(Exp) 55.0 **反低于 BC 63.8**。作者解释：pick-and-place 是高度一致的短 horizon 任务，expert 轨迹已经很好（Fig.5d 里 advantage 尖锐集中在 $+1$），此时过滤会**剪掉太多帧、把本就很小的训练集进一步缩水**。但一旦引入 rollout+correction（STEAM Full），advantage 信号变得高度有益，成功率回到 80.0——因为它能从大量 imperfect rollout 里捞出有用样本。

### Q3 消融：bin 数 $N$ 与集成规模 $M$（§4.3）

在 towel folding（全量 expert+correction+rollout）上消融：

**Table 2（bin 数 $N$）**：$N{=}2$ → 27.3% / 2.8 / 41；$N{=}8$ → 54.6% / 3.8 / 51；$N{=}32$（默认）→ **92.3% / 4.9 / 58**。小 $N$ 把 target 退化成粗糙的“前/后”二元信号，大 $N$ 能区分不同程度的进展/回退。结论：**细粒度 temporal progress 建模给策略更有用的 advantage 信号**。

**Table 3（集成规模 $M$）**：$M{=}1$ → 72.7% / 3.9 / 53；$M{=}3$（默认）→ **92.3% / 4.9 / 58**；$M{=}5$ → 90.9% / 4.6 / 55。$M{=}1$ 无法压制 OOD 过估计；$M{=}1\to M{=}3$ 成功率从 72.7% 跳到 92.3%（证明 ensemble-min 有效削减高 advantage 段里的假阳性）；$M{=}5$ 不再提升——故默认 $M{=}3$，平衡性能与算力。

![[papers/images/liu2026steam/appendix_adv_3models.png|760]]

**Figure 11（Appendix E.4）/ ensemble-min 为何必要的定性铁证。** 上半是 ARX 双臂折毛巾的 face view，下半是同一条 towel-folding rollout 上三个独立预测器（Ensemble 1 蓝 / Ensemble 2 橙 / Ensemble 3 绿）与聚合后 $A_{\text{STEAM}}$（黑，取逐帧最小）的曲线。**读图重点：证明“单模型会在 OOD 回退段过度自信，而取最小能压掉假阳性”**。全程大部分帧三条曲线都高贴近 1.0；关键在 **frame 1200–1400 的 final fold retry（回退段）**：蓝、橙正确识别回退、显著下掉（橙一度跌破 0.0），而**绿（Ensemble 3）严重过估计、仍自信地停在 0.8 以上**、假报“进展正常”。黑色聚合曲线取逐帧最小，**正确跌破 −0.5**，把绿的假阳性压掉。这张图把 Table 3 的“$M{=}1$→$M{=}3$：72.7%→92.3%”从数字变成了可见的机制：正是绿这种“单模型 OOD 过度自信”会在 $M{=}1$ 时毒化训练，而 worst-of-$M$ 把它挡在门外。

## 图表索引与讲解

| 图 / 表 | 读图重点（证明什么） | 关联问题 |
| --- | --- | --- |
| Figure 1（未提取，据 caption） | 全文总览：STEAM 是自监督 advantage 建模，无需人工标注/reward，可作用于 expert/human-correction/rollout；配 CFGRL 显著提升真实任务；含“折毛巾失败→重试成功”的 advantage 可视化。 | STEAM 的输入数据类型与用途边界。 |
| Figure 2（未提取，据 caption） | 三段流水：(a) expert 示范提供 frame pair、算 normalized offset（正/反向都用）；(b) $M$ 个预测器映 frame pair+指令→temporal bin 分布→标量 advantage；(c) 训练好的集成给混合质量数据打分，$A_{\text{STEAM}}$ 经 CFGRL 引导 VLA 策略。 | 自监督 target→分箱预测→集成→策略，如何串成一条离线管线。 |
| Figure 3（未提取，据 caption） | 四任务的机器人与 setup：towel(5)/chip(8)/cola(4) 用 ARX 双臂、pick(2) 用单 Franka；数据含 expert/rollout/correction 不同混比。 | 任务 horizon 与数据构成差异如何影响增益。 |
| Figure 4–6（未提取，据正文） | Fig.4 曲线：expert 高、succ-rollout 抖、fail 掉零、correction 先掉后回；Fig.5 密度：expert 峰在 +1、fail 峰在 ≤0；Fig.6 求和：fail 被显著低值分开，且失败发生阶段影响累计量。 | STEAM 能否细粒度区分推进/停滞/失败/恢复（Q1）。 |
| Figure 7（未提取，据正文数值） | 数据源阶梯：towel/chip/cola 里 STEAM(Exp)>BC、Full 最高；pick-and-place 里 STEAM(Exp)<BC、Full 才回升到 80。 | 不同数据源对策略的边际贡献；过滤在“已很干净的小数据集”上的副作用。 |
| **Figure 11（已嵌入）** | 三预测器 vs 聚合：绿在 retry 段过估计、蓝橙正确下掉，黑（取最小）跌破 −0.5 压掉假阳性。 | ensemble-min 为何必要（Q3、Table 3 的机制解释）。 |
| Table 1 | 四任务成功率/Score/吞吐；STEAM 全面第一，吞吐也涨，RECAP 有时不如 BC。 | STEAM 相对 BC/HG-DAgger/RECAP 的净增益（Q2）。 |
| Table 2 / Table 3 | $N$：2→8→32 单调涨到 92.3%；$M$：1→3 从 72.7% 跳到 92.3%，5 不再涨。 | bin 粒度与集成规模的最优点（Q3）。 |
| Table 4 | 逐任务超参：towel/chip/cola 用 $N{=}H{=}k_{\max}{=}32$、pick 用 16；expert 阈值 0.8、non-expert 0.3。 | 复现所需的关键配置与“分源阈值”设计。 |

## 和你的论文库中其他条目的关系

- 对 [[@yu2026warp-rm]]（WARP-RM）：**最直接的同门**。两者都把 expert 轨迹的**时间结构**转成 progress/reward 类信号，也都用“相对进展”而非绝对进展。差别在机制取向——WARP-RM 偏 **time-warp 数据增强 + relative progress**，STEAM 偏 **分布式带符号分箱 advantage + ensemble-min 保守聚合**。建议交叉读：STEAM 的“$M{=}1$→$M{=}3$ 压过估计”能否移植到 WARP-RM 的 reward 头上；WARP-RM 的 time-warp 能否作为 STEAM 反向配对（pseudo-failure）之外的第二种时间增广。
- 对 [[@wang2026wvm]]（World Value Model）：两者都在做“给机器人数据/进展打分”，但监督来源相反——WVM 借世界模型的未来建模能力出 value/score，STEAM 完全**不依赖任何 world model 或 VLM 先验**，只用轨迹内相对帧序。可对照“打分信号是否需要物理接地的生成式先验”这一取舍：STEAM 恰恰用 introduction 里“VLM 先验未接地会出噪声”为自己的自监督路线辩护。
- 对 [[@li2026zr0]]（VLA 训练与推理监督）：STEAM 处在 VLA 的**上游数据筛选层**——它把 $\pi_0$ 这类 VLA 策略的训练数据按帧级 advantage 二值化后经 CFGRL 引导。可作“数据质量信号如何注入 VLA 训练”的纵向串读。
- 对世界模型线 [[@wang2026orca]]、[[@gigaworld2026roadmap]]、[[@zhang2026qwen-robotworld]]、[[@gao2026fast-leworldmodel]]：这些聚焦 latent/视觉世界建模与规划；STEAM 提供一个**不生成世界、只评估轨迹**的对照视角——在“如何利用混合质量真实数据”这个共同痛点上，它主张“便宜的时间自监督 + 保守聚合”而非“昂贵的世界/价值模型”。
- 论文自身引用的近亲（**均不在当前库**，如需可另行入库）：CFGRL [1]（下游策略优化框架）、TimeRewarder [8]（最接近的 prior，dense reward 版）、ARM [4]（人工标注版相对进展）、RECAP [5]（VLM value 基线）、ReWiND [21]、VLAC [9]、SARM [3]、SPARS [26]（局限里提到的 phase-aware 方向）、$\pi_0$ [24]、HG-DAgger [25]。

## 可追问点

1. **归一化的“效率偏好”是把双刃剑**：Eq.(2) 用 $L_{\max}/L_{\tau_k}$ 让短示范得分更高。但某些任务里“慢而稳”才是对的（如易碎品、精密对齐）。在这类任务上，STEAM 会不会系统性惩罚正确的谨慎执行？
2. **反向配对当 pseudo-failure 的可靠性**：把成功轨迹倒放当负偏移，隐含“回退运动≈失败”。但有些任务的合法动作本身包含往复（如擦拭、来回对齐）。对这类周期性/往复运动，反向配对是否会制造错误的负 target？
3. **ensemble-min 的 recall 代价**：作者自陈“保守偏置可能略降 recall”。$M{=}5$ 已不再涨（还略降到 90.9%）——是否说明 min 聚合在 $M$ 大时会过度保守、把真正的高进展帧也压掉？有没有介于 min 与 mean 之间的分位聚合（如取次小值）更优？
4. **pick-and-place 的反常**：STEAM(Exp) 55.0 < BC 63.8。这暴露“在已很干净的小数据集上，过滤=缩小训练集”的失效模式。能否用“expert 阈值随数据量自适应”来避免这种过度剪枝？
5. **分源阈值（0.8 / 0.3）的敏感性**：expert 保留 top 80%、non-expert 保留 top 30% 是四任务通用的固定值。这两个数如果换，成功率会怎样？论文没给这条消融，属**需回看/未提供**。
6. **只用视觉**：作者在局限里承认 STEAM 主要靠视觉观测，可能漏掉“视觉不可见但关键的状态差异”（如接触力、夹持是否打滑）。加 robot state 作为学习 target 后，advantage 头是否需要重新设计 target 空间？

## 我的阅读笔记

这篇的价值不在“又一个 progress/reward 模型”，而在它把问题从“如何造一个准的进展信号”重构成 **“如何造一个在混合质量数据上不制造假阳性的信号”**。它给的答案很省：**监督完全免费（轨迹内相对帧序 + 成功轨迹倒放），抗噪完全靠结构（worst-of-M 集成取最小）**。Fig.11 那张三预测器分歧图是全文最有说服力的一击——它把“单模型在 OOD 回退段过度自信”从一句话变成一条肉眼可见的绿色假阳性曲线，也让 Table 3“$M{=}1$→$M{=}3$：72.7%→92.3%”的机制无法被绕过。Table 1 里 RECAP 在 cola/pick 上不如 BC，则从反面坐实了 introduction 对“VLM value 未接地会出噪声”的批评。

但要清醒看边界：**增益高度依赖任务的 horizon 与数据构成**。long-horizon 且有大量 imperfect rollout 的 towel/chip 是主场（+59/+54.3 百分点）；而短、已很干净的 pick-and-place 在只用 expert 时反而掉分（55.0 vs 63.8），要靠 594 条 rollout 才回到 80——这说明 STEAM 的机制是“**从大量不完美数据里捞有用帧**”，而非“把已很好的小数据集再榨一层”。方法里两个假设也决定了它的适用面：**“时间前进≈任务进展”**（对往复/多阶段回退任务不总成立）与**“回退运动≈失败”**（反向配对的隐含假设）。加上它目前**只用视觉、advantage 只编码 temporal efficiency**，我会把它定位成“一个把真实混合质量数据变成可用训练信号的、极省标注的离线筛选器”，而不是“一个通用的机器人 reward/value 模型”。

后续我会把它和 [[@yu2026warp-rm]] 并读（两条“时间结构→进展信号”的路线，比较增强方式与聚合方式），并从 [[@li2026zr0]] 的 VLA 训练视角回看“帧级 advantage 二值化 + CFGRL”这条数据注入链路是否可迁移到别的策略骨干。
