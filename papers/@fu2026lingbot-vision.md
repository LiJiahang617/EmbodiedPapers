---
tags:
  - paper
status: unread
aliases:
  - "Vision Pretraining for Dense Spatial Perception"
year: 2026
title: "Vision Pretraining for Dense Spatial Perception"
doi: 
arxiv: "2607.05247"
url: 
venue: 
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/fu2026lingbot-vision.pdf]]"
reading: "[[papers/bilingual/fu2026lingbot-vision_中英混读.md]]"
images: "papers/images/fu2026lingbot-vision/"
image_index: "[[papers/images/fu2026lingbot-vision/index.md]]"
authors:
  - "[[Zelin Fu]]"
  - "[[Bin Tan]]"
  - "[[Changjiang Sun]]"
  - "[[Shaohui Liu]]"
  - "[[Kecheng Zheng]]"
  - "[[Yinghao Xu]]"
  - "[[Xing Zhu]]"
  - "[[Yujun Shen]]"
  - "[[Nan Xue]]"
institutions:
topics:
---

# Vision Pretraining for Dense Spatial Perception

- [ ] PDF:: [[papers/pdfs/fu2026lingbot-vision.pdf]]
- [ ] 元数据:: source=arxiv, confidence=medium
- [x] 精读稿:: [[papers/bilingual/fu2026lingbot-vision_中英混读.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引；精读稿生成后已同步阅读状态。
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract



## 一句话定位

LingBot-Vision 把 image boundary（图像边界）作为自监督预训练的原生信号：用 teacher 自举的 categorical boundary field 找到 boundary tokens，并强制遮住它们，让 1B ViT 同时保留语义抽象与可用于深度、分割、跟踪的稠密几何表征。

## 方法 / 对象

- 方法：masked boundary modeling、a-contrario 无参数边界验证、按几何路由的 teacher–student self-distillation。
- 对象：稠密空间感知，包括 NYUv2 深度、语义/视频对象分割、边界跟踪及 LingBot-Depth 2.0 深度补全。

## 证据

- Table 2--5 对比 DINOv2/DINOv3 等视觉基础模型；作者报告 1B ViT-g 在稠密任务上可超过更大的模型。
- Table 6--8 与 Fig. 8--10 显示该编码器初始化和 150M 深度数据如何共同提升 LingBot-Depth 2.0。

## 局限

- 边界自举依赖 teacher 早期预测足以产生有用伪标签；复杂纹理、弱边界或非线性曲线的失败分析有限。
- 主张的“空间通用性”主要由视觉基准与深度补全支持，尚未直接以闭环机器人策略成功率验证。

## 我的阅读笔记


```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
