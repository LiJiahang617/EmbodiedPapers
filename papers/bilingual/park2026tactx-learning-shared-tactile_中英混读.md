---
tags:
  - bilingual-reading
paper: "[[@park2026tactx-learning-shared-tactile]]"
source_pdf: "[[papers/pdfs/park2026tactx-learning-shared-tactile.pdf]]"
images: "papers/images/park2026tactx-learning-shared-tactile/"
image_index: "[[papers/images/park2026tactx-learning-shared-tactile/index.md]]"
created: 2026-07-07
---

# TactX: Learning Shared Tactile Representations Across Diverse Sensors

paper:: [[@park2026tactx-learning-shared-tactile]]
pdf:: [[papers/pdfs/park2026tactx-learning-shared-tactile.pdf]]
images:: [[papers/images/park2026tactx-learning-shared-tactile/index.md]]

> 单位：UC San Diego · Seoul National University · Amazon FAR（Junsung Park, Sachin Bhadang 共同一作；Carmelo Sferrazza, Sha Yi, **Xiaolong Wang**）｜ arXiv:2606.31236v1（2026-06，CoRL 2026）｜ 主页：https://tactx-project.github.io

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| tactile sensor heterogeneity | 触觉传感器异构 | 不同传感器测接触的物理机制/输出结构都不同，导致表示与策略被硬件绑死。 |
| transduction modality | 转换模态 | 三大类：resistive（电阻）、magnetic（磁）、vision-based（视觉）。 |
| shared / sensor-agnostic latent | 共享/传感器无关潜空间 | 本文目标：把异构触觉映到同一个低维（16 维）潜空间。 |
| paired contact data | 配对接触数据 | 夹爪两指各装一种传感器，同一次抓握测同一接触点→天然对齐信号。 |
| pairwise joint training | 成对联合训练 | 每次只有两传感器，但联合训所有对 + 共享先验→全局一致潜空间。 |
| contrastive alignment (NT-Xent) | 对比对齐 | InfoNCE/NT-Xent，把同一接触的不同传感器 embedding 拉近。 |
| self / cross-reconstruction | 自/交叉重建 | 一指的潜必须能重建另一指的原始信号→强制共享内容穿过潜空间。 |
| transitive alignment | 传递对齐 | 只训 D–E 和 E–F，却能对齐从未共同观测的 D–F（靠 E 桥接）。 |
| sensor-identity probe | 传感器身份探针 | 冻结潜上线性分类器猜传感器；越接近 33.3% 随机=越传感器无关。 |
| zero-shot policy transfer | 零样本策略迁移 | 一种传感器训的 ACT 策略，经共享潜直接部署到另一物理传感器。 |
| Daimon / eFlesh / FlexiTac | 三个具体传感器 | 分别是 vision-based / magnetic / resistive 代表。 |

## 摘要

触觉为接触密集操作提供视觉给不了的关键信息，但触觉表示与策略**牢牢绑定到具体传感器**，限制了跨机器人/硬件的可迁移性。本文提出 **TactX**：一个跨**三种根本不同转换模态**（resistive、magnetic、vision-based）学习**可迁移触觉表示**的框架。TactX 用**模态专属编码器**把异构触觉观测映到**共享潜空间**，在**配对接触数据**上训练——配对交互天然提供跨模态对齐信号，编码器在所有传感器对上**联合训练**，诱导出对所有传感器类型一致的潜空间。实验证明 TactX 在对齐跨传感器表示的同时保留物体级接触信息（由传感器身份预测与物体分类验证）。在四个接触密集任务（pick-and-place、插拔、擦板、物体重定向）上，一种传感器训的策略经共享潜**零样本迁移**到物理上不同的传感器，把平均成功率从纯视觉的 **27.5% 提升到 45.9%**，向传感器无关的触觉操作迈进一步。

## 论文主线

一句话锚定：**用"夹爪两指各装一种传感器、同一次抓握产生配对观测"这一天然对齐信号，把 resistive/magnetic/vision-based 三种根本不同的触觉传感器对齐进同一个 16 维潜空间，从而让一种传感器训的策略零样本迁到另一种传感器。**

![[papers/images/park2026tactx-learning-shared-tactile/fig2_method.png|780]]

**Figure 2 / 方法。** 每次取两传感器的配对接触：各过**模态专属 Encoder + 变分潜头**（输出 `q(z|x)=N(μ,σ²)`，16 维）→ 在**共享潜空间**用 **Contrastive Loss（InfoNCE）** 对齐 posterior 均值 μ_i、μ_j（同一接触应重合）→ 采样 z 经 **Decoder** 做 self-/cross-reconstruction（一指潜重建另一指信号）→ 加 **KL Loss** 向共享先验 N(0,I) 正则。其他传感器对同理训练，最终三传感器共享一个潜空间。

论证链条：

1. **问题定位**：触觉对接触密集操作不可或缺，但传感器不仅外形不同，**测接触的物理机制也不同**（光学形变 / 磁场变化 / 电阻压力）。一个策略绑定到某传感器的观测空间，换传感器往往要重采数据 + 重训。
2. **已有不足**：跨传感器触觉学习大多局限在**视觉基触觉家族内**（共享 image-like 表示）。真正难的是**无共享基底**的跨模态对齐（视觉图 vs 磁场 vs 电阻压力图）。
3. **解法**：TactX 用配对接触数据（同一接触被两传感器同时测）作对齐信号；**对比对齐**拉近配对接触，**自/交叉重建**保留物体/接触级结构，**KL** 给所有模态共同目标区。**成对联合训练**：虽每次只两传感器，但共享潜 + 共同先验把成对对齐"缝"成全局一致表示。
4. **验证**：三层——(a) 跨传感器对齐（sensor-prediction 67.5%→47.5%，逼近 33.3% 随机）；(b) 传递对齐（D–F 余弦 0.626→0.928，虽从未共同观测 D–F）；(c) 内容保留（物体分类 60.8%）；(d) 零样本策略迁移（4 任务，27.5%→45.9%）。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| 跨三种根本不同模态（视觉/磁/电阻）学共享触觉表示（超越只在视觉家族内的先前工作）。 | §3 架构 + 损失。 | Fig 4（sensor-prediction 逼近随机）。 | 强，跨真正异构模态。 |
| 成对训练策略把所有传感器对对齐进全局一致潜空间。 | §3 pairwise joint training。 | Fig 3（传递 D–F 0.928）。 | 强，传递对齐是硬证据。 |
| 共享潜可作传感器无关接口支持零样本策略迁移。 | §4.4，ACT 策略。 | Table 2（27.5%→45.9%）。 | 中到强，4 任务真机但规模小。 |
| 潜空间既传感器无关又保留接触内容。 | §4.3。 | 物体分类 60.8% + 交叉重建可视化。 | 中到强，重建为定性。 |

## 结构地图

- **§1 Introduction**：触觉重要但硬件绑定；跨模态（非仅视觉基）对齐的更一般问题；TactX 概述 + 三点贡献（+~20% over 视觉迁移）。
- **§2 Related Work**：接触密集操作、触觉传感器/表示、跨本体/跨传感器表示（多局限视觉家族）。
- **§3 Methodology**：数据采集（配对抓握，10 indentors）、架构（模态编码器 + 16 维变分潜 + 解码器）、前向（对齐 μ + 采样重建）、训练目标（Eq 1-3）、成对联合训练。
- **§4 Experimental Evaluation**：(4.1) 跨传感器对齐；(4.2) 成对数据能否对齐多传感器（传递）；(4.3) 内容保留；(4.4) 零样本策略迁移（Table 2）。

## 逐节精读

### §3 方法 —— 配对信号 + 对比 + 重建

- **数据采集**：为构造正样本对，把不同触觉传感器装在同一夹爪两指，对刚性对称物体做准静态抓握，每次抓握两传感器测**同一物理接触**→配对 `(x_i, x_j)`（多接触点 + 10 indentors）。因不能同时装多个，故按对采、联合训。
- **架构**：每传感器一个编码器 `f_i`（信号专属 backbone + projection head）输出 16 维共享潜的**变分后验** `q_i(z|x_i)=N(μ_i, diag(σ_i²))`；低维潜逼编码器学共享接触特征、压缩传感器专属细节。每传感器一个解码器 `g_i` 做自/交叉重建。全部从零训练（模态平等起步）。
- **前向**：一条样本是一对 `(x_i,x_j)`；对齐 posterior 均值 μ_i、μ_j（同一接触应重合），reparameterization 采样 z 做重建；每个 z 既被自己解码器解（self）又被配对传感器解码器解（cross）——**一指潜必须重建另一指真值信号**。推理用 posterior 均值 `z=μ_i(x_i)` 作确定性表示喂下游策略。
- **训练目标（Eq 1）**：`L = Σ_{(i,j)}[λ_recon·L_recon + α(t)·L_align + β(t)·L_KL]`。
  - **L_recon（Eq 2）**：self（`‖g_i(z_i)-x_i‖_1+‖g_j(z_j)-x_j‖_1`）+ cross（`‖g_i(z_j)-x_i‖_1+‖g_j(z_i)-x_j‖_1`），L1；cross 强制共享内容穿过潜、把模态绑在一起。
  - **L_align（Eq 3）**：对 L2 归一化 μ̃ 的对称 **NT-Xent**（τ=0.01），同接触两 μ 为正、batch 内其余为负。
  - **L_KL**：向共享先验 N(0,I) 正则，给所有模态共同目标区。
  - λ_recon=1；α 可用"重建优先"课程 ramp；β 前 30 epoch 从 0 warmup 到 0.1。
- **成对联合训练**：每步从每个可用对数据集采并联合优化→每个编码器每步都受配对监督，共享潜 + 共同先验把成对对齐缝成全局一致表示。

**关键证据 / 图表 / 公式**：Fig 2（方法，已嵌入）、Fig 3（传递对齐）、Fig 4（sensor-prediction + object-classification）、Fig 5（自/交叉重建可视化）、Eq 1-3。

## 实验设置、数据集、基线、指标

- **三传感器**：Daimon（vision-based）、eFlesh（magnetic）、FlexiTac（resistive）——原始观测在几何/维度/物理机制上都不同。
- **评测四问**：(4.1) 跨模态是否对齐进共享潜；(4.2) 成对数据能否对齐三传感器（传递）；(4.3) 潜是否保留接触内容；(4.4) 共享潜能否作零样本策略接口。
- **下游策略**：ACT（Action Chunking with Transformers），一种传感器训、另一种传感器零样本部署。
- **四任务**：pick-and-place（含 OOD）、plug insertion、board wiping、object reorientation。
- **基线**：Vision Transfer（纯视觉迁移）、Binary Contact Transfer；对齐消融含 reconstruction-only / contrastive-only / L2-alignment。
- **指标**：正样本对余弦相似度、sensor-prediction 准确率（越低越无关，chance 33.3%）、object-classification 准确率、策略成功率（10 trial×3 run）。

## 主要结果、消融与对比

- **跨传感器对齐（4.1，Fig 4）**：sensor-prediction 从 reconstruction-only 的 **67.5% 降到 47.5%**（最接近 33.3% 随机的重建类变体）；t-SNE 显示三传感器域从分离变混合。contrastive-only 正样本相似度最高（但缺重建→丢内容）。
- **传递对齐（4.2，Fig 3）**：只训 D–E 与 E–F，测从未共同观测的 D–F。D–F 余弦从 reconstruction-only 0.626 / L2-align 0.679 **升到 0.928**——证明不是学独立成对映射，而是**全局一致潜空间**。
- **内容保留（4.3）**：自/交叉重建保留主接触模式；物体分类（10 类未见接触点）TactX 最高，self **60.8%**。
- **零样本策略迁移（4.4，Table 2）**：跨 4 任务，TactX 把平均成功率从纯视觉迁移的 **27.5% 提升到 45.9%**（约 +20 个百分点/~1.7×）。逐任务看，最强 source→deploy 组合上 TactX 普遍最好（如 eFlesh→Daimon 的 P&P 9.0/10、insertion 6.0/10）。

## 图表、公式与表格线索

- **Fig 1**：概念图（共享潜 → 触觉策略零样本迁移）。
- **Fig 2**：方法（配对→编码→对比对齐→自/交叉重建，已嵌入）。
- **Fig 3**：传递对齐 D→E→F（0.928）。
- **Fig 4**：sensor-invariance（67.5→47.5）+ object-classification（60.8）。
- **Fig 5**：自/交叉重建可视化（sphere/plane/circle indentors）。
- **Table 2**：跨传感器策略迁移逐任务成功数（TactX vs Vision/Binary Contact）。
- **Eq 1**：总损失。 **Eq 2**：自+交叉重建。 **Eq 3**：NT-Xent 对齐。

## 主张-证据-边界矩阵

| 主张 | 证据 | 边界 / 可质疑处 |
| --- | --- | --- |
| 跨三真正异构模态对齐成功。 | sensor-prediction 47.5%（近 33.3%）。 | 仍高于随机，未完全传感器无关；只 3 个具体传感器。 |
| 成对数据→全局一致（传递）。 | D–F 0.928。 | 传递质量依赖桥接传感器 E 的覆盖；更多传感器时链式误差？ |
| 共享潜保留接触内容。 | 物体分类 60.8% + 重建。 | 60.8% 绝对值不高；细粒度几何/力信息保留程度未深究。 |
| 零样本策略迁移有效。 | Table 2（27.5→45.9%）。 | 绝对成功率仍偏低（45.9%）；quasi-static 抓握采数据、刚性对称物体。 |

## 局限与可追问点

1. 潜仍 16 维、绝对成功率 45.9%——**共享 vs 专属信息的权衡**在哪？更高维/更强解码能否既无关又保内容？
2. 数据是**准静态抓握、刚性对称物体、10 indentors**——对动态接触、柔性物体、真实操作分布的覆盖有限。
3. 传递对齐靠桥接传感器；**扩到更多传感器**时链式误差如何积累？新模态接入的成本？
4. 只对齐"表示"，未联合优化下游策略；端到端联合训练能否进一步提升迁移？
5. 与 HTT（同期、更大规模 1.6M 数据集 + MAE + cross-sensor prediction）相比，对比+重建 vs MAE+跨传感器预测两条路各自优劣？

## 与当前库的连接

- 与 [[@bi2026heterogeneous-tactile-transformer|HTT]] 是**同一问题（跨异构触觉传感器学共享表示）的同期平行工作**：TactX=**3 模态（视觉/磁/电阻）、16 维变分潜、对比+自/交叉重建、小规模、零样本 ACT 策略迁移**；HTT=**光学+阵列、Transformer trunk、1.6M 帧 HPT 数据集、MAE+跨传感器预测、感知+操作**。两篇对读=跨传感器触觉表示的两种配方。
- 与 [[@wu2026tactile-wam|Tactile-WAM]]（触觉世界动作模型）互补：一个解"触觉表示怎么跨传感器共享"，一个解"触觉如何进世界动作模型"。同属触觉轴。
- 与 [[@kang2026x-tokenizer|X-Tokenizer]]（跨本体动作表示）思想同源：都用"共享潜空间 + 每端编码器"做跨硬件迁移，只是一个在动作侧、一个在触觉观测侧。
- 地图归属：`#map/触觉/跨传感器触觉表示`（与 HTT 同轴）。

## 精读路线 / 为什么需要回看

- **只想抓核心**：读 §1 → Fig 2 → §3 训练目标（Eq 1-3）→ Table 2。
- **要复现**：§3 全部（配对采集、16 维变分潜、self/cross recon、NT-Xent τ=0.01、β warmup）+ 附录 A/B/C。
- **判断可信度**：Fig 3（传递 0.928）+ Fig 4（sensor-prediction 逼近随机）+ Table 2（策略迁移）。
- **回看触发条件**：当你要**换触觉传感器却不想重训策略**、或想做跨异构传感器的触觉表示时，回到 §3。

## 一句话总结

TactX（UCSD/Xiaolong Wang 组）**提出并验证**：用"夹爪两指各装一种传感器、同一次抓握产生配对观测"的天然对齐信号，配合对比对齐 + 自/交叉重建 + 成对联合训练，把 resistive/magnetic/vision-based 三种根本不同的触觉传感器对齐进同一个 16 维潜空间——既传感器无关（身份预测逼近随机）又保留接触内容（传递对齐 0.928、物体分类 60.8%），使一种传感器训的策略零样本迁到另一种传感器，四任务平均成功率 27.5%→45.9%。
