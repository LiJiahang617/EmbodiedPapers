---
tags:
  - bilingual-reading
  - deep-reading
source_pdf: "[[papers/pdfs/chen2025robo-dopamine.pdf]]"
paper: "[[@tan2025robo-dopamine]]"
images: "papers/images/chen2025robo-dopamine/"
image_index: "[[papers/images/chen2025robo-dopamine/index.md]]"
created: 2026-09-02
source_version: "arXiv 2512.23703v1, cross-checked with CVPR 2026 camera-ready"
reading_standard: "full bilingual reading"
---

# Robo-Dopamine: General Process Reward Modeling for High-Precision Robotic Manipulation

paper:: [[@tan2025robo-dopamine]]
pdf:: [[papers/pdfs/chen2025robo-dopamine.pdf]]
images:: [[papers/images/chen2025robo-dopamine/index.md]]
reading:: [[papers/bilingual/tan2025robo-dopamine_中英混读.md]]

## 核心词汇速查

| English | 中文 | 在本文中的含义 |
| --- | --- | --- |
| process reward model, PRM | 过程奖励模型 | 对任务中间状态或状态转移给出进度信号 |
| outcome reward model, ORM | 结果奖励模型 | 只在成功或失败终点给出稀疏信号 |
| General Reward Model, GRM | 通用奖励模型 | Robo-Dopamine 的视觉语言进度估计器 |
| Dopamine-Reward | 奖励建模方法 | 由 hop 标签、GRM 和多视角融合组成的奖励侧方法 |
| Dopamine-RL | 策略学习框架 | 将 GRM 奖励接入 online、offline 或 offline-to-online RL |
| step-wise progress | 分步进度 | 以子任务和相邻状态变化为单位的进度监督 |
| relative-relative progress | 相对相对进度 | 相对于剩余目标距离或已完成距离归一化的变化量 |
| progress hop / regress hop | 前进跳 / 回退跳 | GRM 输出的正向或负向相对进度，范围为 `[-1,1]` |
| multi-perspective fusion | 多视角进度融合 | incremental、forward-anchored、backward-anchored 三路估计的组合 |
| incremental prediction | 增量预测 | 从前一步递推当前进度，局部敏感但会累积误差 |
| forward-anchored prediction | 初始锚定预测 | 以初始状态为零点估计当前进度 |
| backward-anchored prediction | 目标锚定预测 | 以目标状态为一点反向估计，接近完成时更敏感 |
| consistency-aware weighting | 一致性感知加权 | 用前向与后向估计的差异调节 OOD 状态的更新幅度 |
| semantic trap | 语义陷阱 | 直接折扣进度差会奖励停留在高进度中间态 |
| policy-invariant reward shaping, PBRS | 策略不变奖励塑形 | 用势函数改变学习信号但保持每个状态的最优动作排序 |
| one-shot GRM adaptation | 单示范 GRM 适配 | 用一条新任务专家轨迹校准奖励模型的进度尺度 |
| zero-hop anchoring | 零跳锚定 | 显式加入几乎不变的状态对并标为零进度 |
| Value-Order Consistency, VOC | 价值顺序一致性 | 预测进度与真实时间顺序的相关性指标 |
| high-precision manipulation | 高精度操作 | 插入、对齐、装配等容错很小且接触丰富的任务 |

## 摘要

### 原文摘要

> The primary obstacle for applying reinforcement learning (RL) to real-world robotics is the design of effective reward functions. While recently learning-based Process Reward Models (PRMs) are a promising direction, they are often hindered by two fundamental limitations: their reward models lack step-aware understanding and rely on single-view perception, leading to unreliable assessments of fine-grained manipulation progress; and their reward shaping procedures are theoretically unsound, often inducing a semantic trap that misguides policy optimization. To address these, we introduce Dopamine-Reward, a novel reward modeling method for learning a general-purpose, step-aware process reward model from multi-view inputs. At its core is our General Reward Model (GRM), trained on a vast 3,400+ hour dataset, which leverages Step-wise Reward Discretization for structural understanding and Multi-Perspective Reward Fusion to overcome perceptual limitations. Building upon Dopamine-Reward, we propose Dopamine-RL, a robust policy learning framework that employs a theoretically-sound Policy-Invariant Reward Shaping method, which enables the agent to leverage dense rewards for efficient self-improvement without altering the optimal policy, thereby fundamentally avoiding the semantic trap. Extensive experiments across diverse simulated and real-world tasks validate our approach. GRM achieves state-of-the-art accuracy in reward assessment, and Dopamine-RL built on GRM significantly improves policy learning efficiency. For instance, after GRM is adapted to a new task in a one-shot manner from a single expert trajectory, the resulting reward model enables Dopamine-RL to improve the policy from near-zero to 95% success with only 150 online rollouts, approximately 1 hour of real robot interaction, while retaining strong generalization across tasks.

### 中文解读

论文把真实机器人 RL 的奖励问题拆成「看得准」和「用得对」两层。看得准对应 Dopamine-Reward，它用多视角状态、分步 hop 标签和三路进度估计来判断局部前进或回退。用得对对应 Dopamine-RL，它不把进度差直接当作折扣奖励，而是把 GRM 进度当作 potential，构造策略不变的塑形项。这样设计的目标不是让 reward model 代替环境成功判定，而是让它提供可用于探索的密集方向。

摘要中的 one-shot 只描述 GRM 适配。真机实验的 ConRFT 策略仍以 20–30 条 policy demonstrations 做离线初始化，并配合 human-in-the-loop。150 次 rollout 是在线交互达到最终成功率 80% 所需的样本效率指标，不应理解为整个系统只看一条示范就完成训练。

## 一句话总结

作者提出一个以多视角、step-aware GRM 为核心的奖励接口，并用 PBRS 形式把估计进度安全地接入 RL，试图同时解决过程奖励的感知误差、长时程漂移和密集奖励改变任务目标的问题。

## 论文主线

```text
多源机器人、仿真和人类视频
        ↓ 人工多视角 keyframes + 分层采样
状态序列 S={s0,...,sM}，全局进度 Φ(si)=i/M
        ↓ 相对相对 hop 标签 H(sp,sq)∈[-1,1]
35M-sample GRM 训练集
        ↓
RoboBrain 2.0 / Qwen2.5-VL GRM
  task text + initial + goal + BEFORE/AFTER multi-view images
        ↓
incremental + forward-anchored + backward-anchored
        ↓ 多视角融合 Φ*，可选一致性保守更新
        ↓ 一条 human trajectory 做 GRM one-shot adaptation
        ↓ rGRM = rgold + γΦ*(s') − Φ*(s)
        ↓ PPO / ReinFlow / Cal-QL 等策略优化
        ↓ 仿真与真实机器人高精度操作
```

论文的因果链可以分成三个可分离的问题。GRM 的 VOC 和完成判断只测奖励估计质量，Dopamine-RL 的 success rate 和 rollout 数才测下游策略效果。中间还隔着奖励阈值、RL 算法、策略初始化和真实环境，因此不能把两个指标混成一个「模型准确率」。

## 贡献与结论对照

| 论文主张 | 方法位置 | 主要证据 | 证据边界 |
| --- | --- | --- | --- |
| 通用 GRM 能细粒度排序不同任务的状态 | Hop 标签、GRM、融合 | Table 1 的七套数据平均 VOC 为 0.96、0.96、0.94（8B multi-view） | 表格正文一处写 eight datasets，实际列出七套，且标签依赖专家轨迹时间顺序 |
| 多视角能缓解遮挡和近失误判断 | Multi-view GRM | Table 2 完成判断 92.8%，single-view 为 83.9%，GPT-5 为 83.9% | 只测三个真机任务各 60 条 rollout，未报告跨相机布置的置信区间 |
| 进度差可以高效帮助 RL | Dopamine-RL | Table 3 仿真 81.0%、395 rollout，真机 95.2%、150 rollout | Rollout 指达到最终成功率 80% 的门槛，150 次不能严格等同于 150 次后已达 95.2%；真机策略仍用 20–30 条示范、ConRFT 和 HIL |
| PBRS 避免 semantic trap | `γΦ(s')−Φ(s)` | Appendix Proof 2、5 和去塑形消融 41.3% | 证明针对有界 Markov 代理奖励；有限 horizon 和 GRM 自动完成阈值会留下真实目标偏差 |
| 单示范能把预训练 GRM 迁移到新任务 | One-shot GRM Adaptation | MSE 适配公式，去适配成功率从 85.0% 降到 63.2% | 单示范校准的是 reward model，不是整个策略训练；公开实现使用答案 token 的 CE 训练描述 |
| 训练数据带来跨 embodiment 泛化 | 3,400 小时多源数据 | 覆盖 real、simulation、human，Table 4 OOD 相对下降 8.3–19.3% | 主要 OOD 是已知任务的物体、布局、背景变化，非完全未见 task-level 泛化 |

## 结构地图

| 原文 section | 这一节推进什么 | 关键证据或公式 |
| --- | --- | --- |
| Abstract | 提出奖励感知与奖励塑形的双层问题 | 35M samples、VOC、95% / 150 rollouts |
| 1 Introduction | 说明 sparse reward、handcrafted reward 和现有 PRM 的缺口 | Fig. 1 teaser；两个 limitation |
| 2 Related Work | 将工作放在 robotic RL、learned PRM 和多视角进度估计中 | GVL、VLAC、SARM 等对照 |
| 3 Method | 从轨迹构造 hop 监督，融合三种进度，再接入 PBRS | Eq. 1–17、Fig. 2–3 |
| 3.1 GRM Construction | 用 keyframe、分层采样和 zero-hop 生成通用训练对 | Eq. 1–2 |
| 3.2 Multi-Perspective Fusion | 处理局部误差累积、起点锚定和终点敏感性 | Eq. 3–8；可选 Eq. 9–11 |
| 3.3 Dopamine-RL | 单示范适配、策略不变塑形和算法兼容 | Eq. 12–17 |
| 4 Experiments | 分别测 reward accuracy、策略效率、泛化与消融 | Table 1–5 |
| 5 Conclusion | 总结高精度操作的奖励接口并给出扩展方向 | 约 95% success、约 150 rollouts |
| Appendix A | 证明有界进度、semantic trap、折扣一致性和策略不变性 | Proof 1–5 |
| Appendix B | 展开数据来源、embodiment、采样和增强 | Table 6–7；Fig. 5 |
| Appendix C | 给出 GRM、仿真和真机训练设置 | Table 8–10；Fig. 7 |
| Appendix D–F | 展示定性结果、未来工作与 camera-ready 敏感性 | Fig. 8–11；initial/goal、noisy demo 分析 |

## 按原文 section 精读

### 1. Introduction

#### 本节要解决的问题

引言从大规模 imitation learning 的局限切入。静态专家数据让策略拥有稳定先验，却难覆盖长时程接触、精细对齐和 OOD 状态。RL 能通过环境交互修正策略，但真实机器人缺少便宜而可靠的 reward。二值成功信号过于稀疏，手工 dense reward 又需要任务专家逐项设计。

作者因此转向 learned Process Reward Models。引言把现有 PRM 的困难归纳成两组。第一组是感知和监督结构，task-specific 设计限制跨任务迁移，近似均匀的 reward 分配难突出关键子步骤，single-view 在手部遮挡或物体被夹住时看不到细节。第二组是奖励如何进入 RL，直接把进度差放进 discounted return 会改变优化目标，策略可能停在「good-enough」状态。

![[papers/images/chen2025robo-dopamine/dp_teasor_page1.png|760]]

Fig. 1 `Overview of Robo-Dopamine` 将数据、GRM、融合、one-shot adaptation、policy-invariant shaping 和策略学习放在一张图中。左侧的 35M 数据与右侧的 success bar 是规模和下游结果的概览，不是单独的因果消融。图中 radar 的 GRM reward accuracy 与 bar chart 的 policy success 也应分开读。

#### 论文提出的回答

Dopamine-Reward 负责「奖励模型是否知道状态变了多少」，Dopamine-RL 负责「这个信号是否会把策略带向错误目标」。这种拆分让后文可以分别安排 VOC、完成分类、PBRS 推导和策略消融。引言最后给出三条 headline，GRM reward assessment 超过 92.8% 完成判断、Dopamine-RL 在约 150 次真机 rollout 达到约 95%，以及在物体、布局和背景变化下保持较小性能下降。

这里有一个数字口径需要提前标记。Table 1 实际列出 DROID、AGIBOT-World、RoboBrain-X、LIBERO、RoboCasa、RoboTwin2.0 和 EgoDex 七套数据，正文开头却写 eight datasets。阅读后续分析应以可枚举的七套为准。正文还写「four state-of-the-art reward models」，表中实际只有 GVL 和 VLAC-2B 两个外部 reward-model baseline，另外四列是作者自己的 GRM variants。

### 2. Related Work

#### Reinforcement Learning for Robotic Skills

作者把机器人 RL 工作按优化方式和策略架构分组。offline RL 利用已有轨迹，online RL 直接与环境交互，offline-to-online 方法在安全初始化后再吸收真实反馈。策略则可以是 fully-connected、autoregressive、diffusion 或 flow-based。论文的切入点不在于发明新的 RL optimizer，而在于提供一个能跨这些 optimizer 复用的 reward interface。

#### Learned Process Reward Models

Outcome Reward Model 通常只判断最终成功，长时程探索很难得到有效梯度。已有 PRM 用 VLM 对帧对给 progress delta，或对单帧给相对于语言目标的分数。Robo-Dopamine 的区别有三处。它让标签显式依赖前进和回退的剩余距离，输入保留 synchronized multi-view，奖励塑形则遵守 PBRS 的折扣形式。作者用 GVL、VLAC-2B 和 SARM 作为主要语境，但并未在同一实验中覆盖所有近年 reward model。

### 3. Method

#### 3.0 总体框架

![[papers/images/chen2025robo-dopamine/dp_method_page1.png|760]]

Fig. 2 `The overview of our method` 左半边展示 GRM 如何从 initial、goal、BEFORE、AFTER 和 task prompt 预测 hop，底部再以三路估计做融合。右半边展示一条 human demonstration 如何适配 GRM，以及 dense reward 如何通过 policy-invariant shaping 进入 PPO、ReinFlow、Cal-QL 等 RL。图中「universal compatibility」是接口层主张，性能仍取决于具体算法和数据缓冲区。

#### 3.1 General Reward Model Construction

##### Step-wise task progress discretization

一条专家轨迹先由人工标出的同步多视角 keyframes 切成 `N` 个子任务区间。$K_0$ 是初始状态，$K_N$ 是成功终态，每个 keyframe 同时包含可用相机的图像。设每个视角有 $L$ 帧、chunk size 为 $C$，每段插入的中间采样点数为

$$
m=\left\lfloor\frac{1}{N}\left\lfloor\frac{L}{C}\right\rfloor\right\rfloor.
$$

这些采样点组成 $\mathcal S=\{s_0,s_1,\ldots,s_M\}$，作者用 $\Phi(s_i)=i/M$ 作为全局进度。这个定义优点是标签便宜、统一且能覆盖任意任务，代价是把专家轨迹的时间索引当作进度代理。它假设 keyframe 切分足够准确，并默认相邻采样点在进度尺度上近似可比。

##### Hop-based relative progress normalization

直接回归 $\Phi(s_q)-\Phi(s_p)$ 时，连续累加容易漂移到 $[0,1]$ 外。论文改为 relative-relative hop。对一对 BEFORE 状态 $s_p$ 和 AFTER 状态 $s_q$，

$$
\mathcal H(s_p,s_q)=
\begin{cases}
\dfrac{\Phi(s_q)-\Phi(s_p)}{\Phi(s_M)-\Phi(s_p)}, & q\ge p\quad\text{progress},\\[6pt]
\dfrac{\Phi(s_q)-\Phi(s_p)}{\Phi(s_p)-\Phi(s_0)}, & q<p\quad\text{regress}.
\end{cases}
$$

若向前走，分母是尚未完成的距离，因此越接近终点，同样的绝对变化会得到更有辨识度的正 hop。若回退，分母是已经走过的距离，负 hop 表示从当前进度退回的相对比例。理想标签落在 $[-1,1]$，每个 pair 还会在 score bins 与 temporal-gap bins 的笛卡尔组合中分层采样。附录的有界性证明只对 incremental 递推直接成立，forward 锚定、backward 锚定和三路平均在预测误差下未自动保证落在 $[0,1]$，部署时需要额外校准或裁剪。这里的「step-aware」来自相对尺度和子任务结构，不是额外的人类 salience 标注。

##### 分层采样与 zero-hop

连续 hop 被放进 $N_{hop}$ 个 score bins，状态对的时间间隔再放进 $N_{dis}$ 个 gap bins。这样可同时看小幅局部变化、大幅跳跃、短时间快速动作和长时间缓慢动作。为了避免随机采样被静态或小正变化占满，作者额外抽取比例 $\alpha$ 的 zero-hop 对，要求

$$
|\Phi(s_q)-\Phi(s_p)|\le\epsilon.
$$

camera-ready Appendix 给出的实现示例是 25 个 score bins 覆盖 $[-100\%,100\%]$、4 个 gap bins、zero-hop 比例约 5%，并在候选池过采样后填满各桶。负 hop 主要由专家轨迹中反向配对产生，不能等同于系统收集了大量真实失败恢复片段。

![[papers/images/chen2025robo-dopamine/dp_data_page1.png|760]]

Fig. 4 `Overview of GRM training data` 的环形图把 real-world、simulation 和 human-centric 来源合到 35M，右侧长尾柱状图显示任务类别频率。图支持「覆盖广」和「长尾」这两条数据主张，但不能单凭柱状图证明每个长尾任务都有足够的失败样本。

##### GRM 输入与输出

GRM 采用 RoboBrain 2.0 的 Qwen2.5-VL 风格架构，训练 3B 和 8B 两个规模。官方 inference example 的一次 query 共有 8 张图，reference start/end 各 1 张，BEFORE 三视角，AFTER 三视角。语言 prompt 要求模型作为 impartial progress evaluator，输出离散百分比 token，例如 `<score>+15%</score>` 或 `<score>-4%</score>`。三种 perspective 需要分别运行 query，再将结果递推或平均。

![[papers/images/chen2025robo-dopamine/dp_model_page1.png|760]]

Fig. 6 `Overview of GRM model structure` 显示 shared vision encoder、projector、LLM decoder 和 score token。作者把 hop 离散成 token 后采用自回归语言模型训练。论文 Eq. 12 将 one-shot 适配写成 hop 的 MSE，公开微调脚本则保留答案 token 并用 cross-entropy 优化，二者是目标表达上的不同层次，复现时不能默认完全等价。官方后处理还会以约 75% 概率把 reference start/end 换成另一随机样本的锚点，同时保留 queried BEFORE/AFTER，这种 cross-sample anchor swap 是训练增强，也可能引入锚点噪声。

#### 3.2 Multi-Perspective Progress Fusion

单一递推器会积累每一步的预测误差，单一绝对锚点又会受 initial 或 goal 图像质量影响。论文因此让同一个 GRM 从三种视角估计当前全局进度。

**Incremental prediction** 从 $\Phi^*(s_{t-1})$ 和当前 hop $H$ 更新。若 $H\ge0$，

$$
\Delta\Phi^*_{t-1,t}=[1-\Phi^*(s_{t-1})]H,
\qquad
\Phi_I^*(s_t)=\Phi^*(s_{t-1})+\Delta\Phi^*_{t-1,t}.
$$

若 $H<0$，则改为 $\Delta\Phi^*_{t-1,t}=\Phi^*(s_{t-1})H$。正向更新只占剩余空间，回退更新只缩减已有进度，所以在 $H\in[-1,1]$ 时递推不会越过 0 和 1。它对局部接触和短暂回退最敏感，却会把早期误差带到整条长轨迹。

**Forward-anchored prediction** 直接把初始状态当作 BEFORE，

$$
\Phi_F^*(s_t)=\mathcal H^*(s_{init},s_t).
$$

它提供稳定的全局参照，但若 initial image 不清楚，所有时刻都会受到同一锚点误差影响。

**Backward-anchored prediction** 把 goal 当作 BEFORE，并设目标进度为 1，

$$
\Phi_B^*(s_t)=1+\mathcal H^*(s_{goal},s_t).
$$

它在接近完成时有较强分辨率，适合区分「快插入成功」和「看似到位但仍未插入」。代价是 goal image 或目标描述有误时会直接污染后段估计。

基本融合是三路平均，

$$
\Phi^*(s_t)=\frac{\Phi_I^*(s_t)+\Phi_F^*(s_t)+\Phi_B^*(s_t)}{3}.
$$

这种平均不是学习到的 attention，而是一个固定、易部署的 ensemble。Table 5 显示三路中的任一路单独使用都低于完整融合。

##### Optional consistency-aware weighting

作者还给出 OOD 保护机制。先计算前后锚定均值和归一化差异，

$$
\bar\Phi^*(s_t)=\frac{\Phi_F^*(s_t)+\Phi_B^*(s_t)}{2},
\qquad
\Delta_{norm}(s_t)=\frac{|\Phi_B^*(s_t)-\Phi_F^*(s_t)|}{\bar\Phi^*(s_t)+\epsilon}.
$$

再以 Gaussian kernel 得到置信权重

$$
w_t=\exp\left[-\alpha\,\Delta_{norm}(s_t)^2\right],
$$

并用

$$
\Phi^*(s_t)=\Phi^*(s_{t-1})+\frac{w_t}{2}\left(\bar\Phi^*(s_t)-\Phi^*(s_{t-1})+\Delta\Phi^*_{t-1,t}\right)
$$

做保守更新。前后锚点分歧大时，系统宁可保留旧进度，也不让 OOD 高分立即变成策略梯度。需要留意的是，论文把它标为 optional，主表没有单列「启用一致性」相对于简单平均的收益。

![[papers/images/chen2025robo-dopamine/dp_case_page1.png|760]]

Fig. 3 `Reward profiles on a challenging real-world rollout` 对比 human reference、VLAC 和 GRM。图中 VLAC 在错误插入、位置过低和 misalignment 时仍保持高分，GRM 会在这些节点下跌，并在最终插入附近升到高值。它直观支持「奖励曲线能表达回退」，但仍是一条精选 rollout，不是统计评估。

#### 3.3 Dopamine-RL Framework

##### One-shot GRM Adaptation

新任务只提供一条 human expert trajectory。预训练 GRM 已学到跨任务的 object affordance 与操作顺序，因此适配阶段只需把新任务的 hop 尺度对齐。论文写成

$$
\mathcal L_{GRM}(\omega)=\mathbb E_{(s_p,s_q)\sim\mathcal D_{human}}
\left\|\mathcal H^*_{\omega}-\mathcal H_{gt}\right\|_2^2,
$$

以预训练参数 $\omega_0$ 初始化，得到任务专属 $\omega_*$。其作用是校准「什么算完成、哪些视觉变化算前进」，而不是从零学习控制器。

##### 直接进度差的 semantic trap

朴素 dense reward 写成

$$
r_t=\Phi^*(s_{t+1})-\Phi^*(s_t).
$$

放入标准折扣回报后，有限 horizon 的和为

$$
G_T=-\Phi(s_0)+(1-\gamma)\sum_{t=1}^{T-1}\gamma^{t-1}\Phi(s_t)+\gamma^{T-1}\Phi(s_T).
$$

当 $T$ 很大且 $\Phi$ 有界，末项趋近零。优化就变成偏好长时间累积高进度，而不是只关心是否穿过最终成功条件。策略可能快速到达「看起来不错」的中间状态并停在那里，因每一步仍保有较高 proxy reward。这个推导解释了论文所说的 semantic trap，也说明为什么未折扣的直觉「进步就奖励」不能直接搬进 discounted RL。

##### Policy-Invariant Reward Shaping

论文把进度当作 potential，定义单步塑形项

$$
F(s_t,s_{t+1})=\gamma\Phi^*(s_{t+1})-\Phi^*(s_t),
\qquad \gamma=e^{-\lambda h}.
$$

为了避免真实机器人始终需要人工标注终点，作者用 GRM 自己自动化 gold reward。当 $\Phi^*(s_{t+1})\ge1-\delta$ 时置 $r_{gold}=1$，默认 $\delta=0.05$，否则为 0。最终奖励是

$$
r_{GRM}(s_t,a_t,s_{t+1})=r_{gold}+\gamma\Phi^*(s_{t+1})-\Phi^*(s_t).
$$

折扣累加塑形项会 telescoping，

$$
\sum_{t=0}^{\infty}\gamma^tF(s_t,s_{t+1})=-\Phi^*(s_0),
$$

因此

$$
Q_{GRM}^{\pi}(s,a)=Q_{gold}^{\pi}(s,a)-\Phi^*(s),
\qquad
\arg\max_aQ_{GRM}^*(s,a)=\arg\max_aQ_{gold}^*(s,a).
$$

它与 Ng 等人的 Potential-Based Reward Shaping 一致。论文还从 continuous discounted potential $e^{-\lambda t}\Phi(s_t)$ 出发，用 Taylor expansion 和 Forward Euler 说明离散项 $\gamma\Phi_{next}-\Phi_{curr}$ 是一阶时间步更新。严格应用 PBRS 时，需要把 task condition、initial/goal reference 和历史递推视为 augmented Markov state；论文没有展开这一状态扩充。

这里的理论边界需要单独保留。证明使用无限 horizon、Markov state 和有界 potential。有限 episode 的和是 $\gamma^T\Phi(s_T)-\Phi(s_0)$，仍有终端项。论文真机使用 $\gamma=0.98$，仿真使用 $\gamma=0.99$，若 horizon 为 200，终端系数仍约为 0.018 或 0.134，不能自动忽略。更关键的是实际 $\Phi^*$ 的 incremental 分支带有轨迹历史，自动 $r_{gold}$ 也来自 GRM 阈值，所以不变性是相对于定义的 proxy reward，而不是对真实物理成功标签的无条件保证。

##### Universal RL-Algorithm Compatibility

作者把 reward shaping 写成 transition-local 的形式，因而声称它可接 online RL、offline RL 和 offline-to-online RL，也可接 value-based 或 gradient-based optimizer。实验覆盖 PPO + OpenVLA-OFT、ReinFlow + $\pi_0$ 和 ConRFT / Cal-QL + Octo-Small。这个主张更像接口兼容性，而非每个算法都做了同等规模的独立验证。

### 4. Experiments

实验部分把方法拆成四个问题来验证。RQ1 先问 GRM 能否在不同数据域和时间采样密度下恢复状态顺序，再问它能否区分 success、partial success 和 failure。RQ2 才把 GRM 作为 reward 接入策略，比较成功率、达到目标所需交互和受控 OOD 泛化。RQ3 去掉三路融合，RQ4 分别去掉 PBRS 与 one-shot adaptation。这样的顺序把 reward assessment 与 downstream policy learning 分开，后面的表格也应按这条证据链阅读。

### 5. Conclusion

结论把工作概括为「通用、分步、多视角的 reward model」加「策略不变的 dense shaping」。作者认为多源数据和融合让 GRM 能看见遮挡下的细小状态变化，PBRS 让这些信号可以进入不同 RL 算法，真机结果则显示约 150 个在线 rollout 可把策略推到约 95% 的最终成功率。结论没有把 VLM reward latency、连续视频、触觉和音频说成已解决问题，而是列为后续方向。结合 Table 3 的 rollout 定义，约 95% 是最终 SR，150 是到达最终 SR 的 80% 门槛，两个数字不能合成一个严格的时间点断言。

### Appendix A–F

补充材料提供五个理论证明、数据统计、训练超参、仿真与真机算法细节、定性曲线和未来工作。camera-ready 版本还加入 initial/goal 图像不完美与 noisy one-shot demonstration 的 sensitivity analysis。前者显示 anchor 模式示例准确率从 0.96 降到 0.87，incremental 从 0.95 降到 0.93；后者报告 suboptimal demo 造成的 reward accuracy 降幅小于 3%，主要表现为 RL 收敛稍慢。两项结果都没有完整置信区间，适合作为工程提示，不是普适鲁棒性定理。

## 方法细节

### 训练数据与标签生成

原始语料共 27.23M frames，经过 multi-view expansion 和 augmentation 后形成约 35M training samples。论文给出约 3,400 小时、超过 100K trajectories、超过 350 个日常操作任务的总规模。各来源的 raw sample 统计如下。

| 域 | 来源 | raw samples |
| --- | --- | ---: |
| Real-world | AGIBot-World | 3.400M |
| Real-world | DROID | 8.983M |
| Real-world | RoboBrain-X | 3.025M |
| Real-world | Self-Collected Real | 1.107M |
| Simulation | LIBERO | 1.330M |
| Simulation | RoboTwin | 1.678M |
| Simulation | RoboCasa | 0.523M |
| Human | EgoDex | 6.610M |
| Human | Self-Collected Human | 0.574M |
| 合计 | raw corpus | 27.230M |

增强包括可用 wrist / third-person 视角排列、Random Viewpoint Dropout 和 Context Dropout。任务指令还由 Gemini 2.5 Pro 重标注以增加语言多样性。embodiment 覆盖 Franka Emika Panda、AGIBot-A2D、Agilex Piper、ARX-X5、Galaxea 和 UR5。真实数据约占最终语料 60%，simulation 约 13%，human 约 26%，四舍五入后不一定正好相加为 100%。

### GRM 训练配置

| 配置 | GRM-3B | GRM-8B |
| --- | ---: | ---: |
| Global batch | 512 | 256 |
| Vision / LLM learning rate | $5\times10^{-6}$ / $1\times10^{-5}$ | $5\times10^{-6}$ / $1\times10^{-5}$ |
| Scheduler | cosine decay | cosine decay |
| Warmup ratio | 0.03 | 0.03 |
| Optimizer | AdamW | AdamW |
| Weight decay | 0.1 | 0.1 |
| Max sequence length | 8192 | 8192 |
| TP / PP | 1 / 1 | 2 / 2 |
| Hardware | 128 × H100 | 128 × H100 |
| Duration | 约 8 天 | 约 14 天 |

每个 transition 需要 incremental、forward 和 backward 三种推理模式。部署延迟因此不是一次 VLM query 的成本，camera-ready Future Work 提议用 INT4/INT8 或 KV-cache compression 降低开销。

### Dopamine-RL 中的策略算法

仿真有两条设置。PPO + OpenVLA-OFT 使用 action chunk size 8，并通过 clipped objective 控制更新幅度。ReinFlow + $\pi_0$ 把 flow matching 的确定性路径加入可学习噪声，使每个 denoising step 具有可计算的 transition probability，再用 PPO-style objective 优化 velocity 和 noise network。LIBERO-Goal 平均成功率约 81%，训练约 50 小时，使用 8 张 H100。

真机使用 ConRFT。离线阶段用 20–30 条 policy demonstrations 做 BC 与 Cal-QL 初始化，online 阶段把真实 rollout 放入 replay buffer，并在危险动作处由 HIL 修正。策略骨干是 Octo-Small，动作头是 consistency policy。论文的「one-shot」只减少 GRM 适配所需的额外 reward demonstration，不替代这套策略初始化。

## 实验设置、数据集、基线、指标

实验围绕四个问题展开。RQ1 测 GRM 是否能排序过程和判断终点，RQ2 测 Dopamine-RL 的成功率、样本效率和泛化，RQ3 测三路融合，RQ4 测 policy-invariant shaping 与 one-shot adaptation。

| 评测层 | 数据与任务 | 方法 / 基线 | 指标 |
| --- | --- | --- | --- |
| 过程排序 | DROID、AGIBOT-World、RoboBrain-X、LIBERO、RoboCasa、RoboTwin2.0、EgoDex | GVL、VLAC-2B、GRM-3B/8B，single/multi-view | VOC，Sparse / Medium / Dense |
| 完成判断 | stacking、folding、clearing，各 60 条真机 rollout | Gemini-2.5-Pro、GPT-5、Qwen3-VL、RoboBrain 2.0、GVL、VLAC、GRM | SE / PSE / FE 分类准确率 |
| 仿真策略 | 正文写 LIBERO-Goal 与 RoboTwin2.0，共 10 tasks；Appendix 具体展开 LIBERO-Goal 10 tasks | BC、RL + sparse、Dopamine-RL | success rate、达到最终 80% 所需 rollout |
| 真机策略 | 8 个 fine-grained / long-horizon tasks | BC、RL + sparse、Dopamine-RL + ConRFT | success rate、rollout |
| 泛化 | Insert Square、Circuit、Cap Pen | BC 对比 Dopamine-RL | ID/OOD 成功次数与 relative drop |
| 组件消融 | 3 个真机任务 | 单路估计、去 shaping、去 one-shot | 平均 success rate |

VOC 通过打乱轨迹帧并比较预测顺序与真实时间顺序计算，取值范围为 `[-1,1]`。Sparse 只取主要 keyframes，Medium 在 keyframes 间均匀取样，Dense 在整条轨迹均匀取样。完成判断规则为，若最终进度大于 0.8 且最后三分之一平均进度大于 0.6，则标为 SE；若全轨迹平均进度至少为 $\xi=0.4$，则标为 PSE；其余为 FE。Table 2 的 GPT-5、Gemini、Qwen3-VL 对照只给出推荐 prompt 和模型名，未固定 API 版本、采样参数与输入信息量；它们与 GRM 的多视角和 start/end anchor 并非严格同模态对照。

## 主要结果、消融或对比

### Table 1 过程排序 VOC

| 方法 | Sparse | Medium | Dense |
| --- | ---: | ---: | ---: |
| GVL | 0.20 | 0.12 | 0.13 |
| VLAC-2B | 0.24 | 0.29 | 0.33 |
| GRM-3B single-view | 0.91 | 0.89 | 0.87 |
| GRM-3B multi-view | 0.96 | 0.94 | 0.93 |
| GRM-8B single-view | 0.92 | 0.91 | 0.89 |
| GRM-8B multi-view | **0.96** | **0.96** | **0.94** |

GRM-8B multi-view 在七套数据的平均 VOC 近似不随采样变密而崩溃。对比之下，GVL 在 DROID Medium 甚至是负相关，说明单纯逐帧语言打分很难保持细粒度时间顺序。GRM-3B multi-view 在 Dense 下 0.93，高于 8B single-view 的 0.89，显示视角覆盖比参数规模更直接地影响进度排序。

### Table 2 任务完成判断

| 方法 | Stacking | Folding | Clearing | Average |
| --- | ---: | ---: | ---: | ---: |
| Gemini-2.5-Pro | 50/60 | 45/60 | 51/60 | 81.1% |
| GPT-5 | 51/60 | 48/60 | 52/60 | 83.9% |
| Qwen3-VL | 43/60 | 41/60 | 43/60 | 76.7% |
| RoboBrain 2.0 | 38/60 | 35/60 | 41/60 | 61.7% |
| GVL | 25/60 | 27/60 | 15/60 | 37.2% |
| VLAC-2B | 19/60 | 21/60 | 21/60 | 33.9% |
| GRM-8B single-view | 50/60 | 50/60 | 51/60 | 83.9% |
| GRM-8B multi-view | **56/60** | **54/60** | **57/60** | **92.8%** |

每个任务的 60 条 rollout 包含 20 success、20 partial success 和 20 failure。multi-view 相对 single-view 增加 8.9 个百分点，尤其适合区分手部遮挡下的 near-miss。这个结果测的是轨迹级分类，不等价于每一步 reward 的绝对校准误差。

### Table 3 策略成功率和样本效率

| 方法 | Simulation SR | Simulation rollout | Real-world SR | Real-world rollout |
| --- | ---: | ---: | ---: | ---: |
| BC，50 demos | 31.5% | -- | 9.8% | -- |
| RL + Sparse | 79.9% | 560 | 68.0% | 183 |
| Dopamine-RL | **81.0%** | **395** | **95.2%** | **150** |

仿真中 dense GRM 相对 sparse RL 只提升 1.1 个百分点，却把达到最终成功率 80% 的 rollout 从 560 减到 395。真机差距更大，从 68.0% 到 95.2%，同时 rollout 从 183 减到 150。这里的 150 是约 76% 的成功率门槛，不是论文提供的「150 次后已达到 95.2%」曲线终点。这个不对称提示奖励质量在真实接触和感知噪声下更有价值，也提醒读者不要把仿真 81.0% 当作所有收益的代表。正文把仿真来源写成 LIBERO 与 RoboTwin2.0，Appendix D.3 具体展开的却是 LIBERO-Goal 10 tasks，任务集合需要复核。

### Table 4 ID 与 OOD 泛化

| 条件 | Insert Square BC / Ours | Circuit BC / Ours | Cap Pen BC / Ours |
| --- | ---: | ---: | ---: |
| Original ID | 7/20 / **19/20** | 5/20 / **20/20** | 8/20 / **19/20** |
| Object change | 4/20 / **15/20** | 3/20 / **17/20** | 5/20 / **17/20** |
| Layout change | 2/20 / **15/20** | 1/20 / **19/20** | 3/20 / **15/20** |
| Background change | 3/20 / **16/20** | 2/20 / **19/20** | 4/20 / **16/20** |
| Average relative drop | 57.1% / **19.3%** | 60.0% / **8.3%** | 50.0% / **15.8%** |

BC 在 ID 就较低，遇到布局变化后几乎失去可用性。Dopamine-RL 也会下降，但保留更高的相对成功率。论文把这归因于 progress reward 让策略关注物体状态语义，而非背景纹理；不过三个 OOD 轴仍是已知 task family 的受控变化，不足以推出 open-world task generalization。

### Table 5 组件消融

| 变体 | 平均成功率 | 相对完整框架 |
| --- | ---: | ---: |
| Full Dopamine-RL | **85.0%** | -- |
| 只用 incremental | 70.0% | -15.0 |
| 只用 forward-anchored | 65.7% | -19.3 |
| 只用 backward-anchored | 62.5% | -22.5 |
| 去掉 policy-invariant shaping | 41.3% | -43.7 |
| 去掉 one-shot adaptation | 63.2% | -21.8 |

三种 single-perspective 结果都低于平均融合，backward-only 最低，支持局部与全局参照互补。去掉 shaping 的降幅最大，和 semantic trap 的理论预测一致。去掉 one-shot 后仍有 63.2%，说明预训练 GRM 本身带有可迁移先验，但新任务的尺度错位会阻碍收敛。

### 定性与训练曲线

![[papers/images/chen2025robo-dopamine/success_rate_libero.png|700]]

Fig. 7 `Training Curve on LIBERO-Goal` 显示 ReinFlow + $\pi_0$ 使用 GRM shaping 后约 50 小时达到 80% 以上平均成功率。它支持稳定收敛的视觉直觉，但曲线没有给出每个任务的方差和与 sparse reward 的同算力对照。

![[papers/images/chen2025robo-dopamine/dp_hardware_page1.png|760]]

Fig. 4 `Real-world tasks and hardware setup` 展示 Insert Square、Complete Circuit、Fold Towel、Cap the Pen、Pick and Place、Arrange Flowers、Build Blocks 和 Zip the Bag 八个任务，以及 Pika teleoperation 和 calibrated ZED cameras。多视角在这里是数据采集与推理条件，不是只在离线评测中使用的额外输入。

![[papers/images/chen2025robo-dopamine/dp_hop_demos_page1.png|760]]

补充 Fig. `GRM Progress Predictions across Diverse Tasks` 同时画 hop 和 accumulated progress。成功轨迹通常向上，停滞或失败轨迹会出现零 hop 或负 hop。它说明模型能把局部变化转成曲线，但曲线来自作者挑选的 unseen validation tasks，不能替代跨数据集统计。

![[papers/images/chen2025robo-dopamine/dp_interval_page1.png|760]]

补充 Fig. `Progress Estimation Consistency across Sampling Intervals` 用 10、25、50、100 frame stride 重建同一轨迹。曲线重叠支持 hop 归一化对时间粒度较稳健，仍未回答在运动速度突变、循环操作或相机掉帧时是否保持一致。

![[papers/images/chen2025robo-dopamine/dp_real_demo_page1.png|760]]

补充 Fig. `Robustness to Artificial Disturbance during Real-World Execution` 在 Insert Block rollout 中人为移动目标槽。GRM progress 先下降，策略重新对齐、移动到槽上方、完成插入。这个例子把「负反馈可用于恢复」讲得很直观，但只是一条训练约 20 分钟、成功率超过 95% 的精选轨迹。

## 图表、公式与表格线索

| 线索 | 读者应看什么 | 支撑的主张 | 边界 |
| --- | --- | --- | --- |
| Fig. 1 teaser | 35M 数据、GRM、融合、shaping、success radar/bar | 系统全貌与 headline | 不是消融图，reward accuracy 与 policy success 量纲不同 |
| Fig. 2 method | 输入状态、三路预测、one-shot、RL 接口 | 方法模块如何串起来 | 一致性加权标为 optional |
| Eq. 1 | 每个 keyframe 区间的采样点数 | 分步数据构造 | 依赖人工 segment 与 chunk size |
| Eq. 2 | progress / regress hop 的分母 | 相对相对标签与边界控制 | 线性 `Φ=i/M` 是人为进度代理 |
| Eq. 3–8 | incremental、forward、backward 和平均 | 多路融合 | 平均权重固定，未学习 |
| Eq. 9–11 | discrepancy、Gaussian weight、保守更新 | OOD reward hacking 抑制 | 主结果没有单列其增益 |
| Eq. 12 | 单示范 hop MSE | GRM task adaptation | 发布脚本用 token CE，描述存在实现层差异 |
| Eq. 13–17 | discounted potential、PBRS、Q shift | 避免 semantic trap | 依赖 Markov、无限时域和代理 gold reward |
| Table 1 | 七套数据的 VOC 与采样密度 | reward ranking accuracy | 正文曾误写 eight datasets |
| Table 2 | 3×60 rollout 的 SE/PSE/FE | 多视角完成判断 | 轨迹级分类，样本量有限 |
| Table 3 | SR 与达到最终 80% 的 rollout | 下游样本效率 | 150 是约 76% 门槛，仿真任务来源在正文与 Appendix 不一致，仿真和真机策略算法也不同 |
| Table 4 | 三任务三种 shift | OOD robustness | 不是完全未见任务 |
| Table 5 | fusion、shaping、one-shot 消融 | 组件必要性 | 只覆盖三个真机任务 |
| Fig. 4–11 | 数据、prompt、hop 曲线、间隔稳定性、干扰恢复 | 机制的可视化解释 | 多数是定性或精选案例 |

## 主张-证据-边界矩阵

| 主张 | 直接证据 | 尚未证明的部分 |
| --- | --- | --- |
| GRM 能感知细粒度进度 | 7 datasets、3 sampling densities 的 VOC；GRM-8B multi-view 平均 0.96/0.96/0.94 | VOC 只检查顺序，不检查 reward 数值校准或 off-trajectory 可靠性 |
| 多视角提高近失误识别 | 完成判断 92.8% 对 83.9% single-view | 依赖同步标定相机，视角缺失和成本敏感性没有完整曲线 |
| hop 递推保持有界 | Appendix Proof 1 的归纳证明 | 证明直接覆盖 incremental 更新且假设 $H\in[-1,1]$；forward/backward 与三路平均在模型误差下未自动有界 |
| 直接进度差会产生停滞偏好 | Appendix Proof 2 的折扣和展开；去 shaping 41.3% | 真实环境中的停滞行为还受 episode truncation、终止逻辑和算法实现影响 |
| PBRS 保持最优动作 | Eq. 15–17 与 telescoping proof | 只对定义的代理 reward 和理论假设成立，自动 gold 仍由 GRM 估计 |
| one-shot adaptation 有效 | 去适配从 85.0% 降至 63.2% | 适配轨迹质量、任务差异和 token CE/MSE 差异未充分量化 |
| Dopamine-RL 提高样本效率 | 81.0% / 395 仿真，95.2% / 150 真机 | rollout 是达到最终成功率 80% 的门槛，且 ConRFT、HIL、20–30 条 policy demos 和 backbone 差异共同贡献 |
| 策略更能泛化 | OOD relative drop 8.3–19.3% 对 BC 的 50–60% | OOD 仍是已知任务的受控视觉变化，不能代表新任务和新本体 |

## 局限与可追问点

### 监督与模型层

- 人工 keyframe 分段与 $\Phi(s_i)=i/M$ 把时间索引当成进度真值。对于等待、重复擦拭、回收动作或不同速度的专家轨迹，这个 proxy 可能与任务效用不一致。
- 负 hop 多由同一专家轨迹的反向配对获得，真正的 off-policy 失败、碰撞和恢复状态覆盖有限。若策略探索到数据分布外，GRM 可能给出虚假的高分。
- initial 和 goal 不是免费的完美锚点。camera-ready sensitivity analysis 报告 anchor 模式在不完美图像下示例准确率从 0.96 降到 0.87，incremental 从 0.95 降到 0.93。目标模糊时提高 incremental 权重是合理启发式，却还不是自适应校准算法。
- 35M 是 27.23M raw frames 经扩增后的训练样本数，不是 35M 条独立轨迹。按表格相加的 raw corpus 与小时、轨迹、任务统计也没有给出完全可复算的映射。完整训练集在 Hugging Face 上 gated，体量约数百 GB，公开 release 不等于轻量可复现。

### 奖励与理论层

- PBRS 的不变性需要 Markov state、无限 horizon 和有界 potential。实际 incremental progress 含历史，有限 episode 有终端项，严格证明不能直接覆盖所有部署条件。
- `r_gold` 由 $\Phi\ge0.95$ 自动触发。GRM 误判会把 proxy error 变成环境目标，潜在 reward hacking 仍需独立 success detector 或人工审计兜底。
- 论文声称三条 desiderata「uniquely determines」塑形项，但 PBRS 允许任意 potential function。连续时间推导说明为何选择 $\gamma\Phi'-\Phi$，不等于证明所有满足条件的 reward transform 只有这一种。
- 去掉 shaping 的巨大降幅支持理论直觉，却不能单独区分 semantic trap、奖励尺度、终止阈值和具体 RL optimizer 的影响。

### 实验与复现层

- 真机 headline 的一条 demonstration 只属于 GRM adaptation。策略仍有 20–30 条 demonstrations、HIL 和 ConRFT 初始化，复现资源远高于摘要第一印象。
- 官方 GitHub 当前公开 GRM inference/eval、数据生成和 fine-tuning；没有论文 Dopamine-RL、ConRFT、PPO、ReinFlow 的完整端到端 policy-training code。公开 evaluation 默认六类 benchmark、固定 interval，并只跑正向与反向 incremental，不能直接重建 Table 1 的七数据、三密度、三路融合协议。公开 HF benchmark 只有六类 100-episode JSON，和 Table 1 的七数据协议不完全一致。
- Table 1 正文同时出现 eight 和 seven datasets，且外部 reward-model baseline 实际只有 GVL、VLAC-2B 两个。Table 3 的「over 10 simulation」应按实际 10 tasks 读取，但正文把来源写成 LIBERO 与 RoboTwin2.0，Appendix 只展开 LIBERO-Goal。论文结果应优先按可枚举表格核对。
- 主要 OOD 是 object、layout、background 的 shift，未测试完全未见 task、长时移动操作或大幅本体变化。camera-ready Future Work 也承认 continuous video、tactile、audio 尚未纳入。
- GRM 每个 transition 要运行三种 perspective，VLM 推理延迟和显存占用可能成为 online RL 瓶颈。论文给出训练资源和未来量化方向，却没有完整报告端到端 wall-clock 与能耗。Table 2 总共 180 条 rollout、Table 4 每个条件仅 20 次，均未给置信区间或显著性检验。

### 可继续追问的问题

- 如果把人工 keyframe 的 salience 改为真实接触事件、力觉或任务完成条件，VOC 和下游 success 是否仍保持提升？
- consistency-aware weighting 在真实 OOD rollout 中相对于简单平均到底减少了多少错误高奖励？应给出触发率、校准曲线和 reward-hacking 失败案例。
- one-shot trajectory 的质量、长度和视角缺失如何影响 GRM？camera-ready 只报告 suboptimal/noisy demo 的准确率下降小于 3%，缺少完整置信区间和任务分解。
- 能否用独立 verifier 产生真正的 `r_gold`，把 GRM 只用于 shaping，从而把 PBRS 保证与完成判定解耦？
- 在相同 policy backbone、相同示范数和相同算力下，Dopamine-RL 与 SARM、VLAC、RoboMeter、WARP-RM 的下游收益如何？
- 公开 release 的六类 benchmark 能否补齐 RoboBrain-X、RoboTwin2.0 和原论文的图像配对，形成可复核的 Table 1？

## 与当前库的连接

Robo-Dopamine 位于本库中「过程奖励 → 策略更新」的接口位置。它与 [[@yu2026warp-rm]] 都关心从视频中挑出更有信息量的片段，但 WARP-RM 重点是 chunk 级筛选，Robo-Dopamine 重点是状态对的相对进度和奖励塑形。它与 [[@wang2026wvm]] 的 video value 评测共享 VOC、GVL、VLAC 等语境，不过 WVM 更强调视频价值排序，本文进一步把排序信号接入真实 RL。

在策略侧，它连接 [[@luo2024precise-dexterous-robotic-manipulation]] 的 human-in-the-loop 真实机器人 RL、[[@intelligence2025pi06-vla-that-learns]] 的经验自改进和库内的 [[@qian2026wam-rl]]。区别在于 Robo-Dopamine 把「reward correctness」当作独立基础设施，并用 PBRS 处理 dense reward 的目标错位。与 [[@tan2026rl2-vla]] 的 inference-time steering 也形成互补，后者在推理时组合 VLA 与 RL latent 生成候选，本文则在训练时用 GRM 奖励塑造 policy。

它还给 [[@wu2026lingbot-vla2]]、[[@dyna2026dyna2]]、[[@zhou2026zero-wam]] 提出一个共同问题。若世界模型或人类视频接口提供了丰富的状态预测，谁来判断「更接近任务完成」而不是「视觉上更像示范」？GRM 的多视角和回退标签是一个可复用的 reward-side answer，但其线性进度假设和代理完成阈值仍需要其他模态验证。

## 结论

Robo-Dopamine 的系统贡献可以概括为一条明确的工程链。用大规模多源视频训练通用 GRM，用 hop normalization 和三路融合得到有界、抗漂移的进度，再把 progress potential 以折扣一致的 PBRS 形式接入 RL。Table 1–2 说明 GRM 在排序和完成判断上可靠，Table 3–5 说明这份信号在真实策略学习中有用。

最强的结果是多视角 GRM-8B 的 92.8% 完成判断和 Dopamine-RL 的 95.2% 真机成功率，最有解释力的结果是去掉 policy-invariant shaping 后降到 41.3%。但这些数字并不构成无条件的通用奖励保证。GRM 仍由专家时间索引监督，`r_gold` 仍由模型阈值产生，策略初始化仍需要示范与 HIL，公开代码也未覆盖完整 RL 管线。

## 精读路线 / 为什么需要回看

第一次回看可以只抓四个节点。先读 Eq. 2，确认 hop 的分母为何分别是「剩余距离」和「已完成距离」；再读 Eq. 3–8，检查三种 perspective 各自承担的误差类型；随后读 Appendix Proof 2 与 Eq. 13–17，验证为什么 direct difference 会改变 discounted objective；最后对照 Table 3 和 Table 5，把 reward accuracy、policy success、fusion 和 shaping 的因果层次分开。

第二次回看应聚焦复现条件。核对 raw 27.23M 到 augmented 35M 的转换，确认 GRM-3B/8B 的训练资源，分清一条 GRM adaptation demo 与 20–30 条 policy demos，再检查公开 benchmark 是否真的覆盖论文 Table 1。若要把方法迁移到新任务，优先记录 initial/goal 图像质量、失败恢复片段、真实终止标签和端到端 reward latency。

我的判断是，这篇工作最适合被当作「奖励基础设施」来引用，而不是一套已经解决真实机器人 RL 的万能 recipe。它把过程奖励的表示、感知和理论接口同时推进了一步，下一步仍需要独立完成检测器、更多 off-trajectory 负例和可复核的完整策略训练实现。

## 原文摘录

> The primary obstacle for applying reinforcement learning to real-world robotics is the design of effective reward functions.

> A key theoretical advantage is that, when global progress is reconstructed by iteratively applying predicted hops, the resulting progress is guaranteed to remain within the bounds [0, 1].

> This form guarantees policy invariance: the cumulative discounted shaping term forms a telescoping sum.

> The current VLM-based reward model, while accurate, incurs high computational latency which can bottleneck online RL training loops.

## 来源与版本核对

- arXiv 原题与版本  [2512.23703v1](https://arxiv.org/abs/2512.23703)，提交日期 2025-12-29。
- CVPR 正式版本  [General Process Reward Modeling for Robotic Reinforcement Learning](https://openaccess.thecvf.com/content/CVPR2026/html/Tan_General_Process_Reward_Modeling_for_Robotic_Reinforcement_Learning_CVPR_2026_paper.html)，页码 22412–22422。正式题名与 arXiv 标题不同，方法名仍为 Robo-Dopamine。
- 官方项目页  [Robo-Dopamine](https://robo-dopamine.github.io/)。
- 官方代码  [FlagOpen/Robo-Dopamine](https://github.com/FlagOpen/Robo-Dopamine)。
- 模型与 benchmark  [Hugging Face collection](https://huggingface.co/collections/tanhuajie2001/robo-dopamine)。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
