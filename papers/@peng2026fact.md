---
tags:
  - paper
status: unread
aliases:
  - FACT
  - "FACT: Failure-Aware Causal Training for World-Action Models"
  - 失败感知因果训练
year: 2026
title: "FACT: Failure-Aware Causal Training for World-Action Models"
doi: "10.48550/arXiv.2608.10232"
arxiv: "2608.10232v1"
url: "https://arxiv.org/abs/2608.10232"
venue: "arXiv preprint"
venue_short: "arXiv"
arxiv_url: "https://arxiv.org/abs/2608.10232"
arxiv_doi: "10.48550/arXiv.2608.10232"
pdf_url: "https://arxiv.org/pdf/2608.10232v1"
project_url: "https://fact-wam.github.io"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/peng2026fact.pdf]]"
reading: "[[papers/bilingual/peng2026fact_中英混读.md]]"
images: "papers/images/peng2026fact/"
image_index: "[[papers/images/peng2026fact/index.md]]"
map_axis: "世界模型/WAM/失败数据与因果训练"
map_brief: "把 WAM 的次序从「先想未来再解动作」倒成「先出动作再预测后果」，用 teacher-forcing 掩码 mask 掉失败轨迹的动作模仿损失，只保留失败未来与低进度值监督。"
map_role: "研究失败数据在世界动作模型里该怎么用，以及动作条件价值头能否顺带支持候选打分的入口。"
authors:
  - "[[Quanquan Peng]]"
  - "[[Yutong Liang]]"
  - "[[Rui Yan]]"
  - "[[Nicklas Hansen]]"
  - "[[Xiaolong Wang]]"
institutions:
  - "[[University of California San Diego]]"
topics:
  - world-action model
  - failure data
  - causal training
  - action-conditioned prediction
  - future hallucination
  - task progress value
  - best-of-N
  - flow matching
  - bimanual manipulation
  - RoboTwin
---

# FACT: Failure-Aware Causal Training for World-Action Models

- [x] PDF:: [[papers/pdfs/peng2026fact.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/peng2026fact_中英混读.md]]
- [x] 图片索引:: [[papers/images/peng2026fact/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[world-action model]], [[failure data]], [[value model]], [[@yu2026wm-dagger]], [[@qian2026wam-rl]], [[@huang2026rynnvalue]], [[@gao2026fast-leworldmodel]], [[@pan2026vla-corrector-lightweight-detect]]
affiliation:: [[University of California San Diego]]

## Abstract

Recent world-action models (WAMs) show that co-training policies with future prediction can provide physical priors for action generation. Building on the future-prediction ability of video models, many WAMs generate future videos and recover actions with inverse-dynamics models, or use these predicted videos as goal conditions for action generation. In both cases, the world model is trained mostly on successful demonstrations and has little reason to predict the consequences of bad actions. We introduce FACT, a causal World-Action Model that predicts future video and task progress conditioned on the executed action. This action-conditioned interface allows failure rollouts to supervise action consequences, turning bad actions into valid future targets rather than being discarded. Failure-aware training makes the progress predictor aware of both successful and failed action outcomes, which can optionally be used to score sampled action candidates at inference. Extensive experiments on simulation and real-world bimanual manipulation tasks show that FACT outperforms many existing baselines, improves as failure data are incorporated into training, and reduces success-biased future hallucination under bad actions.

## 一句话定位

现有 WAM 的世界模型只在成功示范上训练，坏动作下仍会幻想出成功未来；FACT 把生成次序倒过来，先出动作再以该动作为条件预测未来视频和任务进度值，靠一个 teacher-forcing 掩码把「该模仿什么」和「该预测什么」分开，从而让失败回放轨迹只监督后果而不污染策略。

## 方法 / 对象

- 核心接口：$p_\theta(o'_{t:t+K}, v_t(a^{gt}_{t:t+H}) \mid o_t, \ell, a^{gt}_{t:t+H})$，世界分支以干净的 ground-truth 动作为条件。
- token 顺序：$z=[z^P_{ref} \| z^A_{pred} \| z^G_{gt} \| z^V_{value} \| z^I_{future}]$，V 与 I 注意 G 而非含噪的 A，且 A 看不到 G。
- 骨干：WAN2.2-5B 视频 diffusion transformer 共享给三路模态，每个 block FFN 之后给机器人 token 挂轻量 action adapter 走残差；明确不用 Mixture-of-Transformers，理由是要让世界侧损失能影响动作生成。
- 失败感知价值目标：成功取 $p_{t+H}$，失败取 $\text{clip}(p_{t+H}-\lambda_{fail}\mathbb{1}_{fail}(t+H),0,1)$，实验中 $\lambda_{fail}=1$，进度奖励取均匀故 $p_t=t/T$。
- 损失：三路统一 flow matching 速度预测。成功样本 $w_a\mathcal{L}_a+w_v\mathcal{L}_v+w_I\mathcal{L}_I$，失败样本去掉动作项。$w_a=20$，$w_v=w_I=1$。
- 超参：$H=48$，未来监督取 $[0,H/4,H/2,3H/4,H]$ 五个偏移，推理 20 步 flow-Euler，动作 FFN 学习率 $2\times10^{-4}$、骨干 $2\times10^{-5}$。
- 推理：Stage 1 去噪动作（可到此为止并复用前缀 KV 缓存），Stage 2 填入干净动作槽预测价值与未来；可选 best-of-N 打分，真机取 N=4。
- 失败数据来源：模型自身 rollout。仿真约 1.3K 条，真机每个方块任务约 30 条。

## 证据

- RoboTwin 50 任务：无视频协同训练 81.8% → 有视频 85.6% → 加失败数据 87.5%，接近 Motus 的 87.8% 但部署延迟从 1220 ms 降到 380 ms。
- 真机见过任务（5 个，每格 20 试次）：Ours 82% → w/ failure 89% → + scoring 92%。对比 π0.5 88%、Motus 64%、π0 48%、Cosmos 25%。
- 真机未见变体（3 个）：67% → 77% → 82%，仍低于 π0.5 的 85%（作者归因于 π0.5 有大规模预训练）。
- 消融（真机见过任务）：去视频协同训练 58%，失败动作不 mask 而进模仿损失 63%，去因果掩码 77%，无失败训练时加打分 79%（低于不打分的 82%）。
- 未来预测质量（512 留出样本）：失败子集 PSNR 19.51 → 25.92、SSIM 0.7461 → 0.8290；成功子集 26.12 → 26.08、0.8285 → 0.8286，几乎不动。
- 失败数据缩放（3 个 clean 任务）：$p\in\{0\%,50\%,100\%\}$ 对应平均成功率 32.7% → 57.3%，p=100% 时失败占训练集约 45%。
- 候选数量扫描：相对完成率从 N=1 到 N=4 明显上升，之后收益递减而延迟继续涨。
- 价值热图（Stack Cubes 3×3 网格）：模型给唯一能完成任务的中心放置最高分。

## 局限

- 进度奖励取均匀导致 $p_t=t/T$，把「进度」等同于「时间占比」。倒水、叠碗这类速度不均匀的任务里这个近似的代价没有被讨论，而价值头的判别力正建在这个目标上。
- $\lambda_{fail}=1$ 等于失败一发生就把进度压到 0，没区分失败的严重程度，也没做该超参的敏感性分析。
- 失败数据全部来自自身 rollout，失败分布与当前策略强绑定；策略变强后失败样本变少变微妙，这个 co-training 循环能否持续供血没有讨论（与 DAgger 类方法共享的老问题）。
- 真机每格只有 20 次试验，89% 与 92% 的差距落到单任务上常常只是一两次浮动。
- 共享骨干优于 MoT 这个设计选择只有论证没有对照实验。
- 未见任务仍落后 π0.5，泛化尚不能替代大规模预训练。
- best-of-N 用算力换可靠性，N=4 时延迟约 4 倍；纯动作模式 380 ms 仍比 π0.5 的 47 ms 慢一个数量级。
- 幻觉减少只用 PSNR 和 SSIM 两个像素级指标衡量，没有语义或物理合理性指标。

## 我的阅读笔记

这篇的技术内容其实很薄，核心就是 Eq. 5 那个 token 顺序加 Figure 3 那张掩码图。但薄不等于不好，它把一个大家都能想到的问题（失败数据没法用）解成了一个很干净的接口改动，不需要新模块也不需要新损失形式。

最值得记的数字是 Table 2 里「Ours + scoring」的 79%，比不打分的 82% 还低。价值头在没见过失败后果之前拿来排序是负收益，这个反例把因果关系坐实了，比任何正向提升都硬。写消融的时候这种「负结果对照」很值得学。

Table 4 的对照设计也很聪明。失败子集 PSNR 提升 6.4 dB，成功子集从 26.12 到 26.08 基本不动。一升一平，把「加失败数据不会伤正常预测」这条顺带证掉了，省了一个额外实验。

跟 [[@qian2026wam-rl]] 并读收益最大。WAM-RL 的局限里明确写着「只用成功轨迹更新 world model，对失败原因利用不足」，FACT 正好补的就是那一条。半年之内 WAM 后训练这条线的推进方向，从这两篇的接力能看得很清楚。

保留的怀疑主要在 $p_t=t/T$ 这个简化上。用时间占比当进度，对匀速任务勉强能用，对倒水这种末段才出结果的任务就有问题。价值头的所有判别力都建在这个目标上，作者却一句话带过。如果要复现或者迁移到自己的任务，这里是第一个该改的地方。

## 摘录

> The key challenge is not merely adding more data, but using rollouts that fail to complete the desired task without turning them into bad demonstrations.

> failures teach consequences, not behavior.

> With success-only training, progress prediction is calibrated mainly on the expert action manifold and may assign overly optimistic scores to poor actions.

> This action-conditioned view of world modeling provides a natural interface for future training regimes that include online rollouts, DAgger-style corrections, and reinforcement learning from negative experience.

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
