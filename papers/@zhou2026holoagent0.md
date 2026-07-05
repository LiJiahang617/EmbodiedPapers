---
tags:
  - paper
status: unread
aliases:
  - "HoloAgent-0: A Unified Embodied Agent Framework with 3D Spatial Memory"
year: 2026
title: "HoloAgent-0: A Unified Embodied Agent Framework with 3D Spatial Memory"
doi: 
arxiv: "2606.23565"
url: "https://arxiv.org/abs/2606.23565"
venue: "arXiv"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/zhou2026holoagent0.pdf]]"
reading: "[[papers/bilingual/zhou2026holoagent0_中英混读.md]]"
images: "papers/images/zhou2026holoagent0/"
image_index: "[[papers/images/zhou2026holoagent0/index.md]]"
authors:
  - "[[Xiaolin Zhou]]"
  - "[[Liu Liu]]"
  - "[[Tingyang Xiao]]"
  - "[[Wei Feng]]"
  - "[[Fa Fu]]"
  - "[[Xinrui Meng]]"
  - "[[Xinjie Wang]]"
  - "[[Jialiang Han]]"
  - "[[Boyang Yu]]"
  - "[[Yun Du]]"
  - "[[Wei Sui]]"
  - "[[Zhizhong Su]]"
institutions:
topics:
---

# HoloAgent-0: A Unified Embodied Agent Framework with 3D Spatial Memory

- [ ] PDF:: [[papers/pdfs/zhou2026holoagent0.pdf]]
- [ ] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/zhou2026holoagent0_中英混读.md]]
- [ ] 地图维护:: 已加入 [[论文地图]] 快速索引后，运行 `python setting/scripts/check_paper_map.py --sync-reading-markers`
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

LLM agents follow a practical execution loop in digital environments: they reason over structured states, invoke tools, inspect feedback, and revise actions. Extending this loop to physical robots is difficult because physical execution is continuous, embodiment-dependent, uncertain, and constrained by safety. Existing embodied-AI systems have advanced manipulation, spatial understanding, navigation, and humanoid control, but these capabilities often remain specialized modules or loosely coupled decision loops. In this work, we introduce HoloAgent-0, a unified embodied agent framework for real-world robot deployment. Embodied AgentOS converts language instructions into executable skill graphs, schedules robot resources, monitors execution, and triggers clarification or re-planning from runtime feedback. HoloAgent-0 organizes heterogeneous robot models and controllers through three coupled layers: Embodied AgentOS for closed-loop execution, 3D spatial memory for physical world grounding, and embodied skills for robot action. We deploy HoloAgent-0 on real hardware and evaluate its spatial memory, long-horizon navigation, and closed-loop execution across motion generation, object search, cross-robot coordination, and mobile manipulation.

## 一句话定位

HoloAgent-0 把 LLM agent 的 reason-tool-feedback-replan 循环扩展到物理机器人，用 Embodied AgentOS、3D spatial memory 和 embodied skills 组织真实机器人执行。

## 方法 / 对象

- 对象：真实世界 robot deployment 中的 long-horizon navigation、spatial memory、closed-loop execution、skill scheduling。
- 架构：Embodied AgentOS 将语言指令转成 executable skill graphs，调度机器人资源，监控执行，并根据 runtime feedback 触发 clarification 或 re-planning。
- 三层组织：Embodied AgentOS、3D spatial memory、embodied skills。

## 证据

- 摘要称已部署在 real hardware，并评估 spatial memory、long-horizon navigation、closed-loop execution。
- 关键证据需要查看具体硬件平台、任务集、失败恢复机制和安全约束。

## 局限

- 这是 framework/system 论文，效果可能依赖模块工程质量和集成细节；需要区分架构贡献和单个 skill/controller 的能力。
- 真实机器人部署的可复现性通常受硬件、地图、传感器和安全策略影响较大。

## 我的阅读笔记

- 和 Orca/Qwen-RobotWorld 形成互补：前者学习 world latent/未来预测，HoloAgent-0 更像执行层 agent operating system。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
