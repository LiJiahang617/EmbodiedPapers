---
tags:
  - paper
status: read
aliases:
  - "${\\pi}_{0.7}$: a Steerable Generalist Robotic Foundation Model with Emergent Capabilities"
year: 2026
title: "${\\pi}_{0.7}$: a Steerable Generalist Robotic Foundation Model with Emergent Capabilities"
doi: 
arxiv: "2604.15483v2"
url: "https://arxiv.org/abs/2604.15483"
venue: 
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/intelligence2026pi07-steerable-generalist-robotic.pdf]]"
reading: "[[papers/bilingual/intelligence2026pi07-steerable-generalist-robotic_中英混读.md]]"
images: "papers/images/intelligence2026pi07-steerable-generalist-robotic/"
image_index: "[[papers/images/intelligence2026pi07-steerable-generalist-robotic/index.md]]"
authors:
  - "[[Physical Intelligence]]"
  - "[[Bo Ai]]"
  - "[[Ali Amin]]"
  - "[[Raichelle Aniceto]]"
  - "[[Ashwin Balakrishna]]"
  - "[[Greg Balke]]"
  - "[[Kevin Black]]"
  - "[[George Bokinsky]]"
  - "[[Shihao Cao]]"
  - "[[Thomas Charbonnier]]"
  - "[[Vedant Choudhary]]"
  - "[[Foster Collins]]"
  - "[[Ken Conley]]"
  - "[[Grace Connors]]"
  - "[[James Darpinian]]"
  - "[[Karan Dhabalia]]"
  - "[[Maitrayee Dhaka]]"
  - "[[Jared DiCarlo]]"
  - "[[Danny Driess]]"
  - "[[Michael Equi]]"
  - "[[Adnan Esmail]]"
  - "[[Yunhao Fang]]"
  - "[[Chelsea Finn]]"
  - "[[Catherine Glossop]]"
  - "[[Thomas Godden]]"
  - "[[Ivan Goryachev]]"
  - "[[Lachlan Groom]]"
  - "[[Haroun Habeeb]]"
  - "[[Hunter Hancock]]"
  - "[[Karol Hausman]]"
  - "[[Gashon Hussein]]"
  - "[[Victor Hwang]]"
  - "[[Brian Ichter]]"
  - "[[Connor Jacobsen]]"
  - "[[Szymon Jakubczak]]"
  - "[[Rowan Jen]]"
  - "[[Tim Jones]]"
  - "[[Gregg Kammerer]]"
  - "[[Ben Katz]]"
  - "[[Liyiming Ke]]"
  - "[[Mairbek Khadikov]]"
  - "[[Chandra Kuchi]]"
  - "[[Marinda Lamb]]"
  - "[[Devin LeBlanc]]"
  - "[[Brendon LeCount]]"
  - "[[Sergey Levine]]"
  - "[[Xinyu Li]]"
  - "[[Adrian Li-Bell]]"
  - "[[Vladislav Lialin]]"
  - "[[Zhonglin Liang]]"
  - "[[Wallace Lim]]"
  - "[[Yao Lu]]"
  - "[[Enyu Luo]]"
  - "[[Vishnu Mano]]"
  - "[[Nandan Marwaha]]"
  - "[[Aikys Mongush]]"
  - "[[Liam Murphy]]"
  - "[[Suraj Nair]]"
  - "[[Tyler Patterson]]"
  - "[[Karl Pertsch]]"
  - "[[Allen Z. Ren]]"
  - "[[Gavin Schelske]]"
  - "[[Charvi Sharma]]"
  - "[[Baifeng Shi]]"
  - "[[Lucy Xiaoyang Shi]]"
  - "[[Laura Smith]]"
  - "[[Jost Tobias Springenberg]]"
  - "[[Kyle Stachowicz]]"
  - "[[Will Stoeckle]]"
  - "[[Jiaming Tang]]"
  - "[[Jimmy Tanner]]"
  - "[[Shalom Tekeste]]"
  - "[[Marcel Torne]]"
  - "[[Kyle Vedder]]"
  - "[[Quan Vuong]]"
  - "[[Anna Walling]]"
  - "[[Haohuan Wang]]"
  - "[[Jason Wang]]"
  - "[[XuDong Wang]]"
  - "[[Chris Whalen]]"
  - "[[Samuel Whitmore]]"
  - "[[Blake Williams]]"
  - "[[Charles Xu]]"
  - "[[Sukwon Yoo]]"
  - "[[Lili Yu]]"
  - "[[Wuming Zhang]]"
  - "[[Zhuoyang Zhang]]"
  - "[[Ury Zhilinsky]]"
institutions:
topics:
---

# ${\pi}_{0.7}$: a Steerable Generalist Robotic Foundation Model with Emergent Capabilities

- [x] PDF:: [[papers/pdfs/intelligence2026pi07-steerable-generalist-robotic.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/intelligence2026pi07-steerable-generalist-robotic_中英混读.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，`#map/具身智能/VLA/可操控通用机器人基础模型`
- [x] 阅读状态:: read

related::
affiliation::

## Abstract

We present a new robotic foundation model, called $π_{0.7}$, that can enable strong out-of-the-box performance in a wide range of scenarios. $π_{0.7}$ can follow diverse language instructions in unseen environments, including multi-stage tasks with various kitchen appliances, provide zero-shot cross-embodiment generalization, for example enabling a robot to fold laundry without seeing the task before, and perform challenging tasks such as operating an espresso machine out of the box at a level of performance that matches much more specialized RL-finetuned models. The main idea behind $π_{0.7}$ is to use diverse context conditioning during training. This conditioning information, contained in the prompt, makes it possible to steer the model precisely to perform many tasks with different strategies. It is conditioned not just on a language command that describes what it should do, but on additional multimodal information that also describes the manner or strategy in which it should do it, including metadata about task performance and subgoal images. This enables $π_{0.7}$ to use very diverse data, including demonstrations, potentially suboptimal (autonomous) data including failures, and data from non-robot sources. Our experiments evaluate $π_{0.7}$ across numerous tasks with multiple robot platforms, on tasks that require speed and dexterity, language following, and compositional task generalization.

## 一句话定位

pi0.7：不改架构，而是给每条训练样本配"子任务文本+生成式子目标图+回合元数据(速度/质量/犯错)+控制模式"的多模态上下文并随机 dropout，把示范/失败/自主/非机器人异构数据统一喂给 5B VLA，涌现出开箱即用、跨本体零样本、组合泛化等能力。（用户所说 pi0.7 即本篇，2026-04 发布）

## 方法 / 对象

多样上下文条件化：prompt = 语言 + 子任务 ℓ̂ + 多视角子目标图（BAGEL 世界模型生成）+ 回合元数据 + 控制模式(joint/ee)，训练时各成分随机 dropout。模型 5B（Gemma3-4B VLM + MEM 视频历史编码器 + 860M flow-matching 动作专家），建于 π0.6-MEM，KI recipe + FAST。

## 证据

开箱即用匹配/超 π*0.6 等 RL 微调专家（咖啡/叠衣/换垃圾袋/折箱/削菜）；消融去元数据/去自主评测数据都掉、吞吐差距最大（Fig 7）；未见厨房卧室指令泛化 > π0.5/π0.6；零样本跨本体叠衣匹配专家遥操首试；组合泛化到空气炸锅等新家电。

## 局限

依赖大量人工标注（语言/质量/犯错/子任务）；子目标图依赖 BAGEL 世界模型质量；"涌现/组合泛化"多为选例、缺系统覆盖率；跨本体基准较弱。详见精读稿矩阵。

## 我的阅读笔记


```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
