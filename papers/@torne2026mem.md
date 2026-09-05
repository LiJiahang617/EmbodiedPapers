---
tags:
  - paper
  - cat/vla
  - cat/memory
  - cat/foundation-model
status: unread
aliases:
  - MEM
  - π0.6-MEM
  - "MEM: Multi-Scale Embodied Memory for Vision Language Action Models"
year: 2026
title: "MEM: Multi-Scale Embodied Memory for Vision Language Action Models"
doi: "10.48550/arXiv.2603.03596"
arxiv: "2603.03596v2"
url: "https://arxiv.org/abs/2603.03596"
venue: "arXiv preprint"
venue_short: "arXiv"
arxiv_url: "https://arxiv.org/abs/2603.03596"
arxiv_doi: "10.48550/arXiv.2603.03596"
pdf_url: "https://arxiv.org/pdf/2603.03596v2"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/torne2026mem.pdf]]"
reading: "[[papers/bilingual/torne2026mem_中英混读.md]]"
images: "papers/images/torne2026mem/"
image_index: "[[papers/images/torne2026mem/index.md]]"
map_axis: "具身智能/VLA/多尺度具身记忆与长时程任务"
map_brief: "PI 给 π0.6 装的多尺度记忆，短时用零新增参数的视频编码器把几十秒稠密观测压进当前帧 token，长时让高层策略自更新一段自然语言摘要并训练它主动压缩丢信息，防住训练推理分布偏移，解锁十五分钟厨房任务与看着失败换策略的上下文内适应。"
map_role: "VLA 记忆设计的参考答案与选型地图，回答什么尺度的记忆该用什么模态装、记忆能力为什么必须进预训练。"
authors:
  - "[[Marcel Torne]]"
  - "[[Karl Pertsch]]"
  - "[[Homer Walke]]"
  - "[[Kyle Vedder]]"
  - "[[Suraj Nair]]"
  - "[[Brian Ichter]]"
  - "[[Allen Z. Ren]]"
  - "[[Haohuan Wang]]"
  - "[[Jiaming Tang]]"
  - "[[Kyle Stachowicz]]"
  - "[[Karan Dhabalia]]"
  - "[[Michael Equi]]"
  - "[[Quan Vuong]]"
  - "[[Jost Tobias Springenberg]]"
  - "[[Sergey Levine]]"
  - "[[Chelsea Finn]]"
  - "[[Danny Driess]]"
institutions:
  - "[[Physical Intelligence]]"
  - "[[Stanford University]]"
  - "[[UC Berkeley]]"
  - "[[MIT]]"
topics:
  - robot memory
  - language memory
  - video encoder
  - long-horizon manipulation
  - in-context adaptation
  - partial observability
  - hierarchical policy
  - π0.6
  - space-time attention
  - real-time inference
---

# MEM: Multi-Scale Embodied Memory for Vision Language Action Models

- [x] PDF:: [[papers/pdfs/torne2026mem.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/torne2026mem_中英混读.md]]
- [x] 图片索引:: [[papers/images/torne2026mem/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[robot memory]], [[language memory]], [[video encoder]], [[@intelligence2025pi06-vla-that-learns]], [[@dexmal2026dm05]], [[@zhao2026atlasvla]], [[@jiang2026robottt]], [[@feng2026wam-ttt]], [[@zhou2026holoagent0]]
affiliation:: [[Physical Intelligence]], [[Stanford University]], [[UC Berkeley]], [[MIT]]

## Abstract

Conventionally, memory in end-to-end robotic learning involves inputting a sequence of past observations into the learned policy. However, in complex multi-stage real-world tasks, the robot's memory must represent past events at multiple levels of granularity: from long-term memory that captures abstracted semantic concepts (e.g., a robot cooking dinner should remember which stages of the recipe are already done) to short-term memory that captures recent events and compensates for occlusions (e.g., a robot remembering the object it wants to pick up once its arm occludes it). In this work, our main insight is that an effective memory architecture for long-horizon robotic control should combine multiple modalities to capture these different levels of abstraction. We introduce Multi-Scale Embodied Memory (MEM), an approach for mixed-modal long-horizon memory in robot policies. MEM combines video-based short-horizon memory, compressed via a video encoder, with text-based long-horizon memory. Together, they enable robot policies to perform tasks that span up to fifteen minutes, like cleaning up a kitchen, or preparing a grilled cheese sandwich. Additionally, we find that memory enables MEM policies to intelligently adapt manipulation strategies in-context.

## 一句话定位

主张机器人策略的长短时记忆需要不同模态来装并给出一套系统实现，短时记忆用零新增参数的视频编码器（每 4 层插跨时间因果注意力、顶层丢历史 token）把最长 54 秒稠密观测压进当前帧 token 预算，长时记忆让高层策略把语义事件写成自更新、主动压缩的自然语言摘要，装进 π0.6 后能做需要十五分钟记忆的厨房任务，并解锁看着短时记忆里的失败尝试换操作策略的能力。

## 方法 / 对象

- 分解，$\pi\approx\pi_{LL}(a\mid o_{t-K:t},l_{t+1},g)\cdot\pi_{HL}(l_{t+1},m_{t+1}\mid o_t,m_t,g)$，新意在 $\pi_{HL}$ 以自己上一步的 $m_t$ 为条件预测 $m_{t+1}$，语言记忆是模型自读写的循环状态。
- 语言记忆训练标签由管线生成，episode 的子任务标注加成败指示交给现成 LLM，按「只留对未来执行相关的最小信息」原则产出摘要序列；模型被训练主动压缩丢弃（失败重试不入账），压缩同时换来推理速度和更小的训练推理分布偏移。
- 视频编码器，标准 ViT 每 4 层附加同 patch 跨时间步因果注意力（时空可分离，$O(Kn^2+nK^2)$），固定正弦时间编码且 $e(0)=0$，顶层只传当前帧 token 给骨干（下游 token 数与单帧 VLA 相同），零新增参数可直接继承任何预训练 ViT 权重。
- 集成 π0.6，Gemma3-4B VLM 加 860M 流匹配动作专家（知识绝缘，动作梯度不回流），FAST 离散 token 联合训练，448×448 至多四路相机；本体状态历史走线性投影连续嵌入。预训练 6 帧 1 秒间隔，后训练可扩到 18 帧 54 秒；真机推理用 RTC。
- 预训练数据混合遥操演示、rollout、人类纠正（π*0.6 同款）、视觉语言与视频字幕任务。

## 证据

- 长时程（每格 10 rollout，进度分，数值为读图近似），备菜 42 菜谱训练 5 菜谱未见场景评测，MEM 约 63% 对无记忆 π0.6 约 40%；整理厨房约 90% 对约 20%；消融显示纯视频约 28%、纯文本约 29%、朴素拼接文本约 35%，双组件缺一不可，压缩明显好于朴素拼接。
- 上下文适应，OOD 桌高捡筷子 +11 个百分点，未知铰链方向开冰箱 +62 个百分点（4 次抓取内开门判据），对照为同样纠正数据微调的无记忆 π0.6。
- 记忆能力横评（去掉语言记忆保证公平），平均约 73% 对 Proprio 约 39%、Pool 约 34%、无记忆约 29%；找物体约 89%（随机基线 25%）、三换杯约 76%、擦窗约 64%；Pool 在拆购物袋塌到约 13%，Proprio 在记环境状态的任务上失效。
- 预训练消融，只在后训练引入视频编码器（同一 π0.6 底座出发）明显更差，记忆能力须预训练注入；但 post-train-only 仍好于 Pool，编码器设计本身占优。
- 灵巧任务七个追平 π0.6，加记忆不掉分，反驳因果混淆退化的旧观察。

## 局限

- 高层策略的运行时开销无数字，语言记忆更新频率、单次生成长度、对整体控制时延的贡献都没报，Fig. 3 只测了视频编码器一侧。
- $m_{t+1}$ 依赖 $m_t$ 的循环设计有错误累积风险，十五分钟任务几十次更新，写错记忆的频率与自纠能力零分析。
- 语言记忆标签需要子任务标注加成败指示的 episode，数据基础设施门槛高，可复现性依赖 PI 的标注体系。
- 对照全是自家在 π0.6 上重实现的代表性简化版（Pool、Proprio），MemoryVLA、MemER 等已发表系统一个没直接比。
- 主结果全是柱状图加标准误，每格 10 rollout，无数表，引用数值只能目测近似。
- 计时类记忆是短板，煎三明治任务优势最小，「煎了多久」既难进文本也超出视频窗口。

## 我的阅读笔记

这篇的第一性设计原则值得画出来，记忆的模态跟着信息的性质走。要几个 bit 但保持几分钟的，用文本；要稠密空间细节但只保持几十秒的，用视频。Fig. 8 的横评把单模态方案的死角一个个照出来，Pool 死在长时（拆购物袋比无记忆还差），Proprio 死在环境状态，这张图以后做记忆选型可以直接引。

机制层面最有意思的是压缩那一段。朴素拼接历史指令的版本败在训练推理分布偏移，训练数据是近最优演示、每条指令只出现一次，推理时策略反复失败会堆出训练分布里不存在的重复序列。MEM 的解法是碗没拿起来就不更新记忆，失败被压缩掉。说到底，记忆机制的价值不只在记住什么，更在决定不记什么，这个洞察比架构本身更可迁移。

Fig. 9 那条结论对做训练配方的人是硬约束，记忆能力要在预训练长出来，后训练补装明显更差，哪怕底座是同一个 π0.6 检查点。配合「预训练 5 秒窗口、后训练扩到 1 分钟」的现象，正确姿势是预训练教会时序结构、后训练拉长窗口。

视频编码器是可以整包搬走的工程件，零新增参数、$e(0)=0$ 保证单帧初始化逐位等于预训练 ViT、每 4 层插时间注意力、顶层丢 token。对任何 ViT 底座的 VLA 这是个即插即用的短时记忆方案。

我的保留意见集中在系统时延和记忆出错两处，前者没报数字，后者没做分析，两个都是循环文本状态这个设计天然会被问的问题。另外上下文适应那两个惊艳数字（尤其冰箱 +62）别读成涌现能力，它需要专门采集含失败的纠正数据并在训练时把失败留在上下文里，是训出来的通路。

## 摘录

> the robot's memory must represent past events at multiple levels of granularity.

> the key novelty here is that πHL additionally predicts the updated language memory mt+1 based on its own previous prediction mt.

> Compressing the language memory helps keep it succinct (and thus inference fast) and reduces the potential for train-inference distribution shift, since fewer bits of information are carried over between timesteps.

> our encoder leaves the single-image performance of the VLM we start with invariant, and thus can be used to endow any pre-trained VLM with highly effective (yet computationally cheap) visual memory capabilities.

> pre-training the observation-based memory on a diverse data mix of robot and non-robot data significantly improves the ability of the model to leverage its memory.

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
