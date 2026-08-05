---
tags:
  - paper
status: unread
aliases:
  - "A Survey on Vision-Language-Action Models: An Action Tokenization Perspective"
year: 2025
title: "A Survey on Vision-Language-Action Models: An Action Tokenization Perspective"
doi: 
arxiv: "2507.01925"
url: "https://arxiv.org/abs/2507.01925"
venue: "arXiv preprint"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/zhong2025action-tokenization-survey.pdf]]"
reading: "[[papers/bilingual/zhong2025action-tokenization-survey_中英混读.md]]"
images: "papers/images/zhong2025action-tokenization-survey/"
image_index: "[[papers/images/zhong2025action-tokenization-survey/index.md]]"
authors:
  - "[[Yifan Zhong]]"
  - "[[Fengshuo Bai]]"
  - "[[Shaofei Cai]]"
  - "[[Xuchuan Huang]]"
  - "[[Zhang Chen]]"
  - "[[Xiaowei Zhang]]"
  - "[[Yuanfei Wang]]"
  - "[[Shaoyang Guo]]"
  - "[[Tianrui Guan]]"
  - "[[Ka Nam Lui]]"
  - "[[Zhiquan Qi]]"
  - "[[Yitao Liang]]"
  - "[[Yuanpei Chen]]"
  - "[[Yaodong Yang]]"
institutions:
topics:
  - vision-language-action model
  - action tokenization
  - embodied AI survey
  - action representation
  - robot learning
---

# A Survey on Vision-Language-Action Models: An Action Tokenization Perspective

- [x] PDF:: [[papers/pdfs/zhong2025action-tokenization-survey.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/zhong2025action-tokenization-survey_中英混读.md]]
- [x] 地图维护:: [[论文地图]]
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

The remarkable advancements of vision and language foundation models in multimodal understanding, reasoning, and generation has sparked growing efforts to extend such intelligence to the physical world, fueling the flourishing of vision-language-action (VLA) models. Despite seemingly diverse approaches, we observe that current VLA models can be unified under a single framework: vision and language inputs are processed by a series of VLA modules, producing a chain of \textit{action tokens} that progressively encode more grounded and actionable information, ultimately generating executable actions. We further determine that the primary design choice distinguishing VLA models lies in how action tokens are formulated, which can be categorized into language description, code, affordance, trajectory, goal state, latent representation, raw action, and reasoning. However, there remains a lack of comprehensive understanding regarding action tokens, significantly impeding effective VLA development and obscuring future directions. Therefore, this survey aims to categorize and interpret existing VLA research through the lens of action tokenization, distill the strengths and limitations of each token type, and identify areas for improvement. Through this systematic review and analysis, we offer a synthesized outlook on the broader evolution of VLA models, highlight underexplored yet promising directions, and contribute guidance for future research, hoping to bring the field closer to general-purpose intelligence.

## 一句话定位

这篇综述不按 backbone 或 training recipe 划分 VLA，而把所有中间可执行指导统一成 action tokens，并用 language、code、affordance、trajectory、goal state、latent representation、raw action、reasoning 八类 token 解释不同模型如何把视觉语言语义逐步落到机器人动作。

## 方法 / 对象

- 统一框架：vision/language inputs 经一个或多个 VLA modules 产生 action-token chain，再由生成器、规划器或低层 policy 转成 executable actions；action token 的含义因此比离散 raw-action token 更宽。
- Language description：可解释、可组合且继承 LLM 知识，但需要低层 skill library，语言空间歧义且难表达精密连续控制。
- Code：适合调用工具、控制流和长期任务组合，执行结构清楚；代价是 API/环境变化会导致 brittleness，错误代码可能直接变成危险动作。
- Affordance：keypoint、box、mask、dense map 提供空间 grounding，便于接低层控制器；但多为局部/短视表示，遮挡与 3D 几何变化会破坏可靠性。
- Trajectory：显式表达时空运动意图并可与人类视频对齐；但轨迹只是期望路径，不含完整动力学、接触力和本体约束。
- Goal state：用目标图像或视频描述“应该到哪里”，适合借助生成模型和 world model；但从目标到动作仍需 inverse dynamics，生成误差会传给控制。
- Latent representation：高容量、紧凑且可跨模态压缩；问题是语义不可解释、跨本体对齐困难，并可能把无关因素编码进去。
- Raw action：端到端、闭环且执行直接，是 RT-1/RT-2、OpenVLA、diffusion/flow action heads 的主流路线；代价是依赖昂贵机器人数据、动作空间异构和长时程推理弱。
- Reasoning：用 CoT、subgoal 或 embodied reasoning 显式分解复杂任务，可提高可解释性与纠错能力；但推理延迟、faithfulness 和“语言正确但动作错误”仍是核心问题。

## 证据

- 综述的主要证据不是统一 benchmark，而是跨论文 taxonomy、时间线、每类方法表格及统一 action-token visualization。
- 八类 token 并非互斥：一个 agent 可以先产生 language plan，再产生 affordance/trajectory，最后输出 latent 或 raw action；真正设计变量是 token chain 的层级、训练信号与后处理器。
- 数据被分为 web/human video、synthetic/simulation、real robot 三层，分别提供语义规模、交互覆盖与物理真实性；没有单层数据能同时解决三者。
- 未来趋势被归纳为 VLA model→VLA agent、imitation→RL、受限硬件→全身灵巧与多模态、capability→safety、data scarcity→scalability。

## 局限

- 分类依赖“主要 action token”给方法贴标签，但现实系统通常是 hybrid token chain，边界存在主观性。
- 论文发表于 2025 年，快速发展的 flow policy、world-action model、RL post-training 和新型 tokenizer 很快会使表格过时。
- 各类别引用的任务、机器人和指标不统一，因此“优缺点”多是定性综合，不能直接当作性能排名。
- action token 作为宽泛概念解释力强，但如果不同时区分 representation、generation objective 和 executor，可能把不同层次的设计混在一起。

## 我的阅读笔记

这篇最适合作为“找坐标系”的入口。读新 VLA 时可以先问：模型产生的第一个可行动中间量是什么，谁消费它，它是否可监督、可解释、可跨本体，以及错误在哪一层被放大。这个问题通常比只问 backbone 是 VLM、diffusion 还是 world model 更能解释系统行为。

与 [[@kang2026x-tokenizer]] 对照时尤其有用：survey 给出八类宏观表示，X-Tokenizer 一类工作则在 latent/raw-action 交界处追求跨模态统一。值得保留的判断是 action tokenization 没有单一最优解；长时程 agent 更可能采用 reasoning/language → affordance/goal/trajectory → latent/raw action 的分层混合链。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
