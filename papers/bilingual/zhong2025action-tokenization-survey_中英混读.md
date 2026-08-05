---
tags:
  - bilingual-reading
  - deep-reading
source_pdf: "[[papers/pdfs/zhong2025action-tokenization-survey.pdf]]"
paper: "[[@zhong2025action-tokenization-survey]]"
images: "papers/images/zhong2025action-tokenization-survey/"
image_index: "[[papers/images/zhong2025action-tokenization-survey/index.md]]"
created: 2026-07-11
generator: "setting/scripts/generate_reading_draft.py"
reading_standard: "fba534d bilingual full-reading"
extraction: "pypdf"
source_pages: 70
source_chars: 314393
---

# A Survey on Vision-Language-Action Models: An Action Tokenization Perspective

paper:: [[@zhong2025action-tokenization-survey]]
pdf:: [[papers/pdfs/zhong2025action-tokenization-survey.pdf]]
images:: [[papers/images/zhong2025action-tokenization-survey/index.md]]
reading:: [[papers/bilingual/zhong2025action-tokenization-survey_中英混读.md]]

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| Vision-Language-Action | 视觉-语言-动作模型 | 把视觉观测、语言指令和机器人动作统一到一个策略模型中。 |
| CoT | 具身思维链 | 把场景理解、任务分解和动作规划显式写成训练监督或中间推理。 |
| trajectory | 时间/轨迹建模 | 利用帧序列和历史上下文理解任务进展或未来结果。 |
| tactile | 触觉/接触信号 | 提供 RGB 难以看到的滑移、卡滞、接触法线和局部形变信息。 |
| latent | 潜在表示 | 模型内部用于压缩图像、动作、状态或未来预测的连续表示。 |
| Vision-Language-Action（VLA） | 论文专有缩写 | 论文用括号定义的专有缩写，此处已从上文完整写法还原；回看首次出现可核对精确定义。 |
| VILA-U | 论文专有缩写 | 论文中多次出现的缩写，需结合首次出现位置确认完整含义和作用。 |

## 摘要

The remarkable advancements of vision and language foundation models in multimodal understanding, reasoning, and generation has sparked growing efforts to extend such intelligence to the physical world, fueling the flourishing of vision-language-action (VLA) models. Despite seemingly diverse approaches, we observe that current VLA models can be unified under a single framework: vision and language inputs are processed by a series of VLA modules, producing a chain of \textit{action tokens} that progressively encode more grounded and actionable information, ultimately generating executable actions. We further determine that the primary design choice distinguishing VLA models lies in how action tokens are formulated, which can be categorized into language description, code, affordance, trajectory, goal state, latent representation, raw action, and reasoning. However, there remains a lack of comprehensive understanding regarding action tokens, significantly impeding effective VLA development and obscuring future directions. Therefore, this survey aims to categorize and interpret existing VLA research through the lens of action tokenization, distill the strengths and limitations of each token type, and identify areas for improvement. Through this systematic review and analysis, we offer a synthesized outlook on the broader evolution of VLA models, highlight underexplored yet promising directions, and contribute guidance for future research, hoping to bring the field closer to general-purpose intelligence.

中文解读：本文的核心定位需要结合 Introduction 与 Method 进一步确认。

这部分不是把摘要简单翻译成中文，而是先抓住作者的写作动作：作者通常先指出现有方法在哪个环节失效，再提出一个机制、模型、数据集或系统，最后用 benchmark、真实机器人或 ablation 证明它确实补上了这个缺口。

## 人工校订重点解读

### 统一视角：action token 是可行动中间量

作者把 action token 扩展为“任何逐步把 vision-language input 变成 executable action 的 descriptive guidance”，不局限于离散化关节动作。一个 VLA 可以形成 token chain：先 language/reasoning 分解任务，再生成 affordance、trajectory 或 goal state，最后由 latent/raw-action policy 执行。因此八类是分析坐标，不是互斥架构。

![[papers/images/zhong2025action-tokenization-survey/unified-framework-v8_page1.png|700]]

| Token 类型 | 强项 | 核心短板 | 适合的位置 |
|---|---|---|---|
| Language description | 可解释、组合性强、复用 LLM knowledge | 歧义、控制精度低、依赖 skill library | 长时程规划与 subgoal |
| Code | 控制流、工具调用、可执行结构清晰 | API brittleness 与安全风险 | Agent orchestration |
| Affordance | 空间 grounding 直接，可接 keypoint/mask/controller | 遮挡、3D/接触信息不足、偏局部 | 操作点与可达区域 |
| Trajectory | 显式时空意图，可利用人类视频 | 不包含完整动力学和接触约束 | 中层 motion guidance |
| Goal state | 表达“应到达什么状态”，适合生成/world model | 仍需 inverse dynamics，生成误差会传递 | 视觉规划与 imagined future |
| Latent representation | 紧凑、高容量、易跨模态压缩 | 不透明、难诊断、跨本体对齐难 | World/action representation |
| Raw action | 端到端闭环、可直接执行 | 机器人数据昂贵、动作空间异构、长时程弱 | 低层 action chunk |
| Reasoning | 显式分解、纠错与可解释性 | latency、faithfulness、语言动作错位 | 高层 deliberation |

![[papers/images/zhong2025action-tokenization-survey/action_token_visulazation_page1.png|700]]

### 如何用这套 taxonomy 读新论文

不要只问 backbone 是 VLM、diffusion 还是 world model；应依次问：第一个可行动 token 是什么、谁生成、谁消费、监督来自哪里、是否跨本体、错误会在哪一级放大。复杂 agent 的现实方向更可能是 hybrid hierarchy，而不是八类中选一个全局最优表示。

### 证据性质与时效边界

这是 taxonomy survey，不提供统一 benchmark。它以时间线、各类别论文表格、数据金字塔和定性优缺点作证据，不能把类别结论理解为性能排名。2025 年后的 flow policy、world-action model、RL post-training 与新 tokenizer 更新很快，使用时应把它当坐标系而不是静态清单。

## 论文主线

如果用一条线串起全文，可以这样读：

1. **问题入口**：从 Introduction 回看作者如何定义失败模式、任务缺口和评价目标。
2. **方法钩子**：方法机制需要从 Method / Model / Architecture 章节继续细化。
3. **证据出口**：证据链需要从 Experiments / Evaluation / Results 章节继续细化。
4. **引言铺垫的读法**：
- 这句话在铺设论文问题入口：它帮助读者理解为什么这件事值得做。
  原文线索：`In recent years, Artificial Intelligence (AI) has made remarkable strides toward general-purpose intelligence.`
- 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。
  原文线索：`Central to this progress is the emergence of foundation models [1, 2]—large neural networks trained on internet-scale data, which acquire broad and transferable capabilities by cap...`
- （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）
  原文线索：`As a prominent example, Large Language Models (LLMs), such as GPT-4 [3] and DeepSeek-R1 [4], excel at natural language understanding, reasoning, and generation, forming the backbon...`
- （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）
  原文线索：`In parallel, Vision Foundation Models (VFMs), such as CLIP [5], DINO [6, 7], and SAM [8, 9], have shown strong generalization across a wide range of vision tasks.`
- （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）
  原文线索：`Building upon these, Vision-Language Models (VLMs), exemplified by GPT-4o [10], Gemini 2.5 Pro [11], and Qwen2.5-VL [12], integrate visual and textual modalities to enable multimod...`

阅读时要盯住一个问题：作者的方法机制是否真的直接解决了引言中定义的失败模式，还是只是给同一问题换了更大的模型或更多的数据。

## 贡献与结论对照

| 贡献 / 结论 | 方法位置 | 证据 / 结论 |
| --- | --- | --- |
| 定义核心问题 | Abstract / Introduction |  |
| 提出主要方法或系统 | Method / Model / Architecture | 2.2 Vision Foundation Models . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9 2.3 Vision-Language Models . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10 |
| 通过实验验证主张 | Experiments / Evaluation / Results | corpora, enabling the model to learn rich, context-aware representations that significantly improve downstream sources enables learning to be effectively applied at scale, resulting in general-purpose models that outperform Another line of work improves reasoning capabilities by scaling test-time computation. Following the success of Transformer in the language domain, the computer vision community has begun to |
| 暴露适用边界 | Discussion / Limitations / failure cases | 需要回看作者是否承认失败案例、数据边界或部署限制。 |

## 结构地图

| 原文位置 | 作者在这一部分做什么 | 与全文主线的关系 | 关键图表 / 公式 |
| --- | --- | --- | --- |
| 2.2 Vision Foundation Models . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9 | 给出方法机制，是判断论文贡献是否成立的主要位置。 | 回答怎么做。 | 待回看 PDF 图表 |
| 4 Language Description as Action Tokens 14 | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 4.2 Advantages of Language Descriptions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16 | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 5 Code as Action Tokens 17 | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 6 Affordance as Action Tokens 19 | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 6.4 Affordance Maps: Dense Spatial Fields . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22 | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 7 Trajectory as Action Tokens 23 | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 8 Goal State as Action Tokens 25 | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 8.2 Multi-Frame Video as Goal State . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27 | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 9 Latent Representation as Action Tokens 28 | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 9.4 Advantages of Latent Representation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 31 | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 10 Raw Action as Action Tokens 31 | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 10.7 Recent Advancements . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36 | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 11.3 Advantages of Reasoning as Action Tokens . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 39 | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 12.2 Middle Layer: Synthetic and Simulation Data . . . . . . . . . . . . . . . . . . . . . . . . . . . 40 | 提供经验证据，需要重点核对指标、baseline、ablation 和真实部署设置。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 13.5 From Capability-Centric to Safety-Aware . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45 | 补充论文主线中的一个环节，需要结合上下文判断其论证功能。 | 为主线提供背景或细节支撑。 | 待回看 PDF 图表 |
| 14 Conclusion 45 | 收束主张，并指出方法产出和后续方向。 | 回答边界和意义。 | 待回看 PDF 图表 |
| 1. Introduction | 定义任务、指出现有方法缺口，并把读者带到本文的核心主张。 | 回答为什么要做。 | Figure 1| We present a unified framework of VLA from anaction tokenizationperspective. Action token refers broadly to an...<br>Figure 2| Visualization of action tokens in a single embodied task. Given the same vision and language inputs, different... |

## 按原文 section 精读

### 1. 2.2 Vision Foundation Models . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9

#### 高层故事流

给出方法机制，是判断论文贡献是否成立的主要位置。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“回答怎么做。”来读。给出方法机制，是判断论文贡献是否成立的主要位置。

PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。

#### 关键原文线索

- 未抽取到稳定原文线索。

#### 回看重点

- 输入、隐藏表示、训练目标和输出之间是否闭合。
- 每个新增模块是否有对应 ablation 或对照实验支撑。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 2. 4 Language Description as Action Tokens 14

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。

#### 关键原文线索

- 未抽取到稳定原文线索。

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 3. 4.2 Advantages of Language Descriptions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。

#### 关键原文线索

- 未抽取到稳定原文线索。

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 4. 5 Code as Action Tokens 17

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。

#### 关键原文线索

- 未抽取到稳定原文线索。

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 5. 6 Affordance as Action Tokens 19

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。

#### 关键原文线索

- 未抽取到稳定原文线索。

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 6. 6.4 Affordance Maps: Dense Spatial Fields . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。

#### 关键原文线索

- 未抽取到稳定原文线索。

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 7. 7 Trajectory as Action Tokens 23

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

Trajectories（时间/轨迹建模）

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

术语上先抓住 Trajectories（时间/轨迹建模）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。

#### 关键原文线索

- 未抽取到稳定原文线索。

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：Trajectories（时间/轨迹建模） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 8. 8 Goal State as Action Tokens 25

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。

#### 关键原文线索

- 未抽取到稳定原文线索。

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 9. 8.2 Multi-Frame Video as Goal State . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。

#### 关键原文线索

- 未抽取到稳定原文线索。

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 10. 9 Latent Representation as Action Tokens 28

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

Latent（潜在表示）

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

术语上先抓住 Latent（潜在表示）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。

#### 关键原文线索

- 未抽取到稳定原文线索。

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：Latent（潜在表示） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 11. 9.4 Advantages of Latent Representation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 31

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。

#### 关键原文线索

- 未抽取到稳定原文线索。

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 12. 10 Raw Action as Action Tokens 31

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

VLA（视觉-语言-动作模型）

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

术语上先抓住 VLA（视觉-语言-动作模型）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。

#### 关键原文线索

- 未抽取到稳定原文线索。

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：VLA（视觉-语言-动作模型） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 13. 10.7 Recent Advancements . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。

#### 关键原文线索

- 未抽取到稳定原文线索。

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 14. 11.3 Advantages of Reasoning as Action Tokens . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 39

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。

#### 关键原文线索

- 未抽取到稳定原文线索。

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 15. 12.2 Middle Layer: Synthetic and Simulation Data . . . . . . . . . . . . . . . . . . . . . . . . . . . 40

#### 高层故事流

提供经验证据，需要重点核对指标、baseline、ablation 和真实部署设置。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。提供经验证据，需要重点核对指标、baseline、ablation 和真实部署设置。

PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。

#### 关键原文线索

- 未抽取到稳定原文线索。

#### 回看重点

- 数据集、baseline、指标和样本量是否足以支撑摘要中的强结论。
- 主结果之外是否有 failure cases、消融和真实机器人验证。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 16. 13.5 From Capability-Centric to Safety-Aware . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45

#### 高层故事流

补充论文主线中的一个环节，需要结合上下文判断其论证功能。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

本节术语需结合上下文回看。

#### 原文内容讲解

这一节要按“为主线提供背景或细节支撑。”来读。补充论文主线中的一个环节，需要结合上下文判断其论证功能。

PDF 文本抽取没有给出稳定句子，需要回到原文版面按段落补读。

#### 关键原文线索

- 未抽取到稳定原文线索。

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| 待从原文段落继续细化 | 本节补充论文主线 | 本节正文 | 注意抽取文本可能不完整。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 17. 14 Conclusion 45

#### 高层故事流

收束主张，并指出方法产出和后续方向。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

Vision-Language-Action（视觉-语言-动作模型）

#### 原文内容讲解

这一节要按“回答边界和意义。”来读。收束主张，并指出方法产出和后续方向。

术语上先抓住 Vision-Language-Action（视觉-语言-动作模型）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。

#### 关键原文线索

- `[Page 5] A Survey on Vision-Language-Action Models: An Action Tokenization Perspective`

#### 回看重点

- 这一节与全文主线的关系需要回到前后 section 一起读，不要只摘单句结论。
- 术语复查：Vision-Language-Action（视觉-语言-动作模型） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| [Page 5] A Survey on Vision-Language-Action Models: An Action Tokenization Perspective | 这是本节推进主线的一个局部论点，需要结合前后段落判断它承担的是背景、机制还是证据功能。 | 14 Conclusion 45 | 注意是否被后续实验直接验证。 |

#### 关键公式、表格、原文图嵌入与解释

| 类型 | 原文编号 / 位置 | 对应内容 | 在本节证明什么 |
| --- | --- | --- | --- |
| - | - | 本节未稳定抽取到公式/图表标题 | 需要回到 PDF 原文核对。 |


### 18. 1. Introduction

#### 高层故事流

定义任务、指出现有方法缺口，并把读者带到本文的核心主张。 本节在原文中的作用不是孤立介绍细节，而是服务于全文主线：先把问题讲清楚，再说明方法为什么这样设计，最后给实验结论铺垫。

#### 关键术语 / 机制

VLA（视觉-语言-动作模型）、trajectories（时间/轨迹建模）、latent（潜在表示）

#### 原文内容讲解

这一节要按“回答为什么要做。”来读。定义任务、指出现有方法缺口，并把读者带到本文的核心主张。

术语上先抓住 VLA（视觉-语言-动作模型）、trajectories（时间/轨迹建模）、latent（潜在表示）。这些词不是孤立概念，而是本节把问题定义、模型设计和实验证据连起来的接口。

可以把正文拆成下面几步：

1. 这句话在铺设论文问题入口：它帮助读者理解为什么这件事值得做。

2. 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。

3. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

4. （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。）

#### 关键原文线索

- `In recent years, Artificial Intelligence (AI) has made remarkable strides toward general-purpose intelligence.`
- `Central to this progress is the emergence of foundation models [1, 2]—large neural networks trained on internet-scale data, which acquire broad and transferable capabilities by capturing the diverse knowledge and pattern...`
- `As a prominent example, Large Language Models (LLMs), such as GPT-4 [3] and DeepSeek-R1 [4], excel at natural language understanding, reasoning, and generation, forming the backbone of many text-based applications.`
- `In parallel, Vision Foundation Models (VFMs), such as CLIP [5], DINO [6, 7], and SAM [8, 9], have shown strong generalization across a wide range of vision tasks.`

#### 回看重点

- 缺口是否具体到可验证的失败模式，而不只是泛泛说现有方法不足。
- 作者给出的 motivating example 是否会在实验中被直接覆盖。
- 术语复查：VLA（视觉-语言-动作模型）, trajectories（时间/轨迹建模）, latent（潜在表示） 在本节是否有明确变量、模块或实验定义。

#### 论证功能表

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| In recent years, Artificial Intelligence (AI) has made remarkable strides toward general-purpose intelligence. | 这句话在铺设论文问题入口：它帮助读者理解为什么这件事值得做。 | 1. Introduction | 注意是否被后续实验直接验证。 |
| Central to this progress is the emergence of foundation models [1, 2]—large neural networks trained on internet-scale data, which acquire broad and transferable capabilities by cap... | 这是方法机制线索：重点看输入表示、模块连接、训练目标和推理时如何使用。 | 1. Introduction | 注意是否被后续实验直接验证。 |
| As a prominent example, Large Language Models (LLMs), such as GPT-4 [3] and DeepSeek-R1 [4], excel at natural language understanding, reasoning, and generation, forming the backbon... | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 1. Introduction | 注意是否被后续实验直接验证。 |
| In parallel, Vision Foundation Models (VFMs), such as CLIP [5], DINO [6, 7], and SAM [8, 9], have shown strong generalization across a wide range of vision tasks. | （与上一条线索承担相近的论证功能，重点看它补充了哪个新的对象、细节或数据。） | 1. Introduction | 注意是否被后续实验直接验证。 |

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

2.2 Vision Foundation Models . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9 2.3 Vision-Language Models . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

公式 / 数学定义线索：

- `ΔT=[0.2,−0.2,0.1]ΔR=[15°,16°,22°] ΔT=[0.05,0.1,0.02]ΔR=[−15°,−10°,23°] ΔT=[0.02,−0.1,−0.1]ΔR=[15°,10°,−8°] ΔT=[0,0.2,−0.1]ΔR=[−10°,−8°,−12°]ΔT=[0,0.2,0.1]ΔR=[10°,−7°,−16°]`
- `contact edges. They are typically defined ask =[x, d], wherex, d∈ ℝ3, withx denoting the spatial contact`
- `scene. A 2D bounding box is typically defined asB ={(𝑥tl,𝑦 tl),(𝑥br,𝑦 br)}, marking the top-left and bottom-`
- `2024. ISSN 2835-8856. URL https://openreview.net/forum?id=a68SUt6zFt. Featured`
- `https://openreview.net/forum?id=bdHkMjBJG_w.`
- `URL https://openreview.net/forum?id=F1TKzG8LJO.`
- `openreview.net/forum?id=ZMnD6QZAE6.`
- `id=928V4Umlys.`


## 实验设置、数据集、基线、指标

读实验时不要只看最终分数，要按 `数据集 -> baseline -> 指标 -> 主结果 -> 消融 -> 失败案例` 走。

实验正文线索：

- 这是数据或实验设置线索：重点看数据来源、标注协议、任务分布和真实部署边界。 原文线索：`12.2 Middle Layer: Synthetic and Simulation Data .`

指标 / 结果句线索：

- corpora, enabling the model to learn rich, context-aware representations that significantly improve downstream
- sources enables learning to be effectively applied at scale, resulting in general-purpose models that outperform
- Another line of work improves reasoning capabilities by scaling test-time computation.
- Following the success of Transformer in the language domain, the computer vision community has begun to
- SigLIP [82] improves upon CLIP by replacing the original softmax operations with a sigmoid loss,
- et al.[85] proposes a simple yet effective improvement to these ViT-based models by adding learnable register
- SAMURAI [89] improves the visual object tracking (VOT) performance
- Grounding DINO 1.5 [93] scales model size and training data, improving
- LLaVA-1.5 [118] improves upon LLaVA by adopting a stronger vision encoder,
- It incorporates window attention in the vision encoder to improve inference efficiency.
- Prismatic VLMs, which consistently outperform LLaVA-1.5 across benchmarks and have been used later in
- introducing feedback loops: the system continuously prompts the LLM with signals like success detection,


## 主要结果、消融或对比

| 证据类型 | 原文线索 | 读法 |
| --- | --- | --- |
| 图表/表格 | Figure 1| We present a unified framework of VLA from anaction tokenizationperspective. Action token refers broadly to any descriptive guidance iteratively generated by VLAs that ultimately leads to action execution, extending beyond the notion of raw action. ∗... | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Table of Contents 1 Introduction 5 2 The Evolution of Language and Vision Foundation Models 6 2.1 Language Foundation Models . | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Figure 2| Visualization of action tokens in a single embodied task. Given the same vision and language inputs, different VLA models encode them into diverse action tokens, each conveying varying forms of actionable guidance and requiring distinct strategies fo... | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Figure 3| Evolution timeline of foundation models, VLA models, and data sources. The U-shape reflects how the growing proliferation of VLA is supported by progress in foundation models and data. 8 | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Figure 4| A Venn diagram showing the interrelationships among key AI fields. VLA models intersect with digital AI, hardware, and robotics, representing a core subfield of Embodied AI and a key | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | Table 1| Overview of key advantages, limitations, and empirical results of each type of action token. | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | table summarizing the surveyed works, examining similarities and differences across multiple dimensions pertinent to the respective action token. | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 图表/表格 | table” convey what the robot should accomplish, serving as semantic anchors that can be assigned to skills or policies. | 看它是否直接支撑核心主张，而不是只展示 qualitative demo。 |
| 结果句 | corpora, enabling the model to learn rich, context-aware representations that significantly improve downstream | 核对 baseline、样本量、任务覆盖和统计口径。 |
| 结果句 | sources enables learning to be effectively applied at scale, resulting in general-purpose models that outperform | 核对 baseline、样本量、任务覆盖和统计口径。 |
| 结果句 | Another line of work improves reasoning capabilities by scaling test-time computation. | 核对 baseline、样本量、任务覆盖和统计口径。 |
| 结果句 | Following the success of Transformer in the language domain, the computer vision community has begun to | 核对 baseline、样本量、任务覆盖和统计口径。 |
| 结果句 | SigLIP [82] improves upon CLIP by replacing the original softmax operations with a sigmoid loss, | 核对 baseline、样本量、任务覆盖和统计口径。 |
| 结果句 | et al.[85] proposes a simple yet effective improvement to these ViT-based models by adding learnable register | 核对 baseline、样本量、任务覆盖和统计口径。 |

## 图表、公式与表格线索

图表线索：

- Figure 1| We present a unified framework of VLA from anaction tokenizationperspective. Action token refers broadly to any descriptive guidance iteratively generated by VLAs that ultimately leads to action execution, extending beyond the notion of raw action. ∗Equal contribution.†Corresponding author(s): Yuanpei Chen{yu...
- Table of Contents 1 Introduction 5 2 The Evolution of Language and Vision Foundation Models 6 2.1 Language Foundation Models .
- Figure 2| Visualization of action tokens in a single embodied task. Given the same vision and language inputs, different VLA models encode them into diverse action tokens, each conveying varying forms of actionable guidance and requiring distinct strategies for token generation and post-processing. 7
- Figure 3| Evolution timeline of foundation models, VLA models, and data sources. The U-shape reflects how the growing proliferation of VLA is supported by progress in foundation models and data. 8
- Figure 4| A Venn diagram showing the interrelationships among key AI fields. VLA models intersect with digital AI, hardware, and robotics, representing a core subfield of Embodied AI and a key
- Table 1| Overview of key advantages, limitations, and empirical results of each type of action token.
- table summarizing the surveyed works, examining similarities and differences across multiple dimensions pertinent to the respective action token.
- table” convey what the robot should accomplish, serving as semantic anchors that can be assigned to skills or policies.
- Table 2| Overview of VLA research using language description as action tokens.
- Tabletoprearrangement(simulation, real-world); mobilemanipulation(office kitchen) UR 5e with a gripper; Everyday Robots PaLM-E [14] PaLM-E-562BTrained onVQA, web text, manipulation datasets VLM generates plansFree-form InteractiveLanguagepolicy, RT-1 Trained as in theoriginal papers
- Tabletopmanipulation; humanoidmanipulation UR 5e with a gripper; Humanoid ViLa [143] GPT-4V N/A VLM generates plansvia CoT reasoning ina zero-shot modePredefinedScripted, RL, BC policiesTrained
- Tabletopmanipulation(simulation, real-world) Franka Panda 3D-VLA[38]BLIP-2FlanT 5XL Fine-tuned on acurated 3Dembodiedinstruction tuningdataset containing 2M scene-language-action pairs VLM generatesplans withinteractive tokensFree-formStable Diffusionv 1.4, Point-EFine-tunedLong-horizon tasksin RLBench [144]and CALVIN...
- Table bussing, make a sandwich, grocery shopping UR 5e with a gripper; ARX with a gripper; ARX with a gripperand mobile base 𝜋0.5[125] PaliGemma-3B Trained on robotdata, high-levelsubtask predictiondata, andmulti-modal webdata VLM generates plansFree-form 𝜋0.5
- Tabletopmanipulation NR NaVILA [150] ViLa Trained on 2KYouTube egocentrictouring videos VLM generatesmid-level actionswith spatialinformation Free-form Visuallocomotionpolicy Trained via PPOVLN-CE-Isaac [150]; navigation(25 tasks, real-world) Unitree Go 2; Unitree H 1; Booster T 1
- Table 3| Overview of VLA research using code as action tokens.
- Table 4| Overview of VLA research using affordance as action tokens.

本地精选图：

![[papers/images/zhong2025action-tokenization-survey/action_token_visulazation_page1.png|700]]
![[papers/images/zhong2025action-tokenization-survey/latent_page1.png|700]]
![[papers/images/zhong2025action-tokenization-survey/timeline_page1.png|700]]
![[papers/images/zhong2025action-tokenization-survey/unified-framework-v8_page1.png|700]]

公式线索：

- `ΔT=[0.2,−0.2,0.1]ΔR=[15°,16°,22°] ΔT=[0.05,0.1,0.02]ΔR=[−15°,−10°,23°] ΔT=[0.02,−0.1,−0.1]ΔR=[15°,10°,−8°] ΔT=[0,0.2,−0.1]ΔR=[−10°,−8°,−12°]ΔT=[0,0.2,0.1]ΔR=[10°,−7°,−16°]`
- `contact edges. They are typically defined ask =[x, d], wherex, d∈ ℝ3, withx denoting the spatial contact`
- `scene. A 2D bounding box is typically defined asB ={(𝑥tl,𝑦 tl),(𝑥br,𝑦 br)}, marking the top-left and bottom-`
- `2024. ISSN 2835-8856. URL https://openreview.net/forum?id=a68SUt6zFt. Featured`
- `https://openreview.net/forum?id=bdHkMjBJG_w.`
- `URL https://openreview.net/forum?id=F1TKzG8LJO.`
- `openreview.net/forum?id=ZMnD6QZAE6.`
- `id=928V4Umlys.`
- `Abstractions for Planning, 2024. URLhttps://openreview.net/forum?id=ZGbWq3VqrO.`
- `https://openreview.net/forum?id=NCOP0KYb0u.`
- `URL https://openreview.net/forum?id=S70MgnIA0v.`
- `forum?id=YicbFdNTTy.`

这些线索不等于完整视觉理解。需要解释图中具体曲线、表格数值或失败案例时，应回到 PDF 原图或运行抽图脚本补全图片。

## 主张-证据-边界矩阵

| 主张 / 结论 | 原文证据 | 证据位置 | 解释 | 边界 / 适用条件 |
| --- | --- | --- | --- | --- |
| 核心问题值得解决 |  | Abstract / Introduction | 先确认作者的问题定义是否真实、具体、可检验 | 需要与 Related Work 对照，避免把已有工作重新包装成缺口 |
| 方法机制能回应问题 |  | Method / Model | 看输入、表示、训练目标、输出是否形成闭环 | 需要 ablation 证明关键组件不可替代 |
| 实验支持有效性 | corpora, enabling the model to learn rich, context-aware representations that significantly improve downstream sources enables learning to be effectively applied at scale, resulting in general-purpose models that outperform Another line of work improves reasoning capabilities by scaling test-time computation. Following the success of Transformer in the language domain, the computer vision community has begun to | Experiments / Results | 看主结果是否覆盖任务、数据、baseline 和真实部署 | 指标可能只覆盖局部能力，不能直接外推到所有场景 |
| 方法存在边界 |  | Limitations / Discussion / failure cases | 边界决定这篇论文什么时候值得引用、什么时候不能引用 | 如果作者未充分讨论，需要从失败案例和数据分布反推 |

## 局限与可追问点

- 文献笔记未记录明确局限，需要回看 Discussion、Limitations、Appendix 和失败案例。

额外需要追问：

- 数据是否覆盖足够多 embodiment、任务、传感器、场景和失败模式？
- Baseline 是否足够强，是否和本文方法使用了同等数据、模型规模和计算预算？
- 指标是否直接对应机器人最终成功率，还是只衡量 proxy signal？
- 真实机器人实验是否足够多，是否报告失败案例和部署约束？


## 与当前库的连接

- 连接 VLA/机器人策略路线：可与 ZR-0、X-Tokenizer、HoloAgent-0、STEAM/WARP-RM 对照，重点比较动作表示、推理监督、数据筛选和闭环执行。

## 精读路线 / 为什么需要回看

1. 先读 `摘要` 和 `论文主线`，确认作者到底把哪个缺口定义为核心问题。
2. 再读 `方法细节` 和对应原文 section，检查输入、表示、训练目标、推理过程和模块依赖是否闭合。
3. 最后读 `实验设置、数据集、基线、指标` 与 `主要结果、消融或对比`，重点核对是否有真实机器人、跨任务、跨 embodiment、失败案例和 ablation。
4. 如果后续要写 related work，把 `贡献与结论对照` 和 `主张-证据-边界矩阵` 作为引用依据，不要只引用摘要结论。
