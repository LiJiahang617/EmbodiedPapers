---
tags:
  - bilingual-reading
  - deep-reading
source_pdf: "[[papers/pdfs/xiao2026rove.pdf]]"
paper: "[[@xiao2026rove]]"
images: "papers/images/xiao2026rove/"
image_index: "[[papers/images/xiao2026rove/index.md]]"
created: 2026-07-11
generator: "setting/scripts/generate_reading_draft.py"
reading_standard: "fba534d bilingual full-reading"
extraction: "pypdf"
source_pages: 19
source_chars: 53745
---

# ROVE: Unlocking Human Interventions for Humanoid Manipulation via Reinforcement Learning

paper:: [[@xiao2026rove]]
pdf:: [[papers/pdfs/xiao2026rove.pdf]]
images:: [[papers/images/xiao2026rove/index.md]]
reading:: [[papers/bilingual/xiao2026rove_中英混读.md]]

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| Vision-Language-Action | 视觉-语言-动作模型 | 把视觉观测、语言指令和机器人动作统一到一个策略模型中。 |
| task progress | 相对进展 | 判断两个时间点之间任务推进了多少。 |
| trajectories | 时间/轨迹建模 | 利用帧序列和历史上下文理解任务进展或未来结果。 |
| tactile | 触觉/接触信号 | 提供 RGB 难以看到的滑移、卡滞、接触法线和局部形变信息。 |
| Success Rate | 成功率 | 机器人任务中最直接的结果指标，但需要结合任务难度和评估协议读。 |
| Vision-Language-Action（VLA） | 论文专有缩写 | 论文用括号定义的专有缩写，此处已从上文完整写法还原；回看首次出现可核对精确定义。 |
| ROVE | 论文专有缩写 | 论文中多次出现的缩写，需结合首次出现位置确认完整含义和作用。 |
| Optimistic Value Estimation（OVE） | 论文专有缩写 | 论文用括号定义的专有缩写，此处已从上文完整写法还原；回看首次出现可核对精确定义。 |
| IIL | 论文专有缩写 | 论文中多次出现的缩写，需结合首次出现位置确认完整含义和作用。 |
| Markov Decision Process（MDP） | 论文专有缩写 | 论文用括号定义的专有缩写，此处已从上文完整写法还原；回看首次出现可核对精确定义。 |

## 摘要

Human interventions provide crucial corrective signals for post-training Vision-Language-Action (VLA) models. However, enabling seamless humanoid interventions is a formidable systems challenge due to complex whole-body kinematics and dexterous-hand control. Consequently, the collected intervention trajectories are often suboptimal, and methods that rely on human interventions as expert supervision can absorb hesitant, inefficient, or even erroneous behaviors. To address both the system and algorithmic challenges, we propose ROVE, a reinforcement learning framework for humanoid VLA post-training with imperfect human interventions. First, ROVE introduces a human-in-the-loop pipeline capable of collecting deployment and intervention data for humanoid manipulation. Second, it utilizes Optimistic Value Estimation (OVE) to prioritize high-value behaviors from mixed-quality trajectories. To further robustify value estimation, we incorporate cross-embodiment human experience videos to provide rich supervision for long-tailed failure and recovery modes. The resulting critic yields informative advantage signals, steering the VLA actor to focus on high-value behaviors rather than indiscriminately imitating all actions. On challenging real-world contact-rich and fine-grained humanoid manipulation tasks, ROVE outperforms experience-learning baselines and consistently improves across multiple rollout-intervention iterations.

中文解读：本文的核心定位需要结合 Introduction 与 Method 进一步确认。

这部分不是把摘要简单翻译成中文，而是先抓住作者的写作动作：作者通常先指出现有方法在哪个环节失效，再提出一个机制、模型、数据集或系统，最后用 benchmark、真实机器人或 ablation 证明它确实补上了这个缺口。

## 人工校订重点解读

### ROVE 真正解决的 learning problem

普通 interactive imitation learning 默认 human takeover 是 expert action。Humanoid manipulation 中这个假设很危险：操作者接管后要先重新对齐全身姿态和灵巧手，期间包含 hesitation、adaptation 甚至 mistake。ROVE 因而不直接复制所有 intervention actions，而学习 state value 来判断哪些片段真正推动 task progress。

![[papers/images/xiao2026rove/framework_page1.png|700]]

完整闭环是：部署 VLA actor 收集 autonomous rollout；临近失败时 human takeover；把轨迹拆为 rollout/adaptation/recovery；用机器人数据与每任务 180 条第一视角 human videos 训练 critic；用 critic 计算 action-chunk advantage 并作二值 conditioning；更新 actor 后进入下一轮收集。选择 $V(s)$ 而不是 $Q(s,a)$ 很关键，因为人类视频没有与机器人同构的 action space，但视觉状态进度仍可共享。

### OVE 为什么不是简单的 Monte Carlo value

Optimistic Value Estimation 对 bootstrapped target 使用 expectile loss。$\tau=0.5$ 退化为 mean regression；$\tau$ 趋近 1 时更偏向数据中实际出现过的高价值 continuation。因此它是 in-distribution optimism：从 mixed-quality trajectories 中传播较好的 recovery，而不外推未观察动作。随后以 $A_t=\hat V_t-V(s_t)$ 判断 action chunk 是推动还是损害进度。

边界选择影响标签质量。擦白板任务中默认 $H=16$、失败惩罚放在 adaptation 结束处为 80%；把 horizon 拉长至 50 降至 65%，再把惩罚提前到 intervention start 仅 50%。这说明 adaptation 不能粗暴并入 recovery，否则 OVE 会把“乐观”传播到噪声动作。

### 结果应怎样读

![[papers/images/xiao2026rove/policy_improvement_page1.png|700]]

三轮迭代后，Erase the whiteboard 从 45.0% 升至 80.0%，Put the bread into the toaster 从 56.7% 升至 86.7%。这比单轮 baseline 胜负更重要：结果支持“更好 policy 收集更有信息的 experience，critic 再提供更清晰 advantage”的闭环。证据边界是只有两个任务、一个 humanoid 和成功率指标，不能直接外推到通用 humanoid RL。

## 论文主线

如果用一条线串起全文，可以这样读：

1. **问题入口**：从 Introduction 回看作者如何定义失败模式、任务缺口和评价目标。
2. **方法钩子**：方法机制需要从 Method / Model / Architecture 章节继续细化。
3. **证据出口**：证据链需要从 Experiments / Evaluation / Results 章节继续细化。
4. **引言铺垫的读法**：
- 这句话在铺设论文问题入口：它帮助读者理解为什么这件事值得做。
  原文线索：`Vision-Language-Action (VLA) models provide a promising foundation for general-purpose robot policies by grounding language instructions and visual observations into actions [1, 2]...`
- （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）
  原文线索：`Most re- cent progress has been largely demonstrated on robot-arm manipulation with parallel-jaw grippers, while extending VLA to humanoid robots with dexterous hands substantially...`
- （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）
  原文线索：`This inherent complexity makes the humanoid robot fragile to accumulated errors stemming from whole-body poses, systematic errors, object contacts, etc.`
- 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。
  原文线索：`As a result, VLA policies trained only on offline demonstrations often fail to reach satisfactory performance during deployment, struggling to handle deployment-time distribution s...`
- 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。
  原文线索：`Conse- quently, we seek a post-training solution to harness the deployment data for policy improvement.`

阅读时要盯住一个问题：作者的方法机制是否真的直接解决了引言中定义的失败模式，还是只是给同一问题换了更大的模型或更多的数据。

## 贡献与结论对照

| 贡献 / 结论 | 方法位置 | 证据 / 结论 |
| --- | --- | --- |
| 定义核心问题 | Abstract / Introduction |  |
| 提出主要方法或系统 | Method / Model / Architecture | 3 Methodology Fig. 3 summarizes the overall ROVE framework. The method first collects mixed-quality real-world experience on the humanoid robot, then learns a state-value critic from robot trajectories and human experience videos, and finally uses the resulting advantage signals to extract a stronger VLA policy. We describe these components in order. 3.2 Value function training Data recipe and pretraining objective.The value function is trained in stages. We first pretrain the critic on large-scale robot and egocen... |
| 通过实验验证主张 | Experiments / Evaluation / Results | Success Rate - Multi-IterationErase whiteboard (Contact-rich) (Right) It outperforms all baselines and consistently improves across multiple iterations. performs experience-learning baselines and consistently improves across multiple quently, we seek a post-training solution to harness the deployment data for policy improvement. |
| 暴露适用边界 | Discussion / Limitations / failure cases | 需要回看作者是否承认失败案例、数据边界或部署限制。 |

## 结构地图

| 原文位置 | 作者在这一部分做什么 | 与全文主线的关系 | 关键图表 / 公式 |
| --- | --- | --- | --- |
| 1 Introduction | 定义任务、指出现有方法缺口，并把读者带到本文的核心主张。 | 回答为什么要做。 | Figure 1: ROVE learns from imperfect humanoid interventions.(Left) Our method recovers task progress through re-matching...<br>Fig. 1, ROVE improves upon SFT and experience-learning baselines, including RL and IIL meth- ods, and continues to gain... |
| 2 Preliminary | 建立前人工作和技术背景，说明本文方法为什么有必要。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 3 Methodology | 给出方法机制，是判断论文贡献是否成立的主要位置。 | 回答怎么做。 | Fig. 1, ROVE improves upon SFT and experience-learning baselines, including RL and IIL meth- ods, and continues to gain...<br>Fig. 3 summarizes the overall ROVE framework. The method first collects mixed-quality real-world experience on the human... |
| 3.1 Human-in-the-loop data collection | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | Figure 1: ROVE learns from imperfect humanoid interventions.(Left) Our method recovers task progress through re-matching...<br>Figure 2: Task procedures forPut the bread into the toaster(top) andErase the whiteboard(bottom). 2 Preliminary Problem... |
| 3.2 Value function training | 给出方法机制，是判断论文贡献是否成立的主要位置。 | 回答怎么做。 | Figure 1: ROVE learns from imperfect humanoid interventions.(Left) Our method recovers task progress through re-matching...<br>Figure 2: Task procedures forPut the bread into the toaster(top) andErase the whiteboard(bottom). 2 Preliminary Problem... |
| 3.3 Policy improvement and implementation details | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | Algorithm 1ROVE: Iterative policy improvement Require: Initial policyπ θ0, initial actor and critic data buffersD actor... |
| 4 Experiments | 提供经验证据，需要重点核对指标、baseline、ablation 和真实部署设置。 | 回答是否有效。 | 待回看 PDF 图表 |
| 4.1 Policy improvement results and analysis | 提供经验证据，需要重点核对指标、baseline、ablation 和真实部署设置。 | 回答是否有效。 | Figure 1: ROVE learns from imperfect humanoid interventions.(Left) Our method recovers task progress through re-matching...<br>Fig. 1, ROVE improves upon SFT and experience-learning baselines, including RL and IIL meth- ods, and continues to gain... |
| 4.2 Value estimation analysis | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | Fig. 1, ROVE improves upon SFT and experience-learning baselines, including RL and IIL meth- ods, and continues to gain...<br>Fig. 3 summarizes the overall ROVE framework. The method first collects mixed-quality real-world experience on the human... |
| 5 Related work | 建立前人工作和技术背景，说明本文方法为什么有必要。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 6 Conclusion | 收束主张，并指出方法产出和后续方向。 | 回答边界和意义。 | 待回看 PDF 图表 |
| 7 Limitations | 说明适用边界、失败模式或作者对结果的解释。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |

## 按原文 section 精读

### 1. 1 Introduction

#### 高层故事流

定义任务、指出现有方法缺口，并把读者带到本文的核心主张。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

Vision-Language-Action（视觉-语言-动作模型）、trajectories（时间/轨迹建模）、tactile（触觉/接触信号）

#### 原文内容讲解

这一节要按“回答为什么要做。”来读。定义任务、指出现有方法缺口，并把读者带到本文的核心主张。

术语上先抓住 Vision-Language-Action（视觉-语言-动作模型）、trajectories（时间/轨迹建模）、tactile（触觉/接触信号）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这句话在铺设论文问题入口：它帮助读者理解为什么这件事值得做。

2. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

3. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

4. 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。

图表读法：本节出现的图题/表题应当放回对应段落看，重点确认它是在展示 architecture、data pipeline、main result 还是 ablation。

#### 关键原文线索

- `Vision-Language-Action (VLA) models provide a promising foundation for general-purpose robot policies by grounding language instructions and visual observations into actions [1, 2].`
- `Most re- cent progress has been largely demonstrated on robot-arm manipulation with parallel-jaw grippers, while extending VLA to humanoid robots with dexterous hands substantially increases the com- plexity of the robot...`
- `This inherent complexity makes the humanoid robot fragile to accumulated errors stemming from whole-body poses, systematic errors, object contacts, etc.`
- `As a result, VLA policies trained only on offline demonstrations often fail to reach satisfactory performance during deployment, struggling to handle deployment-time distribution shift.`

#### 回看重点

- 缺口是否具体到可验证的失败模式，而不只是泛泛说现有方法不足。
- 作者给出的 motivating example 是否会在实验中被直接覆盖。
- 术语复查：Vision-Language-Action（视觉-语言-动作模型）, trajectories（时间/轨迹建模）, tactile（触觉/接触信号） 在本节是否有明确变量、模块或实验定义。
- 图表复查：把图题/表题对应到正文 claim，确认图中数值或示意是否真的支撑该 claim。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| Vision-Language-Action (VLA) models provide a promising foundation for general-purpose robot policies by grounding language instructions and visual observations into actions [1, 2]... | 这句话在铺设论文问题入口：它帮助读者理解为什么这件事值得做。 | 1 Introduction | 注意是否被后续实验直接验证。 |
| Most re- cent progress has been largely demonstrated on robot-arm manipulation with parallel-jaw grippers, while extending VLA to humanoid robots with dexterous hands substantially... | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 1 Introduction | 注意是否被后续实验直接验证。 |
| This inherent complexity makes the humanoid robot fragile to accumulated errors stemming from whole-body poses, systematic errors, object contacts, etc. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 1 Introduction | 注意是否被后续实验直接验证。 |
| As a result, VLA policies trained only on offline demonstrations often fail to reach satisfactory performance during deployment, struggling to handle deployment-time distribution s... | 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。 | 1 Introduction | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| Fig. | 1 Introduction | Fig. 1, ROVE improves upon SFT and experience-learning baselines, including RL and IIL meth- ods, and continues to gain performance over multiple rollout-intervention iterations. Our main contributions are summarized as... | 支撑本节的方法、实验或定性解释。 |
| Figure | 1 Introduction | Figure 2: Task procedures forPut the bread into the toaster(top) andErase the whiteboard(bottom). | 支撑本节的方法、实验或定性解释。 |


### 2. 2 Preliminary

#### 高层故事流

建立前人工作和技术背景，说明本文方法为什么有必要。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

VLA（视觉-语言-动作模型）、trajectories（时间/轨迹建模）

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。建立前人工作和技术背景，说明本文方法为什么有必要。

术语上先抓住 VLA（视觉-语言-动作模型）、trajectories（时间/轨迹建模）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

2. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

3. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

4. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

#### 关键原文线索

- `ROVE starts from a generalist VLA model as the initial policya t:t+H−1 ∼π(·|s t), st = (o t, l),o t ∈ O, l∈ L,His the action chunk horizon.`
- `We can define the discounted cu- mulative reward, or return, asR(ξ) = PT t=0 γtrt.`
- `The goal of RL is to maximize the expected discounted return:J(π) =E ξ∼ρπ [R(ξ)] =E ξ∼ρπ [PT t=0 γtrt].`
- `Value estimation.For a policyπ, the value functionV π(st)is the expected future return Eξt+1:T [PT i=t γi−tri].`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：VLA（视觉-语言-动作模型）, trajectories（时间/轨迹建模） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| ROVE starts from a generalist VLA model as the initial policya t:t+H−1 ∼π(·|s t), st = (o t, l),o t ∈ O, l∈ L,His the action chunk horizon. | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 2 Preliminary | 注意是否被后续实验直接验证。 |
| We can define the discounted cu- mulative reward, or return, asR(ξ) = PT t=0 γtrt. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 2 Preliminary | 注意是否被后续实验直接验证。 |
| The goal of RL is to maximize the expected discounted return:J(π) =E ξ∼ρπ [R(ξ)] =E ξ∼ρπ [PT t=0 γtrt]. | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 2 Preliminary | 注意是否被后续实验直接验证。 |
| Value estimation.For a policyπ, the value functionV π(st)is the expected future return Eξt+1:T [PT i=t γi−tri]. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 2 Preliminary | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| Equation | 2 Preliminary | `Decision Process (MDP)M: (S,A,P, r, γ)in a standard RL setting [8], whereS= (O,L),` | 定义变量关系、训练目标或推理过程。 |
| Equation | 2 Preliminary | `robot’s task instruction.Ais the action space of the robot,P:S × A →∆(S)is the stochas-` | 定义变量关系、训练目标或推理过程。 |
| Equation | 2 Preliminary | `tic dynamics of the environment,r:S × A →Ris the reward function, the discount factor` | 定义变量关系、训练目标或推理过程。 |
| Equation | 2 Preliminary | `st = (o t, l),o t ∈ O, l∈ L,His the action chunk horizon. Given the robot policy` | 定义变量关系、训练目标或推理过程。 |


### 3. 3 Methodology

#### 高层故事流

给出方法机制，是判断论文贡献是否成立的主要位置。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

VLA（视觉-语言-动作模型）、trajectories（时间/轨迹建模）

#### 原文内容讲解

这一节要按“回答怎么做。”来读。给出方法机制，是判断论文贡献是否成立的主要位置。

术语上先抓住 VLA（视觉-语言-动作模型）、trajectories（时间/轨迹建模）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

图表读法：本节出现的图题/表题应当放回对应段落看，重点确认它是在展示 architecture、data pipeline、main result 还是 ablation。

#### 关键原文线索

- `The method first collects mixed-quality real-world experience on the humanoid robot, then learns a state-value critic from robot trajectories and human experience videos, and finally uses the resulting advantage signals...`

#### 回看重点

- 输入、隐藏表示、训练目标和输出之间是否闭合。
- 每个新增模块是否有对应 ablation 或对照实验支撑。
- 术语复查：VLA（视觉-语言-动作模型）, trajectories（时间/轨迹建模） 在本节是否有明确变量、模块或实验定义。
- 图表复查：把图题/表题对应到正文 claim，确认图中数值或示意是否真的支撑该 claim。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| The method first collects mixed-quality real-world experience on the humanoid robot, then learns a state-value critic from robot trajectories and human experience videos, and final... | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 3 Methodology | 需要后续实验或 ablation 证明该机制不可替代。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| Fig. | 3 Methodology | Fig. 3 summarizes the overall ROVE framework. The method first collects mixed-quality real-world experience on the humanoid robot, then learns a state-value critic from robot trajectories and human experience videos, and... | 支撑本节的方法、实验或定性解释。 |


### 4. 3.1 Human-in-the-loop data collection

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

VLA（视觉-语言-动作模型）、task progress（相对进展）、trajectories（时间/轨迹建模）

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

术语上先抓住 VLA（视觉-语言-动作模型）、task progress（相对进展）、trajectories（时间/轨迹建模）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是本文的贡献声明：要看作者提出的是新模型、新数据、新训练目标、新评测，还是系统集成。

2. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

3. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

4. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

图表读法：本节出现的图题/表题应当放回对应段落看，重点确认它是在展示 architecture、data pipeline、main result 还是 ablation。

#### 关键原文线索

- `Pipeline overview.We build a human-in-the-loop data collection pipeline that enables whole-body intervention during VLA policy rollouts.`
- `Each episode starts with autonomous execution, where the VLA policy predicts action chunks conditioned on the ego-view observation, task instruction, and proprioceptive state.`
- `When the supervisor detects a potential failure, the VLA action publisher is paused.`
- `Meanwhile, the motion-capture operator observes the robot state through a VR headset and aligns their body and hand pose with the current humanoid and dexterous hand configuration as closely as possible.`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：VLA（视觉-语言-动作模型）, task progress（相对进展）, trajectories（时间/轨迹建模） 在本节是否有明确变量、模块或实验定义。
- 图表复查：把图题/表题对应到正文 claim，确认图中数值或示意是否真的支撑该 claim。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| Pipeline overview.We build a human-in-the-loop data collection pipeline that enables whole-body intervention during VLA policy rollouts. | 这是本文的贡献声明：要看作者提出的是新模型、新数据、新训练目标、新评测，还是系统集成。 | 3.1 Human-in-the-loop data collection | 注意是否被后续实验直接验证。 |
| Each episode starts with autonomous execution, where the VLA policy predicts action chunks conditioned on the ego-view observation, task instruction, and proprioceptive state. | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 3.1 Human-in-the-loop data collection | 注意是否被后续实验直接验证。 |
| When the supervisor detects a potential failure, the VLA action publisher is paused. | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 3.1 Human-in-the-loop data collection | 注意是否被后续实验直接验证。 |
| Meanwhile, the motion-capture operator observes the robot state through a VR headset and aligns their body and hand pose with the current humanoid and dexterous hand configuration... | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 3.1 Human-in-the-loop data collection | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| Figure | 3.1 Human-in-the-loop data collection | Figure 3: Overview of ROVE framework. A VLA actor collects autonomous rollouts and triggers whole-body human intervention near failure. The resulting trajectories are decomposed into rollout, adaptation, and recovery sta... | 支撑本节的方法、实验或定性解释。 |
| Equation | 3.1 Human-in-the-loop data collection | `0, t=Tand the episode succeeds,` | 定义变量关系、训练目标或推理过程。 |
| Equation | 3.1 Human-in-the-loop data collection | `Cfail, t=Tand an autonomous rollout fails,` | 定义变量关系、训练目标或推理过程。 |
| Equation | 3.1 Human-in-the-loop data collection | `Cfail, t=t r at the end of the adaptation stage,` | 定义变量关系、训练目标或推理过程。 |
| Equation | 3.1 Human-in-the-loop data collection | `Cfail =−500. During pretraining, we setC fail to the negative mean episode length of each task,` | 定义变量关系、训练目标或推理过程。 |


### 5. 3.2 Value function training

#### 高层故事流

给出方法机制，是判断论文贡献是否成立的主要位置。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

task progress（相对进展）、trajectories（时间/轨迹建模）

#### 原文内容讲解

这一节要按“回答怎么做。”来读。给出方法机制，是判断论文贡献是否成立的主要位置。

术语上先抓住 task progress（相对进展）、trajectories（时间/轨迹建模）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

2. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

3. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

4. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

图表读法：本节出现的图题/表题应当放回对应段落看，重点确认它是在展示 architecture、data pipeline、main result 还是 ablation。

#### 关键原文线索

- `Data recipe and pretraining objective.The value function is trained in stages.`
- `We first pretrain the critic on large-scale robot and egocentric human demonstrations [10] to learn a general notion of task progress, then fine-tune it for the downstream task.`
- `In later iterations, we train the critic on au- tonomous rollouts and intervention trajectories, with task-relevant human experience videos.`
- `These videos provide cross-embodiment examples of recovery and completion that are sparse in robot ex- perience, improving value estimates on partial-progress and near-failure states.`

#### 回看重点

- 输入、隐藏表示、训练目标和输出之间是否闭合。
- 每个新增模块是否有对应 ablation 或对照实验支撑。
- 术语复查：task progress（相对进展）, trajectories（时间/轨迹建模） 在本节是否有明确变量、模块或实验定义。
- 图表复查：把图题/表题对应到正文 claim，确认图中数值或示意是否真的支撑该 claim。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| Data recipe and pretraining objective.The value function is trained in stages. | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 3.2 Value function training | 注意是否被后续实验直接验证。 |
| We first pretrain the critic on large-scale robot and egocentric human demonstrations [10] to learn a general notion of task progress, then fine-tune it for the downstream task. | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 3.2 Value function training | 注意是否被后续实验直接验证。 |
| In later iterations, we train the critic on au- tonomous rollouts and intervention trajectories, with task-relevant human experience videos. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 3.2 Value function training | 注意是否被后续实验直接验证。 |
| These videos provide cross-embodiment examples of recovery and completion that are sparse in robot ex- perience, improving value estimates on partial-progress and near-failure stat... | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 3.2 Value function training | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| Figure | 3.2 Value function training | Figure 4: Policy improvement results on two real-world humanoid manipulation tasks. ROVE (Ours) outperforms SFT in the demonstration-only setting, achieves the best average performance among experience-learning methods,... | 支撑本节的方法、实验或定性解释。 |
| Equation | 3.2 Value function training | `LMC(ϕ) =E (st,ξ)∼D` | 定义变量关系、训练目标或推理过程。 |
| Equation | 3.2 Value function training | `LOVE(ϕ) =E (st,ξ)∼D` | 定义变量关系、训练目标或推理过程。 |
| Equation | 3.2 Value function training | `τ= 0.5, the objective reduces to standard mean regression; asτapproaches1, the critic places` | 定义变量关系、训练目标或推理过程。 |


### 6. 3.3 Policy improvement and implementation details

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

VLA（视觉-语言-动作模型）、task progress（相对进展）

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

术语上先抓住 VLA（视觉-语言-动作模型）、task progress（相对进展）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是证据线索：读的时候要核对 baseline、指标、任务覆盖和统计口径。

2. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

3. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

4. 这是数据或实验设置线索：重点看数据来源、标注协议、任务分布和真实部署边界。

#### 关键原文线索

- `The VLA actor is trained with advantage conditioning to indicate whether an action chunk is pre- dicted to improve task progress.`
- `In each iteration, we update critic and actor sequentially: train the critic withD critic k , compute advantage statistics on Dactor k , assign binary advantage via a threshold, and fine-tune the actor (details in Append...`
- `Our experiments use the IRON-R01-1.11 humanoid robot with a50-dimensional proprioceptive state and action space covering body joints and dexterous hands.`
- `With limited task-specific robot data, conditioning on the high-dimensional proprioceptive state can overfit to brittle joint-level cues.`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：VLA（视觉-语言-动作模型）, task progress（相对进展） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| The VLA actor is trained with advantage conditioning to indicate whether an action chunk is pre- dicted to improve task progress. | 这是证据线索：读的时候要核对 baseline、指标、任务覆盖和统计口径。 | 3.3 Policy improvement and implementation details | 需要看提升是否来自公平 baseline、足够任务覆盖和同等数据/算力。 |
| In each iteration, we update critic and actor sequentially: train the critic withD critic k , compute advantage statistics on Dactor k , assign binary advantage via a threshold, an... | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 3.3 Policy improvement and implementation details | 注意是否被后续实验直接验证。 |
| Our experiments use the IRON-R01-1.11 humanoid robot with a50-dimensional proprioceptive state and action space covering body joints and dexterous hands. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 3.3 Policy improvement and implementation details | 注意是否被后续实验直接验证。 |
| With limited task-specific robot data, conditioning on the high-dimensional proprioceptive state can overfit to brittle joint-level cues. | 这是数据或实验设置线索：重点看数据来源、标注协议、任务分布和真实部署边界。 | 3.3 Policy improvement and implementation details | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 7. 4 Experiments

#### 高层故事流

提供经验证据，需要重点核对指标、baseline、ablation 和真实部署设置。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“回答是否有效。”来读。提供经验证据，需要重点核对指标、baseline、ablation 和真实部署设置。

可以把正文拆成下面几步：

1. 这句话在提供实验论证：它需要和表格、图和 baseline 对照读。

2. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

#### 关键原文线索

- `Our experiments are conducted in two real-world humanoid manipulation tasks: a contact-rich task (Erase the whiteboard) and a fine-grained task (Put the bread into the toaster).`
- `The analysis is organized around two aspects: policy improvement and value estimation.`

#### 回看重点

- 数据集、baseline、指标和样本量是否足以支撑摘要中的强结论。
- 主结果之外是否有 failure cases、消融和真实机器人验证。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| Our experiments are conducted in two real-world humanoid manipulation tasks: a contact-rich task (Erase the whiteboard) and a fine-grained task (Put the bread into the toaster). | 这句话在提供实验论证：它需要和表格、图和 baseline 对照读。 | 4 Experiments | 注意是否被后续实验直接验证。 |
| The analysis is organized around two aspects: policy improvement and value estimation. | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 4 Experiments | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 8. 4.1 Policy improvement results and analysis

#### 高层故事流

提供经验证据，需要重点核对指标、baseline、ablation 和真实部署设置。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

VLA（视觉-语言-动作模型）、task progress（相对进展）、success rate（成功率）

#### 原文内容讲解

这一节要按“回答是否有效。”来读。提供经验证据，需要重点核对指标、baseline、ablation 和真实部署设置。

术语上先抓住 VLA（视觉-语言-动作模型）、task progress（相对进展）、success rate（成功率）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这句话在提供实验论证：它需要和表格、图和 baseline 对照读。

2. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

3. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

4. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

图表读法：本节出现的图题/表题应当放回对应段落看，重点确认它是在展示 architecture、data pipeline、main result 还是 ablation。

#### 关键原文线索

- `Learn from demonstrations.We fine-tune the pretrained VLA with either standard SFT or ROVE using teleoperated demonstrations.`
- `4 shows that ROVE improves over SFT on both tasks.`
- `This suggests that humanoid teleoperation demonstrations can be suboptimal due to the teleoperation gap and operator variability, and that value-guided extraction recovers higher-quality behavior than uniform imitation.`
- `Learn from experience.We compare ROVE with experience-learning baselines, including HG- DAgger [5], Filtered BC, and RECAP [3] (details in Appendix E).`

#### 回看重点

- 数据集、baseline、指标和样本量是否足以支撑摘要中的强结论。
- 主结果之外是否有 failure cases、消融和真实机器人验证。
- 术语复查：VLA（视觉-语言-动作模型）, task progress（相对进展）, success rate（成功率） 在本节是否有明确变量、模块或实验定义。
- 图表复查：把图题/表题对应到正文 claim，确认图中数值或示意是否真的支撑该 claim。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| Learn from demonstrations.We fine-tune the pretrained VLA with either standard SFT or ROVE using teleoperated demonstrations. | 这句话在提供实验论证：它需要和表格、图和 baseline 对照读。 | 4.1 Policy improvement results and analysis | 注意是否被后续实验直接验证。 |
| 4 shows that ROVE improves over SFT on both tasks. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 4.1 Policy improvement results and analysis | 注意是否被后续实验直接验证。 |
| This suggests that humanoid teleoperation demonstrations can be suboptimal due to the teleoperation gap and operator variability, and that value-guided extraction recovers higher-q... | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 4.1 Policy improvement results and analysis | 注意是否被后续实验直接验证。 |
| Learn from experience.We compare ROVE with experience-learning baselines, including HG- DAgger [5], Filtered BC, and RECAP [3] (details in Appendix E). | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 4.1 Policy improvement results and analysis | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| Figure | 4.1 Policy improvement results and analysis | Figure 5: Human experience improves value estimation. Adding human experience helps the critic assign lower values to incomplete erasing states and better reflect true task progress. Erase Fail t = 9.0s t = 7.7s | 支撑本节的方法、实验或定性解释。 |
| Figure | 4.1 Policy improvement results and analysis | Figure 6: OVE provides sharper value estimates than Monte-Carlo estimates, producing clearer negative-advantage regions during failure and recovery. with RECAP, the remaining gap reflects the combined effect of critic qu... | 支撑本节的方法、实验或定性解释。 |
| Fig. | 4.1 Policy improvement results and analysis | Fig. 4, ROVE consistently improves across three iterations on both tasks. The success rate increases from 45.0% to 80.0% onErase the whiteboard, and from 56.7% to 86.7% onPut the bread into the toaster. This demonstrates... | 支撑本节的方法、实验或定性解释。 |
| Equation | 4.1 Policy improvement results and analysis | `t = 9.0s` | 定义变量关系、训练目标或推理过程。 |
| Equation | 4.1 Policy improvement results and analysis | `t = 7.7s` | 定义变量关系、训练目标或推理过程。 |


### 9. 4.2 Value estimation analysis

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

task progress（相对进展）、trajectory（时间/轨迹建模）

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

术语上先抓住 task progress（相对进展）、trajectory（时间/轨迹建模）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

2. 这是数据或实验设置线索：重点看数据来源、标注协议、任务分布和真实部署边界。

3. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

4. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

#### 关键原文线索

- `We then examine the value function behind policy gains, focusing on how human experience and optimistic value estimation affect the reliability and resolution of value estimates.`
- `5 compares two critics trained with and without human experience videos on the same held-out trajectory.`
- `Without human experience, the critic tends to overestimate inter- mediate states where the robot only partially erases the handwriting.`
- `In contrast, the critic trained with human experience assigns lower values to these incomplete states and produces a value curve that better follows actual task progress.`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：task progress（相对进展）, trajectory（时间/轨迹建模） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| We then examine the value function behind policy gains, focusing on how human experience and optimistic value estimation affect the reliability and resolution of value estimates. | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 4.2 Value estimation analysis | 注意是否被后续实验直接验证。 |
| 5 compares two critics trained with and without human experience videos on the same held-out trajectory. | 这是数据或实验设置线索：重点看数据来源、标注协议、任务分布和真实部署边界。 | 4.2 Value estimation analysis | 注意是否被后续实验直接验证。 |
| Without human experience, the critic tends to overestimate inter- mediate states where the robot only partially erases the handwriting. | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 4.2 Value estimation analysis | 注意是否被后续实验直接验证。 |
| In contrast, the critic trained with human experience assigns lower values to these incomplete states and produces a value curve that better follows actual task progress. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 4.2 Value estimation analysis | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 10. 5 Related work

#### 高层故事流

建立前人工作和技术背景，说明本文方法为什么有必要。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

VLA（视觉-语言-动作模型）、trajectories（时间/轨迹建模）

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。建立前人工作和技术背景，说明本文方法为什么有必要。

术语上先抓住 VLA（视觉-语言-动作模型）、trajectories（时间/轨迹建模）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

2. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

3. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

4. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

#### 关键原文线索

- `Reinforcement learning for VLA post-training.Reinforcement learning has become a key route for improving VLA policies beyond imitation-only tuning.`
- `Prior work spans simulation-scale on- policy RL [14, 15], real-world experience learning with advantage conditioning [3], world-model- based policy improvement [16, 17, 18, 19], and fleet-scale offline-to-online adaptati...`
- `Col- lectively, these results establish the importance of learning from deployment experience for VLA improvement.`
- `ROVE extends this paradigm to real-world humanoid manipulation with dexterous hands, where higher embodiment complexity makes experience distributions noisier and critic ro- bustness more critical than in robot-arm setti...`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：VLA（视觉-语言-动作模型）, trajectories（时间/轨迹建模） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| Reinforcement learning for VLA post-training.Reinforcement learning has become a key route for improving VLA policies beyond imitation-only tuning. | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 5 Related work | 注意是否被后续实验直接验证。 |
| Prior work spans simulation-scale on- policy RL [14, 15], real-world experience learning with advantage conditioning [3], world-model- based policy improvement [16, 17, 18, 19], an... | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 5 Related work | 注意是否被后续实验直接验证。 |
| Col- lectively, these results establish the importance of learning from deployment experience for VLA improvement. | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 5 Related work | 注意是否被后续实验直接验证。 |
| ROVE extends this paradigm to real-world humanoid manipulation with dexterous hands, where higher embodiment complexity makes experience distributions noisier and critic ro- bustne... | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 5 Related work | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 11. 6 Conclusion

#### 高层故事流

收束主张，并指出方法产出和后续方向。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

VLA（视觉-语言-动作模型）

#### 原文内容讲解

这一节要按“回答边界和意义。”来读。收束主张，并指出方法产出和后续方向。

术语上先抓住 VLA（视觉-语言-动作模型）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

2. 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。

3. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

4. 这是证据线索：读的时候要核对 baseline、指标、任务覆盖和统计口径。

#### 关键原文线索

- `We presented ROVE, an RL framework for post-training humanoid VLA policies from demonstra- tions, autonomous rollouts, human interventions, and human experience videos.`
- `The core challenge is that humanoid teleoperation data are not uniformly expert, especially during intervention.`
- `We address this with stage-aware intervention labeling, an optimistic state-value critic learned from het- erogeneous experience, and advantage-conditioned actor training.`
- `Real-world experiments show that ROVE improves over SFT, compares favorably with experience-learning baselines, and contin- ues to improve over rollout-intervention iterations.`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：VLA（视觉-语言-动作模型） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| We presented ROVE, an RL framework for post-training humanoid VLA policies from demonstra- tions, autonomous rollouts, human interventions, and human experience videos. | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 6 Conclusion | 注意是否被后续实验直接验证。 |
| The core challenge is that humanoid teleoperation data are not uniformly expert, especially during intervention. | 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。 | 6 Conclusion | 注意是否被后续实验直接验证。 |
| We address this with stage-aware intervention labeling, an optimistic state-value critic learned from het- erogeneous experience, and advantage-conditioned actor training. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 6 Conclusion | 注意是否被后续实验直接验证。 |
| Real-world experiments show that ROVE improves over SFT, compares favorably with experience-learning baselines, and contin- ues to improve over rollout-intervention iterations. | 这是证据线索：读的时候要核对 baseline、指标、任务覆盖和统计口径。 | 6 Conclusion | 需要看提升是否来自公平 baseline、足够任务覆盖和同等数据/算力。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 12. 7 Limitations

#### 高层故事流

说明适用边界、失败模式或作者对结果的解释。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

tactile（触觉/接触信号）

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。说明适用边界、失败模式或作者对结果的解释。

术语上先抓住 tactile（触觉/接触信号）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

2. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

3. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

4. 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。

#### 关键原文线索

- `First, human experience is currently used only for value learning, not for direct policy learning.`
- `Future work could use representation-level supervision to let policies benefit from human videos.`
- `Second, our system lacks end-effector sensing such as wrist cameras and tactile feedback, which limits precise manipulation.`
- `Third, we have not yet extended ROVE to loco-manipulation.`

#### 回看重点

- 作者承认的边界是否覆盖数据分布、模型规模、传感器/embodiment 和部署条件。
- 术语复查：tactile（触觉/接触信号） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| First, human experience is currently used only for value learning, not for direct policy learning. | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 7 Limitations | 注意是否被后续实验直接验证。 |
| Future work could use representation-level supervision to let policies benefit from human videos. | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 7 Limitations | 注意是否被后续实验直接验证。 |
| Second, our system lacks end-effector sensing such as wrist cameras and tactile feedback, which limits precise manipulation. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 7 Limitations | 注意是否被后续实验直接验证。 |
| Third, we have not yet extended ROVE to loco-manipulation. | 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。 | 7 Limitations | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


## 方法细节

方法部分要拆成四个问题读：

1. **输入是什么**：视觉、语言、动作、触觉、历史轨迹或环境状态分别如何进入模型。
2. **中间表示是什么**：token、latent、memory、value、reward、future state 或 action chunk 是否有明确语义。
3. **训练目标是什么**：监督信号来自人工标注、时间顺序、自监督、world model prediction、diffusion denoising 还是 behavior cloning。
4. **输出如何使用**：输出是 action、future video、value score、progress reward、skill graph，还是只作为下游模块的条件。

当前方法线索：

3 Methodology Fig. 3 summarizes the overall ROVE framework. The method first collects mixed-quality real-world experience on the humanoid robot, then learns a state-value critic from robot trajectories and human experience videos, and finally uses the resulting advantage signals to extract a stronger VLA policy. We describe these components in order. 3.2 Value function training Data recipe and pretraining objective.The value function is trained in stages. We first pretrain the critic on large-scale robot and egocentric human demonstrations [10] to learn a general notion of task progress, then fine-tune it for the downstream task. In later iterations, we train the critic on au- tonomous rollouts and intervention trajectories, with task-relevant human experience videos. These videos provide cross-embodiment examples of recovery and completion that are sparse in robot ex- perience, improving value estimates on partial-progress and near-failure states. For pretraining, we use a Monte-Carlo regression objective to fit the cumulative return from each state: LMC(ϕ) =E (st,ξ)∼D   Vϕ(st)− TX i=t γi−tri !2  .(3) This objective estimates the average return of the dataset behavior distribution. It is stable for large- scale pretraining on heterogeneous data from different tasks and embodiments, and provides a robust initialization for task-level fine-tuning. Optimistic value estimation.For fine-tuning, however, estimating only the average return can be overly conservative. Our training data contain many suboptimal teleoperated behaviors, failed autonomous rollouts, and transient adaptation segments after takeover. If the critic simply averages over these trajectories, the estimated value can be much lower than the value of the best recoverable behavior from the same state. To a...

公式 / 数学定义线索：

- `Decision Process (MDP)M: (S,A,P, r, γ)in a standard RL setting [8], whereS= (O,L),`
- `robot’s task instruction.Ais the action space of the robot,P:S × A →∆(S)is the stochas-`
- `tic dynamics of the environment,r:S × A →Ris the reward function, the discount factor`
- `st = (o t, l),o t ∈ O, l∈ L,His the action chunk horizon. Given the robot policy`
- `ξ= (s 0, a0, r1, s1,· · ·, aT−1 , rT , sT )∈ S × A ×R· · · Sthrough interactions between the policy`
- `mulative reward, or return, asR(ξ) = PT`
- `t=0 γtrt. The goal of RL is to maximize the expected`
- `discounted return:J(π) =E ξ∼ρπ [R(ξ)] =E ξ∼ρπ [PT`


## 实验设置、数据集、基线、指标

读实验时不要只看最终分数，要按 `数据集 -> baseline -> 指标 -> 主结果 -> 消融 -> 失败案例` 走。

实验正文线索：

- 这句话在提供实验论证：它需要和表格、图和 baseline 对照读。 原文线索：`4 Experiments Our experiments are conducted in two real-world humanoid manipulation tasks: a contact-rich task (Erase the whiteboard) and a fine-grained task (Put the bread into th...`
- 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 原文线索：`The analysis is organized around two aspects: policy improvement and value estimation.`
- （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） 原文线索：`4.1 Policy improvement results and analysis Learn from demonstrations.We fine-tune the pretrained VLA with either standard SFT or ROVE using teleoperated demonstrations.`
- （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） 原文线索：`4 shows that ROVE improves over SFT on both tasks.`
- （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） 原文线索：`This suggests that humanoid teleoperation demonstrations can be suboptimal due to the teleoperation gap and operator variability, and that value-guided extraction recovers higher-q...`
- （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） 原文线索：`Learn from experience.We compare ROVE with experience-learning baselines, including HG- DAgger [5], Filtered BC, and RECAP [3] (details in Appendix E).`
- 这是证据线索：读的时候要核对 baseline、指标、任务覆盖和统计口径。 原文线索：`4 shows that ROVE achieves the best average success rate across tasks.`
- （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） 原文线索：`A notable result is that HG-DAgger performs poorly, even below the base demonstration-only policy on one task, and its learned policy often exhibits hesitant behavior.`

指标 / 结果句线索：

- Success Rate - Multi-IterationErase whiteboard (Contact-rich)
- (Right) It outperforms all baselines and consistently improves across multiple iterations.
- performs experience-learning baselines and consistently improves across multiple
- quently, we seek a post-training solution to harness the deployment data for policy improvement.
- post-training methods for VLA have shown that the deployment experience can improve pretrained
- treated as expert supervision or positive improvement signals.
- 1, ROVE improves upon SFT and experience-learning baselines, including RL and IIL meth-
- policy improvement in real-world tasks.Real-world experiments on two manipulation tasks, il-
- 2, show that ROVE improves VLA policies from demonstrations, experience, and
- perience, improving value estimates on partial-progress and near-failure states.
- Figure 4:Policy improvement results on two real-world humanoid manipulation tasks.ROVE
- (Ours) outperforms SFT in the demonstration-only setting, achieves the best average performance


## 主要结果、消融或对比

| 证据类型 | 原文线索 | 读法 |
| --- | --- | --- |
| 图表/表格 | Figure 1: ROVE learns from imperfect humanoid interventions.(Left) Our method recovers task progress through re-matching and re-erasing. (Middle) Human interventions after near-failure VLA rollouts can deviate from ideal corrections in humanoid manipulation; o... | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Fig. 1, ROVE improves upon SFT and experience-learning baselines, including RL and IIL meth- ods, and continues to gain performance over multiple rollout-intervention iterations. Our main contributions are summarized as follows:(i) Human-in-the-loop data colle... | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Figure 2: Task procedures forPut the bread into the toaster(top) andErase the whiteboard(bottom). 2 Preliminary Problem setting and notation. We formulate the humanoid manipulation problem as a Markov Decision Process (MDP)M: (S, A, P, r, γ)in a standard RL se... | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Fig. 3 summarizes the overall ROVE framework. The method first collects mixed-quality real-world experience on the humanoid robot, then learns a state-value critic from robot trajectories and human experience videos, and finally uses the resulting advantage si... | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Figure 3: Overview of ROVE framework. A VLA actor collects autonomous rollouts and triggers whole-body human intervention near failure. The resulting trajectories are decomposed into rollout, adaptation, and recovery stages, and combined with cross-embodiment... | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Figure 4: Policy improvement results on two real-world humanoid manipulation tasks. ROVE (Ours) outperforms SFT in the demonstration-only setting, achieves the best average performance among experience-learning methods, and consistently improves across multipl... | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Figure 5: Human experience improves value estimation. Adding human experience helps the critic assign lower values to incomplete erasing states and better reflect true task progress. Erase Fail t = 9.0s t = 7.7s | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Figure 6: OVE provides sharper value estimates than Monte-Carlo estimates, producing clearer negative-advantage regions during failure and recovery. with RECAP, the remaining gap reflects the combined effect of critic quality and advantage assign- ment of post... | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 结果句 | Success Rate - Multi-IterationErase whiteboard (Contact-rich) | 核对 baseline、样本量、任务覆盖和统计口径。 |
| 结果句 | (Right) It outperforms all baselines and consistently improves across multiple iterations. | 核对 baseline、样本量、任务覆盖和统计口径。 |
| 结果句 | performs experience-learning baselines and consistently improves across multiple | 核对 baseline、样本量、任务覆盖和统计口径。 |
| 结果句 | quently, we seek a post-training solution to harness the deployment data for policy improvement. | 核对 baseline、样本量、任务覆盖和统计口径。 |
| 结果句 | post-training methods for VLA have shown that the deployment experience can improve pretrained | 核对 baseline、样本量、任务覆盖和统计口径。 |
| 结果句 | treated as expert supervision or positive improvement signals. | 核对 baseline、样本量、任务覆盖和统计口径。 |

## 图表、公式与表格线索

图表线索：

- Figure 1: ROVE learns from imperfect humanoid interventions.(Left) Our method recovers task progress through re-matching and re-erasing. (Middle) Human interventions after near-failure VLA rollouts can deviate from ideal corrections in humanoid manipulation; our method learns a value function from mixed-quality and cro...
- Fig. 1, ROVE improves upon SFT and experience-learning baselines, including RL and IIL meth- ods, and continues to gain performance over multiple rollout-intervention iterations. Our main contributions are summarized as follows:(i) Human-in-the-loop data collection pipeline for humanoid manipulation. We build a whole-b...
- Figure 2: Task procedures forPut the bread into the toaster(top) andErase the whiteboard(bottom). 2 Preliminary Problem setting and notation. We formulate the humanoid manipulation problem as a Markov Decision Process (MDP)M: (S, A, P, r, γ)in a standard RL setting [8], whereS= (O, L), Ois the image observation space f...
- Fig. 3 summarizes the overall ROVE framework. The method first collects mixed-quality real-world experience on the humanoid robot, then learns a state-value critic from robot trajectories and human experience videos, and finally uses the resulting advantage signals to extract a stronger VLA policy. We describe these co...
- Figure 3: Overview of ROVE framework. A VLA actor collects autonomous rollouts and triggers whole-body human intervention near failure. The resulting trajectories are decomposed into rollout, adaptation, and recovery stages, and combined with cross-embodiment human experience to train a state-value critic. The critic p...
- Figure 4: Policy improvement results on two real-world humanoid manipulation tasks. ROVE (Ours) outperforms SFT in the demonstration-only setting, achieves the best average performance among experience-learning methods, and consistently improves across multiple iterations of rollout and intervention data. 3.3 Policy im...
- Figure 5: Human experience improves value estimation. Adding human experience helps the critic assign lower values to incomplete erasing states and better reflect true task progress. Erase Fail t = 9.0s t = 7.7s
- Figure 6: OVE provides sharper value estimates than Monte-Carlo estimates, producing clearer negative-advantage regions during failure and recovery. with RECAP, the remaining gap reflects the combined effect of critic quality and advantage assign- ment of post-adaptation intervention segments. Compared with Filtered BC...
- Fig. 4, ROVE consistently improves across three iterations on both tasks. The success rate increases from 45.0% to 80.0% onErase the whiteboard, and from 56.7% to 86.7% onPut the bread into the toaster. This demonstrates that it forms a closed-loop improvement process: better policies collect more informative experienc...
- algorithms. arXiv preprint, 2017. [28] Z. Shao, P. Wang, Q. Zhu, R. Xu, J. Song, X. Bi, H. Zhang, M. Zhang, Y . Li, Y . Wu, et al. Deepseekmath: Pushing the limits of mathematical reasoning in open language models. arXiv preprint, 2024. [29] C. Xu, J. T. Springenberg, M. Equi, A. Amin, A. Esmail, S. Levine, and L. Ke....
- Table 1 studies two implementation choices in value-label construction: the horizon used for TD bootstrapping and advantage computation, and the timingt r of the penalty reward.
- Table 1: Sensitivity of value-label construction.
- Fig. 2 illustrates the manipulation procedure for each task. ForPut the bread into the toaster, the task begins with bread slices in a container and a two-slot toaster on the table. A trial proceeds 13
- Figure 7: Performance comparison between OVE and IQL on D 4RL-AntMaze tasks. 40 cm 30 cm 13 cm x 3 cm 11 cm x 1.7 cm
- Figure 8: Evaluation objects and layout for our tasks. through reaching into the container, grasping one slice, lifting and transporting it above the toaster slot, inserting the bread, releasing it, and retracting the hand. A trial is counted as successful if the bread is fully inserted into the toaster slot and remain...
- Fig. 8 summarizes the evaluation objects and scene layout used in our experiments. ForErase the whiteboard, we draw twenty handwriting marks uniformly distributed on the whiteboard and run one evaluation trial per mark, for twenty trials in total. ForPut the bread into the toaster, we run thirty 14

本地精选图：

![[papers/images/xiao2026rove/bread_continue_success_page1.png|700]]
![[papers/images/xiao2026rove/erase_continue_success_page1.png|700]]
![[papers/images/xiao2026rove/eval_page1.png|700]]
![[papers/images/xiao2026rove/framework_page1.png|700]]
![[papers/images/xiao2026rove/iql_comparison_page1.png|700]]
![[papers/images/xiao2026rove/policy_improvement_page1.png|700]]
![[papers/images/xiao2026rove/task.png|700]]
![[papers/images/xiao2026rove/task_2.png|700]]

公式线索：

- `Decision Process (MDP)M: (S,A,P, r, γ)in a standard RL setting [8], whereS= (O,L),`
- `robot’s task instruction.Ais the action space of the robot,P:S × A →∆(S)is the stochas-`
- `tic dynamics of the environment,r:S × A →Ris the reward function, the discount factor`
- `st = (o t, l),o t ∈ O, l∈ L,His the action chunk horizon. Given the robot policy`
- `ξ= (s 0, a0, r1, s1,· · ·, aT−1 , rT , sT )∈ S × A ×R· · · Sthrough interactions between the policy`
- `mulative reward, or return, asR(ξ) = PT`
- `t=0 γtrt. The goal of RL is to maximize the expected`
- `discounted return:J(π) =E ξ∼ρπ [R(ξ)] =E ξ∼ρπ [PT`
- `t=0 γtrt].`
- `i=t γi−tri]. Then, we can define the advantage of the action chunka t:t+H−1 at state`
- `st asA π(st, at:t+H−1 ) =E ρπ(ξ)[Pt+H−1`
- `i=t γi−tri +γ H V π(st+H )]−V π(st). In practice, we learn`

这些线索不等于完整视觉理解。需要解释图中具体曲线、表格数值或失败案例时，应回到 PDF 原图或运行抽图脚本补全图片。

## 主张-证据-边界矩阵

| 主张 / 结论 | 原文证据 | 证据位置 | 解释 | 边界 / 适用条件 |
| --- | --- | --- | --- | --- |
| 核心问题值得解决 |  | Abstract / Introduction | 先确认作者的问题定义是否真实、具体、可检验 | 需要与 Related Work 对照，避免把已有工作重新包装成缺口 |
| 方法机制能回应问题 |  | Method / Model | 看输入、表示、训练目标、输出是否形成闭环 | 需要 ablation 证明关键组件不可替代 |
| 实验支持有效性 | Success Rate - Multi-IterationErase whiteboard (Contact-rich) (Right) It outperforms all baselines and consistently improves across multiple iterations. performs experience-learning baselines and consistently improves across multiple quently, we seek a post-training solution to harness the deployment data for policy improvement. | Experiments / Results | 看主结果是否覆盖任务、数据、baseline 和真实部署 | 指标可能只覆盖局部能力，不能直接外推到所有场景 |
| 方法存在边界 |  | Limitations / Discussion / failure cases | 边界决定这篇论文什么时候值得引用、什么时候不能引用 | 如果作者未充分讨论，需要从失败案例和数据分布反推 |

## 局限与可追问点

- 文献笔记未记录明确局限，需要回看 Discussion、Limitations、Appendix 和失败案例。

额外需要追问：

- 数据是否覆盖足够多 embodiment、任务、传感器、场景和失败模式？
- Baseline 是否足够强，是否和本文方法使用了同等数据、模型规模和计算预算？
- 指标是否直接对应机器人最终成功率，还是只衡量 proxy signal？
- 真实机器人实验是否足够多，是否报告失败案例和部署约束？


## 与当前库的连接

- 可放入当前库的具身智能/机器人学习线索中，与 world model、VLA、触觉、reward/data curation 四条路线交叉比较。

## 精读路线 / 为什么需要回看

1. 先读 `摘要` 和 `论文主线`，确认作者到底把哪个缺口定义为核心问题。
2. 再读 `方法细节` 和对应原文 section，检查输入、表示、训练目标、推理过程和模块依赖是否闭合。
3. 最后读 `实验设置、数据集、基线、指标` 与 `主要结果、消融或对比`，重点核对是否有真实机器人、跨任务、跨 embodiment、失败案例和 ablation。
4. 如果后续要写 related work，把 `贡献与结论对照` 和 `主张-证据-边界矩阵` 作为引用依据，不要只引用摘要结论。
