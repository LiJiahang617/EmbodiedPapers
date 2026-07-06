---
tags:
  - bilingual-reading
paper: "[[@xiao2026enpire]]"
source_pdf: "[[papers/pdfs/ENPIRE.pdf]]"
images: "papers/images/xiao2026enpire/"
image_index: "[[papers/images/xiao2026enpire/index.md]]"
created: 2026-06-25
---

# ENPIRE: Agentic Robot Policy Self-Improvement in the Real World

paper:: [[@xiao2026enpire]]
pdf:: [[papers/pdfs/ENPIRE.pdf]]
images:: [[papers/images/xiao2026enpire/index.md]]

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| ENPIRE | EN-PI-R-E 机器人自动研究框架 | 用 coding agents 管理真实机器人策略自改进闭环。 |
| physical autoresearch | 物理自动研究 | 让 agent 在真实硬件上提出假设、执行实验、读取反馈、改进算法。 |
| coding agent | 编程智能体 | Codex / Claude Code / Kimi Code 这类能读写代码、跑命令和分析日志的 agent。 |
| Environment module, EN | 环境模块 | 自动 reset、自动 verification/reward、安全约束和 Gym APIs。 |
| Policy Improvement, PI | 策略改进模块 | agent 提出算法假设、改训练代码、调参数、结合 BC/RL/heuristics。 |
| Rollout module, R | 试验执行模块 | 在一个或多个真实机器人上执行 policy，收集轨迹、视频、reward 和日志。 |
| Evolution module, E | 演化模块 | 多 agent 通过 Git 分支异步探索、分享、合并有效 recipe。 |
| automated verification | 自动验证 | 用视觉、状态、力等传感器自动判定成功/失败并给 reward。 |
| automated reset | 自动复位 | 任务结束后用工具 API 把真实场景恢复到可继续试验的状态。 |
| Mean Robot Utilization, MRU | 平均机器人利用率 | 研究墙钟时间中机器人真正执行实验的比例。 |
| Mean Token Utilization, MTU | 平均 token 利用率 | agent 团队每单位时间消耗的 token，用于衡量 autoresearch 成本。 |
| token-to-success | 达成成功所需 token | 成功策略所需 token 预算，衡量多 agent 扩展是否划算。 |
| YAM robot | Yet Another Manipulator | 本文使用的双臂机器人平台，每站两只 6-DoF 机械臂。 |
| code-as-policy | 代码即策略 | 用程序组合感知、规划和控制 API，而非只端到端输出动作。 |

## 论文主线

这篇论文的出发点很现实：真实机器人策略学习不是只有“训练一个模型”这么简单。每次实验都要 reset scene、部署 policy、检查是否成功、保存日志、分析失败、修改代码、再跑下一轮。过去这些环节大量依赖人。ENPIRE 想把这套 real-world policy improvement loop 变成 coding agent 可以自动管理的闭环。

![[papers/images/xiao2026enpire/page1_full.png|700]]

**Figure 1 / Robot fleet。** ENPIRE 的真实硬件基础是 8 个 bimanual YAM robot stations。每个 station 都有自己的机器人、相机、计算机和 coding agent，因此实验不只是单机器人 demo，而是面向 fleet-scale physical autoresearch。

![[papers/images/xiao2026enpire/page2_full.png|700]]

**Figure 2 / ENPIRE 总览。** 左侧是 Environment construction：agent 写 `env.py`，实现 reset、reward、observation、step。右侧是 Policy Improvement：agent 读文献、提出算法、跑 rollouts、总结实验。底部是 hill-climb timeline 和真实任务：GPU insertion、Pin insertion、Push-T、Zip tie cutting。

论文名字 ENPIRE 可以拆成四个模块：

- **EN: Environment**，构造自动 reset / verification / safety / Gym API；
- **PI: Policy Improvement**，自动改训练方法和策略代码；
- **R: Rollout**，执行真实机器人试验并收集反馈；
- **E: Evolution**，多个 agent-robot workers 通过 Git 分享、选择和合并有效想法。

核心判断是：要让机器人策略自改进，缺的不是一个单独算法，而是一个 repeatable feedback loop（可重复反馈循环）：reset the scene、execute a policy、verify the outcome、refine the next iteration。ENPIRE 把这个循环工程化后，coding agents 才能在真实硬件上做 autonomous research。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| formalize physical autoresearch for dexterous manipulation。 | 两阶段 EN + PIRE 框架。 | 主文 Sec. 1-2；真实任务和 fleet 实验。 | 概念贡献强，给机器人自动研究一个清晰问题定义。 |
| coding agents 可以构造真实机器人环境接口。 | safety constraints、automated verification、automated reset、Gym APIs。 | Zip-tie reward、pin reward、GPU reset pipeline、附录 A。 | 工程证据强，但仍需要一次性人类反馈。 |
| agents 可以在真实机器人上自动改进 policy。 | PI module 改 BC/RL/heuristic/code policy 训练代码。 | Push-T、Pin insertion、GPU insertion、Zip tie cutting。 | 很有价值，但具体成功率曲线主要在图中，部分数值需读图。 |
| 多机器人/多 agent 能加速 autoresearch。 | 每个 robot 一个 agent，通过 Git 异步分支探索。 | Push-T 5h -> 2h；Pin insertion >1.5h -> ~40min。 | 墙钟时间收益清楚，但 token 成本升高。 |
| 需要新资源指标衡量物理自动研究。 | MRU、MTU、token-to-success。 | Fig. 7、Fig. 13。 | 重要，因为真实机器人 trial 的瓶颈不是单纯算力。 |
| code-based policies 可以增强 VLA。 | RoboCasa 中用 detection + motion planning + GR00T。 | Fig. 6；真实 zip-tie cutting 策略迁移。 | 思路有力，说明 VLA 和工具调用可互补。 |

## 摘要与核心贡献

摘要提出一个核心瓶颈：dexterous robotic manipulation 依赖 human supervision 和 algorithmic engineering。Coding agents 已经能自动写代码、跑数字实验，但在真实机器人里缺少一个稳定抽象：机器人世界需要 reset、verify、rollout，还要处理硬件安全和实验成本。

ENPIRE 的回答是 harness framework。它把真实机器人学习变成一个 controllable optimization procedure，让 agent 可以在自动环境反馈上 hill-climb policy success rate。论文声称 frontier coding agents 可以自主把策略推到约 99% success rate，并能使用多种 PI regimes：heuristic learning、tool calling、behavior cloning、offline/online reinforcement learning。

贡献可以压成三点。第一，提出 physical autoresearch 这个问题和两阶段流程：先 human-guided 构造环境反馈，再 fully autonomous 做 policy improvement。第二，实现 ENPIRE，让 agent 能写工具、构造 reward/reset、跑真实机器人、改算法。第三，展示多任务真实机器人和 fleet scaling，并提出 MRU / MTU 资源利用指标。

## 1. Introduction / 为什么真实机器人需要 physical autoresearch

真实机器人策略学习慢，不只是因为 policy 算法不够强，而是每轮试验都需要人 babysit：数据采集、评估、复位、看日志、调算法、重新部署。机器人越多，任务越复杂，人力越成为瓶颈。

数字环境里的 autoresearch 很成功，因为实验便宜：agent 写代码，跑 benchmark，看分数，改代码。但真实机器人不同：

- policy deployment 可能损坏硬件；
- scene reset 很难自动化；
- reward / success verification 需要视觉、力和状态判断；
- trial 速度慢，机器人 access 是稀缺资源；
- 多机器人并行时还要决定哪些假设值得继续。

ENPIRE 因此把问题分成两阶段：

1. **Environment construction from human feedback**：用一次性人类反馈帮助 agent 构造安全、reset、verification API；
2. **Automatic policy improvement from real-world feedback**：之后让 agent 独立探索算法和训练 recipe，通过真实 reward 改进策略。

## 2. Method / ENPIRE 方法

### 2.1 Stage One: Environment Construction from Human Feedback

EN 阶段的目标是把物理世界封装成 agent-friendly environment。它至少包含三类东西。

第一是 **hard safety constraints（硬安全约束）**。机器人配置空间和运动行为被限制在安全区域内，一旦越界就终止 episode 并自动 reset。这既保护硬件，也给学习系统提供 failure / truncation 信号。

第二是 **automated verification（自动验证）**。真实机器人需要实时 reward 或 success detector。ENPIRE 让 coding agent 用少量 success / failure demonstrations 构造 reward function。例如：

- pin insertion reward 融合 visual alignment、EEF height 和 force estimates；
- zip-tie reward 用两路相机、cropping、segmentation 和 geometric test 判断扎带是否穿过扎带头；
- zip-tie reward 被优化到 150 ms 以内，接近人类视觉反应量级。

第三是 **automated reset（自动复位）**。任务完成或失败后，agent 用 procedural tool calls 恢复环境。对于 contact-rich tasks，reset 不一定回到最原始状态，而是回到最关键精细阶段之前，例如 pin hovering、GPU seating 前、grasping scissors 前。这样能把 trial budget 集中在真正难的瓶颈阶段。

![[papers/images/xiao2026enpire/page4_full.png|700]]

**Figure 3 / Coding agents benchmark。** 这页把 Push-T heuristic learning、Pin insertion gradient-based learning，以及 1/4/8 agent scaling 放在一起，说明 ENPIRE 支持不同 agent 和不同 policy improvement regime。

### 2.2 Stage Two: Automated Policy Improvement from Real-World Feedback

进入 PIRE 阶段后，agent 的目标是 maximize success rate。它有写训练代码的权限，可以：

- literature review；
- propose algorithm variant；
- 修改 BC / RL / heuristic / code-as-policy；
- 调 batch size、actor-critic update rate、BC regularization weight；
- 调数据 sampler、参数 sweep；
- 跑 rollouts；
- 总结实验结果；
- 根据日志和视频定位 failure mode。

主文用 pin insertion 举例：插针孔径只有 4 mm，需要高精度接触。Agent 测试了 BC、iterative BC、online rollout data aggregation、offline / online / offline-to-online RL with BC regularization 等方法。论文中的 hill-climb timeline 显示关键改进包括 Online RL mix demo、BC regularization、batch size tuning、controller compensation 等。

### 2.3 Multi-Agent Scaling / 多机器人扩展

ENPIRE 的 fleet scaling 是 decentralized collaboration。每个 robot 对应一个 coding agent，所有 agent 从相同 baseline codebase 分支，异步测试不同假设，通过 Git 分享结果：

- 成功的 branch 可以被其他 agent cherry-pick；
- agent 可以 copy / merge peer 的 training recipe；
- Git history 成为各 station 尝试过什么的 single source of truth。

这种设计很朴素但实际：真实机器人没有中心化同步控制也能并行探索，每个 station 可以独立失败和恢复。

资源指标：

- **MRU**：research wall-clock time 中 robot actively executing experiment 的比例；
- **GPU utilization**：GPU actively in use 的比例；
- **MTU**：fleet 平均 token consumption；
- **token-to-success**：达成成功策略所需 token，总结 token 效率。

## 3. Experiments / 实验

### 3.1 Tasks and Agents

真实任务包括：

- **Push-T**：非抓取推动 T 形块到目标区域；
- **Pin insertion**：把 pin 插入 4 mm 直径孔；
- **GPU insertion**：把 GPU chips 插进 motherboard thin sockets；
- **Zip tie cutting**：抓住并闭合 scissors 剪断 zip tie tail。

机器人平台是 bimanual 6-DoF YAM robot。论文评测的 coding agents 包括：

- Codex with GPT-5.5 xhigh；
- Claude Code with Opus 4.7 High；
- Kimi Code with Kimi K2.6 thinking。

成功定义不是普通 i.i.d. best-of-N，而是在一个 rollout 中允许固定次数 retries（这里为 8）。因为每次 retry 都是在看到上一次失败后继续尝试，所以这个 metric 同时衡量 precision 和 in-context recovery。

### 3.2 Heuristic Learning / Push-T

Push-T 用来测试最简单的 policy improvement：coding agent 合成 perception + control tool calls。结果显示所有 coding agents 都能在 simulation 中解决 Push-T，Claude Code 和 Codex 约 2 小时达到 95% success，Kimi 大约需要两倍时间。

但真实 Push-T 更难：接触摩擦、物体运动、机器人 dynamics 都有随机性和时间变化，导致部分 agents 失败。这个对比说明，simulation autoresearch 不能直接代表 physical autoresearch；真实世界需要更鲁棒的学习方法和更多 parallel hypothesis testing。

### 3.3 Gradient-Based Policy Improvement / Pin Insertion

Pin insertion 是 ENPIRE 的核心真实学习任务之一。Agent 需要达到 50 consecutive successes。它尝试的算法包括：

- behavior cloning；
- iterative BC + online rollout aggregation；
- online RL；
- offline RL；
- offline-to-online RL；
- BC regularization；
- batch size / update rate / BC-term tuning。

主文指出，在 pin insertion 中，策略收敛到 100% 的速度快于一个 frontier human-in-the-loop method。附录 Figure 12 进一步显示 idea tree：少数高影响 idea 贡献主要进步，例如 BC regularization 带来 +10.8 pp，后续 batch-size tuning +0.9 pp，controller compensation +1.3 pp。

### 3.4 Scaling on Robot Fleet

![[papers/images/xiao2026enpire/page8_full.png|700]]

**Figure 6-7 / RoboCasa 与资源利用。** Figure 6 显示 simulation 中 ENPIRE 增强 GR00T / CaP-X；Figure 7 显示 MRU、GPU utilization、MTU、token-to-success 与 time-to-success 的 scaling trade-off。

论文给出两个直观 scaling 结论：

- Push-T：从 1 agent 扩到 8 agents，达到 1.0 normalized score 的时间约从 5 小时降到 2 小时；
- Pin insertion：从 1 agent 扩到 8 agents，达到 near-perfect success 的时间从超过 1.5 小时降到约 40 分钟。

但代价也明显：fleet size 变大后，机器人利用率下降，token 消耗超线性增长。8-agent 更快，但 token-to-success 更贵。

### 3.5 Agentic Continue Learning / 经验迁移

ENPIRE 还测试了把一个任务中学到的 autoresearch experience 转移到新任务。Pin insertion 结束后，agent 被要求总结训练 recipe 的演化；在 GPU insertion 新任务中，把这份 summary 加到指令里，可以帮助 coding agents 更快达到高成功率。注意这里不是给 raw trajectories 或 checkpoints，而是只给 markdown summary，因此迁移发生在 agent knowledge / recipe 层。

### 3.6 Code-Based Policies + VLA

ENPIRE 不只训练端到端 policy，也能把 VLA 和 procedural tools 结合。在 RoboCasa365 simulator 中，agent 发现用 detection + motion planning 先移动到 object hover pose，再抓取，可以提升 GR00T VLA 的成功率。这个策略后来迁移到真实世界的 scissors / zip-tie cutting：先 hover over scissors，再 grasp，再 cut zip tie。

这个结果很值得注意：VLA 不一定要完全端到端解决所有操作；coding agent 可以自动发现“VLA + 工具调用 + 运动规划”的 hybrid policy。

## 4. Appendix Details / 系统细节

### 4.1 Automated Reset and Reward

![[papers/images/xiao2026enpire/page17_full.png|700]]

附录 A 展示了具体 reset / reward 构造。GPU insertion reset pipeline 用 SAM3 做 object localization，用 RANSAC 和 OBB 做 3D bounding box，用 gripper torque 验证抓取，再用 cuRobo 做 collision-free handover。Pin insertion reward 则融合视觉对齐、插入深度和接触力。

这些细节说明 ENPIRE 不是“LLM 直接控制机器人”，而是 agent 写程序组合一组强工具 API。工具质量直接决定 autoresearch 上限。

### 4.2 Robot System

每个 station 包含：

| Component | Specification |
| --- | --- |
| GPU | 1x NVIDIA RTX 5090, 32 GB |
| CPU | Intel Core Ultra 9 285K, 24 cores |
| RAM | 128 GB |
| OS | Ubuntu 22.04 LTS |
| GPU stack | NVIDIA driver 595.58.03, CUDA 13.2 |

机器人系统：

- 每站两只 YAM 6-DoF arms；
- 每只手有 1-DoF parallel-jaw gripper；
- 机械臂 joints 用 PD control + gravity compensation；
- gripper 用 torque-limiting compliant grasp；
- policy 30 Hz，低层 joint controllers 100 Hz；
- 摄像头主要是 top-down RealSense D405 + 两个 wrist RealSense D405，GPU insertion 另加 side RealSense D435i。

### 4.3 Agent Sandbox and APIs

每个 station 的 agent 在一个 autoresearch repo sandbox 里工作，拥有较高自治权限，能执行命令、读本轮 robot data、改代码和调用 FastAPI endpoints。常用端点包括：

- `/start`：开始真实硬件 rollout；
- `/restart`：分配新的 rollout buffer directory；
- `/home`：让机器人回 home；
- Push-T 另有 `/avoid` 和 `/resume` 处理 top-camera occlusion。

这些设计保证不同 hypothesis / experiment 的数据不会混在一起，agent 可以把 outcome 归因到具体代码变更。

### 4.4 RoboCasa Simulation Interface

RoboCasa365 的 API 包括 robot state、gripper、RGB-D camera、cuRobo/Pyroki motion、detection、segmentation、AnyGrasp、VLM query、planner world update、GOAT navigation 等。为了公平，canonical evaluation 禁用 oracle target、reset_env、get_task_info 等 privileged APIs。比较 GR00T 时，任务、seed、layout、style、camera 和 success predicate 都一致。

附录还指出一个重要瓶颈：SAM3 对小物体或歧义物体会 mask 错。提高 top-camera 分辨率和让 agent 重写 object prompt 都能改善 detection。Figure 16 显示原始 prompt 在 256x256 时 10/20，较高分辨率约 14/20；candidate prompts 可到 17/20。

## 5. Limitations / 局限

论文主文给出的两个局限都很关键。

第一，robot and compute resources are underutilized。Agent 在读日志、写代码、debug 或等待 LLM backbone 时，机器人并没有执行实验。Fleet 变大后，agent 还要花时间总结 peer branches，MRU 反而下降。

第二，token cost grows super-linearly with fleet size。到 8 agents 时，token 消耗增长超过理想线性趋势。换句话说，多机器人 fleet 能更快成功，但 token efficiency 变差。

我会再补充三个阅读层面的限制：

- EN 阶段还需要人类提供 feedback 和 success/failure examples，自动化不是从零开始；
- 自动 reward 本身可能有偏差，reward hacking 在真实机器人中尤其危险；
- 当前任务虽然真实，但都在高度固定的 station 和工具 API 下，离完全开放世界机器人自动研究还有距离。

## 图表索引与讲解

| 图表 | 读图重点 | 关联问题 |
| --- | --- | --- |
| Figure 1 | 8 个 YAM robot station，每站独立 hardware / compute / coding agent。 | physical autoresearch 的资源基础。 |
| Figure 2 | ENPIRE 四模块和真实任务总览。 | reset-execute-verify-refine 闭环如何工程化。 |
| Figure 3 | Push-T / Pin insertion / agent 和 fleet scaling。 | coding agents 是否能在真实机器人上 hill-climb。 |
| Figure 4 | zip-tie reward 两视角几何验证。 | 自动 reward 如何避免单视角 false positive。 |
| Figure 5 | simulation Push-T heuristic learning。 | 数字环境 autoresearch 与真实环境难度差异。 |
| Figure 6 | RoboCasa365 仿真结果。 | code-based tools 如何增强 VLA。 |
| Figure 7 | MRU / GPU / MTU / token-to-success。 | fleet scaling 的速度和成本 trade-off。 |
| Figure 8-9 | GPU reset tools 和 pin insertion reward。 | EN 阶段的工具化 reset / verification。 |
| Figure 10 | autoresearch prompt。 | agent 被赋予怎样的目标和协作规则。 |
| Figure 11 | camera setups。 | 每站 perception 配置。 |
| Figure 12 | pin insertion idea tree。 | 多 agent 如何通过 Git 演化有效 training recipes。 |
| Figure 13-15 | token、vision、model/harness ablations。 | coding agent 能力和接口设计如何影响效率。 |
| Figure 16-18 | SAM3 detection diagnostics。 | perception API 错误如何限制 generated policies。 |

## 和你的论文库中其他条目的关系

- 对 [[@qian2026wam-rl]]：WAM-RL 研究 WA 模型如何 online RL / video SFT；ENPIRE 研究这种在线策略改进如何由 coding agents 在真实机器人上自动执行。
- 对 [[@yu2026wm-dagger]]：WM-DAgger 用 world model 离线补 recovery data；ENPIRE 把真实 rollouts、reward 和 policy code search 组织成自动闭环。
- 对 [[@tang2026frs]]：FRS 是策略引导方法，ENPIRE 是让 agent 自动试验和组合这类策略改进方法的系统。
- 对 [[@qwen2026robotmanip]]：Qwen-RobotManip 关注大规模跨本体 VLA 数据对齐，ENPIRE 关注真实机器人后训练和自动实验效率。
- 对 [[@xu2026egoguide]]：EgoGuide 优化 demonstration collection；ENPIRE 优化 demonstration 之后的 policy improvement loop。

## 可追问点

1. EN 阶段的人类反馈成本有多大？不同任务迁移时能否复用 reset / reward？
2. 自动 verification 如何防止 reward hacking，尤其当 agent 能改训练代码和策略行为时？
3. Git-based decentralized collaboration 是否会在更大 fleet 中变成冲突和 token 成本瓶颈？
4. MRU 下降是否可以通过更好的调度器、异步 batch rollout、离线日志分析队列改善？
5. 如果把 ENPIRE 接入 WAM-RL / WM-DAgger，agent 是否能自动选择 world-model SFT、synthetic recovery data 或 actor-only RL？
6. 当前 coding agents 的成功是否依赖高质量工具 API；在工具较弱、感知较差的环境中是否仍能自改进？

## 我的阅读笔记

ENPIRE 很像机器人学习版的“自动实验操作系统”。它真正抓住的是机器人研究中的隐性工程成本：不是每个算法 idea 难，而是每个 idea 都要在真实世界里安全、可重复、可验证地试。把 reset、reward、rollout、log、branch、merge 这些东西统一成 harness 后，coding agent 才有机会真正参与机器人研究。

这篇对以后看 VLA / WMA 自改进特别重要。很多论文说模型能从 interaction 中变好，但谁来操作 interaction？谁来复位？谁来定义成功？谁来决定下一个训练 recipe？ENPIRE 给出的是系统层答案。

我会把它放在“真实机器人自动研究 / policy self-improvement infrastructure”位置来回看。它不是单个 policy 的 SOTA 论文，而是把机器人实验吞吐、agent token 成本、机器人利用率和自动 reward 设计变成了可研究、可比较的对象。

