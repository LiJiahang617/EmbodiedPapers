---
tags:
  - paper
  - cat/value-reward
status: unread
aliases:
  - UR-VC
  - "UR-VC: Unsupervised Robotic Value Correction for Time-Derived Progress Proxies"
year: 2026
title: "UR-VC: Unsupervised Robotic Value Correction for Time-Derived Progress Proxies"
doi: "10.48550/arXiv.2607.12892"
arxiv: "2607.12892v1"
url: "https://arxiv.org/abs/2607.12892"
venue: "arXiv preprint"
venue_short: "arXiv"
arxiv_url: "https://arxiv.org/abs/2607.12892"
arxiv_doi: "10.48550/arXiv.2607.12892"
pdf_url: "https://arxiv.org/pdf/2607.12892v1"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/zhao2026urvc.pdf]]"
reading: "[[papers/bilingual/zhao2026urvc_中英混读.md]]"
images: "papers/images/zhao2026urvc/"
image_index: "[[papers/images/zhao2026urvc/index.md]]"
map_axis: "具身智能/价值与奖励/进度标签修正"
map_brief: "指出用归一化时间冒充任务进度的标签在接触密集操作里是坏的（倒退时照涨、固定时域优势退化成常数），提出离线免训练的 UR-VC，用 SigLIP-2 跨 episode 检索相似状态、每 episode 一票平均时间标签得到修正进度，接 π*0.6 优势条件化后真机叠衣成功率 72.8% 到 78.9%。"
map_role: "所有要消费进度、价值或优势信号的管线的前置质检站，回答标签该不该先修再学。"
authors:
  - "[[Lirui Zhao]]"
  - "[[Modi Shi]]"
  - "[[Li Chen]]"
  - "[[Qi Liu]]"
  - "[[Ping Luo]]"
  - "[[Hongyang Li]]"
institutions:
  - "[[The University of Hong Kong]]"
topics:
  - progress label
  - value correction
  - time-derived proxy
  - advantage conditioning
  - cross-episode retrieval
  - SigLIP-2
  - deformable manipulation
  - cloth folding
  - label noise
---

# UR-VC: Unsupervised Robotic Value Correction for Time-Derived Progress Proxies

- [x] PDF:: [[papers/pdfs/zhao2026urvc.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/zhao2026urvc_中英混读.md]]
- [x] 图片索引:: [[papers/images/zhao2026urvc/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[progress label]], [[value correction]], [[advantage conditioning]], [[@intelligence2025pi06-vla-that-learns]], [[@huang2026rynnvalue]], [[@wang2026wvm]], [[@yu2026warp-rm]], [[@liu2026steam]]
affiliation:: [[The University of Hong Kong]]

## Abstract

Modern robot learning systems increasingly rely on dense progress or value signals to evaluate intermediate states, guide policy learning, and detect task completion, making the quality of these signals critical. Since such dense labels are rarely available at scale, normalized time within a demonstration is often used as a scalable substitute: later frames are treated as higher progress. However, this time-derived label is only a noisy proxy for physical task progress. In contact-rich manipulation, a robot may make progress and then lose it through slips, failed grasps, or partial undoing, while the time-derived label continues to increase monotonically. We introduce Unsupervised Robotic Value Correction (UR-VC), an offline, training-free method for correcting time-derived progress labels. UR-VC exploits a simple regularity in demonstration data: similar states often recur across different episodes, but at different timestamps. Instead of trusting the timestamp from a single trajectory, UR-VC retrieves similar states from other episodes and aggregates their time-derived labels to obtain a corrected progress estimate. UR-VC requires no manual progress labels, reward annotations, or additional value model. We evaluate UR-VC on real bimanual cloth flatten-and-fold data, a long-horizon deformable-object manipulation task with visible intermediate progress. The corrected labels capture local regressions and non-uniform progress that normalized time cannot represent, while preserving the overall task trend. We further use the corrected signal to construct advantage labels for VLA training, following recent advantage-conditioned policy learning. UR-VC shows a positive trend in real-robot task success under matched data, model, and training settings.

## 一句话定位

反驳「归一化时间可以当任务进度用」这个默认做法（固定时域下时间标签的优势差分在 episode 内是常数，完全无法区分好坏动作），并构造一个离线免训练的修正器，跨 episode 检索语义相似状态、每 episode 只取一票平均时间标签，修出能表达倒退的进度信号，喂给 π*0.6 式优势条件化后真机叠衣平均成功率 72.8% 到 78.9%。

## 方法 / 对象

- 形式化，时间代理 $g_t=t/T_e$ 对潜在进度 $p(o)$，两层错配（episode 内非单调、episode 间时序畸变），固定时域优势 $g_{t+H}-g_t=H/T_e$ 退化为常数。
- 统计模型 $g^{(e)}=p+\varepsilon_e$，跨独立 episode 平均压误差，同 episode 相邻帧误差相关所以必须 episode 均衡。
- 算法，SigLIP-2 L2 归一化嵌入，$\tau=0.3$ 时间带内每个其他 episode 取最相似一帧，低于 $\rho=0.90$ 丢弃，存活代表的时间标签取均值，修正幅度被 $\tau$ 界住，无匹配则不修。实现是一次 masked scatter-max 加矩阵运算。
- 下游接口照抄 π*0.6，$r_i=\hat g_{i+H}-\hat g_i$（尾部按 Eq. 8 缩放），前 20% 帧加 "advantage: positive" 文本后缀训练，部署带正后缀查询，不加新目标不训价值模型。
- 数据与真机，χ0 展平折叠数据集，主评测 150 episode，检索池到 1 万量级；下游 π0.5 骨干，5700 演示加 1795 恢复演示，AgileX 双臂，6 条件乘 30 试次。

## 证据

- 覆盖率，150 episode 时 98% 帧有相似度不低于 0.90 的跨 episode 近邻，1 万量级时 99.9%（0.955 阈值下 90.4%）。
- 非单调，主评测集 13.4% 帧获负时域优势（$r_i<-0.02$，时域约 1.7 秒），修正估计与时间整体相关 0.98，全局趋势保住。
- 稳定性，检索池 50 到 1 万，粗糙度平均 $\lvert\Delta^2\hat g\rvert$ 降约三分之一，覆盖率 96% 到 99.9%。
- 下游，平均成功率 0.728（131/180）到 0.789（142/180），6 条件赢 5 个，蓝灰桌布从 0.50 掉到 0.43。

## 局限

- 下游基线是不用优势标签，缺「原始时间标签做同样优势条件化」的关键对照，「修正比不修正好」这条因果链在下游证据上是断的。
- 13.4% 负优势帧占比无人工抽验，不是准确度指标，定量真值全文不存在（作者自己也声明不声称有 ground truth）。
- +6.1 点无置信区间，180 试次里差 11 次，作者措辞是 positive trend，引用时别放大。
- 前提（进度视觉可见、状态跨 episode 复现）在布料任务天然成立，遮挡重或进度不可见的任务会塌；无任何超参与设计选择的消融（$\tau$、$\rho$、正例比例、编码器）。
- 视觉相似即进度相似的假设有歧义状态问题，作者自陈 episode 均衡修不了系统性检索错误。

## 我的阅读笔记

这篇的价值密度集中在 Eq. 2 那一行推导，固定时域下时间标签的差分在 episode 内是常数 $H/T_e$。也就是说所有拿归一化时间当进度再做差分当优势的管线，episode 内部给每帧的信号完全一样，好动作和坏动作零区分。这是数学事实不是实验发现，反驳成本为零，以后看到任何用时间差分当优势的工作都可以直接拿这条去照。

方法本身聪明在「每 episode 一票」。普通近邻平滑会把同一条轨迹的相邻帧也拉进来平均，但那些帧的时序误差是同源的，平均了白平均。episode 均衡这一步让平均真的在压独立噪声，Eq. 3 的统计模型和算法设计是严格对应的，这种「假设写清楚、算法长在假设上」的写法值得学。

但下游实验的对照选择我要记一笔。基线是完全不用优势标签，不是用原始时间标签做优势条件化。现在的 Table I 证明的是「条件化比不条件化好」，不是「修过的标签比没修的好」。考虑到原始时间标签下正例会系统性偏向短 episode，这个缺席的对照大概率对作者有利，不做很可惜，做了这篇的说服力会上一个台阶。

适用边界也想清楚了再引。布料任务是这套方法的主场，进度写在外观上、状态跨衣物复现。换成进度藏在内部状态或遮挡后面的任务，SigLIP-2 检索的前提直接塌掉。标题里的 Robotic 覆盖面比证据大，实际是 deformable-with-visible-progress 这个子集。

## 摘录

> under a fixed-horizon progress difference, a linear time proxy assigns the same increase to every frame, so it cannot distinguish actions that improve the physical state from actions that stall or undo progress.

> when the supervision target is a systematically biased time-derived proxy, a learned estimator can inherit the same bias.

> each episode contributes at most one proxy score to the average, so the estimate aggregates evidence across demonstrations rather than across temporally adjacent frames from a single trajectory.

> Time provides useful and scalable supervision, but it should not be conflated with physical progress.

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
