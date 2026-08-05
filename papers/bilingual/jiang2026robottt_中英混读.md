---
tags:
  - bilingual-reading
  - deep-reading
source_pdf: "[[papers/pdfs/jiang2026robottt.pdf]]"
paper: "[[@jiang2026robottt]]"
images: "papers/images/jiang2026robottt/"
image_index: "[[papers/images/jiang2026robottt/index.md]]"
created: 2026-08-05
generator: "setting/scripts/generate_reading_draft.py"
reading_mode: 生成式精读（逐节读原文 + 读图）
reading_standard: "fba534d bilingual full-reading"
extraction: "pypdf"
source_pages: 22
source_chars: 76309
---

# RoboTTT: Context Scaling for Robot Policies

paper:: [[@jiang2026robottt]]
pdf:: [[papers/pdfs/jiang2026robottt.pdf]]
images:: [[papers/images/jiang2026robottt/index.md]]
reading:: [[papers/bilingual/jiang2026robottt_中英混读.md]]

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| Test-Time Training（TTT） | 测试时训练 | 训练与推理**都**对一小部分参数做梯度更新，把上下文压进参数空间；本文的序列建模机制。 |
| fast weights / slow weights | 快权重 / 慢权重 | fast weights 是推理时仍在更新的循环状态；slow weights 是常规模型参数，推理时冻结。 |
| visuomotor context | 视觉-运动上下文 | 策略能看到的历史观测与动作长度；本文把它从 1 步拉到 8K 步。 |
| context scaling | 上下文扩展 | 本文主张的新 scaling 轴：预训练上下文越长，真机闭环表现越好。 |
| Vision-Language-Action（VLA） | 视觉-语言-动作模型 | 本文的宿主模型形态，实例化在 GR00T N1.7 上。 |
| Diffusion Transformer（DiT） | 扩散 Transformer | GR00T N1.7 的动作头；TTT 层就插在它每层的 attention 之后。 |
| register token | 寄存器 token | 每个时间步前置的 $N{=}16$ 个可学 token，替 VL token 把视觉语言信息带过时间。 |
| sequence action forcing | 序列动作强制 | 序列训练时每个 action chunk 独立采噪声等级，避免整条序列同易或同难。 |
| truncated backpropagation through time（TBPTT） | 截断时间反向传播 | 分段回传梯度但 fast weights 跨段延续，使显存与总上下文长度解耦。 |
| DAgger Distillation | DAgger 蒸馏 | 用失败动作作**上下文**、人类纠正作**目标**，把"失败→纠正"映射蒸馏进 fast weights。 |
| Algorithm Distillation | 算法蒸馏 | 把"改进过程"而非"最终策略"写进模型的做法；本文视 DAgger Distillation 为其机器人版本。 |
| Gated DeltaNet（GDN） | 门控 Delta 网络 | 关键对照组：同为定长循环状态，但用线性 delta rule 而非测试时梯度下降。 |
| flow matching | 流匹配 | 动作头的生成目标，本文把它按时间步展开成序列损失。 |
| task completion score | 任务完成分 | 依 rubric 打分并归一化到 $[0,1]$ 的主指标，比二值成功率更细粒度。 |

## 摘要

Recent robot foundation models operate with single-step or short-history visuomotor context. We introduce Test-Time-Training Robot Policies (RoboTTT), a robot model and training recipe that scale visuomotor context to 8K timesteps, three orders of magnitude beyond state-of-the-art policies, without growing inference latency. At this context length, we unlock new robot capabilities: one-shot in-context imitation from human video demonstrations, on-the-fly policy improvement, robustness to perturbations, and stronger performance on multi-stage, long-horizon tasks. We also observe, for the first time, steady gains in closed-loop performance as pretraining context length scales. At its core, RoboTTT integrates Test-Time Training into robot foundation models such as Vision-Language-Action policies, yielding a sequence model whose recurrent state consists of fast weights, parameters updated by gradient descent during both training and inference, compressing histories into weight space and retrieving contextual information for long-context conditioning. To scale training context length, the recipe combines sequence action forcing with truncated backpropagation through time. On challenging real-robot manipulation tasks, RoboTTT improves overall performance by 87% over the single-step context baseline and fully completes a five-minute, ten-stage assembly task, which no baseline ever does. RoboTTT trained with 8K-timestep context outperforms the same model pretrained with 1K timesteps by 62%, suggesting context length as a new scaling axis for robot foundation models.

**中文解读。** 作者的写作动作是"构造 + 测量"：先构造一个把 Test-Time Training（测试时训练）塞进 VLA 的模型与训练配方，再测量一条以前没人给出的曲线——**预训练上下文长度 vs 真机闭环表现**。摘要里三类数字要分开读：(1) 与短上下文基线的横向比较（+87%）；(2) 与自身不同上下文长度的纵向比较（8K vs 1K，+62%/63%）；(3) 能力性的定性结论（十阶段五分钟任务只有它能完整做完、一次性 in-context 模仿）。第三类才是"长上下文解锁新能力"的真正证据，前两类只是性能数字。

> [!warning] 数字口径
> 摘要写"outperforms the same model pretrained with 1K timesteps by **62%**"，而 Introduction 与 Sec. 4 都写 **63%**（71.5% vs 43.9%，比值 1.629）。引用时以正文为准。

## 论文主线

![[papers/images/jiang2026robottt/pull2_page1.png|760]]

**Figure 1（teaser）读法。** 这张图不是效果展示，而是全文的论点结构图：左上"Long-Context Conditioning"是机制，其余三块（One-Shot Imitation from In-Context Human Demonstration、On-the-Fly Improvement、Robustness to External Perturbation）是这个机制解锁的三种能力，右侧"Better Long-Horizon Task Performance (Duration = 5 Minutes)"是它带来的常规性能收益。读全文时可以一直拿它当索引：Sec. 3.3 造出前两种能力，Sec. 4 逐一验证四块。

一条线串起来：

1. **问题入口**：主流机器人基础模型只看当前观测或 2–8 帧历史，而语言模型早已把上下文长度当作核心 scaling 轴。长视觉-运动上下文对三类能力是必需的——从人类视频做 in-context 模仿、从自己的部署历史做 on-the-fly 改进、在多阶段长程任务里保持闭环稳定。于是问题是：**怎样构造能从任意长上下文中学习并利用它的 visuomotor policy？**
2. **三个技术约束**：长上下文策略同时面临三道坎——(a) 要有足够容量编码长历史；(b) 要真的**用得上**被条件化的上下文（不只是"看得到"）；(c) 推理成本不能随上下文增长。Transformer + KV cache 破 (c)，RNN 的向量状态破 (a)。
3. **方法钩子**：fast weights 同时解三道坎。fast model 是 MLP（容量 > 向量状态）；测试时用梯度下降更新（保留显著特征、抹掉冗余，因此"用得上"）；状态定长（推理成本恒定）。再加两个训练技巧把训练上下文推到 8K：sequence action forcing 与 TBPTT。
4. **能力钩子**：因为 fast weights 在部署期仍在学，"上下文"可以是异质的——人类视频、机器人自己的失败片段。用**屏蔽损失**这一个开关就能把某些时间步变成"只更新 fast weights、不作模仿目标"的纯上下文，由此得到 one-shot imitation 与 DAgger Distillation。
5. **证据出口**：三个真机长程装配任务上的完成分与完全成功次数、128→8K 的上下文 scaling 曲线、一次性模仿、扰动恢复、DAgger 对照、五组消融。

全程要盯的一个问题：作者反复强调 **RoboTTT vs GDN** 的对照。两者都是定长状态的序列模型，唯一差别是"状态怎么更新"。如果 GDN 也能随上下文变好，那本文的故事就退化成"有记忆就行"；实际 GDN 在上下文 scaling 曲线上是平的，这才把功劳落到"测试时梯度下降"这个特定 update rule 上。

## 贡献与结论对照

| 贡献 / 结论 | 方法位置 | 证据 / 结论 |
| --- | --- | --- |
| 把 TTT 作为时间维度的序列建模机制接入 VLA，且不破坏预训练能力 | Sec. 3.1（TTT 层置于 attention 之后 + $\tanh$ gating，Eq. 3） | 消融显示 register token 只有配合 TTT 才有增益（+18%），单独加到 GR00T N1.7 上无效 |
| 给出可把训练上下文推到 8K 的配方 | Sec. 3.2（sequence action forcing，Eq. 5；TBPTT，Fig. 4） | 去掉 sequence action forcing 后动作失准、几乎无法推进任务；TBPTT 使显存只随段长增长 |
| 用"屏蔽损失"把长上下文变成能力载体 | Sec. 3.3（in-context video、DAgger Distillation，Fig. 6） | 一次性模仿 6/10（GDN 0/10）；DAgger Distillation 平均 +33%，标准 DAgger 仅 +9% |
| 首次给出上下文长度的闭环 scaling 曲线 | Sec. 4（Fig. 8，128→8K） | 8K 达 71.5%，比 1K（43.9%）高 63%、比最好短上下文基线（45.6%）高 57%，未见饱和；GDN 无此趋势 |
| 长程多阶段任务的实际收益 | Sec. 4（Fig. 7、Table 1） | 平均完成分 79% vs 42%（+87%）；Gear Bot 十阶段五分钟任务 2/10 完全成功，基线全 0 |
| 暴露适用边界 | Sec. 6 + Sec. 4 的低上下文段 | 训练成本随上下文上升；<1K 时不如短上下文基线；不解决所有失败模式，下一步应接 RL |

## 结构地图

| 原文位置 | 作者在这一部分做什么 | 与全文主线的关系 | 关键图表 / 公式 |
| --- | --- | --- | --- |
| Abstract | 给出机制、配方、四种能力和两组核心数字 | 定调：上下文长度是新 scaling 轴 | — |
| 1. Introduction | 定义缺口（单步/短历史）、列出三道技术坎、预告全部结论 | 回答为什么要做 | Fig. 1 |
| 2. Preliminaries | 形式化 TTT 的 update/apply，以及 robot sequence model 的记号 | 提供读方法节所需的符号系统 | Eq. 1、Eq. 2 |
| 3. Method（引言段） | 交代方法三块：架构、训练配方、上下文利用 | 方法总览 | — |
| 3.1 Model Architecture | TTT 层的插入位置、token 布局、$\tanh$ gating | 回答"怎么把序列建模塞进 VLA" | Fig. 2、Fig. 3、Eq. 3 |
| 3.2 RoboTTT Sequence Training | 序列损失、sequence action forcing、TBPTT、推理流程 | 回答"训练上下文怎么做长" | Eq. 4、Eq. 5、Fig. 4 |
| 3.3 Effective Learning from Context | 屏蔽损失 → in-context 视频模仿、DAgger Distillation | 回答"长上下文能换来什么新能力" | Fig. 6 |
| 3.4 Implementation Details | 骨干、层数、参数量、算力、预训练/后训练步数 | 复现所需的最小信息 | — |
| 4. Experiments | 任务与基线设定，五组实验：主结果、上下文 scaling、一次性模仿与扰动、DAgger、消融 | 回答是否有效 | Fig. 5、7、8、9、10、11、12；Table 1、2、3 |
| 5. Related Work | 长上下文策略、TTT、机器人基础模型三条线 | 定位本文与既有工作的差别 | — |
| 6. Limitations and Conclusion | 三条局限 + 收束 | 回答边界与意义 | — |
| Appendix A | 架构、训练、部署细节；预训练数据长度分布 | 复现细节 | Fig. A.1 |
| Appendix B | 三个任务的完整 rubric 与评测协议 | 决定主指标可不可信 | Fig. A.2、A.3、A.4 |

## 按原文 section 精读

### 1. Abstract

**本节在全文中的位置。** 摘要同时承担"定义缺口"和"给结论"两件事，其措辞很讲究：说 context 扩到 8K 是 "three orders of magnitude beyond state-of-the-art"，同时强调 "without growing inference latency"——这一句提前回答了读者最可能的质疑（长上下文是不是拿延迟换的）。

**原文讲解。** 摘要给出的因果链是：TTT → fast weights 作为循环状态 → 把历史压进 weight space 并在需要时取回 → 长上下文条件化。训练侧的两件事（sequence action forcing、TBPTT）被明确定位为"为了把训练上下文做长"，而不是性能技巧。最后 "suggesting context length as a new scaling axis" 是全文最强的一句主张，它需要 Fig. 8 那条曲线支撑，而不是 Fig. 7 的横向比较。

**回看重点。** 摘要里的 87% 与 62%/63% 是两类不同的比较（跨方法 vs 跨自身上下文长度）；引用时不要混用。另外"新能力"这个说法要落到 Sec. 4 的一次性模仿与 DAgger 两组实验上，其余更像是性能提升。

### 2. 1. Introduction

**本节在全文中的位置。** Introduction 把"缺口 → 三道技术坎 → 解法 → 结论清单"一次性铺完，是全文压缩度最高的一节。

**原文讲解。** 作者先指出现状：state-of-the-art 机器人基础模型（π0、GR00T N1、OpenVLA、RDT-1B、Octo 等）用单步或短历史；而 LLM 那边 context length 早已是关键 scaling 轴。他们承认另一条路线的存在——把长程记忆外包给 external memory bank（关键帧、语言摘要、检索），但主张 long visuomotor context 本身仍不可替代，理由是三种能力：one-shot in-context imitation、on-the-fly improvement、multi-stage 长程任务的闭环表现。于是提出问题：`how can we build visuomotor policies that learn from and exploit arbitrarily long contexts?`

接着直接把结论摊开：一次性模仿 6/10（基线全败）、on-the-fly 改进比未针对训练的同模型好 36%、扰动下 83% vs 最好短上下文基线 53%、长程任务总体 +87%、Gear Bot 五分钟十阶段完整完成、8K vs 1K +63%、比最好短上下文基线 +57%。

最关键的是这一段对**三道坎**的拆解，它解释了为什么是 fast weights 而不是别的：

- **容量**：fast model（如 MLP）比 RNN 的向量状态容量大；
- **利用**：在部署期训练 fast model，等于在稠密、重复的机器人观测流里保留显著特征、丢弃冗余——这直接回应 "exploiting the conditioned context" 这条常被忽略的难点（作者引 RoboMME 的记忆基准）；
- **成本**：fast weights 沿时间传播，推理成本恒定，而 Transformer 即使有 KV cache 也随历史增长。

**关键证据 / 图表 / 公式。** Fig. 1 是唯一的图；它把四种能力与"长上下文条件化"这个机制并列，明确了本文的叙事：机制在中间，能力在四周。

**回看重点。** 注意作者说 RoboTTT 也可被看作"循环状态是 fast weights 的 RNN"。这个自我定位很重要：它意味着与 GDN 的对照是同类比较（都是常数成本的循环模型），差别只在 update rule 的表达力，因此 Fig. 8 的分叉才有解释力。

### 3. 2. Preliminaries

**本节在全文中的位置。** 这一节只做两件事：给 TTT 的形式化定义、给 robot sequence model 的记号，为 Sec. 3 的公式做准备。

**原文讲解（TTT 机制）。** 给定 $d$ 维 token 序列 $X$ 及其由投影矩阵 $\theta_Q,\theta_K,\theta_V$ 得到的 $Q,K,V$，fast weights $W$ 参数化一个小网络 $f_W(\cdot):\mathbb{R}^d\to\mathbb{R}^d$（线性层或 MLP）。**update 步**：

$$W_t \leftarrow W_{t-1}-\eta\nabla_W \mathcal{L}_{\text{FW}}\big(f_{W_{t-1}}(K_t),\,V_t\big) \tag{1}$$

其中 $\mathcal{L}_{\text{FW}}(\hat v,v)=\lVert \hat v-v\rVert^2$ 一般取均方误差，$\eta$ 是可学习的（内层）学习率。**apply 步**：

$$O_t=f_{W_t}(Q_t) \tag{2}$$

变量含义要抓住：$K_t\to V_t$ 是"要记住的关联"，一次梯度下降就是"写入"；$Q_t$ 是"要查询什么"，前向一次就是"读出"。直观理解：update 把上下文写进 $f_W$ 的**参数空间**，apply 再取回来给下游预测。这个 "update then apply" 在训练与推理时都执行——这正是 TTT 与普通 attention 的分界：attention 把所有历史 key/value 留在显存里逐步 attend，TTT 把它们压缩进一组权重。

还有一句容易被略过但很关键：$\theta_Q,\theta_K,\theta_V$ 和 $W_0$ 都由**外层任务损失**学到，也就是"记忆机制本身是为任务优化的"。

**原文讲解（robot sequence model）。** 轨迹 $\xi=\{(o_t,q_t,A_t)\}_{t=1}^T$ 由图像、本体感受、动作 chunk 三元组构成（此处省略语言模态），策略写作 $\pi(A_t\mid \xi_{<t},o_t,q_t)$，长上下文策略的目标就是把 $|\xi_{<t}|$ 做大。

**回看重点。** Eq. 1 的 $\mathcal{L}_{\text{FW}}$ 是**通用的**关联记忆目标，不含任何机器人先验——这正是 Sec. 6 承认的局限之一（未来可探索面向机器人的 TTT 目标）。

### 4. 3. Method: Test-Time-Training Robot Policies（总览）

**本节在全文中的位置。** 方法节的引言段落把后面四个小节的分工讲清楚：3.1 架构（怎么接进 VLA）、3.2 训练配方（怎么把训练上下文做长）、3.3 上下文利用（怎么把长上下文变成能力）、3.4 实现细节。

**原文讲解。** 值得注意作者对 DAgger Distillation 的定性：它是一种 **meta-learning method**，教策略"如何在部署中改进"，方式是把 DAgger 式的"次优动作→人类纠正"过程蒸馏进 fast weights。也就是说，这里学的不是某个纠正动作，而是**纠正这一行为模式**。

**回看重点。** 三小节之间是有依赖的：没有 3.2 的 TBPTT 就没法在 8K 上训练，没有 3.1 的 gating 就会破坏预训练模型，没有 3.3 的屏蔽损失就没有异质上下文。读的时候不要把它们当成并列的技巧堆叠。

### 5. 3.1. Model Architecture

![[papers/images/jiang2026robottt/model_arch-fig_page1.png|760]]

**Figure 2 读法。** 图分左右两半：左边 "RoboTTT Sequence Training"，右边 "RoboTTT Inference"。三个信息量最大的细节是——(1) 每个时间步内部先做 Self+Cross Attn，然后 **Flatten over time**，再进 TTT Layer，这就是"attention 管步内、TTT 管跨步"的可视化；(2) 训练时 TTT 层以 mini-batch 方式推进（$W_0\to W_1\to\dots\to W_{T/H}$），推理时每次推理只做一个 mini-batch 并把 fast weights 向前传播；(3) 训练图上标着"+ Different Levels of Noise"，正是 sequence action forcing；推理图上 VLM Encoder / State Encoder / attention 都带雪花（冻结）标记。

**原文讲解。** RoboTTT 实例化在 GR00T N1.7 上：VLM 骨干 + DiT 动作头，DiT 每层的 self-/cross-attention 之后加一层 TTT。时间步 $t$ 的输入 token 是

$$[R_1,\Phi_1,q_1,\tilde A_1,\;\dots,\;R_T,\Phi_T,q_T,\tilde A_T]$$

其中 $\Phi_t$ 是 VLM 输出的 vision-language token，$q_t$ 是编码后的本体感受 token，$\tilde A_t$ 是加噪的动作 token，$R_t$ 是每步前置的 $N=16$ 个 learned register tokens（引 Vision Transformers Need Registers 与 Perceiver），它们会 attend 到该步的所有其他 token。

关键的工程取舍：attention 只作用在步内 token $R_t,q_t,\tilde A_t$ 上并 cross-attend 到该步的 $\Phi_t$；随后把各步的 attention 输出沿时间维拼成 $X=[R_1,q_1,\tilde A_1,\dots,R_T,q_T,\tilde A_T]$ 再过 TTT 层。**$\Phi$ 不进 TTT**，因为 VL token 数量大、算力吃不消；跨时间的视觉语言信息改由数量小得多的 register token 承载。这是一个明确的信息瓶颈设计，也解释了为什么消融里 register token 与 TTT 是绑定生效的。

**gating（保住预训练能力）。**

![[papers/images/jiang2026robottt/gating-fig_page1.png|560]]

RoboTTT 从基座权重初始化，并对每个 DiT 层学一个 $\alpha\in\mathbb{R}^d$（初始化为 0.001），按

$$O=\tanh(\alpha)\odot O_{\text{TTT}}+O_{\text{attn}} \tag{3}$$

把 TTT 输出与 attention 输出相加。$\tanh(0.001)\approx 0.001$，所以训练初期 TTT 分支几乎不影响原模型的前向；随着训练推进模型自己调大 $\alpha$。这是 Flamingo 式 gating 的直接借用，目的只有一个：**别让新模块在早期毁掉预训练 VLA**。

**回看重点。** 三个可追问处：(1) register token 数 $N=16$ 是否成为长上下文的信息瓶颈（论文未做 $N$ 的消融）；(2) $\alpha$ 训练完的量级论文没报，无法判断 TTT 分支最终占多大权重；(3) TTT 层加在"每一层 attention 之后"是唯一选择吗（未做层选择消融）。

### 6. 3.2. RoboTTT Sequence Training

**本节在全文中的位置。** 这是把"能跑"变成"能在 8K 上训"的一节，也是全文最像"配方"的部分。

**原文讲解（序列损失）。** 数据集 $\mathcal{D}=\{\xi^{(i)}\}_{i=1}^N$，每条轨迹 $\xi=\{(l,o_t,q_t,A_t)\}_{t=1}^T$（这里把整条共享的语言指令 $l$ 加回来）。训练序列是完整轨迹或不超过最大上下文长度的连续子轨迹。给定 fast weight 初值 $W_0$，序列损失是逐步 flow-matching 损失 $\ell_t$ 的平均：

$$\mathcal{L}_{\text{fm}}(\xi;W_0)=\frac{1}{T}\sum_{t=1}^{T}\ell_t\big((l,o_t,q_t,A_t);W_{t-1}\big) \tag{4}$$

其中 $W_{t-1}$ 是进入第 $t$ 步时的 fast weight 状态，在 TTT 层内按 Eq. 1 更新为 $W_t$。**内层跑 TTT、外层在每个时间步算任务损失、对平均损失做一次优化**——因此投影矩阵直接从外层任务梯度学到，$W_0$ 则通过"梯度的梯度"被 meta-learn（作者引 MAML 与 end-to-end TTT）。

**原文讲解（sequence action forcing）。** 动作头用 flow matching：$\tilde A_t=A_t^{\tau}=\tau A_t+(1-\tau)\epsilon$，$\tau\in[0,1]$，$\epsilon\sim\mathcal{N}(0,I)$。作者发现序列训练时必须**为每个 action chunk 独立采噪声等级**：

$$\mathcal{L}_{\text{fm}}(\xi;W_0)=\frac{1}{T}\sum_{t=1}^{T}\mathbb{E}_{\tau_t,\epsilon}\Big[\big\lVert v_\theta(\Phi_t,A_t^{\tau_t},q_t;W_{t-1})-(A_t-\epsilon)\big\rVert^2\Big] \tag{5}$$

$\tau_t=s(1-u)$，$u\sim\mathrm{Beta}(1.5,1)$，$s=0.999$。直觉是：若整条序列共用一个噪声等级（full-sequence diffusion），那么整段要么都很容易、要么都很难，训练不稳定——这与 Diffusion Forcing 的发现一致。这个命名也很贴切：**action forcing 之于动作序列，正如 teacher forcing/diffusion forcing 之于 token 序列**。

**原文讲解（TBPTT）。**

![[papers/images/jiang2026robottt/tbptt-fig_page1.png|700]]

**Figure 4 读法**：输入序列被切成 TBPTT segment，梯度只在段内流动（段边界 Detach），但 fast weights 跨段 **Carry**。因此 TTT 在整条序列上是连续的，显存却只由段长决定，训练上下文可以在固定显存预算下任意加长。作者补了一句易漏的细节：$W_0$ 仍能通过**第一段**收到梯度，因为第一段的更新直接源自 $W_0$。

**推理。** 每次 rollout 从学到的 $W_0$ 起步，在当前观测上更新 fast weights 并向下一时刻传播；每步动作 chunk 用 $k$ 步去噪生成。

**回看重点。** (1) 段长是显存与梯度质量的权衡，论文未报段长具体值及其消融；(2) 训练时是"整条序列一次前向"，推理时是"每步一个 mini-batch"，两者的 TTT 更新粒度并不完全一致，这类 train/inference gap 值得在复现时确认；(3) Eq. 4/5 里 $W$ 的下标依赖使损失**不可并行化到时间维**，这正是训练成本随上下文上升的根因（对应 Sec. 6 的第一条局限）。

### 7. 3.3. Effective Learning from Context

**本节在全文中的位置。** 全文最有迁移价值的一节：一个"屏蔽 flow-matching 损失"的小开关，把 fast weight 更新与模仿目标**解耦**，于是上下文可以是异质的。

**原文讲解（in-context 视频模仿）。** 把人类视频序列 $\xi_{\text{video}}$ 与同任务的机器人轨迹 $\xi_{\text{robot}}$ 配对拼成一条训练序列：视频段**只更新 fast weights**（其 flow-matching 损失被屏蔽），动作损失只在机器人轨迹段上算，且以更新后的 fast weights 为条件。这样训练出的模型学会"从 in-context 视频里抽取任务信息"；测试时给一条未见配置的人类视频，就得到 one-shot imitation。

**原文讲解（DAgger Distillation）。**

![[papers/images/jiang2026robottt/dagger_distillation-fig_page1.png|700]]

**Figure 6 读法**：时间轴上交替出现两种片段——`robot actions (fast weight update only)` 与 `human corrections (fast weight update + flow-matching loss)`。一张图就说清了这套**非对称**用法。

考虑一条按 DAgger 采集的 rollout：机器人出错时人类接管纠正，得到 $\xi_{\text{DAgger}}=\{(l,o_t,q_t,A_t)\}_{t=1}^T$，其中每个执行过的动作 chunk 要么是机器人动作 $A_t^{\mathrm{R}}$，要么是人类纠正 $A_t^{\mathrm{H}}$。**标准 DAgger** 在人类纠正上微调、丢掉次优机器人动作；但作者指出，恰恰是这些动作揭示了"每个纠正在回应什么失败"。于是 RoboTTT 两者都用、但角色不同：fast weights 在**完整交互历史**上更新（包括次优机器人动作），flow-matching 损失只屏蔽性地作用在**人类纠正**上。

这句话是本节的论点核心：*failures as context and corrections as targets*——模型学到的是"针对失败产生纠正"，而不是"孤立地模仿纠正"。作者把它定位为 Algorithm Distillation 在机器人领域的实例：被蒸馏的是**由人类干预诱导出的改进过程**，而不是某个改进后的策略。测试时模型自己产生纠正，这些纠正又进入历史、被吸收进 fast weights，与训练时人类纠正扮演的角色完全一致。

**回看重点。** (1) 这套做法要求 fast weights 在部署期真的会更新——它天然只适用于序列模型（论文里 GDN 也能用、也有 +29% 提升，说明这是一类方法而非某个模型的专利）；(2) 屏蔽损失是"硬开关"，是否可以做成软加权（比如按 advantage 加权）是明显的扩展方向；(3) 人类视频与机器人轨迹必须是**同配置**配对采集，数据成本不低（Circuit 每个训练配置 5–20 条视频）。

### 8. 3.4. Implementation Details

**本节在全文中的位置。** 短，但决定复现可行性。

**原文讲解。** 骨干 GR00T N1.7，16 个 DiT 层各加一个 TTT 层，fast model 是两层 MLP。预训练数据是 tabletop 双臂机器人数据 + egocentric 人类数据（EgoScale）的混合，**逐步把预训练上下文长度提升到目标值**（如 RoboTTT-8K 的 8K），30K steps、16 张 NVIDIA GB200；随后在每个下游任务上以 1K 上下文 post-train 20K steps。

Appendix A 的补充值得一并记住：原 DiT 538M 参数，每个 TTT 层约 +10M，合计约 690M；fast model 用 GeLU；沿用 TTT 惯例学习内层学习率（base 0.1）；位置编码用 RoPE（$\theta_{\text{rope}}=10000$）；预训练**只训新增的序列建模层**（TTT 或 GDN）、冻结 GR00T 其他部分，post-train 才全参数微调；优化器 AdamW（weight decay $1\times10^{-5}$），预训练用 WSD 调度（峰值 lr $2\times10^{-5}$），后训练用 cosine（峰值 lr $5\times10^{-5}$）；上下文 ≤4K 时 per-device batch 4（全局 64），更长时为 1（全局 16）。

**回看重点。** "预训练只训新层"是一个很重的设定：它保证了公平（RoboTTT 与 GDN 的对照严格同条件），但也意味着 VLM/attention 的表示从未针对长上下文调整过——这可能低估了 TTT 的潜力，也可能是 8K 未饱和的原因之一。

### 9. 4. Experiments

![[papers/images/jiang2026robottt/tasks-fig_page1.png|760]]

**Figure 5 读法。** 三行分别是 Pup Go Car（2 分钟）、Circuit（1 分钟）、Gear Bot（5 分钟）。它们不是难度递增的同类任务，而是三种不同压力：Pup Go Car 压"多阶段 + 精细工具使用（拧螺丝、电钻交接、翻转车身）"，Circuit 压"配置泛化（80 种配置，训练 20 测试 60）"，Gear Bot 压"极长时程（十阶段）"。

**实验设定。** YAM 双臂平台 + 四路 RGB 相机（top、bottom、左右腕）。三任务分别采集 8、6、5 小时真机数据，平均 episode 长度 2、1、5 分钟。Circuit 的目标配置由语言 prompt（或一条人类视频）指定。基线三个：**GR00T N1.7**（单步上下文）、**GR00T N1.7 Hist.**（加一帧历史）、**GDN**（把 TTT 层换成 Gated DeltaNet 层，线性复杂度、无测试时梯度下降）。所有方法在同任务数据上后训练：序列模型用 1K 上下文，非序列模型按等算力预算训练。每策略 20 次试验（Gear Bot 因时程长为 10 次）。指标是完全成功次数 + rubric 归一化完成分。

**主结果。**

![[papers/images/jiang2026robottt/main_exp_results-fig_page1.png|700]]

平均完成分 **79%**，比 GR00T N1.7（42%）高 87%，比最强基线 GDN（56%）高 41%。完全成功次数（Table 1）：

| Method | Pup Go Car | Circuit | Gear Bot |
| --- | ---: | ---: | ---: |
| **RoboTTT** | **9 / 20** | **13 / 20** | **2 / 10** |
| GR00T N1.7 | 3 / 20 | 3 / 20 | 0 / 10 |
| GR00T N1.7 Hist. | 0 / 20 | 8 / 20 | 0 / 10 |
| GDN | 3 / 20 | 8 / 20 | 0 / 10 |

作者给了三条定性解释，都值得记：(1) **追踪任务进度**——多阶段装配里视觉相似的阶段会造成 state aliasing，基线因此做错动作或跳过阶段，而不断更新的 fast weights 保留了历史中的显著特征、把当前阶段区分开；(2) **策略性恢复**——Pup Go Car 拧屋顶螺丝时若电钻没对准，RoboTTT 会抬臂、重新对齐、再试，基线则当作已经成功继续下一阶段；(3) **精细阶段更准**——长上下文缓解了部分可观测性，被遮挡物体的历史观测仍能指导当前动作。最后一句是全文的方法论主张：相关观测窗口难以事先指定，**足够表达力的序列模型可以把"用多长的历史"学出来，而不是手工设计**。

**"光靠拼历史行不行？"** 不行且可能有害：Pup Go Car 上 GR00T N1.7 Hist.（39.5%）反而低于无历史的 GR00T N1.7（57%）——拼接历史会引入 spurious correlation，并让机器人在推理时处于"时间上的分布外"。GDN 在 Circuit 和 Gear Bot 上优于 GR00T N1.7，但 Pup Go Car 上没有。作者的假设是：gated delta rule 这种"无测试时梯度下降的线性关联更新"难以从上千步稠密重复的机器人流里抽出结构，而 RoboTTT 的非线性 fast model + 梯度下降是更强的压缩器。

**上下文 scaling。**

![[papers/images/jiang2026robottt/ctx_scaling_results_page1.png|700]]

**Figure 8 读法**：横轴是预训练上下文长度（128→8K），纵轴是三任务平均完成分；两条水平参考线是 Single-Step Context（GR00T N1.7）与 Short Context（GR00T N1.7 Hist.）。RoboTTT 稳步上升，从 1K 起超过最好的短上下文基线，8K 时 71.5%，比自身 1K 版本（43.9%）高 63%、比 45.6% 的短上下文基线高 57%，**未见饱和**；GDN 全程平坦。作者的解释落在 meta-learning 上：更长的训练序列意味着更多次 fast weight 更新参与外层优化，因此 $W_0$ 与更新动态被塑造得更好；GDN 的线性关联状态没有这种可 meta-learn 的结构。

低于 1K 时 RoboTTT 反而不如短上下文基线（但仍胜过同长度的 GDN），原因是 rollout 时长超过训练上下文：1K 约半分钟，短于最短任务的 episode，于是推理时 fast weights 被更新到训练从未见过的步数、位置编码也外推到未见位置。**这条边界很重要**：它说明长上下文不是免费的，训练上下文必须覆盖任务时程。

> [!note] 口径提示
> Fig. 8 的评测"predate the DAgger training used for Pup Go Car in the main results"，即这条曲线与 Fig. 7 的主结果不是同一批模型，不能直接横向拼读。

**一次性 in-context 模仿。**

![[papers/images/jiang2026robottt/circuit_one_shot_rollout_2_page1.png|760]]

**Figure 9 读法**：连续录制的画面——人类先演示一个未见配置（帧 1–3），场景重置（帧 4），然后 RoboTTT 复现该装配（第二行）。因为所有配置共用同一句 prompt "assemble circuit"，**目标只能从视频里识别**，这就排除了"靠语言提示作弊"的可能。

数据构造：为训练集里每个配置采 5–20 条人类视频（机器人静止、人手装配，初始布局各异）；训练时采样同配置的一条视频与一条机器人轨迹拼成序列，视频段屏蔽损失。基线只能是 GDN——GR00T N1.7 无法条件化上下文，而人类视频远超 GR00T N1.7 Hist. 的历史窗口。

| Method | Task Completion Score | Successful Rollouts |
| --- | ---: | ---: |
| **RoboTTT** | **65%** | **6 / 10** |
| GDN | 33% | 0 / 10 |

GDN 的失败模式很说明问题：拿错元件、装错顺序——**能编码上下文，但用不上**。这正好回应 Introduction 里的第二道坎。

**扰动鲁棒性。** 在 Pup Go Car 上，人类在机器人装好黄色车顶后把它拆走，或在装好轮胎后拔掉；会条件化自身 rollout 的策略应当回到扰动前的阶段并重装。作者共训了 30 分钟扰动数据。

| Method | Roof Perturbation | Tire Perturbation |
| --- | ---: | ---: |
| **RoboTTT** | **15 / 20** | **18 / 20** |
| GR00T N1.7 | 10 / 20 | 11 / 20 |
| GR00T N1.7 Hist. | 3 / 20 | 5 / 20 |
| GDN | 13 / 20 | **18 / 20** |

读法：所有方法都有一定鲁棒性（很可能来自共训数据），但长上下文方法明显更常成功；轮胎条件下 GDN 与 RoboTTT 打平。这说明**扰动恢复主要依赖"能看到自己刚才做过什么"，对 update rule 的表达力要求没有一次性模仿那么高**。这也是全文中 GDN 唯一追平的实验，值得记住。

**DAgger Distillation。**

![[papers/images/jiang2026robottt/dagger_distillation_results-fig_page1.png|700]]

**Figure 10 读法**：四组方法 × 四种条件（Before DAgger / DAgger (Human Actions Only) / DAgger (Full Trajectory) / DAgger Distillation），其中 DAgger Distillation 只适用于两个序列模型。数据池是 100 条 DAgger 轨迹（RoboTTT 采 50、GR00T N1.7 采 50），所有方法用同一池子训练。

结论链：标准 DAgger（只用人类纠正微调）四方法平均 +9%，两个序列模型上 +13%；DAgger Distillation 平均 **+33%**（RoboTTT +36%、GDN +29%）。最关键的对照是：把完整轨迹（含次优机器人动作）拿去**微调** GR00T N1.7，结果与只用纠正段完全一样（都是 57%）——**次优动作作为模仿目标毫无价值，它们的价值只在作为上下文**。这句对照把"数据变多"与"数据换角色"这两种解释干净地区分开了。

![[papers/images/jiang2026robottt/dagger_distillation_rollout_2_page1.png|760]]

**Figure 11 读法**：Pup Go Car 拧车顶螺丝的连续片段——错过螺丝（帧 1–3），抬臂重试、更近但仍未中（帧 4–5），再次调整后成功（帧 6–8），下方是电钻进度条。它把 Fig. 10 的数字变成可见机制：DAgger Distillation 的增益主要来自**做错之后的恢复**，也就是失败→纠正映射在 rollout 中以 on-the-fly 改进的形式显现。

**消融。**

![[papers/images/jiang2026robottt/ablation-fig_page1.png|700]]

**Figure 12 读法**：左半是两个变体消融，右半是开发路线图式的逐步加法。要点：

- 去掉 **sequence action forcing**：闭环性能显著下降，动作不准到无法推进任务——说明序列训练里"逐 chunk 独立噪声"不是可选项。
- **TTT Linear**（fast model 换成线性层）：优于 GR00T N1.7 基线，但比 MLP 差 **27%**——表达力更强的非线性 fast model 才是关键，与语言/视觉领域的 TTT 结论一致。
- 路线图：State Tokens → + Action Tokens（**+23%**，模型知道自己过去做了什么，更能捕捉环境动力学）→ + Register Tokens（**+18%**，即完整 RoboTTT）。
- 对照项：给 GR00T N1.7 加同样数量的 register token **没有收益**——所以 register token 的作用不是"多点容量"，而是"配合 TTT 的时间建模把上下文编码起来"。这个匹配设计（matched-token comparison）做得很干净。

**回看重点。** (1) 每个条件 10–20 trials，成功率差异的置信区间不小，Table 3 中 15/20 vs 13/20 这类差距应视为"相当"；(2) Fig. 8 与 Fig. 7 的模型批次不同；(3) 所有结论都来自单一平台与三个任务，任务间的收益差异（Pup Go Car 上 GDN 甚至不如无历史基线）提示收益依赖任务结构。

### 10. 5. Related Work

**本节在全文中的位置。** 三条线定位本文：长上下文策略、TTT、机器人基础模型。

**原文讲解（长上下文策略）。** 现有 VLA/WAM 多数只取当前观测或 2–8 帧；扩展观测窗口的做法包括视觉化轨迹提示（TraceVLA）、压缩视觉语言 token（ContextVLA）、预测过去动作（past-token prediction）、缓存并门控历史 token（Gated Memory Policy），但都受限于固定上下文大小。另一条路把历史交给更高层语义：关键帧（BPP）、检索（MemER）、语言（OneTwoVLA、MEM）。还有一类把整段 rollout 自回归处理（RoboCat、VIMA、Gato、causal world modeling），长依赖建模好但真机长程部署时 KV cache 解码延迟线性增长。RNN 策略推理成本恒定，但 LSTM 类架构的 scaling 不如全注意力。**RoboTTT 自我定位为"循环状态是 fast weights 的 RNN"**，并强调正是这种循环结构让上下文长度可扩展。

还有一段专门谈**历史带来的 spurious correlation**（causal confusion、copycat agents）：策略会过拟合到历史观测里隐含编码的过去动作。既有缓解手段是摘要化、辅助目标、选择性绕过；RoboTTT 的答案是让 TTT fast weights 动态地把相关信息写进参数空间、同时擦掉冗余特征。

**原文讲解（TTT）。** TTT 是"用自监督目标在训练与推理时快速更新一小部分参数（fast weights）"的范式，近年在测试时优化目标、与语言/视觉模型的架构整合、训练效率上都有进展，并已在语言建模、视频生成、计算机视觉、3D 重建上验证。作者指出这些模态天然是序列的，而机器人同样是连续流式交互，因此迁移潜力大。

一个必须记住的澄清：近期若干机器人工作（Evolve-VLA、on-the-fly VLA adaptation via test-time RL、TTT-Parkour）也叫 "test-time training"，但**它们并不使用 fast weights**，而是在测试任务上收集额外数据微调整个模型。最接近本文设定的是 VITA（给 VLM 配 fast weights 以适配价值函数），而 RoboTTT 是直接在 TTT 层之上构建 visuomotor policy。

**原文讲解（机器人基础模型）。** 常见范式是从预训练 VLM 初始化 + 动作生成模块，差别主要在动作表示：自回归离散 token（RT-2、FAST、Magma）vs 连续动作 + 扩散/流匹配头（π0、GR00T N1、Octo、KI）。RoboTTT 原则上可插到任意骨干，本文实例化在 GR00T N1.7 上，并强调：**尽管 GR00T N1.7 只用单步/短上下文训练过，RoboTTT 把它的上下文扩到 8K（30 Hz 下约五分钟），而长上下文条件化这类能力只有在上下文足够长之后才涌现。**

**回看重点。** 若要写 related work，这一节的分类值得直接复用：把"长上下文"拆成 *扩大窗口 / 语义摘要 / 全历史自回归 / 循环状态* 四类，RoboTTT 落在第四类并声称同时拿到了容量与常数成本。

### 11. 6. Limitations and Conclusion

**本节在全文中的位置。** 三条局限，都指向具体的下一步而不是套话。

**原文讲解。** (1) **训练成本**随上下文长度上升，作者建议采用 TNT 等更新的 TTT 训练技术；(2) TTT 层的**目标函数仍是通用的**，可以探索面向机器人的自监督目标（如视觉领域 ViT3 的做法）；(3) 虽然任务表现提升明显，**它不解决部署中的所有失败模式**，与 RL 结合直接优化任务成功率是自然的下一步。

结论重申：模型 + 配方把 visuomotor context 扩到 8K，解锁四种能力，核心是把 TTT 作为沿时间维的序列建模机制，配方是 sequence action forcing + TBPTT；并首次观察到预训练上下文长度带来稳定的闭环性能提升，因此提出"上下文长度是机器人基础模型的新 scaling 轴"。

**回看重点。** 作者没有提到的两条边界值得自己补上：单平台单构型（YAM 双臂）、以及所有任务都是**桌面装配**这一类结构化长程任务。对于导航、移动操作或接触密集的力控任务，长上下文是否同样有效尚无证据。

### 12. Appendix A：架构、训练与部署细节

**原文讲解。** 除 Sec. 3.4 已引用的超参外，还有两点值得记：

**预训练数据长度分布（Fig. A.1）。**

![[papers/images/jiang2026robottt/dataset_episode_len_dist_page1.png|620]]

| Episode Length | < 512 | 512–1K | 1K–2K | 2K–4K | > 4K |
| --- | ---: | ---: | ---: | ---: | ---: |
| 占比 | 3.1% | 12.5% | 25.9% | **41.4%** | 17.1% |

数据是**特意 curated 成偏长轨迹**的（近六成轨迹超过 2K 步）。这条信息对解释 Fig. 8 很重要：8K 的收益部分来自"预训练数据本身就有足够长的轨迹去填满这个上下文"，换一批以短轨迹为主的数据，scaling 曲线未必成立。

**部署。** YAM 双臂桌面机器人 + 四台 RealSense D405（top/bottom/左右腕）480p RGB；推理在单张 RTX 5090 工作站上，控制频率 30 Hz。这与"推理成本不随上下文增长"的主张互为印证——8K 上下文仍能在单卡消费级 GPU 上跑 30 Hz。

### 13. Appendix B：任务定义、rubric 与评测协议

**本节在全文中的位置。** 主指标是 rubric 分，所以这一节直接决定主结果可不可信。

**原文讲解。** 三个任务都按任务特定 rubric 归一化到 $[0,1]$：

- **Pup Go Car**（Fig. A.2）：装车顶与第一个轮子，含拧螺丝、电钻使用、双手交接、翻转车身。rubric 是 14 档累进：拿起车顶 0.05 → 放上车身 0.1 → 螺丝插入 0.25 → 拿起电钻 0.3 → 钻头接触螺丝 0.35 → 车顶螺丝拧紧 0.45 → 电钻交给右手 0.5 → 车身翻转并稳定 0.55 → 拿起轮胎 0.6 → 轮胎插入 0.75 → 再拿电钻 0.8 → 对准轮胎螺丝 0.85 → 轮子拧紧 0.9 → 电钻交回左手 1.0。轮子装配最多允许两次尝试。
- **Gear Bot**（Fig. A.3）：底盘两侧各装一个齿轮与两个轮子，翻转底盘两次使轴朝上，装上红色"机器人头"，最后用遥控器让它动起来。rubric 是加法式：每次底盘翻转 +0.1、每个齿轮或轮子安装 +0.1、机器人头 +0.1、成功使用遥控器 +0.1。
- **Circuit**（Fig. A.4）：在电路板上装 2–3 个元件（红/绿/彩色 LED、灯、马达、snap wire、按钮、开关），左右元件遵循不同装配顺序，约 80 种配置。含开关或按钮时还必须在装配后打开电路。rubric 按元件数分档（两元件无开关每件 +0.5；两元件含开关每件 +0.33、通电 +0.33；三元件无开关每件 +0.33；三元件含开关每件 +0.25、通电 +0.25），**装配顺序错误不给部分分**。

**实验细节。** GR00T N1.7 与 Hist. 用官方实现（后者扩展支持历史帧输入）；GDN 用 Flash Linear Attention 库的 Gated DeltaNet 层替换 TTT 层，**层位置、门控与参数量都对齐 RoboTTT**。评测时记录每个任务的初始物体摆放并在各方法评测时复现，保证初始条件一致；Pup Go Car 与 Circuit 各 20 次 rollout，Gear Bot 与 Circuit 的一次性人类视频设定各 10 次。

**回看重点。** rubric 是**累进式**的，因此"完成分"对早期阶段的成功非常敏感：一个在第 3 档卡住的策略得 0.25，而它可能什么有意义的装配都没完成。这解释了为什么作者同时报告"完全成功次数"（Table 1）——两个指标要一起读，只看 79% vs 42% 会高估基线的实际可用性。

## 方法细节

按"输入 → 中间表示 → 训练目标 → 输出如何使用"四问拆解：

1. **输入是什么。** 每个时间步：多视角 RGB（top/bottom/左右腕）与语言指令经 VLM 得到 $\Phi_t$；本体感受编码为 $q_t$；上一步的动作 chunk 加噪后作为 $\tilde A_t$；外加 16 个 learned register token $R_t$。语言指令 $l$ 在整条轨迹上共享。
2. **中间表示是什么。** 两级：步内由 attention 融合（$R_t,q_t,\tilde A_t$ 自注意 + 对 $\Phi_t$ 交叉注意）；跨步由 TTT 层的 **fast weights** $W_t$ 承载——这是全文唯一的"记忆"，是一组两层 MLP 的参数，语义是"把 $K$ 关联到 $V$ 的映射"。注意 $\Phi$ 不进 TTT，跨时间的视觉语言信息只经 register token 传递。
3. **训练目标是什么。** 外层是逐时间步的 flow-matching 损失求平均（Eq. 4/5），每个 action chunk 独立采噪声等级；内层是 TTT 的 MSE 关联损失（Eq. 1），且内层学习率与 $W_0$ 都被外层梯度 meta-learn。长序列训练靠 TBPTT 分段回传但 fast weights 连续。特殊情形下对某些时间步**屏蔽外层损失**，使它们只做内层更新（人类视频段、DAgger 中的机器人失败段）。
4. **输出如何使用。** 每步输出 $H$ 步动作 chunk $A_t=[a_t,\dots,a_{t+H-1}]$，用 $k$ 步去噪生成，直接在 30 Hz 上执行；fast weights 在 rollout 中持续更新并向前传播，因此策略在部署期是"边执行边学"。

核心公式与变量速查：

| 公式 | 含义 | 变量要点 | 出现位置 |
| --- | --- | --- | --- |
| $W_t\leftarrow W_{t-1}-\eta\nabla_W\mathcal{L}_{\text{FW}}(f_{W_{t-1}}(K_t),V_t)$ | TTT 的 **update**：把上下文写入参数 | $\mathcal{L}_{\text{FW}}$ 取 MSE；$\eta$ 可学；$W$ 是两层 MLP 的参数 | Eq. 1，Sec. 2 |
| $O_t=f_{W_t}(Q_t)$ | TTT 的 **apply**：从参数中读出 | $Q_t$ 决定"查什么"，输出并入该层前向 | Eq. 2，Sec. 2 |
| $O=\tanh(\alpha)\odot O_{\text{TTT}}+O_{\text{attn}}$ | 门控，保护预训练能力 | $\alpha\in\mathbb{R}^d$ 初始化 0.001，逐层学习 | Eq. 3，Sec. 3.1 |
| $\mathcal{L}_{\text{fm}}(\xi;W_0)=\frac1T\sum_t \ell_t(\cdot;W_{t-1})$ | 序列级外层损失 | $W_{t-1}$ 的依赖使损失沿时间不可并行 | Eq. 4，Sec. 3.2 |
| $\frac1T\sum_t\mathbb{E}_{\tau_t,\epsilon}\lVert v_\theta(\Phi_t,A_t^{\tau_t},q_t;W_{t-1})-(A_t-\epsilon)\rVert^2$ | sequence action forcing 下的 flow matching | $\tau_t=s(1-u)$，$u\sim\mathrm{Beta}(1.5,1)$，$s=0.999$；**逐 chunk 独立采样** | Eq. 5，Sec. 3.2 |

## 实验设置、数据集、基线、指标

按 `数据集 → baseline → 指标 → 主结果 → 消融 → 失败案例` 走：

- **平台与数据**：YAM 双臂桌面机器人，四路 RealSense D405（480p），30 Hz 控制，RTX 5090 推理。任务数据 Pup Go Car 8 h、Circuit 6 h、Gear Bot 5 h，平均 episode 2 / 1 / 5 分钟。另有 30 分钟扰动数据（Pup Go Car）、Circuit 每训练配置 5–20 条人类视频、100 条 DAgger 轨迹（50 条由 RoboTTT 采、50 条由 GR00T N1.7 采）。预训练数据是 tabletop 双臂机器人 + egocentric 人类数据（EgoScale）的混合，刻意偏长轨迹（>2K 步占 58.5%）。
- **配置泛化设定**：Circuit 有约 80 种配置（元件、顺序、数量都变），训练 20 种、测试其余 60 种。
- **基线**：GR00T N1.7（单步）、GR00T N1.7 Hist.（+1 帧历史）、GDN（Gated DeltaNet 替换 TTT，层位置/门控/参数量对齐）。序列模型统一按 1K 上下文后训练，非序列模型按等算力预算训练。
- **指标**：rubric 归一化完成分（$[0,1]$，报百分比）+ 完全成功试验数。每策略 20 trials（Gear Bot 与一次性模仿设定为 10）。初始物体摆放被记录并在各方法间复现。
- **公平性设计**：GDN 与 RoboTTT 参数量对齐；register token 单独加到 GR00T N1.7 上作为 matched-token 对照；DAgger 实验四种方法共用同一批 100 条轨迹。这几处都做得比一般论文严格。
- **未覆盖**：没有跨本体/跨平台实验、没有 seed 重复与置信区间、没有报告推理延迟的实测数字（只在论述层面说"不随上下文增长"）。

## 主要结果、消融或对比

| 证据类型 | 原文线索 | 读法 |
| --- | --- | --- |
| 主结果（Fig. 7 + Table 1） | 平均 79% vs GR00T N1.7 42%（+87%）、GDN 56%（+41%）；Gear Bot 2/10 vs 全 0 | 完成分与完全成功次数一起看；累进 rubric 会抬高基线的表面分数 |
| 上下文 scaling（Fig. 8） | 8K 71.5% vs 1K 43.9%（+63%）vs 短上下文基线 45.6%（+57%）；GDN 平坦 | 这是"context scaling"主张的**唯一**直接证据；注意该曲线与主结果非同批模型 |
| 低上下文反例（Fig. 8 左段） | <1K 时不如短上下文基线 | 方法的硬边界：训练上下文需覆盖任务时程 |
| 一次性模仿（Table 2） | 65% / 6-of-10 vs GDN 33% / 0-of-10 | prompt 统一，目标只能来自视频，排除语言泄漏；GDN 全败=能编码不能利用 |
| 扰动鲁棒（Table 3） | 屋顶 15/20（GDN 13/20）、轮胎 18/20（GDN 也 18/20） | 唯一 GDN 追平的实验；说明"看到自己刚做过什么"比 update rule 表达力更关键 |
| DAgger（Fig. 10） | 标准 DAgger +9%（序列模型 +13%）；DAgger Distillation +33%（RoboTTT +36%、GDN +29%） | 关键对照是"GR00T 用全轨迹微调 = 只用纠正段（都 57%）"，把"数据更多"与"数据换角色"分开 |
| 恢复行为（Fig. 11） | 错过螺丝 → 抬臂重试 → 再调整 → 成功 | 把 DAgger Distillation 的增益机制可视化：增益主要来自失败后的恢复 |
| 消融（Fig. 12） | 无 sequence action forcing 显著变差；TTT Linear 比 MLP 差 27%；+action tokens +23%；+register tokens +18%；register 加到 GR00T 无效 | 每一条都对应方法中的一个设计点，是本文最扎实的部分 |
| 定性归因（Sec. 4 正文） | state aliasing 消解、策略性恢复、遮挡下的精细操作 | 这三条是"长上下文为什么有用"的机制解释，但都是定性观察，没有量化指标支撑 |

## 图表、公式与表格线索

**图。** Fig. 1 teaser（机制+四能力）｜Fig. 2 架构与训练/推理流程｜Fig. 3 $\tanh$ gating 计算流｜Fig. 4 TBPTT 段切分与 fast weights carry｜Fig. 5 三个评测任务｜Fig. 6 DAgger Distillation 的非对称用法｜Fig. 7 主结果条形图｜Fig. 8 上下文 scaling 曲线｜Fig. 9 一次性 in-context 模仿连续画面｜Fig. 10 DAgger 四条件对比｜Fig. 11 on-the-fly 恢复序列｜Fig. 12 消融｜Fig. A.1 预训练轨迹长度分布｜Fig. A.2–A.4 三个任务的过程图。

**表。** Table 1 三任务完全成功次数｜Table 2 一次性模仿｜Table 3 扰动恢复。三张表都是小样本计数，读的时候要意识到 20 次试验的分辨率。

**公式。** Eq. 1（TTT update）、Eq. 2（apply）、Eq. 3（gating）、Eq. 4（序列损失）、Eq. 5（sequence action forcing 下的 flow matching）。五个公式的关系是：1–2 定义机制，3 定义如何接入预训练模型，4–5 定义如何在长序列上训练。

**本地图片索引**：完整清单见 [[papers/images/jiang2026robottt/index.md]]（共 16 张，含未在正文嵌入的三张任务过程图）。

## 主张-证据-边界矩阵

| 主张 / 结论 | 原文证据 | 证据位置 | 解释 | 边界 / 适用条件 |
| --- | --- | --- | --- | --- |
| 长视觉-运动上下文能显著提升多阶段长程任务表现 | 平均完成分 79% vs 42%；Gear Bot 2/10 vs 0/10 | Fig. 7、Table 1 | 长上下文消解 state aliasing、支持策略性恢复与遮挡下操作 | 单平台三任务、10–20 trials；累进 rubric 抬高基线表面分 |
| 上下文长度是新的 scaling 轴 | 128→8K 单调上升，8K=71.5%，未饱和 | Fig. 8 | 更长训练序列给 $W_0$ 与更新动态更多 meta-learning 信号 | 依赖偏长轨迹的预训练数据；<1K 反向；曲线与主结果非同批模型 |
| 收益来自"测试时梯度下降"，而非"有记忆" | GDN 同为定长状态但 scaling 曲线平坦、一次性模仿 0/10 | Fig. 8、Table 2 | 非线性 fast model + 梯度下降是更强的流式压缩器 | 扰动实验中 GDN 追平，说明并非所有能力都需要这种表达力 |
| 长上下文解锁一次性 in-context 模仿 | 6/10 成功，prompt 统一 | Fig. 9、Table 2 | 视频段只更新 fast weights，模型学会从上下文抽取任务规格 | 仅 Circuit 一个任务、10 次试验；需同配置的人类视频配对数据 |
| 失败动作的价值在"作为上下文"而非"作为目标" | GR00T 全轨迹微调 = 只用纠正段（均 57%）；DAgger Distillation +33% vs 标准 +9% | Fig. 10 | 蒸馏的是失败→纠正的映射，即改进过程本身 | 只在 Pup Go Car 一个任务上验证；DAgger 数据由两种策略混采，来源偏置未分析 |
| 推理成本不随上下文增长 | fast weights 定长；单张 RTX 5090 上 30 Hz 部署 | Sec. 1/3.2、Appendix A.3 | 循环状态定长，与 Transformer KV cache 相反 | 论文未给延迟实测曲线，只给部署可行性 |
| 方法存在明确边界 | 训练成本随上下文上升；TTT 目标通用；不解决所有失败模式 | Sec. 6 | 作者主动承认并给出下一步（TNT、机器人化目标、接 RL） | 未讨论跨本体、非装配类任务、多操作者与安全约束 |

## 局限与可追问点

作者承认的：训练成本随上下文长度上升；TTT 的内层目标不是机器人专用；不解决部署中的所有失败模式（建议接 RL）。

需要自己补的边界与追问：

- **平台与任务面太窄**：单一 YAM 双臂桌面平台、三个装配任务，全部是结构化长程操作。移动操作、力控接触任务、跨本体是否同样受益，完全没有证据。
- **统计口径**：每条件 10–20 次试验、无 seed 重复、无置信区间；Table 3 的 15/20 vs 13/20 不应被当作显著差异。
- **容量与遗忘**：fast weights 是定长状态，8K 步之后是否出现记忆冲突或遗忘？论文没有做"上下文中放入干扰信息"的压力测试，而这正是长上下文模型最容易露馅的地方（可对照 LLM 的 needle-in-a-haystack 与 lost-in-the-middle）。
- **register token 瓶颈**：$N=16$ 未做消融；VL token 不进 TTT 是算力妥协，长期看可能限制"视觉细节"的跨时间保留。
- **plug-and-play 的说法未验证**：只在 GR00T N1.7 上实例化，π0/Octo 等不同动作头结构上的可移植性未测。
- **数据依赖**：预训练数据被 curated 成偏长轨迹（>2K 步占 58.5%），上下文 scaling 结论对数据长度分布的敏感性未知。
- **延迟与吞吐**：主张"不增长"但没有实测数据；fast weights 每步一次梯度下降的额外开销在 30 Hz 下占多少也未报。

## 与当前库的连接

- **人类接管 / 经验学习路线**：[[@xiao2026rove]]（OVE 从不完美接管中挑高价值行为）、[[@deng2026e2hil]]、[[@intelligence2025pi06-vla-that-learns]]（RECAP）、[[@yu2026wm-dagger]]（世界模型侧的 DAgger 数据聚合）。共同问题都是"部署经验怎么用"，但解法分成两派：ROVE/RECAP/STEAM 用 value 或 advantage 决定**哪些动作值得模仿**；RoboTTT 干脆把失败动作**降级为上下文**。这两派可叠加——用 [[@liu2026steam]]/[[@yu2026warp-rm]] 式的 advantage 给纠正段加权，再用 fast weights 承载失败→纠正映射。
- **推理期纠错**：[[@pan2026vla-corrector-lightweight-detect]] 外挂检测-纠正模块并自适应动作时域；RoboTTT 把纠错内化进策略自身的测试时更新。两者是"外挂 vs 内生"的直接对照，值得并读。
- **记忆与空间表示**：[[@zhou2026holoagent0]] 用显式三维空间记忆，RoboTTT 用隐式参数化记忆。互补性问题很具体：显式记忆擅长物体/位置的可查询事实，fast weights 擅长任务进度与动作时序，两者拼起来会不会比任一单独更好？
- **动作表示与 tokenization**：[[@kang2026x-tokenizer]]、[[@zhong2025action-tokenization-survey]]。RoboTTT 不改动作表示（沿用 flow matching 连续动作），改的是**时间维的建模机制**，可以作为综述分类里"raw action + 序列建模"一格的新样本。
- **世界模型 / WAM**：[[@wang2026wvm]]、[[@qian2026wam-rl]]、[[@gao2026fast-leworldmodel]]。RoboTTT 的 related work 明确把 WAM 归入"短上下文"一类，而 [[@wu2026tactile-wam]] 这类工作靠预测未来来获得时间信息——"预测未来"与"压缩过去"是两条互补的时间建模路线，可以做一张对照表。
- **可能的下一步阅读**：论文引用的 TTT 主线（Learning to (learn at test time)、Test-time training done right、TNT）与 Gated DeltaNet，是理解 Fig. 8 分叉的必要背景。

## 精读路线 / 为什么需要回看

1. 先读 `摘要`、`论文主线` 与 Fig. 1，确认作者把"上下文长度"而不是"模型规模/数据量"当作核心变量。
2. 再读 Sec. 2 的 Eq. 1–2 与 Sec. 3.1–3.2 的 Eq. 3–5，把"内层写入/读出 + 外层任务损失 + 分段回传"三层结构在脑子里闭合；这是复现与迁移的最小知识集。
3. 然后读 Sec. 3.3 与 Fig. 6：屏蔽损失这一个开关是本文最容易迁移到其他项目的设计，值得单独记住。
4. 实验部分按 Fig. 8 → Table 2 → Fig. 10 的顺序读（scaling 主张 → 新能力 → 数据用法），最后再看 Fig. 7/Table 1 的横向比较；反过来读容易被 87% 这个数字带偏。
5. 若要引用：引"上下文 scaling"必须带上 Fig. 8 的边界（<1K 反向、数据偏长轨迹、与主结果非同批）；引 DAgger Distillation 必须带上"GR00T 全轨迹微调无增益"这个对照，否则会被误解为"多用数据就好"。
