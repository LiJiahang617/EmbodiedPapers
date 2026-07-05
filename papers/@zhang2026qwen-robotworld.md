---
tags:
  - paper
status: unread
aliases:
  - "Qwen-RobotWorld Technical Report: Unifying Embodied World Modeling through Language-Conditioned Video Generation"
year: 2026
title: "Qwen-RobotWorld Technical Report: Unifying Embodied World Modeling through Language-Conditioned Video Generation"
doi: 
arxiv: "2606.17030"
url: "https://arxiv.org/abs/2606.17030"
venue: "arXiv"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/zhang2026qwen-robotworld.pdf]]"
reading: "[[papers/bilingual/zhang2026qwen-robotworld_中英混读.md]]"
images: "papers/images/zhang2026qwen-robotworld/"
image_index: "[[papers/images/zhang2026qwen-robotworld/index.md]]"
authors:
  - "[[Jie Zhang]]"
  - "[[Xiaoyue Chen]]"
  - "[[Anzhe Chen]]"
  - "[[Dayiheng Liu]]"
  - "[[Deqing Li]]"
  - "[[Gengze Zhou]]"
  - "[[Hale Yin]]"
  - "[[Haoqi Yuan]]"
  - "[[Haoyang Li]]"
  - "[[Jiahao Li]]"
  - "[[Jiazhao Zhang]]"
  - "[[Jingren Zhou]]"
  - "[[Kaiyuan Gao]]"
  - "[[Kun Yan]]"
  - "[[Lihan Jiang]]"
  - "[[Ningyuan Tang]]"
  - "[[Pei Lin]]"
  - "[[Qihang Peng]]"
  - "[[Shengming Yin]]"
  - "[[Tianhe Wu]]"
  - "[[Tianyi Yan]]"
  - "[[Xiao Xu]]"
  - "[[Yan Shu]]"
  - "[[Yanran Zhang]]"
  - "[[Ye Wang]]"
  - "[[Yi Wang]]"
  - "[[Yilei Chen]]"
  - "[[Yixian Xu]]"
  - "[[Yiyang Huang]]"
  - "[[Yuxiang Chen]]"
  - "[[Zekai Zhang]]"
  - "[[Zhendong Wang]]"
  - "[[Zixing Lei]]"
  - "[[Zhixuan Liang]]"
  - "[[Zihao Liu]]"
  - "[[Zikai Zhou]]"
  - "[[Chenxu Lv]]"
  - "[[Xiong-Hui Chen]]"
  - "[[Chenfei Wu]]"
institutions:
topics:
---

# Qwen-RobotWorld Technical Report: Unifying Embodied World Modeling through Language-Conditioned Video Generation

- [ ] PDF:: [[papers/pdfs/zhang2026qwen-robotworld.pdf]]
- [ ] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/zhang2026qwen-robotworld_中英混读.md]]
- [ ] 地图维护:: 已加入 [[论文地图]] 快速索引后，运行 `python setting/scripts/check_paper_map.py --sync-reading-markers`
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

We introduce Qwen-RobotWorld, a language-conditioned video world model for embodied intelligence. With natural language as a unified action interface, it predicts physically grounded future visual trajectories from current observations across robotic manipulation, autonomous driving, indoor navigation, and human-to-robot transfer. This unified formulation provides three promising application directions: synthetic data generation for policy training augmentation, scalable virtual environments for policy evaluation, and language-guided planning signals for downstream robot control. This is achieved through a three-part design: a) Double-Stream MMDiT with MLLM Action Encoding, where a 60-layer double-stream diffusion transformer couples frozen Qwen2.5-VL semantics with video-VAE latents through layer-wise joint attention; b) Embodied World Knowledge (EWK), an 8.6M video-text corpus (200M+ frames) with action-language mapping over 20+ embodiments and 500+ action categories; and c) General+Expert Progressive Curriculum, a two-stage training strategy that first learns general visual priors and then injects embodied specialization under a shared language interface. Extensive results show strong competitiveness: ranks 1st overall on EWMBench and DreamGen Bench, outperforms all open-source models on WorldModelBench and PBench. Additional zero-shot analyses on RoboTwin-IF benchmark further support robust generalization and multi-view consistency.

## 一句话定位

Qwen-RobotWorld 把自然语言作为统一动作接口，训练 language-conditioned video world model 来预测具身任务中的未来视觉轨迹。

## 方法 / 对象

- 对象：robot manipulation、autonomous driving、indoor navigation、human-to-robot transfer 等多 embodiment 场景。
- 核心方法：Double-Stream MMDiT 结合冻结的 Qwen2.5-VL 语义表示与 video-VAE latent；Embodied World Knowledge (EWK) 数据集包含 8.6M video-text、200M+ frames、20+ embodiments、500+ action categories。
- 训练策略：General+Expert Progressive Curriculum，先学通用视觉先验，再注入 embodied specialization。

## 证据

- 摘要声称该统一形式可服务三类下游：synthetic data generation、virtual policy evaluation、language-guided planning signals。
- 证据线索主要来自跨 robotic manipulation/driving/navigation/human-to-robot 的实验覆盖，需要精读表格确认指标、baselines 和数据泄漏风险。

## 局限

- World model 输出以未来视觉轨迹为主，是否足够支持闭环 control 还要看 downstream policy 结果。
- 语言动作接口的粒度、跨 embodiment 泛化边界、合成数据是否真的提高 policy success，需要从实验细节验证。

## 我的阅读笔记

- 和 GigaWorld-1/Orca 的比较重点：Qwen-RobotWorld 更强调 language-conditioned video generation 作为 world model 接口，而不是统一 latent 或 benchmark 工具链。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
