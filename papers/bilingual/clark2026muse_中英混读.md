---
tags:
  - bilingual-reading
  - deep-reading
source_pdf: "[[papers/pdfs/clark2026muse.pdf]]"
paper: "[[@clark2026muse]]"
images: "papers/images/clark2026muse/"
image_index: "[[papers/images/clark2026muse/index.md]]"
created: 2026-07-11
generator: "setting/scripts/generate_reading_draft.py"
reading_standard: "fba534d bilingual full-reading"
extraction: "pypdf"
source_pages: 18
source_chars: 60128
---

# Multisensory Continual Learning: Adapting Pretrained Visuomotor Policies to Force

paper:: [[@clark2026muse]]
pdf:: [[papers/pdfs/clark2026muse.pdf]]
images:: [[papers/images/clark2026muse/index.md]]
reading:: [[papers/bilingual/clark2026muse_中英混读.md]]

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| World Model | 世界模型 | 把状态转移、未来预测或环境动力学作为机器人决策的中间表示。 |
| trajectory | 时间/轨迹建模 | 利用帧序列和历史上下文理解任务进展或未来结果。 |
| tactile | 触觉/接触信号 | 提供 RGB 难以看到的滑移、卡滞、接触法线和局部形变信息。 |
| attention | 注意力机制 | 决定视觉、触觉、动作、语言 token 之间如何相互读取信息。 |
| success rate | 成功率 | 机器人任务中最直接的结果指标，但需要结合任务难度和评估协议读。 |

## 摘要

Robot manipulation often relies on sensory feedback beyond vision, particularly in contact-rich settings where force, tactile, or audio signals reveal interaction states that are not directly observable from images. However, these modalities are often hardware- and task-specific, and large-scale multisensory robot datasets remain scarce. As a result, it is impractical to pretrain policies with every sensor they may encounter. We study multisensory continual learning: adapting a pretrained robot policy to new tasks with newly introduced modalities while preserving performance under the original sensor suite. We propose MultiSensory World Model (MuSe), which incorporates limited multisensory data into pretrained vision-only policies through multi-stage fusion, multisensory future prediction, and experience replay over pretraining data. We instantiate MuSe by augmenting a pretrained vision-only policy with force-torque sensing and evaluate it on real-world manipulation tasks. Our experiments show that MuSe performs strongly on contact-rich finetuning tasks while preserving, and in some cases improving, performance on the original pretraining tasks. These results suggest that a modest multisensory dataset can improve general robot capabilities beyond the finetuning distribution. Project website: https://jadenvc.github.io/multisensory-continual-learning/

中文解读：本文的核心定位需要结合 Introduction 与 Method 进一步确认。

这部分不是把摘要简单翻译成中文，而是先抓住作者的写作动作：作者通常先指出现有方法在哪个环节失效，再提出一个机制、模型、数据集或系统，最后用 benchmark、真实机器人或 ablation 证明它确实补上了这个缺口。

## 人工校订重点解读

### MuSe 的核心不是简单增加 force input

MuSe 把问题定义为 multisensory continual learning：已有 policy 在 21 个 vision-only tasks 上预训练，之后仅用 5 个新 contact-rich tasks 的 434 条 F/T episodes 加入新模态，同时要求 forward transfer 和 backward transfer。若只在新数据上微调，策略会 catastrophic forgetting；若只拼接 F/T，模型也可能学不到可迁移的接触表示。

![[papers/images/clark2026muse/method_4_page1.png|700]]

方法组合有三层：early/late multi-stage fusion 把 F/T 接入视觉动力学表示；multi-mode world model 同时学习 future video、action 和 force trajectory；experience replay 对旧样本遮蔽 F/T input/loss，保留原视觉能力。预测的 force trajectory 还驱动 adaptive compliance，因此 auxiliary prediction 被落实到接触控制，而不只是训练正则项。

### Forward 与 backward transfer 的数字

| 设置 | Vase wiping | Peg insertion | Pick-and-place |
|---|---:|---:|---:|
| Forward: No F/T | 5/15 | 9/15 | 7.5/10 |
| Forward: MuSe | **11.5/15** | **13/15** | **7.5/10** |
| Backward: Pretraining only | 8.5/15 | 8/15 | 5.5/10 |
| Backward: MuSe | **12.5/15** | **10/15** | **6.5/10** |
| Backward: No experience replay | 0.5/15 | 2/15 | 5.5/10 |

![[papers/images/clark2026muse/experiments_13_page1.png|700]]

关闭 adaptive compliance 后，wiping 从 11.5/15 降至 8/15，insertion 从 13/15 降至 11/15。与同样使用 replay 和 masked F/T supervision 的 Diffusion Policy 相比，MuSe 在旧任务上的 F/T prediction error 为 8.42，对方为 18.27，说明 future-image prediction 提供了跨任务共享的视觉动力学锚点。

### 应保留的边界

实验只覆盖 F/T 一种新增模态，每项 10 或 15 trials，部分采用 half credit。Positive backward transfer 很有启发性，但尚不能证明 tactile/audio 等模态或大规模 continual stream 也会成立；保留全部 pretraining data 做 replay 的成本也没有被解决。

## 论文主线

如果用一条线串起全文，可以这样读：

1. **问题入口**：从 Introduction 回看作者如何定义失败模式、任务缺口和评价目标。
2. **方法钩子**：方法机制需要从 Method / Model / Architecture 章节继续细化。
3. **证据出口**：证据链需要从 Experiments / Evaluation / Results 章节继续细化。
4. **引言铺垫的读法**：
- 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。
  原文线索：`Large-scale vision-action pretraining has become a powerful paradigm for robot learning, but vision alone does not fully capture the physical interaction state required for manipul...`
- 这句话在铺设论文问题入口：它帮助读者理解为什么这件事值得做。
  原文线索：`Contact-rich tasks often depend on signals that are only indirectly visible, such as contact forces and slippage.`
- 这是数据或实验设置线索：重点看数据来源、标注协议、任务分布和真实部署边界。
  原文线索：`Additional modalities such as force-torque (F/T), tactile, and audio sensing provide direct feedback about these hidden interaction dynamics, enabling robots to adapt their behavio...`
- （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）
  原文线索：`In practice, however, such modalities are often hardware- and task-specific, and datasets that include them are far smaller than vision-only datasets.`
- （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）
  原文线索：`It is therefore impractical to include every possible sensor during large-scale pretraining.`

阅读时要盯住一个问题：作者的方法机制是否真的直接解决了引言中定义的失败模式，还是只是给同一问题换了更大的模型或更多的数据。

## 贡献与结论对照

| 贡献 / 结论 | 方法位置 | 证据 / 结论 |
| --- | --- | --- |
| 定义核心问题 | Abstract / Introduction |  |
| 提出主要方法或系统 | Method / Model / Architecture | Model ref. pose virt. target action F/T F/T *F/T prediction enables adaptive compliance control Optional masking *if F/T not available Figure 2:MuSe architecture.MuSe encodes image, proprioceptive, language, and optional force-torque (F/T) histories with modality-specific encoders, then fuses them through token-level early fusion and late fusion via cross- attention adapters. The joint sequence model predicts fu- ture actions, F/T signals, and auxiliary video frames, with unavailable F/T inputs and losses masked du... |
| 通过实验验证主张 | Experiments / Evaluation / Results | •Forward transfer:Improve performance on new tasks using the new modality, compared with •Backward transfer:Retain or improve the performance on pretraining tasks after learning new collected (cross-modal generalization), and improved performance on finetuning tasks that benefit ground-truth F/T, and bar plots compare MuSe task success rate with the corresponding baselines. |
| 暴露适用边界 | Discussion / Limitations / failure cases | 需要回看作者是否承认失败案例、数据边界或部署限制。 |

## 结构地图

| 原文位置 | 作者在这一部分做什么 | 与全文主线的关系 | 关键图表 / 公式 |
| --- | --- | --- | --- |
| 1 Introduction | 定义任务、指出现有方法缺口，并把读者带到本文的核心主张。 | 回答为什么要做。 | Figure 1: Multisensory continual learning. A policy is first pretrained on diverse vision-action data without force-torq...<br>Figure 2: MuSe architecture. MuSe encodes image, proprioceptive, language, and optional force-torque (F/T) histories wit... |
| 2 Related Works | 建立前人工作和技术背景，说明本文方法为什么有必要。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 3.1 Problem Statement | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 3.2 Multi-stage Fusion | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| Model | 给出方法机制，是判断论文贡献是否成立的主要位置。 | 回答怎么做。 | Figure 1: Multisensory continual learning. A policy is first pretrained on diverse vision-action data without force-torq...<br>Figure 2: MuSe architecture. MuSe encodes image, proprioceptive, language, and optional force-torque (F/T) histories wit... |
| 3.3 Multisensory Future Prediction | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 3.4 Experience Replay | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 3.5 Implementation | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 4.1 Cross-Modal Generalization | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | Figure 1: Multisensory continual learning. A policy is first pretrained on diverse vision-action data without force-torq...<br>Figure 2: MuSe architecture. MuSe encodes image, proprioceptive, language, and optional force-torque (F/T) histories wit... |
| 4.2 Forward Transfer | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 4.3 Backward Transfer | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 5 Conclusion | 收束主张，并指出方法产出和后续方向。 | 回答边界和意义。 | 待回看 PDF 图表 |

## 按原文 section 精读

### 1. 1 Introduction

#### 高层故事流

定义任务、指出现有方法缺口，并把读者带到本文的核心主张。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

World Model（世界模型）、trajectory（时间/轨迹建模）、tactile（触觉/接触信号）、attention（注意力机制）、success rate（成功率）

#### 原文内容讲解

这一节要按“回答为什么要做。”来读。定义任务、指出现有方法缺口，并把读者带到本文的核心主张。

术语上先抓住 World Model（世界模型）、trajectory（时间/轨迹建模）、tactile（触觉/接触信号）、attention（注意力机制）、success rate（成功率）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。

2. 这句话在铺设论文问题入口：它帮助读者理解为什么这件事值得做。

3. 这是数据或实验设置线索：重点看数据来源、标注协议、任务分布和真实部署边界。

4. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

图表读法：本节出现的图题/表题应当放回对应段落看，重点确认它是在展示 architecture、data pipeline、main result 还是 ablation。

#### 关键原文线索

- `Large-scale vision-action pretraining has become a powerful paradigm for robot learning, but vision alone does not fully capture the physical interaction state required for manipulation.`
- `Contact-rich tasks often depend on signals that are only indirectly visible, such as contact forces and slippage.`
- `Additional modalities such as force-torque (F/T), tactile, and audio sensing provide direct feedback about these hidden interaction dynamics, enabling robots to adapt their behavior between precise trajectory tracking an...`
- `In practice, however, such modalities are often hardware- and task-specific, and datasets that include them are far smaller than vision-only datasets.`

#### 回看重点

- 缺口是否具体到可验证的失败模式，而不只是泛泛说现有方法不足。
- 作者给出的 motivating example 是否会在实验中被直接覆盖。
- 术语复查：World Model（世界模型）, trajectory（时间/轨迹建模）, tactile（触觉/接触信号）, attention（注意力机制） 在本节是否有明确变量、模块或实验定义。
- 图表复查：把图题/表题对应到正文 claim，确认图中数值或示意是否真的支撑该 claim。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| Large-scale vision-action pretraining has become a powerful paradigm for robot learning, but vision alone does not fully capture the physical interaction state required for manipul... | 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。 | 1 Introduction | 注意是否被后续实验直接验证。 |
| Contact-rich tasks often depend on signals that are only indirectly visible, such as contact forces and slippage. | 这句话在铺设论文问题入口：它帮助读者理解为什么这件事值得做。 | 1 Introduction | 注意是否被后续实验直接验证。 |
| Additional modalities such as force-torque (F/T), tactile, and audio sensing provide direct feedback about these hidden interaction dynamics, enabling robots to adapt their behavio... | 这是数据或实验设置线索：重点看数据来源、标注协议、任务分布和真实部署边界。 | 1 Introduction | 注意是否被后续实验直接验证。 |
| In practice, however, such modalities are often hardware- and task-specific, and datasets that include them are far smaller than vision-only datasets. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 1 Introduction | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| Figure | 1 Introduction | Figure 1: Multisensory continual learning. A policy is first pretrained on diverse vision-action data without force-torque (F/T) labels, then adapted with a small amount of multisensory data from new contact-rich tasks.... | 支撑本节的方法、实验或定性解释。 |


### 2. 2 Related Works

#### 高层故事流

建立前人工作和技术背景，说明本文方法为什么有必要。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

vision-language-action（视觉-语言-动作模型）、touch（触觉/接触信号）

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。建立前人工作和技术背景，说明本文方法为什么有必要。

术语上先抓住 vision-language-action（视觉-语言-动作模型）、touch（触觉/接触信号）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

2. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

3. 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。

4. 这是数据或实验设置线索：重点看数据来源、标注协议、任务分布和真实部署边界。

#### 关键原文线索

- `Multisensory robot learning.Recent work has extended robot policies with touch, force, and au- dio, showing that these modalities provide contact state, slip, and interaction dynamics that are diffi- cult to infer from v...`
- `Visuo-tactile world models and video-tactile- action models further demonstrate the value of explicitly modeling contact dynamics for physical interaction [9, 10].`
- `However, multisensory datasets remain far smaller and less diverse than vision- only pretraining corpora.`
- `We therefore study a sensor-incremental setting: learning from limited multisensory data while retaining the broad capabilities acquired during visual pretraining.`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：vision-language-action（视觉-语言-动作模型）, touch（触觉/接触信号） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| Multisensory robot learning.Recent work has extended robot policies with touch, force, and au- dio, showing that these modalities provide contact state, slip, and interaction dynam... | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 2 Related Works | 注意是否被后续实验直接验证。 |
| Visuo-tactile world models and video-tactile- action models further demonstrate the value of explicitly modeling contact dynamics for physical interaction [9, 10]. | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 2 Related Works | 注意是否被后续实验直接验证。 |
| However, multisensory datasets remain far smaller and less diverse than vision- only pretraining corpora. | 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。 | 2 Related Works | 注意是否被后续实验直接验证。 |
| We therefore study a sensor-incremental setting: learning from limited multisensory data while retaining the broad capabilities acquired during visual pretraining. | 这是数据或实验设置线索：重点看数据来源、标注协议、任务分布和真实部署边界。 | 2 Related Works | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 3. 3.1 Problem Statement

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

trajectories（时间/轨迹建模）

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

术语上先抓住 trajectories（时间/轨迹建模）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

2. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

3. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

4. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

#### 关键原文线索

- `We consider a pretrained robot model trained on trajectories comprisingnobservation modal- ities and robot actions.`
- `, on t }denote the observations at timet, where eacho i t corresponds to one modality, such as RGB images or proprioception.`
- `Given a his- tory horizonh, the pretrained model takes as input a sequence of past observations and actions, {ot−h+1, .`
- `, at−1},and predicts future actions and observations over a prediction horizonH:{o t+1, .`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：trajectories（时间/轨迹建模） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| We consider a pretrained robot model trained on trajectories comprisingnobservation modal- ities and robot actions. | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 3.1 Problem Statement | 注意是否被后续实验直接验证。 |
| , on t }denote the observations at timet, where eacho i t corresponds to one modality, such as RGB images or proprioception. | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 3.1 Problem Statement | 注意是否被后续实验直接验证。 |
| Given a his- tory horizonh, the pretrained model takes as input a sequence of past observations and actions, {ot−h+1, . | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 3.1 Problem Statement | 注意是否被后续实验直接验证。 |
| , at−1},and predicts future actions and observations over a prediction horizonH:{o t+1, . | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 3.1 Problem Statement | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| Equation | 3.1 Problem Statement | `ities and robot actions. Leto t ={o 1` | 定义变量关系、训练目标或推理过程。 |


### 4. 3.2 Multi-stage Fusion

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

可以把正文拆成下面几步：

1. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

2. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

#### 关键原文线索

- `HISTORY (INPUTS) images (5Hz) actions (20Hz) text F/T (120Hz) EARLY FUSION LATE FUSION PRED.`
- `TARGET DEPLOYMENT aux loss (not used deployment)video Joint Sequence`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| HISTORY (INPUTS) images (5Hz) actions (20Hz) text F/T (120Hz) EARLY FUSION LATE FUSION PRED. | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 3.2 Multi-stage Fusion | 注意是否被后续实验直接验证。 |
| TARGET DEPLOYMENT aux loss (not used deployment)video Joint Sequence | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 3.2 Multi-stage Fusion | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 5. Model

#### 高层故事流

给出方法机制，是判断论文贡献是否成立的主要位置。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

attention（注意力机制）

#### 原文内容讲解

这一节要按“回答怎么做。”来读。给出方法机制，是判断论文贡献是否成立的主要位置。

术语上先抓住 attention（注意力机制）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

2. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

3. 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。

4. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

图表读法：本节出现的图题/表题应当放回对应段落看，重点确认它是在展示 architecture、data pipeline、main result 还是 ablation。

#### 关键原文线索

- `The joint sequence model predicts fu- ture actions, F/T signals, and auxiliary video frames, with unavailable F/T inputs and losses masked during training.`
- `At deployment, action predictions drive the policy to com- manded reference pose, while predicted future F/T is used to set a virtual target for adaptive compliance control.`
- `A central challenge in multisen- sory learning is how to combine modalities expressively without cor- rupting the pretrained representation.`
- `The new modality should interact deeply with vision, proprioception, language, and action, but it should not overwrite visual-action knowl- edge or cause the policy to over- attend to contact signals when they are uninfo...`

#### 回看重点

- 输入、隐藏表示、训练目标和输出之间是否闭合。
- 每个新增模块是否有对应 ablation 或对照实验支撑。
- 术语复查：attention（注意力机制） 在本节是否有明确变量、模块或实验定义。
- 图表复查：把图题/表题对应到正文 claim，确认图中数值或示意是否真的支撑该 claim。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| The joint sequence model predicts fu- ture actions, F/T signals, and auxiliary video frames, with unavailable F/T inputs and losses masked during training. | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | Model | 需要后续实验或 ablation 证明该机制不可替代。 |
| At deployment, action predictions drive the policy to com- manded reference pose, while predicted future F/T is used to set a virtual target for adaptive compliance control. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | Model | 需要后续实验或 ablation 证明该机制不可替代。 |
| A central challenge in multisen- sory learning is how to combine modalities expressively without cor- rupting the pretrained representation. | 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。 | Model | 需要后续实验或 ablation 证明该机制不可替代。 |
| The new modality should interact deeply with vision, proprioception, language, and action, but it should not overwrite visual-action knowl- edge or cause the policy to over- attend... | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | Model | 需要后续实验或 ablation 证明该机制不可替代。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| Figure | Model | Figure 2: MuSe architecture. MuSe encodes image, proprioceptive, language, and optional force-torque (F/T) histories with modality-specific encoders, then fuses them through token-level early fusion and late fusion via c... | 支撑本节的方法、实验或定性解释。 |


### 6. 3.3 Multisensory Future Prediction

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

latent（潜在表示）

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

术语上先抓住 latent（潜在表示）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。

2. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

3. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

4. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

#### 关键原文线索

- `Multi-stage fusion enables the policy to condition on an added modality, but conditioning alone does not ensure that the new sensor improves the shared representation.`
- `To encourage the model to integrate new sensory information into a unified, physically grounded latent space, we train MuSe with a flexible multisensory future prediction objective.`
- `In addition to predicting future actions, the model predicts future original observations, such as video, as well as the newly introduced modality.`
- `Predicting the new modality encourages the representation to encode information from the added sensor, while predicting future images anchors this representation to visual dynamics that are shared across datasets.`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：latent（潜在表示） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| Multi-stage fusion enables the policy to condition on an added modality, but conditioning alone does not ensure that the new sensor improves the shared representation. | 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。 | 3.3 Multisensory Future Prediction | 注意是否被后续实验直接验证。 |
| To encourage the model to integrate new sensory information into a unified, physically grounded latent space, we train MuSe with a flexible multisensory future prediction objective... | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 3.3 Multisensory Future Prediction | 注意是否被后续实验直接验证。 |
| In addition to predicting future actions, the model predicts future original observations, such as video, as well as the newly introduced modality. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 3.3 Multisensory Future Prediction | 注意是否被后续实验直接验证。 |
| Predicting the new modality encourages the representation to encode information from the added sensor, while predicting future images anchors this representation to visual dynamics... | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 3.3 Multisensory Future Prediction | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| Equation | 3.3 Multisensory Future Prediction | `L=λ aLact +λ oLobs +λ n+1Lnew.` | 定义变量关系、训练目标或推理过程。 |


### 7. 3.4 Experience Replay

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

可以把正文拆成下面几步：

1. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

2. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

3. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

4. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

#### 关键原文线索

- `Naively fine-tuning the pretrained model only on the new multisensory data can lead to catastrophic forgetting: the model may adapt to the new sensor and task distribution while losing performance on the original pretrai...`
- `To mitigate this, we useexperience replayduring finetuning.`
- `Each training batch is sampled from a mixture of the new multisensory datasetD new and the original pretraining datasetD pre.`
- `For samples fromD new, the model receives the expanded multisensory input when available and is supervised with the relevant action, original-observation, and new-modality prediction losses.`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| Naively fine-tuning the pretrained model only on the new multisensory data can lead to catastrophic forgetting: the model may adapt to the new sensor and task distribution while lo... | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 3.4 Experience Replay | 注意是否被后续实验直接验证。 |
| To mitigate this, we useexperience replayduring finetuning. | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 3.4 Experience Replay | 注意是否被后续实验直接验证。 |
| Each training batch is sampled from a mixture of the new multisensory datasetD new and the original pretraining datasetD pre. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 3.4 Experience Replay | 注意是否被后续实验直接验证。 |
| For samples fromD new, the model receives the expanded multisensory input when available and is supervised with the relevant action, original-observation, and new-modality predicti... | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 3.4 Experience Replay | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 8. 3.5 Implementation

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

trajectory（时间/轨迹建模）、attention（注意力机制）、diffusion（扩散生成）

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

术语上先抓住 trajectory（时间/轨迹建模）、attention（注意力机制）、diffusion（扩散生成）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

2. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

3. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

4. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

#### 关键原文线索

- `We instantiate MuSe by augmenting the Unified Video-Action (UV A) model [21] with force-torque (F/T) sensing.`
- `UV A jointly models video and action sequences with a decoupled action decoder for efficient policy inference.`
- `To incorporate F/T, we add the two fusion pathways described above: early fusion encodes F/T histories with a causal convolutional encoder and prepends the resulting tokens to the pretrained token sequence, while late fu...`
- `We also add an F/T diffusion head following the UV A action head design.`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：trajectory（时间/轨迹建模）, attention（注意力机制）, diffusion（扩散生成） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| We instantiate MuSe by augmenting the Unified Video-Action (UV A) model [21] with force-torque (F/T) sensing. | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 3.5 Implementation | 注意是否被后续实验直接验证。 |
| UV A jointly models video and action sequences with a decoupled action decoder for efficient policy inference. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 3.5 Implementation | 注意是否被后续实验直接验证。 |
| To incorporate F/T, we add the two fusion pathways described above: early fusion encodes F/T histories with a causal convolutional encoder and prepends the resulting tokens to the... | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 3.5 Implementation | 注意是否被后续实验直接验证。 |
| We also add an F/T diffusion head following the UV A action head design. | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 3.5 Implementation | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 9. 4.1 Cross-Modal Generalization

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

trajectories（时间/轨迹建模）、attention（注意力机制）、Ablation（消融实验）

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

术语上先抓住 trajectories（时间/轨迹建模）、attention（注意力机制）、Ablation（消融实验）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是证据线索：读的时候要核对 baseline、指标、任务覆盖和统计口径。

2. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

3. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

4. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

图表读法：本节出现的图题/表题应当放回对应段落看，重点确认它是在展示 architecture、data pipeline、main result 还是 ablation。

#### 关键原文线索

- `Cross-modal F/T prediction ablations 12.38 12.06 11.52 11.80 11.80 L2 error 12 8 4 0 9.90 8.42 Muse No VP No ER Model Ablation No Early No Late Linear Additive Fusion Method Ablation Figure 4: L2 error of predicted F/T s...`
- `MuSe achieves the lowest error, while weakening fusion, removing video prediction, or removing experience replay increases prediction error.`
- `Experiment Setup.We collect demonstrations using UMI-FT [2], which equips each gripper finger with a CoinFT sensor and streams all modalities to the control desktop for real-time inference.`
- `We then pretrain the UV A backbone on 1,271 episodes from 21 tasks using only visual ob- servations and actions.`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：trajectories（时间/轨迹建模）, attention（注意力机制）, Ablation（消融实验） 在本节是否有明确变量、模块或实验定义。
- 图表复查：把图题/表题对应到正文 claim，确认图中数值或示意是否真的支撑该 claim。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| Cross-modal F/T prediction ablations 12.38 12.06 11.52 11.80 11.80 L2 error 12 8 4 0 9.90 8.42 Muse No VP No ER Model Ablation No Early No Late Linear Additive Fusion Method Ablati... | 这是证据线索：读的时候要核对 baseline、指标、任务覆盖和统计口径。 | 4.1 Cross-Modal Generalization | 注意是否被后续实验直接验证。 |
| MuSe achieves the lowest error, while weakening fusion, removing video prediction, or removing experience replay increases prediction error. | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 4.1 Cross-Modal Generalization | 注意是否被后续实验直接验证。 |
| Experiment Setup.We collect demonstrations using UMI-FT [2], which equips each gripper finger with a CoinFT sensor and streams all modalities to the control desktop for real-time i... | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 4.1 Cross-Modal Generalization | 注意是否被后续实验直接验证。 |
| We then pretrain the UV A backbone on 1,271 episodes from 21 tasks using only visual ob- servations and actions. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 4.1 Cross-Modal Generalization | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| Figure | 4.1 Cross-Modal Generalization | Figure 4: L 2 error of predicted F/T signals on pretrain- ing tasks. MuSe achieves the lowest error, while weakening fusion, removing video prediction, or removing experience replay increases prediction error. Experiment... | 支撑本节的方法、实验或定性解释。 |
| Figure | 4.1 Cross-Modal Generalization | Figure 3: We pretrain a policy (with no F/T) on 21 tasks, then finetune on 5 unique taskscontaining F/T information that do not exist in pretraining. We then evaluate MuSe on 3 sets of pretraining tasks to measure backwa... | 支撑本节的方法、实验或定性解释。 |
| Figure | 4.1 Cross-Modal Generalization | Figure 5: Cross-modal generalization of F/T prediction on pretraining tasks where F/T signals were recorded but never used for supervision. MuSe accurately predicts changes in F/T across all three axes (defined in top le... | 支撑本节的方法、实验或定性解释。 |


### 10. 4.2 Forward Transfer

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

success rate（成功率）

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

术语上先抓住 success rate（成功率）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

2. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

3. 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。

4. 这是证据线索：读的时候要核对 baseline、指标、任务覆盖和统计口径。

#### 关键原文线索

- `We then evaluate whether multimodal finetuning enables a vision-action pretrained policy to acquire force-aware behaviors from a small number of demonstrations.`
- `Pick and placeevaluates whether adding F/T preserves performance on tasks where force feedback is less central, with perturbed object locations and distractors.`
- `Notably, the model is evaluated on pick and place tasks that exist in the finetuning dataset but not in pretraining.`
- `It achieves 11.5/15 success onvase wiping, com- pared to 5/15 forNo F/Tand 8/15 forNo Pretrain, and 13/15 onpeg insertion, compared to 9/15 and 6/15, respectively.`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：success rate（成功率） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| We then evaluate whether multimodal finetuning enables a vision-action pretrained policy to acquire force-aware behaviors from a small number of demonstrations. | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 4.2 Forward Transfer | 注意是否被后续实验直接验证。 |
| Pick and placeevaluates whether adding F/T preserves performance on tasks where force feedback is less central, with perturbed object locations and distractors. | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 4.2 Forward Transfer | 注意是否被后续实验直接验证。 |
| Notably, the model is evaluated on pick and place tasks that exist in the finetuning dataset but not in pretraining. | 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。 | 4.2 Forward Transfer | 需要看数据分布、标注一致性和任务代表性。 |
| It achieves 11.5/15 success onvase wiping, com- pared to 5/15 forNo F/Tand 8/15 forNo Pretrain, and 13/15 onpeg insertion, compared to 9/15 and 6/15, respectively. | 这是证据线索：读的时候要核对 baseline、指标、任务覆盖和统计口径。 | 4.2 Forward Transfer | 需要看提升是否来自公平 baseline、足够任务覆盖和同等数据/算力。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 11. 4.3 Backward Transfer

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

可以把正文拆成下面几步：

1. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

2. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

3. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

4. 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。

#### 关键原文线索

- `Finally, we evaluate whether multimodal finetuning preserves the original vision-only skills while transferring the newly learned F/T modality back to the pretraining tasks.`
- `We compare against No ER, which removes experience replay from the original pretraining data during finetuning, and Pretraining Only, which uses the original vision-only UV A policy without multimodal finetuning.`
- `We evaluate on three pretraining tasks.Whiteboard wipingrequires the robot to erase a drawing, either with the eraser already grasped or after first picking it up.`
- `Qualitatively,Pretraining Onlyoften attempts the correct behavior but fails to regulate contact.No ERoften forgets the original task structure or overfits to finetuning- specific strategies (e.g.`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| Finally, we evaluate whether multimodal finetuning preserves the original vision-only skills while transferring the newly learned F/T modality back to the pretraining tasks. | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 4.3 Backward Transfer | 注意是否被后续实验直接验证。 |
| We compare against No ER, which removes experience replay from the original pretraining data during finetuning, and Pretraining Only, which uses the original vision-only UV A polic... | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 4.3 Backward Transfer | 注意是否被后续实验直接验证。 |
| We evaluate on three pretraining tasks.Whiteboard wipingrequires the robot to erase a drawing, either with the eraser already grasped or after first picking it up. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 4.3 Backward Transfer | 注意是否被后续实验直接验证。 |
| Qualitatively,Pretraining Onlyoften attempts the correct behavior but fails to regulate contact.No ERoften forgets the original task structure or overfits to finetuning- specific s... | 这是问题缺口或失败模式：要确认它是否被后续方法设计直接响应。 | 4.3 Backward Transfer | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 12. 5 Conclusion

#### 高层故事流

收束主张，并指出方法产出和后续方向。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

tactile（触觉/接触信号）

#### 原文内容讲解

这一节要按“回答边界和意义。”来读。收束主张，并指出方法产出和后续方向。

术语上先抓住 tactile（触觉/接触信号）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是本文的贡献声明：要看作者提出的是新模型、新数据、新训练目标、新评测，还是系统集成。

2. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

3. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

4. 这是数据或实验设置线索：重点看数据来源、标注协议、任务分布和真实部署边界。

#### 关键原文线索

- `We propose MuSe, a general framework for adapting pretrained policies to new modalities through multisensory future prediction, multi-stage fusion, and episodic recall.`
- `We instantiate this frame- work with force–torque sensing as a case study on top of a vision-action policy.`
- `Across real-world experiments, MuSe learns transferable F/T representations, improves forward transfer to contact-rich tasks, and preserves or improves performance on the original vision-only task distribution.`
- `These results suggest that pretrained robot policies can be expanded with new sensors after pretraining, without requiring large-scale multisensory data from the start.`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：tactile（触觉/接触信号） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| We propose MuSe, a general framework for adapting pretrained policies to new modalities through multisensory future prediction, multi-stage fusion, and episodic recall. | 这是本文的贡献声明：要看作者提出的是新模型、新数据、新训练目标、新评测，还是系统集成。 | 5 Conclusion | 需要看新增设计是否有必要性证明，而不是只靠整体结果。 |
| We instantiate this frame- work with force–torque sensing as a case study on top of a vision-action policy. | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 5 Conclusion | 注意是否被后续实验直接验证。 |
| Across real-world experiments, MuSe learns transferable F/T representations, improves forward transfer to contact-rich tasks, and preserves or improves performance on the original... | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 5 Conclusion | 注意是否被后续实验直接验证。 |
| These results suggest that pretrained robot policies can be expanded with new sensors after pretraining, without requiring large-scale multisensory data from the start. | 这是数据或实验设置线索：重点看数据来源、标注协议、任务分布和真实部署边界。 | 5 Conclusion | 注意是否被后续实验直接验证。 |

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

Model ref. pose virt. target action F/T F/T *F/T prediction enables adaptive compliance control Optional masking *if F/T not available Figure 2:MuSe architecture.MuSe encodes image, proprioceptive, language, and optional force-torque (F/T) histories with modality-specific encoders, then fuses them through token-level early fusion and late fusion via cross- attention adapters. The joint sequence model predicts fu- ture actions, F/T signals, and auxiliary video frames, with unavailable F/T inputs and losses masked during training. At deployment, action predictions drive the policy to com- manded reference pose, while predicted future F/T is used to set a virtual target for adaptive compliance control. A central challenge in multisen- sory learning is how to combine modalities expressively without cor- rupting the pretrained representation. The new modality should interact deeply with vision, proprioception, language, and action, but it should not overwrite visual-action knowl- edge or cause the policy to over- attend to contact signals when they are uninformative. Existing multi- sensory robot learning methods typ- ically address this with a single fu- sion stage, either combining modal- ities early to maximize cross-modal interaction or injecting them later to preserve the pretrained representation [3, 2, 6, 8, 20]. MuSe goes beyond these single-stage designs by com- bining both pathways (Fig. 2). MuSe extends the pretrained model by adding a modality-specific en- coder and projection layer for the newly introduced modalityo n+1 t . The projection maps the new modality features into the shared embedding space used by the pre- trained observation and action tokens. The resulting tokens are concatenated with the existing obser- vation, proprioception, and action tokens alo...

公式 / 数学定义线索：

- `ities and robot actions. Leto t ={o 1`
- `L=λ aLact +λ oLobs +λ n+1Lnew.`
- `256×256frame to16×16 = 256spatial tokens of dimension 16. With patch size 1, each token`
- `condition on 4 history frames and predict 4 future frames, yielding4×256 = 1024visual tokens`
- `4 proprioceptive timesteps are concatenated into a4×36 = 144-dimensional vector and passed`


## 实验设置、数据集、基线、指标

读实验时不要只看最终分数，要按 `数据集 -> baseline -> 指标 -> 主结果 -> 消融 -> 失败案例` 走。

实验正文线索：

- 未稳定识别实验正文，需要回看 Experiments / Evaluation / Results 章节。

指标 / 结果句线索：

- •Forward transfer:Improve performance on new tasks using the new modality, compared with
- •Backward transfer:Retain or improve the performance on pretraining tasks after learning new
- collected (cross-modal generalization), and improved performance on finetuning tasks that benefit
- ground-truth F/T, and bar plots compare MuSe task success rate with the corresponding baselines.
- across modalities that generalizes beyond the finetuning data and improves backward transfer.
- both contact-rich and pick-and-place tasks, showing improvements in real-world success rate and
- does not ensure that the new sensor improves the shared representation.
- in addition to outperforming models with no pretraining and no F/T for forward transfer.
- MuSe improves most on the contact-rich tasks.
- It achieves 11.5/15 success onvase wiping, com-
- Takeaway:MuSe leverages F/T to improve success rate on contact-rich tasks, while vision-action
- pretraining improves generalization on task variations.


## 主要结果、消融或对比

| 证据类型 | 原文线索 | 读法 |
| --- | --- | --- |
| 图表/表格 | Figure 1: Multisensory continual learning. A policy is first pretrained on diverse vision-action data without force-torque (F/T) labels, then adapted with a small amount of multisensory data from new contact-rich tasks. MuSe enablesimproved performance on pret... | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Figure 2: MuSe architecture. MuSe encodes image, proprioceptive, language, and optional force-torque (F/T) histories with modality-specific encoders, then fuses them through token-level early fusion and late fusion via cross- attention adapters. The joint sequ... | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Figure 4: L 2 error of predicted F/T signals on pretrain- ing tasks. MuSe achieves the lowest error, while weakening fusion, removing video prediction, or removing experience replay increases prediction error. Experiment Setup. We collect | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Figure 3: We pretrain a policy (with no F/T) on 21 tasks, then finetune on 5 unique taskscontaining F/T information that do not exist in pretraining. We then evaluate MuSe on 3 sets of pretraining tasks to measure backwards transfer, and 3 sets of finetuning t... | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Figure 5: Cross-modal generalization of F/T prediction on pretraining tasks where F/T signals were recorded but never used for supervision. MuSe accurately predicts changes in F/T across all three axes (defined in top left). Failure modes include under or over... | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Table 1: Effect of adaptive compliance on contact-rich finetuning tasks. | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Table 2: Diffusion Policy baseline as an ablation of multi-sensory future prediction. | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Table 2 summarizes the comparison between DP and MuSe. | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 结果句 | •Forward transfer:Improve performance on new tasks using the new modality, compared with | 核对 baseline、样本量、任务覆盖和统计口径。 |
| 结果句 | •Backward transfer:Retain or improve the performance on pretraining tasks after learning new | 核对 baseline、样本量、任务覆盖和统计口径。 |
| 结果句 | collected (cross-modal generalization), and improved performance on finetuning tasks that benefit | 核对 baseline、样本量、任务覆盖和统计口径。 |
| 结果句 | ground-truth F/T, and bar plots compare MuSe task success rate with the corresponding baselines. | 核对 baseline、样本量、任务覆盖和统计口径。 |
| 结果句 | across modalities that generalizes beyond the finetuning data and improves backward transfer. | 核对 baseline、样本量、任务覆盖和统计口径。 |
| 结果句 | both contact-rich and pick-and-place tasks, showing improvements in real-world success rate and | 核对 baseline、样本量、任务覆盖和统计口径。 |

## 图表、公式与表格线索

图表线索：

- Figure 1: Multisensory continual learning. A policy is first pretrained on diverse vision-action data without force-torque (F/T) labels, then adapted with a small amount of multisensory data from new contact-rich tasks. MuSe enablesimproved performance on pretraining tasks with no addi- tional task-specific data(backwa...
- Figure 2: MuSe architecture. MuSe encodes image, proprioceptive, language, and optional force-torque (F/T) histories with modality-specific encoders, then fuses them through token-level early fusion and late fusion via cross- attention adapters. The joint sequence model predicts fu-
- Figure 4: L 2 error of predicted F/T signals on pretrain- ing tasks. MuSe achieves the lowest error, while weakening fusion, removing video prediction, or removing experience replay increases prediction error. Experiment Setup. We collect
- Figure 3: We pretrain a policy (with no F/T) on 21 tasks, then finetune on 5 unique taskscontaining F/T information that do not exist in pretraining. We then evaluate MuSe on 3 sets of pretraining tasks to measure backwards transfer, and 3 sets of finetuning tasks for forward transfer. MuSe outperforms the pretrained m...
- Figure 5: Cross-modal generalization of F/T prediction on pretraining tasks where F/T signals were recorded but never used for supervision. MuSe accurately predicts changes in F/T across all three axes (defined in top left). Failure modes include under or overestimation (middle left, bottom right). 4.2 Forward Transfer...
- Table 1: Effect of adaptive compliance on contact-rich finetuning tasks.
- Table 2: Diffusion Policy baseline as an ablation of multi-sensory future prediction.
- Table 2 summarizes the comparison between DP and MuSe.
- Table 3: Real-world task success on forward transfer (success credit / trials).
- Table 4: Real-world task success on backward transfer (success credit / trials).
- Table 5: Training data used for vision-only pretraining and multisensory finetuning.
- Figure 6: Backward Transfer: Evaluation details for pretraining tasks. Left column shows initial task variation during evaluation, second and third columns show successful rollouts with MuSe, fourth column shows failure modes with no finetuning (typically wrong application of force), and fifth column shows failure mode...
- Figure 7: Forward Transfer: Evaluation details for finetuning tasks. Left column shows initial task variation during evaluation, second and third columns show successful rollouts with MuSe, fourth column show failure modes with no F/T input (typically hits force limit or not enough appli- cation of force), and fifth co...

本地精选图：

![[papers/images/clark2026muse/method_4_page1.png|700]]
![[papers/images/clark2026muse/ablation_bars_page1.png|700]]
![[papers/images/clark2026muse/back_appendix2_page1.png|700]]
![[papers/images/clark2026muse/crossmodal_5_page1.png|700]]
![[papers/images/clark2026muse/experiments_13_page1.png|700]]
![[papers/images/clark2026muse/f_appendix2_page1.png|700]]
![[papers/images/clark2026muse/teaser-v11_page1.png|700]]

公式线索：

- `ities and robot actions. Leto t ={o 1`
- `L=λ aLact +λ oLobs +λ n+1Lnew.`
- `256×256frame to16×16 = 256spatial tokens of dimension 16. With patch size 1, each token`
- `condition on 4 history frames and predict 4 future frames, yielding4×256 = 1024visual tokens`
- `4 proprioceptive timesteps are concatenated into a4×36 = 144-dimensional vector and passed`

这些线索不等于完整视觉理解。需要解释图中具体曲线、表格数值或失败案例时，应回到 PDF 原图或运行抽图脚本补全图片。

## 主张-证据-边界矩阵

| 主张 / 结论 | 原文证据 | 证据位置 | 解释 | 边界 / 适用条件 |
| --- | --- | --- | --- | --- |
| 核心问题值得解决 |  | Abstract / Introduction | 先确认作者的问题定义是否真实、具体、可检验 | 需要与 Related Work 对照，避免把已有工作重新包装成缺口 |
| 方法机制能回应问题 |  | Method / Model | 看输入、表示、训练目标、输出是否形成闭环 | 需要 ablation 证明关键组件不可替代 |
| 实验支持有效性 | •Forward transfer:Improve performance on new tasks using the new modality, compared with •Backward transfer:Retain or improve the performance on pretraining tasks after learning new collected (cross-modal generalization), and improved performance on finetuning tasks that benefit ground-truth F/T, and bar plots compare MuSe task success rate with the corresponding baselines. | Experiments / Results | 看主结果是否覆盖任务、数据、baseline 和真实部署 | 指标可能只覆盖局部能力，不能直接外推到所有场景 |
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
