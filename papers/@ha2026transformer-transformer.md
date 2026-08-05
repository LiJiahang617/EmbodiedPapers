---
tags:
  - paper
status: unread
aliases:
  - "Transformer Transformer: A Unified Model for Motion-Conditioned Robot Co-design"
year: 2026
title: "Transformer Transformer: A Unified Model for Motion-Conditioned Robot Co-design"
doi: 
arxiv: "2607.25798v1"
url: "https://arxiv.org/abs/2607.25798"
venue: "arXiv preprint"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/ha2026transformer-transformer.pdf]]"
reading: "[[papers/bilingual/ha2026transformer-transformer_中英混读.md]]"
images: "papers/images/ha2026transformer-transformer/"
image_index: "[[papers/images/ha2026transformer-transformer/index.md]]"
authors:
  - "[[Huy Ha]]"
  - "[[C. Karen Liu]]"
  - "[[Shuran Song]]"
institutions:
  - "[[Stanford University]]"
  - "[[Columbia University]]"
topics:
  - robot co-design
  - embodiment optimization
  - cross-embodiment control
  - diffusion transformer
  - robot tokenization
  - diffusion guidance
  - whole-body control
  - test-time scaling
---

# Transformer Transformer: A Unified Model for Motion-Conditioned Robot Co-design

- [x] PDF:: [[papers/pdfs/ha2026transformer-transformer.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/ha2026transformer-transformer_中英混读.md]]
- [x] 地图维护:: [[论文地图]]
- [ ] 阅读状态:: unread

related::
affiliation::

## Abstract

An often overlooked factor of robot manipulation performance is the embodiment of the robot itself. Motivated by this problem, we study motion-conditioned robot co-design, where the goal is to generate complete robot designs that track target end-effector trajectories (from human demonstrations) while optimizing user-defined rewards. We introduce Transformer Transformer, a diffusion transformer trained on RoboTokens, a unified tokenization of robot embodiments, states, and actions. The same architecture can be used across embodiment spaces (e.g., wheeled bimanual, quadrupeds, humanoids) and use cases (embodiment generation, cross embodiment controller). Rather than overfitting to one reward function, Transformer Transformer is a dynamics model, whose reward-agnostic state and action predictions can be converted into reward-specific value predictions. These value predictions are used to steer embodiment diffusion towards high value robot designs, through a procedure we call Dynamics Self-Guidance. Experiments across multiple design spaces show zero-shot optimization of unseen rewards and trajectories, improving performance and runtime over the evolutionary baseline. Finally, we fabricated an optimized ALOHA design, which reduced tracking error by over 70% compared to the original design.

## 一句话定位

Transformer Transformer 把"设计机器人本体"和"控制机器人本体"塞进同一个 diffusion transformer：先用 RoboToken 把任意刚体关节机器人的 embodiment（link/joint/motor）与 dynamics（state/action）统一成连续值 token，再训练一个 DiT 同时去噪两者；因为学到的是 reward-agnostic 的动力学模型，推理时可以把预测出的状态与动作代进任何用户 reward，再把梯度回传到 embodiment token 上做 Dynamics Self-Guidance，从而零样本优化训练时没见过的 reward 和轨迹，并用同一个模型充当 generator、critic 与 controller。

## 方法 / 对象

- **RoboToken**：五类 embodiment token（link、fixed joint、sliding/rotating joint、ball joint、motor）+ 四类 state token + action token，另加不加噪的 target pose 条件 token。token 之间靠互存 ID 指针表达任意连接结构（joint 指向两个 link，motor 指向 joint；没有 motor 指向的 joint 自然就是被动关节，如 Cassie 的腿部机构）。属性按类型用 binary / log / signed-log 编码（Table 19 给出完整 schema）。
- 之所以不直接学 MJCF 文本：文本没有统一的 transform 约定，会逼模型学一堆等价的冗余空间偏移；RoboToken 在预处理阶段统一 transform 约定、用平行轴定理拆分 lumped inertia、把变换 collapse 进 joint token。同时 RoboToken 比 GPT-4o 分词后的 MJCF 文本紧凑 27–110×，且是连续值、可微、可全局控制（自回归 LLM 两者都不具备）。
- **架构**：DiT；每类 token 学一个类型专属的线性投影进入隐空间，再加上各类 ID 的 learned positional embedding；每类 token 序列各自 padding 到最大长度后拼成一条长多模态序列；因重力只有 SE(2) 等变，故只做平面变换增强；DDIM 调度；每个 episode 只采 8 个 timestep（motion-to-robot 随机采、control 连续采）。
- **两种 masked modeling 用途**：(a) motion-to-robot 优化——条件为目标末端轨迹，同时扩散 embodiment 与 dynamics，因此模型自己就有评估新设计所需的一切；(b) cross-embodiment control——条件为 embodiment + 当前状态 + 目标轨迹，预测专家动作，靠 token 数量变化天然支持异构状态/动作空间。
- **两个优化器**：Zeroth-Order（并行跑 $n$ 条扩散过程，用模型自身预测的 reward 排序取最优）；**Dynamics Self-Guidance**（在每个 DDIM 步把可微 reward 对 embodiment token 的梯度按 classifier-guided DDIM 注入，即使整条扩散链不可微也能逐步引导）。DGS 需要随机采样 $\eta{=}1.0$ 才显著有效，guidance scale 按设计空间分别取 50 / 100 / 0.2（多轨迹 ViperX 提到 500）；由于 token 对自身的 attention 远高于对其他 token，embodiment 类 reward（size、mass）的梯度量级过大，guidance 里要单独把 $\alpha$ 降到 0.005。
- **数据**：76 条 UMI + ARKit 采集的末端轨迹（56 训练 / 20 验证，含抛掷、拧螺丝、开抽屉、擦洗）+ UMI 双臂洗碗数据；三个设计空间分别压测三种难点——ViperX 固定基座（运动学可达性）、四足 manipulator（全身动态控制）、移动双臂（任务复杂度）。非腿式机器人用 Mink 的 differential IK（补 80 ms 前瞻），腿式用 PPO 训 WBC：7 个二值设计选择 → 128 个 RL 专家，每个在 A100 上训 16 小时。数据集规模：ViperX 3.8M episodes / 2B steps（380K 个本体）、四足 1.3M / 500M（130K）、移动双臂 50K / 69M（5K）。
- 数据质量：过滤时长 < 100 步（2 秒）的 episode；ViperX 与 ALOHA 空间先用 CMA-ES（population 5、3 代）把训练本体偏置到较优区域，再全部纳入训练集。

## 证据

- 测试时扩展（Fig. 5）：三个设计空间、全部 reward 下，Zeroth Order 与 DGS 的 reward 都随并行样本数上升；速度上比 CMA-ES 快数个数量级。ViperX 单轨迹（Table 2）：CMA-ES 5.0 cm / 5.7° / 47.5 s，Zeroth 4.1 / 4.2 / **0.5 s**，DGS 4.1 / 3.9 / 2.8 s。ViperX 多轨迹（Table 3）：CMA-ES 7.1 cm / 663.8 s，Zeroth 3.4 / 1.2 s，DGS **2.4** / 43.5 s。移动双臂多轨迹（Table 5）：CMA-ES 1.7 cm / **11505.2 s**，Zeroth 1.8 / 20.7 s，DGS 1.7 / 30.8 s。
- 并行化解释：CMA-ES 评估一个候选要顺序跑几千步仿真，本模型则用非自回归形式一次性并行推理 8 个时间步，再叠加 batch 维并行，因此"扩散并评估 128 个候选"比 CMA-ES 评估 5 个还快。
- 多轨迹零样本：只用单轨迹训练，靠 diffusion composition 组合出同时服务 26 条未见轨迹的设计，26 条中 20 条占优；CMA-ES 的耗时随轨迹数线性增长（多出约 3 小时）。
- guidance 与 search 是替代而非互补：单样本时 DGS 在双臂多轨迹上领先 Zeroth（341 vs 242 reward），样本预算够大时两者收敛到相当。
- 自验证控制：用同一模型控制自己生成的四足，reward 与 128 个 RL 专家的结果 Pearson $r{=}0.53$（Fig. 8）；双臂空间（Table 1）小模型 6.6 cm / 10.7° / 98.9% / 884.9，大模型 5.9 / 9.6 / 99.5 / 957.0，Mink oracle 4.8 / 7.6 / 100.0 / 1064.3。
- 真机（Fig. 9–10）：为 "Tracking Velocity" reward 优化并制造了一套 ALOHA，用于甩布展开——最大关节速度 2.57 → 1.82 rad/s（−30%），跟踪位置误差 13.0 → 3.5 cm（−73%）；优化解把双臂倒装到工作区后方，用 underarm swing 取代 overhead fling。
- 生成性质：模型只在训练流形内插值（manifold adherence），无条件采样时各机器人类型的出现概率匹配训练分布（mode coverage），且属性联合分布自洽（大 link 配相称的质量与惯量、电机与所驱动关节匹配）。

## 局限

- RoboToken 目前只支持 primitive 几何，不含场景、物体与触觉信息；reward 只能是 embodiment / state / control 的函数，结构强度、外观等超出范围。
- 生成不外推：四足训练集里没有六足，模型就造不出六足；link 长度也不会超出训练区间。扩展设计空间等于扩展数据集，而数据生成本身很贵（128 个 RL 专家 × 16 A100·小时）。
- 四足空间是明显短板：reward 预测相关性最低（Fig. 7），CMA-ES 在单轨迹上仍略优（1.9 cm vs 2.6 cm），原因是学到的 WBC 要处理不连续接触和摔倒终止。
- 超参需按设计空间手调：guidance scale 50 / 100 / 0.2 / 500，加上 embodiment 类 reward 必须单独缩放梯度，说明 Dynamics Self-Guidance 目前不是即插即用。
- test-time compute 的收益不稳定：给到一分钟级别的 refine 后性能不再稳步上升。
- 真机只验证了一个设计空间（ALOHA）、一个任务（flinging），没有多设计重复对比，也没有和人类专家设计做对照。

## 我的阅读笔记

这篇的价值在于把"本体"提升为 first-class token。库里其他 tokenization 工作（[[@kang2026x-tokenizer]]、[[@zhong2025action-tokenization-survey]]）讨论的是"动作怎么离散化/表示"，这篇讨论的是"机器人本身怎么表示才能被生成模型优化"，而且给了一个可检验的判据：表示要 complete（reward 能算）、flexible（结构可变）、consistent（无冗余等价）、optimizable（连续可微）。这四条同样适用于评价任何具身表示方案。

方法上最值得记的是"reward-agnostic dynamics model + 推理期 reward 梯度"这条路线：训练时不绑定 reward，推理时把 reward 当成对 dynamics 预测的函数并回传梯度，从而零样本换 reward。这和世界模型路线（[[@wang2026orca]]、[[@gao2026fast-leworldmodel]]）是同一个母题的不同分支——那边用 dynamics 预测评估**策略**，这边用它评估**硬件**。反过来看，它的短板也和世界模型一致：动力学越难预测（四足接触、摔倒），guidance 就越不可靠，Fig. 7 的相关性图基本可以当作"这个方法在什么设计空间可信"的诊断表。

可追问：(1) 128 个 RL 专家能否真的被单一 cross-embodiment controller 替换，$r{=}0.53$ 离"可用于自动化设计验证"还差多少；(2) 多轨迹组合能否扩到真实操作数据集级别的任务分布，得到"通用平台设计"；(3) 与 [[@paliwal2026do-i-dexterous-manipulation]] 共享 UMI 式末端轨迹表示，那么"先用人类视频定义任务、再反过来生成适配该任务的机器人"是否是比"把人类数据迁到既有机器人"更省力的路径。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
