---
tags:
  - bilingual-reading
  - deep-reading
paper: "[[@kim2026ego-pi]]"
source_pdf: "[[papers/pdfs/2606.08107v1.pdf]]"
images: "papers/images/2606.08107v1/"
image_index: "[[papers/images/2606.08107v1/index.md]]"
created: 2026-07-18
reading_mode: 生成式精读（逐节读原文 + 补充材料 + 读图）
---

# Ego-Pi: VLA Fine-Tuning for Ego-Centric Human and Robot Data

paper:: [[@kim2026ego-pi]]
pdf:: [[papers/pdfs/2606.08107v1.pdf]]
images:: [[papers/images/2606.08107v1/index.md]]

> [!info] 版本说明
> 本稿解析 arXiv `2606.08107v1`。PDF 自述为 **CVPR 2026 论文的 expanded version（扩展版）**，作者来自 Stanford University 与 Meta。

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| egocentric human data | 人类第一视角数据 | 论文用于缓解机器人数据稀缺的入口；但本版本实际实现写的是桌面固定 ZED，结果段还称 human data 为 third-person，需校准名实。 |
| cross-embodiment learning | 跨本体学习 | 把人手与机器人灵巧手的数据放进同一 VLA 训练，目标是从人类示范迁移任务语义。 |
| task-semantic transfer | 任务语义迁移 | 本文真正评测对象：sorting logic、skill chaining、rule-based ordering，而非只提高同任务成功率。 |
| zero target-task robot demonstrations | 目标任务零机器人示范 | 目标组合任务没有对应机器人轨迹；但机器人已经学过组成它的低层原子技能。 |
| Vision-Language-Action (VLA) | 视觉-语言-动作模型 | 以 $\pi_{0.5}$ 为基座，把图像、语言、状态映射到连续 action chunk。 |
| $\pi_{0.5}$ | VLA 基础模型 | 提供预训练 VLM + flow-matching action expert；原 action token 最多 32 维。 |
| flow matching | 流匹配 | 从 Gaussian noise 沿连续路径生成短时域动作，是 $\pi_{0.5}$ 的动作训练目标。 |
| dexterous bimanual control | 灵巧双手控制 | Tesollo 每手 20 个手指关节，连腕位姿为 29D；双手 58D 超过原 head 容量。 |
| action interleaving | 动作交错 | 把同一时刻左/右手动作拆到连续两个 action token，保留原 32D projection head。 |
| effective action horizon | 有效动作时域 | interleaving 以容量换时域：固定 token budget 下，双手时间步从 $H$ 降为约 $H/2$。 |
| robot-centric action representation | 机器人中心动作表示 | 人手角度先映射到 robot-native joint angles，训练时人/机器人共享同一动作坐标语义。 |
| joint retargeting | 关节重映射 | 用逐关节 offset/scale 把 Manus/MANO 角度映到 Tesollo，避免 fingertip IK 的自碰/怪姿势。 |
| skeleton overlay | 骨架叠加 | 给五根手指固定颜色并按深度处理遮挡，试图缩小人手/机器手视觉外观差；实验收益很弱。 |
| subtask prediction / generation | 子任务预测 / 生成 | VLM 先输出 `open box`、`pick block` 等离散中间语义，再由 action expert 动作；Boxing 的关键组件。 |
| skill composition / chaining | 技能组合 / 串联 | 机器人只见过“开盒”和“抓放”分技能，人类示范提供先后关系，测试要求组合成 Boxing。 |
| precondition | 前置条件 | Boxing 中必须先让“盒子已打开”成立，才能放 block；简单混训最容易在这里失败。 |
| rule-based ordering | 规则式顺序 | Packaging 要先放较重/硬的小盒，再放 teddy bear，顺序只由人类示范给出。 |
| wrist-camera dropout | 腕相机丢弃 | 人类数据没有 wrist views；训练时随机丢 40% 机器人腕图以减小输入缺失差异。 |

## 摘要

Ego-Pi 从机器人数据稀缺出发，提出一个比“人类数据能否提高同分布任务表现”更强的问题：**机器人没有看过某个目标组合任务的机器人示范时，能不能从人类数据继承这个任务的高层语义？** 论文选了三个具体语义：按颜色分拣、把已有技能按先后串起来、按规则决定物体放置顺序。

方法建立在 $\pi_{0.5}$ 上。第一道障碍是动作容量：Tesollo 单手含腕位置 3D、腕旋转 6D 和 20 个手指关节，共 29D；双手 58D 超过预训练 action head 的 32D。Ego-Pi 不扩 projection layer，而把左、右手动作交错进两个 token，从而尽量保留预训练参数。第二道障碍是 embodiment alignment（本体对齐）：作者不让模型预测 fingertip 再跑高维 IK，而把人手角度用手工 offset/scale 映射到机器人 joint space。第三道障碍是高层顺序：模型可在动作前先生成 subtask string，让 VLM 显式表示当前阶段。

实验支持一个很具体的结论：**当目标任务只是把机器人已有低层技能按人类示范给出的规则重新组织时，人类数据可以有效传递语义；遇到带前置条件的双手技能串联，仅靠混合数据不够，显式 subtask prediction 才是关键。** Tomato Sorting 从 robot-only 40% 升至 92%，Packaging 从 10% 升至 90%；Boxing 的简单 human+robot co-training 只有 27%，加入 subtask 后到 93%，再加 skeleton 为 100%。同时，skeleton overlay 本身没有稳定收益，Tesollo 大手在 Boxing 只到 67%，显示视觉/形态 gap 仍未被解决。

## 论文主线

![[papers/images/2606.08107v1/intro_v14_page1.png|920]]

**Figure 1 / 全文命题。** 左侧 robot demos 提供能落地的低层运动，human demos 提供目标任务的语义结构；中间 Ego-Pi 用 VLM 生成可选 subtask，并在 action expert 中交错输出左右手动作；右侧不是简单“同任务泛化”，而是三种新组合：sorting logic（分类规则）、sequential skill chaining（先后串联）、rule-based ordering（重物优先）。

全文因果链可以这样读：

1. 机器人交互数据贵，人类操作数据相对易采；人形/灵巧手让两种本体的形态差距缩小。
2. 但预训练 VLA 多为低维 gripper：动作 head 容量不够、human joint 与 robot joint 不同、图像外观也不同。
3. Ego-Pi 用 interleaving 解容量、robot-centric retargeting 解动作坐标、skeleton 解视觉对应、subtask prediction 解任务阶段。
4. 三个 benchmark 刻意把 robot low-level skills 与 human high-level semantics 分开，再看测试时能否合成目标行为。
5. 结果表明 interleaving + co-training 能支撑简单规则迁移；真正带 precondition 的 Boxing 还需要显式语言中间变量。视觉 skeleton 并不是决定因素。
6. 因此论文最强结论是“human data 可以教 semantic composition”，而不是“人类视频已经能直接教会机器人全新 dexterous motor skills”。

## 贡献与结论对照

| 贡献 / 结论 | 方法位置 | 关键证据 | 应如何定性 |
| --- | --- | --- | --- |
| 用两个 token 容纳 58D 双手动作而不改预训练 head | §3.3，Fig.2 | 模型能在 Tesollo/Inspire 真机收敛并执行三任务 | 证明方案可用；未给扩 head 的完整数值消融，且 horizon 减半。 |
| 把人手动作映到 robot-native joint space | §3.2、Supplement §8 | 真机跨本体联合训练可运行；附录公开逐关节映射 | 是工程上清楚的对齐接口；映射手工、平台特定。 |
| 从无目标任务机器人 demo 的人类数据迁移高层语义 | §5–6，Fig.4/5 | Sorting 92%、Packaging 90%、Boxing+subtask 93% | 目标组合无 robot demo，但低层组成技能有 robot demo。 |
| subtask generation 解锁困难 skill chaining | §6 Q2 | Boxing 27%→93%，加 skeleton 后 100% | 本文最清晰的机制消融；样本只有约 15 次评估。 |
| skeleton overlay 缩小视觉本体差 | §3.4，Fig.3 | Sorting 92→92；Boxing skeleton-only 7，subtask 93→100 | 总体不支持它是必要组件；100 vs 93 可能只差 1 次 trial。 |
| 更像人的 hand morphology 更利于迁移 | §6 Q3 | Inspire+subtask 93%，Tesollo+subtask 67% | 有启发，但关节数/动作维度/控制难度均混杂。 |
| 人类无腕图仍不妨碍机器人使用腕图 | §4、§6 Q4 | 测试移除 wrist images 后抓番茄明显变差 | 仅定性，没有成功率或不同 dropout rate 曲线。 |

## 结构地图

| 原文位置 | 作者在做什么 | 与全文主线的关系 | 关键图表 / 公式 |
| --- | --- | --- | --- |
| Abstract | 提出人类数据可教新 task semantics / composition | 给出结论范围 | 摘要无数字 |
| §1 Introduction | 从数据稀缺、人形形态、ego devices 推到 semantic transfer | 定义比同任务泛化更强的目标 | Fig.1；三项 90%+ 结论 |
| §2 Related Work | 对比 EgoMimic、PH$^2$D、EgoVLA、Masquerade/Mirage、并行工作 | 说明本文突出 foundation VLA + 真机 + 高层语义 | 无主公式 |
| §3.1 Preliminaries | 回顾 $\pi_{0.5}$ multimodal input 与 flow matching | 给共同基座 | Eq.(1) 与 interpolant |
| §3.2 Action Alignment | 定义 wrist + robot joints，并做 human→robot retargeting | 统一动作语义 | Eq.(2)；Supplement joint mapping |
| §3.3 VLA Hand Adaptation | 左右手 action token interleaving | 在不改 head 下容纳 58D | Eq.(3)–(5)，Fig.2 |
| §3.4 Visual Alignment | 彩色、遮挡感知 skeleton overlay | 尝试缩小外观差 | Fig.3 |
| §4 Implementation | 平台、传感器、遥操、50/50 co-training、40% wrist dropout | 给真实数据与部署上下文 | Fig.2 right；Supplement Table 2 |
| §5 Experiments | 设计 Sorting / Boxing / Packaging 与数据量 | 将低层 robot skill 与高层 human semantics 解耦 | Fig.4；Table 1 |
| §6 Results | 回答 co-training、subtask、skeleton、hand、wrist 四问 | 形成主证据链 | Fig.5 |
| §7 Conclusion & Limitations | 明确只做短时程固定场景语义 stitching，低层迁移未解 | 防止过度外推 | 无新增实验 |
| Supplement §8 | Manus / HaMeR 到 Tesollo 的逐关节映射 | 提供 action retargeting 细节 | Eq.(6) 与两段 mapping |
| Supplement §9 | $\pi_{0.5}$ 微调超参 | 提供训练配置 | Table 2 |

## 按原文 section 精读

### 1. Introduction / 从数据规模问题转向语义迁移问题

引言的第一层论点是熟悉的：文本/视觉有 web-scale data，机器人 manipulation data 要占用硬件、操作者和真实时间。作者认为两件事让人类数据更可用：人形机器人越来越接近人类 morphology，Apple Vision Pro、Meta Ray-Ban 等 ego devices 又让人类行为采集更容易。

真正的新问题在第二层。既有 human–robot co-training 多证明 in-distribution improvement 或“同一任务换新场景”泛化；Ego-Pi 问的是：**目标规则只在人类数据出现，机器人能否把已有 motor skills 按该规则重新组合？** 这把评测对象从 pixel/domain transfer 提升到 task semantics。

作者随后把挑战落实为三个设计：

- 高维双手动作超过 gripper VLA head 容量 → action interleaving；
- 高 DoF 手的 fingertip IK 会自碰/不自然 → robot-centric joint mapping；
- 复杂组合不能只靠隐式混训 → optional subtask generation。

引言给出的“90% 或更高”来自三种不同配置：Sorting 与 Packaging 的简单联合训练已经 90%+；Boxing 必须加 subtask。引用时不能省略这个条件差异。

### 2. Related Work / 本文到底比什么多做了一步

EgoMimic 证明 human+robot co-training 有益，但机器人是简单 gripper；PH$^2$D 使用 robot fingers，却从头训练而非利用 foundation VLA；EgoVLA 微调 foundation model，但未做真机。Masquerade/Mirage 把人手 mask 掉再渲染机器人，流程重、overlay 不做遮挡感知，还可能盖住目标物。

作者强调自己的增量是**真机、灵巧五指手、目标任务无机器人示范、且评高层语义**。并行的 Physical Intelligence 工作也做颜色分拣语义，但用 gripper 且整体表现较低；EgoScale 用人类数据 + 1 条机器人目标 demo 教新任务，而 Ego-Pi 假定目标任务 0 条 robot demo，但仍要求该任务与已有 robot skills 紧密相关。

这段 related work 提醒了一个公平边界：Ego-Pi 不是把 human trajectory 直接变成 robot trajectory 的 rendering pipeline，也不是任意新任务 one-shot；它是**在共享视觉语言模型里联合训练两个本体，再利用已有低层技能做组合泛化**。

### 3. Ego-Pi / 方法

#### 3.1 Preliminaries / $\pi_{0.5}$ 接口

时间 $t$ 的输入包括语言 $\ell_t$、头部/ego 图像 $I_t^{\mathrm{ego}}$、左右腕图 $I_t^L,I_t^R$ 与 proprioceptive state $s_t$；可先输出 subtask language $\hat\ell_t$，再预测短时域动作 $a_{t:t+H}$。记

$$
o_t=(I_t^{\mathrm{ego}},I_t^L,I_t^R,s_t).
$$

$\pi_{0.5}$ 用 flow-matching action head。论文的训练式为：

$$
\mathcal L=
\mathbb E_{\tau,\omega}
\left[
\left\|\omega-a_{t:t+H}-
f_\theta(a_{t:t+H}^{\tau,\omega},o_t,\ell_t)\right\|^2
\right],
$$

其中 $\tau\in[0,1]$、$\omega\sim\mathcal N(0,I)$，插值动作

$$
a_{t:t+H}^{\tau,\omega}=\tau a_{t:t+H}+(1-\tau)\omega.
$$

直觉上，action expert 在 noise 与 expert action 之间的路径上学习 velocity field；论文采用 $\omega-a$ 的方向约定。VLM 负责图像/语言/可选 subtask 表示，action expert 负责连续动作生成。

#### 3.2 Aligning human and robot actions / 为什么不直接用 fingertip IK

前人常预测 wrist pose + 5 fingertip positions，再用 IK/optimization 得 robot joint angles。对 Tesollo 这类 20 active joint 的手，作者观察到这种 retargeting 容易自碰或产生不自然构型。因此 Ego-Pi 直接把 human MANO/Manus hand pose 转成 per-link joint angles，再映到 robot joint space。

单手动作定义为：

$$
a=\{p,r,q\}\in\mathbb R^{29},
$$

其中 wrist position $p\in\mathbb R^3$、6D rotation $r\in\mathbb R^6$、Tesollo joint angles $q\in\mathbb R^{20}$。Inspire 只有 6 个 controllable joints，因此单手为 $3+6+6=15$D。

关键不是“人和机器人关节天然相同”，而是作者**人为定义一个 robot-native canonical target**：human sample 的 label 先被转换成机器人能执行的 joint action，robot sample 直接使用自身 joint action。这样 action expert 不必在输出端区分两套坐标，但所有跨本体误差都被前移到 retargeting 规则。

#### 3.3 Action interleaving / 用时间 token 换动作维度

Tesollo 双手为 58D，超过原 $\pi_{0.5}$ 每个 action token 最多 32D。直接扩大 output projection 会扰动预训练权重、训练 loss 更高；Ego-Pi 改写序列：

$$
a_t=\{a_t^L,a_t^R\},
$$

标准双手序列本应是 $\{a_t,a_{t+1},\ldots,a_{t+H}\}$，现在变为

$$
\{a_t^L,a_t^R,a_{t+1}^L,a_{t+1}^R,\ldots,a_{t+H/2}^L,a_{t+H/2}^R\}.
$$

![[papers/images/2606.08107v1/model_humanoid_v6_page1.png|920]]

**Figure 2 / 架构与平台。** 左边蓝/黄 token 交替承载 left/right action，flow noise 也按相同位置加入；VLM 可以先生成 `subtask: pick tomato`。右边是 Galaxea R1 Pro、ZED mini、双 wrist camera，以及用 Quest controllers + Manus gloves 遥操的人。

这个技巧的优点很直接：不改预训练 projection shape，单 token 的 unused dimensions 可 mask/忽略。代价也直接：固定 token budget 下有效 bimanual time horizon 减半；而且左右手本是同一物理时刻，却在序列位置上相邻而非并列。论文用真机结果证明这种编码能工作，但没有系统比较同步误差、chunk length 与复杂双手协同的关系。

#### 3.4 Visual alignment / 彩色骨架是否真的需要

![[papers/images/2606.08107v1/skeleton_overlay_comparison_v3_page1.png|700]]

**Figure 3 / Skeleton overlay。** 每根手指固定一种颜色，人手与机器手沿相同拓扑画线；绘制按手指深度排序，近处手指遮住远处线条，从而保留基本 3D 可读性。它试图显式告诉 VLM“哪根机器指对应哪根人指”。

不过实验没有支持它是核心：Tomato 加 skeleton+subtask 仍为 92%，Boxing 的 skeleton-only 甚至从简单联合训练 27% 降到 7%；有 subtask 时 93→100 只相当于约一项 trial 的差异。论文据此承认 high-level semantics 可能无需显式视觉对应，真正瓶颈是任务阶段而非手指纹理。

### 4. Implementation Details / 数据是怎样采的

机器人是 Galaxea R1 Pro，头部 ZED mini，双手可换 Tesollo（20 joint/hand）或 Inspire（6 joint/hand），腕部 Arducam 为 160° FOV。遥操者用装在 Manus gloves 上的 Quest controllers：Quest 跟踪 wrist 6D pose，Manus 给 finger angles，二者 100 Hz；机器人用 IK + PD 重放腕运动，并将手指角映射到 robot joints。

人类数据同样用 Manus + Quest 做动作标签，图像来自**放在桌上的 ZED mini**。论文结果 Q4 进一步明确说 human data only contains third-person images（人类数据只有第三视角图像）。因此标题/动机中的 “ego-centric” 不应被读成已经验证了 wearable, passive, internet-scale first-person video；当前实验是受控相机 + 穿戴式运动追踪的同步示范。

每个 batch 固定 50% human、50% robot。作者说对比例不敏感，但未给曲线。人类样本没有腕图，为减少 modality missing gap，机器人 wrist images 训练时以 40% 概率 dropout；推理仍提供 wrist views。

微调超参来自 Supplement Table 2：AdamW，$\beta_1=0.9,\beta_2=0.95$，weight decay 0，gradient clip 1.0，cosine schedule，warmup ratio 0.001，batch 128，训练 5k–10k steps。

### 5. Experiments / 怎样隔离“语义来自人、技能来自机器人”

![[papers/images/2606.08107v1/task_v6_page1.png|760]]

**Figure 4 / Benchmark construction。** 红框是 robot training data，绿框是 human training data，蓝框是目标泛化。每个任务都故意不给蓝框对应的机器人轨迹，但给组成它的机器人原子动作。

#### 5.1 Tomato Sorting / sorting logic

Robot data 只教“把番茄放进一个 bowl”，不要求分类；human demos 教两种颜色分别进两个 bowl。测试时机器人面对两 bowl，需把 human-only sorting rule 与 robot pick-place skill 合成。

#### 5.2 Boxing / sequential skill chaining

Robot data 分开教“开盒”和“抓 block 放置”，没有一条机器人轨迹完成“先开盒、再放 block 入盒”。Human data 演示直接组合。这里的困难不是仅选对目标，而是 box-open precondition 与 bimanual coordination：一只手开盒，另一只手必须等待，再拿 block。

#### 5.3 Packaging / rule-based ordering

Robot data 分别教“放小盒入大盒”和“放 teddy bear 入大盒”；human demos 教顺序：先较重/硬的小盒，再玩偶。测试看机器人是否继承 ordering rule。

#### 5.4 数据规模

| Task | Human demos | Human minutes | Robot demos | Robot minutes |
| --- | ---: | ---: | ---: | ---: |
| Tomato Sort | 89 | 13 | 150 | 60 |
| Boxing | 60 | 5 | 144 | 21 |
| Packaging | 96 | 11 | 185 | 27 |

这是分钟级、任务定制的小数据实验，而非规模化实验；它能较干净地问 semantic transfer 是否存在，却不能验证随人类数据量扩展的 scaling law。

### 6. Results / 四个实验问题

![[papers/images/2606.08107v1/robot_evaluation_results_v10_page1.png|940]]

**Figure 5 / 全部定量结果。** 米色为 robot-only，深蓝是 human+robot，浅蓝 skeleton，绿色 subtask，灰色 skeleton+subtask，橙色 Tesollo。Sorting 与 Packaging 只混训就显著提升；Boxing 必须显式 subtask。注意三个 panel 的 evaluation denominator 不同，百分比的统计精度不能按同等强度理解。

#### Q1. 简单 co-training 能否教高层语义？

| Task / configuration | Success |
| --- | ---: |
| Tomato robot-only | 40% |
| Tomato human + robot | **92%** |
| Packaging robot-only | 10% |
| Packaging human + robot | **90%** |
| Boxing robot-only | 20% |
| Boxing human + robot | 27% |

Sorting 中 robot-only 不懂颜色规则，随机放入两个 bowl；Packaging 中 robot-only 常先抓 teddy、在两物体间犹豫或撞盒。联合训练使这两个主要依赖 object→destination / order association 的任务达到 90%+。

Boxing 失败揭示了更深层差别。简单联合策略常先抓 block 再往闭盒顶上放，或两手同时开盒/抓块而相撞。它虽然见过 human sequence，却没有可靠形成“盒子开了才能进入下一阶段”的 latent state machine。

#### Q2. Subtask 与 skeleton 各贡献什么？

训练 VLM 先输出 subtask string，相当于让策略在 action flow 前显式选择阶段。Boxing 从 human+robot 的 27% 跳到 **93%**；加 skeleton + subtask 为 **100%**。skeleton-only 只有 **7%**，Tomato 的 human+robot 与 subtask+skeleton 都是 92%。

所以论文标题虽强调 cross-embodiment，最有力的消融却指向 **temporal/semantic abstraction（时间与语义抽象）**：Boxing 需要先判断 precondition，再切换 skill；像素层手指对应不是主要瓶颈。100% 与 93% 在约 15 次评测下很可能只是 15/15 与 14/15，不能据此断言 skeleton 有 7 个百分点的稳定增益。

#### Q3. 机器人手形态是否影响迁移？

Packaging 上 Tesollo 与 Inspire 定性相近；Boxing 中 Inspire+subtask 为 93%，Tesollo+subtask 只有 67%。Tesollo 能正确先开盒，却常只有左手落到某个特定位置才触发下一 subtask，显示 policy 可能过度依赖 state/visual configuration。

作者归因于 Tesollo 比人手大，而 Inspire form factor 更接近人。但比较同时改变 20 vs 6 joint、单手动作 29 vs 15D、控制难度与视觉外观，不能把差异唯一归因于“尺寸像人”。

#### Q4. 人类没有腕图，会不会让模型忽略机器人腕图？

训练时 robot wrist views 40% dropout，但测试移除它们后性能明显变差；Tomato 尤其难以稳定抓持。说明模型仍会在机器人 embodiment 下利用 close-up wrist observation，人类数据缺 modality 并未迫使网络完全不用它。

这个结果只做了 qualitative report，没有给 dropout 0/40/100% 或 test ablation 的成功率，因此能支持“确实依赖”，不能回答 40% 是否最优。

> [!note] 评测次数的来源与口径
> 论文正文/表格给百分比但未写统一 trial protocol。项目页展示 Tomato 37/40、Boxing 14/15、Packaging 9/10，并给 robot-only 16/40、4/15、1/10；这些分别对应图中约 92%、93%、90% 与 40%、20%（页面的 4/15 实为 26.7%，图/正文写 20%，两处存在口径不完全一致）。因此精读稿以 PDF Figure 5 的百分比为论文主结果，同时把小分母与网页差异列为边界。

### 7. Conclusion and Limitations / 论文真正声称与没有声称的事

作者结论是：action interleaving、human↔robot action alignment 与 subtask prediction 共同构成一个实用 recipe，使人形机器人能从人类数据获得只在人类数据出现的 sorting、composition 与 ordering semantics。

作者明确承认：任务短、固定相机、主要是 pick-and-place；应扩展到长时程、移动操作和真正 dexterous manipulation。更关键的是，本工作默认机器人已掌握所需 low-level skills，人类数据负责 stitch；“直接从人类数据迁移低层新技能”仍未解决。这句话是全文最重要的 claim boundary。

### 8. Supplement / Joint Mapping 与训练细节

对 Manus glove 的 20D human angle $q$ 与 Tesollo $q_{\mathrm{robot}}$，基本形式为：

$$
q_{\mathrm{robot},i}=(q_i+\delta_i)f_i,
\qquad i\in\{1,\ldots,20\}.
$$

附录逐关节列出 offset 与 scale，例如食指/中指多为 $1.0$–$1.1$ 倍，部分 thumb joint 有符号反转与条件分支；HaMeR/MANO 来源又使用另一组 offset/scale。这比只说“做 retargeting”更可复现，但也表明 alignment 是手工标定、sensor/source-specific 的：换手型或 tracking pipeline 要重做映射。

Supplement 只给 optimizer 与步数，没有报告 compute、随机种子、checkpoint selection、不同 human:robot ratio 或不同 action horizon 的消融；这些是复现规模化结论时的主要缺口。

## 方法细节

### 三层对齐不是同一件事

| 层级 | Ego-Pi 做法 | 解决什么 | 实验证据强度 |
| --- | --- | --- | --- |
| Action capacity | 左/右手 interleaved tokens | 58D 超过 32D head | 真机可运行；缺对照消融 |
| Kinematic alignment | human angles → robot-native joints | 两本体输出坐标不同 | 附录映射清楚；跨手型泛化未测 |
| Visual alignment | colored depth-aware skeleton | 手指外观对应 | 基本无正收益 |
| Semantic/temporal alignment | subtask string before action | precondition、阶段切换 | Boxing 27→93，证据最强 |

### “目标任务零 robot demo”的精确定义

$$
\underbrace{D_R(\text{primitive }A)+D_R(\text{primitive }B)}_{\text{机器人会执行}}
+
\underbrace{D_H(A\rightarrow B\mid\text{rule})}_{\text{人类教组合}}
\Longrightarrow
\pi_R(A\rightarrow B\mid\text{rule}).
$$

没有的是右侧完整组合的 robot trajectory；不是 primitive $A/B$ 的 robot grounding。这个设定很有价值，因为高层规则确实比真机低层数据更容易由人展示，但不能等同于 human-only robot learning。

### Human data modality

当前实验的人类样本包含受控 RGB + Manus finger angles + Quest wrist pose。它比 robot teleoperation 便宜，且 labels 与动作同步；但与“从任意第一视角视频自动提动作”相距甚远。论文 supplement 提到 HaMeR 映射规则，主实验 implementation 则明确使用 Manus/Quest；不同来源在各任务中的具体占比没有完全展开。

## 实验设置、数据集、基线、指标

| 维度 | 设定 |
| --- | --- |
| Foundation model | $\pi_{0.5}$，VLM + flow-matching action expert |
| Robot | Galaxea R1 Pro；Tesollo 20-joint/hand 或 Inspire 6-joint/hand |
| Cameras | robot head ZED mini + two 160° wrist cameras；human table-mounted ZED mini，无 wrist cameras |
| Tracking | Quest controllers（wrist 6D）+ Manus gloves（finger angles），100 Hz |
| Co-training | batch 内 human:robot = 50:50；robot wrist images 40% dropout |
| Training | AdamW，batch 128，5k–10k steps，cosine LR，clip 1.0 |
| Tasks | Tomato Sorting、Boxing、Packaging；目标组合没有 robot demo |
| Baselines / variants | robot-only、human+robot、+skeleton、+subtask、+skeleton+subtask、Tesollo vs Inspire |
| Metric | task success percentage；未报告 CI / 多 seed /统一 denominator |

## 主要结果、消融或对比

1. **简单语义绑定有效**：Sorting 40→92，Packaging 10→90。
2. **带前置条件的组合不能只靠混训**：Boxing 20（robot）/27（co-train），加 subtask 到 93。
3. **显式视觉 hand correspondence 不重要**：Tomato 不变，Boxing skeleton-only 更差；skeleton 不是论文成功的必要条件。
4. **形态 gap 仍明显**：Tesollo+subtask 67 < Inspire+subtask 93，但比较存在多重混杂。
5. **robot wrist view 仍有用**：训练虽含 human modality missing，推理去 wrist 后抓取恶化；只有定性证据。
6. **没有 scale 证据**：每任务 human data 仅 5–13 min，未画 data-scaling curve。

## 图表、公式与表格线索

| 线索 | 内容 | 阅读时抓什么 |
| --- | --- | --- |
| Fig.1 | robot skill + human semantics → three target behaviors | 论文评的是 semantic composition，不是纯 imitation |
| Fig.2 | interleaved action architecture + hardware | 58D 如何塞入 32D token，左右手从并行变相邻 token |
| Fig.3 | human/robot skeleton overlay | 视觉对齐设计与遮挡处理 |
| Fig.4 | 三任务 train/transfer split | “无目标 robot demo”仍有哪些 primitive robot data |
| Fig.5 | 全部成功率柱状图 | subtask 是主增益，skeleton 不是 |
| Eq.(1) | flow matching loss | 基座如何生成 action chunk |
| Eq.(2) | $a=\{p,r,q\}$ | 单手 29D / 15D 的组成 |
| Eq.(3)–(5) | bimanual interleaving | 容量–horizon trade-off |
| Table 1 | human / robot demos 与分钟数 | 数据是任务定制的分钟级小样本 |
| Supplement Eq.(6) | per-joint offset/scale | retargeting 不是 learned universal alignment |
| Supplement Table 2 | 微调超参 | 5k–10k steps、batch 128；其他复现信息仍缺 |

## 主张-证据-边界矩阵

| 主张 / 结论 | 原文证据 | 解释 | 边界 / 适用条件 |
| --- | --- | --- | --- |
| 人类数据能教新 sorting semantics | Tomato 40→92 | robot skill 与 human color rule 被成功组合 | 单场景、两色/两 bowl、低层 skill 已有 |
| 人类数据能教 rule ordering | Packaging 10→90 | 模型学会先硬盒后 teddy | 10 次级小评测；短时程 pick-place |
| 人类数据能教 skill composition | Boxing+subtask 93/100 | subtask 暴露 open→place 前置关系 | 简单 co-training 仅 27；结论依赖语言辅助 |
| interleaving 可适配 dexterous VLA | 双手真机三任务成功 | 保留预训练 projection 且动作能执行 | horizon 减半；缺 expanded-head / horizon ablation |
| robot-centric joint mapping 优于 IK | 方法动机 + 真机可行性 | 避免高 DoF fingertip IK 的自碰 | 没有同设置 IK 定量对照；映射手工平台特定 |
| skeleton 可帮助视觉对齐 | 设计图 | 对应关系更可解释 | 定量基本不支持性能收益 |
| 更类人的 hand 更易迁移 | Inspire 93 vs Tesollo 67 | morphology 可能影响视觉/状态对齐 | joint count、action dimension、controller 均混杂 |
| 无 human wrist view 仍能用 robot wrist view | test removal 定性变差 | 40% dropout 没让模型完全忽略 wrist | 无数字、无 dropout sweep |
| human data 可规模化缓解稀缺 | 动机 + 小数据成功 | 概念上有潜力 | 当前仅 29 min human data 总量、受控 tracking，无 scaling 实验 |

## 局限与可追问点

1. **Egocentric 的名实问题。** 当前 v1 明写 human ZED 在桌上，Q4 称 human images 为 third-person；应问哪些实验真正用了 wearable/first-person view，以及标题中的 ego-centric 如何操作性定义。
2. **低层技能迁移仍未发生。** 如果 robot 从未见过开盒、抓软物、复杂 in-hand rotation，人类数据能否直接教会？作者明确留作 future work。
3. **手工 joint mapping 的扩展成本。** 换 Shadow Hand、Allegro、不同 glove/HaMeR 版本时，需要多少重新标定？误差如何传播到 policy？
4. **Interleaving 的时域代价。** $H/2$ 对长时程、快速双手接触是否会降低闭环反应？左右手 token 串行化是否产生相位偏差？
5. **Subtask label 成本与来源。** 谁标 subtask、粒度如何定、错误/缺失 label 会怎样？能否由 VLM 自举而不增加人工语义标注？
6. **评测统计不充分。** 需要统一 trial count、训练 seeds、置信区间、失败 taxonomy 和 checkpoint protocol；网页与 PDF 的 Boxing baseline 口径也应统一。
7. **Skeleton 的负结果值得保留。** 它为什么在 Boxing-only 变差到 7%？是遮挡物体、domain artifact、校准误差还是网络已经能自行对齐？
8. **Hand comparison 有混杂。** 应控制 joint/action dimension、训练量与 controller，或在同一手上改变视觉 render/尺寸，才能验证 morphology hypothesis。
9. **Human:robot ratio 与数据规模。** “不敏感”没有曲线；需测 10/25/50/75/90%、human-only，以及分钟数 scaling。
10. **移动与非固定视角。** 现有语义可能依赖固定桌面布局；mobile manipulation 会同时引入视角、导航、遮挡与长时记忆。

## 与当前库的连接

- 与 [[@qwen2026robotmanip|Qwen-RobotManip]]：两者都用 human ego data 解决机器人数据不足。Qwen-RobotManip 大规模做 H2R rendering/retargeting 并统一 canonical action；Ego-Pi 小规模直接 co-train human/robot，重点证明 semantic composition。前者强在 scale/OOD，后者强在可解释的“语义只来自人类”任务切分。
- 与 [[@paliwal2026do-i-dexterous-manipulation|Do as I Do]]：都面向人类视频到灵巧操作。Ego-Pi 的 human action 有 glove/controller 同步标签且目标是 task semantics；Do as I Do 更应对自然人类视频/动作提取时，可从标注成本与低层技能迁移角度对照。
- 与 [[@wang2026vlk-learning-humanoid-loco|VLK]]：VLK 用重建场景、合成全身轨迹与接触 tracker 做 humanoid loco-manipulation；Ego-Pi 用真实 human/robot co-training 做固定桌面双手语义组合。两者分别解决“全身运动可执行性”和“双手任务规则”。
- 与 [[@intelligence2025pi06-vla-that-learns|π*0.6 / RECAP]] / [[@intelligence2026pi07-steerable-generalist-robotic|π0.7]]：Ego-Pi 从 $\pi_{0.5}$ 微调，靠人类 subtask semantics 提升组合；后续模型强调 RL self-improvement / steerable context。可问 subtask token 能否与更通用的上下文/自主经验统一。
- 与 [[@kang2026x-tokenizer|X-Tokenizer]]：Ego-Pi 的 interleaving 是 action dimension 超限的架构 workaround，X-Tokenizer 则学习可跨维度/精度的动作 token。对比点是“保留旧 head”与“重学统一离散表示”的容量–时域 trade-off。
- 与 [[@fu2026lingbot-vision|LingBot-Vision]]：Ego-Pi 发现 skeleton overlay 不必要，暗示强视觉表征可能已能跨 human/robot hand appearance 对齐；可进一步用显式空间/手物关系表征替代粗线条 overlay。

## 精读路线 / 为什么需要回看

1. **先看 Fig.4**：先弄清每个目标任务缺哪类 robot data、又保留了哪些 primitives，否则很容易把 semantic transfer 误写成 human-only skill learning。
2. **再看 Fig.2 + Eq.(3)–(5)**：理解 58D→两个 32D token 的容量–horizon 交换，这是方法最具体的架构创新。
3. **看 Fig.5 时只抓一个主结论**：Boxing 27→93 说明 subtask/precondition 是核心；skeleton 不是。
4. **回看 §3.2 + Supplement §8**：确认跨本体 action alignment 依赖手工 joint mapping，而非模型自动发现 universal hand space。
5. **读 §4 与 Q4 文字**：核对 human camera 是桌面固定、human data 被称为 third-person，校准“egocentric scale”叙事。
6. **最后读 §7 limitations**：作者明确把 low-level skill transfer、long horizon、mobile manipulation 留作未来；引用结论时必须保留这些限定。
7. **若要复现**：优先补齐统一 trial protocol、subtask annotation、interleaved state/action masking、不同 horizon 与 human:robot ratio 消融。
