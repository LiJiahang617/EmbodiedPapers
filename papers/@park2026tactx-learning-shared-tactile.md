---
tags:
  - paper
status: read
aliases:
  - "TactX: Learning Shared Tactile Representations Across Diverse Sensors"
year: 2026
title: "TactX: Learning Shared Tactile Representations Across Diverse Sensors"
doi: 
arxiv: "2606.31236v1"
url: "https://arxiv.org/abs/2606.31236"
venue: 
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/park2026tactx-learning-shared-tactile.pdf]]"
reading: "[[papers/bilingual/park2026tactx-learning-shared-tactile_中英混读.md]]"
images: "papers/images/park2026tactx-learning-shared-tactile/"
image_index: "[[papers/images/park2026tactx-learning-shared-tactile/index.md]]"
authors:
  - "[[Junsung Park]]"
  - "[[Sachin Bhadang]]"
  - "[[Carmelo Sferrazza]]"
  - "[[Sha Yi]]"
  - "[[Xiaolong Wang]]"
institutions:
topics:
---

# TactX: Learning Shared Tactile Representations Across Diverse Sensors

- [x] PDF:: [[papers/pdfs/park2026tactx-learning-shared-tactile.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/park2026tactx-learning-shared-tactile_中英混读.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，`#map/触觉/跨传感器触觉表示`
- [x] 阅读状态:: read

related::
affiliation::

## Abstract

Tactile sensors provide critical information for contact-rich manipulation, yet tactile representations and policies remain tightly coupled to each specific sensor, limiting transferability across robots and hardware platforms. We propose TactX, a framework for learning a transferable tactile representation across sensors spanning three fundamentally different transduction modalities: resistive, magnetic, and vision-based. TactX maps heterogeneous tactile observations into a shared latent space through modality-specific encoders trained on paired contact data. Such paired interactions provide a natural alignment signal across modalities, and the encoders are jointly trained across all sensor pairs, inducing a consistent latent space for all sensor types. Our experiments show that TactX aligns tactile representations across sensors while preserving object-level contact information, as evidenced by sensor-identity prediction and object classification in the learned latent space. We evaluate TactX on four contact-rich manipulation tasks: pick-and-place, plug insertion, board wiping, and object reorientation, and show that policies trained with one sensor transfer zero-shot to physically distinct sensors through the shared latent. This improves the average success rate from 27.5% for vision-only policy to 45.9%, providing a step toward sensor-agnostic tactile manipulation.

## 一句话定位

TactX：用"夹爪两指各装一种传感器、同一次抓握产生配对观测"的天然对齐信号，把 resistive/magnetic/vision-based 三种异构触觉传感器对齐进同一 16 维潜空间，让一种传感器训的策略零样本迁到另一种。

## 方法 / 对象

模态专属编码器→16 维变分潜；对比对齐(NT-Xent τ=0.01) + 自/交叉重建(L1) + KL 向 N(0,I)；成对联合训练→全局一致潜空间（Eq 1-3）。下游 ACT 策略用 posterior 均值作确定性输入，跨传感器零样本部署。

## 证据

sensor-prediction 67.5%→47.5%（近 33.3% 随机）；传递对齐 D–F 余弦 0.626→0.928；物体分类 self 60.8%；四任务(P&P/插拔/擦板/重定向)零样本策略迁移平均成功率 27.5%(纯视觉)→45.9%。

## 局限

准静态抓握、刚性对称物体、10 indentors，分布覆盖有限；绝对成功率仍偏低(45.9%)；传递对齐依赖桥接传感器；只对齐表示未联合优化策略。详见精读稿矩阵。

## 我的阅读笔记


```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
