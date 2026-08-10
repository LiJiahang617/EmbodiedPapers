---
tags:
  - bilingual-reading
  - deep-reading
  - vision-foundation-model
  - dense-perception
paper: "[[@fu2026lingbot-vision]]"
source_pdf: "[[papers/pdfs/fu2026lingbot-vision.pdf]]"
images: "papers/images/fu2026lingbot-vision/"
image_index: "[[papers/images/fu2026lingbot-vision/index.md]]"
created: 2026-07-15
reading_mode: 复现级人工精读（全文 + 公式 + 表格 + 附录）
---

# Vision Pretraining for Dense Spatial Perception

paper:: [[@fu2026lingbot-vision]]
pdf:: [[papers/pdfs/fu2026lingbot-vision.pdf]]
images:: [[papers/images/fu2026lingbot-vision/index.md]]

## 核心词汇速查

| English | 中文 | 在本文中的精确作用 |
| --- | --- | --- |
| dense spatial perception | 稠密空间感知 | 每个 patch/pixel 都需保留可读出的几何与区域结构，而不是只产生 image-level semantic embedding。 |
| semantic invariance | 语义不变性 | DINO/CLIP 类目标希望不同视图语义一致，但可能抹平边界处的小位置变化。 |
| boundary-forcing mask | 边界强制掩码 | 将 teacher 在线发现的 boundary tokens 并入随机 mask，强制 student 从上下文重建最不冗余的位置。 |
| geometry routing | 几何路由 | boundary token 同时接收 semantic iBOT target 和 categorical boundary target；其他 token 只接收语义目标。 |
| boundary field | 边界场 | 每个 support pixel 用 $(d,\theta,\phi_1,\phi_2)$ 冗余编码最近线段的距离、方向和端点几何。 |
| categorical reparameterization | 类别化重参数化 | 将连续 field channel 离散为 $K$ 个 bin 的软标签，使 centering/sharpening 可用并避免 EMA regression collapse。 |
| corner anchoring | 角点锚定 | 把 dense pixel proposals 的两个端点吸附到稀疏 corner pair；从随机 field 也可聚合出短线段。 |
| vote aggregation | 投票聚合 | 多个 support pixels 对同一 corner pair 投票，利用过参数化冗余压制单像素噪声。 |
| a-contrario / NFA | 反先验检验 / 假警报数 | 用“无结构时方向均匀”作为零假设，只保留偶然出现概率低的候选线段。 |
| EMA teacher | 指数滑动平均教师 | teacher 参数由 student EMA 更新，在线产生 semantic 与 boundary targets，且 stop-gradient。 |
| linear probe | 线性探针 | 冻结 backbone，只训练单线性层；因此结果更直接反映 patch feature 是否已经含深度/分割信息。 |
| masked depth modeling (MDM) | 掩码深度建模 | LingBot-Depth 2.0 的 RGB-D 补全框架；缺失深度 patch 本身作为结构化 mask。 |

## 摘要

论文提出 LingBot-Vision：一个把 boundary structure（边界结构）从下游输出提升为预训练原生监督的视觉基础模型。作者认为现有 self-supervised vision pretraining 主要优化跨视角语义一致性，边界和空间布局即使出现也只是副产品；随机 masking 又把平坦区域与物体交界当成同等信息量的预测目标。于是模型可能分类很强，却无法仅靠冻结 patch tokens 线性读出精确深度、分割或可追踪的局部结构。

方法以 DINO+iBOT teacher–student 为骨架。EMA teacher 先输出 sub-token boundary field，再借冻结的一层 corner detector、corner-pair voting 和 a-contrario validation 得到可信线段；线段 rasterize 后得到 boundary token set $B$，并强制加入 student mask $M^+=M\cup B$。每个边界位置用四通道 categorical boundary field 监督，边界 token 同时保留 iBOT semantic target，class token 保留 DINO target。这样“是什么”与“边界在哪里/朝什么方向”在同一 backbone 内协同学习。

关键难点是从零启动：随机初始化 teacher 并不会检测边界。作者利用 boundary field 的冗余表示——每个 support pixel 都能重建整条 segment——配合角点锚定和投票，即便 field 很噪也能得到候选线；a-contrario 再删除不受图像 orientation 支撑的伪线。连续 regression 在 EMA loop 中会漂移/塌缩，故四个 field channels 离散成 $K=32$ bins，既能使用 DINO 式 centering/sharpening，又让“无边界”严格对应均匀分布，直接成为 NFA 检验的零假设。

规模化后，约 1.1B 参数 ViT-g/16 在 160.75M images 上训练。冻结单线性层下，NYUv2 RMSE 0.296，优于 7B DINOv3 的 0.309；DAVIS/YouTube-VOS training-free label propagation 达 70.0/73.5 $J\&F$。蒸馏至 ViT-L/B/S 后 dense advantage 大体保留。将同一 MDM pipeline 的 encoder 从 DINOv2/3 换为 LingBot-Vision，再把 RGB-D 数据从 3M 扩至 150M，得到 LingBot-Depth 2.0，并在 14 个 depth-completion benchmarks 上取得强结果。

## 论文主线

```text
Random-mask self-distillation 的缺口：不知道“该遮哪里、边界处该预测什么”
      ↓
EMA teacher 预测 dense categorical boundary field
      ↓ corner anchors + vote aggregation + a-contrario NFA
validated line segments → boundary tokens B
      ↓
student mask M⁺ = random M ∪ B
      ↓ geometry routing
class token: DINO | all masked tokens: iBOT | boundary positions: boundary CE
      ↓
同时保留 semantic grouping + sharp spatial discontinuity 的 patch representation
```

最重要的 Aha 不只是“多加一个边缘 loss”，而是把三个原本不相干的东西严密拼起来：**boundary field 的冗余性解决从零自举；categorical representation 解决 teacher–student 稳定性；uniform categorical distribution 又恰好等于 a-contrario 的 no-structure null。** 因此同一组输出既是训练 target，又能做无参数统计验证。

## 1. 🎯 核心思想与动机（The “Aha!” Moment）

### 痛点与动机

随机遮住图像 patch 时，模型很可能反复预测大面积墙面、天空或纹理内部，这些位置可从邻域轻易复制；而真正决定深度断裂、物体轮廓、遮挡关系的边界 token 信息最密、最难预测，却没有专属几何 target。单靠 semantic codeword 在两个区域交界处本身就是歧义的。

### 核心思想

让模型自己找“最值得考试的题”：teacher 先猜边界，把这些边界 patch 强制盖住；student 不仅要猜它属于什么语义，还要还原穿过 patch 的线段几何。teacher 初期猜得很差也没关系，因为很多像素会为同一对角点投票，真实线段会积累一致证据；再用统计检验丢掉偶然伪线。随着 student 变好，EMA teacher 和伪边界一起变好，形成 self-bootstrapping curriculum。

## 2. ✨ 核心贡献梳理（Contributions）

- 提出 boundary-centric SSL：不依赖人工 edge/boundary label、外部 edge detector 或 pretrained backbone，让随机初始化 ViT 从 raw images 自举边界，并将其作为 masked modeling 的一级监督。
- 设计 boundary-forcing + geometry routing：$B$ 强制并入 mask，boundary token 同时优化 semantic iBOT 与 geometric boundary CE，从目标层面解决语义不变性和几何敏感性的冲突。
- 将连续 boundary field 重新参数化为四通道 categorical distribution；复用 centering/sharpening 防塌缩，并令均匀分布天然对应 a-contrario null hypothesis，实现在线、近无参数伪边界验证。
- 将方法扩展到 1.1B ViT-g/16、161M images，并蒸馏为 ViT-L/B/S；进一步用其初始化 LingBot-Depth 2.0，在真实相机、block-mask、sparse depth 等 14 个深度补全 benchmark 上验证空间表征价值。

## 贡献与结论对照

| 贡献/主张 | 方法位置 | 关键证据 | 边界 |
| --- | --- | --- | --- |
| categorical boundary target 是有效成分。 | §3.3--3.6，Eq.(8)(9)。 | Table 1：NYUv2 $\delta_1$ 81.4→84.4，RMSE 0.474→0.446。 | ImageNet-1K proof-of-concept；不是所有数据域。 |
| boundary 与 semantic 可协同。 | §3.2/3.5。 | dual supervision 再使 kNN 81.8→82.0、RMSE 0.446→0.443。 | 提升较小，但方向一致。 |
| 只是 forcing mask 不够。 | §3.6。 | semantic-only forcing：RMSE 0.481，反低于 baseline 0.474。 | 直接排除“只因 hard masking”解释。 |
| dense representation 可规模化。 | §4--5。 | NYUv2 0.296；DAVIS/YTVOS 70.0/73.5。 | Image-level classification 仍落后 7B DINOv3。 |
| downstream depth completion 得益于初始化。 | §6，Tables 6--8。 | 同 MDM recipe 下 LingBot-Vision 初始化多数更优；DIODE-In 0.132→0.062（v1→2.0）。 | Depth 2.0 还同时将数据扩到 150M。 |

## 结构地图

| 原文 section | 本节功能 | 关键公式/图表 |
| --- | --- | --- |
| §1--2 | 定义 semantic–spatial trade-off，并回顾 DINO/iBOT、JEPA、boundary field。 | Fig.1。 |
| §3.1 | 重述 EMA teacher、DINO class-token、iBOT patch-token。 | Eq.(1)--(4)。 |
| §3.2 | 定义 boundary token 与 forced mask；解释 geometry routing。 | Eq.(5)(6)，Fig.2。 |
| §3.3 | 定义 field $(d,\theta,\phi_1,\phi_2)$ 与 categorical labels。 | Eq.(7)--(9)，Fig.4。 |
| §3.4 | 在线预测→角点锚定→投票→NFA→rerender。 | Fig.5。 |
| §3.5--3.6 | 总 loss 与 proof-of-concept。 | Eq.(10)，Table 1。 |
| §4 | 161M 数据、GPU pipeline、1.1B 训练配方。 | 系统细节。 |
| §5 | frozen depth/segmentation/video/classification 与蒸馏。 | Tables 2--5，Figs.6--7。 |
| §6 | LingBot-Depth 2.0。 | Tables 6--8，Figs.8--10。 |
| Appendix A--B | 随机场采样实验与并行 a-contrario 推导。 | Eq.(11)，Fig.11。 |

## 3. ⚙️ 方法论全景与精细拆解（Detailed Pipeline & Module Breakdown）

### 模块 1：DINO/iBOT 语义自蒸馏骨架

**物理/数学意义。** 提供已有的全局语义与 patch 语义学习通道；boundary branch 必须在不破坏这一通道的前提下加入空间结构。

**输入。** 原图 $x\in\mathbb R^{H\times W\times3}$；两张 global crops 和若干 local crops。以 patch size $P=16$ 划分为 $N=HW/P^2$ tokens，得到 class token $z_{cls}$ 和 patch tokens $\{z_i^p\}_{i=1}^N$。

**内部机制。** student 参数 $\theta$ 梯度更新，teacher 参数以 EMA：

$$\bar\theta\leftarrow\lambda\bar\theta+(1-\lambda)\theta,\qquad \lambda\to1.\tag{1}$$

DINO head $h$ 把 class token 映射为 $C$ prototypes，teacher 减 center $c$、用更低温度 $\tau_t<\tau_s$ sharpen，再以跨 crop cross-entropy 匹配。iBOT 随机采样 block mask $M\sim p_{mask}(\cdot;r)$，student 的被遮 patch 分布 $q_i^s$ 匹配 teacher 未遮位置 $q_i^t$：

$$\mathcal L_{iBOT}=-\frac1{|M|}\sum_{i\in M}(q_i^t)^\top\log q_i^s.\tag{4}$$

**输出。** class-level semantic distribution 和 patch-level semantic distribution；后者将作用于扩展后的 $M^+$。

### 模块 2：Boundary Field Head（sub-token 稠密几何头）

**物理/数学意义。** ViT 每 patch 只有一个 token，而边界在 patch 内可能精确穿过某几个像素；该 head 将 token 展开到 stride 2 的 sub-token field，使几何 target 不被 patch resolution 限死。

**输入。** teacher/student patch token $z_i^p\in\mathbb R^d$。

**内部机制。** 三层 per-token MLP 将每个 token 扩展为 $r\times r$ tile，pixel-shuffle/rearrange 后得到 stride $s=P/r=2$ 的 dense positions。每个 position feature $v_p$ 做 $\ell_2$ normalize；四个 channel 各用 $K=32$ 个单位范数 prototype，以无 bias 线性层计算 cosine logits。四通道连续语义为：

$$a(p)=(d_p,\theta_p,\phi_{1p},\phi_{2p}),\tag{7}$$

$d$ 是到最近 segment 的距离，$\theta$ 给方向，$\phi_1,\phi_2$ 从位置 $p$ 指向两端点。通过各 bin center 的期望恢复连续值；$\theta$ 用 circular mean。

**输出。** $H/2\times W/2\times4\times K$ 的 categorical field（实现中只在稀疏 boundary tokens 展开，避免真正全量 materialize），teacher 端用于解码，student 端用于 CE。

### 模块 3：从噪声 Field 在线生成可信边界

**物理/数学意义。** 解决“没有边界就无法训练边界预测器；没有预测器又找不到边界”的 bootstrap 问题。

**输入。** teacher categorical field、global crop grayscale image、冻结 single-block ViT corner detector 的角点集合 $C=\{c_m\}$。

**内部机制。** (1) 从 categorical expectation 得到每个 sub-token position 的 chord proposal；(2) proposal 两个端点各自吸附最近 corner，形成 corner pair；(3) 所有落到同一 pair 的 support pixels 投票，票数足够构成 candidate segment；(4) 在 segment 周围固定宽度 rectangle 中统计 level-line orientation 与 segment 对齐的像素；(5) 计算 NFA，删除随机情况下不显著的候选；(6) 将 survivors 重新 rasterize 为 clean field。重要的是只用 rerendered clean field 监督 student，raw teacher prediction 不直接回流。

Finding 1 的机制是：即使 $d,\phi_1,\phi_2$ 从 $U(0,1)$ 采样，只要端点被角点锚定，同一 corner pair 的随机 votes 仍会产生短片段；若 $\theta$ 用无学习的 image level-line orientation 引导，完整、稳定线段会出现。冗余投票提供启动信号，EMA teacher 随训练逐步变准。

**输出。** validated segments $L=\{\ell_j=(x_1,y_1,x_2,y_2)\}$、validated target field $\bar a(p)$ 和 boundary token set $B$。

### 模块 4：a-contrario NFA Validator

**物理/数学意义。** 防止 teacher 把纹理、脸部对角线等 hallucinated structure 当伪标签反复自我强化。

**输入。** 候选 segment，共 $n$ 个 support pixels，其中 $k$ 个方向在容差内对齐；随机对齐概率 $p$，候选测试数 $N_t$。

**内部机制。** 零假设是 orientation 均匀，假警报期望：

$$
\operatorname{NFA}(n,k)=N_t\sum_{i=k}^{n}{n\choose i}p^i(1-p)^{n-i}.\tag{11}
$$

接受条件 NFA $\le\epsilon$，论文取 $\epsilon=1$。实现用 3 px rectangle，orientation modulo $\pi$，容差 $\pi/16$，故 $p=1/16$；$N_t=(HW)^{5/2}$；aligned density 低于 0.5 先删；一张图保留少于 10 条 validated segments 时，本 iteration 不计算 boundary loss。传统 LSD 的 region growing 串行且 seed-order dependent；本文先由 dense endpoint + corner pair 生成候选，再让每个 GPU thread 独立做一个 binomial-tail reduction，从而 batch parallel。

**输出。** 统计显著的 segment list。Appendix Fig.11 显示：强角点时 validation 只去少量残留；弱 field-derived corner 时删除 72% 伪候选后仍恢复近似相同线段；两种 safeguard 同时去掉才崩。

### 模块 5：Boundary-Forcing Mask 与 Geometry Routing

**物理/数学意义。** “遮哪里”和“预测什么”必须同时改变。只遮边界、仍用 semantic target，Table 1 反而略差。

**输入。** random mask $M$、validated segment raster map、patch grid。

**内部机制。** raster map 经 max-pooling 到 token grid：

$$B=\{i:\text{predicted boundary intersects patch}(i)\},\tag{5}$$
$$M^+=M\cup B.\tag{6}$$

student 在 $M^+$ 的 token 全部换成 shared mask token。所有 $i\in M^+$ 优化 iBOT semantic CE；$p\in B$ 的 sub-token positions 额外优化 boundary categorical CE；class token 优化 DINO。它不是把边界 token 从 semantic branch 拿走，而是 dual target，避免学成纯几何 edge code。

**输出。** masked student view，以及每个位置明确的 loss routing mask。

### 模块 6：Categorical Boundary Target 与总损失

**物理/数学意义。** 连续 $L_1/L_2$ teacher field 会随 EMA target 漂移并塌缩；分类分布能使用 DINO 已验证的 centering/sharpening，还能表达“uniform = no structure”。

**输入。** validated teacher scalar $a_c(p)$，channel $c\in\{d,\theta,\phi_1,\phi_2\}$，bin centers $k=1\ldots K$。

**内部机制。** 构造窄 soft label：

$$
\bar y_k^c(p)\propto\exp\left[-\delta_c(k,a_c(p))^2/\tau_l\right],\tag{8}
$$

$\theta$ 的 $\delta$ 是 circular arc distance。student prediction $\hat y^c(p)$ 的 boundary CE：

$$
\mathcal L_{bnd}=-\frac1{|B|}\sum_{p\in B}\sum_c(\bar y^c(p))^\top\log\hat y^c(p).\tag{9}
$$

完整目标：

$$
\mathcal L=\mathcal L_{DINO}+\lambda_i\mathcal L_{iBOT}+\lambda_b\mathcal L_{bnd}+\lambda_k\mathcal L_{KoLeo}.\tag{10}
$$

teacher 所有 target stop-gradient；optimizer 更新 student 后再 EMA 更新 teacher。boundary target 只为分辨率足够的 global crops 生成；local crops 只做 image-level distillation。

**输出。** student gradients，更新可同时表达 semantic region 与 boundary geometry 的 patch backbone。

### 模块 7：规模化训练系统

**物理/数学意义。** 在线 segment decoding/NFA 若每图跑 CPU，会让方法无法成为 foundation pretraining；系统实现是算法可行性的组成部分。

**输入。** 2B raw web images 经 DINOv2 ViT-B embedding retrieval 和去重得到 160.75M corpus：约 143M retrieval pools，加 ImageNet-21k 13.15M、IN1k 1.28M、GLDv2 1.58M、Mapillary 1.46M。

**内部机制。** ViT-g/16 约 1.1B，SwiGLU、fp32 RoPE、4 register tokens；FSDP + bf16 + memory-efficient attention。训练三阶段：300k low-resolution self-distillation、100k Gram anchoring、100k 512px adaptation，global batch 3072。boundary head 只在 $B$ 展开；soft label + CE 融合 kernel；corner-endpoint distance 与 argmin fused，避免二次内存；decode/NFA/rerender 全 CUDA batch，无 host sync。

**输出。** giant teacher，以及蒸馏的 ViT-L/B/S family。

## 4. 🎬 端到端运行实例（End-to-End Running Example）

### 场景设定

输入一张厨房图：透明玻璃杯位于木桌前景，杯后有墙面和窗框。机器人后续需要估计杯缘和桌面深度，因此杯—背景、桌—墙和窗框边界比墙面内部纹理更重要。训练 crop 为 $512\times512$，patch size 16，产生 $32\times32=1024$ patch tokens；boundary field stride 2，对应 $256\times256$ sub-token positions。

### 数据流转推演

**Step 1：多视图与 teacher forward。** 数据增强产生两张 global crops 和若干 local crops。unmasked global crop 输入 EMA teacher；ViT 输出 1024 patch features。boundary head 将每个 patch token 通过三层 MLP 展开为 $8\times8$ tile，每个位置输出 4×32 个 cosine logits，经 expectation 得到 $(d,\theta,\phi_1,\phi_2)$。

**Step 2：候选线段解码。** frozen corner detector 给出杯口两端、桌角、窗框交点。每个 field position 解码一条 chord，端点 snap 到最近 corner；属于杯口两端 corner pair 的大量 positions 对同一 segment 投票，偶然穿过杯面的对角 proposal 也可能形成候选。

**Step 3：统计验证。** 对每条候选，在 3 px 支撑带内计算 level-line orientation。杯缘候选有大量方向一致像素，binomial tail 很小，NFA≤1，被接受；杯面对角线没有真实梯度支撑，NFA>1，被删除。survivors rerender 成 clean categorical field。

**Step 4：生成 forced mask。** clean segments max-pool 到 $32\times32$ grid，得到 $B$：杯缘、桌边、窗框对应的 tokens。随机 block mask $M$ 再与 $B$ 取并集；即使随机 mask 没选中杯缘，它仍必然被遮。

**Step 5：student forward 与 loss routing。** student 看 masked global crop。class token 对齐另一视图 teacher DINO prototype；所有 $M^+$ patch 对齐 teacher iBOT semantic distribution；杯缘等 $B$ 位置还需输出正确 distance/direction/endpoints categorical distribution。于是 student 不能只回答“这是玻璃杯”，还必须从相邻杯身/背景推断杯缘如何穿过被遮 patch。

**Step 6：更新。** Eq.(10) 反传只更新 student；teacher 无梯度，以 Eq.(1) EMA 跟随。训练早期 corner+NFA 提供粗边界，后期 teacher field 变准，伪标签更细，构成 self-paced target refinement。

**Step 7：下游 Forward。** 预训练结束后冻结 encoder。深度任务把新 RGB 图像编码成 patch features，单线性层直接回归每 patch depth；杯内/桌面 feature 平滑、杯缘/遮挡处 feature 突变，因此上采样后深度边界更锐。LingBot-Depth 2.0 则把 RGB tokens 与未 mask 的 raw-depth tokens共同送入 encoder，由 ConvStack decoder 恢复完整 depth map。

## 实验设置、数据集、基线、指标

### Frozen dense evaluation

- Depth：NYUv2、KITTI；冻结 backbone，只训单线性层，报告 RMSE↓。不用 DPT 或多层聚合，避免 decoder 掩盖 representation 差异。
- Semantic segmentation：ADE20K、VOC12、Cityscapes；单线性层，报告 mIoU↑。patch-14/16 调整输入分辨率使 token grid 对齐。
- Video object segmentation：DAVIS-2017、YouTube-VOS；第一帧 GT mask 通过 frozen patch top-k attention 传播，不 finetune，报告 $J\&F$。
- Global semantics：ImageNet-1K linear probe 与 kNN top-1。

### Depth completion

Block-mask：DIODE-In/Out、iBims-1、NYU；Sparse：VOID、iBims-1、NYU、ETH3D；Real sensor：HAMMER D435/L515/ToF、ClearGrasp D415/D435、自采 LingBot D415/D435/D455。指标 RMSE↓ / $D_{1.05}$↑，基线 CDMs、OMNI-DC、Any2Full、PriorDA、LingBot-Depth 1.0。

## 主要结果、消融或对比

### 方法因果消融（Table 1）

| 配置 | IN1K kNN | NYUv2 $\delta_1$ | RMSE↓ |
| --- | ---: | ---: | ---: |
| DINO+iBOT baseline | 81.6 | 81.4 | 0.474 |
| + categorical boundary target | 81.8 | 84.4 | 0.446 |
| + dual supervision | 82.0 | 84.7 | 0.443 |
| + RoPE final recipe | 82.4 | 84.9 | 0.440 |
| forcing + semantic target only | 81.4 | 81.2 | 0.481 |

这张表是全文最关键的机制证据：收益来自 geometric target，不是简单把 hard token 遮住；semantic+geometry 双监督没有产生预期中的冲突。

### Giant frozen features

NYUv2 linear RMSE 0.296，优于 7B DINOv3 0.309、2B V-JEPA2.1 0.307、DINOv2 0.372；KITTI 2.552，在 <2B 模型中最佳，但落后 7B DINOv3 2.346。ADE20K mIoU 53.5，低于 7B DINOv3 55.9 左右与 DINOv3-H+ 54.8，但比 DINOv2 49.5 高 4 点。结论是 dense geometry 优势强于 global semantics 优势，不能笼统说“所有视觉任务 SOTA”。

Video label propagation：LingBot-Vision 70.0/73.5，接近 7B DINOv3 的 71.1/74.1；相同 1B 规模下比 DINOv2 高 6.1/7.9。ImageNet giant linear/kNN 为 86.32/83.39，略低于 DINOv2 87.00/83.68，更低于 DINOv3 87.87/85.68，明确呈现 spatial–global 资源分配差异。

### Distilled family（Table 5）

ViT-L：IN1K linear 86.38，NYU 0.310，约 0.3B student 的 NYU RMSE 几乎等于 7B DINOv3 0.309，参数约少 23×；ViT-B 在同规模取得 linear 85.05、NYU 0.339；ViT-S linear 82.22、NYU 0.383，但 KITTI/Cityscapes 不再全面领先。dense advantage 大体可蒸馏，但不是所有小模型/数据集都保持。

### LingBot-Depth 2.0

同 MDM pipeline 的初始化隔离实验中，ViT-L LingBot-Vision 对 DINOv2：DIODE-In 0.094 vs 0.152，DIODE-Out 2.771 vs 3.192，NYU block 0.145 vs 0.169；并非每格都赢，如 ETH3D sparse 0.414 弱于 DINOv2 0.385。训练数据从 3M→20M→150M 时，LingBot initialization 的 $D_{1.02}$ 从 0.692→0.777→0.795，DINOv2 从 0.689→0.752→0.755，差距随数据放大。

最终 2.0 在 Table 8 八个 block/sparse benchmark 中七个 RMSE 最佳：DIODE-In 从 v1 0.132 降至 0.062，DIODE-Out 3.404→2.440；ETH3D 仍是 v1 更好。真实相机八配置六项最佳，ClearGrasp 透明物体 D415/D435 RMSE 0.010/0.012。ViT-g 并非各格都胜 ViT-L，ClearGrasp 反而偏向 L，说明更大 backbone 不是单调保证。

## 图表、公式与表格线索

| 线索 | 阅读问题 |
| --- | --- |
| Fig.2 | random mask、boundary forcing、field target 三者如何区分？ |
| Figs.3--5 | 随机场为何能从角点产生线；field 四通道如何 vote；在线 target 如何清洗？ |
| Eq.(8)--(10) | categorical label、boundary CE 与总目标如何连接？ |
| Appendix Eq.(11) / Fig.11 | NFA 零假设与两个 safeguard 各自有何作用？ |
| Table 1 | hard mask 还是 geometric target 真正贡献收益？ |
| Tables 2--5 | dense、video、global 三类能力是否同时保持？ |
| Tables 6--8 / Fig.8 | encoder initialization 与下游数据 scaling 是否相乘？ |

## 主张—证据—边界矩阵

| 主张 | 证据 | 解释 | 边界 |
| --- | --- | --- | --- |
| raw image 可自举 boundary。 | Finding 1、Figs.3/5/11。 | corner+vote+NFA 提供早期信号。 | 仍使用冻结 corner detector；“完全无外部组件”需加限定。 |
| categorical field 防塌缩。 | §3.3 与训练成功。 | 可复用 centering/sharpening。 | 缺少连续回归 collapse 的定量曲线。 |
| boundary objective 改善 dense feature。 | Table 1、NYU/seg/VOS。 | 因果消融与多任务结果一致。 | 数据 curation、RoPE/Gram anchoring 也贡献 scaled result。 |
| 更少数据/参数胜更大模型。 | 161M vs DINOv3 corpus；NYU 结果。 | 目标更贴合 dense task。 | 不应外推为总体训练更便宜，在线 boundary pipeline 仍有成本。 |
| 对具身空间感知有价值。 | Depth 2.0 14 benchmarks。 | 透明/反光/缺失区域尤其强。 | 尚无闭环 robot manipulation success 的直接对照。 |

## 局限与可追问点

1. **Corner detector 依赖。** 虽然只是一层冻结 ViT，仍是外部固定模块；其训练来源、跨域角点召回决定 cold-start 上限。
2. **线段先验。** 曲线由短线段链近似；自然纹理、毛发、透明边缘、弱对比轮廓是否会产生过多/过少 candidates，缺少按边界类型分析。
3. **伪标签确认偏差。** teacher 只会强化自己能解码且通过 orientation test 的边界；无明显强度梯度但语义/深度突变的边界可能被系统忽略。
4. **NFA 的“无参数”有实现常数。** $\epsilon=1$ 虽经典，但仍有 3 px width、$\pi/16$ tolerance、0.5 density、至少 10 segments 等固定选择。
5. **规模化归因。** final recipe 还有 RoPE、Gram anchoring、curated retrieval data；Table 1 能隔离部分机制，但 1B 结果不是纯 boundary loss 的单变量实验。
6. **机器人证据间接。** Depth completion 是强具身感知 proxy，却没有证明 policy 因此在闭环抓取/导航上提升多少。

## 与当前库的连接

- 与 [[@wu2026lingbot-vla2]]：后者的 dual-query 用 LingBot-Depth 给几何监督；本文说明 boundary-native encoder 为何可能生成更适合 manipulation 的 depth representation。
- 与 [[@zhang2026lingbot-va2]]：VA 2.0 的 semantic visual-action tokenizer 解决视觉 latent 与 action 的语义对齐；本文处理的是同一 latent 中的空间边界保真，二者分别补“动作语义”和“几何精度”。
- 与 world model 路线：如果 future latent 没有 sharp geometry，预测视频看似合理也可能在接触点上错；LingBot-Vision 提供一种改善 world-state token 空间结构的预训练原则。
- 与触觉路线：boundary token 对应接触/遮挡变化高发位置，未来可与 [[@park2026tactx-learning-shared-tactile]] 等跨传感器表征结合，但本文没有触觉实验。

## 精读路线 / 为什么需要回看

快速理解：Fig.2 → Eq.(5)(6) → Fig.4 → Eq.(8)(9) → Fig.5 → Table 1。复现方法：再读 §3.4、§4.2--4.3 和 Appendix B，逐项实现 tile unfold、circular bins、corner snap、vote graph、NFA CUDA reduction、rerender 与 loss routing。评估主张：按 Table 1（机制）→ Table 2/3（frozen dense/video）→ Table 4/5（语义代价与蒸馏）→ Table 6--8（下游应用）的顺序，避免只引用最亮眼的 NYUv2 数字。
