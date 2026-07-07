---
tags:
  - paper
status: read
aliases:
  - "Do as I Do: Dexterous Manipulation Data from Everyday Human Videos"
year: 2026
title: "Do as I Do: Dexterous Manipulation Data from Everyday Human Videos"
doi: 
arxiv: "2606.19333v1"
url: "https://arxiv.org/abs/2606.19333"
venue: 
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/paliwal2026do-i-dexterous-manipulation.pdf]]"
reading: "[[papers/bilingual/paliwal2026do-i-dexterous-manipulation_中英混读.md]]"
images: "papers/images/paliwal2026do-i-dexterous-manipulation/"
image_index: "[[papers/images/paliwal2026do-i-dexterous-manipulation/index.md]]"
authors:
  - "[[Bhawna Paliwal]]"
  - "[[Haritheja Etukuru]]"
  - "[[William Liang]]"
  - "[[Pieter Abbeel]]"
  - "[[Nur Muhammad Mahi Shafiullah]]"
  - "[[Jitendra Malik]]"
institutions:
topics:
---

# Do as I Do: Dexterous Manipulation Data from Everyday Human Videos

- [x] PDF:: [[papers/pdfs/paliwal2026do-i-dexterous-manipulation.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/paliwal2026do-i-dexterous-manipulation_中英混读.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，`#map/具身智能/数据/人类视频到灵巧操作`
- [x] 阅读状态:: read

related::
affiliation::

## Abstract

How can we scalably generate data for robotic manipulation, especially on human-like platforms such as dexterous multi-fingered hands? Learning from human videos has recently emerged as a likely answer to this question. However, difficulties in estimating hand-object interaction and crossing the human-to-robot embodiment gap have hindered the adoption of abundant monocular RGB-only human videos as the primary source of robot manipulation data. In this work, we present DO AS I DO, an algorithm to reconstruct and retarget monocular RGB human videos to multi-fingered dexterous robotic hands. DO AS I DO reconstructs hand-object interactions from various egocentric and exocentric in-the-wild video sources. The algorithm then retargets these hand-object interaction estimates into a sequence of actions executable in the real world, yielding robot-complete manipulation data from disparate human videos. Overall, DO AS I DO outperforms previous state of the art in estimating hand-object interactions and extracting dexterous manipulation trajectories from RGB videos, as we show in experiments on datasets with ground truths and on a dataset of video clips collected online. Our experiments enable us to propose an efficacy playbook for practitioners collecting human data for manipulation.

## 一句话定位

首个端到端把单目 RGB 人类视频转成真实多指灵巧手可执行操作数据的流水线：视觉基础模型重建 4D 手-物轨迹 + 动力学感知采样优化重定向到机器人手。

## 方法 / 对象

重建：HaWoR 追手 + 把 SAM3D 改造成引导扩散视频物体追踪器（固定形状 latent、姿态 block 向上一帧引导，Eq 1）+ 自适应 α_p（点轨迹）+ SE(3) 聚类选姿态（快 30×）+ MoGe/GeoCalib 对齐。重定向：基于 SPIDER 的退火采样优化 + Warmup/随机力扰动/转换奖励三组件应对噪声参考。22-DoF Sharpa Wave 手 + UR3e 双臂。

## 证据

重建：DexYCB/HOI4D 刷新 SOTA（Table 2），野外 150 视频 67% 人类偏好胜 FoundationPose（Fig 5）。重定向：重建参考成功率 0.25→0.71（Warmup 主导）、OakInk2 0.72→0.81（Table 3）。真机执行 10 任务、产出 500 条核验轨迹（Fig 6）。数据手册：100DOH 2000 clip 仅 4% 通过质检。

## 局限

仅刚体；依赖单目近似度量深度；手-物接触/遮挡歧义；只建手+物不建场景（无环境约束推理）；仿真近似真实动力学设上界；成功仅用几何误差阈值，未报下游策略闭环收益。详见精读稿矩阵。

## 我的阅读笔记


```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
