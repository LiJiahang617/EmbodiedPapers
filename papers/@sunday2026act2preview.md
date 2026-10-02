---
tags:
  - paper
status: unread
aliases:
  - ACT-2
  - "ACT-2 Preview: Generalizing Reliability"
  - "ACT-2 可靠性泛化"
year: 2026
title: "ACT-2 Preview: Generalizing Reliability"
doi:
arxiv:
url: "https://www.sunday.ai/blog/act-2-preview"
venue: "Sunday Robotics 官方博客（非同行评审文章）"
venue_short: "Blog"
pdf_url:
openalex:
metadata_source: "Sunday Robotics 官方博客正文与文章末尾 BibTeX"
metadata_confidence: medium
pdf: "[[papers/pdfs/sunday2026act2preview.pdf]]"
reading: "[[papers/bilingual/sunday2026act2preview_中英混读.md]]"
images: "papers/images/sunday2026act2preview/"
image_index: "[[papers/images/sunday2026act2preview/index.md]]"
map_axis: "具身智能/家庭机器人/跨环境可靠性与 Solve"
map_brief: "ACT-2 用规模化高质量人类预训练缩小 in-domain 与 out-of-domain gap，再用单示范 SFT 迭代可靠性，报告 785 次家庭洗衣折叠尝试的 99.1% 成功率。"
map_role: "把家庭机器人结果按 performance、scope、adaptation cost 三个维度写清楚的公司自报案例，适合与 VLA 规模化和长尾泛化工作对照。"
authors:
  - "[[Sunday Robotics]]"
institutions:
  - "[[Sunday Robotics]]"
topics:
  - home robotics
  - mobile manipulation
  - generalization gap
  - pretraining scale
  - one-shot fine-tuning
  - laundry folding
  - long-tail reliability
  - Solve
---

# ACT-2 Preview: Generalizing Reliability

- [x] 本地快照 PDF:: [[papers/pdfs/sunday2026act2preview.pdf]]
- [x] 元数据:: source=Sunday Robotics 官方博客与 BibTeX, confidence=medium
- [x] 精读稿:: [[papers/bilingual/sunday2026act2preview_中英混读.md]]
- [x] 图片索引:: [[papers/images/sunday2026act2preview/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[home robotics]] · [[mobile manipulation]] · [[@intelligence2025pi06-vla-that-learns]] · [[@intelligence2026pi07-steerable-generalist-robotic]] · [[@generalist2026gen15]] · [[@dexmal2026dm05]] · [[@qwen2026robotmanip]]
affiliation:: [[Sunday Robotics]]

> [!warning] 来源与可信度
> 这是 Sunday Robotics 在官网发布的产品技术博客，不是同行评议论文。文章没有公开模型参数、完整预训练数据规模、后训练循环细节、失败样本和权重。本文档保留作者给出的 785 次 autonomous attempts、778 次 completed folds 两个分母，不能把它们混成同一组样本。
>
> `papers/pdfs/sunday2026act2preview.pdf` 是网页正文文本快照，不是官方排版 PDF。静态图片下载命令位于 [[papers/images/sunday2026act2preview/index.md]]。

## Abstract（博客自述要点，非正式摘要）

ACT-2 是 Sunday Robotics 面向家庭洗衣折叠的移动操作模型。文章的核心配方是高质量、高多样性的 sensorized human pretraining，加上快速的 in-house post-training loop。作者先测量预训练规模如何缩小 in-domain 与 out-of-domain success gap，再展示单个 folding demonstration 可以教会四个独立模型新的 folding technique，最后把这种迁移能力用于持续修复长尾失败。旗舰模型在 9 类衣物、不同房间、床面、光照、起始状态和机器人位置上进行 785 次 autonomous attempts，成功率 99.1% ±0.3% standard error。778 次完成折叠的平均质量是 4.72/5，median completion time 是 2.22 分钟。

## 一句话定位

ACT-2 不是只展示一次漂亮的折衣演示，而是把机器人结果写成 performance、scope、adaptation cost 三个同时声明的 Solve，试图证明预训练规模能让少量本地后训练收益传到陌生家庭；99.1% 是这个边界内的公司自报结果，不是家庭通用机器人的普遍保证。

## 方法 / 对象

- 预训练数据来自 Sunday 的 proprietary data collection hardware、curation system 和 processing pipeline，文章强调质量与多样性同时扩展，但没有给出完整小时数和模型规模。
- 预训练与 post-training 分工明确。预训练负责让行为在陌生环境保持可迁移，后训练用 in-house failures 和 recoveries 做 hill-climbing。
- 单示范实验复制同一个 pretrained checkpoint 四份，每份只接收一个 folding technique 的 demonstration，再在未见过的 garment 上评估。
- 评估对象是 Memo 移动机器人。它可以左右移动、调整高度并向工作区倾身，支持床面两侧和床尾位置。
- Solve 的 adaptation cost 是每个家庭零数据、零专家示范、零 post-training，所有评估使用同一 checkpoint 和系统配置。

## 证据

### 预训练规模与泛化间隔

作者把 post-training 后的 in-domain success 与 held-out out-of-domain success 之差定义为 generalization gap。每个规模使用同一套 post-training procedure，并在两种分布上各做 50 次评估。

| Pretrain data scale | In-domain SR | Out-of-domain SR | Gap |
| ---: | ---: | ---: | ---: |
| 0% | 96% | 14% | 82 |
| 12% | 100% | 90% | 10 |
| 25% | 100% | 92% | 8 |
| 50% | 100% | 96% | 4 |
| 100% | 100% | 100% | 0 |

这组曲线把「本地数据能否转化为野外可靠性」变成可测的差值。0% 预训练时本地 96% 与陌生环境 14% 相差 82 个点，完整预训练后差值归零。作者还比较 high-quality subsampling 与 uniform subsampling，在相同数据量和 compute 下，质量筛选的验证损失更低，下游成功率也更高。

| 采样方式 | 数据比例 | Success rate | Validation loss |
| --- | ---: | ---: | ---: |
| High-quality | 12.5% | 75.6% | 0.0700 |
| High-quality | 25% | 87.9% | 0.0682 |
| High-quality | 50% | 92.3% | 0.0668 |
| Uniform | 12.5% | 43.8% | 0.0738 |
| Uniform | 25% | 53.6% | 0.0713 |
| Uniform | 50% | 64.1% | 0.0682 |

### 单个示范的可迁移行为

四个独立模型副本分别看到一个新的 folding technique，每个模型都在 held-out garment 上执行成功。文章没有给出每种 technique 的试次数、成功率或具体衣物清单，所以这项证据支持「单示范能传递行为」这一存在性判断，不能支持稳定概率估计。

### 家庭场景的 Solve 边界

| 维度 | 宣布的 scope | adaptation cost |
| --- | --- | --- |
| Garments | T-shirts、厚薄长袖、polos、无袖上衣、blouses、pants、leggings、shorts，尺寸 XXS 到 8XL，覆盖颜色、材料、厚度和纹理 | 每个家庭零数据，无目标家庭示范，无 post-training |
| Scenes | 未见过的房间、床和折叠表面，变化的光照，床左侧、右侧和床尾 | 同一 checkpoint 与系统配置 |
| Initial configurations | 篮子、床上堆叠、床面散放、地面衣物，方向任意且自然褶皱 | 不要求整理成标准初始姿态 |

### 成功率与分母

文章把一次成功定义为衣物被机器人自主折叠并堆放。785 次 autonomous attempts 的整体成功率是 99.1% ±0.3% standard error。按衣物类别，shorts、厚薄长袖、polos、无袖上衣都是 100%，blouses 最低，为 94.7%，但 blouse 只有 19 次尝试。

| 类别 | Success | Attempts |
| --- | ---: | ---: |
| Overall | 99.1% | 785 |
| T-shirts | 99.0% | 312 |
| Pants | 98.8% | 85 |
| Leggings | 96.3% | 54 |
| Blouses | 94.7% | 19 |

这里必须把 785 与 778 分开。785 是所有 autonomous attempts 的成功率分母，778 是完成折叠后进入质量和速度统计的样本数。

### 折叠质量

每次 completed fold 从五颗星开始，若出现 overfold、misalignment、unfolded element、stacking error，每类扣一颗星，阈值是多出或错位超过两英寸，堆叠越界超过衣物宽度的三分之一也算问题。

778 次完成折叠的平均分为 4.72/5，98.3% 达到四星或五星，73.8% 得到五星。按衣物类别，leggings 平均 4.88，polos 平均 4.63，blouses 平均 4.61。小样本类别的均值不宜和 T-shirts 的 309 次样本直接等权比较。

### 速度

计时从 Memo 开始取衣物，到把折好的衣物放入堆叠结束，包含自主重试与恢复。778 次成功折叠的 median 是 2.22 分钟，mean 是 2.32 分钟。shorts 最快，median 1.23 分钟，薄长袖最慢，median 2.73 分钟。

### 涌现行为

作者展示了三类没有逐条写进任务脚本的行为。衣物掉到地面或严重褶皱时，模型会取回、重定向并继续折叠。人类干扰或视觉条件改变时，模型会重规划而不是执行固定动作序列。面对婴儿衣物、8XL 衬衫和大毛巾时，Memo 会移动身体、调高度和倾身，扩展固定桌面之外的操作范围。

## 原文结构与论证推进

### ACT-2’s Recipe for Generalizing Reliability

开篇把可靠性放到能力演示之后。文章并不把「能做一次」当成终点，而是要求说明本地迭代的收益是否能传到陌生家庭。后面的三段实验分别对应 gap、单示范迁移和 post-training hill-climbing。

关键证据是 Figure 1 到 Figure 4。它们把预训练规模、数据质量、验证损失和真实成功率连在一起，但没有披露 pretraining hours、参数量或训练预算，因此曲线更像产品研发内部的缩放诊断。

### Home Robotics as a Test of General Intelligence

家庭被当作长尾评测场景。衣物会变形、自遮挡、改变起始姿态，床面和光照也无法完全控制。作者用 laundry folding 作为第一个 Solve，并用 scope 与 adaptation cost 限定 99.1% 的解释范围。

### Performance

这一节把成功、质量和速度拆开。成功率回答是否折好并堆放，星级回答折痕与堆叠质量，完成时间回答使用成本。三个指标必须与 scope 一起读，单独的 99.1% 不足以比较两个机器人系统。

### Solve: A New Standard for Robotics Progress

Solve 的三个字段是 Performance、Scope 和 Adaptation cost。文章认为 demo 若不报告环境、对象、起始状态和介入规则，就很难比较。这个框架的价值在于把「效果好」改写成带边界的声明，代价是每项结果都需要更完整的评测协议。

### Toward General-Purpose Robotics

Sunday 说同一 base model 还在学习吸尘、整理玩具、拉拉链、翻面裤子和冲咖啡。这些能力尚未按 Solve 标准评估，文章只把它们当作共享模型的方向性展示。每个 Solve 累积的数据和恢复策略会反哺其他家庭任务，这是公司对 fleet learning 的长期假设。

### Taking ACT-2 Into the Home

结尾把模型从演示推向 Beta Program。这个产品承诺尚未由公开的家庭部署统计支持，因此应和前面的 785 次受控记录分开阅读。

## 方法细节

ACT-2 的公开方法细节集中在数据与迭代闭环。预训练使用 sensorized human dataset，并强调 quality、diversity 和 curation。后训练从自家 Memo 的真实失败中选样，再用少量 SFT 更新模型。预训练规模越大，作者观察到单个本地示范越可能在陌生衣物上复用，于是每轮本地修复可以用更少样本。

文章没有给出网络结构、action parameterization、控制频率、视觉输入数量、损失函数或优化器。复现层面只能重建评测定义，不能重建模型。

## 实验设置、数据集、基线、指标

预训练缩放实验在五个数据比例上运行，in-domain 与 out-of-domain 各 50 次评估。单示范实验使用四个独立模型副本和四种 folding technique。主结果覆盖 9 类衣物、785 次 autonomous attempts，成功折叠后的 778 次用于质量和速度。

环境维度包含房间、床面、床单颜色、机器人位置、衣物起始配置、尺寸和材质。对比基线不是另一种模型，而是不同 pretraining scale 和 high-quality 与 uniform subsampling。作者没有公开跨公司 baseline，也没有报告完整失败分类。

指标包括 success rate、generalization gap、validation loss、五星 fold quality 和 completion time。成功率误差带使用 standard error，文章说明图中还使用 Wilson intervals。质量评分是离散星级，速度同时报告 median、mean、分位数。

## 主要结果、消融或对比

预训练从 0% 增至 100% 时，out-of-domain success 从 14% 升到 100%，gap 从 82 降到 0。相同规模下 high-quality subsampling 明显优于 uniform subsampling，例如 50% 数据时成功率 92.3% 对 64.1%。

旗舰模型的 99.1% 来自 785 次尝试，778 次完成折叠的质量均值 4.72，98.3% 达到四星或五星，median 时间 2.22 分钟。blouse 是最低成功率类别，但只有 19 次。

单示范实验的四个模型都在 held-out garment 上执行了新 technique。该结果支持 transferability 的存在，不足以估计不同示范和衣物组合的成功分布。

## 图表、公式与表格线索

| 编号 | 内容 | 支撑哪条主张 | 阅读边界 |
| --- | --- | --- | --- |
| Figure 1 | 五个预训练比例的 in-domain 与 out-of-domain success | 规模缩小 generalization gap | 每个成功率背后只有 50 次评估 |
| Figures 2–4 | 成功率、validation loss 和二者相关性 | 数据质量提升效率 | high-quality 与 uniform 的构造细节未公开 |
| Figure 5 | 按衣物类型的成功率 | 长尾衣物覆盖 | blouse 只有 19 次 |
| Figure 6 | 起始配置、机器人位置、床单颜色 | 环境变化下的稳定性 | 床单颜色分组有重叠 |
| Figure 7 | 五星质量构成 | 折痕和堆叠质量 | 质量分母是 778，不是 785 |
| Figure 8 | 成功折叠的时间分布 | 使用成本 | 只统计成功完成的折叠 |
| Emergent Behavior panels | 地面取衣、干扰恢复、超大衣物 | 长尾恢复与移动身体适应 | 多为视频案例，没有逐类分母 |

文章没有公开数学公式。最接近公式的是 gap = in-domain success − out-of-domain success，实际计算使用百分数差值。

## 主张-证据-边界矩阵

| 主张 | 证据 | 边界 |
| --- | --- | --- |
| 预训练规模能缩小泛化间隔 | gap 82 → 0，out-of-domain 14% → 100% | 规模以相对比例报告，绝对数据量和模型量未知 |
| 高质量数据比均匀抽样更有效 | 50% 数据时 92.3% 对 64.1% | 数据质量标签和筛选流程未公开 |
| 单个示范可以教会新 folding technique | 四个独立副本都通过 held-out garment | 没有试次数、失败率和示范细节 |
| ACT-2 在声明范围内达到高成功率 | 785 次尝试，99.1% ±0.3% | 公司自报，家庭分布与采样程序无法外部审计 |
| 折叠质量和速度可接受 | 778 次均值 4.72/5，median 2.22 分钟 | 质量与速度只对成功折叠统计 |
| 同一 recipe 可扩展到更多家务 | 展示吸尘、整理、拉链、咖啡等方向 | 尚未按 Solve 标准评测 |

## 局限与可追问点

这是一篇产品技术博客，不是可复现实验报告。最关键的缺口是完整 pretraining data scale、模型参数、训练 compute、数据过滤规则、post-training 轮次和每个失败案例的公开程度。没有这些信息，gap 曲线无法和其他系统做公平比较。

785 次 attempts 与 778 次 completed folds 的分母不同。若把 778 当作成功率分母，会高估统计样本的独立性。质量和速度还排除了失败折叠，不能回答一次任务从拿衣物到最终堆放的总体耗时。

blouse 的 94.7% 来自 19 次尝试，sleeveless tops 的 100% 也只有 7 次。类别间样本量差异很大，不能把每个百分比视为同等精度。文章给了标准误和区间，却没有逐类完整的失败原因。

单示范实验只有四个模型副本。四次成功足以展示能力存在，不能证明对新衣物、新房间和新示范风格的普遍成功率。预训练规模和 post-training 的关系也可能混入数据质量、机器人硬件和模型选择的共同变化。

## 与当前库的连接

与 [[@generalist2026gen15]] 放在一起看，两篇都把预训练规模转化为低 adaptation cost。GEN-1.5 以 3 到 12 秒 physical prompt 和 1 步适配为核心，ACT-2 则把单示范放进家庭长尾与可靠性评测。前者展示能力接口，后者尝试把 scope 与分母写清楚。

与 [[@intelligence2025pi06-steerable-generalist-robotic]] 对照时，重点看 post-training 的数据闭环。π 系列强调经验数据和持续学习，ACT-2 强调在本地失败上 hill-climb 后收益能否跨房间传递。与 [[@qwen2026robotmanip]] 对照时，重点看数据混合和跨本体对齐是否公开到足以复现。

与 [[@dexmal2026dm05]] 一起读，可以比较开放世界声明与真实长尾统计的差距。ACT-2 的 Solve 框架把 scope 和 adaptation cost 放到结果前面，这种写法适合给其他家庭机器人基准借鉴。

## 精读路线 / 为什么需要回看

第一遍先看 Figure 1 的 gap 曲线和 Solve 三字段。它们决定 99.1% 的解释边界，也能检验本地后训练是否真的传到陌生环境。

第二遍核对 785 与 778 两个分母，再看 Figure 5 到 Figure 8 的类别样本量、质量星级和成功时间。这里最容易把成功率、完成质量和使用速度混为一个指标。

第三遍看单示范实验和 high-quality subsampling。要判断模型是否适合家庭部署，还需要追问示范风格、失败恢复、模型冻结和每个家庭的真实介入次数。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
