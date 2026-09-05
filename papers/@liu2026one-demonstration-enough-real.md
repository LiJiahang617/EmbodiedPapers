---
tags:
  - paper
  - cat/rl
status: unread
aliases:
  - AutoSERL
  - "One Demonstration Is Enough for Real-World Robotic Reinforcement Learning"
year: 2026
title: "One Demonstration Is Enough for Real-World Robotic Reinforcement Learning"
doi: "10.48550/arXiv.2607.01651"
arxiv: "2607.01651v1"
url: "https://arxiv.org/abs/2607.01651"
venue: "ECCV 2026"
venue_short: "ECCV"
arxiv_url: "https://arxiv.org/abs/2607.01651"
arxiv_doi: "10.48550/arXiv.2607.01651"
pdf_url: "https://arxiv.org/pdf/2607.01651v1"
project: "https://autoserl.github.io/"
code: "https://github.com/autoserl/AutoSERL"
openalex: 
metadata_source: "arxiv + official project/repository"
metadata_confidence: high
pdf: "[[papers/pdfs/liu2026one-demonstration-enough-real.pdf]]"
reading: "[[papers/bilingual/liu2026one-demonstration-enough-real_中英混读.md]]"
images: "papers/images/liu2026one-demonstration-enough-real/"
image_index: "[[papers/images/liu2026one-demonstration-enough-real/index.md]]"
map_axis: "具身智能/RL/真实机器人HiL"
map_brief: "把一条示范轨迹改造成 SERL 的自动干预器，用滑动窗口纠偏、卡死恢复和干预终止减少真机 RL 的持续人工接管。"
map_role: "研究如何用单示范的几何轨迹先验替代 HIL-SERL 持续动作纠偏的入口。"
authors:
  - "[[Yuwan Liu]]"
  - "[[Hongze Yu]]"
  - "[[Song Liu]]"
  - "[[Yuhan Wang]]"
  - "[[Junge Zhang]]"
  - "[[Yaodong Yang]]"
  - "[[Yuanpei Chen]]"
  - "[[Ceyao Zhang]]"
institutions:
  - "[[Institute of Automation, Chinese Academy of Sciences]]"
  - "[[Beijing Academy of Artificial Intelligence]]"
  - "[[PKU-PsiBot Joint Lab]]"
  - "[[University of Chinese Academy of Sciences]]"
  - "[[Peking University]]"
topics:
  - real-world reinforcement learning
  - one-shot learning
  - automatic intervention
  - contact-rich manipulation
  - SERL
  - HIL-SERL
  - trajectory guidance
  - safety recovery
  - intervention termination
---

# One Demonstration Is Enough for Real-World Robotic Reinforcement Learning

- [x] PDF:: [[papers/pdfs/liu2026one-demonstration-enough-real.pdf]]
- [x] 元数据:: source=arxiv + official project/repository, confidence=high
- [x] 精读稿:: [[papers/bilingual/liu2026one-demonstration-enough-real_中英混读.md]]
- [x] 图片索引:: [[papers/images/liu2026one-demonstration-enough-real/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[real-world reinforcement learning]], [[automatic intervention]], [[one-shot learning]], [[SERL]], [[HIL-SERL]], [[@deng2026e2hil]], [[@luo2024precise-dexterous-robotic-manipulation]], [[@dodeja2026q2rl]]
affiliation:: [[Institute of Automation, Chinese Academy of Sciences]], [[Beijing Academy of Artificial Intelligence]], [[PKU-PsiBot Joint Lab]], [[University of Chinese Academy of Sciences]], [[Peking University]]

## Abstract

Learning effective robot control policies on physical hardware is challenging due to costly data collection and the difficulty of reward specification. Prior work has incorporated demonstrations into reinforcement learning (RL), yet existing approaches either require large numbers of demonstrations or depend on continuous human intervention during training. To address these limitations, we present AutoSERL, a framework that leverages a single demonstration to fully automate the intervention process in real-world robot RL. The framework includes three complementary mechanisms to accomplish certain tasks: a sliding window intervention mechanism that continuously guides exploration to prevent local optima and unsafe deviations, a safety recovery mechanism that detects and corrects failure states via predefined trajectory recovery points, and an intervention termination criterion that automatically disables guidance once the policy can independently complete the task, preserving its exploration advantage. We evaluate AutoSERL on six contact-intensive manipulation tasks across two robot platforms, spanning insertion, hanging, and hinge-based tasks. AutoSERL consistently outperforms SERL initialized with 20 demonstrations, behavior cloning, and MILES -- a dedicated one-shot imitation learning baseline -- across all tasks while matching HIL-SERL, achieves 100% success rate on insertion tasks, and demonstrates improved robustness to positional variations, all from a single demonstration. Code and videos are available on our project website: https://autoserl.github.io/.

## 一句话定位

AutoSERL 没有从单条示范直接学出完整策略，而是把示范的 6D 末端轨迹变成 SERL 训练期间的几何护栏，在偏离、卡死和过度依赖护栏这三类节点上自动纠偏，试图用一次任务设置替代 HIL-SERL 的持续人工动作接管。

## 方法 / 对象

训练前为每个任务采一条示范，并在轨迹上指定安全回退点 `recover_point0` 与稳定接触点 `recover_point1`。Sliding Window Intervention（滑动窗口干预）持续寻找当前末端位姿前方的最近示范点，偏差超过 $th_2$ 且方向夹角不超过 $90^\circ$ 时，用 motion planning（运动规划）拉回轨迹附近。Safety Recovery（安全恢复）监测最近 $l_{stag}$ 步的轨迹进度，确认卡死后先回到安全点，再重放稳定接触段。Intervention Termination（干预终止）在一次成功 episode 的干预步数低于 $l_{term}$ 后永久关闭后续自动干预，让策略继续自主探索。

底层学习器沿用 SERL / RLPD。输入是双相机 RGB 与 proprioception（本体状态），输出为 6D delta end-effector pose（末端位姿增量）。六项任务覆盖插头与 USB 插入、衣架与修正带与勺子悬挂、用钩子拉抽屉，平台为 Franka 与 UR5。

## 证据

固定场景下每项任务评测 50 次。AutoSERL 六项均为 50/50，同训练时长的 SERL 依次为 20/50、0/50、0/50、6/50、0/50、0/50。相对 HIL-SERL 达到 50/50 所需时间，AutoSERL 在六项里的五项更快或持平，平均约 25.7 分钟，HIL-SERL 约 39.5 分钟，USB 插入是唯一更慢的一项。

Table 3 中 BC 六项平均成功率约 39%，MILES 约 26%，AutoSERL 为 100%。Fig. 7 的消融还揭示三件事。去掉滑动窗口会延迟收敛，保留滑动窗口却去掉恢复机制可能比 SERL 更差，持续不终止干预会在抽屉任务上后期退化。用长度 99 的非最优插头示范训练后，首个 50/50 checkpoint 的 rollout 只有 54 步，支持策略并非逐点复刻示范。

## 局限

标题里的 one demonstration 指每个任务各一条，不是一条示范迁移到六个任务。方法仍要为新任务指定两个恢复点、四个启发式超参数、运动规划与二值稀疏奖励。论文明确写明奖励由人工标注，官方代码也把 SpaceMouse 按键写入 reward，因此自动化的是动作干预，不是整段训练的人力闭环。

所有任务都属于手持物体与单一目标交互，动作空间限定为 6D 末端位姿增量。主表在固定场景中评测，位置扰动只测插头任务。五随机种子也只测插头，而且 Fig. 6(a) 在 12k steps 仍有一个 seed 约 10% success、阴影方差很大，与正文所说各 seed 接近 100% 且低方差并不一致。主结果没有跨 seed 置信区间，50/50 也不能当作总体成功率精确等于 100%。

复现材料仍不完整。官方仓库提供核心 wrapper 与插头配置，但未提供其余五个任务配置、六任务示范、checkpoint 或数据。2026-08-26 检查的 main 分支在 recovery slice 中还出现 list 与 integer 相加的可疑表达式，若执行到该分支可能触发 `TypeError`，需要作者确认或修正。

## 我的阅读笔记

这篇最有价值的部分不是 one-shot imitation，而是把一条示范拆成三种训练期控制信号。几何护栏负责把探索留在有效走廊，恢复段负责处理护栏自身会带来的失败状态，终止条件再把探索权交回 RL。Fig. 7 说到点子上了，只有前两项会制造依赖，只有恢复没有前向引导也不够，三者是一组相互制约的系统设计。

需要保留的判断也很明确。AutoSERL 把持续 teleoperation（遥操作）成本换成了 per-task engineering（逐任务工程设置），并没有消除人工知识。它更像 trajectory-conditioned safety curriculum（轨迹条件安全课程），而不是通用的单示范机器人学习算法。适合与 [[@luo2024precise-dexterous-robotic-manipulation]] 和 [[@deng2026e2hil]] 并读，前者让人持续给纠正，后者筛选哪些纠正值得学习，AutoSERL 则试图把纠正策略本身写成可执行规则。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
