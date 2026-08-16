---
tags:
  - paper
status: unread
aliases:
  - DYNA-2
  - Dyna-2
  - "Dyna-2: A 1-Million-Hour Scaling Law for World-Action Models"
year: 2026
title: "Dyna-2: A 1-Million-Hour Scaling Law for World-Action Models"
doi: 
arxiv: 
url: "https://dyna.co/dyna-2"
venue: "Dyna Robotics 官网技术报告（无 arXiv、无同行评议）"
venue_short: "Tech Report"
pdf_url: 
openalex: 
metadata_source: "官网技术报告正文与官方 BibTeX"
metadata_confidence: high
pdf: "[[papers/pdfs/dyna2026dyna2.pdf]]"
reading: "[[papers/bilingual/dyna2026dyna2_中英混读.md]]"
images: "papers/images/dyna2026dyna2/"
image_index: "[[papers/images/dyna2026dyna2/index.md]]"
map_axis: "世界模型/WAM/人类视频规模化与缩放律"
map_brief: "在 100 万小时第一人称人类视频上预训练 world-action model，证明人类数据缩放律、首次证明跨本体迁移缩放律，并用控制实验说明视频预测目标才是跨本体迁移出现的原因。"
map_role: "判断「人类视频 vs 遥操数据」这条路线分歧的关键证据来源，也是 WAM 部署延迟问题的一个架构解法参考。"
authors:
  - "[[Dyna Robotics]]"
institutions:
  - "[[Dyna Robotics]]"
topics:
  - world-action model
  - scaling law
  - cross-embodiment transfer
  - human egocentric video
  - pseudo-action
  - video co-training
  - flow matching
  - one-step distillation
  - dexterous manipulation
---

# Dyna-2: A 1-Million-Hour Scaling Law for World-Action Models

- [x] 本地快照 PDF:: [[papers/pdfs/dyna2026dyna2.pdf]]
- [x] 元数据:: source=官网技术报告, confidence=high
- [x] 精读稿:: [[papers/bilingual/dyna2026dyna2_中英混读.md]]
- [x] 图片索引:: [[papers/images/dyna2026dyna2/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[world-action model]], [[scaling law]], [[human video]], [[@feng2026wam-ttt]], [[@peng2026fact]], [[@gao2026fast-leworldmodel]], [[@qian2026wam-rl]], [[@xue2026worldsample]], [[@paliwal2026do-i-dexterous-manipulation]], [[@huang2026rynnvalue]], [[@intelligence2026pi07-steerable-generalist-robotic]]
affiliation:: [[Dyna Robotics]]

> [!warning] 来源与可信度
> 这不是论文，是 Dyna Robotics 发在自家官网的技术报告（2026 年 8 月，https://dyna.co/dyna-2 ）。没有 arXiv 版本、没有同行评议、不开源权重代码数据、语料构成与客户现场细节均未披露。所有数字都是作者自报，引用时要标明来源性质。
>
> 库里的 `papers/pdfs/dyna2026dyna2.pdf` 是网页正文的**本地文本快照**，不是官方排版 PDF。缩放律曲线和架构图都是页面内渲染的交互式图表，无法下载，需要对照原网页看。
>
> `rehydrate_images.py` 按 `arxiv` 字段工作，本篇没有 arXiv 号，换机器后需按 [[papers/images/dyna2026dyna2/index.md]] 里的命令手动补图。

## Abstract（报告要点，非原文摘要）

Dyna-2 is a world-action model pre-trained on more than one million hours of egocentric human video (roughly 170 years of continuous waking experience). The report establishes three findings: (i) a scaling law for world-action models exists up to one million hours of human data; (ii) for the first time, a human-to-robot transfer scaling law exists, i.e. more human data in pre-training improves offline prediction on robot data the model has never seen; (iii) both data and objective matter, and world modeling plus scaling on video data are essential for cross-embodiment scaling transfer to emerge. Beyond the offline results, the scaling trend carries through post-training to on-robot performance: with only a few hours of robot data and no robot data in pre-training, post-trained Dyna-2 models perform tasks across bimanual parallel-jaw arms, semi-humanoid and dexterous-hand platforms.

## 一句话定位

机器人基础模型的预训练数据源该选什么，这份报告用 100 万小时第一人称人类视频给出了一条可验证的路线论证，它证明人类数据上存在缩放律、这条律零样本地体现在从未见过的机器人数据上，并用控制实验指出视频预测目标（而非动作监督）才是跨本体迁移得以出现的原因。

## 方法 / 对象

- 架构：world-action model，单模型联合或分别去噪未来视频与未来动作，建在视频扩散骨干上。混合 Transformer，视频与动作各自 token 化并各有一套 DiT 层，本体感受直接进动作 Transformer。
- 注意力格局：视频 token 因果掩码并跨注意文本；动作 token 双向自注意力（无因果掩码），注意已观测上下文的视频 token，文本不直接影响动作 token。
- 浅动作分支：早期探索发现 DiT 视频扩散的时间推理能力大多在浅层，因此动作 Transformer 刻意做浅并只在浅层接入视频流，大幅改善实时推理延迟而不牺牲性能。
- 目标：flow matching。$z_t=tz+(1-t)\varepsilon_z$，$a_t=ta+(1-t)\varepsilon_a$，共训损失 $\mathcal{L}_{co}=\mathbb{E}\|u^{vid}_\theta(z_t;t,c)-(z-\varepsilon_z)\|^2+\lambda\mathbb{E}\|u^{act}_\theta(a_t;t,c)-(a-\varepsilon_a)\|^2$。
- **关键部署性质**：$u^{act}_\theta$ 从不把 $z_t$ 当参数，所以视频损失能塑造共享表示，但推理时策略保持反应式，既不生成也不注意预测视频。
- 数据：100 万+ 小时头戴第一人称人类操作视频。通过手部姿态质量门槛的片段带 3D 手部姿态轨迹，由此导出伪动作监督（腕部位姿给末端轨迹、拇指食指开合给连续抓握信号）。**刻意不做任何缩小视觉或运动学差距的处理**。
- 数据阶梯：恰好 1k / 10k / 100k / 1M 小时的嵌套子集，各源等比例，大预算只加不换；另留 100 小时不相交验证集；训练与评测配置全一致，唯一变量是小时数。计算量与模型规模缩放明确留给未来。
- 指标：MSE、L1（连续）加 accuracy@0.5、accuracy@0.1（离散阈值），四个同报以防指标造成的假涌现。后期窗口取 10 个检查点报均值与标准差。

## 证据

- **人类数据缩放律**：MSE $=0.0691\cdot D^{-0.0184}$（$R^2$ 0.919）、L1 $=0.151\cdot D^{-0.0132}$、acc@0.1 $=0.0116\cdot D^{+0.0606}$、acc@0.5 $=0.357\cdot D^{+0.0203}$（$R^2$ 0.865）。跨整个阶梯 acc@0.1 涨 51%，MSE 只改善 12%。
- **人到机器人迁移**：留出机器人集 39 任务（两个固定式双臂 YAM 平台，12 内部 + 27 来自外部 xdof ABC，无任何轨迹进过训练）。零样本 MSE $=0.306\cdot D^{-0.0713}$（$R^2$ 0.884），acc@0.5 $=0.0241\cdot D^{+0.139}$（$R^2$ 0.918）。拐点在 10k 到 100k 小时之间。
- **真机后训练**：14 任务、三本体（YAM 双臂平行夹爪 11、WUJI-2 二十自由度灵巧手 2、半人形原型 1），每任务最多 10 小时机器人数据，只用机器人数据、不做人机对齐或共训，每任务 10 次盲测试验（语言任务 12 次）。归一化均值 20% → 28% → 45% → 53%，1M 档在 9/14 任务上最好。
- 阈值行为：Lockbox Key Turning 在 1k/10k/100k 全是 0%，1M 时 90%。数据效率：Bottle Cap Untwisting 只用约 10 分钟机器人示范，10%/10%/40%/50%。语言：Targeted Drink Retrieval 58%→75%→83%→83%。
- **世界建模的必要性**：三路对照（action-only / joint / video co-train）在 5k、50k、100k 动作小时上评测，joint 在 39/39 任务上每个规模都胜过 action-only。action-only 随数据扩展严重且不可预测地过拟合，joint 过拟合较少但不随数据扩展，只有视频协同训练随动作数据增长而改善。
- **视频缩放轴**：动作固定 50k 小时，视频专用 0/1k/10k/50k → 零样本机器人 MSE 0.34 → 0.12；动作固定 250k，视频专用 0/250k/750k → 0.10 → 0.084。同批检查点在人类侧相对改进 104%（几乎不变），机器人侧 34%。
- **WAM vs VLA**：早期 Dyna-2 对 Dyna-1（VLA，从 Qwen3-VL-4B 初始化），匹配数据与超参，各 3 个预训练检查点。7 任务 × 3 检查点共 21 格汇总，成功率 1.55×、评分 1.12×；对局 WAM 赢 65%、VLA 赢 29%、6% 平。作者自称这是 WAM 的下界。
- **零样本落地**：客户现场生产验收通过率 Dyna-1 46% 对 Dyna-2 87%（相同后训练预算），内部评测两者均接近 100%。
- **指令跟随**（四个反事实基准）：action-only 早期语料 0.35 → video co-train 早期语料 0.67 → video co-train 完整语料 0.96。物体分拣从 0.10 到 0.95 是最大跃升。
- **单步蒸馏**：H100 上三秒三视角视频从 10,203 ms 降到 110 ms（约 93×）。FVD 121（教师 80，DMD2 单步 599，教师砍到一步 1039），闪烁 1.94（真实录制 2.37），运动完整度 75%（真实 100%）。

## 局限

- **幂指数极小，需要自己算一遍。** MSE 指数 $-0.0184$ 意味着数据翻一千倍只换来 12% 的误差改善（报告如实写了这个数，但叙事重心全在「缩放律成立」上）。缩放律成立和缩放律有用是两回事，这条律很平，更像是在证明这条路没有天花板。
- **证据链断在中间。** Q2 那条最重要的迁移缩放律衡量的是离线动作预测 MSE 和 acc@τ，是行为克隆意义上的拟合度而非任务成功率，且 acc@0.5 绝对值最高只有 0.19 左右。Q3 的真机实验指标对了，但只有 14 任务、每任务 10 试次，统计强度不足。有统计强度的用的是代理指标，用对指标的没有统计强度。
- **单项非单调被均值掩盖。** Rope Tie 在 100k 拿 90% 而在 1M 掉到 40%，Food Scooping 从 80% 掉到 50%，Unsort 在最小预算下最好。10 试次下这些大概率是噪声，但正因如此那条 20/28/45/53 的均值曲线也该有很宽的置信区间，报告没给。报告把均值放最显眼处而把单项藏在滑块里。
- **不可复现。** 不开权重代码数据，无 arXiv 无同行评议。语料构成（合作方、各源占比）未披露，网页上的片段数/指令数/物体数是动画计数器。客户现场的站点、任务、验收标准均未披露。
- **WAM vs VLA 两头站不住。** 作者自述对 WAM 不公平因而是下界，这诚实；但 Dyna-1 也是自家模型，外部无法判断它相对 π0、GR00T N1 处在什么水平。1.55× 只能读作团队内部的架构选择依据。
- **指令跟随实验两个变量同时变。** 0.35→0.67 是换目标，0.67→0.96 同时换了数据量和多样性，报告没拆开。
- **计算与模型规模缩放明确留给未来。** 数据缩放律在固定模型规模下测得，回答不了「一百万小时配多大模型」。
- 单步蒸馏的运动完整度只有真实的 75%，作者也说尚不及完整教师。

## 我的阅读笔记

这份报告最扎实的不是那条头号缩放律，是 Q4 那一节的两个控制实验。

一个是三路对照的 39 比 0。固定动作数据量，joint（同时预测动作和未来视频）在 39 个机器人任务上每个规模都完胜 action-only。世界建模对跨本体迁移的必要性，这一条对照比任何理论论证都硬。

另一个是 Figure 12 的分离。固定动作数据只扩视频，人类侧的相对改进是 104%（几乎不动甚至略差），机器人侧是 34%（MSE 降到三分之一）。视频协同训练的收益不是泛泛的表示改善，它精准地只作用在跨本体泛化上。这个「同域不涨、跨域大涨」的对照设计得非常漂亮。

架构上最值得记的是共训损失里 $u^{act}_\theta$ 不吃 $z_t$ 这一行，加上刻意做浅的动作分支。两件事合起来把「世界模型太慢所以不能部署」这个 WAM 路线最大的质疑处理掉了，训练时做世界建模、推理时完全反应式。这跟 [[@gao2026fast-leworldmodel]] 追问的问题是同一个，Dyna-2 给的答案是不需要测试时想象。

实验设计层面，嵌套子集（大预算只加不换）、固定 100 小时验证集、四指标并报、后期窗口取 10 个检查点，这套做法把缩放律主张常见的几种质疑逐条堵住了。写缩放律实验可以直接抄这个模板。

必须自己算一遍的是幂指数。$D^{-0.0184}$ 千倍换 12%。报告没有藏这个数字，但整体叙事会让人高估。从 100 万小时走到 10 亿小时，再拿 12%。这条律是真的，但它很平，它证明的是没有天花板而不是很快能到。

跟 [[@feng2026wam-ttt]] 的表面矛盾值得单独想清楚。WAM-TTT 的附录 E.6 用数字说重定向伪动作是净负收益（四任务掉 43.4 点），Dyna-2 却靠单目手部姿态导出的伪动作训了 100 万小时。细看是兼容的，WAM-TTT 失败的是把 MANO 姿态重定向到目标本体的关节配置，Dyna-2 恰恰刻意不做本体特定处理，保留的是腕部位姿加开合这种粗粒度、本体无关的动作空间。而且 Dyna-2 的 Figure 10 也显示 action-only 会严重过拟合，扛住扩展的是视频协同训练。两篇合起来的结论一致，单目手部信号太噪不足以单独承载动作学习，用粗一点、别硬往机器人关节上映射、让视频预测承担主要表示学习，才是可行配方。

读这份报告要一直记着它是公司自报、不可复现。结论方向我信，具体数字建议当作上界看待。

## 摘录

> The right source of pre-training data, therefore, ought to be sensorized recording (e.g., video) of humans performing those very tasks, which already exists at effectively unbounded scale.

> Because u_θ^act never takes z_t as an argument, the video loss can shape the shared representation, but at inference time the model stays reactive.

> This way, a larger budget never exchanges data, only adds it, and differences between points on the scaling-law curves cannot be explained by distribution shift between subsets.

> the joint recipe beats action-only on 39 of 39 tasks at every action scale.

> video co-training is the primary driver for establishing cross-embodiment transfer scaling law.

> One million hours is not the end of the scaling axis; it's only the beginning of a new era of scaling for robotics.

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
