---
tags:
  - paper
status: unread
aliases:
  - WM-DAgger
  - "WM-DAgger: Enabling Efficient Data Aggregation for Imitation Learning with World Models"
year: 2026
title: "WM-DAgger: Enabling Efficient Data Aggregation for Imitation Learning with World Models"
doi: "10.48550/arXiv.2604.11351"
url: "https://arxiv.org/abs/2604.11351"
venue: "arXiv preprint"
venue_short: "arXiv"
arxiv: "2604.11351v1"
arxiv_url: "https://arxiv.org/abs/2604.11351"
arxiv_doi: "10.48550/arXiv.2604.11351"
pdf_url: "https://arxiv.org/pdf/2604.11351v1"
code: "https://github.com/czs12354-xxdbd/WM-Dagger"
pdf: "[[papers/pdfs/WM-DAgger.pdf]]"
reading: "[[papers/bilingual/yu2026wm-dagger_中英混读.md]]"
images: "papers/images/yu2026wm-dagger/"
image_index: "[[papers/images/yu2026wm-dagger/index.md]]"
map_axis: "世界模型/WAM/数据聚合与策略修复"
map_brief: "用 eye-in-hand action-conditioned world model 合成 OOD recovery trajectories，再用方向约束和 DINOv2 终帧一致性过滤减少误监督。"
map_role: "研究世界模型如何为 imitation learning 自动补 recovery data 的入口。"
authors:
  - "[[Anlan Yu]]"
  - "[[Zaishu Chen]]"
  - "[[Peili Song]]"
  - "[[Zhiqing Hong]]"
  - "[[Haotian Wang]]"
  - "[[Desheng Zhang]]"
  - "[[Tian He]]"
  - "[[Yi Ding]]"
  - "[[Daqing Zhang]]"
institutions:
  - "[[Peking University]]"
  - "[[JD Logistics]]"
  - "[[Nankai University]]"
  - "[[The Hong Kong University of Science and Technology (Guangzhou)]]"
  - "[[Rutgers University]]"
  - "[[University of Texas at Dallas]]"
  - "[[Institut Polytechnique de Paris]]"
topics:
  - imitation learning
  - DAgger
  - world model
  - robotic manipulation
  - data aggregation
  - out-of-distribution recovery
  - eye-in-hand
  - action-conditioned video generation
  - VLA
  - policy training
---

# WM-DAgger: Enabling Efficient Data Aggregation for Imitation Learning with World Models

- [x] PDF:: [[papers/pdfs/WM-DAgger.pdf]]
- [x] 代码:: [czs12354-xxdbd/WM-Dagger](https://github.com/czs12354-xxdbd/WM-Dagger)
- [x] 精读稿:: [[papers/bilingual/yu2026wm-dagger_中英混读.md]]
- [x] 图片索引:: [[papers/images/yu2026wm-dagger/index.md]]
- [x] 论文地图:: [[论文地图]]
- [ ] 阅读状态:: unread

related:: [[imitation learning]], [[DAgger]], [[world model]], [[@zhang2026contactworld]], [[@qwen2026robotmanip]], [[@xu2026egoguide]], [[@tang2026frs]]
affiliation:: [[Peking University]], [[JD Logistics]], [[Nankai University]], [[The Hong Kong University of Science and Technology (Guangzhou)]], [[Rutgers University]], [[University of Texas at Dallas]], [[Institut Polytechnique de Paris]]

## 一句话问题

Behavioral Cloning（行为克隆）在少量示范下会因为 compounding errors（误差累积）进入训练集没覆盖的 OOD states；传统 DAgger 需要人不断接管纠偏，WM-DAgger 想用 World Model 自动合成“偏离后如何回来”的 recovery data，降低人工成本。

## 方法

- EAC-WM：基于 GE-Sim / Cosmos-Predict2.5 的 Eye-in-Hand Action-Conditioned World Model，把 low-dimensional action 转成 pixel-aligned dense geometric condition，生成动作条件下的未来眼在手相机图像。
- Action2Image：把相机位姿变化映射成每个像素的 origin displacement 和 viewing direction shift，再拼上 gripper condition，缓解稀疏动作向量被高维视觉条件淹没的问题。
- Corrective Action Synthesis：从 expert trajectory 随机选 pivot，先沿随机方向偏离专家轨迹，再反向回到专家流形；只保留 recovery phase 训练策略。
- 方向约束：过滤与后续专家动作夹角小于 120 度的偏离方向，避免生成和任务目标相冲突的 recovery supervision。
- Consistency-Guided Filtering：用 DINOv2 比较合成 rollout 的终帧与同视角真实专家帧的 cosine similarity，低相似度轨迹视为 hallucination 或物理不一致并丢弃。
- Policy training：把 expert Task Data 与筛选后的 synthetic recovery data 聚合，用 action chunking 和 MSE 训练 Gr00t N1.5 policy。

## 证据

- Soft Bag Pushing：只用 5 条示范，WM-DAgger 达到 93.3% 成功率；Standard BC 为 26.7%，DMD 为 40.0%。20-shot 时 WM-DAgger 达 96.7%。
- 合成数据规模：300 / 900 / 1500 / 3000 条 synthetic samples 对应 46.7 / 63.3 / 96.7 / 96.7，说明 1500 左右已能覆盖主要 OOD recovery 行为。
- 消融：Full 96.7%；w/o Play Data 83.3%；w/o Filter 66.7%；w/o Dir. 0.0%。方向约束是防止策略学坏的关键。
- Pick-and-Place：seen objects 达 83.3 / 90.0 / 80.0，unseen objects 达 63.3 / 76.7，明显高于 BC 与 DMD。
- Ballot Insertion：Standard BC 13.3%，DMD 26.7%，WM-DAgger 73.3%，说明 high-precision contact-rich insertion 需要 recovery 能力。
- Towel Folding：BC 0.0%，DMD 10.0%，WM-DAgger 46.7%，但绝对成功率仍显示 deformable 6-DoF 任务很难。

## 局限

- 结果依赖世界模型生成质量；过滤只用终帧相似度，不能保证中间帧的动力学全部正确。
- 当前主要验证 two-finger gripper 和 eye-in-hand 设置；迁移到 dexterous multi-finger hands 会遇到高 DoF、遮挡和关节形变一致性问题。
- 合成 recovery action 的方向/幅度规则仍是启发式；它能减少反向监督，但不等价于真正的 expert optimal recovery。
- 成功率评估任务规模不大，且基于真实机器人但未覆盖长时程多阶段任务。
- 策略训练只把筛选后的合成数据作为监督，没有在线闭环地继续验证和修正 world model 生成偏差。

## 我的阅读笔记

这篇的关键不是“世界模型能生成漂亮视频”，而是把 world model 放进 imitation learning 的数据闭环里：BC 失败是因为部署时会走到示范分布外；DAgger 能补这个分布外区域，但要人接管；WM-DAgger 则尝试让世界模型在专家轨迹周围自动生成“偏出去再回来”的局部 recovery manifold。

最值得记住的设计是两个保险丝。第一，Corrective Action Synthesis 不是随机扰动，而是用方向约束避免和专家动作相冲突。第二，Consistency-Guided Filtering 不相信世界模型所有 rollout，而是用终帧回到专家视角时的 DINOv2 相似度做物理一致性筛选。消融里 w/o Dir. 直接 0.0%，说明合成数据如果方向错，会比没有数据更危险。

和 [[@zhang2026contactworld]] 相比，ContactWorld 更关注 world model 如何用于 contact-rich planning / MPC；WM-DAgger 更关注 world model 如何服务 supervised policy training。和 [[@qwen2026robotmanip]] 这类大规模 VLA scaling 相比，WM-DAgger 的数据规模小得多，但它给了一个很实用的问题切口：不是只收更多成功示范，而是系统性补“失败边缘如何恢复”的数据。

后续复现或扩展时应重点追问三件事：一是 DINOv2 终帧相似度是否能过滤接触力学错误；二是 recovery action 的方向约束是否适用于需要先反向/绕行的任务；三是如果把该方法接入触觉或多视角观测，world model 的 consistency check 是否应该同时看视觉、触觉和状态。

## 摘录

