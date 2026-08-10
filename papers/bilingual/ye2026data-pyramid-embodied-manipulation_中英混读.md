---
tags:
  - bilingual-reading
  - deep-reading
  - survey
source_pdf: "[[papers/pdfs/ye2026data-pyramid-embodied-manipulation.pdf]]"
paper: "[[@ye2026data-pyramid-embodied-manipulation]]"
images: "papers/images/ye2026data-pyramid-embodied-manipulation/"
image_index: "[[papers/images/ye2026data-pyramid-embodied-manipulation/index.md]]"
created: 2026-07-29
reading_mode: "生成式精读（逐节读原文 + 读图）"
source_version: "arXiv:2607.24744v1"
source_pages: 72
project: "https://jasper-aaa.github.io/embodied-data-pyramid/"
github: "https://github.com/worldbench/awesome-embodied-data-pyramid"
---
zheg yao S
# Data Pyramid for Embodied Manipulation

paper:: [[@ye2026data-pyramid-embodied-manipulation]]
pdf:: [[papers/pdfs/ye2026data-pyramid-embodied-manipulation.pdf]]
images:: [[papers/images/ye2026data-pyramid-embodied-manipulation/index.md]]
reading:: [[papers/bilingual/ye2026data-pyramid-embodied-manipulation_中英混读.md]]

> [!important] 论文类型与阅读边界
> 这是一篇 **data-centric survey / taxonomy paper（数据中心综述 / 分类框架论文）**。PDF 共 72 页，正文与结论约到 PDF p.46，之后是 453 项参考文献。全文有 8 幅编号图、7 张编号表，**没有编号公式，也没有作者自己训练的新模型、统一 benchmark、baseline、训练超参数或受控消融**。文中的数据规模和模型表现来自被综述工作；阅读时必须把“作者的分类与综合判断”和“被引用论文的局部结果”分开。

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| Embodied Data Pyramid | 具身数据金字塔 | 全文主框架：从顶到底依次为 real-robot、UMI、ego/exo、simulation、general data；表示监督离真实机器人执行的总体距离，不是质量排行榜。 |
| Scalability | 可扩展性 | 两个主轴之一；同时考虑硬件依赖、人力、环境 reset、安全监督、前期管线与边际生成成本。 |
| Robot Alignment | 机器人对齐 | 两个主轴之一；衡量 observation、representation、supervision 能多直接支持物理机器人学习与执行。 |
| Quality | 质量 | 有效性、一致性、信息量与任务相关性；大量重复、错标或不同步数据仍可能价值低。 |
| Diversity | 多样性 | task、object、scene、viewpoint、instruction、embodiment、sensor、behavior、outcome 等覆盖。 |
| Reusability | 可复用性 | 数据跨任务、环境、本体、传感器和模型族迁移的难易；通常仍需 alignment / retargeting。 |
| Physical Fidelity | 物理保真度 | 对 contact、friction、compliance、noise、latency、object dynamics 等真实交互反馈的保留程度。 |
| Real-Robot Data | 真实机器人数据 | 同一物理平台闭环记录 observation–state–action–outcome；最直接可执行，也最昂贵、最依赖本体。 |
| UMI | Universal Manipulation Interface（通用操作接口） | 用便携手持夹爪、腕部相机与位姿跟踪在无机器人参与时采集 relative EEF motion；位于 robot 与 ego 之间。 |
| EEF | End Effector（末端执行器） | UMI 和跨本体对齐的关键表示；常包含 Cartesian position、orientation 与 gripper state。 |
| Egocentric / Exocentric Data | 第一 / 第三视角人类数据 | 保留真实物理、人类灵巧手与日常环境多样性，但缺少直接 robot proprioception 和 executable action。 |
| Simulation Data | 仿真数据 | 可并行生成 robot-aligned trajectory 与 privileged label，但有 observation / kinematic / dynamic sim-to-real gap。 |
| General Data | 通用数据 | 图文、视频、3D、grounding、planning、physics QA、grasp 等 web-scale 先验；语义宽，但 action/contact grounding 弱。 |
| Action-Free Data | 无动作标签数据 | 主要提供 semantics、temporal / physical prior、future prediction 与 task structure；不能直接说明哪个机器人动作造成转移。 |
| Action-Labeled Data | 有动作标签数据 | 包含 robot action、EEF / gripper motion 或可恢复的 interaction signal，用于 physical grounding 与可执行控制。 |
| Embodied Brain | 具身“大脑”模型 | 强调 perception、grounding、memory、physical reasoning 与 high-level planning，不必直接输出低层动作。 |
| VLA | Vision-Language-Action（视觉-语言-动作模型） | 把视觉与语言理解映射为离散 action token 或连续 action chunk。 |
| WAM | World Action Model（世界动作模型） | 学习世界随时间及动作条件如何演化，可作 simulator、planner、evaluator 或 synthetic-data engine。 |
| Cross-Embodiment Alignment | 跨本体对齐 | 同时包含 action vector 的 structural / semantic alignment 与 coordinate frame 的 geometric alignment。 |
| Semantic Action Slots | 语义动作槽位 | 让共享向量中的每个 block 有固定物理含义；比只统一 tensor shape 的 zero padding 更强。 |
| Action Proxy | 动作代理 | 从无动作视频中恢复 latent action、point trajectory、motion field、hand pose 等；有动作相关性，但不天然可执行。 |
| Data Recipe | 数据配方 | 不同来源的选择、比例、采样、过滤与分阶段分配；本文的核心开放问题之一。 |

## 摘要

多模态基础模型可以从互联网规模的图文与视频中学习“看、说、推理”，但具身智能没有同样的捷径：机器人还要知道 physical state（物理状态）、动作如何改变环境，以及怎样在具体 embodiment（本体）上输出可执行控制。因此，论文从一个数据问题切入：**What data should be used to train embodied foundation models?（应当用什么数据训练具身基础模型？）**

作者提出五层 **Embodied Data Pyramid**。顶层 real-robot data 直接记录机器人动作及其真实物理后果；UMI-style data 去掉采集环节中的机器人，却保留末端执行器和夹爪监督；egocentric / exocentric data 用人类在真实世界中的第一 / 第三视角交互换取更大规模与灵巧手先验；simulation data 恢复可执行 action 和特权标签，但以近似物理为代价；general data 则以最弱的机器人对齐换取最广的语义、空间、时间和推理覆盖。金字塔主要由 Scalability 与 Robot Alignment 两轴组织，再用 Quality、Diversity、Reusability、Physical Fidelity 四维解释每层价值。

论文随后从数据应用角度审视 embodied brain、VLA、WAM。作者指出，训练配方正从 robot-only 走向更大规模的 heterogeneous mixture（异构混合），egocentric data 也越来越重要；但“来源越多越好”尚无统一证据。真正困难的不只是把不同数据塞入同一格式，而是同时统一 action dimensionality / semantics、coordinate frame、units、controller mode，并明确 action-free 与 action-labeled supervision 在不同模型族中的作用。

最后，作者把未来问题归纳为六项：大规模 tactile data、failure / recovery data、跨层可扩展采集、cross-embodiment state-action alignment、egocentric priors for dexterous manipulation，以及 principled data recipes。全文最稳妥的结论不是某一层胜出，而是：**广泛的 semantic / observational prior 必须与本体化、动作化、接触化的 physical grounding 组合；最佳组合仍是未解决的实证问题。**

## 论文主线

作者把中心问题拆成两问：

1. 面对 scalability、robot alignment、physical fidelity、transferability 不同的异构数据，怎样收集、组织、比较与整合？
2. 具身基础模型怎样有效选择、组合并利用这些数据？

全文沿着五步推进：

1. **建立坐标系**：用两主轴、四补充维度定义“数据价值”不止是样本数。
2. **逐层拆解来源**：§2–§6 解释五层的信号、采集管线、规模、优势与不可消除的 gap。
3. **从来源转向模型**：§7 比较数据配方、动作对齐，以及 brain / VLA / WAM 的不同训练需求。
4. **区分观察知识与执行知识**：action-free data 负责 broad prior，action-labeled data 负责 causal / executable grounding；二者不是互相替代。
5. **把缺口变成路线图**：§8 从 what to collect、how to collect、how to use 三问导出六项挑战。

> [!summary] 一句话总结
> 本文构造了一套“监督离真实机器人执行有多近、又有多容易扩展”的具身数据共同坐标系，用它系统解释五类数据如何进入 embodied brain、VLA 与 WAM，并据此指出 tactile、failure/recovery、跨本体动作语义与可因果验证的数据配方是下一阶段的关键缺口。

## 贡献与结论对照

| 贡献 / 结论 | 方法位置 | 证据 / 结论 | 证据边界 |
| --- | --- | --- | --- |
| 建立五层 data-pyramid taxonomy | §1，Fig. 1 | 两主轴 + 四补充维度；real robot → UMI → ego/exo → simulation → general | category-level qualitative synthesis，没有数值评分；不是严格单调排序。 |
| 系统整理每层数据的构造与局限 | §§2–6，Tables 1–6，Figs. 4–8 | 汇总数据集、embodiment、sensor、collection、scale、supervision 与 transfer gap | 统计来自原论文，episode / hour / clip / label 口径未统一重算。 |
| 从数据角度分析 foundation model | §7，Fig. 3，Table 7 | 配方趋向更大、更异构、更多 ego；给出 structural / geometric action alignment；区分 brain / VLA / WAM | presence 图标不含比例、过滤、阶段或算力；不能证明多源因果增益。 |
| 提出未来数据路线图 | §8 | tactile、failure/recovery、scalable collection、cross-embodiment alignment、ego→dexterity、data recipe | 是开放问题，不是已经验证的负结果或解决方案。 |

## 结构地图

| 原文位置 | 作者在这一部分做什么 | 与全文主线的关系 | 关键图表 / 公式 |
| --- | --- | --- | --- |
| §1 Introduction，PDF pp.3–7 | 定义中心问题、六维坐标、五层金字塔、规模与配方趋势 | 建立全文分析语言 | Figs. 1–4；无编号公式 |
| §2 Real-Robot Data，pp.7–14 | 讲 embodiment / modality、script / teleop / HiL、规模与局限 | 给出最 action-aligned 的顶层及其成本 | Fig. 5；Table 1 |
| §3 UMI Data，pp.14–16 | 讲 robot-free interface、relative EEF trajectory、retargeting | 说明怎样用接口工程在 scale 与 action structure 之间折中 | Fig. 5；Table 2 |
| §4 Ego / Exo Data，pp.16–22 | 讲 capture infrastructure 与 semantic / geometric / multimodal / robot-oriented supervision | 解释人类真实交互怎样变成机器人先验 | Fig. 6；Table 3 |
| §5 Simulation Data，pp.22–29 | 讲 asset / backend / embodiment、synthetic generation、world-model simulator、sim-to-real | 给出最可扩展的 robot-aligned 数据层 | Fig. 7；Tables 4–5 |
| §6 General Data，pp.29–35 | 按 cognition、perception、3D、planning、temporal、physics、grasp 组织通用数据 | 给出 broad cognitive prior 的底座 | Fig. 8；Table 6 |
| §7 Data Applications，pp.35–43 | 讲配方趋势、action alignment、brain / VLA / WAM | 回答“数据怎样进入模型” | Fig. 3；Table 7；80-D action vector 案例 |
| §8 Challenges，pp.43–45 | 用 what / how / use 组织六项开放问题 | 把综述差距转成研究议程 | 无新图表 |
| §9 Conclusion，pp.45–46 | 重申五层互补、模型用途与未解配方 | 收束为 data-centric roadmap | 无新图表 |

## 按原文 section 精读

### Section 1. Introduction（PDF pp.3–7）

#### 高层故事流

引言先用“互联网捷径”与“具身无捷径”的对比定义问题：图文预训练可以提供 semantics 与 reasoning，却不会自动给出 action–consequence coupling。机器人必须同时学习物体和场景是什么、动作如何改变状态、某个动作是否适合当前 embodiment。已有 pyramid-like 表述多服务单个模型配方，既有综述则偏模型架构；作者希望建立一个 category-level、data-centric 的共同坐标系。

![[papers/images/ye2026data-pyramid-embodied-manipulation/fig1_page1.png|1000]]

**Figure 1 — Overview of Organization and Scope。** 左侧是五层金字塔，中部对应 §2–§6 的数据构造，右侧对应 §7 的应用与 §8 的趋势。它最重要的作用是提示：本文不是简单列数据集，而是在“来源 → 表示与对齐 → 模型能力 → 未来采集”之间建立一条链。

#### 两个主轴、四个补充维度

Scalability 不只是下载或生成多少条数据，还包括硬件、人工、reset、安全、维护和边际成本；Robot Alignment 则问数据中的 observation、representation、supervision 到真实机器人执行之间还隔着多少转换。二者通常有张力：real robot 很直接却昂贵；general data 很容易扩展却没有接触与执行监督。

Quality、Diversity、Reusability、Physical Fidelity 用来避免把这条张力误解成一维排序。大量轨迹可能高度重复；真实机器人数据可能物理保真，却只覆盖一个机器人和一个任务；人类视频有真实物理，却缺少机器人动作；simulation 有精确 action label，却近似接触动力学。因此作者明确说，五层顺序是六个维度的总体综合，**不要求每个属性严格单调**。

| 顶→底 | 牺牲了什么 | 换来了什么 | 不能忽略的转换 |
| --- | --- | --- | --- |
| Real robot | 硬件、人力、reset、安全与并行性 | 同平台可执行 action、真实 contact / noise / latency | 跨本体 action / frame / sensor 对齐 |
| UMI | robot proprioception 与 actuator dynamics | robot-free in-the-wild 采集 + structured EEF / gripper | calibration、tracking、IK / retargeting |
| Ego / exo | 直接 robot action 与本体状态 | 人类灵巧手、真实物理、日常环境与长时任务 | reconstruction、human–robot alignment、contact feasibility |
| Simulation | 真实世界 observation / dynamics fidelity | 并行、可控、privileged labels、低边际成本 | sim-to-real、asset / skill coverage、real grounding |
| General | robot/action/contact grounding | web-scale semantics、spatial / temporal / planning prior | robot-view adaptation 与 action-conditioned post-training |

#### 规模、配方与多样性的三类描述性证据

![[papers/images/ye2026data-pyramid-embodied-manipulation/fig2_page1.png|1000]]

**Figure 2 — Evolution of Data Scale。** 五类数据都呈增长趋势，但各栏单位不同：simulation / UMI / robot 用 demonstrations，ego 用 hours，general 用 QA pairs。它只能支持“每类内部在增长”，不能让读者比较“一小时 ego 等于多少 robot episode”或判断哪类信息量更大。

引言还提前给出两个重要判断。第一，Fig. 3 / Table 7 显示基础模型从 real-robot 主导逐渐走向异构混合；第二，Fig. 4 用 action keyframe 的空间分布说明 raw scale 不等于 trajectory diversity。后者沿用 PerAct 风格的 heuristic 抽取关键帧，适合作为直观 proxy，却没有形成标准化 metric、重复实验或统计检验。

#### 关键证据 / 图表 / 公式

| 类型 | 位置 | 支撑的主张 | 边界 |
| --- | --- | --- | --- |
| Figure 1 | p.1 | 五层来源、三类模型、六项趋势构成一条完整主线 | 范围图，不是定量证据 |
| Figure 2 | p.4 | 各类数据规模随时间上升 | 跨类别单位不同，selected datasets |
| Figure 3 | p.6 | 更多模型使用多源数据，VLA 之外 WAM 增多 | 只标 presence，不给比例 / stage |
| Figure 4 | p.7 | 同样大规模数据可能具有不同 trajectory coverage | heuristic spatial proxy，不是综合 diversity score |
| 公式 | 全文 | 本文没有编号公式 | 不应从综述对象中虚构“本文 loss” |

### Section 2. Real-Robot Data（PDF pp.7–14）

#### 高层故事流

真实机器人数据处于顶层，因为 observation、robot state、action 和 physical consequence 在同一平台的闭环中产生。它自然包含 sensing noise、controller latency、contact dynamics 与 hardware constraint，动作也能在原平台直接执行；正因为这种紧耦合，每一小时数据都要支付硬件、操作者、重置、维护和安全成本。

#### 2.1–2.2：Embodiment 与 Modalities

数据从 fixed-base single arm + parallel gripper 扩展到 dual arm、mobile manipulation、humanoid、dexterous hand 和 heterogeneous fleet。基础模态是 vision + proprioception + action；tactile 提供 contact location、pressure、incipient slip、grasp stability 等局部信息，force / torque 提供腕部或关节的整体 wrench，audio 提供碰撞和摩擦线索，whole-body 平台还可能包含 IMU、LiDAR、odometry。

动作表示本身就是跨库障碍：joint-space 控制精确却强 morphology-specific；EEF-centric 表示更可迁移，却仍要求一致的 frame、tool center、absolute / delta convention 与 controller。作者也列出 MinMax、Q01–Q99、MeanStd 等 normalization，但没有比较哪一种普遍更优。

#### 2.3：三种采集范式

| 范式 | 主要子类 | 优势 | 主要偏差 / 成本 |
| --- | --- | --- | --- |
| Scripted collection | rule-based、trajectory playback、autonomous policy rollout | episode 边际成本低、可重复、易并行 | 受规则 / seed / 当前 policy 能力与探索策略限制；可能重复或偏向容易状态 |
| Teleoperation | kinesthetic、leader–follower、integrated leader–follower、VR / phone / SpaceMouse、vision、wearable / mocap | 人类可适应目标与接触，示范连贯 | 专用硬件、本体依赖、延迟、精度、操作者负担与视觉分布差异 |
| Human-in-the-loop | DAgger-style intervention、risk-triggered help、fleet takeover、compliant delta correction | 针对 policy-induced difficult states 收 corrective / recovery 数据 | 需要可靠介入触发、标注与人机协同；仍可能遗漏未知 failure mode |

作者特别看好 integrated leader–follower：操作者直接引导 gravity-compensated robot，在同一机构内获得视觉与力反馈，省去独立 leader 的映射误差；代价是操作者手可能出现在训练图像里，部署时形成 distribution shift。

#### 2.4：Scale 与 Diversity

Table 1 的 selected milestones 很能说明“数量”和“覆盖”是两个维度：

| Dataset | Reported scale | Task / embodiment 线索 | 应怎样读 |
| --- | ---: | --- | --- |
| Pinto & Gupta | 50K traj / 700 h | 1 task | 很大，但主要是单一 grasp 行为 |
| QT-Opt | 580K / 800 h | 1 task | 继续证明 scale 不等于 task diversity |
| RT-1 | 130K | 700+ tasks | 用更少轨迹换更广 task coverage |
| Open X-Embodiment | 2.4M | 22 embodiments / 527 tasks | 跨机构聚合，同时带来 action / frame heterogeneity |
| AgiBot World Beta | 1M / 2,976.4 h | 217 tasks | million-scale real-robot 节点 |
| RoboMIND 2.0 | 310K / 1,000+ h | 739 tasks / 6 embodiments；含 tactile / force / failure | 兼顾多模态、跨本体与 failure label 的代表 |
| MolmoAct2-SO100/101 | 38K / 184 h | 1,315 tasks / 2 embodiments | task count 高，但 task 定义不可与其他库直接横比 |
| ABC-130K | 130.7K / 3,591 h | 197 tasks | 小时数高不自动推出更大 effective coverage |

![[papers/images/ye2026data-pyramid-embodied-manipulation/fig4_page1.png|1000]]

**Figure 4 — action-trajectory diversity visualization。** AgiBot-World-2026 呈多个分离空间 cluster，RoboMIND 更 compact / anisotropic，RoboMIND 2.0 更宽且呈垂向层次；EgoVerse、Fast-UMI 与 InternData-A1 又有不同分布。读图重点是“同任务内的路径、接触阶段和空间覆盖可能不同”，不是把点云面积当成唯一质量分。

#### 2.5：优势、局限与本节结论

Real robot 的不可替代价值是 physical/action fidelity；它并不天然保证 diversity 或 reusability。§2.1 一度把真实机器人数据概括为高质量、高保真、高多样和高复用，但 §2.5 又承认许多数据集中于特定平台、任务和环境，跨平台很难。更稳妥的理解是：**物理真实性和原平台可执行性高，其他维度取决于具体采集设计。**

作者建议未来把三件事结合：更自然、细粒度反馈的 teleoperation；更广的 in-the-wild variation / AIGC augmentation；以及 autonomous rollout + human intervention，把真实 failure 转成 recovery supervision。

### Section 3. UMI Data（PDF pp.14–16）

#### 高层故事流

UMI 是金字塔最有解释力的中间层：它移除采集时的 target robot，显著降低场地和本体绑定，却通过 handheld gripper、wrist camera、IMU / visual–inertial SLAM 保留 6-DoF EEF trajectory 与 open / close state。相比普通人类视频，它多了一条结构化 action channel；相比真实机器人，它少了 joint proprioception、actuator dynamics 和真实 robot contact response。

![[papers/images/ye2026data-pyramid-embodied-manipulation/fig5_page1.png|1000]]

**Figure 5 — UMI 与 Real-Robot 对照。** 左侧强调 robot-free、in-the-wild、relative EEF、portable interface；右侧强调 physical embodiment、teleoperation system 与 multimodal robot trajectory。中间的 retargeting 箭头提醒：UMI 并没有消除部署转换，只是把昂贵采集换成后续 calibration / IK / control 问题。

#### 3.1–3.2：采集演化与相对轨迹

原始 UMI 是手持夹爪 + 腕部相机 + 位姿跟踪；FastUMI 减少 setup；LEGATO 用 motion-invariant task space；FreeTacMan 改用 finger-worn interface。随后系统从 single / parallel gripper 扩展到 bimanual、mobile、humanoid、dexterous hand，并加入 multi-view、3D、tactile、force。

论文没有给相对位姿的编号公式，而是用文字说明：future EEF target 相对当前 EEF pose 表达，以降低对 global tracking frame 的敏感性。部署链条可以忠实概括为：

`wrist observation + relative 6-DoF EEF trajectory + gripper command → 与当前 robot EEF pose 合成 → 转到 robot base frame → IK / motion planning / Cartesian controller → joint commands`

#### 3.3：Cross-Embodiment Deployment

LEGATO 用 whole-body IK 把 gripper motion 迁移到 fixed / mobile manipulators。Dexterous hand 更困难：只迁移 wrist 不够，还要解决 finger morphology 与视觉外观。DexUMI 用 exoskeleton 把人手限制到 robot-feasible configuration，再用 inpainting 把图像中的人手替成目标机器人手。这里要抓住一个边界：**visual plausibility、kinematic feasibility、dynamic/contact feasibility 是三件不同的事。**

#### 3.4：规模与局限

| Dataset | Demos | 任务 / 模态线索 |
| --- | ---: | --- |
| UMI | 2.5K | 5 tasks，gripper，无 tactile |
| FastUMI | 9K | 22 tasks |
| FastUMI-100K | 100K | 32 tasks |
| DexWild | 9.5K | dexterous hand |
| DexUMI | 1.8K | dexterous + force / torque |
| FreeTacMan | 10K | 50 tasks + tactile |
| RealOmni | 789.8K | bimanual、diverse、tactile |
| Daimon-Infinity | 274.7K | bimanual、diverse、tactile |

UMI 的主要 failure points 是 pose tracking、sensor synchronization、calibration、camera / end-effector geometry、kinematic / dynamic mismatch 与 contact difference。作者明确把它定位为 real-robot data 的 scalable complement，而不是 replacement。

### Section 4. Egocentric and Exocentric Data（PDF pp.16–22）

#### 高层故事流

这一层保留真实人类在真实环境中的 hand–object interaction、自然 task structure 与 physical dynamics。第一视角把任务相关对象放在视野中心，却容易被手遮挡、发生头动模糊和 partial observability；同步第三视角能补身体与场景上下文，却增加固定场地、跨相机 calibration、同步、存储成本。

![[papers/images/ye2026data-pyramid-embodied-manipulation/fig6_page1.png|1000]]

**Figure 6 — Capture Infrastructure 与 Supervision Fields。** 左侧是 ego / exo camera、tactile、EMG、IMU 等采集设备；右侧将后处理结果分为 semantic、geometry、multimodal、robot-oriented 四类。它说明 raw video 本身不是最终训练信号，真正的工作发生在 annotation、reconstruction 与 alignment 中。

#### 4.2：Capture Infrastructure

| 物理量 | 代表设备 / 方法 | 优势 | 主要风险 |
| --- | --- | --- | --- |
| Visual | monocular、stereo、RGB-D、event camera、exo array | 外观、深度、多视角、快速运动 | depth 缺失 / 范围、反光、blur、occlusion、calibration、场地成本 |
| Motion / pose | IMU、magnetic / flex / optical glove、mocap、AR/VR inside-out tracking | 遮挡下连续手 / 身体运动 | drift、磁干扰、body-specific fitting、专有 pipeline、穿戴负担 |
| Attention / context | gaze、audio | 相关对象、语言和接触事件线索 | wearer calibration、噪声、隐私 |
| Interaction | EMG、force、pressure / tactile array | muscle activation、load、contact distribution | 佩戴与同步、覆盖面积、用户差异、改变自然抓握 |

#### 4.3：Supervision Construction

| Supervision | 典型目标 | 怎样得到 | 不能直接保证什么 |
| --- | --- | --- | --- |
| Semantic | narration、verb–noun、temporal segment、procedure、progress、error | 人工、脚本对齐、model-assisted annotation | 连续 motion 与 contact |
| Geometric | camera pose、depth、point cloud、2D/3D hand/body pose、MANO、object 6-DoF | 标注 + triangulation；模型预测 + fitting；instrumented sensors | 无误差、统一 frame、dynamic feasibility |
| Multimodal | gaze、audio、IMU、EMG、force、tactile map | calibration、filtering、rate synchronization | 与 robot sensor geometry 等价 |
| Robot-Oriented | EEF / joint / gripper / retargeted hand action；human–robot alignment | transform、IK、morphology-aware retargeting、matched tasks/scenes | 真实接触可行性与稳定执行 |

Hand / body pose 的三条路线值得记住：(1) 人工 2D keypoint + depth / multi-view 几何；(2) learned predictor + MANO / body fitting；(3) glove / mocap / headset / inertial sensor capture。它们分别在人工成本、模型偏差、设备负担和 scale 之间取舍。

#### 4.1 / 4.4：规模、价值与边界

Table 3 中 Ego4D 为 3,670 h，Ego-Exo4D 为 1,286 h / 5,035 clips，Egocentric-100K 为 100,405 h / 2.01M clips，EgoVerse 为 1,362 h，Xperience-10M 为 10,000 h，HumanNet 的 reported value 达 967,000 h。这里的 hours / clips 与 supervision density 极不一致：有的只有语义，有的带 calibration / hand pose / metric 3D；因此“小时更多”不能直接等价成“更适合 robot learning”。

这层最强的价值是 human mobility、dexterous hand、everyday variety 和 long-horizon structure；最硬的边界是人类与机器人的 visual、kinematic、morphological、dynamic、contact gap。后续模型应把人类数据视为 task intent、affordance、grasp choice、contact sequence、tool use 等 structured prior，而不是无误差的 robot action label。

### Section 5. Simulation Data（PDF pp.22–29）

#### 高层故事流

Simulation 是“规模”和“动作监督”同时存在的关键层：它可以输出 robot observation、action、success、pose、mask、contact、reward 等特权信号，并安全地并行生成；但真正部署时，视觉、控制和物理差距都会显现。作者因此把 simulation 看成 real-world data 的可控补充，而非替代。

![[papers/images/ye2026data-pyramid-embodied-manipulation/fig7_page1.png|1000]]

**Figure 7 — Simulation Infrastructure and Data Collection。** 左侧把基础设施拆成 embodiment / sensor、scene、object、engine；右侧列 human teleoperation、trajectory replay / augmentation、rule-based、autonomous policy / LLM planning。图的核心信息是：synthetic scale 依赖一整套 asset–task–solver–validation pipeline，不是“开一个 simulator 就免费有数据”。

#### 5.2：三个耦合基础组件

1. **Embodiment–sensor system**：URDF / MJCF / SDF / USD 定义 kinematics、joint limits、inertia、collision geometry、actuator 与 sensor；覆盖 single / dual arm、mobile、humanoid、dexterous hand。
2. **Object / scene assets**：可见 mesh 不够，还要 collision geometry、scale、mass / inertia、material、stable pose、affordance、articulation annotation。ManiTwin 的 100K+ AIGC rigid objects 之所以有意义，是因为每个资产还带 manipulation-oriented annotations。
3. **Physics / rendering backend**：MuJoCo、Isaac、SAPIEN / PhysX、PyBullet、CoppeliaSim、Habitat 及 soft / tactile / differentiable / multi-physics engines，分别限定 contact、parallelism、rendering 与可模拟物理 regime。

#### 5.3–5.4：Benchmark 与生成范式

Table 4 汇总 46 个 simulation benchmark；总体上 rigid-object manipulation 仍占主导，tactile、deformable、mobile 覆盖较少。Table 5 的 10 个大规模资源进一步显示 sample count 可以极大，但任务与物理覆盖未必同步：

| Dataset | Reported scale | 主要覆盖 |
| --- | ---: | --- |
| DexGraspNet | 1.32M | dexterous grasp |
| MimicGen | 50K | 16 tasks / 3 embodiments |
| DexMimicGen | 21K | 9 tasks / dual-arm dexterous |
| DexGraspNet 2.0 | 427M | grasp samples |
| InternData-A1 | 637K / 7.4K h | 70 tasks / 4 embodiments / soft objects |
| InternData-M1 | 244K | 200 tasks |
| GR00T-X Sim | 345K | 6+ embodiments / 58+ tasks / dexterous + mobile |
| SynGrasp-1B | 10M | grasp |
| Dex1B | 1B | 2 tasks / 3 embodiments / dexterous |
| MolmoB0T | 1.7M / 5.8K h | 8 tasks / articulated + mobile |

生成方式可分为 human-executed、rule-based、playback / expansion、autonomous / generative rollout。前者保留人类适应与 recovery，却仍依赖 episode-level 人力；rule-based 可复现但受专家程序表达力限制；playback 保留 seed strategy 却难产生质变；autonomous / LLM / generative pipeline 可大规模扩展，也会继承 reward、planner、policy、simulator 与 filter 的 bias。

#### 5.5：World Models as Simulators

作者把 learned world model 的用途分成三类：

- **Policy training / post-training**：imagined transition 和 reward 用于 RL / adaptation；
- **Policy evaluation**：预测 progress、completion、failure、safety，筛 checkpoint；
- **Synthetic data engine**：按 scene / instruction / action / viewpoint / embodiment 生成未来，再恢复 pseudo-action。

视觉上 plausible 不等于 action-faithful 或 physically valid。World model 还会产生 model exploitation、action ambiguity 和 distribution shift，必须配 filtering、uncertainty 与 real / physics calibration。这与库中的 [[@gigaworld2026roadmap]]、[[@yu2026wm-dagger]] 形成直接研究连接。

#### 5.6–5.7：Sim-to-Real 与结论

Sim-to-real 可拆成 observation mismatch，以及 interaction mismatch 中的 kinematic gap 和 dynamic gap。前者包括 texture、light、material、depth noise、camera、tactile / force；kinematic gap 包括 morphology、joint limit、frame、frequency、controller；dynamic gap 则包括 latency、compliance、backlash、friction、contact、deformation、inertia。后者通常更难消除。

InternData-A1 在 Fig. 4 中即使有 637K trajectories，action keyframe 仍可能高度集中。这个例子把本节结论说得很清楚：**simulation 最容易放大数量，但 effective diversity 和 physical fidelity 必须另行验证。**

### Section 6. General Data（PDF pp.29–35）

#### 高层故事流

General data 位于金字塔底部，不是因为“最差”，而是因为它离 robot execution 最远。作者按它为机器人补什么能力来组织：semantics、grounding、3D、planning、memory、physics / failure reasoning、grasp。它构成 cognitive foundation，之后由 robot-aligned data 把这些知识落到动作与接触。

![[papers/images/ye2026data-pyramid-embodied-manipulation/fig8_page1.png|1000]]

**Figure 8 — General Data Categories。** 中心把 general data 分为 cognition、task reasoning、perception、action；外围示例包含 VQA、OCR、video temporal、physical reasoning、planning、segmentation / localization、3D perception 与 grasping。它提示“通用数据”并非只有 image-caption。

#### 6.2–6.8：能力分解

| 数据能力 | 训练目标 | 对机器人有什么用 | 主要边界 |
| --- | --- | --- | --- |
| Vision–language | caption、VQA、instruction、dialogue | object / relation / intention / function / commonsense | 自动标注会 hallucinate；不含 action consequence |
| Segmentation / localization | box、mask、point、referring、affordance | 把“是什么”变成“在哪里交互” | 机器人视角有 occlusion、重复实例和特殊 viewpoint |
| 3D / spatial | RGB-D、point cloud、mesh、camera pose、3D QA | reachability、collision、viewpoint、search、grasp planning | reconstruction / coordinate / sensor errors |
| Planning | goal + observation → steps / subgoals / next action | 连接 semantics 与 low-level control | LLM plan 可能合理但不可执行，需 state / simulator 验证 |
| Video / temporal | moment localization、step segmentation、memory | 追踪 object state、task progress、past event | observational correlation，不等于 action causality |
| Physical / causal / failure | collision、stability、future、counterfactual、failure cause / recovery | critic、verifier、progress estimator | synthetic physics 与真实 failure 分布不一致 |
| Grasp | 2D rectangle、6-DoF grasp、suction、dexterous pose | 给出交互几何入口 | contact map / mesh / HOI 只是 prior，不等于 executable grasp |

Table 6 的规模跨度极大：SA-1B 有 1.1B masks，GraspNet / SuctionNet 各约 1.1B targets，DexGraspNet 2.0 有 427M grasps；相对地 RoboFail 只有 100 simulated + 30 real videos。这个跨类型对照不能当同质 benchmark，却直观支持作者在 §8 强调 failure data 稀缺。

#### 6.9：优势与局限

General data 无需机器人、teleoperation 或 reset，跨本体复用性极强；但它不记录 proprioception、actuator dynamics、contact force 和执行后的 physical consequence，自动生成的 label / plan 还可能模糊或不物理。最准确的定位是：**它让模型先理解世界，不让模型独立学会在某个身体里可靠地改变世界。**

### Section 7. Data Applications in Embodied Foundation Models（PDF pp.35–43）

#### 高层故事流

前五节回答“数据从哪里来”，这一节回答“数据怎样进入模型”。作者先看 data composition 与 action representation，再分别分析 embodied brain、VLA、WAM。最重要的区分是：action-free data 主要扩大 observation / reasoning / dynamics prior；action-labeled data 把 prior ground 到 physical interaction 与 executable control。

![[papers/images/ye2026data-pyramid-embodied-manipulation/fig3_page1.png|1000]]

**Figure 3 — Evolution of Data Utilization。** 时间线显示早期 VLA 多依赖 real robot，后续模型逐渐加入 general、ego、simulation、UMI，并出现更多 WAM。每张卡片下的图标只表示某类数据出现过，不告诉读者数据量、比例、过滤、采样、pretrain / post-train stage 或 compute。

#### 7.2.1：Data Recipe 的四个观察

1. **配方更异构**：$\pi_0$ 主要 real robot，$\pi_{0.5}$ 加 general，$\pi_{0.7}$ 再加 ego；LingbotVA 用 real + UMI + sim，LingbotVA 2.0 覆盖五层。
2. **来源更多不等于必然更强**：LingbotVLA、DreamZero 等以 robot data 为主仍能获得强结果，作者明确说 optimal recipe 未解决。
3. **reported scale 快速上升**：Qwen-RobotManip 报告约 38,100 h 多源 corpus，其中约 11.4K h open robot，并把 1,933 h ego video 转为 24,808 h robot-compatible trajectories；Xiaomi-Robotics-1 报告 >100K h UMI pretraining + 约 10K h cross-embodiment post-training。不同“小时”因处理和阶段差异不可直接比较。
4. **Ego 成为主要 substrate**：HumanScale controlled pretraining 到 5,000 h，EgoScale 报告 20,854 h action-labeled ego；这些是被综述工作的局部结果，不能替代五层 compute-matched ablation。

$\pi_{0.7}$ 还提供一个初步观察：lower-quality trajectory 若有清晰 prompt 可能仍有用，数据处理可能从 aggressive filtering 转向 quality / intent conditioning。作者把它明确标成 preliminary，而不是定论。

#### 7.2.2：Action-Space Representation

跨本体 action alignment 有两个互补层次：

| 层次 | 策略 | 解决什么 | 留下什么 |
| --- | --- | --- | --- |
| Structural | embodiment-specific projector / adapter / head | 保留 native interface，同时共享 backbone | 每个本体仍有独立 action semantics |
| Structural | fixed-dimensional zero padding + validity mask | 统一 tensor shape 与 batch 接口 | 同一 index 未必同一物理含义 |
| Structural | semantic action slots | 同时统一 shape 与 slot physical meaning | 仍需设计 ontology、frame、unit、mask |
| Geometric | robot / base / world-centric | 与传统 controller 直接对接 | 依赖 base pose、mounting 与 workspace convention |
| Geometric | camera-centric | 让视觉相似运动数值更一致 | 依赖可靠 camera extrinsics 与 viewpoint |
| Geometric | wrist-centric | 分离 local finger articulation 与 global wrist motion | 仍需 hand morphology / contact retargeting |

Qwen-RobotManip 是 semantic slots 的具体例子：

$$
80 = 2 \times 29 + 22, \qquad 29 = 7_{\text{arm joints}} + 9_{\text{EEF pose}} + 1_{\text{gripper}} + 12_{\text{hand joints}}.
$$

这不是本文提出的公式，而是作者转述的 canonical vector 设计。Inactive fields 置零并用 per-dimension mask 从 flow-matching objective 排除。无论采取哪种 frame，都应把 origin、axes、handedness、tool-center point、absolute / delta、rotation parameterization、units 和 controller mode 作为 first-class metadata；现有 coordinate convention 缺充分 controlled ablation。

#### 7.3–7.5：三类模型怎样使用数据

| 模型族 | Action-free data 的主要作用 | Action-labeled data 的主要作用 | 典型推理职责 |
| --- | --- | --- | --- |
| Embodied brain | semantics、OCR、spatial / temporal reasoning、memory、future / masked-video prior | 转为 affordance、grasp pose、waypoint、subtask、next-action 等 transferable grounding | 感知 relevant object / state，恢复 progress，给 plan / subgoal / waypoint |
| VLA | latent action、motion field、hand / point trajectory、plan / CoT / affordance | discrete action token；diffusion / flow-matching continuous action chunk | observation + instruction (+ state) → grounded representation → action chunk → controller |
| WAM | observation-only future prediction，学习 broad dynamics prior | action-conditioned world transition / action generation | imagined rollout、planning、policy evaluation、synthetic data、action prediction |

VLA 的 action-labeled objective 可分为 autoregressive discrete token、diffusion continuous denoising、flow matching vector field。Action-free video 则可生成 latent action 或 explicit geometric proxy；这些 proxy 必须由 robot demonstration / decoder / retargeting 继续对齐，不能直接叫 executable action。

WAM 常用两阶段 recipe：先用 web / ego / exo video 做 action-free future prediction，再用 real robot / UMI / sim 做 action-conditioned post-training。训练后的 WAM 又能生成 imagined trajectories 或替代真实 rollout 做 evaluation，于是金字塔从静态层级变成反馈回路：`broad video prior → action grounding → learned simulator / data engine → policy data`。这个回路的瓶颈是 action fidelity、uncertainty 与 real-world calibration。

#### 本节结论

异构混合、更大规模和更多 ego 是**趋势**，不是最佳配方证明。Table 7 的 presence-only audit 无法回答哪一层的 marginal gain 最大、什么比例最好、哪个 stage 应加入、不同 architecture 是否有相同收益。作者把这些问题留到 §8.6。

### Section 8. Challenges and Future Directions（PDF pp.43–45）

#### 三问组织法

- **What to collect**：补 tactile、failure / recovery；
- **How to collect**：把采集做得更 scalable、adaptive、informative；
- **How to use**：统一 cross-embodiment action，迁移 ego dexterous priors，设计 principled recipe。

#### 六项挑战

1. **Tactile Data for Contact-Rich Learning**：RGB-D 无法直接给 force、slip、local deformation、friction、grasp stability；现有 tactile hardware、signal format、rate、contact area 与 calibration 缺标准，且难与长时 vision–language–action trajectory 对齐。
2. **Failure and Recovery Data**：成功专家轨迹偏置让 policy 不会识别 impending failure、诊断原因或恢复。未来应标注 pre-failure context、onset、category / cause、state change、recovery action 与 final outcome，而不是只存 binary success。
3. **Scalable Collection Across Layers**：wearable ego 正加入 gaze、depth、IMU、glove、tactile、force、EMG，但设备仍受 occlusion、drift、fitting、同步和侵扰限制；需要轻量、无线、模块化、自动 calibration 与标准 metadata。
4. **Cross-Embodiment State–Action Alignment**：统一文件格式不等于 compatible supervision。同一 EEF motion 在 base / camera / local / world frame 中数值不同；coordinate convention 与 controller mode 应成为数据的一等字段。
5. **Egocentric Priors for Dexterous Hands**：human–robot gap 同时涉及 topology、DoF、fingertip geometry、compliance、actuation、sensing、friction、force limit。Inpainting 只减视觉差，不保证 contact physics；更合适的是提取 task / affordance / grasp / contact-sequence prior，再用机器人数据落地。
6. **Data Recipes**：需要 architecture-aware、stage-dependent、compute-matched 的 fixed / curriculum / adaptive mixture 对比，隔离单一 dataset / category 的贡献与交互效应。

### Section 9. Conclusion（PDF pp.45–46）

结论重申五层是互补 supervision spectrum。Real robot 最直接但贵；UMI 便携且保留 EEF，却需 calibration / retargeting；ego 多样且有真实人手交互，却有 embodiment gap；simulation 可控并行，却受 asset 和 sim-to-real 限制；general 提供 broad prior，却缺 action / contact grounding。

本文真正完成的是一种 **ubiquitous language（共同语言）**：以后讨论具身数据时，不再只说“我们有多少小时”，还要问信息是否多样、是否可复用、动作语义是否一致、物理后果是否可信，以及数据在哪个训练阶段服务哪种能力。它没有给出最终 recipe，但把最终 recipe 必须回答的问题列清楚了。

## 方法细节

### 本文自己的“方法”是什么

这篇论文的方法不是 neural architecture，而是一套 review-and-synthesis pipeline：

1. 用 Scalability / Robot Alignment 建立主轴；
2. 用 Quality / Diversity / Reusability / Physical Fidelity 修正一维排序；
3. 将数据归入五层并逐层梳理 collection–signal–transfer–limitation；
4. 用 Tables 1–6 汇总代表资源，用 Figs. 2 / 4 做规模与多样性的描述性可视化；
5. 用 Fig. 3 / Table 7 审计 foundation-model data presence；
6. 用 structural + geometric alignment 和 action-free + action-labeled 两组概念解释三类模型；
7. 从综述缺口归纳六项未来问题。

作者没有公开 systematic-review protocol、统一重算脚本或六维评分器，因此这套方法更接近 expert-curated taxonomy，而不是可重复的 meta-analysis。

### 关键表示接口

- **Real robot**：joint / EEF + gripper / base / whole-body action；跨库需 normalization、frame、frequency、semantics 对齐。
- **UMI**：relative 6-DoF EEF + gripper；目标位姿需与当前 EEF 合成并经 IK / controller 转成 joint command。
- **Ego**：从 image / sensor 恢复 hand / object / contact / task structure，再转为 action proxy 或 robot-oriented target。
- **Simulation**：privileged state 与 exact labels 提供可控监督，但 controller 和 dynamics 仍须 real-to-sim / sim-to-real 校准。
- **General**：以 box / mask / point / 3D / language / plan / future state 等中间表示接到 robot policy。

### 公式与符号审计

全文没有编号公式或原创 loss。上文的 `80 = 2×29 + 22` 是 §7.2.2 转述 Qwen-RobotManip 的 action-vector decomposition，不是本文训练目标；UMI 部署链也是文字流程而非作者给出的数学推导。任何“本文优化了某 loss”或“本文提出了某 inference algorithm”的表述都是误读。

## 实验设置、数据集、基线、指标

### 本文不适用的实验项

- 无 train / validation / test split；
- 无 optimizer、learning rate、batch size、training steps、hardware 或 compute；
- 无 success rate、accuracy、reward、latency、FLOPs、置信区间；
- 无 baseline ranking、learning curve、显著性检验；
- 无原创 ablation。

### 最接近“作者自做分析”的三项

| 分析 | 对象 / 做法 | 能支持什么 | 不能支持什么 |
| --- | --- | --- | --- |
| Fig. 2 scale timeline | 挑选各类 representative datasets，按 demos / hours / QA 分别画趋势 | 每类内部规模增长 | 跨类别有效信息量、质量或模型收益比较 |
| Fig. 3 + Table 7 recipe audit | 给代表模型标注五类 data presence | 异构混合与 WAM 增多的趋势 | mixture ratio、stage、filter、compute、因果性能增益 |
| Fig. 4 diversity view | PerAct-style heuristic 抽 action keyframe，画空间分布 | scale 与 spatial trajectory coverage 可分离 | 完整 diversity score、统计显著性、task / language / contact entropy |

Tables 1–7 是 literature-reported statistics 的索引，不是统一 protocol 下的 benchmark。若要引用某个 dataset / model 数字，应继续回溯表中对应的原始论文。

## 主要结果、消融或对比

### 论文能成立的主要综合结论

1. **Alignment–scale tension 是具身数据的基本结构**：越直接对齐物理机器人，通常越难扩展；但需要四个补充维度避免把它简化成高低优劣。
2. **Scale 不等于 diversity 或 quality**：单一 grasp 行为可有数十万次；simulation 也可能产生大量空间重复轨迹。
3. **Foundation-model recipe 正变得更异构、更大、更多 ego**：这是 Fig. 3 / Table 7 的描述性趋势。
4. **多源不天然优于 robot-only**：当前缺 fixed-compute、stage-aware comparison；作者明确保留判断。
5. **跨本体困难不只是 dimension mismatch**：semantic slot、coordinate frame、units、absolute / delta、controller mode 都要一致。
6. **Action-free / action-labeled 的角色跨模型族不同但互补**：前者给 broad prior，后者给 physical / executable grounding。
7. **Tactile 与 failure / recovery 是两个关键缺口**：前者补当前 contact partial observability，后者补 policy 偏离 nominal manifold 后的 temporal / causal supervision。

### 消融

本文没有作者自己的消融。相反，论文明确指出两个“缺少消融”的地方：coordinate frame 之间没有充分 controlled comparison；五层数据的 proportion、sampling、stage allocation 与 architecture interaction 缺 compute-matched ablation。它们本身就是本文的重要负空间。

## 图表、公式与表格线索

| 编号 | PDF 位置 | 内容 | 读图 / 读表重点 |
| --- | --- | --- | --- |
| Fig. 1 | p.1 | 五层来源 → 数据构造 → 三类模型 → 六项趋势 | 全文结构，不是定量结果 |
| Fig. 2 | p.4 | 五类数据的规模演化 | 各类别单位不同，只看类内增长 |
| Fig. 3 | p.6 | Foundation-model data utilization timeline | 图标只表示 presence；不含比例 / 阶段 / compute |
| Fig. 4 | p.7 | 六个资源的 action-keyframe 空间分布 | heuristic diversity proxy；不能当统一 score |
| Fig. 5 | p.8 | UMI vs real robot 与 retargeting | robot-free scale 如何换来 deployment alignment 问题 |
| Fig. 6 | p.18 | Ego / exo capture 与四类 supervision | raw sensor 到 robot-oriented label 的加工链 |
| Fig. 7 | p.24 | Simulation infrastructure 与 collection | asset / solver / validation 是 synthetic scale 的前提 |
| Fig. 8 | p.30 | General-data capability map | 通用数据不只 VL，还含 grounding / 3D / planning / physics / grasp |
| Table 1 | p.9 | 44 个 real-robot datasets | trajectory / hour / task / embodiment / modalities 口径并不统一 |
| Table 2 | p.15 | 21 个 UMI datasets | arm / task / EEF / demo / tactile |
| Table 3 | p.17 | 38 个 ego / exo datasets | hours / clips 与 label density 要一起看 |
| Table 4 | p.23 | 46 个 simulation benchmarks | tactile / deformable / mobile 覆盖仍少 |
| Table 5 | p.25 | 10 个 large-scale simulation datasets | 样本规模不代表 task / physics diversity |
| Table 6 | p.31 | 50 个 general datasets | 9 组 supervision、不同量纲，仅作索引 |
| Table 7 | p.36 | 74 个 VLA / WAM entries | data presence audit，不是性能榜 |
| Equation | 全文 | 无编号公式 | 不要把被综述模型的 objective 写成本文方法 |

完整图片清单见 [[papers/images/ye2026data-pyramid-embodied-manipulation/index.md]]。

## 主张-证据-边界矩阵

| 主张 / 结论 | 原文证据 | 证据位置 | 解释 | 边界 / 适用条件 |
| --- | --- | --- | --- | --- |
| Real robot 是最直接的 executable supervision | 同平台闭环记录 observation / action / consequence | §2，Table 1 | 原平台动作可直接训练 policy | 不推出最便宜、最多样或最跨平台 |
| UMI 比普通 ego 更 robot-compatible | EEF / gripper / calibrated pose + deployment chain | §3，Fig. 5，Table 2 | 保留 action-like structure | 仍需 tracking、calibration、IK、real grounding |
| Ego 适合 dexterous prior | 人手高 DoF、真实物理、in-the-wild | §4，Fig. 6，Table 3 | 覆盖 affordance / grasp / contact sequence | 人手 action 不等于 robot-executable action |
| Simulation 同时有 scale 与 robot action | 并行 rollout + privileged state / labels | §5，Tables 4–5 | 适合 targeted skill expansion | 不能推出 contact / material / long-horizon fidelity |
| General data 是 cognitive foundation | VL、grounding、3D、memory、planning、physics、grasp | §6，Fig. 8，Table 6 | 补齐 robot data 缺少的知识广度 | 不能单独输出可靠低层控制 |
| Scale 与 diversity 不等价 | Fig. 4；单任务大数据与集中 keyframes | §1 / §2 / §5 | 数量之外需衡量 effective coverage | Fig. 4 只测空间 proxy |
| Heterogeneous mixture 是趋势 | Timeline + Table 7 presence | §7.2 | 越来越多模型接入多层数据 | 不是 performance 的因果证据 |
| Action semantics 比 tensor shape 更深 | zero padding vs semantic slots | §7.2.2 | 同维不代表同物理意义 | 语义 ontology 仍需设计与验证 |
| Action-free video 学 observational dynamics | future / latent prediction 无 action condition | §§7.3–7.5 | 可学 motion / state transition prior | 不能识别本体化因果或 executability |
| Failure data 应保留和结构化 | success-centric bias 与六类未来方向 | §8.2 | 训练 detection、diagnosis、recovery | 失败轨迹仍需 onset / cause / quality filtering |
| 最佳 recipe 未解决 | robot-only 反例 + 缺 compute-matched ablation | §§7.2, 8.6 | 多源互补是合理假设 | 不能给出固定比例或 universal schedule |

## 局限与可追问点

### 作者明确承认的边界

- 最佳 data recipe、source proportion、sampling ratio、stage allocation 未知；robot-only model 仍可能很强。
- 不同模型 reported hours 的 modality、processing、filtering 与 training stage 不同，不可直接比较。
- robot/base、camera、wrist frame 缺充分 controlled ablation。
- Action-free data 主要给 observational prior，executability 仍需 action-conditioned grounding。
- 每一层都有自己的 alignment / fidelity gap，不能把某层当完整替代品。

### 精读审计发现

1. **缺 systematic-review protocol**：没有检索数据库、query、cutoff、纳排、duplicate screening、quality scoring 或 PRISMA-style flow；453 篇很广，但 completeness 不可复核。
2. **六维未 operationalize**：没有 unit、score、rubric 或 inter-rater agreement，无法把数据集可重复地放到连续坐标。
3. **Fig. 2 可视说服力强于可比性**：demonstrations、hours、QA pairs 不是同一量纲，类别内部的 episode 定义也不同。
4. **Fig. 4 proxy 很窄**：空间 keyframe 不包含 task / language entropy、contact mode、failure mode、sensor / viewpoint variation。
5. **Table 7 presence-only**：同样一个 ego 图标，可能代表完全不同的数据量、质量、采样权重和训练阶段。
6. **类别边界具有解释性**：UMI 与 ego 都来自人类真实交互，关键差别是 structured EEF / gripper channel；某些 simulation grasp data 也可从 general grasp supervision 的角度使用。
7. **治理讨论不足**：wearable / web data 的 privacy、consent、license、provenance 没有独立系统分析。
8. **快速过时风险**：这是 2026-07 的 v1 snapshot；持续更新的官方 GitHub 比静态表格更适合跟踪新资源。

### 值得继续追问

- 六个维度能否形成可复现 rubric，并报告 annotator agreement？
- Fixed tokens / updates / compute 下，五层各自的 marginal gain 和 interaction effect 是什么？
- 数据量应按 hours、unique states、task entropy、contact events、failure modes 还是 effective sample size 计？
- 从 1,933 h ego 合成 24,808 h robot-compatible trajectory 时，增加的是独立信息还是同源密度？
- Tactile 应统一 raw sensor signal，还是统一 contact-centric representation？
- 怎样区分 informative near-failure 与无意义噪声，并表示 failure onset、cause、recoverability？
- WAM 作 evaluator 时，怎样证明 world-model ranking 与 real-world policy ranking 一致？

## 与当前库的连接

- **Data recipe 与 semantic action slots**：本文在 §7.2 以 [[@qwen2026robotmanip]] 为 80-D canonical action vector、camera-centric alignment 和多源 corpus 的具体案例。可把本综述当 Qwen-RobotManip 的上位坐标系：前者解释“为何需要多源与对齐”，后者给出一套工程实例。
- **同一模型族的配方演化**：[[@wu2026lingbot-vla2|LingBot-VLA 2.0]] 与 [[@zhang2026lingbot-va2|LingBot-VA 2.0]] 代表 VLA / WAM 两种用途；论文把 LingbotVA 2.0 标为覆盖五层数据的典型，而 LingbotVLA 2.0 使用 real + ego，并采用 semantic-slot 类对齐。
- **低质量数据与可控模型**：[[@intelligence2026pi07-steerable-generalist-robotic|π0.7]] 被用来说明 ego 加入配方，以及 lower-quality trajectory 在清晰 prompt 下可能仍有价值；这是 preliminary observation，适合与 π0.7 精读稿中的数据标签 / steering 机制一起核对。
- **Ego / human → robot**：[[@liu2026last-hd]]、[[@kim2026ego-pi]]、[[@paliwal2026do-i-dexterous-manipulation]] 分别从 latent physical reasoning、第一视角策略迁移、日常人类视频到灵巧操作落地 §4 / §8.5 的 human–robot gap。综述提醒读者把 visual、kinematic、dynamic/contact alignment 分层看。
- **Tactile 缺层**：[[@wu2026tactile-wam]]、[[@liu2026taco-tactile-self-corrector]]、[[@park2026tactx-learning-shared-tactile]]、[[@bi2026heterogeneous-tactile-transformer]] 分别对应 tactile world-action、self-correction、跨传感器共享表征和 heterogeneous tactile foundation；它们是在填 §8.1 所说的 sensor-specific / non-standardized contact layer。
- **Failure、recovery 与数据闭环**：[[@yu2026wm-dagger]] 把 world model 用于 policy-induced state 的数据聚合与修复，[[@gigaworld2026roadmap]] 把 world model 用于 policy evaluation；两者正好落在 §5.5 的 training / evaluation 两类用途。[[@yu2026warp-rm|WARP-RM]] 则补充 Quality 不应只看数量，而应做 progress / reward-based curation。

## 精读路线 / 为什么需要回看

1. **第一次（20 分钟）**：读 Abstract、§1、Fig. 1，记住两主轴、四维、五层；再跳到 §9，确认它是互补谱而非排行榜。
2. **第二次（30–45 分钟）**：读 §7–§8。这是判断密度最高的部分：data recipe、action alignment、brain / VLA / WAM 与六项开放问题。
3. **按研究方向回查**：真实机器人与 HiL 看 §2；UMI / human data 看 §§3–4；world model / synthetic data 看 §5；perception / planning supervision 看 §6。
4. **Tables 1–7 当导航索引，不当排行榜**：准备引用某个数字或据此做设计时，必须回到对应原始论文核对定义、过滤与评测协议。
5. **值得长期回看**：这篇论文最适合在设计新数据管线或混合配方时充当 checklist——每加入一种数据，都追问它提供什么独立信息、动作语义是否一致、物理后果是否可信、在哪一阶段使用、怎样证明 marginal gain。

## 一手来源

- arXiv v1：<https://arxiv.org/abs/2607.24744v1>
- PDF v1：<https://arxiv.org/pdf/2607.24744v1>
- 官方项目：<https://jasper-aaa.github.io/embodied-data-pyramid/>
- 官方持续更新仓库：<https://github.com/worldbench/awesome-embodied-data-pyramid>

> 元数据补充：arXiv 页面给出 DataCite DOI `10.48550/arXiv.2607.24744`（本次核对时标注 pending registration）与 CC BY 4.0 许可。正式标题以 arXiv / PDF 的 **Data Pyramid for Embodied Manipulation** 为准。
