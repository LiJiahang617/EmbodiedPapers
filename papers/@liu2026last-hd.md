---
tags:
  - paper
status: unread
aliases:
  - LaST-HD
  - "LaST-HD: Learning Latent Physical Reasoning from Scalable Human Data for Robot Manipulation"
year: 2026
title: "LaST-HD: Learning Latent Physical Reasoning from Scalable Human Data for Robot Manipulation"
doi:
arxiv: "2606.23685v1"
url: "https://arxiv.org/abs/2606.23685"
venue: "arXiv technical report"
project: "https://siriyep.github.io/last-hd-project-page/"
pdf_url: "https://arxiv.org/pdf/2606.23685v1"
openalex:
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/2606.23685v1.pdf]]"
reading: "[[papers/bilingual/liu2026last-hd_中英混读.md]]"
images: "papers/images/2606.23685v1/"
image_index: "[[papers/images/2606.23685v1/index.md]]"
authors:
  - "[[Jiaming Liu]]"
  - "[[Yinxi Wang]]"
  - "[[Chenyang Gu]]"
  - "[[Siyuan Qian]]"
  - "[[Xiangju Mi]]"
  - "[[Hao Chen]]"
  - "[[Jiawei Chen]]"
  - "[[Qingpo Wuwu]]"
  - "[[Xiaoqi Li]]"
  - "[[Nuowei Han]]"
  - "[[Yiming Zhang]]"
  - "[[Xuheng Zhang]]"
  - "[[Yang Yue]]"
  - "[[Yeqing Yang]]"
  - "[[Lei Wang]]"
  - "[[Peng Jia]]"
  - "[[Hao Tang]]"
  - "[[Shanghang Zhang]]"
institutions:
  - "[[Peking University]]"
  - "[[The Chinese University of Hong Kong]]"
  - "[[Simplexity Robotics]]"
  - "[[Aether Tech]]"
topics:
  - vision-language-action
  - human-to-robot transfer
  - latent physical reasoning
  - action-conditioned world model
  - human-hand demonstrations
  - cross-embodiment alignment
  - Out-of-Lab Glove
  - online correction
  - Mixture-of-Transformers
  - dexterous manipulation
---

# LaST-HD: Learning Latent Physical Reasoning from Scalable Human Data for Robot Manipulation

- [x] PDF:: [[papers/pdfs/2606.23685v1.pdf]]
- [x] 元数据:: source=arxiv, confidence=high；机构与 technical-report 口径由 PDF v1 核对
- [x] 项目页:: [siriyep.github.io/last-hd-project-page](https://siriyep.github.io/last-hd-project-page/)
- [x] 精读稿:: [[papers/bilingual/liu2026last-hd_中英混读.md]]
- [x] 图片索引:: [[papers/images/2606.23685v1/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，并通过 `python setting/scripts/check_paper_map.py`
- [ ] 阅读状态:: unread

related:: [[human-to-robot transfer]], [[latent physical reasoning]], [[action-conditioned world model]], [[@liu2026last0-latent-spatio-temporal]], [[@kim2026ego-pi]], [[@paliwal2026do-i-dexterous-manipulation]], [[@qwen2026robotmanip]], [[@yu2026wm-dagger]]
affiliation:: [[Peking University]], [[The Chinese University of Hong Kong]], [[Simplexity Robotics]], [[Aether Tech]]

## Abstract

Human-hand demonstrations provide a direct and scalable source of physical interaction data for robot learning. While manual retargeting is indispensable for establishing kinematic action correspondence across different morphologies, robust transfer requires going beyond geometry to address the underlying alignment of physical dynamics between human and robot manipulation. To address this, we introduce LaST-HD, a novel human-to-robot action learning paradigm that extends reasoning-before-acting VLA by aligning human-hand and robot demonstrations in a shared latent reasoning space. Rather than mimicking human kinematics, LaST-HD trains an auxiliary action-conditioned world model on unpaired human-hand and robot trajectories to synthesize unified latent targets. After aligning cross-embodiment representations in this shared forward-dynamics space, these targets supervise LaST-HD's latent reasoning process, enabling it to internalize shared physical dynamics and drive efficient human-hand action learning. Moreover, we develop Out-of-Lab (OOL) Glove, a low-cost motion-capture glove tailored to LaST-HD for human-hand data collection. The captured human data provide precise keypoints and serve as universal action supervision across grippers and dexterous hands. Armed with the aligned latent space and high-fidelity human-hand data, we develop a progressive mixed-to-human training recipe comprising mixed human-robot co-training and human-hand online correction post-training. Through mixed co-training, LaST-HD improves generalization to novel objects, scenes, and positions using only human-hand demonstrations. With online correction, LaST-HD further adapts to novel environments and achieves over 90\% accuracy using only 20 minutes of OOL glove data.

## 一句话定位

LaST-HD 是 LaST₀ 的 human-data extension（人类数据扩展）：不用人手/机器人外观或动作本身硬对齐，而让 action-conditioned world model 把两种未配对轨迹映到“动作会造成什么物理后果”的共享 latent target，再用这组 target 监督 MoT reasoning expert，配合 OOL Glove 与 mixed-to-human 训练把廉价人手示范转成机器人泛化与纠错能力。

## 方法 / 对象

- 基座：Janus-Pro / DeepSeek-LLM 1.5B 的 24 层 MoT VLA；reasoning expert 自回归生成 latent CoT，action expert 用 flow matching 输出 action chunk，二者共享 attention。
- Latent alignment：在未严格配对的人手/机器人轨迹上训练 action-conditioned video world model；取最后 denoising step 最深 U-Net 的 forward-dynamics feature，经 MLP、flatten、adaptive pooling 变成 $N_{lat}$ 个 latent target，以 cosine loss 监督 reasoning expert。
- OOL Glove：每手 6 个 9-axis IMU、21 个 hand-wrist 6-DoF keypoints，<100g、>200Hz、<10ms；人手轨迹再启发式 retarget 到 gripper 或 20-DoF WUJI hand。
- Stage 1：混合人手/机器人数据训练 world model，再冻结；LaST-HD 同时优化 flow-matching action loss 与 latent cosine loss。
- Stage 2：真机 rollout 找 failure-prone state，用手套采 targeted human corrections；previous buffer 与 correction buffer 1:1 replay，只后训练 1–2 epochs。
- 评测：Galaxea R1 Lite、Tianji Marvin gripper、Marvin+WUJI 三种配置，六项真机任务；OOD 分 unseen position/object/background。

## 证据

- In-domain：LaST-HD（100 robot demos）六任务均值 0.73，超过 LaST₀ 0.63、$\pi_{0.5}$ 0.62、Cosmos-Policy 0.52；50 robot + 50 human 的 Mix-HD 为 0.68。
- 纯 in-domain checkpoint 的 zero-shot OOD global avg 只有 0.31，与 LaST₀/$\pi_{0.5}$ 的 0.30 接近；加入每个 unseen scenario 60 条目标域 human demos 后，LaST-HD 达 0.56，超过 LaST₀+HD 的 0.46。
- 三类 target-HD 泛化均值：position 0.41、object 0.58、background 0.68；对应 LaST₀+HD 为 0.33/0.49/0.58。
- Sort Fruits online correction：0/10/20/60 条 human corrections 下，background 90→95→100→100，object 70→90→95→100，position 60→65→70→80；60 条用时 20 min，三类平均最终约 93.3%。
- Latent target 消融：action-conditioned WM 73%，WM-only 66%，future SigLIP 63%，无 latent 60%。数据源对比：OOL 73%，Real-60 75%，Real-12（同采集时间）60%，bare hand 63%，UMI 65%，palm-view glove 67%。

## 局限

- “morphology-agnostic” 仍建立在手工 retargeting 上；作者明确承认每增加一种 dexterous hand 都要重建启发式映射，且 world-model pretraining 需含 target embodiment 数据。
- 主要泛化增益不是 zero-shot：Mix-HD 的零样本 global avg 0.31，几乎等于 LaST₀/$\pi_{0.5}$ 的 0.30；达到 0.56 需要每种 unseen scenario 的目标域人手数据。
- “20 分钟超过 90%”只在 Sort Fruits online-correction 实验成立，三类平均约 93%，其中最难 position 最终仍是 80%；不能外推为六任务均超过 90%。
- 2000h OOL 数据用于 world-model latent supervision的具体人/机器人混合比例、覆盖关系与公开状态未充分说明；论文说数据集仍计划发布。VLA 主干为公平比较只用 400K robot trajectories 预训练。
- OOL Glove 的“low-cost”没有 BOM/总价，sub-mm RMS 也缺完整测量协议；完整采集栈还包括腕部 tracker、双腕相机与头部 ZED。
- 每个任务通常只评 20 rollouts，未给多训练 seed、置信区间或显著性统计；UMAP/attention 只能作表征可视化，不能单独证明因果对齐。
- latent reasoning 仍非实时；16-token latent 虽达 0.78，但论文为速度选 4-token（0.73），未给端到端 Hz/latency。

## 我的阅读笔记

这篇最值得记住的判断是：human→robot 的瓶颈不只在“动作坐标怎么映射”，更在“同一动作意图在两种身体下造成的物理后果是否被表示到同一个空间”。LaST-HD 用带动作条件的 forward-dynamics feature 当 teacher，确实比纯 SigLIP appearance target 和无 action 的 WM target 更强；但它并没有消灭 geometry layer，手工 retargeting 仍是 action weak anchor 的前置条件。

与 LaST₀ 的关系要明确：LaST₀ 解决 latent spatio-temporal reasoning 与快慢专家；LaST-HD 继承该 MoT 接口，重点新增跨本体 latent supervision、人手采集硬件和 correction recipe。两篇是独立论文，不是同名版本。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
