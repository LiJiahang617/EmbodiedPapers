---
tags:
  - bilingual-reading
  - deep-reading
paper: "[[@wu2026tactile-wam]]"
source_pdf: "[[papers/pdfs/wu2026tactile-wam.pdf]]"
images: "papers/images/wu2026tactile-wam/"
image_index: "[[papers/images/wu2026tactile-wam/index.md]]"
created: 2026-07-05
reading_mode: 生成式精读（逐节读原文 + 读图）
---

# Tactile-WAM: Touch-Aware World Action Model with Tactile Asymmetric Attention

paper:: [[@wu2026tactile-wam]]
pdf:: [[papers/pdfs/wu2026tactile-wam.pdf]]
images:: [[papers/images/wu2026tactile-wam/index.md]]

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| World Action Model, WAM | 世界-动作模型 | 同时预测未来世界状态、生成动作块的机器人策略范式；本文基于视觉预训练的 WAM（DreamZero / Wan2.2 backbone）来做。 |
| contact-rich manipulation | 接触丰富操作 | insertion / assembly / search / reorientation 等成败取决于 slip、jamming、contact normal、毫米级对齐误差的任务，是本文靶心。 |
| tactile pollution | 触觉污染 | 本文命名的失败模式：把 tactile tokens 无约束接进所有 attention 路径，会逼视觉动力学模型去吸收稀疏、局部、事件驱动的触觉信号，反而**损坏视频预测**。 |
| TAAM (Tactile Asymmetric Attention Mechanism) | 触觉非对称注意力机制 | 本文核心方法，由两件事组成：VideoClean mask（决定“在哪”抑制触觉）+ touch-aware bias（决定“何时”让触觉引导动作）。 |
| VideoClean mask | 视频净化掩码 | 一条硬规则：**屏蔽 video-query 读取 tactile key/value，但保留 action-query 读取**，从而保护预训练视觉路径不被触觉污染。 |
| touch-aware bias | 触觉感知偏置 | 只加在 action→tactile 的注意力 logit 上的加性偏置，让动作去噪在“接触正在变化”的触觉锚点上多加注意力。 |
| touch-state / touch-change proxy $c^\tau,\ \Delta c^\tau$ | 触觉状态 / 触觉变化代理 | 从触觉图像运动导出的辅助监督（图中叫 **virtual force / Δvirtual force**）；不是标定力标签、也不是额外观测 token。$c^\tau$ 表接触加载，$\Delta c^\tau$ 强调 first-contact / slip / compression / jamming 这类 step-like 变化。 |
| future tactile register | 未来触觉寄存器 | 与 action horizon 对齐的可去噪 token $X^\tau$，让动作 token 能在“该纠偏的时间步”读到预测的接触状态。 |
| ManiFeel | ManiFeel 基准 | 本文主用的可复现 visuo-tactile 仿真基准（9 任务），支持 RGB-only WAM / 触觉策略 / 本文方法在同一接触任务上对比。 |
| DreamZero | DreamZero（RGB-only WAM 基线） | 把视频生成 backbone 改造成联合预测未来观测 + 动作块的 WAM，是本文最核心的“只用视觉”对照组。 |
| Wan VAE / UniT tactile encoder | Wan 视频编码器 / UniT 触觉编码器 | 视觉 token 用 Wan VAE 编码，触觉 token 用冻结的 UniT-style 连续触觉表示编码。 |
| Tac-UMI gripper / xArm | Tac-UMI 夹爪 / xArm 机械臂 | 真实机器人平台：xArm + Tac-UMI 式夹爪 + RealSense L515 + 指端 fisheye/触觉，用于 5 个真实接触任务。 |

## 论文主线

![[papers/images/wu2026tactile-wam/fig1_arxiv.png|760]]

**Figure 1 / 全文动机与总览。** 左上 RGB-Only WAM 能生成“看起来合理的视频”，却 **plausible video, missing contact**——底下三个小图点名了三种被 RGB 藏起来的接触失效：**slip（滑移）**、**jamming（卡滞）**、**misalignment（错位）**。中上 Naïve VT-WAM（把触觉直接塞进去）到第四帧画面直接崩成噪声，配字 **Tactile Pollution / Tactile disturbs visual prediction**。右上 Tactile-WAM 四帧干净稳定，配字 **Asymmetric Routing / TAAM: Asymmetric Block Attention**。中间黑框是架构：Video/Tactile/State/Action 四个 encoder → TAAM（**Video→Tactile 记为 Blocked，Action→Tactile 记为 Allowed +Bias**）→ Causal Wan DiT。最底部三个真实机器人小案例最能说明“为什么要预测触觉变化”：**Aligned → keep → continue**（稳定就继续）、**Slip → correct → Retract**（滑移时 ΔForce 出现 local change + Δspike，就纠偏/回撤）、**Jamming → safety → Back off**（卡滞时 ΔForce 大幅上升，就退让）。这张图一眼给出全文的因果链：接触*变化*才是动作决策的信号。

这篇论文的核心问题是：**World Action Model 已经能把“预测未来 + 生成动作”耦合起来，但它预测的“未来”几乎全是视觉的**——世界被表示成“未来画面长什么样”。可是在接触丰富操作里，决定下一步纠偏的往往是 contact onset、slip、jamming、contact normal、毫米级 tilt，这些在 RGB 里弱可见、被遮挡、甚至根本不出现。于是“视觉上合理的 rollout”可能“物理上不完整”。

一个自然的补法是把 tactile tokens 加进 WAM。但作者指出这里有个反直觉的坑：**触觉是稀疏、局部、事件驱动的**，如果让它参与每一条 attention 路径，视觉动力学模型会被迫去“消化”这些对未来画面弱预测性的信号，结果**视频预测本身被搞坏**——作者把这个失败模式命名为 **tactile pollution（触觉污染）**。第二个问题是 **incomplete touch awareness**：一个触觉 WAM 应该知道触觉“何时”才与动作相关，最有用的不是“有没有触觉 token”，而是 step-like 的接触*变化*。

作者的回答是 **TAAM（触觉非对称注意力）**，用两把手术刀而不是一把大锤：
1. **VideoClean mask** 回答“在哪抑制”——单向切断 video-query 对 tactile key/value 的访问，但**保留 action-query 的访问**。视觉路径干净，动作路径还能用触觉。
2. **touch-aware bias** 回答“何时引导”——从 touch-change proxy（≈Δvirtual force）算一个只加在 action→tactile logit 上的偏置，让动作去噪在“接触正在变化”的锚点上加注意力。

阅读时要盯住一句话：**本文的贡献不是“触觉有用”（前人早证明了），而是“触觉该被放在计算图的哪个位置”**——作为一个被接触动力学监督、且只沿非对称动作路径注入的“被生成的物理状态”，而不是无差别的跨模态注意力来源。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| 把接触丰富操作建模为“未来视觉 latent + 未来触觉接触状态 + 动作块”的联合预测（touch-aware WAM）。 | Eq.(2)、§III-A 联合 token 序列 $X=[X^v\mid X^\tau\mid X^a\mid X^s]$。 | 仿真 44.7% vs DreamZero 5.8%（Table III）。 | 概念清晰、增益大；但仍限于单臂指端触觉、9 个仿真任务。 |
| 识别 **tactile pollution** 并提出 **VideoClean** 非对称掩码保护视觉预测。 | Eq.(4)(5)，§III-B。 | Table I：VideoClean 使 RGB MSE −4.42%、PSNR +0.14dB；Table II：Naive VT-WAM 反而从 5.8% 掉到 1.3%。 | 有直接实验支撑，是本文最扎实的一环。 |
| 提出 **touch-aware bias**，用预测的接触*变化*调制动作对触觉的注意力。 | Eq.(6)(7)(13)-(16)，§III-C。 | Table II：加了 proxies & bias 才从 4.9% 跳到 44.7%。 | 消融显示它是“大头增益”来源；但 bias 形状是启发式（阈值+tanh 饱和）。 |
| 在仿真与真实机器人上验证，接触任务增益尤其大。 | §IV，Fig.3/Fig.4。 | 仿真 contact-centric 子集 87.5%（vs DreamZero 1.5%）；真实 51%（+33 百分点）。 | 真实迁移成立；但 bulb/peg insertion、object search 仍是失败点。 |

## 摘要与核心贡献

摘要提出的矛盾是：WAM 同时生成动作与预测未来，是很好的决策接口，但在接触丰富操作里，**视觉上合理的未来可能物理上不完整**——insertion/assembly/search/reorientation 依赖的 slip、jamming、contact normal、微小对齐误差在 RGB 里弱可见或隐藏。直接预测未来触觉状态看似自然，却会触发 **tactile pollution**：无约束的 tactile-token 注入逼迫视觉动力学模型去吸收稀疏、局部、事件驱动的接触信号，从而**同时损害视频预测和动作预测**。

Tactile-WAM 的回答是一个带 **TAAM** 的 touch-aware WAM：

- **VideoClean mask**：屏蔽 video-query 对 tactile key/value 的访问，同时保留 action-query 的访问——保护视觉预测，又让接触信息留给动作生成；
- **touch-aware bias**：从预测的接触变化导出，在去噪过程中调制动作对触觉 token 的注意力。

摘要给的头号数字是：在 **ManiFeel** 上，Tactile-WAM 把 mean success rate 整体提升 **38.9%**、在 contact-rich 任务上提升 **86%**。

> 读原文才发现的一处细节：整体“38.9%”是 44.7% − 5.8% ≈ 38.9 **百分点**（相对 DreamZero）；“86%”则是 contact-centric 子集 87.5% − 1.5% ≈ 86 **百分点**（Table III）。都是“百分点提升”，不是绝对成功率，引用时别写成“成功率 86%”。

作者的实验结论是：**只保护视频（VideoClean）必要但不充分**，必须再加上“预测接触变化 + touch-aware bias 引导动作去噪”，才能把成功率从接近基线拉到 44.7%。

## 1. Introduction / 为什么视觉 WAM 在接触任务里不够

WAM 把动作生成和未来状态预测耦合，让策略能推理“这个动作块会诱发什么”，而不只是“下一步输出哪个动作”。它继承了通用机器人策略（大规模数据、语言条件、action chunking、生成式动作解码器）和视频生成先验。**但绝大多数 WAM 仍是“主要视觉的”：预测的世界 = 未来画面怎么长。**

接触丰富操作暴露了这个视觉未来的局限。作者把两个 attention 层面的问题讲得很清楚：

1. **Tactile pollution（触觉污染）**：因为触觉稀疏、局部、事件驱动，让 tactile token 去条件化每条 attention 路径，会逼视觉动力学模型吸收“对未来视频弱预测”的信号，退化视频预测或视觉主导行为。
2. **Incomplete touch awareness（触觉感知不完整）**：触觉 WAM 应知道触觉“何时”变得与动作相关——最有用的是 step-like 接触变化（first contact / slip onset / compression change / jamming），而非 tactile token 的存在本身。

据此作者提出 Tactile-WAM：和近期触觉 WAM 一样预测未来视觉 latent、未来触觉接触状态、动作块；**其区别在于触觉如何通过 TAAM 影响注意力**——VideoClean 决定“touch 在哪该被压制”，touch-aware bias 决定“touch 何时该引导动作”。作者把贡献列为四点：touch-aware WAM 建模、tactile pollution + TAAM、touch-aware 动作去噪、仿真与真实评估。

**这一节读法**：introduction 的价值在于它没有停在“触觉有用”，而是把问题精确到“注意力路由”这一层——后面每个方法组件都对应 introduction 里的一个具体失败模式，可以逐一回勾验证。

## 2. Preliminaries & Formulation / 问题定式

在决策时刻 $t$，模型观测视觉历史 $o^v_{\le t}$、触觉历史 $o^\tau_{\le t}$、本体状态 $s_{\le t}$ 和语言指令 $l$。给定动作 horizon $H$，一个**视觉 WAM** 预测未来视觉 latent 和动作块：

$$
p_\theta\!\left(z^v_{t+1:t+T},\ a_{t:t+H-1}\ \middle|\ o^v_{\le t},\ s_{\le t},\ l\right)\tag{1}
$$

**Tactile-WAM** 在此基础上加入触觉观测，并额外预测未来触觉接触状态 $z^\tau$：

$$
p_\theta\!\left(z^v_{t+1:t+T},\ z^\tau_{t+1:t+K},\ a_{t:t+H-1}\ \middle|\ o^v_{\le t},\ o^\tau_{\le t},\ s_{\le t},\ l\right)\tag{2}
$$

关键设定：**推理时，未来触觉状态和动作都从噪声初始化、联合去噪；ground-truth 未来触觉只当训练 target**。这一点很重要——它决定了后面 touch-aware bias 在推理时“无法用真值、只能用上一步预测”的设计（见 §3.4）。

## 3. Method / 方法细节

### 3.1 Overview / 单 backbone + 联合去噪

![[papers/images/wu2026tactile-wam/fig2.png|760]]

**Figure 2 / 方法总览（四步）。** ①**Observed context**：RGB 历史 + 左右指触觉历史 + 机器人状态 + 语言（“insert the plug”）+ 三路噪声（future video latents / tactile registers / action chunk，均 $\sim\mathcal{N}(0,I)$），并注明 **“No clean future touch at inference.”** ②**Single Wan-based WAM**：一个 Wan-based transformer 去噪 backbone，对 video/tactile/action/state 四类 token **联合去噪**。③**Tactile Asymmetric Attention**：左边 VideoClean 是一张 4×4 的 query→key 允许表（**Video-Query→Tactile-Key = ✗ blocked；Act-Query→Tactile-Key = ✓ allowed +bias**，其余全 ✓）；右边 touch-aware bias 支路把 tactile hidden state 经 lightweight MLP proxy head 算出 **virtual force $f_{vf}$ 与 Δvirtual force $\Delta f_{vf}$**，再 $\lVert\Delta f\rVert_2\to$ threshold+tanh $\to$ additive bias，且**只加在 action-to-tactile logits 上**。④**Joint outputs**：未来视频、未来触觉接触状态、每指 contact trace、动作块，外加可选诊断（$f_{vf}$、$\Delta f_{vf}$ 曲线）。底部点明 Training/Inference 的 bias 来源差异。

Tactile-WAM 用**单个** Wan/WAM 兼容的去噪 backbone，作用在联合 token 序列上：

$$
X = [\,X^v \mid X^\tau \mid X^a \mid X^s\,]\tag{3}
$$

其中 $X^v,X^\tau,X^a,X^s$ 分别是视觉 token、未来触觉寄存器、动作 token、上下文 token。**未来触觉寄存器与 action horizon 对齐**，这样动作 token 就能“在生成纠偏动作的那些时间步”读取预测的接触状态——这是让触觉真正作用于动作的结构前提。触觉由 TAAM 的两个注意力组件实现：VideoClean 保护视觉路径，touch-aware bias 在“预测会发生接触变化”的锚点上增强动作注意力。

### 3.2 VideoClean 注意力掩码 / 决定“在哪抑制”

Eq.(2) 规定了要预测什么，但没规定 tactile token 该条件化哪些注意力路径。朴素做法是所有 token 组互相 attend（含 video-query 读 tactile key/value），这种**对称注意力**正是 tactile pollution 的温床。VideoClean 用一条硬掩码打断它：

$$
M^{vc}_{q,k} =
\begin{cases}
-\infty, & G(q)=V,\ G(k)=\tau \\
0, & \text{otherwise}
\end{cases}\tag{4}
$$

$$
\bar{B}_{q,k} = B^{0}_{q,k} + M^{vc}_{q,k}\tag{5}
$$

$G(\cdot)$ 是 token 组，$V/\tau$ 分别是视频/触觉 token，$B^0$ 是 backbone 原有的 causal/blockwise/local 注意力规则。**方向是关键**：VideoClean 只切断 *video-query → tactile-key/value*，保留 *action-query → tactile*。于是触觉被拦在视频预测路径之外，却仍对动作去噪可用——这就是标题里“asymmetric（非对称）”的字面含义。

### 3.3 触觉代理与 touch-aware bias / 决定“何时引导”

为让触觉隐状态变得“与动作相关”，Tactile-WAM 用两个 **motion-derived**（从触觉图像运动导出）的代理来 ground 它：touch-state proxy $c^\tau$ 和 touch-change proxy $\Delta c^\tau$。二者**都不是标定力标签、也不是额外观测 token**，只是辅助 target（图中直观叫 virtual force / Δvirtual force）：

$$
\Delta c^\tau_i = c^\tau_i - c^\tau_{i-1}\tag{10}
$$

$c^\tau$ 表局部接触加载，$\Delta c^\tau$ 强调 first contact / slip onset / compression change / jamming / realignment 这类 step-like 转变。一个轻量 proxy head $D_\phi$ 从触觉隐状态预测触觉速度、touch-state、touch-change，并用 SmoothL1 监督：

$$
L_{\text{state}} = \mathrm{SmoothL1}(\hat{c}^\tau,\ c^{\tau,\star}),\qquad
L_{\text{change}} = \mathrm{SmoothL1}(\widehat{\Delta c^\tau},\ \Delta c^{\tau,\star})\tag{12}
$$

**touch-aware bias** 只从 touch-change 算（显式偏好“接触变化”而非“接触大小”）。对第 $i$ 个触觉锚点，先取变化幅度，再经阈值 + 饱和非线性得到分数，最后 clip 成加性偏置：

$$
d_i = \lVert \Delta c^\tau_i \rVert_2\tag{13}
$$

$$
s_i = \mathrm{clip}_{[0,1]}\!\left(\tanh\frac{\mathrm{ReLU}(d_i-\theta)}{T_c}\right)\tag{14}
$$

$$
b^\tau_i = \mathrm{clip}(\alpha\,s_i,\ 0,\ b_{\max})\tag{15}
$$

偏置**只加在 action-query–tactile-key 的注意力 logit 上**：

$$
B_{q,k} = \bar{B}_{q,k} + \mathbb{I}[\,G(q)=A,\ G(k)=\tau\,]\ b^\tau_{a(k)}\tag{16}
$$

$a(k)$ 是 tactile key $k$ 所属的锚点。作者强调：这个 bias **不缩放触觉特征、不影响 video query、也不对所有 token 组增强触觉注意力**——它只让动作去噪在“接触被预测为正在变化”的锚点上更用力地看触觉。当 $b^\tau_i=2$ 时，未归一化 softmax 权重相当于乘 $\exp(2)$。

> 触觉 token 是怎么来的（Appendix B）：每个 action chunk 用 $A$ 个锚点、每锚点 $S=2$ 个指端传感器、每对压成 $Q$ 个 slot token，故触觉 token 总数 $L_\tau = A\,S\,Q$（Eq.8）；每个寄存器 $r^\tau_{i,s,q}=W^\tau\tilde{z}^\tau + e^{\text{time}}+e^{\text{anchor}}+e^{\text{sensor}}+e^{\text{slot}}$（Eq.9），四种 embedding 让动作 token 按预测 horizon 对齐读取未来接触。触觉编码器是冻结的 UniT-style 连续触觉表示。

### 3.4 训练与推理 / 一个绕不开的因果难题

训练时未来触觉与动作都是去噪变量，clean 值与噪声插值（Eq.17），总损失联合五项：

$$
L = L_{\text{video}} + \lambda_a L_{\text{action}} + \lambda_\tau L_{\text{tactile}} + \lambda_s L_{\text{state}} + \lambda_c L_{\text{change}}\tag{18}
$$

这里有个 **teacher-forcing 的因果难题**：touch-aware bias 要在 forward pass *内部*就用上，但 proxy-head 的预测 $\widehat{\Delta c^\tau}$ 只有 forward *之后*才有。作者的处理是——**训练**时 bias 直接用真值 $\Delta c^{\tau,\star}$（teacher forcing）；**推理**时既没有未来触觉真值、也没有 target proxy，于是第一步去噪不加 bias，从第二步起用**上一步预测的** touch-change：

$$
b^{\tau,(0)}_i = 0,\qquad b^{\tau,(m)}_i = g\!\left(\widehat{\Delta c^\tau}^{(m-1)}_i\right),\ m\ge 1\tag{19,20}
$$

**这一节读法**：Eq.(19)(20) 是把 Eq.(2) 那句“推理时未来触觉从噪声开始”落到实处的地方——它保证了方法在部署时不偷看未来标签。要追问的是：推理早期几步 bias 缺失或基于粗糙预测，对短 chunk 任务是否够用。

## 4. Experiment / 实验

### 4.1 Setup / 基准、基线、平台

- **仿真**：ManiFeel 基准，9 个任务（ball sorting、bolt-nut、bulb insertion、gear insertion、object search、peg insertion、peg reorientation、power insertion、USB insertion），每任务 50 rollouts。**contact-centric 子集** = bolt-nut + gear + power + USB（成败最直接依赖局部接触演化）。
- **基线**：$\pi_{0.5}$-based 通用动作策略（从 LeRobot base 起）；**DreamZero-based RGB-only WAM**（与本文一样继承 Wan2.2 预训练权重，是最关键的“只用视觉”公平对照）。
- **真实**：xArm + Tac-UMI 式夹爪 + RealSense L515 + 指端 fisheye/触觉（见 Fig.4），5 个接触任务。

![[papers/images/wu2026tactile-wam/fig_real_setup.png|760]]

**Figure 4 / 真实机器人平台。** 左列点明数据采集用 Tac-UMI Gripper（含 Gripper / Fisheye Camera / Xsense 三件套），右列是 RealSense L515、xArm、指端 Fisheye Cam。桌面 fixtures：Plug & Socket、Nut & Thread、Gear Mesh、Bulb、Peg & Socket。这张图的作用是证明**真实任务确实是“接触敏感、外部 RGB 难看清”的装配/插接**，与仿真的 contact-centric 设定对齐，从而让 sim→real 的趋势可比。

### 4.2 Simulation Results / 主结果

![[papers/images/wu2026tactile-wam/fig3_arxiv.png|760]]

**Figure 3 / 仿真对比（π0.5 白 / DreamZero 蓝 / ours 绿）。** 注文点明“DreamZero 和 ours 都继承 Wan2.2 预训练权重”，即两者除“有没有触觉路由”外条件相当。整体上 ours 44.7% 远超 DreamZero 5.8% 和 π0.5 1.3%；接触任务（bolt nut、insertion）差距最大，视觉主导任务（ball sorting）差距很小。

> **数字口径提醒**：Fig.3 是 caption 自述的 “earlier evaluation run”，与作为 complete 结果的 **Table III** 存在出入（如 object search 在 Fig.3 显示 ours 12%，但 Table III 是 0%）。下表以 **Table III（complete）为准**。

Table III（每格 = 50 次评测中的成功率）：

| Task | $\pi_{0.5}$ | DreamZero | Tactile-WAM |
| --- | ---: | ---: | ---: |
| ball sorting | 0% | 46% | 52% |
| bolt-nut assembly | 0% | 6% | **72%** |
| bulb insertion | 0% | 0% | 0% |
| gear insertion | 0% | 0% | **100%** |
| object search | 0% | 0% | 0% |
| peg insertion | 0% | 0% | 0% |
| peg reorientation | 12% | 0% | 0% |
| power insertion | 0% | 0% | **78%** |
| USB insertion | 0% | 0% | **100%** |
| **Overall** | 1.3% | 5.8% | **44.7%** |
| **Contact-centric 子集** | 0% | 1.5% | **87.5%** |

**这张表要分三类读**：
1. **接触主导任务**（bolt-nut 72%、gear 100%、power 78%、USB 100%）：Tactile-WAM 从近乎全灭的基线大幅拉起，这正是 touch-aware WAM 的主场——成败取决于 first contact / 对齐 / jamming 的地方。
2. **视觉主导任务**（ball sorting）：DreamZero 46% 已经不差，Tactile-WAM 52% 只多一点——触觉增益小，符合直觉。
3. **仍然失败的任务**（bulb/peg insertion、object search、peg reorientation 都是 0%）：作者诚实承认——touch-aware WAM 主要解决 contact-sensitive correction，**不解决 visual search、exploration、long-horizon**。$\pi_{0.5}$ 的 6 个成功全落在 peg reorientation（12%），也印证不同方法的“能力错位”。

### 4.3 Component Analysis / 消融（Table II，最关键的一张）

| 方法 | Future Touch | VideoClean | Proxies & Bias | Success |
| --- | :---: | :---: | :---: | ---: |
| RGB-only WAM | ✗ | ✗ | ✗ | 5.8% |
| Naive VT-WAM | ✓ | ✗ | ✗ | **1.3%** ↓ |
| + VideoClean | ✓ | ✓ | ✗ | 4.9% |
| Full Tactile-WAM | ✓ | ✓ | ✓ | **44.7%** |

这张表几乎独立证明了全文论点：
- **Naive 加触觉反而掉到 1.3%**（低于 5.8% 的纯视觉基线）——tactile pollution 是真实存在的，不是修辞。
- **加 VideoClean 恢复到 4.9%**，但仍≈基线——“保护视频预测”**必要但不充分**。
- **再加 proxies & touch-aware bias 才跳到 44.7%**——真正的增益来自“预测接触变化 + 用它引导动作去噪”，而不仅是“把触觉塞进来”。

### 4.4 VideoClean 预测质量分析（Table I）

在 5K checkpoint、108 个任务均衡样本（9 任务、4-chunk horizon）上，比较 non-clean 与 VideoClean：

| Metric | Non-clean | VideoClean | Change |
| --- | ---: | ---: | ---: |
| RGB MSE ↓ | 0.01524 | 0.01457 | −4.42% |
| RGB MAE ↓ | 0.05813 | 0.05732 | −1.39% |
| PSNR ↑ | 18.91 | 19.05 | +0.14 dB |
| Global SSIM ↑ | 0.9054 | 0.9072 | +0.0017 |

**证明什么**：VideoClean 一致改善解码 RGB 预测质量。数值增量看着不大，但方向全对，且与 tactile-pollution 假设一致——**屏蔽 video-query 对 tactile key/value 的访问，确实帮视觉预测路径保住了质量**。定性上（Appendix E / Fig.9）non-clean 会在预测的夹爪和物体区域引入可见 artifact 和几何畸变，VideoClean 则保住结构。

### 4.5 Real-Robot Results / 真实迁移

5 个接触任务（bolt-nut assembly、bulb insertion、gear insertion、peg insertion、power insertion），同一观测/动作/协议下：Tactile-WAM **51/100 = 51%**，比 RGB-only DreamZero **+33 百分点**，比 $\pi_{0.5}$ **+41 百分点**。真实趋势与仿真一致：**接触敏感对齐、接触转变检测、纠偏插入**处增益最大；robust visual search 与 long-horizon recovery 仍是开放难题。

## 5. Conclusion / 结论与局限

**结论**：Tactile-WAM 预测未来触觉接触状态，并对触觉做**选择性路由**——用 VideoClean 保护视觉预测不被污染，用触觉*变化*引导动作去噪，从而在 ManiFeel 和真实接触任务上提升 contact-sensitive 表现。剩余失败点直指更强的 visual search、recovery 和 long-horizon reasoning。

**作者自陈的局限（Appendix D）**：

- 依赖时间对齐的 RGB / 本体状态 / 动作 / 指端触觉；更快的灵巧操作里接触事件可能比 policy horizon 更高频，需要更密/异步/事件触发的触觉采样与多指感知。
- 触觉监督来自 tactile-image motion proxy，不是标定 force/torque，**不能当 metric force 用**；跨基准部署需显式测量传感器延迟、掉帧、标定漂移、动作-触觉错配。
- VideoClean/TAAM 是为“视觉预训练 backbone”设计的**保守 routing 先验**；当触觉形变在 RGB 里直接可见、或有大规模配对 visuo-tactile 数据时，**learned/adaptive routing 可能更好**。

## 图表索引与讲解

| 图 / 表 | 读图重点 | 关联问题 |
| --- | --- | --- |
| Figure 1 | RGB-only 漏接触；Naive 触觉污染崩画面；TAAM 非对称路由保画面。底部 Aligned/Slip/Jamming 三案例把 Δforce 映射到 keep/correct/back-off。 | 为什么不能把触觉无差别塞进 WAM。 |
| Figure 2 | 四步流水：观测→单 Wan backbone 联合去噪→VideoClean 允许表 + touch-aware bias 支路→联合输出；Training 用真值 Δf，Inference 用上一步预测 Δf。 | 触觉“在哪抑制/何时引导”如何在一个 backbone 里实现。 |
| Figure 3 | 仿真柱状图；接触任务差距大、视觉任务差距小；注意它是 earlier run，数字以 Table III 为准。 | 触觉增益集中在哪类任务。 |
| Figure 4 | xArm + Tac-UMI 夹爪 + L515 + 指端 fisheye/触觉；5 类插接装配 fixture。 | 真实任务是否真的“接触敏感、外部 RGB 难看清”。 |
| Table I | VideoClean 一致改善 RGB MSE/MAE/PSNR/SSIM。 | VideoClean 是否真的缓解 tactile pollution。 |
| Table II | Naive 掉分→VideoClean 回不到位→加 bias 才跳到 44.7%。 | 增益到底来自哪个组件。 |
| Table III | 逐任务真实成功率；contact-centric 87.5%，但 bulb/peg/search 仍 0%。 | 方法的能力边界在哪。 |

## 和你的论文库中其他条目的关系

- 对 [[@wang2026wvm]]（World Value Model）：两者都在追问“world model 在机器人里除了生成画面还能干什么”。WVM 把世界模型的时间/未来建模能力用来**给数据/进展打分**；Tactile-WAM 则把世界模型扩展成**预测物理接触状态并回灌动作**。可对照“world model 的输出被当作 value 还是当作 action 条件”。
- 对 [[@wang2026orca]]、[[@gigaworld2026roadmap]]、[[@zhang2026qwen-robotworld]]、[[@gao2026fast-leworldmodel]]（世界模型路线）：这些多聚焦视觉/latent 世界建模与规划；Tactile-WAM 的独特主张是**视觉未来只是部分世界状态**，必须补上局部接触动力学。它给“世界模型该预测哪些物理变量”提供了一个反例式论据。
- 对 [[@zhou2026holoagent0]]（空间记忆与智能体）、[[@li2026zr0]]（VLA 训练与推理监督）：Tactile-WAM 处在更底层的“接触闭环”，与 agent 级的记忆/规划、VLA 级的动作表示是互补层次，可作“从高层规划到指端接触”的纵向串读。
- **触觉线**：当前库里触觉论文暂时只有本篇。你之前想入库的 **HTT（Heterogeneous Tactile Transformer）** 和 **TactX（跨传感器共享触觉表示）** 正好能和它组成一条线——它们偏“触觉表示/跨传感器泛化”，Tactile-WAM 偏“触觉如何进入世界-动作预测”。入库后建议重点比较：触觉编码器（本文用冻结 UniT）是否可换成 HTT/TactX 的表示。
- 论文自身引用的近亲（**均不在当前库**，如需可另行入库）：DreamZero [19]（RGB-only WAM 基线）、Dream-Tac [10]、VTAM [20]、OmniVTA [24]、VT-WM [5]、DreamTacVLA [18]、TacForeSight [22]，以及触觉传感器经典 GelSight [21]、DIGIT [8]。

## 可追问点

1. touch-change proxy = Δvirtual force 是从触觉图像运动导出的，作者反复强调“不是标定力”。那么当传感器漂移或掉帧时，$\Delta c^\tau$ 的可靠性如何？bias 会不会被伪变化误触发？
2. bias 只用 touch-*change*、不用 touch-*magnitude*（Eq.14 明确偏好变化）。在需要“稳定持握力”而非“检测变化”的任务上，这个选择是否会失分？
3. 推理时前几步 bias 缺失或来自粗糙预测（Eq.19,20）。chunk 越短，这个“冷启动”占比越大——短 horizon 任务是否更吃亏？
4. bulb insertion 在仿真里 0%、却是真实 5 任务之一且整体 51%。仿真-真实为何在同名任务上差这么多？是任务实现差异还是触觉信号质量差异？
5. VideoClean 是硬 mask（−∞）。作者也承认当触觉形变在 RGB 里直接可见时 learned routing 可能更好——有没有中间态（软 gate / 可学掩码）能兼顾？
6. contact-centric 子集 87.5% 很亮眼，但它只含 4 个装配/插接任务。这个子集的定义是否对本方法有利？换一组“接触但非插接”的任务（如擦拭、翻页）是否还成立？

## 我的阅读笔记

这篇的真正价值不在“又一个触觉 WAM”，而在它把问题从“要不要用触觉”重构成 **“触觉该被放在计算图的哪个位置”**。它给出的答案很克制：触觉是一个**被接触动力学监督、被生成出来的物理状态**，只沿**非对称的动作路径**注入，而不去碰视觉预测。Table II 那条“Naive 加触觉反而从 5.8% 掉到 1.3%”是全文最有说服力的一击——它把 tactile pollution 从一个说法变成了可测的现象，也让 VideoClean 的动机无法被绕过。

但要清醒地看边界：**增益高度集中在插接/装配这类 contact-centric 任务**，bulb/peg insertion、object search、peg reorientation 在仿真里仍是 0%；真实整体 51% 也说明离“可靠部署”尚远。方法里 bias 的形状（阈值 + tanh 饱和 + clip）是启发式的，touch proxy 是 motion-derived 而非标定力——这两点决定了它现在更像“一个把触觉正确接进视觉 WAM 的架构原则”，而不是“一个即插即用的接触操作 recipe”。

我会把它作为**“触觉如何进入世界-动作模型”**这条线的入口，和世界模型价值化的 [[@wang2026wvm]] 交叉读：一个把 world model 的未来能力用于*评估*，一个用于*预测物理状态并驱动动作*。等 HTT / TactX 入库，再从“触觉表示层是否可替换/可跨传感器泛化”这个角度回看本文冻结的 UniT 触觉编码器。
