---
tags:
  - paper
status: unread
aliases:
  - "TACO: TActile World Model as a Self-COrrector for Scalable VLA Post-Training"
year: 2026
title: "TACO: TActile World Model as a Self-COrrector for Scalable VLA Post-Training"
doi: 
arxiv: "2607.02840"
url: "https://arxiv.org/abs/2607.02840"
venue: 
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/liu2026taco-tactile-self-corrector.pdf]]"
reading: "[[papers/bilingual/liu2026taco-tactile-self-corrector_中英混读.md]]"
images: "papers/images/liu2026taco-tactile-self-corrector/"
image_index: "[[papers/images/liu2026taco-tactile-self-corrector/index.md]]"
authors:
  - "[[Shengbang Liu]]"
  - "[[Yueru Jia]]"
  - "[[Yuyang Yan]]"
  - "[[Jiaming Liu]]"
  - "[[Xinran Zhang]]"
  - "[[Qiuxuan Feng]]"
  - "[[Yandong Guo]]"
  - "[[Shiji Zhou]]"
  - "[[Boxin Shi]]"
  - "[[Shanghang Zhang]]"
institutions:
topics:
---

# TACO: TActile World Model as a Self-COrrector for Scalable VLA Post-Training

- [ ] PDF:: [[papers/pdfs/liu2026taco-tactile-self-corrector.pdf]]
- [ ] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/liu2026taco-tactile-self-corrector_中英混读.md]]
- [ ] 地图维护:: 已加入 [[论文地图]] 快速索引后，运行 `python setting/scripts/check_paper_map.py --sync-reading-markers`
- [ ] 阅读状态:: unread

related:: [[@wu2026tactile-wam]], [[@pan2026vla-corrector-lightweight-detect]], [[@intelligence2026pi07-steerable-generalist-robotic]], [[@liu2026last0-latent-spatio-temporal]], [[@qian2026wam-rl]]
affiliation:: 北京大学（多媒体信息处理国家重点实验室，通讯 [[Shanghang Zhang]]）· AI² Robotics · 中山大学 · 北京航空航天大学；Project Page: https://taco-wm.github.io/

## Abstract

Vision-Language-Action (VLA) models have shown promising generalization in robotic manipulation, but they still struggle with contact-rich tasks, where minor contact perturbations can cause unrecoverable failures that are hard to detect from vision alone. Since these failures are localized rather than task-level semantic errors, tactile-aware corrective post-training offers an efficient way to improve recovery. However, scaling such supervision through human intervention is costly. Recent works have explored world models to synthesize imagined rollouts for policy improvement, but vision-only world models may produce visually plausible yet contact-inconsistent trajectories. We therefore introduce TACO, a tactile-aware world-model-driven framework for scalable VLA post-training in contact-rich manipulation. Given real robot rollouts, TACO follows a Recognize-Imagine-Label loop with a tactile-aware world model: a unified progress-action model recognizes failure-adjacent states using progress estimates, a visuo-tactile generation model imagines local correction segments, and the progress-action model labels them with executable corrective actions. To incorporate tactile corrective supervision into VLA post-training, TACO combines knowledge-insulated tactile adaptation with advantage-conditioned training, enabling the policy to learn from imagined corrections without degrading pretrained visual-language priors. These components enable TACO to convert real-world failures into imagined visuo-tactile corrections for iterative VLA post-training. Experiments on real-world contact-rich manipulation tasks show that TACO achieves 44% absolute success rate improvement over the base policy and 32% over the policy without knowledge-insulated tactile adaptation.

## 一句话定位

TACO 把一个 **visuo-tactile world model** 当作**离线的"自纠错"数据引擎**：在真实 rollout 里以"进度停滞/下降"的 failure-adjacent 状态为锚点，让世界模型联合去噪出"未来视频 + 力"的局部纠正片段，再用统一 progress-action 模型把它标成可执行动作 + 二元 advantage 标签，喂给 VLA 迭代后训练。目标是在**不做重复人工干预**、也**不损坏预训练视觉-语言先验**的前提下，专门修复 contact-rich 任务里"视觉看不见的**局部接触失败**"（滑移、力不足、异常扭矩），而非语义错误。

## 方法 / 对象

- **对象**：contact-rich manipulation；失败被明确重定义为 *localized contact failure*——"policy 知道要做什么，但接触突变后无法恢复"。
- **世界模型**：Visuo-Tactile Generation Model（**Wan2.2-TI2V-5B** backbone，联合去噪未来视频 + 12 维力，**temporal RoPE 对齐** + **first-frame force anchoring** $F_0$）＋ Unified Progress-Action Model（**DINOv2** 视觉路径 + **MLP** 触觉路径双路融合，输出动作 $\hat a\in\mathbb R^7$ 与进度 $\hat p\in[0,1]$）。
- **Recognize–Imagine–Label 闭环**：进度停滞/下降处选锚点 $p_{t+\Delta}-p_t<\epsilon$ → 从锚点联合去噪 **T=49** 步局部纠正片段 → 标成动作 + 二元 advantage（1=有效纠正 / 0=初始失败）。
- **后训练**：**Knowledge-Insulated tactile adaptation**（对预训练 VLM backbone 施 stop-gradient，力历史 + 优势只经 **adaRMSNorm** 注入 action expert）＋ **advantage-conditioned training**（CFG；推理用正优势条件引导高进度恢复）。base policy = **π₀.₅**，形成 real→imagine→real 闭环。

## 证据

- 6 个真实接触任务（**Franka Research 3** + 前视 **Intel RealSense D455** + 双 **Xense** 6D 触觉），每任务 50 条 SpaceMouse 遥操作示教、40 集评测、跑 **2 轮**后训练。
- **Table 1**：2 轮后平均成功率 **0.38 → 0.82（+44 个百分点** vs base）；vs Filtered BC 0.43（+39）、vs TACO 无 KI 0.50（+32）；完成步数 185.5 → 127.7（执行更平滑）。
- **消融（Fig.5）**：去掉触觉*生成* → **0.28**（比 base 还差），去掉触觉*标注* → **0.65**，完整 → **0.82**；缩放 Insert Flower 真实:想象 = 1:2 / 1:4 / 1:8 → **70% / 93% / 97%**。
- **泛化（Fig.7，Wipe Whiteboard，仅 1 轮 OOD 想象）**：未见背景 25.5→76.0、未见物体 30.0→82.5、未见位置 12.5→45.0（%）。

## 局限

- 想象纠正是**离线**生成、非部署时**在线**；主打**局部接触失败**，不解决长时程/语义错误。作者列的未来方向：online correction generation + 世界模型与策略更紧耦合。
- （阅读补充）**Filtered BC 增益很小**（0.43），说明"筛选成功轨迹"里没有 recovery 行为、只是强化窄示教流形——TACO 的增益关键在"**想象出示教里根本不存在的恢复片段**"（Fig.6 动作分布随迭代变宽可佐证）。
- 触觉监督为 12 维 force-torque，非视觉触觉图像；仅单臂 + 6 任务，v1 无附录数据集清单（正文只说 "broad robot trajectories"，未点名 DROID/AgiBot 等）。

## 我的阅读笔记

- 与 [[@wu2026tactile-wam]]（Tactile-WAM）是最直接的**姊妹篇**：二者都承认"朴素塞触觉会坏事"，但解法层次不同——Tactile-WAM 改**架构**（一个 WAM 内部用非对称注意力 VideoClean 防 *tactile pollution*），TACO 改**训练管线**（世界模型当**外部纠正数据工厂** + knowledge-insulation 用 stop-gradient/adaRMSNorm 保护 VLM 先验）。
- 机制新意 = 把"自改进的数据"来源换成"世界模型想象出的、**示教里不存在的局部恢复片段**"，并只把触觉/优势喂给 action expert。完整交叉对照与可追问点见精读稿 `与当前库的连接` / `局限与可追问点`。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
