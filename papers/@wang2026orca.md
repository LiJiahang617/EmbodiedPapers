---
tags:
  - paper
status: unread
aliases:
  - "Orca: The World is in Your Mind"
year: 2026
title: "Orca: The World is in Your Mind"
doi: 
arxiv: "2606.30534"
url: "https://arxiv.org/abs/2606.30534"
venue: "arXiv"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/wang2026orca.pdf]]"
reading: "[[papers/bilingual/wang2026orca_中英混读.md]]"
images: "papers/images/wang2026orca/"
image_index: "[[papers/images/wang2026orca/index.md]]"
authors:
  - "[[Yihao Wang]]"
  - "[[Yuheng Ji]]"
  - "[[Mingyu Cao]]"
  - "[[Yanqing Shen]]"
  - "[[Runze Xiao]]"
  - "[[Huaihai Lyu]]"
  - "[[Senwei Xie]]"
  - "[[Euan Liu]]"
  - "[[Klara Tian]]"
  - "[[Tianfeng Long]]"
  - "[[Yichi Zhang]]"
  - "[[Zhengliang Cai]]"
  - "[[Ruike Chen]]"
  - "[[Jifan Zhao]]"
  - "[[Ruochuan Shi]]"
  - "[[Zihan Tang]]"
  - "[[Jing Lyu]]"
  - "[[Wenxing Tan]]"
  - "[[Ningbo Zhang]]"
  - "[[Yangtao Hu]]"
  - "[[Yuming Gao]]"
  - "[[Xiansheng Chen]]"
  - "[[Junkai Zhao]]"
  - "[[Congsheng Xu]]"
  - "[[Boan Zhu]]"
  - "[[Ziqi Wang]]"
  - "[[Yupu Feng]]"
  - "[[Qiongqiong Zhang]]"
  - "[[Yingli Zhao]]"
  - "[[Yulong Ao]]"
  - "[[Shaoxuan Xie]]"
  - "[[You Liu]]"
  - "[[Guocai Yao]]"
  - "[[Leiduo Zhang]]"
  - "[[Xiaodan Liu]]"
  - "[[Yunyan Zhang]]"
  - "[[Yance Jiao]]"
  - "[[Xinyan Yang]]"
  - "[[Jiaxing Wei]]"
  - "[[Xu Liu]]"
  - "[[Tengfei Pan]]"
  - "[[Shaokai Nie]]"
  - "[[Chunlei Men]]"
  - "[[Sen Cui]]"
  - "[[Xiaojie Jin]]"
  - "[[Hongyang Li]]"
  - "[[Jianlan Luo]]"
  - "[[Yao Mu]]"
  - "[[Yunchao Wei]]"
  - "[[Jun Yan]]"
  - "[[Hang Zhao]]"
  - "[[Xiaolong Zheng]]"
  - "[[Jiaming Li]]"
  - "[[Yonghua Lin]]"
  - "[[Tiejun Huang]]"
  - "[[Zhongyuan Wang]]"
  - "[[Pengwei Wang]]"
institutions:
topics:
---

# Orca: The World is in Your Mind

- [ ] PDF:: [[papers/pdfs/wang2026orca.pdf]]
- [ ] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/wang2026orca_中英混读.md]]
- [ ] 地图维护:: 已加入 [[论文地图]] 快速索引后，运行 `python setting/scripts/check_paper_map.py --sync-reading-markers`
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

We introduce Orca, an initial instantiation of a general world foundation model. Orca learns a unified world latent space from multimodal world signals and exposes it through multimodal readout interfaces. Rather than optimizing isolated next-token, next-frame, or next-action prediction, we are centered on Next-State-Prediction modeling, offering a unified state-transition modeling route toward understanding, predicting, and acting upon the world. Orca learns through two complementary paradigms: unconscious learning captures dense natural state transitions from continuous videos, and conscious learning models sparse meaningful state transitions by language-described events and VQA supervision. For pre-training, we construct a large-scale world-learning inventory data, including 125K hours of video data and 160M event annotations. After pre-training, Orca learns a unified world latent space. To examine whether the learned latent supports downstream, we evaluate it by three representative downstream readouts: text generation, image prediction, and embodied action generation. Orca's backbone is frozen, and only the lightweight modality-specific decoders are trainable. Experiments show the scalability of the proposed paradigm and verify that stronger world latent enables stronger downstream readouts. Orca outperforms similar-sized specialized baselines. These results show that Orca, as a general world foundation model, presents a promising approach to understanding, predicting, and acting upon the world. Finally, we discuss the current limitations, aiming to provide useful insights and inspiration for the community.

## 一句话定位

Orca 提出一个 general world foundation model 的初始实现，核心目标是学习统一 world latent space，并通过多模态 readout 支持理解、预测和行动。

## 方法 / 对象

- 对象：multimodal world signals，包括视频、事件描述、VQA 监督，以及 embodied action generation readout。
- 建模范式：不是孤立做 next-token、next-frame 或 next-action，而是以 Next-State-Prediction 为中心建模状态转移。
- 训练范式：unconscious learning 捕获连续视频中的密集自然状态转移；conscious learning 用语言描述事件和 VQA 监督建模稀疏有意义状态转移。

## 证据

- 摘要称预训练数据包含 125K hours video 和 160M event annotations。
- 下游验证包含 text generation、image prediction、embodied action generation，并且 backbone frozen、只训练 modality-specific decoders。

## 局限

- “general world foundation model” 是很强的 claim，需要检查任务覆盖是否足以支持“general”。
- Frozen backbone + lightweight decoder 的结果能说明 latent 可迁移，但也可能受 readout 设计影响；需要看 readout 容量、训练数据和指标。

## 我的阅读笔记

- Orca 可作为本批论文的总坐标系：与 Qwen-RobotWorld 的 video world model、Fast-LeWM 的 planning latent、Tactile-WAM 的 tactile future prediction 形成层级对照。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
