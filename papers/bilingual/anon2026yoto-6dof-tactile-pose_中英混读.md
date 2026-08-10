---
tags:
  - bilingual-reading
  - deep-reading
paper: "[[@anon2026yoto-6dof-tactile-pose]]"
source_pdf: "[[papers/pdfs/anon2026yoto-6dof-tactile-pose.pdf]]"
images: "papers/images/anon2026yoto-6dof-tactile-pose/"
image_index: "[[papers/images/anon2026yoto-6dof-tactile-pose/index.md]]"
created: 2026-07-08
reading_mode: 生成式精读（逐节读原文 + 读图）
---

# You Only Touch Once: 6-DoF Object Pose Estimation from Single Tactile Contact

paper:: [[@anon2026yoto-6dof-tactile-pose]]
pdf:: [[papers/pdfs/anon2026yoto-6dof-tactile-pose.pdf]]
images:: [[papers/images/anon2026yoto-6dof-tactile-pose/index.md]]

> 匿名投稿（CoRL 2026 under review，"Do not distribute"）。作者自称基于其 prior work **InvariantCloud [31]**（arXiv:2605.25216, 2026，用于把 GelSight 接触重建成点云）。无 arXiv 号；元数据来自 PDF（confidence=medium）。

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| 6-DoF object pose | 6 自由度物体位姿 | 本文要估计的量 $\mathbf T^W_O\in\mathrm{SE}(3)$：物体在世界系下的旋转 + 平移。 |
| tactile-only / single touch | 纯触觉 / 单次接触 | 本文卖点：**不用视觉、不用接触历史、不用物体运动**，一对传感器**同时**碰一次就出绝对位姿。 |
| GelSight (Mini) | GelSight（Mini）视觉触觉传感器 | 弹性凝胶 + 内置相机，把接触处的**局部几何**成像；本文每次用左右两枚。 |
| localization ambiguity | 定位歧义 | 单个触点只看到一小块表面，**同一局部几何在物体多处重复** → 单帧触觉定位的根本难点。 |
| local 3D point cloud | 局部 3D 点云 | 本文对触点的表示：把 GelSight 接触重建成带法向的点云 $\mathbf X_s$（而非低维描述子或触觉图像）。 |
| surface block $\mathcal B_i$ | 表面 block | 把物体 parent 点云按主轴切成的网格块；**把"全表面稠密匹配"降为"块检索 + 块内偏移回归"**。 |
| coarse-to-fine localization | 粗到精定位 | coarse 用相似度选候选块（top-K），fine 在候选块内回归精确接触点 + 置信度。 |
| normal-aware SVD solver | 法向感知 SVD 解算器 | 本文位姿求解核心：两触点只定"接触-接触轴"、绕轴旋转有歧义，**加入法向**后用正交 Procrustes 闭式一步解出 $\mathrm{SE}(3)$。 |
| kNN-aggregated normal | kNN 聚合法向 | 用预测触点最近 $k{=}20$ 个表面点的法向平均，比"整块一个法向"更局部忠实。 |
| virtual contact / two-stage training | 虚拟接触 / 两阶段训练 | 从物体模型自动采虚拟触觉 patch 做 Stage1 稠密预训练，再用少量真实 GelSight 做 Stage2 微调 → 省真实数据。 |
| consumer-grade scan vs CAD mesh | 消费级扫描 vs CAD 网格 | 本文去掉"必须有 CAD"的前提：可用手机/消费级 3D 扫描重建的 mesh，并量化与 CAD 的差距。 |
| FoundationPose | FoundationPose（视觉基线） | 代表性视觉 6-DoF 位姿估计器，用标定 RGB-D；本文用它作遮挡对照。 |
| InvariantCloud [31] | InvariantCloud（作者 prior work） | 把 GelSight 接触重建成"全局不变、唯一索引"点云的框架，本文用它做接触点云重建。 |

## 摘要

> 精确的 6-DoF 物体位姿估计是机器人操作的基础，但基于视觉的方法在**遮挡、弱光、反光/透明表面**下常失效。本文提出 **YOTO**——一个纯触觉位姿估计系统，从**一对同时接触**恢复完整 6-DoF 物体位姿，**无需接触历史**。YOTO 把每个触点表示为局部 3D 点云，用粗到精网络把它定位到物体表面；两个定位好的触点连同标定的传感器位姿，被送入一个**闭式的法向感知 SVD 解算器**，一步恢复完整 6-DoF 位姿。为降低真实数据需求，定位网络先在从物体模型采样的**虚拟触觉 patch** 上预训练、再用少量真实接触微调。作者进一步展示 YOTO 可运行在**消费级移动扫描重建**的物体模型上，并量化其相对 CAD 模型的差距。在四个几何各异物体上的实验表明触点定位与位姿估计都准确，**在视觉不可靠时尤其优于视觉与触觉/几何基线**。关键词：Tactile Sensing、Pose Estimation、Contact Localization、Sim-to-Real Transfer、Robotic Manipulation。

中文解读：这段摘要的写作动作是**先指出视觉位姿估计恰恰在"操作最需要它"的时候失效（遮挡/弱光/反光透明），再把触觉的短板（局部歧义、通常要接触历史）当作要攻克的问题，最后给出一个"学习定位 + 解析求解"的纯触觉一次性方案**。要抓住三个"不需要"：**不需要视觉、不需要接触历史、不需要物体运动**——这把 YOTO 和依赖 tracking/sliding 的触觉方法明确切开。

## 论文主线

![[papers/images/anon2026yoto-6dof-tactile-pose/page1_fig1.jpeg|860]]

**Figure 1 / 全文动机与总览。** 左/中两列是电钻（drill）在 **Non-occluded** 与 **Occluded** 两种视角下的对比：**YOTO（上排，RGB 三色轴）始终锚定在物体上**，而 **FoundationPose（下排，品红轴）**在遮挡下漂移到遮挡物（手）或错误的 canonical 视角；Mocap GT 为黄色轴。右侧是方法示意：在扫描的电钻模型上显示**预测触点（蓝）vs GT 触点区域（红）**、kNN 聚合的表面法向（品红箭头），以及底部左右两枚 GelSight 的原始触觉图像（Left/Right touch）。这张图一眼给出全文因果：**当视觉被手/夹爪挡住时，只在接触点观测几何的触觉反而稳。**

这篇论文的核心问题是：**6-DoF 物体位姿是几乎所有 contact-rich 操作（抓取、放置、in-hand 重定向、工具使用）的基础，但主流"RGB(-D) + 学习位姿估计"恰好在操作最需要它时失效**——抓取时机械手/夹爪遮挡物体、透明/镜面/低纹理表面破坏光度假设、弱光或不均匀光照污染输入。触觉只在**接触点**观测几何，对这三种失效天然免疫，但它带来一个互补的难题：**定位歧义**——单个触点只看到一小块表面 patch，而同一局部几何可能出现在物体的很多位置；现有触觉方法要么匹配低维接触表示 [5]、要么依赖接触历史做 tracking [6]，因而在几何复杂物体上难做单帧位姿估计。

YOTO 的回答是一个纯触觉系统，从**一次双 GelSight 同时接触**恢复**绝对** 6-DoF 位姿。它把每个触点表示为 3D 点云、用粗到精网络定位到物体表面；**物体表面被切成 block 点云，把"全表面全局定位"降为"局部表面区域检索 + 块内偏移回归"**；两个定位好的触点，连同从各触点周围 kNN 聚合的表面法向、以及标定的传感器位姿，被送入一个闭式的法向感知 SVD 解算器。

阅读时要盯住一句话：**本文真正的机制新意不是"触觉能估位姿"（前人做过），而是把问题拆成"learned 几何检索定位 + analytic 一步解析求解"两块，并用法向消除只有两点约束时的绕轴旋转歧义。** 后面每个组件都对应这条主线。作者把贡献列为四点：**System**（单次双传感器接触、无历史/运动/视觉恢复绝对位姿）、**Method**（surface-block 表示的粗到精定位 + 法向感知双触点 SVD）、**Data pipeline**（自动虚拟接触生成 + 两阶段训练做 sim-to-real）、**Benchmark**（四物体、CAD 与消费级扫描模型、视觉退化下尤其有竞争力）。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| **System**：单次双传感器接触恢复绝对 6-DoF，无接触历史 / 物体运动 / 视觉。 | §3.4，Eq.(9)–(12)，Fig.2③。 | Table 2 遮挡下 YOTO 3.52mm/3.56° 几乎不受影响。 | 卖点清晰、证据强；但仅 4 物体、需每物体微调。 |
| **Method**：surface-block 表示 → 粗到精 3D 触点定位，配法向感知双触点 SVD。 | §3.1–3.4，Eq.(1)–(3)、(9)–(12)，Fig.3。 | Table 1 定位 4.78mm（<1cm）；ICP 52.81mm。 | 方法优雅（learned 检索 + analytic 求解解耦），扎实。 |
| **Data pipeline**：自动虚拟接触生成 + 两阶段训练，limited 真实数据做 sim-to-real。 | §3.1、§3.3，Eq.(4)–(8)。 | Table 1："virtual only" 24.65mm → 加真实微调 4.78mm（误差降 ~5×）。 | 真实微调必要性有直接消融支撑。 |
| **Benchmark**：CAD 与消费级扫描模型、对比视觉/触觉基线，视觉退化下尤优。 | §4，Table 1/2/3，Fig.4。 | 遮挡下 FoundationPose 涨 15.1×/15.7×，YOTO 不变。 | 结论成立；但无公开可复现的同设定触觉基线，只能对 ICP/FoundationPose。 |

## 结构地图

| 原文位置 | 作者在这一部分做什么 | 与全文主线的关系 | 关键图表 / 公式 |
| --- | --- | --- | --- |
| §1 Introduction | 指出视觉位姿在遮挡/弱光/反光失效、触觉有定位歧义，提出 YOTO 与四点贡献。 | 定义问题入口与卖点（三个"不需要"）。 | Fig.1 |
| §2 Related Work | 梳理视觉/视触觉位姿、触觉接触位姿、触觉 tracking 三条线，定位自己为"单次双触点绝对位姿"。 | 把 YOTO 与依赖 history/sliding 的方法切开。 | 引用 [1–18] |
| §3.1 Surface Representation | parent 点云 + surface block 分解 + 虚拟接触生成。 | 把稠密匹配降为块检索 + 偏移回归，并造预训练监督。 | Fig.2①；block 中心 $c_i^O$、$\Delta p^O$ |
| §3.2 Coarse-to-Fine Network | 双共享编码器；coarse 相似度选块 top-K，fine 回归 offset + confidence，kNN 聚合法向。 | 解决"这个 patch 在物体表面哪里"。 | Fig.3；Eq.(1)(2)(3) |
| §3.3 Two-Stage Training | Stage1 虚拟预训练、Stage2 虚拟+真实微调；块分类 + margin + smooth-ℓ1 损失。 | 用少量真实数据跨 sim-to-real。 | Eq.(4)–(8) |
| §3.4 Dual-Contact Pose Recovery | 两触点 + 法向 → 正交 Procrustes 闭式 SVD 解 $\hat R$、再对齐 $\hat t$。 | 把定位结果解析地变成 6-DoF 位姿；法向消歧。 | Eq.(9)–(12) |
| §4.1 Localization Accuracy | 每物体 10 触点测欧氏定位误差；对 ICP + 两个消融。 | 单独验证定位模块。 | Table 1 |
| §4.2 Pose under Occlusion | clear vs occluded 对 FoundationPose。 | 主结果：视觉退化下触觉的优势。 | Table 2、Fig.1 |
| §4.3 Dynamic Tracking | 单次接触开环追踪 SE(3) 轨迹。 | 证明"一次触碰足以支撑持续追踪"。 | Table 3、Fig.4 |
| §5 Conclusion & Limitations | 收束；承认每物体微调、near-coaxial 退化、rigid-grasp 漂移。 | 划边界与后续方向。 | —— |

## 按原文 section 精读

### 1. Introduction / 视觉恰在最需要时失效，触觉补位但有歧义

高层故事流：introduction 的关键动作是**把"视觉位姿很强"与"视觉位姿在操作场景里不可靠"这对张力讲清楚**。主流范式（RGB/RGB-D + 学习位姿 [1,2,3,4]）在物体清晰可见时能到毫米级，但"these methods degrade precisely in the regimes where manipulation most needs them"——手/夹爪遮挡、透明镜面低纹理破坏光度假设、弱光污染输入。触觉只在接触点观测几何、对这三种失效鲁棒，"but introduces a complementary challenge"：**tactile pose estimation faces a severe localization ambiguity**——单触点只看一小块 patch，同一局部几何可能出现在物体多处；现有方法要么匹配低维接触表示 [5]、要么靠接触历史 tracking [6]。作者随后点出一个实用痛点：真实 GelSight 数据贵、且通常依赖每个目标的手工 CAD——YOTO 用"虚拟预训练 + 少量真实微调 + 可用消费级扫描模型"两阶段管线同时解决。

关键证据 / 图表 / 公式：Fig.1 是全文缩影（遮挡列直接对应 §4.2 的 Table 2）。

回看重点：introduction 把问题定义得很干净，但要注意它自选的战场是"视觉不可靠"——在视觉清晰时触觉是否值得，需要看 Table 2 的 clear 行（结论是 clear 时 YOTO 也略优，但差距不大）。

### 2. Related Work / 三条线里的落点

高层故事流：三段。**Vision-based & visuo-tactile pose**——从模板匹配 [7]、直接回归 [1]、隐式嵌入 [8]、keypoint voting [2]，到 foundation-model（FoundationPose [3,4]）；视触觉方法融合相机 + 触觉做 in-hand 位姿/形状重建/neural-field [11,12,13]。**YOTO 反其道：纯触觉、单次双触点、绝对位姿。** **Tactile pose from contact**——早期按时间概率累积接触证据 [14]；Tac2Pose [5,15] 学 object-specific 嵌入、把触觉观测匹配到位姿假设库；Caddeo [16] 在已知 mesh 上采候选接触、用触觉图像特征 + 几何约束 + 优化 refine。**YOTO 改为把接触表示成 3D 点云、定位到 surface block、从两触点 + 法向 + 标定位姿解析求解。** **Tactile tracking & temporal reasoning**——PatchGraph [17]、MidasTouch [18]（对 sliding touch 做粒子滤波）、NormalFlow [6]（从触觉流 tracking）都利用序列/滑动/初始 tracking；**YOTO 处理互补设定：从一次同时双触点估计绝对 6-DoF，无 sliding、无历史、无初始位姿。**

回看重点：related work 的价值在于把 YOTO 的"单次、绝对、无历史"三性坐标钉死——这是判断它新意与适用边界的关键。

### 3. From Tactile Contacts to 6-DoF Pose / 方法

给定物体模型 $\mathcal M$ 与一次同时双 GelSight 接触，YOTO 输出 $\mathbf T^W_O\in\mathrm{SE}(3)$。Fig.2 三段：表面表示（3.1）、粗到精定位（3.2–3.3）、SVD 位姿恢复（3.4）。

![[papers/images/anon2026yoto-6dof-tactile-pose/page3_fig1.jpeg|880]]

**Figure 2 / 系统 pipeline（三段）。** ①**Surface Model Processing**：CAD 或重建 mesh $\mathcal M$ → mesh-to-point-cloud 采样 → parent 点云 $\mathcal P$ →（上）surface partitioning 得 surface blocks $\{\mathcal B_i\}$、（下）采 virtual local tactile point clouds。②**Tactile Surface Localization Learning**：virtual patch + surface blocks 进 Localization Network $f_\theta$（tactile encoder / surface block matching / contact offset regression），**Stage1 虚拟预训练**得 $\theta_0$，**Stage2 few-shot 真实微调**（橙色回路）得 $\theta^\*$。③**Normal-Aware Dual-Contact Pose Recovery**：Dual GelSight 接触物体 → 双触点点云 $X_L,X_R$ + 标定传感器位姿 $P_L^O,P_R^O$ + block 导出法向 $n_L^O,n_R^O$ → 用 $\theta^\*$ 出 object-frame 触点与法向 → **SVD solution + contact alignment** → 6-DoF 位姿。

#### 3.1 Surface Representation & Virtual Contact Generation / 表面表示与虚拟接触

从 $\mathcal M$ 采 parent 表面点云 $\mathcal P=\{(\mathbf x_j,\mathbf n_j)\}_{j=1}^N$（物体系点 + 法向）。**输入可以是高保真 CAD、也可以是消费级 3D 扫描重建的 mesh，走同一管线**——这就去掉了 CAD 前提。为缩小搜索空间，把 $\mathcal P$ 沿物体主轴切成 surface blocks $\{\mathcal B_i\}_{i=1}^{N_B}$，每块存其表面点、法向和物体系中心 $\mathbf c_i^O$。这把"全表面稠密匹配"变成"块检索 + 块内局部偏移回归"。虚拟触觉点云从 $\mathcal P$ 的局部邻域采、支撑匹配 GelSight footprint；每个虚拟样本被赋一个主导块索引 $i^\*$、物体系接触中心 $\mathbf p^O$、偏移 $\Delta\mathbf p^O=\mathbf p^O-\mathbf c_{i^\*}^O$，用于监督 coarse 检索与 fine 回归。

#### 3.2 Coarse-to-Fine Contact Localization Network / 粗到精定位

![[papers/images/anon2026yoto-6dof-tactile-pose/page4_fig1.jpeg|880]]

**Figure 3 / 粗到精定位网络。** 左 INPUTS：触觉点云 $X_s$（coords + normals）与 surface blocks $\mathcal B_i$（block centers + point normals）。中 FEATURE ENCODING & COARSE RETRIEVAL：两个**权重共享**的点云编码器（point MLP + multi-scale kNN aggregation + pooling）分别出 $q_s,\{b_i\}$，用 cosine similarity + temperature 打分选 Top-K candidate blocks，并做 neighborhood retrieval（best + nearby）。右 FINE LOCALIZATION：offset + confidence head 对每个候选出 $(\Delta\hat p_{i,k},\gamma_{s,k})$，选 $\max_k(a_{i_k}+\gamma_{s,k})$ 得 localized contact + point normals。

给定来自传感器 $s\in\{L,R\}$ 的触觉点云 $\mathbf X_s$ 与 surface blocks $\{\mathcal B_i\}$，网络预测物体系接触位置 $\hat{\mathbf p}_s^O$。两支权重共享的轻量点云编码器 [22,23]（PointNet/PointNet++ 式）吃 coords + per-point normals，映射到同一特征空间：触觉特征 $\mathbf q_s=\phi_t(\mathbf X_s)$、块特征 $\mathbf b_i=\phi_b(\mathcal B_i)$。**Coarse** 按归一化特征相似度给每块打分：

$$
a_i = \tau\,\frac{\mathbf q_s^\top \mathbf b_i}{\|\mathbf q_s\|_2\,\|\mathbf b_i\|_2}\tag{1}
$$

$\tau$ 是可学温度。最高分块给出初始接触区域，YOTO 用物体系中心 $\mathbf c_i^O$ 取其空间邻域、保留 top-$K$ 候选（保留多个邻近假设）。**Fine** 对每个候选块 $\mathcal B_{i_k}$ 预测局部偏移与置信度：

$$
(\Delta\hat{\mathbf p}_{s,k}^O,\ \gamma_{s,k}) = g_\theta(\mathbf q_s,\mathbf b_{i_k}),\qquad \hat{\mathbf p}_{s,k}^O = \mathbf c_{i_k}^O + \Delta\hat{\mathbf p}_{s,k}^O\tag{2}
$$

最终由 coarse 匹配分与预测置信度联合选出：

$$
k^\star = \arg\max_k\,(a_{i_k}+\gamma_{s,k}),\qquad \hat{\mathbf p}_s^O = \hat{\mathbf p}_{s,k^\star}^O\tag{3}
$$

定位后，YOTO 用 $\hat{\mathbf p}_s^O$ 最近 $k$ 个表面点（**$k=20$**）的 parent 法向平均，估计接触点法向 $\hat{\mathbf n}_s^O$——这个 kNN 聚合法向比"整块一个法向"更局部忠实，连同接触位置传给 §3.4 的位姿求解器。

#### 3.3 Two-Stage Training Objective / 两阶段训练

Stage1 在从已知表面位置采的虚拟触觉点云上预训练（监督块检索 + 物体系接触位置回归）；Stage2 用**虚拟 + 真实 GelSight 混合**微调（虚拟保稠密表面覆盖、真实适配传感伪影与残余 sim-to-real，**真实样本给更大损失权重**）。GT 接触位置 $\mathbf p_s^O$ 定义 GT 块标签 $y_s$ 与偏移 $\Delta\mathbf p_s^O=\mathbf p_s^O-\mathbf c_{y_s}^O$（Eq.4）。coarse 用块分类损失 $\mathcal L_{\text{cls}}=\mathrm{CE}(\mathbf a,y_s)$（Eq.5）；为在候选选择时保持正确块有竞争力，加最高分块的 margin 损失

$$
\mathcal L_{\text{topK}} = [a_{\hat i}-a_{y_s}+m_1]_+ + [a_{i_K}-a_{y_s}+m_2]_+\tag{6}
$$

（$\hat i$ 最高分块、$i_K$ 保留 top-K 中最低分块，$[\cdot]_+=\max(\cdot,0)$）。fine 用 smooth-ℓ1：

$$
\mathcal L_{\text{pos}}=\sum_{k=1}^K w_k\,\mathrm{SmoothL1}(\hat{\mathbf p}_{s,k}^O,\mathbf p_s^O)\tag{7}
$$

$w_k$ 偏好匹配置信更高、块心更近的候选。全目标 $\mathcal L=\lambda_c\mathcal L_{\text{cls}}+\lambda_k\mathcal L_{\text{topK}}+\lambda_p\mathcal L_{\text{pos}}$（Eq.8）。推理时对左右传感器**各自独立**预测 $\hat{\mathbf p}_s^O$，连同 kNN 法向传给解算器。

#### 3.4 6-DoF Pose Recovery from Dual Contacts / 法向感知的闭式求解

定位网络对每个 $s\in\{L,R\}$ 给出物体系接触 $\hat{\mathbf p}_s^O$ 与局部 kNN 聚合外法向 $\hat{\mathbf n}_s^O$。YOTO 用闭式解把它们转成 $\mathrm{SE}(3)$ 位姿。**为什么需要法向**：两点对应只约束了"接触-接触轴"，但绕该轴的旋转仍歧义。设 $\mathbf p_L^W,\mathbf p_R^W$ 为世界系接触中心（由标定的左右 GelSight 位姿算得），构造物体系/世界系位移方向

$$
\mathbf d^O=\frac{\hat{\mathbf p}_R^O-\hat{\mathbf p}_L^O}{\|\hat{\mathbf p}_R^O-\hat{\mathbf p}_L^O\|_2},\qquad \mathbf d^W=\frac{\mathbf p_R^W-\mathbf p_L^W}{\|\mathbf p_R^W-\mathbf p_L^W\|_2}\tag{9}
$$

连同表面法向组成两组对应方向

$$
\mathbf Q^O=[\,\mathbf d^O\ \ \hat{\mathbf n}_L^O\ \ \hat{\mathbf n}_R^O\,],\qquad \mathbf Q^W=[\,\mathbf d^W\ \ \mathbf n_L^W\ \ \mathbf n_R^W\,]\tag{10}
$$

$\mathbf n_L^W,\mathbf n_R^W$ 来自标定的传感器朝向（世界系外向接触方向）——这类似 oriented point-pair 约束 [26]、并补充学习式点云配准 [27]，但**由稀疏触觉而非深度对应驱动**。旋转由正交 Procrustes 求解

$$
\hat{\mathbf R}=\arg\min_{\mathbf R\in\mathrm{SO}(3)}\|\mathbf Q^W-\mathbf R\mathbf Q^O\|_F^2\tag{11}
$$

有闭式 SVD 解 [28,29]。给定 $\hat{\mathbf R}$，平移由对齐两触点得到

$$
\hat{\mathbf t}=\frac12\sum_{s\in\{L,R\}}\big(\mathbf p_s^W-\hat{\mathbf R}\hat{\mathbf p}_s^O\big)\tag{12}
$$

最终位姿 $\hat{\mathbf T}_O^W=[\hat{\mathbf R},\hat{\mathbf t}]$。

论证功能表：

| 正文要点 | 承担的论证功能 | 证据位置 | 读者应注意的边界 |
| --- | --- | --- | --- |
| surface-block 表示 | 把全表面全局定位降为块检索 + 块内回归 | Fig.2①、Eq.(2) | 块划分沿主轴，依赖物体已建模 |
| coarse 相似度 + top-K 保留 | 保多个邻近假设、抗单块误检 | Eq.(1)(3)、Fig.3 | 局部自相似物体（avocado）仍可能检索进错块 |
| kNN 聚合法向 | 给 SVD 提供局部忠实法向、消绕轴歧义 | §3.2、§3.4 | 法向来自模型 + 定位，非直接测量 |
| 法向感知 Procrustes SVD | 一步闭式解 6-DoF，避免端到端回归不稳 | Eq.(9)–(12) | near-coaxial 双触点下退化（旋转对称物体） |

### 4. Experiments / 实验

平台：**4 个几何各异物体**（drill、squirrel、monkey、avocado），两条 6-DoF **AIRBOT Play** 臂各持一枚 **GelSight Mini** [30] 装在刚性 probe 上。**双臂**让两枚传感器从独立方向接触，避开平行夹爪那种近共轴几何（会让双触点位姿求解 ill-conditioned）。**OptiTrack** mocap 提供物体与两传感器 GT 位姿（仅评测）。每次 GelSight 接触用作者 prior 的 **InvariantCloud** 管线 [31] 转成局部点云；GT 接触位置由同步 mocap 轨迹 + 物体 mesh 自动算得。每物体虚拟预训练 + 少量真实微调。**无公开可复现的同设定（单次、双触点、无历史）触觉位姿估计器**，故对比几何 **ICP**（触觉下界）与 **FoundationPose** [3]（视觉代表）。

#### 4.1 Tactile Contact Localization Accuracy / 定位精度

![[papers/images/anon2026yoto-6dof-tactile-pose/page6_fig1.jpeg|560]]

**4.1 内插图。** 四物体两视角，预测触点（蓝）叠加在 GT 接触区域（红）上——drill 的细长体 + 显著局部几何最易定位，avocado 的表面凸起局部自相似最难。

每物体收 10 个真实 GelSight 接触（跨表面、跨双传感器），算预测触点 $\hat{\mathbf p}_s^O$ 与 mocap GT 的物体系欧氏距离（GT 仅评测、不作模型输入）。**Table 1（定位误差 mm，越低越好）**：

| Method | Avocado | Drill | Squirrel | Monkey | **All** |
| --- | ---: | ---: | ---: | ---: | ---: |
| ICP (geometry only) | 48.17±17.54 | 64.36±35.10 | 47.41±17.16 | 51.31±15.75 | 52.81±22.98 |
| YOTO (Scanned, virtual only) | 26.74±11.63 | 28.52±10.75 | 22.45±7.47 | 20.90±9.67 | 24.65±10.11 |
| YOTO (CAD mesh) | 7.22±1.56 | 5.10±2.07 | 5.43±1.97 | 4.05±2.74 | 5.45±2.35 |
| **YOTO (Scanned mesh)** | **5.97±2.54** | **3.96±1.38** | **4.81±2.16** | **4.36±2.38** | **4.78±2.21** |

三点结论：
1. **YOTO 达 sub-cm 均值定位误差（4.78mm，最差 <10mm）**，远超几何 ICP 的 52.81mm——ICP 在局部自相似表面上会陷入错误配准。
2. **去掉真实微调（"virtual only"）误差涨 5 倍以上**（24.65mm）——少量真实 GelSight 样本对跨 residual sim-to-real gap 是必要的。
3. **扫描 mesh ≈ 甚至略优于 CAD mesh（4.78 vs 5.45）**：作者解释扫描 mesh 隐含了 3D 打印层纹/表面粗糙度这些 GelSight **真实能观测**的伪影，反而更贴合真实触觉——因此全文用扫描模型。

#### 4.2 6-DoF Pose Estimation under Occlusion / 遮挡下的位姿（主结果）

对 FoundationPose [3] 在四物体、两视角（clear：顶视相机看全物体；occluded：操作者手挡住 >50% 投影面积）比较；GT 来自 OptiTrack（仅评测）。每物体/条件对在 5 个不同摆放上评测，每次是连续录制、报 per-placement 时均误差。**Table 2（YOTO 仅用触觉；FoundationPose 用标定 RGB-D）**：

**Translation error (mm)**

| Method | Cond. | Avocado | Drill | Squirrel | Monkey | **All** |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| FoundationPose | clear | 3.88 | 5.86 | 5.93 | 6.24 | 5.48 |
| FoundationPose | occluded | 82.24 | 102.36 | 72.76 | 74.35 | **82.93** |
| YOTO | clear | 1.74 | 4.88 | 4.27 | 2.77 | **3.42** |
| YOTO | occluded | 1.76 | 4.85 | 4.65 | 2.80 | **3.52** |

**Rotation error (deg)**

| Method | Cond. | Avocado | Drill | Squirrel | Monkey | **All** |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| FoundationPose | clear | 5.57 | 5.84 | 6.04 | 4.32 | 5.44 |
| FoundationPose | occluded | 92.73 | 87.81 | 88.28 | 73.44 | **85.57** |
| YOTO | clear | 1.59 | 4.78 | 4.85 | 3.11 | **3.58** |
| YOTO | occluded | 1.51 | 4.72 | 4.88 | 3.12 | **3.56** |

- **clear 视角**：两者都到 sub-cm 平移、few-degree 旋转，**YOTO 在每个物体上都优于 FoundationPose**。
- **occluded 视角**：差距骤开——**FoundationPose 平移误差涨 15.1×、旋转涨 15.7×**（→ 82.93mm / 85.57°），而 **YOTO 基本不受影响**（3.52mm / 3.56°），因为触觉输入与标定传感器位姿都不依赖相机。Fig.1 遮挡列显示 FoundationPose 的 bbox 锁到手上，而 YOTO 轴仍锚在电钻上。
- **一个反直觉的内部趋势**：与 §4.1 相反，**在孤立定位里最好的 drill，在位姿恢复里反而最难**——它旋转对称的长轴迫使近共轴双抓，欠约束绕轴旋转（在 §4.3 动态追踪里再次出现）；而 broadly curved、可非共轴接触的 **avocado 位姿误差最小**（sub-2mm / sub-2°）。

#### 4.3 Dynamic Pose Tracking from a Single Contact / 单次接触的动态追踪

静态摆放精度不保证操作中位姿仍有效（软胶形变、micro-slip、惯性加载都会侵蚀 rigid-grasp 假设）。对每个物体，双胶**建立一次接触**后，系统执行一条随机采样的双臂 SE(3) 轨迹（~100mm 平移、~10–15° 旋转），**开环**：不再感知、位姿由 live gel 位姿解析恢复。

![[papers/images/anon2026yoto-6dof-tactile-pose/page8_fig1.jpeg|880]]

**Figure 4 / 单次接触的逐帧追踪误差（上平移、下旋转；虚线 = 运动中均值，阴影尾 = 运动后 settle）。** 四物体运动中均值：Squirrel 3.52mm/6.05°、Drill 6.52mm/7.79°、Monkey 3.43mm/5.27°、Avocado 2.17mm/2.55°。每条曲线有一个 mid-motion 瞬态峰（max 7–16°）后收敛到一个 settled 尾。

**Table 3（动态追踪误差，5 次均值）**（注：首列 "Rabbit" 应即其余表的 "Squirrel"，论文命名不一致）：

| | Rabbit (=Squirrel) | Drill | Monkey | Avocado |
| --- | ---: | ---: | ---: | ---: |
| Trans. (mm) | 3.5±0.4 | 6.5±0.8 | 3.4±0.5 | 2.2±0.3 |
| Rot. (°) | 6.1±0.7 | 7.8±1.1 | 5.3±0.6 | 2.6±0.4 |

- 平移 <7mm、旋转 <8° across all；**drill 误差最大**（细长体 + 偏移不稳定质心，绕抓取轴的转动惯量与重力扭矩放大了 gel-物体界面滑移）。
- 峰来自惯性加载 + 双臂异步，但**有界不发散**；settled 尾反映**塑性 grasp drift**（小、1–3mm/1–2°，且可从物体几何预测）——这把 YOTO 与"反馈丢失就发散"的 feedback-dependent tracker 区分开。YOTO 每条轨迹**只被调用一次**，有界误差即端到端验证了"一次触碰足以支撑持续 6-DoF 追踪"。

### 5. Conclusion & Limitations / 结论与边界

结论：YOTO 用一次同时双 GelSight 接触恢复绝对 6-DoF；把触觉 patch 表示为 3D 点云、匹配到 surface-block 分解、经法向感知 SVD 解析求解；两阶段虚拟-再-真实训练保物理数据 modest，可用消费级扫描模型 + CAD。四物体上均值定位 <5mm、avocado 重遮挡下 sub-2mm/sub-2° 位姿、单次接触支撑有界动态追踪。

作者自陈局限：(1) 仍需**每物体** ~20 个真实 GelSight 微调，完全 sample-free 部署是 future work；(2) **SVD 在 near-coaxial 抓取上退化**，对旋转对称物体（如 drill）不可避免；(3) 动态追踪依赖 rigid-grasp 假设，长时操作累积塑性漂移，**运动中快速 re-touch 可缓解**。

## 方法细节

四问速拆 YOTO：
1. **输入**：一对左右 GelSight 的接触，经 InvariantCloud 各转成带法向的局部点云 $\mathbf X_L,\mathbf X_R$；物体模型 $\mathcal M$（CAD 或扫描）；标定的传感器世界位姿。**无 RGB、无接触历史、无物体运动。**
2. **中间表示**：parent 点云 $\mathcal P$ + surface blocks $\{\mathcal B_i\}$（含中心 $\mathbf c_i^O$）；触觉/块特征 $\mathbf q_s,\mathbf b_i$；物体系触点 $\hat{\mathbf p}_s^O$ + kNN 法向 $\hat{\mathbf n}_s^O$。
3. **训练目标**：块分类 $\mathcal L_{\text{cls}}$ + top-K margin $\mathcal L_{\text{topK}}$ + smooth-ℓ1 偏移 $\mathcal L_{\text{pos}}$，两阶段（虚拟预训练 → 虚拟+真实微调）。
4. **输出如何用**：$\hat{\mathbf p}_s^O,\hat{\mathbf n}_s^O$ → Eq.(9)–(12) 闭式 SVD 一步出 $\hat{\mathbf T}_O^W$；**没有端到端回归位姿**，位姿是解析的。

公式速查：Eq.(1) coarse 相似度 · Eq.(2) fine offset+confidence · Eq.(3) 选择 · Eq.(4)–(8) 训练损失 · Eq.(9) 位移方向 · Eq.(10) 方向组 · Eq.(11) Procrustes 旋转 · Eq.(12) 平移。

## 实验设置、数据集、基线、指标

- **硬件**：2× AIRBOT Play（6-DoF）各持 1 枚 GelSight Mini；OptiTrack mocap（GT，仅评测）。
- **物体**：drill / squirrel(=rabbit) / monkey / avocado（几何对比：细长-对称 vs 广曲面）。
- **模型来源**：CAD 与消费级 3D 扫描重建 mesh，均走同一 parent-cloud + block 管线；全文默认用扫描模型。
- **接触重建**：InvariantCloud 管线 [31]（作者 prior work）把 GelSight 图像转成点云。
- **基线**：ICP（几何、触觉下界）、FoundationPose（视觉代表，标定 RGB-D）；无公开同设定触觉基线。
- **指标**：定位——物体系欧氏距离（mm）；位姿——平移误差（mm）+ 旋转误差（deg），clear/occluded 分列；动态——逐帧平移/旋转误差。

## 主要结果、消融或对比

| 维度 | 关键数字 | 读法 |
| --- | --- | --- |
| 定位（Table 1） | YOTO 4.78mm vs ICP 52.81mm | <1cm、约 ICP 的 1/11 |
| 真实微调必要性 | virtual-only 24.65 → +真实 4.78mm | 误差降 ~5×，少量真实样本关键 |
| 扫描 vs CAD | 4.78 vs 5.45mm | 扫描略优（含真实感知的打印伪影） |
| 位姿·clear（Table 2） | YOTO 3.42mm/3.58° vs FP 5.48mm/5.44° | clear 也全面小胜 |
| 位姿·occluded | FP 82.93mm/85.57°（涨 15.1×/15.7×） vs YOTO 3.52mm/3.56°（几乎不变） | **主结果**：视觉退化下触觉的决定性优势 |
| 动态追踪（Table 3/Fig.4） | 平移 <7mm、旋转 <8°，峰有界 | 单次接触足以支撑持续追踪 |

## 图表、公式与表格线索

| 图 / 表 | 读图重点 | 关联问题 | 本地文件 |
| --- | --- | --- | --- |
| Figure 1 | 遮挡下 YOTO 锚定物体、FoundationPose 漂到手上；右侧触点法向 + GelSight 原图 | 为什么视觉不可靠时要用触觉 | `page1_fig1.jpeg` |
| Figure 2 | 三段 pipeline：表面表示 → 定位学习（两阶段）→ 法向感知 SVD | 全流程如何从接触到位姿 | `page3_fig1.jpeg` |
| Figure 3 | 双共享编码器 + coarse 相似度 top-K + fine offset/confidence | 定位如何粗到精 | `page4_fig1.jpeg` |
| 4.1 内插图 | 预测触点（蓝）vs GT（红），drill 易 / avocado 难 | 定位在哪类几何上更稳 | `page6_fig1.jpeg` |
| Figure 4 | 四物体逐帧平移/旋转误差；峰有界、尾塑性漂移 | 单次接触能否支撑动态追踪 | `page8_fig1.jpeg` |
| Table 1 | 定位 4.78mm；virtual-only 掉 5×；扫描≈CAD | 定位精度与消融 | —— |
| Table 2 | 遮挡下 FP 涨 15×、YOTO 不变 | 主结果 | —— |
| Table 3 | 动态追踪 <7mm/<8° | 追踪有界 | —— |

## 主张-证据-边界矩阵

| 主张 / 结论 | 原文证据 | 证据位置 | 解释 | 边界 / 适用条件 |
| --- | --- | --- | --- | --- |
| 单次双触点能出绝对 6-DoF | Table 2 clear YOTO 全面优于 FP | §4.2 | learned 定位 + analytic SVD | 需两触点非近共轴、物体已建模 |
| 视觉退化下触觉压倒视觉 | occluded：FP 涨 15.1×/15.7×，YOTO 不变 | Table 2 | 触觉与标定位姿不依赖相机 | clear 时优势较小 |
| 少量真实数据即可 sim-to-real | virtual-only 24.65 → 4.78mm | Table 1 | 真实样本补传感伪影 | 仍需每物体 ~20 真实接触 |
| 可用消费级扫描模型 | 扫描 4.78 ≈/优于 CAD 5.45 | Table 1 | 扫描含真实打印伪影 | 仅 4 物体验证 |
| 一次接触支撑动态追踪 | Table 3 <7mm/<8°、峰有界 | §4.3、Fig.4 | 解析求解不依赖持续反馈 | rigid-grasp 假设，长时累积塑性漂移 |

## 局限与可追问点

作者承认：每物体微调（~20 真实接触）、near-coaxial SVD 退化（旋转对称物体）、rigid-grasp 漂移。

额外可追问：
1. **每物体微调 + 需物体模型**：YOTO 本质是"已知物体、已知模型"的**位姿估计**，不是"未知物体"的。对新物体要重建 mesh + 采 20 真实接触——相较 FoundationPose 的 novel-object 能力，这是适用面上的代价。
2. **法向来自模型 + 定位、非直接测量**：$\hat{\mathbf n}_s^O$ 是 kNN 聚合的模型法向。当定位偏或扫描 mesh 法向噪声大时，Eq.(11) 的旋转会不会被带偏？
3. **near-coaxial 退化**是几何本质：旋转对称物体（drill）绕轴欠约束。双臂能选非共轴接触，但**在线**如何判断当前双触点是否 well-conditioned、并主动换接触点？
4. **仅 4 物体、桌面刚性 probe**：没有真实机械手 in-hand、没有柔性/易碎物体；"single touch suffices" 的结论在更复杂 grasp 下是否成立？
5. **动态追踪是开环解析**：它靠标定的 live gel 位姿 + 一次接触的物体系锚定。若接触点在运动中发生宏观滑移（非塑性微滑），锚定失效——作者建议 re-touch，但未量化 re-touch 频率与误差的权衡。
6. **"Rabbit" vs "Squirrel" 命名不一致**（Table 3 vs 其余）：应是同物体，但提醒核对时别当两个物体。

## 与当前库的连接

- **与库里触觉论文是互补的另一层**：[[@wu2026tactile-wam]]（Tactile-WAM）、[[@liu2026taco-tactile-self-corrector]]（TACO）把触觉接进 **world/action model 做决策与纠错**；YOTO 是**纯触觉感知**——它产出一个 $\mathrm{SE}(3)$ 位姿观测。可以把 YOTO 想成那类策略的**上游状态估计器**：TACO 靠 12 维 force-torque 判断"接触在变"，YOTO 则把接触**解成物体在哪**。三者拼起来是"触觉 → 状态 → 决策/纠错"的纵向链。
- **与触觉表示线 [[@park2026tactx-learning-shared-tactile]]（TactX）/ [[@bi2026heterogeneous-tactile-transformer]]（HTT）**：它们做"跨传感器共享触觉表示"，YOTO 的定位网络用的是自家点云编码器（InvariantCloud 重建）。一个可追问的交叉点：YOTO 的触觉点云表示是否可换成 TactX/HTT 的共享表示以跨 GelSight/DIGIT 传感器泛化。
- **方法论上的独特性**：库里多数触觉/世界模型工作是"端到端学 + 大模型"，YOTO 反其道——**learned 只做几何检索定位、位姿交给 analytic SVD**。这条"学习 + 解析"分工路线，与 world-model 那批"全生成/全回归"形成鲜明对照，值得作为一个方法论坐标记住。
- **引用近亲（均不在库）**：FoundationPose [3]（视觉基线）、Tac2Pose [5]、NormalFlow [6]、MidasTouch [18]、PatchGraph [17]、Caddeo [16]、GelSight [30]，以及作者 prior 的 **InvariantCloud [31]（arXiv:2605.25216）**——若要深挖 YOTO 的接触点云重建，这篇是关键前置，可考虑入库。

## 精读路线 / 为什么需要回看

1. 先读 `论文主线` + Fig.1：确认"视觉恰在被遮挡时失效、触觉补位但有定位歧义"这对张力，以及 YOTO 的三个"不需要"。
2. 再读 `方法细节` + §3.2/§3.4 与 Fig.3：核对**learned 定位（Eq.1-3）+ analytic SVD（Eq.9-12）解耦**这条主线，特别是法向为何是消除绕轴歧义的关键。
3. 然后读 Table 1/2：定位 4.78mm、遮挡下 FP 涨 15× 而 YOTO 不变——这是"视觉退化下触觉优势"的主证据；注意 §4.1 与 §4.2 的**反转**（drill 定位最好但位姿最难）。
4. 最后读 §4.3 + Fig.4：理解"单次接触 + 开环解析"为何能有界追踪，以及 rigid-grasp 假设的边界。
5. 若要写 related work / 做方法对照：把 YOTO 放进"触觉 → 状态 → 决策"链，与 [[@wu2026tactile-wam]] / [[@liu2026taco-tactile-self-corrector]] 的"触觉进决策/纠错"对照，突出它是**感知层**且走"学习+解析"分工。
