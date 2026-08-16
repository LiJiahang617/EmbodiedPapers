---
tags:
  - paper
status: unread
aliases:
  - AtlasVLA
  - "AtlasVLA: Persistent World-Ego State Modeling for Vision-Language-Action Models"
year: 2026
title: "AtlasVLA: Persistent World-Ego State Modeling for Vision-Language-Action Models"
doi: "10.48550/arXiv.2608.06729"
arxiv: "2608.06729v1"
url: "https://arxiv.org/abs/2608.06729"
venue: "arXiv preprint (AAAI 格式投稿)"
venue_short: "arXiv"
arxiv_url: "https://arxiv.org/abs/2608.06729"
arxiv_doi: "10.48550/arXiv.2608.06729"
pdf_url: "https://arxiv.org/pdf/2608.06729v1"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/zhao2026atlasvla.pdf]]"
reading: "[[papers/bilingual/zhao2026atlasvla_中英混读.md]]"
images: "papers/images/zhao2026atlasvla/"
image_index: "[[papers/images/zhao2026atlasvla/index.md]]"
map_axis: "具身智能/VLA/持久空间记忆与状态建模"
map_brief: "只用腕部相机，把 2D 观测按单目深度反投影成 3D 并用体素哈希持续融合成 4D 持久世界状态，再配一块意图查询驱动的自我工作记忆，双路检索后条件化逐步 DiT。"
map_role: "研究 VLA 如何摆脱多视角依赖、用显式空间记忆而非时间缓存对抗部分可观测与长时程遗忘的入口。"
authors:
  - "[[Guiyu Zhao]]"
  - "[[Longteng Guo]]"
  - "[[Yanghong Mei]]"
  - "[[Zilin Zhu]]"
  - "[[Yu Zhang]]"
  - "[[Bin Cao]]"
  - "[[MingMing Yu]]"
  - "[[Xingjian He]]"
  - "[[Jie Jiang]]"
  - "[[Jing Liu]]"
institutions:
  - "[[Institute of Automation, Chinese Academy of Sciences]]"
  - "[[University of Chinese Academy of Sciences]]"
  - "[[Beijing Freedo Technology]]"
  - "[[Beihang University]]"
topics:
  - vision-language-action
  - spatial memory
  - partial observability
  - long-horizon manipulation
  - voxel hashing
  - monocular depth
  - diffusion transformer
  - wrist-only camera
  - LIBERO
  - RLBench
---

# AtlasVLA: Persistent World-Ego State Modeling for Vision-Language-Action Models

- [x] PDF:: [[papers/pdfs/zhao2026atlasvla.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/zhao2026atlasvla_中英混读.md]]
- [x] 图片索引:: [[papers/images/zhao2026atlasvla/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[spatial memory]], [[VLA]], [[long-horizon manipulation]], [[@zhou2026holoagent0]], [[@yang2026dreamtrajectory]], [[@liu2026last0-latent-spatio-temporal]], [[@jiang2026robottt]], [[@wang2026wvm]], [[@intelligence2026pi07-steerable-generalist-robotic]]
affiliation:: [[Institute of Automation, Chinese Academy of Sciences]], [[University of Chinese Academy of Sciences]], [[Beijing Freedo Technology]], [[Beihang University]]

## Abstract

While Vision-Language-Action (VLA) models have advanced embodied AI, their fundamentally reactive paradigm severely limits performance in partially observable and long-horizon tasks. When restricted to a single wrist-mounted camera, they inevitably suffer from perception forgetting as objects exit the field of view, and temporal task-progress forgetting during multi-step execution. To overcome these bottlenecks, we propose AtlasVLA, a novel framework that transitions from direct reactive manipulation to proactive reasoning through a persistent world-ego state. AtlasVLA features a dual-memory architecture: a 4D Persistent World State Memory that lifts transient 2D observations into a globally updated, voxel-hashed spatial state to resolve visual blind spots, and an Ego-Working State Memory that tracks historical ego state and task progress. By conditioning a diffusion transformer (DiT) on this joint World-Ego state, AtlasVLA enables robust spatial reasoning. Extensive evaluations across LIBERO, RLBench, and real-world benchmarks demonstrate that AtlasVLA achieves state-of-the-art performance using solely a wrist camera. Remarkably, it decisively outperforms multi-view baselines, yielding absolute success rate improvements of 9.4% on LIBERO-Long and 17.5% in real-world long-horizon tasks.

## 一句话定位

反应式 VLA 在腕部单相机设定下有两种遗忘，物体出视野即被忘掉的感知遗忘和多步执行中的任务进度遗忘；AtlasVLA 给它装两块记忆，一块是把 2D 观测反投影成 3D 再用体素哈希持续融合的 4D 持久世界状态，一块是用可学习意图查询维护的自我工作状态，双路检索后条件化一个逐步 DiT，从而只靠腕部相机就超过多视角基线。

## 方法 / 对象

- 约束：严格腕部单视角。输入只有腕部 RGB $O^w_t$、本体状态 $S_t$、语言指令 $L$，输出 7 维动作块（6-DoF 末端位姿 + 二值夹爪）。
- 抬升：Depth Anything v3 流式版估深度；外参 $T^{ex}=\psi(S_t)\cdot T_{h2e}$ 由机器人状态加手眼标定推出；反投影得到带 3D 位置的潜 token $m_t$。
- 时空嵌入：$\hat m_t=m_t+E_{spatial}(P_t)+E_{temporal}(t)$，两个编码均为 MLP，用来防空间混叠与时间退化。
- 空间更新：类 TSDF 体素哈希加权融合 $M_t(v)=\frac{W_{t-1}M_{t-1}+w_t m_t}{W_{t-1}+w_t}$，权重 $w_t(v)=c_t(v)$ 取自深度置信度，累积权重 $W_t(v)=\lambda W_{t-1}(v)+w_t(v)$。
- 时间更新：最大窗口 $W$ 的滑窗；首帧记忆「永久初始化」锚定，理由是首帧视野最优且反映初始状态。
- 自我记忆：可学习意图查询 $Q_{ego}\in\mathbb{R}^{N\times d}$ 跨注意力浓缩上下文；记忆库按 $M^{ego}_t=\text{Cons}(M^{ego}_{t-1}\cup\{Z^{ego}_t+E_{temporal}(t)\})$ 做冗余感知合并。
- 双路检索：先 $C^{ego}_t=\text{CrossAttn}(Z^{ego}_t,M^{ego}_t,M^{ego}_t)$，再用它当查询去查世界记忆 $C^{world}_t=\text{AddNorm}(\text{FFN}(\text{IntentAttn}(C^{ego}_t,M_t,M_t)))$。方向是自我查世界。
- 动作生成：逐步条件化 DiT，每个扩散步先过自我工作注意力再过世界状态注意力，堆 $L$ 层；DDIM 10 步，CFG 1.5。
- 规模：LLM 7B，DiT 动作专家约 300M；8× A100 + FSDP，全局批量 256，峰值学习率 $2\times10^{-5}$。

## 证据

- LIBERO（每任务 50 条示范、50 次 rollout，取最终检查点而非最佳验证步）：AtlasVLA 纯腕部 97.6%（五套件），逐套件 99.4/99.8/98.2/94.6/95.8。对比 MemoryVLA 纯腕部 94.0%、π0 纯腕部 90.7%、π0 第三人称+腕部 94.2%、OpenVLA-OFT 第三人称+腕部 97.1%。
- LIBERO-Long 单列：94.6% 对 MemoryVLA 纯腕部 87.6%（+7.0）、π0 第三人称+腕部 85.2%（+9.4，摘要引用的就是这个）。
- 同方法跨相机配置的退化：π0 从 94.2% 掉到 90.7%，MemoryVLA 从 96.5% 掉到 94.0%，LIBERO-Long 上 MemoryVLA 掉 5.8 个点。
- RLBench（6 任务各 20 次试验，8 万步，$128\times128$ 腕部 RGB）：70.8% 对 MemoryVLA 纯腕部 55.0%（+15.8）、其第三人称 63.3%（+7.5）。
- 真机通用任务（Franka + 腕部 RealSense D415，6 任务各 50 次试验）：78.7% 对 MemoryVLA 纯腕部 62.3%（+16.4）、第三人称 70.7%（+8.0）、π0 第三人称+腕部 66.7%。
- 真机长时程（4 任务各 50 次试验）：69.5% 对 π0 52.0%（+17.5）、MemoryVLA 60.5%（+9.0）。
- 消融（LIBERO / 真机长时程）：去世界状态记忆 93.5 / 54.0；去自我工作记忆 95.0 / 56.5；完整 97.6 / 69.5；去时空更新（改朴素累积）94.6 / 58.0；去空间 PE 96.4 / 67.5；去时间 PE 96.8 / 65.0；去世界状态条件化 95.2 / 61.5。

## 局限

- 无独立局限章节（AAAI 格式）。
- **外部依赖的误差敏感性完全没分析。** 整套世界记忆建在单目深度（Depth Anything v3）和由机器人状态加手眼标定推出的外参上。标定漂移会把不同时刻的 token 落进错误体素，深度误差会整体偏移 3D 位置。置信度权重直接取自深度置信度，但该置信度本身的校准也未评估。真机部署里手眼标定漂移很常见，这是最关键的空白。
- 关键超参与函数缺失：体素尺寸、时间窗口 $W$、衰减 $\lambda$、意图查询数量 $N$、合并函数 $\text{Cons}(\cdot)$ 的形式，正文均未给（只说见附录）。体素尺寸直接决定空间分辨率与记忆规模的权衡。
- 计算开销一个数字都没报。持久体素地图 + 7B LLM + 双路跨注意力检索，推理延迟和显存占用未知。对一个主打降低部署门槛的方法来说是硬伤，省掉第三人称相机换来几倍延迟的话这笔账未必划算。
- 缺朴素对照。自我工作记忆要防进度遗忘，最直接的对照是「堆叠过去 N 帧腕部图像」，论文批评了扩展上下文窗口却没跑这个基线，意图查询的增量因此无法单独判定。
- 首帧永久锚定假设首帧视野最优。这在 LIBERO / RLBench 这类固定初始位姿的基准里成立，真实部署里未必，且该规则没有单独消融。
- LIBERO 平均值口径不齐。表注说明「无 LIBERO-90 结果的方法按前四套件平均」，所以 97.6 是五套件、π0 的 90.7 和 OpenVLA-OFT 的 97.1 是四套件。逐列比较（尤其 Long）干净，总平均要打折扣。
- 「逐步条件化优于全局条件化」这个卖点没有对应消融，row 9 只验证了「有没有世界状态注意力」。
- RLBench 每任务只有 20 次试验，5 个点就是 1 次成功。
- 纯腕部基线是否经过同等调优未交代。

## 我的阅读笔记

Table 5 那两列的落差是这篇最有信息量的地方，论文自己没点破。去掉世界状态记忆，LIBERO 只掉 4.1 个点（97.6 → 93.5），真机长时程掉 15.5 个点（69.5 → 54.0）。同一个消融在仿真和真机上差了近四倍。这说明 LIBERO 作为评测环境严重低估了部分可观测的难度，任何在 LIBERO 上做空间记忆的工作都该拿这个落差提醒自己。

方法上最值得抄的不是记忆怎么建，是 Eq. 9 的检索方向。用「我现在想干什么」当查询去筛「世界里哪部分相关」，而不是把整个世界状态无差别喂给动作头。持久记忆的规模会随时间涨，没有这一步筛选，记忆越大反而越糟。这个设计比体素融合本身更通用。

「取最终训练检查点而非最佳验证步」这一句也值得记。作者明说是为了避免验证偏置。这种自我约束在 VLA 论文里不常见，值得肯定。

位置编码的消融有点反直觉，去掉时间 PE（掉 4.5）比去掉空间 PE（掉 2.0）更伤。对一个主打空间记忆的方法来说，可能说明时间戳在区分「同一位置的不同时刻状态」上承担了更多工作，也可能说明空间信息已经被 3D 坐标本身编码了一部分。

最大的保留是外部依赖。整篇论文的空间能力建在单目深度和手眼标定上，两者的误差敏感性一个字没提。仿真里深度和外参都是完美的，真机里不是。真机结果（69.5%）确实比基线好，但如果标定漂移或深度失效，这套记忆会怎么退化，论文没给任何线索。要在自己的机器人上复现，这是第一个要测的东西。

计算开销不报也让人不安。腕部单相机的卖点是部署简单，但持久体素地图加 7B LLM 加双路检索，实际跑起来是什么代价，读者完全没法判断。

## 摘录

> Fundamentally, an instantaneous camera field-of-view (FoV) is not equivalent to the true world state.

> This requires transitioning from a paradigm of memoryless observation to one governed by a continuous cycle: local observation → latent state update → persistent world state → future action.

> existing paradigms remain heavily skewed toward temporal caching without explicit spatial modeling, leaving the inherent partial observability unresolved.

> To demonstrate the robust convergence of our method without validation bias, all reported results are derived directly from the final training checkpoint rather than the best validation step.

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
