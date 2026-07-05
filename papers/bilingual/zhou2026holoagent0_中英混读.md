---
tags:
  - bilingual-reading
  - deep-reading
paper: "[[@zhou2026holoagent0]]"
source_pdf: "[[papers/pdfs/zhou2026holoagent0.pdf]]"
images: "papers/images/zhou2026holoagent0/"
image_index: "[[papers/images/zhou2026holoagent0/index.md]]"
created: 2026-07-05
reading_mode: 生成式精读（逐节读原文 + 读图）
---

# HoloAgent-0: A Unified Embodied Agent Framework with 3D Spatial Memory

paper:: [[@zhou2026holoagent0]]
pdf:: [[papers/pdfs/zhou2026holoagent0.pdf]]
images:: [[papers/images/zhou2026holoagent0/index.md]]

> 本文本地图目录 `papers/images/zhou2026holoagent0/` 当前抽取到 **0 张图片**（见 `index.md`）。因此本稿不嵌入 `![[...]]`，而在“图表索引与讲解”里据全文 Figure/Table caption 文字说明每张图在证明什么。**需要看图时补跑** `python setting/scripts/extract_paper_images.py`。

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| Embodied AgentOS | 具身 AgentOS（运行时层） | 本文的核心层：把自然语言指令编译成 executable skill graph，调度机器人资源，监控执行状态，并在观测偏离意图时触发澄清或 re-planning。它**不是一次性 planner**，而是 observe–retrieve–act–monitor 的闭环 runtime。 |
| embodiment gap | 具身鸿沟 | 本文的问题命名：物理技能不像软件 API 那样有 clean I/O 类型、确定性输出、完整反馈、可逆副作用；机器人会“去错房间/抓不到已移动的物体/只收到部分进度”，所以问题是**系统级**的。 |
| executable skill graph | 可执行技能图 | AgentOS 把指令拆成带 ordering / preconditions / recovery dependencies 的 skill node 图，调度器分发 ready 节点、消费 status、失效时重规划。 |
| typed skill call | 类型化技能调用 | 技能接口的原子：command name + typed params + preconditions + target references + expected effects，例如 `move_to(room=kitchen)`、`pick(object=mug)`、`speak(text=...)`。给 AgentOS 一个稳定的**符号动作空间**。 |
| runtime status interface | 运行时状态接口 | 每个 backend 发布 **execution trace 而非隐藏成功标志**：progress / success / failure mode / confidence / latency / recoverability。这些事件成为“继续/重试/澄清/更新记忆/重规划”的 planning evidence。 |
| ROS2 command/status bus | ROS2 命令/状态总线 | 把四层连起来的物理连线：command topics 下发 skill call，status topics 回传进度、失败、传感器健康、检索到的上下文、memory-update 事件。换模型不换闭环。 |
| 3D spatial memory | 三维空间记忆 | 持久世界表示，含 geometry/topology/occupancy、robot pose/localization、open-vocabulary 3D semantic map、HMSG。是标题里“3D Spatial Memory”的实体。 |
| temporal memory | 时间记忆 | 与空间记忆互补：记录 active goal & plan state、execution & recovery trace、outcome & experience summary——回答“想干什么/已发生什么/试过哪些恢复”。 |
| HMSG (Hierarchical Multimodal Scene Graph) | 分层多模态场景图 | 沿用 FSR-VLN 的 floor / room / view / object 四层索引；**view 层**是关键，桥接几何记忆与视觉推理，让 AgentOS 先几何剪枝、再用少量候选 view 交给 VLM 验证。 |
| HoloNavi | 导航技能族 | 空间导航后端：hierarchical object navigation（CLIP 快匹配）→ online verification loop（VLM 慢验证）→ frontier exploration（信息增益探索）。 |
| HoloBrain | 操作 VLA 后端 [15] | 本文复用的 manipulation VLA，实现 `pick/place/open/handover/push/fold`，输出 arm/gripper/dual-arm 动作，并把 grasp failure、collision risk 等作为 status 上报。 |
| HoloMotion | 全身运动后端 [35] | humanoid whole-body 后端，两种模式：motion-tracking（挥手/鞠躬/握手/跳舞）与 velocity-tracking（走/转/停/恢复）。 |
| fast-to-slow reasoning | 快到慢推理 | 沿用 FSR-VLN [39]：先用 hierarchical CLIP-feature matching 快速剪枝候选，再把小批候选 view 交给 VLM 做慢推理验证，兼顾效率与正确性。 |
| GeoFlow-SLAM++ / FAST-LIVO | 视觉-only / LiDAR 几何后端 | 几何记忆的两个可替换后端：GeoFlow-SLAM++ 是 GeoFlow-SLAM [41] 的多相机（N≥3）扩展，用 3D 基础模型 $\Phi_\theta$ 预测稠密深度、无需 RGB-D 硬件；FAST-LIVO [40] 是 LiDAR-inertial-visual odometry，供 safety-critical 部署用。 |
| SigLIP descriptors $d_0,d_1,d_2$ | SigLIP 描述子 | 语义建图里每个 SAM2 mask 算三份 SigLIP 特征：$d_0$ 全关键帧、$d_1$ 掩码段、$d_2$ 最小外接框，逐维加权融合成一个开放词表检索描述子（Eq.1）。 |
| Monitoring & Verification Layer | 监控与验证层 | 把 raw execution evidence 变成决策与反馈：部署时验证技能结果、给用户文本/语音反馈、给 AgentOS 重规划信号；开发时录 ROS2 bag / 日志 / RViz / Rerun 供调试。 |

## 论文主线

> **Figure 1（框架总览，本地暂无抽图）。** caption 说明 HoloAgent-0 通过一条 ROS2 command/status 总线把 **Embodied AgentOS、embodied memory、embodied skills** 连成闭环，完成 spatial retrieval → skill-graph planning → execution monitoring → memory update → feedback-driven re-planning。图里三层从上到下是：**Embodied AgentOS Layer**（Understand / Plan / Orchestrate / Dialogue / Re-plan 五个动作）、**Embodied Skill Layer**（HoloNavi 导航、HoloBrain 操作、HoloMotion 全身运动 + Voice/Perception + More Skills）、**Monitoring & Verification Layer**（StatusMonitor / Logging / Visualization / User Output）；右侧是 **Embodied Memory Layer**（Spatial Memory：几何/拓扑/占据、pose、3D 语义图、HMSG；Temporal Memory：Goal & Plan State、Execution & Recovery Trace、Outcome & Experience Summary）。中间的 **Agentic Execution Loop** 把 UserPrompt→Task Plan→Gather Context→Embodied Skill Execution→Monitor & Verify（Task Verifier: Success/Failure）→Update / Re-plan / Retry 串起来，云端 LLM/VLM 通过 API 参与推理。这张图一眼给出全文骨架：**把数字 agent 的 reason–tool–feedback–revise 循环，接到物理机器人的 ROS2 技能总线上，用持久 3D 记忆做 grounding。**

这篇论文的核心问题是：**LLM agent 在数字世界里已经有一套成熟的执行循环**——reason over structured state、invoke tools、inspect feedback、revise actions。但把这套循环搬到物理机器人上非常难，因为物理执行是**连续的、依赖具体本体的、不确定的、受安全约束的**。作者把这条鸿沟精确命名为 **embodiment gap**：物理技能不像软件 API——没有干净的输入/输出类型、没有确定性输出、没有完整反馈、副作用不可逆。机器人可能因为空间记忆过期而走错房间，可能因为物体移动而抓空，可能只从运动控制器收到“部分进度”。

作者的判断是：**这不是再训一个更强的策略模型能解决的，而是一个系统级问题**——具身 agent 需要一个执行抽象，让物理技能在长程任务里变得 composable（可组合）、observable（可观测）、verifiable（可验证）。现有系统（VLA / VA / whole-body、spatial understanding、VLN、motion control）推进了各自的能力模块，但大多仍把 manipulation / navigation / spatial understanding / motion control 当成**专门模块、模型级策略或松耦合的 agent loop**，缺一个能组合异构技能、把执行 ground 到持久 3D 记忆、追踪部分进度、并从具身失败里触发恢复的**物理执行接口**。

作者的回答是 **HoloAgent-0**：一个用于真实部署的统一具身 agent 框架。它**不替换底层策略模型**，而是把异构机器人能力组织成一个以 Embodied AgentOS 为中心的闭环 workflow。框架三层耦合：
1. **Embodied AgentOS** —— 任务规划、调度、监控、失败恢复；
2. **Memory Layer** —— 持久空间 grounding + 时间执行历史；
3. **Skill Layer** —— 把机器人能力暴露成带结构化输入、进度信号、失败模式、可恢复性状态的 **typed action**。

阅读时要盯住一句话：**本文的贡献不是“又一个更强的 VLA/导航模型”，而是“把异构机器人技能放进一个可观测、可验证、可恢复的执行操作系统里”**——HoloNavi/HoloBrain[15]/HoloMotion[35] 都只是被 AgentOS 调度、监控、恢复的 skill backend。这是一篇**系统/框架论文**，全文只有一个真正的公式（Eq.1 的 SigLIP 融合），大量篇幅在描述接口与数据流。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| **AgentOS runtime**：把长程具身任务执行形式化为“系统组织问题”，用闭环 workflow 把语言指令编译成 executable skill graph、调度资源、追踪任务状态、从 runtime feedback 重规划。 | §2（四层 runtime + ROS2 接口）、§2.1 四条设计原则。 | Table 1 sim SR 82.6% / SPL 42.8%（超 MSGNav 74.1/33.4、FSR-VLN slow 80.8/41.0）；Table 2 real-robot Top-1 97.70%（超 FSR-VLN 91.95）。 | 导航子系统有量化支撑；但“统一框架”的整体闭环只在导航被严格量化。 |
| **物理执行接口 + 空间/时间记忆**：用 typed embodied skill、spatial & temporal memory、runtime verification，让异构技能可组合、把规划 ground 到持久 3D 记忆、保存跨执行的任务历史。 | §3（typed skill call + 5 类技能族）、§4（Memory Layer）。 | Table 3 语义建图 ScanNet mIoU 31.58（最佳）、f-Acc 61.58（最佳）；Fig.5/Fig.8 instance association 与 dynamic update 可视化。 | 记忆/建图组件量化占优；但很多是复用既有工作（HMSG←FSR-VLN、几何←GeoFlow-SLAM++/FAST-LIVO）。 |
| **真实部署 + 闭环评估**：在真机上跑，量化 3D 语义建图与长程导航，定性演示 motion control / object search / cross-robot coordination / mobile manipulation。 | §5.1 三平台（G1、R1、wheeled dual-arm）；§5.4 定性执行轨迹。 | Fig.2 四个真实案例（含叠衣服的长程 mobile manipulation）；§5.4 承认 manipulation/motion/coordination **无标准 end-to-end benchmark**。 | 真机迁移成立；但操作/全身/跨本体只有定性演示，非量化，需谨慎解读“unified”。 |

## 摘要与核心贡献

摘要的矛盾是：**数字 LLM agent 的执行循环很成熟**（reason over structured state、invoke tools、inspect feedback、revise actions），但**扩展到物理机器人很难**——物理执行连续、依赖本体、不确定、受安全约束。现有具身系统推进了 manipulation / spatial understanding / navigation / humanoid control，却常停留在“专门模块”或“松耦合决策循环”。

HoloAgent-0 的回答是一个统一具身 agent 框架：**Embodied AgentOS 把语言指令转成 executable skill graph、调度机器人资源、监控执行、从 runtime feedback 触发澄清或重规划**；通过三层耦合（AgentOS 做闭环执行、3D spatial memory 做物理世界 grounding、embodied skills 做机器人动作）组织异构机器人模型与控制器。作者在真机上部署，评估 spatial memory、long-horizon navigation、closed-loop execution，横跨 motion generation、object search、cross-robot coordination、mobile manipulation。

摘要给的头号系统承诺是“**unified framework for real-world robot deployment**”，但要注意口径：

> 读原文才发现的口径细节：摘要列的四类任务里，只有 **navigation 与 3D semantic mapping 被量化评测**（Table 1/2/3）；**motion / object search / cross-robot / mobile manipulation 全是定性执行轨迹**（§5.4 明说“not a standardized benchmark … remains future work”）。所以“统一框架”这个词在导航子栈上有硬数字，在操作/全身/跨本体上目前只是 demo。引用时别把定性演示写成量化胜利。

## 1. Introduction / 从数字 agent 到物理 agent 的鸿沟

作者把数字 agent 的循环（reason–tool–feedback–revise）和物理机器人的困难摆在一起：物理执行**随时间展开、依赖 embodiment-specific 控制器与不确定的 3D 状态、可能部分失败或不安全**。这暴露了 embodiment gap——物理技能没有软件 API 的 clean I/O、确定性、完整反馈、可逆副作用。因此中心挑战是**系统级**的：具身 agent 需要一个让物理技能在长程执行里可组合、可观测、可验证的执行抽象。

作者随后梳理了能力模块的现状（VLA/VA/whole-body [10–19]、spatial understanding [20–26]、VLN [27–31]、motion control [32–35]，以及 π0.5 这类先出文本子任务再出连续动作的 dual-level 推理 [11,36–38]），并点名它们的共同缺口：**缺一个物理执行接口**去组合异构技能、把执行 ground 到持久 3D 记忆、追踪部分进度、从具身失败触发恢复。

据此 HoloAgent-0 把长程具身任务执行**形式化为系统组织问题**，AgentOS 编排 HoloNavi（导航）、HoloMotion[35]（全身运动）、HoloBrain[15]（操作）等专门后端。三点贡献：AgentOS runtime、带空间/时间记忆的物理执行接口、真实部署+闭环评估。

**这一节读法**：introduction 的价值在于它把“具身智能难”重构成了“缺执行操作系统”——后面每一层（AgentOS/Skill/Memory/Monitoring）都对应 introduction 里的一个具体缺口，可逐一回勾。它的“非目标”也很关键：**不重训底层策略**。

## 2. Embodied AgentOS / 面向机器人执行的闭环 runtime

AgentOS 是把自然语言意图变成闭环机器人执行的 runtime 层。**它不把语言模型当成一次性 planner**，而是维护任务状态、从记忆检索空间上下文、调度 skill call、监控状态、并在观测结果偏离意图时修订计划。四层（AgentOS / Skill / Memory / Monitoring&Verification）经 ROS2 command/status 总线相连。

> **Figure 2（四个真实闭环案例，本地暂无抽图）。** caption 列出四类代表行为：**(a) Prompt Motion Control**——执行并验证短程 whole-body 命令（“Move forward 1m / Reach”）；**(b) Active Object Search**——探索、建图、验证目标咖啡机（“Looking for a coffee machine”）；**(c) Cross-Robot Coordination**——一台机器人被导航路由、另一台执行 dance 技能（“take me to see the robots dance”）；**(d) Long-Horizon Mobile Manipulation**——把叠衣服拆成 navigation / pick-and-place / motion / manipulation 步骤（“help me fold the freshly washed clothes in that basket”，初始任务图列出 Pick basket → Move to worktable → Place → Pick clothes → Fold next item → Complete）。这张图证明**同一个 AgentOS runtime 能组合异构技能**。

### 2.1 Design Principles / 四条设计原则

- **Closed-loop first（闭环优先）**：把规划当成重复的 observe–retrieve–act–monitor 循环，而非一次性文本生成——技能失败、目标歧义、环境变化时都能改计划。
- **Memory-centric（记忆中心）**：持久空间/时间记忆是规划的**主要上下文**；派发动作前先向记忆查询 rooms / views / objects / poses / active goals / 近期技能结果，而不是只看当前相机帧或对话上下文。
- **Typed skill interface（类型化技能接口）**：机器人能力暴露成带命令参数与状态事件的 typed、可监控 skill call——把高层任务推理与 embodiment-specific 控制器解耦，同时保留恢复所需的进度与失败证据。
- **Observable by default（默认可观测）**：runtime 通过 user feedback、logs、visualization 记录并暴露 command/status 事件、检索到的记忆、状态转移、技能结果——既支持真机调试，也给 AgentOS 提供验证/修订所需的证据。

### 2.2 Runtime Layers & ROS2 接口 / 四层如何分工

AgentOS 用四个功能层实现 runtime loop，经 ROS2 command/status 接口相连。**Command topics** 把调度好的 skill call 从 AgentOS 送到能力模块；**Status topics** 回传 progress / failures / sensor health / retrieved context / memory-update 事件。这种 topic 级接口保证模块化：**换单个模型或控制器时，长程执行所需的闭环反馈路径不变**。

- **AgentOS Layer**：把每条用户指令变成可执行、可监控的 skill graph——解析请求、从记忆检索任务历史与空间证据、拆成带 ordering/preconditions/recovery dependencies 的 skill node；执行中调度器派发 ready 节点、消费 status、计划失效时触发澄清或重规划。
- **Skill Layer**：通过 interaction / perception / navigation / manipulation / whole-body motion 等可调用能力实现 agent 的“身体”；每个技能消费结构化命令参数、发布 progress/success/failure mode/confidence/latency/recoverability 等状态事件。
- **Memory Layer**：给 planning / localization / perception / 跨本体协作共享持久空间+时间记忆；空间记忆返回候选物体、可导航区域、场景图上下文、定位假设；时间记忆记录 active goal & plan、执行与恢复轨迹、结果摘要；执行后 memory-update 模块把新观测与技能结果写回。
- **Monitoring & Verification Layer**：把 raw execution evidence 变成决策与反馈——部署时验证技能结果、给用户文本/语音反馈、给 AgentOS 重规划信号；开发时录 ROS2 bag / 结构化日志 / RViz / Rerun 供跨感知-记忆-规划-控制的失败诊断。

**这一节读法**：ROS2 topic 接口是全文的“物理承诺”——它把“换模型不换闭环”从口号变成工程约束。四层里 **Monitoring & Verification 常被忽略但很关键**：它是让“失败变成 planning evidence”这句话落地的地方。

## 3. Skill Layer / 把机器人能力做成可执行动作接口

Skill Layer 是 AgentOS 计划与机器人硬件之间的**可执行边界**。核心设计是：**不要求语言 planner 直接吐底层控制**，而是把能力暴露成 typed、monitored 的 skill call——skill call 说“要达成什么”，embodiment-specific 后端决定“怎么执行”，runtime status 流报告“是否达到意图状态”。这给 AgentOS 一个稳定动作空间，同时让 foundation model / 经典控制器 / 混合系统在同一 ROS2 接口后独立演进。

### 3.1 Typed Skill Calls & Runtime Status / 技能接口的原子

不像软件工具，物理技能会**部分失败、受本体约束、返回延迟或不完整反馈**。所以接口不只规定发给后端的命令，还规定期望效果与 AgentOS 用来验证/重试/重规划的 runtime evidence。

- **Command schema**：每个技能声明 command name、typed parameters、preconditions、target references、expected effects，例如 `move_to(room=kitchen)`、`pick(object=mug)`、`speak(text=...)`。AgentOS 用这些字段构建 skill graph、绑定 memory-grounded 目标、检查观测结果是否满足 postcondition。
- **Runtime status interface**：每个后端发布 **execution trace 而非隐藏成功标志**——trace 报告 progress / success / failure mode / confidence / latency / recoverability，让 AgentOS 区分“完成”与“被阻塞/歧义/不安全/可恢复”，这些事件成为 planning evidence。
- **Embodiment-specific backend**：learned policy / 经典控制器 / 混合系统把同一技能接口 ground 到具体身体上，让高层动作空间在 humanoid / mobile base / manipulator 间保持稳定，各平台用自己的传感、驱动、安全约束实现。

### 3.2 Interaction & Perception Skills / 人机通道与 grounding 通道

- **Interaction skills**：语音接口把 ASR / dialogue state / TTS 包成 `listen`、`speak` 等可调用技能，返回 transcription confidence、clarification request、user confirmation、interruption、delivery completion 等状态——让 AgentOS 在意图或执行状态不确定时把 human 留在环里。
- **Perception skills**：open-vocabulary 感知暴露 `detect`、`localize`、`verify`；AgentOS 提供 object/region/target 引用，后端返回检测实例、置信度、view evidence、target-verification 结果、memory-update 触发。导航与操作技能用它做目标选择与结果验证，记忆层把它存成 object observation / view descriptor / 刷新的场景图证据。

### 3.3 HoloNavi / 空间导航与探索

> **Figure 3（HoloNavi 物体导航流水线，本地暂无抽图）。** caption：给定语言目标，HoloNavi 先做 **hierarchical semantic navigation**（解析指令 → 对 floor/room/view/object 级记忆匹配），到达候选视点后进入 **online verification loop**（open-vocabulary 检测 + 局部视点微调验证目标），验证失败则进入 **frontier exploration loop**（持续建图 + 在线检测，直到找到目标或搜索耗尽）。图里三块子循环：1. Hierarchical Object Navigation（“Find the bedside table on the bedroom on floor 1” → Hierarchical CLIP Feature Matching → View Selection & Refinement → 2D Detection during moving）、2. Online Verification Loop（“Is there a bedside table in the image?” Yes→Object Center Calculation→Move to object；No→Rotate & Detect）、3. Frontier Exploration Loop（Frontier Point Detection → Move to frontier → Incremental Mapping，First/Second Failure 逐级退到探索）。

- **Hierarchical object navigation**：给 `move_to`/`find`，LLM 先把请求解析成结构化空间+语义查询（floor/room/object），HoloNavi 用 **hierarchical CLIP-feature matching** 在 HMSG 上快匹配候选 room/view/object——**先剪枝再做昂贵视觉推理**。
- **Online verification loop**：快匹配可能返回“视觉相似但错”的候选（小物体、房间名歧义、记忆过期）。HoloNavi 把候选 goal view 送 VLM 做视觉验证与慢推理，**遵循 FSR-VLN [39] 的 fast-to-slow 设计**。VLM 确认则算 object center 并派发导航；失败则旋转机器人采集周边 view、重跑检测+VLM 验证、并把失败候选报给 AgentOS 去更新记忆或换子目标。
- **Active spatial exploration**：当 HMSG 与在线 view 都无法定位目标，AgentOS 触发探索技能（而不是在缺状态下硬规划）。触发来自未解析的房间/物体引用、低置信场景图检索、度量图里的 frontier、或因记忆过期导致的验证失败。探索技能按 **expected information gain、语义相关性、traversability、safety** 给候选视点打分，选中后交 HoloNavi 执行；每步后把新观测区域、未解目标、通行失败报给 AgentOS，memory-update 层再融进几何记忆、语义实例与受影响的 HMSG 子图。

### 3.4 HoloBrain / 操作 VLA 后端

HoloBrain[15] 是 HoloAgent-0 用的 manipulation VLA。它在 skill 层实现 `pick/place/open/handover/push/fold`；每个调用结合 AgentOS 的任务意图、当前视觉观测、机器人 embodiment 先验、以及来自语义记忆的可选 object grounding，端到端策略推理输出可执行的 arm / gripper / dual-arm 动作。

关键是**它作为被监控后端上报执行证据而非只返回终态成功标志**：status 流含 object-not-found、object motion、grasp failure、unreachable poses、collision risk、low policy confidence、user-confirmation requirement——这些让 VLA 执行**可被 AgentOS runtime 使用**：失败变成重试/感知更新/澄清/重规划的显式证据。长程 mobile manipulation 里，HoloNavi 先把机器人带到任务相关区域/视点，HoloBrain 再从当前观测执行局部操作；若物体缺失/遮挡/不可达/需换 approach pose，上报的 status 可触发记忆检索、主动探索、导航重定位或新的操作子计划。

### 3.5 HoloMotion / 全身运动后端

HoloMotion[35] 提供 humanoid whole-body 运动后端，暴露 reference tracking、velocity control、posture adjustment、recovery 技能，并上报 progress、balance state、contact risk、velocity error、recovery availability。两种执行模式：

- **motion-tracking mode**：跟随 retargeted demonstration 做交互行为（waving / bowing / handshaking / dancing）；
- **velocity-tracking mode**：跟随指令线/角速度做移动（walking / turning / stopping / recovery）。

它通过同一 command/status 接口与其他技能族组合：把 HoloNavi 输出实现为稳定行走/转向，或为 HoloBrain 调整躯干姿态、到达稳定交互姿态、接触失败后恢复；AgentOS 用上报的 motion state 决定 continue / slow down / retry / trigger recovery / re-plan。

### 3.6 Cross-Embodiment Coordination / 靠共享接口做跨本体协作

技能执行接口顺带实现了轻量跨本体协作：异构机器人**共享记忆记录、typed skill call、status 事件**，AgentOS 可以把一个任务的不同部分分给不同身体，而不暴露它们的底层控制器。所有本体把 observation/detection/map update/skill outcome 写进**同一分层 3D 记忆**，每次更新都带上空间证据、时间上下文、上报本体的标签。于是 AgentOS 能复用一台机器人的发现来给另一台规划——例如**用移动底盘先填候选物体位置，再让 humanoid 去取**。AgentOS 按 capability / location / availability / safety state 把每个 task-level skill call 绑到某个本体，执行中共享 status 报告让它协调并发执行、避免工作区冲突、在机器人被阻塞时转移责任。**这套机制靠共享记忆+typed skill+可观测 status 组合机器人，而非单独的控制器。**

## 4. Memory Layer / 具身 agent 的空间与时间记忆

Memory Layer 提供空间+时间记忆。空间记忆把传感器流转成持久 3D 世界表示供 AgentOS 查询 grounding/localization/navigation/manipulation，含 geometry/topology/occupancy、robot pose/localization、open-vocabulary 3D semantic map、HMSG。时间记忆记录演变中的 goal & plan state、execution & recovery trace、outcome summary。对一个任务查询，记忆层返回候选地点、物体、位姿、任务历史、近期执行证据；执行后更新受影响的空间记录与时间轨迹。

### 4.1 Spatial Memory: 度量几何、拓扑与定位

Geometry memory 是具身技能的**度量基底**：维护坐标系、robot pose、稠密几何、traversability 证据、定位索引。为把下游 AgentOS 行为与传感器配置解耦，HoloAgent-0 暴露**统一几何接口**，可由 LiDAR 后端或 vision-only 后端填充。

- **LiDAR-based backend**：融合 LiDAR/IMU/camera 成度量点云或 mesh，遵循 FAST-LIVO [40] 式紧耦合 LiDAR-inertial-visual odometry，给 safety-critical 部署与受控评测提供 robust 参考图。
- **Vision-only backend**：用 **GeoFlow-SLAM++**（GeoFlow-SLAM [41] 的多相机扩展）从同步 RGB 建几何。给定标定相机 $\{I_{c_k}\}_{k=1}^{N},\ N\ge 3$，一个 3D 基础模型 $\Phi_\theta$ 从多视图预测稠密深度，再按已知外参反投影并对齐到机器人 body frame，**无需物理 RGB-D 深度硬件**。GeoFlow-SLAM++ 用多相机几何提升鲁棒：tracking 用 multi-view two-stage 光流保持特征连续、在 body frame 统一匹配做联合位姿估计；local mapping 联合优化视觉重投影/point-plane/IMU 约束（应对遮挡、低纹理、走廊场景）；relocalization 加载预建 map atlas、聚合各相机 BoW 向量成统一检索 query、经 cross-view 3D-to-2D 对应与联合 BA 精化候选关键帧。

### 4.2 Semantic Memory: 开放词表 3D 语义建图

> **Figure 4（语义建图框架，本地暂无抽图）。** caption：语义记忆把 open-vocabulary 2D 特征 lift 到几何记忆上，将观测关联到持久 3D instance，为 AgentOS 提供 language-queryable 的物体与区域证据。图里流水线：Real-time observation（RGB + Depth + Pose）→ Instance-level Mapping（Instance Voxel Map with SigLIP Feature / Instance Association / Mask Seg & SigLIP Feature Fusion / Obj-View Assignment）→ Scene Graph Construction（Floor & Region Segmentation / Region Classification / Scene Graph Update）→ Dynamic Scene Adaptation（Pose Alignment / Remove Obsolete Indices / Incremental Update）→ Hierarchical Scene Graph。

语义记忆把度量几何变成语言 grounded 的 3D 记忆。对 **SAM2** 产出的每个 2D mask，算三份 **SigLIP** 描述子：$d_0$ 全关键帧、$d_1$ 掩码段、$d_2$ 最小外接框，逐维加权平均融合：

$$
d = \sum_{i=0}^{2} w_i \odot d_i,\qquad w_i \in \mathbb{R}^{d}\tag{1}
$$

$\odot$ 是 Hadamard 积。融合描述子同时保住 global context、segment 外观、局部物体细节，供开放词表检索。

为维持持久物体身份，语义记忆把新 2D 观测关联到已有 3D instance：先把已有 3D instance $V_{t-1}$ 投影到当前相机视图得到投影 mask $\{\tilde m_j\}$，再计算当前 mask $\{m_k\}$ 与投影 mask 的 $\mathrm{IoU}(m_k,\tilde m_j)$，把匹配观测并进对应 3D instance；无匹配的高置信观测则**初始化新的持久 3D instance**（Figure 5 即此机制的可视化）。

### 4.3 HMSG / 结构化空间检索的分层多模态场景图

> **Figure 6（HMSG，本地暂无抽图）。** caption：HMSG 把记忆组织成 floor / room / view / object 四层，在 HoloAgent-0 里作为 AgentOS 的检索索引，支持 coarse-to-fine 目标 grounding、VLM 验证、从执行反馈做记忆更新。每层带语义+几何属性：Floor（Floor id、Floor-level CLIP / HeightRange、点云）、Room（Room Type、Room-level CLIP / 2D 边界、点云）、View（VLM Description、Image、CLIP / 6-DoF Camera Pose）、Obj（Category、Instance-level CLIP / 3D Bounding Box、点云）；层次边（Floor-Room / Room-View / Room-Object）+ 拓扑边（View-View / View-Object）。

HMSG 沿用 FSR-VLN [39] 的四层组织，作为**持久记忆索引**用于任务规划、目标 grounding、恢复。每层给不同检索粒度：floor/room 把查询收窄到粗区域；view 把机器人位姿连到视觉证据；object 给持久实例级目标。这避免了对原始几何或全部检测实例的穷举，同时保住下游 VLM 验证所需的视觉上下文。**view 层是设计要点**：传统 floor-room-object 层次靠直接特征匹配定位，image-based 拓扑图有视觉证据但缺 room/object 级 grounding——HMSG 两者都保留，view 节点存候选视角与到物体的可见性链接，让 AgentOS 先几何剪枝、再用一小批候选 view 交给 VLM 验证。闭环执行中，HMSG 在 skill dispatch 前被查询、在记忆更新后被刷新。

### 4.4 Temporal Memory / 任务状态、执行轨迹与经验

时间记忆补上“agent 想干什么、已发生什么、试过哪些恢复”。空间记忆答“物体/房间/位姿/可通行区在哪”，时间记忆答“哪个 goal active、哪些计划步未解、哪些技能成/败、什么证据该引导 AgentOS”。三块：

- **Goal & plan state**：存解析后的用户意图、active skill graph、pending sub-goals、分配的本体、preconditions、未解引用——让 runtime 在中断后恢复长程任务、把后续 skill call 绑到早先决策、跨多轮感知-动作不丢上下文。
- **Execution & recovery trace**：每个派发技能都追加 command 参数、检索上下文、status 事件、验证结果、失败模式、重试、用户澄清、memory-update 触发——给 AgentOS 决定 continue/retry/re-plan/ask/标记不可恢复的显式证据。
- **Outcome & experience summary**：任务段结束后存紧凑结果摘要（最终状态、成功/失败的恢复策略、被改动的物体或位置、面向用户的解释），把 raw 日志变成 queryable 经验而非只留底层 ROS2 trace。

### 4.5 Memory Update / 更新空间记录与时间轨迹

记忆层是**有状态、随执行变化**的表示，非一次性扫描。三类事件触发更新：与已有记忆冲突的新观测、移动/移除物体的技能结果、纠正当前状态的显式用户反馈。给新观测时，HoloAgent-0 先在几何记忆里重定位、再更新当前视图周边的局部度量图（移除/刷新与新深度-颜色证据冲突的点/体素、融合新几何）；语义记忆随后把新 mask 关联到已有 instance 或建新 instance；HMSG **只刷新受影响子图**（重算变动物体、其父 room、可见 view、局部空间关系），不重建整图。技能结果提供第二条更新路径：成功 pick 可把物体标记为被携带/离开支撑面、失败 `move_to` 可给路线附上阻塞/定位不确定证据、用户纠正可重命名物体或房间；并行地时间记忆追加对应 command/status/验证结果/恢复决策。

## 5. Experiments / 实验

### 5.1 Setup / 平台、指标、证据范围

评测把**可复现的量化测量**与**更宽的真机系统演示**分开。量化实验覆盖两个可在固定协议下测试的组件：**long-horizon navigation**（完整 AgentOS 导航循环 = 空间记忆 + 目标验证 + 执行反馈）与 **3D semantic mapping**（记忆层提供 language-queryable 空间 grounding）。定性实验展示同一记忆/技能/监控接口如何组合异构行为（humanoid motion、object search、cross-robot coordination、mobile manipulation）。

- **平台**（Figure 7）：三个真机——**Unitree G1 humanoid、R1 humanoid、wheeled dual-arm mobile manipulator**。humanoid 用 memory-layer sensing stack（RGB-D、音频交互设备、板载算力）；mobile manipulator 用轮式底盘 + 两个 6-DoF 臂带夹爪 + 高位 RGB-D 全局感知 + 板载算控。另有可复现仿真场景做导航调试与受控对比。**跨仿真与硬件用同一 command/status 接口**。
- **指标**：3D 语义建图报 mIoU / mAcc / frequency-weighted mIoU / frequency-weighted accuracy；长程导航报 SR（success rate）与 SPL（success weighted by path length），以及真机 Top-1 / Top-5 候选选择下的目标到达成功率。full-stack 具身行为**只报定性执行轨迹**——因为操作/全身/跨本体用异构硬件、尚未在一个可复现协议下标准化。

### 5.2 Long-Horizon Navigation / Agent 循环评测

评测“AgentOS 导航循环是否比独立导航后端更能长程到达目标”。两套设定：仿真用 MSGNav [44] 的 zero-shot ObjectNav（HM3D-ObjNav 协议，压 open-vocab goal grounding / 空间推理 / 路径效率、无硬件噪声）；真机用 FSR-VLN [39] 的 benchmark 在带 digital twin 的真实公寓评测（含定位/驱动/感知噪声）。

**Table 1（HM3D-ObjNav 仿真，遵循 MSGNav 协议）：**

| Method | SR (%) ↑ | SPL (%) ↑ |
| --- | ---: | ---: |
| SG-Nav | 49.6 | 25.5 |
| VLFM | 62.6 | 31.0 |
| DORAEMON | 66.5 | 20.6 |
| WMNav | 72.2 | 33.3 |
| MSGNav | 74.1 | 33.4 |
| FSR-VLN (fast-matching) | 72.1 | 36.9 |
| FSR-VLN (slow-reasoning) | 80.8 | 41.0 |
| **HoloAgent-Nav (w AgentOS loop)** | **82.6** | **42.8** |

**Table 2（真机导航，遵循 FSR-VLN benchmark；Top-1/Top-5 × 1.0/2.0/3.0m 阈值）：**

| Method | T1@1.0m | T1@2.0m | T1@3.0m | T5@1.0m | T5@2.0m | T5@3.0m |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OK-Robot | 60.92 | 60.92 | 60.92 | 63.22 | 63.22 | 63.22 |
| MobilityVLA | 34.48 | 59.77 | 75.86 | – | – | – |
| HOV-SG | 51.72 | 57.47 | 58.62 | 77.00 | 81.61 | 82.76 |
| FSR-VLN | 91.95 | 91.95 | 94.25 | 94.25 | 96.55 | 96.55 |
| **HoloAgent-Nav** | **97.70** | **97.70** | **97.70** | **98.90** | **98.90** | **98.90** |

**这两张表要分开读**：
1. **仿真里增益“看谁比”**：对最强公开 baseline MSGNav（74.1/33.4），HoloAgent-Nav 是 +8.5 SR / +9.4 SPL——很大；但**对它自己的层次记忆骨架 FSR-VLN (slow) 80.8/41.0，只 +1.8 / +1.8**。因为 FSR-VLN 才是隔离“AgentOS loop wrapper 到底加了多少”的对照，所以**仿真里 AgentOS 循环的净增益其实是温和的**（引用时别只拿 vs MSGNav 的大数）。
2. **真机里 wrapper 的价值更明显**：97.70 vs FSR-VLN 91.95（+5.75），且 Top-5 98.90。作者解释：真机才有定位/驱动/感知噪声，feedback-driven 恢复的价值在噪声下才显出来。
3. **一个诚实细节**：HoloAgent-Nav 在 1.0/2.0/3.0m 三个阈值上**分数完全相同（97.70）**——说明成功的 trial 已经停在严格 1.0m 阈值内，剩下的失败**不是“定位不够准”而是“需要更好的恢复”**（放宽阈值也救不回来）。SPL 42.8 也表明反馈驱动执行**保住了路径效率**而非靠绕路刷成功率。

### 5.3 Memory Evaluation / 语义建图与更新可视化

评测记忆层是否为下游规划提供有用的 language-grounded 3D 记忆，把感知/记忆从长程执行里隔离出来。在 **ScanNet 与 Replica** 上做 zero-shot 开放词表 3D 语义建图，用 mIoU/mAcc/f-mIoU/f-Acc（前两个测类别级语义质量，后两个加权强调导航/操作常查的 room-scale 常见实体）。

**Table 3（ScanNet / Replica zero-shot 语义建图；Online 列 ✓=在线, ✗=离线）：**

*(a) ScanNet*

| Method | Online | mIoU↑ | mAcc↑ | f-mIoU↑ | f-Acc↑ |
| --- | :---: | ---: | ---: | ---: | ---: |
| Open-Gaussian | ✗ | 08.64 | 17.86 | 23.71 | 26.44 |
| Lang-Splat | ✗ | 07.22 | 21.01 | 27.59 | 32.21 |
| Grasp-Splats | ✓ | 06.69 | 14.89 | 16.62 | 19.57 |
| Omni-Map | ✓ | 25.42 | **50.93** | **50.86** | 57.05 |
| HOV-SG | ✗ | 20.76 | 41.50 | 38.34 | 45.50 |
| Concept-Fusion | ✓ | 08.50 | 31.81 | 30.05 | 36.64 |
| Concept-Graph | ✓ | 16.29 | 34.07 | 33.29 | 41.60 |
| Open-Fusion | ✓ | 18.02 | 44.31 | 43.82 | 51.09 |
| **HoloAgent-Memory** | ✓ | **31.58** | 45.54 | 47.43 | **61.58** |

*(b) Replica*

| Method | Online | mIoU↑ | mAcc↑ | f-mIoU↑ | f-Acc↑ |
| --- | :---: | ---: | ---: | ---: | ---: |
| Open-Gaussian | ✗ | 06.82 | 16.66 | 15.41 | 18.08 |
| Lang-Splat | ✗ | 10.00 | 22.93 | 39.69 | 44.16 |
| Grasp-Splats | ✓ | 10.42 | 23.79 | 42.67 | 52.39 |
| Omni-Map | ✓ | 29.06 | **44.54** | **64.42** | **72.22** |
| HOV-SG | ✗ | 23.79 | 39.59 | 48.86 | 55.15 |
| Concept-Fusion | ✓ | 04.75 | 19.29 | 25.30 | 28.99 |
| Concept-Graph | ✓ | 16.46 | 31.51 | 35.69 | 42.44 |
| Open-Fusion | ✓ | 16.37 | 35.15 | 51.65 | 60.37 |
| **HoloAgent-Memory** | ✓ | **29.93** | 43.60 | 57.00 | 65.39 |

**证明什么 / 边界**：
- **ScanNet 上强**：HoloAgent-Memory mIoU 31.58、f-Acc 61.58 都是全表最佳，且**保持在线运行**（很多离线 splat 方法反而弱）。
- **Replica 上只是有竞争力、非全面最优**：mIoU 29.93 仍是全表最佳（略高于在线 Omni-Map 的 29.06）；但 **mAcc / f-mIoU / f-Acc 均输给 Omni-Map**（43.60 vs 44.54、57.00 vs 64.42、65.39 vs 72.22）。作者诚实承认：**Replica 上 frequency-weighted 指标的差距**说明大面积实体与多视图特征聚合仍待改进。
- **更新可视化**：Figure 5（instance association，把新 2D 观测并进持久 3D 物体）与 Figure 8（dynamic update，只刷新变动区域不重建全图）说明——标量分割指标看不出的“物体身份在重复观测/环境变化下是否稳定”，靠这两个定性 case 补上。

### 5.4 Qualitative Closed-Loop Robot Execution / 定性闭环执行

超出标量导航/建图指标，作者可视化了行使完整 runtime 的真机执行（Figure 2 的四类：humanoid motion、object search、cross-robot coordination、mobile manipulation）。作者**明确声明这不是标准化 benchmark**，只是展示 AgentOS 如何通过共享任务状态、status 反馈、memory-grounded 规划组合异构技能，把叠衣服这类长程任务拆成 navigation/perception/placement/manipulation 步骤。**对 manipulation / whole-body / cross-embodiment 的严格 end-to-end benchmark 仍是 future work。**

## 6. Related Work / 三条线的定位

- **From Digital to Embodied Agent Frameworks**：数字 LLM agent 收敛到 reason–tool–feedback–memory–revise 循环，在软件里好用是因为工具有 clean I/O、观测是文本/代码/网页/API 返回。物理具身削弱这些假设，因此需要数字框架少有的接口：持久 metric-semantic 记忆、对异构机器人技能的 typed 访问、runtime 监控。现有 ROS2 中间件与 LLM-enabled 机器人 runtime 提供了部分拼图 [53–57]，HoloAgent-0 沿此转型但**把框架中心放在闭环物理执行接口**。
- **Instruction-Conditioned Robot Policies**：TAMP [6,7]、language-conditioned 系统 [8,9,58]、以及 VLA/VA/world-action 模型 [10–13,16–19,36–38,59] 提供了强行为策略，但多绑定特定动作表示/平台/任务族，且本身不提供持久记忆、长程推理、runtime 恢复。**HoloAgent-0 把它们当 embodied skill backend**：它们执行关键物理行为，AgentOS 调度、监控、恢复。
- **3D Spatial Memory & Scene Understanding**：从经典 3D scene graph [60] 到 open-vocabulary mapping / 3D scene-graph [42,43,51,61–63]、再到注入空间先验的 3D-aware 具身模型 [14,18,25,26,64]，以及作为代表应用的 language-guided navigation [39,65,66]。HoloAgent-0 把 3D 表示当成**可操作的记忆层**：几何支持定位/通行、语义支持语言 grounding、场景图结构支持物体/房间级推理。

## 7-8. Conclusion & Future Work / 结论与三个方向

**结论**：HoloAgent-0 是一个统一具身 agent 框架，用于缩小数字 LLM agent 与真实机器人之间的 embodiment gap。三层耦合（AgentOS 做规划/调度/监控/重规划、Memory Layer 做持久空间 grounding + 执行历史、Skill Layer 做结构化可执行能力）。语义建图与 HoloAgent-Nav 导航栈的量化实验显示记忆与导航组件提供了有竞争力的空间 grounding 与目标到达；真机演示进一步显示同一 AgentOS runtime 能组合 humanoid motion / object search / cross-robot coordination / mobile manipulation。**标准化的异构技能 end-to-end benchmark 仍是重要的下一步。**

**Future Work（三方向）**：
1. **Instruction-aligned robot foundation models**：现有机器人模型仍难应对跨导航/操作/全身/交互的广义自然语言指令，逼得 AgentOS 组合接口与失败模式各异的专门后端；未来模型应暴露更 language-aligned、可组合的动作空间。
2. **Broader embodiment support & full-stack humanoid skills**：共享技能接口让加新本体成为可能，但每个本体带来不同的传感/驱动/安全/恢复约束；humanoid 尤其苛刻（mobility/manipulation/balance/interaction 必须作为一个耦合 skill stack）。
3. **Code generation for robot evolution**：让 coding agent 从任务意图、机器人 API、环境上下文直接生成机器人动作与执行策略；因真机执行生成动作有成本与风险，作者将引入基于 **EmbodiedGen [67]** 的 digital-twin sandbox，在部署前快速验证生成策略是否满足任务目标、遵守本体约束、能从受控环境变化中恢复。

## 图表索引与讲解

> 本地暂无抽图，以下据全文 Figure/Table caption 文字说明。需要看图时补跑 `python setting/scripts/extract_paper_images.py`。

| 图 / 表 | 读图重点（证明什么） | 关联问题 |
| --- | --- | --- |
| Figure 1 | 三层（AgentOS/Skill/Memory）+ Monitoring 经 ROS2 command/status 总线连成 Agentic Execution Loop：UserPrompt→Plan→Gather Context→Execute→Monitor&Verify→Update/Re-plan/Retry。 | 数字 agent 循环如何接到物理机器人；“换模型不换闭环”在哪落地。 |
| Figure 2 | 四个真实闭环案例（Prompt Motion / Active Object Search / Cross-Robot / 叠衣服长程 mobile manipulation）。 | 同一 runtime 能否组合异构技能（这是“unified”的定性证据）。 |
| Figure 3 | HoloNavi 三子循环：hierarchical CLIP 快匹配 → VLM 在线验证 → frontier 探索（First/Second Failure 逐级退到探索）。 | fast-to-slow 导航如何兼顾效率与纠错；记忆过期时怎么恢复。 |
| Figure 4 | 语义建图流水线：观测→instance-level mapping（SigLIP 融合 + instance association）→场景图构建→dynamic adaptation→HMSG。 | 2D 开放词表特征如何 lift 成持久 3D 语义记忆。 |
| Figure 5 | instance association：把已有 3D instance 投影到当前视图、与新 2D mask IoU 匹配以维持物体身份。 | 物体身份在重复观测下是否稳定（标量 mIoU 看不出）。 |
| Figure 6 | HMSG 四层（floor/room/view/object）+ 语义/几何属性 + 层次/拓扑边；view 层桥接几何与视觉。 | 为什么要分层索引而非穷举几何/全部实例。 |
| Figure 7 | 三个真机平台（G1、R1 humanoid + wheeled dual-arm）。 | “真实部署”是否真的跨异构本体。 |
| Figure 8 | dynamic memory update：重定位→只刷新变动几何/语义与受影响场景图节点，不重建整图（TableA/TableB 移动前后对比）。 | 环境变化后记忆如何增量更新。 |
| Table 1 | HM3D-ObjNav 仿真 SR/SPL；HoloAgent-Nav 82.6/42.8 最佳，但对自家 FSR-VLN slow 仅 +1.8/+1.8。 | AgentOS loop wrapper 在无噪声仿真里净增益多大。 |
| Table 2 | 真机导航 97.70/98.90，三阈值同分；比 FSR-VLN +5.75。 | 反馈驱动恢复在真实噪声下价值几何；剩余失败是定位还是恢复问题。 |
| Table 3 | ScanNet 上 mIoU/f-Acc 全表最佳且在线；Replica 上 mIoU 最佳但 mAcc/f-指标输 Omni-Map。 | 记忆层的语义 grounding 质量与边界（大面积实体聚合）。 |

## 和你的论文库中其他条目的关系

- 对 [[@li2026zr0]]（用 Dense Embodied Chain-of-Thought 监督训 VLA）：**互补的两个层次**。zr0 关心“怎么把一个 VLA 训得更会推理”；HoloAgent-0 把 VLA（HoloBrain[15]）当成被 AgentOS 调度/监控/恢复的 **skill backend**，关心“VLA 失败时系统怎么办”。可纵向串读：zr0 提升单技能能力，HoloAgent-0 提供把该技能接进长程闭环的接口（status 流里的 grasp failure / low confidence 正是 zr0 类模型需要暴露的信号）。
- 对 [[@wu2026tactile-wam]]（触觉世界-动作模型）：**同一“闭环纠偏”主题的不同粒度**。Tactile-WAM 在**指端接触级**用预测的 Δcontact 引导动作去噪；HoloAgent-0 在 **agent 级**用 skill status（object motion / grasp failure / collision risk）触发重试/重规划。前者是“毫秒级接触闭环”，后者是“任务级技能闭环”——可作“从高层规划到指端接触”的纵向对照，也提示 HoloBrain 若换成触觉感知后端，其 status 流会更细。
- 对 [[@wang2026wvm]]（World Value Model）：**都在问“agent 怎么知道自己成没成”**。WVM 用世界模型给操作打 value 分；HoloAgent-0 的 **Monitoring & Verification 层 + Task Verifier** 走的是符号/感知式 postcondition 验证（`verify` 技能 + open-vocab 检测）。可对照“成功判定用 learned value 还是 typed status + 显式验证”。
- 对世界模型一线 [[@wang2026orca]] [[@zhang2026qwen-robotworld]] [[@gao2026fast-leworldmodel]] [[@gigaworld2026roadmap]]：这些学 world latent / 未来预测 / 视频生成；HoloAgent-0 更像**执行层 agent OS**，把 VA/world-action 模型当 skill backend。特别是 [[@gigaworld2026roadmap]] 主打“world model 做 policy evaluation”，与 HoloAgent-0 **future work 里用 EmbodiedGen[67] 数字孪生 sandbox 在部署前验证生成动作**的构想直接呼应——一个提供评估用世界，一个提供需要被评估的执行栈。
- 对进度/奖励建模一线 [[@liu2026steam]]（自监督时间集成 advantage）、[[@yu2026warp-rm]]（相对进度奖励模型做数据筛选）：HoloAgent-0 的 temporal memory 显式追踪“partial progress / execution trace”，skill status 也报 `progress`——但它是**符号化 status 而非 learned progress reward**。可对照“进度信号用手工 status 还是学出来的 progress/advantage”，STEAM/WARP-RM 的进度模型也许能替换或增强 HoloAgent-0 现在偏规则的验证层。
- 对 [[@kang2026x-tokenizer]]（VLA 预训练的多模态动作 tokenizer）：处在比 HoloAgent-0 更底层的“动作表示”层。HoloAgent-0 的 typed skill call 是**符号动作空间**，X-Tokenizer 是**连续动作的离散化表示**——两者是“符号技能接口 vs 底层动作 token”的上下游关系，HoloBrain 这类后端内部可能就吃 tokenizer 式表示。
- 论文自身依赖但**均不在当前库**（如需可另行入库）：**FSR-VLN [39]**（HMSG 与 fast-to-slow 验证的来源，也是真机导航 benchmark）、**MSGNav [44]**（仿真协议与最强公开 baseline）、**GeoFlow-SLAM [41] / FAST-LIVO [40]**（几何后端）、**HoloBrain [15] / HoloMotion [35] / EmbodiedGen [67]**（同组自研组件）、以及 SAM2 / SigLIP / π0.5 / π0.7 / OK-Robot / MobilityVLA / HOV-SG / Omni-Map 等。

## 可追问点

1. **“统一框架”的量化范围**：只有 navigation + semantic mapping 被量化，manipulation/whole-body/cross-embodiment 全是定性 demo。那么“unified embodied agent framework”的核心闭环（skill-graph 规划 + 失败恢复）在**操作/全身任务**上到底成功率多少？现在无法从数字判断。
2. **AgentOS wrapper 的净增益**：仿真里对 FSR-VLN(slow) 只 +1.8 SR/SPL，真机 +5.75。这说明 AgentOS 的价值主要来自“真实噪声下的反馈恢复”。有没有把恢复次数/重规划频率/因验证救回的失败数**单独消融**出来，证明增益确实来自闭环而非更好的记忆？
3. **记忆与策略的边界**：HMSG、几何、语义建图大量复用 FSR-VLN/GeoFlow-SLAM++/FAST-LIVO，HoloBrain/HoloMotion 是同组既有模型。那么 HoloAgent-0 **自身的算法新增**是接口设计（typed skill + status schema）与 orchestration——这类系统贡献如何量化“比松耦合调用强在哪”？
4. **Replica 上 frequency-weighted 指标输给 Omni-Map**：作者归因于大面积实体与多视图特征聚合。这会不会影响导航——毕竟房间/墙面这类大实体正是 room-level grounding 依赖的？语义建图弱项是否传导到 HMSG 的 room 层检索？
5. **真机导航三阈值同分（97.70）**：意味失败都是“需要更好恢复”的硬失败。这些失败的 failure mode 分布是什么（定位丢失 / 验证误判 / 探索耗尽）？现在只给了总分。
6. **安全约束**：introduction 反复强调物理执行“constrained by safety”，探索技能也把 safety 列为打分项，但正文几乎没给安全机制的具体实现或触发案例。真机上 collision risk / contact risk 的 status 是如何被 AgentOS 消费成“停/退让”的？
7. **EmbodiedGen 数字孪生 sandbox（future work）**：用生成式 3D 世界在部署前验证 coding-agent 生成的动作——这与 [[@gigaworld2026roadmap]] 的“world model for policy evaluation”是同一诉求。生成动作的 sim-to-real gap 谁来兜底？

## 我的阅读笔记

这篇的定位要非常清楚：**它是一篇系统/框架论文，不是算法论文**。全文只有一个真正的公式（Eq.1 SigLIP 三描述子融合），大量内容在描述接口 schema、数据流、四层分工。它真正的贡献是**把异构机器人技能装进一个“可观测、可验证、可恢复”的执行操作系统**——最有价值的设计是 **typed skill call 的 status schema**（progress/success/failure mode/confidence/latency/recoverability）和“**让失败变成 planning evidence**”这条原则：它把“机器人技能不是软件 API”这个痛点，落成了一个具体的 runtime status 契约。这一点比任何单个模块都更像本文的“主张”。

但要清醒看边界。第一，**“unified”目前是半量化的**：导航（Table 1/2）和建图（Table 3）有硬数字，操作/全身/跨本体只有 Figure 2 的定性演示，作者自己也承认没有 end-to-end benchmark。所以引用时“统一具身 agent 框架”应加限定语。第二，**AgentOS 的净增益要看对谁比**：对最强公开 baseline MSGNav 的 +8.5/+9.4 很唬人，但对它自己的记忆骨架 FSR-VLN(slow) 只 +1.8/+1.8——仿真里 wrapper 的贡献其实温和，真机 +5.75 才是它的主场（因为反馈恢复在噪声下才值钱）。第三，**大量组件是复用**（HMSG←FSR-VLN、几何←GeoFlow-SLAM++/FAST-LIVO、HoloBrain/HoloMotion/EmbodiedGen 同组自研），HoloAgent-0 的原创性集中在集成与接口，而非新的感知/策略算法。

我会把它当作**“具身 agent 执行层/操作系统”**这条线的入口，和三类库内工作交叉读：与 [[@li2026zr0]]（怎么训一个会推理的 VLA）读“skill backend 能力 vs 编排它的系统”；与 [[@wu2026tactile-wam]] 读“接触级闭环 vs 任务级闭环”的粒度差；与 [[@wang2026wvm]] 读“成功判定用 learned value 还是 typed status + 显式验证”。它最打动我的一句隐含论点是：**具身智能的瓶颈可能不只在模型能力，而在“没有一个让物理技能可组合可验证可恢复的执行抽象”**——这和世界模型一线（[[@wang2026orca]] 等追求更强的未来预测）形成了一个健康的张力：一边加强“会想”，一边加强“会跑闭环”。
