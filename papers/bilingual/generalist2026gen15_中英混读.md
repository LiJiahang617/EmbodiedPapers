---
tags:
  - bilingual-reading
paper: "[[@generalist2026gen15]]"
source_pdf: "[[papers/pdfs/generalist2026gen15.pdf]]"
images: "papers/images/generalist2026gen15/"
image_index: "[[papers/images/generalist2026gen15/index.md]]"
created: 2026-08-20
---

# GEN-1.5: Embodied Foundation Models are One-Shot Learners

paper:: [[@generalist2026gen15]]
pdf:: [[papers/pdfs/generalist2026gen15.pdf]]
images:: [[papers/images/generalist2026gen15/index.md]]

> [!warning] 来源说明
> 这是 Generalist AI 的官网博客文章，不是同行评议论文。文章给出了任务成功率和若干视频案例，却没有公开模型参数、训练数据总量、硬件配置、完整试次数量或失败分布。下面的数字都标成作者自报。库里的 PDF 是网页正文文本快照，图片索引中保存了官方静态资源和手动补回命令。

## 一句话总结

GEN-1.5 的主张是，大规模 physical pretraining 可以让机器人把一段 3 到 12 秒的 sensorimotor demonstration 当作 physical prompt，立即执行一个新任务。作者在十个简单短时域任务上报告一次示范平均 59% ±10% 成功率，十步梯度适配平均 83% ±9%，并用组合提示、sim-to-real、人到机器人示范和陌生工具案例展示更宽的物理泛化。

## 核心词汇速查

| English | 中文 | 在文章中的作用 |
| --- | --- | --- |
| embodied foundation model | 具身基础模型 | 在大规模物理交互上预训练的多模态机器人模型 |
| physical prompting | 物理提示 | 把 sensorimotor demonstration 放进上下文，不更新参数 |
| in-context learning | 上下文学习 | 依靠当前上下文临时获得任务技能 |
| one-shot learning | 一次示范学习 | 只给一个 3 到 12 秒示范就开始执行 |
| few-shot adaptation | 少样本适配 | 用 1 到 10 个 gradient steps 更新模型 |
| compositional generalization | 组合泛化 | 把两个独立提示串成一个更长的行为 |
| zero-shot sim-to-real | 零样本仿真到现实 | 模拟器示范直接提示真实机器人 |
| human-to-robot imitation | 人到机器人模仿 | 人手示范被机器人相机看到后由机器人复现 |
| physical generalization | 物理泛化 | 对新物体、工具、障碍、策略和本体保持目标行为 |
| test-time training | 测试时训练 | 文章用来描述极少步的低数据适配 |
| action trajectory | 动作轨迹 | 模型以 100 Hz 输出的连续控制信号 |

## 摘要

文章从一个很具体的使用愿望切入，操作者走到机器人旁边，给它看一次怎么做，机器人就能马上完成任务。GEN-1.5 的输入包含视频、语言、传感器和 proprioception，保留约 30 秒上下文，并以 100 Hz 生成动作轨迹。physical prompt 可以来自人类手持夹具记录或机器人自己执行的 rollout。

十个任务的平均结果形成一条清楚但仍很早期的能力梯度。没有梯度更新时，3 到 12 秒的一次示范带来 59% ±10% 成功率。用 5 分钟数据做 10 步 gradient descent 后，平均成功率升到 83% ±9%。只用 1 分钟数据做 1 步适配时，held-out task 成功率为 66.5%。

作者还展示了把两个提示拼接、从仿真示范迁移到真实机器人、用人手提示机器人、用香蕉或簸箕替代刷子、移开遮挡物和换手操作。坦率的讲，这些案例很能说明模型会重组已有行为，但文章没有把它们转成有分母的系统测试，因此证据强度低于十任务表格。

## 论文主线

![[papers/images/generalist2026gen15/generalist-gen1p5-cover-frame.png|760]]

文章把机器人基础模型的价值定义成两件事，学习新任务要快，遇到新情况要能调整。语言模型在 GPT-3 时代通过 one-shot 和 few-shot prompting 展示了类似转折，Generalist AI 想检验 physical interaction 是否也会出现这种能力。

GEN-1.5 的路线不是为每种任务设计一个 meta-learning loop，而是先让一个模型在家庭、仓库和工厂等环境中连续吸收物理数据，再观察它是否自发形成临时学习能力。这里的关键假设是，广泛的观测和动作序列包含足够多的重复结构与可迁移的接触模式，模型可以在上下文里识别并延伸它们。

说到点子上了，physical prompt 不只是给机器人一句语言指令。模型必须从示范里推断目标，理解物体和手的关系，处理新的初始姿态，并在闭环运行中纠正误差。文章把这种接口视为把「教机器人」从写程序改成展示动作。

## 贡献与结论对照

| 文章声称的贡献 | 证据位置 | 结论强度 |
| --- | --- | --- |
| 大规模 physical pretraining 出现一次示范学习 | Figure 2，十任务平均 59% | 中等，任务短且成功率有限 |
| 极少梯度步数足以适配新任务 | Figure 2 与 one-step 结果 | 中等，适配超参没有系统扫描 |
| 提示可以组合成更长行为 | Compositional Generalization 视频 | 早期存在性证据，没有成功率 |
| 模拟示范可提示真实机器人 | Sim-to-real 视频 | 早期存在性证据，没有分层统计 |
| 物理泛化包括陌生工具和障碍处理 | Physical Generalization 案例 | 定性证据，陌生程度未独立验证 |
| 预训练持续八个月仍带来收益 | Figure 3 held-out error 曲线 | 方向清楚，训练曲线细节未公开 |

## 结构地图

| 原文 section | 本文中文理解 | 在论证链中的工作 |
| --- | --- | --- |
| Introduction | 引言 | 把物理一次示范学习放进机器人基础模型历史 |
| Introducing GEN-1.5 | 模型概览 | 给出输入、输出和能力清单 |
| Scaling Pretraining for Robotics | 机器人预训练扩展 | 解释八个月训练与适配步数下降 |
| One-Shot Learning In-Context | 上下文一次示范学习 | 定义 physical prompt 与无梯度执行 |
| Compositional Generalization | 组合泛化 | 证明多个提示可以串联 |
| Zero-Shot Sim-to-Real Transfer | 零样本仿真到现实 | 说明提示不要求预训练含仿真数据 |
| Human-to-Robot In-Context Learning | 人到机器人上下文学习 | 观察 embodiment gap 能否被示范跨过 |
| Few Gradient Step Adaptation | 极少步梯度适配 | 测量 1 到 10 步的任务更新效率 |
| Physical Generalization | 物理泛化 | 观察陌生工具、障碍、物体和策略 |
| Looking Ahead | 展望 | 把一次示范学习连接到物理通用智能 |

## Introduction

引言先把目标说得很直白，机器人应当能在操作者走近后很快学会一项任务。作者把即时性和普适性放在一起，认为只会复现固定动作还不够，模型还得在闭环中面对现实变化。

文章借 GPT-3 的 one-shot 与 few-shot 结果作类比，再回溯 Unimate 的 teach-by-guiding 和 MIT Copy Demo。这个历史段落的作用不是提出新算法，而是把 GEN-1.5 的 claim 放到一条长期研究问题上，过去的机器人示范学习通常受限于物体、任务类别或传感器，本文试图扩大这些范围。

### 关键证据 / 图表 / 公式

Figure 1 并列语言模型问答和具身模型的 Marker Into Cup。语言模型的 prompt 是文字，具身模型的 prompt 是 sensorimotor sequence。原文没有数学公式，这一节的证据主要是概念类比，不能把类比当成性能等价。

## Introducing GEN-1.5

这一节给出系统边界。模型能记住约 30 秒视频和其他传感输入，动作轨迹以 100 Hz 产生。作者把能力分成 one-shot prompting、few-shot gradient adaptation 和 improvisation，且强调没有为这些能力加入专门的架构改造或 meta-learning 目标。

十任务表格是文章最完整的定量证据。拿钱、折纸、拧罐盖、叠杯、扫垃圾、开书、刷方块、翻手机、拉开铅笔袋、取下吸盘都属于短时域原子操作。十步适配比一次示范通常高，但某些任务的 in-context 结果接近甚至超过 1 到 5 步适配。

### 关键证据 / 图表 / 公式

Figure 2 同时画出两种设置。一次示范列使用 3 到 12 秒 prompt，另一列使用 5 分钟数据和 10 步更新。注意两种设置不只差梯度步数，也差数据量，不能把柱高差完全归因于更新机制。

## Scaling Pretraining for Robotics

Generalist AI 说 GEN-1.5 已连续训练超过八个月，held-out next-action prediction error 在三个训练阶段持续下降。作者把数据吸收、compute efficiency、架构修改和算法改进放在同一条进步叙事里，观察到新任务需要的数据和计算逐渐减少。

这段还交代了研究顺序。团队先看到数百步适配，再看到几十步，最后尝试 1 步，随后才问能否去掉全部梯度更新。换到研究方法的角度，这是一种由 adaptation cost 驱动的能力探测，而不是事先设计好的 one-shot benchmark。

### 关键证据 / 图表 / 公式

Figure 3 展示三个训练阶段的 held-out error。网页正文没有给坐标轴完整数值、模型版本或计算量，因此可以确认趋势，无法重算 scaling exponent。

## One-Shot Learning In-Context

一次示范被放入 30 秒 context window，剩余时间保留滚动观测。模型不做训练，直接执行。Physical prompt 可以是人类用一对 handheld grippers 做的示范，也可以是 robot rollout。这个接口的优点是任务切换快，代价是当前技能比 fine-tuned model 更脆弱。

作者承认为什么会出现这种行为还在摸索。一个猜测是物理序列和语言序列一样存在 burstiness 与 Zipfian structure，另一个猜测是日常工作包含重复周期，模型学会了检测并延伸这些模式。训练时随机抽取连续片段，未专门把示范打包成 prompt，physical prompt 反而引入了训练中没见过的时间跳跃。

很多团队会遇到同一个接口选择，语言容易表达高层目标，动作示范更容易表达精确接触。GEN-1.5 的 physical prompt 同时考验目标推断和运动执行，所以比单纯的语言条件更接近 sensorimotor understanding。

### 关键证据 / 图表 / 公式

一次示范平均 59% 是这一节的核心数字。视频展示了拉链袋和取钱两个任务背靠背执行，但没有给每次提示的试次数和置信区间。没有原文公式。

### Compositional Generalization

两个独立 prompt 分别示范解开铅笔袋和取出钱。它们被同时放进上下文，模型连续完成两个任务，并自行产生重定位、重新抓取、错误恢复和换手动作。中间过渡并未出现在单独示范里。

这个结果把 physical prompt 从一次性例子变成技能库里的可组合单元。若每个短 prompt 都能稳定复用，长时域任务就可以通过上下文编排而不是重新收集整段复合示范。不过当前材料只有视频，没有任务成功率、组合顺序的数量或失败案例。

### Zero-Shot Sim-to-Real Transfer

作者把模拟器里录制的 demonstration 直接放入真实机器人的 context。预训练不含 simulation data，模型也没有在该任务的模拟或现实轨迹上训练。真实执行会面对不同手型、物体位置和尺寸。

这里的 zero-shot 定义要读仔细。它不是常见的「在仿真训练策略后直接上真机」，而是「模型从未见过该任务，只有一段模拟示范作为运行时 prompt」。这让结果更像跨来源示范理解，而不是经典 simulator policy transfer。

### Human-to-Robot In-Context Learning

人用自己的手在机器人相机视野内做示范，机器人随后执行同一目标。这个例子把人手、机器人手和相机视角之间的差异压缩进一次上下文推断，展示了跨 embodiment 的可能性。

文章没有给出人到机器人案例的任务列表、成功率、试次和干预规则。说到点子上了，这一节证明的是接口可行，不是跨本体性能曲线。

## Few Gradient Step Adaptation

GEN-1.5 的另一条路径是用 1 到 10 个 gradient steps 更新预训练权重。作者把它与过去需要数万步的任务训练比较，并指出十步适配时 held-out task 的权重变化小于 0.15%。这个变化幅度支持一种解释，更新主要是在已有行为库上做轻量重排。

十步实验从 5 分钟数据采样，超参大致沿用预训练。一步实验从 1 分钟数据采样，held-out task 成功率 66.5%。更大的 batch 和 learning rate 有帮助，但作者没有针对 adaptation 做系统 sweep，结果应读作未经充分调优的样例。

### 关键证据 / 图表 / 公式

Figure 4 用 classical MDS 把不同任务的权重变化画在预训练点周围。它支撑任务更新方向各不相同，不支持参数空间距离就是能力距离。本文没有公开适配损失公式或 optimizer 参数。

## Physical Generalization

这一节把「学会示范」和「达到目标」分开。fine-tuned models 不只复制演示里的抓法，还会面对新 embodiment、物体实例、环境、障碍和工具，甚至改变同一目标的操作策略。

### Novel tool use improvisation

模型只在 5 分钟人类示范中看过刷子扫方块进碗。遇到香蕉时，它把香蕉当临时刷子。遇到簸箕时，它改用抬起方块并倒入碗中的接触序列。作者称训练数据和最近邻预训练场景都没有相同用法，也没有语言指导。

这个例子最有价值的地方在策略层面的改写，不是物体识别。模型没有寻找一个外观相似的刷子，而是根据目标与工具可用接触重新安排动作。可是最近邻场景来自 1,891,392 个场景的语言搜索，文章没有公开搜索误差和真正的视觉相似度，因此「陌生」仍是作者的描述。

### Obstacle handling and recovery

方块入碗的适配数据没有纸张遮挡。运行时碗被纸盖住，模型会移开纸再完成任务，有时还把纸放回去。其他案例包括从指尖移除卡住的 Lego、用双手拧罐盖、按颜色或类别整理方块。

这些行为支持模型拥有更宽的 physical prior。其证据形态仍是精选视频，缺少对所有障碍类型的覆盖率，也没有说明失败后是否有人工干预。

### New objects and ambidexterity

拧罐盖的适配数据只涉及一种罐子，模型后来尝试杯子、瓶子和不同容器，需要选择新的抓取位置、双手关系和腕部旋转。刷子案例也展示了演示只用一只手而 rollout 可以换另一只手。

这些结果更接近结构泛化，目标是拧开或扫入，而不是复制某条轨迹。当前材料没有把每种新物体的试次数放在表里，所以不在一个尺度上比较它们与十任务平均值。

## Looking Ahead

结尾把 GEN-1.5 放进 Generalist AI 的长期路线。作者说团队原本并没有专门追求 one-shot learner，而是在搭建高质量 physical data engine 的过程中观察到适配成本下降。达到某个预训练阈值后，几秒示范或一分钟数据更像提醒模型调用已有技能，而不是从零训练。

这段也重新定义了 general-purpose robot 的使用者。过去「通用」常常意味着专家要花数月编程，本文希望把交互变成展示动作。说到底，这是一篇关于能力接口和未来路线的公司叙事，不能替代开放实验协议。

### 关键证据 / 图表 / 公式

原文没有新的定量图。Citation 给出官方引用，Generalist Team, GEN-1.5: Embodied Foundation Models are One-Shot Learners, Generalist AI Blog, Aug 2026。这里直接保留英文书目信息，中文解释使用「」避免混淆。

## 方法细节

数据侧是持续 physical pretraining，场景来自家庭、仓库、工厂等环境。模型输入多模态上下文，保存 30 秒历史，动作以 100 Hz 生成。运行时 prompt 可以是人类夹具示范、机器人 rollout 或模拟器 rollout。

适配侧有两个 regime。一次示范只改变 context，不改权重。少样本适配从 1 到 10 步更新权重，数据从 1 分钟到 5 分钟。作者没有公布模型层数、参数量、action chunk、损失函数或控制器接口，不能据此重建系统。

评测侧把能力拆成平均任务成功率、held-out one-step success、组合案例、sim-to-real 案例、工具即兴和障碍恢复。定量表只有十个短时域任务，其他能力主要靠视频。

## 实验设置、数据集、基线、指标

十任务比较两种 adaptation condition。In-context condition 使用 3 到 12 秒单示范且零梯度步，few-shot condition 使用约 5 分钟数据和 10 步梯度更新。另一个一步实验使用 1 分钟数据和 1 gradient step，在 held-out task 上得 66.5%。

文章没有标准 baseline model，也没有公开不同预训练规模的横向表。Figure 3 只显示训练阶段的 next-action validation error。基线更多是同一模型的不同适配方式，而不是不同架构。

成功率是任务完成比例，表格同时给出标准差。Physical Generalization 的工具、障碍和新物体案例没有统一 metric。Figure 4 的 MDS 使用权重间 L2 距离，图形是解释性展示。

## 主要结果、消融或对比

十任务一次示范平均成功率 59%，十步适配 83%。单项差异很大，扫垃圾的适配后 99% 而一次示范 37.3%，翻手机的一次示范 78% 而适配后 81%。这说明上下文示范对任务结构的帮助不等，不能只看平均值。

一步适配在 held-out task 上为 66.5%，权重变化在十步设置小于 0.15%。组合 prompt 产生了独立示范之外的中间动作。仿真 prompt 在没有仿真预训练的前提下提示真实任务。工具和障碍案例展示了目标导向的策略改写。

这些结果共同支持「预训练提高 adaptation efficiency」的方向，但没有把数据质量、模型规模、架构手术和训练时长拆开。还在摸索的部分是能力何时出现，以及它在更长时域任务上是否保持。

## 图表、公式与表格线索

| 编号 | 内容 | 支撑主张 | 阅读提醒 |
| --- | --- | --- | --- |
| Figure 1 | 语言 one-shot 与具身 physical prompt 对照 | 定义物理提示 | 概念图，不是性能比较 |
| Figure 2 | 十任务两种适配条件 | 一次示范与十步适配 | 两种条件数据量不同 |
| Figure 3 | 八个月预训练的 held-out error | 预训练持续带来收益 | 轴值与训练配置未完整公开 |
| Figure 4 | 任务权重的 MDS 嵌入 | 适配方向随任务不同 | 不是能力因果图 |
| Videos 84–86 | 两个 physical prompt 的组合 | 长行为可由短提示拼接 | 没有成功率与分母 |
| Videos 87–89 | sim-to-real 与 human-to-robot | 跨来源、跨本体提示 | 以定性展示为主 |
| Videos 90–113 | 工具、障碍、双手和新物体 | 物理泛化与即兴 | 最近邻和失败分布未公开 |
| Figure 4 的 MDS | 权重更新距离 | 轻量重排已有知识 | L2 距离不等同语义变化 |

文章没有公开数学公式。可以把一次示范条件写成行为接口，`context = demonstration + rolling observations`，随后模型直接输出 action trajectory。这个表示是本文的运行逻辑，不是作者正式给出的训练公式。

## 主张-证据-边界矩阵

| 主张 | 证据 | 边界 |
| --- | --- | --- |
| 物理一次示范学习已经出现 | 十任务平均 59% ±10% | 任务短、成功率中等、公司自报 |
| 少量梯度步数能快速适配 | 十步平均 83%，一步 held-out 66.5% | 超参未系统搜索，数据分布未公开 |
| physical prompt 可以组合 | 解拉链袋后取钱的连续 rollout | 只有视频，没有组合任务统计 |
| 模拟示范可直接提示真实机器人 | 预训练不含仿真数据仍完成示例 | 任务数量、物体变化和试次数未知 |
| 人手示范能跨到机器人手 | 相机前人手示范后的机器人执行 | 没有成功率和 embodiment 分层 |
| 预训练带来工具与障碍即兴 | 香蕉、簸箕、纸张和卡住 Lego 案例 | 精选视频，陌生程度无法独立核验 |
| 适配逐渐变得便宜 | 八个月训练叙述、权重变化小于 0.15% | 没有按模型规模和数据量拆解因果 |

## 局限与可追问点

最重要的限制是统计协议不完整。文章报告了十任务平均和标准差，却没有每个任务的试次数、置信区间、随机种子、硬件差异和失败类型。59% 的平均值可以证明能力不是零，但不能预测新家庭里的可靠性。

其次，physical prompt 的选择可能影响很大。拖放界面允许人工挑选示范，文章没有报告随机选取、坏示范、不同演示者和不同上下文长度的结果。若挑选过程依赖专家，所谓 zero-shot 的实际使用成本仍未明确。

再者，物理泛化案例把多种变量放在一起。工具改变、物体改变、手的改变和障碍出现都可能调用不同的预训练先验，当前没有消融来区分它们。1,891,392 个最近邻场景的搜索文本也不足以证明视觉和动作分布真的陌生。

最后，作者把连续八个月和能力出现联系起来，却没有公开数据小时、compute、参数量和版本切换。若没有这些控制，无法判断收益来自规模、数据质量、架构改造还是工程筛选。

## 与当前库的连接

和 [[@sunday2026act2preview]] 一起读，能看到两种低 adaptation cost 的证据形态。GEN-1.5 用秒级 physical prompt 和少量梯度步展示接口，ACT-2 用家庭 scope、785 次尝试和 778 次质量样本展示可靠性。两篇都应把公司自报与可复现统计分开。

和 [[@jiang2026robottt]] 对照，重点看 context 的时间范围与用途。RoboTTT 关注测试时上下文如何扩大，GEN-1.5 关注上下文里放一段完整示范。和 [[@intelligence2025pi06-steerable-generalist-robotic]] 对照，重点看经验回放、后训练和 one-shot prompt 的成本边界。

和 [[@paliwal2026do-i-dexterous-manipulation]] 对照，重点是人类示范到机器人动作的粒度。Do as I Do 强调人手轨迹的迁移，GEN-1.5 以传感器与动作序列的上下文重用为主，二者都还需要更完整的跨本体统计。

## 精读路线 / 为什么需要回看

第一遍读 Figure 2 和 One-Shot Learning In-Context，先分清一次示范、五分钟十步和一分钟一步这三个数据点。它们的 adaptation cost 不同，不能只比较成功率。

第二遍看 Compositional Generalization、Sim-to-Real 和 Human-to-Robot 三段视频，再追问每段的分母、失败规则和示范选择方式。说到底，视频证明了行为存在，表格才有机会说明行为稳定。

第三遍看 Physical Generalization 的工具、障碍和新物体案例。重点不是把案例当作全能证明，而是观察模型是否根据目标重新组织接触序列。

需要回看这篇文章的场景包括设计 demonstration interface、比较 in-context 与 test-time training、评估跨本体示范和讨论预训练规模的边际收益。还在摸索的下一步是把这些展示性能力变成公开、分层、有失败样本的 benchmark。
