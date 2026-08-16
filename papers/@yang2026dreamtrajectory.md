---
tags:
  - paper
status: unread
aliases:
  - DreamTrajectory
  - DT
  - "DreamTrajectory: Trajectory-Guided Action Generation with World Model Alignment for Mobile Manipulation"
year: 2026
title: "DreamTrajectory: Trajectory-Guided Action Generation with World Model Alignment for Mobile Manipulation"
doi: "10.48550/arXiv.2608.01381"
arxiv: "2608.01381v1"
url: "https://arxiv.org/abs/2608.01381"
venue: "arXiv preprint"
venue_short: "arXiv"
arxiv_url: "https://arxiv.org/abs/2608.01381"
arxiv_doi: "10.48550/arXiv.2608.01381"
pdf_url: "https://arxiv.org/pdf/2608.01381v1"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/yang2026dreamtrajectory.pdf]]"
reading: "[[papers/bilingual/yang2026dreamtrajectory_中英混读.md]]"
images: "papers/images/yang2026dreamtrajectory/"
image_index: "[[papers/images/yang2026dreamtrajectory/index.md]]"
map_axis: "具身智能/VLA/轨迹引导与世界模型对齐"
map_brief: "移动操作里把末端执行器轨迹当显式任务空间中间表示，双流 action expert 联合去噪轨迹与全身动作，再用 49M 参数的轨迹世界模型在执行前做 search-predict-score 精修。"
map_role: "研究移动操作如何用中间运动表示压缩全身动作空间，以及轻量世界模型如何在任务空间而非像素空间做测试时对齐的入口。"
authors:
  - "[[Zheng Yang]]"
  - "[[Wenjie Zhang]]"
  - "[[Xiangyu Chen]]"
  - "[[Wenxuan Song]]"
  - "[[Xianpeng Wang]]"
  - "[[Yihang Kang]]"
  - "[[Wen Chen]]"
  - "[[Lujia Wang]]"
  - "[[Renjing Xu]]"
  - "[[Xiaowen Chu]]"
institutions:
  - "[[Hong Kong University of Science and Technology (Guangzhou)]]"
  - "[[Ola Dimensions]]"
topics:
  - mobile manipulation
  - trajectory-guided policy
  - world model
  - test-time refinement
  - whole-body control
  - flow matching
  - group-causal attention
  - MS-HAB
  - ARX LIFT
---

# DreamTrajectory: Trajectory-Guided Action Generation with World Model Alignment for Mobile Manipulation

- [x] PDF:: [[papers/pdfs/yang2026dreamtrajectory.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/yang2026dreamtrajectory_中英混读.md]]
- [x] 图片索引:: [[papers/images/yang2026dreamtrajectory/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[mobile manipulation]], [[world model]], [[test-time scaling]], [[@peng2026fact]], [[@gao2026fast-leworldmodel]], [[@zhou2026holoagent0]], [[@intelligence2026pi07-steerable-generalist-robotic]], [[@qwen2026robotmanip]]
affiliation:: [[Hong Kong University of Science and Technology (Guangzhou)]], [[Ola Dimensions]]

## Abstract

Mobile manipulation requires a robot to coordinate base and arm motion under continuously changing viewpoints and contact conditions, within an action space far larger than that of fixed-base manipulation. Existing Vision-Language-Action (VLA) policies are limited in two respects. (i) They map observations directly to whole-body action chunks, searching this large action space without an explicit task-space motion plan, which makes coordinated base-arm prediction imprecise. (ii) They execute the predicted chunk open-loop, without checking whether the actions can realize the motion the policy intended, so control errors and unmodeled contacts accumulate into a gap between planned and realized motion. We present DreamTrajectory, a trajectory-guided framework for language-conditioned mobile manipulation that introduces one component for each limitation. Addressing (i), DreamTrajectory jointly predicts an intention-level end-effector trajectory and a whole-body action chunk in a single action expert, so that the trajectory explicitly guides base-arm action generation instead of remaining implicit. Addressing (ii), a lightweight trajectory world model predicts the trajectory that a candidate action chunk would induce, and a test-time search-predict-score procedure selects the candidate best aligned with the planned trajectory. On MS-HAB, trajectory guidance raises average success from 32.3% to 47.5% and test-time refinement further to 54.8%, with the largest gains on contact-rich articulated-object tasks. On three real-world mobile manipulation tasks, the corresponding average success rates are 63.3%, 81.7%, and 90.0%.

## 一句话定位

移动操作的动作空间远大于固定底座操作，现有 VLA 既没有显式的任务空间运动计划，也不在执行前验证动作能否实现意图；DreamTrajectory 用一个双流 action expert 联合生成末端执行器轨迹和全身动作块，再用一个 49M 参数的轨迹世界模型在任务空间对候选动作做 search-predict-score 精修。

## 方法 / 对象

- 中间表示：7D 末端位姿轨迹 $\tau_{t+h}=[p^{B_t}_{t+h}, q^{B_t}_{t+h}]\in\mathbb{R}^7$，表达在 chunk-local frame $B_t$（锚在当前底盘位姿、时域内固定），因此同时编码底盘与手臂的合成运动。
- 联合生成：轨迹流与动作流共享时域 $H$ 和 flow time $\sigma$，用条件 flow matching 同步去噪，损失 $\mathcal{L}_{VLA}=\mathbb{E}[\lambda_\tau\|v_\tau-u_\tau\|^2+\lambda_a\|v_a-u_a\|^2]$。
- 分组因果注意力：轨迹 token 只看多模态前缀与之前的轨迹 token；动作 token 额外看完整轨迹流与之前的动作 token。轨迹引导动作，动作不回流。
- 轨迹世界模型：$\tilde\tau(a)=W_\phi(o_t,s_t,a_{t:t+H-1})$，GRU 架构，49.02M 参数，$H=16$，不吃语言（任务意图由计划轨迹承载）。
- 候选构造：$N=30$，保留原始动作块，其余 29 个按每维独立 AR(1) 高斯过程扰动，$\sigma=0.05$，$\rho=0.9$（保证扰动时间上平滑）。
- 选择规则：$\tilde a=\arg\max_{a\in\mathcal{C}}[\lambda S_{traj}(a)+(1-\lambda)\eta S_{smooth}(a)]$，$\lambda=0.5$，$\eta=10^{-3}$。$S_{traj}$ 与 $S_{smooth}$ 的定义只在补充材料。
- 训练：两阶段分开。Stage I VLA 从 π0.5 权重初始化，在专家示范上微调；Stage II 世界模型在含成功与失败的交互数据上监督训练，目标 $\tau^{exec}$ 由记录的底盘速度积分加末端位姿变换构造，带一步时间偏移。
- 部署：两者只通过测试时精修结合，VLA 不需重训。

## 证据

- MS-HAB set_table 六子任务（Fetch，每任务 100 episode）：π0.5 32.3% → 加轨迹引导 47.5% → 加精修 54.8%。基线 ACT 28.0%、Diffusion Policy 27.7%、GR00T N1 21.2%、RDT-1B 8.7%。
- 收益拆分：22.5 点总提升中 15.2 点来自轨迹引导、7.3 点来自精修。
- 轨迹引导收益不均匀：open fridge 5.0% → 44.0%，close counter 38.0% → 72.0%；但 pick apple 37.0% → 34.0%，open counter 87.0% → 80.0%。
- 精修收益均匀：六个子任务全部提升，close counter 72.0% → 80.0% 说明强策略上仍有残余误差可纠。
- 真机（ARX LIFT，三任务各 20 episode）：63.3% → 81.7% → 90.0%。水果抓放 45→70→80，开抽屉 60→75→90，关抽屉 85→100→100。
- 世界模型架构（4096 条轨迹，$H=16$）：GRU xyz ADE 0.028 m / FDE 0.035 m / 角度 ADE 6.2°；Cross Attention 0.033/0.045/7.4；One-shot Transformer 0.036/0.049/7.7；Diffusion 0.061/0.086/8.1；Analytical FK 0.241/0.345/27.0。
- 开销（RTX 4090，BF16）：轨迹头 0.017M（+3.65 ms），世界模型 49.02M（+8.10 ms），合计 49.04M 即 3.5B VLA 的 1.40%，共 +11.75 ms。

## 局限

- 打分函数 $S_{traj}$ 与 $S_{smooth}$ 的定义不在正文，只给了加权形式和两个超参。整个精修流程的效果取决于它们，复现必须去补充材料。
- 候选数量 $N=30$ 没有敏感性分析，$\lambda$、$\eta$ 也没扫描。（对比 [[@peng2026fact]] 专门扫了候选数量并画出完成率与延迟的权衡。）
- 世界模型不吃语言，只能判断动作能否走出这条轨迹，判断不了轨迹本身对不对。VLA 规划出语义错误的轨迹时，精修会忠实地把动作对齐到错误轨迹上。这个失效模式论文没讨论。
- 轨迹引导在 pick apple 和 open counter 上是负收益，而这两个恰是 π0.5 基线最强的两项。作者只归因于「主要惠及接触密集任务」，没查「简单任务被加了不必要约束」这个更直接的解释。
- 分组因果掩码的方向性没有对照消融，没有比过双向注意力。
- 世界模型训练数据的规模与失败占比都没有报告，而这是个靠数据学接触偏差的模型。
- 未来预测类 VLA 因本体接口不兼容被排除在定量对比外，只在 Table 1 定性比较，所以没跟同类世界模型方法直接比过成功率。
- 本体覆盖窄，仿真只有 Fetch，真机只有 ARX LIFT。chunk-local frame 对差速、全向、腿式底盘是否同样合适没有证据。
- 真机每任务只有 20 个 episode，一次试验就是 5 个点；关抽屉在中间档已饱和到 100%。
- 绝对水平仍低。仿真最好只有 54.8%，所有基线都在 33% 以下，这个设定离可用还远。

## 我的阅读笔记

这篇的结构是我最近读到最清爽的一种，两个具体缺口配两个具体组件，消融正好把两个组件的贡献切开成 15.2 和 7.3。写法上值得学。

最值得记的技术点是 Eq. 2 的 chunk-local frame。把参考系锚在当前底盘位姿上并在时域内冻住，一条末端轨迹就自动编码了底盘位移和手臂运动的叠加。移动操作里这个表示选得很巧，比分别预测底盘轨迹和手臂轨迹要简洁得多。

第二个值得记的是 Table 5 那一个数量级的差距。解析开环 FK 的 xyz ADE 0.241 米对 GRU 的 0.028 米，把「接触和控制误差不是解析模型能覆盖的」说得很硬。这个对照可以直接引用到任何需要论证「为什么这里得学一个模型」的地方。

Table 6 那笔账也很实在。1.40% 参数、11.75 毫秒换 7.3 个成功率点。相比像素空间世界模型动辄几百毫秒的代价，任务空间的世界模型确实不在一个尺度上。

跟 [[@peng2026fact]] 并读最有意思，两篇的测试时流程几乎同构（采候选、预测、打分、执行），但打分空间完全不同。FACT 在价值空间打分能判语义好坏，DT 在轨迹空间打分只能判运动学可实现性。把两者叠起来大概是个自然的下一步。

保留的怀疑主要在两处。一是打分函数不在正文，这让整篇论文最关键的一环无法直接评估。二是轨迹引导在两个任务上掉分，作者的解释太快就收住了，我更倾向于是给简单任务加了多余约束，但没有数据能判定。

## 摘录

> Our central hypothesis is that a compact end-effector trajectory provides a physically meaningful intermediate representation for whole-body control: it specifies where the gripper should move before how base and arm commands should realize that motion.

> This mapping is learned from interaction data rather than derived analytically, because the deviation between commanded and realized motion originates from contacts with external objects, self-collisions of the arm, and tracking error of the low-level controller, none of which an analytic dynamics model captures reliably.

> Language is omitted because the world model predicts task-agnostic task-space execution outcomes; task intent is represented by the planned trajectory.

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
