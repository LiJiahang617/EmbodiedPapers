---
tags:
  - bilingual-reading
paper: "[[@liu2026confal-wm]]"
source_pdf: "[[papers/pdfs/liu2026confal-wm.pdf]]"
images: "papers/images/liu2026confal-wm/"
image_index: "[[papers/images/liu2026confal-wm/index.md]]"
arxiv: "2608.25572v1"
created: 2026-09-05
---

# ConfAL-WM: Confidence-Guided Active Learning for Action-Conditioned World Models

paper:: [[@liu2026confal-wm]]
pdf:: [[papers/pdfs/liu2026confal-wm.pdf]]
images:: [[papers/images/liu2026confal-wm/index.md]]

> [!warning] 版本与证据状态
> 本稿按 arXiv 2608.25572v1 逐节整理，正文 9 页加 21 页附录，模板带 Impact Statement，看格式是投 ICML 系会议的预印本，正文没有声明录用状态。项目页是 ConfAL-WM.github.io。主对比跑 3 个种子（42、3407、123）并给 paired bootstrap 95% 区间，选择准则消融只跑种子 42。全文没有下游策略评测，所有结论都建立在 EWMBench 的代理指标上，作者自己也在局限里承认了这一点。以下涉及领先与提升的表述均按作者报告处理。

## 一句话总结

这篇要解决的不是「世界模型怎么预测得更准」，而是「后训练的算力和数据该往哪儿投」。作者在 EVAC 的 UNet 解码器上挂了一个 8.2M 的置信度探针，让它在潜空间预测稠密风险图，然后把同一个信号同时用在两处，选哪些任务和场景值得进后训练集，以及训练时哪些帧和哪些 patch 该加权。

## 核心词汇速查

| English | 中文 | 在论文中的作用 |
| --- | --- | --- |
| action-conditioned world model | 动作条件世界模型 | 给定动作预测未来观测的模型，本文的优化对象 |
| EVAC, EnerVerse-AC | 本文的骨干世界模型 | 基于 UNet 潜扩散、在 AgiBot World 上预训练 |
| confidence probe | 置信度探针 | 挂在 UNet 解码器特征上的轻量预测头 |
| dense confidence map | 稠密置信图 | 潜空间上 $H_p \times W_p$ 的逐 patch 可靠性预测 |
| risk map | 风险图 | $r = 1 - \hat q$，置信度的补 |
| decoder feature tapping | 解码器特征取点 | 从第 $\ell$ 个解码块取特征，权衡语义与空间分辨率 |
| velocity prediction | 速度预测 | EVAC 的扩散参数化，$\hat v^{(\tau)}$ 对 $v^{(\tau)}$ |
| EMA-calibrated random threshold | EMA 校准随机阈值 | 用批内分位数在线估计阈值区间并 EMA 平滑 |
| active learning | 主动学习 | 用模型自身的不确定性挑数据 |
| task-level prescreening | 任务级预筛 | 用探针估任务难度并分配采样配额 |
| mean / tail / persistent risk | 均值 / 尾部 / 持续风险 | 三种把稠密风险聚合成任务分数的准则 |
| frame weighting | 帧加权 | 把帧内空间均值风险均匀施加到该帧所有 patch |
| patch weighting | patch 加权 | 保留原始逐 patch 风险作为局部权重 |
| EWMBench | 具身世界模型评测基准 | 本文的评测协议来源 |
| Traj-HSD / Traj-Dyn / Traj-nDTW | 三项轨迹一致性指标 | 衡量生成视频里机器人轨迹的合理性 |
| ECE, Brier | 期望校准误差、Brier 分数 | 附录用来检验置信度是否是校准概率 |

## 摘要

论文的观察很具体。动作条件世界模型已经成为具身预测、规划与合成数据生成的重要底座，但它们在新任务和新场景分布下的误差从来不是均匀铺开的，而是集中在机器人手臂、被操作物体、接触区域和被遮挡物体这些局部时空区域上。

由此推出的做法是，后训练不该只是全局地加更多数据，而应该按「模型可能在哪里失败」来选数据和加强训练。作者在 EVAC 上挂一个轻量置信度探针，从 UNet 解码器特征预测潜空间的稠密置信图，再把这些图聚合成任务级、帧级和 patch 级分数，同时服务于高效数据选择和局部训练增强。

流水线分三步走。先用一小部分目标域数据重训探针并热身 EVAC，得到 EVAC-v1；再用探针做任务级预筛，分配采样配额；最后在选出的数据上重训，可选地叠加帧或 patch 加权的数据增强。

RoboTwin2.0 上的实验显示，置信度引导的选择提升了后训练效率，稠密的帧与 patch 加权进一步改善预测质量和具身轨迹一致性，优于标量奖励、进度和裁判类打分基线。

## 论文主线

![[papers/images/liu2026confal-wm/An_introduction_of_our_work_page1.png|760]]

Figure 1 把全文分成三块。A 块是带探针的世界模型推理，给定参考帧和动作条件，UNet 潜扩散世界模型生成未来，探针在解码器特征上预测稠密风险图并叠在预测帧上。B 块是置信度引导的主动学习，风险信号同时用于挑数据和给帧、patch 加权，图里画出了 0.5 / 1 / 1.5 三档权重。C 块是两个代表性 episode 的重训对比，从 GT、Warmup v1、Frame retrained 到 Frame+Patch。

论证顺序也照这个结构。第一步先证明置信度是有意义的风险信号，Section 4.2 用 Spearman、AUROC、IoU 和时间稳定性四组统计回答 Why Confidence。第二步再证明这个信号能换成后训练收益，Section 4.3 用 EWMBench 九项指标回答 Why Active Learning。

这条线里最容易被忽略的是「两种用法共用一个信号」这件事。作者反复强调 confidence 相比标量奖励、进度、裁判模型的区别不在于能不能排序，而在于能不能给出 patch 级的预测风险。排序谁都能做，定位只有稠密信号能做。

## 贡献与结论对照

| 作者声称的贡献 | 对应证据 | 可接受的结论 | 不能外推的部分 |
| --- | --- | --- | --- |
| 提出分阶段的置信度引导主动学习流水线 | Section 3.2 与 Section 4.3 的主对比 | 在固定数据预算下确实优于随机与标量打分 | 只在 EVAC + RoboTwin2.0 一个组合上验证 |
| 把稠密置信度适配到 UNet 世界模型 | Figure 3 的解码器层对比，8.2M 探针 | 解码器特征比瓶颈特征更适合定位 | 层号 $\ell$ 的完整消融没给，只给了三层可视化 |
| 用 EMA 自适应阈值替代随机二值区间 | Figure 9，界从 0.20/0.70 收敛到约 0.0705/0.2610 | 在线校准比手工迁移固定阈值稳 | 没有与固定阈值的下游对照 |
| 提出 frame 与 patch 加权的数据增强 | Table 2，Fr.+Patch 在 8/9 项最好 | 稠密加权确实带来额外收益 | Scene Consistency 反而低于 frame-only |
| 优于标量奖励、进度、裁判打分 | Table 2、Table 4、Table 5 | 在选择-only 一档确实全面领先 | Semantics 的 bootstrap 区间跨 0 |
| mean risk 是最好的采集准则 | Table 3，7/9 项最好 | 均值聚合抑噪且反映整体难度 | 只跑种子 42，无重复 |

## 结构地图

| 原文 section | 主要内容 | 在论证链中的工作 |
| --- | --- | --- |
| 1 Introduction | 误差局部化的观察与四条贡献 | 把「加数据」改成「按失败位置选数据并加权」 |
| 2 Related Work | 世界模型与评测、稠密置信与标量打分、主动学习 | 划出与 C3、SAVE、PhysisForcing 的边界 |
| 3 Method | 探针定义、EMA 阈值、选择准则、加权重训 | 完整交代机制 |
| 3.1 Dense Confidence Probe | 置信定义、解码器取点、EMA 阈值、BCE 目标 | 建立稠密风险信号 |
| 3.2 Confidence-Guided Active Learning | 三阶段流水线、三种选择准则、帧与 patch 加权 | 把信号变成训练预算的分配规则 |
| 4 Experiments | 两个问题，Why Confidence 与 Why Active Learning | 分开验证信号有效性与下游收益 |
| 4.1 Experimental Setup | 数据划分、实现细节、基线、评测指标 | 交代可比性条件 |
| 4.2 Why Confidence? | 定性定位、多尺度排序、时空行为 | 证明风险信号有意义 |
| 4.3 Why Active Learning? | 主对比与选择准则消融 | 证明信号能换成后训练收益 |
| 5 Conclusion | 三条局限，跨架构迁移、表征评估、评测协议 | 收束并自划边界 |
| Appendix A | 潜空间误差构造与 EMA 阈值推导 | 补方法的数学细节 |
| Appendix B.1 | 聚合方式、空间定位、校准、参数敏感性 | 支撑「序数信号而非校准概率」这个定位 |
| Appendix B.2 | 聚合结果、paired bootstrap、逐种子明细 | 提供统计强度 |
| Appendix B.3 | 六个 episode 的重训演化 | 定性说明 patch 加权改善了什么 |
| Appendix B.4 | 置信可视化的最好与最差样例 | 展示信号的上下界 |

## 按原文 section 精读

### 1 Introduction

引言从一个经验观察起步。无论是零样本迁移到新数据集，还是在已有域上做后训练，预测误差很少均匀分布在整段视频上，它们集中在移动的机械臂、被操作物体、接触区域、遮挡处和长时交互误差上。作者引了两条近期工作作旁证，置信度感知的视频生成和物理强化的世界模拟都指向同一件事，不可靠或物理不一致的区域通常在空间和时间上是局部的。

这个观察直接推出一条后训练策略，不要全局地加数据，而要按模型可能在哪里失败来选择和增强数据。

第二段交代技术路线并点明与前人的差别。作者在 EVAC 上挂轻量探针。这里有一处工程上的关键区分，之前基于 DiT 的稠密置信估计里每个潜 token 天然对应一个视频 patch，UNet 没有这种对应，必须显式设计特征取点。作者选解码器特征而不是瓶颈特征，理由是解码器特征保留更强的空间局部性，同时仍从潜扩散骨干带来全局上下文。另外把之前置信训练用的随机二值阈值区间换成了自适应 EMA 阈值。

第三段是流水线的三阶段。EVAC 原本在 AgiBot World 上预训练，作者用 RoboTwin2.0 做后训练数据以评估新任务新场景分布下的主动学习效果。先用一小部分数据重训探针并热身 EVAC 得到 EVAC-v1；再用探针做快速任务级预筛，难任务给更大采样配额，易任务少选场景；场景选完之后有两条重训路径，直接用选出的数据训 EVAC-v2，或者再让 EVAC-v1 和探针跑一遍推理拿到帧级与 patch 级置信分数，用它们加权。后一条路多花一次推理和打分的成本，换来置信度引导的数据增强。

作者把这个设计概括成置信度的两个角色，选择层面估计哪些任务和场景值得更多重训预算，训练层面定位哪些帧和 patch 该受到更强监督。这正是它与标量奖励、进度或裁判模型的分界，后者能给轨迹或帧排序，但通常给不出 patch 级的预测风险。

#### 关键证据 / 图表 / 公式

- 四条贡献分别对应 Section 3.2 的流水线、Section 3.1 的探针与 EMA 阈值、Section 3.2 的加权重训、Section 4.3 的对比实验。
- 引言里 UNet 与 DiT 的对比是全文的技术起点。这条区分成立与否决定了「解码器取点」这个设计是不是必要，而论文只给了 Figure 3 的三层可视化，没给瓶颈特征的定量对照。

### 2 Related Work

相关工作分三块，每块都在给方法定坐标。

世界模型与评测这块交代了骨干和评测协议的来源。EVAC 是 UNet 骨干，在 AgiBot World 上预训练，作者在 RoboTwin2.0 上做后训练，面对的是新任务、新场景和新机器人本体。最接近的是 C3，它在 DiT 视频模型里做稠密置信估计。EWMBench 从重构、场景、运动与语义四个维度评具身世界模型，是本文的主要评测协议。

稠密置信、奖励、进度与裁判信号这块把对照组一次列全。S3 分析生成式视频模型的不确定性，C3 引入稠密校准置信图，PRM-as-a-Judge 提供带宏观与微观信号的过程级机器人审计。作者的区分句是，本文的置信度还额外充当采集分数和局部训练权重。标量类的四个是 GVL（上下文价值学习估时间进度）、RoboReward（通用视觉语言机器人奖励）、Robometer（帧级进度加轨迹偏好）和 LRMs（在线生成过程与完成奖励）。

局部化监督这块补了两条平行路线。CD-LAM 通过聚焦本体的重构和动作感知目标减少与动作无关的潜偏置，PhysisForcing 通过强调物理信息量大的交互区域增强物理一致性。作者说本文用世界模型置信度识别这类区域，并用于主动选择和 patch 加权重训。

主动学习这块最值得看的是与 SAVE 的对比。Römer 等人推导 velocity-field disagreement 来量化 flow-based VLA 的认知不确定性，并用它给任务和初始场景排优先级做主动多任务微调。作者承认目标一致，都想用模型不确定性降低适配成本，但区分点很清楚，SAVE 作用在动作策略的不确定性上，本文估计的是稠密视频预测置信度，且同时用于数据选择和局部世界模型重训。

#### 关键证据 / 图表 / 公式

- 这一节没有数字，但它确定了 Section 4.1 的六个基线来源，读实验表时要回来对照每个基线原本是干什么的。
- 作者主动说明不与 C3 直接比较，理由是 C3 为 DiT 风格视频世界模型设计，直接比不完全公平。这个理由合理，但也留下一个缺口，最接近的方法没有被对照。

### 3 Method

#### 3.1 Dense Confidence Probe for UNet World Models

![[papers/images/liu2026confal-wm/Confidence_probe_training_and_inference_page1.png|760]]

置信度的定义是「局部预测误差低于某阈值的预测概率」。在 EVAC 里扩散模型对真值目标 $v^{(\tau)}$ 预测去噪方向 $\hat v^{(\tau)}$。对预测的未来帧 $t$ 和潜 patch $(i,j)$，局部平均绝对误差定义为

$$
m^{(\tau)}_{t,(i,j)} = \frac{\sqrt{1-\bar\alpha_\tau}}{|\mathcal P_{i,j}|}\sum_{p\in\mathcal P_{i,j}}\big|\hat v^{(\tau)}_{t,p}-v^{(\tau)}_{t,p}\big|
= \frac{1}{|\mathcal P_{i,j}|}\sum_{p\in\mathcal P_{i,j}}\big|\hat z^{(\tau)}_{t,p}-z^{(0)}_{t,p}\big|
$$

这里 $p=(c,x,y)$ 索引潜张量里的一个通道-空间条目，$\mathcal P_{i,j}$ 是探针 patch $(i,j)$ 对应的潜区域，$z^{(0)}$ 是真值视频编码出的干净潜，$\hat z^{(\tau)}$ 是从 $\hat v^{(\tau)}$ 闭式恢复的预测。这个等价形式的意义是构造置信目标时不必跑完整条反向扩散轨迹。附录 A.1 给了完整推导，核心是

$$
\hat z^{(\tau)} - z^{(0)} = \sqrt{1-\bar\alpha_\tau}\,\big(\hat v^{(\tau)}-v^{(\tau)}\big)
$$

也就是说在固定扩散时间步下，干净潜重构误差与速度预测误差只差一个标量因子。

二值置信目标是 $q_{t,(i,j)} = \mathbb I\{m^{(\tau)}_{t,(i,j)} < \theta_t\}$，$\theta_t$ 从自适应区间里随机采样。

![[papers/images/liu2026confal-wm/decoder_index_mean_page1.png|560]]

探针挂在第 $\ell$ 个 UNet 解码块的特征 $h^{(\ell)}_{\text{dec}}$ 上，输出

$$
\hat q_t = \sigma\Big(f_\phi\big(h^{(\ell)}_{\text{dec}}, e_\tau, e_\theta\big)\Big) \in [0,1]^{H_p\times W_p}
$$

其中 $e_\tau$ 是扩散时间步嵌入，$e_\theta$ 是采样阈值嵌入。探针内部依次是通道投影、空间 Transformer 层、时间 Transformer 层和逐 patch 输出头。解码器层号 $\ell$ 让探针在粗语义上下文与更细空间分辨率之间权衡，Figure 3 用同一帧对比了 VAE 潜（$40\times 64$）与 $\ell=5$（$20\times 32$）、$\ell=8$、$\ell=11$（均 $40\times 64$）的通道平均特征。

EMA 校准随机阈值是这一节的第二个设计。训练步 $s$ 上取批内局部误差分布的上下分位数并做 EMA。

$$
p^{(s)}_l = \text{Quantile}_{0.1}\big(m^{(s)}\big),\qquad p^{(s)}_h = \text{Quantile}_{0.9}\big(m^{(s)}\big)
$$

$$
l^{(s)} = (1-\gamma_s)l^{(s-1)}+\gamma_s p^{(s)}_l,\qquad h^{(s)} = (1-\gamma_s)h^{(s-1)}+\gamma_s p^{(s)}_h
$$

更新率 $\gamma_s$ 在学习率热身期较大、之后显著变小，先快速初始化再稳定在线校准。每个预测未来帧独立采一个 $\theta_t \sim \mathcal U(l^{(s)}, h^{(s)})$，同一帧内所有空间 patch 共享这个阈值。

探针用 BCE 训练，训练时 EVAC 骨干冻结，梯度只走 $f_\phi$。推理时的稠密风险图是 $r_{t,(i,j)} = 1-\hat q_{t,(i,j)}$。

#### 关键证据 / 图表 / 公式

![[papers/images/liu2026confal-wm/Tensor_feature_map_page1.png|560]]

- Figure 8（附录 A.1）画出 patch 级误差怎么从通道维平均再在对齐区域上池化，是 Equation 1 与 Equation 20 的图解。
- 附录 A.2 给了随机阈值的一个漂亮性质。对固定局部误差 $m$，把 $\theta$ 边缘化后得到连续目标 $\text{clamp}\big((h-m)/(h-l),0,1\big)$，而这正是 BCE 下的最优预测。所以二值监督在期望意义上诱导出一个随误差单调下降的连续置信排序。
- 附录 A.2 的实现数字值得记，RoboTwin2.0 上初始化 $l^{(0)}=0.20$、$h^{(0)}=0.70$，$S_{\text{warm}}=300$，$\gamma$ 从 0.20 降到 0.002，6000 步探针训练后界稳定在约 $l=0.0705$、$h=0.2610$。初值和收敛值差了三倍多，这条数字本身就说明为什么固定阈值跨数据集迁移不了。

![[papers/images/liu2026confal-wm/ema_threshold_evolution_zoom.png|420]] ![[papers/images/liu2026confal-wm/ema_threshold_evolution.png|420]]

#### 3.2 Confidence-Guided Active Learning

流水线分三步。先在数据池的一小部分上训探针并热身 EVAC，得到的 EVAC-v1 用于任务级预筛，代表性 episode 估计任务难度并决定每个任务的候选配额，再在每个任务内随机采样 episode。第二步，候选子集可以直接用于 selection-only 的 EVAC-v2 重训，也可以再跑一遍推理和置信打分，用得到的置信图给 EVAC-v2 的训练目标加权。

三种基于风险的选择准则各有侧重。均值风险把稠密风险图在所有空间位置和预测未来帧上平均，衡量整体预测难度。尾部风险强调严重的局部失败，把所有 patch 风险展平成长度 $K=TH_pW_p$ 的向量升序排序后取最高的 $\eta$ 比例平均。

$$
S_{\text{mean}} = \mathbb E_{t,(i,j)}\big[r_{t,(i,j)}\big],\qquad
S_{\text{tail}} = \frac{1}{\lceil \eta K\rceil}\sum_{n=K-\lceil \eta K\rceil+1}^{K} r_{[n]}
$$

持续风险捕捉跨多帧反复出现的高风险局部失败，先在帧内取最高 $\eta_p$ 比例 patch 的平均得到帧分数 $u_t$，再在帧间取最高 $\eta_t$ 比例的平均。

$$
u_t = \frac{1}{\lceil \eta_p K_p\rceil}\sum_{n=K_p-\lceil \eta_p K_p\rceil+1}^{K_p} r_{t,[n]},\qquad
S_{\text{persistent}} = \frac{1}{\lceil \eta_t T\rceil}\sum_{n=T-\lceil \eta_t T\rceil+1}^{T} u_{[n]}
$$

帧加权与 patch 加权被统一成一个插值形式。

$$
r^{(\alpha)}_{t,(i,j)} = \mathbb E_{(i',j')}\big[r_{t,(i',j')}\big] + \alpha\Big(r_{t,(i,j)} - \mathbb E_{(i',j')}\big[r_{t,(i',j')}\big]\Big),\qquad \alpha\in[0,1]
$$

$\alpha=0$ 时帧内所有 patch 拿到相同的帧级风险，$\alpha=1$ 时恢复原始 patch 级风险图，中间值保留帧级基线并加入局部残差调制。分位数归一化并裁剪后记为 $\tilde r^{(\alpha)}$，再转成局部损失乘子。

$$
w_{t,(i,j)} = 1+\lambda_{\text{eff}}(s)\,\tilde r^{(\alpha)}_{t,(i,j)},\qquad
\mathcal L_{\text{WM}} = \frac{\mathbb E_{t,(i,j)}\big[w_{t,(i,j)}\ell_{t,(i,j)}\big]}{\mathbb E_{t,(i,j)}\big[w_{t,(i,j)}\big]}
$$

其中 $\lambda_{\text{eff}}(s)=\lambda_{\text{conf}}\min(1, s/s_{\text{warm}})$ 在前 $s_{\text{warm}}$ 步线性增强加权强度。置信图在 EVAC 重训时被 detach，梯度只走世界模型。

#### 关键证据 / 图表 / 公式

- Equation 9 的 $\alpha$ 插值是设计上最讨巧的一处，它把 frame-only 与 patch-level 变成同一个公式的两端，理论上可以扫 $\alpha$。但论文只报了 frame（$\alpha=0$）与 Fr.+Patch 两档，中间值没扫。
- Equation 10 的分母做了归一化，保证加权不改变整体损失尺度，这是防止加权变相调学习率的必要步骤。
- $\eta$、$\eta_p$、$\eta_t$ 三个比例的具体取值正文没给。

### 4 Experiments

实验被明确拆成两个问题，置信信号是否真的指示世界模型的预测误差，以及置信引导的主动学习能否改善后训练效率和最终质量。

#### 4.1 Experimental Setup

数据设置是一个跨任务、跨场景、跨本体的迁移。EVAC 在 AgiBot World 上预训练，主动学习与后训练在 RoboTwin2.0 的一个子集上做，用 Aloha-AgileX 双臂机器人的数据，覆盖 50 个操作任务，每个任务 500 个随机化场景，总共 24,992 段视频，视频长度从 98 帧到 578 帧。

实现细节里几个数字要记住。探针训练时整个 EVAC 骨干冻结，只优化 $f_\phi$；EVAC-v1 热身和 EVAC-v2 重训时 UNet 去噪器和两个投影模块可训，VAE、CLIP 嵌入器和动作条件重采样器保持冻结。EVAC 完整模型约 2.33B 参数，探针约 8.2M。用 6,248 个 episode（约 25% 数据）做探针训练和 EVAC-v1 热身，剩下 18,244 个构成候选池，从中选 7,298 个做 EVAC-v2 重训。AdamW，学习率 $5\times 10^{-5}$，fp16，默认 4,000 优化步，两张 A800。置信打分时 EVAC-v1 在 $\tau\in[50,200]$ 的三个扩散时间步上平均探针分数。主对比跑三个随机种子 42、3407、123，正文报均值。

基线里作者主动说明不与原版 C3 直接比，因为它是为 DiT 风格视频世界模型设计的，直接比不完全公平。主要对比集中在主动学习的打分方法上，RoboReward、GVL、Robometer-Prog、Robometer-Pref、PRM-as-Judge、LRMs，再加一个 Random。

评测follow EWMBench。PSNR 和 SSIM 衡量低层重构质量，Scene consistency 衡量布局与物体保持，Logics 评估更高层的物理与交互合理性，Sem.-CLIP 和 Sem.-BLEU 衡量视觉语义与文本语义一致性，Traj-HSD、Traj-Dyn、Traj-nDTW 评估机器人轨迹，数值越高越好。

#### 关键证据 / 图表 / 公式

- 数据划分这里有一处对不上。6,248 加 18,244 是 24,492，比声明的 24,992 少 500，论文没有交代这 500 条的去向。按 50 个任务每任务 10 条估计，可能是留作评测，但正文没说。
- 「$\tau\in[50,200]$ 的三个时间步平均」是打分成本的关键参数，但论文没给这个区间和数量的敏感性分析。
- 7,298 / 18,244 约等于 40%，这是所有方法共享的固定数据预算，主对比的可比性建立在这个预算上。

#### 4.2 Why Confidence?

![[papers/images/liu2026confal-wm/Qualitative_confidence_visualization_page1.png|760]]

定性部分先看 Figure 4。作者在 50 个预筛任务里各取一个 episode，用 EVAC-v1 生成预测和置信图。风险图响应的是空间局部失败而不是全局视频质量，高风险区域常出现在移动的机械手、物体交互、接触处和临时被遮挡的物体周围。图里给了最好与最差两个样例，patch 级 Spearman 分别是 0.713（place_container_plate, ep290, frame 122）和 0.241（place_phone_stand, ep308, frame 73）。把最差样例一起放出来，比只放最好样例诚实得多。

![[papers/images/liu2026confal-wm/Validity_of_confidence_as_a_latent-space_risk_signal_page1.png|760]]

定量部分是 Figure 5 和 Table 1。潜空间里风险与 oracle 误差的 Spearman 相关在 patch、frame、task 三个尺度分别是 0.540、0.590、0.595。检测误差最高的前 5% patch 时 AUROC 0.761、AUPRC 0.146，随机基线分别是 0.5 和 0.05。

| Property | Metric | Result |
| --- | --- | --- |
| Multi-scale ranking | Patch / Frame / Episode Spearman ($\uparrow$) | 0.540 / 0.590 / 0.595 |
| High-error detection | AUROC / AUPRC@top-5% ($\uparrow$) | 0.761 / 0.146 |
| Spatial agreement | Top-5% IoU ($\uparrow$) | 0.130 |
| Temporal stability | Adjacent-frame IoU ($\uparrow$) / Flicker ($\downarrow$) | 0.740 / 0.005 |
| Temporal alignment | Peak correlation ($\uparrow$) / \|lag\| ($\downarrow$) | 0.602 / $\approx 0$ |

时空行为这一栏最能说明信号的性质。相邻帧的高风险区域 IoU 有 0.740、闪烁分只有 0.005，说明风险图在时间上稳定；风险与潜误差的峰值相关 0.602 出现在接近零延迟处，说明两者时间同步。但 top-5% 的空间 IoU 只有 0.130，说明置信度能可靠地找到容易出错的区域，却不能精确复现它们的边界。

作者的收束句写得很克制，探针提供的是排序 patch、frame 和 task 的强序数风险信号，但它的输出不应被当作绝对校准的概率。附录 B.1 用 ECE、Brier 和可靠性图进一步支撑这个定位，在潜空间里阈值越松校准越好，但在主要工作点附近探针仍明显过度自信。

#### 关键证据 / 图表 / 公式

- Table 1 是 Why Confidence 这一问的完整答案，五行分别对应排序、检测、定位、稳定与同步。
- 0.130 的 top-5% IoU 是全表最弱的一格，也是作者自己拿来论证「该用软 patch 加权而不是硬空间选择」的依据。附录 B.1 里 top-5% 的 overlap 约 0.22，IoU 与 overlap 的差距说明风险区能覆盖不少真误差区，但边界画不准。
- AUPRC 0.146 相对随机 0.05 是近三倍，但绝对值仍低，读的时候不要把 AUROC 0.761 当成检测器已经好用。

#### 4.3 Why Active Learning?

![[papers/images/liu2026confal-wm/main_results_comparison.png|760]]

为了紧凑比较，所有分项指标被归一化到 $[0,1]$ 并聚成四个维度，Reconstruction 是 PSNR 与 SSIM 的均值，Scene 是 Scene Consistency，Semantics 是 Logics、Sem.-CLIP、Sem.-BLEU 的均值，Motion 是三项轨迹指标之和。

主对比的读法分两档。在 selection-only 一档，置信度引导的 mean-risk 选择在九个分项指标里的八个最好，包括 PSNR、SSIM、Scene Consistency、Sem.-CLIP、Sem.-BLEU 和三项轨迹指标（唯一没拿第一的是 Logics，RoboReward 的 0.6391 更高）。

| Scoring | Weighting | PSNR | SSIM | Scene | Logics | Sem.-CLIP | Sem.-BLEU | Traj-HSD | Traj-Dyn | Traj-nDTW |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Base EVAC | – | 0.5532 | 0.5778 | 0.8757 | 0.4298 | 0.8523 | 0.1799 | 0.0007 | 0.0001 | 0.0006 |
| EVAC Warmup v1 | – | 0.6446 | 0.7309 | 0.9047 | 0.5537 | 0.8824 | 0.2708 | 0.1045 | 0.0721 | 0.1439 |
| Random | None | 0.5968 | 0.6849 | 0.8524 | 0.3554 | 0.8689 | 0.2372 | 0.1067 | 0.0725 | 0.1518 |
| GVL | None | 0.6630 | 0.7546 | 0.9057 | 0.5992 | 0.8898 | 0.2849 | 0.1114 | 0.0688 | 0.1592 |
| RoboReward | None | 0.6266 | 0.7158 | 0.8470 | **0.6391** | 0.8861 | 0.2815 | 0.1113 | 0.0693 | 0.1554 |
| PRM-as-Judge | None | 0.6467 | 0.7580 | 0.9033 | 0.6033 | 0.8880 | 0.2852 | 0.1154 | 0.0746 | 0.1606 |
| LRMs | None | 0.6617 | 0.7603 | 0.8966 | 0.5744 | 0.8827 | 0.2756 | 0.0946 | 0.0587 | 0.1352 |
| Confidence | None | **0.6746** | **0.7692** | **0.9196** | 0.5923 | **0.8903** | **0.2865** | **0.1181** | **0.0812** | **0.1650** |
| Confidence | Frame | 0.6595 | 0.7500 | 0.9143 | 0.6171 | 0.8874 | 0.2789 | 0.1106 | 0.0684 | 0.1608 |
| Confidence | Fr.+Patch | 0.6772 | 0.7758 | 0.8942 | 0.6226 | 0.8925 | 0.2952 | 0.1118 | 0.0759 | 0.1633 |

在加权一档，置信加 frame 加权拿到最好的 Scene Consistency，置信加 frame-and-patch 加权拿到最好的 PSNR、SSIM、Logics、Sem.-CLIP、Sem.-BLEU 和三项轨迹指标。

作者主动指出一处不一致。Frame-and-patch 加权的 Scene Consistency 略低于 frame-only，尽管它在 Reconstruction、Semantics、Motion 三个维度都更好。作者把这归因于视觉一致性与运动导向指标之间已知的张力，并引了三篇文献，同时承认这也暴露了用这类代理指标间接评估下游具身表现的局限。

聚合成四维之后，配上 paired bootstrap 的 95% 区间（三个种子的 episode 级配对差异先按种子内配对再合并，10,000 次百分位 bootstrap）。

| Scoring | Weighting | $\Delta$Reconstruction | $\Delta$Scene | $\Delta$Motion | $\Delta$Semantics |
| --- | --- | --- | --- | --- | --- |
| Random | None | [-0.055, -0.039] (-0.047) | [-0.060, -0.045] (-0.052) | [-0.035, +0.056] (+0.011) | [-0.112, -0.046] (-0.079) |
| GVL | None | [+0.018, +0.024] (+0.021) | [-0.001, +0.003] (+0.001) | [-0.008, +0.046] (+0.019) | [+0.003, +0.042] (+0.023) |
| PRM-as-Judge | None | [+0.011, +0.018] (+0.015) | [-0.004, +0.001] (-0.001) | [+0.005, +0.056] (+0.030) | [+0.001, +0.040] (+0.021) |
| Confidence | None | [+0.031, +0.037] (+0.034) | [+0.012, +0.018] (+0.015) | [+0.018, +0.070] (+0.044) | [-0.002, +0.038] (+0.018) |
| Confidence | Frame | [+0.014, +0.020] (+0.017) | [+0.007, +0.012] (+0.010) | [-0.007, +0.045] (+0.019) | [+0.007, +0.044] (+0.026) |
| Confidence | Fr.+Patch | [+0.036, +0.042] (+0.039) | [-0.013, -0.008] (-0.010) | [+0.008, +0.054] (+0.031) | [+0.011, +0.049] (+0.030) |

区间里有两条不该被平均值盖过去。Confidence selection-only 的 $\Delta$Semantics 区间是 $[-0.002, +0.038]$，跨了 0，所以语义维度的提升在统计上还不能算稳。Confidence Fr.+Patch 的 $\Delta$Scene 区间是 $[-0.013, -0.008]$，整段在 0 以下，也就是场景一致性相对 EVAC-v1 是确定性的退化，而不是噪声。

选择准则的消融在 Table 3，只用默认种子 42、不加额外加权。

| Variant | PSNR | SSIM | Scene | Logics | Sem.-CLIP | Sem.-BLEU | Traj-HSD | Traj-Dyn | Traj-nDTW |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Random | 0.5968 | 0.6849 | 0.8523 | 0.3554 | 0.8689 | 0.2372 | 0.1067 | 0.0725 | 0.1518 |
| Mean Risk | **0.6838** | **0.7797** | **0.9322** | **0.6198** | 0.8894 | 0.2754 | **0.1313** | **0.0921** | **0.1780** |
| Tail Risk | 0.6317 | 0.7197 | 0.9218 | 0.5579 | 0.8890 | **0.3047** | 0.1207 | 0.0711 | 0.1630 |
| Persistent Risk | 0.6529 | 0.7470 | 0.9230 | 0.5496 | **0.8928** | 0.2858 | 0.0926 | 0.0608 | 0.1342 |

Mean risk 在九项里赢七项，tail risk 拿到最高的 Sem.-BLEU，persistent risk 拿到最高的 Sem.-CLIP。作者据此把 mean risk 定为主实验的默认采集准则。附录 B.1 补了一句解释，mean 聚合的全局 Spearman 相关最强，因为平均抑制了局部噪声并衡量整段的整体预测难度，而 tail 和 persistent 分别强调稀疏严重误差与跨帧反复的失败，它们本来就不需要与 episode 级平均误差强相关。

#### 关键证据 / 图表 / 公式

- Figure 6 的误差棒是 paired bootstrap 95% 区间，比只看柱高更可靠。
- Base EVAC 的三项轨迹指标是 0.0007、0.0001、0.0006，聚合后的 Motion 是 0.0014，相对 EVAC-v1 是 −99.6%。这个数字说明零样本跨本体迁移到 RoboTwin2.0 时 EVAC 基本产不出可用的机器人轨迹，所有后续提升都是在已经热身过的模型上做的增量。
- Table 3 只跑一个种子，而主表跑三个种子。选择准则这条结论的统计强度明显低于主对比。

### 5 Conclusion

结论重述三块贡献之后，给了三条局限，写得比多数论文具体。

第一条是可迁移性。置信探针围绕 UNet 扩散骨干的内部解码器特征设计，且只在 EVAC 和 RoboTwin2.0 上训过，跨世界模型架构和跨域直接迁移困难。作者提出的方向是用多个骨干世界模型和多样具身数据集训一个通用的世界置信模型，那也需要一个更通用的输入接口。

第二条是置信表征难以直接评估。它的有用性主要靠误差相关、数据排序和下游重训表现间接推断，而不是靠一个独立的、判断是否学到了期望可靠性表征的度量。作者认为需要更显式的表征诊断和受控因果评估。

第三条是当前世界模型评测本身不完整，视觉保真度与运动准确度可能冲突。未来协议可以分开评估机械臂运动、被操作物体动力学、交互区域与静态背景，从而更精确地刻画局部重构质量与动作条件下的物理演化。

#### 关键证据 / 图表 / 公式

三条局限都是定性的，但第三条在正文里有对应证据，Fr.+Patch 的 Scene Consistency 与其他三维的反向变化正是「视觉保真与运动准确冲突」的一个实例。

### Appendix A More Details on Methods

A.1 补全潜扩散与速度目标的定义，并推导 $\hat z^{(\tau)}-z^{(0)} = \sqrt{1-\bar\alpha_\tau}(\hat v^{(\tau)}-v^{(\tau)})$。这条恒等式是整个置信监督能便宜下来的原因，构造目标时不用跑完整反向扩散。Figure 8 图解了通道平均加区域池化得到 patch 级误差的两步。

A.2 推导随机阈值的边缘化性质。$\theta^{(s)}_t\sim\mathcal U(l^{(s)},h^{(s)})$，对固定误差 $m$ 有

$$
\mathbb E_\theta[q=1\mid m] = \text{clamp}\!\left(\frac{h^{(s)}-m}{h^{(s)}-l^{(s)}},0,1\right)
$$

而 BCE 下的最优预测恰是这个条件概率。作者补了一句实现说明，$\theta^{(s)}_t$ 还被嵌入进探针，所以探针学的是阈值条件下的可靠性而不只是这个边缘化形式。

### Appendix B More Experimental Results

B.1 是把「序数信号而非校准概率」这个定位坐实的地方。

![[papers/images/liu2026confal-wm/Task-level_risk_aggregation_in_latent_and_pixel_spaces_page1.png|760]]

Figure 10 在潜空间与像素空间对比三种任务级聚合。作者的解释很关键，这些相关只验证每个分数含有有意义的误差信号，本身并不能决定哪种采集规则能训出最好的后训练模型，下游差异要看 Table 3。

![[papers/images/liu2026confal-wm/topk_iou_overlap_latent.png|420]] ![[papers/images/liu2026confal-wm/topk_iou_overlap_pixel.png|420]]

Figure 11 给空间定位。top-5% 处潜空间约 0.13 IoU、0.22 overlap，像素空间略低。overlap 相对高而 IoU 中等，说明风险能找到不少相关误差区却画不准边界，这直接支持软 patch 加权而不是硬空间选择。作者还提醒一句，更大比例下分数上升只是因为空间覆盖变粗，不该读成定位分辨率提高。

![[papers/images/liu2026confal-wm/ece_brier_vs_tau_latent.png|420]] ![[papers/images/liu2026confal-wm/reliability_sweep_latent_page1.png|420]]

Figure 12 与 Figure 13 扫操作阈值 $\theta_{\text{eval}}$。改变 $\theta_{\text{eval}}$ 不改变预测的置信图，只改变「预测算不算正确」这个事后定义。潜空间里阈值越松 ECE 与 Brier 越好，但在主要工作点附近探针仍明显过度自信。像素空间在自己选的阈值下看起来校准更好，但两者依赖不同的误差尺度，不可直接比。

Figure 14 做参数敏感性。帧聚合方式上 mean 在潜空间与像素空间都给出最强的帧级与任务级 Spearman，极值型聚合会放大孤立噪声 patch。探针条件阈值 $\theta_{\text{cond}}$ 上，中低阈值给出最强空间判别，大阈值让大多数 patch 都变得高置信、降低定位对比度，默认阈值落在表现较好的区间内且整体变化温和。

B.2 提供聚合结果、paired bootstrap 与逐种子明细。Table S2 之外还给了每个种子的完整分项指标（种子 42、3407、123 各一张表）。

B.3 是定性演化，六个代表性 RoboTwin2.0 episode，覆盖物体放置、柜子交互、方块堆叠、碗堆叠和开关操作。作者对每个 episode 逐句描述失败模式，写得相当细。

![[papers/images/liu2026confal-wm/place_burger_fries_aloha-agilex_randomized_500_ep130.png|760]]

place burger fries（ep130）上，EVAC-v1 出现强烈蓝色偏移且托盘内容从 rollout 中段开始崩坏；Frame 加权去掉了大部分托盘崩坏，但左臂幻觉出一个物体而不是抓住汉堡，右臂持有的物体明显变形；Fr.+Patch 正确抓取并放置汉堡，薯条保持得最忠实。

![[papers/images/liu2026confal-wm/stack_blocks_two_aloha-agilex_randomized_500_ep325.png|760]]

stack blocks two（ep325）上，EVAC-v1 有强烈颜色闪烁，绿块被举起堆叠时下方蓝块消失；Frame 加权基本去掉了色偏但绿块没能保持吸附在夹爪上，因而错过堆叠交互；Fr.+Patch 同时解决了物体持久性和抓取两个失败。

六个 episode 的聚合数字在 Table 9，Fr.+Patch 在全部六个 episode 上都拿到最强的 Reconstruction。但 place empty cup（ep294）上 Frame 加权的 Semantics 相对 EVAC-v1 掉了 51.3%、Motion 掉了 25.9%，说明帧级加权在个别 episode 上会明显变坏。

B.4 给置信可视化的最好与最差样例各两个，patch 级 Spearman 从 0.713、0.695 到 0.265、0.241。把最差的一起放出来是这篇在证据呈现上比较可信的一点。

## 方法细节

把 ConfAL-WM 串成一次完整的后训练流程，可以分成五段。

探针训练段。EVAC 骨干冻结，从真值视频编码干净潜 $z^{(0)}$，按扩散调度加噪得 $z^{(\tau)}$，UNet 在动作条件下预测 $\hat v^{(\tau)}$。用等价形式算 patch 级潜 L1 误差 $m^{(\tau)}_{t,(i,j)}$，与该帧采样的阈值 $\theta_t$ 比较得二值目标，探针从第 $\ell$ 个解码块特征加时间步嵌入加阈值嵌入预测稠密置信图，BCE 训练 6,000 步。阈值区间由批内 0.1 与 0.9 分位数经两段 EMA 在线校准。

热身段。用同一批约 25% 的目标域数据（6,248 个 episode）热身 EVAC，得到域适配后的 EVAC-v1。UNet 去噪器与两个投影模块可训，VAE、CLIP 嵌入器与动作条件重采样器冻结。

预筛段。EVAC-v1 加探针在每个任务的代表性 episode 上跑推理，按均值风险估计任务难度，难任务分到更大的候选配额，任务内再随机采 episode。从 18,244 的候选池里选出 7,298 个。

打分段（可选）。对选出的 episode 再跑一遍 EVAC-v1 推理与置信打分，在 $\tau\in[50,200]$ 的三个扩散时间步上平均，得到帧级与 patch 级风险。这一段是加权路径额外付出的成本。

重训段。按 Equation 9 决定用帧级还是 patch 级风险，分位数归一化并裁剪后按 Equation 10 转成局部损失乘子，$\lambda$ 在前 $s_{\text{warm}}$ 步线性升起。置信图 detach，梯度只走世界模型。AdamW，学习率 $5\times 10^{-5}$，fp16，4,000 步，两张 A800。

## 实验设置、数据集、基线、指标

| 项目 | 设置 |
| --- | --- |
| 骨干 | EVAC，UNet 潜扩散，约 2.33B 参数，AgiBot World 预训练 |
| 探针 | 约 8.2M 参数，挂解码块特征，空间加时间 Transformer |
| 后训练域 | RoboTwin2.0，Aloha-AgileX 双臂，50 任务 $\times$ 500 随机场景，24,992 段视频 |
| 视频长度 | 98 到 578 帧 |
| 探针与热身 | 6,248 episodes（约 25%） |
| 候选池 | 18,244 episodes |
| 重训预算 | 7,298 episodes（约候选池的 40%） |
| 优化 | AdamW，lr $5\times 10^{-5}$，fp16，4,000 步，2 $\times$ A800 |
| 打分 | EVAC-v1 在 $\tau\in[50,200]$ 三个时间步上平均 |
| 种子 | 主对比 42 / 3407 / 123，消融只用 42 |
| 基线 | Random、GVL、RoboReward、Robometer-Prog、Robometer-Pref、PRM-as-Judge、LRMs |
| 评测 | EWMBench 九项，归一化后聚成四维 |

论文没有报告探针训练与打分的 wall-clock 成本、显存占用、以及加权路径相对 selection-only 路径的额外算力比例。这对一个以「后训练效率」为卖点的方法是明显缺口。

## 主要结果、消融或对比

选择信号的差异是最清楚的一档。同样 7,298 个 episode 的预算，Random 的四个维度里三个低于 EVAC-v1，Confidence 四个维度全部高于 EVAC-v1，Reconstruction +5.0%、Scene +1.6%、Motion +13.7%、Semantics +3.6%。

标量基线里表现最好的是 GVL 与 PRM-as-Judge，两者的 Reconstruction 分别 +3.1% 与 +2.1%，都低于 Confidence 的 +5.0%。LRMs 的 Reconstruction +3.4% 不差，但 Motion −10.0%，是所有非随机基线里唯一在运动维度大幅退化的。

加权带来的额外收益不是免费的。Fr.+Patch 把 Reconstruction 推到 +5.6%、Semantics 推到 +6.1%，但 Scene 从 +1.6% 变成 −1.2%，Motion 从 +13.7% 降到 +9.5%。所以 selection-only 与 Fr.+Patch 并不是简单的强弱关系，前者的运动与场景更好，后者的重构与语义更好。

选择准则消融里 mean risk 在九项赢七项，但只跑了一个种子。Tail 与 persistent 各赢一项语义指标，作者的解释是它们本来就在强调不同的失败模式。

跨方法的统计强度差别要注意。Confidence selection-only 的 Reconstruction、Scene、Motion 三个区间都不含 0，Semantics 区间含 0。Fr.+Patch 的 Scene 区间整段为负。

## 图表、公式与表格线索

| 编号 | 内容 | 支撑主张 | 阅读提醒 |
| --- | --- | --- | --- |
| Figure 1 | 三块总览，推理、主动学习、重训结果 | 全文结构 | 概念图 |
| Figure 2 / Figure 7 | 探针训练与推理管线 | 特征取点与监督构造 | 两图内容相同 |
| Figure 3 | VAE 潜与三层解码器特征对比 | 解码器层的语义与分辨率权衡 | 只有定性可视化，无定量层扫描 |
| Figure 4 | 最好与最差两个置信可视化 | 风险响应局部失败 | 给出了 0.241 的最差样例 |
| Figure 5 | 置信箱、帧任务散点、AUROC / AUPRC | 多尺度排序有效 | 潜空间单调性比像素空间清楚 |
| Figure 6 | 主对比四维柱状图 | 置信引导优于标量打分 | 误差棒是 paired bootstrap 95% |
| Figure 8 | patch 级误差构造 | Equation 1 的图解 | 附录 A.1 |
| Figure 9 | EMA 阈值带演化 | 在线校准优于固定阈值 | 界从 0.20/0.70 收到 0.0705/0.2610 |
| Figure 10 | 三种任务级聚合的相关 | 每种分数都含误差信号 | 相关强弱不决定下游好坏 |
| Figure 11 | top-k IoU 与 overlap | 定位粗，支持软加权 | 大比例下分数升高是覆盖变粗 |
| Figures 12–13 | ECE、Brier 与可靠性图 | 置信是序数信号非校准概率 | 主要工作点附近过度自信 |
| Figure 14 | 帧聚合与探针阈值敏感性 | mean 聚合最稳，默认阈值合理 | 变化温和 |
| Figures 15–20 | 六个 episode 的重训演化 | patch 加权改善局部几何与交互 | 精选样例 |
| Figures 21–24 | 置信可视化的最好与最差各两例 | 信号上下界 | 最差样例 Spearman 0.241 |
| Table 1 | 置信有效性五行汇总 | Why Confidence 的完整答案 | top-5% IoU 只有 0.130 |
| Table 2 | 九项分指标主对比 | 选择与加权的分项胜负 | Logics 由 RoboReward 拿下 |
| Table 3 | 三种选择准则消融 | mean risk 为默认 | 只用种子 42 |
| Table 4 | 四维聚合与相对变化 | 汇总视图 | Fr.+Patch 的 Scene 为 −1.2% |
| Table 5 | paired bootstrap 区间 | 统计强度 | 两处区间需单独读 |
| Table 9 | 六个 episode 的聚合演化 | 定性对应的量化 | ep294 的 Frame 加权大幅退化 |
| Equations 1, 11–21 | 潜误差构造与等价推导 | 便宜的监督构造 | 只在固定 $\tau$ 下成立 |
| Equations 4–5, 24–29 | EMA 阈值与边缘化性质 | 二值监督诱导连续排序 | 探针另外吃阈值嵌入 |
| Equations 7–8 | 三种风险聚合 | 采集准则定义 | $\eta$、$\eta_p$、$\eta_t$ 取值未给 |
| Equations 9–10 | 帧与 patch 加权与损失乘子 | 局部训练增强 | $\alpha$ 中间值未扫 |

## 主张-证据-边界矩阵

| 主张 | 最强证据 | 证据强度 | 边界 |
| --- | --- | --- | --- |
| 世界模型误差在时空上局部集中 | Figure 4 的定性图与 Table 1 的时间稳定性 | 中等 | 只在 EVAC + RoboTwin2.0 上观察 |
| 解码器特征比瓶颈特征更适合稠密置信 | Figure 3 的三层可视化 | 弱 | 没有瓶颈特征的定量对照 |
| 置信是有效的多尺度序数信号 | Spearman 0.540 / 0.590 / 0.595，AUROC 0.761 | 较强 | AUPRC 0.146 绝对值仍低 |
| 置信不是校准概率 | Figures 12–13 的 ECE、Brier 与可靠性图 | 较强 | 作者自己给的负面结论 |
| 置信选择优于标量打分 | Table 2 的 8/9 项，Table 5 的三个非零区间 | 较强 | 固定 40% 预算下的单次对比 |
| 稠密加权带来额外收益 | Fr.+Patch 在 8/9 项最好 | 中等 | Scene 区间整段为负 |
| mean risk 是最好的采集准则 | Table 3 的 7/9 项 | 弱 | 只跑种子 42 |
| EMA 阈值优于固定阈值 | Figure 9 的收敛轨迹与初值差三倍 | 弱 | 没有固定阈值的下游对照 |
| 方法提升后训练效率 | 四维相对提升与 bootstrap 区间 | 中等 | 没有报告任何算力或时间成本 |

## 局限与可追问点

最该追问的是「效率」这个词到底怎么算。论文的卖点是 improves post-training efficiency，但全文没有一个时间或算力数字。探针训练 6,000 步、EVAC-v1 热身、预筛推理、加权路径的额外打分推理，这四项加起来的成本相对于「直接用全部 18,244 个 episode 重训」到底省了多少，没有算过。加权路径作者自己承认要多一次推理和打分，那这次推理占总预算的比例是多少，也没给。没有这笔账，效率主张只能理解成「同样 7,298 个 episode 下效果更好」，而不是「更省」。

第二是没有下游评测。世界模型后训练的最终用途是策略评估、合成数据生成和规划，论文全部用 EWMBench 的代理指标衡量，而且自己在正文里就点出 Scene Consistency 与运动指标可能冲突、这类代理指标不足以间接评估下游具身表现。既然已经意识到了，最有说服力的补充实验是拿 EVAC-v2 生成的数据去训一个策略，或者做一次离线策略评估的相关性检验。这里作者没给证据。

第三是数据划分对不上。24,992 减去 6,248 与 18,244 还剩 500 条，论文没有交代。数量不大，但对一篇讲数据选择的论文来说，池子的边界应该是清楚的。

第四是消融的统计强度。选择准则这条结论只跑种子 42，而主对比跑三个种子并给了区间。Mean、tail、persistent 三者的差距在 PSNR 上是 0.6838 对 0.6317 对 0.6529，考虑到主表里三种子之间本身就有波动，单种子的排序不足以支撑「mean risk 最好」这个默认选择。

第五是 $\alpha$ 没扫。Equation 9 把 frame 与 patch 统一成一个插值，这是设计上的亮点，但论文只报了两端。中间值是否能在 Reconstruction 与 Scene Consistency 之间取到更好的折中，恰恰是这个公式最该回答的问题。

第六是探针的层号与超参。$\ell$ 的选择只给了三层的定性可视化，$\eta$、$\eta_p$、$\eta_t$ 三个尾部比例、$\lambda_{\text{conf}}$、$s_{\text{warm}}$ 都没有给数值或敏感性。附录 B.1 扫了帧聚合方式和 $\theta_{\text{cond}}$，但那两个都不是流水线里最关键的旋钮。

第七是与最近邻方法没有对照。C3 是最接近的稠密置信工作，作者以架构不同为由不比，理由成立，但也让「稠密置信优于标量打分」这条结论缺了同类对照。至少可以把 C3 的训练目标搬到 UNet 上做一个复现版本。

第八是零样本基线太弱带来的读数偏差。Base EVAC 的三项轨迹指标接近 0，Motion 相对 EVAC-v1 是 −99.6%。所有相对提升都以 EVAC-v1 为基准，而 EVAC-v1 已经吃了 25% 的目标域数据。跨域迁移的绝对难度被这个基准掩盖了。

## 我的阅读判断

这篇最值得画出来的是那句区分，标量打分能排序，稠密置信能定位。选数据这件事标量信号就够用，Table 2 里 GVL 和 PRM-as-Judge 的表现并不难看；真正拉开差距的是训练时的局部加权，那需要一张图而不是一个数。作者把同一个信号同时用在两个位置，这个设计比单独的置信估计更有价值。

第二个值得记的是 Table 1 那行 0.130 的 top-5% IoU。它是全文最诚实的一格。风险图找得到出问题的区域，画不准边界，所以只能做软加权。很多做不确定性的会遇到这个问题，定位质量不够就硬做掩码选择，反而把好的区域也切掉。作者用一个弱指标反推出一个正确的设计决策，这条推理链比结果本身更值得学。

最大的隐忧还是评测。EWMBench 的九项指标之间已经出现互相打架的情况，Fr.+Patch 在八项上赢却在 Scene Consistency 上确定性退化。当代理指标彼此冲突时，「哪个方法更好」这个问题就没有唯一答案，只能靠下游任务来裁。作者在局限里说得很清楚，但没有补这个实验。说实话也不确定 Fr.+Patch 的场景一致性退化在合成数据生成场景里是不是可以接受。

和 [[@liu2026steam|STEAM]]、[[@yu2026warp-rm|WARP-RM]] 放在一起读，能看清一条正在成形的分工。数据筛选这条线上，奖励模型给的是任务级偏好，过程奖励给的是帧级进度，世界模型置信给的是 patch 级风险。三者的粒度依次变细，可用的位置也依次从「选轨迹」推进到「选帧」再到「加权像素区域」。ConfAL-WM 是目前把粒度推得最细的一篇。

## 与当前库的连接

- [[@liu2026steam|STEAM]] 与 [[@yu2026warp-rm|WARP-RM]] 同在数据筛选与奖励建模这条轴上，粒度分别停在轨迹级与任务级。与本篇对读可以看清打分粒度从粗到细的完整谱系。
- [[@peng2026fact|FACT]] 用失败数据做世界模型的因果训练，与本篇的「按失败位置加权」是同一直觉的两种实现，一个改数据构成，一个改损失权重。
- [[@qian2026wam-rl|WAM-RL]] 做世界模型的在线强化学习与后训练，本篇做的是有监督后训练的数据分配，两篇合起来覆盖了 WAM 后训练的两条主要路径。
- [[@wu2026tactile-wam|Tactile-WAM]] 与 [[@zhou2026zero-wam|Zero-WAM]] 是库里另外两篇 WAM 工作，前者换模态，后者换任务规范来源，可以和本篇的「换域后怎么选数据」并读。
- [[@xue2026worldsample|WorldSample]] 关注用世界模型生成的合成经验做真机闭环 RL，正好是本篇缺失的下游验证场景。若要检验 EVAC-v2 的提升是否真的有用，那类实验是最直接的。
- [[@gao2026fast-leworldmodel|Fast LeWorldModel]] 与 [[@wang2026orca|Orca]] 提供世界模型架构侧的对照，本篇的探针依赖 UNet 解码器特征，换成这类架构后是否还成立是作者自己列的第一条局限。
- [[@murray2026flowdagger|FlowDAgger]] 的 Cosmos-Policy 分支同样在处理「UNet 或 DiT 之外的联合生成结构怎么接入外部信号」，两篇在工程上的取点问题是同一类。

## 精读路线 / 为什么需要回看

第一遍看 Figure 1、Table 1 和 Table 2。三处分别回答方法长什么样、置信信号靠不靠谱、下游收益有多大。Table 1 里的 0.130 和 Table 2 里 Fr.+Patch 的 Scene Consistency 是两个必须记住的负面数字。

第二遍看 Section 3.1 与附录 A。Equation 17 的等价推导解释了监督为什么便宜，Equation 28 的边缘化解释了二值随机阈值为什么能诱导连续排序。这两条是方法在数学上站得住的地方，也是最容易被跳过的地方。

第三遍看 Table 5 的 bootstrap 区间而不是 Table 4 的百分比。Confidence selection-only 的 Semantics 区间跨 0、Fr.+Patch 的 Scene 区间整段为负，这两条在 Table 4 的相对变化里看不出来。

第四遍看附录 B.3 的六个 episode。Table 9 的逐 episode 数字比聚合均值更能说明加权在什么情况下有效，ep294 上 Frame 加权的 Semantics 掉 51.3% 就是一个反例。定性描述写得很细，配着图看能理解「patch 加权改善了物体持久性和夹爪几何」这句话具体指什么。

等代码公开后最该补看的是三样，探针的完整超参与层号扫描、加权路径相对 selection-only 的额外算力占比、以及 EVAC-v2 生成数据在任何一个下游任务上的表现。可以确定的是，第三样会决定这套方法是「让代理指标更好看」还是「让世界模型真的更有用」。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
