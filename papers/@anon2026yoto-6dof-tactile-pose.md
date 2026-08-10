---
tags:
  - paper
status: unread
aliases:
  - "You Only Touch Once: 6-DoF Object Pose Estimation from Single Tactile Contact"
year: 2026
title: "You Only Touch Once: 6-DoF Object Pose Estimation from Single Tactile Contact"
doi: 
arxiv: 
url: 
venue: "CoRL 2026 (under review)"
openalex: 
metadata_source: pdf
metadata_confidence: medium
pdf: "[[papers/pdfs/anon2026yoto-6dof-tactile-pose.pdf]]"
reading: "[[papers/bilingual/anon2026yoto-6dof-tactile-pose_中英混读.md]]"
images: "papers/images/anon2026yoto-6dof-tactile-pose/"
image_index: "[[papers/images/anon2026yoto-6dof-tactile-pose/index.md]]"
authors:
  - "[[Anonymous (CoRL 2026 under review)]]"
institutions:
topics:
---

# You Only Touch Once: 6-DoF Object Pose Estimation from Single Tactile Contact

- [ ] PDF:: [[papers/pdfs/anon2026yoto-6dof-tactile-pose.pdf]]
- [ ] 元数据:: source=pdf, confidence=medium
- [x] 精读稿:: [[papers/bilingual/anon2026yoto-6dof-tactile-pose_中英混读.md]]
- [ ] 地图维护:: 已加入 [[论文地图]] 快速索引后，运行 `python setting/scripts/check_paper_map.py --sync-reading-markers`
- [ ] 阅读状态:: unread

related:: [[@wu2026tactile-wam]], [[@liu2026taco-tactile-self-corrector]], [[@park2026tactx-learning-shared-tactile]], [[@bi2026heterogeneous-tactile-transformer]]
affiliation:: 匿名投稿（CoRL 2026 under review，"Do not distribute"）；作者自称基于其 prior work InvariantCloud [31]（arXiv:2605.25216, 2026，用于把 GelSight 接触重建成点云）

## Abstract

Accurate 6-DoF object pose estimation is fundamental to robotic manipulation, yet vision-based methods often fail under occlusion, poor lighting, and reflective or transparent surfaces. We present YOTO, a tactile-only pose estimation system that recovers the full 6-DoF object pose from a single pair of simultaneous contacts, without requiring contact history. YOTO represents each tactile contact as a local 3D point cloud and localizes it on the object surface through a coarse-to-fine network. The two localized contacts, together with the calibrated sensor poses, are then fed to a closed-form normal-aware SVD solver that recovers the full 6-DoF object pose in one step. To reduce real-data requirements, the localization network is pretrained on virtual tactile patches sampled from the object model and fine-tuned with a small number of real contacts. We further show that YOTO can operate on object models reconstructed from consumer-grade mobile scans, and quantify the gap relative to CAD-based models. Experiments on four geometrically diverse objects demonstrate accurate tactile contact localization and pose estimation, outperforming vision-based and tactile/geometric baselines, especially when visual perception is unreliable.

## 一句话定位

YOTO 用一对双 GelSight 传感器**单次同时接触**、不依赖接触历史 / 物体运动 / 视觉，就**一步**恢复物体的**绝对 6-DoF 位姿**。做法是把每个触点表示成局部 3D 点云，在物体表面的 block 分解上做粗到精定位，再把两个触点 + kNN 聚合法向 + 标定的传感器位姿喂给一个 **normal-aware 闭式 SVD 解算器**解出 $\mathrm{SE}(3)$ 位姿。靶心是视觉位姿估计失效的场景——遮挡（夹爪/手挡住物体）、弱光、反光/透明表面。

## 方法 / 对象

- **对象**：contact-rich 操作里的 6-DoF 位姿估计；视觉在被遮挡、弱光、反光透明时失效，触觉只在接触点观测几何、天然鲁棒，但有"**局部歧义**"（同一小块表面几何在物体多处重复），且单帧接触信息稀疏。
- **三段式（Fig.2）**：① 表面表示 + 虚拟接触生成——CAD 或**消费级扫描 mesh** 采成 parent 点云 $\mathcal P$，按主轴切成 surface blocks $\{\mathcal B_i\}$；从 $\mathcal P$ 局部邻域采虚拟触觉 patch 作监督。② 粗到精定位网络（Fig.3）——双权重共享点云编码器（coords + normals），coarse 用余弦相似度 $a_i=\tau\,\frac{q_s^\top b_i}{\|q_s\|\|b_i\|}$ 选 block、retrieve top-K，fine head 回归 offset + confidence $\gamma$，取 $\arg\max_k(a_{i_k}+\gamma_{s,k})$；再 kNN（k=20）聚合触点法向 $\hat n_s^O$。③ normal-aware dual-contact SVD——两触点只定 contact-to-contact 轴、绕轴旋转有歧义 → 引入法向组 $Q^O=[d^O,\hat n_L^O,\hat n_R^O]$、$Q^W=[d^W,n_L^W,n_R^W]$，正交 Procrustes 闭式解 $\hat R$，再对齐平移 $\hat t$。
- **两阶段训练**：Stage1 虚拟预训练（block 分类 CE + top-K margin + smooth-ℓ1 offset），Stage2 虚拟 + 少量真实 GelSight 微调（真实样本权重更大，跨 sim-to-real gap）。

## 证据

- 4 个几何各异物体（drill / squirrel / monkey / avocado），双 6-DoF **AIRBOT Play** 臂各持一枚 **GelSight Mini**，**OptiTrack** 提供 GT（仅评测）；接触经作者 prior 的 **InvariantCloud** 管线转成点云。基线：几何 **ICP**（触觉下界）+ **FoundationPose**（视觉代表）。
- **定位误差（Table 1）**：YOTO（扫描 mesh）全物体均值 **4.78 mm**（<1cm），ICP 52.81 mm；去掉真实微调误差涨 5 倍（24.65 mm）；**扫描 mesh ≈ 甚至略优于 CAD mesh（4.78 vs 5.45）**——因扫描 mesh 隐含了 GelSight 真实能感知的 3D 打印层纹/粗糙度。
- **遮挡下位姿（Table 2）**：clear 时 YOTO 全面优于 FoundationPose；**occluded 时 FoundationPose 平移涨 15.1×、旋转涨 15.7×（→ 82.93 mm / 85.57°），YOTO 几乎不变（3.52 mm / 3.56°）**——因触觉与标定传感器位姿都不依赖相机。
- **动态追踪（Table 3 / Fig.4）**：单次接触、开环追踪 ~100 mm / 10–15° 轨迹，平移 <7 mm、旋转 <8°；峰值有界不发散，settle 后是可预测的塑性 grasp drift（1–3 mm / 1–2°）。

## 局限

- 仍需**每物体**用少量真实 GelSight（20 个）微调；完全 sample-free 部署是 future work。
- **SVD 在 near-coaxial 抓取上退化**（旋转对称物体如 drill 不可避免——drill 定位最好、位姿反而最难，因长轴近共轴使绕轴旋转欠约束）。
- 动态追踪依赖 rigid-grasp 假设，长时操作累积塑性漂移；运动中快速 re-touch 可缓解。
- （阅读补充）Table 3 首列写作 "Rabbit"（3.5 mm / 6.1°），与其余表的 "Squirrel"（Fig.4 = 3.52 mm / 6.05°）应为同一物体，论文命名不一致。

## 我的阅读笔记

- 与库里其它触觉论文是**互补的另一层**：[[@wu2026tactile-wam]] / [[@liu2026taco-tactile-self-corrector]] 是"触觉进入 world/action model 做**决策/纠错**"，YOTO 是"纯触觉做**感知**（位姿估计）"——它产出一个 $\mathrm{SE}(3)$ 观测，恰好能作为上游状态喂给那类策略。
- 方法上最漂亮的是把 **learned localization** 与 **analytic SVD** 解耦：网络只解决"这个 patch 在物体表面哪里"（几何检索），位姿由闭式解一步给出——避开端到端回归 6-DoF 的不稳定，也让**法向成为消除绕轴歧义的关键**。完整对照与追问见精读稿。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
