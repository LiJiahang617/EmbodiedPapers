---
tags:
  - bilingual-reading
  - deep-reading
paper: "[[@wang2026wvm]]"
source_pdf: "[[papers/pdfs/wang2026wvm.pdf]]"
images: "papers/images/wang2026wvm/"
image_index: "[[papers/images/wang2026wvm/index.md]]"
created: 2026-07-05
reading_mode: 生成式精读（逐节读原文 + 读图）
---

# World Value Models for Robotic Manipulation

paper:: [[@wang2026wvm]]
pdf:: [[papers/pdfs/wang2026wvm.pdf]]
images:: [[papers/images/wang2026wvm/index.md]]

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| generalist value model | 通用价值模型 | 从大规模、混合质量机器人数据里为每帧估计"任务进展/价值"，给 RL 与离线数据筛选提供学习信号；本文靶心。 |
| task progress $v_t=t/T$ | 任务进展 | 把 value 归一化成"当前帧 / 总长度"。在 sparse-reward（非终止 −1、完成 0）下，$V(o_t)$ 退化为负的"到目标距离"，于是 **value estimation ≡ task-progress prediction**，天然朝向未来。 |
| World Value Model, WVM | 世界价值模型 | 本文方法：把**预训练视频 world model** 当价值学习的骨干，让 value 流去读世界模型的时空 latent。 |
| Mixture-of-Transformers, MoT | 混合 Transformer 耦合 | 视频 DiT + 轻量 value DiT 两条流，通过多模态 self-attention 逐层耦合；value token 读视频 latent，但**视频 token 从不读 value**（非对称）。 |
| asymmetric attention mask | 非对称注意力掩码 | 关键结构先验：value→video 允许、video→value 禁止，保护预训练视频流不被 value 任务干扰（借自 Fast-WAM [72]）。 |
| distributional value chunk | 分布式价值块 | 不预测单个标量，而是预测长度 $h$ 的**逐帧价值序列**（分布），用 flow matching 训练——密集监督 + 表达力强。 |
| flow matching | 流匹配 | 本文 value/video 两条流共用的生成式训练目标：学速度场 $y-\epsilon$，推理用 Euler 求解器**单步**去噪即可。 |
| prefix randomization $p$ | 前缀随机化 | 防捷径正则：以概率 $p$ 把 overlapping chunk 的前缀 value 换成随机标量，逼 value 流靠视觉证据而非前缀外推。 |
| video rewinding | 视频回放增强 | 借 ReWiND：把专家片段按 rising/plateau/descending 三种时序模式重排（保留/重复/反转帧），造出停滞与回撤的非单调进展监督。 |
| VOC (Value-Order Correlation) | 价值序相关 | GVL 提出的指标，衡量预测 value 与真实时间序的单调相关；**只对专家（单调）轨迹有意义**，测不了 suboptimal 段。 |
| Suboptimal-Value-Bench | 次优价值基准 | 本文新基准：800 条 human-verified 轨迹、3 embodiment、15 任务，专测 **hesitation（停滞）+ retry（回撤）** 两类次优行为。 |
| Hesitation-RMSE / Retry-VOC | 停滞 RMSE / 回撤 VOC | 两个新指标：停滞段真值恒定→用 RMSE 罚"漂移"；回撤段真值单调下降→把 VOC 限制到下降窗口，考"能不能跟住掉分"。 |
| π0.5-base | π0.5 基座策略 | 下游策略学习的基础 VLA，用 WVM 的 value 做 Filtered BC / AWR 加权微调。 |

## 论文主线

**Figure 1（Overview，无独立图片文件，据正文 caption 转述）**：左侧是三套自采数据（AgileX Mixed 200、ARX Dual Arms 300、RoboSuite Single Arm 300）经 World Value Model → 输出 $V_{t-h+1:t}$，能在视频里**检测 retry 与 hesitation**；右侧 Suboptimal-Value-Bench 上，WVM 相对 baselines 把 **Retry-VOC 抬高、Hesitation-RMSE 压低**；最右两组柱图是把 WVM 接入下游后，**仿真与真实的 policy improvement**（Filtered BC 明显高于 vanilla BC）。这张图一眼给出全文的因果链：**世界模型 → 更好的 value → 更好的数据筛选 → 更好的策略**。

这篇论文的核心问题是：**做机器人 generalist value model，最缺的能力是"时间理解"**。准确估值在数学上要同时具备两件事——用历史上下文 ground 当前信念（past grounding），并对长期未来结果做前瞻规划（future planning）。而现有机器人 value model 绝大多数建在 **VLM backbone** 上，VLM 预训练看的是静态或时间稀疏的图像，天生缺时间建模。作者据此点名现有 value model 的三个瓶颈：(1) 重度依赖**标量 value 监督**导致样本低效、预测脆弱；(2) 窄任务定制导致泛化差；(3) VLM 的稀疏视觉建模导致时间理解/未来规划受损。

作者的关键洞察很干脆：**world model 天生擅长时间动力学与未来预测，正好是 value 估计需要的双重能力**——所以不必再从 VLM 硬补时间，而应把预训练视频 world model 里的时空先验**直接改造成 value 学习的地基**。这就是 World Value Model（WVM）：用 Wan2.2 的视频 VAE + 视频 DiT 作世界建模流，旁挂一条**轻量 value DiT**，两条流用 **MoT 非对称注意力**耦合——value token 去读视频 latent，视频 token 绝不回读 value，从而在借用世界模型时空表示的同时**不破坏视频生成流**。

第二个设计支点是把 value 从"标量回归"升级为 **distributional value chunk**：一次预测长度 $h$ 的逐帧 value 序列，用 **flow matching** 训练。这既给了密集训练信号，又能表达 plateau（停滞）/regression（回撤）这类**局部进展形态**——而这正是标量回归看不见的东西。

阅读时要盯住一句话：**本文的贡献不是"再训一个 reward/value 模型"，而是论证"value 该长在世界模型上、且该被建成分布式进展块"**。全篇最锋利的一击在 §5.3 消融——把视频权重**冻结**会让 Retry-VOC 崩到 0.45，说明起作用的不是"用了个世界模型当特征器"，而是"**世界模型必须持续 co-train**"。第二锋利处是 prefix 随机化揭示的现象：关掉它，Expert-VOC 反而**升到 0.98**，但 suboptimal 指标全线变差——这暴露出 **Expert-VOC 单独用是不够的**，一个模型可以靠前缀捷径"刷单调性"，却完全测不出它会不会跟踪回撤。这也正是 Suboptimal-Value-Bench 存在的理由。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| 把预训练 **world model 改造成 value 学习骨干**，用其时空先验取代 VLM。 | §3.1 Eq.(3)、§3.2 MoT 非对称耦合。 | Table 3 Expert-VOC 均值 0.95 vs 最强 baseline 0.88；消融"冻结视频"→Retry-VOC 崩到 0.45（Table 4）。 | 概念清晰、消融直接支撑"必须 co-train"，是最扎实的一环。 |
| WVM 是**首个把 value 建成 distributional chunk 的大规模 value flow model**。 | §3.1 Eq.(1) 长度-$h$ 块、§3.3 Eq.(5)-(7) flow matching。 | Table 4：换成 HL-Gaussian 分类头，Retry-VOC 0.78→0.59、Expert-VOC 0.95→0.87。 | flow-matching 头相对分类头优势明显；但"首个"是相对性表述。 |
| 提出 **Suboptimal-Value-Bench**：800 条 human-verified、专测 hesitation/retry 的评测集。 | §4、Appendix B。 | Table 1/2：WVM Hesitation-RMSE 0.05（最强 baseline 0.14）、Retry-VOC 0.78（0.62）。 | 基准新颖、标注可核（见 human_verifier 图）；但目前偏 pick-and-place。 |
| 接入下游 policy learning 能在仿真与真实中提升多种抽取方法。 | §5.2、Appendix E（AWR/Filtered BC 都用 WVM advantage 代理 $\Delta_i$）。 | Fig.6：三种 WVM 加权变体一致优于 vanilla BC（仿真 RoboSuite + 真实 AgileX）。 | 趋势成立；但主文只给柱图、无逐格数字，微调只用 10/50 条次优数据。 |

## 摘要与核心贡献

摘要的立论链条：generalist value model 是从大规模混合质量数据 scale 策略学习的基石；数学上准确估值要求**深度时间理解 = 历史 grounding + 未来规划**；但现有机器人 value model 多建在 VLM 上，VLM 预训练偏静态/时间稀疏，缺这份时间建模能力。**world model 恰好天生擅长时间建模与未来规划**，是学习可泛化 value 函数的理想地基。于是作者"把 world model 和 value estimation 联姻"，得到 WVM，输出精确 task progression 以评估数据质量。

摘要给的头号结论：WVM 在标准 benchmark 上取得 SOTA 的 **VOC**；并另建 **Suboptimal-Value-Bench**（800 条 suboptimal 轨迹、高保真人工帧标注）证明它在专家与次优数据上都稳；接入 policy learning 后在仿真与真实里都能提升 manipulation 表现。

三条主贡献（原文 Introduction 结尾）：
1. **把 world model 复用为机器人 value 学习的基础骨干**，用其时空先验克服标准 VLM 的局限；
2. WVM 是**首个把 value 函数建成 distributional chunk 的大规模 value flow model**，配合简单有效的设计，在多样 benchmark 上 SOTA 且对 policy improvement 有效；
3. 提出 **Suboptimal-Value-Bench**——一个含密集、人工标注 suboptimal 轨迹的新评测套件。

> 读原文才注意到的口径细节：摘要说的"SOTA VOC"里，Expert-VOC WVM 均值 0.95、最强 baseline（RoboReward）0.88；但在 **EgoDex 单个数据集上 WVM 0.92 反被 RoboReward 0.95 略胜**（Table 3）。作者自己在 §5.3 用这个反例说明"Expert-VOC 作为唯一指标是不充分的"——引用时别把"6 项全胜"当成结论，是 6 中 5。

## 按原文 section 逐节精读

### 1. Introduction / 为什么 value model 缺的是"时间"

作者先把 value model 的定位讲清：它给大规模真实 RL 系统提供学习信号，也当离线数据过滤器。核心能力是"过去时间上下文的透彻理解"+"对长期未来结果的前瞻规划"，但**把这两个时间维度合进单个 value estimator 在实践中很难**。随后点名三瓶颈（标量监督低效、窄任务定制、VLM 稀疏视觉建模伤时间理解），并给出核心 insight：world model 已在视频生成与机器人操作里证明了时空理解与未来预测能力，**天然具备 generalist value estimator 所需的双重属性**——所以把它的时空先验"复用"为 value 地基。

**这一节读法**：Introduction 没有停在"value model 有用"，而是把问题精确到"缺的是时间建模、而时间建模是 world model 的强项"这一层——后面每个组件（MoT 耦合、分布式块、co-train、prefix 随机化）都能回勾到这条主张。

### 2. Related Work / 三条线的定位

- **Value models for manipulation**：现有工作的三持续瓶颈（标量回归监督稀疏、单任务定制、VLM 表示偏静态）。最接近本文的是 **ViVa [39]**（也基于视频模型做 value），但它**局限单任务、且依赖 action-annotated 数据**；WVM 则把 value 重构成 distributional chunk，能在**海量 action-free 视频**上做可扩展多任务学习。
- **World models for manipulation**：近来经由 **World Action Models（WAMs）** 兴起，联合建模 action-conditioned 视觉动力学。**Fast-WAM [72]** 证明未来预测完全在 latent 空间做也能保留表示收益——WVM 的**非对称掩码正是引用 [72]**。与这些"策略中心"部署不同，WVM 把 latent 视频先验**转用于 value 估计**。
- **Evaluation of value models**：早期靠定性看曲线不可扩展；一类用下游策略成功率间接测（把 value 保真度和策略选择纠缠）；**GVL [43] 提出 VOC，但单调性判据只适用专家轨迹**，测不了 suboptimal 段。本文的 Suboptimal-Value-Bench 用人工标注的 hesitation/retry 轨迹，直接反映模型标记次优段的能力。

### 3. Method / 方法

#### 3.1 Problem Formulation / 把估值写成"进展块预测"

给定 $h$ 帧观测 $o_{t-h+1:t}$ 与语言指令 $l$，value model 定义一个长度-$h$ 逐帧价值序列的条件分布：

$$
p_\psi\!\left(\hat{v}_{t-h+1:t}\ \middle|\ o_{t-h+1:t},\ l\right),\qquad \hat{v}_{t-h+1:t}\in[0,1]^h\tag{1}
$$

其中 $v_t = t/T$ 是归一化任务进展（$T$ 为轨迹总长）。**建模整块而非孤立标量**，是为了捕捉 plateau、regression 这类局部进展形态。经典 RL 里 value 是折扣未来回报之和：

$$
V(o_t)=\mathbb{E}\!\left[\sum_{t'=t}^{T}\gamma^{\,t'-t} r_{t'}\ \middle|\ o_t\right]\tag{2}
$$

作者接着做了一个漂亮的化归：在标准 sparse-reward（非终止步 $r=-1$、完成时 $0$）下，$V(o_t)$ 退化为**负的期望到目标距离**，于是 **value estimation 等价于 task-progress prediction**，价值函数因此"本质上朝向未来"。这句话就是把世界模型请进来的理由——它自然驱动用视频 world model $M_\omega$ 当 value 的富特征器：

$$
p_\psi\!\left(\hat{v}_{t-h+1:t}\mid o_{t-h+1:t},l\right)=p_\psi\!\left(\hat{v}_{t-h+1:t}\mid M_\omega(o_{t-h+1:t},l)\right)\tag{3}
$$

#### 3.2 WVM Architecture / 视频流 + value 流 + 非对称 MoT

**Video stream**：用 Wan2.2 的视频 VAE 与视频 DiT。对锚在 $[t-h+1,t]$ 的 value 块，先喂给 VAE 一段长度 $(2h+1)$ 的干净视频——1 帧前缀 + $h$ 当前帧 + $h$ 未来帧：

$$
\underbrace{o_{t-h}}_{\text{1-frame prefix}}\ \Vert\ \underbrace{o_{t-h+1:t}}_{h\text{ current frames}}\ \Vert\ \underbrace{o_{t+1:t+h}}_{h\text{ future frames}}\tag{4}
$$

VAE 编成三个时序 latent：**丢掉 prefix latent、保留 current latent 当上下文、把 future latent 加噪做视频生成去噪**。

**Value stream & MoT 耦合**：value 流是一条**镜像视频 DiT 但参数少得多**的轻量 DiT，从带噪 value token 预测 value 块，并通过 MoT 多模态 self-attention 读视频 DiT 的中间特征。核心是一条**非对称注意力掩码**：**value token 读当前视频 token，但视频 token 永不读 value token**（引用 Fast-WAM [72]）。这与 [[@wu2026tactile-wam]] 的 VideoClean 是同一种"保护预训练视觉流"的非对称哲学——只是一个保护视频不被触觉污染，一个保护视频不被 value 任务干扰。

#### 3.3 Training / flow matching + 两个增强

**训练目标**：对被监督的视频与 value token 都用 flow matching。令 $y$ 为未来视频 latent $\xi_{t+1:t+h}$ 或 value 块 $v_{t-h+1:t}$，$f_\psi$ 为对应速度预测器。采噪声 $\epsilon\sim\mathcal{N}(0,I)$、时间步 $\tau\sim(0,1)$，构造插值 $y_\tau=\tau y+(1-\tau)\epsilon$，训 $f_\psi$ 预测速度场 $y-\epsilon$：

$$
L_{\mathrm{FM}}(y)=\mathbb{E}_{y,\epsilon,\tau}\!\left[\left\lVert f_\psi(y_\tau,\tau,o_{t-h+1:t},l)-(y-\epsilon)\right\rVert_2^2\right]\tag{5}
$$

$$
L_{\text{value}}=L_{\mathrm{FM}}(v_{t-h+1:t}),\qquad L_{\text{video}}=L_{\mathrm{FM}}(\xi_{t+1:t+h})\tag{6}
$$

$$
L=L_{\text{value}}+\lambda\,L_{\text{video}}\tag{7}
$$

**Prefix randomization**：chunk overlapping 推理能改善块间连续性，但会给 value 流留一个**捷径**——直接从前缀 value 外推、绕过视觉证据。作者类比 CFG 的 conditioning dropout：以概率 $p$ 把前缀 value 换成 $[0,1]$ 上均匀采的随机标量、否则保留；损失只加在剩余 value token 上。混合干净与随机前缀，既保块间连续、又防捷径。$p$ 在 §5.3 消融。

**Video rewinding**：专家轨迹只给单调进展标签，对 plateau/regression 监督不足。沿 ReWiND [74]，对每个窗口按三种时序模式重排 $h$ 帧——**rising / plateau / descending（保留 / 重复 / 反转帧）**，value 相应重标。这让 value 流见到平滑推进、停滞、回撤三种局部进展形态。（这一手和库内 [[@yu2026warp-rm]] 的 time-warp augmentation 是同源思路：都从单调专家数据里**合成非单调进展**当监督。）

### 4. Suboptimal-Value-Bench / 专测两类次优行为

真实机器人数据常有 hesitation/retry 段，对实用估值很关键。基准含 **800 条人工标注轨迹、3 embodiment（AgileX/ARX/RoboSuite）、15 任务**，每帧配一条聚焦停滞/回撤的密集 value 曲线。

- **4.1 Hesitation**：机器人静止或做与任务无关的微动，不推进进展——来自遥操作者认知停顿或硬件约束（近关节限位减速），**该段任务进展不变**。因为标准 VOC 对"恒定目标轨迹"无定义，改用 RMSE：

$$
\text{Hesitation-RMSE}=\sqrt{\frac{1}{|H|}\sum_{t\in H}(\hat{v}_t-v_t)^2}\tag{8}
$$

$H$ 是停滞段帧集，$v_t$ 是该区间恒定真值。它显式罚"预测漂移"：维持恒定准确预测→误差 0，波动预测→RMSE 升高。

- **4.2 Retry**：一次失败尝试（如抓空）后 release + retraction 再重试。抓住"随之而来的 value 下降"是识别 retry 的关键，故评测**只取真值单调下降的窗口**，把 VOC 限制到这些窗口，记为 Retry-VOC。完美跟住下降→ $+1$，反向单调上升→ $-1$。

### 5. Experiments / 实验

#### 5.1 Value Estimation Quality / 估值质量

**基准与基线**：Suboptimal-Value-Bench + 标准 VOC；六个竞争基线 **GVL / VLAC / Robometer / TopReward / RoboReward / Robo-Dopamine**（均不在当前库；实现细节见 Appendix D，如 GVL 用 gpt-5.4 API、VLAC 用 InternVL、Robometer/RoboReward 用 Qwen3-VL、TopReward 用 Qwen3-VL-8B、Robo-Dopamine 3B GRM）。

**Table 1（Hesitation-RMSE ↓，越低越好）**：WVM 在三 embodiment 全部最低，均值压到 **0.05**，把最强基线 GVL、Robometer（都 0.14）甩开一大截。

| Embodiment | GVL | VLAC | Robometer | TopReward | RoboReward | Robo-Dopamine | WVM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| AgileX | 0.11 | 0.47 | 0.13 | 0.36 | 0.12 | 0.41 | **0.07** |
| ARX | 0.14 | 0.50 | 0.12 | 0.24 | 0.17 | 0.52 | **0.05** |
| RoboSuite | 0.16 | 0.54 | 0.16 | 0.33 | 0.31 | 0.51 | **0.04** |
| **Average** | 0.14 | 0.51 | 0.14 | 0.31 | 0.21 | 0.49 | **0.05** |

**Table 2（Retry-VOC ↑，越高越好）**：WVM 三 embodiment 全部第一，均值从 **0.62 抬到 0.78**。要读的是**符号**：VLAC −0.37、Robometer 均值 −0.16、TopReward 0.00——这些模型在回撤段**朝错方向跟踪**（机器人在退，它们还在预测进展升），WVM 0.78 是**质的不同**。

| Embodiment | GVL | VLAC | Robometer | TopReward | WVM |
| --- | ---: | ---: | ---: | ---: | ---: |
| AgileX | 0.73 | −0.37 | 0.32 | 0.15 | **0.79** |
| ARX | 0.76 | / | −0.27 | −0.19 | **0.79** |
| RoboSuite | 0.43 | / | −0.37 | 0.00 | **0.75** |
| **Average** | 0.62 | −0.37 | −0.16 | 0.00 | **0.78** |

（"/" = ill-defined VOC，对 RoboReward、Robo-Dopamine 恒成立，故这两者未列入 Retry 表。）

**Table 3（Expert-VOC ↑，专家轨迹）**：WVM 均值 **0.95**，最强基线 RoboReward 0.88；6 数据集里 **5 项第一**，三套自采数据均 $>0.99$。唯一失手是 **EgoDex（WVM 0.92 vs RoboReward 0.95）**——作者用它引出"Expert-VOC 单独不充分"。

| Dataset | GVL | VLAC | Robometer | TopReward | RoboReward | Robo-Dopamine | WVM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| OXE | 0.67 | 0.48 | 0.63 | 0.19 | 0.92 | 0.72 | **0.94** |
| RoboCOIN | 0.70 | 0.60 | 0.77 | 0.47 | 0.85 | 0.75 | **0.95** |
| EgoDex | 0.82 | 0.62 | 0.86 | 0.37 | **0.95** | 0.88 | 0.92 |
| Self-collected (3 emb.) | 0.93 | 0.50 | 0.93 | 0.58 | 0.84 | 0.76 | **0.99** |
| **Average** | 0.78 | 0.59 | 0.81 | 0.42 | 0.88 | 0.82 | **0.95** |

（Figure 4 是定性曲线对比：hesitation/retry/expert 三行，WVM 标记的段与人类直觉贴合——正文说"consistent with 定量结果"。）

#### 5.2 Downstream Policy Learning / 下游策略学习

**Setup**：3 个仿真 RoboSuite 任务 + 3 个真实 AgileX 双臂任务，基座策略 **π0.5-base**。微调**只用 suboptimal 数据**：每仿真任务 10 条、每真实任务 50 条。加权方式：vanilla BC、AWR、两种 Filtered BC（binary 保留 $\text{Adv}>0$ 的段、percentile 保留按 WVM value 排序 top 70%）。所有加权都基于同一个 **chunk 级 advantage 代理** $\Delta_i=V(t^{\text{tail}}_i)-V(t^{\text{head}}_i)$（Eq.E.4）。

**结果（Figure 6）**：三种 WVM 加权变体在仿真与真实中**一致优于 vanilla BC**，说明 WVM 能真正把"真实进展"从"次优行为"里分出来，让策略更有效地利用不完美数据。（主文只给柱图，无逐格数字——这是引用时要注意的边界。）

#### 5.3 Ablation Study / 消融（Table 4，全文最关键）

| Metric | Ours | w/o $L_{\text{video}}$ | scratch | frozen | $p{=}0$ | $p{=}1$ | HL-Gaussian |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hesitation-RMSE ↓ | **0.05** | 0.08 | 0.08 | 0.12 | 0.09 | 0.05 | 0.06 |
| Retry-VOC ↑ | **0.78** | 0.68 | 0.62 | 0.45 | 0.67 | 0.75 | 0.59 |
| Expert-VOC ↑ | 0.95 | 0.95 | 0.96 | 0.92 | **0.98** | 0.91 | 0.87 |

三组消融各证一件事：

1. **Video co-training（$\lambda$）**：去掉 $L_{\text{video}}$→RMSE 0.05→0.08、Retry-VOC 0.78→0.68；视频流从随机初始化 scratch→Retry 0.62；**完全冻结视频权重→最惨（RMSE 0.12、Retry 0.45）**。结论：**持续 co-train 世界模型不可或缺**——起作用的不是"拿世界模型当冻结特征器"，而是让它在 value 梯度里继续被优化。这一格直接证成 WVM 的中心前提。
2. **Prefix randomization（$p$）**：$p{=}0$ 时 RMSE 恶化到 0.09、Retry 掉到 0.67，但 **Expert-VOC 反升到 0.98**——这正暴露"病态地把前缀当因果捷径"，也证明 **Expert-VOC 单独不足以评价 value model**；$p{=}1$（全掩码）恢复 retry（0.75）却因块间一致性被破坏、Expert-VOC 掉到 0.91。**$p{=}0.5$ 取得最佳平衡**。
3. **Value head**：把 flow-matching 头换成 HL-Gaussian 分类头（$K{=}51$ 固定 bin），RMSE 小升（0.05→0.06）但判别性分数**大跌**（Retry 0.78→0.59、Expert 0.95→0.87）。原因：分类头固定 bin 支撑保住了条件均值，却丢掉了 ordinal 指标需要的细粒度密度差；flow-matching 头能捕连续 return 密度、不限支撑/分辨率，保住了"给时序相邻块排序"所需的局部 value 微分。

### 6. Conclusion & 7. Limitations / 结论与局限

**结论**：WVM 是一个扎根于预训练 world model 预测能力的 generalist robotic value flow model，继承其历史 grounding 与未来 planning 的原生优势，在标准 benchmark 与新 Suboptimal-Value-Bench 上都 SOTA；下游仿真与真实部署证明这套"世界模型派生"的架构能为混合质量数据学习提供稳健指引。

**作者自陈的局限**：(1) 受算力限制，**训练数据规模目前有限**，导致 WVM 对完全没见过的任务/场景 zero-shot 能力受限；(2) Suboptimal-Value-Bench 虽超越"只有专家"的评测，但**范围主要在 pick-and-place**，扩展到更灵巧、长 horizon 操作是关键下一步。计划未来同时扩大训练混合与评测多样性。

### Appendix 关键数字（值得记住的工程细节）

- **架构（App.A）**：视频流基于 **Wan2.2-TI2V-5B**；Wan2.2-VAE 按 $4{\times}16{\times}16$ 压缩→48 通道时空 latent，patch $(1,2,2)$。**视频 DiT** 30 层、hidden 3072、24 头（head dim 128）、FFN 14336、约 **5.0B** 参数；**value DiT** 同深度但 hidden 512、8 头（dim 64）、FFN 14336。MoT 里 value token 由 512 线性投到共享 3072（24 头 dim 128）参与联合注意力再投回 512；value 侧组件约 **0.7B** 可训参数，**整机约 5.7B**。VAE 冻结当 tokenizer，T5 文本编码器离线预算。
- **训练（App.A）**：$32{\times}$A100-40GB、约 **40h**、AdamW、peak LR $1{\times}10^{-4}$ cosine 衰减到 $0.1\times$、warmup 500、global batch 1024、**30,000 步**、bf16、$p{=}0.5$、rewind ratio 0.5、plateau ratio 0.1、**value chunk 长 $h{=}4$**、latent target FPS 2.0（AgileX/ARX 自采 3.0）、$\lambda{=}1.0$。
- **推理（App.A）**：flow-matching 速度场用 Euler 求解器、**所有结果只用单步去噪**——作者归因于"训练语料相对模型容量适中，速度场足够光滑、一步已落在真值附近"。$h{=}4$ + overlapping-window 平均。
- **训练混合（Table A.2）**：共 **590 subsets、407,086 条轨迹、1,410.83 小时**——RoboCOIN 98,171、EgoDex 299,100、RoboReward 7,428、RoboSuite(ours) 1,865、AgileX 单臂 160 / 双臂 120、ARX 242。
- **Suboptimal-Value-Bench（Table B.3）**：AgileX 200 + ARX 300 + RoboSuite 300 = **800**（400 hesitation + 400 retry），每任务两组各含两种模式。
- **真值曲线（App.B）**：四点分段线性过 $(0,0),(m,v_m),(n,v_n),(T{-}1,1)$；设 $x=n-m$。Hesitation 段平台：$v_m=v_n=\frac{m}{T-1-x}$；Retry 段匀速回撤（后退速率 = 正常前进速率 $r=\frac{1}{T-2x}$）：$v_m=\frac{m}{T-2x},\ v_n=\max\!\left(0,\frac{m-x}{T-2x}\right)$。
- **下游（Table E.5）**：π0.5-base、$16{\times}$A100、peak LR $2.5{\times}10^{-5}$、batch 256；RoboSuite（EEF、5000 步、$H{=}10$、AWR $\tau{=}10$、top-70% $\kappa{=}0.02$、50 trials）、AgileX（Joint、10000 步、$H{=}50$、AWR $\tau{=}2$、$\kappa{=}0.06$、30 trials）。AWR 权重 $w_i=\min(\exp(\tau\Delta_i),\delta),\ \delta{=}2.0$。

## 方法细节

一句话把 WVM 的"三件套"串起来：**世界模型骨干（借时空先验）+ 非对称 MoT 耦合（借而不损）+ 分布式 value 块 × flow matching（密集且有表达力）**，再靠 prefix 随机化与 video rewinding 两个增强，把"只见单调专家"的监督扩到"停滞/回撤"的非单调世界。

- **为什么是块而不是标量**：Eq.(1) 的长度-$h$ 输出让模型能表达 plateau/regression——这直接对应 Suboptimal-Value-Bench 的两类行为，是"任务定义"与"指标定义"闭环自洽的设计。
- **为什么非对称**：视频流是预训练资产，双向注意力会让 value 任务反向污染视频表示（与 [[@wu2026tactile-wam]] 命名的 tactile pollution 同构）；单向 value→video 既取用又不破坏。
- **为什么 co-train 而非冻结**：Table 4 的 frozen→0.45 说明世界模型的时序表示需要**在 value 目标下继续塑形**才对齐"进展"语义，冻结只能拿到"生成视频"的表示、不是"评估进展"的表示。
- **为什么单步推理够用**：flow matching 学到的是光滑速度场，在中等规模语料下一步 Euler 已足够；这让 WVM 当数据过滤器时**推理开销可控**——对"给 40 万条轨迹逐帧打分"这种规模很关键。

## 实验

- **Setup**：估值质量在 Suboptimal-Value-Bench（800 条、3 emb、15 任务）+ 标准 Expert-VOC（359 subsets、1,605 条，Table C.4，均按轨迹级从训练集 hold out 防泄漏）上评。下游在 3 仿真 RoboSuite + 3 真实 AgileX 上评，基座 π0.5-base，只用 10/50 条次优数据微调。
- **Baselines**：GVL、VLAC、Robometer、TopReward、RoboReward、Robo-Dopamine（均不在当前库），统一 2fps（AgileX/ARX 3fps）采样、各按官方协议评。
- **Metrics**：Expert-VOC（单调专家）、Hesitation-RMSE（停滞漂移）、Retry-VOC（回撤跟踪）三件套 + 下游成功率。
- **主结果**：Expert-VOC 均值 0.95（最强 0.88）、Hesitation-RMSE 0.05（最强 0.14）、Retry-VOC 0.78（最强 0.62）——三线全 SOTA，且 Retry 上多个 baseline 是负值（跟错方向）。
- **消融**：见 Table 4——co-train 不可或缺（frozen→0.45）、$p{=}0.5$ 最优（$p{=}0$ 虽把 Expert-VOC 刷到 0.98 却是前缀捷径）、flow-matching 头优于分类头（Retry 0.78 vs 0.59）。

## 图表索引与讲解

**Figure B.1（human_verifier.png）读图重点**：这是 Suboptimal-Value-Bench 的**人工核验界面**，直接证明"100% human-verified"不是空话。

![[papers/images/wang2026wvm/human_verifier.png|760]]

界面右栏把两阶段流水的关键量都摆出来了：某条 AgileX "carrot_off_plate_sub_hesitation" 轨迹，**VLM PREDICTION** 给的粗分割是 start 45 / end 108 / length 64；**YOUR LABEL**（人工）改成 start 52 / end 100 / length 49，**$\Delta$start 7、$\Delta$end −8、IoU 0.766**。也就是说 VLM 只当"proposer"给候选边界，人再逐帧拖动收紧——TASK 与 VLM DESCRIPTION 也在图上（"robot arm holds position over the carrot without advancing... stalling with no forward progress"），底部时间轴用红（VLM pred）/绿（human label）/蓝（cursor）三色叠放。这张图回答的正是最自然的质疑：**你 800 条真值是不是就是 VLM 自动标的？** 答案是否——VLM 只是加速器，最终边界全在人工控制下，$\Delta$ 与 IoU 量化了人对 VLM 的修正幅度并非可忽略。

其余图表（无独立图片文件，据正文/caption 转述）：

| 图 / 表 | 读图重点＝证明什么 | 关联问题 |
| --- | --- | --- |
| Figure 1 | 全文因果链：世界模型→检测 hesitation/retry→更好 value→仿真+真实 policy improvement。 | WVM 到底改善了下游什么。 |
| Figure 2 | 架构：Video VAE/DiT 流 + 轻量 Value 流经 MoT 非对称 self-attention 耦合；prefix 随机化 + chunk overlapping 示意。 | value 如何"读视频但不污染视频"。 |
| Figure 3 | Suboptimal-Value-Bench 采集：3 emb、15 任务、800 条、蓝箭头示意 hesitation（平台）/retry（下降）的人标 value 曲线。 | 两类次优行为的真值长什么样。 |
| Figure 4 | 定性 value 曲线：hesitation/retry/expert 三行，WVM 标记段贴合人类直觉。 | 定量优势是否有可视证据。 |
| Figure 5 | 下游 6 任务 setup（3 仿真 + 3 真实 pick-and-place）。 | 下游评测覆盖哪些任务。 |
| Figure 6 | 下游柱图：三种 WVM 加权（AWR / Filtered BC×2）一致高于 vanilla BC。 | WVM 的 value 能否转成策略增益。 |
| Table 1 | Hesitation-RMSE：WVM 0.05 vs 最强 0.14，抗漂移最好。 | 停滞段谁不"乱动"。 |
| Table 2 | Retry-VOC：WVM 0.78，多个 baseline 负值（跟错方向）。 | 回撤段谁跟得住掉分。 |
| Table 3 | Expert-VOC：WVM 0.95、5/6 第一，EgoDex 略负于 RoboReward。 | 专家单调轨迹上的天花板 + 指标局限。 |
| Table 4 | 三消融：co-train 必需、$p{=}0.5$ 最优、flow head 胜分类头。 | 每个设计到底贡献多少。 |

## 和你的论文库中其他条目的关系

- **数据打分/进展价值线（最直接的同题竞品）**：[[@liu2026steam]]（STEAM，self-supervised temporal ensemble advantage，给真实轨迹分辨"有效进展/停滞/恢复/失败"）与 [[@yu2026warp-rm]]（WARP-RM，time-warp 增强从成功演示学 dense relative progress reward、用于数据筛选与加权 BC）和 WVM 是**三足鼎立的同一主题**：都想给混合质量数据打 frame-level 进展分再做加权/过滤 BC。差异是路线——STEAM 走 self-supervised advantage、WARP-RM 走 time-warp 自监督 reward、**WVM 走"预训练视频世界模型 + 分布式 value flow"**。尤其 **WVM 的 video rewinding 与 WARP-RM 的 time-warp 是同源增强**（都从单调专家造非单调进展），值得并读对比"合成非单调监督"的两种实现。
- **世界模型线（骨干与哲学来源）**：[[@wang2026orca]]（统一 world latent space + 多模态 readout 支持理解/预测/行动）、[[@zhang2026qwen-robotworld]]（language-conditioned video world model 预测未来视觉）、[[@gao2026fast-leworldmodel]]（latent world model 的 action-prefix 快速 rollout）、[[@gigaworld2026roadmap]]（world model 用于**策略评估**）。WVM 与这条线共享"世界模型是地基"的信念，但**独特主张是把世界模型的 readout 头做成 value/进展**而非视频或动作。特别值得和 [[@gigaworld2026roadmap]] 对照：**GigaWorld 用世界模型评估策略（生成 rollout 看成败），WVM 用世界模型评估数据（逐帧打进展分）**——同是"world model as evaluator"，评估对象不同。
- **触觉世界-动作模型（结构同构）**：[[@wu2026tactile-wam]]。二者都在追问"world model 除了生成画面还能干什么"，且**共享同一条非对称注意力先验**——Tactile-WAM 的 VideoClean 屏蔽 video→tactile 保护视觉预测，WVM 的 MoT 掩码屏蔽 video→value 保护视频生成。一个把世界模型扩成"预测物理接触状态并回灌动作"，一个把它转成"给数据打价值分"，可对照"world model 的输出被当作 action 条件还是 value 信号"。
- **策略侧（互补层次）**：[[@li2026zr0]]（dense ECoT 监督训 VLA）、[[@kang2026x-tokenizer]]（action tokenization 当语义接口）、[[@zhou2026holoagent0]]（agent 级 reason-plan 循环 + 3D 空间记忆）处在动作/agent 层，与 WVM 的"数据评估层"是纵向互补——WVM 产出的 advantage 代理正好可喂给这些策略的加权微调。
- **论文自身引用的近亲（均不在当前库，如需可另行入库）**：value/reward baseline **GVL、VLAC、Robometer、TopReward、RoboReward、Robo-Dopamine**；最接近的 video-value 前作 **ViVa [39]**（单任务、依赖 action 标注）；非对称掩码来源 **Fast-WAM [72]**（注意：与库内 [[@gao2026fast-leworldmodel]] 是不同论文）；增强来源 **ReWiND [74]**；骨干 **Wan2.2 [64]**、MoT [33]、flow matching [34]。

## 可追问点

1. **"单步推理够用"是否只在中等语料成立**？作者自己把它归因于"训练语料相对模型容量适中，速度场光滑"。若把训练数据 scale 到十倍、任务更长 horizon，速度场是否仍光滑到一步收敛？届时是否需要多步、反而抵消掉"当过滤器时推理便宜"的优势？
2. **prefix 捷径的悖论**：$p{=}0$ 时 Expert-VOC 升到 0.98，说明前缀外推能"刷"单调性。那 WVM 上报的 0.95 是否也含少量前缀增益？如果把 overlapping 推理关掉、纯单块评测，Expert-VOC 会掉多少？
3. **Retry-VOC 的正负号差距太干净**（WVM 0.78 vs VLAC −0.37、Robometer −0.16）。这更像"WVM 见过 rewind 造的 descending 模式、baseline 没见过"的分布内优势，而非泛化优势——把 retry 换成训练时没造过的失败模式（如打翻后重摆），WVM 还能保持正 VOC 吗？
4. **下游只给柱图、无逐格数字**，且微调只用 10/50 条次优数据。这个规模下的 policy improvement 有多稳（方差多大）？换更强 baseline（π0.6/π0.7 级）或更多数据，WVM 的 value 加权还有多少边际收益？
5. **EgoDex 上 WVM 略负于 RoboReward**。EgoDex 是**人手 egocentric 视频**、非机器人本体——这是否说明 WVM 的世界模型先验对"机器人分布"过拟合、对人手第一视角的进展估计偏弱？跨 embodiment（人→机器人）的 value 迁移是不是它的软肋？
6. **contact/dexterous 缺席**：作者自承基准偏 pick-and-place。value = 归一化时间进展 $t/T$ 在"进展不单调映射到画面变化"的任务（如拧螺丝、揉捏、擦拭）上是否还成立？这类任务的"进展"未必在 RGB 里线性可见。

## 我的阅读笔记

这篇的真正价值不在"又一个 reward/value 模型"，而在它把问题从"用什么 backbone 学 value"重构成 **"value 该长在哪种时间先验上、且该被建成什么形状"**。它给的答案很自洽：**value ≡ 负的到目标距离 ≡ 任务进展，天然朝向未来，而未来正是 world model 的主场**——这条化归（Eq.2→Eq.3）是全文最优雅的一步，把"为什么用世界模型"从口号变成了推导。配套的两个"形状"选择也讲得通：分布式 value chunk 对应 plateau/regression 两类局部形态，非对称 MoT 对应"借世界模型而不损世界模型"。

全文最有说服力的两击都在消融：**冻结视频权重→Retry-VOC 崩到 0.45**，把"world model 必须持续 co-train、而非当冻结特征器"从主张变成可测现象；**关掉 prefix 随机化→Expert-VOC 反升到 0.98**，则一箭双雕地既证成了正则、又证否了"Expert-VOC 单独可用"——后者顺手为 Suboptimal-Value-Bench 的存在提供了不可绕过的动机。Retry-VOC 上多个 baseline 是负号（跟错方向）也很直观地说明"现有 VLM-value 在回撤段是瞎的"。

但要清醒看边界：**下游只给柱图、微调只用 10/50 条数据、训练语料作者自承"规模有限"、基准偏 pick-and-place、EgoDex 上还被 RoboReward 略胜**。这些合起来说明它现在更像"**一个把 value 正确接进视频世界模型的架构原则 + 一个补上次优评测的基准**"，而不是"一个已验证可规模化部署的数据过滤 recipe"。Retry-VOC 的漂亮很可能部分来自 rewind 增强带来的分布内优势，真正的泛化考验要看没造过的失败模式。

我会把它作为 **"world model 的 readout 到底该输出什么"** 这条线的一个明确坐标：[[@gigaworld2026roadmap]] 输出"策略评估用的 rollout"、[[@wu2026tactile-wam]] 输出"物理接触状态并驱动动作"、WVM 输出"逐帧价值/进展"。同时它和 [[@liu2026steam]]、[[@yu2026warp-rm]] 组成"进展价值化用于数据筛选"的三人组——下一步该做的是把三者放到同一批混合质量数据上、用同一个下游策略，直接比"谁的进展分让 Filtered BC 涨得最多"。
