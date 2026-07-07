---
tags:
  - bilingual-reading
paper: "[[@intelligence2025pi06-vla-that-learns]]"
source_pdf: "[[papers/pdfs/intelligence2025pi06-vla-that-learns.pdf]]"
images: "papers/images/intelligence2025pi06-vla-that-learns/"
image_index: "[[papers/images/intelligence2025pi06-vla-that-learns/index.md]]"
created: 2026-07-07
---

# π*0.6: a VLA That Learns From Experience（RECAP）

paper:: [[@intelligence2025pi06-vla-that-learns]]
pdf:: [[papers/pdfs/intelligence2025pi06-vla-that-learns.pdf]]
images:: [[papers/images/intelligence2025pi06-vla-that-learns/index.md]]

> 单位：Physical Intelligence（Levine, Finn, Hausman, Black, Pertsch 等）｜ arXiv:2511.14759v2（2025-11）｜ 主页：https://pi.website/blog/pistar06
> 备注：用户所说的 "pi0.7" 目前不存在；Physical Intelligence 最新公开 VLA 即本篇 **π\*0.6**（π0.6 的 RL 版本），故按此篇解析。

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| RECAP | 本文方法名 | RL with Experience and Corrections via Advantage-conditioned Policies，让 VLA 从经验中学的通用配方。 |
| π\*0.6 | 本文模型 | π0.6 的 RL 版本，能条件化于 advantage 指示器，可被价值函数改进。 |
| learn from experience | 从经验中学 | 不止用示范，还用**自主部署采集的经验数据**纠正真实部署中的错误。 |
| advantage conditioning | 优势条件化 | 把策略条件在“这动作是否优于参考策略”的二值指示器上，是本文可扩展 RL 的核心技巧。 |
| iterated offline RL | 迭代式离线 RL | 采一批数据→重训→重复；避开 on-policy PPO 的不稳定与不可扩展。 |
| distributional value function | 分布式价值函数 | 预测“到成功还剩多少步”的分布（201 bins），提供 advantage。 |
| expert interventions | 专家干预 | 自主执行中人类遥操纠偏（HG-DAgger 式），强制 I=True 加入数据。 |
| CFGRL | 分类器自由引导 RL | 本文优势条件化的理论近亲；训练同时建模 π(a\|o) 与 π(a\|I,o)。 |
| throughput | 吞吐量 | 每小时成功完成的任务数（兼顾成功率与速度），本文首要实用指标。 |
| KI recipe (Knowledge Insulation) | 知识隔离训练 | π0.6 的训练法：端到端训连续动作+离散 token，用 stop-gradient 隔离 flow-matching 动作专家。 |
| FAST tokenizer | FAST 动作分词 | 把动作 chunk 离散化成 token，与 flow matching 连续动作并行预测。 |
| action expert | 动作专家 | 860M 专用权重，用 flow matching 生成 50Hz 动作。 |
| flow matching | 流匹配 | 生成式连续动作建模；本文难点之一是让 RL 与它兼容。 |

## 摘要

本文研究 VLA 模型如何通过**真实世界部署 + 强化学习**自我改进。提出通用方法 **RECAP**（RL with Experience and Corrections via Advantage-conditioned Policies），用**优势条件化**为 VLA 做 RL 训练。方法把异构数据纳入自改进：示范、on-policy 自主采集数据、以及自主执行中专家遥操的干预。RECAP 先用**离线 RL 预训练**一个通用 VLA（称 **π\*0.6**），再通过在机采数据把它专门化到下游任务达到高性能。用完整 RECAP 训练的 π\*0.6 能在真实家庭里**叠各种衣物**、可靠**装配纸箱**、用专业咖啡机**做浓缩咖啡**。在一些最难任务上，RECAP 把**任务吞吐量翻倍**、**失败率约减半**。

## 论文主线

一句话锚定：**把“示范 + 自主经验 + 人类纠偏”三类异构数据，用一个可扩展的“优势条件化”技巧统一进 VLA 的（迭代）离线 RL 训练，让大模型 VLA 真正从部署经验里变得更稳更快——而不必依赖难扩展的 on-policy PPO。**

![[papers/images/intelligence2025pi06-vla-that-learns/fig1_recap_overview.png|780]]

**Figure 1 / RECAP 总览。** 起点是能做**优势条件化**的预训练 VLA（π\*0.6，含 high-level / low-level / action expert，输入 language + advantage）。对每个任务：部署模型采集**自主 rollouts + 在线人类纠正** → 用这些在线数据**微调价值函数**（VLM + value head，预测进展）→ 用更新后的 advantage 估计**微调并条件化 VLA** → 策略行为改进。整个 RL training 环由 “interventions and labeling” 驱动。

论证链条：

1. **问题定位**：模仿学习受**误差累积**限制、且最好只能与示范一样好。要更可靠更快，就得**超越离线示范的模仿**——让策略从它在部署中实际犯的错里学、超越人类遥操的速度、适应新部署条件。
2. **为什么难**：真机大模型 RL 面临——为大模型设计可扩展稳定的 RL、处理来自不同策略的异构数据、在奖励模糊/随机的真实世界搭 RL。此前工作要么用离散动作/简单高斯（不适配 flow matching VLA），要么用 on-policy PPO/REINFORCE（难扩展）。
3. **方法**：RECAP 用**优势条件化**做策略抽取——训练一个能同时表示 `π(a|o,ℓ)` 与 `π(a|I,o,ℓ)` 的策略（I=优势超阈的二值指示器），从**全部**（off-policy/离线）数据用监督式目标学习，避开策略梯度对 flow matching 的 log-likelihood 需求。配一个**分布式价值函数**估 advantage。
4. **实例化**：π\*0.6（基于 π0.6=π0.5 的升级：多机器人数据、Gemma3-4B 骨干、860M 动作专家），加“Advantage: positive/negative”文本条件。三阶段：离线 RL 预训练 → 下游 SFT（I 固定 True）→ 一或多轮在机采数据（自主+干预）迭代改进。
5. **结果**：难任务吞吐量 >2×、失败率约减半；多数任务 90%+ 成功率；能连续做咖啡 13 小时、在新家叠衣 2 小时。优势条件化显著优于 AWR 与 PPO。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| RECAP：在**全流程**（预训练→部署经验）注入 reward feedback 的通用 VLA-RL 配方。 | §IV，Algorithm 1。 | Fig 7/8（吞吐/成功率全面提升）。 | 强，跨三大真实任务。 |
| 优势条件化策略抽取，适配 flow-matching VLA、可用全部 off-policy 数据。 | §IV-B（Eq 2/3/4）。 | Fig 11（>> AWR/PPO）。 | 强，正面对比两主流抽取法。 |
| 分布式价值函数（steps-to-success）可靠判失败/进度。 | §IV-A（Eq 1）、§V-C（Eq 5）。 | Fig 4（价值函数可视化捕捉错误）。 | 中到强，定性可视化 + 端到端收益。 |
| 迭代式在机改进持续提升吞吐/成功率。 | §V-D、Algorithm 1 循环。 | Fig 9/10（多轮提升，box 2×）。 | 中到强，两任务两轮验证。 |
| 可用少量数据定向移除特定失败模式。 | §VI-C4。 | Fig 12（严格叠衣 97%，纯 RL 无干预）。 | 强，针对性消融。 |
| 达到实用鲁棒性水平。 | §VI。 | 咖啡 13h、叠衣 2h、工厂装箱。 | 中，长时演示为主。 |

## 结构地图

- **§I Introduction**：模仿学习的天花板；从经验学的挑战；RECAP 概述与 π\*0.6 定位；主结果口径。
- **§II Related Work**：在线干预（HG-DAgger）、真机 RL 自改进、VLA-RL（PPO/residual/action-head/noise-space）、reward/value conditioning（CFGRL）。定位=**端到端迭代离线 RL + 优势条件化 + flow-matching VLA**。
- **§III Preliminaries**：RL 记号、advantage 定义、正则化 RL 与 `π̂ ∝ π_ref·p(I|A)^β` 的改进保证。
- **§IV RECAP**：三子程序（数据采集 / 价值函数训练 Eq 1 / 优势条件化策略抽取 Eq 2-3）；(A) 分布式价值函数；(B) 优势条件化；(C) 方法总结 + Algorithm 1。
- **§V 实现/模型/系统**：(A) π0.6 模型（KI recipe、FAST、860M 动作专家、Gemma3-4B）；(B) π0.6→π\*0.6 的 advantage 条件化（Eq 4）；(C) 奖励与价值函数（Eq 5，201 bins，670M VLM）；(D) 预训练/采数据/从经验学（ε_ℓ=30% 分位、强制干预 I=True）。
- **§VI 实验**：任务（叠衣/咖啡/装箱）、基线（π0.5、π0.6、RL 预训练、offline RL+SFT、AWR、PPO）、吞吐/成功率、多轮、失败模式移除、抽取法对比。
- **§VII Discussion**：非全自主、探索朴素、迭代离线非全在线。

## 逐节精读

### §III–IV 方法核心 —— 用“优势条件化”把 RL 变成监督学习

本文最关键的技术判断：**大模型 flow-matching VLA 上做策略梯度很痛**（flow matching 没有可解 log-likelihood），而 AWR 类加权回归又**丢弃/降权大量数据**（等于过滤式模仿）。RECAP 的解法是**优势条件化**——不改损失结构，而是给策略加一个输入 I，表示“这动作是否优于参考策略”。训练时用**全部数据**做监督（既学 `π(a|o,ℓ)` 又学 `π(a|I,o,ℓ)`），推理时把 I 设为 True 就采到改进后的策略（对应 β=1），或用 CFG（β>1）进一步锐化。理论依据（§III）：`π̂(a|o)∝π_ref(a|o)·p(I|A^{π_ref}(o,a))^β` 保证 `J(π̂)≥J(π_ref)`。

**价值函数（§IV-A）**：分布式，`p_ϕ(V|o,ℓ)` 映射到 B=201 个离散 value bin，用蒙特卡洛回报的交叉熵训练（Eq 1）。它是行为策略 π_ref 的 on-policy 估计——作者选它是因为**简单可靠**，虽不如经典 off-policy Q 最优，但足以带来显著提升。

**策略抽取（§IV-B）**：改进指示器 `I_t=1[A^{π_ref}(o_t,a_t,ℓ)>ε_ℓ]`，作为文本 “Advantage: positive/negative” 输入。策略目标是 NLL（Eq 3）：`min E[-log π(a|o,ℓ) - α log π(a|I,o,ℓ)]`。对**人类纠正强制 I=True**（假设专家纠正总是好的）。连续动作用 flow matching loss、离散 FAST token 用似然，二者相加近似整体动作 log-likelihood 的下界（Eq 4）。

### §V 实现 —— π0.6 与 π\*0.6

- **π0.6**（源自 π0.5）：可用 flow matching 表示 chunked 动作、产中间文本做高层推理；用 **KI（Knowledge Insulation）** 端到端训连续动作 + FAST 离散 token，**stop-gradient** 防 flow-matching 动作专家污染其余模型；预训练含机器人数据 + 网络 VL 数据。相对 π0.5 改进：多机器人预训练数据、**Gemma3-4B** VLM 骨干、动作专家增至 **860M**。模型 `π_θ(a_{t:t+H}, ℓ̂ | o_t, ℓ)`：先预测下一子任务文本 ℓ̂ 再生成动作（高层指引），50Hz 关节+夹爪。
- **π0.6→π\*0.6**：加“Advantage: positive/negative”文本输入（位于 ℓ̂ 之后、动作之前，只影响动作 log-likelihood）；训练随机丢弃 I 以支持 CFG。
- **奖励/价值（§V-C，Eq 5）**：稀疏——成功末步 0、失败末步 −C_fail、其余 −1 → 价值=负的“到成功剩余步数”，按任务最大长度归一化到 (−1,0)。价值函数用更小 **670M** VLM 骨干、co-train 少量网络数据防过拟合；VLA 训练时**在线**推理价值函数算 advantage（成本很小）。ε_ℓ 取该任务价值分布的 **30% 分位**。
- **采数据（§V-D）**：先 SFT（I=True）得 π_ℓ^0 → 采自主 rollouts（部分由专家监控随时干预）→ 微调价值函数与策略（都从**预训练 checkpoint** 而非上一轮 finetune，避免多轮 drift）→ 可重复；实践中常一轮就显著提升。

### §VI 实验 —— 叠衣 / 咖啡 / 装箱

三大真实任务，每个 5–15 分钟、含受力操作/倒液体/布料纸板/多阶段。机器人=静态双臂（两 6-DoF 臂 + 平行夹爪，50Hz 关节位置，3 相机：base + 两 wrist）。

## 方法细节（实现口径）

- **算法**：迭代离线 RL；分布式价值函数（201 bins，MC，交叉熵）+ 优势条件化策略抽取（NLL，I 二值文本）。
- **模型**：π0.6（Gemma3-4B 骨干 + 860M flow-matching 动作专家 + FAST 离散 token + KI stop-gradient + 子任务 ℓ̂）；价值函数 670M VLM + value head。
- **关键超参**：ε_ℓ=30% 分位；β=1 默认（可 CFG β>1）；C_fail 大常数；价值归一化 (−1,0)。
- **数据/迭代**：预训练=数万小时多任务多机器人示范；T-shirt 折叠每轮 300 条×4 机器人、纯自主两轮；box 每轮 600 自主 + 360 干预、两轮。
- **对干预**：HG-DAgger 式，强制 I=True；整段（自主+干预）可选入 D_ℓ。

## 实验设置、数据集、基线、指标

- **任务**：Laundry（t-shirt/shorts；diverse 11 类，测最难的 button-up shirt；targeted failure removal=严格 collar-up 单橙 T 恤）；Cafe（double espresso，全流程 <200s）；Box assembly（工厂纸箱：flatten→组装→贴标→入筐，<600s）。
- **指标**：**throughput**（每小时成功数，兼顾成功率+速度）、**success rate**（人工标注）。
- **基线**：π0.5；π0.6（SFT，无 advantage）；RL 预训练 π\*0.6；π\*0.6 offline RL+SFT；π\*0.6（RECAP 全，默认 β=1，含自主+干预）；抽取法对比 **AWR**、**PPO**（DPPO/FPO 变体 + SPO 约束）。

## 主要结果、消融与对比

- **主结果（Fig 7/8）**：最终 π\*0.6 在所有任务上显著超过 base π0.6、RL 预训练 π\*0.6、offline RL+SFT。**diverse laundry 与 espresso 吞吐量翻倍以上**（从 offline RL+SFT 到最终模型，靠在机数据），失败率约减半。除 diverse laundry 外，最终成功率都在 **90%+**。box assembly 四阶段（取箱/成型/贴标/入筐）全阶段最高成功；多数失败因超时。
- **多轮迭代（Fig 9/10）**：T-shirt 仅用**自主数据（无人类纠正）**两轮，吞吐 +50%（成功率首轮已 90%+）；long-horizon box 需更多数据，第二轮后吞吐 **2×**，折叠+贴标 ~90%（600s 内）。
- **失败模式移除（Fig 12）**：严格 collar-up 叠衣，对抗性初始态，RECAP 两轮（每轮 600 条）**纯 RL、无干预无额外示范**达 **97%**——说明可用少量数据定向改行为。
- **抽取法对比（Fig 11）**：同数据下，RECAP 远超 **AWR**（成功率尚可但策略更慢、吞吐低）与 **PPO**（需小 trust-region η=0.01 才稳，但性能上不去）。
- **实用性**：espresso 连续 13 小时、新家叠新衣 2 小时不中断、工厂真实装箱。

## 图表、公式与表格线索

- **Fig 1**：RECAP 训练环（已嵌入）。
- **Fig 3**：π\*0.6 VLA 与价值函数在 RECAP 中的交互（KI recipe、advantage 指示器）。
- **Fig 4**：价值函数可视化——正确识别叠衣成功/开冰箱失败中的错误与进度。
- **Fig 7/8**：吞吐/成功率主结果。
- **Fig 9/10**：多轮迭代提升。
- **Fig 11**：RECAP vs AWR/PPO。
- **Fig 12**：定向移除失败模式（97%）。
- **Eq 1**：分布式价值函数交叉熵。 **Eq 2/3**：优势条件化改进策略与 NLL 目标。 **Eq 4**：离散+连续动作 log-likelihood 下界。 **Eq 5**：steps-to-success 稀疏奖励。 **Algorithm 1**：完整迭代流程。

## 主张-证据-边界矩阵

| 主张 | 证据 | 边界 / 可质疑处 |
| --- | --- | --- |
| RECAP 让 VLA 从经验中显著改进。 | Fig 7/8（吞吐 2×、失败减半）。 | 三任务、单一双臂平台；奖励标注/干预/复位仍需人。 |
| 优势条件化优于策略梯度/加权回归。 | Fig 11（>> AWR/PPO）。 | 对比用 RECAP 采的数据（对基线略有利仍胜，但数据分布偏 RECAP）。 |
| 价值函数可靠。 | Fig 4 可视化。 | on-policy MC 估计非最优；奖励=稀疏成功标签，模糊成功判定下如何？ |
| 迭代持续改进。 | Fig 9/10。 | 仅两任务两轮；box 首轮吞吐先降后升，收敛性未充分刻画。 |
| 可定向移除失败模式。 | Fig 12（97%）。 | 单一严格任务；泛化到多失败模式并存时如何？ |

## 局限与可追问点

作者在 §VII 明确：
1. **非全自主**：仍靠人类做奖励标注、干预、复位；如何自动化（如用高层策略自动复位/打标）是关键。
2. **探索朴素**：基本贪心，靠策略随机性 + 人类干预探索；更强探索方法有大空间。
3. **迭代“离线”而非全在线**：采一批→重训→重复，而非并发在线 RL；全并发在线是有前景方向。

可继续追问：
- advantage 指示器只二值（正/负）+ ε_ℓ 阈值——更细粒度的 advantage 分档是否更好？CFG β 的收益/风险边界？
- 价值函数是 on-policy MC 估计，作者也承认可扩展到 off-policy Q——off-policy 化能否进一步提升样本效率？
- 奖励=稀疏 episode 成功标签，需人工判定——能否用 VLA 自身或价值函数自动判成功以去人力？
- 与 HIL-SERL 相比，π\*0.6 把“纠正+RL”推到 VLA 尺度，但也继承了“需要人类纠正/标注”的成本——真正 scalable 的自改进离“零人力”还有多远？

## 与当前库的连接

- 与 [[@luo2024precise-dexterous-robotic-manipulation|HIL-SERL]] 是**同一 Levine/Berkeley 谱系、同一核心思想（demos + 人类纠正 + RL）的两代**：HIL-SERL=**小模型、单任务、从零真机 RL**；π\*0.6/RECAP=把 experience+corrections 推广到**大规模通用 VLA**（优势条件化 + 价值函数 + 迭代离线 RL），并直接引用 HG-DAgger。两篇对读=“真机 RL 从 skill-level 到 foundation-model-level”。
- 基于 **π0.5/π0.6**：这与本库多篇共享底座——[[@pan2026vla-corrector-lightweight-detect|VLA-Corrector]] 以 π0.5 为主骨干、[[@wang2026vlk-learning-humanoid-loco|VLK]] 从 π0.5 初始化。π\*0.6 展示了“同一底座 + RL 后训练”的另一条改进路径（推理期纠正 vs 训练期 RL vs 数据生成）。
- 与 [[@xiao2026enpire|ENPIRE]]（自改进/物理自动研究）、[[@yu2026wm-dagger|WM-DAgger]]（世界模型合成 recovery）同题“让策略从错误变强”，路径分别是：RL+人类纠正 / 自动研究 / 世界模型。
- 地图归属：`#map/具身智能/VLA/经验强化学习自改进`（本文新开轴）。

## 精读路线 / 为什么需要回看

- **只想抓核心**：读 §I → Fig 1 → §IV-B 优势条件化（为什么把 RL 变成带 I 的监督）→ Fig 7/8/11。
- **要理解算法**：§III（改进保证）+ §IV（Eq 1-3）+ Algorithm 1 + §V-C（Eq 5 奖励）。
- **要复现/实现**：§V 全部（KI、FAST、860M 动作专家、670M 价值函数、ε_ℓ=30%、β=1/CFG）+ 附录 C–F。
- **判断可信度**：Fig 11（vs AWR/PPO）+ Fig 12（定向移除 97%）+ 多轮 Fig 9/10。
- **回看触发条件**：当你要在**大 VLA** 上做真机 RL 自改进、或想把“人类纠正”从 skill-level（HIL-SERL）搬到 foundation 尺度时，回到 §IV–V。

## 一句话总结

Physical Intelligence **提出并验证** RECAP：用“优势条件化”把示范、自主经验、人类纠偏三类异构数据统一进 flow-matching VLA 的迭代离线 RL，从而绕开 on-policy PPO 的不可扩展；据此把 π0.6 训成能从部署经验中自我改进的 π\*0.6，在真实叠衣/做咖啡/装箱上把最难任务吞吐量翻倍、失败率约减半，并证明优势条件化显著优于 AWR/PPO——是把 HIL-SERL 式“纠正 + RL”思想推到通用 VLA 尺度的代表作。
