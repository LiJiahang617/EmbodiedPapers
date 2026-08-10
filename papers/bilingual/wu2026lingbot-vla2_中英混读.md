---
tags:
  - bilingual-reading
  - deep-reading
  - vla
  - cross-embodiment
paper: "[[@wu2026lingbot-vla2]]"
source_pdf: "[[papers/pdfs/wu2026lingbot-vla2.pdf]]"
images: "papers/images/wu2026lingbot-vla2/"
image_index: "[[papers/images/wu2026lingbot-vla2/index.md]]"
created: 2026-07-15
reading_mode: 复现级人工精读（全文 + 公式 + 表格 + 图题）
---

# From Foundation to Application: Improving VLA Models in Practice

paper:: [[@wu2026lingbot-vla2]]
pdf:: [[papers/pdfs/wu2026lingbot-vla2.pdf]]
images:: [[papers/images/wu2026lingbot-vla2/index.md]]

## 核心词汇速查

| English | 中文 | 在本文中的精确作用 |
| --- | --- | --- |
| Vision-Language-Action (VLA) | 视觉—语言—动作模型 | 以图像、语言指令和机器人状态为条件，输出连续动作 chunk；本文将其从双臂桌面操作扩展至多本体全身控制。 |
| cross-embodiment pretraining | 跨本体预训练 | 在 20 种机器人构型上联合训练，让共享模型学习跨平台的操作规律，同时由稀疏专家吸收本体差异。 |
| canonical action vector | 规范动作向量 | 把 arm/EEF/gripper/hand/waist/head/base 填入统一 55D 槽位；不存在的部件 padding，并配合维度 mask。 |
| relQpos / absQpos | 相对/绝对关节位置 | 实验表明 relQpos 把全局姿态回归变成低方差局部运动回归，平均成功率 33.7%→55.0%。 |
| end-effector (EEF) action | 末端执行器动作 | Cartesian 位姿控制；与 joint action 平均相近，但 contact-rich、可达性和数据分布使不同任务各有偏好。 |
| loss-free MoE | 无辅助损失 MoE | 不把 load-balancing loss 加进动作目标，而用 routing bias 修正专家负载；保留无偏 affinity 作为混合权重。 |
| shared / routed expert | 共享/路由专家 | shared expert 每 token 必经，编码通用控制先验；Top-K routed experts 稀疏激活，吸收任务/本体专门化。 |
| dual-query distillation | 双查询蒸馏 | 在 VLM token 中追加当前查询 $Q_t$ 和未来查询 $Q_{t+T}$，分别对齐当前/未来的深度与视频 teacher 特征。 |
| DINO-Video | 因果视频表征 teacher | DINOv3 加 block-wise causal temporal attention 与 3D-RoPE，在 5M clips 上训练，为未来 query 提供运动语义目标。 |
| action chunk horizon $T$ | 动作块时域 | 未来 query 的预测跨度与策略一次输出的 action chunk 长度一致，使视觉未来目标与控制时间尺度对齐。 |
| progress score | 任务进度分 | 将长任务拆成带权子步骤；比二元成功率更能区分“已推进但最后一步失败”。 |

## 摘要
LingBot-VLA 2.0 不是只改一个网络层，而是一篇围绕 practical VLA（可落地 VLA）的系统论文。作者把实验室模型到真实部署的差距拆成三个相互耦合的缺口：训练数据覆盖的机器人本体和任务不够广；动作接口通常只覆盖双臂和夹爪，无法控制 head、waist、mobile base、dexterous hand；策略对当前图像反应，却没有被明确要求表征未来几何和运动后果。

系统对应做三类改造。数据侧从约 90,000 小时、20 种机器人原始轨迹中过滤出 50,000 小时高质量轨迹，并从约 20,000 小时第一视角人类视频中保留 10,000 小时，通过 SLAM 和 MANO pose 将手运动重建到世界坐标。接口侧把所有 state/action pack 到 55D canonical vector，并用相对关节动作、MeanStd normalization 和 L2 regression 降低跨任务回归难度。模型侧在 action expert 的所有 FFN 位置放入 token-level loss-free MoE，再追加 $Q_t,Q_{t+T}$ 两组 query，以 LingBot-Depth 和 DINO-Video 分别蒸馏当前/未来几何与运动语义。

实验在 GM-100 的九个双臂任务和两个长时程移动操作上进行。LingBot-VLA 2.0 在 Agilex 平台平均 progress/success 为 66.2/34.4，对 $pi_{0.5}$ 的 59.1/32.2；在长程冰箱收纳与灶台清洁上，ID 和 OOD 均优于 $pi_{0.5}$。但结果也暴露重要边界：平台之间仍有明显 embodiment gap，许多任务 progress 高于 success，说明最后的精确放置、释放和收尾仍是瓶颈。

## 论文主线

全文可以压缩成一条因果链：

```text
更多但异构的 robot/ego data
        ↓ 质量过滤、坐标统一、动作 packing、语言标注
可比较的 55D state/action + task/subtask instruction
        ↓ VLM understanding expert + sparse MoE action expert
跨本体 action-token 表征
        ↓ Q_t / Q_{t+T} 对齐 Depth 与 causal DINO-Video
同时知道“现在的几何”与“执行一个 chunk 后的场景”
        ↓ continuous action chunk
双臂 / 全身 / 移动操作
```

作者真正的判断是：**VLA 的“泛化”不能只理解成换物体、换指令；实际部署要求模型同时跨 embodiment、跨 action space，并在与动作 chunk 相同的时间尺度上预判未来。** MoE 不是目的，而是让扩大总容量时每个 token 只激活少量专家；dual-query 也不是额外的感知 head，而是通过未来 teacher target 把策略 hidden state 约束为 dynamics-aware representation。

## 1. 🎯 核心思想与动机（The “Aha!” Moment）

### 痛点与动机

现有 VLA 往往在少数双臂平台上使用窄动作接口训练：即使换任务还能工作，一旦换成具有头、腰、移动底盘或灵巧手的机器人，动作维度、动力学和视觉分布同时改变；而只用 action imitation 的目标又允许模型“看懂当前、却不理解动作后果”。

### 核心思想

大白话说，作者做的是先造一张所有机器人的“公共控制表格”：每种身体部件都有固定列，没有该部件就空着；再让每个 action token 自己挑少量专家处理，而不是强迫一个 dense FFN 同时记住所有机器人的控制规律。最后，在模型输出动作时同时考试两道题：“你能还原当前场景的深度/动态特征吗？”和“你能预测执行这一段动作后场景会变成什么特征吗？”——后一道题迫使策略在生成动作前编码未来结果。

## 2. ✨ 核心贡献梳理（Contributions）

- 构建约 60,000 小时的跨本体预训练集：50,000 小时 robot trajectories 覆盖 20 configurations，10,000 小时 egocentric human videos；给出 jerk/Z-score/静止占比、URDF 回放、人审视频、SLAM/MANO 重建等具体 QC 流程。
- 提出覆盖全身部件的 55D canonical state/action representation，并用自动 VLM pipeline 生成 task-level 与 subtask-level 语言标注；18 类闭集动作包含 15 个 manipulation primitives 和 transit/idle/other。
- 在 action expert 内提出 token-level sparse loss-free MoE：一个 shared expert + $N_r$ routed experts，Top-$K$ 稀疏激活；用 correction bias 调负载而不污染 action-learning objective。
- 提出 spatiotemporal dual-query distillation：$Q_t,Q_{t+T}$ 同时回归 LingBot-Depth 的几何 token 与 causal DINO-Video 的 patch feature，让策略表征当前状态并预测 action horizon 后的几何/语义状态。

## 贡献与结论对照

| 论文主张 | 方法位置 | 关键证据 | 结论强度 |
| --- | --- | --- | --- |
| 数据处理和跨本体覆盖提升 generalization。 | §3，Figs.2--6，Tables 1--2。 | 20 embodiments、60k h；GM-100/移动任务。 | 系统结果支持，但数据规模、质量和模型变化同时发生，难完全隔离。 |
| 稀疏 MoE 在相同 active compute 下优于 dense。 | §4.1，Eq.(2)--(8)。 | Fig.7：Dense 0.6B vs MoE 1.6B-A0.6B，MoE 的训练 loss 与验证 action error 更低。 | 对相同 active params 的证据直接；仍需更多规模点验证 scaling law。 |
| future query 注入几何和时间理解。 | §4.2，Eq.(9)--(10)。 | DINO-Video Table 3；Fig.13 current/future depth/PCA 预测。 | 证明可预测 teacher feature；对 action success 的独立增益表格不够完整。 |
| 全身动作和长程任务更强。 | §5，Tables 5--7。 | 两平台、每 task-setting 15 trials，ID/OOD 均高于 $pi_{0.5}$。 | 有真实部署证据，但任务数和平台数仍小。 |

## 结构地图

| 原文 section | 本节推进什么 | 关键图表/公式 |
| --- | --- | --- |
| §1 Introduction | 将 deployment gap 分解为 data/embodiment/prediction 三项。 | Fig.1。 |
| §2 Related Work | 区分 generalist policy、跨本体数据、latent dynamics、MoE VLA。 | 无核心新证据。 |
| §3 Pre-training Dataset | 给出 robot/ego 清洗、统一 action、自动语言标注。 | Figs.2--6，Tables 1--2，Eq.(1)。 |
| §4.1 MoE-based VLA | 定义稀疏专家、sigmoid routing 和 loss-free balance。 | Eq.(2)--(8)，Fig.7。 |
| §4.2 Dual-Query | 以 current/future query 蒸馏 depth/video teacher。 | Eq.(9)--(10)，Table 3。 |
| §5 Experiments | 验证 GM-100 和长时程移动操作。 | Tables 4--7，Figs.8--9。 |
| §6 Ablations | 比较 target、space、normalization、loss，并展示蒸馏感知结果。 | Figs.10--13。 |

## 3. ⚙️ 方法论全景与精细拆解（Detailed Pipeline & Module Breakdown）

### 总体数据流

```text
Robot episodes / Ego videos
→ [QC + coordinate reconstruction]
→ synchronized frames, robot states, 55D actions
→ [VLM task/subtask annotation]
→ image tokens + text tokens + state tokens + noised action tokens
→ [VLM understanding expert + MoE action expert]
→ denoised continuous action chunk
  ↘ [Q_t,Q_{t+T}] → Depth/DINO projections → auxiliary distillation losses
```

### 模块 1：机器人数据清洗与时间同步（Robot Data QC）

**物理/数学意义。** 把“采到了轨迹”变成“图像、状态和动作在物理上可信且时间一致的轨迹”。跨本体预训练的主要风险不是数据少，而是某个平台的噪声和错位会被模型误学成控制规律。

**输入。** 单个 episode 的多视角 RGB 视频 ${I_t^v}$、state $s_t$、action $a_t$、URDF、时间戳和 embodiment ID。不同平台 15/30 Hz，总 DoF 约 8--32。

**内部机制。** 对 action/state 计算一阶速度、二阶加速度、三阶有限差分 jerk，并计算导数 Z-score；阈值按 embodiment 单独设定，任一超阈 episode 丢弃。若所有 state/action 变化很小的时段超过 episode 的 95%，视为静止数据丢弃。随后用 URDF 和记录关节把机器人投影到 image plane，与视频回放比对；人工删除 projection/video 不一致、模糊、严重遮挡、掉帧或多相机错位的样本。

**输出。** 时间同步且运动平滑的 $(I_t^v,s_t,a_t)$ 序列，进入统一 action packing 和语言标注。约 90k h 原始 robot data 最终保留约 50k h；这个 55.6% 保留率说明质量筛选本身是系统的重要部分。

### 模块 2：第一视角人类视频重建（Egocentric Reconstruction）

**物理/数学意义。** 人类视频没有机器人 action，却包含大规模 hand-object interaction。作者把“手在世界中的轨迹”当成可跨视频源共享的 proxy action，再在训练时表达成当前相机坐标系下的未来运动。

**输入。** Ego RGB video $I_{1:L}$；部分样本已有 hand/action label，另一部分没有；可能带相机内参/外参。

**内部机制。** 先用统一 VLM video filter 删除第三人称、纯走路、无手物交互、无可操作物体和非操作者手占主导的视频。已有标签的样本做 metadata、timestamp、coordinate transform 和 completeness check；无标签视频运行 egocentric SLAM 得到 $T^W_{C_t}$，运行 hand pose estimator 得到 camera-frame MANO parameters，再组合为世界系连续手轨迹 $p^W_\tau$。有效 hand pose frame ratio 低于 20%、SLAM 二阶运动突变、手轨迹 displacement/velocity/acceleration/jerk 异常或违反人体约束的样本删除。采样当前帧 $t$ 时执行：

$$
p^{C_t}_{\tau}=T_{C_t\leftarrow W}p^W_{\tau}.\tag{1}
$$

这一步把未来手轨迹表达为“从当前摄像头看，手接下来如何运动”，避免把佩戴者头部运动混入手动作。

**输出。** 当前 ego frame、instruction 和 camera-frame future hand trajectory，pack 到统一动作槽位。20k h 候选约保留 10k h。

### 模块 3：55D 统一状态/动作表示（Canonical Packing）

**物理/数学意义。** 给不同机器人建立字段级同构，而不是假设它们的关节一一对应。模型看到固定宽度 token，但通过有效维 mask 和数据分布知道哪些身体部件存在。

**输入。** 平台原始 joint position、EEF pose、gripper/hand、waist、head、base signal。EEF 单臂表示为 $(x,y,z,q_x,q_y,q_z,q_w)\in\mathbb R^7$。

**内部机制。** 构造 $x_t\in\mathbb R^{55}$：arm joint 14D、双臂 EEF 14D、gripper 2D、dexterous hand 12D、waist 4D、head 2D、mobile base 3D，外加 4D reserved。单臂只写对应一侧的 6/7 joint + 7 EEF，其余 padding；没有 waist/head/hand/base 的平台同样 padding。action target 优先使用 relative joint displacement $\Delta q_t=q_{t+1}-q_t$，并以训练集 mean/std 逐维归一化。

**输出。** 固定形状的 state token 和 action chunk $A_{t:t+T-1}\in\mathbb R^{T\times55}$，传入 action expert。消融说明：relQpos 相比 absQpos 把 pooled raw std 从约 0.80 降至 0.28，目标尺度仅为绝对动作的 31%--37%。

### 模块 4：自动 task/subtask 语言标注

**物理/数学意义。** 让视频与语言在任务级和原子动作级对齐，避免一个长 instruction 对整条长轨迹只提供粗监督。

**输入。** 同步的 overhead/wrist multi-view clips；robot/ego 操作视频。

**内部机制。** Qwen3.6-27B 联合看多相机视角，将视频切成时间连续 subtasks。每段输出：(i) 18 类 closed vocabulary 中的 action type；(ii) open-vocabulary primary object；(iii) concise subtask instruction；整段视频再生成一个 global task instruction。15 个原子动作包括 move/pour/push/pull/rotate/open/close/fold/unfold/wipe/stir/cut/press/attach/detach，辅助类为 transit、idle、other；idle 从训练中滤掉。边界只在对象改变、动作类型改变或持续 pause 进入新 subgoal 时建立，grasp-carry-release 通常合为一个 subtask。

**输出。** 与帧区间对齐的 task-level text $c^{task}$ 与 subtask text $c^{sub}_k$，转为 language tokens 并与视觉/状态 token 一起进入 VLM。

### 模块 5：Token-level Loss-free MoE Action Expert

**物理/数学意义。** 将“跨本体共享规律”和“本体/任务专门化”分开承载；active compute 固定时，通过更多总专家容量降低多分布相互干扰。

**输入。** 第 $\ell$ 层 token $u_{\ell,t}\in\mathbb R^d$，它已融合 image/text/state/noised-action context。MoE 只替换 action expert transformer block 中的 FFN，不替换 attention。

**内部机制。** 一个 shared expert 始终执行，$N_r$ 个 routed experts 中选择 Top-$K$：

$$
m_\ell(u)=E_\ell^{(s)}(u)+\lambda\sum_{j\in R(u)}g_{\ell,j}(u)E_{\ell,j}^{(r)}(u).\tag{2}
$$

每个 expert 是 SwiGLU MLP：

$$E(u)=W_{down}\left[\operatorname{SiLU}(W_{gate}u)\odot W_{up}u\right].\tag{3}$$

FP32 router 用可学习 expert embedding $e_{\ell,j}$ 得到 $z_{\ell,j}=u^\top e_{\ell,j}$，再用独立 sigmoid affinity $s_{\ell,j}=\sigma(z_{\ell,j})$，避免 softmax 迫使专家强竞争。选择集合看加 bias 的 affinity，实际 mixture weight 却保持无偏：

$$
R(u)=\operatorname{TopK}_j(s_{\ell,j}+b_{\ell,j},K),\qquad
g_{\ell,j}=\frac{s_{\ell,j}}{\sum_{k\in R(u)}s_{\ell,k}}.\tag{4--7}
$$

每轮跨 micro-batch/rank 累计专家 token count $n_{\ell,j}$，再按相对平均负载的符号更新 bias：

$$
b_{\ell,j}\leftarrow b_{\ell,j}-\gamma\operatorname{sign}\left(n_{\ell,j}-\frac1{N_r}\sum_kn_{\ell,k}\right).\tag{8}
$$

关键点：$b$ 只决定“谁被选”，不进入 $g$；因此无需给 action loss 加一个会改变优化方向的 auxiliary balancing term。

**输出。** 更新后的 action-token hidden states，经残差连接回 transformer，再由连续动作 head/flow-matching head 输出 action chunk。Fig.7 的 MoE 1.6B-A0.6B 与 Dense 0.6B active params 相当，但训练 loss 和 GM-100 validation action error 都更低。

### 模块 6：Dual-Query Spatiotemporal Distillation

**物理/数学意义。** action imitation 只约束最终动作，不保证 hidden state 显式编码几何和未来。两组 query 把“当前/未来”变成可监督的瓶颈。

**输入。** 图像/文本 token 序列后追加 learnable $Q_t,Q_{t+T}$；teacher 侧输入当前帧 $I_t$ 和执行 horizon 后的真实帧 $I_{t+T}$。$T$ 等于 action chunk size。

**内部机制。** LingBot-Depth 从两帧抽取 depth representations $D_t,D_{t+T}$，cross-attention projection 对齐维度并使用 L1：

$$
\mathcal L_{depth}=\mathbb E[\|P_d(Q_t)-D_t\|_1+\|P_d(Q_{t+T})-D_{t+T}\|_1].\tag{9}
$$

DINO-Video 从 DINOv3 初始化，增加 block-wise causal temporal attention 与 3D-RoPE；在 Internet/ego/robot 共 5M clips 上，以每 clip 16 frames、按 effective FPS 赋 absolute time encoding，并使用 video-adapted DINO+iBOT self-distillation。它在单次 causal forward 中产生 patch-level $Z_t,Z_{t+T}$：

$$
\mathcal L_{video}=\mathbb E[\|P_v(Q_t)-Z_t\|_F^2+\|P_v(Q_{t+T})-Z_{t+T}\|_F^2].\tag{10}
$$

训练总目标可理解为 action objective 加两项加权 distillation loss；论文正文明确给出两项定义，但没有在相邻公式中统一写出权重总式。

**输出。** $Q_t$ 是当前几何/运动语义摘要，$Q_{t+T}$ 是 action horizon 后的预测表征；两者主要作为训练辅助约束，动作生成仍由 action tokens 完成。Fig.13 显示 causal inference 时可从 query 解码 current/future depth 和 DINO PCA feature。

## 4. 🎬 端到端运行实例（End-to-End Running Example）

### 场景设定

Astribot S1 接到“把桌上的饮料和两个水果放进冰箱并关门”。当前 head camera 看见机器人位于厨房岛旁，篮子在右前方；state 包含双臂 14D joint、双 gripper 2D、head 2D、body/base signal。该任务对应 Table 7 的 11 个阶段。

### 数据流转推演

**Step 1：观测编码。** 当前多视角 RGB $I_t^v\in\mathbb R^{H\times W\times3}$ patchify 为 visual tokens；全局指令和 planner/subtask 文本（例如 “pick up the drink and place it into the basket”）编码为 language tokens。机器人 state 写入 55D：有效的 arm/gripper/head/base 槽位填值，不存在的 dexterous-hand 等槽位 padding，并携带有效维 mask。

**Step 2：构造动作生成输入。** 训练时取真实未来 $T$ 步 relative action chunk $A_{t:t+T-1}\in\mathbb R^{T\times55}$，MeanStd normalize 后加噪成为 noised action tokens；推理时从模型规定的噪声/初始 action representation 开始。visual/text/state/action tokens 连同 $Q_t,Q_{t+T}$ 进入 transformer。

**Step 3：VLM 上下文化。** self/cross attention 让 action token 获得“饮料位置、篮子位置、当前夹爪姿态、文本子目标”信息。$Q_t$ 聚合当前场景；由于 causal mask，future query 不能偷看未来真实帧，只能从当前上下文和动作相关 hidden state 推断 $t+T$。

**Step 4：MoE 专家计算。** 每层 router 对每个 action token 计算 $N_r$ 个 sigmoid affinities，以 $s+b$ 选 Top-$K$，shared expert 总是处理通用的“接近/抓取”规律，routed expert 可能对 mobile whole-body、双臂或当前接触阶段响应更强。专家输出按无偏 $g$ 加权，再经残差传到下一层。

**Step 5：训练时的未来考试。** $P_d(Q_t)$ 对齐当前 depth token，$P_d(Q_{t+T})$ 对齐真实未来帧 depth token；$P_v$ 同理对齐 causal DINO-Video feature。若模型计划的动作会让夹爪运动方向与“饮料进入篮子”的未来几何不一致，future-query loss 会反向推动 hidden state 编码更合适的动作后果。

**Step 6：输出动作。** action head 输出 $T\times55$ normalized relative actions，反归一化并只读取 Astribot 有效维度。当前 chunk 的具体控制量包括双臂各关节增量、左右夹爪开合、head 与 omnidirectional base 增量；padding 槽位不下发。控制器执行一小段后重新采图并滚动预测，直至饮料、水果入篮、底盘移动到冰箱、开门、逐件放入并关门。

**Step 7：评估。** 若机器人完成前 10 步但没有关门，progress 约按 Table 7 累积到 94 分附近而 success=0；这解释了为什么论文同时报告 progress 和 success，以及为何“高 progress”不能等价成完整长程成功。

## 实验设置、数据集、基线、指标

### 预训练数据

| 数据 | 候选/保留 | 关键处理 |
| --- | ---: | --- |
| Robot trajectories | 约 90k h → 50k h | 20 embodiments；jerk/Z-score/静止过滤、URDF 回放、人工多视角 QC。 |
| Ego human videos | 约 20k h → 10k h | VLM filter、SLAM、MANO、world-frame trajectory、20% 有效帧门槛。 |
| DINO-Video clips | 5M clips | Internet + ego + robot；16 frames；causal attention + DINO/iBOT。 |

### GM-100

九个双臂任务涵盖 sorting、drawer retrieval、scooping、paper-roll replacement、packing、pushing、squeezing 等；每任务将子步骤映射到总分 100。基线包括 GR00T N1.7、$\pi_{0.5}$、LingBot-VLA 1.0。报告 progress/success，平台至少包含 Agilex Cobot Magic 与 Galaxea R1 Pro。

### 长程移动操作

Astribot S1 做 11 阶段 refrigerator sorting；Cobot Magic-ARX X5 做 7 阶段 stove cleaning。每个 task-setting 15 trials。ID 使用训练分布初始位姿/物体；OOD 将起始位姿向四方向扰动 $\pm10$ cm，冰箱任务还替换两个水果和饮料为 unseen categories。

## 主要结果、消融或对比

### 双臂主结果（Table 5）

Agilex 平台总体：GR00T N1.7 为 36.3/17.8，$\pi_{0.5}$ 59.1/32.2，LingBot-VLA 1.0 58.2/30.0，LingBot-VLA 2.0 66.2/34.4（progress/success）。最醒目的单项是 Retrieve Keychain 达 100/100；Block Sorting 却为 56.8/0，说明模型能完成若干排序步骤但完整顺序/最终放置不稳。论文也指出两个平台间差异仍明显，camera viewpoint、kinematics 和 action alignment 没被统一表示彻底消除。

### 长程移动主结果（Table 6）

| 任务 | Setting | LingBot-VLA 2.0 | $\pi_{0.5}$ |
| --- | --- | ---: | ---: |
| Refrigerator sorting | ID | 77.1 / 60.0 | 65.3 / 46.7 |
| Refrigerator sorting | OOD | 37.0 / 13.3 | 30.3 / 6.7 |
| Stove cleaning | ID | 84.3 / 66.7 | 79.9 / 60.0 |
| Stove cleaning | OOD | 67.5 / 40.0 | 62.5 / 33.3 |

冰箱 OOD 跌幅最大，因为同时改变初始位置与物体类别；灶台 OOD 主要改变位置。结果支持较强 robustness，但 15 trials 意味着 success 每一次约对应 6.7 个百分点，差异的统计稳定性应谨慎解读。

### Action-space 消融（Fig.10--12）

- **Target**：relative joint 55.0% vs absolute joint 33.7%。局部增量的低方差使回归更集中。
- **Space**：EEF 平均 56.0%，joint 55.0%，没有全局赢家。Barcode Scan joint 58.7 vs EEF 24.0；Squeeze Ketchup EEF 81.7 vs joint 41.7。前者与 pooled joint distribution 更对齐，后者的 Cartesian endpoint motion 更自然。
- **Normalization**：MinMax 47.5、Q01--Q99 47.4、MeanStd 55.0。MinMax normalized std 仅 0.15；Q01--Q99 0.32；MeanStd 0.95，并保留约 10% 的 $|x|>1.5$ 大修正动作。
- **Loss**：L2 55.0 vs L1 46.4。多数 relQpos 是零附近的连续小修正，L2 更精确；但 heavy-tail/contact-rich 的 ketchup 上 L1 更好。

## 图表、公式与表格线索

| 图/表/公式 | 精读时要回答的问题 |
| --- | --- |
| Fig.1 | action expert、MoE、55D action 与 dual query 如何连接？ |
| Fig.2 / Table 1 | 20 本体到底覆盖哪些 body DoF，数据是否均衡？ |
| Fig.3--4 / Eq.(1) | ego hand trajectory 如何从 world 转 current camera；不同动作如何 packing？ |
| Eq.(2)--(8) / Fig.7 | loss-free balance 为什么不改变 mixture weight；MoE 是否在相同 active compute 下更好？ |
| Eq.(9)--(10) / Table 3 | depth 与 DINO-Video 分别监督什么，future horizon 如何定义？ |
| Tables 5--6 | progress 与 success 是否一致；ID/OOD 每项究竟提升多少？ |
| Figs.10--12 | action target/space/normalization/loss 哪个设计对结果最敏感？ |

## 主张—证据—边界矩阵

| 主张 | 原文证据 | 解释 | 边界 |
| --- | --- | --- | --- |
| 60k h 数据支持跨本体泛化。 | Fig.2、Table 1、主实验。 | 覆盖确实广，且有明确 QC。 | 各本体小时占比、任务熵和许可证未充分公开。 |
| MoE 比 dense 更有效。 | Fig.7 active-param matched curve。 | 同 active 0.6B 下，更多稀疏总容量有效。 | 只有有限模型规模和训练区间。 |
| dual query 学到未来感知。 | Eq.(9)(10)、Fig.13。 | 能预测 future teacher features。 | “能解码未来 feature”与“动作成功提升多少”之间的独立量化仍弱。 |
| 统一 action 支持 whole-body。 | 55D + 两项移动任务。 | 头/腰/base/hand 都有槽位。 | padding 只是接口统一，不解决动力学、控制频率和观测差异。 |
| OOD 更稳健。 | Table 6。 | 四个 task-setting 全胜 $\pi_{0.5}$。 | 每设置仅 15 trials，且 OOD 类型较窄。 |

## 局限与可追问点

1. **系统变量耦合。** 2.0 同时改数据、action target、MoE、teacher 和动作覆盖；除 action-space 与 sparse scaling 外，缺少全因子消融，无法给每项准确归因。
2. **未来监督的可控性。** $I_{t+T}$ 同时由动作和环境随机性决定；query 预测 teacher feature，却没有显式输出 uncertainty，多模态未来可能被 L2/L1 压成均值。
3. **Canonical vector 的语义冲突。** 相同槽位在不同机器人上的关节拓扑、限位和控制延迟不同；模型只能靠 embodiment context/route 自行区分。
4. **自动语言标签偏差。** move/transit 占比极高，cut/fold/stir 极少；VLM segmentation 错误和长尾 action imbalance 可能决定专家路由，而论文没有给标注准确率。
5. **评测统计。** 长程 15 trials 的分辨率为 6.7%，需要更多随机种子、置信区间和跨实验室复现。

## 与当前库的连接

- 与 [[@qwen2026robotmanip]]：两者都把 cross-embodiment alignment 作为规模化 VLA 的前提；LingBot-VLA 2.0 更强调 55D whole-body interface、MoE 和 future perception teacher。
- 与 [[@zhang2026lingbot-va2]]：VLA 2.0 仍是直接 action policy，并用 future feature 做 auxiliary distillation；LingBot-VA 2.0 则原生联合建模 visual future 与 action，是更接近 world-action model 的路线。
- 与 [[@fu2026lingbot-vision]]：后者提供 boundary-centric spatial encoder，并推动 LingBot-Depth 2.0；这里的 LingBot-Depth teacher 正是将几何先验注入 VLA query 的接口。
- 与 [[@wang2026wvm]] / [[@qian2026wam-rl]]：共同问题是未来预测如何真正帮助控制；本文用 feature distillation，另两条路线更直接把 world model 用于 value/planning/RL。

## 精读路线 / 为什么需要回看

若只读 20 分钟：Fig.1 → §3.1.3 的 55D action → Eq.(2)(6)(7)(8) → Eq.(9)(10) → Tables 5--6 → Fig.10。若准备复现：必须再核对 Table 1 的各平台 DoF/频率、ego QC 门槛、action mask、MeanStd 统计范围、MoE 的 $N_r/K/\lambda/\gamma$、总 loss 权重和 action chunk $T$；其中部分超参正文未完整披露，需要结合代码与配置，不能从本文擅自补数。
