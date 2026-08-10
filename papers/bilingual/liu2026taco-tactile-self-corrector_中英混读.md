---
tags:
  - bilingual-reading
  - deep-reading
paper: "[[@liu2026taco-tactile-self-corrector]]"
source_pdf: "[[papers/pdfs/liu2026taco-tactile-self-corrector.pdf]]"
images: "papers/images/liu2026taco-tactile-self-corrector/"
image_index: "[[papers/images/liu2026taco-tactile-self-corrector/index.md]]"
created: 2026-07-08
reading_mode: 生成式精读（逐节读原文 + 读图）
---

# TACO: TActile World Model as a Self-COrrector for Scalable VLA Post-Training

paper:: [[@liu2026taco-tactile-self-corrector]]
pdf:: [[papers/pdfs/liu2026taco-tactile-self-corrector.pdf]]
images:: [[papers/images/liu2026taco-tactile-self-corrector/index.md]]

> 作者：Shengbang Liu, Yueru Jia, Yuyang Yan, Jiaming Liu, Xinran Zhang, Qiuxuan Feng, Yandong Guo, Shiji Zhou, Boxin Shi, Shanghang Zhang。机构：北京大学（多媒体信息处理国家重点实验室，通讯 Shanghang Zhang）· AI² Robotics · 中山大学 · 北京航空航天大学。arXiv:2607.02840v1（2026-07-03，cs.RO），Project Page: https://taco-wm.github.io/

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| VLA (Vision-Language-Action) | 视觉-语言-动作模型 | 本文要改进的策略基座，base policy 是 **π₀.₅**（VLM prefix + action expert 结构）。 |
| localized contact failure | 局部接触失败 | 本文对失败的**重定义**：不是语义错误（policy 知道要做什么），而是接触突变（slippage / 力不足 / 异常扭矩）后无法恢复的**局部**故障——这是全文靶心。 |
| tactile-aware world model | 触觉世界模型 | 本文的"发动机"：一个能**联合想象未来视频 + 未来力**的世界模型，被当作**离线纠正数据引擎**，而非在线仿真器。 |
| Recognize–Imagine–Label loop | 识别-想象-标注闭环 | 本文的数据生成范式：识别 failure-adjacent 状态 → 想象局部纠正片段 → 标注可执行动作 + 优势标签。 |
| failure-adjacent state | 临近失败状态 | 进度停滞或下降处的状态 $p_{t+\Delta}-p_t<\epsilon$，被选作想象纠正的**锚点**。 |
| Visuo-Tactile Generation Model | 视觉-触觉生成模型 | 基于 **Wan2.2-TI2V-5B** 的联合去噪 DiT，把视频 token 与力 token 拼进同一自注意力，联合 flow-matching 去噪出 $\hat V_{t:t+H},\hat F_{t:t+H}$。 |
| Unified Progress-Action Model $U_\phi$ | 统一进度-动作模型 | 双路（DINOv2 视觉 + MLP 触觉）→ 双头，输出动作 $\hat a\in\mathbb R^7$ 和进度 $\hat p\in[0,1]$；**同一个模型**既做 Recognize（打进度）又做 Label（打动作）。 |
| temporal RoPE alignment | 时间 RoPE 对齐 | 把只含时间维的力 token 用 $\rho(i)$ 映射到 3D 视频 latent 的时间轴上，保证视频-力在自注意力里"时间对得上"。 |
| first-frame force anchoring | 首帧力锚定 | 保留 $F_0\in\mathbb R^{12}$ 为 clean anchor 不加噪，减少 contact-state 歧义、稳住联合去噪。 |
| Knowledge-Insulated (KI) tactile adaptation | 知识隔离触觉适配 | 本文保住 VLA 泛化的关键：对预训练 **VLM backbone 施 stop-gradient**，力历史+优势只经 **adaRMSNorm** 注入 action expert；只训练触觉编码器/适配层/action expert。 |
| advantage-conditioned training | 优势条件训练 | 借 offline-RL 思路，用二元 advantage（1=有效纠正 / 0=失败）作 CFG 条件；推理用**正优势**条件引导"高进度恢复"行为。 |
| adaRMSNorm conditioning | 自适应 RMSNorm 条件 | 把 force / advantage / timestep 条件以调制 RMSNorm 的方式注入 action expert 的通道——是"隔离"得以成立的注入接口。 |
| 6-DoF force-torque (×2 = 12-D) | 六维力/力矩（双指共 12 维） | 触觉信号形态：左右两个 Xense 各 6D，拼成 12 维力向量，不是触觉图像。 |
| Filtered BC | 过滤式行为克隆 | 最关键的对照基线：只把"成功 rollout"筛出来再 BC——它验证"是否只靠成功数据就够"，结论是不够（见 Table 1）。 |

## 摘要

> Vision-Language-Action (VLA) 模型在机器人操作中展现出不错的泛化，但在 **contact-rich** 任务上仍然脆弱——微小的接触扰动会造成**仅凭视觉难以察觉**的不可恢复失败。由于这些失败是**局部的**、而非任务级的语义错误，"触觉感知的纠正式后训练"提供了一条高效的恢复改进路径。然而，靠人工干预来规模化这类监督成本很高。近期工作用 world model 合成想象 rollout 来改进策略，但**纯视觉** world model 会生成"视觉上合理却接触不一致"的轨迹。为此本文提出 **TACO**：一个触觉感知、world-model 驱动的、面向 contact-rich 操作的可规模化 VLA 后训练框架。给定真实机器人 rollout，TACO 走一个 **Recognize–Imagine–Label** 闭环：统一 progress-action 模型用进度估计**识别** failure-adjacent 状态，visuo-tactile 生成模型**想象**局部纠正片段，progress-action 模型再把它们**标注**成可执行的纠正动作。为把触觉纠正监督注入 VLA 后训练，TACO 结合 **knowledge-insulated tactile adaptation** 与 **advantage-conditioned training**，让策略从想象纠正中学习而**不损坏预训练的视觉-语言先验**。这些组件使 TACO 能把真实失败转化为想象的 visuo-tactile 纠正，用于迭代式 VLA 后训练。真实 contact-rich 操作实验表明，TACO 相对 base policy 取得 **44% 的绝对成功率提升**、相对"无 knowledge-insulated 触觉适配"的版本提升 **32%**。关键词：Robotic Manipulation, Tactile World Model。

中文解读：这段摘要的写作动作是**先精确定位一个被前人忽略的失败类型（局部接触失败），再指出两条现成路子各自的坑（人工干预贵、纯视觉 world model 接触不一致），最后用一个"触觉世界模型 + 保护性训练管线"同时补上两个坑**。三个数字要记牢它们的口径：**44% 与 32% 都是"绝对成功率提升 = 百分点"**（0.38→0.82 是 +44pp，0.50→0.82 是 +32pp），不是相对增幅。

## 论文主线

![[papers/images/liu2026taco-tactile-self-corrector/methods_01_page1.png|820]]

**Figure 1 / 全文总览。** 左半 **TACO Iterative Post-Training Loop**：从 **6D Tactile Feedback** 出发，`1) Recognize` 用 Unified Progress-Action Model 在 rollout 上打进度、圈出 **Failures**（进度曲线由升转降的红色区段）；`2) Imagine` 让 Video-Tactile Generation Model 想象纠正；`3) Label` 把纠正片段标成动作并打 **Advantage=1（Corrections）/ Advantage=0（Failures）**；最后进 **Autonomous Post-Training**：VLM 被 **Stop Gradient** 挡住，只有 Action Expert 接收条件，基座是 **π₀.₅**，产出 **Improved VLA Policy**，再回灌下一轮。右半 **Real-World Experiments Results** 两根柱状图一眼给出结论：Ave Success Rate **0.38 → 0.43 → 0.50 → 0.82**（Base / Filtered BC / TACO w/o KI / TACO），Ave Completion Step **185.5 → 155.5 → 146.5 → 127.7**（越低越好）。这张图把"闭环怎么转"和"最后涨了多少"同时讲清楚了。

这篇论文的核心问题是：**VLA 已经能把视觉-语言先验迁移到动作生成，但在 contact-rich 任务里，成败往往取决于"看不见的接触"**——擦白板时橡皮没压够力、拧瓶盖时夹爪对准了却没有有效扭矩。作者一句话点破这类失败的性质：**"These failures are localized rather than semantic: the policy knows what to do, but cannot recover when contact shifts unexpectedly."**（失败是局部的、不是语义的：策略知道该做什么，但接触突变后无法恢复。）

既然是局部接触失败，最对症的补法就是**"触觉感知的纠正式后训练"**——针对失败邻近状态补上恢复监督。但这条路有两个坑：
1. **靠人工干预造纠正数据不可规模化**（要反复盯着、在失败点手动救场）；
2. **用 world model 合成 rollout 省人力，但纯视觉 world model 会产出"视觉合理却接触不一致"的轨迹**——它想象的画面里，接触物理是错的。

TACO 的回答是把这两个坑一起填掉：**造一个能联合想象"未来视频 + 未来力"的触觉世界模型，让它在真实失败的邻近状态上"做梦"般想象出局部恢复片段，再把这些片段标注成动作监督**，从而无需重复人工、又保住接触一致性。而要把这种"触觉重"的纠正数据灌进 VLA 又不把预训练的视觉-语言能力冲垮，作者上了第二道保险——**knowledge-insulated 适配**：stop-gradient 把 VLM backbone 冻在原地，触觉与优势只从 action expert 这条支路进。

阅读时要盯住一句话：**本文的贡献不是"触觉有用"、也不是"world model 能后训练"（都是前人共识），而是把 world model 的角色从"在线仿真器"改成"离线的自纠错数据引擎"，并给出一整套"识别失败→想象接触一致的恢复→标注→保护性注入"的闭环。** 后面每个组件都对应这条主线的一环，可逐一回勾。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| 造一个 **tactile-aware world model**：visuo-tactile 生成模型经 temporal RoPE 联合去噪视频+力，配统一 progress-action 模型从视觉+触觉预测进度与纠正动作。 | §3.1，Fig.3，$\mathcal L_{\text{joint}}$、$\rho(i)$、$\mathcal L_{\text{UPA}}$。 | 消融 Fig.5：去掉触觉生成 SR 掉到 0.28、去掉触觉标注掉到 0.65；力/动作 val loss 与 VOC/FL 全面变好。 | 组件必要性由消融直接支撑，较扎实；但生成质量只有代理指标（VOC/FL/val-loss），无独立视频保真度基准。 |
| 提出迭代 **Recognize–Imagine–Label** 监督生成框架：识别 failure-adjacent、想象 visuo-tactile 纠正、标注恢复动作。 | §3.2，Fig.2，anchor 选择式、$G_\psi$、$U_\phi$、advantage $y_t$。 | Table 1 两轮迭代持续上涨（0.38→0.66→0.82）；Fig.4 定性展示 Hanoi/BottleCap 真实失败 vs 想象纠正。 | 迭代有效、且能自洽闭环；但"想象片段真的物理正确"主要靠下游 SR 间接证明。 |
| 提出 **knowledge-insulated tactile adaptation + advantage-conditioned training**，注入触觉纠正而不侵蚀视觉-语言先验。 | §3.3，$\mathcal L_\pi$、$c_{\text{adaRMS}}$、stop-gradient + adaRMSNorm。 | Table 1：TACO 0.82 vs **TACO w/o KI 0.50**（+32pp）；Fig.7 一轮 OOD 想象即大幅提升泛化。 | 这是本文**最有分量**的一环——"无 KI"版几乎停在 0.50，说明"保护先验"不是锦上添花而是决定性的。 |
| 在真实 contact-rich 任务上验证并分析（动作分布、OOD 泛化）。 | §4，Fig.6/Fig.7。 | Fig.6 动作分布随迭代变宽；Fig.7 未见背景/物体/位置分别 76.0/82.5/45.0。 | 真实验证成立；但仅单臂、6 任务、无长时程/搜索类任务，边界明确。 |

## 结构地图

| 原文位置 | 作者在这一部分做什么 | 与全文主线的关系 | 关键图表 / 公式 |
| --- | --- | --- | --- |
| §1 Introduction | 把失败重定义为 localized contact failure，指出"人工干预贵 + 纯视觉 WM 接触不一致"两坑，给出三点贡献。 | 定义问题入口，明确"为什么需要一个触觉 world model 当纠错器"。 | Fig.1；Wipe/Twist 两个 motivating example |
| §2 Related Work | 梳理"World Models for Robot Learning"与"Tactile-Aware Robot Learning"，点名 naive 加触觉会损害 pre-contact 感知[63]、以及 KI 训练思路[30]。 | 把本文定位成"用真实失败识别 + 局部想象 + 重标注"，区别于"在线 rollout / 长时程预测"的世界模型用法。 | 引用簇 [22-46]、[47-63] |
| §3.1 Tactile-Aware World Model | 定义 visuo-tactile 生成模型（Wan2.2-TI2V-5B、联合 flow-matching、temporal RoPE、首帧力锚定）与统一 progress-action 模型。 | 造出"发动机"——既能想象接触一致的未来，又能给未来打进度和动作。 | Fig.3；$\mathcal L_{\text{joint}}$、$\rho(i)$、$\mathcal L_{\text{UPA}}$ |
| §3.2 Iterative Correction Framework | 把发动机组织成 Recognize–Imagine–Label 三步，产出带 advantage 的纠正监督。 | 把"能想象"变成"能持续产出可训练数据"的闭环。 | anchor 选择式、$G_\psi(\cdot\mid I_t,F_t,l)$、$y_t\in\{0,1\}$ |
| §3.3 Knowledge-Insulated Tactile Adaptation | stop-gradient 隔离 VLM，力+优势经 adaRMSNorm 只进 action expert；advantage-conditioned 的 CFG flow-matching。 | 把纠正数据安全地灌回策略而不冲垮泛化——决定成败的一步。 | $\mathcal L_\pi$、$c_{\text{adaRMS}}=c_t+\lambda_f c_f+\lambda_a c_a$ |
| §4.1 Setup | Franka FR3 + D455 + 双 Xense；6 任务；每任务 50 示教、40 评测；π₀.₅ warm-start；2 轮迭代。 | 交代证据的可信度边界（单臂、6 任务、真实机器人）。 | Setup 图（display1） |
| §4.2 Main Results | Table 1 两轮成功率；Fig.4 想象纠正可视化。 | 给主结论（+44pp）与定性证据。 | Table 1、Fig.4 |
| §4.3 Ablation | 去触觉生成/去触觉标注的消融 + 想象数据缩放。 | 拆开"增益来自哪个组件"。 | Fig.5（表 + 缩放柱） |
| §4.4 Analysis | 动作分布随迭代变宽；OOD 泛化（背景/物体/位置）。 | 解释"为什么会涨"——不是复读示教，而是扩宽了成功动作空间。 | Fig.6、Fig.7 |
| §5 Conclusion & Limitations | 收束主张；承认"离线想象、只解局部接触失败"，指向在线纠正。 | 划定适用边界与后续方向。 | —— |

## 按原文 section 精读

### 1. Introduction / 把失败重定义为"局部接触失败"

高层故事流：introduction 的关键动作是**把问题从"VLA 不够强"收窄到一个可验证的失败类型**。作者举了两个极具体的例子——*Wipe Whiteboard*（橡皮擦到了标记但没压够力，擦不掉）、*Twist Bottle Cap*（夹爪对准了瓶盖却生成不了有效扭矩）。它们的共同点是：**视觉观测几乎没变，但触觉信号因滑移/力不足/异常扭矩而显著改变**。据此作者下了本文的定性判断——这些失败 *localized rather than semantic*，所以纠正应当**聚焦于 contact-sensitive 的局部片段，而不是整条轨迹**。

接着作者堵住两条现成路：靠人工干预造纠正数据"requires repeated monitoring and manual recovery at failure states"（不可规模化）；用纯视觉 world model 合成 rollout 则"visually plausible rollouts may still contain inconsistent contact dynamics"（接触不一致）。于是提出 TACO，并把贡献列成三点（world model / RIL 框架 / KI 适配 + advantage 训练）。

关键证据 / 图表 / 公式：Fig.1 是全文缩影；两个 motivating example 直接对应后面 Table 1 里的 Wipe Whiteboard 与 Twist Bottle Cap 两列，可回勾"引言承诺的失败是否被实验覆盖"。

回看重点：引言把失败定义得很干净，但要警惕——"localized contact failure"是作者自选的问题切片，它天然**利于**一个专修局部接触的方法；读实验时要看是否存在该切片之外仍失败的任务（有：作者没放长时程/搜索类任务）。

### 2. Related Work / 本文在两条线里的落点

高层故事流：两段分别对应两条线。**World Models for Robot Learning**——世界模型预测未来观测/视觉状态，配 inverse dynamics 从生成视频反推动作、配 reward model 做失败定位，近期还被当**在线 RL 仿真器**做策略后训练。作者的区分句很重要：*"Unlike prior methods that rely on long-horizon prediction or online human correction, we use real rollouts to recognize failure states, imagine segments with tactile estimation, and relabel them into corrective action data."* —— 即 **TACO 不做长时程预测、不在世界模型里在线 rollout，而是"真实失败识别 + 局部想象 + 重标注"**。

**Tactile-Aware Robot Learning**——触觉能改善 contact awareness / force-sensitive control；近期 visuo-tactile world model 更主张"触觉该被建模进环境动力学、而非仅作辅助输入"。但作者点出关键张力：**"naively adding tactile inputs can impair pre-contact perception and grounding [63]"**——这正是 §3.3 KI 适配要解决的问题，也是与姊妹篇 Tactile-WAM"tactile pollution"呼应的地方。

关键证据 / 图表 / 公式：无图；但 [63]（朴素加触觉损害 pre-contact 感知）与 [30]（KI 训练）是理解本文两处设计动机的引用锚点。

回看重点：related work 把 TACO 和"世界模型当在线仿真器"（如库里 [[@qian2026wam-rl]]、[[@yu2026wm-dagger]]）明确切开——这是判断本文新意的关键坐标。

### 3. Method / 方法

Method 开门见山：*"Given real robot rollouts, TACO converts real-world failures into visuo-tactile corrective supervision through a Recognize–Imagine–Label loop."* 下面 §3.1 造发动机、§3.2 组装闭环、§3.3 保护性注入。

#### 3.1 Tactile-Aware World Model / 发动机：联合想象 + 统一打分

![[papers/images/liu2026taco-tactile-self-corrector/model_arch_v3_page1.png|860]]

**Figure 3 / 触觉世界模型架构（三块）。** 左 **Visuo-Tactile Joint Denoising Generation Model**：当前帧 $V_t$ 经 **VAE** 成视觉 token、$F_t$ 经 **Tactile Tokenizer** 成力 token，与 Noisy Token 一起过 **Joint Self-Attention → Cross-Attention（吃语言 "Move Hanoi Rings"）→ FFN** 的 **DiT Blocks ×N**、循环 **Denoising Steps ×T**，再由 **WAN Decoder / Tactile Head** 解出未来视频 $\hat V_{t:t+H}$ 与未来力 $\hat F_{t:t+H}$。中 **Unified Progress-Action Model**：$V_t$→**DINOv2**、$F_t$→**Tactile MLP**，融合 $\oplus$ 后进 **Progress Head**（$\hat p_t$）与 **Action Head**（$\hat a_t$）。右 **Temporal RoPE Alignment**：$T{=}49,\ N_v{=}12$，**Clean Anchor $F_0$** 单列，其余力 token 分组对齐到视频时间轴——$F_1\!-\!F_4\!\to\!V_1$、$F_5\!-\!F_9\!\to\!V_2$、…、$F_{45}\!-\!F_{48}\!\to\!V_{12}$。这张图把"力 token 怎么和视频 token 在同一注意力里对上时间"讲得最直观。

**Visuo-Tactile Generation Model** 建在 **Wan2.2-TI2V-5B** 上，先在大规模机器人轨迹上微调（视觉保真 + 机器人-场景一致性），再用滑窗适配到 contact-rich 示教。给定视频 latent token $X^v\in\mathbb R^{B\times N_v\times d}$ 与力序列 $F\in\mathbb R^{B\times T\times 12}$（12 维 = 左右各 6-DoF force-torque），力被 tokenize 成 $X^f=T_\eta(F)\in\mathbb R^{B\times T\times d}$，再与视频 token 拼接：

$$
X = [\,X^v;\ X^f\,]\in\mathbb R^{B\times(N_v+T)\times d}
$$

从而在 **DiT 自注意力内部实现双向 video-force 交互**。去噪后各自解码回未来视频与力。训练时视频与力共享同一采样 timestep，联合 flow-matching：

$$
\mathcal L_{\text{joint}} = \big\|u^v_\psi-(\xi^v_1-\xi^v_0)\big\|_2^2 + \lambda_f\big\|u^f_\psi-(\xi^f_1-\xi^f_0)\big\|_2^2
$$

其中 $(\xi^v_1,\xi^f_1)$ 为 clean video-latent / 力段，$(\xi^v_0,\xi^f_0)$ 为对应高斯噪声，$\lambda_f$ 平衡力去噪项。

两个稳定性设计很关键。**Temporal RoPE alignment**：Wan2.2 的 RoPE 作用在 3D 视频 latent 网格上，而力 token 只有时间维，于是把每个力 token 对齐到视频 latent 的时间轴——给定力 token 长度 $T$、视频 latent 时间长度 $f$，第 $i$ 个力 token 分配到

$$
\rho(i)=\mathrm{round}\!\left(\frac{i}{T-1}(f-1)\right),\quad i=0,\dots,T-1
$$

每个力 token 在 $\rho(i)$ 处用时间 RoPE、空间 RoPE 置为 $1+0j$。**First-frame force anchoring**：保留 $F_0\in\mathbb R^{12}$ 为 clean 首帧锚点（不加噪），以减少 contact-state 歧义、稳住联合去噪（Fig.3 右侧 "Clean Anchor $F_0$" 即此）。

**Unified Progress-Action Model $U_\phi$**：给定 RGB 帧 $I_t$ 与 force-tactile 信号 $F_t\in\mathbb R^{12}$，预测 $(\hat a_t,\hat p_t)=U_\phi(I_t,F_t)$，$\hat a_t\in\mathbb R^7$、$\hat p_t\in[0,1]$。视觉走 **DINOv2** + direction-aware decoder（空间 grounding），触觉走 **MLP**（归一化 12 维编码），融合 $[z^v_t;z^f_t]$ 后进双头 $\hat a_t=h_a([z^v_t;z^f_t])$、$\hat p_t=\sigma(h_p([z^v_t;z^f_t]))$，联合训练：

$$
\mathcal L_{\text{UPA}}=\mathrm{SmoothL1}(\hat a_t,a_t)+m_t\,\|\hat p_t-p_t\|_2^2
$$

$m_t$ 指示该帧是否有有效进度标签。进度 target 来自**人工标注的 task-stage 标签**，每帧按其阶段赋一个归一化 completion 值，提供 dense、stage-aware 的进度监督。**注意这个 $U_\phi$ 是"一模两用"**：Recognize 阶段用它的进度头找失败锚点，Label 阶段用它的动作头给想象片段打动作——这是全框架能自洽的结构支点。

论证功能表：

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 视频+力拼进同一自注意力联合去噪 | 保证想象的未来"接触一致" | Fig.3 左、$\mathcal L_{\text{joint}}$ | 力仅 12 维 force-torque，非触觉图像/高分辨接触形貌 |
| temporal RoPE + 首帧力锚定 | 让异构（3D 视频 vs 1D 力）token 时间可对齐、去噪稳定 | $\rho(i)$、Fig.3 右 | 是启发式对齐（round 到整数格），非学习式对齐 |
| $U_\phi$ 一模两用（进度+动作） | 让 Recognize 与 Label 共享同一世界理解 | $\mathcal L_{\text{UPA}}$ | 进度 target 依赖人工 task-stage 标注 |

#### 3.2 TACO Iterative Correction Framework / 闭环：识别→想象→标注

![[papers/images/liu2026taco-tactile-self-corrector/pipeline_v5_page1.png|880]]

**Figure 2 / TACO 框架（5 阶段迭代）。** ①**Real-World Rollouts**：当前策略在真实机器人上跑（Xense Tactile Sensor、6-DoF Force-Torque、标注 **Contact-State Deviation** 的红色⚠）。②**Failures**：进度曲线由升转降处（红段）被挑出。③**Tactile-Aware World Model**：Visuo-Tactile Generation Model 负责 `Imagine`、Unified Progress-Action Model 负责 `Recognize`/`Label`。④**Corrections**：想象出的未来帧 + 力 $\hat F_{t:t+H}$ + 动作 $\hat a_{t:t+H}$，并标 **Advantage=1（Corrections）/ Advantage=0（Failures）**。⑤**Autonomous Post-Training**：VLM 被 **Stop Gradient** 挡住，力/优势经 $C_{\text{adaRMS}}$ 只进 **Action Expert**，基座 **π₀.₅**，产出 **Improved VLA Policy** 并回灌 **Iterative Post-Training Loop**。

**Recognize failure-adjacent states.** 第 $k$ 轮部署当前策略 $\pi_\theta^{(k)}$ 收 rollout；不把状态等同看待，而是用 $U_\phi$ 打 dense 进度 $p_t$，在**进度停滞或下降**处选纠正锚点：

$$
\mathcal S^{(k)}_{\text{anchor}}=\Big\{(\tau,t)\ \Big|\ \tau\in\mathcal D^{(k)}_{\text{roll}},\ p_{t+\Delta}-p_t<\epsilon\Big\}
$$

$\Delta$ 是短窗、$\epsilon$ 是进度阈值。

**Imagine visuo-tactile corrections.** 从每个锚点起，想象 **$T=49$** 步局部纠正：生成模型条件于当前视觉观测、力、语言指令，联合去噪未来视频与力，产出局部合理的纠正片段

$$
(\hat I_{t:t+T},\ \hat F_{t:t+T})\sim G_\psi(\cdot\mid I_t,F_t,l)
$$

它捕获 failure-adjacent 状态附近的**视觉演化 + 接触-力动力学**。

**Label actions.** 把想象出的视觉+触觉喂回 $U_\phi$ 得动作与进度 $(\hat a_{t:t+T},\hat p_{t:t+T})=U_\phi(\hat I_{t:t+T},\hat F_{t:t+T})$，并给每段打**二元 advantage** $y_t\in\{0,1\}$：$y_t=1$ 为有效纠正、$y_t=0$ 为初始失败。这些标签就是 advantage-conditioned 后训练的 recovery 监督。

回看重点：这一节把 §3.1 的"能想象"变成"能持续产数据"。要追问的是——**anchor 只由进度阈值触发**：如果 $U_\phi$ 的进度头在某任务上噪声大，锚点会选偏；而"想象片段真的物理正确"在本节没有独立校验，只能靠下游 SR 与 Fig.5 的 val-loss/VOC/FL 代理来间接背书。

#### 3.3 Knowledge-Insulated Tactile Adaptation / 保护性注入（最关键一步）

痛点直说：*"Directly optimizing the entire VLA on tactile-heavy correction data can degrade the pretrained visual-language knowledge needed for pre-contact perception and grounding."* 也就是"朴素全量微调会把 VLM 的视觉-语言先验冲垮"。TACO 的处理是**把 tactile-action 梯度挡在 VLM backbone 之外，只让 action expert 学触觉**：image/language/state token 编码为 **VLM prefix token**，而**力历史与 advantage 只经 adaRMSNorm 注入 action expert**；后训练中只优化**触觉编码器、适配层、action expert**。更新后的 $\pi_\theta^{(k+1)}$ 再去收新 rollout，形成 **real→imagine→real** 的闭环，逐轮压低 contact-sensitive 失败。

**Advantage-Conditioned Post-Training.** 用力与优势条件训练 action expert 以区分"高进度纠正"与"停滞/歧义"行为。给定加噪动作块 $x_\sigma=\sigma\epsilon+(1-\sigma)a_t$，action expert 在 CFG 下预测 flow velocity：

$$
\mathcal L_\pi=\mathbb E\Big[\big\|u_\theta(x_\sigma,\sigma\mid z_t,\tilde c_{\text{adaRMS}})-(\epsilon-a_t)\big\|_2^2\Big],\qquad c_{\text{adaRMS}}=c_t+\lambda_f c_f+\lambda_a c_a
$$

$z_t$ 是 VLM prefix 表示，$c_t$ 是 flow timestep 条件，$c_f,c_a$ 分别是从力历史、片段优势编码的力/优势条件。训练时以一定概率把 $c_{\text{adaRMS}}$ 替换为 null 条件（学到条件/无条件两种预测，即 CFG）；**推理时用正优势条件**，引导"高进度触觉恢复"行为。

论证功能表：

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| stop-gradient 隔离 VLM backbone | 保住 pre-contact 感知与语言 grounding | §3.3、Fig.2 "Stop Gradient" | 触觉能力被限制在 action expert，跨模态深层耦合被牺牲 |
| 力/优势只经 adaRMSNorm 进 action expert | 提供"轻量、可隔离"的注入接口 | $c_{\text{adaRMS}}$ | adaRMSNorm 通道调制的表达力上限未讨论 |
| advantage-conditioned CFG | 让策略偏向"有效纠正"而非复读失败 | $\mathcal L_\pi$、Table 1 消融 | 依赖 $y_t$ 标注质量（来自 $U_\phi$ 的进度判断） |

### 4. Experiments / 实验

#### 4.1 Setup / 平台、任务、协议

![[papers/images/liu2026taco-tactile-self-corrector/display1_page1.png|860]]

**Setup 图 / 平台与任务。** (a) 六任务实拍：Insert Flower、Wipe Whiteboard（白板上写着 "TACO"）、Twist Bottle Cap、Play Xylophone（彩色木琴）、Toast Bread（面包机）、Move Hanoi Rings（汉诺塔环）。(b) 平台：**Franka Research 3 Arm** + **Intel RealSense D455 Camera**（前视）+ 夹爪双指各一枚 **Xense Tactile Sensor**（6D 力/力矩）。

- **平台**：单臂 Franka Research 3，前视相机 + 夹爪上两枚 Xense 触觉传感器。
- **6 任务**：Insert Flower / Wipe Whiteboard / Twist Bottle Cap / Play Xylophone / Toast Bread / Move Hanoi Rings，每任务 **50 条 SpaceMouse 遥操作示教**。
- **协议**：先用示教 warm-start **π₀.₅** 作 base policy；然后部署当前策略收 rollout、用世界模型生成想象纠正、在"示教 + 经验数据 + 想象纠正"上后训练；**每任务跑 2 轮迭代**；每方法在**每任务 40 独立 episode**（桌面物体位置随机）上评测。

> **读原文才澄清的口径**：正文只说世界模型"first fine-tuned on broad robot trajectories"，**没有点名具体预训练数据集**（v1 无附录，网络二手摘要里出现的 DROID/AgiBot/RoboMIND 无法从本文证实，勿写入）。相机型号 **D455** 则由 Setup 图明确标出，可信。

#### 4.2 Main Results / 主结果

![[papers/images/liu2026taco-tactile-self-corrector/Visualization2_page1.png|860]]

**Figure 4 / 想象纠正可视化（Real World 上排 vs World Model 下排）。** *Move Hanoi Rings*：真实 rollout 把环与柱错位、插不进；想象纠正调整接触、对准并把环套上柱。*Twist Bottle Cap*：真实 rollout 接触到盖子却打滑、无有效扭矩；想象纠正保持稳定接触并完成拧转。这两例正是把"RGB 里弱可见的接触转变"补出来，产出后训练用的纠正监督。

**Table 1 逐任务成功率（SR，每格 = 40 集中的成功率；Ave = 六任务均值）：**

| Method | Insert Flower | Wipe Whiteboard | Twist Bottle Cap | Play Xylophone | Toast Bread | Move Hanoi Rings | **Ave SR** |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Base Policy (π₀.₅) | 0.50 | 0.51 | 0.45 | 0.46 | 0.30 | 0.08 | **0.38** |
| *Iter 1* Filtered BC | 0.55 | 0.54 | 0.50 | 0.49 | 0.32 | 0.07 | 0.41 |
| *Iter 1* TACO (w/o KI) | 0.55 | 0.33 | 0.55 | 0.58 | 0.48 | 0.42 | 0.49 |
| *Iter 1* **TACO** | 0.70 | 0.55 | 0.85 | 0.63 | 0.70 | 0.51 | **0.66** |
| *Iter 2* Filtered BC | 0.52 | 0.57 | 0.48 | 0.51 | 0.36 | 0.11 | 0.43 |
| *Iter 2* TACO (w/o KI) | 0.62 | 0.35 | 0.65 | 0.52 | 0.51 | 0.37 | 0.50 |
| *Iter 2* **TACO** | **0.93** | **0.65** | **0.98** | **0.78** | **0.81** | **0.79** | **0.82** |

- **主结论**：2 轮后 **Ave SR 0.38 → 0.82（+44pp vs base）**；相对 **Filtered BC 0.43（+39pp）**、相对 **TACO w/o KI 0.50（+32pp）**。完成步数（CS，仅成功集平均）**Ave 185.5 → 127.7**，即执行更平滑、少停顿/冗余/犹豫接触。
- **迭代单调上涨**：TACO 从 0.66（Iter1）到 0.82（Iter2），闭环确实"越滚越好"。
- **Move Hanoi Rings 是最戏剧的一列**：base 仅 0.08 → TACO 0.79（这是最依赖 first-contact/对准的任务）。
- **Filtered BC 基本原地踏步（0.41/0.43）**：作者点破原因——筛出来的成功 rollout **不含 failure-adjacent 的恢复行为**，只是反复强化窄示教流形，所以跨迭代饱和。这条对照最能说明"TACO 的增益来自想象出示教里不存在的恢复片段，而非单纯多用成功数据"。

#### 4.3 Ablation Study / 消融与缩放

![[papers/images/liu2026taco-tactile-self-corrector/Ablation.png|820]]

**Figure 5 / 消融（左表）+ 想象数据缩放（右柱）。** 图例：$V,F,A,R$ 分别是 video、force、action、progress；val loss 报 force 预测 $F$ 与 action 预测 $A$；VOC = 视频逐帧进度秩相关，FL = 失败定位准确率，Real SR = 真实成功率。

| Setting | Gen 输入→输出 | PA-Model 输入→输出 | Val Loss $F$↓ / $A$↓ | VOC↑ / FL↑ | Real SR↑ |
| --- | :---: | :---: | :---: | :---: | ---: |
| w/o tactile generation | $V\to V$ | $V\to A{+}R{+}F$ | 0.004 / 0.025 | 0.78 / 0.87 | **0.28** |
| w/o tactile labeling | $V{+}F\to V{+}F$ | $V\to A{+}R$ | **0.002** / 0.038 | 0.88 / 0.90 | 0.65 |
| **TACO** | $V{+}F\to V{+}F$ | $V{+}F\to A{+}R$ | **0.002** / **0.019** | **0.94** / **0.95** | **0.82** |

这张表几乎独立证明了"触觉在两处都不可省"：
- **去掉触觉生成 → SR 掉到 0.28**（比 base 0.38 还差）：只靠视觉想象抓不住 RGB 里弱可见的 contact-state 转变，想象出的"纠正"反而误导。
- **去掉触觉标注 → 0.65**：触觉参与了想象但没参与 Label，恢复监督的质量打折。
- **完整 TACO → 0.82**，且 action val-loss（0.019）、VOC（0.94）、FL（0.95）全面最好——**触觉信号在"想象动力学生成"和"纠正标注"两处扮演互补角色**。

**想象数据缩放（Fig.5 右，Insert Flower）**：相对 base，真实:想象比 **Real Only 50% → 1:2 = 70% → 1:4 = 93% → 1:8 = 97%**。作者强调 **1:8 还优于 1:4**，说明更大规模的想象纠正能覆盖更广的 failure-adjacent 接触状态——**想象数据能显著降低纠正数据采集成本，且尚未见饱和**。

#### 4.4 Analysis / 为什么会涨 & 泛化

![[papers/images/liu2026taco-tactile-self-corrector/action_distribution_v3.png|820]]

**Figure 6 / 动作分布分析（Insert Flower，40 成功 rollout 的末端位姿在 X-Y 平面投影）。** 五配置：Expert Demo / Base Policy / Filtered BC / Iteration 1 / Iteration 2。**Base policy 分布窄**、紧贴示教流形（对累积执行误差敏感）；**Filtered BC 只复读 base 已覆盖的轨迹**、无法外扩；**TACO 随迭代（Iter1→Iter2）分布逐步变宽**，把策略暴露给更多样的成功调整行为。结论：TACO **把动作空间扩到窄示教流形之外**，从而能在示教里没见过的情形下恢复并完成任务。

![[papers/images/liu2026taco-tactile-self-corrector/generalization_new.png|820]]

**Figure 7 / 泛化（Wipe Whiteboard，base 仅 ID 示教 vs TACO 一轮 OOD 想象纠正）。** 三种迁移下 Base → TACO：**Unseen Background 25.5 → 76.0**、**Unseen Object 30.0 → 82.5**、**Unseen Position 12.5 → 45.0**（%）。base 在三种迁移下都明显退化，TACO **只需一轮适配**即大幅回升。尤其关键：这些 OOD 设置**在视觉/触觉/动作上都落在世界模型训练分布之外，世界模型仍能生成有效纠正**——说明 tactile-aware world model 的泛化能"robustly beyond its training data"。这也把 TACO 从"提升 in-domain 接触执行"延展成"高效适配新位置/物体/视觉扰动"的机制。

回看重点：Fig.6 是"机制解释"（涨是因为动作空间扩宽，不是复读示教），Fig.7 是"能力外延"（一轮 OOD 想象就能迁移）。二者一起把主结论从"数字更高"升级成"为什么更高 + 还能迁移"。

### 5. Conclusion & Limitations / 结论与边界

结论：TACO 用 Recognize–Imagine–Label 把真实失败转成想象纠正、无需反复人工——触觉世界模型联合去噪未来视频+力，统一 progress-action 模型识别 failure-adjacent 并打纠正动作；再用 knowledge-insulated 适配 + advantage-conditioned 训练把监督灌回而不侵蚀先验，真实任务平均成功率相对 base +44pp，并能泛化到未见背景/物体/位置。

作者自陈局限（原文只给一条明确 limitation）：**"imagined corrections are generated offline rather than online during deployment"**——想象纠正是**离线**生成，非部署时**在线**；且主张聚焦"用触觉想象恢复**局部**接触失败"。未来方向：**online correction generation + 世界模型与策略更紧耦合**。

## 方法细节

按四个问题拆 TACO：

1. **输入是什么**：世界模型吃当前 RGB $I_t$ + 12 维力 $F_t$ + 语言 $l$；策略（π₀.₅）把 image/language/state 编成 VLM prefix，力历史/优势另走 action expert。
2. **中间表示是什么**：视频 latent token $X^v$ 与力 token $X^f$ 拼进同一 DiT 自注意力（temporal RoPE 对齐、$F_0$ clean 锚定）；$U_\phi$ 融合 $[z^v_t;z^f_t]$；策略侧条件 $c_{\text{adaRMS}}=c_t+\lambda_f c_f+\lambda_a c_a$。
3. **训练目标是什么**：世界模型 = 联合 flow-matching $\mathcal L_{\text{joint}}$；$U_\phi$ = SmoothL1 动作 + 掩码 MSE 进度 $\mathcal L_{\text{UPA}}$；策略 = CFG flow-matching $\mathcal L_\pi$，条件含 advantage $y_t$。
4. **输出如何使用**：世界模型输出 $(\hat I,\hat F)$ 只用于**离线生成纠正数据**（不在线 rollout）；$U_\phi$ 输出进度→选锚点、动作→标注；策略输出 7 维动作块，推理用**正优势**条件。

公式/数学定义速查：

- 锚点：$\mathcal S^{(k)}_{\text{anchor}}=\{(\tau,t)\mid \tau\in\mathcal D^{(k)}_{\text{roll}},\ p_{t+\Delta}-p_t<\epsilon\}$
- 拼接：$X=[X^v;X^f]\in\mathbb R^{B\times(N_v+T)\times d}$
- 联合去噪：$\mathcal L_{\text{joint}}=\|u^v_\psi-(\xi^v_1-\xi^v_0)\|_2^2+\lambda_f\|u^f_\psi-(\xi^f_1-\xi^f_0)\|_2^2$
- RoPE 对齐：$\rho(i)=\mathrm{round}\big(\tfrac{i}{T-1}(f-1)\big)$，空间 RoPE $=1{+}0j$，$F_0$ clean
- 进度-动作：$(\hat a_t,\hat p_t)=U_\phi(I_t,F_t)$，$\mathcal L_{\text{UPA}}=\mathrm{SmoothL1}(\hat a_t,a_t)+m_t\|\hat p_t-p_t\|_2^2$
- 想象：$(\hat I_{t:t+T},\hat F_{t:t+T})\sim G_\psi(\cdot\mid I_t,F_t,l)$，$T=49$
- 策略：$x_\sigma=\sigma\epsilon+(1-\sigma)a_t$，$\mathcal L_\pi=\mathbb E\|u_\theta(x_\sigma,\sigma\mid z_t,\tilde c_{\text{adaRMS}})-(\epsilon-a_t)\|_2^2$

## 实验设置、数据集、基线、指标

- **机器人/传感**：单臂 Franka Research 3；前视 Intel RealSense D455；夹爪双指各一枚 Xense（6D force-torque，共 12 维）。
- **任务/数据**：6 个真实 contact-rich 任务；每任务 50 条 SpaceMouse 遥操作示教；每方法每任务 40 独立评测集（物体位置随机）；2 轮后训练迭代。
- **世界模型预训练**：Visuo-Tactile Generation Model 基于 Wan2.2-TI2V-5B，先在"broad robot trajectories"上微调（**未点名具体数据集**），再滑窗适配到 contact-rich 示教。
- **基线**：① **Base Policy** = warm-start 的 π₀.₅；② **Filtered BC** = 只用筛出的成功 rollout 做 BC（探"是否只靠成功数据就够"）；③ **TACO (w/o KI)** = 去掉 knowledge-insulated 适配的消融版（探"保护先验是否必要"）。
- **指标**：Success Rate（SR，成功率）；Completion Steps（CS，仅成功集平均，越低越平滑）；消融另用 val loss（力/动作预测）、VOC（视频逐帧进度秩相关）、FL（失败定位准确率）。

## 主要结果、消融或对比

| 维度 | 关键数字 | 读法 |
| --- | --- | --- |
| 主结果（Table 1，Iter2） | Ave SR 0.38→**0.82**（+44pp）；CS 185.5→127.7 | 相对 base 的**绝对**提升；对照 Filtered BC 0.43 / w/o KI 0.50 |
| KI 的价值 | TACO 0.82 vs w/o KI 0.50（**+32pp**） | 保护 VLM 先验不是可选项，是决定性因素 |
| 迭代 | 0.38 → 0.66（Iter1）→ 0.82（Iter2） | 闭环单调上涨，未见退化 |
| 消融·去触觉生成 | SR **0.28**（< base 0.38） | 纯视觉想象有害；触觉必须进"想象" |
| 消融·去触觉标注 | SR **0.65** | 触觉也必须进"标注" |
| 缩放（Insert Flower） | 50→70→93→**97%**（Real Only / 1:2 / 1:4 / 1:8） | 想象数据可规模化替代真实，1:8 仍在涨 |
| 泛化（Wipe Whiteboard，1 轮 OOD） | 背景 25.5→76.0、物体 30.0→82.5、位置 12.5→45.0 | 世界模型能在训练分布外生成有效纠正 |

## 图表、公式与表格线索

| 图 / 表 | 读图重点 | 关联问题 | 本地文件 |
| --- | --- | --- | --- |
| Figure 1（总览） | 左闭环右柱状；一眼给出 0.38→0.82 与步数下降 | 全文缩影 | `methods_01_page1.png` |
| Figure 2（框架） | 5 阶段 Recognize/Imagine/Label + Stop-Gradient 注入 | 闭环怎么转 | `pipeline_v5_page1.png` |
| Figure 3（架构） | 联合去噪 + $U_\phi$ 双头 + temporal RoPE 对齐（T=49,N_v=12） | 力与视频如何时间对齐 | `model_arch_v3_page1.png` |
| Setup 图 | 6 任务实拍 + FR3 + D455 + 双 Xense | 证据可信度边界 | `display1_page1.png` |
| Figure 4（想象可视化） | Hanoi/BottleCap 真实失败 vs 想象纠正 | 想象是否补出接触转变 | `Visualization2_page1.png` |
| Figure 5（消融+缩放） | 去生成→0.28、去标注→0.65；1:8→97% | 增益来自哪、想象能否 scale | `Ablation.png` |
| Figure 6（动作分布） | 分布随迭代变宽、超出示教流形 | 为什么会涨 | `action_distribution_v3.png` |
| Figure 7（泛化） | 背景/物体/位置三迁移大幅回升 | 能否迁移到 OOD | `generalization_new.png` |
| 附录图（未嵌入） | 更多消融/泛化/失败案例/可视化 | 需要时回看 | `ablation_appendix2.png`、`generalization_appendix.png`、`failure_case_analysis_appendix2_page1.png`、`Visualization_appendix.jpg`、`task_visualization1/2.jpg` |

> 完整图片清单见 [[papers/images/liu2026taco-tactile-self-corrector/index.md]]。

## 主张-证据-边界矩阵

| 主张 / 结论 | 原文证据 | 证据位置 | 解释 | 边界 / 适用条件 |
| --- | --- | --- | --- | --- |
| 失败是"局部接触失败"、值得专门纠正 | Wipe/Twist 例子 + Table 1 这两列的提升 | §1、Table 1 | 视觉几乎不变而触觉大变，故需触觉纠正 | 这是作者自选的问题切片；长时程/搜索类失败不在其内 |
| 触觉世界模型能想象"接触一致"的纠正 | Fig.4 定性 + Fig.5 去触觉生成 SR 崩到 0.28 | §4.2/4.3 | 触觉进入想象才抓得住 contact-state 转变 | "物理正确"只有代理指标（val-loss/VOC/FL），无独立视频保真基准 |
| KI 适配保住泛化、是主增益来源 | TACO 0.82 vs w/o KI 0.50 | Table 1 | stop-gradient + adaRMSNorm 隔离 VLM 先验 | 代价是触觉能力被限制在 action expert，深层跨模态耦合被舍 |
| 想象数据可规模化降本 | 1:2/1:4/1:8 → 70/93/97% | Fig.5 右 | 更多想象覆盖更广 failure-adjacent 状态 | 仅在 Insert Flower 单任务验证缩放律 |
| 能高效适配 OOD | 背景/物体/位置一轮即 76.0/82.5/45.0 | Fig.7 | 世界模型泛化出训练分布外的有效纠正 | 仅 Wipe Whiteboard 单任务；位置迁移仍只有 45.0 |

## 局限与可追问点

作者明确承认的局限：**想象纠正离线生成、非在线**；只解**局部接触失败**。未来：在线纠正生成 + WM-策略紧耦合。

额外可追问点：

1. **anchor 完全由进度阈值触发**——$U_\phi$ 进度头在某些任务（如 Wipe Whiteboard，w/o KI 一度掉到 0.33/0.35）不稳时，锚点会不会选偏，从而把纠正想象在"错误的地方"？
2. **"想象片段物理正确"缺独立校验**：全靠下游 SR 与 val-loss/VOC/FL 代理背书。有没有可能想象出"看着像纠正、实际不可执行"的片段被 $U_\phi$ 误标为 advantage=1？
3. **触觉仅 12 维 force-torque**，非高分辨触觉图像。对需要**细粒度接触形貌/滑移场**的任务（如布料、易碎物），这个信号是否够？（与姊妹篇 [[@wu2026tactile-wam]] 用触觉图像的路线正好对照。）
4. **temporal RoPE 是启发式 round 对齐**（$T{=}49$ 力 token 挤到 $f{=}13$ 视频时间格），信息压缩比约 4:1。更细的接触事件（比 chunk 更高频）会不会被这层对齐抹平？
5. **缩放律只在 Insert Flower 验证**；1:8→97% 很亮眼，但换到 Move Hanoi Rings 这种低基线任务，想象数据的边际收益是否同样不饱和？
6. **KI 是"保守 routing 先验"**：当有大规模配对 visuo-tactile 数据、或触觉在 RGB 里直接可见时，完全隔离 VLM 是否反而丢掉了可学的跨模态耦合？（与 Tactile-WAM 结论里"learned/adaptive routing 可能更好"同一追问。）
7. **CS 只在成功集上平均**：失败集的步数没进 CS，会不会让"更平滑"的结论对失败率高的方法有利/不利？

## 与当前库的连接

- **最直接的姊妹篇 [[@wu2026tactile-wam]]（Tactile-WAM）**：两篇都锚定 contact-rich、都发现"朴素塞触觉会坏事"，但**解法层次不同**。Tactile-WAM 在**一个 World Action Model 内部**用非对称注意力（VideoClean）防 *tactile pollution*——改的是**架构**；TACO 把世界模型当**外部离线纠正数据引擎**，并用 knowledge-insulation（stop-gradient + adaRMSNorm）保护 VLM 先验——改的是**训练管线**。一个"让触觉在计算图里待对位置"，一个"让触觉数据安全地灌回策略"。强烈建议二者并读，作为"触觉进入 world/action model 的两种范式"。
- **π 家族 [[@intelligence2026pi07-steerable-generalist-robotic]] / [[@intelligence2025pi06-vla-that-learns]]**：TACO 的 base 是 π₀.₅，属同一谱系；π*0.6/RECAP 用**真实经验 RL** 自改进，TACO 用**世界模型合成纠正数据**自改进——可对照"自改进的监督从哪来"（真实经验 vs 想象数据）。
- **[[@pan2026vla-corrector-lightweight-detect]]（VLA-Corrector）**：它在**推理期**轻量检测并纠正、自适应动作时域；TACO 在**训练期**用想象数据把纠正能力**灌进**策略权重。两者是"运行时纠错"与"训练时内化纠错"的互补两层，值得对照。
- **世界模型后训练 [[@qian2026wam-rl]]（WAM-RL）/ [[@yu2026wm-dagger]]（WM-DAgger）**：同属"世界模型驱动的后训练"，但 TACO **不在世界模型里在线 rollout**、也不做长时程预测，而是"真实失败识别 + 局部想象 + 重标注"——正是 §2 里作者刻意切开的坐标。可比较"世界模型是当在线仿真器，还是当离线数据工厂"。
- **人在环纠正 [[@deng2026e2hil]]（E2HiL）/ [[@luo2024precise-dexterous-robotic-manipulation]]（HIL-SERL）**：它们靠人工在失败处介入纠正；TACO 的卖点正是**把这类纠正数据的生成自动化**（"without repeated human intervention"）。可对照"纠正数据：人来造 vs 世界模型来造"的成本-质量权衡。
- **同组/引用近亲（多不在库）**：[[@liu2026last0-latent-spatio-temporal]]（LaST₀，引用 [13]，同 Shanghang Zhang 组）、Video2Act [12]（同组的 dual-system 视频扩散策略）、Hi-WM [19]（human-in-the-world-model）、Twinrl-VLA [20]（数字孪生 RL）、Compliant Residual DAgger [17]（人工纠正的 contact-rich）、RoboDreamer [22]（组合式机器人想象世界模型）。

## 精读路线 / 为什么需要回看

1. 先读 `论文主线` + Fig.1/Fig.2：确认作者把"局部接触失败"定为核心缺口，并把 world model 从"在线仿真器"改成"离线纠错数据引擎"。
2. 再读 `方法细节` + §3.1/§3.3 与 Fig.3：核对世界模型如何联合想象视频+力（temporal RoPE、$F_0$ 锚定）、以及 KI 如何用 stop-gradient+adaRMSNorm 保住 VLM 先验——这是全文两处最实的机制。
3. 然后读 Table 1 + Fig.5：重点看 **TACO vs Filtered BC vs w/o KI** 的三方对照（+39pp / +32pp），以及"去触觉生成→0.28、去触觉标注→0.65"两条消融——增益到底来自哪。
4. 最后读 Fig.6/Fig.7：把"数字更高"升级为"动作空间变宽"与"一轮 OOD 想象即迁移"的机制解释。
5. 若要写 related work / 做方法对照：用 `与当前库的连接` 与 `主张-证据-边界矩阵` 作依据，尤其把 TACO 与 [[@wu2026tactile-wam]] 摆成"触觉进入 world/action model 的两种范式"，不要只引摘要里的 +44pp。
