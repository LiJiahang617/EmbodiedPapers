---
tags:
  - paper
status: unread
aliases:
  - GEN-1.5
  - "GEN-1.5: Embodied Foundation Models are One-Shot Learners"
  - "GEN-1.5 具身基础模型"
year: 2026
title: "GEN-1.5: Embodied Foundation Models are One-Shot Learners"
doi:
arxiv:
url: "https://generalistai.com/blog/gen-1.5"
venue: "Generalist AI 官方博客（非同行评审文章）"
venue_short: "Blog"
pdf_url:
openalex:
metadata_source: "Generalist AI 官方博客正文与文章末尾引用"
metadata_confidence: medium
pdf: "[[papers/pdfs/generalist2026gen15.pdf]]"
reading: "[[papers/bilingual/generalist2026gen15_中英混读.md]]"
images: "papers/images/generalist2026gen15/"
image_index: "[[papers/images/generalist2026gen15/index.md]]"
map_axis: "具身智能/VLA/物理提示与少样本适配"
map_brief: "GEN-1.5 用大规模物理交互预训练获得 physical prompting、组合泛化、零样本 sim-to-real 和极少步适配，十个短时域任务的一次示范平均成功率为 59%。"
map_role: "观察具身基础模型是否把预训练规模转化为即时任务学习与物理泛化的代表性公司自报案例。"
authors:
  - "[[Generalist Team]]"
institutions:
  - "[[Generalist AI]]"
topics:
  - embodied foundation model
  - physical prompting
  - in-context learning
  - one-shot imitation
  - few-step adaptation
  - compositional generalization
  - sim-to-real transfer
  - physical generalization
---

# GEN-1.5: Embodied Foundation Models are One-Shot Learners

- [x] 本地快照 PDF:: [[papers/pdfs/generalist2026gen15.pdf]]
- [x] 元数据:: source=Generalist AI 官方博客与引用, confidence=medium
- [x] 精读稿:: [[papers/bilingual/generalist2026gen15_中英混读.md]]
- [x] 图片索引:: [[papers/images/generalist2026gen15/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[in-context learning]] · [[vision-language-action]] · [[@jiang2026robottt]] · [[@intelligence2025pi06-vla-that-learns]] · [[@intelligence2026pi07-steerable-generalist-robotic]] · [[@paliwal2026do-i-dexterous-manipulation]] · [[@dexmal2026dm05]]
affiliation:: [[Generalist AI]]

> [!warning] 来源与可信度
> 这是 Generalist AI 在官网发布的公司博客文章，不是同行评议论文，也没有公开权重、代码、完整数据或正式实验附录。文章末尾给出的引用把发布日期写作 2026 年 8 月。本文档把成功率、预训练时长和场景数量都视为作者自报，不能当作独立复现实验。
>
> `papers/pdfs/generalist2026gen15.pdf` 是用 Jina 保存的网页正文文本快照，不是排版 PDF。网页里的视频没有纳入 Git，图片补回命令放在 [[papers/images/generalist2026gen15/index.md]]。

## Abstract（博客自述要点，非正式摘要）

GEN-1.5 是 Generalist AI 的具身基础模型。它把约 30 秒的视觉和传感上下文与 proprioception、语言及动作轨迹一起处理，并以 100 Hz 输出动作。作者报告模型能够从单个 3 到 12 秒的 physical prompt 立即学会新任务，也能用 1 到 10 个 gradient steps 在 1 到 5 分钟数据上适配。十个简单短时域操作任务的一次示范平均成功率是 59% ±10%，十步梯度适配平均是 83% ±9%。文章还展示了组合提示、仿真到现实、人到机器人示范、陌生工具、障碍处理、双手协同和陌生物体泛化。

## 一句话定位

GEN-1.5 试图证明，足够广的 physical pretraining 可以把机器人新任务学习从「重新训练一个策略」推到「放进几秒示范就能运行」，而一次示范的 59% 平均成功率和单步适配的 66.5% 更适合作为能力出现的早期证据，不是已解决通用操作的结论。

## 方法 / 对象

- 模型形态是 large multimodal robot foundation model，输入包含视频、其他传感器、语言、proprioceptive signals 和 action trajectories，记忆窗口约 30 秒，动作输出频率为 100 Hz。
- Physical prompting 把一段 sensorimotor sequence 放进上下文。示范可以来自带手持夹具的人类记录，也可以来自机器人 rollout。模型不更新参数，示范后直接闭环执行。
- Few-shot adaptation 用 gradient descent 更新模型，文章给出的范围是 1 到 10 步，数据量是 1 到 5 分钟，约等于 10 到 50 个 demonstrations。
- 作者没有为 in-context learning、meta-learning 或工具即兴额外加入专门目标，主张这些行为从持续的 physical pretraining 中自然出现。
- Physical prompt engineering 用拖放界面选择上下文里的示范，允许把多个短任务拼成更长的行为。

## 证据

### 十个任务的对比

| 任务 | 10 gradient steps，5 min | In-context，3–12 s |
| --- | ---: | ---: |
| Retrieve money from purse | 83.3% | 60.7% |
| Fold and crease paper | 69.3% | 50.0% |
| Twist lid off glass jar | 94.5% | 60.0% |
| Stack two small cups | 75.0% | 67.0% |
| Sweep trash with brush | 99.0% | 37.3% |
| Open book cover | 82.7% | 54.7% |
| Brush cube into bowl | 71.2% | 60.8% |
| Flip phone upside down | 81.0% | 78.0% |
| Unzip pencil pouch | 86.0% | 55.5% |
| Remove vacuum pad | 86.0% | 64.0% |

十个任务的平均值是一次示范 59% ±10% 标准差，十步适配 83% ±9% 标准差。样本覆盖拉链、罐盖、纸张、杯子、刷子和钱包等原子操作，但任务都短，成功率也没有接近稳定的全能水平。

### 能力类型

- Compositional generalization 把两个独立示范放在同一个上下文里，模型先解开铅笔袋，再从袋中取钱。中间的重新定位、重新抓取、恢复和换手动作没有出现在任一示范中。
- Zero-shot sim-to-real 用完全来自模拟器的 rollout 做 physical prompt。预训练没有模拟视频或模拟动力学，真实机器人仍能在新手型、新位置和新尺寸上执行。
- Human-to-robot in-context learning 让人直接在机器人相机前用手示范，模型随后用机器人双手复现目标行为。这个结果跨过了人手到机器人手的 embodiment gap，但文章没有给出系统成功率。
- Novel tool use 以刷子示范把方块扫入碗中，遇到香蕉时把香蕉当作临时刷子，遇到簸箕时改用抬起并倾倒的接触策略。作者还展示了多方块、双手和不同物体的变体。
- Obstacle handling 只用无遮挡的方块入碗数据做一次梯度适配，模型在碗口被纸遮住时会移开纸张，完成任务后有时还会把纸放回去。

### 预训练过程与数据效率

GEN-1.5 连续预训练超过八个月，作者称 held-out next-action prediction error 在三个训练阶段持续下降。随着训练继续，适配新任务所需的梯度步数从数百降到数十，再降到 1 步。十步适配时权重在 held-out task 上的变化小于 0.15%，作者据此把它解释成对已有知识的轻量重排。

在极端的一步设置中，只从 1 分钟数据采样，held-out task 成功率是 66.5%。更大的 batch size 和更高 learning rate 会改善结果，但作者没有做系统的适配超参数 sweep，所以这个数字更像未经充分调参的能力下限。

## 局限

- 文章是公司博客，缺少模型规模、训练数据总量、机器人硬件、任务拆分、试次数量、置信区间和失败样本分布，外部无法重建统计检验。
- 十个任务都属于短时域原子操作，59% 的一次示范平均值不能外推到长时域家庭任务或连续多任务工作流。
- 物理提示的来源、示范选取界面、上下文中动作与观测的精确编码没有公开，组合提示是否依赖人工挑选也没有量化。
- sim-to-real 和 human-to-robot 示例以视频展示为主，没有按物体、手型、初始状态列出分母，跨本体泛化的边界仍然模糊。
- 工具即兴、障碍处理、分类和双手协同主要是定性案例。最近邻场景搜索包含 1,891,392 个场景，但这些场景的来源与覆盖率未披露，无法判断所谓陌生程度。
- 作者把能力归因于预训练规模，却没有公开相同数据和不同模型规模的控制实验，也没有拆分数据质量、架构修改和算法迭代各自的贡献。

## 我的阅读笔记

这篇文章最值得留下的是任务学习接口的变化。Physical prompt 把 demonstration 变成上下文里的可组合对象，类似语言模型把例子放进 prompt，但机器人还要面对接触、遮挡、误差恢复和双手协调。文章给出的数字足够说明能力不是单个演示视频的偶然剪辑，却不足以证明它已具备可部署的开放世界可靠性。

与 [[@jiang2026robottt]] 对照时，重点看两者怎样使用 context。RoboTTT 讨论测试时上下文扩展和持续适配，GEN-1.5 把上下文直接当作 physical prompt。与 [[@intelligence2025pi06-vla-that-learns]] 对照时，重点看 adaptation cost，π 系列强调少量梯度更新和经验回放，GEN-1.5 把零梯度示范也纳入同一条能力曲线。

真正需要后续追问的是可重复的失败结构。若一次示范成功率在不同机器人、不同采集者和不同物体上仍保持相近，physical prompting 才能从展示性接口变成通用编程方式。当前文章没有提供这样的分层统计。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
