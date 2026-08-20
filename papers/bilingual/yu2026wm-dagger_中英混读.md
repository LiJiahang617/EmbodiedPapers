---
tags:
  - bilingual-reading
paper: "[[@yu2026wm-dagger]]"
source_pdf: "[[papers/pdfs/WM-DAgger.pdf]]"
images: "papers/images/yu2026wm-dagger/"
image_index: "[[papers/images/yu2026wm-dagger/index.md]]"
created: 2026-06-25
---

# WM-DAgger: Enabling Efficient Data Aggregation for Imitation Learning with World Models

paper:: [[@yu2026wm-dagger]]
pdf:: [[papers/pdfs/WM-DAgger.pdf]]
images:: [[papers/images/yu2026wm-dagger/index.md]]

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| Behavioral Cloning, BC | 行为克隆 | 用专家示范直接监督策略，是本文要改进的基础 imitation learning baseline。 |
| compounding errors | 误差累积 | 策略小误差把机器人带到训练分布外，随后错误继续放大。 |
| out-of-distribution, OOD states | 分布外状态 | 专家示范没覆盖、但部署时常会遇到的状态。 |
| DAgger | 数据聚合 | 传统做法是专家在线纠偏并把纠偏轨迹加入训练集。 |
| World Model, WM | 世界模型 | 输入历史图像和动作，生成未来视觉状态；本文用它代替人工生成 recovery data。 |
| EAC-WM | Eye-in-Hand Action-Conditioned World Model | 本文的动作条件世界模型，针对眼在手机器人视觉动态。 |
| Action2Image | 动作转图像条件 | 把低维动作映射成像素对齐的几何条件，让视频模型能读懂动作。 |
| Play Data | 探索数据 | 每个任务约 5 分钟无目标探索，用来让世界模型熟悉场景几何与物理。 |
| Task Data | 专家任务数据 | 每个任务 20 条人类示范，是真实 imitation learning 监督来源。 |
| Corrective Action Synthesis | 纠偏动作合成 | 先偏离专家轨迹再返回，用世界模型生成 OOD recovery 轨迹。 |
| Deviation Phase | 偏离阶段 | 从专家轨迹推到 OOD 状态；训练策略时丢弃。 |
| Recovery Phase | 恢复阶段 | 从 OOD 状态回到专家流形；训练策略时保留。 |
| Consistency-Guided Filtering | 一致性引导过滤 | 用 DINOv2 终帧相似度过滤 hallucinated rollouts。 |
| hallucination | 幻觉/物理不一致 | 世界模型生成的物体形变、位置或动态不符合真实任务。 |
| action chunking | 动作分块 | 策略一次预测未来多步动作，减少逐帧控制噪声。 |

## 论文主线

这篇论文要解决的是 imitation learning 中一个很实际的问题：少量专家示范通常只覆盖成功轨迹附近的状态，Behavioral Cloning（BC）在部署时稍微偏一点，就会进入训练集没见过的 OOD states；模型在 OOD states 上动作更差，继续偏离，最后任务失败。传统 DAgger 的答案是让专家持续接管并提供 recovery action，但这又把成本推回人工。

![[papers/images/yu2026wm-dagger/page1_full.png|700]]

**Figure 1 / 首页总览。** 左侧是 Standard BC 的问题：few-shot expert data 只覆盖窄轨迹，失败后没有回来的监督。右侧是 WM-DAgger：World Model 生成大量 recovery data，再经过 filtering 加入策略训练。

WM-DAgger 的核心判断是：World Models 可以当作“低成本的轨迹想象器”，在专家轨迹周围生成偏离和恢复过程。但作者也很清楚，直接相信生成模型是危险的，因为 world model 会 hallucinate，而且错误 recovery action 会把策略训练坏。因此整套方法有两层约束：第一，用 Corrective Action Synthesis 合成“任务导向”的偏离-恢复动作，而不是任意扰动；第二，用 Consistency-Guided Filtering 过滤视觉/物理不一致的 rollout。

最终训练时，策略看到的不只是 expert demonstrations，还看到大量从 OOD 状态回到专家流形的 recovery trajectories。这样 policy 学到的不是“只沿着成功轨迹走”，而是“偏出去时如何回来”。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| 用 World Model 自动合成 DAgger 所需的 OOD recovery data。 | EAC-WM + Corrective Action Synthesis。 | 四个真实机器人任务成功率；Soft Bag 5-shot 93.3%。 | 证据较强，特别是少量示范下相对 BC/DMD 的提升明显。 |
| 合成数据必须 task-oriented，不能随便扰动。 | 方向约束：过滤与专家下一步动作夹角小于 120 度的偏离方向；只保留 Recovery Phase。 | w/o Dir. 成功率 0.0%。 | 很强；消融显示错误方向监督会直接毁掉策略。 |
| World Model hallucination 需要过滤。 | DINOv2 embedding + terminal frame cosine similarity。 | w/o Filter 从 96.7% 降到 66.7%。 | 有力，但终帧相似度无法完全保证中间过程动力学正确。 |
| Play Data 能帮助 world model 学到场景物理。 | 每个任务约 5 分钟 goal-agnostic exploration。 | w/o Play Data 从 96.7% 降到 83.3%。 | 支持明确，说明任务外探索对生成质量有帮助。 |
| WM 比 single-frame diffusion 更适合 recovery data。 | EAC-WM 生成连续未来帧，DMD 作为 diffusion baseline。 | DMD 在所有任务低于 WM-DAgger；图 8 显示 DMD morphing。 | 趋势明确，但只比较一个主要 generative baseline。 |
| 方法可用于不同真实操作任务。 | pushing、pick-and-place、insertion、folding。 | Table I/IV/V/VI。 | 覆盖刚体/软体/插入/折叠，但任务规模仍偏小。 |

## 摘要与核心贡献

摘要的逻辑可以拆成四步。第一，Imitation learning 很强，但 compounding errors 会让策略从少量专家数据覆盖的窄分布滑出去。第二，DAgger 能解决这个问题，但需要持续 human intervention（人工介入），不容易规模化。第三，World Models 可以根据历史帧和动作生成未来帧，因此有机会合成 OOD recovery data。第四，World Models 也会 hallucinate，且没有专家纠偏动作，所以必须设计合成动作和过滤机制。

本文提出 WM-DAgger：在 eye-in-hand robotic arm 场景中，用少量 expert demonstrations 和少量 Play Data 训练 EAC-WM，然后从专家轨迹附近生成大量 OOD recovery trajectories。训练数据由两部分组成：原始 expert Task Data 和通过一致性过滤保留下来的 synthetic recovery data。

核心贡献有三点。第一，概念上把 World Model 引入 DAgger-style data aggregation，用于少示范 imitation learning 的 OOD recovery。第二，技术上提出 Corrective Action Synthesis 和 Consistency-Guided Filtering，分别处理“动作监督会不会误导”和“生成轨迹会不会幻觉”。第三，实验上在四个真实机器人任务上验证，尤其 Soft Bag Pushing 只用 5 条示范达到 93.3% 成功率。

## 1. Introduction / 为什么 BC 和 DAgger 都不够

BC 的问题不是训练阶段拟合不了 expert trajectory，而是部署阶段没有 closed-loop recovery。机器人稍微偏离，例如夹爪没有对准、推软袋时角度偏了、插纸时边缘没对齐，就进入专家示范没覆盖的状态。此时 BC 模型通常继续输出不合适动作，使偏差扩大。

DAgger 的思想是对的：让 expert 在 OOD state 给出正确动作，把这些状态也加入训练集。但在真实机器人里，这意味着专家要一直在线监控、接管、纠偏。对于高频操作、长任务、多任务，这种人力成本很高。

作者认为 World Model 提供了第三条路：如果 world model 能根据动作生成接下来会看到什么，就可以在专家轨迹周围“想象”一些偏离状态，再想象如何回到专家轨迹。问题是这里有两个坑：

- 没有 expert 人类为 OOD 状态标注最优 recovery action，随便合成会产生 contradictory supervision（矛盾监督）。
- World Model 生成长 rollout 时会累积误差，出现 object morphing（物体形变错误）、object position drift（物体位置漂移）等幻觉。

WM-DAgger 的方法就是围绕这两个坑设计。

## 2. Related Work / 和已有路线的差别

### 2.1 Dataset Aggregation for Imitation Learning

传统 DAgger、HG-DAgger、CR-DAgger 都在解决同一个核心问题：让策略在训练时看到自己部署时可能遇到的 OOD 状态。区别在于 human expert 如何介入、何时接管、如何减少接管成本。但它们本质上仍依赖人。

Diffusion Meets DAgger（DMD）这类 generative data aggregation 方法试图用生成模型合成 OOD 数据。本文对它的批评是：single-frame generation 难以建模连续 recovery dynamics，尤其在软物体、接触丰富和精确插入任务里，单帧视觉逼真不等于物理过程可信。

### 2.2 World Models in Robot Learning

World Model 在机器人里通常作为内部模拟器：给定当前状态和动作，预测未来。Dreamer 系列在 latent dynamics 中学习和规划；Cosmos 等大模型把视频生成和物理先验结合；World4RL 用 imagined rollouts 做 policy refinement。

本文的独特位置是：不直接用 world model 做 planning，也不直接用它替代环境，而是用它为 imitation learning 生成 recovery supervision。也就是把 world model 变成 DAgger 的数据生成器。

## 3. Methodology / 方法整体

![[papers/images/yu2026wm-dagger/page3_full.png|700]]

**Figure 2 / 总 pipeline。** 左侧训练 world model：互联网视频预训练提供通用物理先验，Play Data 和 Task Data 做 video-action post-training。中间从 Task Data 选 pivot 合成 candidate recovery data，再过滤。右侧把 Augmented Data 和原 Task Data 一起训练 policy。

方法有四个阶段：

1. 用 Cosmos-Predict2.5 初始化 EAC-WM，并用每个任务的 Play Data + Task Data 做后训练。
2. 从 expert trajectory 中随机选择 pivot timestep，合成先偏离再恢复的动作序列。
3. 用 EAC-WM 根据历史图像和合成动作生成未来视觉帧。
4. 用 DINOv2 终帧一致性过滤掉 hallucinated trajectories，只保留 recovery phase 训练 policy。

### 3.1 EAC-WM / Eye-in-Hand Action-Conditioned World Model

EAC-WM 的输入是历史 eye-in-hand 图像和一串动作，输出未来图像。动作定义为：

$$
a_t=[t_t,q_t,g_t]^\top
$$

其中 $t_t \in \mathbb{R}^3$ 是 Cartesian translation，$q_t \in \mathbb{R}^4$ 是 unit quaternion orientation，$g_t \in \mathbb{R}$ 是 continuous gripper state。形式化地：

$$
\hat I_{t:t+q}=f_\theta(I_{t-p:t}, a_{t-p:t+q})
$$

这里 $I$ 是真实图像，$\hat I$ 是 world model 生成图像，$p$ 是历史窗口，$q$ 是未来动作/帧长度。

![[papers/images/yu2026wm-dagger/page3_fig16.jpeg|700]]

**Figure 3 / EAC-WM architecture。** 关键不是简单把动作 token 拼到视频模型里，而是把动作转成与像素对齐的几何条件。

### 3.2 Action2Image Conditioning / 为什么动作要变成图像条件

普通动作向量维度很低，而视频模型的视觉条件维度很高。如果直接把 $[t,q,g]$ 放进去，模型可能忽略动作，只根据历史图像做平均式预测。Action2Image 的目的就是把低维动作变成每个像素都有的 motion condition。

对每个像素 $(u,v)$，根据相机内参 $K$ 和旋转 $R_t$ 得到 viewing direction：

$$
d_t^{(u,v)}=
\frac{R_t K^{-1}[u,v,1]^\top}
{\lVert R_t K^{-1}[u,v,1]^\top\rVert_2}
$$

再把未来相机位置变化写成 origin displacement grid $\Delta O_{t+i}$，把每个像素视线方向变化写成 directional tensor $\Delta D_{t+i}$，再拼上 gripper map：

$$
C_{geo,t+i}=[\Delta O_{t+i}, \Delta D_{t+i}, C_{grip}] \in \mathbb{R}^{H \times W \times 7}
$$

直观讲，模型不是只知道“夹爪向右移动了 2 cm”，而是知道相机运动会如何改变每个像素对应的空间射线。这对 eye-in-hand 视觉尤其重要。

### 3.3 World Model Training / Play Data 和 Task Data 怎么用

EAC-WM 先继承 Cosmos-Predict2.5 的 video-only physical priors，再用机器人场景的 visual-action sequences 后训练。数据分两类：

- Play Data：无目标探索，演示者随机移动和接触物体，帮助 world model 学会场景几何、物体外观和基本交互。
- Task Data：少量专家任务示范，帮助 world model 学会任务相关动作导致的视觉变化。

训练目标采用 Rectified Flow。未来目标 token $x_k$ 与 Gaussian noise $\epsilon$ 线性插值得到：

$$
z_{\lambda,k}=(1-\lambda)x_k+\lambda\epsilon
$$

Video DiT 学习从噪声回到数据的 velocity field：

$$
L=\mathbb{E}_{\lambda,x,\epsilon,c}
\left[
w(\lambda)\lVert \phi_\theta(z_\lambda,\lambda,c)-(\epsilon-x)\rVert_2^2
\right]
$$

其中 condition $c=\{c_{mem},c_{geo}\}$ 包含历史图像条件和 Action2Image 的几何动作条件。

## 4. World Model for Data Aggregation / 怎样合成 recovery data

### 4.1 Corrective Action Synthesis Module

![[papers/images/yu2026wm-dagger/page4_full.png|700]]

**Figure 4 / Corrective Action Synthesis。** 从专家轨迹中选 pivot，沿一个方向偏离，再沿反方向返回。重点是只保留返回阶段给策略学习。

给定专家轨迹：

$$
\tau=\{a_i,I_i\}_{i=1}^n \in D
$$

随机选择 pivot timestep $m$，设置 deviation horizon $k$，再采样一个随机单位方向 $v_d \in \mathbb{R}^3$。如果这个方向和专家下一步动作 $a_{m+1}$ 的夹角小于 $120^\circ$，则过滤掉。论文文字说这是为了避免 recovery action 与 expert trajectory 的方向相冲突；从消融结果看，这个约束非常关键。

合成轨迹分两段：

- Deviation Phase $\tau_d'$：从专家 pose 走到扰动 OOD state。
- Recovery Phase $\tau_r'$：从 OOD state 返回专家轨迹附近。

World model 根据历史帧和合成动作预测视觉：

$$
\hat I_{1:2k}=f_\theta(I_{m-p:m},a'_{1:2k})
$$

训练 policy 时丢弃 Deviation Phase，只保留 Recovery Phase。这个选择很合理：偏离阶段本质上是在制造 OOD，不应该教策略主动偏离；恢复阶段才是策略真正需要学的。

### 4.2 Consistency-Guided Filtering Module

![[papers/images/yu2026wm-dagger/page4_fig1.jpeg|700]]

**Figure 5 / 一致性过滤。** 低质量生成会出现 morphing 或物体位置错误；高质量生成在回到专家视角时应和真实帧相似。

World Model 的 hallucination 通常会随 rollout 时间增长而累积，所以终帧最容易暴露问题。作者用 DINOv2 提取合成终帧 $\hat I_{2k}$ 与对应专家真实帧 $I_m$ 的 embedding，再计算 cosine similarity。如果相似度低于自适应阈值，就丢弃整个轨迹。

这个过滤器的直觉是：Recovery Phase 的终点应该回到专家轨迹对应视角。如果终点看起来还不像真实专家帧，要么物体位置错了，要么物体形变错了，要么视觉结构不一致，这条合成数据就不适合训练。

但也要注意它的边界：终帧相似不代表中间每一步的接触动力学都正确。对于强接触、遮挡或触觉关键的任务，未来可能需要更细的 trajectory-level consistency。

## 5. Policy Training / 策略怎么训练

最终训练集是：

$$
D_{aug}=D \cup D_{virtual}
$$

其中 $D$ 是原始 expert demonstrations，$D_{virtual}$ 是经过过滤的 synthetic recovery trajectories。策略采用 action chunking：

$$
\hat A_t=\pi(I_t)=[\hat a_t,\hat a_{t+1},\ldots,\hat a_{t+H-1}]
$$

训练目标是未来 $H$ 步动作的 MSE：

$$
L_{policy}
=
\mathbb{E}_{(I_t,A_t)\sim D_{aug}}
\left[
\frac{1}{H}\sum_{i=0}^{H-1}\lVert \hat a_{t+i}-a_{t+i}\rVert_2^2
\right]
$$

论文使用 Gr00t N1.5 作为 policy model。这里 policy 本身不是本文主要创新，关键创新在于训练数据的 recovery 覆盖被 world model 扩展了。

## 6. Evaluation / 实验设置

![[papers/images/yu2026wm-dagger/page5_full.png|700]]

**Figure 6-8 / 硬件、任务与生成视觉。** 页面上半部分是 UMI-style 采集硬件和四个任务；下半部分展示 EAC-WM 在不同动作方向下生成的未来帧，以及与 DMD 的软袋生成对比。

硬件设置基本沿用 UMI-style robot-free demonstration collection：

- 手持 two-finger gripper；
- GoPro eye-in-hand fisheye camera 作为视觉观测；
- HTC Vive Tracker 采集 6-DoF pose；
- 真实执行平台是 Universal Robots UR7e + Robotiq 2F-140 gripper；
- 训练使用 4 张 NVIDIA L20，推理使用 1 张 L20。

每个任务采集约 5 分钟 Play Data 和 20 条 Task Data。默认每个任务生成 1500 条 recovery episodes。Baseline 有两个：

- Standard BC：只用专家示范，不做数据聚合。
- DMD：Diffusion Meets DAgger，用 diffusion-based synthesis 做数据增强。

四个任务覆盖不同难点：

- Soft Bag Pushing：软袋推动到目标篮，测试 deformable object 和 OOD recovery。
- Pick-and-Place：抓取并放置刚体，同时看 seen / unseen object 泛化。
- Ballot Insertion：抓取纸片插入窄槽，测试 deformable planar object + contact-rich precision。
- Towel Folding：6-DoF 复杂轨迹和严重形变。

## 7. Results / 主要结果

### 7.1 生成质量：EAC-WM vs DMD

Figure 7 展示同一真实起点下，EAC-WM 按 right / left / up / down / forward / backward 六个方向生成不同未来帧。重要的是它不只是改像素，而是能维持任务对象结构，例如软袋形变、毛巾褶皱。

Figure 8 对比 DMD 和 EAC-WM。DMD 在软袋任务中容易出现 visual morphing，而 EAC-WM 能保持结构和物理一致性，甚至模拟出 $t=16$ 时 bag dropping 的动态。这是作者认为 world model 优于 single-frame generative baseline 的关键证据。

### 7.2 Task 1: Soft Bag Pushing

Soft Bag Pushing 是最完整的实验。成功率如下：

| Method | 1-shot | 3-shot | 5-shot | 10-shot | 20-shot |
| --- | ---: | ---: | ---: | ---: | ---: |
| Standard BC | 6.7 | 20.0 | 26.7 | 30.0 | 30.0 |
| DMD | 13.3 | 33.3 | 40.0 | 53.3 | 56.7 |
| WM-DAgger | 73.3 | 86.7 | 93.3 | 93.3 | 96.7 |

这个表说明两件事。第一，BC 即使有 20 条示范也只有 30.0%，因为真实部署时一旦推偏就不会回来。第二，WM-DAgger 在 1-shot 下就到 73.3%，说明 synthetic recovery data 对少示范场景特别有效。

合成数据规模消融：

| Synthetic samples | 300 | 900 | 1500 | 3000 |
| --- | ---: | ---: | ---: | ---: |
| Success Rate | 46.7 | 63.3 | 96.7 | 96.7 |

性能在 1500 之后趋于饱和，说明对这个任务而言，更多合成数据不是无限增益，关键是覆盖主要 OOD recovery manifold。

模块消融：

| Variant | Success Rate |
| --- | ---: |
| WM-DAgger Full | 96.7 |
| w/o Play Data | 83.3 |
| w/o Filter | 66.7 |
| w/o Dir. | 0.0 |

这里最值得记住的是 w/o Dir. = 0.0。方向约束不是小技巧，而是防止 synthetic supervision 反向误导策略的底线。

### 7.3 Task 2: Pick-and-Place

| Method | O1 seen | O2 seen | O3 seen | O4 unseen | O5 unseen |
| --- | ---: | ---: | ---: | ---: | ---: |
| Standard BC | 13.3 | 13.3 | 6.7 | 0.0 | 10.0 |
| DMD | 33.3 | 36.7 | 26.7 | 6.8 | 16.7 |
| WM-DAgger | 83.3 | 90.0 | 80.0 | 63.3 | 76.7 |

Seen object 上的提升说明 recovery data 解决了靠近、抓取、偏离后的纠偏问题。Unseen object 上仍保持 63.3 / 76.7，说明合成数据没有只让策略记住具体纹理，而是增加了视觉和物理状态覆盖。

### 7.4 Task 3: Ballot Insertion

| Method | Success Rate |
| --- | ---: |
| Standard BC | 13.3 |
| DMD | 26.7 |
| WM-DAgger | 73.3 |

Ballot insertion 难在 narrow slot 和 deformable paper。小偏差会导致纸片错过槽口或被挤皱。WM-DAgger 的提升说明 recovery supervision 对 high-precision insertion 很有价值。

### 7.5 Task 4: Towel Folding

| Method | Success Rate |
| --- | ---: |
| Standard BC | 0.0 |
| DMD | 10.0 |
| WM-DAgger | 46.7 |

Towel folding 的成功率没有像 pushing 那么高，这是很有信息量的结果。它说明 WM-DAgger 对复杂 deformable 6-DoF 操作有帮助，但 world model 对毛巾这类高自由度形变的预测仍然困难。这里是方法边界，不是失败：它揭示了未来 world model conditioning 需要更强的形态和动力学先验。

## 8. Conclusion and Future Work / 结论与未来工作

论文结论是：World Models 可以作为 scalable, high-fidelity supervisors，为 imitation learning 合成物理一致的 recovery data。Corrective Action Synthesis 解决“怎么产生不误导的 recovery action”，Consistency-Guided Filtering 解决“怎么筛掉 hallucination”。四个真实机器人任务表明，这种数据聚合能显著提升少示范策略的成功率。

作者明确指出未来难点是 dexterous multi-finger hands。多指灵巧手有更高 DoF、更多遮挡、更复杂接触拓扑和更难的 articulated visual consistency。未来可能需要把 morphology priors（形态先验）和 kinematic topologies（运动学拓扑）加入 world model conditioning。

## 图表索引与讲解

| 图表 | 读图重点 | 关联问题 |
| --- | --- | --- |
| Figure 1 | BC 只有少量成功轨迹，WM-DAgger 生成偏离后的恢复监督。 | 为什么需要 world-model-based DAgger。 |
| Figure 2 | 训练 EAC-WM、合成 candidate data、过滤、训练 policy 的完整 pipeline。 | 端到端流程。 |
| Figure 3 | Action2Image 把动作变成像素级几何条件。 | 为什么普通 action token 不够。 |
| Figure 4 | 偏离-恢复两阶段，只保留恢复阶段。 | 合成监督如何避免教策略主动偏离。 |
| Figure 5 | DINOv2 终帧相似度过滤 morphing 和位置错误。 | 如何处理 world model hallucination。 |
| Figure 6 | UMI-like 硬件和四个真实任务。 | 实验覆盖哪些操作类型。 |
| Figure 7 | EAC-WM 按不同方向动作生成未来帧。 | 动作条件生成是否有效。 |
| Figure 8 | EAC-WM 与 DMD 的 soft bag rollout 对比。 | 世界模型是否优于单帧扩散合成。 |
| Table I | Soft Bag few-shot 成功率。 | 少示范收益最大。 |
| Table II | synthetic samples scaling。 | 合成数据边际收益何时饱和。 |
| Table III | Play Data、Filter、Dir. 消融。 | 哪些模块不可省。 |
| Table IV-VI | pick/place、insertion、folding 结果。 | 方法是否跨刚体/软体/接触精度泛化。 |

## 和你的论文库中其他条目的关系

- 对 [[@zhang2026contactworld]]：两者都把 world model 用到机器人操作，但 ContactWorld 偏 planning / MPC 和触觉视觉表征，WM-DAgger 偏 imitation learning 的数据聚合。
- 对 [[@qwen2026robotmanip]]：Qwen-RobotManip 解决跨本体数据对齐与大规模 VLA 训练；WM-DAgger 解决少量示范下 OOD recovery data 的自动补充。两者可以互补：一个扩数据来源和本体，一个补失败边缘数据。
- 对 [[@xu2026egoguide]]：EgoGuide 关注如何更好采集 robot-free demonstrations；WM-DAgger 关注已有示范周围如何自动生成纠偏轨迹。
- 对 [[@tang2026frs]]：FRS 是用 flow policy 反向引导生成更好的动作；WM-DAgger 是用 world model 生成视觉-动作 recovery 监督，二者都属于 policy improvement / steering 方向。

## 可追问点

1. DINOv2 终帧相似度是否会误保留“终点像但中间动力学错”的轨迹？
2. 方向过滤阈值 $120^\circ$ 是否对所有任务合理？需要绕行、回撤、先退后进的任务会不会被误过滤？
3. 如果专家示范本身只有成功轨迹，合成 OOD 的半径如何决定？偏离太小学不到 recovery，偏离太大 world model 失真。
4. 生成数据只保留 Recovery Phase，那么策略是否缺少“如何识别自己已经偏离”的显式状态标签？
5. 对接触丰富任务，视觉终帧一致性是否足以替代 force / tactile consistency？
6. 如果把 WM-DAgger 用到多臂或灵巧手，Action2Image 之外是否还需要 hand morphology token、joint contact graph 或 object dynamics prior？

## 我的阅读笔记

这篇最值得借鉴的是“合成数据不是越多越好，而是方向要对、物理要可信”。很多机器人数据增强论文只强调生成更多状态，但 WM-DAgger 的消融说明，错误 recovery supervision 会直接让策略崩掉。w/o Dir. = 0.0 是一个很强的警告：在 imitation learning 里，合成数据的动作标签比视觉逼真更重要。

把它放进 VLA / WAM 方向看，它提供了一个很具体的世界模型用法：不是让 world model 直接控制，也不是做长时程规划，而是离线填补 BC 最缺的 OOD recovery distribution。这个用法工程上更稳，因为最终部署时仍是 policy model 执行动作，world model 只在训练数据层面发挥作用。

我会把这篇作为“世界模型辅助数据聚合”的入口来回看。后续如果读到更强的视频世界模型、触觉世界模型或 VLA 自训练论文，可以拿它的三个问题去对照：生成的 OOD 状态从哪里来，动作监督如何保证不误导，过滤机制如何证明物理一致。

