---
tags:
  - bilingual-reading
  - deep-reading
paper: "[[@gigaworld2026roadmap]]"
source_pdf: "[[papers/pdfs/gigaworld2026roadmap.pdf]]"
images: "papers/images/gigaworld2026roadmap/"
image_index: "[[papers/images/gigaworld2026roadmap/index.md]]"
created: 2026-07-05
reading_mode: 生成式精读（逐节读原文 + 读图）
---

# GigaWorld-1: A Roadmap to Build World Models for Robot Policy Evaluation

paper:: [[@gigaworld2026roadmap]]
pdf:: [[papers/pdfs/gigaworld2026roadmap.pdf]]
images:: [[papers/images/gigaworld2026roadmap/index.md]]

> 阅读提示：本文是 GigaAI + Tsinghua 于 2026-07-02 放出的 **roadmap / technical report**（全长约 43 页），不是单点算法论文。它的骨架是「一个新问题（world model as policy evaluator）+ 一个 benchmark（WMBench）+ 一套受控实验（3 个问题 / 10 个 Finding）+ 一个据此实现的模型（GigaWorld-1）」。读它要盯的不是某个 SOTA 数字，而是它论证的**因果链**：什么样的 world-model 设计才是可靠的策略评估器。

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| world model as policy evaluator | 世界模型作为策略评估器 | 本文的"第一类研究问题"：让 world model 反复接收 policy 的动作、预测未来观测，从而**替代真机 rollout 来判断一个 policy 会不会成功**。区别于 world model 作为 data engine / policy / interaction env / value critic 这四种既有范式。 |
| WMBench | WMBench 基准 | 本文构建的评估器基准：2,989 条配对轨迹、8 个任务族，含真机遥操作数据 + 多个 policy checkpoint 的 rollout 数据（成/败各半），也是 CVPR 2026 GigaBrain Challenge World Model Track 官方数据集。 |
| WMES (World Model as Evaluator Score) | 世界模型评估器分数 | 4 级序数标注（0/1/2/3），把"结果对不对（outcome）"和"画面保不保真（fidelity）"两个维度**解耦**：Score 3=结果对且高保真，Score 0=结果错且崩坏。是全文所有相关性分析的 ground truth。 |
| evaluator-world agreement $\rho$ | 评估器-真机一致性 | 全文核心量：$\rho=\mathrm{Corr}(S_{\text{real}}(\pi),S_{\text{wm}}(\pi))$，即 world-model 预测的成功率与真机成功率在一组 policy 上的相关。评估器好不好，最终看它。 |
| action-faithful rollout | 动作忠实的 rollout | 本文反复强调：好评估器的关键不是"画面漂亮"，而是**长时程里机器人/物体轨迹是否忠实跟随输入动作**。视觉上合理但动作不忠实的 rollout 是评估器杀手。 |
| degenerate metric | 退化指标 | 本文点名的陷阱：Background/Photometric Consistency 这类"外观稳定性"指标，**一个完全静止的视频就能刷高分**却完全无视动作，因此与 WMES **负相关**——用它排名会奖励坏 world model。 |
| EE pose map / ray map control | 末端位姿图 / 光线图控制 | 统一的 pixel-aligned 动作接口：head 视角（相机近似静止）用投影到像平面的**末端执行器位姿图**编码操作意图；wrist 视角（相机随臂运动）用**光线图**编码相机几何。二者 width 维拼接成统一控制图。 |
| channel-concat control | 通道拼接控制 | Finding 9 的胜出接口：把控制 latent **从去噪第一步就与噪声视频 latent 通道拼接**，比 cross-attention / ControlNet 都更能保证轨迹忠实（Traj.Acc 0.3528 vs 0.1620 / 0.2566）。 |
| hierarchical history + first-frame anchor | 分层历史 + 首帧锚点 | 长时程记忆模块：短/中/长三尺度时序记忆 $H^{(S)},H^{(M)},H^{(L)}$ 保运动与场景，外加一个**永不驱逐的首帧 latent** $x_{\text{anchor}}$ 防止 identity/color/scene 漂移。 |
| Relative RoPE | 相对旋转位置编码 | 每个自回归步都对"历史+当前窗口"重建局部时间坐标 $\{0,\dots,T_h+T_f-1\}$，使模型在训练/推理时总看到同一段位置分布，抑制长 rollout 的重复运动与时间不稳。 |
| GigaData / PhysData | Giga 机器人数据 / 泛物理视频 | 两类训练语料：GigaData 是标定过的自采机器人演示（最贴测试域）；PhysData 是互联网+物理视频（提供广义世界知识）。Finding 7 的结论：GigaData+PhysData 是最佳折中。 |
| Giga DataCrafter | Giga 数据加工器 | 数据管线：为每段清洗后的视频自动产出三路结构化监督——语义掩码（SAM2）、深度（Depth Anything 3）、fast–slow 语言描述。 |
| DMD2 distillation | DMD2 少步蒸馏 | 默认必做的加速：把多步自回归 teacher 蒸成 few-step student，结合分布匹配+score consistency+对抗监督（Eq.43）。ODE 蒸馏只作可选 warm start。评估器要跑海量 rollout，必须快。 |
| GigaWorld-1-Nano / -Plus | Nano(1.3B) / Plus(5B) | 最终模型两个规模，均基于 Wan backbone。Plus AVG 0.6834、Nano 0.6717，双双超过所有开源基线。 |
| VLM-assisted evaluator | VLM 辅助评估器 | LoRA 微调的 Qwen3-VL-8B，用 score-focused token 加权损失，从三视角 rollout 视频预测 WMES + 证据化理由；与人工标注 87.80% 精确一致，替代昂贵人工。 |

## 论文主线

**核心问题**：机器人基础模型（VLA、world-action model 等）越来越强，但**评估**成了主要瓶颈。LLM 可以拿新 checkpoint 秒刷数字基准，机器人 policy 却要在真机上反复 rollout——OpenVLA 报告 2,500 次 rollout 要 100 个人工小时，且真机连"每次复位到同一初始态"都做不到。经典仿真便宜可复现，但有 sim-to-real gap 和逐场景数字孪生的高昂建模成本。于是有人提出用 **world model 当 policy 的代理评估器**：让 policy 在学出来的环境里闭环 rollout，看它保不保留真机上的成/败结论。

**动机与缺口**：现有文献大多只证明了"world model **能**用来评估"（proof-of-concept），却回避了更根本的科学问题——**到底哪些设计，才让一个 world model 成为可靠的策略评估器？** 本文明确不去"再交一个新评估器 + 报一个 headline 数字"，而是问三个具体问题：

1. 除了通用视频质量指标，**该如何系统地判断**一个 world model 是不是好评估器？
2. **预训练与训练数据**如何影响评估器质量？
3. 哪些**架构/算法设计**最强地决定评估器可靠性？

**核心观点（三条 insight，全文反复回勾）**：

- **评估器质量由"长时程、动作忠实的 rollout 一致性"主导，而非短时视觉真实感**。强短视频生成器不一定是强评估器；autoregressive 反复反馈会让小误差累积，最终翻转 policy 层面的结论。
- **预训练收益不只来自数据规模，更来自"通用世界知识 ↔ 机器人可控性"的平衡**。更大的模型不自动更好；关键是预训练里有没有**可迁移的物理先验**能适配 robot-conditioned 预测。
- **架构选择（动作编码、记忆设计、面向评估的后训练）强烈决定与真机行为的对齐**。动作必须走**空间对齐**接口注入；长时程必须有**持久记忆**。

作者把这些提炼成一张 data→model→evaluation 的 design map，并落地成 **GigaWorld-1**：在核心 evaluator-alignment 指标上比最强基线（Wan 2.2 5B）相对提升 **14.9%**，并全量开源代码/模型/数据/工具。

阅读时要盯住一句话：**本文的贡献不是"world model 能评估 policy"（前人已证明），而是把"什么设计让它可靠"从直觉变成了可测的经验规律**——每个 Finding 都是一条"××指标/××数据/××架构，对/错"的可验证结论。

## 贡献与结论对照

| 论文声称的贡献 | 方法/证据位置 | 关键证据 | 结论强度 |
| --- | --- | --- | --- |
| 把 **world model as policy evaluator** 立为第一类研究问题，并识别决定"能否预测 policy 质量"的核心因素。 | §1–§3，Eq.(1)–(4)，Fig.2。 | 定义评估器目标为 $\rho=\mathrm{Corr}(S_{\text{real}},S_{\text{wm}})$；区分于 data engine/policy/interaction env/value critic 四范式。 | 问题定式清晰、有区分度；但"评估器"这一角色仍以视频类 world model 为主，未含结构化/3D 混合方案。 |
| 提出 **WMBench**：真机遥操作 + policy rollout 配对基准，配 WMES 序数标注。 | §4，Fig.3、Fig.6。 | 2,989 配对轨迹 / 8 任务；324,000 rollout 段人工标注（>100 队伍）；HF 数据集 >50,000 下载。 | 规模与协议扎实（episode-disjoint、outcome-balance）；但 8 任务族未覆盖移动操作/灵巧手/安全关键。 |
| 系统经验研究：评估器可靠性如何依赖**指标设计 / 预训练与数据 / 架构**。 | §5，Findings 1–10，Tables 1–4 / Figs 4–5。 | 视觉+几何主导 WMES（$\rho$=0.78/0.71）；外观稳定性负相关（−0.45/−0.42）；channel-concat 控制、hierarchical memory 显著更优。 | 本文最扎实的一环，多为受控对照；部分结论（AgiBot 反而拉低）依赖当前 GigaData 中心设定。 |
| 汇成 design map 并实例化为 **GigaWorld-1**（12000+ 小时数据训练）。 | §6，Tables 5–10，Figs 7–17。 | Plus(5B) AVG 0.6834 / Nano(1.3B) 0.6717；比 Wan 2.2 5B 相对 +14.9%、比 Cosmos-Predict2.5 +11.6%。 | 增益集中在 JEPA/Trajectory/Semantic；closed-loop 仍有"乐观偏置"（对 contact-sensitive 失败预测偏成功）。 |

## 摘要与核心贡献

摘要开门见山：评估具身机器人基础模型仍是**关键瓶颈**；LLM 靠数字基准高效评估，机器人 policy 却要**慢而贵的真机 rollout**，受限于硬件与人工监督——这催生了用 **world model 当代理评估器**的兴趣，但"让一个 world model 可靠地用于策略评估"的关键属性**仍知之甚少**。

本文的回答是一个系统研究 + 一个基准 **WMBench**（从真机遥操作数据与匹配的 policy rollout 构建，覆盖多样操作任务），用于在**模型家族、动作编码、rollout 时程、评估指标**之间做受控对比。基于 WMBench，作者分析了 **7 个视频 world model、4 种动作表示、324,000+ 条模拟 rollout（与真机执行配对）**，再用 **CVPR 2026 GigaBrain Challenge** 的大规模社区提交、精选合成轨迹、以及 **12,000+ 小时训练视频**来丰富分析。

三条核心 insight（见"论文主线"），据此导出一张实用 design roadmap，并落地为 **GigaWorld-1**——一个专为 policy evaluation 优化的 world model；相较有竞争力的 SOTA 基线，evaluator-alignment 指标提升 **14.9%**，且**全量开源**。

> 读原文才看清的数字口径：**"14.9%" 是相对提升**（relative），不是绝对分或百分点。它 = GigaWorld-1-Plus 的 AVG 0.6834 相对 Wan 2.2 5B 的 0.5948，即 $(0.6834-0.5948)/0.5948\approx14.9\%$；对 Cosmos-Predict2.5（0.6123）则是 $\approx11.6\%$（§6.5.1 / Table 9）。引用时别写成"绝对高 14.9 分"。

> 标题口径提醒：库内笔记曾记录 PDF metadata 一度显示 `GigaBrain-0`。以正文标题页为准，本报告真实标题是 **"GigaWorld-1: A Roadmap to Build World Models for Robot Policy Evaluation"**（GigaAI + Tsinghua University，2026-07-02，Project Page: open-gigaai.github.io/giga-world-1）。

## 按原文 section 逐节精读

### 1. Introduction / 为什么"评估"是机器人基础模型的主瓶颈

作者把 LLM 与机器人评估的**结构性差异**讲得很直白：LLM 的 checkpoint 可以低开销地在标准化基准上评估，评估几乎不构成瓶颈；机器人却需要在物理硬件上反复 rollout、持续人工监督、长时间占用机器人——**评估反倒成了制约 policy 进步的第一瓶颈**。经典仿真能部分降本，但受 sim-to-real gap 与逐场景数字孪生开销限制。World model 提供了一个"中间地带"：它能学到丰富视觉动力学、一定程度的可控物理演化，若能与 policy 交互并**准确保留其 rollout 的相对成/败**，就能当高效评估器。

本节最重要的一句立场：现有工作大多停在"world model **can** be used for evaluation"，本文要回答"**which designs are reliable**"。它把目标从 proof-of-concept 推向 principled design rules，并聚焦上面三个问题。四点贡献见"贡献与结论对照"表。

### 2. Related Work / 四种 world-model 范式，以及"评估器"这个缺口

作者把机器人 world model 归为**四种既有范式**，这是理解本文定位的关键坐标系：

1. **data engine**：生成大规模多样合成数据以扩训 policy；
2. **policy**：把预测动力学直接接进动作生成回路，做端到端控制器（← [[@wu2026tactile-wam]] 属于此类）；
3. **interaction environment**：提供学出来的、视觉丰富的闭环规划/RL 测试场；
4. **value critic**：评估观测、给长时程 return 估计，引导动作选择与 RL bootstrap（← [[@wang2026wvm]] 属于此类）。

作者的论点是：**这四种范式都没直接回答"world model 能否当可靠的 policy evaluator"**——一个判断"某 policy 在真实视觉与物理动力学下会不会完成任务"的外部机制。这个区分正是本文的立足点。2.3 节进一步把 policy evaluation 从"真机测试（最可信但慢/贵/难 scale）→ 经典仿真（便宜可复现但有 sim-to-real gap）→ world-model 评估器（可 scale + 更高视觉/物理真实感）"排成一条谱系。

### 3. Preliminaries / 把"评估器"形式化

policy $\pi$ 接收观测 $o_t$、可选状态 $s_t$、指令 $l$，输出动作 $a_t=\pi(o_t,s_t,l)$。真机评估得到轨迹：

$$
\tau_{\text{real}} = \{(o_t, s_t, a_t)\}_{t=1}^{T}\tag{1}
$$

当用 world model $M_\theta$ 当评估器时，policy 改为与**学出来的环境**交互：给定初始观测/指令/可选状态，模型在 policy 动作条件下预测未来观测：

$$
\hat{o}_{t+1:t+H} \sim M_\theta(\cdot \mid o_{\le t}, s_{\le t}, a_{\le t}, l)\tag{2}
$$

迭代得到 world-model 轨迹 $\tau_{\text{wm}}=\{(\hat{o}_t,s_t,a_t)\}_{t=1}^{H}$（Eq.3）。**评估器的职责不是生成"看起来合理"的观测，而是保留真实轨迹里与决策相关的属性**：对一组 policy $\{\pi_i\}_{i=1}^N$，我们关心 world-model 分数是否保留了真机上的 ranking、success prediction、risk profile。于是把主评估目标定义为 world-model 与真机结果的一致性——ranking 相关：

$$
\rho = \mathrm{Corr}\!\left(S_{\text{real}}(\pi),\ S_{\text{wm}}(\pi)\right)\tag{4}
$$

$S_{\text{real}}$/$S_{\text{wm}}$ 分别是 policy $\pi$ 的真机/world-model 预测成功率，跨 policy、checkpoint、task、rollout 条件评估。**这个 $\rho$ 是全文的中心量**：后面所有指标分析，本质都在问"某自动指标能不能像 $\rho$ 那样排出对的模型"。

### 4. WMBench / 一个专测"评估器"的基准

#### 4.1 Data Source / 数据来源与清洗

- **配对语料**：2,989 条配对轨迹、8 个任务（含刚性与可形变操作），来自两个互补源——(a) 覆盖多种操作与相机视角的**真机遥操作数据**；(b) 由 GigaBrain checkpoint 产生、**含成功也含失败**的 **policy-rollout 数据**，遥操作与 rollout 比例接近 **1:1**。
- **划分三原则**：**episode-disjointness**（测试轨迹不与训练重叠）、**diversity preservation**（压泛化而非记忆）、**outcome balance**（区分视觉相近的成/败）。清洗后训练集 **82,470 秒**、测试集 **7,200 秒**。
- **保守清洗**：移除损坏/截断视频、相机失同步、缺机器人状态、控制时间戳无法对齐观测的片段；人工核验后仍模糊的结果标签剔除；近重复遥操作轨迹折叠去冗余。
- **大规模标注 rollout 集**：从 CVPR 2026 挑战赛 >100 个参赛队的提交里采样 **324,000 段** world-model rollout，闭环链接成完整长时程 episode（每条约 **20–30 段**），再人工按 4 级序数标注为 **WMES**。

**WMES（World Model as Evaluator Score）** 把两个维度解耦：

- **Score 3**（结果对 & 高保真）：预测的成/败与真机一致，且动作/物体状态高度对齐、无明显畸变、物理与碰撞真实。
- **Score 2**（结果对 & 低保真）：最终结果对，但中间生成有瑕疵（物体畸变、非真实物理、轨迹轻微错位）。
- **Score 1**（结果错 & 高保真）：**没预测对结果**（真成假败或反之），但视频本身视觉/时间稳定、手臂大体跟随动作。
- **Score 0**（结果错 & 低保真）：完全对不上结果且严重崩坏，动作与物体状态视觉不稳、高度畸变或物理无意义。

每段由 **3 名标注员独立打分 + 1 名 senior 随机抽检**。HF 上该数据集累计 **>50,000 下载**。

#### 4.2 Evaluation Protocol / 四步闭环协议（Fig.3）

模仿"world model 当评估器"的真实部署：**Step 1** 真机 policy 数据收集（记录初始观测、指令、多视角 rollout 视频、人工成功标签）；**Step 2** world model 在指定训练集上训练，测试 episode 的物体布局与初始态严格 hold out（考泛化而非记忆）；**Step 3** 从 hold-out 测试 episode 首帧起，policy 出动作→world model 据动作+当前状态预测多视角未来观测→反馈回 policy，闭环执行到任务终止；**Step 4** 用 §4.3 指标体系评估，双流并行：(1) 算捕捉视觉保真与物理运动的**自动指标**，(2) 用 hybrid evaluator（人工或 VLM）评**最终 WMES**。

#### 4.3 Metric System / 把"结果评估"与"rollout 诊断"分开

指标体系把 **outcome evaluation（WMES）** 与 **rollout diagnostics** 分离；诊断指标从 **WorldArena** 选子集，分三族：**frame & representation fidelity**（Image/Aesthetic Quality、JEPA Similarity、Subject/Background Consistency、Photometric Consistency）；**geometry, semantics & interaction**（Geometry Accuracy、Perspectivity、Semantic Alignment、Instruction Following、Interaction Quality、Trajectory Accuracy）；**motion & long-horizon rollout**（Dynamic Degree、Flow Score、Motion Smoothness、PSNR/FID/FVD）。其中 §6.5 汇总表主报 **六个核心诊断**：Aesthetic Quality、Image Quality、JEPA Similarity、Semantic Alignment、Subject Consistency、Trajectory Accuracy。

值得记住的实现细节：Instruction Following / Perspectivity / Interaction Quality 用 **Qwen3-VL** 当 judge；Semantic Alignment 先用 Qwen2.5-VL 生成结构化描述再算归一化 CLIP-text 相似度；Trajectory Accuracy 用 SAM-style 分割抽机械臂 bbox → 中心轨迹 → **NDTW（归一化 DTW）** 与参考轨迹比对；Subject/Background Consistency 带 **dynamic-degree penalty** 以防"近静止 rollout"骗高分。

### 5. What Matters / 三个问题、十个 Finding（全文的实证核心）

#### 5.1 Question I：评估器质量该怎么测？

对提交的自动指标 $m$ 与 ground-truth WMES $c$，在有效提交集 $\Omega_m$ 上用 pairwise deletion 算 Pearson 相关：

$$
\rho(m, c) = \frac{\sum_{i\in\Omega_m}(m_i-\bar{m})(c_i-\bar{c})}{\sqrt{\sum_{i\in\Omega_m}(m_i-\bar{m})^2}\ \sqrt{\sum_{i\in\Omega_m}(c_i-\bar{c})^2}}\tag{5}
$$

用 10,000 次 non-parametric bootstrap 估 95% 置信区间；**上界低于 0 的指标记为 negative predictor**（分越高 WMES 越差）。指标组 $\mathcal{G}$ 的组级分是组内相关均值 $\rho(\mathcal{G},c)=\frac{1}{|\mathcal{G}|}\sum_{m\in\mathcal{G}}\rho(m,c)$（Eq.6）。

- **Finding 1：视觉与几何保真主导 WMES 预测。** 组级：Visual Fidelity $\rho=0.78$、Geometry $\rho=0.71$、Semantics $\rho=0.59$。单指标：**Subject Consistency $\rho=0.88$、Perspectivity $\rho=0.86$、Instruction Following $\rho=0.84$** 最强。而 **Semantic Alignment 单独只有 $\rho=0.11$**——高层语义标签若不捕捉 policy 相关的几何状态就不够用。
- **Finding 2：退化指标误导排名。** **Background Consistency $\rho=-0.45$、Photometric Consistency $\rho=-0.42$、Interaction Quality $\rho=-0.11$ 与 WMES 负相关**。前两者失败是因为**一个完全静止的视频就能刷高外观稳定性、却无视所有动作**；Interaction Quality 不可靠是因为它来自 VLM 对物理一致性的判断，而当前 VLM 还判不准细粒度物理真实。**不显式惩罚"忽略动作"、或判不准物理的指标，会偏爱退化 world model。**
- **Finding 3：评估器质量必须在长时程 rollout 下测，而非单步生成。** 自回归 rollout 会累积误差，最终翻转 policy 结论。作者按 chunk 在 **40 秒**上评 PSNR（多视角重建）+ FID/FVD。Wan/Cosmos/LTX/SVD 这类通用 backbone 常"短段合理→后段 viewpoint drift / object-identity collapse / texture accumulation"，**SVD 后期退化尤其严重**。
- **Finding 4：outcome-centric 监督是可 scale VLM 评估的关键。** LoRA 微调 **Qwen3-VL-8B-Instruct**（rank 16、scale 32、dropout 0.05，作用于 attention projection；rollout 2 fps、15–32 帧），用**结构化监督**把总 WMES 分与证据化理由（summary rationale + overall video quality / instruction following / physical adherence 的 aspect 级评估）耦合。因 rationale token 远多于 score token，采用 **token-type-aware 损失加权**：overall score token 权重 **8.0**、格式 token **1.0**、自由 rationale token 最低 **0.05**（长度自适应），防止冗长解释淹没优化目标。
- **Finding 5：VLM 评估器与人工近乎完全一致。** 在 **5,000+ 视频**上：**exact agreement 87.80%、adjacent agreement 99.16%**，仅 0.84% 差两级；MAE 0.1304、RMSE 0.3836、**QWK 0.7349**、Spearman 0.7574、Kendall $\tau_b$ 0.7507（Table 1）。→ VLM 可作 method-level WMES 的可靠代理，突破人工标注瓶颈。

#### 5.2 Question II：预训练与训练数据如何影响？

- **Finding 6：可迁移物理先验比原始规模更重要。** 因大厂预训练数据/管线通常不可得，作者改用一组开源 backbone 对比：**Cosmos-Predict2.5 最强（AVG 0.6123）**，说明 robotics+自动驾驶预训练带来有用物理先验；通用 backbone 里 **Wan 2.2 5B 最强（AVG 0.5948）**，且**超过更大的 LTX 2.3（22B，AVG 0.5775）**；CogVideoX 居中（0.5620）；**SVD 最差（0.5569），Trajectory Accuracy 仅 0.0926**。→ 大模型不自动是好评估器，关键是预训练先验能否适配 robot-conditioned 预测。
- **Finding 7：广义物理视频给出最佳整体折中。** 用 Wan2.1 1.3B 当 backbone 续训不同数据混合（Table 2）。**GigaData+PhysData 整体最好：平均 0.5654→0.6144（+0.0490）**，最大增益来自 **Photometric Consistency（+0.3074）**，兼有 Image Quality、Subject Consistency 小涨；虽然 JEPA/Semantic/Trajectory 略降，但 PhysData 恢复了通用世界知识、又保住了 GigaData 的任务相关偏置。
- **Finding 8：机器人专属数据主要提升 embodiment 保真，但折中更尖锐。** 加 AgiBot：0.5654→0.5940（+0.0286），增益更选择性——Subject Consistency +0.1401、Aesthetic +0.0367、Photometric +0.3031，但 **JEPA Similarity −0.2426、Trajectory Accuracy −0.1084 明显下滑**。→ 窄机器人域数据会 over-specialize 生成器、削弱结构/运动泛化；在当前 GigaData 中心设定下，**加广义物理视频更划算**。核心教训：评估器训练本质是**平衡问题**。

#### 5.3 Question III：模型设计如何影响？

- **Finding 9：动作控制必须走空间对齐接口注入。** 对比四种控制（Table 3）：无控制 Traj.Acc 0.1576；**cross-attention 仅 0.1620**（且拉低运动指标，说明 attention 侧动作 token 易被外观/语义 token 淹没）；ControlNet 0.2566（控制以空间特征进入，更强）；**channel-concat 控制最强，Traj.Acc 0.3528**，且 Dynamic/Smooth/Flow/Subject/Photo 全面第一。→ 最可靠的动作表示不只是"显式"，而是**从去噪一开始就与噪声 latent 空间对齐**。具体实现是 §6.2 的 pixel-aligned 表示：head 视角用 EE pose map、wrist 视角用 ray map，编码进共享控制 latent 后**贯穿自回归全程与噪声 latent 拼接**——在相机运动与物体运动易混淆的多视角设定下尤其重要。
- **Finding 10：可靠评估器需要持久记忆做长时程 rollout。** 迭代 rollout 有 temporal accumulation error：每个生成窗又成为下一步条件，小错被放大成大状态误差，对 policy 评估尤其致命。按 chunk 在 40 秒上评（Table 4）：在 Wan 2.1 1.3B 上**加记忆全区间大幅提升**——0–8s PSNR **19.82**（vs 无记忆 14.46）、FID **40.58**（vs 219.67）、FVD **35.30**（vs 197.46），到 32–40s 仍 PSNR 17.41 / FID 121.61。记忆实现为**分层 history buffer + 持久首帧锚点**（短/中/长时序记忆），既保原始场景 identity 又保近期运动上下文。

### 6. Final Design Map & GigaWorld-1 / 把经验落成模型

经验研究汇成一张 data→model→evaluation 的 design map：**数据层**平衡通用世界知识与机器人可控性；**模型层**暴露显式低级动作表示、保空间对齐、加记忆稳住长时程；**评估层**决定性目标是与真机 policy 成功的一致（ID 与 OOD 双设定），而非孤立的视觉真实。据此实例化 **GigaWorld-1**（Table 5 设计表）：Wan-[1.3B/5B] backbone、physical+开源机器人+egocentric+Giga 自采语料、质量/运动/分布过滤、语义掩码+深度+fast-slow caption 结构化监督、EE pose map + ray map 显式动作接口、first-frame anchor + 分层历史记忆模块、Relative RoPE、渐进多阶段训练。

**采用 Wan 而非 Cosmos 的理由**（§6）：二者都提供强预训练先验，但 Wan 是受控对比里**最强的通用开源 backbone**，且生态更成熟便于 redesign 与工程化。

#### 6.1 数据与 Giga DataCrafter

- **语料构成（Table 6，~12,980 小时，四来源）**：Physical Data（互联网/物理视频）**~1,298 h**；Open-source Robot Data（Open X、AgiBot）**~5,377 h**；Human-centric Data（EgoDex、SynData，egocentric 手部）**~2,411 h**；Giga-collected Data（Giga Humanoid、Giga Dual-arm）**~3,894 h**。覆盖 humanoid / dual-arm / single-arm / dexterous hand。
- **数据整流**：先 video-level 质量门，再语义过滤。质量向量 $q(x_i)=[s(x_i),e(x_i),n(x_i),c(x_i),b(x_i)]$（sharpness/exposure/noise/contrast/compression，Eq.7）→ 聚合分 $Q_{\text{img}}(v)=\frac{1}{K}\sum_i w^\top q(x_i)$（Eq.8）；时间完整性用相邻帧的直方图+embedding 差 $D_t=\lambda_h(1-\mathrm{sim}(h_t,h_{t+1}))+\lambda_\varphi(1-\cos(\varphi_t,\varphi_{t+1}))$（Eq.9）检测 scene jump/黑屏/掉帧与冻结片段；最终门 Eq.(10) 综合 $Q_{\text{img}},A(v),\max_t D_t,\mathrm{Var}_t(D_t)$。运动过滤：光流幅度 $M_t=\frac{1}{|\Omega|}\sum_u\|F_t(u)\|_2$（Eq.11），并用 jerk $J(v)=\frac{1}{T-2}\sum|M_{t+1}-2M_t+M_{t-1}|$（Eq.12）剔除高频抖动/不连续运动；再把标定动作图投影到帧上，用 VL verifier 查动作-观测一致性。
- **Giga DataCrafter（Fig.7）**：为每段视频产三路同步监督——**语义掩码**用 SAM2 得 $\mathcal{S}_t=\{(m_t^k,c_t^k)\}$（Eq.13）；**深度**用 **Depth Anything 3 (DA3)** 得 dense depth；**caption** 用 **fast–slow 系统**（fast 流出高频短时子任务描述如 reach/grasp/lift/place，slow 流出低频长时环境描述），$\mathcal{C}(v)=\{\mathcal{C}_{\text{short}}(v),\mathcal{C}_{\text{long}}(v)\}$（Eq.14），离线算一次缓存复用，省训练时反复调 VLM 的 GPU 开销。

#### 6.2 架构与控制接口（Fig.8）

三条原则：保住大预训练视频 backbone 的时空先验、经显式且几何对齐的接口注入动作、跨迭代 rollout 维持状态。**VAE、text encoder、backbone 主体冻结**，只训 LoRA adapter 与轻量控制通路。

- **自回归世界生成**：把固定窗双向去噪 backbone 改成 video-continuation。给历史 latent $X_{\text{hist}}=\{x_1,\dots,x_t\}$ 与未来窗 $X_{\text{future}}=\{x_{t+1},\dots,x_{t+T_f}\}$，学 $p(X_{\text{future}}\mid X_{\text{hist}},C)$（Eq.17，$C$ 为控制条件）；训练时未来窗被扩散腐化 $X_\tau=\alpha_\tau X_{\text{future}}+\sigma_\tau\epsilon$（Eq.18），网络预测 $\epsilon_\theta=f_\theta(X_\tau,H_t,C,\tau)$（Eq.19）；推理时每段生成 append 回 history，得因子分解 $p(X_{1:T}\mid C)=\prod_{k=1}^K p(X_k\mid H_{k-1},C)$（Eq.20）。
- **统一控制注入**：head 相机近似静止→未来主要由动作决定→用**EE pose map**（把未来末端轨迹投影到像平面，编码臂位姿+夹爪态）；wrist 相机随臂运动→变化主要来自视角→用 **ray map**（每像素存 world 坐标的 ray origin + 归一方向）。二者 width 维拼接 $C_t=\mathrm{Concat}_W(C_t^{\text{ee}},C_t^{\text{ray}})$（Eq.21），编码成 $Z_{\text{ctrl}}=E(C)$（Eq.22），自回归第 $k$ 窗取时间对齐段 $Z_{\text{ctrl}}^{(k)}$（Eq.23），去噪网络 $\epsilon_\theta=f_\theta(X_\tau,Z_{\text{ctrl}}^{(k)},H_t,\tau)$（Eq.24）**全程持续**注入对齐控制。
- **分层历史注入**：多尺度记忆 $H_t=\{H_t^{(L)},H_t^{(M)},H_t^{(S)}\}$（Eq.25，短保运动连续、中保动作演化/物体交互、长保全局布局/物体 identity），外加持久首帧锚点 $\tilde{H}_t=\{x_{\text{anchor}},H_t^{(L)},H_t^{(M)},H_t^{(S)}\}$（Eq.26）——**anchor 永不驱逐**，每步都能拿到原始外观统计。
- **分层历史引导注意力**：历史与噪声上下文统计不同、应区别对待——历史是"引导"而非"再生成"。self-attention 对拼接后的 $[Q_{\text{Noisy}},Q_{\text{Hist}}]$ 等做（Eq.29）；**cross-attention 只作用于当前噪声窗** $X_{\text{Cross}}=\mathrm{Attention}(Q_{\text{Noisy}},K_{\text{Task}},V_{\text{Task}})$（Eq.30），因历史已累积过语义、无需对历史 token 反复条件化任务描述；最终 $X=X_{\text{Self}}+X_{\text{Cross}}$（Eq.31）。
- **Relative RoPE**：每个自回归步对"历史+当前窗"建局部时间坐标 $\mathcal{P}=\{0,\dots,T_h+T_f-1\}$（Eq.32-33），旋转编码 $Q'_p=R(p)Q_p$（Eq.34）。局部位置每步重初始化、不依赖绝对时间戳，使训练/推理总看到同段位置分布，抑制长 rollout 的重复运动与时间不稳。
- **SLERP prompt 过渡**（Fig.9）：长视频跨阶段要平滑换语义。两 prompt embedding 夹角 $\theta=\arccos\frac{e_1^\top e_2}{\|e_1\|\|e_2\|}$（Eq.35），球面插值 $\mathrm{SLERP}(e_1,e_2,t)=\frac{\sin((1-t)\theta)}{\sin\theta}e_1+\frac{\sin(t\theta)}{\sin\theta}e_2$（Eq.36），沿 $t_i=\frac{i}{N-1}$ 采一串条件注入连续窗，比线性插值更保 embedding 角结构与长时程语义一致。

#### 6.3 渐进训练（Fig.10）

四阶段课程：**Stage 1 robot world foundation model**——从预训练 backbone 续训机器人语料，学双向机器人视频先验，flow-matching 目标 $\mathcal{L}_{\text{FM}}=\mathbb{E}[\|u_t-u_\theta(x_t,t)\|_2^2]$（Eq.39），不加自回归因果；**Stage 2 autoregressive world modeling**——用 Relative RoPE + 分层历史 + 首帧锚点 + 统一控制把双向模型转成 AR，$\mathcal{L}_{\text{AR}}=\mathbb{E}[\|\epsilon-\epsilon_\theta(X_\tau,H_t,C,\tau)\|_2^2]$（Eq.40），训练用真实历史、推理用生成窗，训推对齐是降累积误差的关键；**Stage 3 scene adaptation LoRA（可选）**——$W=W_0+BA$（Eq.41）适配具体工作单元；**Stage 4 few-step distillation**——ODE 蒸馏为可选 warm start $\mathcal{L}_{\text{ODE}}=\mathbb{E}[\|\hat{x}_0^{\text{teacher}}-\hat{x}_0^{\text{student}}\|_2^2]$（Eq.42），**DMD2 为必做**：$\mathcal{L}_{\text{DMD2}}=\lambda_{\text{dm}}\mathcal{L}_{\text{distill}}+\lambda_{\text{score}}\mathcal{L}_{\text{score}}+\lambda_{\text{GAN}}\mathcal{L}_{\text{GAN}}$（Eq.43）。超参见 Table 7（Stage1 LR 5e-5/rank128/13k steps；Stage2 LR 1e-4/rank256/36k steps；batch 32；32× NVIDIA H20）与 Table 8（ODE 3759 步、DMD2 2250 步）。

#### 6.4 系统效率

用自定义 kernel + 分布式替换 memory-bound 算子：**SageAttention**（drop-in 低精度注意力）、**TinyVAE（TAESD）** 预览解码（终评仍用全 VAE）、**Ulysses 序列并行**（沿 token 维分片，激活近似按 GPU 数下降）、**Flash Norm / Flash RoPE**（Triton 融合核）。推理基准（H20 96G，1920×480，99 帧）：注意力核优化单独 **1.25×–1.31×**；SageAttention + 6-step DMD2 + Ulysses 组合最高 **35.93× 加速**——这正是评估器"要跑海量 rollout"必须的速度。

## 方法细节

- **动作接口的核心洞见**：不是"是否显式给动作"，而是"动作是否从去噪第一步就空间对齐地进入 latent"。channel-concat > ControlNet > cross-attention（Traj.Acc 0.3528 / 0.2566 / 0.1620，Table 3）几乎是全文架构结论里最干脆的一条。
- **记忆的核心洞见**：长时程 rollout 的敌人是 identity/color/scene drift；对策是**多尺度记忆 + 永不驱逐的首帧锚点**。Table 4 显示这一个模块就能把 40s FID 从三位数压到两位数。
- **评估指标的核心洞见**：外观稳定性是"陷阱指标"——静止视频能刷高分却零动作忠实，故与 WMES 负相关；真正预测 WMES 的是 Subject Consistency / Perspectivity / Instruction Following（Finding 1-2）。这直接决定了 §6.5 汇总表**故意排除** Background/Photometric Consistency。
- **一个绕不开的因果点**：本文没有像分类论文那样报"成功率高多少"，而是报"world-model 成功率与真机成功率的对齐"。closed-loop 一致性（§6.5.5）比 replay 保真更严——replay 好不代表能评估 policy。

## 实验

**Setup**：所有 backbone 在 §6.1 同一 curated 语料上后训练、同一 rollout 协议评估；主汇总用六个核心 evaluator-relevant 指标（Aesthetic、Image、JEPA、Semantic、Subject、Trajectory）的归一化平均，**排除** Background/Photometric Consistency 这类会误导排名的外观稳定性指标。

**主结果（Table 9，AVG↑）**：

| Model | Size | Type | Aesthetic | Image | JEPA | Semantic | Subject | Trajectory | **AVG** |
| --- | :---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| SVD | 1.5B | General | 0.2861 | 0.6497 | 0.6454 | 0.8411 | 0.8267 | 0.0926 | 0.5569 |
| Wan 2.1 1.3B I2V | 1.3B | General | 0.3422 | 0.6856 | 0.6002 | 0.8705 | 0.5568 | 0.1576 | 0.5355 |
| LTX 2.3 | 22B | General | 0.3900 | 0.6967 | 0.5380 | 0.8678 | 0.8248 | 0.1479 | 0.5775 |
| CogVideoX | 5B | General | 0.3303 | 0.6775 | 0.6437 | 0.8633 | 0.6963 | 0.1609 | 0.5620 |
| Wan 2.2 5B TI2V | 5B | General | 0.3538 | 0.6980 | 0.5853 | 0.8789 | **0.8883** | 0.1643 | 0.5948 |
| Cosmos-Predict2.5 | 2B | Robot/Auto | 0.3491 | **0.7184** | 0.6781 | 0.8764 | 0.8747 | 0.1770 | 0.6123 |
| **GigaWorld-1-Nano** | 1.3B | Robot/Auto | 0.3538 | 0.6802 | 0.8911 | 0.8920 | 0.8600 | 0.3528 | **0.6717** |
| **GigaWorld-1-Plus** | 5B | Robot/Auto | 0.3534 | 0.6765 | **0.9337** | **0.8926** | **0.8883** | **0.3561** | **0.6834** |

**这张表要分三层读**：
1. **总分**：Plus(5B) 0.6834、Nano(1.3B) 0.6717，双双超过最强开源基线 Cosmos-Predict2.5（0.6123）与最强通用 Wan 2.2 5B（0.5948）——Plus 相对 +14.9%（vs Wan 2.2 5B）、+11.6%（vs Cosmos）。
2. **增益集中在 evaluator-critical 指标**：GigaWorld-1 在 **JEPA Similarity（0.9337，遥遥领先第二名 0.6781）** 和 **Trajectory Accuracy（0.3561 vs 基线普遍 0.15–0.18）** 上是决定性拉开，正对应 Question I 里"最能预测 WMES"的维度。
3. **它不靠刷外观分**：Aesthetic/Image Quality 上 GigaWorld-1 并不领先（Image 0.6765 甚至低于 Cosmos 0.7184）——恰印证本文立场：**好评估器不是画面最漂亮的，而是动作最忠实、结构最稳的**。

**长时程 rollout（Table 4，每 8 秒均值）**：GigaWorld-1（对应 Wan 2.1+Mem 行）在 0–40s 全区间 PSNR/FID/FVD 最优；0–8s PSNR 19.82 / FID 40.58 / FVD 35.30，到 32–40s 仍 PSNR 17.41 / FID 121.61 / FVD 98.34，而通用 backbone（SVD 尤甚，PSNR 从 14.05 崩到 6.88）后期严重退化。

**VLM 评估器一致性（Table 1，5,000+ 视频）**：Acc 0.8780、Adj.Acc 0.9916、Large Err 0.0084、MAE 0.1304、RMSE 0.3836、QWK 0.7349、Spearman 0.7574、Kendall $\tau_b$ 0.7507、W-F1 0.8744、|Bias| 0.0455。

**OOD 泛化（Fig.15）**：对容器颜色、物体内容（不同食物）、桌面纹理变化无几何崩坏；关键是第四行的 **action-outcome 泛化**——能同时模拟成功放置与失败（如洒出），这是可靠评估器的必需属性。

**闭环 policy 一致性（§6.5.5，Table 10 / Figs 16-17）**：4 个任务（put banana into basket / put green bowl into pink plate / fold paper boxes / pour fries into box）拆成子任务级 outcome check。GigaWorld-1 的 fitted line 比 challenge 基线更贴真机对角线（更好校准任务难度）；Success-rate bias（Fig.17）显示它 Gen−Real 偏差更小、更平衡，而 challenge 基线倾向**过度自信地预测成功**。作者诚实点名一个开放问题：**video generation 模型对 contact-sensitive 失败仍有"乐观偏置"**。

## 图表索引与讲解

> 本地 `papers/images/gigaworld2026roadmap/` 当前 **0 张抽图**（index.md 记为"未自动抽取到可用图片"）。以下据全文 Figure/Table caption 用文字说明其证明目标；需要真图时补跑 `python setting/scripts/extract_paper_images.py`。严禁凭空描述图内像素。

| 图 / 表 | 读图重点（证明什么） | 关联问题 |
| --- | --- | --- |
| Figure 1 | 全文体量海报：324,000 分析过的 rollout 视频、7 个 video world model、4 种动作表示、12,000+ 小时训练数据，导出 GigaWorld-1（AVG 0.683 > Cosmos2.5 0.612 > Wan2.2 0.595）。 | 本文规模与定位。 |
| Figure 2 | "world model as policy evaluator" 框架：world model 迭代接收 policy 动作、预测未来观测，配 VLM 判成/败——可靠评估既要视觉质量，也要 action-faithful 与真机结果一致。 | 评估器角色与四范式的区别。 |
| Figure 3 | WMBench 四步闭环协议：真机采集→严格划分训 world model→在 world model 内闭环 rollout→算指标+WMES 与真机对齐。 | 评估协议如何逼近真实部署。 |
| Figure 4 | 指标组与 WMES 的相关：Visual Fidelity 0.78 / Geometry 0.71 最强，Subject 0.88 / Perspectivity 0.86 / Instruction 0.84 领跑；**Appearance Stability −0.44 为负预测**。 | 哪些自动指标能替代人工排名，哪些是陷阱。 |
| Figure 5 | 全指标 Pearson 相关热图：印证 Subject/Perspectivity/JEPA/Instruction/Image/Aesthetic 与 WMES 强相关，Background/Photometric/Interaction 不可靠。 | 指标之间的冗余与可信度结构。 |
| Figure 6 | VLM-assisted 评估器：三视角 rollout + 任务 prompt → LoRA-Qwen3-VL 出 WMES + 证据化 aspect 评估（示例 Score 2）。 | 如何 scale 掉人工标注瓶颈。 |
| Figure 7 | 数据构建管线：多源过滤/平衡/自动标注（含 Giga DataCrafter）。 | 12,980h 语料如何被清洗成结构化监督。 |
| Figure 8 | GigaWorld-1 总架构：memory patchification + 时间对齐控制注入 + 分层历史引导 + Relative RoPE + LoRA；VAE/text encoder 冻结。 | 三条设计原则如何在一个 AR-DiT 里落地。 |
| Figure 9 | SLERP prompt 过渡：沿球面测地线插值文本条件，注入连续自回归窗，平滑换阶段（示例：抓 carton flaps→gripper 到位→压盖）。 | 长视频跨子任务语义如何不突变。 |
| Figure 10 | 训练流水：foundation → AR → optional ODE warm start → required DMD2；虚线为可跳过模块。 | 四阶段课程的必做/可选边界。 |
| Table 1 | VLM vs 人工：87.80% 精确 / 99.16% 相邻一致、QWK 0.7349。 | VLM 评估是否可信代理。 |
| Table 2 | 数据组成消融：GigaData+PhysData 平均 0.5654→0.6144（+0.0490）最好；AgiBot 使 JEPA/Trajectory 明显下滑。 | 加什么数据对评估器最有利。 |
| Table 3 | 控制接口消融：channel-concat Traj.Acc 0.3528 全面第一。 | 动作该怎么注入才轨迹忠实。 |
| Table 4 | 长时程质量：Wan2.1+Mem 全区间 PSNR/FID/FVD 最优（0–8s FID 40.58 vs 219.67）。 | 记忆对长 rollout 的决定性作用。 |
| Table 5 | GigaWorld-1 设计表（backbone/data/control/memory/RoPE/recipe）。 | design map 的成品配方。 |
| Table 6 | 语料总览：~12,980h，四来源占比。 | 训练数据规模与构成。 |
| Table 7 / 8 | 非蒸馏阶段与 ODE/DMD2 蒸馏的超参（32× H20）。 | 复现所需训练细节。 |
| Table 9 | 主对比表：Plus 0.6834 / Nano 0.6717 全面领先。 | GigaWorld-1 相对基线的核心增益来源。 |
| Table 10 / Fig.16-17 | 闭环一致性：4 任务子任务级校准，GigaWorld-1 更贴真机对角线、Gen−Real 偏差更小。 | replay 之外，能否真判 policy 成/败。 |
| Figure 11-15 | 架构对比雷达图、长时程动态曲线、长时程定性崩坏（identity/rank/sink collapse）、memory+SLERP 消融、OOD 泛化。 | 各设计模块的定量/定性证据。 |

## 和你的论文库中其他条目的关系

本文在 Related Work 里给出了一张极好用的坐标系——world model 在机器人里的**四种既有范式**（data engine / policy / interaction environment / value critic），并主张自己开的是**第五种角色：policy evaluator**。用这张坐标系串库最清晰：

- 对 [[@wu2026tactile-wam]]（Tactile-WAM，world model as **policy**，范式 2）：Tactile-WAM 把世界模型接进动作生成回路做控制器，还额外预测触觉接触状态；GigaWorld-1 则把世界模型当**外部裁判**去判 policy 成/败。二者恰是"world model 输出被当作 **action 条件** vs 被当作 **evaluation 结论**"的对照。有趣的是，GigaWorld-1 承认自己对 **contact-sensitive 失败有乐观偏置**（§6.5.5），而这正是 Tactile-WAM 用触觉去攻的地方——两篇合读能看清"接触信号在世界模型里既是控制难点也是评估难点"。
- 对 [[@wang2026wvm]]（World Value Models，world model as **value critic**，范式 4）：WVM 用世界模型的未来建模能力**给数据/进展打 value 分**；GigaWorld-1 用它**预测 rollout 的成/败一致性**。两者都在问"world model 除了生成画面还能输出什么可用信号"，一个输出 value、一个输出 evaluator agreement $\rho$；且 GigaWorld-1 的 VLM-assisted WMES 与 WVM 的价值/进展评分，本质都是"用大模型给 rollout 打可 scale 的分"。
- 对 [[@zhang2026qwen-robotworld]]（Qwen-RobotWorld，语言条件视频生成世界模型）、[[@wang2026orca]]（Orca）、[[@gao2026fast-leworldmodel]]（Fast LeWorldModel）（多偏 world-model 作为 simulator / interaction environment / data engine）：这些聚焦"把世界建得更可控、更快、更像"；GigaWorld-1 的独特追问是"**建得像不等于评得准**"——它用 Finding 2（外观稳定性负相关）、Finding 3（长时程才是评估器试金石）给这条路线提供了一个反例式的评估学论据。Fast LeWorldModel 关心"快"，与 GigaWorld-1 的 DMD2/Ulysses（35.93× 加速为评估器海量 rollout 服务）是同一工程动机的不同侧面。
- 对 [[@yu2026warp-rm]]（WARP-RM，面向数据整流的 relative progress reward model）：两者都在做"给 rollout / 轨迹打可靠的分"，只是层次不同——WARP-RM 是 reward/进展模型服务数据 curation，GigaWorld-1 是 evaluator 服务 policy 选型。可对照"reward 信号 vs evaluator agreement"两种打分范式的可靠性判据。
- 论文自身引用、**均不在当前库**（如需可另行入库）：GigaBrain [101]（产生 WMBench rollout 的 policy）、Cosmos-Predict2.5 [3] / Cosmos-3 [1]（最强机器人域 backbone 对照）、Wan 2.1/2.2 [109]（最终采用的 backbone）、WorldArena [96]（诊断指标来源）、V-JEPA [11]、Depth Anything 3 [60]、SAM2/SAM3 [93,18]、DMD2/Self-Forcing 系列、$\pi_{0.5}$ [43]、OpenVLA [50]、AgiBot/Galaxea/RoboMind 数据集等。

## 可追问点

1. WMES 把"结果对/错"与"保真高/低"解耦成 4 级，但 **Score 1（结果错却高保真）** 恰是最危险的评估器失效——一个看着稳、动作跟随、却把成败判反的 rollout。本文对"Score 1 占比"和"这类失败集中在哪些任务"没有单独拆分，值得追。
2. "14.9%" 是相对 Wan 2.2 5B 的 AVG 提升；但 GigaWorld-1 在 **Image/Aesthetic 上并不领先甚至落后**，增益几乎全来自 JEPA + Trajectory。**如果换一组更看重外观真实的下游用途，这个"评估器优先"的取舍是否反而失分？**
3. Finding 8 说 AgiBot 数据在**当前 GigaData 中心设定下**反而拉低 JEPA/Trajectory。这个结论对"评估目标本就贴 GigaData"高度依赖——换一个不以 GigaData 为测试域的场景，"robot 专属数据有害"是否还成立？
4. closed-loop 一致性只报了 **4 个任务**（Table 10），远少于 WMBench 的 8 任务族。为什么 closed-loop 部分收缩到 4 个？是算力（每任务要跑完整 policy×world-model 闭环）还是这 4 个才有足够的多 checkpoint policy？
5. VLM 评估器（Qwen3-VL）与被评的 world model 都重度用 Qwen 系；且 Interaction Quality 因"VLM 判不准物理"被判为不可靠指标。**用一个判不准物理的 VLM 家族当 outcome judge，会不会系统性放过某类物理失败？**
6. Relative RoPE / 分层记忆 / channel-concat 都是为长时程稳定设计的**保守先验**。当任务本身很短（几秒即结束）时，这些模块的收益是否被 DMD2 的 few-step 生成噪声抵消？短任务评估是否更吃亏？

## 我的阅读笔记

这篇的真正价值不在"又发了个更强的机器人 world model"，而在它**把"world model 能不能当评估器"从一句口号变成了一套可测的经验学**。它最锋利的两处，都是"反直觉但可验证"的结论：一是 **Finding 2——外观稳定性指标（Background/Photometric Consistency）与 WMES 负相关**，因为一个静止视频就能刷满外观分却零动作忠实；二是 **Finding 3 + Table 4——短视频质量强不代表评估器强，长时程 rollout 才是试金石**。这两条直接决定了它后面所有汇总表**故意不报**外观稳定性、只报 action-faithful 维度，逻辑闭环得很干净。方法侧最实的一击是 **Table 3 的 channel-concat 控制**：把"动作从去噪第一步就空间对齐地拼进 latent"证成 Traj.Acc 0.3528 vs cross-attention 0.1620，几乎是全文架构结论里最不含糊的一条。

但要清醒看边界。第一，**它衡量的是"评估器与真机的一致性"，不是"world model 有多真"**——所以它的所有"提升"都要放在"更贴真机 ranking"这个语境里读，不能当成通用视频生成 SOTA（它在 Image/Aesthetic 上本就不领先）。第二，作者自己承认的 **contact-sensitive 失败的乐观偏置**（§6.5.5）是硬伤：video generation 天然倾向把"接触/插入/倾倒"这类临界失败画得"看起来成功了"，而这恰是评估器最该判准的地方——这也解释了为什么它和 [[@wu2026tactile-wam]] 的触觉路线是天然互补的。第三，**结论对当前 GigaData 中心的评估域依赖较重**（Finding 8 里"robot 专属数据有害"就是这种依赖的产物），WMBench 8 任务族也还没覆盖移动操作/灵巧手/安全关键。

我会把它当作**"world model 作为 policy evaluator（第五范式）"这条线的锚点**，和 [[@wang2026wvm]]（value critic）、[[@wu2026tactile-wam]]（policy）三篇交叉读：同一个"世界模型"，一个用来评 policy、一个用来估 value、一个用来出 action——三种输出用途，恰好覆盖了 GigaWorld-1 在 Related Work 里画的那张范式地图的三个角。它开源 code/model/dataset/toolkit + WMBench 这一点，若能复现，价值可能比那 14.9% 更长久。
