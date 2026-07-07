---
tags:
  - paper
status: read
aliases:
  - "LaST_0: Latent Spatio-Temporal Chain-of-Thought for Robotic Vision-Language-Action Model"
year: 2026
title: "LaST_0: Latent Spatio-Temporal Chain-of-Thought for Robotic Vision-Language-Action Model"
doi: 
arxiv: "2601.05248v1"
url: "https://arxiv.org/abs/2601.05248"
venue: 
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/liu2026last0-latent-spatio-temporal.pdf]]"
reading: "[[papers/bilingual/liu2026last0-latent-spatio-temporal_中英混读.md]]"
images: "papers/images/liu2026last0-latent-spatio-temporal/"
image_index: "[[papers/images/liu2026last0-latent-spatio-temporal/index.md]]"
authors:
  - "[[Zhuoyang Liu]]"
  - "[[Jiaming Liu]]"
  - "[[Hao Chen]]"
  - "[[Jiale Yu]]"
  - "[[Ziyu Guo]]"
  - "[[Chengkai Hou]]"
  - "[[Chenyang Gu]]"
  - "[[Xiangju Mi]]"
  - "[[Renrui Zhang]]"
  - "[[Kun Wu]]"
  - "[[Zhengping Che]]"
  - "[[Jian Tang]]"
  - "[[Pheng-Ann Heng]]"
  - "[[Shanghang Zhang]]"
institutions:
topics:
---

# LaST_0: Latent Spatio-Temporal Chain-of-Thought for Robotic Vision-Language-Action Model

- [x] PDF:: [[papers/pdfs/liu2026last0-latent-spatio-temporal.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/liu2026last0-latent-spatio-temporal_中英混读.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，`#map/具身智能/VLA/潜空间时空思维链CoT`
- [x] 阅读状态:: read

related::
affiliation::

## Abstract

Vision-Language-Action (VLA) models have recently shown strong generalization, with some approaches seeking to explicitly generate linguistic reasoning traces or predict future observations prior to execution. However, explicit reasoning typically incurs non-negligible inference latency, which constrains the temporal resolution required for robotic manipulation. Moreover, such reasoning is confined to the linguistic space, imposing a representational bottleneck that struggles to faithfully capture ineffable physical attributes. To mitigate these limitations, we propose LaST$_0$, a framework that enables efficient reasoning before acting through a Latent Spatio-Temporal Chain-of-Thought (CoT), capturing fine-grained physical and robotic dynamics that are often difficult to verbalize. Specifically, we introduce a token-efficient latent CoT space that models future visual dynamics, 3D structural information, and robot proprioceptive states, and further extends these representations across time to enable temporally consistent implicit reasoning trajectories. Furthermore, LaST$_0$ adopts a dual-system architecture implemented via a Mixture-of-Transformers design, where a reasoning expert conducts low-frequency latent inference and an acting expert generates high-frequency actions conditioned on robotics-oriented latent representations. To facilitate coordination, LaST$_0$ is trained with heterogeneous operation frequencies, enabling adaptive switching during deployment. Across 10 real-world tasks spanning tabletop, mobile, and dexterous hand manipulation, LaST$_0$ improves mean success rates by 13%, 14% and 14% over prior SOTA VLA methods, respectively.

## 一句话定位

把 VLA 的"先思后行"从缓慢、困在语言的显式 CoT，换成紧凑潜空间自回归预测未来 2D 视觉/3D 几何/本体状态、跨时间一致的 Latent Spatio-Temporal CoT，再用 MoT 双系统让慢推理与快动作异步协作。（用户所说 LAST-HD 即本篇 LaST₀）

## 方法 / 对象

从 Janus-Pro/DeepSeek-1.5B 初始化的 MoT 双系统：慢推理专家低频自回归合成潜 CoT（SigLIP 视觉 + Uni3D 点云[仅训练] + action tokenizer 本体，交错成 3×H 序列，余弦相似度监督），快动作专家高频 flow matching 生成动作，共享自注意力；异步频率 κ∈{2,4,8} 混合训练。400K 轨迹预训练 + 联合 SFT。约 3.3B。

## 证据

LIBERO 98.1%、RLBench 82%（+8% over HybridVLA-7B，7/10 最佳）、真机 Franka/移动/灵巧手 +13/14/14%；比显式 CoT VLA 快 14×（15.4 vs 1.1Hz）；MoT vs 单骨干 82% vs 74%；叠蛋 3 连 0.66→0.47→0.33 vs π0.5 0.47→0.20→0.07。

## 局限

移动/灵巧操作预训练覆盖有限；复杂物体交互仍难（计划加物理约束/3D 关系图）；每任务单独 SFT 需 200 示范、未测零样本泛化；潜推理正确性缺显式可解释验证；待加 RL 后训练。详见精读稿矩阵。

## 我的阅读笔记


```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
