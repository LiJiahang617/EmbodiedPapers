---
tags:
  - paper
status: unread
aliases:
  - Qwen-RobotManip
  - Qwen RobotManip
  - "Qwen-RobotManip Technical Report"
  - "Qwen-RobotManip Technical Report: Alignment Unlocks Scale for Robotic Manipulation Foundation Models"
year: 2026
title: "Qwen-RobotManip Technical Report: Alignment Unlocks Scale for Robotic Manipulation Foundation Models"
doi: "10.48550/arXiv.2606.17846"
url: "https://arxiv.org/abs/2606.17846"
venue: "arXiv preprint"
venue_short: "arXiv"
arxiv: "2606.17846v2"
arxiv_url: "https://arxiv.org/abs/2606.17846"
arxiv_doi: "10.48550/arXiv.2606.17846"
pdf_url: "https://arxiv.org/pdf/2606.17846v2"
blog: "https://qwen.ai/blog?id=qwen-robotmanip"
code: "https://github.com/QwenLM/Qwen-RobotManip"
pdf: "[[papers/pdfs/Qwen-RobotManip Technical Report Alignment Unlocks Scale for Robotic Manipulation Foundation Models.pdf]]"
reading: "[[papers/bilingual/qwen2026robotmanip_中英混读.md]]"
images: "papers/images/qwen2026robotmanip/"
image_index: "[[papers/images/qwen2026robotmanip/index.md]]"
map_axis: "具身智能/VLA/跨本体对齐与规模化预训练"
map_brief: "用 canonical state-action、camera-frame delta EEF、in-context policy adaptation 把多本体操作数据对齐后规模化到约 38,100 小时。"
map_role: "VLA scaling 与 cross-embodiment alignment 的核心技术报告。"
authors:
  - "[[Qwen Team]]"
  - "[[Haoqi Yuan]]"
  - "[[Zhixuan Liang]]"
  - "[[Anzhe Chen]]"
  - "[[Ye Wang]]"
  - "[[Haoyang Li]]"
  - "[[Pei Lin]]"
  - "[[Yiyang Huang]]"
  - "[[Zixing Lei]]"
  - "[[Tong Zhang]]"
  - "[[Chenfei Wu]]"
  - "[[Xiong-Hui Chen]]"
institutions:
  - "[[Qwen Team]]"
topics:
  - vision-language-action
  - robotic manipulation foundation model
  - cross-embodiment alignment
  - camera-frame end-effector action
  - human-to-robot synthesis
  - egocentric video
  - flow matching
  - Qwen-VL
  - OOD evaluation
  - RoboTwin-IF
  - RoboTwin-XE
---

# Qwen-RobotManip Technical Report: Alignment Unlocks Scale for Robotic Manipulation Foundation Models

- [x] PDF:: [[papers/pdfs/Qwen-RobotManip Technical Report Alignment Unlocks Scale for Robotic Manipulation Foundation Models.pdf]]
- [x] 代码:: [QwenLM/Qwen-RobotManip](https://github.com/QwenLM/Qwen-RobotManip)
- [x] 博客:: [qwen.ai/blog?id=qwen-robotmanip](https://qwen.ai/blog?id=qwen-robotmanip)
- [x] 精读稿:: [[papers/bilingual/qwen2026robotmanip_中英混读.md]]
- [x] 图片索引:: [[papers/images/qwen2026robotmanip/index.md]]
- [x] 论文地图:: [[论文地图]]
- [ ] 阅读状态:: unread

related:: [[vision-language-action]], [[cross-embodiment]], [[robot manipulation]], [[@tencent2026hy-embodied-05]], [[@lin2026physbrain]], [[@xu2026egoguide]], [[@tang2026frs]], [[@kim2026serf]], [[@zhang2026contactworld]]
affiliation:: [[Qwen Team]]

## 一句话问题

机器人操作数据不像文本那样天然同构：不同 robot embodiment、state/action 表示、坐标系、采集质量和任务分布会互相冲突；Qwen-RobotManip 的核心问题是如何先把 representation、motion 和 behavior 对齐，再让约 38,100 小时多源操作数据真正产生 scaling，而不是噪声叠加。

## 方法

- 数据规模：约 38,100 小时 manipulation pretraining corpus，其中真实/仿真 robot data 约 11,420 小时，egocentric human videos 约 1,933 小时，human-to-robot synthesized data 约 24,808 小时；另有约 28M vision-language co-training 数据。
- Human-to-Robot synthesis：从 EgoDex、VITRA、EgoVerse 的人手轨迹出发，经 hand retargeting、SAM3 hand segmentation、ProPainter inpainting、base pose search、MuJoCo IK 和 depth-guided compositing，把人类第一视角操作渲染成 15 种双臂机器人形态。
- 数据清洗：五阶段 state/action 过滤，包括 sudden change、state-action trend alignment、extreme value、FK consistency、base/end-effector orientation alignment；再用 instruction consistency、video-state consistency 和 video quality checks 做跨模态质量控制。
- 架构：Qwen3.5-4B VLM backbone + flow-matching Diffusion Transformer action expert；VLM 负责多视角视觉和语言语义，DiT 负责连续 action chunk 生成。
- Representation alignment：把不同机器人统一到 80 维 canonical state/action vector，每只手臂 29 维，含 joint、EEF pose、gripper、dexterous hand slots，缺失维度用 binary mask 排除 loss。
- Motion alignment：end-effector action 采用 camera-frame delta pose，使视觉上相似的动作在数值空间也相近；配合 Camera Positional Encoding 和 end-effector type embedding。
- Behavior alignment：structured embodiment prompt 提供 robot、instruction、speed、fps、camera view direction；in-context policy adaptation 用同 episode 历史 observation-state-action chunks 作为隐式 embodiment/kinematic signature。
- 训练：pretraining 用 VLA stream 与 VLM stream dual-stream co-training，robot:VL 约 9:1；VLA 用 masked flow matching loss，VLM 用 next-token loss；SFT 阶段主要做 domain-specific generalist fine-tuning。

## 证据

- 标准 IID benchmark 不能说明 pretraining 质量：StarVLA、scratch model 在 LIBERO/RoboTwin 上可接近或超过 pretrained model；但到 LIBERO-Plus、RoboTwin-Clean2Rand 后差距明显拉开。
- OOD task/scene generalization：Qwen-RobotManip-Context 在 LIBERO-Plus 达 91.4%，RoboTwin-C2R Hard 达 69.4%；Qwen-RobotManip 在 EBench 为 45.6% SR / 60 score，RoboCasa365 total 为 35.9%。
- Instruction following：RoboTwin-IF 平均 72.2%，高于 π0.5 的 49.6%，尤其在 Pick-Diverse、Place-Relative、Operate-Mic-Drawer、Operate-Tabletop 上差距大。
- Cross-embodiment transfer：RoboTwin-XE 中，AgileX 训练后零样本迁移到 ARX/UR5/Franka，camera-frame EEF 平均 23.9%，高于 joint control 14.5%，也高于 π0.5 EEF 7.5%。
- Real-world CobotMagic ALOHA：ID 7 任务平均 88.6%，π0.5 为 42.9%，StarVLA 为 20.0%；OOD 4 任务平均 87.5%，π0.5 为 37.5%，StarVLA 为 0.0%。
- Real-world ARX few-shot：130 条 teleop demonstrations 下，Put Blocks、Fold Towel、Unscrew Cap 等任务均优于 π0.5；cross-embodiment skill transfer 中 full model 55.0%，w/o UnifiedEEF 12.5%，w/o UnifiedSpace 7.5%。
- RoboChallenge Table30-v1 generalist track：总成功率 45%、process score 59.83，超过 DM0_generalist 的 37% / 48.43，并在 bimanual coordination、pick-and-place 和 retry behavior 上有案例优势。
- Ablation：无 unified action space 时 scaling 曲线不稳定；Human-to-Robot 数据在 RoboTwin-C2R Hard 从 robot-only 54.7 提到 58.7；去掉 VL co-training 在 RT-C2R Hard 从 62.6 降到 54.4、RT-IF 从 71.6 降到 64.6。

## 局限

- Human-to-Robot synthesis 依赖 retargeting、inpainting、depth compositing，仍会引入视觉和动力学 distribution gap。
- 大量 OOD 结果仍是 simulation-based；真实机器人虽覆盖 ALOHA、ARX、UR、Franka 等平台，但规模和公开可复现性仍有限。
- 模型报告的很多数据处理、VLM annotation、过滤细节和完整训练混合比例不容易复现；工程基础设施门槛高。
- In-context variant 有启动阶段 zero-padded history 导致 hesitation 的现实问题；更高 denoising steps 提高效果但增加推理成本。
- 固定 action chunk length 与远程推理 latency 会限制 sub-second reactive control、快速接触调整和高频动态任务。
- Camera-frame EEF 依赖相机内外参；校准误差、相机遮挡或多相机 reference selection 错误会直接影响 action representation。

## 我的阅读笔记

这篇是当前 VLA scaling 路线里很值得回看的系统报告。它的主张不是“模型更大自然更好”，而是“alignment 是 scaling 的前置条件”：如果不同机器人数据没有共享语义槽位、共享 motion reference frame 和可读的 embodiment/context signal，增加数据只会让模型学习互相冲突的 convention。

最值得借鉴的三个设计是：第一，80 维 canonical state-action + mask，把异构本体问题变成“哪些语义槽位有效”；第二，camera-frame delta EEF，把动作坐标系从 robot-specific base frame 拉回视觉坐标系；第三，VLM/VLA dual-stream co-training，避免 VLA SFT 后退化成忽略语言的 vision-action matcher。

和 [[@tencent2026hy-embodied-05]] 相比，HY-Embodied 更像“VLA 之前的 embodied VLM brain”，而 Qwen-RobotManip 更直接地进入 action representation、robot data scaling 和 OOD/real-world evaluation。和 [[@lin2026physbrain]]、[[@xu2026egoguide]] 的 human egocentric data 思路相比，这篇把人类第一视角视频进一步合成为 15 种机器人形态，是更激进的数据扩增方案。

后续阅读时应重点追问三件事：一是 camera-frame EEF 在真实相机标定误差下有多稳；二是 H2R synthetic data 的边际收益是否会随着真实 robot data 扩张而降低；三是 RoboTwin-IF/XE 这类 benchmark 是否会成为比 LIBERO/RoboTwin IID 更可信的 VLA foundation model 评价标准。

## 摘录
