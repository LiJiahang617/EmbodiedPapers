---
tags:
  - paper
status: read
aliases:
  - "$\\pi^{*}_{0.6}$: a VLA That Learns From Experience"
year: 2025
title: "$\\pi^{*}_{0.6}$: a VLA That Learns From Experience"
doi: 
arxiv: "2511.14759v1"
url: "https://arxiv.org/abs/2511.14759"
venue: 
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/intelligence2025pi06-vla-that-learns.pdf]]"
reading: "[[papers/bilingual/intelligence2025pi06-vla-that-learns_中英混读.md]]"
images: "papers/images/intelligence2025pi06-vla-that-learns/"
image_index: "[[papers/images/intelligence2025pi06-vla-that-learns/index.md]]"
authors:
  - "[[Physical Intelligence]]"
  - "[[Ali Amin]]"
  - "[[Raichelle Aniceto]]"
  - "[[Ashwin Balakrishna]]"
  - "[[Kevin Black]]"
  - "[[Ken Conley]]"
  - "[[Grace Connors]]"
  - "[[James Darpinian]]"
  - "[[Karan Dhabalia]]"
  - "[[Jared DiCarlo]]"
  - "[[Danny Driess]]"
  - "[[Michael Equi]]"
  - "[[Adnan Esmail]]"
  - "[[Yunhao Fang]]"
  - "[[Chelsea Finn]]"
  - "[[Catherine Glossop]]"
  - "[[Thomas Godden]]"
  - "[[Ivan Goryachev]]"
  - "[[Lachy Groom]]"
  - "[[Hunter Hancock]]"
  - "[[Karol Hausman]]"
  - "[[Gashon Hussein]]"
  - "[[Brian Ichter]]"
  - "[[Szymon Jakubczak]]"
  - "[[Rowan Jen]]"
  - "[[Tim Jones]]"
  - "[[Ben Katz]]"
  - "[[Liyiming Ke]]"
  - "[[Chandra Kuchi]]"
  - "[[Marinda Lamb]]"
  - "[[Devin LeBlanc]]"
  - "[[Sergey Levine]]"
  - "[[Adrian Li-Bell]]"
  - "[[Yao Lu]]"
  - "[[Vishnu Mano]]"
  - "[[Mohith Mothukuri]]"
  - "[[Suraj Nair]]"
  - "[[Karl Pertsch]]"
  - "[[Allen Z. Ren]]"
  - "[[Charvi Sharma]]"
  - "[[Lucy Xiaoyang Shi]]"
  - "[[Laura Smith]]"
  - "[[Jost Tobias Springenberg]]"
  - "[[Kyle Stachowicz]]"
  - "[[Will Stoeckle]]"
  - "[[Alex Swerdlow]]"
  - "[[James Tanner]]"
  - "[[Marcel Torne]]"
  - "[[Quan Vuong]]"
  - "[[Anna Walling]]"
  - "[[Haohuan Wang]]"
  - "[[Blake Williams]]"
  - "[[Sukwon Yoo]]"
  - "[[Lili Yu]]"
  - "[[Ury Zhilinsky]]"
  - "[[Zhiyuan Zhou]]"
institutions:
topics:
---

# $\pi^{*}_{0.6}$: a VLA That Learns From Experience

- [x] PDF:: [[papers/pdfs/intelligence2025pi06-vla-that-learns.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/intelligence2025pi06-vla-that-learns_中英混读.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，`#map/具身智能/VLA/经验强化学习自改进`
- [x] 阅读状态:: read

related::
affiliation::

## Abstract

We study how vision-language-action (VLA) models can improve through real-world deployments via reinforcement learning (RL). We present a general-purpose method, RL with Experience and Corrections via Advantage-conditioned Policies (RECAP), that provides for RL training of VLAs via advantage conditioning. Our method incorporates heterogeneous data into the self-improvement process, including demonstrations, data from on-policy collection, and expert teleoperated interventions provided during autonomous execution. RECAP starts by pre-training a generalist VLA with offline RL, which we call $π^{*}_{0.6}$, that can then be specialized to attain high performance on downstream tasks through on-robot data collection. We show that the $π^{*}_{0.6}$ model trained with the full RECAP method can fold laundry in real homes, reliably assemble boxes, and make espresso drinks using a professional espresso machine. On some of the hardest tasks, RECAP more than doubles task throughput and roughly halves the task failure rate.

## 一句话定位

RECAP：用“优势条件化”把示范+自主经验+人类纠偏统一进 flow-matching VLA 的迭代离线 RL，让 π0.6 训成能从部署经验自我改进的 π*0.6（用户所说 pi0.7 实为此篇）。

## 方法 / 对象

分布式价值函数（201 bins，预测 steps-to-success）给 advantage；策略抽取用优势条件化——把 I=1[A>ε_ℓ] 作“Advantage: positive/negative”文本输入，同时建模 π(a|o) 与 π(a|I,o)，从全部 off-policy 数据做监督（避开对 flow matching 不友好的策略梯度）。三阶段：离线 RL 预训练→下游 SFT(I=True)→在机采数据（自主+专家干预，强制 I=True）迭代。π0.6=Gemma3-4B+860M 动作专家+FAST+KI。

## 证据

难任务（diverse laundry/espresso）吞吐 >2×、失败率约减半（Fig 7/8）；多数任务 90%+ 成功；严格叠衣纯 RL 无干预达 97%（Fig 12）；显著优于 AWR/PPO（Fig 11）；咖啡连续 13h、新家叠衣 2h。

## 局限

非全自主（人工标注/干预/复位）；探索朴素贪心；迭代离线非全在线；奖励=稀疏成功标签需人工判定；仅三任务单一双臂平台。详见精读稿矩阵。

## 我的阅读笔记


```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
