---
tags:
  - bilingual-reading
paper: "[[@sun2026revisiting-embodied-chain-thought]]"
source_pdf: "[[papers/pdfs/sun2026revisiting-embodied-chain-thought.pdf]]"
images: "papers/images/sun2026revisiting-embodied-chain-thought/"
image_index: "[[papers/images/sun2026revisiting-embodied-chain-thought/index.md]]"
arxiv: "2606.03784v2"
created: 2026-08-20
---

# Revisiting Embodied Chain-of-Thought for Generalizable Robot Manipulation

paper:: [[@sun2026revisiting-embodied-chain-thought]]
pdf:: [[papers/pdfs/sun2026revisiting-embodied-chain-thought.pdf]]
images:: [[papers/images/sun2026revisiting-embodied-chain-thought/index.md]]

> [!warning] 版本与证据状态
> 本稿按 arXiv 2606.03784v2 和同版本源码逐节整理。论文使用 NeurIPS 2026 preprint 模板，正文没有声明录用状态。作者承诺公开代码、数据与模型，但截至 2026-08-20，公开项目仓库仍只有项目页、论文和展示文件。涉及最大规模、SOTA 与真机泛化的表述均按作者报告处理。

## 一句话总结

ERVLA 研究的不是怎样让机器人生成更长的思维链，而是怎样让 embodied CoT（具身思维链）真正改变动作表征。作者用 978,743 条机器人轨迹发现 movement description（运动描述）和 point trajectory（点轨迹）比孤立的高层解释更有用，又用 reasoning dropout（推理丢弃）、choice policy（候选策略）、knowledge truncation（知识截断）与 flow-matching DiT 把 CoT 留在训练期，部署时直接生成连续动作。

## 核心词汇速查

| English | 中文 | 在论文中的作用 |
| --- | --- | --- |
| embodied chain-of-thought, ECoT | 具身思维链 | 把任务理解、空间定位、子任务规划和动作提示写成结构化监督 |
| representation-shaping supervision | 表征塑形监督 | CoT 的最终用途，不要求部署时逐 token 输出 |
| CoT contamination | CoT 污染 | 抖动坐标与错误框对相似观测施加不一致监督 |
| reasoning dropout | 推理丢弃 | 训练样本在 /cot 与 /no_cot 间随机切换 |
| Understanding | 任务理解 | 保存全局 goal |
| Grounding | 空间落地 | 保存多视角物体框等视觉坐标 |
| Planning | 规划 | 保存 episode-level plan、当前 subtask 与 reasoning |
| Acting | 动作提示 | 保存 movement、gripper 与 future point trajectory |
| choice policy | 候选策略 | 预测 5 个候选连续动作块和候选误差 |
| action-query token | 动作查询 token | 把动作级判别监督注入 VLM hidden state |
| knowledge truncation, KT | 知识截断 | DiT 只读取语义前缀 KV，不读取控制查询 KV |
| knowledge insulation, KI | 知识隔离 | 阻断动作损失回传 VLM 的对照设计 |
| diffusion transformer, DiT | 扩散 Transformer | 通过 flow matching 生成连续动作块 |
| rectified flow | 整流流 | 连续动作头的训练目标 |
| per-layer KV cache | 逐层 KV 缓存 | VLM 向 DiT 传递语义记忆的接口 |
| action horizon | 动作时域 | 预训练为 30，LIBERO 与 VLABench 后训练为 10 |
| success rate, SR | 完整成功率 | 任务全部完成的比例 |
| progress score, PS | 过程分 | 长任务已完成子步骤的部分得分 |
| intention score, IS | 意图分 | VLABench 对语义意图理解的评分 |

## 摘要

论文从三个没有被拆干净的问题出发。具身 CoT 应该包含哪些字段，推理怎样接入动作策略，推理数据增加后是否真的会继续带来收益。以往工作常把三件事绑在一起，更换 CoT 字段时也换架构，更换动作头时也换训练数据，很难判断提升来自哪里。

作者先构造一套结构化 ECoT schema（具身 CoT 模式），再把 AgiBot World、DROID、Fractal、BridgeData V2 和 MolmoAct 统一标注成 978,743 条轨迹、226.3M 个样本、2592.5 小时的数据。字段由 Understanding、Grounding、Planning 与 Acting 四组组成，覆盖 goal、plan、subtask、object box、gripper、movement description 和 image-space future trajectory。

受控实验给出一个不太讨巧的结论。Goal、Planning、Subtask 与 Reasoning 单独使用都让 VLABench 平均成功率小幅下降。Movement 带来 +4.1，Point trajectory 带来 +4.8，Subtask+Movement+Point trajectory 带来 +7.4。到了自动标注预训练，Gripper 与 Bounding box 又因坐标抖动分别掉 5.6 和 6.1 个点。reasoning dropout 把损失压到 0.8 和 1.0 个点，并让 Point trajectory 的收益从 +1.4 回升到 +3.0。

ERVLA 据此选用 Qwen3-VL-4B 加 36 层 DiT。VLM 同时学习 CoT token、5 候选动作块和候选误差，DiT 从语义前缀的逐层 KV cache 读取条件并生成连续动作。Knowledge truncation 切掉 appended control-query turns（附加控制查询轮次）的 KV，防止 DiT 复制训练期捷径。动作 flow loss 仍回传 VLM，因此不是 knowledge insulation 那种完全隔离。

最终模型在 LIBERO-Plus 得到 86.9% 总成功率，比 π0.5 的 85.5% 高 1.4 个点。在 VLABench 上，平均 SR、PS 与 IS 分别为 53.2、65.9 和 70.4。真机实验含 20 个任务，每任务 5 次，ERVLA 平均 SR 为 55、PS 为 67。真正拉开差距的是 Semantic 与 Long-horizon，而不是干净的 Basic 操作。

## 论文主线

![[papers/images/sun2026revisiting-embodied-chain-thought/overview.png|760]]

Figure 1 把整篇论文压在一张图里。左侧是大规模 ECoT 语料，中间是 CoT supervision、action query、knowledge-truncated KV 与 DiT，右侧是仿真、缩放与真机结果。论证顺序也照这个结构展开。

作者先问推理内容。孤立高层语言不够，推理必须把语义接到末端运动和图像空间轨迹。再问推理接口。把长 CoT 当成动作 token 的前缀会引入延迟、长度变化与 exposure error（暴露误差），把 VLM 与动作头完全隔离又得不到动作反馈。论文选择把显式 CoT 当训练脚手架，让 choice loss 与 flow loss 共同把 VLM 调成 action-aware representation（动作感知表征）。

数据规模是第三个环节。AR CoT+FAST 在扩大预训练混合时不升反降，ERVLA 才在图示的扩展曲线上稳定上升。主张并不是 CoT 天然可扩展，而是标注质量和推理到动作接口共同决定它能否扩展。

## 贡献与结论对照

| 作者声称的贡献 | 对应证据 | 可接受的结论 | 不能外推的部分 |
| --- | --- | --- | --- |
| 最大规模结构化 ECoT 语料 | 978,743 trajectories、226.3M samples、2592.5 h | 数据覆盖五个公开机器人源和多视角、双臂设置 | 数据与标注尚未公开，最大规模声明无法独立核验 |
| 找出更有效的 CoT 字段 | 固定 Qwen3-VL-4B 与 AR CoT+FAST 的 15 组字段消融 | 动作相关字段比孤立高层字段更直接 | 结论仍依赖 VLABench 和当前动作接口 |
| 定义并缓解 CoT contamination | Gripper -5.6、Box -6.1，dropout 后为 -0.8、-1.0 | 自动坐标标注的时序抖动会伤害动作学习 | dropout 没有替代置信度估计和标注校准 |
| 提出可扩展的 ERVLA 接口 | No Choice 61.9、No CoT 70.8、No Choice+KI 76.5、Choice w/o KT 84.7、Full 86.9 | choice 与 KT 都对 LIBERO-Plus 总分有贡献 | 缺少多随机种子和完整计算预算 |
| 获得仿真 SOTA | LIBERO-Plus 86.9，VLABench SR 53.2 | 当前表格中的总指标领先所列基线 | 若干子指标不领先，LIBERO-Plus 总分优势仅 1.4 |
| 提高真机语义与长时域能力 | Semantic SR 42、Long-horizon PS 55 | 在两族任务和当前示范集内优于对照 | 不能代表开放世界家庭或跨本体零样本 |

## 结构地图

| 原文 section | 主要内容 | 在论证链中的工作 |
| --- | --- | --- |
| 1 Introduction | 三个未决问题与 CoT contamination | 把研究对象从「有没有 CoT」改成「什么信号、什么接口、怎样扩展」 |
| 2 Methodology | 数据、ERVLA 架构、联合损失 | 给出训练期推理到连续动作的完整实现 |
| 2.1 Embodied CoT Data Construction | 四组字段和五个数据源 | 建立可做受控消融与规模研究的数据底座 |
| 2.2 ERVLA Architecture | Qwen3-VL、choice branch、DiT、KT | 设计推理表征与动作生成的耦合接口 |
| 2.3 Training Recipe | CoT CE、flow、choice、score、dropout | 说明各监督怎样共同更新 |
| 3 Experiment | benchmark、baseline 与三个研究问题 | 把内容、接口、规模逐层验证 |
| 3.1 Effective ECoT Signals | 字段、污染、AR 缩放、VLM transfer | 找出 ERVLA 设计的经验依据 |
| 3.2 ERVLA Design and Scaling | 主结果和架构消融 | 检验 choice、KT 与数据规模 |
| 3.3 Real-world Experiments | 20 个真机任务和四档难度 | 验证收益是否集中在语义与长时依赖 |
| 4 Conclusion | 推理是接口而非输出格式 | 收束论文主张 |
| Appendix A Related Work | 显式、视觉、潜式推理与动作表示 | 标出 ERVLA 在设计空间中的位置 |
| Appendix B Data Pipeline | 分段、投影、轨迹、grounding、过滤 | 交代自动标注怎样控制时序噪声 |
| Appendix C Training Details | 数据表、超参、后训练、消融定义 | 提供复现所需但仍不完整的配置 |
| Appendix D Detailed Results | 字段、VLM transfer、仿真和真机明细 | 检查平均数背后的混合结果 |
| Appendix E Limitations | 标注质量与动态推理 | 划出作者自己承认的边界 |

## 按原文 section 精读

### 1 Introduction

引言把 VLA 的困难放在 semantic-to-action gap（语义到动作鸿沟）上。更强的 VLM 知道更多物体、属性和常识，却不保证末端执行器能在正确时刻移动到正确位置。reason-before-act（先推理再行动）因此出现，但现有方案把可见文字、潜变量、未来图像和动作 token 混成不同实现，缺少统一比较。

作者提出三个问题。哪些 ECoT form（具身 CoT 形式）真能帮助控制，reasoning 应作为 visible trace、latent variable 还是 training signal，CoT data 能否扩展。第三个问题很关键，因为自动标注一旦扩到亿级样本，微小的 detector jitter 会在近似相同的画面上反复给出矛盾坐标。

CoT contamination 由此进入主线。论文没有把自动标注噪声当成普通数据清洗问题，而是强调 reasoning label 会直接改变表征空间。高频抖动的 box 与 gripper coordinate 比偶发语言错误更容易迫使相似 observation 分开。稀疏标注、几何投影和 reasoning dropout 都服务于这个诊断。

ERVLA 的答案是 mixture-of-transformers（混合 Transformer）结构。VLM 保留文本推理能力，choice branch 给 VLM 注入动作级判别，DiT 用 flow matching 生成平滑连续动作，KT 控制 DiT 能读哪些 KV。推理在训练时可见，在部署时可以省略。

#### 关键证据 / 图表 / 公式

- Figure 1 展示语料、模型与结果的全链路，支撑本文研究对象是推理监督到动作表征的接口。
- Figure 2 展示 ECoT schema 和数据规模，支撑大规模受控研究的前提。
- 引言报告 LIBERO-Plus 86.9、VLABench SR 53.2，以及 Spatial track 的 background 与 lighting variation 达到 100%。这些是作者用来证明 OOD generalization（分布外泛化）的入口数字。

阅读时要留一个边界。更强 VLM 不自动变成更强 VLA 是论文的动机，后文的 VLM transfer 表也不是所有 backbone 都因 CoT 提升。PaliGemma 与 Florence 在多项任务上反而下降，真正稳定获益的是较强的 Qwen 系列。

### 2 Methodology

这一节依次回答数据怎样造、模型怎样接、损失怎样训。三个子节不能拆开看。若只看 ERVLA 图，会误以为 choice policy 是主贡献。受控实验真正支持的是一组联合设计，ECoT field selection、dropout、choice supervision、KT 与 end-to-end flow feedback 缺一块都会改变结果。

#### 2.1 Embodied CoT Data Construction

![[papers/images/sun2026revisiting-embodied-chain-thought/dataset.png|760]]

Figure 2 给出四层 schema。Understanding 保存 task goal，Grounding 保存 view-indexed visible objects，Planning 保存 global plan、current subtask 与 subtask reasoning，Acting 保存 movement、gripper 和 future waypoint。高层字段按 episode 或 semantic segment 生成，动作字段按 frame 和未来 action chunk 生成。

数据混合的量级并不均匀。AgiBot World 占 204.94M 样本和 1879.4 小时，是语料主体。DROID 有 15.12M 样本和 280 小时，Fractal 有 3.70M 和 342.5 小时，Bridge 有 1.43M 和 79.7 小时，MolmoAct 有 1.10M 和 10.9 小时。样本数与时长并不同比例，源数据频率、action horizon 与采样方式不同。

| Dataset | Trajectories | Samples | Duration h | 数据形态 |
| --- | ---: | ---: | ---: | --- |
| AgiBot World | 765,649 | 204.94M | 1879.4 | multi-view、bimanual |
| DROID | 74,682 | 15.12M | 280.0 | in-the-wild single-arm |
| Fractal | 86,703 | 3.70M | 342.5 | tabletop manipulation |
| BridgeData V2 | 43,807 | 1.43M | 79.7 | tabletop interaction |
| MolmoAct | 7,902 | 1.10M | 10.9 | Franka single-arm |
| Total | 978,743 | 226.3M | 2592.5 | 不含少量 general VLM data |

这套数据的用途不是让模型背更多解释文本，而是让不同粒度的语义和动作共享同一接口。Appendix B 才详细说明 trajectory segmentation、geometric projection 与 sparse grounding，主文这里只建立 schema 和规模。

#### 关键证据 / 图表 / 公式

Figure 2 支撑字段覆盖与规模声明。Table 5 给出每个源数据的轨迹、样本、时长和 action horizon。论文没有给 annotation acceptance rate、每类字段缺失率或人工核验样本量，数据质量仍靠后续消融间接判断。

#### 2.2 ERVLA Architecture

![[papers/images/sun2026revisiting-embodied-chain-thought/method.png|760]]

ERVLA 的 reasoning backbone 是 Qwen3-VL-4B。输入包含图像 $I$、指令 $x$、可选 CoT $c$、状态 $s$、动作查询 $\{a_i\}$ 和 score query $a_{\mathrm{score}}$。模型输出 hidden states 与每层 KV cache。

$$
\mathbf{H}^{\mathrm{vlm}},
\{(\mathbf{K}^{\mathrm{vlm}}_{\ell},\mathbf{V}^{\mathrm{vlm}}_{\ell})\}_{\ell=1}^{L}
=f_{\mathrm{vlm}}(I,x,c,s,\{a_i\},a_{\mathrm{score}})
$$

State token 被投影状态替换，action-query token 被可训练查询替换。Choice branch 从 action-query 的 hidden state 预测 $N$ 组候选动作，从 score-query 预测候选误差。

$$
\hat{\mathbf a}_{t}^{(n)}
=g_{\mathrm{act}}(\mathbf H_a)_{t,n},
\qquad
\hat{\mathbf r}=g_{\mathrm{score}}(\mathbf H_s)
$$

每个候选索引 $n$ 跨 $T$ 个时间位置组成一个连续 action chunk。

$$
\hat{\mathbf A}^{(n)}
=[\hat{\mathbf a}_{1}^{(n)},\ldots,\hat{\mathbf a}_{T}^{(n)}]
\in\mathbb R^{T\times D}
$$

最终执行动作不是 choice branch 直接输出，而是 DiT 对 noisy action $\mathbf z_{\tau}$ 做 rectified flow prediction。DiT 输入 sink token、projected state 和 noisy action token，时间步 $\tau$ 通过 MLP 和 AdaLN 注入。

$$
\hat{\mathbf v}_{\theta}
=f_{\mathrm{dit}}
(\mathbf z_{\tau},\tau,s
\mid
\{(\mathbf K^{\mathrm{vlm}}_{\ell},\mathbf V^{\mathrm{vlm}}_{\ell})\})
$$

Choice branch 的作用是让 VLM 的 hidden state 对候选动作好坏敏感，DiT 才是最终 continuous-action generator（连续动作生成器）。两条支路共享 VLM 语义，但训练角色不同。

Knowledge truncation 是本文较容易被忽略的接口。VLM 在语义前缀后还接 state 与 action query，若 DiT 读取完整 cache，它可能利用这些训练期 token 形成 shortcut。KT 用 $m_{\mathrm{cond}}$ 切到语义前缀末尾。

$$
\{(\mathbf K^{\mathrm{KT}}_{\ell},\mathbf V^{\mathrm{KT}}_{\ell})\}
=
\mathrm{SlicePrefix}
\left(
\{(\mathbf K^{\mathrm{vlm}}_{\ell},\mathbf V^{\mathrm{vlm}}_{\ell})\},
m_{\mathrm{cond}}
\right)
$$

DiT 的注意力把截断后的 VLM memory 与自身 token 拼接。

$$
\mathrm{Attn}
\left(
\mathbf Q,
[\mathbf K^{\mathrm{KT}}_{\ell};\mathbf K^{\mathrm{dit}}_{\ell}],
[\mathbf V^{\mathrm{KT}}_{\ell};\mathbf V^{\mathrm{dit}}_{\ell}]
\right)
$$

它和 knowledge insulation 不同。KT 限制 forward condition（前向条件）里可见的 token，动作梯度仍能回到 VLM。KI 则切断 gradient（梯度），保护预训练知识的代价是 VLM 不再被动作损失塑形。

#### 关键证据 / 图表 / 公式

Figure 3 展示完整架构。Figure 4 把三类接口并列，AR next-token 在 CoT 后生成动作容易脆裂，KI 限制动作反馈，ERVLA 让 ECoT、choice 与 flow loss 在表征空间协同。Table 3 和 Table 4 的架构消融才是 KT 与 choice 的直接证据。

#### 2.3 Training Recipe

联合目标包含四项。

$$
\mathcal L
=
\lambda_{\mathrm{vlm}}\mathcal L_{\mathrm{vlm}}
+\lambda_{\mathrm{flow}}\mathcal L_{\mathrm{flow}}
+\lambda_{\mathrm{choice}}\mathcal L_{\mathrm{choice}}
+\lambda_{\mathrm{score}}\mathcal L_{\mathrm{score}}
$$

$\mathcal L_{\mathrm{vlm}}$ 是 CoT token cross-entropy，$\mathcal L_{\mathrm{flow}}$ 是连续动作 rectified flow loss。Choice loss 从 $N$ 个候选里选 L1 error 最小的一条。

$$
\mathcal L_{\mathrm{choice}}
=
\frac{1}{B}\sum_{b=1}^{B}\min_n d_b^{(n)},
\qquad
d_b^{(n)}
=
\frac{1}{T_bD}
\left\|
\hat{\mathbf A}_{b}^{(n)}-\mathbf A_b^*
\right\|_1
$$

Score head 回归每个候选的 stop-gradient error。

$$
\mathcal L_{\mathrm{score}}
=
\frac{1}{B}
\sum_{b=1}^{B}
\left\|
\hat{\mathbf r}_b
-
\mathrm{sg}
\left(
[d_b^{(1)},\ldots,d_b^{(N)}]
\right)
\right\|_2^2
$$

Reasoning dropout 以 $p_{\mathrm{cot}}=0.5$ 把样本转换成 /cot 或 /no_cot。无 CoT 样本仍学习相同动作，模型不能把显式文本当成必经前缀。部署可直接用 /no_cot，也可稀疏刷新 CoT。论文没有给稀疏刷新策略的定量比较，主结果默认不强制解码 CoT。

### 3 Experiment

实验围绕内容、迁移接口和规模三个问题。内容研究固定 Qwen3-VL-4B 与 AR CoT+FAST。VLM transfer 研究固定 StarVLA 与 FAST，只替换 backbone 和 CoT。完整 ERVLA 再换成 choice+DiT+KT，和主流显式、视觉、潜式及 continuous-action baseline 比较。

#### Benchmarks、baselines 与 metrics

LIBERO 用于 post-training 与 in-distribution 检查。LIBERO-Plus 在 camera、robot state、language、lighting、background、noise 和 layout 上施加偏移，所有模型只在 LIBERO 后训练后 zero-shot transfer。VLABench 含 In-distribution、Cross Category、Commonsense、Instruction 与 Texture 五条 track，报告 SR、PS 和 IS。

LIBERO-Plus baseline 包括 ECoT、Emma-X、OpenVLA-OFT、UniVLA、WorldVLA、π0、π0-FAST、Spatial Forcing、PokeVLA 与 π0.5。VLABench 还加入 X-VLA 与 ACoT-VLA。真机对照选 ECoT、WorldVLA、UniVLA 和 π0.5，用来代表 AR linguistic、visual prediction、latent reasoning 与 VLM-conditioned DiT。

#### 3.1 Exploring Effective Embodied Chain-of-Thought Signals

字段消融是全文最扎实的诊断实验。直接 post-training 的 no-CoT baseline 为 19.0。Goal、Planning、Subtask 和 Reasoning 单独使用分别变化 -1.2、-0.8、-0.6 和 -1.0。Movement 为 +4.1，Point trajectory 为 +4.8。Movement+Reasoning 为 +5.2，Subtask+Movement+Point trajectory 为 +7.4，Full ECoT 为 +8.2。

| CoT setting | w/o pretraining 相对变化 | Bridge pretraining 相对变化 | Bridge + dropout 相对变化 |
| --- | ---: | ---: | ---: |
| Goal | -1.2 | -0.8 | -0.6 |
| Planning | -0.8 | -0.5 | -0.3 |
| Subtask | -0.6 | -0.7 | -0.5 |
| Movement | +4.1 | +2.0 | +1.9 |
| Reasoning | -1.0 | -0.9 | -0.6 |
| Gripper | -0.7 | -5.6 | -0.8 |
| Point trajectory | +4.8 | +1.4 | +3.0 |
| Bounding box | -1.4 | -6.1 | -1.0 |
| Movement+Reasoning | +5.2 | +3.0 | +3.2 |
| Subtask+Movement+Point trajectory | +7.4 | +3.7 | +4.4 |
| Full ECoT | +8.2 | +2.5 | +4.0 |

高层字段并非永远无用。Movement+Reasoning 比 Movement 单独高 1.1 个点，Full ECoT 也最高。准确的读法是高层理解需要 concrete action guidance（具体动作引导）作为落脚点，不能只生成任务描述。

CoT contamination 在 pretraining block 里暴露。Simulator replay 能拿到较准的 grounded coordinate，大规模 open data 却依赖 detector 与 calibration。相邻帧几乎相同，box 和 gripper label 仍可能跳动。模型若在每帧都拟合这些坐标，会把连续状态拉出不连续表征。dropout 通过让一半样本不见显式 CoT，降低这种依赖。

作者随后把 AR CoT+FAST 的预训练源从 Bridge 扩到 Bridge+Fractal，再加 MolmoAct 和 DROID。Bridge 单独小幅提升，多源混合却逐步下降。四源设置相对无预训练在 VLABench 的 In-dist、Category、Common、Instruction 与 Texture 分别为 -3.6、-3.0、-2.2、-3.2、-3.4。更多 CoT 数据没有救活脆弱的 autoregressive prefix。

VLM transfer 实验使用九个 backbone 和同一 FAST 接口。较弱的 PaliGemma-2-3B 与 Florence-2-large 加 CoT 后多项下降，Qwen3-VL 系列更常受益。Qwen3-VL-8B 在 VLABench In-dist 从 24.8 升 40.8，Category 从 16.6 升 32.4，Commonsense 从 15.2 升 22.6。可是 Qwen3-VL-2B 的 Commonsense 从 21.2 降到 13.9，Qwen3-VL-4B 也从 18.8 降到 13.6。论文的相关性结论是方向性证据，不是每模型单调成立。

#### 关键证据 / 图表 / 公式

- Table 1 给字段平均变化，Table 11 给五条 VLABench track 的完整值。
- Table 2 证明 AR CoT+FAST 在增加多源 CoT 时退化。
- Figure 5 左侧和 Table 12 对比 VLM capability 与 downstream VLA。
- 字段实验固定接口，能回答哪个监督有用，却不能直接证明在所有连续动作头上保持同样排序。

#### 3.2 Studies of ERVLA Design Choices and ECoT Scaling

![[papers/images/sun2026revisiting-embodied-chain-thought/why.png|640]]

Figure 4 给出设计判断。AR CoT+action token 把错误顺着 prefix 传到动作，isolated VLM+DiT 缺少动作对 VLM 的塑形，ERVLA 用 choice 和 flow feedback 建立中间接口，再用 KT 清理 DiT 的条件。

LIBERO-Plus 总分是 86.9。π0.5 为 85.5，PokeVLA 为 79.3，OpenVLA-OFT 为 69.6。ERVLA 在 Spatial 96.2、Long 82.1、Camera 77.2、Language 87.1、Noise 92.3 上领先。π0.5 在 Object 89.9 对 89.6、Goal 81.0 对 79.6、Robot 75.5 对 75.3、Light 96.1 对 95.1、Background 95.7 对 94.7、Layout 87.5 对 86.4 上仍略高或更高。

| LIBERO-Plus method | Spatial | Object | Goal | Long | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| π0.5 | 90.4 | 89.9 | 81.0 | 80.8 | 85.5 |
| No Choice E2E | 70.8 | 65.4 | 58.6 | 55.2 | 61.9 |
| No CoT | 77.4 | 71.8 | 65.2 | 62.0 | 70.8 |
| No Choice + KI | 83.8 | 78.6 | 71.4 | 69.0 | 76.5 |
| Choice + No KT | 89.2 | 88.6 | 79.4 | 79.8 | 84.7 |
| ERVLA | 96.2 | 89.6 | 79.6 | 82.1 | 86.9 |

这张表给出两层判断。Choice + No KT 已到 84.7，说明 choice branch 是主要跃升来源之一。加 KT 再涨 2.2 个点，说明 control-query shortcut 确实存在。No Choice+KI 高于 No Choice E2E 14.6 个点，却仍低于 full ERVLA，表明无 choice 时盲目让 flow gradient 改 VLM 可能比隔离更差，不能把 end-to-end 本身当成优势。

VLABench 上 ERVLA 平均 SR、PS、IS 为 53.2、65.9、70.4。π0.5 为 48.1、62.3、64.9。最大 SR 增益出现在 Instruction，58.0 对 48.2，Cross Category 为 47.0 对 38.2。Commonsense 的 SR 只差 0.1，ERVLA 的 PS 55.0 低于 57.3，IS 57.2 低于 60.0。Texture PS 同为 62.3，ACoT-VLA 的 Texture IS 74.6 还高于 ERVLA 的 70.6。

| VLABench method | In-dist SR | Category SR | Commonsense SR | Instruction SR | Texture SR | Avg SR / PS / IS |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| π0.5 | 65.4 | 38.2 | 43.9 | 48.2 | 44.9 | 48.1 / 62.3 / 64.9 |
| No CoT | 52.6 | 34.8 | 38.8 | 44.2 | 34.0 | 40.9 / 50.4 / 57.1 |
| Choice + No KT | 62.0 | 42.4 | 43.0 | 53.6 | 35.0 | 47.2 / 59.8 / 63.4 |
| ERVLA | 69.7 | 47.0 | 44.0 | 58.0 | 47.4 | 53.2 / 65.9 / 70.4 |

![[papers/images/sun2026revisiting-embodied-chain-thought/ablation.png|760]]

Figure 5 右侧给 ECoT scaling 曲线。ERVLA 随预训练数据增加持续上升，AR CoT+FAST 变脆，isolated VLM+DiT 较早饱和。源码没有给每个横轴点的数值表、误差棒和计算量，能确认趋势，不能重算 scaling law。

#### 关键证据 / 图表 / 公式

- Table 3 是 LIBERO-Plus 的主结果与接口消融。
- Table 4 是 VLABench 的 SR、PS、IS 完整结果。
- Figure 4 解释三种 reasoning-action interface。
- Figure 5 同时支撑 VLM transfer 与 ECoT scaling。
- 表格只给单组数值，没有随机种子方差或置信区间。

#### 3.3 Real-world Experiments

![[papers/images/sun2026revisiting-embodied-chain-thought/realworld.png|760]]

真机使用一个第三视角相机和一个 wrist camera。任务分成抽屉收纳与桌面清理两族，再按 Basic、Distractors、Semantic 与 Long-horizon 四档组织。每档 5 条 instruction，共 20 个任务，每任务做 5 次，每种方法 100 次 rollout。

Basic 使用明确物体名和干净场景。Distractors 加入无关或相似物体。Semantic 用「不是水果的物体」「下层抽屉上面的抽屉」「应该扔掉的东西」这类间接指令。Long-horizon 需要按类别连续处理多个物体并记住已完成进度。

所有方法使用约 10 小时真机示范和同一 fine-tuning schedule，8 张 NVIDIA A100、每 GPU batch 16、20,000 steps。Continuous-action method 共用 temporal action ensemble，减少执行抖动。这个设置比较的是同一适配数据下的接口差异，不是 zero-shot real-world transfer。

| Method | Basic SR / PS | Distractor SR / PS | Semantic SR / PS | Long-horizon SR / PS | Average SR / PS |
| --- | --- | --- | --- | --- | --- |
| ECoT | 60 / 68 | 18 / 30 | 10 / 25 | 6 / 18 | 24 / 35 |
| WorldVLA | 78 / 84 | 28 / 42 | 18 / 35 | 12 / 28 | 34 / 47 |
| UniVLA | 76 / 82 | 31 / 45 | 22 / 38 | 18 / 34 | 37 / 50 |
| π0.5 | 97 / 98 | 45 / 57 | 31 / 45 | 35 / 38 | 53 / 60 |
| ERVLA | 96 / 97 | 44 / 58 | 42 / 58 | 38 / 55 | 55 / 67 |

Basic 上 π0.5 还以 97/98 略高于 ERVLA 的 96/97。Distractor 的 SR 也是 π0.5 高 1 点。差距集中在 Semantic，ERVLA 比 π0.5 多 11 SR 和 13 PS。Long-horizon 的 SR 只多 3 点，PS 却多 17 点，表明 ERVLA 更常完成中间子任务，但没有同等幅度地把整条指令做完。

![[papers/images/sun2026revisiting-embodied-chain-thought/real_case.png|760]]

Figure 12 展示真机 rollout。图像能帮助理解任务形态，不能代替 100 次试验的统计。论文没有按单条 instruction 给出成功分布，也没有报告失败类型、控制频率、推理时延和人工复位规则。

#### 关键证据 / 图表 / 公式

- Figure 6 展示四档真机设置与汇总曲线。
- Table 14 给 SR 和 PS，Table 15 列出全部 20 条 instruction。
- Figure 12 给代表性 rollout。
- 每方法 100 次是可读的分母，但每个 tier 只有 25 次，细分百分比的统计精度有限。

### 4 Conclusion

结论把 embodied CoT 从 output format（输出格式）改写成 semantic reasoning 与 action learning 之间的 interface。更长、更密、更显式的 reasoning 不会自动改进策略。标签要可靠，内容要接近动作，耦合方式要能塑形表征又不拖累解码。

ERVLA 用 explicit linguistic CoT、reasoning dropout、VLM-level action shaping 与 semantic-conditioned continuous control 实例化这个判断。正向结果说明 action-oriented supervision 可以调动 VLM 的语义先验，负向结果则说明 noisy grounding 和 naive AR coupling 会让规模化反噬。

这节没有新增实验。它把数据 pipeline、字段消融、接口消融和 benchmark 结果收回到同一句研究结论，推理是否有用取决于它如何进入动作表征，而不是机器人是否在屏幕上输出一段解释。

#### 关键证据 / 图表 / 公式

结论依赖 Table 1 的字段差异、Table 2 的 AR scaling failure、Tables 3–4 的 ERVLA 主结果和 Table 14 的真机语义、长时域收益。没有新的 Figure 或 Equation。

### Appendix A Related Work

附录把 reasoning-aware VLA 分成三条路线。Explicit linguistic or action-space CoT 包括 ECoT、EMMA-X、LAP、ACoT-VLA 与 ECoT-Lite，优点是可监督、可解释，代价是 latency、prefix noise 与 exposure bias。Visual or world-model reasoning 用 future image、heatmap 或 video prediction 表达动力学，空间信息强，却更贵，还需要 inverse dynamics 把视觉预测变成动作。Latent reasoning 以 ThinkAct、Fast-ThinkAct、LaST₀ 与 UniVLA 为代表，部署快，但有用结构往往要先被显式监督或蒸馏学到。

动作表示也分 autoregressive token 与 continuous chunk。RT-2、OpenVLA、FAST 等复用 language decoder，但有量化误差和序列延迟。ACT、Diffusion Policy、RDT、DexVLA 与 π0 系列直接建模连续动作。ERVLA 站在 continuous-action 一侧，研究的重点不是选哪种 tokenizer，而是让 CoT loss 与 action loss 怎样共同塑形 VLM。

与 knowledge-insulated VLA 的差别很清楚。KI 保护 backbone，不让 continuous action gradient 回去。ERVLA 仍让 flow gradient 回传，只在 DiT condition 上截断 control-query KV。一个处理优化路径，一个处理条件捷径，不在一个尺度上。

### Appendix B Embodied CoT Dataset Construction Pipeline

![[papers/images/sun2026revisiting-embodied-chain-thought/datapipeline.png|760]]

Appendix B 是论文复现价值最高的部分之一。Figure 7 把 raw trajectory 变成结构化 ECoT 的步骤串起来，trajectory segmentation、episode planning、future-motion language、geometric projection、future point trajectory、sparse object grounding、multi-view correspondence 与 quality filtering。

#### Trajectory Segmentation and Episode-Level Planning

机器人状态写成位置、旋转和 gripper。

$$
\mathbf s_t=[\mathbf p_t,\mathbf R_t,g_t]
$$

候选边界来自平移、旋转和夹爪变化。

$$
\Delta p_t=\|\mathbf p_{t+1}-\mathbf p_t\|_2,
\quad
\Delta R_t=\|\log(\mathbf R_t^\top\mathbf R_{t+1})\|_2,
\quad
\Delta g_t=|g_{t+1}-g_t|
$$

Gripper open/close、持续停顿和 approach-to-manipulation transition 都会提出边界。它们只是 proposal。Qwen3.5-397B 再读 task instruction、keyframe 与 segment，一次生成全局 goal 和 subtask sequence。相邻帧继承 episode-level plan，长 segment 只在 anchor frame 生成详细 reasoning，非 anchor frame 复用。

#### Action-Oriented Reasoning From Future Motion

每帧取未来 $K$ 步 action chunk，跨 subtask boundary 时截断。

$$
\mathbf A_{t:t+K}
=[\mathbf a_t,\mathbf a_{t+1},\ldots,\mathbf a_{t+K-1}]
$$

Movement description 只写超过 threshold 的 dominant translation、rotation 与 gripper change。小幅 controller jitter 不被语言化。这个规则解释了 movement 字段为何比逐帧坐标稳定。

#### Geometric Gripper Projection

静态第三视角相机使用内参 $\mathbf K_c$ 和 world-to-camera transform $\mathbf T_w^c$，把 tool center 或 fingertip midpoint 从 end-effector frame 投到 image plane。

$$
\lambda
\begin{bmatrix}
u_t^c\\v_t^c\\1
\end{bmatrix}
=
\mathbf K_c
\begin{bmatrix}
\mathbf I_{3\times3}&\mathbf 0
\end{bmatrix}
\mathbf T_w^c
\bar{\mathbf p}_{\mathrm{grip}}^w(t)
$$

若 camera coordinate 为 $(X,Y,Z)$，像素为

$$
u_t^c=f_x\frac{X}{Z}+c_x,
\qquad
v_t^c=f_y\frac{Y}{Z}+c_y
$$

只保留 $Z>0$ 且落在画面内的点，再归一化到 $[0,1000]$。Wrist camera 随末端刚性移动，当前 gripper 在画面中近似固定，所以不用于这项 action-oriented supervision。

#### Future Point-Trajectory Annotation

未来若干 timestamp 的 gripper position 用同一 camera model 投影，形成

$$
\mathcal P_t^c
=
[
(\tilde u^c_{t+\delta_1},\tilde v^c_{t+\delta_1}),
\ldots,
(\tilde u^c_{t+\delta_M},\tilde v^c_{t+\delta_M})
]
$$

相邻重复点和近重复点被跳过，不足 $M$ 个时用 $[-1,-1]$ pad。Point trajectory 提供 image-space motion trend，又避免每帧硬拟合不可靠位置。

#### Object Grounding、Multi-view 与 Bimanual

Object box 来自 LLMDet。候选类别先从 instruction、plan、subtask 与 detector shard 组成 episode vocabulary，再按小批类别查询。Box 同样归一化到 $[0,1000]$。作者只在 keyframe 或稀疏间隔标注，低置信度 frame 直接缺字段，不用错误坐标补齐。

Visible objects、gripper 和 waypoint 按 camera view 存成 dictionary。同一物体在 base、front 与 wrist view 有独立坐标。双臂数据保留 left/right identity，单臂使用同一 schema 但只填 active arm。这让多本体数据共享语言接口，同时不抹掉视角和手臂结构。

#### Quality Control

缺图、state 无效、action length 不一致的 trajectory 被移除。负深度、越界、相邻跳变异常的 gripper point 被丢弃。几何无效、面积过小、类别不稳定的 box 也被删掉。空字段或与 observation 矛盾的 CoT 被裁掉。

作者明确偏向 sparse but trustworthy supervision（稀疏但可信的监督）。可以确定的是，这个原则与字段消融互相呼应。说实话也不确定的是，正文没有给各 filter 删除了多少样本，也没有人工审计精确率，pipeline 的绝对质量还不能复算。

### Appendix C Training Details

预训练使用 Qwen3-VL-4B-Instruct、5 个 choice、36 层 DiT。Action horizon 为 30，action 和 state pad 到 60 维，以便单臂与双臂共享接口。图像最大 90,000 pixels，token packing 上限 17,600 tokens。模型训练 120,000 steps，batch size 64，bfloat16，learning rate $5\times10^{-5}$，warmup 2,000，weight decay 0.1，gradient clipping 1.0。

| Pretraining item | Setting |
| --- | --- |
| Backbone | Qwen3-VL-4B-Instruct |
| Action / state | $30\times60$ / $1\times60$ |
| Choices / DiT layers | 5 / 36 |
| Reasoning dropout | 0.5 |
| Training steps / batch | 120,000 / 64 |
| LR / warmup | $5\times10^{-5}$ / 2,000 |
| Max image pixels | 90,000 |
| Max packed length | 17,600 tokens |
| Precision / distributed | bfloat16 / DeepSpeed |

采样权重并不按样本数原样分配。AgiBot 权重 0.518，DROID 0.180，Fractal 0.120，Bridge 0.100，MolmoAct 0.082。AgiBot 有 90% 以上样本却只占约一半 nominal sampling weight，较小数据源被显著上采样。

Post-training 数据共 7,000 条 trajectory 和 913,676 个 sample。VLABench 为 5,000 条、575,101 个 sample。LIBERO-10、Goal、Object、Spatial 各 500 条，sample 分别为 138,090、63,728、74,507、62,250。LIBERO 与 VLABench 的 action horizon 都是 10，state 和 action 继续 pad 到 60 维并做 Gaussian normalization。

VLM-to-VLA transfer 统一使用 StarVLA、FAST、7-DoF end-effector chunk、horizon 10、AdamW、peak LR $10^{-4}$、warmup 2,000 和 weight decay 0.1。LIBERO 训练 10,000 steps，VLABench 20,000 steps。九个 VLM 都同时 fine-tune vision encoder、LLM、token embedding 与 action-token head。

四个 ERVLA variant 的定义必须和结果一起读。No Choice E2E 去掉 choice 但允许 flow gradient 回 VLM。No Choice+KI 进一步阻断 gradient。Choice+No KT 保留 choice，却让 DiT 看到完整 KV。Full ERVLA 才把 explicit CoT、dropout、choice、KT 与 end-to-end flow 合在一起。

### Appendix D Detailed Experimental Results

附录表把主文的平均变化拆到每条 track。Full ECoT 在无预训练时平均 27.2，对 no-CoT 的 19.0 多 8.2。Bridge pretraining without dropout 时平均 27.7，对 25.2 多 2.5。加 dropout 后平均 29.2，多 4.0。组合字段 Subtask+Movement+Point trajectory 在 dropout 设置达到 29.6，反而高于 Full ECoT 的 29.2，说明更多字段仍可能带入噪声。

VLM transfer 表也给出重要反例。Qwen3-VL-8B 在 LIBERO Spatial 从 90.8 升 97.2，Goal 从 86.4 升 93.2。PaliGemma-2-3B 的四个 LIBERO suite 全部下降，VLABench 多数 track 也下降。CoT 更像一个能放大已具备语义能力的 transfer interface，不是对任意 backbone 都有效的插件。

![[papers/images/sun2026revisiting-embodied-chain-thought/vlabench_sim.png|720]]

![[papers/images/sun2026revisiting-embodied-chain-thought/liberoplus_sim.png|720]]

Figures 10–11 的 simulation rollout 用于观察不同偏移下的行为。定量结论仍应回到 Tables 3–4 与 Tables 11–12。精选成功轨迹不包含完整失败分布。

真机附录把 20 条 instruction 全列出来，也解释 PS 如何给部分完成计分。模型可能找对物体但放置失败，可能完成多物体指令的一部分，也可能执行正确 primitive 却选错 container。Long-horizon PS 的 17 点提升因此值得读，但它不是 17 点完整成功率。

### Appendix E Limitations and Future Work

作者承认 reasoning value 受 reasoning substrate quality 限制。语言字段较稳，却可能欠具体。Dense grounding 更接近动作，却受 detector error、calibration bias 和 occlusion 影响。dropout 与 KT 只减轻伤害，没有让模型知道某个字段此刻有多可信。

论文也主要把 reasoning 当 offline pretraining signal。Long-horizon execution 可能需要记住已完成子任务、识别失败并重规划，或在 scene 与 instruction 冲突时请求澄清。固定 /no_cot 高效，却没有回答执行中何时应该刷新 reasoning。

未来方向是 uncertainty-aware annotation（带不确定度的标注）和 adaptive test-time reasoning（自适应测试时推理）。目标不是让机器人每个动作都说一遍，而是让策略在需要时展开推理，在低层稳定段直接行动。

## 方法细节

把 ERVLA 串成一次前向过程，可以分成语义前缀、动作塑形与连续生成。图像和 instruction 先进入 Qwen3-VL-4B，训练时可附带 ECoT。VLM 在语义前缀后接 state、action query 与 score query。CoT CE 训练语言推理，choice loss 让 action-query state 区分候选动作，score loss 学会估计候选误差。

DiT 不直接读取 action-query KV，只读取 KT 后的 semantic-prefix cache，再结合当前 state、noisy action 与 diffusion timestep 预测 flow velocity。Flow loss 仍能穿过 cache 回到 VLM。这样既避免 full-cache shortcut，也不做 gradient insulation。

Reasoning dropout 贯穿 pretraining 与 post-training。半数样本带 /cot，半数用 /no_cot。显式 CoT 提供结构，no-CoT 样本逼迫结构进入 hidden state。部署默认省略 CoT decoding，choice branch 主要承担训练期 representation shaping，DiT 负责最终 action chunk。

数据侧用 episode-level VLM planning 保持全局一致，用 future robot motion 生成 action-oriented text，用 calibrated projection 生成 gripper 和 waypoint，用 sparse LLMDet box 控制 grounding noise。字段按可靠性采用不同时间粒度，不把每种 reasoning 都硬做成 frame-dense label。

## 实验设置、数据集、基线、指标

| 实验组 | 训练数据与接口 | 评测 | 目的 |
| --- | --- | --- | --- |
| CoT field study | VLABench 或 Bridge pretrain + VLABench，Qwen3-VL-4B，AR CoT+FAST | VLABench average SR 与五 track | 隔离字段内容与 contamination |
| AR scaling study | Bridge、Fractal、MolmoAct、DROID 逐步加入，CoT+FAST+dropout | LIBERO 与 VLABench | 检查显式 prefix 是否可扩展 |
| VLM transfer | 9 个 VLM，固定 StarVLA+FAST，with/without ECoT | LIBERO 与 VLABench | 检查 VLM 强度能否传到 VLA |
| ERVLA main | 五源 226.3M ECoT pretrain，再做 benchmark post-train | LIBERO-Plus、VLABench | 检查完整接口与 OOD generalization |
| Real-world | 约 10 h 同一示范，20,000 steps | 20 tasks × 5 trials | 检查语义、干扰和长时依赖 |

LIBERO-Plus 报 task suite 与七类 perturbation success rate。VLABench 报 SR、PS、IS。真机也报 SR 与 PS。论文没有统一报告 latency、control frequency、compute、seed variance 或 confidence interval，这些缺口会限制跨方法比较。

## 主要结果、消融或对比

内容层面的结果最清楚。Movement 与 point trajectory 有正收益，孤立 goal、planning、subtask 和 reasoning 没有。高层字段和动作字段组合后又变强，所以问题不在语言本身，而在语义是否有 executable anchor（可执行锚点）。

噪声层面的结果也很直接。Bridge ECoT pretraining 让 gripper 与 bounding box 分别损失 5.6、6.1 个点，dropout 把损失缩到 0.8、1.0。Point trajectory 从 +1.4 回到 +3.0。自动标注越接近动作，越需要稳定的几何和时间一致性。

接口层面，LIBERO-Plus 从 No Choice E2E 的 61.9、No CoT 的 70.8、No Choice+KI 的 76.5、Choice+No KT 的 84.7 逐步到 Full 86.9。VLABench 也从 No CoT 的平均 SR 40.9 升到 Full 53.2。Choice 和 KT 都有可见贡献。

Benchmark 层面，LIBERO-Plus 总分只领先 π0.5 1.4 个点，VLABench 平均 SR 领先 5.1 个点。真机平均 SR 只领先 π0.5 2 点，PS 领先 7 点。Semantic 的优势最大，Long-horizon 主要提高过程完成而非完整成功。

## 图表、公式与表格线索

| 编号 | 内容 | 支撑主张 | 阅读提醒 |
| --- | --- | --- | --- |
| Figure 1 | ERVLA 全局概览 | CoT 作为 representation shaping | 概念图，不给独立数值 |
| Figure 2 | ECoT schema 与 2592.5 h 数据 | 数据规模与字段覆盖 | 公开状态仍是承诺 |
| Figure 3 | VLM、choice、KT、DiT | 推理到动作接口 | choice 不是最终执行头 |
| Figure 4 | AR、KI 与 ERVLA 对比 | 解释 KT 和 action feedback | 机制图需配合消融 |
| Figure 5 | VLM transfer 与 ECoT scaling | 强 VLM 迁移和数据扩展趋势 | 缺每点数值与误差棒 |
| Figure 6 | 真机四档评测 | 语义与长时域收益 | 细分每档 25 次 |
| Figure 7 | 自动标注 pipeline | 稀疏可信监督 | 无 filter acceptance rate |
| Figure 8 | 多视角空间 CoT 样例 | 视角对应与双臂格式 | 单个格式示例 |
| Figure 9 | LIBERO-10 帧级标注 | post-training 与 pretraining 共用 schema | 单个格式示例 |
| Figures 10–11 | VLABench 与 LIBERO-Plus rollout | 定性展示 OOD 行为 | 精选轨迹不能代表分布 |
| Figure 12 | 真机案例 | 任务形态和中间步骤 | 仍应回到 SR、PS |
| Table 1 / 11 | CoT 字段消融 | 动作字段更有效，污染可缓解 | 固定 AR CoT+FAST |
| Table 2 | AR CoT pretrain scaling | 更多多源 CoT 反而退化 | 未包含 AgiBot full ERVLA 接口 |
| Tables 3–4 | 仿真主结果与架构消融 | choice、KT 与 full ERVLA | 无随机种子方差 |
| Tables 14–15 | 真机结果和 20 条任务 | Semantic 与 Long-horizon 增益 | 同一约 10 h 示范适配 |
| Equations 1–7 | VLM cache、choice、DiT、KT、loss | 完整训练接口 | λ 权重未在正文给数值 |
| Appendix projection equations | 3D gripper 到 2D waypoint | 几何标签比 detector 更稳 | 只适用于有 calibration 的静态相机 |

## 主张-证据-边界矩阵

| 主张 | 最强证据 | 证据强度 | 边界 |
| --- | --- | --- | --- |
| 高层 CoT 需要动作锚点 | Movement +4.1、Point +4.8、组合 +7.4、Full +8.2 | 较强受控消融 | 只在当前 benchmark 和 AR FAST 接口验证 |
| CoT contamination 会破坏预训练 | Gripper -5.6、Box -6.1 | 较强诊断 | 没有人工测量 label noise 与性能的因果曲线 |
| reasoning dropout 能缓解污染 | 两项损失缩到 -0.8、-1.0，Point 升到 +3.0 | 中等 | dropout 也改变显式依赖，机制不只去噪 |
| AR explicit CoT 不可靠扩展 | 四源混合在五条 VLABench track 全降 | 中等 | 只测 CoT+FAST，一些配方可能不同 |
| choice 与 KT 构成有效接口 | 84.7 到 86.9，No Choice 明显更低 | 较强消融 | 无多 seed 和 λ sensitivity |
| ERVLA 在 LIBERO-Plus 领先 | 86.9 对 π0.5 85.5 | 中等 | 优势小，多个子项落后 |
| ERVLA 在 VLABench 更强 | Avg SR 53.2 对 48.1 | 较强表格 | Commonsense PS、IS 不领先 |
| ERVLA 真机语义能力更强 | Semantic 42/58 对 31/45 | 中等 | 两族任务、每档 25 次、同分布适配 |
| ERVLA 改善长时执行 | Long-horizon PS 55 对 38 | 中等 | SR 只从 35 到 38 |
| ECoT pretraining 可规模化 | Figure 5 右侧上升曲线 | 早期证据 | 无完整数值、compute 与误差棒 |

## 局限与可追问点

论文最需要补的是开放性。Code、data 与 checkpoint 仍未发布，226.3M 样本的 schema、过滤率、字段缺失率和人工核验精度无法审计。最大规模声明建立在作者统计上。

标注 pipeline 使用 Qwen3.5-397B 和 LLMDet，却没有报告 annotation cost、failure rate、人工复核协议和模型版本冻结方式。Dataset source 的 domain imbalance 也很大，AgiBot 占绝大多数原始样本，nominal weight 只能缓和，不能消除语义和本体偏差。

Reasoning dropout 是一个有效但粗粒度的开关。所有字段一起出现或一起省略，没有按 box confidence、view calibration、subtask boundary uncertainty 调权。很多做 VLA 的会遇到这个问题，可靠 goal 和不可靠 box 被放进同一 CoT block，模型无法知道应该信哪一项。

KT 的解释有说服力，但缺少更细的 cache slicing 对照。语义前缀截在哪里、是否保留 state、保留部分 action query 会怎样，论文只给 full-cache 与 prefix-cache 两端。还在摸索的部分是 shortcut 到底来自 token identity、state leakage 还是 choice prediction。

真机实验不是 zero-shot。所有模型都用约 10 小时示范做 20,000 steps fine-tuning。任务只有 drawer placing 与 table clearing，物体是 toy car、fruit model、bottle 和 can。需要追问跨房间、跨机器人、动态障碍、失败恢复和更长记忆下的表现。

LIBERO-Plus 的 1.4 点领先没有 error bar。VLABench 的多个 metric 呈混合结果，作者突出平均 SR 与总分是合理的，却不能替代逐 track 阅读。说到底，论文证明了一个有竞争力的接口，还没证明统一解决具身推理。

部署端只说支持 explicit、sparse 或 no-CoT，没有比较三种模式的 latency、成功率与 failure recovery。若推理真是可选条件，下一版应给 adaptive refresh policy，以及何时从直接行动切回显式 reasoning 的触发标准。

## 我的阅读判断

这篇工作说到点子上了。具身 CoT 的核心不是让 VLA 多写几句，而是给 action head 一个经过语义整理、空间落地且时间稳定的 representation。Field ablation 比模型总分更有长期价值，因为它把「推理」拆成可检验的监督成分。

值得画出来的是两个反例。孤立的 Goal 和 Planning 会掉点，更多多源 CoT 在 AR 接口上也会掉点。它们共同排除了「文本越丰富、数据越多就越强」的简单叙事。ERVLA 的贡献正是把 negative finding 变成 architecture recipe。

ERVLA 与 [[@liu2026last0-latent-spatio-temporal|LaST₀]] 代表两种收起显式 CoT 的办法。LaST₀ 把未来视觉、3D 和本体状态压进 latent spatio-temporal trajectory，ERVLA 保留 linguistic ECoT 作为训练监督，再让部署走 no-CoT continuous action。前者强调不可言说的物理状态，后者强调标注可控与表征塑形。

与 [[@li2026zr0|ZR-0]] 对照时，应关注 test-time reasoning 是否参与闭环。ERVLA 默认把 reasoning 放在训练期，动态刷新仍空着。与 [[@zhong2025action-tokenization-survey|VLA Action Tokenization Survey]] 对照时，ERVLA 又提供一个清楚案例，AR action token 的问题不只在速度和量化，还会放大前置 reasoning 的误差。

## 与当前库的连接

- [[@liu2026last0-latent-spatio-temporal|LaST₀]] 选择 latent spatio-temporal CoT 与慢推理、快动作双系统。ERVLA 选择 explicit training CoT 加 no-CoT inference，适合比较可解释监督与潜式推理。
- [[@liu2026last-hd|LaST-HD]] 把人类视频和潜空间物理推理接到机器人动作。ERVLA 的 multi-view point trajectory 与 action-oriented language 可作为另一种跨数据接口。
- [[@li2026zr0|ZR-0]] 关注 VLA 的训练与推理监督。和 ERVLA 一起读，可以区分 offline representation shaping 与 online deliberation。
- [[@zhong2025action-tokenization-survey|VLA Action Tokenization Survey]] 提供离散 token、FAST、diffusion 和 flow action 的全景。ERVLA 直接展示 AR CoT+FAST 与 DiT flow 在 CoT scaling 上的差异。
- [[@intelligence2025pi06-vla-that-learns|π*0.6 / RECAP]] 关注经验数据与后训练。ERVLA 则把监督结构和接口放在预训练阶段，两者共同指向数据不是只靠数量，标签与更新路径同样决定泛化。

## 精读路线 / 为什么需要回看

第一遍先看 Table 1、Table 2 和 Figure 4。它们分别回答什么 CoT 有用、更多 CoT 为什么会失败、ERVLA 怎样改接口。若这三处读通，模型总分就不会遮住论文真正的研究问题。

第二遍看 Figure 3 与 Equations 1–7，分清 choice branch、DiT、KT 和 KI。Choice 负责动作感知表征，DiT 负责最终连续动作，KT 切 forward cache，KI 切 backward gradient。四者混在一起会把消融表读错。

第三遍核对 Tables 3、4 和 14。LIBERO-Plus 看 86.9 与 85.5 的小差距，VLABench 看 Commonsense 的混合指标，真机看 Long-horizon 的 SR 只涨 3 点而 PS 涨 17 点。平均数之外的边界都在这里。

回看 Appendix B 时重点追 geometric projection、sparse grounding 和 episode-level planning。它们解释 CoT contamination 为什么出现，也解释作者为何没有把所有字段都做成 dense per-frame supervision。

等代码和数据公开后，最该补看的不是演示视频，而是 field missing rate、annotation confidence、每个 scaling point 的 compute 与多 seed 方差。可以确定的是，这些材料会决定 ERVLA 是一套可复现配方，还是一篇实验诊断很强但开放性尚未跟上的预印本。

~~~dataviewjs
const {Research} = customJS
Research.topic(dv)
~~~
