---
tags:
  - bilingual-reading
  - deep-reading
source_pdf: "[[papers/pdfs/ha2026transformer-transformer.pdf]]"
paper: "[[@ha2026transformer-transformer]]"
images: "papers/images/ha2026transformer-transformer/"
image_index: "[[papers/images/ha2026transformer-transformer/index.md]]"
created: 2026-08-05
generator: "setting/scripts/generate_reading_draft.py"
reading_mode: 生成式精读（逐节读原文 + 读图）
reading_standard: "fba534d bilingual full-reading"
extraction: "pypdf"
source_pages: 26
source_chars: 76312
---

# Transformer Transformer: A Unified Model for Motion-Conditioned Robot Co-design

paper:: [[@ha2026transformer-transformer]]
pdf:: [[papers/pdfs/ha2026transformer-transformer.pdf]]
images:: [[papers/images/ha2026transformer-transformer/index.md]]
reading:: [[papers/bilingual/ha2026transformer-transformer_中英混读.md]]

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| robot co-design | 机器人协同设计 | 同时优化"本体"与"控制"，本文特指由目标末端轨迹驱动的本体生成。 |
| motion-conditioned | 运动条件化 | 以人类演示得到的末端轨迹作为任务表示与生成条件。 |
| embodiment | 本体 / 形态 | 机器人的运动学、几何、动力学参数总和；本文把它当作可生成的 token 序列。 |
| RoboToken | 机器人 token | 本文提出的统一表示：时不变的 embodiment token + 时变的 dynamics token。 |
| Diffusion Transformer（DiT） | 扩散 Transformer | 主干架构，同时去噪 embodiment 与 dynamics token。 |
| Dynamics Self-Guidance（DGS） | 动力学自引导 | 用模型自身对 reward 的预测求梯度，反过来引导 embodiment 扩散，无需额外网络。 |
| Zeroth-Order Optimizer | 零阶优化器 | 并行采 $n$ 个设计、用模型自评排序取最优；DGS 的对照与基础。 |
| reward-agnostic / reward-specific | 与奖励无关 / 特定奖励 | 训练时学与奖励无关的动力学，推理时才把预测折算成特定 reward 的分数。 |
| cross-embodiment control | 跨本体控制 | 同一模型条件化在本体上，输出该本体的专家动作，用于自我验证生成的设计。 |
| whole-body controller（WBC） | 全身控制器 | 腿式机器人的 RL 控制器；本文训了 128 个专家用于数据生成与设计验证。 |
| CMA-ES | 协方差矩阵自适应进化策略 | 协同设计领域的标准进化基线，本文的主要对照。 |
| diffusion composition | 扩散组合 | 把多个条件的扩散过程组合起来，实现单轨迹训练 → 多轨迹零样本优化。 |
| manifold adherence | 流形贴合 | 扩散模型只在训练分布内插值、不外推的性质；本文既当特性也当局限。 |
| test-time scaling | 测试时扩展 | 增加并行采样/引导步数换取更优设计，本文观察到与语言模型类似的现象。 |

## 摘要

An often overlooked factor of robot manipulation performance is the embodiment of the robot itself. Motivated by this problem, we study motion-conditioned robot co-design, where the goal is to generate complete robot designs that track target end-effector trajectories (from human demonstrations) while optimizing user-defined rewards. We introduce Transformer Transformer, a diffusion transformer trained on RoboTokens, a unified tokenization of robot embodiments, states, and actions. The same architecture can be used across embodiment spaces (e.g., wheeled bimanual, quadrupeds, humanoids) and use cases (embodiment generation, cross embodiment controller). Rather than overfitting to one reward function, Transformer Transformer is a dynamics model, whose reward-agnostic state and action predictions can be converted into reward-specific value predictions. These value predictions are used to steer embodiment diffusion towards high value robot designs, through a procedure we call Dynamics Self-Guidance. Experiments across multiple design spaces show zero-shot optimization of unseen rewards and trajectories, improving performance and runtime over the evolutionary baseline. Finally, we fabricated an optimized ALOHA design, which reduced tracking error by over 70% compared to the original design.

**中文解读。** 作者的写作动作是"构造 + 统一"：把协同设计流程里原本各自为政的三个模块——生成器（generator）、评价器（critic）、控制器（controller）——用同一个 DiT 实现，靠的是一个新表示（RoboToken）和一个新推理技巧（Dynamics Self-Guidance）。摘要里有两处措辞值得抠：一是 "Rather than overfitting to one reward function... is a dynamics model"，这是全文的方法论主张——**不要学 reward，要学 dynamics，reward 留到推理时再算**；二是 "improving performance and runtime over the evolutionary baseline"，性能与耗时被并列，因为本文相对 CMA-ES 最硬的优势其实是**几个数量级的时间**（最极端处 20.7 s vs 11505.2 s），而设计质量只是持平或略优。

标题的双关作者在脚注里点明了：第一个 Transformer 指变形金刚（会变形的机器人），第二个指自注意力架构。

## 论文主线

![[papers/images/ha2026transformer-transformer/teaser_v6.jpg|760]]

**Figure 1（teaser）读法。** 三段式流程 **Demonstrate → Generate → Validate**：左侧人手持 UMI 夹爪演示末端轨迹；中间由目标运动 + **未见过的** reward 生成优化后的完整机器人设计；右侧再用同一个模型控制生成的机器人去跟踪该轨迹，完成自我验证。这张图就是全文的骨架：任务表示是末端轨迹，产出是完整本体，闭环靠自己的控制器。

一条线串起来：

1. **问题入口**：操作性能里最常被忽略的变量是**机器人本体自身**。末端轨迹这种任务表示是 embodiment-agnostic 的，但它的**执行**不是——能不能跟得上取决于本体，于是同一批数据迁到不同机器人上表现天差地别。作者把这个"迁移不完美"从局限翻转成机会：如果轨迹已经定义了任务，那就反过来**为轨迹设计机器人**。
2. **问题定义**：motion-conditioned robot co-design——给定 (i) 一组目标末端轨迹与 (ii) 一组用户定义 reward，自动生成**完整**本体（跨运动学、几何、动力学的大型异构设计空间），reward 可以同时依赖本体属性（尺寸、质量）与动态行为（关节速度、跟踪精度）。
3. **三个"统一"作为贡献**：统一表示（RoboToken）、统一架构（同一 DiT 当 generator/critic/controller）、统一训练目标（学 dynamics 而不是学某个 reward）。
4. **推理期的关键一招**：因为模型同时输出 embodiment 与 dynamics 预测，任何可微 reward 都能就地算出来，并把梯度回传到 embodiment token——这就是 Dynamics Self-Guidance，不需要额外的动力学模型或可微仿真器。
5. **证据出口**：三个设计空间（ViperX 固定基座、四足 manipulator、移动双臂）上的零样本 reward/轨迹优化、与 CMA-ES 的质量-时间对比、多轨迹组合、跨本体控制自验证（Pearson $r=0.53$），以及真机制造的 ALOHA 优化版（跟踪误差 −73%、最大关节速度 −30%）。

全程要盯的一个问题：**"模型自评"是否可信**。整套流程里生成、排序、控制都由同一个模型完成，一旦它的动力学预测不准，优化就是在优化幻觉。作者自己给了这张诊断表——Fig. 7 的 reward 预测相关性，四足空间明显最低，而四足恰恰是唯一 CMA-ES 仍然占优的设计空间。这条自洽性是本文最漂亮的地方之一。

## 贡献与结论对照

| 贡献 / 结论 | 方法位置 | 证据 / 结论 |
| --- | --- | --- |
| RoboToken：可表示任意刚体关节机器人的统一 token 化 | Sec. 2.1 + Appendix 9.1（Table 19 schema） | 11 个 MuJoCo Menagerie 机器人（质量 0.65–67.5 kg、DoF 6–35）都映射到长度 28–101 的序列；比 MJCF 文本 token 紧凑 27–110× |
| 同一 DiT 同时充当生成器、评价器与控制器 | Sec. 2.2（两种 masked modeling 条件） | 生成的四足可由同一模型控制，reward 与 128 个 RL 专家相关 $r=0.53$（Fig. 8） |
| 学 dynamics 而非学 reward → 零样本换 reward | Sec. 2.2/2.3 | 五种未见 reward（tracking / torque / velocity / size / weight）上都能优化（Appendix 8 的 Tables 2–18） |
| Dynamics Self-Guidance：用自身 reward 梯度引导扩散 | Sec. 2.3 + Appendix 9.4 | 单样本预算下领先零阶搜索（双臂多轨迹 341 vs 242）；样本充足时两者收敛 |
| 相对进化基线的效率优势 | Sec. 3 | ViperX 多轨迹 1.2 s vs CMA-ES 663.8 s；双臂多轨迹 20.7 s vs 11505.2 s（约 3.2 小时） |
| 单轨迹训练 → 多轨迹零样本组合优化 | Sec. 3（diffusion composition） | 26 条未见轨迹同时优化，20/26 占优；CMA-ES 耗时随轨迹数线性增长 |
| 真机验证 | Sec. 3（Fig. 9–10） | 制造优化版 ALOHA：跟踪位置误差 13.0→3.5 cm（−73%）、最大关节速度 2.57→1.82 rad/s（−30%） |
| 暴露适用边界 | Sec. 3（manifold adherence）+ Sec. 4 Limitations | 只在训练流形内插值；四足空间动力学预测差、CMA-ES 仍占优；guidance scale 需逐空间手调 |

## 结构地图

| 原文位置 | 作者在这一部分做什么 | 与全文主线的关系 | 关键图表 / 公式 |
| --- | --- | --- | --- |
| Abstract | 给出问题、三统一、DGS 与真机结论 | 定调：一站式协同设计 | — |
| 1 Introduction | 把"末端轨迹迁移不完美"翻转成设计机会，列三条贡献 | 回答为什么要做 | Fig. 1 |
| 2 Method（Overview / Scope） | 交代方法顺序与适用范围 | 划定边界：刚体关节、primitive 几何、UMI 末端轨迹 | Fig. 2 |
| 2.1 RoboToken | 提出表示并论证 complete / flexible / consistent / extensible / optimizable 五性质 | 回答"机器人怎么表示才可生成可优化" | Fig. 2、Fig. 3 |
| 2.2 架构 | DiT + 两种 masked modeling：motion-to-robot 与 cross-embodiment control | 回答"一个模型怎么身兼三职" | Fig. 4 |
| 2.3 Dynamics Self-Guidance | 用 reward 对 embodiment token 的梯度做 classifier-guided DDIM | 回答"怎么高效搜到高价值设计" | Fig. 4 右下的 gradient 回路 |
| 2.4 Data Collection & Generation | 76 条 UMI 轨迹、三个设计空间、DiffIK 与 128 个 RL 专家 | 说明训练数据从哪来、成本多大 | — |
| 3 Results | 表示通用性、生成性质、零样本优化、并行化优势、多轨迹组合、测试时扩展、guidance vs search、跨本体控制、真机 | 回答是否有效 | Fig. 5–10；Table 1 |
| 4 Related Works + Limitations | 三条线定位（本体优化、跨本体控制、协同设计）+ 局限 | 回答与既有工作的差别和边界 | — |
| 5 Conclusion | 收束 | 回答意义 | — |
| 7 Additional Experiments | 模型容量消融（11.6M vs 63.6M）与控制器对照 | 补充证据 | Fig. 11、Fig. 12、Table 1 |
| 8 Additional Metrics | 五种 reward 的完整定义与全部指标表 | 决定主张能被怎样引用 | Eq. 1–4；Tables 2–18 |
| 9 Additional Method Details | RoboToken 细节、超参、数据生成、推理设置 | 复现所需 | Table 19、Table 20 |

## 按原文 section 精读

### 1. 1 Introduction

**本节在全文中的位置。** 用一次视角翻转确立选题：把"策略在不同机器人上迁移不均"从缺陷读成"机器人应该为任务而设计"。

**原文讲解。** 作者把操作任务形式化为末端轨迹（end-effector trajectories）——这是 UMI 系列及大量模仿学习工作采用的任务表示。关键论断是：这种表示**本身**与本体无关，但它的**执行**高度依赖本体决定的跟踪性能，所以在这类数据上训练的策略迁移到不同机器人时表现并不均等（引 UMI-on-Air）。既然如此，与其抱怨迁移损失，不如反过来问：*What is the best robot embodiment for a given manipulation task?*

问题定义随之给出：给定目标末端轨迹集合与用户定义 reward 集合，自动生成**完整**机器人本体。"完整"意味着要在跨运动学、几何、动力学的大型异构设计空间里推理；reward 可以既依赖本体（尺寸、质量）又依赖动态行为（关节速度、跟踪精度）。

三条贡献被明确写成三个"统一"：

- **Unified Robot Representation**：RoboToken 能表示任意关节机器人的本体、状态与动作，是"一个模型跨多个设计空间"的表示基础。
- **Unified Architecture**：同一个模型用不同 masked modeling 训练后，同时是 generator、critic 与 controller；把所有协同设计模块塞进一个网络，使流水线简单且天然可 GPU 并行。
- **Unified Dynamics Training Objective**：不学特定 reward 的信号，而学多样本体的**通用动力学**；推理时把 reward-agnostic 的动力学预测折算成 reward-specific 的分数，再用它引导本体扩散。

**回看重点。** 这三条其实是层层依赖的：没有统一表示就没法一个模型跨空间；没有统一架构就没法自评自控；没有 reward-agnostic 目标就没法零样本换 reward。读的时候不要当成并列贡献清单。

### 2. 2 Method（Overview 与 Scope）

**本节在全文中的位置。** 很短，但 Scope 段落是判断这篇工作能不能用在自己问题上的关键。

**原文讲解。** Overview 给出叙述顺序：RoboToken（2.1）→ 在其上训练 DiT 及两种用途（2.2）→ Dynamics Self-Guidance（2.3）。

Scope 段落明确划界：RoboToken 面向**刚体关节机器人**（范围与 MJCF 相同），目前只支持 **primitive 几何**；任务表示只用 **UMI 演示的末端轨迹**；reward 只覆盖本体、状态与控制量的函数，**结构强度、外观**等属性明确排除在外。

**回看重点。** 这段 Scope 直接决定了 Sec. 4 Limitations 里的扩展方向（复杂几何、场景/物体、触觉）。如果你的设计目标涉及柔性体、外观或结构力学，这套框架当前不适用。

### 3. 2.1 RoboToken: A Unifying Robot Representation

![[papers/images/ha2026transformer-transformer/tokenization_v2e.png|760]]

**Figure 2 读法。** 左半 "Parse robot simulation"：从仿真模型里解析出 link、joint、motor 及其状态；右半 "Concat attributes into RoboTokens"：每类 token 把自己的属性拼成一个连续向量，蓝色是 **Embodiment**（time-invariant），橙色是 **Dynamics**（time-varying）。图里能直接看到指针机制——joint token 里存 `link ids`、motor token 里存 `joint id`、motor state token 里存 `time id` 与 `motor id`。

**原文讲解。** 作者按五条性质组织这一节：

- **Complete（完整）**：包含本体的全部属性（时不变）与动力学（时变）。tokenizer 把任意机器人描述转成五类 embodiment token——links、fixed joints、sliding/rotating joints、ball joints、motors；再把每个 episode 的状态与动作转成四类 state token（除 fixed joint 外的每类）与 action token。例如 link token 含几何类型、几何尺寸、惯量等物理参数，link state token 含该时刻的位姿。每类 token 内部所有属性拼成一个可直接学习的连续值向量。
- **Flexible（灵活）**：支持可变数量的 embodiment token 与任意连接结构。joint 通过两个 link ID 指向它连接的两个 link，motor 通过 joint ID 指向它驱动的 joint；**没有 motor 指向的 joint 自然就是被动关节**（如 Cassie 的腿部机构）。状态/动作按"每个 link/joint/motor 每时刻一个 token"来表示，并指回对应的时间步与 embodiment token，因此异构状态/动作空间（不同 DoF）只体现为 token 数量不同。这些 ID 后续被转成各类 ID 的可学习位置嵌入。
- **Consistent（一致）**：MJCF 这类格式为了方便人类编辑，对 transform 的处理没有严格约定，直接在文本上学习会迫使网络学一堆**等价但写法不同**的空间偏移，徒增方差而无信息。RoboToken 在预处理阶段统一 transform 约定、自动拆分惯量、collapse 变换。
- **Extensible（可扩展）**：为新任务加 token 类型很容易，本文即为轨迹跟踪任务加了 **Target Pose token**（Fig. 4 中的 "Target Pose"），它们在训练时**不加噪**，并指向应当跟踪它的末端 ID 与时间步 ID——这是"条件"进入模型的方式。
- **Optimizability（可优化）**：MJCF 文本虽然也能被生成，但难以优化——LLM 是自回归的、类别型的，既缺乏 **global controllability**（后面的 token 影响不了前面的），又不可微（采样与反 token 化都断梯度）。而在连续值 RoboToken 上做扩散，两者兼得。

![[papers/images/ha2026transformer-transformer/robotokens_v3.png|760]]

**Figure 3 读法。** 从噪声扩散出各种机器人；每个机器人旁标注"蓝色 RoboToken 数 / 灰色 MJCF 文本 token 数"：28 vs 2,300（固定臂）、38 vs 4,197、60 vs 3,019（灵巧手）、85 vs 7,820（四足+臂）、85 vs 8,377（双足）、194 vs 5,281（人形）——对应正文"紧凑 27–110×"的说法。图里同时能看到扩散过程的中间态（散乱的几何块逐渐组织成机器人），是"embodiment 也能被去噪生成"的直观证据。

Appendix 9.1 的补充值得一并记：文本 token 数按 GPT-4o tokenizer 对 MJCF 计；**惯量拆分**假设 link 内各 primitive 密度均匀，先算各 primitive 的局部惯量与质量，再用平行轴定理 $I_{\text{total}}=\sum\big(I_i+m_i[(r_i\cdot r_i)E-r_i\otimes r_i]\big)$ 归并到 link 质心；**变换规范化**把所有变换 collapse 进 joint token，使所有几何都位于其 link 坐标系原点；**属性编码**上布尔/枚举/整数用二进制编码，跨多个数量级的连续量（惯量、电机增益）用 log 或 signed-log；**上下文长度**上，除自由基座机器人的 free link 与末端（schema 里叫 "Track Link"）外，其余 link 的位姿观测全部删掉，以显著压缩 dynamics token 部分。

**回看重点。** 这五条性质其实是一份**具身表示的评价清单**，可以直接拿去评估其他表示方案（动作 token、场景 token）：能不能算 reward（complete）、能不能变结构（flexible）、有没有冗余等价（consistent）、能不能加新字段（extensible）、能不能被梯度优化（optimizable）。

### 4. 2.2 Transformer Transformer: A Unifying Architecture

![[papers/images/ha2026transformer-transformer/hardware_diffusion_v14.jpg|760]]

**Figure 4 读法。** 上半是通用前向：输入是"带噪或作为条件"的 RoboToken（蓝 embodiment：link/joint/motor；橙 dynamics：target pose / link state / joint state / motor state / action），每个 token 加上自己的 ID 位置嵌入（link id、joint id、motor id、时间 id `t`），扩散步 $k$ 通过 **AdaLN** 注入，输出是去噪后的 RoboToken。下半是两种用法：**(a) Motion-to-Robot Optimization**——输入目标运动轨迹与 reward 函数，输出优化后的 embodiment，注意左下角那条绿色 `diffusion guidance` 回路：`reward → gradient → embodiment token`；**(b) Cross-Embodiment Control Policy**——embodiment、target pose、状态都作为**干净条件**（实线框），只有 action 是带噪的（点状框），输出动作。一张图同时说清了"同一网络、不同 mask"。

**原文讲解。** 需求是能建模**变长序列**的**高精度连续值**数据，因此选 DiT。两种用途：

- **Motion-to-Robot Optimization**：评估 reward 通常同时需要本体信息（如质量惩罚）与动力学信息（如力矩惩罚）以及跟踪表现，所以模型在目标轨迹条件下**同时**扩散 embodiment 与 dynamics token——这样模型手上就有评估新设计所需的一切。非自回归形式还有第二个好处：避免自回归动力学模型的**误差累积**，从而给出时间上更连贯的长时程预测。因为模型也输出 action token，这个优化过程**把控制一并考虑进去了**。由此构造出一个偏向高价值候选的生成器：并行跑 $n$ 条扩散过程，用指定 reward 对 $n$ 个候选排序，返回最好的一个——这就是 **Zeroth-Order Optimizer**。
- **Cross-Embodiment Control**：条件化在本体、当前状态与目标运动上，预测"用于跟踪该运动的专家动作"。由于 RoboToken 的完整性，条件里包含运动学、动力学与驱动能力等关键信息，因此动作预测是 embodiment-aware 的；由于灵活性，异构状态/动作空间只表现为 token 数量差异。在多样机器人数据上训练后，模型可泛化到推理时未见过的本体。

**Model & Training。** 每类 token 学一个该类型专属的线性投影映入 DiT 隐空间，再加上各类 ID 的可学习嵌入。因为有重力，问题域只有 **SE(2) 等变**（不是 SE(3)），所以只做平面变换增强。各类 token 序列先各自 padding 到同一最大长度，再拼成一条长的多模态序列。用 DDIM 训练。为加速训练，对 episode 的时间步做子采样，形成较短的定长序列——作者发现 **8 个时间步**已足够：motion-to-robot 任务里在 episode 内**随机**采，控制任务里**连续**采（以提供过去动作与未来目标信息）。

Appendix 9.2 的补充细节很实用：**joint token 顺序**——每个 joint 用两个 embodiment token 表示，各自指向一个 link 并编码到该 link 的变换，其余属性在两 token 间重复；为让扩散模型区分二者，加一个 joint ordering ID（指向较大 link ID 的那个为 1），并转成可学习位置嵌入。**时间分辨率**——尝试放更多时间步并未显著改善下游硬件优化，却大幅增加训练与推理时间，故定为 8。**扩散步数**——动力学建模受益于更长的扩散过程，动作建模则不需要：精确的状态预测对 reward 引导（尤其是跟踪误差目标）至关重要，因此 motion-to-robot 用 **100 步**，cross-embodiment control 用 **5 步**。**显式 padding token**——motion-to-robot 会生成变长序列，故训练模型**显式预测** padding token（注意力不做 mask），由 detokenizer 识别；控制任务则把 padding token mask 掉。**checkpoint 选择**——motion-to-robot 性能早期就上来了，而跨本体控制要到很后期才 plateau，故取最后几个 checkpoint 中最好的。

**回看重点。** "同时扩散 embodiment 与 dynamics"是全文最核心的架构决定：它既是自评能力的来源，也是误差来源。dynamics 预测不准 → reward 估计不准 → 排序与引导都失真，Fig. 7 正是这条链路的体检。

### 5. 2.3 Optimization with Dynamics Self-Guidance

**本节在全文中的位置。** 从"采样 + 排序"（零阶）升级到"梯度引导"（一阶）的一节。

**原文讲解。** 动机：在困难的优化地形上，零阶优化器可能需要很多样本才能返回高价值设计。作者的做法是把模型对 reward 的**含噪预测**的梯度，用来优化它对 embodiment 的**含噪预测**。与既往工作的差别写得很明确：DGDM 之类需要单独训练一个动力学模型，其他方法需要可微仿真器；本文只用一个统一的扩散模型。

机制：给定可微 reward，就能把梯度反传到 embodiment token。在扩散步 $k$，DiT 预测 $\epsilon_k$ 用于把 token 从第 $k$ 步去噪到第 $k-1$ 步；因此**即使整条扩散链不可微，逐步的 reward 梯度仍能把样本推向更高 reward 的候选**。这一步按 classifier-guided DDIM 的形式实现。推理时并行跑 $n$ 条被引导的扩散过程，再由模型排序返回最优设计。

Appendix 9.4 给了两个不写出来就复现不了的细节：(1) **随机 DDIM 采样**——DDIM 的噪声注入超参 $\eta$ 常取 0（确定性），但作者发现 **DGS 必须用 $\eta=1.0$** 才显著改善，而零阶采样器对 $\eta$ 不敏感；作者的解释是一阶方法容易陷局部极小，逐步衰减的噪声有助于沿扩散过程探索。(2) **guidance scale** 取"不至于把模型推出分布、生成非法机器人"的最大值：ViperX 50、四足 100、双臂 0.2，多轨迹 ViperX 提到 500。

还有一处在 Appendix 8.4 提到但属于方法层面的坑：由于扩散训练要求模型看自己上一步的含噪 token 才能去噪，**token 对自身的注意力显著高于对其他 token 的注意力**，因此用到 embodiment token 的 reward（size、weight）其梯度量级远大于用 dynamics token 的 reward（tracking error）。不做量级校正会直接生成非法机器人，所以 guidance 里把 $\alpha_{\text{size}}$、$\alpha_{\text{mass}}$ 降到 0.005，而汇报 reward 时仍用原值（0.1、10）。

**回看重点。** DGS 不是免费午餐：它需要随机采样、需要逐设计空间调 guidance scale、还需要对不同类型 reward 单独缩放梯度。这三点合起来说明当前版本**不是即插即用**，也是最值得改进的地方。

### 6. 2.4 Data Collection & Generation

**本节在全文中的位置。** 说明训练数据从哪来——这是本文成本最高、也最容易被忽略的一节。

**原文讲解。**

- **目标运动数据集**：用 UMI 夹爪的扩展版本（基于 ARKit）采集 **76 条**运动轨迹，涵盖抛掷、拧螺丝、开抽屉、擦洗等多样技能；**56 条训练 / 20 条验证**。双臂设计空间另用 UMI 的双臂洗碗演示（验证集 26 条轨迹）。
- **三个设计空间**（分别压测三种协同设计难点）：
  - **Kinematic Design — Trossen ViperX 300S**：变化安装位姿、DoF 数量、关节朝向、连杆长度。固定基座控制简单，但对糟糕的运动学设计毫不宽容——不会推理可达性就会遭受巨大跟踪惩罚。
  - **Dynamic Control — 四足 manipulator**：腿部设计变化（串联 vs 弹簧连杆）、机械臂安装方式（固定 vs 滑轨），外加躯干、腿、臂的长度变化。要设计出高价值四足，算法必须推理每个设计的**全身控制表现**，权衡稳定性、惯量与敏捷性。
  - **Task Complexity — 移动双臂**：脊柱设计（固定 / 伸缩 / 弯曲）加长度变化。双臂全身操作比单末端任务复杂得多，含长时程、协调动作与多子任务（如洗碗）。
- **控制器（用于生成 state/action token）**：非腿式（固定基座与移动双臂）用 **Mink**（MuJoCo 的 differential IK），因其不考虑动力学，作者用固定 **80 ms 前瞻**补偿关节位置控制滞后，并包含跟踪、姿态正则与阻尼项。腿式用 **RL/PPO 训 WBC**：为每个离散变体训一个策略，把连续变化（腿长等）放进策略观测，从而一个策略覆盖一族连续变体；四足的 7 个二值设计选择因此产生 **128 个 RL 专家**。作者也试过 GPU 加速的轨迹优化，但发现总墙钟时间上 RL 更快。

Appendix 9.3 的关键补充：

- **过程化生成语法**：从公共根组件向外"生长"机器人；在 MJCF 的 custom data 字段里扩展出一套元语言，支持随机连续属性（腿的尺寸）、属性间约束（左右小腿等长）、随机离散属性（关节转轴、是否包含弹簧连杆机构）。因此每个本体可参数化为"一串离散选择 + 一串连续选择"，且两串长度可变。四个空间的具体变化范围写得很细（如 ViperX 的 4 种安装朝向、5/6/7 DoF、每个上部关节 3 种转轴、连杆长度 −5 cm 到 +20 cm 等）。
- **WBC 训练**：沿用 UMI-on-Legs 的 WBC 形式，PPO + 跟踪 reward + 正则惩罚（关节速度、加速度、限位、机体朝向等）+ 训练中扰动（随机踢击、搬运）；专家还观测本体的连续变化参数与**未来 4 个目标位姿**；摔倒即终止并给终止惩罚。每个 RL 策略在一张 A100 上训 **16 小时**。数据生成时按随机离散/连续选择流过程化生成机器人、加载对应策略、跟踪训练轨迹；对专家动作加控制扰动以增加状态多样性，但**记录未扰动的专家动作**作为监督（PDP 的做法）。
- **数据质量**：过滤时长 < 100 步（2 秒）的 episode（代表摔倒或超出跟踪误差阈值）；对 ViperX 与 ALOHA 空间，因随机本体的跟踪误差极高（19.4 cm / 8.9°），先用 **CMA-ES（population 5、3 代）** 跑训练轨迹，把搜索过程中采到的**所有**本体纳入训练集，从而把训练分布偏置到较优区域。作者顺带指出这是 CMA-ES 与本方法配合的一种方式，另一种可能是在推理时让本模型充当进化算法的采样器。
- **数据规模**：ViperX 380 万 episode / 20 亿时间步；四足 130 万 / 5 亿；移动双臂 5 万 / 6900 万。每个本体设计用 10 个 episode，因此训练本体数分别为 **38 万 / 13 万 / 5 千**。

**回看重点。** 两点值得记在心里：(1) 训练数据质量是被 CMA-ES **预先偏置**过的——所以"我们比 CMA-ES 好"这句话要加上"在 CMA-ES 帮助构造的数据上训练之后"；(2) 128 个 RL 专家 × 16 A100·小时的代价，决定了这套方法目前难以随意扩到新设计空间，这也是作者把"更高效的腿式控制数据生成"列为未来工作的原因。

### 7. 3 Results

**RoboToken 统一多样本体空间。** 作者把 MuJoCo Menagerie 里 **11 个机器人**（灵巧手、固定基座臂、四足及四足+臂、双足、人形）token 化：质量跨两个数量级（Allegro V3 的 0.65 kg 到 Anymal C 的 67.5 kg），DoF 从 6 个主动关节（UR5e）到 35 个主动/被动关节（Cassie），但序列长度都落在 **28–101** 之间。这是表示层面的通用性证据。

**生成结果落在训练流形上。** 作者用扩散模型的理论性质解释生成范围：**manifold adherence（流形贴合）**——score function 在训练分布外无定义，去噪器会把样本推回数据流形，因此生成的设计在训练分布内插值但不外推（四足训练集里没有六足就造不出六足，连杆长度也不会超出训练范围）；作者明说这**既是特性也是局限**（物理合理性天然成立 / 扩展设计空间必须扩展数据集）。**mode coverage（模式覆盖）**——无条件模型生成各机器人类型的概率匹配训练分布。**cross-attribute coherence（属性间一致）**——生成结果尊重本体属性的联合分布：大 link 配相称的质量与惯量，电机与其驱动的关节匹配，因此不需要显式约束就能保证物理可行性。

**零样本优化未见 reward。**

![[papers/images/ha2026transformer-transformer/hardware_opt_results_v3.jpg|760]]

**Figure 5 读法。** 横轴是优化耗时（对数），纵轴是验证轨迹上的平均 reward（含 95% 置信区间，CMA-ES 与扩散采样各 9 个随机种子）；每个子图是一个"设计空间 × reward"组合，(b)(d) 是多轨迹设定。要看三件事：(1) 两条本文曲线（Zeroth Order、Dynamics Self-Guidance）随并行样本数增加而上升——**测试时扩展**；(2) 它们相对 CMA-ES 的位置——多数子图上在**左上方**，即更快且不差；(3) 四足子图上 CMA-ES 仍在上方，这与 Fig. 7 的相关性低相互印证。

四种方法：**Random**（离散与连续选择都随机采）、**CMA-ES**（协同设计常用的进化算法，先采离散再优化连续）、**Zeroth Order**（本文，采 $n$ 个 → 模型排序 → 取最优）、**Dynamics Self-Guidance**（本文，在零阶基础上加梯度引导）。为隔离本体优化性能，每个设计空间单独训一个模型，且只训 motion-to-robot 任务。

评估流程：报告优化过程产出优化机器人所需的**墙钟时间**；对每个优化后的机器人，在 MuJoCo 中用该设计空间对应的控制器（RL 专家 / Mink）验证，报告 episode 的平均 reward 之和。所有计时在一张轻载 RTX 4090 与 i9 上完成。

"Tracking Only" reward 下的完整数字（Appendix 8.1）：

| 设定 | 方法 | Pos Err (cm)↓ | Orn Err (deg)↓ | Survival (%)↑ | Optimize Time (s)↓ |
| --- | --- | ---: | ---: | ---: | ---: |
| ViperX 单轨迹（Table 2） | Random | 19.4 | 8.9 | 72.2 | – |
| | CMA-ES | 5.0 | 5.7 | 98.3 | 47.5 |
| | **Zeroth** | **4.1** | 4.2 | 96.1 | **0.5** |
| | **DGS** | **4.1** | **3.9** | **99.4** | 2.8 |
| ViperX 多轨迹（Table 3） | Random | 17.0 | 9.4 | 80.6 | – |
| | CMA-ES | 7.1 | 6.1 | 86.7 | 663.8 |
| | Zeroth | 3.4 | 3.9 | 95.6 | **1.2** |
| | **DGS** | **2.4** | **3.5** | **98.9** | 43.5 |
| 四足 单轨迹（Table 4） | Random | 3.4 | 8.4 | 96.1 | – |
| | **CMA-ES** | **1.9** | **5.8** | **100.0** | 265.5 |
| | Zeroth | 2.6 | 7.4 | 99.4 | **0.8** |
| | DGS | 2.6 | 7.4 | 99.4 | 5.0 |
| 双臂 多轨迹（Table 5） | Random | 2.8 | 4.4 | 99.6 | – |
| | CMA-ES | **1.7** | **2.5** | **100.0** | 11505.2 |
| | Zeroth | 1.8 | **2.5** | 99.6 | **20.7** |
| | DGS | **1.7** | 2.7 | 99.1 | 30.8 |

这张合表就是全文最核心的证据：**ViperX 上本文在质量与时间上双赢；双臂上质量持平而时间快约 500 倍（20.7 s vs 11505.2 s≈3.2 小时）；四足上质量输给 CMA-ES，只赢时间。**

**并行化解释（为什么快这么多）。** CMA-ES 评估一个候选设计必须让控制器与仿真器**顺序**跑上千个时间步；本文的模型则用非自回归形式，把 episode 的少量时间步**并行**推理，直接给出长时程动力学（从而给出性能）。这两个并行维度（batch × time）相乘，使本文"扩散并评估 128 个候选"比 CMA-ES 评估 5 个还快。

**扩散生成多样设计。**

![[papers/images/ha2026transformer-transformer/qualitative_results_v4.jpg|760]]

**Figure 6 读法。** 展示模型如何随条件变化改变生成分布：为了准确跟踪抛掷轨迹，模型倾向生成**更大**（更稳）且**臂更长**（末端速度更快）的机器人；当 reward 里加入尺寸惩罚时，分布转向**更小**的机器人；把目标轨迹从 "Floor Scrub" 换成 "Dynamic Toss" 同样改变优化地形，安装方式从多样收敛到**只剩直立安装**。作者归因：对不同 reward 的多样性来自 RoboToken 的完整性（reward 有很多可操控的把手），对同一 reward 的多样性来自扩散形式本身。

**多轨迹组合优化。**

![[papers/images/ha2026transformer-transformer/reward_prediction_accuracy_v0.jpg|700]]

**Figure 7 读法。** 预测 reward 与实际 reward 的散点/相关性：ViperX 与双臂的相关性明显高于四足。作者的解释是——学习腿式机器人的动力学意味着要推理学到的 WBC 如何应对**不连续接触**与**摔倒导致的终止风险**，这比固定基座的运动学难得多。**这张图应当被当作"本方法在哪个设计空间可信"的诊断表**，它同时解释了 Table 4 中四足输给 CMA-ES 的原因。

回到多轨迹：作者用 **diffusion composition** 实现"只用单轨迹训练 → 零样本多轨迹优化"，组合后的扩散过程生成的设计在多条未见轨迹上同时表现良好（Fig. 5b、5d 中 **20/26** 条轨迹占优）。相比之下 CMA-ES 的优化时间随轨迹数**线性**增长，多花约 3 小时。作者指出这条能力扩大了应用面：不像既往计算设计工作多聚焦任务专用设计，多轨迹优化可以用来设计**通用操作平台**（例如条件化在一个操作数据集里多任务的运动上）。

**测试时计算量的作用。** 与语言推理模型类似，给更多测试时计算（搜索更多并行种子）能产出更好设计，且这一现象**跨全部设计空间与 reward 成立**，纯粹从"建模本体与动力学"中涌现。但作者也诚实指出：虽然模型可以 refine 长达一分钟（Fig. 5d，guided），性能**并不稳健地随测试时计算继续上升**——与早期语言模型的观察类似；未来可从提高动力学（进而 reward）建模精度与改进推理方案两方面改善。

**Guidance 替代 search，而非互补。** DGS 改进的是**每一个样本**，零阶改进的是**从多个中挑最好**，因此二者是替代关系。它们的差距在"搜索最没得挑"时最大：**单样本**时，在双臂多轨迹设定上 DGS 的 reward 为 **341**，零阶为 **242**（一个设计要服务全部 26 条轨迹）；给足采样预算后，零阶的挑选能力抹平差距，两者变得难以区分。作者由此给出实用判据：**当样本昂贵时（更大模型、更长 episode、交互式使用）guidance 最有价值；样本便宜到可以暴力枚举时则不必**。

**跨本体控制自验证。**

![[papers/images/ha2026transformer-transformer/quadruped_control_performance_v0.jpg|620]]

**Figure 8 读法。** 横轴是 RL 专家控制该本体得到的 reward，纵轴是本文模型控制同一本体得到的 reward；多数点沿对角线聚集，**Pearson $r=0.53$**。要点是"faithful"这个词的操作化定义：**自验证与专家验证得到相近 reward**，那么用自己的控制器评估自己生成的设计就是可信的。挑战在于控制器要迁移到扩散出来的本体上，而它训练时只见过干净的过程化生成机器人；迁移失败会让机器人摔倒、episode 截断、reward 归零。作者称这是"用单一统一跨本体控制器替换 128 个 RL 专家"的**有希望的第一步**——措辞很克制。

Appendix 7 的补充实验把这条线做得更细：在移动双臂空间训练**统一模型**（同时训 motion-to-robot 与 cross-embodiment control），比较 11.6M 小模型与 63.6M 大模型，用 UMI 双臂洗碗的 26 条验证轨迹、每个离散变体配 5 个连续变体，共 25 个机器人 650 个 episode：

| Approach | Pos Err (cm)↓ | Orn Err (deg)↓ | Survival (%)↑ | Reward↑ |
| --- | ---: | ---: | ---: | ---: |
| Ours (Small, 11.6M) | 6.6 | 10.7 | 98.9 | 884.9 |
| Ours (Large, 63.6M) | 5.9 | 9.6 | 99.5 | 957.0 |
| Mink (Oracle) | **4.8** | **7.6** | **100.0** | **1064.3** |

![[papers/images/ha2026transformer-transformer/bimanual_control_performance_v2.jpg|700]]

**Figure 11 读法**：本文控制器（小/大）与 oracle Mink 控制器在每个本体上的表现强正相关——也就是"用我们的跨本体控制器评估机器人设计，对 oracle 评估是忠实的"。

![[papers/images/ha2026transformer-transformer/bimanual_opt_ablation_page1.png|620]]

**Figure 12 读法**：模型容量消融，横轴优化时间、纵轴平均 reward。大模型更好，但同样并行样本数下运行时间是小模型的 **4×**。作者还坦白了一个口径问题：本实验按**梯度步数**归一化，若按**训练 FLOPs** 归一化，小模型本应获得 **5.5×** 的训练步数——所以"大模型更好"这个结论在等 FLOPs 口径下并未验证。

**真机设计验证。**

![[papers/images/ha2026transformer-transformer/real_world_v1.jpg|760]]

**Figure 9 读法。** 为 "Tracking Velocity" reward 优化的 ALOHA 设计与其真机甩布展开（cloth unfolding by flinging）过程。选这个任务是因为它是**动态操作**，压测框架对建模误差与未建模扰动（空气阻力、布料摩擦与重量）的鲁棒性。结果：最大关节速度 **2.57 → 1.82 rad/s（−30%）**，跟踪位置误差 **13.0 → 3.5 cm（−73%）**。优化解的两个特征值得记：连杆长到足以覆盖完整运动，同时轻到 ALOHA 的 Dynamixel 电机撑得住；双臂**倒装在工作区后方**，从而用更高效的 **underarm swing** 取代 overhead fling。

![[papers/images/ha2026transformer-transformer/real_world_velocity_v0.jpg|760]]

**Figure 10 读法。** 原始 ALOHA（a）与优化设计（b）的真机展开序列与关节速度曲线对比：优化设计的最大关节速度更低、**尖峰更少**。这是"设计改变让同一动作更容易执行"的直接可视化——不是控制器变好，而是硬件让任务变简单了。

**回看重点。** 真机部分只有**一个**设计空间、**一个**任务、**一次**制造，没有多设计重复比较，也没有与人类专家设计的对照。它证明的是"这条流水线能一路走到实物且不崩"，而不是"生成设计普遍优于人类设计"。

### 8. 4 Related Works 与 Limitations

**原文讲解（本体设计与优化）。** 传统基于梯度的方法要求受限的本体表示（如 cage-based）或依赖启发式，且难以扩展到有复杂控制与接触的领域（例如腿式机器人的 RL）。数据驱动方法更灵活但**过拟合到单一 reward**。dynamics-guided generation（DGDM、DiffuseBot）通过一个动力学模型的梯度引导设计，从而跨 reward 泛化，但它们仍采用固定开环或简化运动学动作，**回避了完整的控制问题**。Transformer Transformer 的差异点是：在**任意动作空间**上学动力学模型来服务设计。

**原文讲解（跨本体控制）。** GPU 仿真器让 RL 成为运动与全身控制的主流方法，跨本体扩展的常见做法是把单本体专家蒸馏进一个条件化在本体上的共享策略；但这些工作的**本体表示通常是不完整的**——这正是 RoboToken 想补的位置。

**原文讲解（Limitations 段）。** 作者自陈：要走向更完整的操作协同设计，RoboToken 的范围应扩展到复杂几何、场景/物体信息与触觉信息；此外，把 RoboToken 数据生成扩展到更多样机器人（例如更高效的腿式控制）对"把本体当作 first-class token 的基础模型"至关重要。最终目标是让机器人形态像它们要执行的操作任务一样多样，**不再把机器人硬件当作静态约束**。

**原文讲解（协同设计）。** 进化算法证明了"有仿真器 + 足够算力就能找到高价值设计"；后续数据驱动工作用学到的生成器、评价器或控制器加速这个循环，但这些组件建立在**互不相同的表示与目标**上，流水线迭代且难以加速。Transformer Transformer 把三者统一进一个模型，把协同设计整合成**单一 GPU 加速的扩散过程**。

**回看重点。** 这一节的分类可以直接复用为 related work 骨架：本体优化（梯度/启发式 → 数据驱动 → 动力学引导）、跨本体控制（专家蒸馏 + 本体条件化）、协同设计（进化 → 学习组件加速）。本文的差异化就落在"完整表示 + 三合一模型 + 推理期 reward 梯度"。

### 9. 5 Conclusion

**原文讲解。** 收束三句：提出一个能做生成式机器人设计与控制的 DiT，实现运动条件协同设计的"一站式"；仿真结果跨固定基座、腿式与移动双臂三个设计空间，证明效率、性能与对未见 reward 的零样本能力；真机结果验证了模型对**误设定/未建模动力学**的鲁棒性与实用性。

**回看重点。** 结论里"效率"排在"性能"之前，与数据一致——本文最硬的证据是数量级的时间优势，而非设计质量的碾压。

### 10. Appendix 8：五种 reward 的定义与全部指标

**本节在全文中的位置。** 这一节决定了"零样本优化未见 reward"这句话到底覆盖了什么。五种 reward 都是**推理时才引入**的，训练时模型只学动力学。

**Tracking Only（Eq. 1）。** 给定目标位姿轨迹 $\{p^t_{\text{target}},o^t_{\text{target}}\}_{t\in T}$ 与达成轨迹 $\{p^t_{\text{achieved}},o^t_{\text{achieved}}\}$，位置误差 $\epsilon^t_p=\lVert p^t_{\text{target}}-p^t_{\text{achieved}}\rVert_2$，姿态误差 $\epsilon^t_o=\arccos\big(\tfrac{\mathrm{Tr}(R)-1}{2}\big)$（$R$ 是从达成姿态到目标姿态的旋转）。逐步 reward 求和：

$$\sum_{t}^{T}\exp\left(-\frac{\lVert\epsilon^t_p\rVert_2}{\sigma_p}-\frac{\lVert\epsilon^t_o\rVert_2}{\sigma_o}\right) \tag{1}$$

误差全为零时每步 reward 为 1，否则小于 1；$\sigma_p=0.01$、$\sigma_o=0.5$ 控制衰减速度。这种"负误差取指数"是机器人 RL 的常见写法。**终止条件**：四足摔倒，或 $\epsilon^t_p$ 超过阈值（ViperX 与移动双臂 50 cm，四足 80 cm）。双臂情形下 $\epsilon_p,\epsilon_o$ 取**两个末端之和**，因此只有两只手都准才可能拿高分。

**Tracking Torque（Eq. 2）。** 在 Eq. 1 基础上减去力矩惩罚并对每步取非负：

$$\sum_{t}^{T}\max\left(\exp\left(-\frac{\lVert\epsilon^t_p\rVert_2}{\sigma_p}-\frac{\lVert\epsilon^t_o\rVert_2}{\sigma_o}\right)-\alpha_{\text{torque}}\lVert\tau_t\rVert_2,\;0\right) \tag{2}$$

$\alpha_{\text{torque}}=5\times10^{-5}$。取 $\max(\cdot,0)$ 是为了避免出现大负 reward 时智能体反而倾向**提前终止 episode**——这是 RL 里的常见工程惯例。

**Tracking Velocity。** 与 Eq. 2 同形，把 $\alpha_{\text{torque}}\lVert\tau_t\rVert_2$ 换成 $\alpha_{\text{velocity}}\lVert\dot q_t\rVert_2$；$\alpha_{\text{velocity}}$ 取 ViperX 0.1、移动双臂 0.5、四足 0.005。这就是真机实验用的那个 reward。

**Tracking Size（Eq. 3）与 Tracking Weight（Eq. 4）。** 尺寸用"所有几何体最长维度之和"度量，质量用所有几何体质量之和：

$$-T\,\alpha_{\text{size}}\min\big(s_{\text{achieved}}-s_{\text{target}},\,0\big) \tag{3}$$

$$-T\,\alpha_{\text{mass}}\min\big(m_{\text{achieved}}-m_{\text{target}},\,0\big) \tag{4}$$

两式都加到 Eq. 1 上。参数：$\alpha_{\text{size}}=0.1$，目标尺寸 ViperX 2.0 m、四足 6.5 m、移动双臂 5.0 m；$\alpha_{\text{mass}}=10$，ViperX 目标质量 3.2 kg。前面提过的梯度量级问题在这里处理：guidance 时用 $\alpha=0.005$，汇报 reward 时用原值。

> [!warning] 疑似笔误
> 正文说"This term is zero only if the size of the robot is **below** the target size"，但按 Eq. 3 写法（$\min(\cdot,0)$ 再取负），当 $s_{\text{achieved}}>s_{\text{target}}$ 时该项才为 0，当尺寸低于目标时反而给正奖励。语义上想要的显然是"超标才罚"，即 $\max(\cdot,0)$。Eq. 4 同理。复现时以文字语义（惩罚超标）为准。

**跨 reward 的结果要点（Tables 6–18）。** 几处比主表更能说明边界：

- **Velocity, ViperX 多轨迹（Table 10）**：Zeroth 3.4 cm / 0.362 rad/s / 7.3 s，**DGS 反而更差**（5.5 cm / 0.394 rad/s / 43.4 s）。这是 DGS 并非总是更优的直接反例。
- **Size, 四足单轨迹（Table 15）**：CMA-ES 2.3 cm / 7.28 m，Zeroth 4.2 cm / 7.40 m，DGS 4.6 cm / 7.17 m——本文在四足 + 尺寸 reward 上跟踪精度明显更差，只是尺寸压得略小。
- **Weight, ViperX（Tables 17–18）**：这是所有 reward 里最难的——单轨迹 CMA-ES 13.2 cm、Zeroth 8.7 cm、DGS 9.2 cm；多轨迹 CMA-ES 17.4 cm 甚至**劣于 Random 的 17.0 cm**，而 Zeroth 8.6 cm、DGS 8.1 cm。质量约束与跟踪精度的冲突最尖锐，本文优势也最明显。
- **Torque, 四足（Table 8）**：CMA-ES 2.0 cm / 3.2 Nm，Zeroth 2.5 cm / 3.1 Nm——再次是"四足上互有胜负、时间本文快得多"。

**回看重点。** "零样本优化未见 reward"这句主张的正确读法是：**在五种由本体量与动力学量构成的解析 reward 上成立**，而不是任意 reward。所有 reward 都必须可微且能由模型输出的 token 直接算出——这既是 DGS 的前提，也是 Scope 里"结构强度、外观不在范围内"的技术原因。

### 11. Appendix 9.2 / Table 20：模型与训练超参

| Hyperparameter | Value |
| --- | --- |
| Hidden dim | 256 |
| Num layers | 8 |
| Num heads | 4 |
| Dropout | 0.0 |
| LR | $5\times10^{-3}$ |
| LR ramp up | 500 steps |
| Batch size | 64 |
| Weight decay | 0.0 |
| EMA power | 0.75 |
| Num epochs | 50 |
| Num steps per epoch | 16,384 |

统一模型（同时训两个任务）时作者发现**更大的模型训得明显更快**，于是把隐藏维与头数翻倍、层数增到 12（即 63.6M 的 large 模型），并为稳定训练把学习率降到 $1\times10^{-4}$。

**回看重点。** 这是一份**很小**的模型（小 11.6M / 大 63.6M），与当下机器人基础模型动辄数亿参数形成对比。它提示这条路线的瓶颈目前在**数据与表示**而非模型规模——同时也意味着"scaling 会不会带来质变"完全没被测试。

## 方法细节

按"输入 → 中间表示 → 训练目标 → 输出如何使用"四问拆解：

1. **输入是什么。** 统一是 RoboToken 序列：蓝色 embodiment token（link / fixed joint / dynamic joint / ball joint / motor，含几何、惯量、阻尼、增益、限位等，Table 19 是完整 schema）+ 橙色 dynamics token（link/joint/motor 的逐时刻状态、action、以及**不加噪**的 target pose 条件 token）。token 之间用 ID 互指表达拓扑；每个 token 还带各类 ID 的位置嵌入（含 time id）。扩散步 $k$ 经 AdaLN 注入。
2. **中间表示是什么。** DiT 的隐空间；每类 token 有专属线性投影入口。一个 episode 只取 **8 个时间步**：motion-to-robot 随机采、control 连续采。由于自注意力是 $O(n^2)$，除自由基座 link 与末端（Track Link）外的 link 位姿观测被删除以压上下文。
3. **训练目标是什么。** 标准扩散去噪（DDIM）。同一网络用**不同的掩码/条件方案**训练出两种用途：(a) motion-to-robot——target pose 为条件，embodiment 与 dynamics 都加噪；(b) cross-embodiment control——embodiment、状态、target pose 为干净条件，只有 action 加噪。训练里没有任何 reward 信号，这正是"reward-agnostic dynamics"的含义。数据增强只用 SE(2) 平面变换（因为有重力）。扩散步数：motion-to-robot 100 步，控制 5 步。
4. **输出如何使用。** 三种角色：**generator**（去噪出 embodiment token，detokenize 成完整机器人描述，含显式 padding token 以支持变长）；**critic**（用去噪出的 dynamics token 代入用户 reward 得到分数，用于排序或求梯度）；**controller**（输出 action token 直接驱动机器人）。两个优化器：Zeroth-Order（并行 $n$ 条 → 排序 → 取最优）与 Dynamics Self-Guidance（每个 DDIM 步把 $\nabla_{\text{embodiment}}\,r$ 按 classifier guidance 注入，$\eta=1.0$，guidance scale 逐空间设定）。

## 实验设置、数据集、基线、指标

- **设计空间**：ViperX 300S 固定基座（安装朝向 4 种、DoF 5/6/7、每上部关节 3 种转轴、连杆 −5～+20 cm 等）；四足 manipulator（7 个二值选择：臂固定/滑轨、每条腿串联/弹簧连杆、前后膝朝向；连续量含臂长、臂安装位、机体长、腿长、腿安装角、电池位置）；移动双臂（脊柱固定/伸缩/弯曲、躯干 45° 俯仰 DoF、脊柱与臂长等）；另有 ALOHA 空间用于真机（3 种安装朝向 + 安装位置与臂长连续变化，约束左右对称）。
- **数据**：76 条 UMI/ARKit 末端轨迹（56 训练 / 20 验证）+ UMI 双臂洗碗（26 条验证轨迹）。生成数据规模 ViperX 3.8M episodes / 2B steps（380K 本体）、四足 1.3M / 500M（130K）、双臂 50K / 69M（5K），每个本体 10 个 episode。过滤 <100 步的 episode；ViperX 与 ALOHA 的训练本体经 CMA-ES（pop 5、3 代）预先偏置。
- **控制器**：非腿式用 Mink DiffIK（80 ms 前瞻，含跟踪/姿态正则/阻尼项）；腿式用 PPO WBC，每个离散变体一个专家（四足共 128 个，各 16 h A100），观测含连续本体参数与未来 4 个目标位姿，动作加扰动但记录未扰动专家动作作为监督。
- **基线**：Random、CMA-ES（协同设计领域标准进化算法）；控制侧的 oracle 是 Mink（双臂）与 128 个 RL 专家（四足）。
- **指标**：episode 平均 reward 之和（主指标）、位置误差 cm、姿态误差 deg、survival rate %、优化墙钟时间 s；本体类 reward 另报 size(m)、weight(kg)、torque(Nm)、velocity(rad/s)。9 个随机种子、95% 置信区间；计时在轻载 RTX 4090 + i9 上。
- **未覆盖**：没有与人类专家设计的对照；真机只有一次制造；跨设计空间的单一统一模型只在 Appendix 7 的双臂空间做了（主实验为每空间单独训模型）；模型容量对比未按等 FLOPs 归一。

## 主要结果、消融或对比

| 证据类型 | 原文线索 | 读法 |
| --- | --- | --- |
| 表示通用性 | 11 个 Menagerie 机器人 → 长度 28–101 的序列；比 MJCF 文本紧凑 27–110× | 这是"能表示"的证据，不是"能生成好设计"的证据，两者别混 |
| 主结果（Fig. 5 + Tables 2–5） | ViperX 双赢；双臂质量持平、时间 20.7 s vs 11505.2 s；四足质量输给 CMA-ES | 结论要按设计空间分开陈述，不能笼统说"优于进化基线" |
| 多轨迹零样本（Fig. 5b,d） | 26 条未见轨迹中 20 条占优；CMA-ES 多花约 3 小时 | 单轨迹训练 + diffusion composition，是本文最"零样本"的一条 |
| 测试时扩展 | 更多并行种子→更好设计，跨空间与 reward 普遍成立；但一分钟级 refine 后不再稳定上升 | 正反两面都要引，作者自己就写了不稳定 |
| Guidance vs Search | 单样本时 DGS 341 vs Zeroth 242（双臂多轨迹）；预算大时无差别 | 结论是"替代而非互补"，并给出何时该用 guidance 的判据 |
| Reward 预测精度（Fig. 7） | ViperX/双臂相关性高，四足低 | 全文最有价值的自我诊断；解释四足为何败给 CMA-ES |
| 跨本体控制（Fig. 8、Fig. 11、Table 1） | 四足 $r=0.53$；双臂小/大模型 6.6/5.9 cm vs oracle 4.8 cm | "有希望的第一步"，离替换 128 个专家还远 |
| 容量消融（Fig. 12） | 大模型更好但同样样本数下慢 4×；等 FLOPs 下小模型应多训 5.5× | 结论在等 FLOPs 口径下未验证，引用需谨慎 |
| 真机（Fig. 9–10） | 跟踪误差 13.0→3.5 cm（−73%），最大关节速度 2.57→1.82 rad/s（−30%） | 单设计单任务；证明流水线可落地，不证明普遍优越 |
| 生成性质 | manifold adherence / mode coverage / cross-attribute coherence | 物理合理性"免费"来自数据流形，代价是不能外推 |

## 图表、公式与表格线索

**图。** Fig. 1 teaser（Demonstrate–Generate–Validate）｜Fig. 2 RoboToken 的解析与拼装｜Fig. 3 RoboToken 扩散与 token 数对比｜Fig. 4 统一架构与两种用途（含 guidance 回路）｜Fig. 5 测试时扩展与 CMA-ES 对比｜Fig. 6 不同 reward/轨迹下的多样设计｜Fig. 7 reward 预测精度｜Fig. 8 生成四足的自控制验证｜Fig. 9 真机甩布展开｜Fig. 10 原始 vs 优化 ALOHA 的关节速度｜Fig. 11 双臂控制器与 oracle 的相关性｜Fig. 12 模型容量消融。

**表。** Table 1 控制器 vs oracle｜Tables 2–5 Tracking Only｜Tables 6–8 Tracking Torque｜Tables 9–12 Tracking Velocity｜Tables 13–16 Tracking Size｜Tables 17–18 Tracking Weight｜Table 19 RoboToken schema（每类 token 的属性、维度与编码方式）｜Table 20 模型超参。

**公式。** Eq. 1 跟踪 reward（含位置/姿态误差定义与终止条件）、Eq. 2 力矩惩罚版、Eq. 3 尺寸惩罚、Eq. 4 质量惩罚（Eq. 3/4 存在 min/max 笔误，见上文提示）。另有 Appendix 9.1 的平行轴定理惯量拆分式。

**本地图片索引**：完整清单见 [[papers/images/ha2026transformer-transformer/index.md]]（共 12 张，全部来自 arXiv source）。

## 主张-证据-边界矩阵

| 主张 / 结论 | 原文证据 | 证据位置 | 解释 | 边界 / 适用条件 |
| --- | --- | --- | --- | --- |
| RoboToken 能统一表示多样刚体关节机器人 | 11 个 Menagerie 机器人 → 28–101 token；比 MJCF 文本紧凑 27–110× | Sec. 3 开头、Fig. 3 | 完整 + 灵活 + 一致 + 可扩展 + 可优化五性质 | 只支持 primitive 几何，无场景/物体/触觉；MJCF 同等范围 |
| 一个模型可同时当生成器、评价器、控制器 | 生成四足由同一模型控制，与 RL 专家 $r=0.53$；双臂控制接近 oracle | Fig. 8、Fig. 11、Table 1 | 用不同 masked modeling 训同一网络 | $r=0.53$ 仅"有希望"，尚不足以替换 128 个专家 |
| 可零样本优化未见 reward 与未见轨迹 | 五种 reward、多条验证轨迹上均可优化；多轨迹 20/26 占优 | Tables 2–18、Fig. 5 | 训练学 dynamics，推理才折算 reward | reward 必须可微且能由输出 token 算出；结构强度/外观等不适用 |
| 相对进化基线在质量与时间上更优 | ViperX 4.1 cm / 0.5 s vs CMA-ES 5.0 cm / 47.5 s；双臂 20.7 s vs 11505.2 s | Tables 2、3、5 | 双重并行（batch × time）+ 非自回归长时程预测 | 四足空间质量输给 CMA-ES（Table 4、15）；训练数据本身被 CMA-ES 偏置过 |
| Dynamics Self-Guidance 提升样本效率 | 单样本 341 vs 242 | Sec. 3 "Guidance Substitutes for Search" | 逐步 reward 梯度改进每个样本 | 与零阶是替代关系；velocity 多轨迹上反而更差（Table 10）；需 $\eta=1.0$ 与逐空间 guidance scale |
| 优化设计在真机上有效 | 跟踪误差 −73%、最大关节速度 −30% | Fig. 9、Fig. 10 | 更长但仍可承载的连杆 + 倒装以改用 underarm swing | 单一设计空间、单任务、单次制造；无人类设计对照 |
| 生成设计物理合理但不外推 | manifold adherence / mode coverage / cross-attribute coherence | Sec. 3 | 扩散模型的固有性质 | 想要新形态必须先扩数据；这是能力上限而非工程缺陷 |

## 局限与可追问点

作者承认的：RoboToken 需扩展到复杂几何、场景/物体、触觉；需把数据生成扩到更多样机器人（尤其更高效的腿式控制）；生成不外推（在 Results 中作为性质陈述）。

需要自己补的边界与追问：

- **"优于 CMA-ES"要分空间说**：ViperX 双赢、双臂时间赢质量平、四足质量输。而且训练数据本身用 CMA-ES 偏置过（ViperX/ALOHA），"击败老师"的说法要打折。
- **自评闭环的风险**：生成、排序、控制都由同一模型完成，误差不是独立的。Fig. 7 只给了 reward 预测的相关性，没有给"模型自评排序"与"真值排序"的秩相关；后者才是 Zeroth-Order 有效性的直接指标。
- **DGS 的可用性**：需要随机 DDIM（$\eta=1.0$）、逐设计空间 guidance scale（50/100/0.2/500）、按 reward 类型缩放梯度（0.005 vs 0.1/10）。这三处手工调参说明它离即插即用还远，也让"零样本"这个词略显乐观——reward 是零样本的，超参不是。
- **公式笔误**：Eq. 3/4 的 $\min$ 与正文语义相反（见上文提示）。
- **等 FLOPs 口径缺失**：容量消融按梯度步数归一，作者自陈等 FLOPs 下小模型应多训 5.5×，因此"大模型更好"未被证实。
- **真机证据薄**：一个任务、一次制造、无重复、无人类设计对照；且 ALOHA 空间的训练数据同样被 CMA-ES 偏置过。
- **成本结构没被算清**：128 个 RL 专家 × 16 A100·小时 + 数百万 episode 的数据生成，是一次性摊销还是每换设计空间就要重来？如果是后者，"比 CMA-ES 快 500 倍"的推理耗时优势在总账上会被抵消很多。论文没有给这笔账。
- **未被测试的规模效应**：模型只有 11.6M/63.6M，是否存在"再大就质变"的空间完全未知。

## 与当前库的连接

- **tokenization 路线的另一维**：[[@kang2026x-tokenizer]]、[[@zhong2025action-tokenization-survey]] 讨论"动作怎么表示"，本文讨论"**本体**怎么表示"。RoboToken 的五条性质（complete / flexible / consistent / extensible / optimizable）可以作为评价任何具身表示的通用清单，直接搬去读动作 tokenization 的论文。
- **dynamics model 作为评价器**：[[@wang2026orca]]、[[@gao2026fast-leworldmodel]]、[[@wang2026wvm]] 都是"用预测未来的模型给某样东西打分"。差别在打分对象：世界模型打分**策略/轨迹/数据**，本文打分**硬件**。共同的失效模式也一致——动力学越难预测（接触、摔倒），打分越不可信，本文的 Fig. 7 就是这条规律的干净证据。
- **跨本体**：[[@qwen2026robotmanip]] 做跨本体对齐与规模化预训练，本文做的是"跨本体控制器 + 本体生成"。若把两者接起来，可以问：跨本体 VLA 是否能直接作为这里的 controller，从而免去 128 个 RL 专家？
- **人类演示作为任务定义**：[[@paliwal2026do-i-dexterous-manipulation]]、[[@wang2026vlk-learning-humanoid-loco]] 都在处理"人类数据 → 机器人"，共享 UMI 式末端轨迹表示。本文提供了一个反向思路：与其把人类数据硬迁到既有机器人，不如**为这批人类演示生成合适的机器人**。这个视角值得写进任何"human-to-robot transfer"的 related work。
- **测试时扩展**：本文观察到"更多并行采样 → 更好设计"，与 [[@gao2026fast-leworldmodel]] 那类"要不要在测试时想象未来"的讨论是同一族问题（测试时计算怎么花）。可以做一张跨论文的对照表：测试时计算用于**采样更多候选** / **更长的想象** / **更多的梯度引导步**，各自的收益曲线与饱和点。

## 精读路线 / 为什么需要回看

1. 先读 `摘要`、`论文主线` 与 Fig. 1，抓住"末端轨迹是任务、机器人是变量"这个视角翻转，以及 Demonstrate–Generate–Validate 的三段式。
2. 再读 Sec. 2.1 与 Fig. 2/3，把 RoboToken 的五条性质记住——这是本文可迁移性最高的部分，即使不做协同设计也用得上。
3. 然后读 Sec. 2.2–2.3 与 Fig. 4，重点是"同一网络两种掩码"和 guidance 回路；配合 Appendix 9.2/9.4 的细节（8 个时间步、100 vs 5 扩散步、$\eta=1.0$、guidance scale）才算真读懂。
4. 结果部分按 Fig. 7 → Tables 2–5 → Fig. 5 的顺序读：**先看模型自评有多准，再看优化结果，最后看效率曲线**。反过来读容易被"快 500 倍"带偏而忽略四足空间的失败。
5. Appendix 8 必须翻一遍：五种 reward 的定义决定了"零样本 reward"这句话的实际覆盖面，Tables 10/15/17-18 则给出方法的失效与优势边界。
6. 若要引用：引"优于进化基线"必须限定设计空间（ViperX/双臂 vs 四足）并注明训练数据经 CMA-ES 偏置；引"零样本优化未见 reward"必须说明 reward 需可微且由输出 token 直接计算；引真机的 −73% 必须注明是单一 ALOHA 设计、单一 flinging 任务。
