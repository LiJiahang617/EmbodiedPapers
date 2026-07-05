---
tags:
  - bilingual-reading
  - deep-reading
paper: "[[@kang2026x-tokenizer]]"
source_pdf: "[[papers/pdfs/kang2026x-tokenizer.pdf]]"
images: "papers/images/kang2026x-tokenizer/"
image_index: "[[papers/images/kang2026x-tokenizer/index.md]]"
created: 2026-07-05
reading_mode: 生成式精读（逐节读原文 + 读图）
---

# X-Tokenizer: A Multimodal Action Tokenizer for Vision-Language-Action Pretraining

paper:: [[@kang2026x-tokenizer]]
pdf:: [[papers/pdfs/kang2026x-tokenizer.pdf]]
images:: [[papers/images/kang2026x-tokenizer/index.md]]

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| action tokenizer | 动作分词器 | 把连续 action chunk 映射成离散符号，供 VLM-style backbone 自回归预测。本文的核心主张是：它不该只当**压缩器**，而该当**语义接口**。 |
| semantic interface learning | 语义接口学习 | 本文对 action tokenization 的重定义：action token 应作为 **representation-shaping target**，把 high-level vision-language reasoning 与 executable continuous control 连起来，而不是任意的 reconstruction index。 |
| X-Tokenizer | 本文方法 | 一个轻量 **Encoder–SRQ–Decoder** 跨 embodiment 动作分词器，在 2.4M 轨迹 / 2.0B 帧 / 17 个 arm family 上预训练，冻结后作为下游 VLA 的表示塑形监督信号。 |
| SRQ (Semantic Residual Quantization) | 语义残差量化 | 本文核心组件：给标准 RVQ 施加**非对称监督**——第一级 $q_0$ 接受语义监督形成 discrete action language（coarse intent），更深层 $q_1{:}3$ 只做 reconstruction residual（fine detail）。 |
| MAM (Masked Action Modeling) | 掩码动作建模 | BERT 式 masked-prediction，只作用在 top-level 离散码 $c^{(1)}_{1:M}$ 上，逼 top-level 码流“可从自身上下文预测”，从而成为一门内部 **action language**。 |
| VL contrastive alignment | 视觉-语言对比对齐 | 用 InfoNCE 把 encoder 的 pre-quantization latent $h_{1:M}$ 拉向**冻结 Qwen2.5-VL-7B** 的 fused VL 特征空间（global + local 两粒度）。 |
| next-frame VL prediction | 下一帧 VL 特征预测 | 让量化后的 latent $\tilde z_{1:M}$ 去预测 chunk 之后一帧的 VL 特征，给 codebook 注入“动作的**即时物理后果**”这一前瞻信号。 |
| RVQ (Residual Vector Quantization) | 残差向量量化 | 底层量化机制：$Q=4$ 级、每级 $V=2048$ 码字，量化 latent = 各级选中码字之和。标准 RVQ 各级同等监督；SRQ 打破这一对称。 |
| delta action + anchor $o$ | 增量动作 + 锚点 | tokenize 的是相对 chunk 前一刻本体锚点 $o$ 的 per-frame 偏移，而非绝对指令——避免固定 codebook 把容量浪费在与 embodiment 相关的位置偏置上。 |
| mixed discrete-continuous VLA | 混合离散-连续 VLA | 下游部署形态：causal VLM backbone 的 hidden state 同时被离散 token 的 AR loss 监督、被连续 **Flow Matching** expert 消费。X-Tokenizer 只在此处当训练期 scaffold。 |
| Wall-OSS | Wall-OSS（下游 backbone，不在当前库） | 本文用作可控实验台的 hybrid discrete-continuous VLA（RoboTwin 与真机都用它），X-Tokenizer 冻结后替换它的离散动作接口。 |
| FAST | FAST（主对照 tokenizer，不在当前库） | 唯一公开、可比规模的 cross-embodiment BPE 式 reconstruction-only tokenizer，是全文的头号 baseline。 |

## 论文主线

**Figure 1（Overview，本仓库未抽取该图，按原文描述）。** 全图给出 X-Tokenizer 的四模块流水：①**Action Encoder** 把 action chunk 压成 $M$ 个连续 latent；②**SRQ** 把每个 latent 量化成多级离散 token；③**Action Decoder** 重建可执行动作；④**Next-Feature Prediction** 只在预训练用。图右侧还画出 VLM 流：一个冻结的 Qwen2.5-VL 从多视角图 + 指令（"Package the coffee box / Use the right arm..."）抽 VL 特征，作为对齐目标。图的关键注解是 **"Inference uses only modules ①②③; pretraining additionally uses module ④ and the VLM stream."**——这句话把全文最独特的设计点一句讲清：**所有语义监督都在预训练期发生、部署时全部拆掉**，跑在机器人上的只剩轻量 Encoder–SRQ–Decoder 核。

这篇论文的核心问题是：**现代 VLA 要同时利用预训练 vision-language backbone 的语义推理、又要输出精确连续控制，可这两者的表示天生错配**——VLM 在语义结构化的离散 token 上运作，机器人策略最终要吐连续 motor command。Action tokenizer 是搭桥的一条路：把连续 action chunk 变成 VLM 能预测的离散符号。但作者点出：**绝大多数现有 tokenizer 只被设计成压缩模块**——在固定 token 预算下最小化 reconstruction error，于是产出的码只是把几何动作空间切块，**没有和 task semantics / visual context / language-conditioned intent 对齐**。

为什么这在 hybrid discrete-continuous VLA 里格外要命？因为在这类系统里，**离散 action-token 的预测 loss 不只是辅助目标，它还塑造着下游 continuous expert 所依赖的共享 hidden state**。如果 token 目标是任意的 reconstruction index，这条自回归 loss 只会把 VLM 的 hidden state 往“几何码模式”上拉，而不是往“动作相关的多模态语义”上拉——**弱监督甚至侵蚀了 backbone 的 multimodal grounding**。

作者的回答是把 action tokenization 重新表述为 **semantic interface learning**，并给出 X-Tokenizer。它的答案很克制，落在“该往 quantizer 的哪一层放语义”这个层面：**只有第一级 RVQ 接受语义监督**（用 MAM 形成 coarse motion intent 的 action language），**更深层保持 reconstruction-oriented residual**（保住毫米级执行细节）。再叠加两个预训练信号——对齐冻结 VLM 表示的 contrastive alignment、预测下一帧 VL 特征——把语义灌进 codebook。三个辅助头在预训练后全部移除，部署时零额外感知/动力学开销。

阅读时要盯住一句话：**本文的贡献不是“又一个 action tokenizer”，而是“action token 应该被当作监督信号、去塑造 VLM 的 hidden state”**——它把 tokenizer 从“内部动作压缩模块”提升成“可复用的 VLA 预训练语义接口”，而衡量它好坏的指标从 reconstruction 变成了 downstream 的 multimodal grounding 与 long-horizon 表现。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| 把 action tokenization 重构为 **semantic interface learning**（token 是塑造 VLM hidden state 的监督目标，非压缩码）。 | §1、§3.1；下游 co-training Eq.(8)。 | 真机 vs FAST：multimodal grounding +13.5%（75.7→85.9）、long-horizon +8.25（61.0→69.25）。 | 论点清晰、增益方向一致；但“接口”价值高度绑定 Wall-OSS 这一种 hybrid 架构。 |
| 提出 **SRQ** 非对称残差量化：$q_0$ 接语义监督、$q_1{:}3$ 只做 reconstruction residual。 | §3.2、Eq.(2)(3)、App.A.2。 | Fig.5：Layer1 长尾（76.4% 用量、跨 4 个数量级），Layer2–4 近均匀（93.8/99.3/99.8%）；Table 1：full 模型得到单调 PPL 谱 510→700→828→916。 | 有直接 codebook 级证据，是本文最扎实的结构主张。 |
| 三个预训练语义头（**MAM / Align / Pred**）把几何码变成语义码，且部署时全部移除。 | §3.3、Eq.(4)-(7)、App.A.4-A.6。 | Table 1 消融：单个信号都拿不到完整单调谱；Fig.7：部署核 30 tok/chunk、324ms，无额外模块。 | 消融支持“需三头合力”；但代价是 recon ℓ1 相对 FAST +17%。 |
| 单个冻结 X-Tokenizer 跨 embodiment / 跨 backbone 复用。 | §3.4；2.4M 轨迹 / 17 arm families；对齐 7B、被 3B 消费。 | RoboTwin 82.8% Avg（超 π0.5）；joint 5-embodiment 76.2 > single 67.5；真机用 3B backbone 仍取得最佳 aggregate。 | 迁移成立；但 published-baseline 对比非严格受控，作者自己也如此定性。 |

## 摘要与核心贡献

摘要提出的矛盾是：现代 VLA 必须**同时**桥接 pretrained vision-language reasoning 与 precise continuous robot control，可现有 action tokenizer 主要为 **reconstruction** 而离散化，产出的码保住了 motion geometry，却**只给 backbone 提供弱语义监督**。于是作者把 action tokenization **从 mere compression 重新表述为 semantic interface learning**——多模态推理与可执行控制之间的语义接口。

X-Tokenizer 的回答是一个轻量 **Encoder–SRQ–Decoder** 架构，跨多种机械臂 embodiment 提供共享动作接口。其关键组件 **SRQ** 给 residual vector quantization 施加非对称结构：

- **第一级用 Masked Action Modeling (MAM) 训练**，形成捕捉 coarse motion intent 的 discrete **action language**；
- **更深层保持 reconstruction-oriented residual**，保留 fine-grained 细节；
- 再加 **contrastive alignment**（对齐冻结 foundation model 表示空间）与 **next-frame vision-language feature prediction**，把 action token 与多模态语义对齐。

在 **2.4M trajectories（2.0B action frames）** 上预训练后，单个冻结 X-Tokenizer 插入 mixed discrete-continuous VLA，充当 **representation-shaping supervision signal**。摘要给的头号数字：取得 top real-world aggregate 与 strong RoboTwin 2.0 结果；相较 reconstruction-only 的 **FAST**，multimodal grounding **+13.5%**、long-horizon **+8.25**。

> 读原文才对得上的口径：**+13.5% 是相对增益**（VQA 75.7→85.9），**+8.25 是绝对增益**（long-horizon PR 61.0→69.25，均 vs FAST）。App.C.2 里另有一处“59.5→69.25”是相对 **+RVQ(no-aux)** 而非 FAST——两个 baseline 别混。全部数字来自 §4.4 与 App.C.2，引用时注明是 progress-rate（PR，有 partial credit），不是 binary success rate。

作者的实验结论是：**只上多级离散层级（+RVQ no-aux）必要但不充分**——它能抬高 VQA（75.7→79.4），却把 7-task 动作均分从 73.0 拉低到 69.1；**必须再加 MAM/Align/Pred 三个语义头**，才能把 VQA 抬到 85.9、7-task 均分抬到 77.4。

## 按原文 section 逐节精读

### 1. Introduction / 为什么“压缩式 tokenizer”对 hybrid VLA 是弱监督

Introduction 的功能是把“表示错配”这个抽象问题精确到 hybrid VLA 的 loss 结构。作者指出：pretrained VL backbone 在语义结构化的**离散**表示上运作，机器人策略却要输出**连续** motor command；action tokenizer 是搭桥一路，但大多只当压缩模块，产出的码**partition 几何动作空间**、不与语义对齐。

关键洞察在第二段：在 hybrid discrete-continuous VLA 里，离散 action-token 的预测 loss **不仅是辅助目标，还塑造 continuous expert 依赖的共享 hidden state**。若 token target 是任意 reconstruction index，AR loss 只会把 hidden state 拉向 geometric code pattern 而非 action-relevant multimodal semantics。据此作者提出两条“有用 tokenizer”的要求：**(1) 离散码要与 backbone 语义对齐**，使 AR 预测“保住而非侵蚀” multimodal grounding；**(2) 仍要保留足够 low-level 细节**以重建精确动作。现有方法只部分满足——FAST/VQ-BeT/VQ-VLA/FASTer 偏 reconstruction、不显式对齐 VL；ActionCodec 引入 contrastive 但**不锚定冻结 VLM**、也不沿 quantizer 深度分离 intent 与 residual。

**这一节读法**：Intro 没停在“语义对齐好”，而把问题定位到“**沿 RVQ 深度分离 semantic intent 与 execution residual**”这一具体设计选择——后面 SRQ 的每一层监督都对应这里的一句话，可逐一回勾。

### 2. Related Work / action-space 设计与 tokenizer 谱系

功能是把 X-Tokenizer 放进两条谱系。**Action-space 设计**：discrete AR head（继承 VLM token 接口但序列长、有离散化误差）、continuous generative head（平滑精细但与 language-token 训练不直接对齐）、hybrid head（兼具但收益取决于离散分支是否给**语义有意义**的监督）——这正是本文的落点。**Tokenizer 谱系**：reconstruction-oriented（FAST/VQ-BeT/VQ-VLA/FASTer/OAT）保住轨迹几何但不对齐 VL；ActionCodec 往 cross-modal 走但对齐空间是内部学的、不锚定冻结 VLM；并发工作 CLAP（对齐视觉动力学特征）、UniT（把 action/visual/fused 联合嵌入统一 codebook，但推理时强制紧耦合多流编码，作为 plug-and-play 接口不够灵活）。X-Tokenizer 的组合拳是：**asymmetric residual quantization + frozen-VLM contrastive alignment + next-frame VL prediction**，且三者只在预训练用、部署移除。

### 3. Method / 方法

#### 3.1 Overview / 沿 RVQ 深度分离 intent 与 residual

给定 action chunk $a_{t:t+T-1}\in\mathbb{R}^{T\times D}$，tokenizer 定义为一条三段流水：

$$
a_{t:t+T-1}\ \xrightarrow{\;E_\theta\;}\ h_{1:M}\ \xrightarrow{\;Q_\psi\;}\ \tau_{1:M}\ \xrightarrow{\;D_\phi\;}\ \hat a_{t:t+T-1}\tag{1}
$$

$E_\theta$ 把 chunk 编成 $M$ 个连续 latent，$Q_\psi$ 是 SRQ 瓶颈把每个 latent 映成多级离散 token，$D_\phi$ 重建可执行动作。SRQ 把每个 latent $h_i$ 映成 $Q$ 个 codebook 索引，得到离散元组与连续重建：

$$
\tau_i=\big(c^{(1)}_i,\dots,c^{(Q)}_i\big),\qquad \tilde z_i=\sum_{q=1}^{Q} e^{(q)}_{c^{(q)}_i}\tag{2}
$$

预训练优化联合目标：

$$
\mathcal{L}_{\text{pre}}=\mathcal{L}_{\text{rec}}+\lambda_{\text{mam}}\mathcal{L}_{\text{mam}}+\lambda_{\text{align}}\mathcal{L}_{\text{align}}+\lambda_{\text{pred}}\mathcal{L}_{\text{pred}}\tag{3}
$$

**这就是 SRQ 非对称性的落点**：$\mathcal{L}_{\text{mam}}$ 只作用于 top-level 离散码 $c^{(1)}_{1:M}$，$\mathcal{L}_{\text{align}}$ 作用于 pre-quantization latent $h_{1:M}$，$\mathcal{L}_{\text{pred}}$ 作用于量化后 latent $\tilde z_{1:M}$——**只有第一级 RVQ 收到 discrete-level 语义监督，$q>1$ 的深层一律不收**。三个辅助头预训练后移除，只留下 encoder–SRQ–decoder 核，把 expert 轨迹**离线**编成离散 token 去监督下游 co-training；下游策略推理时**不再调用** X-Tokenizer。

#### 3.2 Encoder–SRQ–Decoder 核 / “粗意图 vs 细校正”的双层结构

**Encoder** 把 $T$ 帧 chunk 压成 $M$ 个连续 latent（$M\ll T$，默认 $T{=}64\to M{=}16$，压缩比 $r{=}4$）。关键是 tokenize **delta action**（相对本体锚点 $o$ 的 per-frame 偏移）而非绝对指令：绝对指令 state-dependent、跨 embodiment 变动，会逼固定 codebook 把容量浪费在位置偏置而非可复用运动模式上。用 Perceiver 式网络、$M$ 个可学 query 经 cross-attention 下采样；$m$ 是可学 embodiment token，带一个 CFG-style dropout 的 "none" slot 以对未见 embodiment 更鲁棒。**每个 latent slot 概括一段连贯运动子段——就是下游量化的语义单元。**

**SRQ** 是离散化瓶颈。用 RVQ（$Q$ 级堆叠，Eq.2），但**非对称监督各级**。作者点名标准 RVQ 的病灶：每级都看同一 reconstruction loss，会把所有级推向近均匀使用，**没有哪一级承担可解释的独特角色**（§4.2.2 的 per-level perplexity 实证了这点）。SRQ 的非对称监督对应机器人轨迹天然的两分结构——**coarse motion intent**（机器人在干什么，如"move to the cup"）与 **fine geometric correction**（具体怎么做），各路由进自己的 RVQ 层。

**Decoder** 用 Perceiver IO 式 read-out 从 requantized latent 重建全长 chunk，且刻意保持轻量：大部分建模容量在 encoder 与 SRQ，decoder 只把离散 latent 翻回可执行控制——这限定了离线编码 expert 轨迹的 per-call 延迟。

#### 3.3 三个语义头 / 让 token “语义化”而非“几何聚类化”

作者把三个头对应到“什么让 token 语义化”的三个侧面：**时间可预测性（MAM）**、**与 VL 空间对齐（contrastive）**、**对物理后果的前瞻（next-frame VL）**——分别是 syntactic regularity、semantic grounding、predictive physical consequence。

**MAM.** BERT 式 masked prediction，只作用于 top-level 离散索引 $c^{(1)}_{1:M}$；随机遮一子集 $\mathcal{M}$，小 Transformer 从上下文恢复：

$$
\mathcal{L}_{\text{mam}}=\mathbb{E}_{i\in\mathcal{M}}\Big[-\log p_\theta\big(c^{(1)}_i\mid \tilde c^{(1)}_{1:M}\big)\Big]\tag{4}
$$

要求 top-level 码流“可从自身上下文预测”，就把它变成一门内部 **action language**，同时把深层留给 reconstruction residual。

**VL Contrastive Alignment.** 把 encoder 的 pre-quantization latent $h_{1:M}$ 对齐到冻结 Qwen2.5-VL-7B 抽的 fused VL 特征 $u_{1:M}$（时间池化到长度 $M$）。虽然 $\mathcal{L}_{\text{align}}$ 作用在量化前，但它**重塑 encoder 特征分布**，让语义相似的 chunk 聚拢——第一级 RVQ 的最近邻查找随即继承这一结构，深层吸收残差。两粒度 InfoNCE：

$$
\mathcal{L}_{\text{global}}=-\frac{1}{B}\sum_{b=1}^{B}\log\frac{\exp(\bar h_b\!\cdot\!\bar u_b/\kappa_1)}{\sum_{b'=1}^{B}\exp(\bar h_b\!\cdot\!\bar u_{b'}/\kappa_1)}\tag{5}
$$

$$
\mathcal{L}_{\text{local}}=-\frac{1}{B\,M}\sum_{b=1}^{B}\sum_{i=1}^{M}\log\frac{\exp(h_{b,i}\!\cdot\!u_{b,i}/\kappa_2)}{\sum_{b'=1}^{B}\sum_{j=1}^{M}\exp(h_{b,i}\!\cdot\!u_{b',j}/\kappa_2)}\tag{6}
$$

两方向对称化（CLIP 式），$\mathcal{L}_{\text{align}}=\tfrac12(\mathcal{L}_{\text{global}}+\mathcal{L}_{\text{local}})$。二者互补：**global** 用 across-chunk batch negative 强制 chunk 级“动作段↔指令引导的视觉上下文”对应；**local** 把每个 slot 绑到它 time-aligned 的视觉时刻，与 batch 里全部 $BM{-}1$ 个 (chunk, time) 对比。

**Next-Frame VL Prediction.** 给量化后 latent $\tilde z_{1:M}$ 挂一个小预测器 $G$，回归 chunk 窗口后**紧接一帧**的 VL 特征：

$$
\mathcal{L}_{\text{pred}}=\big\|\,G(\tilde z_{1:M})-u^{+}\,\big\|_1\tag{7}
$$

MAM 与 contrastive 把码 ground 在当前 chunk 与其视觉上下文，这一项则加**前瞻**信号：codebook 被要求编码“动作的即时物理后果”，而非只当前 chunk 的瞬时几何。

> 三个头之外，App.A.7-A.8 还有三条**稳定性正则**（不贡献 codebook 语义）：rotation geodesic loss（$SO(3)$ 测地角，$\lambda_{\text{geo}}{=}0.2$）、DCT frequency-domain ℓ1（压高频抖动，$\lambda_{\text{dct}}{=}0.5$）、temporal smoothness（匹配一阶速度，$\lambda_{\text{smooth}}{=}0.3$）。它们都进 $\mathcal{L}_{\text{rec}}$。

#### 3.4 下游 co-training 与部署 / 训练期 scaffold，推理期消失

X-Tokenizer **不是策略**，而是 hybrid discrete-continuous VLA 的**训练期语义脚手架**。此设定里，causal VLM backbone 与 continuous Flow Matching expert 共享 hidden state $h_{\text{vlm}}$。离散分支以 **position-major raster order**（先在位置 $i$ 出齐全部 $Q$ 级，再到 $i{+}1$）自回归预测 X-Tokenizer 码，连续分支回归动作轨迹：

$$
\mathcal{L}_{\text{co}}=-\sum_{i=1}^{M}\sum_{q=1}^{Q}\log p_\psi\!\big(c^{(q)}_i\mid h_{\text{vlm}},\,c^{(1:Q)}_{<i},\,c^{(<q)}_i\big)+\lambda_{\text{fm}}\,\mathbb{E}_{t,x_t}\!\Big[\big\|v_\phi(x_t,t\mid h_{\text{vlm}})-u^\star_t\big\|_2^2\Big]\tag{8}
$$

离散 loss **正则化共享 hidden state**，Flow Matching 分支保住高保真连续控制。因为 X-Tokenizer 的码在预训练时已对齐 VLM 特征空间，预测它们施加的是**动作语义监督**而非 FAST 那样的 reconstruction-only 词表。**推理时 AR head 与 X-Tokenizer 都被关掉**，策略退化为单次前向的连续 flow 回归器，无离散 token 开销——这就是 §3.1 那句“部署只留三模块核”的兑现。

### 4. Experiments / 实验（见下方分节）

四个研究依次是：多模态对齐分析（§4.1）、codebook 侧 SRQ 专业化/语义头消融/部署鲁棒性与延迟（§4.2）、RoboTwin 2.0 受控基准（§4.3）、四种 action interface 的真机对比（§4.4）。

### 5. Conclusion / 结论与未来

结论重申论点：**为 VLA 预训练设计 action tokenization，应考虑 token 被消费时所处的多模态上下文，而非只当动作压缩优化**。X-Tokenizer 用 SRQ 加三个预训练监督头，把 top-level 码塑成多模态语义、深层保住执行细节；三头预训练后移除，部署仍是轻量核。一次预训练（2.4M 轨迹 / 17 arm families）后单个冻结 tokenizer 可跨下游 VLA 复用、无需 tokenizer 侧重训。两条未来方向：**(1)** 当前把每个 chunk 锚在 end-effector 空间，推广到 dexterous hand / joint-space 需要面对“无 canonical end-effector 锚点”的 embodiment；**(2)** SRQ 深度调度目前固定了 reconstruction–semantics 的静态平衡，可改成随任务自适应。作者还提出一个更宽的猜想：**context-guided compression 或许对 foundation model 与下游预测器之间的其它离散接口（如 world-model latent）也有用**——这是它和世界模型路线的接口。

## 方法细节（Appendix 关键实现）

- **Delta-action 布局（App.A.1，Tab.3）**：$D{=}26$ 通道。左右 end-effector position（3+3，欧氏差分）、左右 6D rotation（6+6，$SO(3)$ 复合）、左右 gripper（2，identity，state-like）、base velocity（3，identity，本身已是时间导数）、lift（1）、head pitch+yaw（2）。逐通道 MinMax 用 0.1%/99.9% 分位做鲁棒归一到 $[-1,1]$。
- **Encoder（App.A.1）**：hidden $H{=}1024$，12 层 Transformer（8 头，FFN 宽 $4H$，dropout 0.1），time 维 RoPE（base $10^4$），$M_{\max}{=}16$ 可学 latent query，可选 state cross-attention。
- **SRQ（App.A.2）**：$Q{=}4$ 级、每级 $V{=}2048$ 码字，EMA 更新（decay 0.8，dead-code reset 阈 2），k-means（100 iter）初始化，**欧氏（非 cosine）**最近邻。
- **MAM head（App.A.4）**：2 层 Transformer，mask 概率 0.15，BERT 式 80% [MASK]/10% 随机/10% 不变；前 10 epoch 关闭、之后 $\lambda_{\text{mam}}{=}0.1$。
- **VL 特征抽取（App.A.3）**：Qwen2.5-VL-7B（bf16 + FlashAttn-2）**离线**抽取存盘，部署永不调用；取 layer $-3$ hidden（比末层的图像 token 空间结构更干净），3 视角（face/left wrist/right wrist），$H_{\text{vl}}{=}3584$；prompt 用 global instruction + current sub-step 两级语言条件。
- **CFG-style dropout（App.A.1）**：state $o$ 以 0.2、embodiment id 以 0.2、额外 0.1 换 "none" slot——部署对缺失 state 与未登记 embodiment 鲁棒。
- **训练调度（App.A.9）**：100 epoch，batch 256，AdamW（lr $5\times10^{-5}$，wd 0.01），chunk 长 $T\in[8,64]$ 均匀采样，cosine schedule。

## 实验

### Setup / 语料、baseline、平台

- **预训练语料（App.B）**：~2.4M 轨迹、~2.0B 有效 action frame，跨 17 arm families（由 54 个 `robot_type` 映射，registry 另声明 ~15 个共享 delta-action 布局但尚未入训练，合计 >70 预定义 embodiment）。来源含 X2Robot 内部数据 + AgiBotWorld/DROID/RoboTwin 2.0/RoboMind/RoboCoin/RoboChallenge/R1Lite/RealOmni/Bridge-V2/Fractal-RT/BC-Z/FurnitureBench/Open-X 子集（Tab.4-5）；各源**不重加权**，按 union 均匀采 chunk。
- **对照 tokenizer**：**FAST**（唯一公开、可比规模的 cross-embodiment tokenizer，头号 baseline）；**RDT2 VQ**（单 codebook VQ-VAE，仅用于 §4.2.3 噪声探针）；**256-bin per-channel uniform**（非学习，仅作 reconstruction-ℓ1 轴锚点）。VQ-BeT/FASTer/ActionCodec 因无可比 checkpoint 或架构不兼容而未直接跑（App.B.3）。
- **下游 backbone**：**Wall-OSS**（hybrid discrete-continuous VLA）。RoboTwin 用全自由度（dual arms/base/lift/head）released checkpoint 微调 70k 步；真机用 Qwen2.5-VL-3B backbone（**注意 X-Tokenizer 预训练对齐的是 7B、这里被 3B 消费——一次 cross-backbone transfer 测试**）。

### §4.1 与 VLM 的多模态对齐

三个视角验证 action latent 是否与消费它的 VLM 处于同一流形：

- **§4.1.1 统计（Fig.2）**：Fig.2a 的 $16\times16$ slot 级 cosine 热图有清晰对角带、**mid-chunk 峰值 ~0.60**，边界处（VL 上下文不全）减弱；Fig.2b 的 arm-family 矩阵对角一致为正、**中心在 corpus mean 之上 ~0.05**，形态相近的臂之间还有亮的 off-diagonal block。
- **§4.1.2 几何（Fig.3，UMAP）**：(a) action 特征按 embodiment 聚簇；(b) 同 chunk 的 VL 特征跨臂交错；(c) 叠加两模态时占据**同一片共享区域**而非分成两簇——对齐头把 action 与 VL 拉进共享空间，又保住 task/embodiment 级变化。
- **§4.1.3 功能替换（Fig.4）**：把 fused VL 特征直接灌进同一 SRQ-decoder 栈。VL 驱动路线**保住动作方向**（per-task cosine **0.85–0.95**，vs action-encoded 的 ≈0.99），但 $L_1$ 误差更大，且**在 insert/plug、press/button 这类精细 pre-contact 任务上差距最大**——说明 VL 特征抓的是 high-level motion family，action encoder 保的是毫米级执行几何。标准 action-only tokenizer（FAST/RDT-VQ）根本没有这条 VL→codebook 通路。

### §4.2 Codebook 结构与部署属性

**§4.2.1 SRQ 专业化（Fig.5）**：SRQ 四级出现明确分工——**MAM 正则的 Layer 1 明显长尾**（少量高频"motion word"覆盖大多数 chunk，token 频率跨 4 个数量级，仍保 **76.4%** codebook 活跃）；Layer 2–4 只被 reconstruction 监督，**填得更均匀（93.8/99.3/99.8%）**，充当 residual correction 码。这条 Zipf-vs-uniform 对比正是 SRQ 想要的，且**没有任何一级出现 action VQ 常见的灾难性坍缩（<10% 活跃）**。

**§4.2.2 语义头消融（Table 1）**：报告 reconstruction ℓ1（Δ% vs FAST）与 per-level RVQ perplexity（$q_0$ 越低=intent 越集中，深层越高=residual 越广）。

| Method | Recon ℓ1 ↓ | Δ% vs FAST | PPL $q_0$ ↓ | $q_1$ | $q_2$ | $q_3$ ↑ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FAST | 0.01446 | – | – | – | – | – |
| 256-bin uniform | 0.00486 | −66% | – | – | – | – |
| No aux | 0.00815 | −44% | 751 | 693 | 756 | 757 |
| w/o Align+Pred | 0.00830 | −43% | 687 | 904 | 853 | 793 |
| w/o MAM | 0.01564 | +8% | 603 | 677 | 830 | 871 |
| **X-Tokenizer (full)** | 0.01693 | +17% | **510** | **700** | **828** | **916** |

**要点**：没有单一信号能给出完整模式——**MAM 单独能压 $q_0$ 但不组织深层残差；Align+Pred 单独改善深层排序但缺最强 main-code 压缩**。只有 full 模型产出想要的**单调 PPL 谱 510→700→828→916**，代价是 recon ℓ1 相对 FAST **+17%**。作者直言这是 intended trade-off：256-bin 重建最好但**无学到的语义结构**，而下游 §4.3-4.4 吃的正是 SRQ 诱导的结构。

**§4.2.3 噪声鲁棒性与延迟**：向物理动作空间注入小高斯噪声（归一化/tokenize 前），同一 noisy chunk 喂所有 codec，报 Word Error Rate（WER，越低越好，Table 2）。

| $\sigma$ | X-Tokenizer(ours) | FAST | 256-bin | RDT2 VQ |
| --- | ---: | ---: | ---: | ---: |
| 0.004 | **0.313** | 0.313 | 0.454 | 0.325 |
| 0.006 | **0.437** | 0.899 | 0.533 | 0.439 |
| 0.008 | **0.526** | 1.445 | 0.597 | 0.549 |

X-Tokenizer 在各噪声级 WER 最低；**FAST 一旦扰动触发 BPE 重分段就急剧退化**（0.899、1.445）。但 raw WER 说不清“edit 落在哪”，这正是 Fig.6 三张图要回答的：

![[papers/images/kang2026x-tokenizer/noise_code_probe_token_strip_chunk02_v3_2_full.png|760]]

**读图重点（X-Action Tokenizer 面板）：证明 SRQ 把物理噪声挤进低级残差、保住 top-level intent。** 24 token 定长，每 4 格一组，**每组第一格（深黑边框）= 最粗的 $q_0$**。看行内变化：绝大多数组的 $q_0$ 码在 Clean→σ=0.002→0.004→0.006 全程**稳定**（如 1868、1868、946、946、946 保持不变），红圈标出的 substitution 主要落在 $q_1{:}3$（组内第 2-4 格），只有个别组（第 3 组 1215→946）在最高噪声下才动到 $q_0$。这直接兑现 §4.2.3 的论断：**$q_0$ 的粗动作标签在小扰动下不翻转，改的是执行残差**——因为下游 AR 分支拿这条码流当 VLM hidden state 的监督，$q_0$ 翻转会改变 backbone 看到的“粗动作语义”，$q_1{:}3$ 翻转只改残差细节。

![[papers/images/kang2026x-tokenizer/noise_code_probe_token_strip_chunk02_fast.png|760]]

**读图重点（FAST 面板）：证明 BPE 变长编码在噪声下会重分段、爆发大量增删。** 顶行 Clean 是一条长序列（265 1605 523 …，已比 X-Tokenizer 的 24 长得多）；σ=0.002 时只零星 substitution（红圈），但 **σ=0.004/0.006 时序列被重新分段**——出现蓝色 insertion 与成串红色 substitution，序列长度改变。这解释了 Table 2 里 FAST 的 WER 为何在 σ=0.006 直接跳到 0.899：**它的失效是“语义级 token flip + 长度突变”，而非局部残差修正**。

![[papers/images/kang2026x-tokenizer/noise_code_probe_token_strip_chunk02_rdt2_vq.png|760]]

**读图重点（RDT2 VQ 面板）：证明单 codebook 定长 VQ 的替换“无结构地散布全序列”。** RDT2 VQ 长度固定（不像 FAST 会变长），但 substitution（红圈）**随噪声大致成比例地散落整条序列**——因为**单一 codebook 不分离 intent 与 residual**，任何一格被改都同等地改变监督信号。三图并读的结论：X-Tokenizer 的鲁棒**不只体现在 edit 数少，更体现在“把小物理噪声转成低级修正、而非语义 token 翻转”**——这是 SRQ 层级结构独有的性质。

**延迟（Fig.7）**：训练输入长度 tokens/chunk——FAST **156**、RDT2-VQ **27**、X-Tokenizer **30**；推理延迟（LM-tokid→action，ms）——FAST **332**、RDT2-VQ **758**、X-Tokenizer **324**。X-Tokenizer 只测**移除三个预训练头后的部署核**，即“语义监督不带来部署期额外模块”。

### §4.3 RoboTwin 2.0 基准

用 Wall-OSS hybrid 架构，附冻结 X-Tokenizer，全自由度微调 70k 步；50 dual-arm 任务，每任务 50 Clean + 500 Randomized demo，各任务 100 rollout，Easy/Hard 双协议。

**Fig.8（50 任务 dual-arm，%）**：

| 方法 | Easy | Hard | Avg |
| --- | ---: | ---: | ---: |
| π0 | 65.9 | 58.4 | 62.1 |
| π0.5 | 82.7 | 76.8 | 79.8 |
| X-VLA | 72.9 | 72.8 | 72.8 |
| **Wall-OSS + X-Tokenizer** | **84.7** | **80.9** | **82.8** |

Wall-OSS+X-Tokenizer 取得最佳 aggregate，且 **Hard randomization 下增益更大**——暗示对齐的 action-token 接口在**视觉条件漂移时最有用**。作者诚实说明：published baseline 在 backbone/预训练数据/算力上各异，这是 **benchmark comparison 而非受控 ablation**。（App.Tab.6 给出逐任务成功率，从 adjust_bottle 100/100% 到 hanging_mug 31/20%、turn_switch 45/38% 不等，均分 84.7/80.9%。）

**Fig.9（cross-embodiment，70k，%）**：在 5 个单臂 embodiment 上，比较“5 个独立单臂模型”与“1 个 union 联合模型”。

| | Easy | Hard | Avg |
| --- | ---: | ---: | ---: |
| Single-embodiment | 70.9 | 64.0 | 67.5 |
| **Joint (5-embodiment)** | **77.9** | **74.4** | **76.2** |

联合训练把 Easy 70.9→77.9、Hard 64.0→74.4，**Hard 增益更大**，与 Fig.2b 的 arm-family 对齐一致——共享 action-token 空间能跨 embodiment 复用运动结构。作者也提醒：联合训练带来的数据多样性也可能贡献增益，**不单独归因于 tokenizer**。

### §4.4 真机评估（最关键的受控对比）

7 个桌面任务（5 短程操作 + 2 长程推理），同一 Wall-OSS 测试台、**四种 action interface**：原 Wall-OSS flow head、FAST、+RVQ(no-aux)（reconstruction-only 4 级 RVQ）、full X-Tokenizer。四者共享同一 Qwen2.5-VL-3B backbone 初始化/数据/调度/Flow Matching expert/评估协议，**只换 action interface**；X-Tokenizer 冻结自 26-D 预训练 checkpoint。每任务 10 rollout，用 stage-wise progress-rate（PR，有 partial credit）打分；VQA 用 107 个 held-out point-grounding 样本（预测点落在 GT mask 内算对）。

**X-Tokenizer 取得最佳 aggregate**：**85.9% VQA**、**80.6% PR**（5 短程操作）、**69.3% PR**（2 长程）、**77.4% 平均 PR**（全 7 任务）。

**关键的 +RVQ(no-aux) 消融**：相对 FAST，它把 VQA 抬高（75.7→79.4），却把 7-task 动作均分**拉低**（73.0→69.1）——**说明“多级离散结构”本身只帮到 backbone 表示、不足以保证动作质量**。再加 MAM/Align/Pred 才两头都涨到 85.9% VQA、77.4% 均分。逐任务趋势一致：X-Tokenizer 在“操作 + 视觉 grounding / 多步指令跟随”的任务上最强，在**重复低级摆放**的任务上增益小——**主要回退出现在 distribute-blocks-by-color**（stage credit 高度依赖低级摆放精度），与 §4.2.2 的 reconstruction trade-off 一致。

（Fig.10 逐任务：Pick-Up-Cup、Push-Towel、Distribute-Blocks、Stack-Bottle、Place-Tape 为短程；Arrange-Flowers、Turn-On-Light-Switch 为长程。真机监督每任务 ~500 遥操轨迹（合 ~3.5k），并混入 ~480k grounding 样本占每 batch 25%。）

## 图表索引与讲解

| 图 / 表 | 读图重点=证明什么 | 关联问题 |
| --- | --- | --- |
| Figure 1（未抽取） | 四模块流水；核心注解“推理只用①②③，预训练额外用④+VLM 流”。 | 语义监督为何是“训练期加、部署期减”。 |
| Figure 2 | (a) slot 级 cosine 对角带 mid-chunk 峰值 ~0.60；(b) arm-family 对角正、中心 +0.05。 | action latent 是否真活在 VLM 流形里。 |
| Figure 3（UMAP） | action 按 embodiment 聚簇、VL 跨臂交错，叠加占同一共享区。 | 对齐是“同空间”还是只是“图上邻近”。 |
| Figure 4 | VL 直接驱动 SRQ-decoder：cosine 0.85–0.95、L1 更大，insert/press 差距最大。 | 对齐是否“功能可用”而不止统计相似。 |
| Figure 5 | Layer1 长尾（76.4%）、Layer2–4 近均匀（93.8/99.3/99.8%），无坍缩。 | SRQ 非对称是否真在 codebook 级分工。 |
| Figure 6（3 面板，已嵌入） | X-Tok 把噪声挤进 $q_1{:}3$、保住 $q_0$；FAST 重分段爆增删；RDT2 VQ 替换散布全序列。 | 鲁棒性是“少改”还是“不改语义 token”。 |
| Figure 7 | 部署核 30 tok/chunk、324ms；FAST 156/332，RDT2 27/758。 | 语义监督是否带来部署开销。 |
| Figure 8 | RoboTwin dual-arm Avg 82.8 > π0.5 79.8，Hard 增益更大。 | 对齐接口在视觉漂移下是否更有用。 |
| Figure 9 | Joint 76.2 > Single 67.5，Hard 增益更大。 | 共享 token 空间能否跨 embodiment 复用。 |
| Figure 10 | X-Tok 4-变体中最佳（VQA 85.9、7-task 77.4）；回退在 distribute-blocks。 | 语义头到底帮了 grounding/长程还是动作精度。 |
| Table 1 | 单信号拿不到单调 PPL 谱，full 得 510→700→828→916，代价 recon +17%。 | 三个语义头是否缺一不可。 |
| Table 2 | X-Tok WER 最低；FAST σ=0.006 跳到 0.899。 | 谁在小物理噪声下更稳。 |

## 和你的论文库中其他条目的关系

- 对 [[@li2026zr0]]（ZR-0，VLA reasoning/推理监督）：**互补性最强的一对**。X-Tokenizer 解决“**action token 怎么表示、怎么当监督塑造 hidden state**”，ZR-0 解决“**reasoning supervision 怎么给**”。两者可拼成一套 VLA training stack 的两类模块——一个在动作接口侧、一个在推理监督侧；都在追问“离散监督信号如何不侵蚀 multimodal grounding”。
- 对 [[@wu2026tactile-wam]]（Tactile-WAM，触觉世界-动作模型）：**共享同一元问题——某个信号该被放在计算图的哪个位置**。Tactile-WAM 问“触觉该沿哪条 attention 路径注入”，X-Tokenizer 问“语义监督该放在 RVQ 的哪一层”；两者都用“非对称结构”作答（前者 asymmetric attention，后者 asymmetric residual quantization），且都强调“加了信号反而变差”的失败模式（tactile pollution vs +RVQ(no-aux) 掉动作分）。这条“**非对称注入**”的对读很值得做。
- 对 [[@wang2026wvm]]（World Value Model）、[[@wang2026orca]]、[[@zhang2026qwen-robotworld]]、[[@gao2026fast-leworldmodel]]、[[@gigaworld2026roadmap]]（世界模型/latent 建模路线）：X-Tokenizer 的结论里明确留了接口——“**context-guided compression 或许对 world-model latent 这类离散接口也有用**”。可对照“**离散 latent 是被当作 value / world-state / action supervision**”这一分类：WVM 把世界模型未来能力用于*评估*，世界模型路线用于*预测未来状态*，X-Tokenizer 用于*塑造动作监督*。
- 对 [[@zhou2026holoagent0]]（空间记忆与智能体）：处在更高的 agent/记忆层，与 X-Tokenizer 的“底层动作接口”是纵向互补，可作“从高层规划到 token 级动作监督”的串读。
- 论文自身的近亲（**均不在当前库**，如需可另行入库）：**FAST**（头号 reconstruction-only baseline）、**RDT2 VQ**、**VQ-BeT**、**FASTer**、**OAT**、**ActionCodec**、并发的 **CLAP** 与 **UniT**（unified action tokenizer）、下游 backbone **Wall-OSS** 与对照策略 **π0 / π0.5 / X-VLA**、VL 抽取器 **Qwen2.5-VL**。

## 可追问点

1. Recon ℓ1 相对 FAST **+17%**、相对 256-bin **+248%**（0.00486→0.01693）。作者说“下游吃的是结构不是重建”，但 distribute-blocks 的回退恰恰是精度问题——**在更依赖毫米级摆放的任务上，这个 reconstruction 代价会不会成为硬上限**？
2. cross-backbone transfer 只测了“7B 对齐→3B 消费”**一个方向**。若换成更弱/更强的 backbone、或非 Qwen 系，语义对齐是否还迁移？对齐目标绑定 Qwen2.5-VL 到底有多深？
3. SRQ 只让 **$q_0$** 接语义监督、$q_1{:}3$ 纯 reconstruction。深度调度是**静态**的（作者自己列为未来工作）。任务复杂度差异大时，固定“1 级语义 + 3 级残差”是否最优？自适应深度会不会改变结论？
4. RoboTwin 的 π0/π0.5/X-VLA 对比是 published baseline（backbone/数据/算力各异），作者定性为“非受控”。**唯一严格受控的是 §4.4 的四 interface 真机对比**（只换接口）——那么 RoboTwin 的 82.8% 到底多大程度归功于 X-Tokenizer、多大归功于 Wall-OSS backbone？
5. 三个语义头的权重（$\lambda_{\text{mam}}{=}0.1$、$\lambda_{\text{align}}{=}0.5$、$\lambda_{\text{pred}}{=}0.2$）与 MAM 10-epoch warm-up 都是启发式。Table 1 只给了“全有/去 MAM/去 Align+Pred/全无”四档，**没有逐头单独 on/off 的完整 $2^3$ 网格**——三头的边际贡献能否进一步拆清？
6. 噪声鲁棒性用的是**注入高斯噪声后的 WER**，属合成扰动。真实部署的动作噪声（传感器抖动、遥操漂移）分布不同——“$q_0$ 不翻转”的性质在真实噪声下是否同样成立？

## 我的阅读笔记

这篇的真正价值不在“又一个 action tokenizer”，而在它把问题从“**tokenizer 重建得多准**”重构成 **“tokenizer 作为监督信号，把 VLM 的 hidden state 塑造成什么样”**。它的答案很有结构感：**沿 RVQ 深度分离 semantic intent 与 execution residual**，只给最粗那一级上语义监督（MAM + VL 对齐 + 前瞻），其余留给重建。Table 1 那条“**单调 PPL 谱 510→700→828→916**”和 Fig.6 那张“**$q_0$ 在噪声下不翻转、edit 挤进 $q_1{:}3$**”，是全文最有说服力的两击——它们把“非对称监督真的在 codebook 里产生分工”从一句主张变成了可测现象。§4.4 的 +RVQ(no-aux) 消融也很关键：它证明“**多级离散结构本身只帮 VQA、不足以保动作质量**”，从而把语义头的必要性钉死。

但要清醒看边界：**最干净的因果只在 §4.4 那组“只换接口”的真机对比里**；RoboTwin 的 82.8% 是 benchmark comparison，backbone/数据/算力都不受控，作者自己也这么说。增益结构也偏科——**在“操作 + grounding / 多步指令”上强，在重复低级摆放上（distribute-blocks）反而回退**，这与 recon ℓ1 相对 FAST +17% 的代价是一体两面。方法里三头权重、MAM warm-up、SRQ 深度都是启发式/静态的，作者把“自适应深度调度”明确留给未来。

我会把它作为 **“action token 如何作为语义监督进入 VLA 训练栈”** 这条线的入口，和 [[@li2026zr0]] 交叉读（一个管动作接口、一个管推理监督），再和 [[@wu2026tactile-wam]] 做“**非对称注入**”的方法学对读——两篇都在回答“某个信号该放在计算图的哪个位置、以及无差别注入为什么会变差”。等世界模型侧的条目深读后，再回看作者结尾那句“context-guided compression 对 world-model latent 也许有用”能否成立。
