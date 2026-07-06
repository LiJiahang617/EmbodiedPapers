---
tags:
  - paper
status: unread
aliases:
  - WAM-RL
  - WA-RL
  - "World-Action Model Reinforcement Learning"
  - "WAM-RL: World-Action Model Reinforcement Learning with Reconstruction Rewards and Online Video SFT"
year: 2026
title: "WAM-RL: World-Action Model Reinforcement Learning with Reconstruction Rewards and Online Video SFT"
doi: "10.48550/arXiv.2606.17906"
url: "https://arxiv.org/abs/2606.17906"
venue: "arXiv preprint"
venue_short: "arXiv"
arxiv: "2606.17906v1"
arxiv_url: "https://arxiv.org/abs/2606.17906"
arxiv_doi: "10.48550/arXiv.2606.17906"
pdf_url: "https://arxiv.org/pdf/2606.17906v1"
pdf: "[[papers/pdfs/WAM-RL.pdf]]"
reading: "[[papers/bilingual/qian2026wam-rl_中英混读.md]]"
images: "papers/images/qian2026wam-rl/"
image_index: "[[papers/images/qian2026wam-rl/index.md]]"
map_axis: "世界模型/WMA/在线强化学习与世界模型后训练"
map_brief: "在 World-Action Model 中同时优化 world model 和 actor：成功轨迹做 online video SFT + KL 稳定 latent space，actor 用 reconstruction-based dense reward 做 RL。"
map_role: "研究 WA/WAM 如何从专家轨迹监督扩展到在线交互强化学习的入口。"
authors:
  - "[[Zezhong Qian]]"
  - "[[Xiaowei Chi]]"
  - "[[Yu Qi]]"
  - "[[Haozhan Li]]"
  - "[[Zhi Yang Chen]]"
  - "[[Shanghang Zhang]]"
institutions:
  - "[[Peking University]]"
  - "[[State Key Laboratory of Multimedia Information Processing]]"
  - "[[Northeastern University]]"
  - "[[Tsinghua University]]"
topics:
  - world-action model
  - reinforcement learning
  - online video SFT
  - reconstruction reward
  - flow matching
  - Flow-SDE
  - VLA
  - robot manipulation
  - LIBERO
  - RLBench
---

# WAM-RL: World-Action Model Reinforcement Learning with Reconstruction Rewards and Online Video SFT

- [x] PDF:: [[papers/pdfs/WAM-RL.pdf]]
- [x] 精读稿:: [[papers/bilingual/qian2026wam-rl_中英混读.md]]
- [x] 图片索引:: [[papers/images/qian2026wam-rl/index.md]]
- [x] 论文地图:: [[论文地图]]
- [ ] 阅读状态:: unread

related:: [[world-action model]], [[reinforcement learning]], [[online fine-tuning]], [[@yu2026wm-dagger]], [[@zhang2026contactworld]], [[@tang2026frs]], [[@qwen2026robotmanip]]
affiliation:: [[Peking University]], [[Northeastern University]], [[Tsinghua University]]

## 一句话问题

World-Action Models（WA/WAM）通常靠 expert trajectories 做监督训练，难以通过真实交互继续提升；WAM-RL 试图把 reinforcement learning 加进 WA 范式，让 world model 和 actor 在线共同优化，而不是只调动作头。

## 方法

- 基础范式：WA policy 由 world model 和 actor 组成，world model 生成 imagined future observations，actor 把 latent predictions 翻译成 executable actions。
- actor RL：用 Flow-SDE 把 flow-based action model 的去噪过程变成带随机性的轨迹，从而可以估计 action likelihood 并做 policy gradient。
- reconstruction-based reward：比较 world model imagined trajectory $\hat{x}_{t+1:t+H}$ 与真实执行得到的 trajectory $x_{t+1:t+H}$ 的相似度，作为 dense reward。
- reward 设计：尝试 Pixel MSE、Optical Flow MSE、DINOv2 MSE、V-JEPA2 MSE；最终 Pixel MSE 下游成功率最高。
- online video SFT：只用交互中成功 rollouts 的 observation sequences 对 world model 做自监督视频微调，让它学到 failure / recovery dynamics。
- KL regularization：用 frozen pretrained world model 的 latent feature distribution 约束更新后的 world model，防止 latent space 漂移导致 actor 失效。

## 证据

- LIBERO-Object：Base 68%，actor-only $\pi_{RL}$ 78%，WAM-RL 82%。
- RLBench Water Plants：Base 19%，actor-only $\pi_{RL}$ 18%，WAM-RL 22%。这支持作者的核心结论：长时程任务中只优化 actor 不够。
- reconstruction reward 消融：Pixel MSE 21%，Optical Flow MSE 19%，DINO MSE 16%，V-JEPA2 17%。Optical Flow 区分成功/失败更强，但不一定更适合优化。
- video SFT 定性结果：没有 video SFT 时失败后没有 recovery，轨迹漂到 OOD；有 video SFT 后，模型在单个 open-loop chunk 内会预测重新定位夹爪、再次抓取等 recovery behavior。

## 局限

- 实验规模偏小：只报告 LIBERO-Object 和 RLBench Water Plants 两个设置，且提升幅度在 RLBench 上较小。
- online video SFT 的 KL regularization 保稳定，但也限制 world model 能离开预训练分布的幅度。
- reconstruction rewards 仍是手工/预训练表示定义，成功和失败的 reward contrast 有限，尤其 Pixel MSE 可解释但语义性弱。
- 只用 successful trajectories 更新 world model，可能强化已有成功模式，对探索失败原因和困难负样本利用不足。
- 没有展示真实机器人实验，当前证据主要来自仿真基准。

## 我的阅读笔记

这篇和 [[@yu2026wm-dagger]] 很适合并排看。WM-DAgger 用 world model 离线合成 recovery data，然后训练 policy；WAM-RL 则尝试在在线交互里让 world model 自己变好，再让 actor 用 reconstruction reward 对齐“想象”和“执行”。两者共同指向一个判断：如果机器人策略依赖世界模型，那么只调动作输出层是不够的，world model 本身的 failure / recovery dynamics 也要更新。

本文最重要的 insight 是：WA model 的能力上限主要由 world model 决定，actor 更像 latent prediction 到 action 的 translator。短任务中 actor-only RL 可能有效，但长时程任务里 world model 的预测误差会累积，actor 无法凭空修正错误想象。因此在线 video SFT 是 WAM-RL 的关键。

需要谨慎的是，当前实验还不足以证明这个 recipe 已经成熟。LIBERO 提升明显，RLBench 只从 19% 到 22%；reward 设计也还比较粗。但它提出了一个值得跟踪的问题：未来 VLA/WAM 的 RL 后训练，是否应该从“policy-only RL”转向“world-model-and-policy co-training”。

## 摘录

