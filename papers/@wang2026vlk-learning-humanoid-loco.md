---
tags:
  - paper
status: read
aliases:
  - "VLK: Learning Humanoid Loco-Manipulation from Synthetic Interactions in Reconstructed Scenes"
year: 2026
title: "VLK: Learning Humanoid Loco-Manipulation from Synthetic Interactions in Reconstructed Scenes"
doi: 
arxiv: "2606.30645v1"
url: "https://arxiv.org/abs/2606.30645"
venue: 
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/wang2026vlk-learning-humanoid-loco.pdf]]"
reading: "[[papers/bilingual/wang2026vlk-learning-humanoid-loco_中英混读.md]]"
images: "papers/images/wang2026vlk-learning-humanoid-loco/"
image_index: "[[papers/images/wang2026vlk-learning-humanoid-loco/index.md]]"
authors:
  - "[[Yen-Jen Wang]]"
  - "[[Jiaman Li]]"
  - "[[Sirui Chen]]"
  - "[[Takara E. Truong]]"
  - "[[Pei Xu]]"
  - "[[Pieter Abbeel]]"
  - "[[Rocky Duan]]"
  - "[[Koushil Sreenath]]"
  - "[[Angjoo Kanazawa]]"
  - "[[Carmelo Sferrazza]]"
  - "[[Guanya Shi]]"
  - "[[Karen Liu]]"
institutions:
topics:
---

# VLK: Learning Humanoid Loco-Manipulation from Synthetic Interactions in Reconstructed Scenes

- [x] PDF:: [[papers/pdfs/wang2026vlk-learning-humanoid-loco.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/wang2026vlk-learning-humanoid-loco_中英混读.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，`#map/具身智能/人形/重建场景合成数据与Loco-Manipulation`
- [x] 阅读状态:: read

related::
affiliation::

## Abstract

Perception-based humanoid loco-manipulation requires connecting egocentric observations and task instructions to whole-body motion. Learning this mapping requires synchronized egocentric images, language commands, and robot-compatible kinematic trajectories, yet no existing data source provides this complete tuple at scale. We address this bottleneck by generating vision-language-kinematics (VLK) supervision synthetically in reconstructed scenes. Our pipeline leverages 3D Gaussian Splatting to reconstruct metric-scale indoor environments, synthesizes navigation and object-interaction trajectories using privileged scene information, and renders paired egocentric observations after the fact. We produce 48,000 paired trajectories with no human intervention and train a VLK policy that predicts short-horizon whole-body kinematic trajectories. A whole-body tracker converts these predictions into actions on the physical humanoid. We evaluate on the physical Unitree G1 performing navigation and single-object transport, demonstrating that synthesized interactions in reconstructed scenes provide effective supervision for sim-to-real perception-based humanoid loco-manipulation. Project Website: https://vision-language-kinematics.github.io/

## 一句话定位

在重建的真实场景里合成 (视觉,语言,全身运动学) 配对监督，突破人形移动操作“三元组无处可得”的瓶颈，免遥操训练出可真机零样本部署的 VLK 策略。

## 方法 / 对象

3DGS 重建度量尺度室内场景 + 标注语义包围盒/可行走区域；用特权信息 + 条件扩散合成 G1 导航（BONES-SEED）与物体交互（OMOMO→OmniRetarget）轨迹；Isaac Sim 事后渲染第一人称观测（域随机化）。从 π0.5 微调得 VLK 策略（图像+指令+状态→未来全身运动学 + 手腕接触标签，flow matching x0-预测），SceneBot 接触感知 tracker 转成 G1 关节动作。

## 证据

600 GPU-h 产 48k 配对轨迹/环境。真机 G1 导航/楼层搬运高成功、桌面级较弱（Table 1）；无接触标签 Pick(Floor) 真机 0/5；数据量消融 Pick(Surface) 0%@10%→46%@100%（Fig 4）；域随机化 41%→90% 走路成功（Table 2）。

## 局限

交互合成受 OMOMO 覆盖限制，偏大物体（箱体）双手搬运，不解决小物体精确抓取；tracker 靠手腕接触稳定大物体；仅 2 场景、G1 单本体验证。详见精读稿矩阵。

## 我的阅读笔记


```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
