---
tags:
  - bilingual-reading
  - deep-reading
source_pdf: "[[papers/pdfs/liu2026rapid.pdf]]"
paper: "[[@liu2026rapid]]"
arxiv: "2609.30249v1"
images: "papers/images/liu2026rapid/"
image_index: "[[papers/images/liu2026rapid/index.md]]"
created: 2026-10-02
reading_mode: full-close-reading
reading_standard: "bilingual full-reading"
source_pages: 9
---

# RAPID: Robot Agentic Programming from Demonstrations

paper:: [[@liu2026rapid]]
pdf:: [[papers/pdfs/liu2026rapid.pdf]]
images:: [[papers/images/liu2026rapid/index.md]]
reading:: [[papers/bilingual/liu2026rapid_中英混读.md]]

## 核心词汇速查

| English | 中文 | 在本文中的具体含义 |
| --- | --- | --- |
| Robot Agentic Programming from Demonstrations, RAPID | 从示范进行机器人智能体编程 | 从一次人类视觉示范生成、测试并修订可复用操作程序的框架 |
| Agentic coding loop | 智能体编程闭环 | agent 生成代码，执行候选程序，检查结果，再根据失败修改代码 |
| Nonprehensile manipulation | 非抓持操作 | 用推、翻转、绕接触点转动、倾倒等接触行为改变物体状态 |
| Quasi-static rigid-body manipulation | 准静态刚体操作 | 本文问题定义的适用范围，不包含已验证的高速动态或柔性物体控制 |
| Object-centric relational program, OReP | 以对象为中心的关系程序 | 用对象角色、关系和期望效果定义原语及其组合 |
| Primitive | 操作原语 | 为实现局部对象效果而求解轨迹优化的可执行程序 |
| Strategy | 任务策略 | 按阶段组合原语，并计算各次调用参数的任务级程序 |
| Semantic role binding | 语义角色绑定 | 将场景实体分配给目标物、支撑面、夹具、操作器等角色 |
| Geometry resolver | 几何解析器 | 根据当前场景状态计算接触面、翻转轴和物体尺寸等特征 |
| Connecting constraint | 连接约束 | 根据上一阶段的状态与对象关系生成下一原语的效果参数 |
| Success predicate | 成功判据 | 将语义目标转成可执行的布尔检查，用于验证程序 |
| Trajectory optimization | 轨迹优化 | 在仿真中搜索能使原语代价较低的机器人运动 |
| Cross-entropy method, CEM | 交叉熵方法 | 不需要对接触仿真求导的采样式优化方法 |
| Real-to-sim / sim-to-real | 真实到仿真 / 仿真到真实 | 重建观察到的场景，并将仿真优化所得动作迁移到机器人 |
| Scene variants, SV | 场景变体 | 扰动物体与物理属性，再经任务相关过滤器筛选的验证场景 |
| Debug scene | 调试场景 | LIBERO-Pro 中供 agent 探索和修改程序的初始环境 |

## 摘要

> Coding agents have demonstrated enormous success in solving complex programming problems.
> To leverage their potential for robot systems, this work introduces Robot Agentic Programming from Demonstrations (RAPID), which automatically generates, verifies, and refines robot programs, given a single visual human demonstration.
> The iterative agentic loop of code refinement requires several key ingredients: (i) a testable task specification,
> (ii) action primitives for robot execution, and
> (iii) an interactive environment for program execution and verification.
> RAPID infers all three from the demonstration automatically.
> To make the resulting program reusable beyond the demonstration setting, RAPID uses an object-centric relational program representation that focuses on the underlying structure of the demonstrated strategy rather than the specific motion per se: it expresses the action primitives as trajectory-optimization programs that realize object-level motion effects, while composing them through relational constraints that capture scene-specific geometry at run time.
> We evaluated RAPID in simulation on eight challenging contact-rich nonprehensile manipulation tasks as well as general prehensile manipulation tasks in the LIBERO-Pro benchmark.
> We also successfully deployed it on a real Franka arm and evaluated on all eight nonprehensile tasks.
> In all experiments, RAPID demonstrated strong performance, with generalization over object pose, shape, material, and environment.

作者提出 RAPID，目的是让机器人编程闭环所需的三项条件能够从一次示范中产生。示范和语言描述提供目标与接触过程，系统据此编写成功判据及操作原语，并重建能执行候选程序的仿真环境。程序通过反复测试和修改形成，再在筛选后的场景变体中接受验证。

泛化依赖两层表示。原语只要求某个对象效果，如移动指定距离或翻转指定角度，具体动作交给局部轨迹优化；策略则用对象关系连接阶段，运行时根据前一阶段的状态计算下一阶段参数。实验支持这套组合在八项非抓持任务中的场景泛化和 Franka 真机部署。LIBERO-Pro 是另一个无示范实验，不能将其结果写成一次示范学习的成绩。

## 论文主线

1. 机器人 coding agent（编程智能体）需要可测试目标、可执行动作和可交互环境，直接给它语言与控制 API 并不足以产生可靠接触行为。
2. 人类示范同时提供一个可行接触过程及其结果。RAPID 将其拆成局部目标、可执行判据与仿真场景，建立生成、执行、验证、修订的循环。
3. 固定坐标或固定时序难以跨场景复用。OReP 把对象角色与关系保存在程序中，将几何和动作求解留到具体场景中完成。
4. 单个场景验证仍可能过拟合。系统生成并过滤场景变体，在多个效果参数与场景上修改原语，再冻结原语、修改策略组合。
5. Table II 检验闭环、表示及变体的配合；Table III 检验抓持任务中的另一种输入条件；Fig. 5 检验仿真优化动作能否在真实接触中执行。

一句话总结：作者构造了一个从示范自动建立机器人编程与验证条件的系统，并用关系程序及轨迹优化保留示范策略的可迁移结构；主实验平均成功率为 75.9%，支持同一任务族内的场景泛化。

## 贡献与结论对照

| 贡献或结论 | 方法位置 | 直接证据 | 结论的范围 |
| --- | --- | --- | --- |
| 从一次示范建立编程闭环的三项条件 | Sec. III、V，Algorithm 1 | 八项任务不预先提供原语、成功信号或实例化仿真场景 | 使用既有感知模型、MuJoCo、机器人模型和控制 API |
| 原语以对象效果定义，动作由局部优化产生 | Sec. IV-A，Table I | 与 Python 程序基线的 Table II 对比 | 支持包含 CEM 的整体表示，不能分离单个组件贡献 |
| 用关系约束组合原语，冻结程序后跨场景实例化 | Sec. IV-B、IV-C，Fig. 3 | 每项任务在 50 个新场景中测试 | 同一任务族与可满足角色关系的新场景 |
| 变体验证改善泛化 | Sec. V、VI-B | 平均 0.759±0.024 对 0.532±0.071 | T1 无均值增益，T2 增益较小，并非所有任务收益相同 |
| 扩展到抓持任务及真机 | Sec. VI-C、VI-D | Table III，Fig. 5 | LIBERO-Pro 无示范；真机限于单一 Franka 平台 |

## 结构地图

原文共九页，主体为第 1–7 页，参考文献延续至第 9 页。下表列出 PDF 的章节结构。

| 原文章节 | 本节推进的论证 | 关键证据 / 图表 / 公式 |
| --- | --- | --- |
| I. Introduction | 提出缺少闭环条件的问题，以示范和关系表示回应 | Fig. 1、Fig. 2 |
| II. Related Work | 对照机器人编程、少示范学习与非抓持操作 | CaP、CaP-X、ASPIRE 等工作的位置 |
| III. Overview of RAPID | 规定输入、输出、任务族与构造/部署阶段 | 从 $(D,l)$ 到 $(\mathcal P,\Pi)$ 的映射 |
| IV. Object-Centric Relational Programs | 定义原语、组合约束、新场景绑定 | Table I、Fig. 3，原语与策略公式 |
| V. Agentic Programming from a Demonstration | 说明如何重建、验证并修订这些程序 | Algorithm 1 |
| VI. Experiments | 分别检验非抓持泛化、LIBERO-Pro 和真机 | Table II、Table III、Fig. 4、Fig. 5 |
| VII. Conclusion | 收束结论并提出灵巧手、RL、可变形仿真的后续方向 | 没有新增实验 |

## 按原文 section 精读

### I. Introduction

引言的核心问题是如何补足机器人编程的验证条件。普通软件可以运行测试；机器人代码还必须确定什么算任务成功、怎样把程序动作变成实际接触，以及在哪里反复执行候选动作。作者认为，现有机器人 coding-agent 系统常把成功信号、手工原语和可重置环境当作已给定条件。

人类示范提供的不是单纯动作坐标。它展示了环境接触如何使目标物体变得可抓取，并与语言描述一起表达目标。RAPID 因此从示范提取局部对象效果、任务判据和场景模型，给 agent 提供可反复测试的程序开发环境。

Nonprehensile manipulation（非抓持操作）是有针对性的测试范围。抓持任务常能调用 pick、move、place；推、翻转、绕支点转动和倾倒却依赖接触面及物体几何，很难用固定原语库覆盖。八项任务均从平行夹爪不能直接抓取的物体开始，检验 agent 是否能自行构造这些行为。

关键证据 / 图表 / 公式：Fig. 1 是示范到复用程序的定性展示；Fig. 2 给出完整机制。两图帮助理解研究目标，最终泛化幅度仍要由 Table II 与 Fig. 5 判断。

### II. Related Work

Programming for Robotics（机器人编程）一段从 Code as Policies 出发，区分生成程序、几何约束、奖励、仿真场景，以及带执行反馈的 agentic programming。CaP-X、ENPIRE、GaP、RoboRSI 是反馈闭环路线，Voyager 与 ASPIRE 强调技能积累。本文的区别是从示范建立任务相关的验证条件，而非仅在现成工具上写更长的程序。

Learning from Few Demonstrations（少示范学习）一段强调跨对象与跨场景时应保留任务结构。视觉对齐、对象对应、接触关系和原语分解都有先例；本文将对象效果与组合约束写成可被 agent 调试的程序，使表示与迭代验证共同作用。不能把所有对象中心抽象都视为 RAPID 首创。

Nonprehensile Manipulation 一段将本文放在接触力学、规划、轨迹优化和学习策略的交叉处。RAPID 仍使用物理仿真及优化，改变的是任务定义、原语构造与组合的生成方式。

关键证据 / 图表 / 公式：本节没有独立结果表。阅读重点是对照依赖条件；CaP-Agent0 和 ASPIRE 在后续实验中获得的成功反馈、原语与调试场景数量并不相同。

### III. Overview of RAPID

输入是单次视觉人类示范 $D$ 与语言描述 $l$，输出是可执行原语集合 $\mathcal P$ 和任务级策略 $\Pi$。任务族 $\mathcal E$ 中的目标相近，但对象外观、几何、位姿、物理属性与场景配置可以变化。问题限定为 quasi-static rigid-body manipulation（准静态刚体操作）。

$$
(D,l)\mapsto(\mathcal P,\Pi),\qquad
\Pi(E^\star,l^\star;\mathcal P)\text{ succeeds for }(E^\star,l^\star)\in\mathcal E.
$$

$E^\star,l^\star$ 是未见场景及其指令。这个表达式陈述目标，不是证明所有任务族成员都成功的定理。构造阶段先分段，再建立目标与环境、生成并验证原语，最后组成策略；部署阶段重建新场景，绑定角色，优化动作并在机器人上执行。

![[papers/images/liu2026rapid/method_page1.png|1000]]

Fig. 2. *Overview of RAPID.* $E$ 是从示范重建的环境，$P_i$ 是操作原语，$c_i$ 连接连续原语，$\Pi$ 是生成的策略程序。

左侧强调仿真反馈支持程序修改，中间强调原语优化与关系组合，右侧强调已有程序在新场景中的实例化。后两项使程序复用成为可能，左侧则检验程序是否真实产生期望接触效果。示范推导出的任务条件之外，基础感知工具和机器人控制接口仍由系统提供。

关键证据 / 图表 / 公式：映射式明确输入输出；Fig. 2 区分构造与部署。几秒的部署开销仅针对 semantic binding（语义绑定），不包含全部重建、优化和执行时间。

### IV. Object-Centric Relational Programs

#### IV-A. Primitives as Local Trajectory-Optimization Programs

每个 primitive（操作原语）要求一个对象效果，例如推动给定位移或翻转给定角度。原语包含五项内容：

$$
P_i=(G_i,C_i,\Psi_i,\rho_i,J_i)\in\mathcal P,\qquad
C_i=(\mathbf r_i,\Gamma_i,\mathbf q_i).
$$

$G_i$ 是语义目标，$C_i$ 是关系接口，$\Psi_i$ 是成功判据，$\rho_i$ 是几何解析器，$J_i$ 是优化代价。接口中的 $\mathbf r_i$ 声明对象角色，$\Gamma_i$ 声明角色之间必须成立的关系，$\mathbf q_i$ 声明效果参数的类型。角色声明与场景中的实际对象分开，效果参数声明与调用时的实际数值分开。

$$
b_i\in\operatorname{Bind}_E(\mathbf r_i,\Gamma_i),\qquad
g_i\in\operatorname{Val}(\mathbf q_i),\qquad
\phi_{i,t}=\rho_i(E,x_t,b_i),\quad t=0,\ldots,T.
$$

$b_i$ 是满足类型和关系要求的对象绑定，$g_i$ 是符合接口类型的效果值。$x_t\in\mathcal X(E)$ 为环境状态，$\phi_{i,t}$ 为本步解析的几何特征。这样，翻转所需的支撑面、夹具朝向和转轴能由具体场景确定，不必写死在示范坐标中。

Table I. *Local trajectory-optimization program for the primitive flip.*

| 组件 | 翻转原语的具体内容 |
| --- | --- |
| Semantic goal $G_i$ | 借助夹具将目标物体翻转指定角度 |
| Relational interface $C_i$ | 角色为目标物、支撑平面、夹具、操作器；物体位于支撑面上，夹具提供朝向物体且可达的竖直面；效果参数为翻转角度 |
| Success predicate $\Psi_i$ | 达到目标旋转角，物体仍有支撑、靠近夹具且已稳定 |
| Geometry resolver $\rho_i$ | 每步解析支撑面、夹具竖直面、翻转轴和目标物尺寸 |
| Final cost $J_i^{\mathrm f}$ | 惩罚终态角度误差、物体与夹具间距和终态速度 |
| Progress cost $J_i^{\mathrm p}$ | 鼓励旋转与操作器接近物体，抑制回退和不规则运动 |

成功判据在终态检查期望对象关系及效果：$\Psi_i(E,x_T;g_i,\phi_{i,T})\in\{0,1\}$。它与优化代价有不同用途。代价引导搜索，判据决定候选执行是否通过验证；代价低不能直接当作任务成功。

$$
J_i(E,\tau;g_i,\phi_{i,0:T})
=J_i^{\mathrm f}(E,x_T;g_i,\phi_{i,T})
+\lambda_iJ_i^{\mathrm p}(E,\tau;g_i,\phi_{i,0:T}),\quad\lambda_i\ge0.
$$

$\tau=(x_0,\ldots,x_T)$ 是完整仿真轨迹。终态项衡量期望效果的偏差，过程项可以依赖整段轨迹，用接触启发式帮助搜索。Agent 依据示范编写这些启发式，也提出基于几何与目标效果的初始化运动。

$$
\tau(z)=\operatorname{Rollout}_E(x_0,z),\qquad
z_i^\star=\arg\min_z J_i\!\left(E,\tau(z);g_i,\phi_{i,0:T}(z)\right).
$$

$z$ 参数化候选机器人运动，$\operatorname{Rollout}$ 在仿真中产生轨迹。CEM 通过采样搜索求解，避免对复杂接触仿真求导。原文没有给出运动参数化维度、采样规模、优化轮数或统一代价权重，不能据上述目标式复现全部优化设置。

关键证据 / 图表 / 公式：Table I 将抽象接口落实到翻转；代价式解释如何产生动作。这里的原语是带场景求解过程的程序，不能把泛化解释为固定示范轨迹的平移。

#### IV-B. Strategies as Primitive Composition by Constraints

策略明确调用顺序、对象角色映射与各次原语所需效果：

$$
\Pi=\left(G_\Pi,C_\Pi,\Psi_\Pi,
\left\langle(P_{i_k},m_k,c_k)\right\rangle_{k=1}^{K}\right),\qquad
C_\Pi=(\mathbf r_\Pi,\Gamma_\Pi).
$$

$G_\Pi$ 是总目标，$\Psi_\Pi$ 检查最终任务结果，$C_\Pi$ 暴露策略角色及关系。每个阶段选择原语 $P_{i_k}$、角色映射 $m_k$ 和连接约束 $c_k$。策略不要求调用者手动给出所有原语效果值，而是在每个阶段开始时求出它们。

$$
\begin{aligned}
b_k&=m_k(b)\in\operatorname{Bind}_E(\mathbf r_{i_k},\Gamma_{i_k}),\\
g_k&=c_k(E,s_{k-1},b)\in\operatorname{Val}(\mathbf q_{i_k}),\\
s_k&=\operatorname{Exec}(P_{i_k};E,s_{k-1},g_k,b_k).
\end{aligned}
$$

$b$ 是策略层绑定，$s_{k-1}$ 是上一阶段执行后的环境状态。$m_k$ 将策略角色映射到原语角色，$c_k$ 从实际阶段状态计算效果参数，$\operatorname{Exec}$ 求解该原语的局部轨迹优化并执行。

![[papers/images/liu2026rapid/program_page1.png|1000]]

Fig. 3. *Composing primitives by relational constraints.*

图中的翻转后接 press move（按压移动）是全文最具体的关系组合例子。`storage_displacement` 根据棕色障碍物和白色夹具形成的通道确定目标位置，再减去翻转后的物体位置，将差值投影到夹具轴向。固定的是寻找通道、计算位移、调用原语的程序结构；改变的是场景几何及由此求出的位移。

`flip` 的代价项包括角度误差、转轴漂移、夹具接触、违反支撑约束的程度和运动平滑性；`press_move` 则包含终态位置、朝向、工具接触、支撑与平滑性。这些是图中的示例项，Table I 与正文没有给出其全部数值权重。

关键证据 / 图表 / 公式：Fig. 3 和 $g_k=c_k(E,s_{k-1},b)$ 共同说明阶段依赖。本节定义的是环境状态驱动的程序执行；正文没有给出真机每阶段重新获取 RGB-D 并重建状态的协议，不能据此宣称已验证连续视觉纠错。

#### IV-C. Strategy Instantiation in Novel Scenes

新场景 $E^\star$ 与指令 $l^\star$ 到来后，coding agent 生成 $b^\star\in\operatorname{Bind}_{E^\star}(\mathbf r_\Pi,\Gamma_\Pi)$，把新对象分配给策略暴露的角色。随后策略自动计算各阶段的原语绑定及效果值。作者称角色绑定仅需几秒。

整个过程冻结 $\Pi$ 与其引用的原语。适应性来自语义绑定、关系约束和针对新几何及物理属性的轨迹优化。测试时重新绑定角色不等于重新学习整套任务程序，也不能据此推断新场景中会任意改变阶段顺序。

关键证据 / 图表 / 公式：冻结条件使 Table II 成为复用程序的场景泛化测试。绑定必须仍满足声明关系，物理上无法实现原任务的场景不在这一条件之内。

### V. Agentic Programming from a Demonstration

#### V-A. Reconstructing Interactive Environments

系统从示范的初始 RGB-D 帧重建环境。
VLM（视觉语言模型）识别对象、赋予语义标签并估计物理属性。SAM 3 根据语义名称取得 mask（分割掩码）。
RGB-D 与 mask 送入 SAM 3D，重建完整 mesh（网格）。FoundationPose 将网格配准到 RGB-D 帧，最后将对象和机器人模型组装进 MuJoCo。

这个环境提供程序执行所需的对象、几何与空间关系。质量依赖被遮挡形状的补全、位姿配准以及物理参数估计。作者用 VLM 先验估计质量、摩擦和恢复系数，未报告逐对象测量校准的误差。

Task-agnostic variation sampler（任务无关变体采样器）随机改变外观、尺寸、位姿、质量、摩擦与弹性。Agent 为每个原语或策略写过滤器，只接受保持角色关系、任务含义与物理可行性的变体。过滤可避免把无解场景当作程序失败，但正文未报告扰动范围、过滤通过率与验证场景数量。

关键证据 / 图表 / 公式：Algorithm 1 中的 `Reconstruct` 和 `Variants` 对应这两步。方法需要初始 RGB-D 及现成工具栈，不能泛化成仅靠任意二维网络视频即可重建全部验证条件。

#### V-B. Primitive Construction

分段 agent 将完整示范拆成有序片段 $(D_1,\ldots,D_K)$，为每段生成局部描述 $l_i$。若行为已由原语库覆盖，可以复用既有原语；否则推断 $G_i,\Psi_i$，识别示范中的接触机制、跨调用保持的关系及可变效果参数，再生成 $C_i,\rho_i,J_i$。

$$
\mathcal V_i=\{(g_i,\widehat E_i)\}\cup
\operatorname{Variants}(g_i,\widehat E_i,P_i).
$$

$\widehat E_i$ 是片段对应的重建环境，$g_i$ 是从示范推断的效果值。验证集不仅改变场景，也可以改变效果参数；每对参数与场景都用关联的 $\Psi_i$ 检查。失败轨迹和评价结果进入诊断修订，直至集合内所有执行成功，然后冻结原语并放入 $\mathcal P$。

关键证据 / 图表 / 公式：上式说明原语验证覆盖一组调用条件。通过有限集合中的自动判据意味着经验验证，不意味着形式化安全证明；判据本身的目标忠实性也是独立问题。

#### V-C. Strategy Composition

完整示范和描述给出 $G_\Pi,\Psi_\Pi$。片段顺序决定原语组合顺序，agent 为每阶段选择已验证原语、定义 $m_k$ 与 $c_k$。在重建环境 $\widehat E_0$ 及可行变体组成的 $\mathcal V_\Pi$ 上执行整套策略，失败后修改组合，原语保持冻结。

Algorithm 1. *RAPID.* 其关键步骤如下。

| 顺序 | 构造或验证操作 | 产物及冻结条件 |
| --- | --- | --- |
| 1 | 将 $(D,l)$ 分成 $(D_i,l_i)$ | 有序交互片段 |
| 2 | 重建 $\widehat E_i$，推断局部目标、判据和效果 | $G_i,\Psi_i,g_i$ |
| 3 | 生成原语，构造效果—环境变体验证集 | $P_i,\mathcal V_i$ |
| 4 | 执行、评价、诊断并修订原语 | 所有验证调用成功后冻结 $P_i$ |
| 5 | 重建完整任务初始环境并组合原语 | 初始策略 $\Pi$ |
| 6 | 在 $\mathcal V_\Pi$ 上执行、评价并修订组合 | 原语不变，成功后冻结策略 |

共享的 `VerifyRevise` 循环以 `AllSuccessful` 为停止条件。原文伪代码没有明确失败退出、最大修订次数或总计算上限。有限验证集通过后的外推能力由测试集评估，不应把停止条件改述为所有未来场景均可成功。

### VI. Experiments

#### VI-A. Experimental Setup for Nonprehensile Manipulation

八项任务都以不可直接抓取的目标物体开始；每项提供一次人类视觉示范与语言描述，原语未预先交给 agent。

| 任务 | 原文目标与阶段 | 主要几何或接触要求 |
| --- | --- | --- |
| T1 | 推向通道，更换接触面，再推入通道储存 | 两次推动与通道方向 |
| T2 | 推向夹具，翻转以暴露可抓边缘，再抓取 | 夹具接触与翻转角度 |
| T3 | 将物体移离障碍，推向夹具，翻转并抓取 | 避障位置、夹具和后续抓取关系 |
| T4 | 推向夹具，翻转，再调整位置以暴露边缘并抓取 | 翻转后的状态决定调整位移 |
| T5 | 推向夹具，翻转以对齐开口，再移入开口储存 | 姿态、开口与最终位置同时满足 |
| T6 | 绕接触点转动盒子以对齐通道，推近，再移入通道 | 方向对齐与多阶段通道进入 |
| T7 | 倾倒物体以暴露边缘，再抓取 | 倾倒接触及可抓状态 |
| T8 | 将物体移到平台边缘，露出可抓边缘，再抓取 | 物体与平台边缘的相对位置 |

![[papers/images/liu2026rapid/experiment_visualization_page1.png|800]]

Fig. 4. *Real-world execution of the solution trajectories found by RAPID.* 图中给出八项真实执行序列，说明各项任务包含什么接触阶段；它不是每项成功率的统计来源。

仿真基准在 MuJoCo 中使用 Franka Research 3 和 compliant operational-space controller（柔顺操作空间控制器）。每项构造 50 个新测试场景，改变物体位姿、外观、大小、形状及材质，并添加无关物体造成视觉干扰。任务成功由对 RAPID 隐藏的独立判据评估，实验重复三次，报告均值与标准差。

所有方法使用相同机器人控制 API。编程 agent 为 `Codex`，模型是 `GPT-5.6 Sol`，reasoning effort 为 high。三条对比轴分别是 Agent、OReP 和 SV。

| 方法 | 编程闭环 | 关系表示与 CEM | 场景变体 | 额外条件 |
| --- | --- | --- | --- | --- |
| CaP | 无 | 无 | 无 | 每个测试场景可重新生成 Python 程序，但不能用仿真反馈修改 |
| CaP + OReP | 无 | 有 | 无 | 允许相对对象表达动作，仍无程序验证闭环 |
| CaP-Agent0 | 有 | 无 | 无 | 构造时有真值成功信号、环境状态和图像；测试时还可 rollout 并修改程序 |
| CaP-Agent0 + SV | 有 | 无 | 有 | 在上述条件上增加变体模块 |
| RAPID w/o SV | 有 | 有 | 无 | 只在示范重建环境中验证 |
| RAPID | 有 | 有 | 有 | 由示范推断判据；冻结程序后跨场景测试 |

这里给予 CaP-Agent0 的反馈与测试时修改权限比 RAPID 更充分。作者未在非抓持任务上比较 ASPIRE，因为后者要求预先提供运动原语。这种设置有助于检验 RAPID 的整体表示，但没有构成计算预算完全匹配的对比。

#### VI-B. Simulation Experiments for Nonprehensile Manipulation

Table II. *Success rates on nonprehensile manipulation tasks in simulation.* 数值是三次实验的 mean±std，成功率范围为 0–1；下表保留全部任务与 Average 列。

| 方法 | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | Average |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CaP | 0.053±0.009 | 0.000±0.000 | 0.000±0.000 | 0.000±0.000 | 0.000±0.000 | 0.000±0.000 | 0.013±0.009 | 0.040±0.016 | 0.013±0.003 |
| CaP + OReP | 0.040±0.000 | 0.000±0.000 | 0.000±0.000 | 0.000±0.000 | 0.000±0.000 | 0.000±0.000 | 0.013±0.009 | 0.033±0.025 | 0.011±0.002 |
| CaP-Agent0 | 0.353±0.115 | 0.040±0.057 | 0.000±0.000 | 0.013±0.019 | 0.173±0.176 | 0.053±0.041 | 0.240±0.128 | 0.293±0.242 | 0.146±0.025 |
| CaP-Agent0 + SV | 0.440±0.141 | 0.053±0.009 | 0.020±0.028 | 0.047±0.066 | 0.113±0.034 | 0.080±0.059 | 0.167±0.066 | 0.087±0.096 | 0.126±0.043 |
| RAPID w/o SV | 0.933±0.009 | 0.833±0.125 | 0.400±0.161 | 0.440±0.315 | 0.447±0.256 | 0.340±0.236 | 0.567±0.229 | 0.293±0.415 | 0.532±0.071 |
| RAPID | 0.933±0.057 | 0.847±0.025 | 0.700±0.033 | 0.787±0.082 | 0.793±0.009 | 0.587±0.050 | 0.807±0.203 | 0.620±0.028 | 0.759±0.024 |

第一层结论是闭环必要性。CaP 与 CaP + OReP 平均仅为 1.3% 和 1.1%，即使给出关系表示和 CEM，一次性生成仍不能可靠建立接触程序。作者据此认为关系程序需要执行反馈帮助构造，而不是自动使任何生成程序都能泛化。

第二层结论是整体表示的作用。CaP-Agent0 即使得到真值成功反馈且可在测试场景继续修改，也只有 14.6% 平均成功率；RAPID 为 75.9%。作者观察到前者常用世界坐标系固定偏移和预设时序，后者按阶段状态计算几何相关子目标，并用优化表达翻转和倾倒。表格支持整体方法差距，未单独识别关系接口、CEM 或代价设计各自解释多少差距。

第三层结论是变体验证。去掉 SV 后，RAPID 均值从 75.9% 降到 53.2%，相差 22.7 个百分点；Average 的标准差从 0.024 升到 0.071。T1 均值相同，T2 只差 1.4 个百分点，T3–T8 才是主要增益来源。T7 的完整方法标准差仍达 0.203，说明平均较高并不意味着每次构造都稳定。

SV 对普通 Python agent 不产生同样结果，CaP-Agent0 + SV 平均为 12.6%，低于无 SV 的 14.6%。这是表示与变体验证需要配合的证据，不能写成任意 agent 增加随机场景都可受益。

每项程序只需构造一次，耗时约几十分钟；完成后，原语与策略保持冻结，用于 50 个新场景。正文未分解 token 用量、重建时间、CEM 总计算量和失败修订次数，也未给出三次实验随机性来源的完整说明。

#### VI-C. Simulation Experiments on LIBERO-Pro

LIBERO-Pro 在 LIBERO 上增强 position perturbation（位置扰动，Pos.）和 instruction perturbation（指令扰动，Task.）。任务主要为抓取放置和基于抓持的关节物体操作。VLA 基线 OpenVLA、$\pi_0$、$\pi_{0.5}$ 的成绩直接取自 LIBERO-Pro 论文；CaP 方法为 CaP-Agent0 与 ASPIRE。

该实验改变了输入条件。为与不使用示范的 CaP 方法比较，RAPID 也不接收示范，只获得任务描述和一个调试场景，通过探索与修订实现原语。ASPIRE 每任务使用 15 个调试场景；CaP 基线还有预定义抓取、放置和运输原语。本文结果因而检验程序表示与构造机制在另一种条件下是否可用。

Table III. *Experimental Results on LIBERO-Pro.* Pos. 与 Task. 的列值均为相应设置的平均成功率。

| 方法 | Object Pos. | Object Task. | Goal Pos. | Goal Task. | Spatial Pos. | Spatial Task. |
| --- | --- | --- | --- | --- | --- | --- |
| OpenVLA | 0 | 0 | 0 | 0 | 0 | 0 |
| $\pi_0$ | 0 | 0 | 0 | 0 | 0 | 0 |
| $\pi_{0.5}$ | 0.17 | 0.01 | 0.38 | 0 | 0.20 | 0.01 |
| CaP-Agent0 | 0.22 | 0.18 | 0.26 | 0.17 | 0.12 | 0.14 |
| ASPIRE | 0.98 | 0.95 | 0.81 | 0.45 | 0.51 | 0.60 |
| RAPID | 1.00 | 0.95 | 0.67 | 0.53 | 0.83 | 0.81 |

作者称 RAPID 在六个设置中五项最高。按数值细分，是四项单独最高、Object Task. 一项与 ASPIRE 并列最高，Goal Pos. 一项第二。Goal Pos. 的 0.67 低于 ASPIRE 的 0.81，作者归因于单一调试场景生成的抽屉开启等原语对位置变化较脆弱，而 ASPIRE 得到 `interpolate segment` 原语。

这里没有提供结果标准差、每列评估次数或统计显著性检验。表中某些 VLA 的零成功率是该扰动基准下的成绩，不能外推为这些模型在所有抓持任务上无能力。

#### VI-D. Real-World Experiments for Nonprehensile Manipulation

硬件为 Franka Research 3、平行夹爪和 Intel RealSense L515 RGB-D 相机。八项任务每项十个测试场景，只比较 RAPID 与 CaP-Agent0。

![[papers/images/liu2026rapid/experiment_setup_page1.png|500]]
![[papers/images/liu2026rapid/real_world_results_page1.png|800]]

Fig. 5. *Real-world experimental setup (left) and results (right).* Fig. 5 并列展示真实机器人硬件和各任务的成功率。

| 方法 | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CaP-Agent0 | 0.3 | 0 | 0 | 0 | 0.1 | 0.1 | 0.2 | 0 |
| RAPID | 0.9 | 0.8 | 0.7 | 0.6 | 0.7 | 0.4 | 0.7 | 0.6 |

按图中数值及每项十次试验计算，RAPID 为 54/80，即 67.5%，CaP-Agent0 为 7/80，即 8.75%。这是从 Fig. 5 计算的汇总，原文没有把这两个总平均写成独立结果。所有任务上 RAPID 均高于基线，但 T6 仅 4/10，说明真实接触中的多阶段泛化仍有失败。

作者认为关系程序与柔顺控制使仿真优化动作可以直接执行，VLM 估计的物理参数与 SAM 3D 重建有助于控制真实与仿真的差距。这是系统层面的解释；没有独立消融来测量感知、物理估计或控制器各自贡献。仿真和真机测试场景不同，不能直接用 75.9% 与 67.5% 的差值量化 sim-to-real gap。

关键证据 / 图表 / 公式：Fig. 4 展示接触序列，Fig. 5 给出硬件与逐任务统计。每项样本为十次，图中没有重复实验误差条或置信区间。

### VII. Conclusion

结论将贡献收束到从示范建立任务、动作和验证环境，再以关系程序保存可迁移的接触策略。八项任务支持对象与场景变化下的复用，LIBERO-Pro 与真机结果支持向其他操作类型和真实平台扩展。

作者提出将 reinforcement learning（强化学习）用于灵巧手原语，以及利用更好的 coding agents、机器人基础模型和支持可变形物体的仿真引擎扩展系统。这些是未来方向；本文未实验验证灵巧手、可变形物体或多本体部署。原文没有独立 Limitations 或附录章节。

## 方法细节

| 接口或状态 | 程序构造时确定什么 | 新场景中改变什么 |
| --- | --- | --- |
| 任务目标与判据 | $G_\Pi,\Psi_\Pi$ 及各 $G_i,\Psi_i$ | 输入实体和状态，程序定义保持冻结 |
| 原语接口 | 角色、关系要求、效果参数类型 | 具体对象绑定与调用效果值 |
| 几何解析与优化 | $\rho_i,J_i$ 及初始化启发式 | 几何特征、仿真轨迹和优化结果 |
| 策略组合 | 原语顺序、$m_k,c_k$ | 基于上一阶段状态计算参数 |
| 验证环境 | 从示范重建并采样可行变体 | 部署时从新 RGB-D 观察重建 |

需要区分三种反馈。构造阶段的 agentic loop 使用模拟执行失败来修改代码；实例化时的状态依赖用阶段状态生成效果参数；底层柔顺控制负责真实运动执行。正文没有将这三种反馈都定义成部署时的连续视觉代码修订。

## 实验设置、数据集、基线、指标

| 实验 | 数据与调试输入 | 测试规模及指标 | 泛化轴 |
| --- | --- | --- | --- |
| 八项非抓持仿真任务 | 每项一次人类示范与语言描述 | 每项 50 个新场景，三次实验，隐藏判据成功率 mean±std | 位姿、外观、大小、形状、材质、无关物体 |
| LIBERO-Pro | RAPID 无示范、一个调试场景；ASPIRE 15 个 | 三个套件各有 Pos. / Task. 两列平均成功率，本文未列试验次数 | 位置与语言指令扰动 |
| 八项真实非抓持任务 | 重建、仿真优化及 Franka 执行 | 每项十个测试场景，逐任务成功率 | 同类非抓持任务的真实场景变化 |

主实验是作者构建的 MuJoCo 基准，全文没有为其给出独立数据集名称、完整采样区间或发布文件清单。物理变体采样涵盖质量、摩擦与弹性，但实验未分别报告每条泛化轴的单因素性能。

## 主要结果、消融或对比

Table II 的最直接消融是 RAPID 与 RAPID w/o SV，识别变体验证在完整表示中的收益；CaP-Agent0 与其 +SV 版本则显示该收益不能脱离表示直接推广。CaP 与 CaP + OReP 说明关系接口及优化器在缺少验证闭环时仍不足以解决任务。

尚未单独消融连接约束、几何解析器、CEM、初始化启发式、自动判据、重建模型或物理参数估计。OReP 与 Python 的对比包含多个设计差异，证据支持整套关系优化表示，不能宣称某一个组件已经被证明是全部增益的原因。

## 图表、公式与表格线索

| 原文编号 | 内容 | 支撑的主张或回看重点 |
| --- | --- | --- |
| Fig. 1 | 一次示范与新对象/环境/指令执行 | 直观任务范围；定量效果要回看结果表 |
| Fig. 2 | 构造闭环、关系表示与部署实例化 | 区分代码修订阶段和冻结程序阶段 |
| Fig. 3 | `flip`、`press_move` 与位移计算 | 理解 $c_k$ 如何根据上一阶段状态计算下一阶段参数 |
| Fig. 4 | 八项真实执行序列 | 接触阶段和任务目标；不能替代成功率统计 |
| Fig. 5 | 硬件与八项真机成功率 | 十场景/任务的真机试验证据，T6 仍较弱 |
| Table I | 翻转原语六项内容 | 语义目标、接口、判据与代价的不同责任 |
| Table II | 六种方法、八项仿真任务 | 闭环、OReP 与 SV 的组合及消融 |
| Table III | 六种方法、六个 LIBERO-Pro 设置 | 无示范输入条件，Goal Pos. 为例外 |
| Algorithm 1 | 分段、原语冻结、组合修订 | 有限验证集上的停止条件 |

原文公式均未编号。核心顺序是 $P_i$ 与 $C_i$ 定义、运行时绑定、$\rho_i$、$\Psi_i$、$J_i$、$z_i^\star$，再到 $\Pi$ 和 $b_k,g_k,s_k$。符号 $\mathcal E$ 表示任务族，$E$ 表示具体环境，$\widehat E$ 表示重建环境，三者不能混用。完整本地图片列表见 [[papers/images/liu2026rapid/index]]。

## 主张-证据-边界矩阵

| 主张 | 实测证据或作者论证 | 证据位置 | 可支持的结论 | 边界 |
| --- | --- | --- | --- | --- |
| 一次示范能启动机器人编程闭环 | 自动推断目标、原语、环境；八项新场景测试 | Sec. III、V，Table II | 示范可替代任务相关条件的手工提供 | 依赖工具栈、RGB-D 和机器人模型 |
| 关系优化程序增强场景泛化 | RAPID 0.759，CaP-Agent0 0.146 | Table II | 整体表示与构造流程优于该 Python 基线 | 多组件差异，预算未完全配平 |
| 变体验证提高鲁棒性 | 无 SV 0.532，完整 0.759，平均标准差降低 | Table II | 完整方法受益于变体测试 | T1 无均值增益，T7 仍有较大波动 |
| 冻结程序仍可适应新场景 | 相同策略和原语用于每项 50 个新场景 | Sec. IV-C、VI-B | 角色绑定和轨迹求解支持任务族内迁移 | 不证明新任务序列或任意关系变化 |
| 能扩展到抓持任务 | 四项单独最高、一项并列最高 | Table III | 无示范调试条件下可构造抓持程序 | Goal Pos. 低于 ASPIRE；VLA 数据来自引用 |
| 仿真优化能真实部署 | 八项真机分别 0.4–0.9 成功率 | Fig. 5 | Franka 上接触行为具有可执行性 | 单本体、每项十次、无组件级迁移消融 |

## 局限与可追问点

- **目标与验证的可靠性。** Agent 同时生成程序和成功判据，验证可能接受目标描述的错误形式化。隐藏测试判据保护最终评分，但未给出生成判据与独立判据的一致性、误报或漏报统计。可追问是否固定判据后只修改动作代码，以及如何检查错误判据。
- **任务族与场景选择。** 程序保留示范阶段顺序，变体过滤要求角色和关系可满足。没有新目标结构、额外阶段或全新接触模式的测试。可追问筛掉多少场景、哪些几何关系变化会要求重构策略。
- **物理与感知依赖。** 完整网格与 VLM 参数估计影响优化可靠性；正文没有估计误差、校准精度或感知失败分解。可追问质量/摩擦偏差分别达到多少时策略失效，遮挡或非刚体会怎样影响接口。
- **计算与停止条件。** 每项构造几十分钟，只有语义绑定报告几秒。没有完整部署延迟、token 成本、CEM 开销和修订上限。可追问无法达到 `AllSuccessful` 时如何停止，以及能否检测部署前的无解场景。
- **统计与组件归因。** 主表仅三次实验，LIBERO-Pro 无标准差，真机每项十次。未有独立组件消融或置信区间。可追问 T7 的跨次波动、T6 的失败阶段及在匹配计算预算下的差距。
- **部署范围。** 已验证 Franka 平行夹爪的准静态刚体操作；灵巧手、可变形物体和跨本体仅是扩展方向。正文未报告执行中持续视觉更新、在线代码修订或完整扰动恢复协议。

这些边界中，LIBERO-Goal 的关节物体泛化不足由作者明确解释；其余主要是问题定义或实验报告留下的条件，不能写成作者已经测量过的失败结论。

## 与当前库的连接

- [[@xiao2026enpire|ENPIRE]] 也是本文 Related Work 直接引用的 coding-agent 路线。ENPIRE 组织真实机器人 reset、verification、rollout 与策略改进；RAPID 从示范重建仿真环境并修订操作程序。对读时比较反馈来源、验证条件由谁建立及物理试验成本。
- [[@zhou2026holoagent0|HoloAgent-0]] 侧重用空间记忆、技能图和执行调度组织系统。RAPID 更细地规定单个技能内部的对象效果及跨技能连接约束。可比较技能接口是否暴露角色关系、动作目标如何从场景状态产生。
- [[@jiang2026robottt|RoboTTT]] 同样涉及人类视频的一次性模仿。RoboTTT 将上下文写入 fast weights（快速权重），RAPID 将示范结构写入可冻结程序并重建仿真。比较的是适应信息存放位置与所需训练/工具条件，不是共享基准上的性能排名。

## 精读路线 / 为什么需要回看

1. 先读 Sec. III 与 Fig. 2，确认准静态刚体任务族、示范输入和构造/部署分工。后续引用一次示范结论时必须保留这些条件。
2. 重点读 Sec. IV-A 的 Table I 和代价式，再读 IV-B 的 Fig. 3。回看理由是区分对象效果、几何求解、动作优化和阶段连接，避免把关系程序写成抽象任务图。
3. 用 Algorithm 1 对照 Sec. V，追踪哪些判据和环境由 agent 生成、何时冻结原语、何时只改组合。这里决定闭环到底验证了什么。
4. 回看 Table II 的全部行，再分别看 Table III 和 Fig. 5。引用时保留三次实验、每项 50 个新仿真场景、无示范 LIBERO-Pro 与每项十次真机试验的不同口径。
5. 若要迁移方法，优先追问优化超参数、验证集大小、过滤范围和真实状态更新协议。论文给出清楚的表示与构造框架，但这些工程条件仍需要更多材料才能复现。
