---
tags:
  - paper
status: unread
aliases:
  - "Fast LeWorldModel"
year: 2026
title: "Fast LeWorldModel"
doi: 
arxiv: "2606.26217"
url: "https://arxiv.org/abs/2606.26217"
venue: "arXiv"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/gao2026fast-leworldmodel.pdf]]"
reading: "[[papers/bilingual/gao2026fast-leworldmodel_中英混读.md]]"
images: "papers/images/gao2026fast-leworldmodel/"
image_index: "[[papers/images/gao2026fast-leworldmodel/index.md]]"
authors:
  - "[[Yuntian Gao]]"
  - "[[Xiangyu Xu]]"
institutions:
topics:
---

# Fast LeWorldModel

- [ ] PDF:: [[papers/pdfs/gao2026fast-leworldmodel.pdf]]
- [ ] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/gao2026fast-leworldmodel_中英混读.md]]
- [ ] 地图维护:: 已加入 [[论文地图]] 快速索引后，运行 `python setting/scripts/check_paper_map.py --sync-reading-markers`
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

Joint-Embedding Predictive Architectures (JEPAs), including recent LeWorldModel (LeWM), have become a promising foundation for reconstruction-free visual world models. For visual planning, however, LeWM evaluates candidate action sequences by repeatedly applying a local one-step latent transition model. This autoregressive rollout makes planning computationally expensive and exposes the predicted trajectory to accumulated latent errors as the horizon grows. We propose Fast LeWorldModel (Fast-LeWM), a fast latent world model that replaces repeated local rollout with action-prefix prediction. Given the current latent and a candidate action sequence, Fast-LeWM encodes its prefixes and predicts the future latents reached after executing those prefixes in parallel. By making action prefixes the basic prediction unit, Fast-LeWM directly models action effects accumulated to different extents over multiple horizons. This prefix-level supervision forces the model to learn how states continuously evolve under different action prefixes, rather than only fitting one-step state transitions. During planning, the predictor can use the last prefix token from the encoded action sequence to evaluate the corresponding future latent without explicitly rolling through each intermediate imagined state. Across multiple tasks, Fast-LeWM improves average success over LeWM while substantially reducing planning time, achieving lower open-loop latent loss whose growth becomes significantly slower as the rollout horizon increases.

## 一句话定位

Fast LeWorldModel 将 LeWorldModel 的 autoregressive latent rollout 改成 action-prefix prediction，从而加速 visual planning 并减少长 horizon 误差累积。

## 方法 / 对象

- 对象：JEPA/LeWorldModel 类型 reconstruction-free visual world model 的 planning 阶段。
- 问题：原 LeWM 需要反复调用 one-step latent transition model 来评估 candidate action sequences，计算贵且会积累 latent errors。
- 方法：给定 current latent 和 candidate action sequence，编码 action prefixes，并行预测不同 prefix 执行后的 future latents。

## 证据

- 摘要说明 Fast-LeWM 以 action prefixes 为基本预测单元，直接建模多 horizon 下动作效果的累积。
- 需要在正文中检查 planning speedup、prediction error、下游控制性能，以及相对原 LeWM 的公平计算预算。

## 局限

- Prefix-level supervision 是否泛化到更长/更复杂 action sequence 需要实验支持。
- 如果 latent 表示本身不足，parallel prefix prediction 只能减少 rollout 成本，不能解决 world model 表征瓶颈。

## 我的阅读笔记

- 适合作为“world model 如何服务 planning”的代表，与 Orca/Qwen-RobotWorld 的通用 world model claim 分开讨论。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
