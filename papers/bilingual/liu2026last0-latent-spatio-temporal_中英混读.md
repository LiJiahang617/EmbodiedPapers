---
tags:
  - bilingual-reading
paper: "[[@liu2026last0-latent-spatio-temporal]]"
source_pdf: "[[papers/pdfs/liu2026last0-latent-spatio-temporal.pdf]]"
images: "papers/images/liu2026last0-latent-spatio-temporal/"
image_index: "[[papers/images/liu2026last0-latent-spatio-temporal/index.md]]"
created: 2026-07-07
---

# LaST₀: Latent Spatio-Temporal Chain-of-Thought for Robotic Vision-Language-Action Model

paper:: [[@liu2026last0-latent-spatio-temporal]]
pdf:: [[papers/pdfs/liu2026last0-latent-spatio-temporal.pdf]]
images:: [[papers/images/liu2026last0-latent-spatio-temporal/index.md]]

> 单位：Peking University（Zhuoyang Liu, **Jiaming Liu** 共同一作；Shanghang Zhang 通讯）· CUHK · 北京人形机器人创新中心｜ ICML 2026 ｜ arXiv:2601.05248v4（2026-06）｜ 主页：https://vla-last0.github.io
> 备注：用户所说 "LAST-HD" 即本篇 **LaST₀**（下标 0）。

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| reason-before-act | 先思后行 | VLA 在动作前先做一步推理；本文用**潜空间**推理取代显式文本/图像推理。 |
| explicit CoT | 显式思维链 | 生成语言推理迹或未来图像；本文批评它慢且困于语言空间。 |
| Latent Spatio-Temporal CoT (LaST CoT) | 潜空间时空思维链 | 本文核心：在紧凑潜空间自回归预测未来多模态潜表示，跨时间保持一致。 |
| latent CoT space | 潜思维链空间 | token 高效，编码未来 2D 视觉/3D 几何/本体状态动态。 |
| 2D visual / 3D geometric / proprioception latent | 三类潜表示 | 分别由 SigLIP / Uni3D / action tokenizer 编码未来帧、点云、机器人状态。 |
| dual-system / Mixture-of-Transformers (MoT) | 双系统 / 混合 Transformer | 慢推理专家 + 快动作专家，共享自注意力，一个骨干内两套参数。 |
| slow reasoning expert | 慢推理专家 | 低频自回归合成 LaST CoT 潜表示，捕捉时空依赖。 |
| fast acting expert | 快动作专家 | 高频 flow matching 生成动作，条件于最近潜表示。 |
| asynchronous frequency (κ) | 异步频率 | 更新比 κ∈{2,4,8}：慢专家只在关键帧激活，快专家每步跑。 |
| flow matching | 流匹配 | 动作生成的连续生成式策略。 |
| Janus-Pro / DeepSeek-LLM 1.5B | 初始化骨干 | 两个专家都从同一预训练 VLM 初始化（24 层 decoder-only）。 |
| cosine similarity latent loss | 余弦潜损失 | 用方向对齐监督连续潜 CoT（而非离散 token 似然）。 |

## 摘要

VLA 模型泛化能力强，一些方法在执行前显式生成语言推理迹或预测未来观测。但**显式推理带来不可忽略的推理延迟**，限制了机器人操作所需的时间分辨率；而且推理**困在语言空间**，形成表示瓶颈，难以忠实捕捉难以言说的物理属性。为此本文提出 **LaST₀**：通过 **Latent Spatio-Temporal Chain-of-Thought (CoT)** 实现高效"先思后行"，捕捉难以言说的细粒度物理与机器人动态。具体地，引入 **token 高效的潜 CoT 空间**，建模未来视觉动态、3D 结构信息、机器人本体状态，并把这些表示**沿时间扩展**以形成时间一致的隐式推理轨迹。进一步，LaST₀ 采用 **Mixture-of-Transformers (MoT)** 的**双系统**架构：推理专家做低频潜推理，动作专家做高频动作生成；用异构操作频率训练，部署时可自适应切换。在跨越桌面、移动、灵巧手的 **10 个真实任务**上，LaST₀ 分别把平均成功率提升 **13% / 14% / 14%**（超过此前 SOTA）。

## 论文主线

一句话锚定：**把 VLA 的"先思后行"从缓慢、困在语言的显式 CoT，搬到一个紧凑、多模态、跨时间一致的潜空间；再用双系统 MoT 让慢推理与快动作异步协作，从而同时拿到"更强的物理推理"与"更快的实时控制"。**

![[papers/images/liu2026last0-latent-spatio-temporal/fig2_framework.png|780]]

**Figure 2 / 框架。** a) 双系统：**慢推理专家**（低频，取图像+文本，自回归构建 LaST CoT）与**快动作专家**（高频，flow matching 生成动作，条件于周期性更新的潜表示），二者通过 **Shared Attention with Latent CoT** 交互，源自同一 MoT 骨干。b) 潜时空空间：未来 RGB（SigLIP）、点云（Uni3D，仅训练用）、机器人状态（action tokenizer）各经 average pooling 成一个 token，作为潜 CoT 的 ground-truth 目标，用**余弦相似度损失**监督推理专家。

论证链条：

1. **问题定位**：显式 CoT VLA（生成语言推理或未来图像）有两个根本病——(1) 自回归生成带来**推理延迟**，限制实时性与时间维度上的一致推理；(2) 推理**困在语言空间**，无法忠实表达"难以言说的物理属性"（几何、接触、动力学）。
2. **解法一（潜 CoT）**：在紧凑潜空间自回归预测未来 **2D 视觉 + 3D 几何 + 本体状态**潜表示，隐式建模物理动态的语义与几何结构、以及机器人-环境关系；再沿未来关键帧扩展，形成**时间一致的因果推理**，提升闭环动作连贯性。压成长度 3×H 的潜序列，避开解码像素/长文本的高成本。
3. **解法二（双系统 MoT）**：潜 CoT 仍带额外推理开销，故用 MoT 把**慢推理专家**（低频潜推理）与**快动作专家**（高频动作）放进同一骨干、共享自注意力；异步频率 κ 让慢专家只在关键帧激活、快专家每步跑并条件于最近潜表示。混合 fast-slow 比训练→部署可自适应选频。
4. **验证**：LIBERO 98.1%、RLBench 82%（+8% over HybridVLA-7B），真实 10 任务三场景 +13/14/14%，且比显式 CoT VLA **快 14×**（15.4Hz vs CoT-VLA 1.1Hz），与 π0.5 (13.8Hz) 相当。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| LaST₀：潜空间"先思后行" VLA，捕捉难言说的物理动态。 | §3.2–3.3。 | Table 1/2/3 全面 SOTA。 | 强，仿真+真机一致。 |
| 时空潜 CoT：自回归建模未来语义/几何/本体，时间一致。 | §3.3（Eq 1/2）。 | 消融 Fig 5c（时域 0→4 步 68→82%）。 | 强，时域扩展直接涨点。 |
| 双系统 MoT 协调低频推理与高频动作，实时。 | §3.2/3.4。 | 15.4Hz（14× over CoT-VLA）；MoT vs 单骨干 82% vs 74%。 | 强，速度与结构消融双证。 |
| 多模态潜（2D+3D+state）互补。 | §3.3。 | Fig 5a（单模态 74–76%，组合更高）。 | 中到强，各模态单独已强、组合再增。 |
| 长时程一致性更好。 | §4.3。 | 叠蛋 3 连：0.66→0.47→0.33 vs π0.5 0.47→0.20→0.07。 | 中到强，差距随时程拉大。 |

## 结构地图

- **§1 Introduction**：显式 CoT 两病（延迟 + 语言瓶颈）；LaST₀ 概述；贡献三点。
- **§2 Related Work**：VLA（扩散/流匹配头、reason-before-act 文本/图像 CoT）、Latent CoT（通用域 + 具身域 LCDrive/Thinkact）。定位=物理接地潜空间联合编码语义/几何/状态。
- **§3 Method**：(3.1) VLA 形式化与动作空间；(3.2) 架构（Janus-Pro/DeepSeek-1.5B、SigLIP、Uni3D 训练用、MoT 24 层 d=2048、MLP 组件）；(3.3) LaST CoT（潜嵌入构建 Eq 1、序列结构与特殊 token、余弦潜监督 Eq 2）；(3.4) 双系统协调（异步频率 κ）；(3.5) 训练配方（400K 预训练 + 联合 SFT + 混合 fast-slow）。
- **§4 Experiments**：(4.1) 仿真（RLBench Table 1 / LIBERO Table 2 + 效率 + 注意力热图 Fig 4）；(4.2) 消融（Fig 5 四项 + MoT）；(4.3) 真机（Table 3，Franka/AgileX/TienKung）。
- **§5–6 结论与局限**：迈向物理接地推理；局限=数据覆盖、复杂交互、待加 RL 后训练。

## 逐节精读

### §1–2 为什么要"潜空间 CoT"

本节把显式 CoT 的两病讲透：**延迟**（自回归文本/图像生成拖慢实时性、且沿时间做一致推理更难）与**语言瓶颈**（物理属性难被语言忠实编码）。相关工作把 latent CoT 从通用 VLM（LCDrive、Thinkact）引到机器人，但本文强调**物理接地**——潜空间联合编码语义意图、几何结构、机器人状态，从而捕捉机器人与环境的具身交互。这是与"只压缩语言/动作"的 latent CoT 的关键差异。

### §3 方法

- **§3.2 架构**：从 **Janus-Pro（DeepSeek-LLM 1.5B、24 层 decoder-only）** 初始化，改造成 **MoT** 双系统——非嵌入组件（FFN、注意力投影 W_Q/K/V/O、LayerNorm）**每专家一套参数**，但**共享全局自注意力**（d=2048）。慢推理专家自回归合成潜 CoT 嵌入 Z，快动作专家用 flow matching 生成动作。视觉用 **SigLIP-Large**（384²）；**Uni3D 点云编码器仅训练时用**（把 ground-truth 点云编成 3D 几何潜，推理不需点云）；本体状态过 action tokenizer。
- **§3.3 LaST CoT**：对未来每步 k∈{1..H} 抽三模态潜 `z^v_k`(SigLIP)/`z^p_k`(Uni3D)/`z^s_k`(state)，average pooling 成单 token，按时间交错排成 `Z_GT=[z^v_1,z^p_1,z^s_1,…,z^v_H,z^p_H,z^s_H]`（长度 3×H，Eq 1）。特殊 token `<latent start/end/pad>`：训练时用 teacher forcing 把 pad 换成 Z_GT；推理时从 `<latent start>` + 一串 pad 起，慢专家自回归填满。**潜监督用连续回归 + 余弦相似度损失**（Eq 2，`L_latent=Σ(1-cos(ẑ_t, z_GT_t))`）而非离散 token 似然——鼓励方向对齐、结构化预测未来物理状态。
- **§3.4 异步协作**：更新比 κ∈{2,4,8}；慢专家只在 `t mod κ=0` 的关键帧做潜推理，其余步休眠；快专家每步跑、条件于最近潜输出。慢专家收低频观测 I_slow + 指令，快专家收高频观测 I_fast，靠共享注意力让快专家高效 attend 到语言目标与潜 CoT token。**经验发现：扩大潜表示的时间跨度（多预测几个未来关键帧）能提升动作预测**。
- **§3.5 训练**：大规模预训练 **400K+ 轨迹**（OXE/DROID/RoboMIND 等）；联合 SFT（慢专家 L_latent + 快专家 flow loss），动作专家用**随机混合 fast-slow 比（1:1/1:2/1:4）**训练→部署可自适应选频（消融显示混合比不掉点反而更鲁棒）。300 epoch，8×A800，评测用 1:4。

**关键证据 / 图表 / 公式**：Fig 2（架构，已嵌入）、Fig 3（异步频率示意）、Fig 4（注意力热图：LaST CoT 聚焦被操作物体/机器人）、Eq 1（交错潜序列）、Eq 2（余弦潜损失）。

## 方法细节（实现口径）

- **骨干/编码器**：Janus-Pro / DeepSeek-LLM 1.5B（24 层，d=2048）；SigLIP-Large（视觉，384²）；Uni3D（点云，仅训练，1024 点子采样）；action tokenizer（本体）。模型总规模约 **3.3B**。
- **动作空间**：SE(3)，单臂 7-DoF（Δxyz + roll/pitch/yaw + gripper），双臂 14-DoF，移动额外估基座线/角速度。
- **潜 CoT**：每模态 1 token 最优（消融）；时域覆盖 4 步最优；潜序列长 3×H。
- **监督**：L_latent（余弦）+ L_flow（flow matching）。
- **频率**：κ∈{2,4,8}，混合训练，测试 1:4。

## 实验设置、数据集、基线、指标

- **仿真**：RLBench（10 任务，Franka Panda，单前视，100 轨/任务 keyframe，CoppeliaSim）；LIBERO（Spatial/Object/Goal/Long，500 trial/suite，双视 384²，无点云则去掉 3D 潜、latent stride=8）。
- **真机**：单臂/双臂 Franka + AgileX 移动 + TienKung 2.0 人形灵巧手；每任务 200 遥操示范，15 rollout×3。
- **基线**：OpenVLA、π0.5、CogACT、SpatialVLA、CoT-VLA、HybridVLA（RLBench）；+ OpenVLA-OFT（LIBERO）；真机对比 π0.5 / SpatialVLA / CoT-VLA。CoT-VLA 在同一 Janus-Pro 上复现以公平对比。
- **指标**：成功率（多 seed 均值±方差）、推理速度（4090 上 Hz）。

## 主要结果、消融与对比

**Table 1｜RLBench（10 任务均值成功率 / 推理速度）**

| Model | Mean S.R.↑ | Infer.↑ |
| --- | --- | --- |
| OpenVLA | 0.40 | 6.3 Hz |
| SpatialVLA | 0.46 | 7.9 Hz |
| CogACT | 0.61 | 9.8 Hz |
| CoT-VLA | 0.66 | **1.1 Hz** |
| π0.5 | 0.65 | 13.8 Hz |
| HybridVLA | 0.74 | 6.1 Hz |
| **LaST₀** | **0.82** | **15.4 Hz** |

LaST₀ 均值 82%（10 任务中 7 项最佳），比 HybridVLA-7B +8%、π0.5 +17%、CogACT +21%；同时**比显式 CoT 的 CoT-VLA 快 14×**（15.4 vs 1.1Hz），与 π0.5 相当。

**Table 2｜LIBERO（成功率%）**：LaST₀ 均值 **98.1**（Spatial 99.2 / Object 99.6 / Goal 98.0 / Long 95.6），超 π0.5 (96.9)、OpenVLA-OFT (97.1)、CogACT (93.6)、CoT-VLA (81.1)。Long суite 尤其体现长时程优势。

**Table 3｜真机（成功率）**：Franka 6 任务均值 **0.72**，超 π0.5 (0.59)、CoT-VLA (0.50)、SpatialVLA (0.41)（+13%）。移动（AgileX）与灵巧手（TienKung 2.0）各 +14%。**长时程叠蛋 3 连**：LaST₀ 0.66→0.47→0.33，π0.5 0.47→0.20→0.07——差距随时程拉大。

**消融（Fig 5 + MoT）**：
- (a) 模态：单用 2D/3D/state 各 74/76/75%，组合再涨——多模态物理动态建模有效。
- (b) 潜 token 数：0→68%，1 token→**82%**，更多无增益（高层潜可紧凑编码）。
- (c) 时域覆盖：0→4 步 68→**82%**，>4 步无增益（选 4）；因 fast-slow 设计，扩时域几乎不拖慢动作。
- (d) 协作频率：1:1/1:2/1:4 约 75–79%，1:8→74%，**混合训练→82%**（测试用 1:4）。
- **MoT vs 单骨干**：82% vs 74%（+8%）——双系统解耦确有必要。

**效率/可解释性**：无 action chunking 时 15.4Hz；Fig 4 注意力热图显示 LaST CoT 相比 no-CoT 与显式 CoT-VLA 有更聚焦于被操作物体/机器人的注意力。

## 图表、公式与表格线索

- **Fig 1**：显式 CoT vs LaST₀ 概念对比（推理延迟 vs 高效潜推理）。
- **Fig 2**：双系统 MoT 架构 + 潜时空空间（已嵌入）。
- **Fig 3**：异步频率（慢关键帧推理、快每步动作）。
- **Fig 4**：注意力热图（no-CoT / 显式 CoT / LaST CoT）。
- **Fig 5**：四项消融（模态/token 数/时域/频率）。
- **Fig 6**：真机任务执行可视化。
- **Eq 1**：交错多模态潜序列。 **Eq 2**：余弦相似度潜监督损失。
- **Table 1/2/3**：RLBench / LIBERO / 真机。

## 主张-证据-边界矩阵

| 主张 | 证据 | 边界 / 可质疑处 |
| --- | --- | --- |
| 潜 CoT 比显式 CoT 又快又强。 | Table 1（82% & 15.4Hz vs CoT-VLA 66% & 1.1Hz）。 | CoT-VLA 复现于同骨干，但显式 CoT 实现选择会影响对比。 |
| 多模态潜互补。 | Fig 5a。 | 单模态已 74–76%，组合增益相对小；3D 仅训练用，推理无点云的收益来自"蒸馏"进潜。 |
| 时空扩展提升长时程。 | Fig 5c、叠蛋 3 连。 | 真机 15×3 rollout、规模有限；长时程仍会衰减（0.33）。 |
| 双系统 MoT 必要。 | MoT 82% vs 单骨干 74%。 | 未拆分 MoT 参数量增加 vs 结构本身的贡献。 |
| 跨本体（桌面/移动/灵巧手）通用。 | Table 3 三场景 +13/14/14%。 | 每任务 200 示范、单独训练；跨任务/零样本泛化未测。 |

## 局限与可追问点

作者在 §6 明确：(1) 公开机器人数据稀缺，**移动与灵巧操作的预训练覆盖有限**；(2) **复杂物体交互仍难**，计划在潜 CoT 里显式加物理约束与 3D 关系图；(3) 计划用 **RL 后训练** 增强鲁棒，联合优化潜推理与动作生成。

可继续追问：
1. 潜 CoT 的"正确性"无显式监督可解释性——余弦损失只对齐方向，如何验证潜推理真的编码了有用物理（而非捷径）？Fig 4 热图是弱证据。
2. 3D 几何潜仅训练用、推理无点云：等于把 3D 知识"蒸馏"进 2D 条件推理——在真正需要精确 3D（遮挡/堆叠）时是否够？
3. 时域覆盖 4 步就饱和、潜 token 1 个就够——是任务较简单，还是潜表示容量的本质上限？更难任务会否需要更多？
4. 与预测未来观测的**世界模型**式 VLA 相比，"预测未来潜"本质是隐式世界模型——两者边界与取舍？
5. 每任务单独 SFT、需 200 示范；与 π0.5/π*0.6 的规模化后训练相比，LaST₀ 的数据效率与泛化如何？

## 与当前库的连接

- 与本库多篇共享/对比 **π0.5** 基线：[[@pan2026vla-corrector-lightweight-detect|VLA-Corrector]]（π0.5 主骨干）、[[@wang2026vlk-learning-humanoid-loco|VLK]]（π0.5 初始化）、[[@intelligence2025pi06-vla-that-learns|π*0.6]]（π0.5→π0.6）。LaST₀ 代表**另一条改进路线**：不改数据/RL，而在**推理结构**上加"潜时空 CoT"。
- 与"预测未来"的世界模型/WMA 线（[[@yu2026wm-dagger|WM-DAgger]] 等）相通：LaST₀ 的潜 CoT = **隐式、token 高效的世界模型**，把未来视觉/几何/状态压进潜序列供动作条件化。
- 与 [[@kang2026x-tokenizer|X-Tokenizer]]（动作表示）互补：一个管"动作 token 化"，一个管"推理 token 化到潜空间"。
- 双系统"慢推理 + 快动作"与 [[@gao2026fast-leworldmodel|Fast LeWorldModel]] 的快规划思想遥相呼应（快慢分工）。
- 地图归属：`#map/具身智能/VLA/潜空间时空思维链CoT`（本文新开轴）。

## 精读路线 / 为什么需要回看

- **只想抓核心**：读 §1（显式 CoT 两病）→ Fig 2 架构 → §3.3 潜 CoT 构建（Eq 1/2）→ §3.4 异步频率 → Table 1/3。
- **要复现**：§3.2–3.5（Janus-Pro/DeepSeek-1.5B、SigLIP、Uni3D 训练用、MoT、κ、混合比）+ 附录 A/B。
- **判断可信度**：Table 1（速度+成功率双赢）+ Fig 5 四项消融 + MoT 消融（82 vs 74）+ 叠蛋 3 连长时程。
- **回看触发条件**：当你要给 VLA 加"reason-before-act"又不想吃显式 CoT 的延迟、或想把"预测未来"做成隐式世界模型条件时，回到 §3。

## 一句话总结

Jiaming Liu 等**提出并验证** LaST₀：把 VLA 的"先思后行"从缓慢、困在语言的显式 CoT，换成在紧凑潜空间自回归预测未来 2D 视觉/3D 几何/本体状态、并跨时间保持一致的 **Latent Spatio-Temporal CoT**，再用 **MoT 双系统**让慢推理与快动作异步协作——在 LIBERO(98.1%)/RLBench(82%, +8%) 与桌面/移动/灵巧手三类真机任务(+13/14/14%)上均达 SOTA，同时比显式 CoT VLA **快 14×**。
