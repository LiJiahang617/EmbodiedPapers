---
tags:
  - bilingual-reading
paper: "[[@sunday2026act2preview]]"
source_pdf: "[[papers/pdfs/sunday2026act2preview.pdf]]"
images: "papers/images/sunday2026act2preview/"
image_index: "[[papers/images/sunday2026act2preview/index.md]]"
created: 2026-08-20
---

# ACT-2 Preview: Generalizing Reliability

paper:: [[@sunday2026act2preview]]
pdf:: [[papers/pdfs/sunday2026act2preview.pdf]]
images:: [[papers/images/sunday2026act2preview/index.md]]

> [!warning] 来源说明
> 这是 Sunday Robotics 的官方产品技术博客，不是同行评议论文。文章披露了评测范围、成功率、折叠质量和速度，却没有公开参数量、完整数据小时、模型结构、后训练轮次和失败样本。所有结果都是公司自报。785 次 autonomous attempts 用于成功率，778 次 completed folds 用于质量和速度，两个分母必须分开。

## 一句话总结

ACT-2 试图把家庭机器人进展写成一个带边界的 Solve。预训练规模先把 in-domain 与 out-of-domain 的 success gap 从 82 个点压到 0，再让单个 folding demonstration 在四个模型副本上教会新 technique。旗舰系统在 9 类衣物和多种陌生家庭条件下报告 785 次尝试、99.1% ±0.3% 成功率，778 次完成折叠的质量均值为 4.72/5。

## 核心词汇速查

| English | 中文 | 在文章中的作用 |
| --- | --- | --- |
| generalization gap | 泛化间隔 | in-domain 与 out-of-domain 成功率之差 |
| in-domain | 域内 | 后训练数据代表的环境分布 |
| out-of-domain | 域外 | held-out 房间、物体和起始配置 |
| pretraining scale | 预训练规模 | 高质量人类传感数据的相对比例 |
| high-quality subsampling | 高质量抽样 | 从预训练池中保留更高价值片段 |
| uniform subsampling | 均匀抽样 | 与高质量抽样对照的数据选择方式 |
| post-training | 后训练 | 用本地失败和恢复样本继续改进策略 |
| Solve | 可声明的可靠能力 | 同时写清 performance、scope、adaptation cost |
| fold quality | 折叠质量 | 五星规则评估对齐、完整、紧凑和堆叠 |
| adaptation cost | 适应成本 | 新家庭所需数据、示范、微调或人工介入 |
| long tail | 长尾 | 家庭中难以预先穷举的物体和状态 |
| hill-climbing | 迭代爬坡 | 从真实失败中快速修复可靠性 |

## 摘要

文章从「演示成功」和「可靠服务」的差别切入。ACT-2 的中心假设是，强而多样的 sensorized human pretraining 能让本地 post-training 的收益跨到陌生家庭，而不是只在收集数据的房间里变好。作者把这个假设拆成三个观察，规模越大泛化间隔越小，单个示范能教会新行为，失败闭环能持续爬升可靠性。

预训练比例从 0% 到 100% 时，in-domain success 从 96% 到 100%，out-of-domain success 从 14% 到 100%，gap 从 82 降到 0。相同数据量下，high-quality subsampling 在 50% 比例达到 92.3%，uniform subsampling 只有 64.1%。旗舰模型覆盖 9 类常见衣物、XXS 到 8XL 尺寸、不同材质颜色、床面与房间变化，785 次尝试的整体成功率是 99.1% ±0.3%。

说到点子上了，文章并没有把 99.1% 当成脱离条件的能力数字，而是用 Solve 要求同时声明 performance、scope 和 adaptation cost。这个写法提高了结果的可读性，但数据和模型细节仍不足以让外部团队复现。

## 论文主线

![[papers/images/sunday2026act2preview/act2-cover.png|700]]

文章先用飞行史的比喻区分「证明可能」和「成为日常服务」。机器人演示可以让人相信某个动作能做，家庭部署还要求动作在房间、床面、衣物和扰动变化下持续可靠。ACT-2 的研究问题因此不是单纯追求一条最高成功率，而是如何把本地迭代变成跨环境的可靠性提升。

作者的机制链条可以压缩成一条闭环。高质量多样预训练提供 broad prior，小量本地 SFT 修补边缘失败，缩小的 generalization gap 让本地 success 更能预测陌生环境，随后 fleet 中的新失败又成为下一轮 post-training 数据。家庭洗衣折叠是第一项按 Solve 标准公开的能力。

坦率的讲，最有价值的实验不是 99.1% 本身，而是 0% 预训练时 82 个点的 gap 与完整预训练时 0 个点的 gap。它把「本地微调会不会过拟合」从一句担忧变成了一个可比较的量。不过文章没有公开相对比例对应的绝对小时数，规模效应的外推仍然有限。

## 贡献与结论对照

| 文章声称的贡献 | 证据位置 | 结论强度 |
| --- | --- | --- |
| 预训练规模关闭泛化间隔 | Figure 1，gap 82 → 0 | 中等，绝对数据量与模型规模未知 |
| 数据质量影响预训练效率 | Figures 2–4，高质量抽样优于均匀抽样 | 中等，筛选管线未公开 |
| 一个示范可教会可迁移 folding technique | 四个独立模型均通过 held-out garment | 早期存在性证据，样本仅四个模型 |
| 家庭长尾折叠可靠 | 785 次尝试，99.1% 成功 | 公司自报，类别样本量不均 |
| 质量与速度同时可用 | 778 次均值 4.72/5，median 2.22 分钟 | 只统计成功折叠 |
| Solve 可作为机器人进展标准 | 明确 Performance、Scope、Adaptation cost | 方法论提议，尚未有跨公司基准 |

## 结构地图

| 原文 section | 本文中文理解 | 在论证链中的工作 |
| --- | --- | --- |
| Opening | 从飞行演示到可靠服务 | 提出 reliability 评测问题 |
| ACT-2’s Recipe for Generalizing Reliability | 可靠性泛化配方 | 连接预训练、单示范和后训练 |
| Closing the Generalization Gap by Scaling Pretraining | 用规模缩小泛化间隔 | 给出 0% 到 100% 的五点曲线 |
| Learning Transferable Behaviors from One Example | 单示范学习可迁移行为 | 四个模型、四种 folding technique |
| Hill-Climbing Reliability Through Post-Training | 后训练迭代爬坡 | 解释失败如何回流数据 |
| Home Robotics as a Test of General Intelligence | 家庭作为通用智能试场 | 声明衣物、场景和起始状态范围 |
| Performance | 性能 | 成功、质量和速度的结果入口 |
| Success Across the Long Tail | 长尾成功率 | 785 次尝试与类别分布 |
| Fold Quality | 折叠质量 | 五星规则与 778 次完成折叠 |
| Speed | 速度 | 成功折叠耗时分布 |
| Emergent Behavior | 涌现行为 | 地面恢复、扰动恢复和身体移动 |
| Solve: A New Standard for Robotics Progress | Solve 标准 | 把结果绑定到范围和成本 |
| Toward General-Purpose Robotics | 通用机器人方向 | 展示尚未按 Solve 评测的家务任务 |
| Taking ACT-2 Into the Home | 进入家庭 | 从博客预览连接 Beta Program |

## Opening

开头回顾 Wright brothers 的十二秒飞行，借此说明 demo 证明可能性，却不等于安全、稳定和可日常使用。ACT-2 的叙事位置是从「机器人能做什么」转向「条件变化时还能做得多可靠」。

文章把 central advance 写成两点结合，本地 post-training 能快速 hill-climb，预训练又能把收益泛化到 unseen environments。单个 fine-tuning example 教会新 behavior 是这条机制的桥梁。

### 关键证据 / 图表 / 公式

Opening 没有图表和公式。它的功能是建立评测标准，读者后面应把每个百分比和 scope、adaptation cost 一起看。

## ACT-2’s Recipe for Generalizing Reliability

这一节提出 broad pretraining 与 narrow post-training 的组合。多样数据让 base model 保持泛化，精选本地数据负责修复可靠性。作者把两者的关系写成一条可循环的研发流程，而不是二选一。

预训练来自 Sunday 自有的硬件、数据筛选和处理管线。数据质量和 composition 被单独拿出来讨论，因为在相同 volume 与 compute 下，片段质量会同时影响 validation loss 和真实成功率。

### Closing the Generalization Gap by Scaling Pretraining

作者先定义 overfitting 的操作性版本。post-training 后，in-domain 是后训练环境代表的分布，out-of-domain 是 held-out 环境、物体和配置，二者成功率的差就是 generalization gap。每个预训练比例都使用相同 post-training procedure。

| Pretrain data scale | In-domain SR | Out-of-domain SR | Gap |
| ---: | ---: | ---: | ---: |
| 0% | 96% | 14% | 82 |
| 12% | 100% | 90% | 10 |
| 25% | 100% | 92% | 8 |
| 50% | 100% | 96% | 4 |
| 100% | 100% | 100% | 0 |

0% 的模型已经在本地数据上到 96%，但陌生环境只有 14%，这正是窄数据后训练的过拟合形状。12% 预训练就把 gap 压到 10，之后继续下降，到完整比例时两种分布都为 100%。每个点背后 50 次评估，图中阴影是 ±1 standard error。

作者再比较 high-quality subsampling 与 uniform subsampling。50% 规模时，高质量抽样的 success 是 92.3%，均匀抽样是 64.1%，validation loss 分别为 0.0668 和 0.0682。这个差距说明「有多少数据」和「留下哪部分数据」不是同一件事。

### 关键证据 / 图表 / 公式

Figure 1 直接支撑 gap 曲线。Figures 2–4 分别展示 success rate、validation loss 和二者相关性。拟合变量写成 `L = validation loss × 10^-3`、`D = pretrain data %`，但正文没有给出完整拟合系数，不能据图重建缩放律。

### Learning Transferable Behaviors from One Example

作者把单示范结果放在 gap 曲线之后。泛化间隔越小，本地示范的行为越可能在新衣物上保留。四个相同 pretrained checkpoint 的独立副本，各自只接收一个不同 folding technique 的 demonstration，之后在 SFT 未出现的 garment 上评估，四个副本全部成功。

存在性证据很干净，变量也很少。可是四个成功不能估计概率，文章没有公开 technique 的具体动作、示范时长、held-out garment 数量或失败处理。

### Hill-Climbing Reliability Through Post-Training

单示范不足以达到部署级可靠性，真实运行中的 edge cases 才是后训练的主要来源。ACT-2 的 loop 从反复运行中收集失败和恢复，再把这些例子送回 SFT。由于同一团队控制机器人、模型、fleet 和数据流程，作者认为迭代速度可以很快。

这节没有公开训练轮次、每轮样本量、更新冻结策略或停止条件。它说明了研发机制，却没有提供可复现的算法描述。还在摸索的是本地数据质量和跨家庭收益之间的定量关系。

## Home Robotics as a Test of General Intelligence

家庭被选作长尾场景，因为房间持续变化，衣物会变形、自遮挡并以任意姿态出现。Laundry folding 同时有实际价值和操作难度，适合作为第一项 Solve。

### Scope 与 adaptation cost

| 维度 | 声明的范围 | 适应成本 |
| --- | --- | --- |
| Garments | T-shirts、厚薄长袖、polos、无袖上衣、blouses、pants、leggings、shorts，XXS 到 8XL，覆盖颜色、材料、厚度、纹理 | 每个家庭零数据、零目标家庭示范、零 post-training |
| Scenes | 未见过的房间、床和折叠面，光照变化，床左侧、右侧和床尾 | 同一 checkpoint 与配置 |
| Initial configurations | 篮子、床上堆、床面散放、地面衣物，方向任意、自然褶皱 | 不要求整理成标准姿态 |

这张表限定了 99.1% 的含义。它不是对所有衣物和所有家庭的无条件承诺，而是在列明的分布中使用一个固定系统且不为每个家庭适配。作者还声明评估家庭与衣物没有用于任务特定的 post-training 或 model selection，权重在评测期间保持固定。

### 关键证据 / 图表 / 公式

这里的核心是 scope 表，不是数学公式。读者需要把「zero-shot」理解成零家庭级适配，而不是零预训练或零研发数据。

## Performance

Performance 章节把结果拆成 success、quality 和 speed。每次尝试由训练过的 annotators 用固定 grading tool 标注，第二位 annotator 独立复核，差异交给 review lead。rubric 在评估前固定，没有事后修改。

### Success Across the Long Tail

成功定义为衣物被自主折叠并堆放。785 次 autonomous attempts、9 类主要衣物的总体成功率为 99.1% ±0.3% standard error。

| 类别 | Success | ±1 SE 区间 | Attempts |
| --- | ---: | --- | ---: |
| Overall | 99.1% | 98.8–99.4% | 785 |
| Shorts | 100% | — | 98 |
| Long-sleeved tops, thick | 100% | — | 85 |
| Long-sleeved tops, thin | 100% | — | 79 |
| Polos | 100% | — | 46 |
| Sleeveless tops | 100% | — | 7 |
| T-shirts | 99.0% | 98.5–99.6% | 312 |
| Pants | 98.8% | 97.7–100% | 85 |
| Leggings | 96.3% | 93.7–98.9% | 54 |
| Blouses | 94.7% | 89.6–99.9% | 19 |

按环境配置看，bed pile 98.8%、basket on bed 100%、basket on ground 99.5%。机器人在床左侧 98.7%、右侧 100%、床尾 98.5%。浅色床单 99.2%、深色 98.0%、其他颜色 99.6%，颜色分组存在重叠。

这里要把样本量放在百分比旁边看。blouse 的最低值来自 19 次，sleeveless tops 的 100% 来自 7 次，二者的精度都不在同一个尺度上。作者推测 blouse 轻薄且可变形，抓取和对齐线索更少，但这只是解释性假设。

### Fold Quality

每次完成折叠先给五颗星，再按四类缺陷扣分。Overfold 是多出材料向内折超过两英寸，misalignment 是对应边缘相差超过两英寸，unfolded element 是袖子、裤腿或帽子伸出超过两英寸，stacking error 是堆叠越界超过衣物宽度三分之一或折痕被破坏。

778 次 completed folds 的平均质量为 4.72/5。98.3% 达到四星或五星，73.8% 是五星。leggings 平均 4.88，pants 4.82，shorts 4.78，T-shirts 4.67，polos 4.63，blouses 4.61。

785 和 778 的差别在此处必须重复。失败尝试进入 785 的成功率分母，却不进入 completed-fold quality 分母。质量结论因此只描述成功完成后的折叠，不描述从失败中恢复的整体用户体验。

### Speed

计时从开始取衣物到折好衣物放入堆叠，包含 autonomous retries 和 recovery。778 次成功折叠的 median completion time 为 2.22 分钟，mean 为 2.32 分钟，10th percentile 1.36，Q1 1.86，Q3 2.64，90th percentile 3.24。

shorts 的 median 1.23 分钟，薄长袖 2.73 分钟。速度只对成功尝试统计，因此不能直接当作每件衣物的期望完成时间。说到点子上了，家庭部署更关心「从拿起一件随机衣物到最终收好」的总时间，文章没有给出包含失败重来次数的全分布。

## Emergent Behavior

作者把 emergent behavior 分成 edge-case recovery、robustness under disturbance 和超出固定 tabletop workspace 的 whole-body manipulation。

衣物掉到地面或严重褶皱时，ACT-2 能取回衣物、重新定向并继续折叠。与人共享空间时，儿童互动、对抗性扰动和明暗变化会改变中间状态，模型会重新规划而不是照固定序列走完。

衣物尺寸从婴儿衣物 16×8 英寸到 8XL 衬衫 38×42 英寸，再到 53×28 英寸的大毛巾。Memo 可以移动、调高度和倾身，让模型处理超出固定桌面工作区的对象。案例很直观，但没有按尺寸或扰动类型给出成功率。

### 关键证据 / 图表 / 公式

Emergent behavior panels 是视频和静态图，没有统一的 trial count。它们适合用来提出后续测试问题，不适合和 99.1% 放在同一张统计表里。

## Solve: A New Standard for Robotics Progress

文章认为单独的 performance 不足以表达机器人进展。相同的 99.1% 可以来自一个熟悉房间和一件整理好的衣物，也可以来自陌生家庭和任意褶皱衣物，二者的实际价值不同。

Solve 要求同时声明三个组件。Performance 包括成功、质量和速度。Scope 指环境、对象和配置的分布。Adaptation cost 指每次新部署所需的额外数据、示范、微调、人工介入或系统改造。

这个框架的优点是让结果可比较、可累积。缺点是需要每个团队公开更长的评测协议，还要解决 scope 之间是否可比的问题。当前 ACT-2 是一个公司自定义的第一个 Solve，尚没有跨团队统一审核。

### 关键证据 / 图表 / 公式

文章没有给出数学公式，但可以把 Solve 写成三元组 `Solve = (Performance, Scope, Adaptation cost)`。三项缺一，99.1% 就无法表达部署难度。

## Toward General-Purpose Robotics

Sunday 说同一个 base model 还在学习 vacuuming、toy organization、zipping、inside-out pants 和 coffee preparation。这些能力分别涉及工具使用、杂乱空间整理、精细操作和长时域可靠性，却尚未按 Solve 标准评估。

作者的长期假设是每个 Solve 都会让下一项更容易。洗衣任务产生的数据和恢复策略能增强共享模型，再迁移到其他家庭能力。这个 fleet flywheel 很有吸引力，但当前文章没有展示跨任务迁移实验或数据复用比例。

## Taking ACT-2 Into the Home

结尾把 Beta Program 作为从 demo 到日常服务的下一步。产品部署会产生更多家庭级失败数据，理论上能继续推动 hill-climbing。需要回看的是，Beta 用户的人工介入规则、隐私处理、暂停条件和真实成功标准是否与这篇文章的 Solve 边界一致。

## 方法细节

公开信息能重建的流程只有高层版本。Sunday 先用自有硬件采集 sensorized human data，再进行 curation 和 processing。预训练比例实验保持 post-training procedure 不变，改变的是数据规模与抽样方式。旗舰模型固定后，真实家庭评估不再针对每个家庭更新权重。

单示范实验使用四份独立模型副本，每份接收一个 folding technique 的单条 demonstration。后训练循环则从反复运行中获取 edge cases、失败和恢复样本，再把它们加入下一轮 SFT。网络、动作空间、学习率、batch size、冻结层和训练步数均未公开。

## 实验设置、数据集、基线、指标

规模实验包含 0%、12%、25%、50%、100% 五个预训练数据比例，每个比例在 in-domain 和 out-of-domain 各评估 50 次。high-quality 与 uniform subsampling 在相同 volume 和 compute 下比较 success 与 validation loss。

主评估覆盖 9 类衣物、不同尺寸材质颜色、床面、房间、光照、机器人位置和初始配置。共有 785 次 autonomous attempts，778 次成功完成折叠用于 quality 与 speed。四个模型副本用于单示范迁移。

基线是不同 pretraining scale 和数据抽样方式，没有公开外部模型或同一家庭上的其他系统。指标包括 success rate、generalization gap、validation loss、五级 fold quality、median 和 mean completion time。成功率区间使用 standard error，文章还说明图中使用 Wilson intervals。

## 主要结果、消融或对比

预训练扩展把 out-of-domain success 从 14% 推到 100%，gap 从 82 推到 0。high-quality subsampling 在 12.5%、25%、50% 三个比例都优于 uniform，50% 时差距为 28.2 个百分点。

旗舰系统的成功率是 99.1% ±0.3%，但这个数字来自 785 次尝试。778 次完成折叠质量均值 4.72，98.3% 达到四星或五星，73.8% 五星。median 时间 2.22 分钟，mean 2.32 分钟。

四个单示范模型都在 held-out garment 上执行新 technique。这个结果和 gap 曲线共同支持「预训练让本地示范更可迁移」，但没有回答不同示范质量、不同家庭和不同衣物组合的成功概率。

## 图表、公式与表格线索

| 编号 | 内容 | 支撑主张 | 阅读提醒 |
| --- | --- | --- | --- |
| Figure 1 | in-domain 与 out-of-domain gap | 预训练规模带来泛化 | 50 次评估，比例无绝对小时 |
| Figures 2–4 | success、validation loss、相关性 | 数据质量影响效率 | 抽样规则未公开 |
| Figure 5 | 衣物类别成功率 | 长尾覆盖 | blouse n=19，sleeveless n=7 |
| Figure 6 | 配置与环境成功率 | 房间、床面、位置变化 | 床单颜色分组重叠 |
| Figure 7 | 五星质量构成 | 折叠整洁和堆叠 | n=778 completed folds |
| Figure 8 | 成功折叠的时间分布 | 使用速度 | 排除了失败尝试 |
| Emergent panels | 地面恢复、扰动和超大衣物 | 策略恢复与全身移动 | 定性视频，没有统一分母 |

## 主张-证据-边界矩阵

| 主张 | 证据 | 边界 |
| --- | --- | --- |
| 预训练规模关闭泛化 gap | 82 → 0，out-of-domain 14% → 100% | 只有相对比例，绝对规模未知 |
| 数据质量提升样本效率 | 50% high-quality 92.3% 对 uniform 64.1% | 筛选器和数据混合未公开 |
| 单示范迁移新行为 | 四个模型均成功 | 样本只有四份，没有概率估计 |
| 家庭折叠高可靠 | 785 次尝试成功率 99.1% | 公司自报，类别分母很不均衡 |
| 成功折叠质量高且速度可用 | 778 次质量 4.72/5，median 2.22 分钟 | 只统计成功完成的样本 |
| Solve 适合描述机器人进展 | Performance、Scope、Adaptation cost 三字段 | 尚无跨团队标准和审计 |
| 能力可扩展到其他家务 | 展示五类额外任务 | 未按 Solve 评估，仍是方向性材料 |

## 局限与可追问点

文章最明显的缺口是模型与数据的不可复现。没有参数量、预训练小时、数据来源比例、动作空间、视觉传感器、compute 和后训练配方，外部无法判断 12% 或 100% 预训练对应的真实资源。

统计分母需要持续保留。785 次 attempts 的成功率包含失败，778 次 completed folds 只包含成功完成的样本。质量和速度因此存在条件化选择，不能直接当作端到端家庭服务指标。

类别分布也会影响总体数字。T-shirts 有 312 次，blouses 19 次，sleeveless tops 7 次。低样本类别的 100% 或 94.7% 置信区间很宽，不能与大样本类别等权解读。

单示范实验只做了四个副本。四次成功说明行为可以传递，不说明任意 technique 都能成功。还需要不同示范者、不同床面、不同衣物和坏示范的系统矩阵。

最后，gap 变小可能同时来自预训练数据质量、模型容量、硬件变化和评测筛选。文章把规模作为主解释，但没有给出控制模型或独立数据混合实验。说到底，Solve 是很好的报告格式，真正的跨家庭可靠性仍需公开 fleet 统计。

## 与当前库的连接

与 [[@generalist2026gen15]] 对照，ACT-2 把低 adaptation cost 放进家庭 scope 和长尾分母，GEN-1.5 则把几秒 physical prompt 放进短时域操作。前者回答「可靠性怎么写清楚」，后者回答「任务怎么快速教会」。

与 [[@intelligence2025pi06-steerable-generalist-robotic]] 对照，重点是 post-training 数据闭环和经验如何传到新场景。与 [[@qwen2026robotmanip]] 对照，重点是跨本体数据对齐、质量筛选和公开程度。与 [[@dexmal2026dm05]] 对照，重点是开放世界宣称是否有明确 scope 与 adaptation cost。

ACT-2 也可作为当前库里家庭机器人工作的评测模板。以后新增家务能力时，至少应同时记录成功、质量、速度、环境范围、初始配置和每个新家庭的适应成本，避免只保留一条演示视频或一个最高百分比。

## 精读路线 / 为什么需要回看

第一遍看 Figure 1 和 Solve 三字段，先理解本地 success 与陌生家庭 success 的差别。第二遍核对 785 和 778 两个分母，再读 Figure 5 到 Figure 8 的类别样本量、质量规则和时间分布。

第三遍回看单示范实验、high-quality subsampling 和 emergent behavior。要判断模型能否部署，必须追问示范质量、失败恢复、人工介入和每个家庭是否真的零数据。

遇到家庭机器人结果比较时，回到这篇文章的 scope 表。说到点子上了，99.1% 只有放在衣物、房间、起始状态和 adaptation cost 的边界里才有意义。还在摸索的下一步是把 Solve 变成跨团队可审计的公开基准。
