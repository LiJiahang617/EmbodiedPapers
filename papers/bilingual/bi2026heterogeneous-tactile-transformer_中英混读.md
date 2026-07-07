---
tags:
  - bilingual-reading
paper: "[[@bi2026heterogeneous-tactile-transformer]]"
source_pdf: "[[papers/pdfs/bi2026heterogeneous-tactile-transformer.pdf]]"
images: "papers/images/bi2026heterogeneous-tactile-transformer/"
image_index: "[[papers/images/bi2026heterogeneous-tactile-transformer/index.md]]"
created: 2026-07-07
---

# Heterogeneous Tactile Transformer (HTT)

paper:: [[@bi2026heterogeneous-tactile-transformer]]
pdf:: [[papers/pdfs/bi2026heterogeneous-tactile-transformer.pdf]]
images:: [[papers/images/bi2026heterogeneous-tactile-transformer/index.md]]

> 单位：National University of Singapore · Carnegie Mellon University（Jianxin Bi … **Harold Soh** 通讯）｜ arXiv:2606.29948v1（2026-06）｜ 数据/代码/权重承诺发布

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| heterogeneous tactile sensors | 异构触觉传感器 | 光学 vs 阵列两大类：测接触方式与输出结构都不同。 |
| optical tactile (GelSight/9DTact) | 光学触觉 | 从弹性体形变的图像推接触，空间信息丰富但受帧率限。 |
| array-based tactile (Xela/Tac-02) | 阵列触觉 | 分布式敏感元件，高频力/压力信号但空间分辨率低。 |
| HTT | 本文框架 | 传感器专属编码器 + 共享 Transformer trunk + 跨模态预测器。 |
| HPT dataset | 异构配对触觉数据集 | 1.6M 同步配对帧，UMI 采集，本文核心资产。 |
| UMI (Universal Manipulation Interface) | 通用操作接口 | 手持夹爪采数据装置，两指对置装两种传感器→同步配对。 |
| masked reconstruction (MAE) | 掩码重建 | 每模态自监督重建被 mask 的 token，学传感器专属结构特征。 |
| cross-modal alignment / prediction | 跨模态对齐/预测 | 从源传感器 + 可见目标 token 预测被 mask 的目标 embedding，对齐潜空间。 |
| shared transformer trunk | 共享 Transformer 主干 | 处理各传感器 token 到共同潜空间的统一主干。 |
| stop-gradient | 停梯度 | 施于对齐回归目标，防表示坍缩。 |
| transferable representation | 可迁移表示 | 适配新任务与**预训练未见的新传感器**。 |

## 摘要

触觉传感器天生异构：一个传感器上训的模型不能直接用到另一个，这限制了从多样触觉数据规模化学接触密集操作策略。本文提出 **HTT（Heterogeneous Tactile Transformer）**，跨异构传感器学**共享触觉表示**。HTT 由**传感器专属编码器 + 共享 Transformer trunk** 组成，用**逐模态掩码重建 + 配对传感器间跨模态对齐**做预训练。预训练用作者新建的 **HPT（Heterogeneous Paired Tactile）数据集**：跨四种视觉基与阵列基触觉传感器的 **1.6M 同步配对帧**。在多个触觉感知与真实操作任务上，HTT 学到可迁移表示，能适配**新任务与此前未见的新传感器**。

## 论文主线

一句话锚定：**造一个 1.6M 帧的"同一接触被两种触觉传感器同步测量"的配对数据集（HPT），再用"逐模态 MAE 掩码重建 + 跨传感器掩码预测对齐"训一个"传感器专属编码器 + 共享 Transformer trunk"的骨干，让触觉表示能跨光学/阵列传感器迁移、甚至泛化到预训练未见的新传感器。**

![[papers/images/bi2026heterogeneous-tactile-transformer/fig1_htt_framework.png|780]]

**Figure 1 / HTT 框架 + HPT 数据集。** 左：UMI 夹爪两指对置装两种传感器采**配对触觉数据**（HPT，1.6M 帧，Xela/Tac-02/9DTact/GSMini）。中：vision patches → V.Encoder、taxel patches → T.Encoder → **Shared Transformer Trunk**。① **Masked Reconstruction**：各模态解码器重建被 mask 的 token（`L_MAE`）。② **Cross-Modal Alignment**：从源 `z_i`（no mask）+ 可见目标预测被 mask 的目标 `z_j`（Cross-Modal Predictor，stop-gradient，`L_Align`）。右：预训练后用于感知（物体/力/滑）与操作（拧螺丝/抓豆腐）。

论证链条：

1. **问题定位**：触觉对接触密集操作关键，但**难规模化**——传感器异构，测接触方式与数据结构都不同（光学=图像、阵列=时间序列）。互补但难合并，也难训"可复用表示/传感器无关策略"。
2. **已有不足**：触觉表示学习大多只做**光学触觉**（MAE 从 GelSight 图像学特征），无法直接吃阵列信号，也**缺大规模同步的光学-阵列配对数据集**。
3. **解法**：先补数据（HPT，UMI 采 1.6M 同步配对帧，4 传感器），再造骨干（HTT：传感器专属编码器 + 共享 trunk + 跨模态预测器），预训练 = **MAE 掩码重建**（保各传感器专属结构）+ **双向跨传感器预测对齐**（对齐潜空间）。
4. **验证**：三感知任务（物体分类、力估计、滑动检测）+ 仿真/真实操作（拧玩具螺丝、抓豆腐），且能适配**预训练未见的新传感器**。物体分类上 HTT 在光学传感器超最强基线 SITR 13.5%（9DTact）/17%（GSMini）。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| HPT：1.6M 配对帧、光学+阵列同步的大规模数据集（首个此类）。 | §3。 | 数据统计（Fig 1/2）。 | 强，填补数据空白。 |
| HTT：MAE 掩码重建 + 双向跨传感器预测的自监督框架。 | §4。 | Q1–Q5 全面评测。 | 强，方法自洽。 |
| 学到可迁移表示、可作异构触觉通用骨干、适配新传感器。 | §4/§5。 | Table 1（超 Scratch/SITR）+ 操作任务。 | 中到强，感知强、操作定性偏多。 |
| 跨传感器对齐带来额外增益（vs 仅 MAE）。 | §4.2。 | HTT vs MAE(ours) 对比。 | 中到强，消融隔离对齐效果。 |

## 结构地图

- **§1 Introduction**：触觉难规模化（异构）；只做光学的局限；HTT + HPT 概述；三点贡献。
- **§2 Related Work**：触觉传感器（光学 vs 阵列）、触觉数据集（多局限光学、缺同步光学-阵列配对）、异构触觉表示学习（UniTac/UniForce/Touch-to-touch 对比）。
- **§3 HPT Dataset**：UMI 采集系统（两指对置，Pair A Xela↔9DTact、Pair B TAC-02↔GS Mini）；四组件（配对无标签预训练 / 物体分类 20 类 / 力估计 F/T 探针 / 滑动检测 Page CUSUM，类别 13.6/1.2/85.2%）。
- **§4 HTT**：(4.1) 架构（编码器/共享 trunk/解码器/跨模态预测器、输入 patch）；(4.2) 预训练（MAE Eq 1 + 对齐 Eq 2 + 联合 Eq 3）。
- **§5 Experiments**：Q1–Q5（表示有用性、跨任务迁移、对齐收益、操作策略、新传感器适配）。

## 逐节精读

### §3 HPT 数据集 —— 先补"同步配对"这块拼图

作者用 **UMI** 手持夹爪、3D 打印模块化壳把两种传感器装在**对置两指**，一次交互同时测同一接触→同步配对流。两配置：Pair A（Xela↔9DTact）、Pair B（TAC-02↔GS Mini）。共 **1.6M 帧**（日常物体），四组件：**配对无标签**（预训练核心，非脚本交互）、**物体分类**（20 物体、press/twist/slide 动作）、**力估计**（外接 6D F/T 传感器提供同步力标签，4 种探针几何，力范围 ≤40N 法向/14N 剪切）、**滑动检测**（从 6D 力算摩擦系数时间序列 + 双侧 Page CUSUM 变点检测，得 static/incipient/slide 三类，分布 13.6/1.2/85.2%——罕见类难检）。预训练与评测数据无重叠。

### §4 HTT —— MAE + 跨传感器预测

- **架构（4.1）**：四组件——**Encoders `E_i`**（光学用 ViT、阵列用 self-attention transformer）、**Shared Trunk `T`**（统一潜空间）、**Decoders `D_i`**（掩码重建）、**Predictors `P_ij`**（cross-attention，从源 + 可见目标预测被 mask 的目标 embedding）。输入 patch：光学帧 resize 224×224 → ViT 空间 patch；阵列高频时序 → 时间 patch；所有模态先**减去非接触参考帧**；τ=0.2s 窗口。
- **预训练（4.2）**：
  - **MAE 重建（Eq 1）**：编码器+trunk 只处理可见 token，解码器重建被 mask token（per-patch 归一化目标），跨模态平均。逼编码器-trunk 保留高保真局部细节。
  - **跨模态对齐（Eq 2）**：对每有序对 `(i,j)`，`z_i=T(E_i(x_i))`、`z_j=T(E_j(x_j))`；predictor `P_ij` 从源 `z_i` + 可见目标 `z_jv` 预测被 mask 的目标 `z_jm`；对回归目标施 **stop-gradient** 防坍缩。对所有有序对平均。
  - **联合（Eq 3）**：`L_HTT = L_MAE + α_t·L_Align`；α_t warmup 期为 0（先靠 MAE 建传感器专属特征）后 ramp 到 **α_max=0.1**；且**在编码器输出处阻断对齐梯度**——`L_Align` 只更新 predictor 与共享 trunk，编码器只由 `L_MAE` 更新（保护专属特征）。预训练后**丢弃解码器与预测器**，只留编码器 `E_i` + 共享 trunk `T` 供下游。

**关键证据 / 图表 / 公式**：Fig 1（框架 + 数据，已嵌入）、Fig 2（力/滑数据采集与统计）、Eq 1（MAE）、Eq 2（跨模态对齐）、Eq 3（联合损失）、Table 1（物体分类）。

## 实验设置、数据集、基线、指标

- **感知任务**：物体分类（20 类 top-1）、力估计（6D 力回归）、滑动检测（3 类，类不均衡）。
- **操作任务**：仿真 + 真实（拧玩具螺丝 toy screw、抓豆腐 grasp tofu 等接触密集）。
- **五问 Q1–Q5**：表示是否有用、是否跨任务迁移、跨传感器对齐是否有益、是否提升接触密集策略学习、是否适配预训练未见新传感器。
- **基线**：Scratch（同架构从零、不预训练）、T3、SITR、**MAE(ours)**（同架构仅 MAE 预训练，用于隔离跨传感器对齐效果）。

## 主要结果、消融与对比

- **物体分类（Table 1，20 类 top-1 %）**：MAE 与 HTT 在**每个传感器**都超 Scratch，证明预训练配方有用。HTT 在两光学传感器上超最强基线 **SITR 13.5%（9DTact）/17%（GSMini）**。T3 迁到 9DTact 差（对光学传感器迁移弱）。HTT vs MAE(ours) 的差距**隔离出跨传感器对齐的增益**。（MAE(ours) 参考行：56.68 / 26.16 / 90.08 / 88.59 / 65.38。）
- **跨任务迁移 / 对齐收益 / 操作 / 新传感器（Q2–Q5）**：HTT 学到可迁移表示、提升接触密集策略（toy screw、grasp tofu），并能适配预训练未见的新传感器——支撑"配对异构预训练是通用触觉骨干的实用路径"。

## 图表、公式与表格线索

- **Fig 1**：HTT 框架 + HPT 数据（已嵌入）。
- **Fig 2**：力/滑数据采集装置与统计（力范围、滑动类别不均衡）。
- **Table 1**：物体分类（HTT 超 Scratch/SITR，MAE(ours) 对照隔离对齐效果）。
- **Eq 1**：MAE 掩码重建。 **Eq 2**：跨模态对齐（stop-gradient）。 **Eq 3**：联合损失（α warmup、编码器梯度隔离）。

## 主张-证据-边界矩阵

| 主张 | 证据 | 边界 / 可质疑处 |
| --- | --- | --- |
| HPT 填补光学-阵列同步配对数据空白。 | 1.6M 帧、4 传感器、UMI。 | 仅两配对（A/B）、四传感器；日常物体、非脚本交互的分布覆盖未量化。 |
| HTT 学到有用可迁移表示。 | Table 1（超 Scratch/SITR）。 | 力估计/滑动检测的具体增益未在本稿摘出；滑动罕见类难。 |
| 跨传感器对齐带额外增益。 | HTT vs MAE(ours)。 | 增益幅度依传感器；对阵列传感器的相对收益？ |
| 适配预训练未见新传感器。 | Q5。 | "新传感器"与预训练分布的距离决定迁移；极端异构传感器边界未知。 |

## 局限与可追问点

1. 仅**两配对配置、四传感器**——扩到更多/更异构传感器（电容、压电、声学）时框架是否仍稳？成对配置组合爆炸如何处理？
2. 滑动检测**类别极不均衡**（static 13.6/incipient 1.2/slide 85.2%）——罕见但关键的 incipient slip 检测是否可靠？
3. 编码器梯度隔离 + α warmup 是精心平衡的训练技巧——对超参敏感度、坍缩风险如何？
4. 操作任务以定性/少量为主——大规模、多任务下"通用触觉骨干"的真实收益？
5. 与 TactX（同期，3 模态视觉/磁/电阻、变分潜、对比+重建、零样本策略迁移）相比，MAE+跨传感器预测 vs 对比+重建两配方在"感知 vs 策略迁移"上各自更擅长什么？

## 与当前库的连接

- 与 [[@park2026tactx-learning-shared-tactile|TactX]] 是**同一问题（跨异构触觉传感器学共享表示）的同期平行工作**：HTT=**光学+阵列、Transformer trunk、1.6M 帧 HPT 大数据集、MAE+跨传感器预测、感知任务为主 + 操作**；TactX=**视觉/磁/电阻三模态、16 维变分潜、对比+自/交叉重建、小规模、零样本 ACT 策略迁移**。两篇对读=跨传感器触觉表示的两条配方（生成式 MAE vs 判别式对比）。
- 与 [[@wu2026tactile-wam|Tactile-WAM]]（触觉世界动作模型）互补：HTT 解"触觉表示怎么跨传感器共享/预训练"，Tactile-WAM 解"触觉如何进世界动作模型驱动策略"。同属触觉轴。
- 与 [[@kang2026x-tokenizer|X-Tokenizer]]（跨本体动作表示）思想同源：共享潜 + 每端编码器做跨硬件迁移。
- 地图归属：`#map/触觉/跨传感器触觉表示`（与 TactX 同轴）。

## 精读路线 / 为什么需要回看

- **只想抓核心**：读 §1 → Fig 1 → §4.2（MAE + 跨模态对齐 + 梯度隔离）→ Table 1。
- **要复现**：§3（HPT 采集/组件）+ §4.1（patch/编码器）+ §4.2（Eq 1-3、α warmup、编码器梯度隔离）+ 附录 A.1。
- **判断可信度**：Table 1（超 Scratch/SITR，MAE(ours) 对照）+ Q3 对齐消融 + Q5 新传感器。
- **回看触发条件**：当你要预训练一个**跨光学/阵列触觉的通用骨干**、或需要"同步配对触觉数据集"时，回到 §3–4。

## 一句话总结

HTT（NUS/Harold Soh 组）**构建并验证**：先用 UMI 采一个 1.6M 帧、四传感器同步配对的 HPT 数据集，再用"逐模态 MAE 掩码重建 + 双向跨传感器掩码预测对齐（stop-gradient、编码器梯度隔离）"训一个"传感器专属编码器 + 共享 Transformer trunk"的异构触觉骨干——在物体分类等感知任务上超 Scratch/SITR（光学传感器 +13.5/17%），并能迁移到接触密集操作与预训练未见的新传感器，是与 TactX 平行的跨传感器触觉表示代表作。
