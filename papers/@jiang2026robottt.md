---
tags:
  - paper
status: unread
aliases:
  - "RoboTTT: Context Scaling for Robot Policies"
year: 2026
title: "RoboTTT: Context Scaling for Robot Policies"
doi: 
arxiv: "2607.15275v1"
url: "https://arxiv.org/abs/2607.15275"
venue: "arXiv preprint"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/jiang2026robottt.pdf]]"
reading: "[[papers/bilingual/jiang2026robottt_中英混读.md]]"
images: "papers/images/jiang2026robottt/"
image_index: "[[papers/images/jiang2026robottt/index.md]]"
authors:
  - "[[Yunfan Jiang]]"
  - "[[Yevgen Chebotar]]"
  - "[[Ruijie Zheng]]"
  - "[[Fengyuan Hu]]"
  - "[[Yunhao Ge]]"
  - "[[Jimmy Wu]]"
  - "[[Tianyuan Dai]]"
  - "[[Scott Reed]]"
  - "[[Li Fei-Fei]]"
  - "[[Yuke Zhu]]"
  - "[[Linxi Fan]]"
institutions:
  - "[[NVIDIA]]"
  - "[[Stanford University]]"
  - "[[The University of Texas at Austin]]"
topics:
  - long-context policy
  - test-time training
  - fast weights
  - robot foundation model
  - vision-language-action model
  - in-context imitation
  - DAgger distillation
  - context scaling
---

# RoboTTT: Context Scaling for Robot Policies

- [x] PDF:: [[papers/pdfs/jiang2026robottt.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/jiang2026robottt_中英混读.md]]
- [x] 地图维护:: [[论文地图]]
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

Recent robot foundation models operate with single-step or short-history visuomotor context. We introduce Test-Time-Training Robot Policies (RoboTTT), a robot model and training recipe that scale visuomotor context to 8K timesteps, three orders of magnitude beyond state-of-the-art policies, without growing inference latency. At this context length, we unlock new robot capabilities: one-shot in-context imitation from human video demonstrations, on-the-fly policy improvement, robustness to perturbations, and stronger performance on multi-stage, long-horizon tasks. We also observe, for the first time, steady gains in closed-loop performance as pretraining context length scales. At its core, RoboTTT integrates Test-Time Training into robot foundation models such as Vision-Language-Action policies, yielding a sequence model whose recurrent state consists of fast weights, parameters updated by gradient descent during both training and inference, compressing histories into weight space and retrieving contextual information for long-context conditioning. To scale training context length, the recipe combines sequence action forcing with truncated backpropagation through time. On challenging real-robot manipulation tasks, RoboTTT improves overall performance by 87% over the single-step context baseline and fully completes a five-minute, ten-stage assembly task, which no baseline ever does. RoboTTT trained with 8K-timestep context outperforms the same model pretrained with 1K timesteps by 62%, suggesting context length as a new scaling axis for robot foundation models.

## 一句话定位

RoboTTT 把 Test-Time Training（TTT）的 fast weights 当作机器人策略的循环状态，把 visuomotor context 从"单步 / 几帧"拉到 8K timesteps（30 Hz 下约四到五分钟）而推理延迟不随上下文增长；作者由此第一次给出"预训练上下文越长、真机闭环表现越好"的 scaling 曲线，并把长上下文变成新能力的载体——in-context 人类视频一次性模仿、rollout 内自我纠错、扰动恢复和十阶段长程装配。

## 方法 / 对象

- 骨干是 GR00T N1.7（Eagle VLM + 538M 的 DiT action head）；在它的 16 个 DiT 层每层各加一个 TTT 层（每层约 10M，合计 690M）。分工是：attention 只在同一 timestep 内部做，TTT 层沿时间维度做——这是本文"把序列建模插进 VLA"的核心接口。
- 每个 timestep 的 token 是 $[R_t, \Phi_t, q_t, \tilde{A}_t]$：$N{=}16$ 个 learned register tokens、VLM 输出的 vision-language tokens、proprioception token、加噪 action tokens。为省算力，VL tokens **不**过 TTT 层，改由 register tokens 把视觉语言信息带过时间。
- fast weights $W$ 参数化一个两层 MLP（GeLU）。更新式 $W_t \leftarrow W_{t-1}-\eta\nabla_W \mathcal{L}_{\text{FW}}(f_{W_{t-1}}(K_t),V_t)$ 把 key 关联到 value，再用 $O_t=f_{W_t}(Q_t)$ 取回；$\theta_Q,\theta_K,\theta_V$ 和初值 $W_0$ 都由外层任务损失（经"梯度的梯度"）meta-learn，inner learning rate 可学、base 为 0.1。
- $\tanh$ gating：$O=\tanh(\alpha)\odot O_{\text{TTT}}+O_{\text{attn}}$，$\alpha$ 初始化 0.001，保证训练初期 TTT 贡献接近零，不破坏预训练 VLA 的能力。
- 训练配方两件套：**sequence action forcing**（序列里每个 action chunk 独立采 flow-matching 噪声 $\tau_t=s(1-u),\ u\sim\mathrm{Beta}(1.5,1),\ s=0.999$，避免整条序列同难同易）+ **TBPTT**（按段截断梯度、fast weights 跨段 carry，显存只由段长决定，因此训练上下文可任意加长）。
- 长上下文条件化的关键开关：对选定 timestep **屏蔽 flow-matching 损失**，这些步就只更新 fast weights、不提供模仿目标。据此得到两种用法——(a) 把人类视频与同配置机器人轨迹拼成一条训练序列，视频段只更新 fast weights；(b) **DAgger Distillation**：整条含失败的 rollout 都更新 fast weights，但损失只算在人类纠正段，把"失败→纠正"的映射蒸馏进 fast weights。
- 平台与算力：YAM 双臂桌面机器人 + 4 路 RealSense D405（顶/底/左右腕）480p，30 Hz 控制，RTX 5090 推理；预训练 16×GB200、30K steps 且只训新增的 TTT/GDN 层，下游每任务 post-train 20K steps @1K context 全参数微调。

## 证据

- 三个真机装配任务（Pup Go Car 2 min、Circuit 1 min、Gear Bot 5 min / 十阶段）平均任务完成分 79%，比单步上下文 GR00T N1.7（42%）高 87%，比最强基线 GDN（56%）高 41%；Gear Bot 上 2/10 完全成功，所有基线均为 0。
- 上下文 scaling（128→8K）：8K 达 71.5%，比同模型 1K 预训练（43.9%）高 63%，比最好的短上下文基线（45.6%）高 57%，且未见饱和；GDN 完全没有这个趋势。1K 以下反而变弱，作者归因于 rollout 时长超过训练上下文、位置编码外推。
- 一次性 in-context 模仿（Circuit 未见配置，prompt 统一为 "assemble circuit"）：RoboTTT 65% / 6 of 10 成功，GDN 33% / 0 of 10。
- 外部扰动恢复：拆屋顶 15/20（GDN 13/20、GR00T 10/20、Hist. 3/20），拆轮胎 18/20（GDN 也 18/20）；作者只用 30 分钟扰动数据共训。
- DAgger Distillation：同一批 100 条 DAgger 轨迹下，标准 DAgger 平均提升 9%（两个序列模型上 13%），DAgger Distillation 平均提升 33%（RoboTTT 36%、GDN 29%）；把 suboptimal 机器人动作当模仿目标毫无价值（GR00T 全轨迹微调 57%，与只用纠正段持平），它们的价值只在"作为上下文"。
- 消融：去掉 sequence action forcing 后动作明显失准、几乎无法推进任务；fast model 换成线性层比 MLP 差 27%；从 state tokens 起步，加 action tokens +23%、再加 register tokens +18%，而同样的 register tokens 加到 GR00T N1.7 上没有收益。

## 局限

- 训练成本随上下文长度上升，作者自陈需要 TNT 一类更高效的 chunkwise TTT 训练方法。
- TTT 的 inner objective 仍是通用的 MSE 关联记忆，没有面向机器人的自监督目标（作者把这留给未来工作）。
- 全部结论来自单一 YAM 双臂平台和三个装配任务，每个条件仅 10–20 trials，成功率类指标的统计噪声不小；没有跨本体、跨场景验证。
- 8K 是能力展示而非最优点：低于 1K 时长上下文反而不如短上下文基线，说明该方法对"训练上下文 ≥ 任务时长"有硬性依赖。
- 方法不解决所有部署失败模式，作者指出下一步应与 RL 结合直接优化任务成功率。
- 数字口径要注意：摘要写"比 1K 预训练高 62%"，Introduction 与 Sec. 4 写 63%（71.5 vs 43.9）。引用时以正文为准。

## 我的阅读笔记

RoboTTT 真正改变的是"历史存在哪里"这个问题的答案。外部 memory bank（关键帧、语言摘要、检索）把历史放在模型之外，Transformer 把历史放在 KV cache 里、推理成本随时间线性增长，RNN 把历史压进定长向量、表达力不足。RoboTTT 把历史放进**参数空间**：fast weights 是一个每步做一次梯度下降的小 MLP，既是定长状态（推理成本恒定），又比向量状态更有容量，而且"要记住什么"是被外层任务损失 meta-learn 出来的，不用手工指定观测窗口。GDN 对照组很关键——同样是定长状态，只是把"测试时梯度下降"换成线性 delta rule，长上下文的收益就基本消失了，说明收益来自 update rule 的表达力而非"有记忆"本身。

DAgger Distillation 是我认为最值得迁移的一条：它把 [[@xiao2026rove]]、[[@deng2026e2hil]]、[[@intelligence2025pi06-vla-that-learns]] 这一路"如何用人类接管数据"的问题换了一个解法——ROVE/RECAP 用 value 或 advantage 决定**哪些动作值得模仿**，RoboTTT 干脆不把失败动作当模仿目标，而是把它们留作**上下文**，让模型学"看到这种失败之后该出什么纠正"。两者可以叠加：用 OVE/STEAM 式的 advantage 决定纠正段的权重，再用 fast weights 承载失败→纠正映射。与 [[@pan2026vla-corrector-lightweight-detect]] 的对照也很直接：后者外挂一个检测-纠正模块，RoboTTT 则把纠错内化进策略自身的测试时更新。

还需要继续追问的是：(1) fast weights 的容量上限在哪，8K 之后是否会出现"记忆冲突"；(2) 长上下文与 [[@zhou2026holoagent0]] 式显式空间记忆是互补还是替代；(3) 这套 TTT 层能否直接挂到别的 backbone（作者声称 plug-and-play 但只验证了 GR00T N1.7）。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
