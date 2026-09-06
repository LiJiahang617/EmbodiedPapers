---
tags:
  - bilingual-reading
paper: "[[@murray2026flowdagger]]"
source_pdf: "[[papers/pdfs/murray2026flowdagger.pdf]]"
images: "papers/images/murray2026flowdagger/"
image_index: "[[papers/images/murray2026flowdagger/index.md]]"
arxiv: "2607.08877v1"
created: 2026-09-05
---

# FlowDAgger: Human-in-the-Loop Adaptation of Generative Robot Policies in Latent Space

paper:: [[@murray2026flowdagger]]
pdf:: [[papers/pdfs/murray2026flowdagger.pdf]]
images:: [[papers/images/murray2026flowdagger/index.md]]

> [!warning] 版本与证据状态
> 本稿按 arXiv 2607.08877v1 逐节整理，论文用 CoRL 风格模板，正文没有声明录用状态。作者给出项目页 microsoft.github.io/FlowDAgger，截至 2026-09-05 代码仓库已建但内容仍以介绍为主。仿真结果报 3 seeds、每点 25 rollouts，真机结果报 30 rollouts 但不报 seed，附录两个补充实验只跑单 seed。以下涉及领先幅度的表述均按作者报告处理。

## 一句话总结

FlowDAgger 想解决的不是「怎样让生成式机器人策略更强」，而是「人纠正了一下之后，这一下该写进模型的哪个位置」。作者证明把人类纠正动作反演回冻结基座策略的噪声空间，再训一个轻量 noise policy 去复现这些噪声，比改权重、加动作残差或用奖励做潜空间 RL 都更省样本、更省显存，而且不破坏预训练技能。

## 核心词汇速查

| English | 中文 | 在论文中的作用 |
| --- | --- | --- |
| generative robot policy | 生成式机器人策略 | 从噪声出发、由 ODE 积分得到动作块的一类策略 |
| flow matching | 流匹配 | 直接学习速度场 $v_\theta$ 的生成式训练目标 |
| action chunk | 动作块 | 一次生成的长度为 $H$ 的动作序列 |
| noise space $\mathcal W$ | 噪声空间 | 基座策略暴露出来的、可用于适配的输入面 |
| action inversion | 动作反演 | 把纠正动作映射回能生成它的噪声向量，本文核心机制 |
| per-step fixed-point inversion | 逐步不动点反演 | 对每个 Euler 步解隐式方程，本文默认反演器 |
| trajectory-level inversion | 轨迹级反演 | 图像扩散里常用的整条轨迹残差校正，本文对照组 |
| noise policy $\pi_w$ | 噪声策略 | 观测编码器加 MLP，唯一被训练的部件 |
| intervention buffer | 干预缓冲区 | 存放反演得到的 $(s,w^*)$ 监督对 |
| autonomous buffer | 自主缓冲区 | 存放成功自主 rollout 中真实用过的噪声 |
| behavioral prior | 行为先验 | 预训练模型已掌握、适配时不该被改坏的技能 |
| WAM, world-action model | 世界动作模型 | 动作与未来状态在同一潜张量里联合生成的策略族 |
| EDM schedule | EDM 噪声调度 | Cosmos-Policy 使用的、终点噪声不为零的扩散调度 |
| DSRL | 潜空间 RL 基线 | 在冻结扩散策略噪声空间用 RL 训小控制器 |
| Residual-DAgger | 动作残差 DAgger | 冻结基座、在动作空间学加性修正 |
| LoRA-DAgger | 低秩权重 DAgger | 用同一批纠正去更新低秩权重 |
| held-out task | 留出任务 | 用于检验适配是否损坏预训练能力的饱和任务 |

## 摘要

论文从一个部署现实出发。基于 diffusion policy 和 flow matching 的机器人基础模型在大规模示范上学到了很宽的行为先验，可一旦落到具体工位，陌生物体、场景动力学差异、本体癖性和长尾边缘情况都会让它稳定地失败。补数据再离线微调很贵，在真机上做在线 RL 又不安全。

现有几条补救路线各有硬伤。动作空间的交互式模仿确实处理了 covariate shift（协变量偏移），但它更新整个生成式策略，代价高且容易把先验改坏。残差方法保持基座冻结，却把修正加在无约束的动作空间，可能把策略推离它本来能可靠产生的行为。DSRL 那类潜空间 RL 样本效率高得多，但依赖奖励信号和自主探索，这两样在真实部署里都是瓶颈。

FlowDAgger 的答案是 action inversion（动作反演）。给定观测 $s$ 和专家纠正动作 $a^*$，反演出噪声 $w^*$，使冻结基座从 $w^*$ 出发能重现这个纠正。每个 $(s,w^*)$ 就成了一条噪声空间的监督，用来回归一个轻量 noise policy。基座权重一个字节都不改，只走前向。

评测覆盖仿真与真机、单臂与双臂、action-head VLA 与 world-action model 两大生成式族。MetaWorld 12 个任务上，FlowDAgger 平均成功率从冻结基座的 0.53 提到 0.78，比同样吃这批纠正的 LoRA-DAgger 和 Residual-DAgger 分别多 10 和 14 个点。真机 8 个任务只用 5 到 20 次干预 episode 就全部改善，Toolbox Packing 从 13% 提到 80%。适配显存约 8 GB，一张消费级显卡够用。

## 论文主线

![[papers/images/murray2026flowdagger/overview_page1.png|760]]

Figure 1 把整套机制画成一条闭环。预训练生成式策略 $\pi_{gp}$ 带着人在环部署，人一介入就给出纠正动作 $a^*$，反演器把它送回策略的潜空间得到 $w^*$，$(s,w^*)$ 训练一个轻量 latent policy 去操纵基座，而基座权重始终不动。

论证顺序也照这个结构走。第一步是把「适配接口」本身当成研究对象。作者反复强调一句话，adaptation interface matters，权重空间更新会伤先验，无约束动作空间修正会离开生成式策略的支撑集，噪声空间既能改行为又天然留在流形上。

第二步是补上潜空间方法缺的那块。DSRL 已经证明冻结策略可以被噪声操纵，但人类专家给的是动作不是噪声。动作反演正是这块缺口的桥，把 human correction 变成 noise target。

第三步是把机制推到 WAM 上。Cosmos-Policy 没有独立的动作生成过程，动作只是联合潜视频张量的若干帧。作者选择反演整个联合过程，而不是只优化动作帧噪声，附录 A.2 用数字说明后者会卡在不可接受的重构误差上。

## 贡献与结论对照

| 作者声称的贡献 | 对应证据 | 可接受的结论 | 不能外推的部分 |
| --- | --- | --- | --- |
| 提出 action inversion 把动作纠正变噪声监督 | Table 5，per-step FP 的 Action MSE 0.00168 | 逐步不动点反演在少步 ODE 上确实能高精度重构 | 只在 $K=10$ 的 flow head 和一个 EDM WAM 上验过 |
| 少步动作头必须用逐步不动点而非轨迹级反演 | Table 5、Table 6，$\sim$20$\times$、$\sim$14$\times$ 的 MSE 差距 | 图像扩散的反演结论不能直接搬到动作头 | 结论绑定 $\Delta t = 0.1$ 这一档，更长调度未测 |
| 噪声空间监督比权重与动作空间更省样本 | Table 1，平均 +0.25 对 +0.15 / +0.11 | 同一批纠正下，改的位置确实决定收益 | 12 个 MetaWorld 任务，Door Lock 就是反例 |
| 机制跨生成式策略族通用 | Table 2，$\pi_{0.5}$ +0.26、Cosmos-Policy +0.21 | 不依赖存在一个可分离的动作头 | 每族各一个代表模型，附录两个补充只有单 seed |
| 冻结基座能保住预训练技能 | Table 3，留出任务均值只掉 0.08 | 权重法在这组对照里代价明显更大 | 只测 5 个基座近饱和的任务，Push 仍从 0.96 掉到 0.56 |
| 真机可用且计算便宜 | Table 4 八任务全改善，约 8 GB 显存 | 在两个双臂平台上确实低成本见效 | 真机只对照 base 与 SFT，没有 Residual、LoRA、DSRL |

## 结构地图

| 原文 section | 主要内容 | 在论证链中的工作 |
| --- | --- | --- |
| 1 Introduction | 部署失败模式与三条补救路线的代价 | 把问题从「怎样适配」改成「在哪个空间适配」 |
| 2 Related Work | 生成式策略、交互式模仿、潜空间学习、生成模型反演 | 定位 FlowDAgger 与 DSRL 只差监督来源 |
| 3 Background | 噪声到动作映射、Euler 离散、噪声作为适配面 | 给出反演赖以成立的确定性映射前提 |
| 4 Method | 动作反演、WAM 反演、噪声策略与聚合循环 | 完整交代机制与训练目标 |
| 4.1 Action Inversion | 逐步不动点迭代与收敛条件 | 论文最核心的技术贡献 |
| 4.2 Inverting World-Action Models | 联合过程反演与 minimal-delta swap | 把机制从动作头推到 WAM |
| 4.3 FlowDAgger | 噪声策略、双缓冲区、L2 回归 | 说明稀疏纠正怎样不过拟合 |
| 5 Experiments | 四个研究问题与五组实验 | 依次验样本效率、跨族、保先验、真机 |
| 6 Limitations | 支撑集边界、干预质量、多模态反演 | 作者自划的三条边界 |
| 7 Conclusion | 把交互当成对潜决策的监督 | 收束论文立场 |
| Appendix A | EDM 反演、动作帧反演为何不够、噪声策略参数化 | 补上 WAM 分支的工程细节 |
| Appendix B | 反演器对照、迭代数扫描、Gr00t 与 diffusion policy 复现 | 支撑「不是针对某个基座调出来的」 |

## 按原文 section 精读

### 1 Introduction

引言先承认基础模型的成绩，再立刻把镜头拉到部署现场。大规模示范训出来的生成式策略在跨本体、跨任务上迁移得出乎意料地好，但在任何一个具体工位上，它们照样会因为陌生物体、新的场景动力学、本体癖性和长尾边缘情况而反复失败。

接着作者把三条已有路线逐个否掉，理由不是效果差，而是代价结构不对。补示范再离线微调，采集烦、算力贵，而且微调后的策略往往侵蚀基座已有的广义技能。动作空间的交互式模仿处理了协变量偏移，可它同样要更新整个生成式策略，这是一次昂贵且不稳定的更新。残差方法保住了基座，却把修正加在无约束动作空间，能把策略推到它本来不可靠的区域。

这一段的收束句是全文的立场句，adaptation interface matters。权重空间会伤先验，无约束动作空间会离开支撑集，那就只剩噪声空间。DSRL 已经在这个空间做过 RL，样本效率显著更高，可它依赖奖励和自主探索，两者在真机上都难落地。

FlowDAgger 的定位由此非常清楚，把 DSRL 的架构前提留下，把监督来源换掉。人类专家介入时给的是动作，不是噪声，所以缺的那一环是从动作到噪声的映射。

#### 关键证据 / 图表 / 公式

- Figure 1 是唯一的机制总览图，支撑「基座冻结、只训 latent policy」这条主张。
- 引言给出的三个量化承诺分别是，比离线 BC 和动作空间 DAgger 需要更少人类干预，比潜空间 RL 需要更少环境交互，适配轻到能在消费级显卡上训。三条承诺分别由 Table 1、Figure 3 与 Figure 4 兑现。

读到这里要留一个边界。作者说的 sample-efficient 是相对同一批纠正而言，不是说 FlowDAgger 需要的纠正绝对很少。MetaWorld 主表统一给 50 个 rollout 预算，真机则是 5 到 20 个 episode，两者不在一个尺度上。

### 2 Related Work

相关工作分四块写，每块都在替方法定位而不是罗列。

生成式机器人策略这块把范围划得很干脆，任何动作生成是由噪声样本驱动的 ODE 积分的策略都在射程内。Diffusion Policy 起头，扩到大规模多任务，flow matching 撑起近期的 VLA 和 WAM。这条边界后面被 Table 2 和附录 B.3、B.4 兑现，一个 VLA、一个 WAM、一个额外 VLA、一个 vanilla diffusion policy。

交互式模仿这块从 DAgger、HG-DAgger、IWR 一路写到 Sirius 与 Sirius-Fleet，再到把干预折进 RL 的 HIL-SERL 和 RLIF，最后落到 residual DAgger。作者的区分句只有一句，FlowDAgger 共享它们的数据采集方式，但监督发生在噪声空间。

潜空间与噪声空间学习这块专门给 DSRL 留了一整段。作者明说 DSRL 是最近的方法论邻居，架构前提一致，差别只在监督来源，DSRL 从奖励下的自主 rollout 学，FlowDAgger 从被反演回噪声空间的人类纠正学。

生成模型反演这块交代了技术债从哪来。DDIM inversion、null-text inversion 和 rectified flow 的反演都在图像合成里成熟，但搬到机器人要改两处。少步 ODE 调度下轨迹级方法不稳，所以改用逐步不动点；WAM 没有纯动作过程，所以直接反演联合扩散。

#### 关键证据 / 图表 / 公式

这一节没有数字，但埋了两条后文必须兑现的伏笔，Section 4.1 的少步反演和 Section 4.2 的联合反演。附录 B.1 正是为第一条伏笔准备的对照实验。

### 3 Background

背景节把三件事讲清楚，缺一件反演就不成立。

生成式动作策略被写成 $\pi_{gp}: \mathcal S \to \mathcal P(\mathcal A)$，从噪声 $w \sim \mathcal N(0, I)$ 出发，沿学到的速度场 $v_\theta$ 积分一条 ODE 得到动作块 $a$。

$$
\frac{dx}{dt} = v_\theta(x, t, s),\qquad x(0)=w,\qquad a = x(1).
$$

作者用 $\pi_{gp}(s,w)$ 记这个噪声到动作的映射。Flow matching 直接学 $v_\theta$，diffusion policy 的反向过程也有等价的 probability-flow ODE，所以两族都落在同一描述里。

实践中用 $K$ 步 Euler 离散，步长 $\Delta t = 1/K$。

$$
x_{k+1} = x_k + \Delta t\, v_\theta(x_k, t_k, s),\qquad k=0,\dots,K-1,\qquad a = x_K.
$$

这里埋着全文最关键的一个数量级差异。Flow-matching 动作头的 $K$ 大约是 10，而图像扩散常用几百步。少步这件事不是实现细节，它直接决定 Section 4.1 为什么必须解隐式方程。

第三件事是把噪声认成适配面。观测 $s$ 固定后，$\pi_{gp}(s,\cdot)$ 是确定性映射，噪声样本单独决定动作，动作分布完全由 $\mathcal W$ 上的分布控制。把标准抽样换成状态条件下的噪声选择，就能在不动 $\theta$ 的前提下操纵行为。

#### 关键证据 / 图表 / 公式

- Equation 1 与 Equation 2 是全文的地基，动作反演反的正是 Equation 2 的递推。
- 「$K$ 约为 10 而图像扩散是几百」这句是 Section 4.1 全部论证的支点，读的时候要记住。

### 4 Method

方法节分成两个部件加一条循环。动作反演把纠正动作变成噪声目标，噪声策略在这些目标上训练，部署时操纵冻结基座。4.2 是给 WAM 的扩展分支。

#### 4.1 Action Inversion

映射 $\pi_{gp}(s,\cdot)$ 是 $K$ 个 Euler 步的复合，没有闭式逆，所以作者逐步反。每个前向步重排成隐式方程 $x_k = x_{k+1} - \Delta t\, v_\theta(x_k, t_k, s)$，用不动点迭代解。

$$
x_k^{(m+1)} = x_{k+1} - \Delta t\, v_\theta\!\left(x_k^{(m)}, t_k, s\right),\qquad x_k^{(0)} = x_{k+1}.
$$

只要 $\Delta t L < 1$（$L$ 是 $v_\theta$ 对第一个自变量的 Lipschitz 常数），右端就是压缩映射，迭代几何收敛，$M=5$ 步足够。从 $x_K = a^*$ 往回跑到 $x_0$，取 $w^* = x_0$。

作者花了一整段解释为什么必须解隐式方程而不是走一步显式反向。显式反向在 $x_{k+1}$ 而不是 $x_k$ 处求速度场，误差是 $O(\Delta t)$。图像扩散里 $\Delta t \sim 10^{-3}$，这点误差可以忽略；动作头 $K=10$、$\Delta t = 0.1$，就忽略不了。更要命的是机器人动作本身数值很小，一个在图像潜空间可忽略的误差，在动作里可能占一大截。

成本核算写得很清楚。反演一次纠正要 $KM$ 次 $v_\theta$ 求值，不需要对基座反向传播，纠正一边收一边就能在线反。

#### 关键证据 / 图表 / 公式

- Equation 3 是本文技术核心，收敛条件 $\Delta t L < 1$ 是它成立的前提，论文没有实测 $L$，属于依赖假设的部分。
- Table 5 用 Action MSE 兑现这段论证，per-step FP（$M=5$）0.00168，Euler reverse 0.0329，trajectory FP（$k=5$）0.0228，Adam 20 步 0.0275。
- 需要注意，「反演一次不需要反向传播」这句在 4.1 成立，但 4.2 的 EDM 终端去噪是例外。

#### 4.2 Inverting World-Action Models

WAM 打破了 4.1 的前提。Cosmos-Policy 把动作块与未来世界状态、价值估计一起生成，它们是同一条潜视频序列的切片，形状是 $C\times T\times H\times W = 16\times 9\times 28\times 28$，没有一个纯动作的生成过程可反。

作者的选择是直接反演联合过程。反演目标从基座自己预测的干净潜张量 $x_0^{\text{base}}$ 出发，只在动作帧上加「专家减基座」的动作差，状态帧与价值帧保持基座输出不变。这个 minimal-delta swap 的用意是让目标留在基座流形上，反向过程恢复出的 $w^*$ 能重现完整的 $x_0^*$，而不只是动作切片。

Cosmos-Policy 用的是 EDM 调度而不是 flow-matching ODE，附录 A.1 补了这处修改。调度不终止于零噪声，而是从 $\sigma_{\max}=80$ 降到非零的 $\sigma_{\min}=4$，前向采样器是 $\sigma_{\max}\to\sigma_{\min}$ 的 1-Euler 积分加一次终端去噪 $D(\cdot,\sigma_{\min})$。1-Euler 部分照旧用逐步不动点反，而终端去噪是一次强变换，单步显式反向反不回来，只能用一段短的 Adam 局部求解，锚定在基座自己的 pre-terminal 状态上，每步 Adam 反传一次去噪器。

#### 关键证据 / 图表 / 公式

- 附录 A.2 给出反例数字。只优化动作帧噪声（本文配置里 112 维）会卡在不小的重构误差上，反演基座自己的动作时约 0.04，反演真实专家动作时 0.076，而且去噪步数越多越差，因为链式去噪目标对动作帧噪声高度非凸。
- 附录 A.3 说明高维联合噪声怎么回归。反演器返回的联合噪声约 $10^5$ 维，$\pi_w$ 直接回归不动，作者比较了 Full（回归整个联合潜）与 Basis（回归 $k=64$ 个 PCA 系数），两者都能用，Basis 更稳，是 Cosmos-Policy 实验的默认。
- 这里作者顺手戳了 DSRL 一下，DSRL 为了让 SAC 稳定，把 $\pi_0$ 的 1600 维块噪声压成一个逐步向量并在整块重复；监督回归不需要这种降维。

#### 4.3 FlowDAgger: Human-in-the-Loop Adaptation

噪声策略 $\pi_w$ 是一个观测编码器加 MLP，参数 $\phi$ 与冻结基座完全分离。部署时把标准抽样 $w\sim\mathcal N(0,I)$ 换成确定性的 $\pi_w(s)$。

$$
a = \pi_{gp}\big(s, \pi_w(s)\big).
$$

适配循环照 DAgger 的方式在线收纠正。当前策略带人部署，操作员觉得行为不满意就介入给 $a^*$，得到策略真正访问过的状态上的纠正对 $(s,a^*)$。反演成 $(s,w^*)$ 后进训练集 $\mathcal D$，噪声策略回归这些目标。

$$
\mathcal L(\phi) = \mathbb E_{(s,w^*)\sim\mathcal D}\big\|\pi_w(s)-w^*\big\|_2^2.
$$

这一节最有工程价值的是双缓冲区设计。纠正相对策略自身的转移非常稀疏，只在纠正上回归会把 $\pi_w$ 过拟合到那几十个被介入的状态。作者把 $\mathcal D$ 拆成两个缓冲区，反演纠正进 intervention buffer，成功自主 rollout 里每个转移真正用过的噪声进第二个 buffer，每个训练 batch 从两边等比例抽。自主 buffer 把 $\pi_w$ 锚在基座已能处理的状态上，固定比例又保证稀疏纠正在每次更新里都不被淹没。

#### 关键证据 / 图表 / 公式

- Equation 4 是部署形式，Equation 5 是训练目标，两条合起来说明整个方法只有一个 L2 回归，没有奖励、没有 critic、没有对基座的梯度。
- 双缓冲区的等比例采样是论文给的唯一防过拟合手段，没有做比例消融，这里作者没给证据。

### 5 Experiments

实验节明确列了四个问题，样本与算力效率如何、能否跨基座族、是否比微调更能保住先验、真机上是否兑现。

#### 5.1 Setup

任务覆盖从基础抓放到接触密集与双臂。仿真用 MetaWorld，真机用两个双臂平台，FR3 Duo（两条 FR3 臂）和 Dual UR5e，按任务决定控一条臂还是两条。单臂任务是 Block Pick、Glassware Stacking 以及 BusyBox 基准的三个任务（Button Push、Slider、Wire Pull），双臂任务是 Jenga Stack、Toolbox Packing、Plug Insertion。

![[papers/images/murray2026flowdagger/glassware.jpg|360]] ![[papers/images/murray2026flowdagger/busybox.jpg|360]]

![[papers/images/murray2026flowdagger/toolbox.jpg|240]] ![[papers/images/murray2026flowdagger/jenga.jpg|240]] ![[papers/images/murray2026flowdagger/plug_insertion_b.jpg|240]]

Figure 2 的实拍图说明了任务形态，Glassware Stacking 与 Plug Insertion 属于误差容限很小的接触密集操作，Toolbox Packing 与 Jenga 属于需要双臂配合的装载与堆叠。

基座各取一族的代表，$\pi_{0.5}$ 代表 action-head VLA，Cosmos-Policy 代表 WAM。前者走 4.1 的动作空间反演，后者走 4.2 的联合反演。附录 B 再补 Gr00t N1.7 和一个 vanilla diffusion policy。

基线的排布很讲究，每一个都在隔离一个变量。冻结基座定起点。SFT 对离线示范做全权重行为克隆，隔离的是「在线监督带来的协变量偏移修正」这一项。LoRA-DAgger 和 Residual-DAgger 吃同一条纠正流，但分别把纠正写进低秩权重和动作残差，隔离的是「在噪声空间适配」这一项。DSRL 同样在噪声空间，但学的是稀疏奖励下的自主探索，隔离的是「监督信号来源」。除非另有说明，每个方法都给 $N=50$ 个额外 rollout 的匹配预算，报 3 seeds、每 seed 25 rollouts 的平均成功率。

#### 关键证据 / 图表 / 公式

- Figure 2 只给任务形态，不给数值。
- 基线设计本身是这篇论文方法论上最扎实的部分，三个隔离变量清清楚楚。缺的是一个「同样在噪声空间、但用轨迹级反演」的对照，那部分放在附录 B.1 而不是主表。

#### 5.2 FlowDAgger adapts $\pi_{0.5}$ from a handful of corrections

Table 1 在 12 个 MetaWorld 任务上对齐所有基线。

| Task | Base | SFT | LoRA-DAg. | Res-DAg. | DSRL | FlowDAgger |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Assembly | 0.64 | 0.85 | 0.81 | 0.53 | 0.64 | **0.89** |
| Bin Picking | 0.56 | **0.76** | 0.68 | 0.63 | **0.76** | 0.69 |
| Box Close | 0.36 | **0.70** | 0.52 | 0.69 | 0.48 | 0.59 |
| Coffee Pull | 0.84 | 0.96 | 0.68 | 0.95 | 0.84 | **1.00** |
| Dial Turn | 0.20 | 0.64 | **0.88** | 0.59 | 0.43 | 0.75 |
| Door Lock | 0.44 | 0.48 | 0.76 | **0.85** | 0.28 | 0.75 |
| Hammer | 0.40 | 0.80 | 0.68 | 0.56 | 0.27 | **0.84** |
| Hand Insert | 0.84 | 0.88 | 0.72 | 0.71 | 0.92 | **0.99** |
| Lever Pull | 0.28 | 0.44 | 0.52 | 0.37 | 0.35 | **0.61** |
| Pick Place | 0.76 | 0.80 | 0.68 | 0.71 | 0.60 | **0.85** |
| Soccer | 0.24 | 0.36 | 0.32 | 0.28 | 0.33 | **0.44** |
| Stick Push | 0.84 | 0.84 | 0.92 | 0.84 | 0.73 | **1.00** |
| Mean SR | 0.53 | 0.71 | 0.68 | 0.64 | 0.55 | **0.78** |
| $\Delta$ vs. Base | – | +0.18 | +0.15 | +0.11 | +0.02 | **+0.25** |

三条读法值得记住。FlowDAgger 拿到最大均值提升并在 12 个里赢 8 个。动作空间与权重空间的 DAgger 吃同一条纠正流却收益小得多，所以优势来自纠正被写到哪里，而不是纠正本身。DSRL 几乎没动基座，稀疏奖励加自主探索在 50 个 rollout 里发现不了几次干预就能直接给出的纠正行为。

![[papers/images/murray2026flowdagger/success_rate_metaworld_page1.png|760]]

Figure 3 把静态表格变成训练曲线，五个任务上 FlowDAgger 升得最快也最高，而且五条线都平滑。Residual-DAgger 学得很不稳，在 Hammer 上来回震荡，在 Assembly 和 Hand Insert 上先升后塌到基座以下。

作者对 Door Lock 这个唯一的例外给了合理解释。无约束动作空间修正只有在「一个小而一致的偏移就够」的时候才是良态问题，Door Lock 正是这种情况，Residual-DAgger 在那里平滑上升并略微领先。噪声空间操纵留在基座流形上，所以无论纠正幅度多大，适配都保持稳定。

![[papers/images/murray2026flowdagger/compute_efficiency_assembly_page1.png|560]]

Figure 4 换了个坐标看同一件事，横轴是训练峰值显存的对数刻度，纵轴是 Assembly 在 $N=50$ 时的成功率。FlowDAgger 独占左上角，精度不输任何基线而显存只有零头。适配所需显存约 8 GB，和部署 $\pi_{0.5}$ 本来就要的量级相同。

#### 关键证据 / 图表 / 公式

- Table 1 是全文最强的单张证据表，但它没有给每格的 seed 方差，只说 3 seeds 平均。
- Figure 3 的阴影带是 per-seed 的 min/max 而不是置信区间，读的时候不要当成统计显著性。
- Figure 4 的横轴刻度标了 8、22.5、70 三个位置，SFT 落在最右。

#### 5.3 Adaptation transfers across base-policy families

Table 2 在 7 个共享任务上把同一套流程分别用在 $\pi_{0.5}$ 和 Cosmos-Policy 上。

| Task | $\pi_{0.5}$ Base | $\pi_{0.5}$ Flow | $\Delta$ | Cosmos Base | Cosmos Flow | $\Delta$ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Assembly | 0.64 | 0.89 | +0.25 | 0.52 | 0.92 | +0.40 |
| Bin Picking | 0.56 | 0.69 | +0.13 | 0.28 | 0.44 | +0.16 |
| Box Close | 0.36 | 0.59 | +0.23 | 0.36 | 0.64 | +0.28 |
| Dial Turn | 0.20 | 0.75 | +0.55 | 0.44 | 0.68 | +0.24 |
| Hand Insert | 0.84 | 0.99 | +0.15 | 0.76 | 0.88 | +0.12 |
| Lever Pull | 0.28 | 0.61 | +0.33 | 0.56 | 0.64 | +0.08 |
| Stick Push | 0.84 | 1.00 | +0.16 | 0.76 | 0.96 | +0.20 |
| Mean | 0.53 | 0.79 | +0.26 | 0.53 | 0.74 | +0.21 |

两族的增益量级相当，尽管 Cosmos-Policy 的动作只是联合世界动作潜张量的切片，没有可分离的动作头。作者据此说 FlowDAgger 不依赖一个纯动作的生成过程。这条结论对做 WAM 的人价值最大，它说明只要生成过程是可反演的确定性积分，人类干预就有地方落。

#### 关键证据 / 图表 / 公式

- Table 2 的两个 Base 列均值都恰好是 0.53，这是任务集选择的巧合，不要读成两个基座能力相同，逐任务看差别不小（Dial Turn 0.20 对 0.44，Lever Pull 0.28 对 0.56）。
- 附录 B.3 与 B.4 把族的覆盖再扩两个，但都只有单 seed、每点 15 rollouts。

#### 5.4 Noise-space adaptation preserves the base prior

这一节的实验设计很干净。在 Hammer 上适配 50 个 episode（SFT 用 50 条示范并匹配梯度步预算），然后到 5 个基座近乎饱和的留出任务上评。

| Method | Hammer（域内） | Door | Drawer | Faucet | Plate | Push | Held-out Mean | $\Delta$ vs base |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Base $\pi_{0.5}$ | 0.40 | 1.00 | 1.00 | 0.96 | 0.88 | 0.96 | 0.96 | — |
| FlowDAgger | **0.84** | 0.88 | 1.00 | 0.96 | 1.00 | 0.56 | **0.88** | **−0.08** |
| Residual-DAg | 0.56 | 0.88 | 0.68 | 0.80 | 1.00 | 0.08 | 0.69 | −0.27 |
| LoRA-DAg | 0.68 | 0.80 | 0.00 | 0.36 | 0.00 | 0.36 | 0.30 | −0.66 |
| SFT（50 demos） | 0.80 | 0.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.02 | −0.94 |

数字本身比作者的措辞更有冲击力。SFT 把 Hammer 从 0.40 拉到 0.80，代价是五个留出任务几乎全部归零，均值从 0.96 掉到 0.02。LoRA-DAgger 好一点但 Drawer 和 Plate 也直接归零。Residual-DAgger 保住了大半先验，可它的域内收益本来就小，作者点破了这一点，它保住先验只是因为它几乎没适配。

只有 FlowDAgger 两头都要到了。不过留出集里的 Push 从 0.96 掉到 0.56，是 FlowDAgger 唯一明显的退化项，均值 −0.08 里几乎全部来自这一个任务。这条不能被平均数盖过去。

#### 关键证据 / 图表 / 公式

- Table 3 是全文对「保先验」这条主张最直接的证据，加粗规则是「在基座噪声范围内或更高」。
- 留出任务只有 5 个且都接近饱和，这个设置对权重法不利，也不能代表更广的技能保持。
- SFT 这一行标注了 openpi finetune，50 条示范做全参数微调本来就容易过拟合，这个对照更像是给出代价上界而不是最优微调实践。

#### 5.5 Real-world adaptation

真机在 FR3 Duo 与 Dual UR5e 上跑 8 个任务，每个报 30 次 rollout。

| Task | Base | SFT | FlowDAgger（$\Delta$） | 干预 episode 数 |
| --- | ---: | ---: | ---: | ---: |
| Block Pick | 0.73 | 0.80 | **0.90** (+0.17) | 5 |
| Glassware Stacking | 0.26 | 0.53 | **0.76** (+0.50) | 5 |
| Button Push | 0.60 | **0.73** | **0.73** (+0.13) | 10 |
| Slider | 0.36 | 0.43 | **0.66** (+0.30) | 5 |
| Wire Pull | 0.40 | 0.53 | **0.70** (+0.30) | 10 |
| Jenga Stacking | 0.76 | **0.90** | 0.86 (+0.10) | 5 |
| Toolbox Packing | 0.13 | 0.63 | **0.80** (+0.67) | 10 |
| Plug Insertion | 0.60 | 0.66 | **0.72** (+0.12) | 20 |

最能说明问题的是 Toolbox Packing，10 次纠正把 13% 提到 80%，一个基本不可用的策略变成可靠策略，而基础模型一个参数没动。除了 Jenga Stacking 被 SFT 略微超过之外，FlowDAgger 在每个任务上都赢 SFT。

#### 关键证据 / 图表 / 公式

- Table 4 是真机唯一一张表，对照只有 base 与 SFT，Residual-DAgger、LoRA-DAgger、DSRL 都没上真机。这是主表覆盖上的一个缺口。
- 30 次 rollout 的粒度是 1/30 约 3.3 个点，Jenga 的 0.86 与 0.90 差距只有一次多的 rollout，不宜过度解读。
- 干预 episode 数从 5 到 20 不等，作者没说这个数是怎么定的，是预设预算还是达标即停。

### 6 Limitations

作者自己划了三条边界，写得比多数论文诚实。

第一条是支撑集边界。像其他潜空间适配方法一样，FlowDAgger 通过操纵冻结策略的潜变量改变行为，而不是改策略本身，所以适配能力被预训练模型的支撑集限住。想要的行为若远在策略动作流形之外，反演只能恢复基座可表示的最接近行为，这时还得靠加数据或权重空间适配。

第二条是干预质量。与其他 DAgger 系方法一样，只有给了纠正监督的状态区域才能改善，纠正里的系统性偏差或不一致会被原样学进适配策略。

第三条是反演精度。高度多模态的动作分布或条件很差的生成动力学都会让反演精度下降，专家纠正在潜空间的表示保真度随之降低。

#### 关键证据 / 图表 / 公式

三条边界都是定性陈述，论文没有给出对应的量化实验。附录 B.1 的 Euler-reverse 一行算是第三条的间接证据，反演误差高于约 0.03 Action MSE 的目标会腐蚀而不是引导策略，Assembly 上 0.59 甚至低于冻结基座的 0.64。

### 7 Conclusion

结论把方法抬到一个更一般的立场上。作者说 FlowDAgger 把交互当成对冻结生成式策略潜决策的监督，与其修改基础模型参数去吸收新经验，不如恢复出「本该产生专家行为的那个潜决策」并直接学会复现它。这个视角把适配与模型规模解耦，保住预训练能力，也给出一条让基础模型通过交互变好而仍然稳定、可复用、算得起的路径。

### Appendix A World-Action Model Inversion Details

A.1 交代 EDM 调度反演。逐步不动点照搬，因为每步只依赖当前潜变量和噪声水平，反演是无记忆且无梯度的；只有 $\sigma_{\min}$ 处的终端去噪需要短 Adam 求解并对基座反传，这是整个反演器里唯一反传的部分。

A.2 用数字回答「为什么不只反演动作帧」。早期版本只对动作帧噪声（112 维）做 Adam 优化，非动作帧固定，最小化经过链式去噪的动作重构损失，结果稳定卡在 0.04（反演基座自己的动作）与 0.076（反演真实专家动作），而且去噪步数越多越差。

A.3 处理高维联合噪声的回归。Full 直接回归整个联合潜，容量最大但没有先验；Basis 回归在短暂 warmup 中收集的反演噪声上拟合的 $k=64$ 个 PCA 系数，把输出锚在成功基座噪声的流形上。两者都能用，Basis 更稳，成为默认。

### Appendix B Additional Experiments

B.1 是全文方法论上最有价值的附录。四种反演器在 assembly 上反同样的 29 条脚本专家动作块。

| Method | Action MSE | Time (ms) | SR (Assembly) | SR (Hammer) |
| --- | ---: | ---: | ---: | ---: |
| Euler reverse | 0.0329 | 315 | 0.59 | 0.71 |
| Optimization (Adam, 20 steps) | 0.0275 | 1350 | 0.79 | 0.75 |
| Trajectory FP ($k=5$) | 0.0228 | 1662 | 0.77 | 0.68 |
| Per-step FP ($M=5$, default) | **0.00168** | 456 | **0.87** | **0.96** |

逐步不动点比所有轨迹级方案精确约一个数量级，同时快约 3 倍。作者的解释是轨迹级方法校正的是一个全局残差，无法归因到任何单步，而在 $\Delta t = 0.1$ 时逐步线性化误差太大，全局残差消不掉。这与图像扩散领域的结论并不矛盾，那些结论建立在 50 到 1000 步调度的极小逐步误差上，少步动作头处在另一个 regime。

更关键的是这些重构差距会传导到下游。Euler-reverse 监督把噪声策略压到 0.59，低于冻结基座的 0.64，噪声高于约 0.03 Action MSE 的目标是在腐蚀而不是引导策略。所以精确反演不只是更快到达同一天花板，而是抬高了天花板本身。

B.2 扫迭代数。逐步 FP 从 $M=3$ 到 $M=5$，Action MSE 降 2.4 倍；$M=5$ 到 $M=10$ 只再降 1.1 倍而耗时涨 1.3 倍，所以默认取 5。轨迹级 FP 从 $k=5$ 到 $k=20$ 没有可测的改善，全局残差里能提取的信息已经取尽。作者还给了一个匹配算力的比较，$k=5$ 与 $M=10$ 都是 110 次模型求值，即便如此逐步 FP 的 MSE 仍低约 15 倍且快约 2.7 倍。

![[papers/images/murray2026flowdagger/appendix_groot_libero_page1.png|560]]

B.3 换到 Gr00t N1.7，用作者发布的 LIBERO-10 checkpoint，评在训练集外的 LIBERO-90 task 57，零样本 60%。为让 SAC 在 Gr00t 的 $40\times 132 = 5280$ 维噪声空间里可训，DSRL 把噪声投到 $K=10$ 的 DCT-II 多项式基（1320 维有效动作空间）。FlowDAgger 5 个 episode 追平基座，第 20 个 episode 逼近 100%；DSRL 也升但停在约 70%。

![[papers/images/murray2026flowdagger/appendix_dp_lift_page1.png|560]]

B.4 换到 vanilla DDPM diffusion policy，在 robomimic LIFT 的低维状态观测上适配，基座约 48%。FlowDAgger 第 25 个 episode 到约 97%，DSRL 停在约 80%。作者主动解释了为什么这里的差距比 Gr00t 小，这个基座的动作与噪声空间维度低得多，DSRL 只靠任务奖励的搜索更可行，而且 LIFT 的稠密进展结构让奖励信号本身就有信息量。这段自我归因写得比结果本身更值得读。

## 方法细节

把 FlowDAgger 串成一次完整的部署到更新循环，可以分成四段。

部署段。当前 $\pi_w$ 给出确定性噪声 $\pi_w(s)$，送进冻结基座的 $K$ 步 Euler 积分得到动作块并执行。没有采样随机性，部署行为可复现。

采集段。人在环观察，觉得不满意就介入给 $a^*$，得到 $(s,a^*)$。这些状态是当前适配后的策略真正访问的状态，所以 $\mathcal D$ 会随轮次推进而跟着策略分布走。

反演段。从 $x_K = a^*$ 出发，对每个 Euler 步解一次隐式方程，每步 $M=5$ 次不动点迭代，共 $KM$ 次速度场求值，得到 $w^* = x_0$。动作头分支不反传；WAM 分支只在 $\sigma_{\min}$ 的终端去噪处反传。反演在线做，纠正一边收一边反。

更新段。$(s,w^*)$ 进干预缓冲区，成功自主 rollout 里每个转移用过的噪声进自主缓冲区，每个 batch 两边等比例抽，L2 回归 $\pi_w$。轮次之间 $\mathcal D$ 累积，所以后期的纠正针对的是适配后策略诱导的状态。

WAM 分支多两处改造。反演目标用 minimal-delta swap 构造，只在动作帧加专家减基座的差；$\pi_w$ 的输出用 64 维 PCA 基而不是全维联合潜。两处都在做同一件事，把适配约束在基座已经能产生的成功噪声流形附近。

## 实验设置、数据集、基线、指标

| 实验组 | 基座与接口 | 评测 | 目的 |
| --- | --- | --- | --- |
| MetaWorld 主表 | $\pi_{0.5}$，动作空间反演 | 12 任务，3 seeds $\times$ 25 rollouts，$N=50$ | 与 SFT、LoRA、Residual、DSRL 对齐比较 |
| 跨族 | $\pi_{0.5}$ 与 Cosmos-Policy | 7 共享任务，同上预算 | 检验是否依赖可分离动作头 |
| 保先验 | $\pi_{0.5}$，Hammer 适配 | 5 个饱和留出任务 | 量化适配对预训练技能的破坏 |
| 真机 | $\pi_{0.5}$ | FR3 Duo 与 Dual UR5e，8 任务 $\times$ 30 rollouts | 检验低干预预算下的实用性 |
| 反演器对照 | $\pi_{0.5}$，assembly | 29 条脚本专家块，RTX 5090 | 隔离反演精度对下游成功率的影响 |
| 附录复现 | Gr00t N1.7、DDPM diffusion policy | LIBERO-90 task 57、robomimic LIFT，单 seed $\times$ 15 rollouts | 检验结论不是针对两个基座调出来的 |

指标只有三类，任务成功率、Action MSE（4 维环境动作空间，每维范围 $[-1,1]$）与训练峰值显存。论文没有报控制频率、推理延迟、$\pi_w$ 的参数量、每个真机任务的干预时长，也没有给 Table 1 每格的方差。

## 主要结果、消融或对比

同一批纠正下适配位置的差异最清楚。FlowDAgger +0.25，LoRA-DAgger +0.15，Residual-DAgger +0.11，三者吃的是同一条纠正流，差别只在纠正被写去哪里。

监督来源的差异同样清楚。DSRL 与 FlowDAgger 在同一个噪声空间，前者 +0.02，后者 +0.25。50 个 rollout 的自主探索加稀疏奖励，发现不了几次人类干预直接给出的行为。

先验保持的代价差了一个数量级。留出任务均值 FlowDAgger −0.08，Residual-DAgger −0.27，LoRA-DAgger −0.66，SFT −0.94。

反演精度直接决定天花板。Per-step FP 的 Action MSE 比 Euler reverse 低约 20 倍，下游 Assembly 成功率 0.87 对 0.59，后者甚至低于冻结基座。

跨族增益接近但不相同，$\pi_{0.5}$ +0.26、Cosmos-Policy +0.21。两个附录基座上 FlowDAgger 都比 DSRL 高，Gr00t 上差约 25 个百分点，diffusion policy 上差约 17 个百分点。

真机上 8 个任务全部改善，幅度从 +0.10 到 +0.67，干预预算 5 到 20 个 episode。

## 图表、公式与表格线索

| 编号 | 内容 | 支撑主张 | 阅读提醒 |
| --- | --- | --- | --- |
| Figure 1 | FlowDAgger 全局机制 | 基座冻结、只训 latent policy | 概念图，不给数值 |
| Figure 2 | 八个真机任务实拍 | 任务覆盖单臂、双臂、接触密集 | 只说明形态 |
| Figure 3 | 五个 MetaWorld 任务的适配曲线 | FlowDAgger 升得快且平滑 | 阴影是 per-seed min/max 不是置信区间 |
| Figure 4 | Assembly 成功率对训练显存 | 精度与显存双优 | 横轴对数刻度，只有一个任务 |
| Figure 5 | Gr00t N1.7 上 FlowDAgger 与 DSRL | 结论跨 VLA 成立 | 单 seed，每点 15 rollouts |
| Figure 6 | diffusion policy 上同样对照 | 结论跨 diffusion 成立 | 单 seed，差距明显收窄 |
| Table 1 | 12 任务全基线对照 | 适配位置决定收益 | 无每格方差，Door Lock 是反例 |
| Table 2 | 跨基座族 | 不依赖可分离动作头 | 两个 Base 均值同为 0.53 属巧合 |
| Table 3 | 留出任务先验保持 | 权重法代价大得多 | 留出任务只有 5 个且近饱和 |
| Table 4 | 真机八任务 | 低干预预算即见效 | 只对照 base 与 SFT |
| Table 5 | 四种反演器 | 逐步不动点是关键 | 只在 assembly 上测反演精度 |
| Table 6 | $M$ 与 $k$ 扫描 | $M=5$ 已收敛 | 给了匹配算力对照 |
| Equations 1–2 | 噪声到动作映射与 Euler 离散 | 反演的对象 | $K\approx 10$ 是后续论证支点 |
| Equation 3 | 逐步不动点迭代 | 本文核心机制 | 收敛条件 $\Delta t L<1$ 未实测 |
| Equations 4–5 | 部署形式与 L2 回归目标 | 整个方法只有一个回归 | 双缓冲区比例无消融 |

## 主张-证据-边界矩阵

| 主张 | 最强证据 | 证据强度 | 边界 |
| --- | --- | --- | --- |
| 适配接口比适配数据更决定结果 | Table 1 同一纠正流下 +0.25 对 +0.15 / +0.11 | 较强受控对照 | 12 个 MetaWorld 任务，Door Lock 反向 |
| 少步动作头必须逐步反演 | Table 5、Table 6 的 MSE 与下游 SR | 强，含匹配算力对照 | 只在 assembly 上测精度，只测 $K=10$ |
| 反演精度设定成功率上限 | Euler-reverse 监督把 Assembly 压到 0.59（基座 0.64） | 较强 | 单任务单反演器的因果链 |
| 机制不依赖可分离动作头 | Table 2，Cosmos-Policy +0.21 | 中等 | 每族一个代表模型 |
| 冻结基座保住预训练技能 | Table 3 留出均值 −0.08 对 −0.94 | 较强 | Push 从 0.96 掉到 0.56，5 个饱和任务 |
| 真机低预算可用 | Table 4 八任务全改善 | 中等 | 无 seed，只对 base 与 SFT |
| 比潜空间 RL 更省交互 | Table 1 DSRL +0.02，Figure 5、6 的曲线 | 中等 | 附录两图单 seed，作者自承 LIFT 上差距收窄 |
| 适配算得起 | Figure 4，约 8 GB | 中等 | 只测 Assembly 一个任务的峰值显存 |

## 局限与可追问点

最该追问的是「多少纠正才够」这条曲线论文没画。主表统一给 50 个 rollout 预算，真机给 5 到 20 个 episode，但没有一张图把成功率对干预次数画出来并给出饱和点。Figure 3 画的是 episode 而不是干预次数，两者在 human-gated 设定下并不等价。很多做 VLA 后训练的会遇到这个问题，采集预算怎么排是第一现实约束。

双缓冲区的等比例采样是唯一的防过拟合手段，却没有消融。比例改成 1:3 或 3:1 会怎样，自主 buffer 只收「成功」rollout 是否引入选择偏差，论文都没答。这里作者没给证据。

收敛条件 $\Delta t L < 1$ 是逐步不动点成立的前提，论文没有实测任何基座的 $L$，也没有报告不动点迭代的失败率或残差分布。$M=5$ 是经验值，Table 6 只给了三档。

真机部分的对照最薄。Residual-DAgger 和 LoRA-DAgger 在仿真里是核心对照组，到真机就消失了，只剩 SFT。真机恰恰是「保先验」最值钱的场景，缺这两组对照让 Table 3 的结论无法在真机上复验。

留出任务的选择偏向对权重法不利。5 个任务的基座成功率分别是 1.00、1.00、0.96、0.88、0.96，本来就接近天花板，掉下来特别显眼。若换成基座中等水平的任务，四种方法的相对排序未必一样。

WAM 分支的证据比动作头分支薄不少。Cosmos-Policy 只在 7 个 MetaWorld 任务上跑，没上真机，Basis 与 Full 的对照只有一句「both worked, Basis somewhat more stable」，没有数字。反演一次 WAM 的耗时也没报，而它比动作头多一段 Adam 求解。

Table 1 的 3 seeds 平均没有给方差。Bin Picking 上 FlowDAgger 的 0.69 低于 SFT 与 DSRL 的 0.76，Box Close 上 0.59 低于 SFT 的 0.70 与 Residual 的 0.69，这两格靠平均值盖过去了。说实话也不确定这些是任务特性还是 seed 噪声。

## 我的阅读判断

这篇的贡献点值得画出来的是一句方法论上的话，人类纠正的信息该以什么形式进入一个冻结的生成模型。动作空间残差把它当成加性偏移，权重微调把它当成新的训练样本，FlowDAgger 把它当成「本该被抽到的那个噪声」。三种理解对应三种代价结构，Table 3 那一列 −0.08 对 −0.94 就是三种理解的价签。

Table 5 比主表更能说服我。它把「反演精度」这个中间量与「下游成功率」这个终点量直接连起来，而且给出了一个反向案例，反演不准时监督会把策略压到基座以下。有这条因果链，方法就不只是又一个 DAgger 变体，而是一个可以被独立检验的组件。

真正的隐忧在支撑集这条边界上。FlowDAgger 能做的一切都限制在基座能生成的行为里，作者自己也承认。Toolbox Packing 从 13% 到 80% 之所以成立，是因为正确行为本来就在 $\pi_{0.5}$ 的流形上，只是被错误的噪声抽样掩盖了。遇到基座压根没学过的新技能，这套机制给不出增益，而论文没有构造这样的反例任务。

与 [[@yu2026wm-dagger|WM-DAgger]] 放在一起读最有意思。两者都在补 DAgger 的数据，但一个用世界模型合成 recovery trajectory，另一个把人类真实纠正反演回噪声。前者省人力但要承担合成数据的误监督风险，后者要人在环但每条监督都是真的。选哪条，取决于你的瓶颈是人还是数据质量。

## 与当前库的连接

- [[@yu2026wm-dagger|WM-DAgger]] 同样在解 DAgger 的数据聚合问题，用 eye-in-hand action-conditioned world model 合成 OOD recovery 轨迹并做方向约束过滤。和 FlowDAgger 对读，能区分「合成纠正」与「反演真实纠正」两条路的成本与风险。
- [[@luo2024precise-dexterous-robotic-manipulation|HIL-SERL]] 与 [[@deng2026e2hil|E2HiL]] 把人类干预折进真机 RL 回路，需要奖励与在线更新。FlowDAgger 走的是纯监督回归，不需要奖励，对比这三篇能看清人在环学习里「要不要奖励」这条分叉。
- [[@xiao2026rove|ROVE]] 做人形机器人的干预后训练，关注的是干预怎样变成有效梯度。FlowDAgger 的答案是根本不给基座梯度。
- [[@pan2026vla-corrector-lightweight-detect|VLA-Corrector]] 在推理期检测并纠正，与 FlowDAgger 的部署形态互补，一个负责「什么时候该管」，一个负责「管了之后怎么写回去」。
- [[@intelligence2026pi07-steerable-generalist-robotic|π0.7]] 与 [[@intelligence2025pi06-vla-that-learns|π*0.6 / RECAP]] 都在讨论可操控与经验后训练，FlowDAgger 提供了一个不改权重的操控接口，适合和它们一起看「基础模型该在哪一层被定制」。
- [[@zhang2026lingbot-va2|LingBot-VA 2.0]] 与 [[@wang2026wvm|WVM]] 属于 WAM 与价值模型一侧，Table 2 的 Cosmos-Policy 分支说明这类联合生成模型同样存在可用的适配面。

## 精读路线 / 为什么需要回看

第一遍只看 Figure 1、Equation 3 和 Table 1。三处分别回答机制长什么样、反演怎么算、同一批纠正写在不同地方差多少。读通这三处，全文骨架就立住了。

第二遍看 Table 5 与 Table 6。它们是把「反演」从实现细节抬成研究对象的地方，也是唯一给出反例的地方。Euler-reverse 那一行的 0.59 低于基座 0.64，这个数字比任何正面结果都更能说明反演精度不是可选项。

第三遍看 Table 3 与 Section 5.4 的正文。数字要逐格读，不要停在均值上。FlowDAgger 的 Push 从 0.96 掉到 0.56，Residual-DAgger 的 Push 掉到 0.08，两者的失败位置一样，只是幅度不同，这提示留出集里 Push 可能与 Hammer 存在某种干扰关系。

第四遍回附录 A。A.2 的 0.04 与 0.076 解释了为什么 WAM 分支必须反演联合过程，A.3 的 PCA 基解释了 $10^5$ 维噪声怎么回归。做 WAM 的读者应该把这两小节当正文读。

等代码公开后最该补看的不是演示视频，而是三样东西，噪声策略 $\pi_w$ 的具体结构与参数量、双缓冲区的采样比例与它的消融、以及每个真机任务的干预时长与操作员一致性。可以确定的是，这三样会决定 FlowDAgger 是一套可以照抄的配方，还是一个需要按基座重新调的技巧。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
