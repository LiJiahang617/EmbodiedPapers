---
tags:
  - paper
status: unread
aliases:
  - "X-Tokenizer: A Multimodal Action Tokenizer for Vision-Language-Action Pretraining"
year: 2026
title: "X-Tokenizer: A Multimodal Action Tokenizer for Vision-Language-Action Pretraining"
doi: 
arxiv: "2606.14752"
url: "https://arxiv.org/abs/2606.14752"
venue: "arXiv"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/kang2026x-tokenizer.pdf]]"
reading: "[[papers/bilingual/kang2026x-tokenizer_中英混读.md]]"
images: "papers/images/kang2026x-tokenizer/"
image_index: "[[papers/images/kang2026x-tokenizer/index.md]]"
authors:
  - "[[Miracle Kang]]"
  - "[[Lights Shi]]"
  - "[[Lucy Liang]]"
  - "[[Roy Gan]]"
  - "[[Dongxiu Liu]]"
  - "[[Pushi Zhang]]"
  - "[[Sylas Chen]]"
  - "[[Shawn Qin]]"
  - "[[Yinan Zheng]]"
  - "[[Jinliang Zheng]]"
  - "[[Hao Wang]]"
  - "[[Xianyuan Zhan]]"
  - "[[Hang Su]]"
institutions:
topics:
---

# X-Tokenizer: A Multimodal Action Tokenizer for Vision-Language-Action Pretraining

- [ ] PDF:: [[papers/pdfs/kang2026x-tokenizer.pdf]]
- [ ] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/kang2026x-tokenizer_中英混读.md]]
- [ ] 地图维护:: 已加入 [[论文地图]] 快速索引后，运行 `python setting/scripts/check_paper_map.py --sync-reading-markers`
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

Modern Vision-Language-Action (VLA) models must bridge pretrained vision-language reasoning and precise continuous robot control. Existing action tokenizers discretize actions primarily for reconstruction, producing codes that preserve motion geometry but provide only weak semantic supervision to the backbone. We therefore formulate action tokenization not as mere compression, but as semantic interface learning between multimodal reasoning and executable control. To this end, we introduce X-Tokenizer, a lightweight encoder-Semantic Residual Quantization (SRQ)-decoder architecture that provides a shared action interface across diverse robotic arm embodiments. Its key component, SRQ, imposes an asymmetric structure on residual vector quantization: the first level is trained with Masked Action Modeling (MAM) to form a discrete action language that captures coarse motion intent, while deeper levels remain reconstruction-oriented residuals that preserve fine-grained details. To further align action tokens with multimodal semantics, X-Tokenizer is pretrained with contrastive alignment to the representation space of a pretrained foundation model and with next-frame vision-language feature prediction. Pretrained on 2.4M trajectories (2.0B action frames), a single frozen X-Tokenizer plugs into a mixed discrete-continuous VLA as a representation-shaping supervision signal. X-Tokenizer achieves top real-world aggregate and strong RoboTwin 2.0 simulation results. Outperforming FAST in multimodal grounding (+13.5%) and long-horizon tasks (+8.25), it shows that action tokenizers serve as semantic interfaces for VLA pretraining beyond mere action compression.

## 一句话定位

X-Tokenizer 把 robot action tokenization 从“压缩连续动作”重新定义为 VLA 预训练中的语义接口学习。

## 方法 / 对象

- 对象：跨 robotic arm embodiments 的连续控制动作，以及 VLA backbone 能理解的离散 action language。
- 架构：lightweight encoder-Semantic Residual Quantization (SRQ)-decoder。
- 关键机制：第一级 residual quantization 用 Masked Action Modeling 形成 coarse motion intent 的离散动作语言；更深层 residuals 保持 reconstruction-oriented 以保留细粒度控制。
- 对齐：用 contrastive alignment 对齐 pretrained foundation model representation，并结合 next-frame vision-language feature 进行语义约束。

## 证据

- 摘要主张它能同时服务 multimodal reasoning 和 executable control，并提供 shared action interface。
- 需要在精读中重点检查 reconstruction quality、semantic alignment 指标、VLA 下游任务成功率，以及跨 embodiment 泛化。

## 局限

- 离散动作语言可能牺牲精确控制；多级 residual 是否能稳定补回精度需要看实验。
- “semantic token” 是否真正可解释，还是只在 representation space 中对齐，需要看可视化和 ablation。

## 我的阅读笔记

- 和 ZR-0 的互补性强：一个解决 action token 表示，一个解决 reasoning supervision；可作为 VLA training stack 的两类模块。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
