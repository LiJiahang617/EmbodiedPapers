---
tags:
  - paper
status: read
aliases:
  - "Heterogeneous Tactile Transformer"
year: 2026
title: "Heterogeneous Tactile Transformer"
doi: 
arxiv: "2606.29948v1"
url: "https://arxiv.org/abs/2606.29948"
venue: 
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/bi2026heterogeneous-tactile-transformer.pdf]]"
reading: "[[papers/bilingual/bi2026heterogeneous-tactile-transformer_中英混读.md]]"
images: "papers/images/bi2026heterogeneous-tactile-transformer/"
image_index: "[[papers/images/bi2026heterogeneous-tactile-transformer/index.md]]"
authors:
  - "[[Jianxin Bi]]"
  - "[[Qiang Wang]]"
  - "[[Jayaram Reddy]]"
  - "[[Kelvin Lin Soibkhon Khajikhanov]]"
  - "[[Ruihan Gao]]"
  - "[[Harold Soh]]"
  - "[[Corresponding authors]]"
institutions:
topics:
---

# Heterogeneous Tactile Transformer

- [x] PDF:: [[papers/pdfs/bi2026heterogeneous-tactile-transformer.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/bi2026heterogeneous-tactile-transformer_中英混读.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，`#map/触觉/跨传感器触觉表示`
- [x] 阅读状态:: read

related::
affiliation::

## Abstract

Tactile sensors are inherently heterogeneous: a model trained on one sensor cannot be directly used on another, which limits learning contact-rich manipulation policies from diverse tactile data at scale. To bridge this gap, we propose the Heterogeneous Tactile Transformer (HTT), a framework that learns shared tactile representations across heterogeneous sensors. HTT consists of sensor-specific encoders and a shared transformer trunk, and is pretrained with per-modality masked reconstruction together with cross-modal alignment between paired sensors. Pretraining uses our novel Heterogeneous Paired Tactile (HPT) dataset, containing 1.6M synchronized paired frames across four vision- and array-based tactile sensors. Across distinct tactile perception and real-world manipulation tasks, HTT is shown to learn transferable representations that adapt to new tasks and previously unseen sensors. Dataset, code, and model checkpoints will be released upon publication at https://jxbi1010.github.io/htt-gh-page/.

## 一句话定位

HTT：先用 UMI 采 1.6M 帧、四传感器同步配对的 HPT 数据集，再用"逐模态 MAE 掩码重建 + 双向跨传感器掩码预测对齐"训"传感器专属编码器 + 共享 Transformer trunk"的异构触觉骨干，跨光学/阵列传感器迁移并泛化到未见新传感器。

## 方法 / 对象

传感器专属编码器(光学 ViT / 阵列 self-attn) + 共享 trunk + 跨模态预测器；预训练 = MAE(Eq 1，减非接触参考帧、per-patch 归一) + 跨模态对齐(Eq 2，stop-gradient) + 联合(Eq 3，α warmup 0→0.1、编码器梯度隔离只由 MAE 更新)。HPT：UMI 两指对置采配对，Pair A Xela↔9DTact / Pair B TAC-02↔GSMini。

## 证据

物体分类每传感器超 Scratch；光学传感器超最强基线 SITR +13.5%(9DTact)/+17%(GSMini)；HTT vs MAE(ours) 隔离出跨传感器对齐增益；提升接触密集操作(拧螺丝/抓豆腐)并适配预训练未见新传感器。

## 局限

仅两配对配置、四传感器；滑动检测类别极不均衡(incipient 1.2%)；训练技巧(梯度隔离/α warmup)超参敏感；操作评测偏定性。详见精读稿矩阵。

## 我的阅读笔记


```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
