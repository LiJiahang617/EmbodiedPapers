---
tags:
  - paper
status: unread
aliases:
  - WorldSample
  - "WorldSample: Closed-loop Real-robot RL with World Modelling"
year: 2026
title: "WorldSample: Closed-loop Real-robot RL with World Modelling"
doi: "10.48550/arXiv.2607.02431"
arxiv: "2607.02431v1"
url: "https://arxiv.org/abs/2607.02431"
venue: "arXiv preprint"
venue_short: "arXiv"
arxiv_url: "https://arxiv.org/abs/2607.02431"
arxiv_doi: "10.48550/arXiv.2607.02431"
pdf_url: "https://arxiv.org/pdf/2607.02431v1"
project_url: "https://xxreinsno.github.io/worldsample/"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/xue2026worldsample.pdf]]"
reading: "[[papers/bilingual/xue2026worldsample_中英混读.md]]"
images: "papers/images/xue2026worldsample/"
image_index: "[[papers/images/xue2026worldsample/index.md]]"
map_axis: "世界模型/WAM/真机闭环RL与合成经验"
map_brief: "把一次真机 rollout 用动作条件世界模型扩成多条反事实合成轨迹，再用 Policy-Paced Learning（Q 感知筛选 + 策略熵调度）控制合成数据何时进入 critic 训练。"
map_role: "研究世界模型当增强器而非当环境用时，合成经验该怎么被安全地喂进真机 RL 的入口。"
authors:
  - "[[Yuquan Xue]]"
  - "[[Le Xu]]"
  - "[[Zeyi Liu]]"
  - "[[Zhenyu Wu]]"
  - "[[Zhengyi Gu]]"
  - "[[Xinyang Song]]"
  - "[[Bofang Jia]]"
  - "[[Ziwei Wang]]"
institutions:
  - "[[Nanyang Technological University]]"
  - "[[Tsinghua University]]"
  - "[[Central South University]]"
  - "[[Beijing University of Posts and Telecommunications]]"
topics:
  - real-robot RL
  - world model
  - data augmentation
  - counterfactual trajectory
  - value overestimation
  - human-in-the-loop
  - HIL-SERL
  - Cosmos-Predict2.5
---

# WorldSample: Closed-loop Real-robot RL with World Modelling

- [x] PDF:: [[papers/pdfs/xue2026worldsample.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/xue2026worldsample_中英混读.md]]
- [x] 图片索引:: [[papers/images/xue2026worldsample/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[real-robot RL]], [[world model]], [[data augmentation]], [[@luo2024precise-dexterous-robotic-manipulation]], [[@deng2026e2hil]], [[@qian2026wam-rl]], [[@peng2026fact]], [[@yu2026wm-dagger]], [[@huang2026rynnvalue]]
affiliation:: [[Nanyang Technological University]], [[Tsinghua University]], [[Central South University]], [[Beijing University of Posts and Telecommunications]]

## Abstract

Reinforcement learning (RL) can overcome the demonstration-coverage limitation of imitation learning (IL) by allowing robots to improve through trial-and-error interaction beyond the states observed in demonstrations. However, deploying RL on real robots remains constrained by high interaction costs, since each physical rollout is costly and reflects only one realized action-outcome path. To address this challenge, we propose WorldSample, a physically grounded data augmentation framework for real-robot RL that closes a real-synthetic loop between physical rollouts, world-model generation, and policy improvement. Grounded on real rollouts, WorldSample generates high-fidelity synthetic transitions through a post-trained world model, which greatly lowers the visual hallucination. Specifically, rather than simply using these transitions as real-world experience, WorldSample introduces Policy-Paced Learning (PPL) to regulate the training process through sample selection and scheduling, balancing useful augmentation against value overestimation and mitigating the hallucination-induced noise. Experiments on robot manipulation tasks involving contact-rich and precise tasks show that WorldSample improves policy success rate by 28% while reducing training steps by 59% compared with baselines. Furthermore, WorldSample improves world model visual fidelity by 19.4dB in PSNR and 0.47 in SSIM over demonstration-only post-training, validating the effectiveness of the real-synthetic loop for both policy and world model performance.

## 一句话定位

真机 RL 卡在 rollout 成本上，每次物理试错只揭示一条已实现的动作结果路径；WorldSample 用动作条件世界模型把每次 rollout 扩成多条锚在真实动作附近的反事实轨迹，再用 Policy-Paced Learning 控制这些合成数据「哪些能进」和「什么时候能信」，从而在不替代物理交互的前提下把每次交互榨得更干净。

## 方法 / 对象

- 真实-合成回路：物理 rollout 同时做策略训练数据和世界模型生成的接地来源；新 rollout 持续后训练世界模型，闭合回路。
- 反事实生成：$a'_t=\Pi_{\mathcal{A}}(a_t\odot\xi+\epsilon_t)$，$\xi_j\sim\mathcal{U}(1-s,1+s)$ 整段轨迹共享逐维尺度抖动，$\epsilon_{t,j}\sim\mathcal{N}(0,\sigma^2)$ 逐步局部扰动，不活跃维保持零。全实验 $s=0.20$、$\sigma=0.05$。动作是 7 维末端增量指令。
- 生成与标注：$\tilde O_{1:T}\sim p_\phi(\cdot\mid o_0,\tilde A_{0:T-1})$，$\tilde r=\hat R_\psi(\tilde O_{1:T})$。世界模型底座是动作条件 Cosmos-Predict2.5，先用示范适配再用在线 rollout 精修。
- 异步：世界模型生成与策略执行并行，不阻塞实时控制，可起多 worker。
- 误差动机：$\Delta Q(s,a)\approx\mathbb{E}[\sum_k\gamma^k\epsilon_{syn}(s_k,a_k)]$，合成残差会沿 Bellman 回溯放大。
- PPL 损失：$\mathcal{L}^{PPL}_Q=\mathbb{E}_{real}[\ell_Q]+\rho(H_t)\mathbb{E}_{syn}[w_Q\ell_Q]$。
- Q 感知筛选：正负合成轨迹分队列，约束 $|(\mathbb{E}_{D^+}Q+\mathbb{E}_{D^-}Q)-\mathbb{E}_{real}Q|\le\delta_Q$，防止 critic 被系统性推向乐观或保守。
- 熵调度：$H_t$ 是 actor 在真实状态上的熵，$\rho(H_t)=\rho_{max}/(1+\kappa H^p_t)$。实现用线性近似，$\rho_{max}=0.30$，$\kappa$ 与 $p$ 未给。
- 底座：建在 HIL-SERL 的 SAC/RLPD 学习器上，只改数据流。策略批量 256，每任务 20 条人类示范起步。

## 证据

- 真机五任务（Galaxea A1X，侧视 + 腕部 RealSense D435i）成功率：WorldSample 82%，WMPO 69%，VLAW 64%，HIL-SERL 56%。逐任务 95/95/95/84/42 对 HIL-SERL 的 84/63/66/55/10。
- 效率：平均训练步数 56K → 23K（降 59%），训练时间 83 → 64 分钟（物理交互降 23%）。Insertion 与 Sorting 分别少用 50% 和 33% 的真实交互步。
- WMPO 不需要真实交互但平均 547 分钟，是 WorldSample 的八倍多。省掉真机不等于省掉时间。
- 世界模型保真度：Pretrained 8.50 PSNR / 0.334 SSIM / 0.743 LPIPS；Demo-only 10.27 / 0.428 / 0.809；Rollout-only 28.43 / 0.906 / 0.034；Demo+Rollout 29.66 / 0.910 / 0.035；Dual-view 29.89 / 0.925 / 0.035。
- Demo-only 的 LPIPS（0.809）比 Pretrained（0.743）还差，只用窄覆盖示范微调反而伤了预训练先验。
- PPL 消融（insertion）：完整 95% / 干预 24% / 10K 步 / 30 分；w/o Scheduling 61% / 43% / 18K / 48 分；w/o Q-Selection 76% / 42% / 12K / 36 分；w/o Full-PPL 86% / 23% / 32K / 69 分；HIL-SERL 63% / 27% / 40K / 60 分。

## 局限

- **奖励模型 $\hat R_\psi$ 全文没有定义。** 它给每条合成轨迹打标，正负分队列和整套 Q 感知筛选都建在它之上，但架构、训练方式、训练数据、在生成视频上的标注准确率一概没有。世界模型会产幻觉，一条「看起来成功」的幻觉轨迹被标成正样本就会直接喂给 critic 做乐观外推。这是本文最大的空白。
- $s=0.20$、$\sigma=0.05$ 没有敏感性分析。这两个值决定反事实离真实多远，也就决定「增强有效性」与「世界模型外推误差」的平衡点，论文选一组用到底。
- 正文推导的 $\rho(H_t)=\rho_{max}/(1+\kappa H^p_t)$ 与实现用的线性近似对不上，$\kappa$ 和 $p$ 从未出现。Section 3.3 的理论部分和实际跑的东西是两回事。
- 评测试次数未报告。42% 这类数字如果只跑 20 次就是 8 到 9 次成功，方差很大。
- Eq. 5 的文字提到 $\Delta Q_{real}$，但式中并未出现该符号，记号有出入。正文还有「Further task details are provided in Appendix X」这样的占位符残留。
- 停止协议对本方法有利：基线训到收敛定义参考预算，WorldSample 则在收敛或墙钟追平时即停。
- 基线被改造过。VLAW 被降格成纯 IL 基线（20 真实 + 50 生成，20K BC 步），跟它原本的策略与世界模型迭代共同改进不是一回事；WMPO 的停止判据是「在世界模型里收敛」，本身就偏向让它过拟合世界模型。
- 「反事实生成比无约束 rollout 更物理可行」这条主张没有对照实验，论文没有跑「从随机动作先验采样」的对照组。
- Table 2.b 出现倒挂，只留一个 PPL 组件（61%、76%）比两个都不留（86%）更差。论文只解释了效率没解释成功率倒挂。
- Assemble 上所有方法都很差（最好 42%），这套增强对长时程精密装配帮助有限，作者未讨论天花板为何这么低。
- 作者自陈：只在单任务与相对固定的场景分布内做增强，实例级、任务级、场景级泛化留给未来。

## 我的阅读笔记

Table 2.a 是这篇最有冲击力的一块。预训练视频模型在目标机器人域上 PSNR 只有 8.50，用人类示范微调到 10.27，用在线 RL rollout 适配直接到 28.43。作者的解释是在线数据含失败和恢复行为，覆盖了示范之外的状态动作结果。这跟 [[@peng2026fact]] 的核心主张是一条线上的，两篇一起看，「世界模型必须见过失败」这个判断就相当扎实了。

还有一处论文没点破但更尖锐，Demo-only 的 LPIPS（0.809）比 Pretrained（0.743）还差。只用窄覆盖示范微调不仅没帮上忙，还把预训练先验搞坏了一点。这是「示范不够」最直接的证据。

Table 2.b 那个倒挂值得记。只去掉调度是 61%，只去掉 Q 筛选是 76%，两个都不用反而 86%。我的读法是两个组件必须配套，只留一个会制造偏斜的合成分布，比完全不调控更危险。这跟 [[@feng2026wam-ttt]] 里「写得不对的记忆比没有记忆更糟」是同一类现象，半套机制往往最坏。

Table 1 里 WMPO 那 547 分钟也值得单独记一笔。它不用真机，但世界模型 rollout 本身很慢，八倍于 WorldSample 的墙钟时间。「省掉真机」在直觉上等于省成本，实际上不一定。

保留的最大怀疑是奖励模型。整套 PPL 的前提是合成轨迹的标签可信，而这个打标器论文一个字都没交代。这一块恰好是 [[@huang2026rynnvalue]] 最擅长的，两者其实可以拼起来，用一个通用价值基础模型替掉这里的黑盒打标器。

## 摘录

> each rollout reveals only one realized action-outcome path.

> Rather than drawing actions from a random action prior, we sample trajectory segments from the real rollout distribution with local perturbations.

> Thus, naively injecting synthetic transitions can induce severe Q-value overestimation and extrapolation errors.

> Together, Q-aware selection and uncertainty-guided scheduling separate which synthetic trajectories are admitted from when they are trusted.

> This suggests that online RL data provides more diverse state-action outcomes, including failures and recovery behaviors, which helps the world model generalize beyond the demonstration distribution.

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
