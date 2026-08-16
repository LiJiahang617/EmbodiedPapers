---
tags:
  - bilingual-reading
paper: "[[@huang2026rynnvalue]]"
source_pdf: "[[papers/pdfs/huang2026rynnvalue.pdf]]"
images: "papers/images/huang2026rynnvalue/"
image_index: "[[papers/images/huang2026rynnvalue/index.md]]"
created: 2026-08-16
---

# RynnValue: Scaling Robotic Value Foundation Models with Temporal Distance

paper:: [[@huang2026rynnvalue]]
pdf:: [[papers/pdfs/huang2026rynnvalue.pdf]]
images:: [[papers/images/huang2026rynnvalue/index.md]]

## 一句话总结

这篇论文在论证一件事，机器人奖励模型不该继续用 preference（偏好）和 normalized progress（归一化进度）这类任务内部锚点做监督目标，而应该换成 temporal distance（时间距离），也就是从当前观测到语言指定目标还需要多少秒。作者用这个目标训了一个 8B 的 value foundation model（价值基础模型），在完全没有偏好标注的情况下超过了全偏好监督的 SOTA，并把它接成 dense reward 喂给真机 RL。

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| value foundation model | 价值基础模型 | 本文的定位，一个可复用的通用价值接口，不是某个任务的奖励启发式。 |
| temporal distance | 时间距离 | 本文的监督目标，从观测到目标完成还剩多少时间。 |
| cost-to-go | 待付代价 | 控制里的标准价值语义，temporal distance 在最短时间目标下等价于 hitting-time cost-to-go。 |
| normalized progress | 归一化进度 | 被本文点名批评的旧目标，把每条轨迹压到 [0,1]，是轨迹内坐标而非目标条件价值。 |
| preference supervision | 偏好监督 | 需要人工构造轨迹对比，标注贵且难跨数据源复用。 |
| absolute / relative value head | 绝对 / 相对价值头 | 两个分布式预测头，一个预测到完成的剩余时间，一个预测相邻观测间的有符号时间位移。 |
| value-isolation attention | 价值隔离注意力 | 让不同观测的 value query 互相看不见，堵住外推捷径。 |
| temporal-order shuffling | 时序打乱 | 打乱采样帧的先后顺序，切断序列位置和进度的对应关系。 |
| random temporal sampling | 随机时间采样 | 用不均匀时间间隔采 8 帧，破坏等差价值模式。 |
| instruction-mismatch augmentation | 指令错配增强 | 10% 样本换成别的指令，逼模型学会说 Match No。 |
| symlog binning | symlog 分箱 | 把连续时间目标离散成 256 个 symlog 间距的箱，压缩大尺度长尾。 |
| two-hot target | 双热目标 | 用相邻两个箱精确表示连续值，把回归变成稳定的分类问题。 |
| potential-based shaping | 势函数塑形 | Ng 等人 1999 年的经典结论，保证塑形后最优策略不变。 |
| Kendall's τ_a | Kendall τ_a 相关系数 | 本文主指标，衡量预测排序和真值轨迹质量排序的一致程度。 |
| RBM-EVAL-OOD | RBM-EVAL 分布外测试集 | Robometer 提出的评测套件，976 条轨迹，六个跨机构跨本体数据集。 |
| DSRL | 扩散策略隐空间强化学习 | 本文在线 RL 用的算法，Diffusion Steering via RL。 |
| IQL | 隐式 Q 学习 | 本文离线 RL 用的算法，Implicit Q-Learning。 |
| shortcut learning | 捷径学习 | 模型抓住输入里的规律性而不是视觉证据，本文两个训练设计都在防这个。 |

## 摘要

通用奖励模型正在变成机器人学习规模化的瓶颈，但怎么从大规模异构语料里学到价值能力，这套配方还没被研究透。现有方法把监督绑在任务内部的锚点上，比如偏好或者归一化进度，这些锚点都没法干净地跨本体、跨数据源迁移。

作者提出 RynnValue，一个开源的机器人操作价值基础模型，用 temporal distance 替换掉上述锚点。temporal distance 是从观测到语言指定目标的有向 cost-to-go。因为这种标签能直接从时间戳算出来，RynnValue 得以扩展到 7000 多小时、约 300 万条指令条件片段，全程不需要偏好或进度标注。

为了让时间价值学习在大规模下仍然可靠，作者组合了 random temporal sampling、temporal-order shuffling 和 value-isolation attention 三件事，压制那些会让预测对失败和倒退不敏感的捷径。在没有任何偏好标签的情况下，RynnValue 在 RBM-EVAL-OOD 上拿到平均 Kendall's τ_a 0.675，超过全偏好监督的 SOTA 0.655，比只用进度监督的对照组 0.292 高出一倍多，同时零样本泛化到没见过的任务、本体和视角。通过 potential-based shaping 转成 dense reward 之后，真机策略成功率在线从 52.5% 提到 72.5%，离线从 63.8% 提到 82.5%。

## 论文主线

![[papers/images/huang2026rynnvalue/RynnValue_arch_page1.png|760]]

**Figure 1 RynnValue 总览。** 模型接收语言指令和一串采样观测，构造成绝对价值查询和相对价值查询交错的多模态序列，由 RynnBrain 一次前向编码。两个分布式头分别输出到完成的绝对时间距离和相邻观测间的有符号相对位移，语言分支另外产出视频分析和任务验证。产物同时服务进度估计、失败检测和 RL 奖励指定三件事。

论文的推进线索很清楚。作者先指出，通用机器人奖励模型现在卡在监督目标上，而不是卡在模型容量上。手工奖励在开放任务上不泛化，稀疏成功信号对长时程行为指导太弱，而已有的通用奖励模型依赖偏好、参考示范或局部状态比较，这些都把监督绑死在特定轨迹或特定比较集合上。退而求其次用的归一化 [0,1] 进度，问题在于它是轨迹内坐标，不是目标条件的 cost-to-go，跟控制里价值的标准含义对不上，也没法在时长、本体、任务结构都变化时保持一致。

于是作者提出换框架，从「给轨迹级锚点打分的 reward model」换成「预测目标条件 cost-to-go 的 value foundation model」。这一步是全文的支点。换了目标之后，标签可以直接从时间戳读，异构数据被统一到同一个接口下，规模化的障碍就消失了。

但作者紧接着承认，光堆数据不够。多帧输入下，模型可以靠采样间隔的规律、观测的呈现顺序、或者别的 value query 表示来蒙答案，而不去看视觉证据。这种捷径会让价值曲线看起来很平滑，对倒退和失败却完全不敏感。RynnValue 因此在视觉层和价值层各加一道防线，视觉层做不规则采样加顺序打乱，价值层做注意力隔离。

最后作者两条腿验证，一条是把它当独立价值模型在 RBM-EVAL-OOD 上测排序能力，另一条是把它接成 dense reward 在四个真机任务上跑在线和离线 RL。

说到底，这篇的野心不是刷榜，是想把 temporal distance 立成一个能长期复用的监督目标。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| 指出 normalized progress 是通用奖励建模的监督瓶颈，改用 temporal distance 作为规模化目标 | Section 1、Section 3.1 | Table 2 里 progress-only 对照组只有 0.292 | 强，对照组差距足够大 |
| 一套标签便宜的数据配方，标签直接从时间戳导出，覆盖 7000+ 小时、约 3M 片段 | Section 3.1，Table 1、Table 6 | 语料统计和 curation 保留率 83.35% | 强，配方描述完整可复现 |
| 两个互补的捷径压制设计，temporal-order shuffling 和 value-isolation attention | Section 3.2.1、Section 2 | Table 3 消融，去掉 shuffling 掉到 0.189，去掉 isolation 掉到 0.482 | 很强，这是全文最扎实的一块 |
| 不用偏好标注就超过偏好监督 SOTA | Section 4.2 | Table 2，8B 拿 0.675 对 Robometer 0.655 | 中等偏强，领先幅度只有 0.02 |
| 经 potential-based shaping 后能改善真机在线和离线策略学习 | Section 3.3、Section 4.5 | Table 4，在线 72.5% 对 52.5%，离线 82.5% 对 63.8% | 中等，四个任务每个 20 试次，样本量偏小 |

## 结构地图

| 章节 | 原文标题 | 这节在全文里干什么活 |
| --- | --- | --- |
| 1 | Introduction | 立靶子，把问题从 reward model 重述成 value foundation model，给出四条贡献 |
| 2 | Model Architecture | 讲清楚 grouped temporal queries、双分布头、value-isolation attention、语言分支怎么拼 |
| 3.1 | Data Preparation | 异构数据混合和 temporal-distance relabeling，解释标签为什么便宜 |
| 3.2 | Training Recipe | 采样策略、指令错配增强、三个联合损失 |
| 3.3 | Inference and Reward Interface | 推理时怎么关掉增强，怎么把时间距离翻成势函数 |
| 4.1-4.2 | Setup and Benchmark | RBM-EVAL-OOD 主结果、指令轨迹对齐分析、组件消融 |
| 4.3 | Scaling Analysis | 拆开数据量和任务多样性，回答「异构配方到底哪一半有用」 |
| 4.4 | Case Study | 价值曲线定性对比，展示对倒退的敏感度 |
| 4.5 | Real-World Policy Learning | 四个真机任务的在线和离线 RL |
| 5 | Conclusion | 收口，列三个未来方向 |
| A | Appendix Data Curation | 指令清洗和动作相关性过滤的量化效果 |

## 1 Introduction / 把奖励模型重述成价值基础模型

这节干的活是换问题定义。作者列了现有路线的三种毛病。手工设计奖励在开放任务上基本不泛化；sparse success 信号对长时程行为提供的指导有限；已有通用奖励模型依赖 preferences、reference demonstrations 或 local state comparisons，把监督绑在特定轨迹或比较集合上，异构数据难以复用。

至于大家常退守的 normalized [0,1] progress，作者的批评更锋利。它是 intra-trajectory coordinate（轨迹内坐标），不是 goal-conditioned cost-to-go。任务时长不同、本体不同、任务结构不同的时候，同样是 0.5，含义可能完全不在一个尺度上。

RynnValue 的答案是估计从当前观测到语言指定目标的 directed temporal cost。在 minimum-time objective（最短时间目标）假设下，这个量对应 hitting-time cost-to-go，方向性和任务条件都是清楚的，再经 potential-based shaping 就能变成 dense reward。

### 关键证据 / 图表 / 公式

Table 2 里的 Robometer (Progress only) 一行给了这节的直接支撑。同一套数据、同一个模型，只把监督目标换成 progress，平均 τ_a 就从 0.655 掉到 0.292。这说明作者对 progress 的批评不是理念之争，是可测的性能差。

## 2 Model Architecture / 序列怎么拼，捷径怎么堵

RynnValue 建在 RynnBrain 之上，并在大规模机器人数据上继续预训练。给定指令 $\ell$、本体元数据 $m$ 和一串 $K$ 个观测 $I=\{I_{t_i}\}_{i=1}^{K}$，主设定取 $K=8$。

**Grouped temporal queries（分组时间查询）。** 单个 query token 是信息瓶颈，因为时间距离估计要一次性概括物体构型、机器人与物体的交互、中间任务阶段和完成证据。作者因此给每个时间预测配一组 $N$ 个重复 query token，实现里 $N=8$。绝对价值组 $V_i$ 用 `<value>` 类型，从第二个观测起额外插入相对价值组 $R_{i-1}$，用 `<relative_value>` 类型。最终序列是

$$
x=\bigl(m,\ \ell,\ I_{t_1},V_1,\ I_{t_2},R_1,V_2,\ \dots,\ I_{t_K},R_{K-1},V_K,\ p_{\text{ver}}\bigr)
$$

同组内的 token 用双向注意力互相看，然后沿特征维拼接而不是平均

$$
\tilde h^{V}_i=H_\theta(x)_{\text{pos}(V_{i,1})}\ \|\ \cdots\ \|\ H_\theta(x)_{\text{pos}(V_{i,N})}
$$

拼接保留了不同 query 位置抓到的互补信息，得到 $Nd$ 维表示。

**Continuous temporal readouts（连续时间读出）。** 两个专用分布头输出 bin logits，数值预测完全由这两个头负责，原来的 LM head 只留给后续的自然语言分析和验证。绝对范围 $[0,512]$ 秒、相对范围 $[-256,256]$ 秒各离散成 256 个 symlog 间距的箱，用 two-hot 目标训练。推理时取 symlog 空间的期望箱心再做逆变换

$$
v_i=\operatorname{symexp}\Bigl(\sum_{b=1}^{|B_V|}c^V_b\,\operatorname{softmax}(z^V_i)_b\Bigr),\qquad
\Delta_i=\operatorname{symexp}\Bigl(\sum_{b=1}^{|B_R|}c^R_b\,\operatorname{softmax}(z^R_i)_b\Bigr)
$$

这套做法的用意是把回归变成稳定的分类。symlog 分箱跨越了时间距离的大动态范围，压缩大幅值长尾同时几乎不扭曲接近零的目标，two-hot 编码用最近的两个箱精确表示每个连续目标，让梯度幅值和目标尺度解耦。

**Value-isolation attention（价值隔离注意力）。** 这是全文最关键的一个结构设计。没有显式注意力约束时，一个时间查询可以从之前暴露的 value token 外推出自己的答案，而不去解读对应的视觉证据。产出的价值曲线看着很光滑，但对倒退、失败这类非单调事件完全不敏感。作者因此禁止不同观测的绝对与相对查询互相注意，同一观测内部的查询仍可互看。作者还进一步禁止 context token 注意到时间查询 token，避免之前的价值预测通过后续语言或视觉表示间接传播。

**语言分支。** 视觉序列处理完之后，验证提示 $p_{\text{ver}}$ 让模型先生成视频描述，再判断任务匹配和任务成功

$$
y_{\text{lang}}=\bigl(\text{Video Description: } y_{\text{vid}},\ \text{Match: } y_{\text{match}},\ \text{Success: } y_{\text{succ}}\bigr)
$$

这个自回归顺序有讲究，先说清楚看到了什么行为、什么物体交互、什么完成证据，再下匹配和成功的判断。语言输出不回流到时间头，所以失败检测这个能力是白送的，不需要额外分类头。

### 关键证据 / 图表 / 公式

Figure 1 给出整体序列结构，Figure 2(b) 画出隔离掩码的可见性格局。Table 3 的 w/o Isolation 行是这节的硬证据，去掉隔离之后平均 τ_a 从 0.675 掉到 0.482。

## 3 Learning Temporal Distance as a Reward Interface / 数据、训练和奖励接口

### 3.1 数据准备

![[papers/images/huang2026rynnvalue/RynnValue-train_page1.png|760]]

**Figure 2 训练流程与价值隔离注意力。** (a) 训练策略，含随机时间采样、时序打乱、指令错配增强和三路监督信号。(b) 价值隔离注意力，同组重复查询互相可见并能看语言视觉上下文，跨组不可见。

语料混合了真实、仿真和第一人称三类数据，超过 7000 小时。subtask 展开前是 167 万条原始 episode，经过子任务切分和 cutoff 重标注后变成 300 多万条指令条件片段。

| 数据源 | 原始 episode | 切分后片段 | 指令数 | 切分依据 |
| --- | --- | --- | --- | --- |
| AgiBot | 167,535 | 1,166,042 | 3,741 | coarse task |
| EgoDex | 338,234 | 338,234 | 2,038 | full trajectory |
| Galaxea Open-World | 16,979 | 95,671 | 11,070 | coarse task |
| InternData-A1 | 320,905 | 320,905 | 348 | full trajectory |
| Open X-Embodiment | 693,037 | 693,037 | 180,090 | full trajectory |
| RDT | 6,109 | 6,109 | 272 | per-file coarse task |
| RoboCOIN | 67,420 | 410,877 | 2,124 | coarse task |
| RoboMIND | 32,138 | 32,138 | 184 | full trajectory |
| RoboTwin | 27,414 | 27,414 | 23,527 | full trajectory |
| Soft-FOLD | 1,542 | 1,542 | 1 | per-file coarse task |
| 合计 | 1,671,313 | 3,091,969 | 223,395 | 无 |

标签怎么来的这件事是本文最省事也最聪明的地方。每个片段先定一个 completion cutoff，默认用片段终点，必要时按数据集特定的比例或时长裁剪去逼近首个语义完成观测。之后 cutoff 之前的观测按剩余时间打标，cutoff 之后的观测标零。整个过程不需要任何针对数据集的进度归一化。视频描述那一路则用 Qwen3-VL-27B 生成片段级描述，只监督语言输出，不碰时间目标。

### 3.2 训练配方

**随机时间采样。** 每个片段在不规则时间戳上随机采 $K=8$ 帧。不均匀的时间间隔破坏了均匀采样导致的近似等差价值模式，模型没法把固定采样间隔当捷径。

**时序打乱。** 一半训练序列独立采样且不做时间排序，另一半走前向偏置的时间游走并偶尔回退，回退的每步概率叫 rewind probability，实现里取 0.3。相对时间目标按呈现顺序上的相邻关系计算，因此可正可负。

作者对这两个设计的关系讲得很清楚，打乱阻止模型从序列位置回归一条刻板价值曲线，隔离注意力阻止模型从别的查询组外推。两者压制的是不同捷径，缺一不可。

**指令错配增强。** 10% 的样本把原指令换成另一条轨迹的指令，语言分支监督成 Match No 和 Success No。因为替换后原来的 completion cutoff 不再成立，绝对时间损失被 mask 掉，相对时间损失保留，理由是相对目标只衡量观测之间的时间位移，跟指令无关。这个设计让模型学会识别语言和视频对不上的情况，而不是无论看到什么都报告一条平滑的进度。

**联合目标。** 三个交叉熵损失，前两个在分布箱上，第三个在语言词表上

$$
\mathcal{L}_{\text{abs}}=-\frac{\omega}{K}\sum_{i=1}^{K}\sum_{b=1}^{|B_V|}\bigl[\text{TwoHot}_{B_V}(v^\star_i)\bigr]_b\log\bigl(\operatorname{softmax}(z^V_i)\bigr)_b
$$

$$
\mathcal{L}_{\text{rel}}=-\frac{1}{K-1}\sum_{i=1}^{K-1}\sum_{b=1}^{|B_R|}\bigl[\text{TwoHot}_{B_R}(\Delta^\star_i)\bigr]_b\log\bigl(\operatorname{softmax}(z^R_i)\bigr)_b
$$

$$
\mathcal{L}=\mathcal{L}_{\text{abs}}+\mathcal{L}_{\text{rel}}+\lambda_{\text{lang}}\mathcal{L}_{\text{lang}},\qquad \lambda_{\text{lang}}=2
$$

其中绝对目标 $v^\star_i=\max(0,\ t_G-t_i)$，相对目标 $\Delta^\star_i=t_{i+1}-t_i$，$t_G$ 是重标注的完成 cutoff。$\omega$ 是样本级掩码，指令匹配时为 1，错配时为 0。这里的 consecutive 指的是呈现序列上的相邻，不是原视频里的相邻，读的时候容易看漏。

### 3.3 推理与奖励接口

推理时关掉训练期的采样增强，观测按时间顺序排列，但价值隔离掩码保持开启，避免前面的预测影响后面的预测。

RynnValue 预测的是时间距离而不是奖励，所以要做一次符号翻转才能对上「越大越好」的价值语义

$$
\Phi_t=\Phi_\theta(I_t,\ell,m)=-v_t
$$

完成之前势为负，接近目标时趋于零。这一步保留了时间尺度，没有把预测归一化到任务特定的 $[0,1]$ 区间，这跟前面对 progress 的批评是自洽的。

### 关键证据 / 图表 / 公式

Table 1 支撑「标签便宜」这条主张，Table 6 的 curation 统计支撑「删掉的是无效标注不是稀有任务」，保留 1,436,150/1,722,966 个轨迹单元（83.35%）的同时保留了 192,989/194,967 条唯一指令（98.99%）。这两个比例的落差本身就是证据。

## 4 Experiments / 四条验证线

### 4.1 实验设置

主实验用 8B 模型，Table 2 里额外报了 4B 变体探模型规模的影响。两个时间头都是 BroNet 残差 MLP，隐藏宽度 4096、深度 8、ReLU 激活。优化器 AdamW，学习率 $1\times10^{-6}$，$\beta_1=0.9$、$\beta_2=0.95$，weight decay 0.1，常数学习率无 warm-up，梯度范数裁到 100，bfloat16 加 FSDP hybrid sharding，每设备 batch size 2。时序打乱概率 0.5，rewind 概率 0.3，指令错配比例 10%。

### 4.2 基准评测

评测跑在 Robometer 提出的 RBM-EVAL-OOD 轨迹排序赛道，976 条轨迹来自六个分布外数据集，跨机构、跨本体、跨相机视角、跨任务族。每个任务提供不同执行质量的轨迹，含失败、次优和成功三档。指标是真值质量序和预测得分序之间的 Kendall's τ_a。

因为 RynnValue 输出的是时间距离而非归一化进度，作者用最后一个查询观测的势 $-v_{\text{end}}$ 给整条轨迹打分。τ_a 只依赖相对序，所以不需要额外归一化或跨数据集校准。

| Method | USC Franka | USC Koch | USC Trossen | USC xArm | MIT Franka | UTD SO101 | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GVL | 0.250 | −0.008 | 0.292 | 0.056 | 0.306 | 0.300 | 0.199 |
| VLAC-8B | 0.271 | 0.064 | −0.417 | 0.139 | 0.072 | 0.167 | 0.049 |
| Dopamine-GRM-2.0-8B | 0.479 | 0.442 | 0.333 | 0.431 | 0.431 | 0.700 | 0.453 |
| RoboReward-4B | 0.625 | 0.332 | 0.333 | 0.528 | 0.494 | 0.700 | 0.502 |
| RoboReward-8B | 0.625 | 0.264 | 0.389 | 0.347 | 0.396 | 0.767 | 0.465 |
| Robometer (RBM-1M) | 0.646 | 0.471 | 0.653 | 0.694 | 0.601 | 0.867 | 0.655 |
| Robometer (Progress only) | 0.083 | 0.231 | 0.333 | 0.389 | 0.183 | 0.533 | 0.292 |
| ReWiND | −0.125 | 0.336 | 0.028 | −0.167 | 0.080 | −0.067 | 0.014 |
| RynnValue-4B | 0.542 | 0.488 | 0.917 | 0.667 | 0.473 | 0.933 | 0.670 |
| RynnValue-8B | 0.667 | 0.544 | 1.000 | 0.500 | 0.503 | 0.833 | **0.675** |

有个细节容易被榜单数字盖住。4B 拿 0.670，8B 拿 0.675，差距只有 0.005。作者自己也点破了，收益来自 temporal-distance 这个表述方式和配套的训练与结构设计，不是靠模型规模堆出来的。这对想复现的人是好消息，也说明这条路线的上限还没被模型容量卡住。

![[papers/images/huang2026rynnvalue/Matrix_page1.png|760]]

**Figure 3 指令与轨迹的混淆矩阵。** 行是指令，列是轨迹，格子里是预测奖励，接地良好的模型应该把质量集中在对角线上。矩阵下方数字是归一化对角边际。RynnValue 拿 0.79，最强基线 0.67。

这个分析回答的是一个很实在的怀疑，模型到底是在跟踪语言指定的目标，还是只在跟踪泛泛的视觉进度。所有基线都用公开权重在统一协议下重跑，这一点让对比可信度高不少。

### 4.3 消融

| Variant | Shuffle | Isolation | Language | Random | Relative | Average τ_a |
| --- | --- | --- | --- | --- | --- | --- |
| w/o Shuffle | ✗ | ✓ | ✓ | ✓ | ✓ | 0.189 |
| w/o Isolation | ✓ | ✗ | ✓ | ✓ | ✓ | 0.482 |
| w/o Language | ✓ | ✓ | ✗ | ✓ | ✓ | 0.537 |
| Uniform Sampling | ✓ | ✓ | ✓ | ✗ | ✓ | 0.379 |
| w/o Relative | ✓ | ✓ | ✓ | ✓ | ✗ | 0.627 |
| Full Model (8B) | ✓ | ✓ | ✓ | ✓ | ✓ | **0.675** |

这张表是全文最有说服力的部分。去掉时序打乱直接崩到 0.189，比大多数基线都差；换成均匀采样掉到 0.379。两个都是「不改模型只改数据呈现方式」的操作，掉分幅度却远大于加大模型带来的收益。可以确定的是，这类多帧价值模型对捷径的脆弱程度被严重低估了。

相对价值那一项整体只贡献 0.048，但在 USC Trossen 上去掉它会从 1.000 掉到 0.639，说明它的作用高度依赖数据集特性，不是均匀分布的收益。

### 4.4 规模化分析

![[papers/images/huang2026rynnvalue/scaling_analysis_page1.png|620]]

**Figure 4 episode 数量与任务多样性的对比缩放。** 橙线固定全部任务只抽 episode，蓝线固定每任务 episode 数只抽任务，两条线在 100% 处收敛到同一个训练集。纵轴是未见任务验证集上的平均绝对时间距离误差。

结论很干脆，episode 数量的缩放几乎立刻饱和，超过一小部分之后误差就平了；任务多样性的缩放在整个区间单调下降，过了中点还有明显收益。作者用这个实验回答的问题是，异构数据配方到底贡献了什么。答案是多样性，不是样本量。

这个结果对做数据的人很有指导价值。同一个任务反复采集很快就不再提供新信号，扩任务覆盖才是有效投入。

### 4.5 真机策略学习

![[papers/images/huang2026rynnvalue/value-case_page1.png|760]]

**Figure 5 真实轨迹上的价值曲线对比。** 两条曲线都调整成越高越接近完成。高亮区间是任务倒退期，RynnValue 的势急剧下落，Robometer 相对平坦。

![[papers/images/huang2026rynnvalue/case_study_page1.png|760]]

**Figure 6 四个真机评测任务。** 从上到下是面包放篮、锅铲盛牛排、盒子入抽屉、双臂搬箱，覆盖抓取、空间操作和铰链物体交互。

平台是双臂 Franka，两个腕部相机加左右两个第三人称相机。四个任务每个跑 20 试次。所有奖励模型都通过同一个势函数塑形接口使用

$$
r'_t=\kappa\bigl(\gamma\Phi_{t+1}-\Phi_t\bigr)+
\begin{cases}
0, & t=T\ \text{且轨迹成功}\\
-1, & \text{其他}
\end{cases}
$$

RynnValue 用 $\kappa=0.1$，Robometer 用 $\kappa=1.0$。保留稀疏完成项的理由是奖励模型预测可能有噪声，而成功标签是干净可靠的最终目标信号。离线 RL 用 IQL，基座策略是 $\pi_{0.5}$；在线 RL 用 DSRL，带任务特定的策略初始化。

| Algorithm | Baseline | 面包放篮 | 锅铲盛牛排 | 盒子入抽屉 | 双臂搬箱 | Average |
| --- | --- | --- | --- | --- | --- | --- |
| Online RL | RynnValue | 45.0% | 75.0% | 70.0% | 100.0% | **72.5%** |
| Online RL | Robometer | 35.0% | 45.0% | 65.0% | 65.0% | 52.5% |
| Online RL | Sparse | 40.0% | 45.0% | 40.0% | 70.0% | 48.8% |
| Offline RL | RynnValue | 100.0% | 90.0% | 90.0% | 50.0% | **82.5%** |
| Offline RL | Robometer | 80.0% | 80.0% | 50.0% | 45.0% | 63.8% |
| Offline RL | Sparse | 70.0% | 20.0% | 0.0% | 0.0% | 22.5% |
| SFT | 无 | 70.0% | 25.0% | 0.0% | 0.0% | 23.8% |

最有意思的是盒子入抽屉和双臂搬箱这两栏，SFT 策略是 0，稀疏奖励离线 RL 也是 0，只有带 RynnValue 的 RL 把它们做起来了。这两个任务本来就是长时程加精细对齐，稀疏信号根本不够用。

作者自己也标出了一个不漂亮的地方。盒子入抽屉的在线提升很小，从共享的 50% 起点，Robometer 到 65%，RynnValue 到 70%。原因是奖励模型只看第三人称 RGB，视觉上很像的构型在抓取稳定性和对齐精度上可能差很远，中间奖励没法校准。这段自陈写得很坦白，我觉得比很多论文的 limitation 段落诚实。

## 方法细节

把方法拆成可执行的几件事，大致是这样。

数据侧要做的是，把每条轨迹切成指令条件片段，给每个片段定一个语义完成 cutoff，然后按时间戳算剩余时间当标签，cutoff 之后一律标零。指令要过一遍清洗，去掉占位符、数据质量元数据、截断标签和非英文标注，再把只描述移动接近而没有操作目标的段落删掉。

模型侧要做的是，把观测序列和两类价值查询组交错拼成一个多模态序列，每个查询组用 8 个重复 token 并沿特征维拼接，两个 BroNet 头分别输出 256 个 symlog 箱上的分布，用 two-hot 目标训练。注意力上加两道掩码，一道禁止跨观测的价值查询互看，一道禁止上下文 token 回看价值查询。

训练侧要做的是，不规则采 8 帧，一半样本打乱时序且带 0.3 的回退概率，10% 样本做指令错配并对绝对损失打掩码，三个交叉熵按 $1:1:2$ 加权。LM output projection 保持冻结，但语言损失的梯度仍然透过它更新主干。两个时间头和主干之间没有 stop-gradient。

部署侧要做的是，推理关增强、开隔离、按时间序输入，输出取负号变势函数，再套 potential-based shaping 公式接进任何 RL 算法。

## 实验设置、数据集、基线、指标

评测数据集是 RBM-EVAL-OOD，六个子集 USC Franka、USC Koch、USC Trossen、USC xArm、MIT Franka、UTD SO101，共 976 条轨迹，标注了失败、次优、成功三档执行质量。

基线覆盖三类。in-context 价值学习那一类有 GVL 和 ReWiND；偏好或过程奖励建模那一类有 VLAC-2B/8B、RoboDopamine、Dopamine-GRM-2.0-8B、RoboReward-4B/8B、Robometer；还有一个 Robometer 的 progress-only 消融，专门用来对照本文的核心论点。

主指标是 Kendall's τ_a。辅助指标有归一化对角边际（指令轨迹对齐）、未见任务上的平均绝对时间距离误差（缩放分析）、真机成功率和成功回合的平均 action chunk 数。

真机侧是双臂 Franka，四相机，四个任务各 20 试次。离线评测用固定初始构型，在线评测除盒子入抽屉外都随机化初始物体构型。

## 主要结果、消融或对比

主结果那三个数字值得单独拎出来。RBM-EVAL-OOD 上 8B 拿 0.675，压过全偏好监督的 Robometer 0.655；在偏好无关的方法里，把此前最强的 0.502 提到了 0.670（4B）和 0.675（8B）；对照 progress-only 的 0.292，差距超过一倍。

消融里的排序是这样，去掉时序打乱最致命（0.189），其次是均匀采样（0.379），再次是去掉隔离注意力（0.482），然后是去掉语言监督（0.537），最轻的是去掉相对价值（0.627）。这个排序传达的信息是，捷径压制的价值大于辅助监督的价值。

真机 RL 那边，在线平均 72.5% 对 52.5% 对 48.8%，离线平均 82.5% 对 63.8% 对 22.5%，SFT 只有 23.8%。执行效率上也有收益，面包放篮离线 100% 成功且平均只用 16.8 个 action chunk，Robometer 是 80% 加 18.9 个，SFT 是 70% 加 24.8 个。

## 图表、公式与表格线索

| 编号 | 内容 | 支撑哪条主张 | 读的时候注意什么 |
| --- | --- | --- | --- |
| Figure 1 | 模型总览与三个下游用途 | 单一价值接口可复用 | 语言分支不回流到时间头，这是失败检测能力白送的原因 |
| Figure 2(a) | 训练策略四件套 | 捷径压制的设计动机 | 相对目标按呈现顺序算，可正可负 |
| Figure 2(b) | 价值隔离掩码 | 跨组不可见 | 同组内仍可互看，隔离粒度是组不是 token |
| Figure 3 | 指令轨迹混淆矩阵 | 预测跟踪语言目标而非泛化视觉进度 | 所有基线用公开权重统一重跑，对比协议干净 |
| Figure 4 | 数据量与多样性对比缩放 | 异构配方的收益来自多样性 | 两条线在 100% 收敛到同一训练集，是公平对照 |
| Figure 5 | 价值曲线定性对比 | 对倒退敏感、近完成不早饱和 | 两个模型输出尺度不同，只能比形状不能比绝对值 |
| Figure 6 | 四个真机任务 | 任务覆盖抓取、空间、铰链 | 这些任务及场景都不在奖励模型训练语料里 |
| Table 1 | 数据混合构成 | 标签便宜且能跨源统一 | 切分依据一列暴露了各数据源标注粒度差异很大 |
| Table 2 | RBM-EVAL-OOD 主结果 | 无偏好超越偏好监督 | 4B 与 8B 只差 0.005 |
| Table 3 | 组件消融 | 捷径压制是主要收益来源 | w/o Shuffle 掉到 0.189，比多数基线还差 |
| Table 4 | 真机 RL 结果 | 可作为 dense reward 接口 | 每格只有 20 试次 |
| Table 6 | 数据清洗统计 | 删的是无效标注不是稀有任务 | 单元保留 83.35% 对指令保留 98.99% |
| Eq. 1 | 多模态序列构造 | 查询交错方式 | 相对组插在绝对组之前 |
| Eq. 4 | symlog 期望解码 | 分布头如何回到连续值 | 解码在 symlog 空间做期望再逆变换 |
| Eq. 10 | 势函数定义 | 时间距离到价值语义的翻转 | 保留时间尺度，不做 [0,1] 归一化 |
| Eq. 11 | 塑形后的奖励 | 真机 RL 的统一接口 | 保留了稀疏完成项，κ 两个模型取值不同 |

## 主张-证据-边界矩阵

| 主张 | 证据 | 边界 |
| --- | --- | --- |
| temporal distance 比 normalized progress 是更好的监督目标 | Table 2 中 0.675 对 0.292 | 对照组只有 Robometer 一家的 progress 消融，没有跨多个 progress 方法验证 |
| 不需要偏好标注也能超过偏好监督 SOTA | Table 2 中 0.675 对 0.655 | 领先 0.02，且在 USC xArm 和 MIT Franka 两个子集上其实低于 Robometer |
| 捷径压制设计是性能的主要来源 | Table 3，去 shuffle 掉到 0.189 | 消融只在 8B 上做，没有验证小模型是否同样脆弱 |
| 数据配方的收益来自任务多样性而非样本量 | Figure 4 两条曲线走势相反 | 只报了平均绝对误差一个指标，没有报同一实验下的 τ_a |
| 可作为真机 RL 的 dense reward 接口 | Table 4，在线 72.5%，离线 82.5% | 四任务各 20 试次，且 κ 是逐模型调过的超参 |
| 零样本泛化到未见任务、本体和视角 | RBM-EVAL-OOD 全部是 OOD 数据集，真机任务不在训练语料 | 都是桌面双臂或单臂抓放类，没有灵巧手和移动操作 |
| 模型规模不是瓶颈 | 4B 0.670 对 8B 0.675 | 只测了两个规模，没有更小的点来确认下界在哪 |

## 局限与可追问点

作者自己承认的有三条。当前只从一小段采样观测估计时间距离，扩到更长时程和流式推理才能真正当在线奖励源用；目标假设的是近似最短时间目标，能耗、安全、精度这类任务特定代价还没进来；末端执行器种类窄，灵巧手和移动操作都还没覆盖。

我另外想追问几个。

κ 这个塑形强度对 RynnValue 取 0.1 而对 Robometer 取 1.0，差了一个数量级。论文没解释这个取值怎么定的，也没有做 κ 的敏感性分析。如果 RynnValue 的优势有一部分来自更合适的 κ，那这个对比就没有看上去那么干净。

再一个是 cutoff 重标注。作者说默认用片段终点，必要时按数据集特定的比例或时长裁剪。这个「必要时」是人工判断还是有规则，论文没写清楚。既然全文卖点是标签便宜且自动，这一步的人工含量应该量化。

第三个是评测集规模。RBM-EVAL-OOD 六个子集加起来 976 条轨迹，单个子集的 τ_a 波动很大，USC Trossen 上 RynnValue-8B 拿到 1.000 这种满分本身就提示该子集样本很少。平均值 0.675 与 0.655 的差距是否稳健，需要看方差或置信区间，论文没给。

最后一个偏方向性的。temporal distance 假设「完成得越快越好」，但很多操作任务里慢而稳比快而险更可取。把 minimum-time 换成别的代价结构之后，这套 timestamp 导出标签的便宜性还剩多少，是个真问题。

## 与当前库的连接

跟 [[@wang2026wvm]] 是同一轴上的两篇。WVM 走的是世界模型内部做价值估计和规划，RynnValue 走的是独立价值模型对外提供奖励接口。两篇并排看能看清一个分歧，价值到底该嵌在策略里还是抽出来当可复用组件。

跟 [[@yu2026warp-rm]] 和 [[@liu2026steam]] 构成奖励建模与数据筛选这条线。WARP-RM 和 STEAM 处理的是怎么用奖励信号筛数据，RynnValue 提供的是这类信号本身可以怎么更便宜地拿到。

跟 [[@qian2026wam-rl]] 的关系值得画出来。WAM-RL 用 reconstruction-based reward，靠比较想象轨迹和执行轨迹的相似度造 dense reward，那是个自监督的、语义偏弱的信号。RynnValue 给的是语言条件的、语义明确的信号。两条路解决的是同一个痛点，真机 RL 缺 dense reward，但代价结构完全不同，一个不需要额外模型，一个需要一个 8B 的外部模型在线推理。

跟 [[@yu2026wm-dagger]] 的连接在失败处理上。WM-DAgger 用世界模型合成恢复数据，RynnValue 则让价值曲线对倒退敏感从而能检测失败。Figure 5 里那段势的急剧下落，正好是 WM-DAgger 想要触发数据聚合的时刻。

跟 [[@intelligence2025pi06-vla-that-learns]] 的 RECAP 也能对照。π*0.6 用经验强化学习自改进，同样需要价值估计，两篇对「价值信号从哪来」给的答案不同。

## 精读路线 / 为什么需要回看

第一遍只读 Section 1 加 Table 2，弄明白 temporal distance 和 normalized progress 的差别，以及这个差别在数字上有多大。这两处读完，全文的立论就抓住了。

第二遍读 Section 2 的 value-isolation attention 加 Section 3.2.1 的两个采样设计，然后直接跳 Table 3。这是本文技术含量最高也最可迁移的一块，任何做多帧价值或多帧奖励模型的工作都该看一眼这张消融表。

第三遍读 Section 4.3 的缩放分析和 Section 4.5 的真机部分。前者影响数据采集策略的判断，后者影响这个模型能不能真接进你的 RL 流程。

需要回看的场景有几个。要给真机 RL 找 dense reward 的时候回看 Eq. 10 和 Eq. 11，那是接口定义。要做多帧视觉价值模型的时候回看 Table 3，先确认自己有没有踩同样的捷径坑。要规划数据采集预算的时候回看 Figure 4，那条橙线的早期饱和是个很贵的教训。要做失败检测的时候回看 Section 2 的语言分支设计，那套 Match 和 Success 的自回归顺序是可以直接抄的。
