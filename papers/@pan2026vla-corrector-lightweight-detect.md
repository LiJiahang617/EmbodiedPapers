---
tags:
  - paper
status: read
aliases:
  - "VLA-Corrector: Lightweight Detect-and-Correct Inference for Adaptive Action Horizon"
year: 2026
title: "VLA-Corrector: Lightweight Detect-and-Correct Inference for Adaptive Action Horizon"
doi: 
arxiv: "2607.01804v1"
url: "https://arxiv.org/abs/2607.01804"
venue: 
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/pan2026vla-corrector-lightweight-detect.pdf]]"
reading: "[[papers/bilingual/pan2026vla-corrector-lightweight-detect_中英混读.md]]"
images: "papers/images/pan2026vla-corrector-lightweight-detect/"
image_index: "[[papers/images/pan2026vla-corrector-lightweight-detect/index.md]]"
authors:
  - "[[Yi Pan]]"
  - "[[Miao Pan]]"
  - "[[Qi Lu]]"
  - "[[Jiaming Huang]]"
  - "[[Man Zhang]]"
  - "[[Siteng Huang]]"
  - "[[Xin Li]]"
  - "[[Jie Zhang]]"
  - "[[Yongliang Shen]]"
  - "[[Xuhong Zhang]]"
  - "[[Wenqi Zhang]]"
institutions:
topics:
---

# VLA-Corrector: Lightweight Detect-and-Correct Inference for Adaptive Action Horizon

- [x] PDF:: [[papers/pdfs/pan2026vla-corrector-lightweight-detect.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/pan2026vla-corrector-lightweight-detect_中英混读.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，`#map/具身智能/VLA/推理期检测纠正与自适应动作时域`
- [x] 阅读状态:: read

related::
affiliation::

## Abstract

Vision-Language-Action (VLA) foundation models have recently achieved strong progress in embodied intelligence. To reduce policy-call frequency while preserving temporal coherence, most generative policies adopt an action chunk mechanism, executing multiple future actions in an open-loop manner under a fixed action horizon. However, this "predict-then-blindly-execute" paradigm sacrifices closed-loop reactivity: in contact-rich physical interactions, even small local perturbations can rapidly amplify within the open-loop blind spot, leading to compounding errors and ultimately task failure. To address this limitation, we propose VLA-Corrector, a lightweight corrective inference framework for action-chunked VLA policies. Without modifying the backbone policy weights, VLA-Corrector introduces a lightweight Latent-space Vision Monitor (LVM) that continuously compares predicted and actual visual feature evolution, enabling online detection of visual dynamics deviations. Once persistent deviation is detected, the system triggers a truncation event, discards the remaining stale actions, and invokes corrective replanning via Online Gradient Guidance (OGG). The detect-and-correct mechanism of VLA-Corrector naturally induces an event-triggered adaptive action horizon: it preserves long-horizon execution when the current chunk remains reliable, and invokes short-horizon corrective replanning when execution begins to drift. In doing so, VLA-Corrector mitigates the trade-off imposed by static horizons between execution robustness and policy-call frequency. It can be integrated into different VLA models without further retraining the VLA backbone, interrupting compounding errors while preserving much of the efficiency benefit of action chunking and substantially improving robustness in long-horizon, contact-rich robotic manipulation tasks.

## 一句话定位

不改 VLA 骨干权重、用一个约 40M 外置潜动态校正器，把 action chunking 的“固定盲执行时域”变成“检测到视觉漂移就自动截断并 OGG 引导纠正”的自适应时域，缓解鲁棒性与策略调用频率的静态权衡。

## 方法 / 对象

冻结 VLA，抽视觉编码器潜特征训练残差 MLP 校正器 `M_φ`（预测动作引起的短程潜残差 `ΔZ`）。在线用 LVM 比对期望 vs 实际潜演化得不一致分数 `E_t`（Eq 5），经 MAD 鲁棒双阈值 + 持续计数（Eq 6-7,12-13）做事件触发截断（`H_adaptive=h<H`）；截断后仅对下一次重规划施加 OGG（Eq 8-11），把纠正方向 `ΔZ_corr=ΔZ_exp-ΔZ_dev` 注入 flow-matching 速度场。

## 证据

MetaWorld 跨 π0.5/SmolVLA/X-VLA 三骨干平均成功率 +15.65/+4.75/+4.05（Table 1）；success-per-call 效率最高 +29.9%/+45.3%/+39.1% 且多设置下调用次数下降（Table 4）；LIBERO few-shot+纠正 97.8% 反超全量微调 96.95%（Table 2）；83.7% 截断落在关键相位（Fig 6）；OGG 恢复率平均 +0.23（Fig 7）；真实 AgileX PiPER 平均 55.6→73.3，扰动组 +28.3（Table 5）。

## 局限

`E_t` 仅用单一预测间隔 `k`，对缓慢/视觉难辨漂移可能漏检；阈值超参多只报默认值；OGG 受限于冻结骨干先验（救不了骨干表达不了的行为）、单次开销 2.12×；校正器需域匹配示范才最有效（Table 10）。详见精读稿「主张-证据-边界矩阵」。

## 我的阅读笔记


```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
