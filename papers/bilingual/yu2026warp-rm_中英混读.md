---
tags:
  - bilingual-reading
  - deep-reading
paper: "[[@yu2026warp-rm]]"
source_pdf: "[[papers/pdfs/yu2026warp-rm.pdf]]"
images: "papers/images/yu2026warp-rm/"
image_index: "[[papers/images/yu2026warp-rm/index.md]]"
created: 2026-07-05
reading_mode: 生成式精读（逐节读原文 + 读图）
---

# WARP-RM: A Warp-Augmented Relative Progress Reward Model for Data Curation

paper:: [[@yu2026warp-rm]]
pdf:: [[papers/pdfs/yu2026warp-rm.pdf]]
images:: [[papers/images/yu2026warp-rm/index.md]]

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| data curation | 数据筛选 | 本文靶心：从含犹豫/重试/恢复的 mixed-quality teleop 演示里，挑出并加权"高质量片段"再喂给 imitation learning。 |
| absolute progress regime | 绝对进度范式 | 现有做法（ReWiND 用 normalized frame index、VIP/LIV 用 temporal contrastive）给每帧一个全局 $[0,1]$ 完成度 target；作者论证它在 long-horizon teleop 里被 label noise 污染。 |
| relative / signed progress velocity $\hat v_t$ | 相对（有符号）进度速度 | 本文核心量：一小段时间"把任务往前推还是往后退、推多快"。校准为 $\hat v_t\!\approx\!1$ 匹配参考演示平均节奏、$\hat v_t\!\approx\!0$ 停滞、$\hat v_t\!<\!0$ 倒退。 |
| WARP (Warp-Augmented Relative Progress) | 时间扭曲增广的相对进度 | 全自监督的算法：靠 time-warp 增广把一条成功演示变出连续范围的"进度速度"训练信号。 |
| time-warp augmentation | 时间扭曲增广 | 用可变播放速度（慢放↔快进）+ 随机反向重放成功演示，帧的相对位移就是自监督伪标签。 |
| AR(1) process | 一阶自回归过程 | 采样"平滑相关"的逐帧 log-速度（而非 IID），模拟推理时连续视频流里自然、渐变的执行速度。 |
| reversal / negative progress | 反向 / 负进度 | 借 ReWiND 思路，用反向播放制造"任务倒退"监督，让模型见到 $\hat v_t<0$ 的样本。 |
| two-hot categorical target | 两热分类目标 | 不直接回归 $y_j$，而是预测 30 个 bin 上的分布、用两热编码 + 交叉熵训练（缓解回归的优化不稳/容量浪费）。 |
| temporal-diff token | 时间差分 token | 每帧输入 = $[\phi(o_{i_j}),\ \phi(o_{i_j})-\phi(o_{i_{j-1}})]$，把"当前特征 + 与上一帧之差"拼进 token。 |
| terminal-frame aggregation $\hat v_{\text{end}}$ | 末帧聚合 | WARP-BC 用 action chunk **末帧**的速度而非 chunk 均值来 gate/加权——避免瞬时高速尖峰掩盖随后的倒退。 |
| RA-BC / advantage-filtered BC | 奖励对齐 / 优势过滤行为克隆 | 训练范式：$\hat v_{\text{end}}$ 当作 advantage 的经验代理，过滤掉 $w=0$ 的 chunk、并按 $\hat v_{\text{end}}$ 连续加权 flow-matching 损失。 |
| WARP-BC | 扭曲增广相对进度行为克隆 | 把 WARP-RM 的逐帧 $\hat v_t$ 用于 action-chunk 级 gating + reweighting 的 BC 策略。 |
| ReWiND / VIP / LIV | 三个绝对进度基线 | 分别用 normalized 帧索引、value-implicit / language-image 对齐做 progress reward，是本文"绝对进度有噪声"论证的对照。 |
| SARM / ARM / SCIZOR / DemInf | 四个数据筛选/奖励基线 | SARM、ARM 需人工标注 subtask 边界；SCIZOR 自监督预测两帧时间差；DemInf 用互信息做 episode 级筛选——都是 Table 2 的匹配对照。 |
| TTC / throughput | 完成用时 / 吞吐 | 关键评测量：成功轨迹平均完成时间；每小时成功折叠数（失败按 4 min 超时计入分母）。在 $n=20$ 成功率相近时更能区分好坏。 |

## 论文主线

![[papers/images/yu2026warp-rm/ep3405_curve_with_frames.png|760]]

**Figure 1 / 全文动机与总览（WARP-RM 在一条混合质量 T-shirt 折叠演示上的 signed progress 输出）。** 上排 a)–l) 是同一条演示的关键帧，下面是模型逐帧输出的 $\hat v_t$ 曲线。读法直接对应校准语义：**绿色正区**（如 b 处出现 $\hat v_t\!\approx\!3$ 的尖峰）= 决定性的向前推进（果断抓布、铺平、对折）；**近零平段**（如 e/h/j 附近贴着 0）= 停滞、微调、犹豫；**红色负谷**（e 处 $\hat v_t$ 掉到约 $-1$、l 处结尾再次转负）= 任务倒退（夹爪把衣服掉了或状态回退）。这张图一眼给出全文因果链：**progress 不等于 elapsed time**——同一条演示里，时间一直在走，但"任务前进量"时正时负时零，只有把这个**有符号、逐帧、相对**的量估出来，才能在下游 BC 里把"果断推进段"留下、把"停滞/倒退段"剔掉或降权。

这篇论文的核心问题是：**imitation learning 要 scale 就得吃大规模人类 teleop 数据，但人类遥操作天然产出 mixed-quality 演示——里面混着 hesitation、失败抓取、来回微调、recovery。** 如果照单全收地 BC，策略会连人类的"卡顿和 fumble"一起学会，在 long-horizon 任务上直接 derail。但这些 suboptimal 片段又不能整条丢——它们里常藏着有价值的 recovery（类似 DAgger 数据）。

现有两条补救路线各有硬伤。**Episode 级筛选**（DemInf、influence-function 类）粗暴丢弃低于阈值的整条 episode：既误杀了 suboptimal 执行里嵌着的高优势片段，又没法剪掉保留演示里局部的犹豫/fumble。**Frame 级 progress reward** 更细，但主流都工作在 *absolute progress regime*：ReWiND 拿 normalized 帧索引当监督、VIP/LIV 用 temporal contrastive 做全局对齐。作者的关键批评是——**equating elapsed timesteps with task progress 会注入大量 label noise**：因为不同 operator 会在不同点暂停、重试、恢复，两条演示在**同一 normalized 帧索引**上可能对应完全不同的任务阶段。更近的 dense reward model（SARM/ARM）改用人工标注 subtask 边界，但标注昂贵且不一致。

作者的回答是把问题从"绝对进度"重构为 **relative progress velocity（相对进度速度）**：不去问"这一帧完成度是多少"，而问"这一小段把任务往前还是往后推、推多少"。这个提法**根本上绕开了 cross-demonstration 时间对齐**，同时仍产出适合 action-chunk 加权的 dense 标量信号。

阅读时要盯住一句话：**本文贡献不是"用 progress 做筛选"（前人做过），而是"用什么信号来定义 progress"——用 time-warp 自监督出的、有符号的相对速度，而非有噪的绝对时间轴。** 后面的每个组件（AR(1) 采样、反向播放、末帧聚合、连续加权）都对应这条主线的一个具体决定。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| **WARP**：全自监督的 time-warp 增广，从成功演示学 dense relative progress velocity（训得 WARP-RM）。 | §3.1–3.3，Eq.(1)–(3) | Fig.1 定性曲线；校准 $\hat v\!\approx\!1/0/<0$ 语义成立。 | 概念新颖（相对 vs 绝对进度）；但监督只来自成功演示，负进度靠反向播放**近似**。 |
| **WARP-BC**：用 WARP-RM 的末帧速度 $\hat v_{\text{end}}$ gate + 连续加权 action chunk。 | §3.5，Eq.(4)(5) | Table 3：terminal 19/20 vs chunk-mean 15/20；continuous 19/20 vs binary 16/20（同样 34.4% 保留）。 | 消融干净：terminal + continuous 是增益关键，不是随手选的。 |
| **420 次真实试验、双任务**，验证对 suboptimal 数据的鲁棒性。 | §4，Table 1/2/4 | T-shirt D2：WARP-BC 19/20 vs vanilla BC 2/20，吞吐 $\sim$18×；bottle：74/80 vs 59/80，1.6×。 | 真实增益大且稳；但**单一 bimanual 平台、两任务、$n=20$** 有采样噪声。 |

## 摘要与核心贡献

摘要的矛盾是：scaling imitation learning 需要大数据集，但 human teleoperation 不可避免产出含 hesitation/recovery 的 mixed-quality 演示。既有 frame-level progress reward model 要么监督在**绝对时间进度代理**上（受 label noise 污染），要么依赖**昂贵的人工标注**来定义 subtask 边界。

WARP 的回答是一个 **fully self-supervised** 算法：用 time-warp 增广（可变播放速度 + 反向）从成功演示生成逐帧 progress target，训练 WARP-RM 去预测输入帧之间的 normalized elapsed time；把这些预测在 overlapping windows 上聚合，得到 dense 逐帧 progress 信号。再用 WARP-BC——用这些标量 reward 在 behavior cloning 里 upweight 高优势 action chunk（chunk 级 advantage 由逐帧 reward 聚合而来）。

摘要给的头号数字是：在物理 bimanual robot 上做 long-horizon 可形变物体操作（从随机揉皱起点折叠 T-shirt），当训练集被放宽到吃进更多 inefficiency 时，**vanilla BC 崩到 2/20，WARP-BC 稳在 19/20，成功折叠吞吐提升最高 $\sim$18×**。

> 读原文才校准清楚的数字口径：$\sim$18× 是 Table 1 里 **D2 tier** 的吞吐比（vanilla BC 1.5/hr → WARP-BC 27.4/hr $\approx$ 18.3×），不是成功率倍数；D1 tier 上两者都 20/20 成功，吞吐提升是 1.78×（31.6 → 56.3/hr）。引用时别把"18×"写成"成功率 18 倍"。

## 1. Introduction / 为什么绝对进度不够

作者把动机拆成三层：
1. **策略对演示质量高度敏感**：近期 policy modeling / 大规模预训练提升了表达力和泛化，但仍会把 human teleop 里的 pause 和 fumble 一起 mimic，long-horizon 尤甚。
2. **suboptimal 片段不可整条丢**：里面常含有价值的 recovery（类比 DAgger）。episode 级筛选（丢整条 episode）有两个短板——误杀 suboptimal 执行里的高优势段，又剪不掉保留演示里的局部犹豫。
3. **frame 级 progress 的绝对进度陷阱**：ReWiND 用 normalized episode duration、VIP/LIV 用 temporal contrastive 做全局对齐。但 *temporal progression ≠ task progression*——因 pause/失败抓取/不同 operator 策略，同一 normalized 帧索引可对应完全不同的任务阶段。人工标注（SARM/ARM）虽降噪但昂贵、不一致。

据此 WARP 学一个**局部相对**进度信号：把成功演示以非均匀速度（含反向）重放，训模型从图像序列预测 progress velocity——决定性前进时大正、pause/fumble 时近零、状态回退时为负；聚合后得到能识别 decisive progress / stagnation / regression 的 dense 信号，再由 WARP-BC 用于 filter + reweight action chunk。

**这一节读法**：introduction 的价值在于它把"数据筛选"这个模糊目标，锐化到一个可证伪的技术判断——"绝对进度轴有 cross-demonstration alignment noise"。后面 Table 2 里 SCIZOR（自监督时间距离代理）和 SARM（人工标注绝对进度）双双在 D5 掉到 2/20，就是对这句批评的实证回勾。

## 2. Related Work / 三条脉络的定位

- **Time Warping for Video Representation Learning**：前人多用**均匀**速度变换 + 速度分类做自监督 pretext；少数做离散、逐帧独立的 skip-count 预测。WARP 的区别有两点：(a) 把 time warping 建模成**结构化随机过程**（平滑相关、非均匀，覆盖慢放到快进）；(b) time warping **不是** pretext，而是直接服务于终端任务——progress estimation。
- **Data Curation for Robot Imitation**：dataset 级（Re-Mix 优化数据源混合）、episode 级（DemInf 互信息、influence function 类）。WARP 工作在更细的 frame/chunk 级。
- **Progress Reward Models**：绝大多数是绝对进度（ReWiND 帧索引、VIP/LIV 对比对齐）。最接近本文的是 **SARM/ARM**（用人工标注训 progress model 做 RA-BC）和 **SCIZOR**（自监督预测两帧时间差做筛选）。WARP-BC 的增量是**额外按 magnitude 加权保留的 chunk**。作者还点名基于 VLM 的多任务 reward（RoboMeter、ToPReward、Robo-Dopamine）：语义泛化强，但常为了 breadth 牺牲高频时间分辨率（VLM query 要粗采样帧），且多锚在绝对进度/离散语义里程碑上，仍受对齐噪声影响。

## 3. Method / 方法

### 3.1 Overview & Notation / 定式与校准

WARP-RM 是一个 **vision-based** 模型，从视觉观测直接估计逐帧 progress velocity。一条演示是固定频率录制的 $T$ 帧 RGB $o_0,\dots,o_{T-1}$，冻结视觉编码器 $\phi$ 给出逐帧特征。从每条演示，通过 time-warp 程序采样一个 $N$ 帧索引窗口 $i_0,\dots,i_{N-1}$——因为变速+反向，索引可以**非单调、非线性**。每个索引配一个伪标签 $y_k$：从 $o_{i_0}$ 到 $o_{i_k}$ 的 normalized time delta（窗口起点起算的累计时间位移）。

模型在给定 $\phi(o_{i_0}),\dots,\phi(o_{i_{N-1}})$ 时预测 $y_1,\dots,y_{N-1}$。推理时输入帧以固定 canonical stride $S$ 秒线性排布、覆盖 $L=(N-1)S$ 秒的窗口，按 §3.5 聚合，给每帧一个 signed progress velocity，校准为：

$$
\hat v_t \approx 1\ \text{（匹配参考演示平均节奏）},\quad
\hat v_t \approx 0\ \text{（停滞）},\quad
\hat v_t < 0\ \text{（倒退）}
$$

### 3.2 Time-Warp Sampler / 采样器：如何造出连续的进度速度

![[papers/images/yu2026warp-rm/sampler_submission.png|760]]

**Figure 2 / 时间扭曲采样器（两步）。** ①**Sample a Sequence of Velocities**：上框 *Playback Speeds*——先从 **AR(1)** 采逐帧相关的 log-速度（比 average pace 时快时慢，在 slow-motion↔fast-forward 之间连续摆动），再按一个采样的平均速度 $\sim$Uniform 整体缩放；下框 *Playback Direction*——反转点数 $\sim$Poisson($\lambda=1$)、位置均匀随机，每次还有 **50% 概率整体反向**（绿=forward、橙=rewind）。②**Convert Velocities to Input Frames**：把这些有符号速度累加，映射回一条真实 episode timeline（图里从 frame 0 到 frame 1710），得到 $N=32$ 个输入帧的**帧偏移**（示例 $+195,-75,+327,+594$）；曲线绿升橙降，正好对应 forward/rewind。这张图是全文机制的核心——**一条演示，靠随机的变速+反向重放，就能给出覆盖慢放到快进、正到负的连续 progress 监督**。

采样器细节。先从平稳 AR(1) 过程抽 $N-1$ 个相对 log-速度：

$$
z_0 \sim \mathcal{N}(0,\sigma_\infty^2),\qquad
z_k = \alpha\, z_{k-1} + \sqrt{1-\alpha^2}\,\sigma_\infty\,\epsilon_k,\quad \epsilon_k\sim\mathcal{N}(0,1),\ k=0,\dots,N-2 \tag{1}
$$

**在 log 空间操作**保证 2× 加速与 0.5× 减速等概率，且所有速度严格为正（反向单独采）；用边缘分布初始化 $z_0$ 使过程平稳，log-速度方差在 $N-1$ 步上恒定；$\alpha$ 控制相邻帧速度变化的平滑度。指数化得未归一化速度 $\tilde v_t = e^{z_t}$。

接着从 $\text{Uniform}([\tfrac{1}{3}L,\ \tfrac{5}{3}L])$ 采总路径长 $\ell$（保证训练里同时见到慢放与快进视角），把速度 rescale 到和为 $\ell$：

$$
\tilde u_k = \ell\cdot\frac{\tilde v_k}{\sum_{j=0}^{N-2}\tilde v_j},\qquad k=0,\dots,N-2 \tag{2}
$$

此时 $\tilde u_k$ 全非负（都是前进）。为造**非单调**进度，采 $R\sim\text{Poisson}(\lambda_{\text{rev}})$ 个反转点、位置在 $\{1,\dots,N-1\}$ 里无放回均匀选；每个反转点把其后所有速度符号翻转，使轨迹在 forward/backward 之间交替。最后整条轨迹以 0.5 概率再整体反向，保证 reward model 见到大致等量的增/减进度样本，得到有符号归一化速度 $u_0,\dots,u_{N-1}$。

令累计有符号位移 $c_j=\sum_{k=0}^{j-1}u_k$（$c_0=0$）。起始索引 $i_0$ 从整数区间 $[\lceil-\min_j c_j\rceil,\ \lfloor T-1-\max_j c_j\rfloor]$ 均匀抽（这个区间恰好保证后续所有索引都落在 $[0,T-1]$ 内），其余索引 $i_j=\text{round}(i_0+c_j)$。

### 3.3 Progress Model Training / 目标与分类式损失

由采样索引，逐帧累计进度伪标签是从窗口起点起算、被常数 $C_{\text{norm}}$ 归一化的有符号位移：

$$
y_j = (i_j - i_0)/C_{\text{norm}},\qquad j=0,\dots,N-1 \tag{3}
$$

关键选择：**不直接回归 $y_j$**，而是让 WARP-RM 对每帧预测 $N$ 个 evenly-spaced categorical bin 上的独立分布，用**两热（two-hot）目标 + 交叉熵**训练（两热把连续值编码为两个最近 bin 中心的线性插值系数）。作者引 Farebrother et al.（"Stop Regressing"）说明这种分类式回归能缓解直接回归的优化不稳与容量欠用。推理时 $\hat y_j$ 取预测分布的期望。

### 3.4 Model Architecture / 冻结 DINOv3 + 双向 Transformer

![[papers/images/yu2026warp-rm/model_arch_submission.png|760]]

**Figure 3 / WARP-RM 架构。** 左侧：32 帧演示窗口经模型输出一条 $\hat v_t$ 曲线（图里 $t\!\approx\!33$–$35$s 有一个明显负谷，对应一次 regression；黄色阴影是一个 sliding prediction window）。右侧是数据流五层：**❄ 冻结 DINOv3 ViT-B/16 ($\phi$)** 出 $N\times768$ → **Temporal-Diff** 拼成 $\text{concat}[\phi(o_j),\phi(o_j)-\phi(o_{j-1})]$ 得 $N\times1536$ → **可训练 Linear Projection + Pos. Embedding** 回到 $N\times768$ → **双向注意力 Transformer（12 层 / 8 头）** → **Relative-Progress Head（30-bin 分类）** 每帧出一个分布 $\hat y_0,\dots,\hat y_{N-1}$ → 底部离散时间导数 $v_j=(N-1)(\hat y_j-\hat y_{j-1})$ 得 intra-window 速度。这图证明：**WARP-RM 结构极轻**——借 SARM 的"冻结 backbone + Transformer 时间聚合器"，但把 stage 分类器 + subtask 回归器替换成单个 progress velocity head。

具体：$\phi$ 是冻结的 DINOv3 ViT-B/16，每帧 768 维。每个 token 由帧嵌入与其时间差拼接而成：$[\phi(o_{i_j}),\ \phi(o_{i_j})-\phi(o_{i_{j-1}})]\in\mathbb{R}^{1536}$（$j=0$ 的差设为 0）。token 投影到 transformer 维度、加固定 sinusoidal 位置编码、过 12 层双向 Transformer encoder，末端线性层映射到各自的概率分布。

### 3.5 WARP-BC / 从逐帧速度到 chunk 加权

**Velocity Aggregation（聚合）**：以 canonical stride $S$ 秒、每次只平移一个 source-frame 的 overlapping windows 跑 WARP-RM。窗口内对相邻期望累计进度做差分并缩放，得 intra-window 速度 $v_j=(N-1)(\hat y_j-\hat y_{j-1})$。episode 里每个内部 source-frame $t$ 被多个重叠窗口覆盖，最终逐帧速度 $\hat v_t$ 取所有覆盖它的 $v_j$ 的**均值**。

**Action Chunk Weighting（加权）**：策略预测 1 秒的 action chunk。用 chunk **末帧**速度 $\hat v_{\text{end}}$ 计算 RA-BC 权重：

$$
w(s,a) = \hat v_{\text{end}}\cdot\mathbb{1}[\hat v_{\text{end}} > \tau] \tag{4}
$$

$w=0$ 的 chunk 在训练**前**就被过滤掉（避免缩小有效 batch size，遵循 advantage-filtered BC）。这里 $\hat v_{\text{end}}$ 是 advantage 的**经验代理**（进度速度），而非带 value baseline 的显式 RL advantage。最终策略损失是标准 flow-matching 损失、按样本权重加权：

$$
L_{\text{BC}} = \mathbb{E}_{(s,a)\sim D}\big[w(s,a)\cdot L_{\text{flow}}(\pi_\theta; s,a)\big] \tag{5}
$$

**这一节读法**：Eq.(4) 里两个决定后面都被消融证明是"必要选择"——用**末帧**而非 chunk 均值（避免瞬时尖峰掩盖倒退）、用**连续**而非二值权重（按进度大小放大损失）。$w=0$ 预过滤则解释了 Table 1 里"Act. Chunks Kept"只有 22–36%——WARP-BC 是**在更少数据上训**却更强。

## 方法细节 / 关键超参一览

| 组 | 符号 / 名称 | 取值 |
| --- | --- | --- |
| 采样器 | 窗口长 $N$ | 32 帧 |
| 采样器 | canonical stride $S$ | 1.5 s（30 Hz 下 45 帧）|
| 采样器 | AR(1) 自相关 $\alpha$ | 0.5 |
| 采样器 | log-速度边缘标准差 $\sigma_\infty$ | $\ln 2$ |
| 采样器 | 反转率 $\lambda_{\text{rev}}$ | 1（Poisson）|
| 采样器 | 整体反向概率 $p_{\text{flip}}$ | 0.5 |
| 目标 | 帧率 $f$ / 归一化 $C_{\text{norm}}$ | 30 Hz / $(N-1)Sf=1395$ source-frames |
| 目标 | 输出 bin | 30 个，中心线性布于 $[-3,3]$；两热编码 |
| 架构 | backbone $\phi$ | 冻结 DINOv3 ViT-B/16，768 维，输入 $224\times224$ |
| 架构 | encoder | 12 层 / 8 头 / 768 维，双向自注意力，dropout 0.15 |
| 优化 | optimizer / lr / batch / steps | AdamW / peak $4\times10^{-4}$ / 1024 windows / 15000 |
| 策略 | backbone / chunk | $\pi_0$ flow-matching / $H=30$ source-frames（1.0 s）|
| 过滤 | 阈值 $\tau$ | 1.0（只加权高于参考专家节奏 $\hat v_{\text{end}}>1$ 的 chunk）|

**要点**：一个 WARP-RM **训一次就跨所有 tier 复用**——它只在固定参考子集 $D_{\text{RM}}$（1,950 条最短、$\le59.8$ s 的演示）上训，给出 canonical 执行节奏 $\hat v=1$ 的干净参考信号。bottle 任务的 WARP/WARP-RM 超参与 T-shirt **完全一致**，只换训练数据。

## 实验

### Setup / 平台、任务、数据分层

- **平台**：bimanual **I2RT YAM** 机械臂。所有 footage 30 Hz。
- **任务 1（T-shirt folding，主任务）**：从料箱里取出揉皱衬衫 → 铺平 → 两袖内折 → 对折两次 → 移到工作区左上角。240 s 内未完成算失败（该预算 = 2× 最长训练演示）。TTC 只对成功轨迹计；throughput = 每小时成功折叠数，失败按 4 min 超时计入分母。用不同颜色、训练中未见的中号 T-shirt，每策略 20 trials。
- **任务 2（bottle-in-bin）**：把 4 个塑料瓶放进箱，90 s 超时，每策略 20 trials（共 80 瓶）。
- **数据分层**（都是单一大数据集按 episode 长度过滤的子集，长度作为 sub-optimality 的粗代理）：

| Dataset / Tier | 描述 | Episodes | Total hours |
| --- | --- | ---: | ---: |
| $D_1$ | 策略训练，$\le60$ s | 2,427 | 36.1 |
| $D_2$ | 策略训练，$\le90$ s | 4,124 | 71.3 |
| $D_3$ | 策略训练，$\le120$ s | 6,473 | 139.7 |
| $D_A$ | 标注数据（SARM 训练用）| 867 | 13.9 |
| $D_{\text{RM}}$ | WARP-RM 训练，$\le59.8$ s | 1,950 | 28.7 |

$D_4=D_1\cup D_A$、$D_5=D_2\cup D_A$ 用于和需要标注的 SARM 匹配对照。消融都在 $D_2$ 上做。

### Cross-tier Results / 随数据变脏的鲁棒性（Table 1 + Fig.4）

![[papers/images/yu2026warp-rm/ttc_distribution.png|760]]

**Figure 4 / 成功轨迹的 TTC 分布（灰=Vanilla BC，蓝=WARP-BC）。** $D_1$：两者都 20/20，但 WARP-BC 的点云整体压到更低（均值 64s vs 114s）且更紧。$D_2$：vanilla BC 只剩 2 个成功点、都贴在 200s 高位；WARP-BC 19/20，均值 119s。$D_3$：vanilla BC **0/20**（无点），WARP-BC 14/20。这图证明的正是主线论点——**当训练集被放宽到吃进更多低效演示，vanilla BC 迅速崩溃，而按相对进度加权的 WARP-BC 保持稳健**。

Table 1（每格 = 20 trials）：

| Method | Metric | $D_1$ | $D_2$ | $D_3$ |
| --- | --- | ---: | ---: | ---: |
| Vanilla BC | Success ↑ | 20/20 | 2/20 | 0/20 |
| | Mean TTC (s) ↓ | 113.8 | 199.0 | N/A |
| | Thrput (/hr) ↑ | 31.6 | 1.5 | 0.0 |
| | Act. Chunks Kept | 100% | 100% | 100% |
| WARP-BC | Success ↑ | 20/20 | **19/20** | **14/20** |
| | Mean TTC (s) ↓ | 63.9 | 118.8 | 117.4 |
| | Thrput (/hr) ↑ | 56.3 | 27.4 | 16.3 |
| | Act. Chunks Kept | 35.7% | 34.4% | 22.5% |

三点读法：
1. **$D_1$（干净数据）**：两者都 100% 成功，但 WARP-BC 靠加权更果断片段把 TTC 从 113.8 压到 63.9 s，吞吐 1.78×——**即便数据干净，去掉犹豫段也提速**。
2. **$D_2$（中等变脏）**：分水岭。vanilla BC 崩到 2/20、吞吐 1.5/hr；WARP-BC 19/20、27.4/hr，$\sim$18× 吞吐。
3. **$D_3$（最脏）**：vanilla BC 全灭 0/20，WARP-BC 仍 14/20。作者定性观察：vanilla BC 在脏 tier 上常陷入"重复的局部微调"，一直 micro-adjust 到 240 s 超时。

### Matched Baseline Comparisons / 和四个筛选法对打（Table 2）

因 SARM 需人工标注 subtask 边界，所有方法在 $D_4/D_5$（并入标注专家演示 $D_A$）上比；其余基线把 $D_A$ 当无标注数据。

| Method | Metric | $D_4$ | $D_5$ |
| --- | --- | ---: | ---: |
| SARM | Success ↑ | 19/20 | 2/20 |
| | Chunks Kept | 78.5% | 66.6% |
| DemInf | Success ↑ | 19/20 | 18/20 |
| | Chunks Kept | 45.6% | 33.7% |
| SCIZOR | Success ↑ | 19/20 | 2/20 |
| | Chunks Kept | 77.9% | 66.7% |
| **WARP-BC** | Success ↑ | **20/20** | **20/20** |
| | Mean TTC (s) ↓ | 71.2 | 80.7 |
| | Thrput (/hr) ↑ | 50.6 | 44.6 |
| | Chunks Kept | 45.6% | 33.7% |

**核心规律**：保留越多 chunk 的方法在 $D_5$ 掉得越狠。SARM（保 66.6%）和 SCIZOR（保 66.7%）都在 $D_5$ 崩到 2/20——筛选不够 selective。DemInf 在匹配保留预算下稳（18/20），但 WARP-BC 在两 tier 上吞吐都更高。WARP-BC 在同样 33.7% 保留预算下做到 $D_5$ 20/20——说明**它保留的 chunk 质量更高**（不是保留更多，而是选得更准）。这条实证正好回勾 introduction 对"绝对进度/时间距离代理有对齐噪声"的批评。

### Ablations / 三个设计选择的证据（Table 3，$D_2$）

| 组 | Variant | Success | TTC (s) | Thrput | Kept |
| --- | --- | ---: | ---: | ---: | ---: |
| Weighting | $\tau=0$（不过滤）| 3/20 | 201.4 | 2.3 | 97.0% |
| | $\tau=1$, binary | 16/20 | 139.6 | 18.0 | 34.4% |
| | $\tau=1$, continuous **[WARP-BC]** | **19/20** | 118.8 | 27.4 | 34.4% |
| Aggregation | Mean $\hat v$ over chunk | 15/20 | 127.0 | 17.4 | 34.0% |
| | Mean $\hat v$, future offset | 14/20 | 124.2 | 15.9 | 34.3% |
| | Terminal $\hat v_{\text{end}}$ **[WARP-BC]** | **19/20** | 118.8 | 27.4 | 34.4% |
| Sampler | IID log-normal | 18/20 | 131.0 | 22.8 | 28.7% |
| | AR(1) process **[WARP-BC]** | **19/20** | 118.8 | 27.4 | 34.4% |

- **Weighting**：$\tau=0$（保 97%、不筛）只有 3/20——**过滤是刚需**。binary 与 continuous 用同一阈值、保留**完全相同**的 34.4% chunk，但 continuous 19/20 > binary 16/20——**连续加权按进度大小放大损失**，比单纯二值掩码强。
- **Aggregation**：末帧 $\hat v_{\text{end}}$（19/20）优于对齐 chunk 均值（15/20）和未来偏移均值（14/20）。作者解释：均值聚合（无论时间对齐与否）会让**瞬时高速尖峰掩盖同窗口内随后的倒退**；末帧聚合能更好隔离高优势段的边界——偏向保留进度的"leading edge"、对减速进入犹豫的"trailing edge"给更锐的截断。
- **Sampler**：AR(1) 平滑相关采样 vs IID log-normal。成功率只微增（19 vs 18），但吞吐增益更明显。原因：推理面对**时间连续**的视频流、执行速度平滑变化，AR(1) 在训练里 mimic 这种连续性；IID 采样产生更 erratic 的帧间隔分布，偏离下游推理分布。

### Bottle-in-Bin / 第二个任务的复现（Table 4 + Fig.5）

![[papers/images/yu2026warp-rm/bottle_time_per_bottle_distribution.png|760]]

**Figure 5 / 每瓶放置用时分布（灰=Vanilla BC 59/80，蓝=WARP-BC 74/80）。** 每个点是放一个瓶的用时（相邻两次落瓶的间隔），黑条是均值（15.9 s vs 11.3 s）。WARP-BC 不仅放得更多、更快，分布也更紧；vanilla BC 有明显的"慢放置"重尾。这图证明主任务之外的**跨任务可复现性**——同一套 WARP/WARP-RM 超参、只换数据，就在结构完全不同的抓放任务上重现增益。

Table 4：WARP-BC 放 74/80 瓶（vs 59/80），每瓶均时 11.3 s（vs 15.9 s），吞吐 237.8 vs 147.8/hr（1.6×），且只用 30.6% 的 action chunk。

## 图表索引与讲解

| 图 / 表 | 读图重点（证明什么）| 关联问题 |
| --- | --- | --- |
| Figure 1（ep 曲线）| 同一演示上 $\hat v_t$ 时正（果断推进）时零（停滞）时负（掉衣服/回退）——progress ≠ elapsed time。 | 为什么需要有符号的相对进度而非绝对时间轴。 |
| Figure 2（sampler）| 一条演示靠 AR(1) 变速 + Poisson 反转 + 50% 整体反向，就能造出覆盖慢放↔快进、正↔负的连续进度监督。 | 自监督信号从哪来，为何无需人工标注。 |
| Figure 3（arch）| 冻结 DINOv3 + temporal-diff token + 双向 Transformer + 30-bin 分类头 + 离散差分出速度；结构极轻。 | WARP-RM 如何从帧序列产出逐帧速度。 |
| Figure 4（TTC）| 数据放宽到 $D_2/D_3$，vanilla BC 崩（2/20、0/20），WARP-BC 稳（19/20、14/20）且 TTC 更低更紧。 | 对 suboptimal 数据的鲁棒性有多大。 |
| Figure 5（bottle）| 换任务、同超参：WARP-BC 74/80 且每瓶更快、分布更紧。 | 增益是否可跨任务复现。 |
| Table 1 | 逐 tier 成功率/TTC/吞吐/保留比；$D_2$ 处 $\sim$18× 吞吐分水岭。 | 增益随数据变脏如何演化。 |
| Table 2 | 保留 chunk 越多的方法（SARM/SCIZOR 66%+）在 $D_5$ 崩；WARP-BC 同 33.7% 预算下 20/20。 | 相对进度筛选是否比绝对/时间距离代理更 selective。 |
| Table 3 | 过滤必需（$\tau=0$→3/20）；continuous>binary；terminal>chunk-mean；AR(1)>IID。 | 每个设计选择各贡献多少。 |
| Table 4 | bottle 74/80 vs 59/80，均时 11.3 vs 15.9 s，1.6× 吞吐。 | 第二任务的定量增益。 |

## 和你的论文库中其他条目的关系

- 对 [[@liu2026steam]]（STEAM，最近亲）：**几乎是同期同思路的姊妹工作**——都 label-free、都在 expert 演示的帧对上用 *normalized temporal offset* 当自监督信号、都为 mixed-quality rollout 打 frame-level advantage/progress。差异值得逐点对照：STEAM 训一个 **temporal-offset 预测器的 ensemble**、取 ensemble **最小** advantage 做**保守**打分，再配 CFGRL；WARP-RM 是**单模型**，但把信号做成**有符号的相对速度**（含反向播放的负进度）、用 AR(1) 平滑变速增广、并强调 **terminal-frame** 聚合 + 连续加权。可交叉追问：WARP 的"有符号相对速度 + 末帧 gating"与 STEAM 的"conservative ensemble min"哪种在 curation 上更稳、更省数据。（你的文献笔记里已标了这条对照意图。）
- 对 [[@wang2026wvm]]（World Value Model）：同样冲着"给 mixed-quality data 打 task-progression / value 分"这个目标，但路线正交——WVM 用 **world model backbone** 换掉 VLM 以获得时间建模能力、输出可泛化 value，还自带 Suboptimal-Value-Bench；WARP-RM 走**轻量自监督 + time-warp 增广**、不需大 backbone 也不需标注。可对照"progress/value 信号该由重型时序基础模型学，还是由一个巧妙的自监督增广逼出来"。
- 对 [[@li2026zr0]]（ZR-0）：二者共享 **$\pi_0$ / flow-matching action expert** 这一策略骨架（ZR-0 的 System 1、WARP-BC 的 policy backbone 同源）。区别在"从哪拿监督"：ZR-0 靠 dense ECoT reasoning 对齐跨 embodiment 表示；WARP 靠 progress reward 对 BC 损失做**数据侧**加权。可作"同一 flow-matching 策略，reasoning 监督 vs 数据 curation 两条正交增强"的对读。
- 对世界模型/规划一线（[[@wang2026orca]]、[[@gigaworld2026roadmap]]、[[@zhang2026qwen-robotworld]]、[[@gao2026fast-leworldmodel]]）：这些聚焦生成式世界建模/rollout；WARP-RM 提供一个**互补的"数据质量层"**——不预测未来，而评估已有演示每段的推进价值。若与世界模型联用，$\hat v_t$ 可作 rollout 段落的筛选/加权信号。
- 论文自身引用的近亲（**均不在当前库**，如需可另行入库）：ReWiND [21]、VIP [22]、LIV [23]（绝对进度基线）、SARM [25]、ARM [26]、SCIZOR [34]、DemInf [19]、Re-Mix [33]（数据筛选/奖励基线）、DINOv3 [40]（冻结 backbone）、$\pi_0$ [2]（策略骨架）、advantage-filtered BC [41]。

## 可追问点

1. **负进度全靠反向播放近似**（作者自陈借自 ReWiND，且承认反向可能 physically implausible）。这种合成的"倒退"是否真能训出对下游 filtering 有用的表示？在有真实失败/recovery 段的数据上，合成负进度 vs 真实负进度谁更该被信任？
2. **T-shirt 的 2D 图像面积可能是强隐式进度代理**（衣服铺开面积单调增）。作者也把这列为局限——在**缺乏这类视觉线索**的任务（如透明/小位移/遮挡严重）上，WARP-RM 还能否给出可靠 $\hat v_t$？bottle 任务算不算一个反例（它靠"落瓶事件"而非面积）？
3. **末帧聚合 $\hat v_{\text{end}}$ 对 chunk 边界敏感**：chunk 只有 1 s（30 帧），若一次关键推进恰好横跨两个 chunk 边界，末帧 gating 会不会误杀？消融里 chunk-mean 明显更差，但有没有介于二者之间的（如末段加权均值）？
4. **$\tau=1$ 把阈值锚在"参考专家节奏"上**，而参考子集 $D_{\text{RM}}$ 是"最短最快"的演示。这个锚点会不会系统性偏向"更快"而非"更好"？在需要谨慎慢动作的接触任务上是否会误筛？
5. **单一 bimanual 平台、两任务、$n=20$**：作者自己在脚注提醒 19/20 与 20/20 落在 binomial 采样噪声内。跨 embodiment / 更多任务类型（尤其非可形变、强接触、多阶段循环）上的可迁移性仍是开放问题。
6. **保留比只有 22–36%**却更强，说明大量数据被丢。这些被丢的 chunk 里有多少是真正"有害"、多少是"中性但可用"？在数据本就稀缺的场景，这种激进过滤是否还划算？

## 我的阅读笔记

这篇的真正价值不在"又一个 progress reward 做 curation"，而在它把问题从 **"这一帧完成度是多少（绝对）"** 干脆重构成 **"这一小段把任务推进了多少、朝哪个方向（相对）"**。这个转向一举绕开了 long-horizon teleop 里最脏的一块——cross-demonstration 时间对齐噪声。而它给出的自监督手段（time-warp 增广：AR(1) 平滑变速 + Poisson 反转 + 50% 整体反向）非常巧：**一条成功演示就能吐出覆盖慢放到快进、正到负的连续监督**，不需要任何人工标注，也不需要重型 backbone。Table 2 里"保留 chunk 越多的方法在 $D_5$ 崩得越狠、而 WARP-BC 同预算下 20/20"这一条，是全文最有说服力的一击——它把"绝对进度/时间距离代理不够 selective"从一个论断变成了可测的对照。

但要清醒看边界。第一，**负进度是合成的**（反向播放），作者自己都不担保它对下游有用、并明确让人在自己任务上验证——这意味着 WARP 在"负进度"半轴上的可靠性是个经验问题而非理论保证。第二，**T-shirt 的面积单调性可能替方法背了不少书**，真正的压力测试应该在缺视觉进度线索的任务上；bottle 任务算半个反例，但它仍是"事件明确（落瓶）"的任务。第三，**评测规模**：单平台、两任务、$n=20$，作者的脚注很诚实——很多 19/20 vs 20/20 的差别本就在采样噪声内，所以我更看重 **throughput/TTC** 而非成功率本身，而吞吐上的 1.6–18× 增益确实是稳的信号。

我会把它作为 **"自监督进度/优势信号用于数据 curation"** 这条线的一个锚点，和 [[@liu2026steam]] 并排读——两者用的自监督内核（预测帧间 normalized 时间偏移）几乎一样，但一个走"单模型 + 有符号相对速度 + 末帧 gating"、一个走"ensemble min 保守打分 + CFGRL"，正好构成同一想法的两种工程实现，适合直接 A/B 式对照。再往上，可与 [[@wang2026wvm]] 交叉：一个用巧妙增广逼出轻量 progress 信号，一个用 world-model backbone 学重型可泛化 value——"进度/价值信号该轻该重"是这条线值得持续追的分歧点。
