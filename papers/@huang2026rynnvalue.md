---
tags:
  - paper
status: unread
aliases:
  - RynnValue
  - "RynnValue: Scaling Robotic Value Foundation Models with Temporal Distance"
year: 2026
title: "RynnValue: Scaling Robotic Value Foundation Models with Temporal Distance"
doi: "10.48550/arXiv.2608.09853"
arxiv: "2608.09853v1"
url: "https://arxiv.org/abs/2608.09853"
venue: "arXiv preprint"
venue_short: "arXiv"
arxiv_url: "https://arxiv.org/abs/2608.09853"
arxiv_doi: "10.48550/arXiv.2608.09853"
pdf_url: "https://arxiv.org/pdf/2608.09853v1"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/huang2026rynnvalue.pdf]]"
reading: "[[papers/bilingual/huang2026rynnvalue_中英混读.md]]"
images: "papers/images/huang2026rynnvalue/"
image_index: "[[papers/images/huang2026rynnvalue/index.md]]"
map_axis: "具身智能/价值模型与规划"
map_brief: "把机器人奖励模型的监督目标从 preference / normalized progress 换成 temporal distance（到语言目标的 cost-to-go），标签直接由时间戳导出，7000+ 小时、3M 片段无偏好标注训练。"
map_role: "研究通用机器人价值模型该用什么监督目标，以及价值信号如何接成真机 RL 的 dense reward 的入口。"
authors:
  - "[[Dongchi Huang]]"
  - "[[Hongyin Zhang]]"
  - "[[Bohan Hou]]"
  - "[[Siteng Huang]]"
  - "[[Zhian Su]]"
  - "[[Hang Guo]]"
  - "[[Tong Lu]]"
  - "[[Zhaofeng Xu]]"
  - "[[Jiahao Tang]]"
  - "[[Jianfei Yang]]"
  - "[[Donglin Wang]]"
  - "[[Peixi Peng]]"
  - "[[Mingxiu Chen]]"
  - "[[Deli Zhao]]"
  - "[[Xin Li]]"
institutions:
  - "[[DAMO Academy, Alibaba Group]]"
  - "[[Hupan Lab]]"
topics:
  - value foundation model
  - reward model
  - temporal distance
  - cost-to-go
  - potential-based shaping
  - shortcut learning
  - robot manipulation
  - offline RL
  - online RL
  - RBM-EVAL-OOD
---

# RynnValue: Scaling Robotic Value Foundation Models with Temporal Distance

- [x] PDF:: [[papers/pdfs/huang2026rynnvalue.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/huang2026rynnvalue_中英混读.md]]
- [x] 图片索引:: [[papers/images/huang2026rynnvalue/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[value model]], [[reward model]], [[reinforcement learning]], [[@wang2026wvm]], [[@yu2026warp-rm]], [[@liu2026steam]], [[@qian2026wam-rl]], [[@yu2026wm-dagger]], [[@intelligence2025pi06-vla-that-learns]]
affiliation:: [[DAMO Academy, Alibaba Group]], [[Hupan Lab]]

## Abstract

General-purpose reward models are increasingly the bottleneck for scaling robot learning, yet the recipe for learning value-related capabilities from large-scale heterogeneous corpora remains underexplored. Existing approaches tie supervision to task-internal anchors such as preferences or normalized progress, none of which transfer cleanly across embodiments and data sources. We introduce RynnValue, an open-source value foundation model for robotic manipulation that replaces these anchors with temporal distance, the directed cost-to-go from an observation to the language-specified goal. Because temporal-distance labels can be derived directly from timestamps, RynnValue scales to over 7,000 hours and roughly 3M instruction-conditioned clips without preference or progress annotations. To make temporal-value learning reliable at scale, we combine random temporal sampling, temporal-order shuffling, and value-isolation attention, suppressing shortcuts that would leave predictions insensitive to failures and regressions. Trained without preference labels, RynnValue attains an average Kendall's tau_a of 0.675 on RBM-EVAL-OOD, surpassing the fully preference-supervised state of the art (0.655) and more than doubling a progress-only counterpart (0.292), while generalizing zero-shot to unseen tasks, embodiments, and viewpoints. Converted into dense rewards via potential-based shaping, it raises real-world policy success from 52.5% to 72.5% online and from 63.8% to 82.5% offline. These results establish temporal distance as a scalable supervision target and practical reward interface for generalist robot policies.

## 一句话定位

通用机器人奖励模型卡在监督目标上，preference 和 normalized progress 都是任务内部锚点，没法跨本体跨数据源迁移；RynnValue 把目标换成 temporal distance，也就是从观测到语言指定目标的有向 cost-to-go，标签直接从时间戳读，因此能在 7000+ 小时、约 3M 指令条件片段上规模化训练，并作为 dense reward 接口接进真机 RL。

## 方法 / 对象

- 监督目标：temporal distance 而非 normalized progress。绝对目标是到重标注 completion cutoff 的剩余时间 $v^\star_i=\max(0,t_G-t_i)$，相对目标是呈现序列上相邻观测的有符号时间位移 $\Delta^\star_i=t_{i+1}-t_i$。
- 骨干：RynnBrain 上继续预训练，8B 为主，另报 4B 变体。
- 序列构造：观测与绝对/相对价值查询组交错，每组 8 个重复 token，同组双向注意力后沿特征维拼接而非平均。
- 读出：两个 BroNet 残差 MLP 头，输出 256 个 symlog 分箱上的分布，two-hot 目标训练，推理取期望箱心再 symexp 逆变换。
- 捷径压制一（视觉层）：random temporal sampling 用不规则时间戳采 8 帧，temporal-order shuffling 以 0.5 概率打乱时序、rewind 概率 0.3。
- 捷径压制二（价值层）：value-isolation attention 禁止跨观测的价值查询互相注意，同时禁止上下文 token 回看价值查询。
- 语言监督：10% 样本做 instruction-mismatch augmentation 并对绝对损失打掩码；语言分支自回归输出视频描述、Match、Success，不回流到时间头。
- 联合损失：$\mathcal{L}=\mathcal{L}_{abs}+\mathcal{L}_{rel}+2\mathcal{L}_{lang}$。
- 奖励接口：势函数 $\Phi_t=-v_t$，套 potential-based shaping $r'_t=\kappa(\gamma\Phi_{t+1}-\Phi_t)$ 加稀疏完成项。
- 数据：AgiBot、EgoDex、Galaxea、InternData-A1、OXE、RDT、RoboCOIN、RoboMIND、RoboTwin、Soft-FOLD 混合，1.67M episode 展开成 3.09M 片段。

## 证据

- RBM-EVAL-OOD 轨迹排序：RynnValue-8B 平均 Kendall's τ_a 0.675，4B 0.670，超过全偏好监督的 Robometer (RBM-1M) 0.655，是 progress-only 对照 0.292 的两倍多。
- 偏好无关方法内部对比：此前最强 0.502（RoboReward-4B），本文提到 0.675。
- 消融（Table 3）：去掉 temporal-order shuffling 掉到 0.189，换均匀采样 0.379，去掉 value-isolation 0.482，去掉语言监督 0.537，去掉相对价值 0.627。
- 指令轨迹对齐（Figure 3）：归一化对角边际 0.79，最强基线 0.67，所有基线用公开权重统一协议重跑。
- 缩放分析（Figure 4）：固定任务只加 episode，误差很快饱和；固定每任务 episode 只加任务数，误差在整个区间单调下降。收益来自多样性。
- 真机 RL（Table 4）：在线平均成功率 72.5%（Robometer 52.5%，Sparse 48.8%），离线 82.5%（Robometer 63.8%，Sparse 22.5%，SFT 23.8%）。盒子入抽屉和双臂搬箱在 SFT 与稀疏离线 RL 下均为 0%。
- 数据清洗（Table 6）：保留 1,436,150/1,722,966 个轨迹单元（83.35%），同时保留 192,989/194,967 条唯一指令（98.99%）。

## 局限

- 领先幅度有限。0.675 对 0.655 只差 0.02，且在 USC xArm 和 MIT Franka 两个子集上低于 Robometer；论文没给方差或置信区间。USC Trossen 上的 1.000 提示该子集样本很少。
- 塑形强度 κ 对 RynnValue 取 0.1、对 Robometer 取 1.0，差一个数量级，论文没解释取值来源也没做敏感性分析，真机对比的干净程度因此打折。
- completion cutoff 重标注写的是「必要时按数据集特定的比例或时长裁剪」，人工含量没有量化，跟「标签全自动且便宜」的卖点有张力。
- 真机只有四个任务、每任务 20 试次，全是桌面单臂或双臂抓放类，没有灵巧手和移动操作。
- 只从短窗口采样观测估计时间距离，尚不支持长时程和流式推理。
- 目标假设近似 minimum-time，能耗、安全、精度这类代价没有进来；很多操作任务里慢而稳优于快而险。
- 盒子入抽屉的在线提升只有 5 个点，作者归因于奖励模型只看第三人称 RGB，视觉相似但抓取稳定性差异大的构型无法校准。
- 消融只在 8B 上做，没验证小模型是否同样脆弱。

## 我的阅读笔记

这篇最值得抄的不是 temporal distance 这个想法本身，TimeRewarder 那条线早就在做帧间时间距离了。真正扎实的是 Table 3 那张消融表。去掉时序打乱平均 τ_a 掉到 0.189，比表里大多数基线都差，这个数字说明多帧价值模型对捷径的脆弱程度被整个领域低估了。任何做多帧奖励或多帧价值的工作，动手前都该先确认自己有没有踩同一个坑。

4B 和 8B 只差 0.005 这件事也值得单独记一笔。它把「这条路线的收益来自表述方式而不是模型容量」这个判断落到了实处，同时也提示上限还没被摸到。

Figure 4 那组对照实验对做数据的人价值最大。同一任务反复采集很快就不再提供新信号，扩任务覆盖才有效。这个结论跟 [[@liu2026steam]] 的数据筛选思路是一条线上的，可以并读。

跟 [[@qian2026wam-rl]] 并排看会更清楚。WAM-RL 的 reconstruction reward 是自监督的、不需要外部模型但语义弱；RynnValue 的信号语义明确、语言条件化，但要挂一个 8B 模型在线推理。真机 RL 缺 dense reward 这个痛点，现在至少有了两种代价结构完全不同的解法。

需要保留的怀疑是 κ。塑形强度差一个数量级还没做敏感性分析，这让真机那张表的说服力比基准表弱一档。基准结果我信，真机结果我会打个问号再看后续复现。

## 摘录

> We argue for a shift in framing: from a reward model scoring trajectory-level anchors to a value foundation model predicting goal-conditioned cost-to-go as a single reusable interface.

> Such shortcuts can leave learned values insensitive to regressions, failures, and other non-monotonic events.

> Task-diversity scaling behaves qualitatively differently: increasing the number of training tasks reduces error monotonically across the entire range, with substantial gains still observable well past the midpoint.

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
