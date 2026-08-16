---
tags:
  - paper
status: unread
aliases:
  - WAM-TTT
  - "WAM-TTT: Steering World-Action Models by Watching Human Play at Test Time"
year: 2026
title: "WAM-TTT: Steering World-Action Models by Watching Human Play at Test Time"
doi: "10.48550/arXiv.2607.06988"
arxiv: "2607.06988v2"
url: "https://arxiv.org/abs/2607.06988"
venue: "arXiv preprint"
venue_short: "arXiv"
arxiv_url: "https://arxiv.org/abs/2607.06988"
arxiv_doi: "10.48550/arXiv.2607.06988"
pdf_url: "https://arxiv.org/pdf/2607.06988v2"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/feng2026wam-ttt.pdf]]"
reading: "[[papers/bilingual/feng2026wam-ttt_中英混读.md]]"
images: "papers/images/feng2026wam-ttt/"
image_index: "[[papers/images/feng2026wam-ttt/index.md]]"
map_axis: "世界模型/WAM/人类视频测试时适配"
map_brief: "部署时把未标注第一人称人类视频通过自监督视频预测吸进冻结 WAM 视频专家的 TTT 快权重，用键值记忆重建损失把人类 Key/Value 校准成机器人可用的记忆，不做重定向也不碰动作专家。"
map_role: "研究机器人基础模型部署后如何被廉价操控，以及人类视频到底该以什么形式注入的入口。"
authors:
  - "[[Yusen Feng]]"
  - "[[Bingchen Han]]"
  - "[[Jiangran Lyu]]"
  - "[[Kai Liu]]"
  - "[[Yixin Zheng]]"
  - "[[Yuxuan Wan]]"
  - "[[Weiheng Liu]]"
  - "[[Sun Han]]"
  - "[[Ruiqin Li]]"
  - "[[Yulong Zhang]]"
  - "[[Fangfu Liu]]"
  - "[[Xuesong Shi]]"
  - "[[Libin Liu]]"
  - "[[Yizhou Wang]]"
  - "[[Zhizheng Zhang]]"
  - "[[He Wang]]"
institutions:
  - "[[Peking University]]"
  - "[[Galbot]]"
  - "[[CASIA]]"
  - "[[Tsinghua University]]"
topics:
  - world-action model
  - test-time training
  - fast weights
  - adaptive memory
  - human video
  - steerability
  - meta-training
  - linear attention
  - LDA
---

# WAM-TTT: Steering World-Action Models by Watching Human Play at Test Time

- [x] PDF:: [[papers/pdfs/feng2026wam-ttt.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/feng2026wam-ttt_中英混读.md]]
- [x] 图片索引:: [[papers/images/feng2026wam-ttt/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[world-action model]], [[test-time training]], [[human video]], [[@jiang2026robottt]], [[@paliwal2026do-i-dexterous-manipulation]], [[@qian2026wam-rl]], [[@peng2026fact]], [[@intelligence2026pi07-steerable-generalist-robotic]], [[@zhang2026qwen-robotworld]]
affiliation:: [[Peking University]], [[Galbot]], [[CASIA]], [[Tsinghua University]]

## Abstract

Steering robot foundation models (RFMs) toward new task variants or user-preferred behaviors remains challenging, often requiring additional robot demonstrations, task-specific fine-tuning, or long-context conditioning. We present WAM-TTT, a test-time training framework for steering world action models from raw human videos. Rather than treating human videos as trajectories to imitate, WAM-TTT absorbs them into a lightweight adaptive memory inside a frozen WAM through self-supervised video prediction. To make this memory useful for control, we introduce a meta-training stage that aligns human demonstrations with robot behaviors using paired human-robot data and a key-value memory reconstruction objective. At test time, only unlabeled human videos are required to adapt the memory, while the pretrained WAM remains frozen. This enables efficient and reusable steering without robot actions, human-side annotations, or task-specific fine-tuning, while preserving the generalization ability of the foundation model. Extensive experiments show that WAM-TTT consistently outperforms in-context human-video conditioning baselines across diverse manipulation tasks and generalization settings.

## 一句话定位

机器人基础模型部署后行为被预训练权重锁死，想换任务变体就得再采机器人数据或全模型微调；WAM-TTT 让用户只拍几段未标注的第一人称人类视频，在部署现场通过自监督视频预测把它们写进冻结 WAM 视频专家里的 TTT 快权重，从而操控动作生成，全程不需要重定向、机器人动作或人侧标注。

## 方法 / 对象

- 骨干：LDA（Qwen3-VL-4B-Instruct VLM + DiT-L MMDiT 动作头），16 个 MMDiT block、隐藏维 1536、32 头。
- 结构改动：只给视频专家加 TTT 残差，$z^{(\ell+1)}=\hat z^{(\ell+1)}+\Delta z^{(\ell)}_{TTT}$，而 $x^{(\ell+1)}=\hat x^{(\ell+1)}$ 恒等透传。动作专家完全不被触碰，这是「不覆盖预训练动作先验」的结构保证。
- TTT 层：慢投影 $\theta_{K,V,Q,O}$ 加快权重 MLP（头维 48、隐藏宽度 128），读出 $\Delta z^{(\ell)}_{TTT}=\theta_O f_{W}(\theta_Q(z^{(\ell)}))$。
- 键值记忆重建损失：$\mathcal{L}^{(\ell)}_{KVM}=\frac{1}{BL_hd}\|f_{W_i}(K_h)-V_h\|^2_2$，人类 token 出 K/V，机器人视频 token 出 Q。
- 内循环：$\mathcal{L}_{adapt}=\mathcal{L}^{human}_{vg}+\lambda\sum_\ell\mathcal{L}^{(\ell)}_{KVM}$，$\lambda=4\times10^{-2}$。两项都只依赖无动作人侧，所以测试时同样可用。
- 外循环：配对机器人数据上的 WAM 多任务损失，梯度穿过 TTT 残差与内层解析更新，优化 WAM 参数、慢投影和 $W_{init}$。
- 相位对齐：机器人时间步 $t$ 取 $\phi=t/T_r$，从人类视频取最近相位帧。
- 部署：全部冻结，只对目标域人类视频跑内层 SGD 更新快权重。$N=1$ 步，学习率 0.01（元训练内层 0.1）。
- 理论（附录 A）：线性特例下 $W^\ast=V_h^\top K_h(K_h^\top K_h)^{-1}$，在各向同性假设下退化成 Hebbian 外积 $\sum_i v_ik_i^\top$，查询即 $\sum_i(k_i^\top Q_r)v_i$，正是线性注意力读出。作者据此论证 KVM 在线性情形下就是交叉注意力的变分定义。
- 数据：2286 对人机 episode，9 任务 3 本体（Unitree G1 600、Galbot gripper 544、Galbot sharpa 1142）。机器人在标准化立方间遥操，人类用 GoPro 在真实家庭场景第一人称录制，无任何姿态或重定向标注。
- 训练规模：10 万步，批量 16/128，8× H800，DeepSpeed ZeRO-2。

## 证据

- New 设定（未见家庭环境，9 任务各 25 试次）平均 progress：WAM-TTT 46.2%，LDA 32.5%，WAM-COTRAIN 25.3%，EgoScale 15.0%，π0.5 14.8%，WAM-ICL 7.1%。九任务赢七个、平一个，唯一输的是 Stamp Paper（8.3 对 33.3）。
- Orig. 设定（标准化立方间）：WAM-TTT 61.1%，LDA 50.2%，WAM-ICL 48.4%，π0.5 31.8%，EgoScale 30.1%，WAM-COTRAIN 29.8%。
- 保留率（New/Orig）：WAM-TTT 0.76（−14.9），LDA 0.65（−17.7），EgoScale 0.50，π0.5 0.47，WAM-ICL 0.15（−41.3）。WAM-COTRAIN 的 0.85 是起点低造成的假象。
- WAM-COTRAIN 在 Orig. 上（29.8）低于完全不用人类数据的 π0.5（31.8）和 EgoScale（30.1）。没有对齐机制地混人类数据会主动损害分布内性能。
- 消融（2 任务各 10 试次，New）：Table Bussing / Swap Place 上 WAM-TTT 100.0/88.9，WAM-LoRA 30.0/0.0，w/o Meta Training 9.0/0.0，w/o Memory Recon. 66.7/72.0，w/o TTT 40.0/74.1。
- 泛化保持（Deliver Drink）：光照扰动 WAM-TTT 66.0 对 LDA 54.0、π0.5 28.0、WAM-ICL 12.0；空间扰动 56.0 对 28.0、0.0、20.0。
- 数据配比（3 任务）：(100,0) 59.5；(10,190) 51.4；(100,100) 74.1；(200,0) 73.7；(100,200) 73.3。人类数据可一比一替换机器人数据，但不能完全替代，且 h=100 已饱和。
- 架构（Table Bussing，10 试次）：DiT only 72.0，DiT+VLM 无预训练 80.0，VLM 冻结 54.0，VLM 开放 100.0。冻结 VLM 比不用 VLM 还差。
- 伪动作（4 任务各 25 试次）：VG only 72.3，VG+FD（MediaPipe + MANO + EgoScale 重定向）28.9，掉 43.4 点且四任务全降。即使在最接近 MANO 的灵巧手 Swap Place 上也掉 25.5 点。

## 局限

- 作者自陈：相位配对假设人机 episode 覆盖同一技能阶段分布，配不上时内层信号退化而损失不报警；部署适配受限于快权重表达力与元训练定死的慢投影，边界未实证刻画；接口只接受第一人称 RGB，不用手部姿态、接触或 3D 线索。
- $N=1$ 只做一步内层 SGD，论文没扫过 $N$，也没测对人类视频长度与数量的敏感度。这跟第二条自陈局限是同一问题的两面。
- 指标是加权部分得分，权重来自作者的生产评测细则。论文没有同时报二值成功率，读者无法判断 46.2% 里真正完成的试次占多少。
- WAM-LoRA 在 Swap Place 上为 0.0，但秩、学习率、更新步数、注入位置均未交代。这一行目前不足以支撑「收益来自 TTT 记忆结构而非通用低秩适配」。
- 泛化保持的定量证据只有一个任务两种扰动；附录 E.3 的六轴扰动只有定性 rollout。
- 伪动作负结果只测了一条 MediaPipe + MANO + EgoScale 管线，正确读法是「当前这条单视角管线不行」而非「伪动作这条路不行」。
- 自称即插即用，但需要配对人机数据做元训练并在每层挂 TTT 分支重跑 10 万步。真正即插即用的只有部署那一步。
- WAM-ICL 是作者自己实现的对照，上下文长度与演示数量的选取未交代。
- 数据配比只在三个任务、总预算 200 这一个量级上验证。

## 我的阅读笔记

这篇有两个可以直接拿走的结论，价值都超出论文本身。

第一个是 Table C.1 的保留率一列。同样的人类视频，当上下文 token 用（WAM-ICL）在立方间里能拿 48.4，一换家庭场景崩到 7.1，保留率 0.15；写进快权重（WAM-TTT）是 61.1 到 46.2，保留率 0.76。怎么用比用什么更重要，这个对照做得非常干净。长上下文条件化在分布内是帮手，分布一移就是负担。

第二个是附录 E.6。作者去试了大家都在走的重定向路线（MediaPipe 手部估计加 MANO 拟合加 EgoScale 重定向加前向动力学损失），四个任务平均掉 43.4 个点，全部下降。归因也很具体，夹爪和三指手的开合指令在 MANO 姿态里根本不存在，得靠手工后处理器补，这个后处理器叠在本来就噪的单目估计上，产出的伪动作离真实动作分布太远。这是个可引用的负结果，做人类视频迁移的人应该先看这一页。

结构上最该记的是 Eq. 1 里 $x^{(\ell+1)}=\hat x^{(\ell+1)}$ 那一行。TTT 残差只加视频流，动作专家恒等透传。这一个位置选择同时解决了三件事，不需要机器人动作监督、不覆盖预训练动作先验、人侧域偏移只能改写记忆改写不了策略。这种「用结构而不是用正则去保证性质」的做法很值得学。

消融里有个论文没点破的细节。Swap Place 上 w/o Memory Recon.（72.0）低于 w/o TTT（74.1）。一块写得不对的记忆比完全没有记忆更糟。这说明 KVM 损失的作用与其说是增益，不如说是防止记忆变成噪声源。

保留的怀疑主要在 $N=1$ 和 WAM-LoRA 那个 0.0。前者太激进却没有任何扫描支撑，后者低到不像方法本身的结论。这两处都会影响我对「TTT 记忆结构是必要的」这个论断的信心。

## 摘录

> Rather than treating human videos as trajectories to imitate, WAM-TTT absorbs them into a lightweight adaptive memory inside a frozen WAM through self-supervised video prediction.

> The TTT residual modifies only the video stream, leaving the action expert's output untouched; this places test-time human-video adaptation entirely on the video side, in the modality where the action-free human videos can naturally supervise.

> In other words, LKVM is not an auxiliary regularizer next to the cross-attention behaviour; in the linear case it is the variational definition of that behaviour.

> simply diluting robot supervision with human data without an explicit human-to-robot alignment mechanism actively damages in-distribution performance.

> under current single-view hand-tracking and retargeting maturity, injecting retargeted pseudo-actions into the human-side training signal is net-negative

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
