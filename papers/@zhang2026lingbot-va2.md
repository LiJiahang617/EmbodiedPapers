---
tags:
  - paper
status: unread
aliases:
  - "Native Video-Action Pretraining for"
year: 2026
title: "Native Video-Action Pretraining for Generalizable Robot Control"
doi: 
arxiv: "2607.08639"
url: 
venue: 
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/zhang2026lingbot-va2.pdf]]"
reading: "[[papers/bilingual/zhang2026lingbot-va2_中英混读.md]]"
images: "papers/images/zhang2026lingbot-va2/"
image_index: "[[papers/images/zhang2026lingbot-va2/index.md]]"
authors:
  - "[[Generalizable Robot Control Qihang Zhang]]"
  - "[[Lin Li]]"
  - "[[Luyao Zhang]]"
  - "[[Shuai Yang]]"
  - "[[Yiming Luo]]"
  - "[[Shuaiting Li]]"
  - "[[Ruilin Wang]]"
  - "[[Junke Wang]]"
  - "[[Jiahao Shao]]"
  - "[[Gangwei Xu]]"
institutions:
topics:
---

# Native Video-Action Pretraining for

- [ ] PDF:: [[papers/pdfs/zhang2026lingbot-va2.pdf]]
- [ ] 元数据:: source=arxiv, confidence=medium
- [x] 精读稿:: [[papers/bilingual/zhang2026lingbot-va2_中英混读.md]]
- [ ] 地图维护:: 已加入 [[论文地图]] 快速索引后，运行 `python setting/scripts/check_paper_map.py --sync-reading-markers`
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract



## 一句话定位

LingBot-VA 2.0 从头预训练 semantic visual-action tokenizer 与 causal video-action DiT，把无标签网络视频也转成 action-relevant 监督，并用 MCP、MoE 与 Foresight Reasoning 支持少样本、高频闭环机器人控制。

## 方法 / 对象

- 对象：通用机器人控制中“现成视频生成器后接动作头”造成的语义、因果和实时性缺口。
- 方法：共享视觉—动作语义 latent、严格因果预训练、多 chunk 未来预测、MoE、基于最新实测观测回锚的异步推理。

## 证据

- Table 1/2：RoboTwin 2.0 成功率与 tokenizer 消融；Fig. 10：MCP 收敛；Table 3：推理加速频率。
- Fig. 8、11：真实任务部署和定性长程操作；摘要报告峰值异步执行频率 225 Hz、10--15 条示范适配。

## 局限

- 数字、硬件和任务分布主要来自作者系统；对第三方平台、安全恢复和极端 OOD 的外部验证仍需补充。

## 我的阅读笔记


```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
