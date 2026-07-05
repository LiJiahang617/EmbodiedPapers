---
tags:
  - bilingual-reading
  - deep-reading
paper: "[[@zhang2026qwen-robotworld]]"
source_pdf: "[[papers/pdfs/zhang2026qwen-robotworld.pdf]]"
images: "papers/images/zhang2026qwen-robotworld/"
image_index: "[[papers/images/zhang2026qwen-robotworld/index.md]]"
created: 2026-07-05
reading_mode: 生成式精读（逐节读原文 + 读图）
---

# Qwen-RobotWorld Technical Report: Unifying Embodied World Modeling through Language-Conditioned Video Generation

paper:: [[@zhang2026qwen-robotworld]]
pdf:: [[papers/pdfs/zhang2026qwen-robotworld.pdf]]
images:: [[papers/images/zhang2026qwen-robotworld/index.md]]

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| language-conditioned video world model | 语言条件视频世界模型 | 全文范式：把 world model 形式化成状态转移 $s_{t+1}=f(s_t,a_t)$，其中 state 是视觉观测（帧或 latent），action 用**自然语言**表示，模型据此生成未来视觉轨迹。 |
| action-language mapping | 动作-语言映射 | 本文数据侧核心贡献：把 20+ 种 robot embodiment、500+ 动作类别的异构动作（关节角/waypoint/转向指令/heading）统一投影到自然语言空间，使 Franka 夹爪、自动驾驶车、导航 agent 都变成同一个「语言条件视频生成」任务。 |
| Double-Stream MMDiT | 双流多模态扩散 Transformer | 骨干架构：**understanding stream** 处理冻结 Qwen2.5-VL 抽的语义（=action），**generation stream** 处理 video-VAE latent（=state），两流在**每一层 joint attention** 双向融合。60 层。 |
| MLLM Action Encoding | 用 MLLM 做动作编码 | 用冻结的 Qwen2.5-VL（而非 T5/CLIP）当 action encoder：深层语言理解可解析组合指令，且其内化的 world knowledge（如「机械臂是刚体、连杆定长」）隐式约束物理合理的转移空间。 |
| Embodied World Knowledge (EWK) | 具身世界知识数据集 | 本文构建的 8.6M video-text 语料（200M+ 帧），70% 具身 + 30% 通用，横跨 manipulation / driving / navigation / human-to-robot 四域。 |
| General+Expert Progressive Curriculum | 通用+专家 渐进式课程 | 两阶段训练：pretraining 学通用视觉先验（T2I/T2V/TI2V 联合），SFT 用四阶段混合调度注入具身专精，且**每个 batch 都保留通用数据**避免遗忘。 |
| Scene2Robot | 场景到机器人（多段条件） | 把 first-frame conditioning 扩成三段序列（scene condition / robot reference / generation），在同一 VAE-MMDiT 里做 human-to-robot 的跨具身视频编辑，无需改架构。 |
| Asymmetric 3D RoPE | 非对称 3D 旋转位置编码 | 时间/高/宽三轴独立编码，但维度分配非均匀：时间 16 维、高/宽各 56 维（`pe_axes_dim=[16,56,56]`）。相邻帧强相关故时间少分维；空间物体位置多样故多分维。配合 multi-view concatenation 实现跨视角几何一致。 |
| multi-view concatenation | 多视角拼接 | 把 2–4 路同步相机的首帧在**空间上横向拼成一张输入**，让模型一次生成所有视角的后续帧，强迫 attention 层建立跨视角空间对应。~1.6M/6M 具身样本含此监督。 |
| human-to-robot transfer / MANO-to-robot | 人到机器人迁移 | 用 MANO 重建手部 3D 关键点 → retarget 到机器人末端轨迹 → inpainting 去人手 → MuJoCo IK 渲染 14 种机械臂，产出配对的「人演示 ↔ 机器人执行」视频，作为视频编辑监督。 |
| Hierarchical Five-Layer Annotation | 分层五层标注 | 标注框架：前三层（task goal / action detail / physical feedback）是结构化 CoT，后两层生成 comprehensive（50–100 词）与 concise（15–30 词）两种粒度 caption，训练时各 50% 采样。 |
| flow matching | 流匹配训练目标 | 训练目标：video 经 VAE 编码进 latent，噪声取标准正态，timestep 取 log-normal 且随序列长自适应 shift；TI2V 任务首帧 timestep 固定为 0。 |
| EWMBench / DreamGen Bench / PBench / WorldModelBench | 四个评测基准 | 分别测「具身运动保真」「机器人视频生成质量」「物理行为理解+画质」「物理合规+指令跟随」。 |
| RoboTwin-IF | RoboTwin 指令跟随基准 | 基于 RoboTwin 仿真新建的复杂任务基准，本文做**零样本**评测（训练只混了少量开源 RoboTwin 数据），四难度层：基础操作→相对定位→双臂协作→长程复杂指令。 |

## 论文主线

**核心问题**：world model 想当「可扩展的具身训练/评估平台」，就得学好状态转移 $s_{t+1}=f(s_t,a_t)$。但当前有一条根本张力——**通用视频生成模型**（Sora、Veo）从互联网规模数据学到丰富视觉先验，却**不会建模具身物理**（接触动力学、刚体结构约束、动作-后果关系）；**领域专用具身模型**（Cosmos 等）物理对了，却依赖 robot-specific 的结构化动作表示（关节角/waypoint），**无法跨 embodiment、跨任务泛化**，因此当不成通用仿真环境。

**动机/核心观点**：作者主张用**自然语言当统一动作接口**来弥合这道裂缝。一句 "pick up the red cup and place it on the shelf" 隐式编码了完整动作序列、目标状态与物理约束，却不需要任何 robot-specific 控制接口。更关键的是作者的**互补物理知识**论证：manipulation 教精细接触物理与物体状态变换；autonomous driving 教大尺度多智能体动力学与 3D 几何（靠 ego-motion 视差）；indoor navigation 教房间尺度空间推理与「语言指令→空间连贯轨迹」的接地。因为共享语言接口，**这四域可以联合训练、彼此强化而非冲突**——这是没有单域模型能达到的互补泛化。

作者把答案落成三件套：**架构**（Double-Stream MMDiT + 冻结 Qwen2.5-VL 做动作编码）、**数据**（action-language mapping 造出 EWK 8.6M）、**训练**（general+expert 渐进课程）。并强调这个统一骨干经任务特定适配可服务三类具身应用：**合成数据引擎、策略评估环境、动作规划器**。

阅读时要盯住一句话：**本文的赌注是「语言是最通用、最可及的动作表示」**（引 Ye et al. 2026「World action models are zero-shot policies」）。它把跨域异构问题从「统一 latent / 统一控制接口」重构成「统一 caption 格式」——好处是零架构改动就能混训四域，代价是所有跨域一致性都压在标注质量与 MLLM 的语言理解上。

> 本报告没有 architecture/overview 图的可嵌资源（图库仅含两张零样本结果图 Fig.7/Fig.8），故主线这里不嵌图；两张真实图放在 §5 结果处就近讲解，避免堆在顶部。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| **Framework**：语言作为通用动作接口，联合训练 manipulation/driving/navigation/H2R 四域，取得单域模型无法企及的互补物理泛化。 | §3 Double-Stream MMDiT + §4 联合训练 | Table 2–5 四基准 + Fig.5–10 定性 | 概念清晰、跨域覆盖广；但「统一」是靠一套 caption 格式，不是一个闭环控制策略，下游 policy 成功率增益本报告未直接测。 |
| **Data**：action-language mapping 标准化 20+ embodiment、500+ 动作类别 → EWK ≈8.6M 高质量跨场景视频-文本对。 | §2.1 + Table 1 | §2.3.4 语料统计（70% 具身 / 30% 通用，200M+ 帧） | 数据规模是最硬的贡献；但质量/泄漏依赖 LLM-judge + 部分人工复核，纯语言接口把一致性风险都压在 caption 上。 |
| **Training**：general+expert 联合训练范式，既有广世界建模又有深具身专精，稳定可扩展地混训多场景。 | §4.1 四阶段 SFT 调度 | WorldModelBench 物理合规满分、T2I anchoring 防形变 | 合理且工程细节详实；但**没有独立消融**去隔离课程 / T2I anchoring 各自贡献。 |
| **Performance**：EWMBench & DreamGen Bench 综合第一，WorldModelBench & PBench 开源第一。 | §5.1 | Table 2 (4.60)、Table 3 (4.952)、Table 5 (8.99)、Table 4 (0.804) | 生成类基准上确实领先；但这些指标测的是**视频质量/指令跟随/物理合规**，不是闭环任务成功率——离「可用的仿真器」还有验证空档。 |

## 摘要与核心贡献

摘要给出的定位是：Qwen-RobotWorld 是 Qwen 系列里的 language-conditioned video world model，以自然语言为统一动作接口，从当前观测预测 physically grounded 的未来视觉轨迹，覆盖 manipulation / driving / navigation / human-to-robot transfer。这一统一形式指向三个应用方向：**合成数据增广、可扩展虚拟评估环境、语言引导的规划信号**。

三件套设计（摘要原话）：
- **a) Double-Stream MMDiT with MLLM Action Encoding**：60 层双流扩散 transformer，通过 layer-wise joint attention 把冻结 Qwen2.5-VL 语义与 video-VAE latent 耦合；
- **b) Embodied World Knowledge (EWK)**：8.6M video-text 语料（200M+ 帧），动作-语言映射覆盖 20+ embodiments、500+ 动作类别；
- **c) General+Expert Progressive Curriculum**：两阶段，先学通用视觉先验，再在共享语言接口下注入具身专精。

摘要给的头号成绩：**EWMBench 与 DreamGen Bench 综合第一**，**WorldModelBench 与 PBench 超过所有开源模型**；RoboTwin-IF 上的零样本分析进一步佐证鲁棒泛化与多视角一致。

> 读原文才发现的一处口径细节：摘要说「outperforms all open-source models on WorldModelBench」，正文 §5.1.4 明确是 **8.99、开源第一、总榜第 3**（仅次于闭源 Wan2.6 的 9.27、Veo3 的 9.25）。所以「开源第一」≠「总榜第一」，引用别写成「WorldModelBench 第一」。EWMBench(4.60) 和 DreamGen(4.952) 才是**总榜**第一。

## 按原文 section 逐节精读

### 1. Introduction / 为什么需要「语言条件」的世界模型

world model 被形式化为**状态转移函数**：给定当前 state $s_t$ 与 action $a_t$，预测下一 state。

$$
s_{t+1} = f(s_t,\ a_t)
$$

在 video-based world model 里，state 就是视觉观测（帧或其 latent），模型据当前观测 + 动作信号生成未来视觉轨迹。动作 $a_t$ 可以是低层电机指令、高层 waypoint 轨迹或自然语言指令——作者论断**自然语言是最通用、最可及的动作表示**。而且语言动作能双向用：既可作为 **input** 融进条件信号来支配状态转移，也可作为 **output** 从生成视频事后推断出动作标签。

作者随即点出那道根本张力（见「论文主线」）：general video models 有视觉先验没具身物理；domain-specific embodied models 有物理没跨域泛化。弥合之道 = 用通用视觉先验接地多样具身经验 + 自然语言当统一接口。**这一节读法**：introduction 的价值在于它把「为什么是语言、为什么要四域混训」讲成了因果链——manipulation/driving/navigation 各贡献一类物理知识，语言接口让它们能在同一骨干里互不冲突地叠加。后面每个组件都对应这条链的一环。

### 2. Data / EWK 数据集与动作-语言映射

#### 2.1 Action-Language Mapping / 把异构动作投到语言空间

核心洞察是一处**不对称**：视觉 state（视频帧）本就在共同的像素空间，但 action 表示碎裂在不兼容的模态里（关节角 vs 转向指令 vs heading）。框架把所有动作信号投到共享语言空间，于是同一个 diffusion transformer 无论底层物理域是什么都能学 $s_{t+1}=f(s_t,a_t)$。这对标注质量提出苛刻要求：**每条 caption 必须是完整自足的动作规范**，精确到模型仅凭 $a_t$ 与 $s_t$（无任何 robot metadata / proprioception）就能预测 $s_{t+1}$。

**Hierarchical Five-Layer Annotation（分层五层标注）**——前三层是结构化 CoT：
1. **Task Goal Layer**：推断转移的高层意图（$s_t\to s_{t+1}$ 该变什么）；
2. **Action Detail Layer**：把动作分解成时空轨迹/微动作/速度/力，**强制显式声明视角**（egocentric main / wrist / external / 多视角拼接）；
3. **Physical Feedback Layer**：描述动作对环境的**可观测**后果（位移、形变、接触状态变化），把每次转移接地到可验证的物理结果。

再据此生成两种粒度：**Comprehensive（50–100 词）**完整指定 viewpoint-agent-action-feedback 四元组；**Concise（15–30 词）**只留核心要素以支持推理时的简短高层指令。训练时两者各 50% 采样。四条质量准则：operation focus / viewpoint definition / objectivity / physical verifiability。

**覆盖度**：embodiment 轴含人手 + 七种机械臂构型（单臂夹爪、双臂夹爪、单臂灵巧手、双臂灵巧手、移动双臂、半人形、全人形）+ ego vehicle + pedestrian/drone + 移动导航 agent，共 **20+ distinct embodiments**（来自 RoboCoin 的 15 机型 / Robomind 的 4 形态 / InternData-A1 的 4 机型 / Groot-XE 等）；action 轴 **500+ 类别**（仅 Agibot-World 就定义 84 个 manipulation primitives），组织成四层：(1) manipulation primitives、(2) long-horizon compositions、(3) locomotion/navigation、(4) dynamic & deformable interactions。

#### 2.2 Data Collection / 四域数据来源

- **General Data**（30%）：互联网视频（统一 24 FPS，多分辨率多宽高比）+ 高质量静态图（作为 visual quality anchor）。**对 AIGC 采保守立场**：通用数据排除 AI 生成的图/视频，避免伪影、物理不一致与隐性偏差污染泛化。
- **Manipulation**（核心，~5.9M）：沿 Multi-Embodiment（人手 EgoHOD/EPIC-Kitchens 当 dexterity ceiling → robot 数据学映射到不同形态，习得 embodiment-invariant action semantics）、Multi-Task（短程 Bridge V2/RH20T 接触原语 + 长程 Agibot-World/Galaxea 链式序列 + 动态 Humanoid-Everyday 高速全身运动）、Multi-Scenario（real-first + 光真实仿真 InternData-A1 补足，因为大量 VLA policy 在仿真里训练/评测——world model 想当通用仿真骨干必须能生成 simulator-style 外观与物理）、Multi-View（同步 head/wrist/external，训练时当几何正则、推理时可任选视角或合成互一致的多视角；**~1.6M/6M 具身样本含 2–4 视角同步拼接**）四维组织。
- **Autonomous Driving**：Waymo E2E（真实，8 环视相机，7,044 clips / 11.3h）、NVIDIA PhysicalAI-AD（真实，5 相机 30°–120° FoV，1,342,418 clips / 1,715.9h）、Bench2Drive（CARLA 仿真，9,881 场景，6 相机，384,948 clips / 511.2h）、Sekai（行人/无人机 egocentric，9,995 clips / 166.6h）。**合计 1,744,405 clips / 2,405 小时**。三阶段处理：轨迹统一成 waypoint → 按 ego 机动切分 2–8s clip → 结构化轨迹描述 + 可选 VLM 增广 caption。
- **Indoor Navigation**：跟随 VLNVerse，用 Isaac Sim 采集 **6,064** 成功 episode，**134 室内场景**，egocentric RGB（256×256 @10FPS）配语言指令；轨迹平均 **8.2m**（4–17.5m），总里程 ≈49.8km、≈5.8h。指令两种格式：单串 step-by-step（3,031 集，均 67.2 词）+ 多粒度 formal/natural/casual（3,033 集）。
- **Human-to-Robot Transfer**：两路来源。其一 MANO 重建手部 3D 关键点 → retarget 机器人末端 → 视频 inpainting 去手 → MuJoCo IK 渲染 **14 种机械臂**，每 episode 产 4 路对齐视频（原始人视频/去手场景/纯仿真/机器人叠加）。其二基于 InternA1（Isaac Sim 有光影）在 MuJoCo 里渲染**无光影**的配对视图，让模型学「简化渲染↔真实观测」的视觉映射，覆盖 Franka/AgileX/ARX/AgiBot 四构型 **~80K episodes**。

#### 2.3 Data Processing / 四阶段流水线

统一流水线四阶段：(1) Raw Data Collection（五类源）、(2) Video Preprocessing（frame extraction / interpolation / sub-task splitting / main-view selection / multi-view concatenation 五种域自适应操作）、(3) Hierarchical Annotation（上文五层，附完整 prompt 模板）、(4) Caption Quality Filtering（LLM judge 沿 factual accuracy / specificity / instruction clarity / viewpoint consistency 打分 + 人工复核 + **闭环迭代**：对 scenario/task/embodiment 特定的系统性失败触发定向 prompt 重设计，回炉重标直到达标）。

**最终语料统计**：≈8.6M video-text（200M+ 帧），**具身 70% / 通用 30%**；具身内部——单视角 manipulation ≈**4.3M**（多数）、多视角同步拼接（2–4 相机）≈**1.6M**、navigation+driving ≈**200K**。

### 3. Model / 三组件与双流骨干

#### 3.1 Architecture / MLLM + VAE + MMDiT

三组件：**MLLM 当 action encoder**、**VAE 当 state encoder/decoder**、**MMDiT 当 transition function**，组织成双流。

- **MLLM — Action Encoder**：冻结 Qwen2.5-VL，对输入文本 $S$ 取末层隐状态作为 action condition：

$$
h = \phi(S)
$$

- **VAE — State Encoder/Decoder**：采用 Wan-VAE，编码视频帧到 latent、解码预测 latent 回视觉：

$$
z = E(x)
$$

- **MMDiT — Transition Function**：understanding stream 收 MLLM 编码 $h$（经可训练 connector 投影），generation stream 收来自 VAE 的带噪 state latent；每个 block 两流经 **joint attention** 交互。

**规格（原文真实数字）**：60 个 double-stream blocks，24 个 attention heads（head dim 128），hidden size 3,072，patch size 2×2。参数量：**MLLM 7B、VAE 127M（encoder 54M + decoder 73M）、MMDiT 20B**。context length 支持最多 **48,360** video tokens。

用 MLLM（而非 T5/CLIP 轻量编码器）当动作编码器的两点好处：(1) 深层语言理解把复杂组合指令解析成精确条件信号；(2) 其内化 world knowledge（机械臂是刚体、连杆定长、关节受限）**隐式约束物理合理转移空间**，配合 T2I co-training 防止跨帧物体形变——这正是缺乏语义接地的模型的常见失败模式。

#### 3.2 3D Rotary Position Encoding / 非对称维度分配

3D RoPE 独立编码 temporal / height / width 三轴，但**非均匀分维**：时间 16 维、高/宽各 56 维，合计 128（`pe_axes_dim = [16, 56, 56]`）。理由：相邻帧强相关故时间少分维；空间轴要抓物体位置与场景布局的多样性故多分维。另用 Scalable RoPE 支持推理时对不同分辨率/时长的泛化。**这是本文实现「零架构改动的多视角几何一致」的关键之一**：多段/多视角各自分到独立的 temporal index 区间。

#### 3.3 Scene2Robot / 多段条件做跨具身视频编辑

在双流 MMDiT + 非对称 3D RoPE 之上，Scene2Robot 复用**同一骨干**做跨具身合成。

- **First-Frame Conditioning（TI2V baseline）**：首帧 VAE latent 赋 timestep $t=0$ 且排除出 denoising loss，冻结 Qwen2.5-VL 编码文本进 understanding stream；joint attention 让 generation token 同时 attend 视觉锚点与语义动作规范。
- **Multi-Segment Extension（H2R transfer）**：把首帧条件扩成**三段**输入，全在同一 VAE-MMDiT 里无架构改动处理——① Scene condition（$F$ 帧，人手 mask 掉的原演示，供外观/布局/物体状态）② Robot reference（$F$ 帧，MuJoCo 渲染的仿真机器人执行，供目标 embodiment 的运动学轨迹/形态）③ Generation（$F$ 帧，待去噪成最终光真实机器人执行）。段①②共享 $t=0$ 且不计 loss，**只有段③吃梯度**；3D RoPE 给每段独立 temporal index。joint attention 让 generation token 同时读段①的场景外观、段②的机器人运动、understanding stream 的语义——tripartite conditioning 合成既保场景又守指令行为的执行视频。

### 4. Training / 从通用先验到具身专精

#### 4.1 Training Strategy / 两阶段渐进课程

统一范式：general scene generation 与 robot manipulation prediction 被统一成**同一个条件视频生成任务**（共享语言接口），模型全程从两类数据同时吃梯度，让通用世界先验与具身动作先验经共享骨干互相强化。

- **Pretraining**：从 14 个高质量视频平台采 200M+ 真实观测样本（自然场景/日常/运动）建 domain-agnostic 世界先验；引入大规模第一人称手部操作（Ego4D、EPIC-Kitchen）当「通用↔具身」的天然桥；**T2I / T2V / TI2V 联合训练**——T2I 学锐利视觉表示当 visual quality anchor，其物体形态知识经共享骨干自动迁移到视频生成、防形变与身份不一致。任务比例从纯 T2I 渐移到三任务联合。
- **SFT（四阶段混合调度）**：single-view manipulation → multi-view expansion（加 wrist/third-person 视角）→ multi-view concatenated generation（同步首帧空间拼接、逼 attention 建跨视角对应）→ complex tasks & cross-domain（pouring/folding/bimanual 等稀缺高复杂任务 + 长程推理）。**70% 具身 / 30% 通用**，具身内部 manipulation ≈90% 采样权重保深度，multi-view concat 与 nav/driving 各 ≈5% 保广度；**通用数据每个 batch 都在**，确保专精与通用建模同步前进而非此消彼长。

#### 4.2 Training Objective and Infrastructure

训练目标是 **flow matching**：视频经 VAE 编码进 latent、噪声取标准正态、timestep 取 log-normal 且随视频序列长自适应 shift；TI2V 任务首帧 timestep 固定 0 以保证生成以给定观测帧为条件。基础设施：Megatron-LM + hybrid parallelism，对**部分 dual-stream blocks** 用 selective activation recomputation 平衡显存与吞吐。

### 5. Experiments / 实验

见下方 ## 实验 专节（含四基准真实数字 + 两张真实零样本图讲解）。

### 6. Conclusion / 结论

Qwen-RobotWorld 用共享自然语言动作接口统一 manipulation/driving/navigation/H2R，靠三件套（双流 MMDiT + MLLM 动作编码、EWK 数据、general+expert 课程）让**一个共同骨干**可适配三类具身应用（合成数据、策略评估、动作规划）。基准 + 零样本分析均显示强而一致的表现与鲁棒的多视角指令跟随泛化。作者的收尾定位是「不仅感知强，还要对下游机器人学习/控制**功能有用**」——这句话恰恰暴露了本报告的验证空档：它证明了「生成质量/指令跟随强」，但「合成数据真能提策略成功率、虚拟环境真能替代真机评估」这些 downstream 闭环收益，本报告未直接测。

## 方法细节速览（架构与训练超参）

| 维度 | 取值（原文） | 备注 |
| --- | --- | --- |
| MMDiT blocks | 60 double-stream | 每层 joint attention |
| attention heads / head dim | 24 / 128 | hidden size 3,072 |
| patch size | 2×2 | |
| 参数量 | MLLM 7B + VAE 127M + MMDiT 20B | VAE = encoder 54M + decoder 73M |
| context length | ≤48,360 video tokens | |
| 3D RoPE 维度 | `[16, 56, 56]`（temporal/H/W） | 非对称，合计 128 |
| action encoder | 冻结 Qwen2.5-VL（取末层 hidden） | 非 T5/CLIP |
| state VAE | Wan-VAE | 图/视频通吃 |
| 训练目标 | flow matching | log-normal timestep + 自适应 shift；TI2V 首帧 t=0 |
| 基础设施 | Megatron-LM + hybrid parallelism | 部分块 selective activation recomputation |
| 数据混比 | 70% 具身 / 30% 通用 | SFT 内具身 manip ≈90% 权重 |

> 说明：本报告是 technical report，**没有独立的 method ablation 表**（无「去掉某组件掉几分」的对照）。所谓「消融」由跨基准对比 + RoboTwin-IF 零样本 model-to-model 比较承担，见下。

## 实验

### Setup / 基准、基线、指标

- **四个量化基准**：EWMBench（具身运动保真）、DreamGen Bench（机器人视频生成质量）、PBench（物理行为理解 + 画质）、WorldModelBench（物理合规 + 指令跟随）。约定：加粗=每列最优，下划线=次优。
- **基线两类**：**通用视频生成** Sora2 / Veo3 / Wan2.6 / Kling / LTX-2；**具身世界模型** Cosmos / WoW / LVP / Vidar / GigaWorld。
- **零样本鲁棒**：RoboTwin-IF 上做 model-to-model side-by-side，对手 LVP 与 Cosmos2.5-14B，四个 Unitree G1 任务。

### 主结果 1：EWMBench（Table 2，总榜第 1）

EWMBench 含 21 样本 / 7 任务（有明确动作顺序约束）。三维：scene consistency（SceneC）、motion correctness（HSD/Dyn/nDTW）、semantic alignment（Diversity/BLEU/CLIP/Logics）。

| Model | SceneC | HSD | nDTW | Logics | **Overall** |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sora2（通用最佳） | 0.853 | 0.281 | 0.275 | 0.947 | 3.89 |
| GigaWorld | 0.871 | 0.305 | 0.278 | 0.900 | 3.56 |
| LVP（次优） | 0.880 | 0.425 | 0.623 | 0.952 | 4.05 |
| Wow | 0.887 | 0.249 | 0.257 | 0.952 | 3.52 |
| **Ours** | **0.914** | **0.566** | **0.671** | **1.000** | **4.60** |

**读法**：Ours 综合 **4.60 总榜第 1**，超次优 LVP(4.05) **+0.55**；motion fidelity 的 **HSD 0.566 比 LVP 0.425 高 33%** 是最亮的领先项；SceneC 0.914 与 Logics 1.00 也居顶。注意 Diversity(0.0114) 偏低——它更像「多样性↔一致性」的权衡而非缺陷。

### 主结果 2：DreamGen Bench（Table 3，总榜第 1）

测 GR1 机器人三子集（Env/Object/Behavior 泛化）的 physics alignment(PA) 与 instruction following(IF)，IF 用 Qwen2.5-VL 当评判。

| Model | GR1-Object IF | GR1-Behavior IF | **Total** |
| --- | ---: | ---: | ---: |
| LVP | 0.829 | **0.889** | 4.758 |
| GigaWorld | 0.852 | 0.884 | 4.216 |
| Wow | 0.849 | 0.696 | 4.728 |
| **Ours** | **0.878** | 0.832 | **4.952** |

**读法**：Ours **总分 4.952 第 1**，GR1-Object IF 0.878 第 1（object-level 组合泛化强），PA across 子集稳定（0.828/0.840/0.781）。作者诚实点出**短板**：GR1-Behavior IF 0.832 略逊 LVP(0.889) 与 GigaWorld(0.884)——**长程行为泛化是待改方向**。

### 主结果 3：WorldModelBench（Table 5，开源第 1 / 总榜第 3）

350 实例 / 7 域 / 56 子域。三维：instruction following(0–3)、common sense(frame/temporal)、physics adherence（Newton/Mass/Fluid/Penetration/Gravity 五类违规）。

| Model | Instr(0-3) | Common Overall | Physics Overall | **Total** |
| --- | ---: | ---: | ---: | ---: |
| Wan2.6（闭源第 1） | 2.50 | 1.94 | 4.83 | 9.27 |
| Veo3（闭源） | 2.52 | 1.93 | 4.80 | 9.25 |
| Cosmos | 2.14 | 1.94 | 4.86 | 8.94 |
| LVP | 2.01 | 1.80 | 4.87 | 8.67 |
| **Ours** | **2.33** | 1.72 | **4.94** | **8.99** |

**读法**：Ours **8.99 开源第 1、总榜第 3**（仅次于闭源 Wan2.6/Veo3）；**physics adherence 在 Newton/Mass/Fluid/Gravity 四类拿满分 1.00**（penetration 0.94），与领先闭源持平；instruction following 2.33/3.0 强。common-sense(1.72) 偏低，作者归因于**输出分辨率较低**（专为具身任务而建）。

### 主结果 4：PBench（Table 4，开源第 1）

两维：Domain Score（物理行为理解 QA，六域，Qwen2.5-VL 评）+ Quality Score（8 项 VBench 画质指标），Overall = 二者均值。

| Model | Aes | Mot(smooth) | Quality | Domain | **Overall** |
| --- | ---: | ---: | ---: | ---: | ---: |
| Veo3（通用） | 0.526 | 0.994 | 0.771 | 0.882 | 0.827 |
| Cosmos | 0.470 | 0.989 | 0.763 | 0.840 | 0.802 |
| LVP | 0.515 | 0.991 | 0.772 | 0.812 | 0.792 |
| **Ours** | 0.455 | 0.990 | 0.751 | **0.857** | **0.804** |

**读法**：Ours **Overall 0.804 超所有开源**；最强维度是 **Domain understanding 0.857（总榜第 3，超多数闭源）**；motion smoothness 0.990（开源第 2）。Aes(0.455)/Img(0.649) 偏低——作者再次归因于**为具身任务定制、输出分辨率低于通用视频生成器**，拉低了 VBench 的像素级画质分，但「对下游机器人控制足够」。

### 定性与零样本分析（§5.2）

三层递进：fine-grained language grounding（Fig.5：对比对——同初始帧只改一个关键词就产出不同视频；复杂指令——多步依赖/抽象目标推断）；generalization across embodiments/tasks/viewpoints（Fig.6：一条指令驱四种形态；跨任务跨环境；多视角一致）；zero-shot robustness（Fig.7/Fig.8）。

![[papers/images/zhang2026qwen-robotworld/lamv_zero_shot_comparison.png|760]]

**Figure 7 / 语言-动作对齐 × 多视角一致的零样本对比。** 同一 conditioning（相同初始帧、prompt、相机布局）下把 Ours 与 **LVP**、**Cosmos2.5-14B** 摆一起比，四个 Unitree G1 任务：Task 01 把黑色矩形件插进匹配黑壳；Task 02 用灰抹布擦净桌上黄渍；Task 03 把香蕉/西瓜片/牛油果放到色彩匹配的盘；Task 04 用蓝板擦擦掉白板红波纹线。**读图重点＝证明什么**：Ours（前两个任务是 multi-view，画面右下带 wrist 视角小窗）**更一致地保住 language-grounded execution**——正确的物体/动作对应 + 更干净的目标完成，且多视角轨迹连贯；两个基线各有不同 failure：**LVP 更常产出未完成执行**（如 Task 01 末帧插件半途而废），**Cosmos2.5-14B 在复杂情形更常出现指令与操作后果对不齐**（画面漂移/物体走形）。这张图把聚合分数拆开，让「指令不匹配 / 跨视角不一致 / 通用画质退化」三种失败源能被分离着看。

![[papers/images/zhang2026qwen-robotworld/robotwin_zero_shot_showcase.png|760]]

**Figure 8 / RoboTwin-IF 零样本定性案例。** 基准建在 RoboTwin 仿真器上、含大量新构复杂任务，本文**零样本**评测（训练只混了少量开源 RoboTwin 数据）。四难度层每层两例，每任务 10 帧（首末帧锚定）：**Basic Manipulation**（左臂拿蓝纸巾盒 / 右臂拿魔方并摇一次）→ **Relative Positioning**（左臂把鼠标放到桌左上区 / 右臂把木盒放到手机上）→ **Bimanual Collaboration**（左臂拿木盒交接右臂再放到肥皂上 / 左拿魔方同时右拿面包）→ **Long-Horizon / Complex Instructions**（木盒放前、鼠标放左、面包放右的三步序列 / 黄盒放中、铃放右、鼠标放左的序列）。**读图重点＝证明什么**：跨这四个由易到难的层级，Ours 都**保住连贯执行与跨视角一致**（多行画面右下含第二视角小窗），定性上与 RoboTwin-IF 的量化结论一致——增益不是几个精挑的例子，而能泛化到更难的**未见**具身任务。

### Cross-Domain Generalization（§5.3）

Fig.9 human-to-robot transfer 跨 **8 个目标 embodiment**，保住人演示的任务意图同时适配各自运动学约束；Fig.10 mobility——自动驾驶（Bench2Drive/NVIDIA PhysicalAI-AD/Sekai/Waymo）+ 室内导航（VLNVerse 语言引导第一人称）。共同说明学到的语言条件转移模型能越出单一 embodiment/场景族。（Fig.5/6/9/10 不在本地图库，故不嵌。）

## 图表索引与讲解

| 图 / 表 | 读图重点＝证明什么 | 关联问题 |
| --- | --- | --- |
| Figure 1（未嵌） | EWK 语料总览：通用先验（上）+ 结构化具身数据沿 Multi-Embodiment/Task/Scenario/View 四轴（中）→ 供出语义/几何/物理对齐/因果（下）。 | 四域数据如何互补地喂给状态转移函数。 |
| Figure 2（未嵌） | 四阶段数据流水线：采集→预处理→五层标注→caption 质检闭环回炉。 | 纯语言接口的一致性靠什么保证。 |
| Figure 3（未嵌） | 60 层 double-stream MMDiT：Qwen2.5-VL(action)+VAE(state)+MMDiT(transition)，每层 joint attention。 | 语言条件的状态转移在架构上怎么落地。 |
| Figure 4（未嵌） | Scene2Robot 三段条件（scene/robot/generation），只有 generation 段计 loss。 | 无架构改动怎么做跨具身视频编辑。 |
| Figure 5/6（未嵌） | 细粒度语言接地（改一个关键词换一种行为）+ 跨具身/任务/视角泛化。 | 语言当动作接口是否真的可分辨、可迁移。 |
| **Figure 7（已嵌）** | 四 Unitree-G1 任务下 Ours vs LVP vs Cosmos2.5-14B：Ours 更一致保住语言接地执行 + 多视角连贯；LVP 常未完成、Cosmos 常对不齐。 | 聚合分之外，逐 failure-source 的零样本可比性。 |
| **Figure 8（已嵌）** | RoboTwin-IF 四难度层零样本：基础→相对定位→双臂→长程，Ours 均保连贯执行与跨视角一致。 | 增益能否泛化到未见的更难任务。 |
| Figure 9/10（未嵌） | H2R 跨 8 形态 + 驾驶/导航 mobility 生成。 | 转移模型是否越出单一 embodiment/场景。 |
| Table 1 | EWK 数据混合清单（按域列 embodiment/views/tasks/贡献）。 | 每个数据集补哪类物理知识。 |
| Table 2 | EWMBench 4.60 总榜第 1，HSD 0.566(+33%)、SceneC 0.914、Logics 1.00。 | 运动保真与场景一致的领先幅度。 |
| Table 3 | DreamGen 4.952 总榜第 1，GR1-Object IF 0.878 第 1；GR1-Behavior IF 0.832 逊 LVP/GigaWorld。 | 组合泛化 vs 长程行为泛化的强弱。 |
| Table 4 | PBench 0.804 开源第 1，Domain 0.857 强；Aes/Img 因分辨率偏低。 | 物理理解强、像素画质弱的权衡。 |
| Table 5 | WorldModelBench 8.99 开源第 1/总榜第 3；四类物理满分 1.00，Instr 2.33。 | 物理合规到顶后，差距在 common-sense/分辨率。 |

## 和你的论文库中其他条目的关系

- 对 [[@gigaworld2026roadmap]]（GigaWorld-1）：**直接相关且是本文基线**——本报告在全部四个基准里都拿 GigaWorld（GigaWorld-0，Team et al. 2025）当对手（EWMBench 3.56 / DreamGen 4.216 / WorldModelBench 7.31 / PBench 0.794，均被 Ours 超过）。两者路线互补：GigaWorld-1 把 world model 主要当**策略评估的工程/流程栈**（训练/推理/评测生态），Qwen-RobotWorld 则把重心放在**用语言统一多域生成**这个建模问题上。可对照「world model 的价值兑现在评测工具链 vs 在跨域生成能力」。
- 对 [[@wang2026orca]]（Orca, "The World is in Your Mind"）：两者都想要「通用 world foundation model」，但**接口哲学正相反**——Orca 追求统一 **world latent space** 并靠多模态 readout 支持理解/预测/行动；Qwen-RobotWorld 明确放弃统一 latent，改用**统一 caption（语言）** 当接口。对读点：跨域统一到底该压在 latent 空间还是语言空间。
- 对 [[@gao2026fast-leworldmodel]]（Fast LeWorldModel）：都做 video/visual world model 用于规划，但 Fast LeWorldModel 聚焦**推理效率**（把 autoregressive latent rollout 改成 action-prefix prediction 以加速 visual planning、减少长 horizon 误差累积）；Qwen-RobotWorld 聚焦**数据/接口的广度**。恰好一个补「怎么把 world model 跑快」，一个补「怎么把 world model 铺广」，可纵向串读。
- 对 [[@wang2026wvm]]（World Value Model）：两者都在问「world model 除了生成画面还能干嘛」。WVM 把世界模型的**时间/未来建模能力用于 value 评分**（在 mixed-quality 数据里评任务进展）；Qwen-RobotWorld 把它用于**跨域未来视觉轨迹生成**并自陈可当策略评估环境——正好能和 WVM 组成「生成式评估环境 + 价值式打分」的两种评估路径对照。
- 对 [[@wu2026tactile-wam]]（Tactile-WAM）：**反例式互补**。Tactile-WAM 的核心论点恰恰是「视觉未来只是部分世界状态，接触动力学（slip/jamming/contact normal）在 RGB 里弱可见」；而 Qwen-RobotWorld 是纯视觉世界模型、动作接口是语言、完全不含触觉通道。把两者并读能清楚看到本文的能力边界：**它擅长语言可描述、视觉可见的状态转移，但对「视觉不可见的接触事件」无建模手段**。
- 对 [[@li2026zr0]]（VLA + dense embodied CoT 监督）：处在不同层次——Qwen-RobotWorld 是「预测未来视觉轨迹」的 world model，ZR0 是「输出动作」的 VLA 策略。本报告自陈可当**合成数据引擎/规划信号**，恰能给 ZR0 这类 VLA 供数据或语言规划先验，是「world model → policy」的上下游关系。
- 论文自身引用/对比的近亲（**均不在当前库**，如需可另行入库）：LVP（Large Video Planner，最强对手，Chen et al. 2025a）、Cosmos [Agarwal et al. 2025]、WoW [Chi et al. 2025]、Vidar [Feng et al. 2025]；数据侧 Agibot-World、RoboMind、RoboCoin、Bridge V2、DROID、VLNVerse、InternData-A1；理论近亲 Ye et al. 2026「World action models are zero-shot policies」（本文「语言是最通用动作表示」的直接引据）。

## 可追问点

1. 全部结论都建在**生成类基准**（视频质量/指令跟随/物理合规）上，没有一个 downstream **闭环任务成功率**数字。「合成数据真提 policy success、虚拟环境真能替代真机评估」这三大应用主张，本报告实际验证到哪一步？
2. 跨域一致性全压在 **caption 质量** 上（LLM-judge + 部分人工）。当 caption 与视频有系统性偏差（如遮挡下的接触状态被误标），模型学到的 $f(s_t,a_t)$ 会不会被 caption 噪声带偏？质检闭环覆盖率有多高？
3. WorldModelBench 物理四类已满分 1.00，但**penetration 只有 0.94**、common-sense 1.72 偏低（归因分辨率）。物理合规到顶后，剩余差距是否本质是「分辨率/画质」而非「物理」？提分辨率会不会反噬 embodied 专精？
4. 纯视觉 + 语言接口，**没有触觉/力觉通道**（对比 [[@wu2026tactile-wam]]）。对 insertion/assembly 这类成败取决于毫米级接触的任务，语言 caption 能编码到什么精度？Fig.7 的 Task 01 插件成功是真接触对齐还是「看起来插进去了」？
5. RoboTwin-IF 是零样本，但训练**混了少量开源 RoboTwin 数据**。「少量」是多少？零样本的成色（是否有分布泄漏）需要看数据配比——原文未给具体比例（需回看）。
6. GigaWorld-0 作为基线在 WorldModelBench(7.31)、EWMBench(3.56) 都不高，但它本身定位是数据引擎而非高保真生成器。用「生成质量基准」比较一个「数据引擎工具链」是否 apples-to-apples？（同问 Vidar/WoW。）
7. Human-to-robot transfer 靠 MANO→retarget→inpainting→MuJoCo IK 的合成管线产数据。这条管线的物理保真（IK 误差、inpainting 伪影）会不会成为 H2R 生成质量的隐性上限？

## 我的阅读笔记

这篇是 **Qwen 系列的具身 world model 技术报告**，它最扎实的贡献其实在**数据与接口工程**，而非某个新算法模块。真正的赌注是那句「**自然语言是最通用、最可及的动作表示**」——一旦接受这个前提，跨 20+ embodiment、四大域的异构问题就被优雅地压平成「同一个语言条件视频生成任务」，于是零架构改动混训、Scene2Robot 复用同一骨干、multi-view 靠 concatenation + 非对称 3D RoPE 而非新模块，全都顺理成章。这种「把复杂性推给数据标注、让模型保持简单」的路线选择，是它和 [[@wang2026orca]]（推给统一 latent）最本质的分野。

但要清醒看边界。**第一，所有硬指标都是生成质量类的**（EWMBench/DreamGen/PBench/WorldModelBench 测的是视频好不好、指令跟没跟、物理违不违规），**没有一个闭环 policy success**——而摘要开出的三张支票（合成数据、虚拟评估、动作规划）恰恰都需要闭环证据。所以现在更准确的说法是：它证明了「能生成高质量、强指令跟随、物理合规的具身视频」，但「这些视频对下游控制真有用」仍是承诺而非结论。**第二，纯视觉 + 语言接口意味着它对视觉不可见的接触物理天然失明**——把它和 [[@wu2026tactile-wam]] 并读，能立刻定位到它的盲区在 insertion/assembly 这类毫米级接触任务。**第三，几个诚实的自陈短板值得记住**：GR1-Behavior 长程行为泛化逊于 LVP/GigaWorld、common-sense 因分辨率偏低、Aes/Img 画质因专精而弱——这些说明「统一」是有代价的，具身专精换来了通用画质的让步。

我会把它作为**「语言条件、跨域统一」这条世界模型路线的代表**入库，与 [[@wang2026orca]]（latent 统一）、[[@gigaworld2026roadmap]]（评估工具链，且是本文基线）、[[@gao2026fast-leworldmodel]]（推理提速）横向对照，构成「world model 的接口/工程/效率」三视角；再与 [[@wang2026wvm]]（价值式评估）、[[@wu2026tactile-wam]]（触觉补盲）纵向互补。等看到它当合成数据引擎、真把某个 VLA（如 [[@li2026zr0]]）的成功率提上去的实测，才是它兑现「functionally useful」承诺的时刻。
