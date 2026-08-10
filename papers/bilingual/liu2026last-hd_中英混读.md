---
tags:
  - bilingual-reading
  - deep-reading
paper: "[[@liu2026last-hd]]"
source_pdf: "[[papers/pdfs/2606.23685v1.pdf]]"
images: "papers/images/2606.23685v1/"
image_index: "[[papers/images/2606.23685v1/index.md]]"
created: 2026-07-18
reading_mode: 生成式精读（逐节读原文 + 完整附录 + 读图）
---
核心论点是：某些隐式世界模型的最深层特征，具备的是物理后果（dynamics）的表征提取而不是视觉效果的表征提取，因此用这些世界模型的隐帧座位监督，可将本体（人类/机械臂）差异进行缩小，而让不同本体数据的物理后果作为policy学习的重点，克服跨本体数据学习难的问题。
# LaST-HD: Learning Latent Physical Reasoning from Scalable Human Data for Robot Manipulation

paper:: [[@liu2026last-hd]]
pdf:: [[papers/pdfs/2606.23685v1.pdf]]
images:: [[papers/images/2606.23685v1/index.md]]

> [!info] 版本与论文关系
> 本稿解析 arXiv `2606.23685v1`（2026-06-22），PDF 自称 **LaST-HD Technical Report**，不据模板样式额外推定正式 venue。LaST-HD 与 [[@liu2026last0-latent-spatio-temporal|LaST₀]] 是两篇独立论文：LaST₀ 提出 latent spatio-temporal CoT 与 MoT 快慢专家；LaST-HD 继承这类 reasoning-before-acting 接口，新增人手—机器人 latent physical alignment、OOL Glove 与 human correction。

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| human-to-robot action learning | 人类到机器人动作学习 | 用易采集的人手交互数据帮助机器人策略学习，而不只把人手姿态机械复制到机器人。 |
| embodiment gap | 本体差距 | 人手与机器人在外观、运动学、动作维度和接触方式上的差异，是直接联合训练的障碍。 |
| kinematic retargeting | 运动学重映射 | 把人手 keypoints 映到 gripper / dexterous hand；LaST-HD 承认它仍是必要的几何前置层。 |
| morphology-agnostic | 形态无关 | 论文希望 latent 表示关注共同物理后果而非身体外观；实际仍依赖 target-embodiment data 和手工 retargeting。 |
| reasoning-before-acting | 先推理后行动 | 先由 reasoning expert 生成紧凑 latent CoT，再让 action expert 生成动作。 |
| latent physical reasoning | 潜空间物理推理 | 表示动作—接触—物体变化等不易语言化的动力学，是跨本体迁移的中间接口。 |
| Mixture-of-Transformers (MoT) | 混合 Transformer | 同一 24 层骨架内分 reasoning expert 与 action expert，通过 shared attention 传递 latent CoT。 |
| action-conditioned world model | 动作条件世界模型 | 给视觉与 action chunk，预测未来；最深 U-Net feature 被当作跨本体 latent teacher。 |
| forward-dynamics feature | 前向动力学特征 | 表示“执行这段动作后会发生什么”，比 future SigLIP appearance feature 更贴物理后果。 |
| unpaired trajectories | 未配对轨迹 | 人手和机器人轨迹不要求逐帧/逐样本对应；动作标签作为 weak anchor（弱锚点）。 |
| latent target / Latent GT | 潜目标 / 潜真值 | 世界模型 feature 经 MLP、flatten、pooling 压成 $N_{lat}$ token，监督 reasoning expert。 |
| cosine latent loss | 潜表示余弦损失 | 对齐预测 latent 与 world-model target 的方向，和 flow-matching action loss 联合优化。 |
| shared attention | 共享注意力 | 让 action expert 读取 reasoning expert 生成的 latent CoT，而非把世界模型放进实时控制环。 |
| Out-of-Lab (OOL) Glove | 实验室外人手采集手套 | 六个 IMU、21 个手腕关键点，用于高频自然人手动作采集与跨机器人重映射。 |
| hand-centric representation | 手中心统一表示 | 保存 wrist pose 与相对 keypoint geometry；可派生二指 gripper command 或灵巧手 joint target。 |
| mixed-to-human recipe | 混合到纯人手训练配方 | Stage 1 混合人/机器人共同训练，Stage 2 用失败状态的人手 correction 后训练。 |
| human-hand online correction | 人手在线纠错 | 真机 rollout 找失败状态，再用 OOL Glove 快速采针对性人手示范，类似 human-data DAgger。 |
| balanced replay | 平衡回放 | 后训练 batch 一半旧数据、一半 correction，1–2 epochs，减轻 catastrophic forgetting。 |
| Mix-HD | 混合人手数据版本 | In-domain 用 50 robot + 50 human demo，比较能否用人手替代一半机器人数据。 |
| w/ unseen HD | 加目标场景人手数据 | 每种 OOD scenario 加 60 条 human demos；与 zero-shot checkpoint 必须分开解释。 |
| UMAP / attention map | 降维 / 注意力图 | 展示人/机器人 latent 是否重叠、是否关注接触区域；是解释性线索而非独立因果证明。 |

## 摘要

LaST-HD 研究一个比运动学 retargeting 更深的问题：**即使人手轨迹能被映射成机器人动作，人和机器人对同一物体施加动作时的接触动力学、可达性与视觉后果仍不同；怎样让 VLA 学到二者共享的“物理推理”而不是只记外观与动作坐标？**

作者把 action-conditioned world model（动作条件世界模型）用作离线 teacher。该 world model 在未严格配对的人手与机器人轨迹上训练，连续 action chunk 通过 cross-attention 注入每层；最后 denoising step 的深层 U-Net feature 被视作 action-aware forward dynamics。特征经 MLP 与 adaptive pooling 压成少量 latent tokens，作为 LaST-HD reasoning expert 的监督。部署时 world model 不参与推理；reasoning expert 自回归预测 latent CoT，action expert 通过 shared attention 读取它并用 flow matching 生成机器人动作。

系统贡献还包括 OOL Glove：每手 6 个 9-axis IMU，重建 20 个手部 + 1 个腕部 6-DoF keypoints；论文报告单手 <100g、>200Hz、<10ms、每点平均 RMS 位置误差低于 1 mm。训练则分两阶段：先混合 human/robot co-training，再部署找 failure-prone states，用手套采 human corrections，旧数据与 correction 1:1 回放、只更新 1–2 epochs。

六项真机任务上，完整 LaST-HD 的 in-domain 平均成功率 0.73，高于 LaST₀ 0.63、$\pi_{0.5}$ 0.62、Cosmos-Policy 0.52；用 50 robot + 50 human 的 Mix-HD 为 0.68。更需要校准的是泛化：仅用 in-domain checkpoint 的 zero-shot global average 为 0.31，和 LaST₀/$\pi_{0.5}$ 的 0.30 基本相同；每种 unseen condition 加 60 条目标域人手数据后，LaST-HD 才到 0.56，高于 LaST₀+human 的 0.46。Sort Fruits 的 targeted online correction 用 60 条/20 分钟人手数据，把 background/object/position 提到 100/100/80%，三者平均超过 90%。

## 论文主线

![[papers/images/2606.23685v1/Teaser_V5_page1.png|940]]

**Figure 1 / 全文总览。** 左上 OOL Glove 产出每手 21 个 6-DoF hand-wrist keypoints；中上 human（蓝）与 robot（橙）轨迹无需配对，只要各自有动作。Action-conditioned world model 将两域映射成 Latent GT，监督两专家 LaST-HD。右上 UMAP 试图说明：无 alignment 时两域分离，有 alignment 后在相同任务结构上交织。下方六任务覆盖 R1 Lite 双夹爪、Tianji 双夹爪、Tianji+WUJI 灵巧手；右下把两种结果分开：in-domain 完整 LaST-HD 73%，generalization 在无目标人手数据时 31%，加入后 56%。

全文的论证链是：

1. **Robot data 贵，human-hand data 易扩展；但几何 retargeting 只对齐“怎么动”，没对齐“动作会造成什么”。**
2. **Action-conditioned forward dynamics 是跨本体中间接口。** 外观与关节不同，但推苹果都会造成苹果移动；动作标签给未配对轨迹提供 weak anchors。
3. **世界模型只做离线 latent teacher。** 这样利用其时空动力学，又避免将大型视频生成模型直接放进控制环。
4. **LaST-HD reasoning expert 学 teacher latent，action expert 用 shared attention 执行；OOL Glove提供更快、更精确的人手 action supervision。**
5. **Stage 1 测人手能否替代/补充机器人数据，Stage 2 测失败点人手 correction 能否低成本适应新场景。**
6. **消融支持 action conditioning + latent reasoning 的组合优于纯视觉 latent / 纯 action co-training；但真正 OOD 增益依赖目标场景 human data，且 geometry retargeting 仍未消失。**

## 贡献与结论对照

| 贡献 / 结论 | 方法位置 | 关键证据 | 应如何定性 |
| --- | --- | --- | --- |
| 以 latent physical reasoning 对齐未配对 human/robot trajectories | §3.2，Fig.2a | Ours 73 > WM-only 66 > SigLIP 63 > w/o latent 60；UMAP/attention | 消融支持 dynamics+action target 有效；“真正形态无关”仍受 retargeting/target embodiment 限制。 |
| 继承 LaST₀ 的 MoT reason-before-act 接口 | §3.1 | In-domain 0.73 > LaST₀ 0.63；复杂任务 Sort 0.95、Put&Zip 0.80 | 模型架构有增益；并非全部来自 human data。 |
| OOL Glove 提供可扩展 action supervision | §3.3、Appendix A | OOL 0.73 > same-time Real-12 0.60、bare 0.63、UMI 0.65；接近 Real-60 0.75 | 数据效率结果有力；成本和精度测量细节不足。 |
| 50% human demo 可替代部分 robot demo | §4.2 Table 1 | Mix-HD 0.68；六任务中四项与 full robot LaST-HD 相同 | 能维持多数任务，但平均低于 full robot 0.73，Pour 0.40 vs 0.60。 |
| 目标域 human data 改善 OOD | §4.2 Table 2 | LaST-HD+HD global 0.56 > LaST₀+HD 0.46；position/object/background 0.41/0.58/0.68 | 证明低成本适配；不是 zero-shot。 |
| 人手 online correction 20 分钟可达 90%+ | §4.2 Fig.4a | Sort Fruits 60条后 80/100/100，平均 93.3% | 单任务、已有较高起点；position 未到 90。 |
| action-conditioned latent 更关注接触 | §4.3、Appendix D | attention 集中于 object/contact，UMAP 人/机器人结构更重叠 | 解释性佐证，受可视化方法与样本选择影响。 |

## 结构地图

| 原文位置 | 作者在做什么 | 与全文主线的关系 | 关键图表 / 公式 |
| --- | --- | --- | --- |
| Abstract | 提出 latent alignment + glove + mixed-to-human recipe | 概括三层系统与 20 分钟结论 | 无主图 |
| §1 Introduction | 从 robot data 成本与 kinematics-only gap 引出 physical reasoning interface | 定义“对齐物理后果”的问题 | Fig.1；三项贡献 |
| §2 Related Work | VLA/CoT、human video、retargeting、cross-embodiment co-training | 说明本文相对 action/representation alignment 的增量 | 无主公式 |
| §3.1 Preliminaries | 定义 action chunk、三种动作空间与 Janus-Pro MoT | 建立 LaST₀→LaST-HD 的模型接口 | $\pi_\theta$；$\mathcal Z$；Fig.2a |
| §3.2 Human-to-Robot Latent Alignment | world model 注入 action，抽深层 future feature 作 Latent GT | 全文核心：对齐“动作物理后果” | Fig.2a；latent cosine loss 在 §3.4 |
| §3.3 Human-Hand Data Collection | OOL Glove 硬件、多视图与 retargeting | 给 scale / fidelity 的数据入口 | Fig.2b；Appendix Fig.6 |
| §3.4 Mixed-to-Human Recipe | Stage 1 mixed co-train；Stage 2 human correction | 把表示方法变成训练/适配流程 | $L_{latent}$、$L_{act}$、balanced batch |
| §4.1 Setup | 六任务、三 embodiment、数据量与 baselines | 界定比较协议 | Appendix Fig.7；动作 14/16/54D |
| §4.2 Results | in-domain、zero-shot、target-HD、online correction | 回答能力、泛化、适配三种问题 | Table 1/2；Fig.3/4a |
| §4.3 Ablations | latent target 与 data source 比较 | 验证 dynamics alignment / glove 质量 | Fig.4b/c |
| §5 Conclusion | 总结并承认 latent reasoning 非实时 | 给出部署边界 | 无新增实验 |
| Appendix A | OOL Glove、语言标注、camera placement、retargeting | 核对低成本与跨本体主张 | Fig.6；4–5× |
| Appendix B–C | 平台动作空间、400K robot pretrain、2000h OOL、任务成功条件 | 核对数据与评测口径 | Eq.(6)–(8)；Table 3/4 |
| Appendix D | UMI/denoise/latent length、UMAP/attention | 补充效率和表征证据 | Table 5–7；Fig.8/9 |
| Appendix E–F | baseline 实现与 failure cases | 检查公平性与失败边界 | Fig.10 |

## 按原文 section 精读

### 1. Introduction / 为什么动作重映射仍不够

引言先建立数据动机：VLA 规模化依赖大量真机 demonstration，而 teleoperation 同时消耗硬件与人工；human hand demonstration 能更自然地覆盖多物体、多接触与多场景。现有方法主要做 kinematic retargeting、morphological translation、visual representation 或 object trajectory prior；近期 VLA 把人手当另一 embodiment 做 joint co-training，但容易依赖数据规模，也可能只学到外观/动作共现。

LaST-HD 的核心问题是：**能否把 VLA 自己的 physical reasoning 当成人→机迁移接口？** 作者不否认 kinematic mapping，而把它视为必要但不充分：几何层先给 action correspondence，latent 层再让人手与机器人围绕相同 predicted physical consequences 对齐。

方法选择 action-conditioned world model 而非 future-frame visual feature，理由是后者主要编码 appearance evolution；带 action 的 forward dynamics 更能表示接触后果。人/机器人轨迹无需严格成对，动作 label 作为 weak anchor。OOL Glove 则负责把 human action label 从不稳定视觉估计升级为高频 metric keypoint。

最后引言把训练分为 two-stage curriculum：mixed human-robot co-training 先把人类 prior 注入策略，部署后再在失败状态采 targeted human correction。注意“human-hand online correction”仍要先跑机器人、识别失败状态，然后由人重新示范；不是人直接实时接管 robot action。

### 2. Related Work / 三条工作线如何交汇

#### 2.1 VLA 与 reason-before-act

VLA 从 RT/OpenVLA 扩展到 action tokenization、flow matching、diffusion decoder。Reason-before-act 又分 textual CoT、future visual/multimodal prediction 和 latent reasoning。LaST-HD 选第三条，因为需要一个足够紧凑、又能承载接触动力学的接口；架构直接延续 LaST₀ 的 MoT latent expert / action expert。

#### 2.2 Learning from human data

Ego4D 等 ego corpora最初多用于视觉 representation；Track2Act/MimicPlay 等提取 keypoints/point tracks，affordance work 学物体可供性，另一些方法学 latent action 或用 AR/VR 收 paired human-robot action。EgoMimic/DexWild 做 explicit kinematics，EgoVLA 通过 IK 转预训练 human motion，H-RDT/EgoScale 用大规模 pre-/mid-training 缩 embodiment gap。

论文声称的差异是第一次用 latent physical reasoning 对齐 human/robot。但“first”属于作者定位，精读时更应看可证伪部分：在相同训练 recipe 下，action-conditioned WM latent 是否确实优于 SigLIP、WM-only 与 no-latent——Fig.4b 给出了肯定结果。

### 3. Methodology

#### 3.1 Problem formulation 与 MoT architecture

给定语言 $\mathbf l$ 和单时刻视觉 $\mathbf I_t\in\mathbb R^{H\times W\times3}$，策略预测：

$$
\mathbf a_{t+1:t+H}\sim \pi_\theta(\cdot\mid \mathbf I_t,\mathbf l).
$$

动作依 embodiment 变化。正文用 dual-arm gripper 的两个 7-DoF EEF action 作例子；WUJI 则在 arm action 上加 20 hand joints。图像统一为 $384\times384$，SigLIP-Large 提取 $f_{img}\in\mathbb R^{N_{img}\times d_v}$，MLP 投到 LLM hidden space。

骨干以 Janus-Pro / DeepSeek-LLM 1.5B 为基础，把 24-layer decoder-only transformer 攅成 MoT：

- reasoning expert 自回归生成 $\mathcal Z\in\mathbb R^{N_{lat}\times d_l}$；
- action expert 通过 flow matching 生成 $\mathbf a_{t:t+H-1}$；
- shared attention 把 latent reasoning 传给 action branch。

和 LaST₀ 相比，结构接口相近，但 teacher target 改了：不再主要用未来 SigLIP/3D/状态多模态 latent，而用 action-conditioned world-model forward-dynamics latent 来对齐 human/robot。

#### 3.2 World Model as Alignment Bridge / 核心机制

![[papers/images/2606.23685v1/Method_V2_page1.png|940]]

**Figure 2a / Latent alignment。** 左侧 world model 在 human/robot 图像与未来 action chunk 上训练，action 经 MLP 后 cross-attend 到 spatial/temporal transformer；最后得到的 feature 被 token pooling 成 Latent GT。中间 LaST-HD 用 cosine loss学 latent token，再让 action expert通过 shared attention 读 reasoning；world model 区域明确标注 “used only during training”。

数据流可写为：

$$
(I_t,a_{t+1:t+H})
\xrightarrow{\text{action-conditioned world model}}
F^{deep}_{WM}
\xrightarrow{\text{MLP + flatten + avg pool}}
z^{GT}_{1:N_{lat}}.
$$

具体选择是：连续 action chunk 通过 cross-attention 注入 world model 每一层；在 final denoising step 抽 deepest U-Net layer，既包含预测未来的时空信息，又比像素 feature 更 domain-invariant。随后 MLP 对齐 $d_l$，adaptive average pooling 固定 token 数。

作者不让 world model 直接出 action，理由有二：其 latent 不够 compact，不适合实时控制；更重要的是 world model 训练时看到了 ground-truth action，直接用于 action prediction 会 information leakage。当前做法把这种 action-aware feature 仅当 teacher target；部署时 student reasoning expert 必须从当前视觉/语言自己预测 latent。

这也形成一个潜在 teacher–student gap：$z^{GT}$ 含 future action 条件，而 inference latent 不含真实未来动作。消融表明这个 target 比无 action WM 更有效，但论文没有单独测 latent 是否解码出 action identity、是否产生 shortcut。它更准确的描述是“action-anchored dynamics supervision”，而非完全无动作泄漏的物理表征。

作者的 invariance 直觉是：人推苹果、机器人推苹果的关节与外观不同，但苹果的运动后果遵循相同物理规律。因此若 world model 学“动作→物体后果”，同任务的两域 feature 应比纯视觉 feature 更接近。UMAP 与 attention 支持这一解释，但它依赖 action label 已被有意义地 retarget 到相应 robot embodiment。

#### 3.3 OOL Glove / 人手数据层

![[papers/images/2606.23685v1/app_OOL_page1.png|900]]

**Appendix Figure 6 / 采集栈。** 单手六个 9-axis IMU 放在手指/手背，配 wrist 6-DoF tracker；头胸 ZED 2i 与左右 Insta360 GO 3S 同步记录。输出是 20 anatomical hand keypoints + 1 wrist keypoint 的 6-DoF metric trajectory，而不只是 glove-specific joint angle。

论文报告：

- 每只手套 <100g；
- tracking >200Hz，end-to-end latency <10ms；
- 每 keypoint average RMS position error <1mm；
- 标准任务数据采集比 robot teleoperation 快 4–5×。

Native human representation 经统一手中心坐标后再派生 robot action：parallel gripper 的开合来自 fingertip distance，wrist trajectory 控制 EEF；dexterous hand 用相对 keypoint geometry 做 IK retargeting。论文明确承认新 hand embodiment 需要新 heuristic mapping，retarget quality 对 pretrain 与 SFT 都关键。因此 “universal action supervision” 是**同一人手轨迹可被多次重映射**，并非不用做机器人专属映射。

语言指令可先录语音再用 VLM润色转写，或由 VLM直接标注。这里潜在有自动标签噪声，但论文未单独评估 instruction pipeline。

“low-cost”也应保留系统口径：手套本体轻量，但完整 setup 含六 IMU、wrist tracker、两腕相机和 ZED；论文没有 BOM、总价或 sub-mm calibration benchmark 表。

#### 3.4 Mixed-to-Human Training Recipe

**Stage 1 / Mixed co-training。** 先在 mixed human/robot trajectories 上训练 action-conditioned WM，目标 embodiment 只要在 pretraining mixture 出现，后续每个 task 无需重训 WM。冻结 WM 并离线预计算 latent GT；LaST-HD 同时在 human/robot sample 上优化 action expert 与 reasoning expert。

对第 $t$ 个 latent token：

$$
\mathcal L_{latent}
=\sum_{t=1}^{N_{lat}}
\left(
1-\frac{\hat z_t\cdot z_t^{GT}}
{\|\hat z_t\|\,\|z_t^{GT}\|}
\right),
$$

总损失为：

$$
\mathcal L_{loss}=\mathcal L_{act}+\lambda\mathcal L_{latent}.
$$

$\mathcal L_{act}$ 是 flow-matching action loss。论文没有给 $\lambda$、batch composition、learning rate 或完整训练 schedule，复现仍需代码/补充配置。

**Stage 2 / Human correction。** 部署 robot、定位 failure state，再用 OOL Glove 采 targeted human-hand DAgger buffer。WM 保持冻结，VLA 只训练 1–2 epochs。每 batch：

$$
\mathcal B=\mathcal B_{prev}\cup\mathcal B_{dagger},
\qquad |\mathcal B_{prev}|=|\mathcal B_{dagger}|.
$$

这一步是“用人手示范替代昂贵 robot teleoperation correction”，不是在线 RL；没有 reward/value update，仍属于 supervised post-training / DAgger-style aggregation。

### 4. Experiments

#### 4.1 三种平台、六项任务

![[papers/images/2606.23685v1/Asset_page1.png|820]]

**Appendix Figure 7 / Real setup。** Galaxea R1 Lite 与 Tianji Marvin，后者可接双夹爪或 WUJI 20-DoF dexterous hand；所有平台使用 head ZED 2i + two wrist Insta360 GO 3S。

| Embodiment | Action space | Tasks | 操作难点 |
| --- | ---: | --- | --- |
| Galaxea R1 Lite dual gripper | 14D：两臂各 6 joint delta + gripper | Unscrew Bottle Cap；Organize Box | 双臂持续接触、重复旋拧；多物体分区+盖板 |
| Tianji Marvin dual gripper | 16D：两臂各 7 joint delta + gripper | Sort Fruits；Put Items to Bag and Zip | 多步分类；放物+一手固定袋、一手拉链 |
| Tianji Marvin + dual WUJI | 54D：两臂各 7 + 每手20 joint delta | Pour Water；Grasp with a Clamp | 高维抓瓶/倾倒；操纵夹子夹肉饼并放面包 |

每任务收 100 条 in-domain robot teleop 与 50 条 in-domain OOL human demo；每个 unseen position/object/background scenario 只收 60 条 OOL demo。三路 RGB 为 $384\times384$。每方法每任务评 20 rollouts，报 task completion success。

基线为 $\pi_{0.5}$、Cosmos-Policy、LaST₀，均 official full fine-tuning。输入分辨率依官方保持：$\pi_{0.5}$/Cosmos 224，LaST₀/HD 384；高维手任务直接修改 action output dimension。不同分辨率忠实于各自预训练，但也不是完全同输入容量比较。

#### 4.2 In-domain / 架构能力与人手替代能力要分开

| Method | Unscrew | Organize | Sort | Put&Zip | Pour | Clamp | Avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| $\pi_{0.5}$ | 0.70 | **0.70** | 0.85 | 0.75 | 0.30 | 0.40 | 0.62 |
| Cosmos-Policy | 0.75 | 0.50 | 0.85 | 0.60 | 0.20 | 0.20 | 0.52 |
| LaST₀ | 0.80 | **0.70** | 0.75 | 0.60 | 0.40 | **0.50** | 0.63 |
| **LaST-HD (100 robot)** | **0.85** | **0.70** | **0.95** | **0.80** | **0.60** | 0.45 | **0.73** |
| **LaST-HD Mix-HD (50 robot+50 human)** | **0.85** | **0.70** | 0.85 | **0.80** | 0.40 | 0.45 | **0.68** |

完整 LaST-HD 的 0.73 证明 latent reasoning architecture 即使只用 robot downstream demos 也有优势；它不直接证明 human data。Mix-HD 用一半 human 替代一半 robot 后在四任务持平，但 Sort 0.95→0.85、Pour 0.60→0.40，平均掉 5 points。更准确的结论是：**人手数据能在多数任务替代相当一部分 robot data，但对精细灵巧动力学仍有 gap。**

LaST-HD 也并非逐项第一：Grasp Clamp 是 LaST₀ 0.50 > LaST-HD 0.45；Organize 多法同为 0.70。

#### 4.3 Generalization / zero-shot 与 target-HD adaptation

论文评两种完全不同的范式：

- **Zero-shot**：直接拿 in-domain checkpoint 测 unseen scenario，不再训练；
- **w/ unseen HD**：在原 100 robot demos 之外，再加入该 unseen scenario 的 60 human demos 训练。

| Method / training | Unseen Position | Unseen Object | Unseen Background | Global Avg |
| --- | ---: | ---: | ---: | ---: |
| $\pi_{0.5}$，in-domain only | 0.12 | 0.36 | 0.43 | 0.30 |
| Cosmos，in-domain only | 0.13 | 0.28 | 0.38 | 0.26 |
| LaST₀，in-domain only | 0.15 | 0.32 | 0.43 | 0.30 |
| LaST-HD Mix-HD，in-domain only | 0.15 | 0.35 | 0.43 | **0.31** |
| LaST₀ + unseen HD | 0.33 | 0.49 | 0.58 | 0.46 |
| **LaST-HD + unseen HD** | **0.41** | **0.58** | **0.68** | **0.56** |

核心结果是 target human data 的利用效率：同样拿到 60 human demos，LaST-HD 比 LaST₀ global 高 10 points，三类 scenario 分别高 8/9/10 points。最难的是 spatial shift，position 只有 0.41；background 最容易到 0.68。

![[papers/images/2606.23685v1/vis_V3_page1.png|900]]

**Figure 5 / OOD qualitative。** 左列是真机 execution，右列是 unseen-background/object/position 下针对性 OOL human demos。它展示了训练信号来自目标条件的人，而非 robot 在该条件的 teleoperation。

论文文字说 “using only human-hand demonstrations” 时，精确含义是**OOD target-domain 追加数据只有 human**；模型仍保留 100 条 in-domain robot demos、400K robot pretraining 和含 target embodiment 的 world-model pretraining。不能解读成从零 human-only policy。

#### 4.4 Human-Hand Online Correction / 20 分钟结论

![[papers/images/2606.23685v1/ablation_V2_page1.png|940]]

**Figure 4a / Sort Fruits correction curve。** 横轴同时标数据条数与采集秒数：10条=200s，20条=400s，60条=1200s。三条曲线在 n=0 已有较高起点，纠错逐步提高。

| Human correction trajectories | Time | Position | Object | Background | Mean |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0s | 0.60 | 0.70 | 0.90 | 0.73 |
| 10 | 200s | 0.65 | 0.90 | 0.95 | 0.83 |
| 20 | 400s | 0.70 | 0.95 | 1.00 | 0.88 |
| 60 | 1200s / 20min | 0.80 | 1.00 | 1.00 | **0.93** |

因此摘要的“only 20 minutes, over 90% accuracy”是三 scenario 平均的合理概括，但不是每类都 >90，也不是六任务平均。20 trajectories 时只有 background 达100；正文相应句子没有说总体已100，引用时要保留对象。

#### 4.5 Main ablation / latent target 到底贡献多少

Figure 4b 左侧：

| Latent supervision | Avg success |
| --- | ---: |
| **Action-conditioned WM (LaST-HD)** | **0.73** |
| WM-only（无 action condition） | 0.66 |
| Future SigLIP feature | 0.63 |
| W/o latent（只留 action expert） | 0.60 |

三个差值分别回答三个问题：latent reasoning 本身约 +13 points；world-model temporal target 相对 future appearance约 +3；再加 action anchor 约 +7。由于都是 Sort Fruits 三 OOD setting 的平均，尚不能断言相同分解在六任务全部成立。

Figure 4c 显示 LaST-HD latent attention 更集中在手/夹爪与 object contact，SigLIP target 更分散；这与 forward-dynamics 解释一致。

#### 4.6 Data collection ablation / OOL 是不是只因数据更多

| Data source | Trajectories / time relation | Success |
| --- | --- | ---: |
| Real-robot | 60 | **0.75** |
| **OOL Glove** | 60 | **0.73** |
| Real-robot | 12，与 60 OOL 同采集时间 | 0.60 |
| Vision-based bare hand (HawOR) | 60 | 0.63 |
| UMI portable gripper | 60 | 0.65 |
| OOL Glove palm-view camera | 60 | 0.67 |

OOL 只比 Real-60 低2 points，却比同时间 Real-12 高13 points，支持 data-efficiency claim。Bare-hand 低10 points说明精确 keypoint/action labels有价值；UMI 受二指 gripper 限制，难重映射到 high-DoF hand。Thumb-index web-space camera 比 palm view 更能看到接触，差6 points。

### 5. Conclusion / 显式承认的限制

结论将贡献收束到：action-conditioned WM latent 监督、OOL Glove、mixed-to-human recipe。作者明确承认 **latent reasoning is not yet real-time**；未来考虑 fast-slow design 或进一步压缩 latent space。

这与 Appendix latent-length ablation 相呼应：16 token 成功率最高 0.78，但自回归 latency 更大；主实验选 4 token、成功率 0.73。论文为了控制速度牺牲约5 points，却没有报告实际 Hz/ms，所以只能知道 trade-off 存在，不能量化是否满足具体控制频率。

### 6. Appendix / 复现与边界

#### 6.1 Pretraining data / “2000 小时 human”如何使用

LaST-HD VLA backbone 预训练使用 400K robot trajectories / 28M frames，来自 Open-X、DROID、RoboMIND 等；为和 $\pi_{0.5}$/LaST₀ 公平，**VLA MoT 本身只在 robot trajectories 上 pretrain**。

团队另报告 OOL Glove 累积数据恰好约 216M frames / 2000.1h：

| Category | Frames | Duration | Ratio |
| --- | ---: | ---: | ---: |
| Household | 98,680,680 | 913.7h | 45.7% |
| Precise | 3,504,600 | 32.5h | 1.6% |
| Deformable | 106,519,320 | 986.3h | 49.3% |
| Mobile manipulation | 7,295,400 | 67.6h | 3.4% |

Human + robot data用于 action-conditioned world-model pretraining，再离线生成 VLA latent targets。论文没有给 world-model mixture ratio、具体多少 2000h 真正进入当前 checkpoint，也说计划未来发布 high-quality dataset。因此“2000h”是资源规模报告，不应直接当作当前全部训练量或已公开数据集。

#### 6.2 World model denoising 与 latent length

| Ablation | Values | Success | 选择 |
| --- | --- | --- | --- |
| Denoising steps | 2 / 5 / 10 | 0.73 / 0.72 / 0.76 | 2，离线 target 构造更快 |
| Latent tokens | 2 / 4 / 8 / 12 / 16 | 0.67 / 0.73 / 0.67 / 0.70 / **0.78** | 4，性能–延迟折中 |

World model 不参与 inference，所以 denoising step 只影响预计算成本；10 step 高3 points但作者视为接近，选2。Latent token 则直接影响 runtime，因为 reasoning expert 自回归生成；主配置没有选最佳性能16。

#### 6.3 UMAP 与 attention

![[papers/images/2606.23685v1/ap_UMAP_page1.png|900]]

**Appendix Figure 8 / 四个 UMAP case。** SigLIP target 下 human blue 与 robot orange 分成不同 clusters；action-conditioned target 下两色沿相似几何轨迹交织。它说明表示更难按 embodiment 线性分开、同任务进程更接近，但 UMAP 会扭曲距离，且没有 retrieval/classification metric；不能单独证明 latent 是真实 causal physics。

Attention 图同样显示 Ours 更盯 manipulated object、contact region，而非背景。更强验证可包括 cross-embodiment phase retrieval、forward consequence prediction、linear probe 去 embodiment / 保 task，以及对 action label shuffle 的敏感性。

#### 6.4 Task protocol 与一个内部不一致

六任务 success 都是人定义的完整/阶段完成：Sort 必须所有物体分层正确；Put&Zip 要物体入包且拉链全关；Clamp 要肉饼放在面包上。Pour Water 的 protocol 特别写明**测试时瓶盖保持关闭，只评完整倾倒动作而非真实液体转移**。

但 Appendix failure analysis 又展示 liquid spill，并称模型无法判断水是否仍在流。可能是额外定性试验或文稿版本不一致；因此主表中的 Pour 0.60 应按“闭盖倾倒动作”理解，不能作为真实 liquid dynamics 成功率。

#### 6.5 Failure cases

![[papers/images/2606.23685v1/app_fialue_page1.png|880]]

**Appendix Figure 10 / 三类失败。**

1. **Object slipping**：夹子抓点/接触力不准，肉饼运输时滑落；策略会尝试 re-clamp，但掉入不可恢复状态仍失败。
2. **Fluid process prediction**：液体随机、难判断是否仍在流，可能 spill；与主评测闭盖 protocol 需分开。
3. **Accumulated coordination errors**：双臂旋盖需长期保持相对接触，小 pose error 累积后左手让瓶身倾斜，右手无法继续。

这些失败说明 latent physics 并没有取代 force/tactile feedback、精确双臂约束或显式 fluid state。论文只有 RGB + kinematic action，接触力仍主要从视觉/先验间接推断。

## 方法细节

### LaST₀ → LaST-HD 的增量

| 层面 | LaST₀ | LaST-HD |
| --- | --- | --- |
| 核心问题 | 怎样用 latent spatio-temporal CoT 兼顾推理与快动作 | 怎样让 human data 的 physical dynamics 进入 latent CoT |
| Latent teacher | future visual / 3D / proprioceptive representations | action-conditioned world-model deepest future feature |
| 跨本体 | 不是主问题 | human/robot unpaired latent alignment |
| 数据系统 | robot demonstrations | robot + OOL human hand + targeted correction |
| 硬件贡献 | 无 | OOL Glove |
| 训练流程 | pretrain / SFT + heterogeneous frequency | mixed co-train → human correction |
| 当前速度 | 强调 fast-slow / 15.4Hz（原论文） | 本文明确说 latent reasoning 尚非实时，未报Hz |

### 三种“对齐”不要混为一谈

1. **Geometric alignment**：keypoints / fingertip distance / IK 把人手动作映到特定 robot action；仍是手工。
2. **Dynamic latent alignment**：world model 学 action-conditioned physical consequence；这是论文的新贡献。
3. **Policy alignment**：reasoning expert 预测 latent、action expert 生成 executable robot action；由 mixed training 实现。

如果第1层动作 anchor 错了，第2层可能学到错误后果；因此 latent alignment 是对 retargeting 的补充，不是替代。

### Offline teacher, online student

$$
\underbrace{(I,a_{future})\rightarrow WM\rightarrow z^{GT}}_{\text{offline only}}
\quad\Longrightarrow\quad
\underbrace{(I,l)\rightarrow \hat z\rightarrow \pi(a)}_{\text{deployment}}.
$$

这个分工让重 world model 不拖慢推理，但真正 runtime 瓶颈变成 $N_{lat}$ 个 autoregressive latent token；16-token 性能更好却更慢。

## 实验设置、数据集、基线、指标

| 维度 | 设定 |
| --- | --- |
| Backbone | Janus-Pro；SigLIP-Large；DeepSeek-LLM 1.5B，24-layer MoT |
| Observation | head + two wrist RGB；LaST-HD/LaST₀ 为 $384^2$，$\pi_{0.5}$/Cosmos 为 $224^2$ |
| Action | dual gripper 14D/16D；dual WUJI 54D；flow-matching chunk |
| VLA pretrain | 400K robot trajectories、28M frames；仅 robot data 以公平比较 |
| World-model teacher | mixed OOL human + real robot；action-conditioned；offline latent precompute |
| Downstream in-domain | 每任务100 robot；Mix-HD 为50 robot+50 human |
| OOD adaptation | 每任务、每个 unseen scenario 加60 human demos |
| Online correction | Sort Fruits；0/10/20/60 human trajectories，balanced replay，1–2 epochs |
| Baselines | $\pi_{0.5}$、Cosmos-Policy、LaST₀；data-source 对照 Real/HawOR/UMI/palm view |
| Evaluation | 六任务、三 embodiment；每方法每任务20 rollouts；success rate，无 CI/seed |

## 主要结果、消融或对比

1. **模型架构结果**：LaST-HD full-robot 0.73 > LaST₀ 0.63，但 Clamp 任务 LaST₀ 更高。
2. **人手替代结果**：50 robot+50 human 为0.68，可在四任务持平 full robot；不是无损全面替代。
3. **zero-shot 结果弱**：Mix-HD 0.31 vs LaST₀/$\pi_{0.5}$ 0.30；主要价值是更好吸收目标域 human data。
4. **target-HD 结果**：同样60 human，LaST-HD global 0.56 vs LaST₀ 0.46。
5. **correction 结果**：Sort Fruits 用20min达到80/100/100，平均93.3%，不是所有场景/任务都 >90。
6. **机制消融**：action-conditioned WM 73 > WM-only66 > SigLIP63 > no-latent60。
7. **采集效率**：OOL73≈Real-60 75，显著高于同时间 Real-12 60；但 glove cost/accuracy protocol 欠缺。
8. **性能–延迟**：16 latent token 0.78最佳，主配置4 token 0.73；没有 runtime 数字。

## 图表、公式与表格线索

| 线索 | 内容 | 阅读时抓什么 |
| --- | --- | --- |
| Fig.1 | glove→unpaired human/robot→WM→LaST-HD→六任务 | 系统三层与31/56泛化口径 |
| Fig.2a | action-conditioned WM teacher + MoT student | WM只训练时使用；latent GT 如何进入 shared attention |
| Fig.2b | OOL Glove | 六IMU、完整相机/追踪栈，不只是手套布料 |
| Fig.2c | mixed co-train→human correction | WM冻结、VLA更新、balanced replay |
| $L_{latent}$ | cosine target alignment | 监督的是方向，不是像素/文本 token |
| Table 1 | in-domain | full robot 0.73、Mix-HD0.68，分开模型与人手贡献 |
| Table 2 | OOD | zero-shot 0.31 与 target-HD0.56，最重要口径 |
| Fig.3/5 | robot rollout 与 unseen human demos | target condition 只有human追加数据 |
| Fig.4a | correction scaling | 20min平均>90，但 position80 |
| Fig.4b/c | latent/data消融与attention | action-conditioned dynamics 是核心组件 |
| Appendix Table 3/4 | 400K robot pretrain、2000h OOL | 哪些数据进VLA、哪些进teacher要分清 |
| Appendix Table 5–7 | data source、denoise、latent length | 采集效率与速度–性能折中 |
| Fig.8/9 | UMAP / attention | 定性表征解释，不是因果证明 |
| Fig.10 | failures | slip、fluid、coordination accumulation |

## 主张-证据-边界矩阵

| 主张 / 结论 | 原文证据 | 解释 | 边界 / 适用条件 |
| --- | --- | --- | --- |
| Latent dynamics 比 action-only co-training 更能用 human data | 73 vs no-latent60 | reasoning target 提供跨本体时空约束 | 单任务三OOD平均消融；未跨六任务重复 |
| Action conditioning 是对齐关键 | Ours73 vs WM-only66 | action是weak anchor，feature更关注物理后果 | teacher看future action；shortcut/信息泄漏需更强probe |
| 比 future visual latent 更好 | 73 vs SigLIP63 | dynamics target比appearance evolution更适合接触 | SigLIP与WM teacher容量/训练代价未完全等价 |
| Human trajectories无需配对 | 方法设定 + target-HD gains | 共享任务/动作后果可弱对齐 | 仍需相似任务语义、人工retarget与target embodiment pretrain |
| OOL human可替代部分robot data | Mix-HD0.68 vs full0.73 | 一半robot data被human替换，四任务持平 | Pour掉20points；非全部任务无损 |
| OOL可高效驱动OOD | HD global0.56 vs zero-shot0.31 | 目标条件人手示范提供覆盖 | 不是zero-shot；保留in-domain robot基础 |
| 20分钟达到90%+ | Sort correction均值93.3 | targeted failure-state data效率高 | 单任务；position80；起点已73平均 |
| Glove比bare/UMI数据好 | OOL73 vs63/65 | 高频metric keypoints降低tracking噪声 | 未控制全部硬件/视角差；无CI |
| 低成本且高精度 | <100g, >200Hz, <10ms, sub-mm, 4–5× | 硬件指标符合快速采集方向 | 无BOM、校准/ground-truth protocol、用户规模 |
| 2000h human data可规模化 | Table 4 | 216M frames覆盖家务/形变/移动 | 当前checkpoint使用比例和数据公开状态不明 |
| Morphology-agnostic | UMAP/attention +三平台结果 | latent弱化外观差异 | 新hand仍要heuristic mapping，target embodiment data不可少 |

## 局限与可追问点

1. **Zero-shot claim 要收紧。** 为什么 Mix-HD 的 global zero-shot 只比 LaST₀ 高1 point？方法更像 target-human-data adapter，而非无需目标数据的通用泛化器。
2. **Action-conditioned teacher 是否学 shortcut？** 应做 action shuffle、wrong-action counterfactual、latent→action linear probe、只给action不看未来图像等实验。
3. **“Unpaired”需要多大任务重合？** 若 human/robot任务语义、物体或动作完全不重叠，弱 anchor 是否仍能形成共同空间？
4. **Retargeting 仍是瓶颈。** 作者承认新hand要新pipeline；应报告mapping误差、contact preservation和learned retargeter基线。
5. **World-model pretraining数据不透明。** 2000h中实际用了多少、human/robot ratio、target embodiment覆盖、是否存在downstream object/scene leakage？
6. **训练超参不完整。** $\lambda$、action horizon、batch ratio、optimizer/LR、WM规模/预训练步数、VLA更新策略均未充分给出。
7. **Glove指标缺测量协议。** sub-mm ground truth由何系统提供、覆盖多少用户/手型/姿态、磁干扰和IMU drift如何处理？
8. **采集成本应算完整栈。** Wrist tracker、Insta360、ZED与校准时间是否计入“low-cost/4–5×”？
9. **统计不足。** 20 rollouts无CI/多seed；5%步进往往就是1次trial，0.73等消融平均也缺方差。
10. **Online correction的失败状态如何复现给人？** robot failure pose如何转成human演示的初始条件，correction是否需要人工场景重置？论文没有展开操作成本。
11. **Latency未量化。** 既然结论承认不实时，应报告4/16 token的端到端Hz、控制频率和success-per-latency。
12. **真实液体协议不一致。** 主评测闭盖只看倾倒姿态，failure figure又展示spill；需区分定量benchmark与额外实液演示。
13. **缺力/触觉。** slip、clamp、unscrew均暴露contact force误差，纯RGB latent dynamics对接触状态仍不充分。

## 与当前库的连接

- 与 [[@liu2026last0-latent-spatio-temporal|LaST₀]]：直接技术谱系。LaST₀ 回答“怎样在VLA里做高效潜时空推理”，LaST-HD 回答“怎样用action-conditioned teacher把human/robot物理后果放进这个潜空间”。
- 与 [[@kim2026ego-pi|Ego-Pi]]：两者都用人手数据、都保留几何retargeting。Ego-Pi主要迁移sorting/ordering/subtask semantics，LaST-HD主要对齐forward dynamics并覆盖target-scene correction；Ego-Pi证明语言subtask重要，LaST-HD证明action-conditioned latent重要。
- 与 [[@qwen2026robotmanip|Qwen-RobotManip]]：Qwen用大规模human-to-robot rendering和canonical action实现scale；LaST-HD不渲染robot外观，而用world-model latent吸收未配对human data。前者强在数据规模/跨本体预训练，后者强在目标域human correction效率。
- 与 [[@paliwal2026do-i-dexterous-manipulation|Do as I Do]]：同属human→dexterous路线。LaST-HD用专用IMU glove取得高精度action label，代价是硬件/校准；自然视频路线更可扩展但动作重建噪声更大。Bare-hand63 vs OOL73正是该trade-off的局部证据。
- 与 [[@liu2026taco-tactile-self-corrector|TACO]]：同组都用world model做policy supervision/correction。TACO引入触觉检测并自纠错接触失败，正好回应LaST-HD的slip/force盲区；可组合成human dynamics pretrain + tactile online corrector。
- 与 [[@yu2026wm-dagger|WM-DAgger]]：两者都先部署找failure再聚合修复数据。WM-DAgger用world model发现/生成修复，LaST-HD用人手在failure condition采targeted corrections；比较点是failure identification与correction成本。
- 与 [[@qian2026wam-rl|WAM-RL]] / [[@zhang2026lingbot-va2|LingBot-VA 2.0]]：这些工作把world/action model更直接地放进动作生成或RL；LaST-HD把world model限制为offline latent teacher，避免实时生成开销，但student latent仍有自回归latency。
- 与 [[@dodeja2026q2rl|Q2RL]] / [[@deng2026e2hil|E2HiL]]：三者都是post-training数据效率问题。Q2RL门控BC/RL动作，E2HiL筛human intervention sample，LaST-HD以human-hand示范替代robot correction；监督接口分别是Q、entropy influence、latent dynamics。

## 精读路线 / 为什么需要回看

1. **先看 Fig.1 右下两组柱**：先记住 in-domain73、zero-shot31、target-HD56，防止把target adaptation写成zero-shot。
2. **再看 Fig.2a + $L_{latent}$**：弄清world model看future action但只作offline teacher，部署时reasoning expert自己预测latent。
3. **读 §3.3 + Appendix A**：确认OOL不是裸手视觉估计，而是IMU+tracker+三相机的完整采集栈；“universal”仍需robot-specific retargeting。
4. **用 Table 1 分离两类贡献**：LaST-HD full-robot73是架构效果，Mix-HD68才是human替代robot的证据。
5. **用 Table 2 分离两种泛化**：in-domain-only的zero-shot与加60条unseen human是不同训练范式。
6. **看 Fig.4a/b**：20分钟结论只在Sort Fruits，机制消融则只在该任务三OOD平均；不要外推到全部六任务。
7. **最后读 Appendix Table 4/6/7 + failure analysis**：核对2000h使用口径、4 vs16 latent速度trade-off、retargeting/接触/液体边界。
8. **若要复现**：优先索要WM/VLA完整训练超参、action-conditioning counterfactual、glove calibration protocol、真实runtime和多seed统计。
