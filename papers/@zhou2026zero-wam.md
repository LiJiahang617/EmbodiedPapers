---
tags:
  - paper
status: unread
aliases:
  - "Zero-WAM: In-Context World-Action Modeling from Human Videos for Open-Ended Task Generalization"
year: 2026
title: "Zero-WAM: In-Context World-Action Modeling from Human Videos for Open-Ended Task Generalization"
doi: "10.48550/arXiv.2608.26103"
arxiv: "2608.26103v2"
url: "https://arxiv.org/abs/2608.26103"
project_url: "https://robbyant-research.github.io/Zero-WAM/"
code_url: "https://github.com/robbyant-research/Zero-WAM"
venue: "arXiv preprint"
openalex:
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/zhou2026zero-wam.pdf]]"
reading: "[[papers/bilingual/zhou2026zero-wam_中英混读.md]]"
images: "papers/images/zhou2026zero-wam/"
image_index: "[[papers/images/zhou2026zero-wam/index.md]]"
map_axis: "世界模型/WAM/人类视频任务规范与跨任务泛化"
map_brief: "把人类操作视频作为部署时的task specification，利用自动生成的HumanGen人机配对数据和IFP辅助目标训练causal video-action model，在没有目标任务机器人示范的情况下生成未来机器人视频并解码动作。"
map_role: "连接人类视频任务接口、世界动作模型和task-level zero-shot评测的入口，也暴露合成视频和输入不对称带来的证据边界。"
authors:
  - "[[Jiaming Zhou]]"
  - "[[Qihang Zhang]]"
  - "[[Gangwei Xu]]"
  - "[[Cunxin Fan]]"
  - "[[Yujie Zhao]]"
  - "[[Ruilin Wang]]"
  - "[[Yiming Luo]]"
  - "[[Shuai Yang]]"
  - "[[Xing Zhu]]"
  - "[[Yujun Shen]]"
  - "[[Junwei Liang]]"
  - "[[Yinghao Xu]]"
institutions:
  - "[[Robbyant]]"
  - "[[HKUST (GZ)]]"
  - "[[HKUST]]"
topics:
  - world-action model
  - human video
  - in-context learning
  - zero-shot cross-task generalization
  - causal video-action modeling
  - synthetic data
  - future chunk prediction
---

# Zero-WAM: In-Context World-Action Modeling from Human Videos for Open-Ended Task Generalization

- [x] PDF:: [[papers/pdfs/zhou2026zero-wam.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/zhou2026zero-wam_中英混读.md]]
- [x] 图片索引:: [[papers/images/zhou2026zero-wam/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[world-action model]], [[human video]], [[@feng2026wam-ttt]], [[@dyna2026dyna2]], [[@zhang2026lingbot-va2]], [[@generalist2026gen15]], [[@paliwal2026do-i-dexterous-manipulation]]
affiliation:: [[Robbyant]], [[HKUST (GZ)]], [[HKUST]]

## Abstract

Zero-WAM 把机器人 task-level zero-shot generalization 重写成 task specification 问题。人类视频不提供可执行机器人动作，却直接展示物体状态变化、空间关系和操作顺序，因而被用作部署时的 in-context prompt。作者从多源机器人轨迹出发，用 VLM、图像编辑器和视频生成器自动构造语义匹配的人类视频，形成 74.2K 对人机 ICL pairs，覆盖 8.6K tasks。模型基于 Wan-2.2-TI2V-5B 改造成 causal video-action model，并用 in-context future chunk prediction（IFP）迫使主视频分支真正读取人类视频。RoboTwin 2.0 的 7 个未见任务平均成功率为 46.95%，比 LingBot-VA 高 29.50 个百分点。真机实验也显示对未见配置、长时序和精细插入有迁移能力，但人类视频主要是生成数据，且真机基线使用的输入模态不同。

## 一句话定位

Zero-WAM 用生成式人类视频提供任务规范，用一个能预测未来机器人视频再解码动作的 WAM 把视觉意图转成控制，在没有目标任务机器人示范和部署时参数更新的条件下完成 task-level zero-shot 泛化。

## 方法 / 对象

- Task-diverse VA 从 AgiBot、InternData-A1、Open-X-Embodiment、RoboCOIN 和 RoboMIND 重新按 manipulation action 与 object 划分任务，每个 epoch 采样超过 6000 tasks 和约 400K robot trajectories。
- HumanGen pipeline 先让 VLM 提取任务名、初始状态、状态变化和终态，再编辑机器人首帧，生成 human video prompt，调用 Wan 2.7 或 Kling AI 3.0 合成视频，最后用 VLM 按 semantic preservation 与 physical plausibility 筛选。
- HumanGen 总计约 74.2K human-robot ICL pairs，包含 External 41,188 对、In-house 30,247 对、Simulation ICL 2,500 对和 Real-world ICL 252 对，覆盖约 8.6K tasks 与超过 45 种 robot embodiments。
- 模型把 Wan-2.2-TI2V-5B 改成 MoT causal video-action model。video Transformer 先预测下一段机器人视频，action Transformer 再从预测视频做 inverse dynamics 解码动作。
- 人类视频被放在序列前端作为 prefix memory。height-axis RoPE 偏移 $Δ_H=32$ 将人类 latent 与机器人多视角 latent 的坐标区间分开。
- IFP 训练时从当前机器人视频表示预测多个有 stride 的更远 future chunks。默认 $K=4$、stride $s=2$、权重为 $(0.5,0.25,0.15,0.15)$，推理时删除 IFP 分支。

## 证据

- RoboTwin 2.0 的 7 个 unseen tasks 上，Zero-WAM 平均成功率 46.95%（标准差 0.72），LingBot-VA 为 17.45%（1.40），WAN-Action 为 10.98%（1.07）。Zero-WAM 在 7 个任务逐项胜出。
- Zero-WAM 在 Place empty cup 达到 84.87%，Open microwave 达到 59.00%，Move stapler to pad 达到 69.14%。最难的 Stack blocks three 只有 9.00%，但两个基线均为 0。
- 只用 43 个 seen RoboTwin tasks 做 ICL 对照时，Zero-WAM w/o pretrain 平均为 36.36%，高于 WAN-Action 的 10.98% 和 LingBot-VA 的 17.45%，说明 human video prompt 提供了 text-only 条件之外的任务信息。
- IFP 消融把 7-task 平均从 28.55% 提升到 46.95%。在 Stack blocks three 上从 0 提升到 9%，说明它确实缓解了只靠局部机器人历史的 shortcut。
- 把人类视频遮掉、保留 task-balanced robotic pretraining 的 text-only 变体为 39.44%，比 LingBot-VA 高 21.99 个百分点，说明数据重采样本身也贡献了跨任务迁移。
- 真机 Franka 三类任务中，Object-to-container placement 为 53.3% 对 LingBot-VA 的 43.3%，Three-object sequential manipulation 为 33.3% 对 10.0%，Two-table-leg insertion 为 16.7% 对 0%。每类 30 次试验。

## 局限

- HumanGen 视频由 Gemini、Qwen、Nano Banana、Wan 或 Kling 等生成模型串联得到，不是自然采集的人类示范。论文没有报告生成通过率、人工审计、伪影统计或真实人类视频对照。
- RoboTwin 的 unseen task 没有对应的机器人训练轨迹，但 human prompt 是从该任务的机器人轨迹生成的。准确表述应是没有目标任务机器人示范，而不是完全没有任务信息。
- 真机比较输入不对称。Zero-WAM 看 human video，LingBot-VA 看 detailed text，因此提升不能只归因于架构。
- 真机仍用 252 对 Real-world ICL data 做本体适配，系统部署时不更新参数，却不是完全没有任务或 embodiment adaptation。
- 评测集中在 stationary tabletop manipulation，真实试验每类只有 30 次，论文没有给出置信区间，长时程误差累积仍明显。
- action branch 依赖预测机器人视频。视频生成错误会传给动作解码，并带来 autoregressive error accumulation。IFP 的 $K$、stride 和 loss weights 也没有系统扫描。
- 训练约 15,360 GPU hours，5B backbone 和外部生成模型依赖让复现门槛很高。截至 2026-09-01，代码、模型和数据尚未公开，GitHub README 预计在 2026-09-15 前发布。

## 我的阅读笔记

可以确定的是，Zero-WAM 把「任务是什么」和「机器人怎么动」拆成两种监督。人类视频负责前者，机器人轨迹负责后者，WAM 中间的未来视频是桥。这个接口比把人类手部运动硬重定向到机器人关节更宽松，也更容易跨本体。

值得画出来的是三层增益并没有混在一起。human video ICL、task-balanced robot data 和 IFP 各有独立消融，46.95% 并非单个技巧的结果。文本变体的 39.44% 提醒我们，数据分布整理本身就可能带来大幅收益。

说实话也不确定的是生成视频的真实贡献。HumanGen 从对应机器人轨迹出发，又由 VLM 写 prompt、编辑首帧和筛视频，链条里存在强大的任务先验。论文证明了这套合成管线有效，还没有证明自然人类视频会得到同样幅度的收益。

回到跨论文比较，Zero-WAM 的泛化轴是 task-level unseen，而 RL$^2$-VLA 主要测已知任务上的 prompt、物体和环境 shift。两篇论文的数字不应放在同一张 leaderboard 里直接排序，它们解决的是不同层面的不确定性。

## 摘录

> the natural task specification for manipulation is a human video

> Human videos enable Zero-WAM to condition these predictions on demonstrated visual state changes

> IFP modules are not directly conditioned on the human video prompt

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
