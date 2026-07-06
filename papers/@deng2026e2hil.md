---
tags:
  - paper
status: unread
aliases:
  - E2HiL
  - "Entropy-Guided Sample Selection"
  - "E2HiL: Entropy-Guided Sample Selection for Efficient Real-World Human-in-the-Loop Reinforcement Learning"
year: 2026
title: "E2HiL: Entropy-Guided Sample Selection for Efficient Real-World Human-in-the-Loop Reinforcement Learning"
doi: "10.48550/arXiv.2601.19969"
url: "https://arxiv.org/abs/2601.19969"
venue: "arXiv preprint"
venue_short: "arXiv"
arxiv: "2601.19969v1"
arxiv_url: "https://arxiv.org/abs/2601.19969"
arxiv_doi: "10.48550/arXiv.2601.19969"
pdf_url: "https://arxiv.org/pdf/2601.19969v1"
project: "https://e2hil.github.io/"
pdf: "[[papers/pdfs/2601.19969v1.pdf]]"
reading: "[[papers/bilingual/deng2026e2hil_中英混读.md]]"
images: "papers/images/2601.19969v1/"
image_index: "[[papers/images/2601.19969v1/index.md]]"
map_axis: "具身智能/RL/真实机器人HiL"
map_brief: "用样本对 policy entropy 的 covariance influence 选择中等影响的人工/探索样本，剪掉 shortcut 与 noisy samples，提升真实机器人 HiL-RL 样本效率。"
map_role: "研究真实机器人在线 RL 中 human intervention samples 如何被筛选和高效利用的入口。"
authors:
  - "[[Haoyuan Deng]]"
  - "[[Yuanjiang Xue]]"
  - "[[Haoyang Du]]"
  - "[[Boyang Zhou]]"
  - "[[Zhenyu Wu]]"
  - "[[Ziwei Wang]]"
institutions:
  - "[[Nanyang Technological University]]"
  - "[[Beijing University of Posts and Telecommunications]]"
topics:
  - human-in-the-loop reinforcement learning
  - real-world reinforcement learning
  - robotic manipulation
  - entropy regularization
  - sample selection
  - policy entropy
  - influence function
  - RLPD
  - HIL-SERL
  - Lerobot SO-101
---

# E2HiL: Entropy-Guided Sample Selection for Efficient Real-World Human-in-the-Loop Reinforcement Learning

- [x] PDF:: [[papers/pdfs/2601.19969v1.pdf]]
- [x] 精读稿:: [[papers/bilingual/deng2026e2hil_中英混读.md]]
- [x] 图片索引:: [[papers/images/2601.19969v1/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，并运行 `python setting/scripts/check_paper_map.py`
- [ ] 阅读状态:: unread

related:: [[human-in-the-loop reinforcement learning]], [[real-world reinforcement learning]], [[entropy regularization]], [[robotic manipulation]], [[RLPD]], [[@qian2026wam-rl]], [[@yu2026wm-dagger]], [[@tang2026frs]]
affiliation:: [[Nanyang Technological University]], [[Beijing University of Posts and Telecommunications]]

## 一句话问题

真实机器人 HiL-RL 中，人工接管样本虽然能加速学习，但并非所有样本都值得同等更新策略；E2HiL 试图用样本对 policy entropy 的 influence value 筛出真正有信息量的样本，避免 shortcut samples 过早压塌熵，也避免 noisy samples 拖慢学习。

## 方法

- 基于 RLPD / entropy-regularized actor objective，先把样本对策略熵变化的影响近似为 `log pi(a|s)` 与 logit change 的 covariance。
- 将 actor gradient 写成 soft advantage 形式，得到 `Delta z = eta pi(a|s) A_soft(s,a)`，从而把 entropy change 近似为 `-eta Cov(log pi, pi A_soft)`。
- 对每个 state-action sample 估计 influence value `c(s_t,a_t)=-eta Cov_hat(s_t,a_t)`，作为 stop-gradient signal。
- 用 batch-wise dynamic bounds `[ell,u]` 保留中等 `|c|` 样本；过大影响视为可能导致 entropy collapse 的 shortcut samples，过小影响视为 noisy/redundant samples。
- 在 actor update 中用 indicator `I(s_t,a_t)` mask 掉极端样本，只让 entropy-consistent samples 贡献策略梯度。

## 证据

- 四个真实 SO-101 操作任务上，E2HiL 平均成功率 83.9，HIL-SERL 为 41.8；平均人工接管率 33.9，HIL-SERL 为 44.0。
- E2HiL 平均只需 68.7k steps 达到 70% success rate，而 HIL-SERL 更容易因 aggressive entropy collapse 收敛到次优表现。
- Touch-Cube 中，batch-wise covariance 与 policy entropy derivative `-Delta H` 的曲线趋势相近，支持 covariance influence 估计。
- 人工干预样本的 covariance magnitude 明显高于自探索样本；Top 2% 中 intervention samples 为 368.1，exploration samples 为 5.56。
- 被剪样本多数来自 human interventions，且空间上常落在 workspace 外或重复状态，支持 clipping 同时去除 shortcut 与 noisy/low-diversity corrections。

## 局限

- 实验只覆盖 SO-101 和四个 cube/block 真实操作任务，还不能证明对灵巧手、长时程多阶段任务或复杂接触装配同样有效。
- covariance influence 依赖 critic 的 Q-value 和 soft advantage，训练早期 Q 不准时估计会偏；论文也观察到前 5k steps 有偏差。
- `[ell,u]` 的 5th / 90th percentile clipping 是启发式，缺少阈值敏感性和任务阶段自适应分析。
- 成功率和接管率缺少充分的多随机种子、多操作者、置信区间或显著性统计。
- 与 VLA 在线 RL 的关系仍是未来工作，当前实验不是大规模 VLA backbone。

## 我的阅读笔记

这篇适合放在真实机器人 RL 和 VLA 后训练之间看。它的重点不是“什么时候让人接管”，而是“接管后的样本是否应该驱动策略更新”。这比单纯降低 intervention frequency 更细，因为人类纠偏样本通常强影响策略：用得好可以快速纠正，用不好可能让策略熵过早塌缩。

最值得记住的是 covariance influence 这条链：`Delta H -> Cov(log pi, Delta z) -> Cov(log pi, pi A_soft)`。它把样本选择从经验规则推进到一个可估计的 entropy dynamics proxy。虽然这个 proxy 依赖 critic 质量，但它提供了一个清晰接口，可以和 workspace constraints、state novelty、human feedback type 或 future VLA RL 的 token/action entropy 结合。

需要警惕的是，论文的真实机器人证据很有价值但规模还小。Table I 的提升很大，不过没有充分统计展开。后续如果复现，应重点看三件事：早期 critic 校准、clipping percentile 敏感性、以及被剪样本是否真的对 downstream policy 有负贡献。

## 摘录

