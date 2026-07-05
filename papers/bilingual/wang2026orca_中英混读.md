---
tags:
  - bilingual-reading
  - deep-reading
paper: "[[@wang2026orca]]"
source_pdf: "[[papers/pdfs/wang2026orca.pdf]]"
images: "papers/images/wang2026orca/"
image_index: "[[papers/images/wang2026orca/index.md]]"
created: 2026-07-05
reading_mode: 生成式精读（逐节读原文 + 读图）
---

# Orca: The World is in Your Mind

paper:: [[@wang2026orca]]
pdf:: [[papers/pdfs/wang2026orca.pdf]]
images:: [[papers/images/wang2026orca/index.md]]

> 读图说明：本文的 arxiv source 只随附了一张 **ORCA 项目 logo 字标**（`papers/images/wang2026orca/BAAI.png`，`index.md` 也确认"总计 1 张图片"）。它是 logo、无内容价值，故**不嵌入**。正文里的 Figure 1–8 / A1 / C1 / E1–E7 / F1–F3 都是矢量图，未导出成独立 PNG，本稿据原文 caption 与正文文字重建它们的"证明什么"。

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| general world foundation model | 通用世界基础模型 | Orca 的目标形态：从多模态 world signals 学一个统一 world latent，再用多模态 readout 支持"理解/预测/行动"。本文是它的 initial instantiation（初始实例）。 |
| Next-State-Prediction (NSP) | 下一状态预测 | 全文核心范式主张：**不**优化 next-token / next-frame / next-action，而是把"状态转移 $S_t\!\to\!S_{t+\Delta}$"作为唯一建模目标（Eq.1）。 |
| world latent space / world latent | 世界潜空间 | Encoder 学到的统一潜表示，是标题"the world is in your mind"的落点；三个 readout 全从它读出。frozen 之后做 probing 验证它是否可迁移。 |
| unconscious learning | 无意识学习 | 无标签自监督，从连续视频抓 **dense natural** 状态转移（$c_t=\emptyset$），target 取最近未来帧的 latent。对应目标 $\mathcal L_{\text{obs}}$。 |
| conscious learning | 有意识学习 | 语言约束下学 **sparse meaningful** 状态转移：用 event 描述预测相邻事件 latent（$\mathcal L_{\text{evt}}$）+ VQA 监督（$\mathcal L_{\text{vqa}}$）。 |
| implicit dynamics $z_t$ / explicit conditions $c_t$ | 隐式动力学 / 显式条件 | Eq.(1) 里驱动状态变化的两类因素：$z_t$ 是不可观测因子（物理规律、物体属性、场景动力学），$c_t$ 是可观测条件（人类指令/事件）。 |
| observation-only state transition ($\mathcal L_{\text{obs}}$) | 纯观测状态转移 | 通过 `<Query 1>` $q_1$ 预测**下一相邻帧**的 latent $\hat v^l_{t+1}$，是 unconscious learning 的实现。 |
| event-conditioned state transition ($\mathcal L_{\text{evt}}$) | 事件条件状态转移 | 给定帧 + instruction $e_{t+\Delta}$ + `<Query 2>` $q_2$，预测相邻事件（前/后向）的 latent $\hat v^l_{t+\Delta}$。 |
| VQA response generation ($\mathcal L_{\text{vqa}}$) | VQA 应答生成 | 用 backbone 自带 LM head 做 next-token 预测答案，保住语言接口 + 常识/语义 grounding。 |
| learnable query | 可学习查询向量 | 从头训练的 256 个 query，把两条状态转移预测挂到冻结不动的 VLM 输入序列上：`<visual token>,<Query 1>,<Instruction>,<Query 2>`。 |
| latent matching loss | 潜空间匹配损失 | $0.1$ MSE $+\,0.9$ cosine（Eq.C-1），**在冻结 vision encoder 的 latent 空间**监督预测帧，而非像素级重建——聚焦"状态建模"而非"画画"。 |
| readout probing / frozen backbone | 读出探针 / 冻结主干 | 下游只训 readout（LM head / SD3.5 LoRA / Action Expert），backbone 全程冻结——用"探针"直接检验 latent 好坏，而非追 task SOTA。 |
| Action Expert | 动作专家 | DiT + flow-matching，从头训练；吃 Orca latent（$q_1$）+ noisy action + proprioception，多步去噪出 action chunk（horizon 30、dim 16）。 |
| PRICE-V0.1 | PRICE 基准 | 本文自建的真实世界 **TI2I**（instruction-conditional image-to-image）预测基准，用 MLLM-as-judge 打 1–5 分，测"执行指令后的状态变化图"。 |
| PRM-as-a-Judge | 过程奖励评审 | 提供轨迹级 dense 诊断指标（M25/M50/SR/MaxP-F/FNS/DRR/SQS）的评审器，用于真实机器人动作评估。 |
| inventory data | 库存数据 | 125K 小时视频 + 160M event 标注 + 11.5M VQA 的"世界学习库存"；**本版仅用 1/10 视频**（约 12.5K h）。 |
| FlagScale / FSDP2 | 训练框架 / 全分片并行 | 自研训练栈，配合 chunked CE + activation recompute + pre-fetch，把吞吐从 0.66 拉到 2.91 samples/sec/GPU。 |

## 论文主线

**核心问题**：智能的下一步该以什么为建模目标？作者的判断是——不该继续绑在某个模态的输出上。现有范式都"以它预测的输出为中心"：LLM 做 **Next-Token-Prediction**（语义理解）、图像/视频模型做 **Next-Frame-Prediction**（视觉动力学）、具身模型做 **Next-Action-Prediction**（动作可供性）。这些都能造出强的 task-level 能力，但建模目标始终"tied to specific modalities"。Orca 主张把**世界的潜状态**当作唯一的建模对象，语言/视觉/动作只是同一个 world state 的不同 observation 或 readout，于是范式从 next-token/frame/action 转向 **Next-State-Prediction**（Appendix A 的 Figure A1 把这条"从 passive task-driven 到 active world learner"的转变画成一张概念图）。

**动机**：一个 general world foundation model 应当持续吸收多模态 world signals 来建模世界的 latent state，并用 state-transition modeling 作为"已观测/未知域"通用范式。理想里这些信号该覆盖 vision/text/audio/action/tactile 等 neural signals、force/light 等 physical signals、乃至宏观宇宙、微观量子、生命科学等 fields。本版本只落到 **vision + language** 两类最基础的信号：视觉对应"人如何感知世界"，语言对应"人如何理解世界（因果解释 + 任务意图）"。

**核心观点**（Figure 1 / Encoder-Decoder 总览）：Orca 走 **Encoder–Decoder** 架构。给多模态 world signal，**Encoder**（一个原生预训练 VLM，Qwen3.5，vision/language 已对齐）通过两个互补范式学 world latent——unconscious learning 抓 dense natural 转移，conscious learning 抓 sparse meaningful 转移。**预训练后 Encoder 冻结，只训练轻量、按模态分开的 Decoder**；Decoder 把 latent 读出成 text / image / action。关键立场是：这些 readout **不是为了刷 task-specific SOTA**，而是回答两个核心问题——(1) 这套范式是否 feasible & scalable；(2) 更强的 world modeling 是否带来更强的 downstream readout。

阅读时要盯住一句判断：**本文的贡献不是"某个 readout 打赢了谁"，而是"一个被冻结的 world latent，能不能同时喂好语言/视觉/动作三条下游"**——正是"backbone frozen + 只训 readout"这个设定，把"latent 是否真的通用"变成了可测的实验（§4.1 的 Q1.1/Q1.2、§4.3 的消融）。而且有一个反直觉的观察：预训练**没有用任何 action 标签**，动作 readout 却能靠视频数据涨起来（§4.1.2 的 emergent capability），被作者视为缓解"机器人数据稀缺→泛化差"的一条线索。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| 提出 Orca：从多模态 world signals 学统一 world latent，作为下游 readout 的通用接口，把建模目标从 next-token/frame/action 转向 **next-state**。 | §2.1 Eq.(1) 状态转移；§2.2 Encoder-Decoder；Fig.1 | 三类 readout 全部在冻结 backbone 上得到结果（Table 1/3/4）。 | 概念清晰、工程扎实；但"general"目前仅落到 **vision+language 两模态、三 readout**。 |
| 设计两个互补学习范式：unconscious（dense natural）+ conscious（sparse meaningful）。 | §2.1、§3.1.1；三目标 $\mathcal L_{\text{obs}}/\mathcal L_{\text{evt}}/\mathcal L_{\text{vqa}}$（Eq.2） | 消融 Table 5：三目标联用 Avg **48.0** 最均衡。 | 消融支持"三者互补且各有分工"；但每个 readout 主要吃其中一两个目标。 |
| 构建大规模 inventory：125K h 视频 + 160M event + 11.5M VQA，覆盖 ego/exo/action-free/natural dynamics。 | §3.1.2；Fig.3 | 本版**仅用 1/10 视频**（≈12.5K h）就跑出 scaling 曲线（Fig.5/6）。 | 数据体量大；但只有 1/10 入训，"数据规模 ↔ 世界知识"关系尚未打满。 |
| 实验证明 latent 有效、可 scale，且更强 latent → 更强 readout。 | §4.1（Q1.1 Fig.5 / Q1.2 Fig.6） | Fig.5 loss 随数据持续下降、4B<0.8B loss；Fig.6 三 readout 随数据同步上升；Table 1 Orca-4B Avg **51.8** 居首。 | probing 逻辑成立；action 无标签仍涨是亮点，但真实 SR 仍很低（Overall SR **6%**）。 |
| Orca 在可比规模上超过 specialized baselines。 | §4.2 三 readout | 文本超同尺寸 VLM 与大号 world model；图像 PRICE Avg 最高；动作超 Qwen3.5、与预训练 $\pi_{0.5}$ 相当。 | 三线都"可比或更好"，但动作只与 $\pi_{0.5}$ 打平、object OOD 还略输。 |

## 摘要与核心贡献

摘要把 Orca 定位成"a general world foundation model 的初始实例"。它从多模态 world signals 学一个 **unified world latent space**，并通过多模态 readout interface 暴露出来。与"孤立地优化 next-token / next-frame / next-action"不同，Orca 以 **Next-State-Prediction** 为中心，提供一条统一的 state-transition modeling 路线来"理解、预测、作用于"世界。学习靠两个互补范式：**unconscious learning** 从连续视频抓 dense natural 状态转移；**conscious learning** 用 language-described events + VQA 监督建模 sparse meaningful 转移。

预训练用一个大规模 **world-learning inventory**：**125K 小时视频 + 160M event 标注**（正文补：另有 11.5M 通用 VQA，且本版只用 1/10 视频）。预训练后得到统一 world latent，用三个代表性 readout 检验——**text generation、image prediction、embodied action generation**；backbone 冻结，只训轻量的 modality-specific decoder。实验显示范式可 scale，且"更强的 world latent → 更强的 downstream readout"，在可比规模上超过 specialized baselines。

> 读原文才注意到的口径细节：摘要里"outperforms similar-sized specialized baselines"要看清尺寸标注——文本里 Orca-4B（Avg 51.8）赢的是**同尺寸 tiny/small VLM 与更大号的 world model（Emu3.5-34B 只有 29.8）**；图像里 Orca 记作 **4+2B**（4B backbone + 2B SD3.5 解码），赢过 12B 的 FLUX.1-Kontext；动作里 Orca 只是与预训练在大规模机器人数据上的 $\pi_{0.5}$ **相当**，且 object OOD 还略低。所以"超过 baseline"是"可比规模下总体更优"，不是全项碾压。

## 按原文 section 逐节精读

### 1. Introduction / 从"预测什么输出"转向"预测世界状态"

作者开宗明义：通向 general intelligence 的关键一步，是造一个能像人一样持续学习、self-evolve、最终突破人类认知边界的模型；它内化物理规律、因果关系、动态演化，成为 self-emerging 的智能系统。这样的模型应持续吸收多模态 world signals 来建模世界的 latent state，并用 **state-transition modeling** 作为"已观测域 + 未知域"的统一范式。

由此推出核心论点：智能**不该**只是能听指令的 Next-Token-Prediction、能生成好图/视频的 Next-Frame-Prediction、或能生成好动作的 Next-Action-Prediction；它应由"构建 world state、支撑多样下游任务的 latent space"来定义。这指向一个 grounded in **Next-State-Prediction** 的 general world foundation model，含 **implicit dynamics** 与 **explicit conditions**。

**这一节读法**：introduction 没有停在"世界模型很重要"，而是把"世界模型"从"能生成漂亮画面的生成器"重新定义成"能建模状态转移的 latent 学习器"——后面 §2 的 Eq.(1)、§3 的三目标、§4 的两个探针问题，都可以回勾到这里的"next-state 而非 next-{token,frame,action}"这句主张。四点贡献（提出 Orca / 两范式 / inventory 数据 / 可 scale 的实验）正是这条主张的逐项兑现。

### 2. Orca / 建模与架构

#### 2.1 Modeling（宏观 + 细节）

**Macro.** Orca 把 world learning 形式化成 latent world-state modeling，含"从多模态信号做 state abstraction"和"state transition"两步。给世界信号 $\mathbf X=\{X_m\}_{m\in\mathcal M}$，映射到 latent world state $\mathbf S=f_\theta(\mathbf X)$。状态在 **implicit dynamics** 与 **explicit conditions** 下前向/后向演化：

$$
S_{t+\Delta}\ \sim\ p_\Theta\!\left(S_{t+\Delta}\ \middle|\ S_t,\ z_t,\ c_t\right),\qquad \Delta\in\mathbb Z_{\neq 0}. \tag{1}
$$

其中 $z_t$ 实现 **invisible dynamics**（捕获物理规律、物体属性、场景动力学、环境力等驱动状态变化的隐/未观测因子），$c_t$ 实现 **explicit conditions**（人类指令等可观测条件）。$\Delta>0$ 预测未来 $S_{>t}$，$\Delta<0$ 回溯过去 $S_{<t}$——**双向**是 Orca 有别于纯前向视频预测的一处设计。

**Details.** 本版用 vision + language 两类信号，用两个互补范式实现 Eq.(1)：

1) **Unconscious learning** 从纯观测学转移，等价于 $c_t=\emptyset$：
$$
S_{t+\Delta}\ \sim\ p^{u}_\Theta\!\left(S_{t+\Delta}\ \middle|\ S_t,\ z_t\right),
$$
target state 取自 **nearest future observation**，学 dense & natural 转移（物体运动、遮挡、场景变化）。

2) **Conscious learning** 在显式语义条件下学转移，语言可指定一个 event $c_t=e_{t+\Delta}$（未来或过去事件）：
$$
S_{t+\Delta}\ \sim\ p^{c}_\Theta\!\left(S_{t+\Delta}\ \middle|\ S_t,\ z_t,\ e_{t+\Delta}\right),
$$
条件也可以是 task intention 或 causal premise，学 sparse & meaningful 转移。

#### 2.2 Architecture（Encoder / Decoder）

**Encoder**（Figure 2）是全文重点：用一个原生预训练 VLM（Qwen3.5，vision/language 已对齐）学统一 world latent，通过三个子过程实现——

- **1) Observation-only state transition**：输入视频某帧 $v_t$，经 VLM + 两层 MLP 预测下一相邻帧 latent $\hat v^l_{t+1}$；ground-truth 帧 $v_{t+1}$ **只过冻结的 vision encoder** 得 $v^l_{t+1}$，与预测做 teacher forcing。
- **2) Event-conditioned state transition**：把视频按 meaningful event 切段，每段配一条 instruction；输入 $v_t$ + 相邻（前/后）event 的描述 $e_{t+\Delta}$，输出该 event 关联的随机帧 latent $\hat v^l_{t+\Delta}$。
- **3) VQA response generation**：输入视频 $V$ + 问题 $l_q$，输出语言答案 $l_a$——conscious learning 里"理解世界"的那条通路。

**Decoder** 是 modality-specific 的读出模块，细节在 §3.2（不是本节重点）。

**这一节读法**：注意监督位置——前两条转移都在**冻结 vision encoder 的 latent 空间**里 teacher forcing，不做像素重建。这既简化训练，也埋下 §5 自陈的局限之一：latent 被对齐到了 VLM 的语义空间，而非"从多源信号直接定义"的原生 world space。

### 3. Training / 两阶段

Orca 分两阶段：**pre-training** 用大规模视觉+语言数据学 world latent；**downstream post-training** 冻结 backbone，只训 modality-specific readout 得到语言/视觉/动作能力。

#### 3.1 Pre-Training

**3.1.1 Recipe.** 预训练把 world-state modeling 落成三目标：observation-only、event-conditioned、VQA。前两条用 backbone 输入里的 **learnable query** 实现，第三条走 backbone 的 **LM head**。输入格式为 `<visual token>,<Query 1>,<Instruction>,<Query 2>`，**所有 query 从头训练**（共 256 个）。总损失：

$$
\mathcal L=\lambda_{\text{obs}}\,\mathcal L_{\text{obs}}+\lambda_{\text{evt}}\,\mathcal L_{\text{evt}}+\lambda_{\text{vqa}}\,\mathcal L_{\text{vqa}}. \tag{2}
$$

前两条在 vision encoder 的 latent 空间监督（focus 状态建模，不做像素重建），第三条用标准 next-token loss。潜空间匹配用 MSE + cosine 的组合（Appendix C-1）：

$$
\ell_{\text{lat}}(\hat v^l,v^l)=0.1\,\lVert \hat v^l-v^l\rVert_2^2\ +\ 0.9\left(1-\frac{\langle \hat v^l,\,v^l\rangle}{\lVert \hat v^l\rVert_2\,\lVert v^l\rVert_2}\right). \tag{C-1}
$$

$$
\mathcal L_{\text{obs}}=\mathbb E\big[\ell_{\text{lat}}(\hat v^l_{t+1},\,v^l_{t+1})\big],\qquad
\mathcal L_{\text{evt}}=\tfrac12\,\mathbb E\big[\ell_{\text{lat}}(\hat v^l_{\text{prev}},v^l_{\text{prev}})+\ell_{\text{lat}}(\hat v^l_{\text{next}},v^l_{\text{next}})\big]. \tag{C-2,\,C-3}
$$

注意 $\mathcal L_{\text{evt}}$ 是**前向 + 后向两个方向的平均**（对应 Eq.1 的 $\Delta\gtrless0$）。实际系数为 $\mathcal L_{\text{pre}}=0.1\,\mathcal L_{\text{obs}}+0.5\,\mathcal L_{\text{evt}}+0.4\,\mathcal L_{\text{vqa}}$，state-transition 与 VQA 样本采样比约 **5:1**。

**3.1.2 Data**（Figure 3）：三类互补数据——
- **A. Video Data**：真实世界观测，四类：**ego-centric interaction**（第一视角物理交互）、**exo-centric manipulation**（第三视角物体变化）、**action-free robot execution**（机器人执行，无动作标签）、**natural dynamics**（自然演化场景）。支撑目标 1 与 2。
- **B. Event Data**：由 A 经多层 event 分割 + 语言标注得到，**coarse events** 描述主步骤、**fine-grained events** 描述步内更短的转移，每段配一条转移 caption。支撑目标 2。
- **C. VQA Data**：由语言信号 + 视频构成，教 Orca 描述/解释观测到的 world state。支撑目标 3。

现存数据：**125K h 视频 + 160M event 标注 + 11.5M 通用 VQA**；**本版只用 1/10 视频**，其余留给后续迭代。

#### 3.2 Downstream Post-Training（Figure 4）

目标是"探针"式验证 latent 是否对下游有效，所以 **backbone 永远冻结，只训对应 readout**：做视觉就只训 image 模块、做具身就只训 action 模块。

- **(a) To Language**：直接复用 backbone 的 **LM head**，不加额外 decoder，把 latent 表达成自然语言。
- **(b) To Vision**：latent 过 **MLP adaptor** 后作为一路输入进冻结的 **SD3.5（MMDiT）**；GT 图加高斯噪声、过冻结 VAE 进另一路；多步去噪出图。训练时只有 **MLP adaptor + LoRA** 可训（可训参数 556.9M，target image 768×768）。
- **(c) To Action**：**Action Expert** 是 DiT + flow-matching，**从头训练**；接 latent（$q_1$ 过 MLP adaptor 当条件）+ noisy action（带 time embedding）+ proprioception，多步去噪出 action chunk。关键约束：**Action Expert 每个任务只见过 200 条轨迹**（horizon 30、action/state dim 16、8 个 DiT block、推理 4 步）。

#### 3.3 Infrastructures

基于自研 **FlagScale**，用 FSDP2 重建训练：flexible 参数分片 + reshard；**activation recompute** 省激活显存；**chunked cross-entropy** 避免物化整个 logits（长序列/大词表下的显存尖峰）；**forward/backward pre-fetching** 把 all-gather 通信与计算重叠。吞吐从 **0.66 → 2.91 samples/sec/GPU（H100）**，相对常用的 StarVLA **约 4.4×**、相对 FSDP2 baseline（0.97）**约 3.0×**（Table D1 拆了每步增量：0.97→1.35→2.86→2.91）。

### 4. Evaluation / 实验

见下方"## 实验"节的完整 setup / baseline / 指标 / 主结果 / 消融拆解。这里先记住 §4.1 的两个"探针问题"作为全章骨架：

- **Q1.1**：随模型/数据 scale up，Orca 的学习范式是否 effective？**Answer 1.1**（Fig.5）：总 loss 随数据持续下降、且 4B 的目标 loss 低于 0.8B——范式 effective & scalable，loss 曲线未快速收敛而是持续受益于更多数据/更大模型。
- **Q1.2**：更强的 pre-training latent 是否提升 downstream readout？**Answer 1.2**（Fig.6，在 0.8B/4B 上 probe 多个 checkpoint）：文本/图像/动作三 readout 随预训练数据同步提升；且**预训练无 action 标签**，动作 readout 仍靠视频数据获益——一种可能缓解机器人数据稀缺的 emergent capability。

### 5. Conclusion / 结论与局限

**结论**：Orca 不是为某个孤立下游任务定制，而是先从多模态 world signals 学 world state 的内部表示，再通过一套 readout 接口暴露它——把建模目标从 next-token/frame/action 转向 next-state，是通向 general world foundation model 的一个 early exploratory milestone。

**作者自陈的 8 条局限（§5 Discussion & Limitation，非常坦诚）**：
1. **模态有限**：只 vision+language；很多状态转移靠 audio（水沸腾常先有声）、tactile/force（接触、滑移、刚度、是否抓牢）才能感知，未来应纳入更多 neural/physical 信号。
2. **ViT 空间监督**：在冻结 vision encoder 的 latent 里监督，简化了训练，但把 world state 对齐到了**语义空间**；理想应从多源信号**直接**定义/约束状态。
3. **模型规模受限**：只做到 4B / 0.8B；且 4B 随预训练进行在"语言/图像/动作"间出现 **trade-off**，0.8B 更明显——说明 world learning 不仅受数据规模限制，也需要足够模型容量（故 125K h 只用了 1/10）。
4. **视觉 benchmark 受限**：PRICE-V0.1 的规模/多样性/交互丰富度仍有限。
5. **短时程监督**：event 标注多是 minute-level 短时程转移，难建模小时/天级的长期演化。
6. **readout 有限**：只验了语言/视觉/动作，尚缺听觉、量子电路、蛋白质等 field。
7. **loss function 受限**：三个 loss 对 NSP 建模"不够一致"，需要更简洁的监督。
8. **具身任务难度受限**：设定 stringent 导致数值偏低，但当前任务本身仍偏短偏易。

**Future works** 五条：更多模态**对齐到同一 state**、native world-state modeling（从头训、不依赖某个 ViT 空间）、构建 world-model 状态转移评估体系、Model-Data-Evaluation 自进化闭环、从具身扩展到 AI for science / 量子 / 宇宙 / 生命科学。

## 方法细节

- **为什么用 learnable query 而非直接回归**：两条状态转移都靠 `<Query 1>`/`<Query 2>` 的最后一层 hidden state 过两层 MLP 得预测 latent（Fig.C1）。query 从头训练、backbone 只微调 LLM 部分（Table C1：Visual encoder/ViT 冻结、LLM 可训、Base VLM lr $3.5\!\times\!10^{-5}$、visual head lr $1.2\!\times\!10^{-4}$、256 queries、10,844 步、32 节点/256 GPU）。这让"状态预测"成为挂在 VLM 上的一个可插拔头，而非改造 backbone 本身。
- **latent 空间监督 vs 像素重建**：Eq.(C-1) 的 $0.1$ MSE $+\,0.9$ cosine 明显偏向方向（cosine）而非幅度（MSE），呼应"我们要的是状态一致，不是逐像素还原"。这也解释了图像 readout 为何要另接 SD3.5——Orca 本身不生成像素，只生成"目标状态的 latent"，像素交给冻结的扩散解码器。
- **双向转移**：$\mathcal L_{\text{evt}}$ 同时预测 previous-event 与 next-event 的 latent（Eq.C-3 取二者平均），把 Eq.(1) 的 $\Delta<0$ 回溯落到实处——这是"world model"而非"future predictor"的一个标志性区别。
- **Action Expert 的极小数据设定**：DiT flow-matching、8 block、hidden 1024、12 heads、horizon 30、推理 4 步；每任务仅 200 条轨迹、20k 步、batch 128。对比 $\pi_{0.5}$ 用官方配置 30k 步、batch 32。**"从头 Action Expert + 冻结 world backbone"**是全文"latent 是否可迁移到动作"的最硬核测试。

## 实验

### Setup / 基准、基线、平台

- **文本生成**：benchmark = MVBench（通用视频理解 QA）、TemporalBench（细粒度时序，用 MBA 指标）、3DSRBench（3D 空间推理）、SWITCH（真实世界 TCI 交互、因果预测）。baseline 两类：**world models**（V-JEPA 2.1 + LLaMA3-8B @10B、Emu3 @8B、Emu3.5 @34B）与 **VLMs**（Qwen3.5、Gemma 4、SmolVLM2、MiniCPM-V-4.6、DeepSeek-VL2）。全 **zero-shot**，不在评测集上 tune。
- **图像预测**：自建 **PRICE-V0.1**（真实世界 TI2I，源自 AgiBot-World / HomeInteract / PE-Video / PSI-Ego）。指标 = 用 **Gemini 3.1 Pro / GPT 5.4 / Doubao-Seed-2.0 / 开源 Gemma 4-31B 四个 judge** 读"初始图 + 指令 + 生成的目标图"打 1–5 分（看指令执行、场景一致、物理合理），转百分比。baseline：OmniGen2（3+4B）、FLUX.1-Kontext（12B）、FLUX.2 [klein]（4+4B）。
- **动作生成**：**双臂轮式人形机器人**，5 任务：Take Book、Stacked Bowls、Pull Out Tissue、Stamp、Scoop Sugar，各采 200 条轨迹。两种 OOD：**environment OOD**（换 3 种未见桌布/背景）、**object OOD**（换语义相关的未见物体/容器，如 book→cutting board、bowls→boxes、tissue→bread、regular stamp→children's stamp、sugar→candy）。指标：task-specific **rule-based score**（按 key-stage 打分，见 Table E2）+ **PRM-as-a-Judge** 轨迹级诊断（M25/M50/SR/MaxP-F/FNS/DRR/SQS）。baseline：V-JEPA 2.1 w/ AE、Qwen3.5 w/ AE（都接**同一个** Action Expert，只是条件不同）、$\pi_{0.5}$（大规模机器人数据预训练的强 VLA）。所有 backbone 冻结、Action Expert 从头训。

### Scaling 行为（Fig.5 / Fig.6，§4.1）

- **Fig.5**：横轴预训练视频小时数、纵轴总 loss（Eq.2）；0.8B 与 4B 两条线都持续下降，4B 更低。→ 范式 effective & scalable。
- **Fig.6**：三 readout（text / image / action）性能随预训练数据单调上升，4B 高于 0.8B。→ 更强 latent → 更强 readout；动作在**无 action 标签预训练**下仍涨，是 emergent。

### 主结果 1：文本生成（Table 1）

同尺寸/更大号 baseline 逐项对比（越高越好；Avg 为四项均值）：

| Model | Size (B) | MVBench↑ | TemporalBench↑ | 3DSRBench↑ | SWITCH↑ | Avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Emu3 (Chat) | 8 | 35.2 | 9.5 | 39.1 | 38.0 | 30.4 |
| Emu3.5 | 34 | 39.5 | 9.5 | 31.3 | 38.9 | 29.8 |
| Qwen3.5 | 0.8 | 52.7 | 19.1 | 21.8 | 38.8 | 33.1 |
| MiniCPM-V-4.6 | 2 | 41.4 | 21.2 | 47.7 | 41.2 | 37.9 |
| Gemma 4 | 4 | 45.6 | 20.2 | 44.8 | 52.4 | 40.8 |
| Qwen3.5 | 4 | **67.1** | 25.2 | 48.1 | 42.8 | 46.7 |
| **Orca** | 0.8 | 53.6 | 22.6 | 43.4 | 43.7 | 40.8 |
| **Orca** | 4 | 65.3 | **34.2** | **52.1** | **55.6** | **51.8** |

**怎么读**：Orca-4B 的 Avg **51.8** 是全表最高，且在 TemporalBench（时序）、3DSRBench（空间）、SWITCH（交互因果）三项拿到最好——这几项恰是"状态转移/时序动力学"最吃重的维度。MVBench 上 Qwen3.5-4B（67.1）略高于 Orca（65.3），说明纯"视频识别"类不是 Orca 的独占优势区。值得注意的是 34B 的 Emu3.5 Avg 只有 29.8，印证作者"生成式 world model ≠ 强状态理解"的观点。（注：V-JEPA 2.1+LLaMA3-8B 因未公开对齐数据，只报了 MVBench 75.4 / TemporalBench 28.5，不参与 Avg。）

**Table 2（跨 benchmark 能力聚合，Orca-4B vs Qwen3.5-4B）**——把样本按能力维度重聚合：

| 能力维度 | Qwen3.5-4B | Orca-4B |
| --- | ---: | ---: |
| State Transition | 51.86 | **64.13 (+12.27%)** |
| Commonsense Reasoning | 57.76 | **62.95 (+5.19%)** |
| Spatial Relations | 54.68 | **55.25 (+0.57%)** |
| Dynamic Motion | 57.03 | **65.55 (+8.52%)** |

增益最大的是 **State Transition（+12.27%）** 与 **Dynamic Motion（+8.52%）**，Spatial Relations 几乎持平（+0.57%）。这条曲线很干净地支持全文主张：Orca 强的是"状态如何随时间/动作演变"，而非静态空间几何。

### 主结果 2：图像预测（Table 3，PRICE-V0.1）

四个 judge 打分（越高越好；Avg 记 $a\pm b$，avg 大、std 小更好）：

| Model | Size (B) | Gemini 3.1 Pro | GPT 5.4 | Doubao-Seed-2.0 | Gemma 4-31B | Avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OmniGen2 | 3+4 | 24.6 | 46.8 | 41.4 | 45.5 | 39.6±10.2 |
| FLUX.1-Kontext | 12 | 21.6 | 46.9 | 42.7 | 52.5 | 40.9±13.5 |
| FLUX.2 [klein] | 4+4 | 29.7 | 64.6 | 60.0 | **70.2** | 56.1±18.1 |
| **Orca** | 0.8+2 | 17.0 | 48.5 | 46.0 | 26.5 | 34.5±15.3 |
| **Orca** | 4+2 | **44.0** | **67.9** | **61.0** | 66.3 | **59.8±10.9** |

**怎么读**：Orca-4+2B 的 Avg **59.8** 最高，且 std **10.9** 比 FLUX.2 的 18.1 低——四个 judge 打分更一致。Gemini 3.1 Pro（最严格的 judge）上 Orca 44.0 远超 FLUX.2 的 29.7，这一格差距最能说明"Orca 不是画得更漂亮，而是状态变化更贴指令"。Figure 7 的定性对比佐证：通用图像生成 baseline 常有"无关物体凭空出现/瞬移、幻觉人手、指令不遵从、先验偏置"；Orca 更好地保住 robot morphology、场景/物体一致、contact relationship、指令遵从。但要注意 Orca-0.8+2B 只有 34.5，低于所有强 baseline——图像 readout 对 backbone 规模很敏感。

### 主结果 3：动作生成（Table 4，PRM-as-a-Judge，均越高越好）

| Overall | Rule-based↑ | M25↑ | M50↑ | SR↑ | MaxP-F↑ | FNS↑ | DRR↑ | SQS↑ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| V-JEPA 2.1 w/ AE | 17.0 | 27 | 7 | 0 | 17.4 | 10.1 | 20.5 | 0.0 |
| Qwen3.5 w/ AE | 10.5 | 18 | 5 | 0 | 13.1 | 7.6 | 11.9 | 0.0 |
| $\pi_{0.5}$ | 29.4 | 54 | 14 | 5 | 26.5 | 15.3 | 26.7 | **3.0** |
| **Orca** | **32.4** | **55** | 14 | **6** | **27.9** | 15.1 | **30.3** | 2.9 |

分 OOD 看：**environment OOD** 下 Orca rule-based **36.6** 最高（$\pi_{0.5}$ 27.6）；**object OOD** 下 $\pi_{0.5}$ **31.2** > Orca 28.2。（Table E3 逐任务：env OOD 里 Orca-4B 在 Stamp 拿到 62 分远超 $\pi_{0.5}$ 的 9，是拉开总分的关键任务。）

**三点结论**：
1. **latent 迁移到动作成立**：从头 Action Expert 下，Orca 在**所有 OOD 设定**上超过 Qwen3.5 w/ AE（Qwen 的 SR 全 0，Orca 实现"从 0% 到有成功"的突破），并与大规模机器人数据预训练的 $\pi_{0.5}$ **相当**。而 Orca 预训练**没用任何 action 标签**，这一步全靠 world latent。
2. **推进更远、卡死更少、恢复更好**：Orca 的 **FNS**（失败前也能到更后阶段）与 **DRR**（progress 掉落后更能纠回）更高——Fig.8 的定性案例是 Scoop Sugar 里 Orca 从多次抓勺失败中恢复并最终推进（DRR 100.0 vs $\pi_{0.5}$ 53.7），Fig.E3–E7 是更多"失败仍具推进性 / 偏差后恢复"的例子。
3. **边界**：SR 绝对值仍很低（Overall **6%**），object OOD 还略输 $\pi_{0.5}$——作者自陈任务 stringent、且当前具身任务"仍偏短偏易"。

### 消融：三个预训练目标（Table 5）

Text/Image/Action 分别是文本 benchmark 均分、PRICE-V0.1、总体 rule-based 动作分（"-"= 该设定不成立；caption 注明前三行按两指标平均、后两行按三指标平均）：

| $\lambda_{\text{obs}}$ | $\lambda_{\text{evt}}$ | $\lambda_{\text{vqa}}$ | Text | Image | Action | Average |
| :---: | :---: | :---: | ---: | ---: | ---: | ---: |
| ✓ | | | 48.4 | - | 10.2 | 29.3 |
| ✓ | ✓ | | - | 58.2 | 30.9 | 44.6 |
| ✓ | | ✓ | 50.5 | - | 32.6 | 41.6 |
| | ✓ | ✓ | 50.1 | 54.7 | 23.0 | 42.6 |
| ✓ | ✓ | ✓ | **51.8** | **59.8** | **32.4** | **48.0** |

**怎么读**（这是全文分工最清楚的一张）：
- **三目标联用最均衡**（Avg 48.0），且 Text/Image/Action 三项同时拿到各自最高——三目标从自然动力学、语义条件、语言监督三个角度共同约束 world latent。
- **$\lambda_{\text{obs}}$ 对动作最关键**：只要加上它，动作分明显上去（连续视频的 dense 自然动力学给了时序变化/物体运动/局部物理交互，这些对真实动作最有用）。
- **$\lambda_{\text{evt}}$ 是视觉 readout 的关键监督**：图像预测需要"在语义条件下推目标状态"，$\lambda_{\text{evt}}$ 把 language-described event 对齐到视觉状态转移（去掉它的第一、三行 Image 直接"-"）。
- **$\lambda_{\text{vqa}}$ 保住语言接口 + 强化语义 grounding**：单独看它对图像帮不上，但配合两条转移目标能提升整体平衡（去掉 $\lambda_{\text{obs}}$ 的第四行 Action 只有 23.0，明显偏低）。

## 图表索引与讲解

（本文 arxiv source 未导出可嵌的内容图，下表据 caption/正文重建"证明什么"。）

| 图 / 表 | 读图重点 = 证明什么 | 关联问题 |
| --- | --- | --- |
| Figure 1 | Encoder-Decoder 总览：Encoder 用 unconscious+conscious 学 world latent，冻结后只训 modality-specific decoder 读出 text/image/action。 | 一个冻结 latent 能否同时喂好三条下游。 |
| Figure 2 | Encoder 的三子过程：observation-only / event-conditioned 转移 + VQA 应答。 | 两个学习范式在一个 VLM 里怎么落地。 |
| Figure 3 | 预训练数据三件套：Video（ego/exo/action-free/natural）+ Event（coarse/fine）+ VQA，各支撑哪个目标。 | 三目标的监督分别从哪类数据来。 |
| Figure 4 | 三 readout 架构：LM head / SD3.5+LoRA / DiT Action Expert；backbone 冻结（❄）、只 readout 可训（🔥）。 | "只训 readout"如何在三模态统一实现。 |
| Figure 5 | 0.8B/4B 的总 loss 随数据持续下降、4B 更低。 | 范式是否 effective & scalable（Q1.1）。 |
| Figure 6 | text/image/action 三 readout 随预训练数据同步提升；动作无标签仍涨。 | 更强 latent 是否→更强 readout（Q1.2）。 |
| Figure 7 | 图像预测定性：baseline 有幻觉手/瞬移物/不遵指令，Orca 保住形态/一致/接触/指令。 | Orca 是"更贴状态"还是"更会画"。 |
| Figure 8 / E3–E7 | 失败轨迹仍具推进性（高 FNS）、偏差后恢复更强（高 DRR）的真实案例。 | Orca 的动作优势体现在过程哪一段。 |
| Figure A1 | 概念图：从 passive task-driven（next-token/frame/action）到 active world learner（next-state）。 | 全文范式主张的一图化。 |
| Figure C1 | learnable query 实现：Query1/Query2 的 hidden state 过 MLP 预测 latent，GT 过冻结 ViT teacher forcing。 | 状态预测头如何挂到 VLM 上。 |
| Table 1 / 2 | 文本：Orca-4B Avg 51.8 居首；能力聚合下 State Transition +12.27%、Dynamic Motion +8.52% 最突出。 | Orca 强在"状态演变"而非静态识别/空间。 |
| Table 3 | 图像：Orca-4+2B Avg 59.8±10.9（avg 最高、std 更小），最严 judge Gemini 上 44.0 远超 FLUX.2。 | latent 是否含"未来视觉状态"的预测信息。 |
| Table 4 / E3 | 动作：Overall rule-based 32.4 > $\pi_{0.5}$ 29.4；env OOD 36.6 最高，object OOD 略输 $\pi_{0.5}$。 | 无 action 标签的 latent 能否迁移到真实动作。 |
| Table 5 | 三目标联用 Avg 48.0 最均衡；obs↔动作、evt↔视觉、vqa↔语言接口。 | 每个预训练目标各管哪条下游。 |
| Table C1–C3 / D1 | 训练超参（4B/0.8B、256 query、10,844 步）+ readout 设置 + 吞吐 0.66→2.91（4.4×）。 | 复现所需的规模与工程细节。 |

## 和你的论文库中其他条目的关系

- 对 [[@zhang2026qwen-robotworld]]（language-conditioned video world model）：两者都用"语言条件 + 视频"学世界演化，但**建模目标不同**。Qwen-RobotWorld 预测**未来视觉轨迹（像素/帧）**、把语言当统一动作接口；Orca 明确主张"不做 next-frame"，只在**冻结 vision encoder 的 latent 空间**预测下一状态，像素交给外挂 SD3.5。可对照"world model 到底该输出帧还是输出 latent state"。
- 对 [[@gao2026fast-leworldmodel]]（JEPA 式 pixel→latent rollout 加速）：Orca 的 observation-only 转移与 JEPA 系的 latent prediction 同源（related work 明确把 V-JEPA / LeWorldModel 列为最近亲）。差别是 Orca 把 latent 预测从"自监督视觉表示"扩展成"含 implicit dynamics + explicit condition、且双向（$\Delta\gtrless0$）的 world-state 转移"，并强行加了语言/动作 readout。适合对照"latent world model 是纯视觉表示，还是要接语言条件与动作"。
- 对 [[@gigaworld2026roadmap]]（robot policy evaluation 的 world model 工程栈）：GigaWorld 侧重"world model 作为策略评估器/仿真器"的训练-推理-评测生态；Orca 侧重"world latent 作为下游 readout 的通用接口"。两者可拼成"世界模型的两种用法：评估 vs 通用表示"。此外 Orca 的 related work 提到 GigaWorld-Policy（action-centric world action model），是同一 world-action 谱系的近邻。
- 对 [[@wang2026wvm]]（World Value Model）：两者都在追问"world model 除了生成画面还能干什么"。WVM 把 world model 的时间/未来能力用于**给数据/任务进展打价值分**；Orca 把它用于**学一个可读出 text/image/action 的统一 latent**。有意思的是 Orca 的动作评估直接用了 PRM-as-a-Judge 系列，与 WVM 的"价值/进展评分"是同一评测思路的两个面。
- 对 [[@wu2026tactile-wam]]（触觉 world-action model）：**互为镜像**。Tactile-WAM 论证"视觉未来只是部分世界状态，必须补上局部接触动力学"；而 Orca 在 §5 局限里**主动承认**"目前只有 vision+language、缺 tactile/force，很多状态转移（接触、滑移、是否抓牢）要靠触觉才感知"。可以把 Tactile-WAM 读成"Orca 局限第 1 条的一个具体补丁"，把 Orca 读成"Tactile-WAM 缺的那个通用底座"。
- 对 [[@li2026zr0]]（VLA 的 dense embodied CoT 监督）、[[@zhou2026holoagent0]]（3D 空间记忆的具身 agent）：Orca 处在更底层的"world latent + Action Expert"，而 zr0 偏动作层的推理监督、HoloAgent-0 偏 agent 层的空间记忆/规划——可作"从高层 agent 规划 → VLA 动作表示 → world latent"的纵向串读。
- 论文自身引用的近亲（**均不在当前库**，如需可另行入库）：V-JEPA 2.1、Emu3 / Emu3.5、DreamZero、Motus、Being-H0.7、Cosmos-Policy、GigaWorld-Policy、$\pi_{0.5}$、GR00T、PRM-as-a-Judge、FlagScale。

## 可追问点

1. **"general world foundation model"的 claim 有多硬**？目前只落到 vision+language、三 readout，且动作真实 SR 仅 6%、object OOD 还略输 $\pi_{0.5}$。这个"general"更像**范式声明**还是**能力事实**？
2. **ViT 空间监督的天花板**（作者自陈局限 2）：latent 被对齐到 VLM 语义空间。那 Orca 学到的"状态"到底是"世界物理状态"还是"VLM 眼中的语义状态"？如果换更弱/更强的 vision encoder，Table 2 的 State Transition 优势还在吗？
3. **无 action 标签却能涨动作**（Answer 1.2）是核心卖点，但它是否只是"视频里本就隐含大量人手/机械臂操作，等于弱监督的动作先验"？换成纯 natural dynamics（无操作）的视频占比更高时，这个 emergent 还成立吗？
4. **4B 的读出 trade-off**（局限 3）：随预训练进行，语言/图像/动作之间出现此消彼长。这说明单一 world latent 可能容量不足以同时服务三 readout——加大模型能消除，还是 NSP 范式本身的结构性张力？
5. **latent matching 用 0.1 MSE + 0.9 cosine**：极度偏向方向而非幅度。对"需要幅度信息"的状态（如物体位移大小、力度）是否会系统性丢信息？这会不会正是动作 SR 上不去的一个原因？
6. **PRICE-V0.1 的 judge 依赖 MLLM 打分**（Gemini/GPT/Doubao/Gemma4）：judge 之间方差不小（Orca 同一张榜在 Gemini 上 44.0、GPT 上 67.9）。用 MLLM 当 judge 评"物理合理性"，本身是否引入了 judge 的先验偏置？
7. **双向转移（$\Delta<0$ 回溯）**在方法里占一半 $\mathcal L_{\text{evt}}$，但实验几乎没单独评"回溯过去状态"的能力。这条"world model vs future predictor"的关键区别，有没有被验证？

## 我的阅读笔记

这篇最值得记住的是它的**立场**而非某个 SOTA 数字：它把"世界模型"从"能生成漂亮帧的生成器"重新定义成"能建模 state transition 的 latent 学习器"，并用一个很克制的实验设定去证——**backbone 冻结、只训 readout**，从而把"latent 是否通用"变成可测问题。三条 readout（text/image/action）全部在冻结 latent 上成立，尤其"预训练零 action 标签、动作仍靠视频涨起来"这一点，是全文最有想象力的观察。Table 2 的能力聚合也很干净：Orca 赢的恰是 State Transition / Dynamic Motion，而非静态空间——方法主张和证据是对齐的。

但要冷静看边界。**"general"目前是范式意义上的 general，不是能力意义上的**：只两模态、三 readout，动作真实 SR 只有个位数，object OOD 还输给 $\pi_{0.5}$；作者自己一口气列了 8 条局限，其中"ViT 空间监督把 world state 对齐到语义空间""4B 已出现读出 trade-off""125K h 只用了 1/10"三条，直接戳中"这套 latent 到底学到了世界还是学到了 VLM 语义"的软肋。方法上也有明显的启发式味道——latent matching 的 0.1/0.9 权重、损失系数 0.1/0.5/0.4、5:1 采样比，都是手调而非从原理推出，作者也承认"三个 loss 对 NSP 不够一致"。

我会把 Orca 当作**本批世界模型论文的"总坐标系"**：[[@zhang2026qwen-robotworld]] 是"输出帧"的一端、[[@gao2026fast-leworldmodel]] 是"纯视觉 latent rollout"的一端、[[@wu2026tactile-wam]] 是"补触觉物理状态"的一端、[[@wang2026wvm]] 是"world model 用于评估"的一端——而 Orca 试图用"统一 world latent + 多 readout"把它们收进一个框架。它现在更像**一份有说服力的范式宣言 + 一套可复现的探针实验**，而不是一个即插即用的 world model recipe；真正的考验会在"上更多模态、上更大规模、且不再依赖某个预训练 ViT 空间"之后才到来。
