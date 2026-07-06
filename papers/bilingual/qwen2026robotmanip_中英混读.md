---
tags:
  - bilingual-reading
paper: "[[@qwen2026robotmanip]]"
source_pdf: "[[papers/pdfs/Qwen-RobotManip Technical Report Alignment Unlocks Scale for Robotic Manipulation Foundation Models.pdf]]"
images: "papers/images/qwen2026robotmanip/"
image_index: "[[papers/images/qwen2026robotmanip/index.md]]"
created: 2026-06-24
---

# Qwen-RobotManip Technical Report: Alignment Unlocks Scale for Robotic Manipulation Foundation Models

paper:: [[@qwen2026robotmanip]]
pdf:: [[papers/pdfs/Qwen-RobotManip Technical Report Alignment Unlocks Scale for Robotic Manipulation Foundation Models.pdf]]
images:: [[papers/images/qwen2026robotmanip/index.md]]

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| Qwen-RobotManip | Qwen 机器人操作模型 | 本文提出的 generalizable Vision-Language-Action foundation model。 |
| Vision-Language-Action, VLA | 视觉-语言-动作模型 | 输入多视角图像、语言指令、本体状态，输出连续 action chunk。 |
| alignment first, then scale | 先对齐，再规模化 | 本文主线：没有跨本体表示和动作空间对齐，数据规模只会造成冲突。 |
| cross-embodiment alignment | 跨本体对齐 | 让不同机器人形态的数据能进入同一训练目标。 |
| canonical state-action representation | 标准化状态-动作表示 | 80 维统一向量，按 left/right arm、joint、EEF、gripper、hand 等语义槽位组织。 |
| binary mask | 二值掩码 | 对缺失或无效维度不计算 loss，避免零填充维度产生伪监督。 |
| end-effector, EEF | 末端执行器 | 机器人执行抓取、移动、插入等动作的末端部件。 |
| camera-frame delta pose | 相机坐标系下的相对位姿增量 | 本文的 motion alignment 核心，使视觉上相似的动作在动作数值空间也相近。 |
| Camera Positional Encoding, CaPE | 相机位置编码 | 把相机外参和图像 token 几何关系注入 DiT cross-attention。 |
| flow matching | 流匹配 | action expert 的训练目标，从 noise 到真实 action 学 velocity field。 |
| Diffusion Transformer, DiT | 扩散 Transformer | 连续动作生成头，用 cross-attention 读取 Qwen-VL 隐状态。 |
| action chunk | 动作片段 | 一次预测多个未来控制步，便于低延迟执行。 |
| Real-Time Chunking, RTC | 实时动作分块 | 部署时异步生成下一段动作以隐藏网络/推理延迟。 |
| human-to-robot synthesis, H2R | 人类示范到机器人示范合成 | 把第一视角人手视频 retarget 成 15 种双臂机器人轨迹与视频。 |
| retargeting | 重定向 | 将 MANO hand keypoints 映射到 parallel-jaw gripper pose/width。 |
| data curation | 数据清洗 | 用 state/action、video/state、instruction/video 检查过滤低质量样本。 |
| embodied chain-of-thought, ECoT | 具身链式思考 | 用 VLM 合成 scene、progress、next action 三段式监督，服务 VLM/VLA co-training。 |
| in-context policy adaptation | 上下文策略适应 | 用同一 episode 近期 observation-state-action 历史作为隐式本体/行为签名。 |
| stochastic context sampling | 随机上下文采样 | 训练时随机抽取历史 chunk，避免模型只复制最近动作。 |
| VLA-to-VA degradation | VLA 退化为 VA | SFT 后模型忽视语言，只按视觉模式输出动作。 |
| RoboTwin-IF | RoboTwin 指令跟随基准 | 本文新提出，用 held-out instruction templates 测 language-conditioned control。 |
| RoboTwin-XE | RoboTwin 跨本体迁移基准 | 本文新提出，用 AgileX 训练，零样本测试 ARX、UR5、Franka。 |
| OOD evaluation | 分布外评测 | 本文认为比 IID benchmark 更能衡量 foundation model 质量。 |

## 论文主线

这篇 technical report 的核心判断很直接：机器人操作领域不能直接照搬语言模型的 scaling recipe，因为 manipulation data（操作数据）天生异构。不同机器人有不同关节、夹爪、相机、坐标系、速度、状态记录方式和动作定义；不同数据集还有不同采集质量、标注风格和任务分布。只把这些数据堆进一个模型，模型不会自动获得 generalization，反而可能学到互相冲突的 convention。

![[papers/images/qwen2026robotmanip/page1_full.png|700]]

**Figure overview: Qwen-RobotManip 的总览图。** 这页把论文主线压成四块：先扩展 manipulation data；再做 unified cross-embodiment alignment；然后在 IID、OOD、instruction following、cross-embodiment 和 real-world settings 中验证；最后用 scaling law 说明 alignment 之后数据规模才转化为能力。

作者的回答是 **alignment first, then scale（先对齐，再规模化）**。Qwen-RobotManip 做了三层对齐：representation alignment（用 80 维 canonical state/action 表示不同本体），motion alignment（用 camera-frame delta EEF 表示末端执行器动作），behavior alignment（用 structured embodiment prompt 和 in-context policy adaptation 让模型识别当前机器人和执行风格）。这些机制把多源机器人数据、人类第一视角视频和 synthetic robot data 组织进统一训练目标。

数据方面，论文构建了约 38,100 小时 pretraining corpus：约 11,420 小时 robot demonstrations，1,933 小时 egocentric human videos，以及 24,808 小时从人类视频合成的 Human-to-Robot 数据。模型方面，它用 Qwen3.5-4B/Qwen-VL 作为 perception/reasoning backbone，接一个 flow-matching DiT action expert 生成连续 action chunks。训练方面，它采用 dual-stream co-training：一边训练 VLA action prediction，一边混入 vision-language 数据，防止 VLM backbone 在动作学习中遗忘语言、视觉和空间推理能力。

评测方面，作者反复强调标准 IID benchmark 不够。LIBERO 和 RoboTwin 这类训练/测试分布接近的 benchmark 很容易被 benchmark-specific pattern matching 解决，无法说明 pretraining 真的提供了可迁移结构。因此论文把重点放到 LIBERO-Plus、RoboTwin-Clean2Rand、RoboCasa365、EBench、RoboTwin-IF、RoboTwin-XE 和真实机器人评测。结果显示 Qwen-RobotManip 在 OOD、instruction following 和 cross-embodiment transfer 上明显领先 π0.5、GR00T、StarVLA、Abot-M0 等基线。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| 跨本体对齐是 VLA scaling 的前提。 | 80 维 canonical state/action、camera-frame EEF、in-context adaptation。 | Figure 18/19 scaling curves；Table 20；RoboTwin-XE。 | 证据较强，尤其是 w/o UnifiedSpace/UnifiedEEF 的 scaling 和 transfer 退化。 |
| 只用开源 robot data 与 egocentric human videos 也能构建大规模操作语料。 | Section 2 robot data、human data、H2R synthesis、curation。 | 约 38,100 小时 corpus；Human2Robot ablation。 | 工程规模强，但复现依赖大量未完全展开的数据处理细节。 |
| H2R synthesis 把人类第一视角视频转成有动作标签的机器人数据。 | retargeting、SAM3、ProPainter、MuJoCo IK、Depth Anything compositing。 | RoboTwin-C2R Hard +4.0；LIBERO-Plus Camera +7.2。 | 有明确消融，但 synthetic distribution gap 仍是限制。 |
| VLM/VLA dual-stream co-training 保持语言和视觉泛化。 | 9:1 robot:VL pretraining；LVLM + LFM joint objective。 | 去掉 VL data 后 RT-C2R Hard 62.6 -> 54.4，RT-IF 71.6 -> 64.6。 | 对复杂 OOD 和 instruction following 的证据清楚。 |
| OOD benchmark 比 IID benchmark 更能衡量 foundation model 能力。 | Section 6.1 对比 LIBERO/RoboTwin vs LIBERO-Plus/RoboTwin-C2R。 | IID 中 scratch 可接近 pretrained；OOD 中差距明显。 | 论点有力，直接影响后续 VLA 评价标准。 |
| camera-frame EEF 支持 cross-embodiment transfer。 | Section 3.3；CaPE；EEF type conditioning。 | RoboTwin-XE 平均 23.9 vs joint 14.5；UR5 22.8 vs 4.1。 | 方向正确，但仍依赖相机标定和 morphology 相似性。 |
| 真实机器人上有实际泛化能力。 | ALOHA ID/OOD、ARX few-shot、ARX cross-embodiment、RoboChallenge。 | CobotMagic ID 88.6%、OOD 87.5%；RoboChallenge 45%/59.83。 | 结果强，但真实任务数量、试验次数和可复现程度仍有限。 |

## 摘要与核心贡献

摘要的逻辑是：语言和多模态 foundation models 之所以能泛化，是因为异构数据可以被统一到共同 formulation，并且互联网数据廉价、丰富、多样。机器人操作也想要这种 scaling，但 manipulation data 同时面临三个难题：数据昂贵、分布窄、表示异构。Qwen-RobotManip 试图证明，只要先完成 alignment，就可以让多源机器人/人类/合成数据在大规模训练中相互强化。

核心贡献可以压成四点。第一，提出 cross-embodiment alignment framework：canonical state-action representation、camera-frame delta pose、in-context policy adaptation。第二，构建约 38,100 小时操作语料，包含 open-source robot datasets、egocentric human videos 和 Human-to-Robot synthetic data。第三，提出/采用更强调 OOD 的评测，包括 LIBERO-Plus、RoboTwin-Clean2Rand、RoboCasa365、EBench，以及新 benchmark RoboTwin-IF 和 RoboTwin-XE。第四，在 simulation 和 real-world settings 中展示优于已有 VLA baselines 的泛化能力。

需要注意的是，这篇不是单点算法论文，而是系统技术报告。它的价值不在某一个公式，而在把数据工程、动作表示、模型架构、训练 recipe 和评测标准串成了一个完整 VLA scaling pipeline。

## 1. Introduction / 为什么 VLA 需要先对齐再扩展

Introduction 从 foundation model 的 scaling recipe 出发：LLM/VLM 能扩展，是因为文本和图像-文本数据可以被统一成 token prediction 或类似目标。机器人操作不是这样。一个 Franka 的 joint action、一个 ALOHA 的双臂 EEF action、一个 humanoid 的移动操作状态、一个人类第一视角视频，它们都不是天然同一种数据。

作者把现有 VLA 泛化不足归因于两个层面。第一，demonstration corpora 过窄，很多数据集中在少数 teleoperation setup 上，embodiment 和 task diversity 不够。第二，单纯增加 diversity 不够，因为不同数据源的 observation/action representation 互不兼容。没有 alignment 时，模型用额外数据学到的是冲突，不是 transferable skill。

因此 Qwen-RobotManip 的原则是 **alignment first, then scale**。三层对齐分别回答：

- representation alignment：不同机器人状态和动作放到哪里？
- motion alignment：不同坐标系下的同一 EEF motion 如何变成相近数值？
- behavior alignment：部署时模型如何知道当前机器人/episode 的行为风格？

Introduction 还提出评价标准转向：IID benchmark 容易奖励 memorization，真正的 foundation model 质量应该看 OOD transfer、instruction following、cross-embodiment 和 real-world deployment。

## 2. Data Sources / 数据从哪里来

### 2.1 Robot datasets / 真实与仿真机器人数据

机器人数据是 pretraining corpus 的核心。论文合并九个开源数据源，总量超过 11,000 小时，覆盖 single-arm、dual-arm、mobile manipulation、humanoid 和 simulation。主要数据包括 OXE、AgiBotWorld-Beta、RoboMIND/RoboMIND 2.0、Galaxea Open-World、RoboCOIN、DROID、RH20T、RDT-1B 和 InternData-A1。

Table 1 给出的总账是：

| 数据类型 | 本体类型 | 时间 |
| --- | --- | ---: |
| Robot single-arm | OXE、RoboMIND、DROID、RH20T 等 | 3,808 h |
| Robot dual-arm | AgibotWorld、RoboCOIN、RDT 等 | 6,744 h |
| Robot mobile & humanoid | InternData-A1、Galaxea 等 | 868 h |
| Human hands | EgoDex、VITRA、EgoVerse | 1,933 h |
| Human-to-Robot | 15 dual-arm platforms | 24,808 h |

这个表很重要：Qwen-RobotManip 的大部分“新增规模”不是直接来自真实 robot teleoperation，而是来自人类视频合成后的 H2R 数据。

### 2.2 Egocentric human data / 第一视角人类操作视频

人类第一视角视频的价值在于：它和 robot-mounted camera 有视角相似性，而且现实世界对象、场景、动作远比小规模机器人数据多。论文使用三类数据：

- EgoDex：Apple Vision Pro 采集，194 个 tabletop tasks，829 小时 30 Hz egocentric video，使用其中 732 小时。
- VITRA：从 Ego4D、EPIC-KITCHENS 等无结构视频中恢复 hand reconstruction、camera trajectory 和 action segmentation，使用约 247 小时。
- EgoVerse：1,362 小时、1,965 tasks、240 scenes、2,087 demonstrators，使用 industry-contributed 部分约 954 小时。

所有 hand poses 都转成统一 MANO parameters 和 21 keypoints。这为下一步 retargeting 提供基础。

### 2.3 Human-to-Robot synthesis / 人类视频转机器人示范

![[papers/images/qwen2026robotmanip/page5_full.png|700]]

**Figure 1: Human-to-Robot synthesis pipeline.** 这张图是数据章节的核心：输入是 egocentric human video，输出是多 robot morphology 下的 synthetic robot demonstrations。

H2R pipeline 分成 action alignment 和 visual alignment。Action alignment 先把人手关键点映射成 gripper pose 和 gripper width。作者定义 virtual finger：

$$
k_{vf}=0.7k_{index}+0.3k_{middle}
$$

然后用 thumb tip 和 virtual finger 的中点作为 EEF position，用二者距离作为 gripper width：

$$
p=\frac{1}{2}(k_{thumb}+k_{vf}), \quad w=\|k_{thumb}-k_{vf}\|_2.
$$

gripper orientation 由 grasp axis、wrist-to-fingertip direction 和右手系构造。为了减少 per-frame hand detection noise，位置和宽度用 Savitzky-Golay filtering，旋转用 Gaussian-weighted SLERP。

Visual alignment 则把视频里的人手“换成机器人”。先用 SAM3 分割 human arm mask，再用 ProPainter inpaint 出没有手臂的背景。由于人类视频没有 robot base，作者要搜索一个可行 base pose，使目标 EEF trajectory 尽可能被 robot IK 追踪。然后用 MuJoCo 渲染机器人图像与深度，用 Depth Anything v3 估计场景深度，最后做 depth-guided compositing。

每条人类示范被渲染成 15 种双臂机器人配置，包括 Panda、UR5e、ARX-L5、xArm7、Sawyer、Kinova Gen3、IIWA、Jaco、FR3、UR10e、ViperX、WidowX、Piper、YAM、AgileX ALOHA。这样 1,933 小时人类视频扩成约 24,808 小时 synthetic demonstrations。

### 2.4 Data curation / 数据清洗为什么关键

![[papers/images/qwen2026robotmanip/page6_full.png|700]]

**Figure 2: Multi-stage data curation pipeline.** 这张图说明多源机器人数据的噪声不是“小问题”：state/action 可能突变、时序错位、FK 不一致，视频和状态也可能对不上。

五阶段 state-action filtering 包括：

1. **Sudden Change Detection**：检测 residual、acceleration、jerk，过滤碰撞或记录异常。
2. **State-Action Trend Alignment**：动作应领先或同步状态变化；用 cross-correlation 和 directional agreement 检查 state/action 时序是否错位。论文提到 RoboMIND UR-type data 中 81% episodes 因该检查失败而被排除。
3. **Extreme Value Filtering**：按 embodiment type 的 q1/q99 区间过滤极端值，避免训练归一化被 outlier 拉坏。
4. **Joint-End-Effector FK Consistency**：用 Pinocchio 和 URDF 检查 joint state 与 logged EEF pose 是否一致，并修正 TCP offset、frame definition 等问题。
5. **Base Frame and EEF Orientation Alignment**：统一 world-frame orientation convention。

三类 cross-modal checks 包括 instruction consistency、video-state consistency 和 video quality filtering。直观讲，这一步保证“语言、视频、状态、动作”都在描述同一件事。

### 2.5 Vision-Language co-training data / 为什么还要混 VLM 数据

VLA 训练可能损伤原始 VLM 的 perception、language grounding 和 spatial reasoning，所以作者加入约 28M vision-language mixture，分为 general visual understanding、spatial perception/reasoning、OCR、multimodal knowledge、instruction/multilingual/text 和 embodied-centric VL data。

最有机器人味的是 embodied-centric VL data，包括：

- ECoT：当前 multi-view observation + task instruction -> scene description、task progress assessment、next atomic action。
- Egocentric video understanding：从 1.5-3 秒人类第一视角 clips 描述手/物体交互和状态变化。
- 2D trajectory prediction：把 EEF 或 hand trajectory 投影到图像上，让模型学习视觉中的运动规划线索。

这里的逻辑是：VLM backbone 不只要“看懂图”，还要形成可被 action expert 使用的 embodied representations。

## 3. Model Design / Qwen-RobotManip 怎样建模

![[papers/images/qwen2026robotmanip/page11_full.png|700]]

**Figure 3: Qwen-RobotManip architecture.** 左侧是 Qwen-VL backbone，右侧是 DiT action expert；底部显示统一 state/action 表示和 camera-frame EEF action。

### 3.1 Main architecture

模型采用 decoupled architecture：Qwen3.5-4B/Qwen-VL 做 vision-language backbone，负责多视角图像和指令的共同编码；flow-matching DiT action expert 做 continuous action generation。这样设计的好处是：VLM 保持 perception/reasoning，action expert 专注高频细粒度控制。

Action expert 是 10 层 transformer blocks，hidden dimension 768，12 heads。每层先对 state/action tokens 做 self-attention，再 cross-attend 到 VLM hidden states。偶数层 attend visual tokens，奇数层 attend language tokens，试图把空间 grounding 和语言 instruction 分阶段注入动作生成。

训练目标是 flow matching。给定真实 action chunk $a$，采样 timestep $t$ 和 Gaussian noise $\epsilon$，构造：

$$
x_t=(1-t)\epsilon+ta
$$

模型学习 velocity field $a-\epsilon$。推理时用 4 次 Euler integration 生成 action sequences，以满足低延迟控制。

### 3.2 Canonical state-action representation

跨本体训练的第一难题是：不同机器人 state/action 维度和语义不一样。Qwen-RobotManip 把所有 state/action 放入 80 维 canonical vector。结构是两个 29 维 per-arm blocks，加 22 个 reserved dims。每只手臂包含：

- joint positions: 7 dims
- EEF pose: 9 dims，3D position + 6D rotation representation
- gripper state: 1 dim
- dexterous hand joints: 12 dims

双臂机器人填两侧，单臂机器人只填一侧，灵巧手填 hand joints，缺失维度填零但用 binary mask 排除 loss。这个设计的重点不是“80 维刚好够”，而是每个维度有固定语义，模型可以跨 embodiment 共享同类信号。

### 3.3 Camera-frame EEF motion

canonical vector 解决的是槽位对齐，但还没解决坐标系对齐。同一个“向前移动夹爪”的动作，在不同 robot base frame、world frame 或 wrist frame 中数值可能完全不同。作者采用 camera-frame delta pose：把 EEF motion 投到 reference camera coordinate frame 中。

核心性质是：视觉上相似的动作，在 action space 中也相似。这对 imitation learning 很关键，因为策略从图像里看见的是 camera view，而不是 robot base frame。

论文给出 pose action 的表达：

$$
a_p=
\begin{bmatrix}
{}^c_eR\,{}^e_{e^\*}R\,{}^e_cR & {}^c_eR\,{}^e t_{e^\*}\\
0 & 1
\end{bmatrix}
$$

直观解释：旋转部分把 EEF relative rotation 通过 camera-to-end-effector extrinsics 共轭到 camera frame；平移部分把 desired EEF displacement 投影到 camera coordinates。作者也讨论了更紧凑的 $a_p = {}^cT_{e^\*}{}^eT_c$，但认为它更容易受 calibration error 和 long-tail distributions 影响。

为了让 DiT 理解相机几何，论文使用 Camera Positional Encoding（CaPE）：image tokens 用各自 camera extrinsics，state/action tokens 用 selected reference camera extrinsics。Camera intrinsics 也通过 normalized image-plane coordinates 注入 token。

### 3.4 Embodiment prompt

structured embodiment prompt 包含：

```text
embodiment: robot_aloha
instruction: Take the toy off the table and put it on the mat.
speed: 1000
fps: 30
camera view direction: arm side
```

这不是给用户看的自然语言说明，而是给策略的 execution context：哪个机器人、做什么任务、时间尺度、采样率、相机方向。训练时 embodiment、speed、fps 有 15% 概率被 drop，以增强缺失 metadata 时的鲁棒性。

### 3.5 In-context policy adaptation

in-context policy adaptation 的直觉是：同一个模型部署到新机器人或新场景时，不一定要更新参数，但可以通过近期执行历史了解当前 robot 的行为风格。一个 context chunk 是 $(o_h,s_h,a_h)$：机器人看到什么、处于什么状态、刚执行了哪段 action chunk。

历史视觉帧被送入 VLM visual encoder；历史 state/action 通过 MLP 投影到 VLM hidden space，并按时间顺序串成 context token sequence。作者比较 unified mode 和 dual mode，最终采用 unified mode：context tokens 直接进入 VLM 输入序列，让 VLM 在 self-attention 中联合推理视觉、语言和历史。

一个关键训练技巧是 stochastic context sampling。不能总给最近的 H chunks，否则模型可能偷懒复制最近动作。训练时从 episode 随机位置抽 context，使模型学习“这个 episode 的行为 profile”，例如速度、抓取方式、运动签名，而不是复制。

## 4. Training / 训练 recipe

### 4.1 Pre-training

Pretraining 使用两条 stream。VLA stream 来自真实 robot、human videos 和 H2R synthetic trajectories；VLM stream 来自 Section 2.5 的 vision-language 数据。实际比例约 robot:VL = 9:1。

VLA loss 是 masked flow matching：

$$
L_{FM}=\frac{1}{B}\sum_i
\frac{\sum_{t,j}m_{i,t,j}(f_\theta(x_{i,t},t_i,s_i,o_i)_j-v_{i,t,j})^2}
{\sum_{t,j}m_{i,t,j}}
$$

这里 $m$ 由 three masks 组合：slot mask、step validity mask、human hand validity mask。这个归一化保证不同 embodiment 的 active dimensions 不同，但每个 sample 对梯度贡献相等。

VLM loss 是 next-token prediction：

$$
L_{VLM}=-\mathbb{E}\sum_i\log p_\phi(y_i|y_{<i},c)
$$

总目标：

$$
L=L_{FM}+\lambda L_{VLM},\quad \lambda=0.1
$$

### 4.2 Post-training

SFT 阶段采用 generalist SFT paradigm：对每个 benchmark 或 deployment scenario，把所有 available demonstrations 合成一个训练集，训练一个统一模型，而不是每个任务一个 specialist。

作者指出 SFT 的风险是 VLA-to-VA degradation：模型在 domain-specific SFT 中学会视觉模式匹配，语言指令变成弱信号，尤其在训练/测试场景高度相似的 benchmark 上。这也是他们提出 RoboTwin-IF 的原因：如果同一场景里有多个可行动作，模型必须真正读懂 instruction 才能选对。

## 5. Deployment / 部署

部署时，推理在 remote server 上运行，机器人通过 WiFi 传 observation/action。为了隐藏网络和推理延迟，作者使用 Real-Time Chunking（RTC）：机器人执行当前 action chunk 时，server 异步生成下一段 chunk。这个设计让 flow policy 的分块输出可以用于实时控制。

## 6. Experiments / 实验为什么强调 OOD

### 6.1 Standard benchmarks are not enough

![[papers/images/qwen2026robotmanip/page16_full.png|700]]

**Figure 4: IID 与 OOD benchmark 对比。** 左边显示标准 LIBERO/RoboTwin 上 scratch models 可以很强；右边显示 LIBERO-Plus/RoboTwin-Clean2Rand 上 pretrained models 的优势才明显。

作者认为 LIBERO 和 RoboTwin 这类 standard in-domain benchmarks 结构性地低估 pretraining。原因是 training/evaluation 来自同一环境和任务分布，模型可以通过 visual/behavioral pattern matching 拿高分，不需要真正泛化。Figure 4 中 StarVLA 和 Qwen-RobotManip-scratch 在 IID benchmarks 上能达到很高水平，但到 OOD settings 时显著掉队。

这个论点对读 VLA 很重要：以后看到一个 VLA 在 LIBERO/RoboTwin 上很高，不能直接推断它有 foundation model 能力。更应该看 OOD perturbation、language grounding、cross-embodiment transfer 和 real-world adaptation。

### 6.2 OOD generalization capabilities

![[papers/images/qwen2026robotmanip/page19_full.png|700]]

**Figure 7 / Table 8 所在页：OOD generalization summary 和 RoboTwin-IF。** 这页把 task/scene、instruction following、cross-embodiment 三个轴的结果放在一起。

论文的 OOD 评测分三类：

1. **Task and scene generalization**：LIBERO-Plus、RoboTwin-Clean2Rand、RoboCasa365、EBench。
2. **Instruction following**：新提出 RoboTwin-IF。
3. **Cross-embodiment generalization**：新提出 RoboTwin-XE。

关键数字如下：

| Benchmark | Qwen-RobotManip 结果 | 对比基线 |
| --- | ---: | --- |
| LIBERO IID | 99.1 / Context 99.2 | 竞争或 SOTA |
| RoboTwin Easy/Hard IID | 93.4/92.5，Context 93.7/94.0 | 高于 π0.5、StarVLA、Abot-M0 |
| LIBERO-Plus | 89.0，Context 91.4 | π0.5 84.4 |
| RoboTwin-C2R Hard | 62.6，Context joint 69.4 | π0.5 47.9 |
| RoboCasa365 total | 35.9 | RLDX-1 33.2，π0.5 16.9 |
| EBench overall | 45.6 SR / 60 score | π0.5 27.1 / 41 |
| RoboTwin-IF average | 72.2 | π0.5 49.6 |
| RoboTwin-XE EEF average | 23.9 | π0.5 EEF 7.5 |

LIBERO-Plus 的 per-dimension 结果显示，大规模 robot pretraining 最有价值的部分不是 language/light/background 这种 VLM 本来就擅长的 perturbation，而是 robot initial state、camera viewpoint、layout、noise 等更接近控制和空间泛化的扰动。RoboTwin-C2R 的 clutter 结果也很典型：scratch 从 71.6 Easy 掉到 24.6 clutter，说明只靠 benchmark SFT 很难学会在干扰物中关注任务相关对象。

RoboTwin-IF 是本文最有意义的新基准之一。它把多个可交互对象放在同一场景中，要求模型按 held-out instruction template 选择正确行为。比如 Operate-Tabletop 同时有 bell、stapler、pickable object，指令可能要求 ring、press 或 pick。Qwen-RobotManip 平均 72.2%，π0.5 为 49.6%，说明语言条件控制没有在 VLA training 中完全退化。

RoboTwin-XE 则验证 camera-frame EEF。模型只在 AgileX demonstrations 上 fine-tune，测试时替换成 ARX-X5、UR5-WSG、Franka Panda。joint control 对 UR5/Franka 基本失败，因为 joint actions 是 robot-specific；camera-frame EEF 让 ARX 达 42.9、UR5 达 22.8、Franka 达 5.9，平均 23.9。

### 6.3 Real-world evaluation

![[papers/images/qwen2026robotmanip/page24_full.png|700]]

**Figure 11 / Table 10 / Table 11: CobotMagic ALOHA real-world ID/OOD。** 这页展示真实双臂平台上的 in-domain 和 out-of-domain tasks。

CobotMagic ALOHA 上，作者用 22.9 小时 teleop demonstrations fine-tune。ID benchmark 有 7 个任务：table cleanup、three-bowl stacking、melon-in-bowl、towel folding、block-in-drawer、yellow-disc insertion、three-block stacking。Qwen-RobotManip 平均 88.6%，π0.5 42.9%，StarVLA 20.0。它在 5 个任务上 5/5，yellow-disc-insertion 只有 2/5，是主要短板。

OOD benchmark 有 4 个任务：target-object-in-basket、left-right-bowl-stacking、tool-on-towel、banana-on-towel，强调 clutter、unseen objects、left-right spatial reference、dynamic lighting。Qwen-RobotManip 平均 87.5%，π0.5 37.5%，StarVLA 0.0。π0.5 在简单 OOD 还能保持部分能力，但在 left-right bowl stacking 和 small tool grounding 上崩掉。

![[papers/images/qwen2026robotmanip/page26_full.png|700]]

**Figure 12 / Table 12 / Table 13: ARX ALOHA few-shot 和 cross-embodiment skill transfer。** 这页展示 ARX 平台任务和跨本体 skill transfer 设置。

ARX few-shot 使用 130 条 teleop demonstrations，覆盖 Put Fruits、Put Blocks、Fold Towel、Insert Screw、Unscrew Cap。Qwen-RobotManip 在 Put Blocks、Fold Towel、Unscrew Cap 上相比 π0.5 更好；Insert Screw 对所有模型都难，完整插入为 0/10。

更关键的是 cross-embodiment skill transfer：policy 用 6K CobotMagic + 130 ARX demonstrations joint fine-tune，但 ARX 对四个 novel tasks 没有 task-specific demonstrations。Full Qwen-RobotManip 达 55.0%，w/o UnifiedEEF 12.5%，w/o UnifiedSpace 7.5%。这说明跨本体迁移不是靠简单 zero padding，而是依赖语义槽位和 EEF action alignment。

### 6.3.2 RoboChallenge Table30-v1

RoboChallenge Table30-v1 generalist track 有 30 个任务、4 种 robot embodiments。generalist track 要求每个 embodiment 一个统一 policy 处理多任务，比每任务一个 specialist 更接近真实需求。

Qwen-RobotManip 以匿名身份 Lira_generalist 提交，成功率 45%、process score 59.83，超过 DM0_generalist 的 37% / 48.43。作者重点分析了三种能力：

- **Strong bimanual coordination**：8 个 ALOHA 双臂任务平均 40%，高于 π0.5 21.2 和 DM0 16.2。
- **Robust pick-and-place across embodiments**：12 个 pick-and-place 任务平均 63.3%，高于 DM0 48.3。
- **Emergent retry behavior**：失败后自发重试，例如 sort electronic products 中物体掉落两次后第三次成功。

这些案例说明模型不仅会按轨迹模仿，还学到了一些 recovery strategy。作者推测这来自 diverse pretraining demonstrations 中自然包含失败和修正。

## 6.4 Ablation / 哪些设计真正有用

![[papers/images/qwen2026robotmanip/page31_full.png|700]]

**Figure 18 / Figure 19: action representation 与 scaling。** 这是全篇最重要的消融之一：只有 representation 对齐后，更多数据才稳定降低 OOD prediction error 并提升 downstream OOD success。

作者比较三种 action space：

- w/o UnifiedSpace：原始 action fields 拼接 + zero padding，没有语义对齐。
- w/o UnifiedEEF：有 80 维语义槽位，但 EEF action 不是 camera-frame delta。
- Ours：语义槽位 + camera-frame delta EEF。

Figure 18 显示 unified representations 有更清晰的 data scaling law，validation MSE 随数据比例增加近似 log-linear 下降。w/o UnifiedSpace 在 EEF prediction 上不稳定且误差高。Figure 19 进一步显示，在 RoboTwin-C2R Hard 的 downstream success 中，Ours 随 pretraining data 从 1% 到 100% 增长更稳定，尤其 EEF mode 下明显优于 ablations。

![[papers/images/qwen2026robotmanip/page32_full.png|700]]

**Table 15: prompt 与 in-context adaptation 消融。** structured prompt 比 soft prompt/natural language prompt 更好，但真正大的提升来自 context + 足够 denoising steps。

Table 15 中，structure prompt 平均 65.9，高于 w/o UnifiedEEF baseline 的 62.7。加入 context 但只用 4 denoising steps 会抖动，平均 63.3；把 denoising steps 提到 10 后平均 70.9，20 steps 只有 71.0，没有额外收益。作者解释：context 增加了 action distribution 的复杂性，需要更多 denoising capacity 才能解码好。

Human-to-Robot ablation 显示 +H2R 比 robot-only 好：RoboTwin-C2R Hard 从 54.7 到 58.7；LIBERO-Plus total 从 87.1 到 89.0，Camera 维度从 72.8 到 80.0。这个结果支持“人类视频先提供视觉多样性，H2R 进一步通过动作/视觉对齐提供 robot-usable supervision”。

VL co-training ablation 也很关键。去掉 pretraining VL data：

| 设置 | LIBERO | LIBERO-Plus | RT-C2R Easy | RT-C2R Hard | RT-IF |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full | 99.1 | 90.1 | 73.2 | 62.6 | 71.6 |
| w/o VL pretraining | 98.2 | 88.9 | 66.5 | 54.4 | 64.6 |
| with VL post-training | 98.6 | 91.4 | 74.0 | 62.5 | 73.1 |

结论是：VL data 对简单 IID benchmark 影响不大，但对复杂 OOD、instruction following 很重要，因为它保护了 VLM 的 language grounding 和 spatial reasoning。

## 6.5 New features after alignment / 对齐之后出现的新能力

![[papers/images/qwen2026robotmanip/page36_full.png|700]]

**Table 20: camera-frame delta EEF 的三层收益。** 这张表总结了从 in-distribution EEF control 到 cross-embodiment skill composition，再到 zero-shot transfer 的递进证据。

Camera-frame EEF 的收益体现在三层：

1. **EEF control quality**：RoboTwin-C2R Easy/Hard EEF mode 中，Ours 72.5/56.6，best baseline w/o UnifiedEEF 49.0/33.0，提升约 23 点。
2. **Skill composition**：CobotMagic -> ARX 四个 novel tasks 中，Ours 55.0%，w/o UnifiedEEF 12.5%，约 4.4x。
3. **Zero-shot transfer**：AgileX -> ARX/UR5/Franka 平均，EEF 23.9%，joint 14.5%，约 1.65x。

这一节的核心是：camera-frame EEF 不只是一个控制接口，而是把 manipulation primitives 从 robot-specific joint kinematics 中解耦出来，让同一技能可以跨 embodiment 组合和迁移。

## 7. Conclusion / 结论与局限

结论回到开头：机器人操作可以应用 foundation model scaling recipe，但前提是 alignment 和 scale 同时成立。没有 unified cross-embodiment formulation，数据规模带来冲突；没有足够数据多样性，对齐后的模型也不能泛化。

作者总结了三个更广泛的启示：

第一，canonical representation、camera-frame delta pose 和 in-context adaptation 不只是兼容异构本体的工程技巧，而是让 scaling law 出现的条件。第二，只用开源 robot data 和 egocentric human videos，通过 synthesis 和 curation，也能构建大规模 manipulation corpus，这降低了 manipulation foundation model 的数据门槛。第三，领域评价应从 IID benchmark rank 转向 OOD generalization。

论文也明确承认局限。H2R synthesis 会带来 retargeting approximation 和 inpainting artifacts。OOD evaluations 虽然比标准 benchmark 难，但仍主要是 simulation-based。真实世界评测需要更多平台和部署条件。固定 action chunk length 和当前 inference latency 也限制了需要 sub-second reactive control 的任务。

## 贡献与结论对照

| 结论 | 支撑证据 | 我的判断 |
| --- | --- | --- |
| Alignment unlocks scale。 | Figure 18/19 中 unified representation 才有稳定 scaling；w/o UnifiedSpace 不稳定。 | 本文最可信的主线。 |
| H2R synthetic data 有价值。 | Robot-only -> +Ego -> +H2R 在 RoboTwin-C2R 和 LIBERO-Plus 上递进。 | 有用，但未来要看和真实数据规模增长的边际关系。 |
| VL co-training 防止语言/视觉退化。 | 去掉 VL 后 RT-C2R Hard、RT-IF 明显下降。 | 对 VLA-to-VA degradation 很有启发。 |
| OOD benchmark 比 IID benchmark 更合理。 | IID 中 scratch model 表现强，OOD 中差距拉开。 | 对读 VLA 论文非常重要。 |
| camera-frame EEF 支持跨本体。 | RoboTwin-XE、ARX skill transfer、Table 20。 | 方向很强，但依赖标定和相机设置。 |
| real-world 泛化能力较强。 | CobotMagic ID/OOD、ARX few-shot、RoboChallenge。 | 结果漂亮，但仍需更多公开复现。 |

## 图表索引与讲解

- [[papers/images/qwen2026robotmanip/index.md]] 包含脚本抽取的 195 张 PDF 内嵌图和本文额外渲染的整页精选图。
- `page1_full.png`：论文整体总览，适合第一次读时建立结构。
- `page5_full.png`：Human-to-Robot synthesis pipeline，理解数据扩展的关键图。
- `page6_full.png`：data curation pipeline，理解为什么多源机器人数据难清洗。
- `page11_full.png`：模型架构、统一 state/action、camera-frame EEF 的总图。
- `page16_full.png`：IID vs OOD benchmark 的核心论证。
- `page19_full.png`：OOD summary、RoboTwin-IF 和 cross-embodiment 结果。
- `page24_full.png`：CobotMagic ALOHA ID/OOD 真实机器人评测。
- `page26_full.png`：ARX few-shot 和 cross-embodiment skill transfer。
- `page31_full.png`：action representation scaling law。
- `page32_full.png`：prompt/context adaptation 消融。
- `page36_full.png`：camera-frame EEF 三层收益总结。

## 参考文献与延伸阅读

- [[@tencent2026hy-embodied-05]]：更偏 embodied VLM backbone 和 VLA 前置认知模型。
- [[@lin2026physbrain]]：human egocentric video 作为 VLA physical intelligence bridge。
- [[@xu2026egoguide]]：robot-free demonstrations 和 egocentric guidance 数据采集。
- [[@tang2026frs]]：利用 flow policy 的反向 steering 做策略改进。
- [[@kim2026serf]]：长时程 mobile manipulation 中的 explicit spatial memory。
- [[@zhang2026contactworld]]：vision-tactile world model 与 contact-rich manipulation。
