---
tags:
  - bilingual-reading
paper: "[[@pan2026vla-corrector-lightweight-detect]]"
source_pdf: "[[papers/pdfs/pan2026vla-corrector-lightweight-detect.pdf]]"
images: "papers/images/pan2026vla-corrector-lightweight-detect/"
image_index: "[[papers/images/pan2026vla-corrector-lightweight-detect/index.md]]"
created: 2026-07-07
updated: 2026-10-02
reading_mode: full-close-reading
---

# VLA-Corrector: Lightweight Detect-and-Correct Inference for Adaptive Action Horizon

paper:: [[@pan2026vla-corrector-lightweight-detect]]
pdf:: [[papers/pdfs/pan2026vla-corrector-lightweight-detect.pdf]]
images:: [[papers/images/pan2026vla-corrector-lightweight-detect/index.md]]

原文为 arXiv:2607.01804v1，提交日期 2026-07-02。作者来自 Zhejiang University 与 Alibaba DAMO Academy，PDF 共 22 页，主文含 5 节，附录含 A–E。代码地址为 <https://github.com/ZJU-OmniAI/vla-corrector>。本稿按 PDF 和对应 TeX 源码解释主文、附录、公式与图表；实验数值沿用论文，未作独立复现。

## 核心词汇速查

| English | 中文 | 本文含义 |
| --- | --- | --- |
| Vision-Language-Action, VLA | 视觉-语言-动作模型 | 以视觉观测和语言指令为条件生成机器人动作的策略。 |
| action chunk, `A_t` | 动作块 | 一次策略调用生成 `C` 个未来动作。 |
| action horizon, `H` | 动作执行时域 | 当前 chunk 中实际执行的前 `H` 步，满足 `H≤C`。 |
| open-loop blind spot | 开环盲区 | 执行队列期间已有新观测，但主策略尚未重新查询的窗口。 |
| stale actions | 过期动作 | 状态变化后仍按旧观测生成、已不适合当前状态的剩余动作。 |
| compounding errors | 误差累积 | 局部偏差在后续动作执行中扩大，可能导致分布外状态。 |
| Latent-space Vision Monitor, LVM | 潜空间视觉监视器 | 比较预期与观测视觉潜动态，提供在线漂移信号。 |
| external latent dynamics corrector, `M_φ` | 外置潜动态校正器 | 在冻结视觉特征上训练的约 40M 残差 MLP，供 LVM 与 OGG 共用。 |
| residual latent evolution, `ΔZ` | 潜表示残差演化 | 两个时刻视觉潜表示的差，表征局部变化。 |
| prediction interval, `k` | 预测间隔 | 从 `t` 到 `t+k` 的潜动态预测跨度；不同于执行上限 `H`。 |
| inconsistency score, `E_t` | 不一致分数 | `1−CosSim(ΔZ_exp,ΔZ_real)`，主要度量方向失配。 |
| median absolute deviation, MAD | 中位数绝对偏差 | 构造在线鲁棒阈值的尺度统计量。 |
| hysteresis | 迟滞 | 激活阈值高于恢复阈值，减少状态反复切换。 |
| persistence counter, `c_t` | 持续计数器 | 对高分计数、低分清零、中间区间保持。 |
| interrupt / truncation | 中断 / 截断 | 清除当前队列尚未执行的动作，并触发新调用。 |
| adaptive action horizon | 自适应动作时域 | 实际执行长度按监测事件缩短为 `h<H`；没有事件时仍执行到 `H`。 |
| Online Gradient Guidance, OGG | 在线梯度引导 | 在中断后的单次重规划中，对流匹配速度场加入纠正梯度。 |
| corrective latent direction, `ΔZ_corr` | 纠正潜方向 | 先前预测的潜位移减去已经发生的潜位移。 |
| flow matching / velocity field | 流匹配 / 速度场 | 本文动作生成和 OGG 更新的数学接口。 |
| success-per-call efficiency | 每次策略调用的成功效率 | 成功率除以每 episode 平均调用次数，非单位时间成功率。 |
| post-interrupt recovery rate | 中断后恢复率 | 中断后 10 个控制步内 `E_t<T_off` 的事件比例。 |
| frozen backbone | 冻结骨干 | 接入纠正器后不再更新 VLA 参数；不表示整个系统无需训练。 |

## 摘要

英文摘要的核心表述是 *“Without modifying the backbone policy weights”* 与 *“an event-triggered adaptive action horizon”*。前者限定参数更新范围，后者说明执行时域由检测事件决定。

生成式 VLA 常通过 action chunk（动作块）降低策略调用频率，并保持动作的时间连续性。但固定 horizon 内按旧观测执行多个动作，会减弱对新状态的反应。接触密集操作中的局部扰动可能在这个窗口内扩大，最终导致任务失败。

VLA-Corrector 为已获得的 VLA 策略加入一个纠正推理层。LVM 持续比较预测与实际视觉潜表示变化；检测到持续失配后，系统截断当前队列，丢弃过期动作，并用 OGG 引导下一次重规划。执行稳定时保留长时域，发生漂移时提前重新查询策略，由此形成事件触发的自适应 horizon。

论文报告了仿真、跨骨干和真实机器人上的成功率改善，以及 success-per-call 改善。接入阶段冻结 VLA，但外置动力学校正器需要示范训练。附录还报告了 OGG 的额外推理耗时，因此摘要中的效率收益应按策略调用口径理解。

## 论文主线

作者测量固定 horizon 的成功率与调用次数权衡，再分别处理两个问题：何时停止执行旧动作，以及中断后怎样改善恢复。LVM 回答前者，OGG 回答后者。

1. 一次预测多个动作可摊薄昂贵的 VLA 调用，但预测后的真实状态可能变化。
2. 短 horizon 提供更频繁的反馈，长 horizon 减少调用。Figure 2 与 Table 4 在三个骨干上给出经验权衡。
3. 用局部视觉潜动态的一致性判断当前 chunk 是否仍可靠，避免只按固定时间重规划。
4. 持续漂移触发截断；纠正方向用于引导下一次动作生成，而骨干参数保持冻结。
5. 主实验检查成功率和每次调用效率，机理实验检查检测、触发相位和恢复，附录补充训练条件、推理成本与真实失败模式。

这条主线讨论的是既有策略在执行中的局部纠偏能力。它要求策略已能完成基本任务、相机能提供相关变化、校正器学到适用的局部动态。

## 贡献与结论对照

| 贡献或结论 | 方法与证据 | 可支持的判断 |
| --- | --- | --- |
| 测量固定 horizon 的性能与调用权衡 | Figure 1/2；Table 4 的 15 组同 horizon 对照 | 三个所测骨干上长 horizon 通常降低调用并降低成功率；并未证明所有环境下都不存在合适的固定 horizon。 |
| 构造 detect-and-correct 推理层 | §3.1–3.4；Eq. (2)–(11)；Figure 3 | 外置预测、漂移检测、截断和梯度引导可接入冻结骨干。 |
| 提升鲁棒性与每次调用效率 | Table 1/2/4/5 | 所报告设置均提高平均成功率；每次调用的效率提升不意味着实际运行时间缩短。 |
| 检测事件与关键相位相关 | Figure 5/6 | 失败 episode 具有较重高分尾部，83.7% 截断位于关键相位；缺少误检、漏检与相位时长归一化。 |
| OGG 改善截断后恢复 | Figure 7；Table 6 | 检测定义下平均恢复率增加 0.23，组件平均成功率增加 4.00 个百分点；个别难度子集仍下降。 |
| 外置检测优于所测内部 head | Table 7 | 在 π0.5/MetaWorld 的此实现中，64.35% 高于 49.55%；表征受干扰是作者解释，未被直接测量。 |
| 对真实扰动有帮助 | Table 5/15；Figure 9–12 | 单臂、9 个任务、限定扰动范围内有改善；不覆盖任意扰动或无法恢复的状态。 |

## 结构地图

| 原文章节 | PDF 页码 | 本节目的与主要线索 |
| --- | --- | --- |
| §1 Introduction | 1–3 | 开环盲区、固定 horizon 权衡、检测与纠正两个问题；Figure 1/2。 |
| §2 Preliminaries | 3 | 定义 `A_t`、`C`、`H`、`Q_t`；Eq. (1)。 |
| §3.1 Corrector Training | 4–5 | 学习局部潜残差；Eq. (2)–(4)。 |
| §3.2 LVM Detection | 5 | 比较预测与观测方向；Eq. (5)。 |
| §3.3 Event-Triggered Truncation | 5 | MAD、双阈值与提前截断；Eq. (6)/(7)。 |
| §3.4 OGG Correction | 5–6 | 候选动作效果、纠正目标与流速度更新；Eq. (8)–(11)。 |
| §4.1 Main Results | 6–8 | 跨骨干、LIBERO、数据比例和 horizon 扫描；Table 1–4、Figure 4。 |
| §4.2 Mechanism Analysis | 8–10 | 检测分布、截断相位、恢复对照和案例；Figure 5–8。 |
| §4.3 Real-World Evaluation | 10 | PiPER 三组任务与总体结果；Table 5、Figure 9。 |
| §4.4 Ablation Studies | 10–11 | 截断、OGG 与检测器架构；Table 6/7。 |
| §5 Conclusion | 11 | 汇总冻结骨干上的定向鲁棒性改善。 |
| References | 11–14 | VLA、action chunking、推理引导与恢复相关来源。 |
| Appendix A Related Work | 15 | 生成式策略、horizon 权衡、失败恢复三类工作。 |
| Appendix B Method Details | 16 | 持续计数状态机与运行参数；Eq. (12)/(13)。 |
| Appendix C Training and Implementation | 16–17 | 数据协议、残差 MLP、训练和算力。 |
| Appendix D Additional Results | 17–19 | 引导强度、模型容量、跨域与耗时；Table 8–13。 |
| Appendix E Real-World Details | 19–22 | 九个任务、逐任务结果、协议、失败与示例；Table 14/15、Figure 10–12。 |

## 逐节精读

### §1 Introduction：把动作生成成本与反馈频率联系起来

生成式策略可表示多模态连续动作，但单次调用较贵。Action chunking（动作分块）让控制器先预测未来动作，再执行其中一段，代价是新观测不能及时影响这段队列。作者区分即时反应不足和累积误差进入 OOD 状态两种风险。

![[papers/images/pan2026vla-corrector-lightweight-detect/fig1_openloop_vs_closedloop.png|760]]

**Figure 1 — Open-loop vs. Closed-loop execution.** 图中两排标注相同初始状态与 `t_2` 的相同偏离。`H=10` 的旧队列继续执行，抽屉任务失败；`H=1` 每步重规划，任务成功。该图提供问题示例，不是对所有任务的统计保证。

英文问题归纳是 *“when the current chunk should stop being trusted”*。作者随后提出及时检测与截断、截断后纠正两个问题。Table 4 中 π0.5 从 `H=10` 到 `H=50`，baseline 调用次数为 20.41→5.15，成功率为 64.50%→48.72%，说明频繁反馈与调用成本存在经验权衡。

**Figure 2 — Performance–efficiency trade-off across fixed action horizons.** 小 horizon 在所测设置中获得较高成功率，大 horizon 保留较少调用的收益。图展示三个骨干的经验权衡。

**关键证据 / 图表 / 公式**：Figure 1 展示误差累积案例，Figure 2 展示固定 horizon 曲线。曲线支持研究动机，不能单独证明任意自适应方法都优于调好的静态设置。

### §2 Preliminaries：区分生成长度与执行长度

设 `o_t` 为视觉观测，`𝔈` 为视觉编码器，`Z_t^real=𝔈(o_t)` 为当前潜表示，`l` 为语言指令，`θ` 为策略参数。一次调用产生长度 `C` 的动作块：

$$
A_t=[a_t,a_{t+1},\ldots,a_{t+C-1}]\sim\pi_\theta(\cdot\mid Z_t^{\mathrm{real}},l).\tag{1}
$$

控制器执行前 `H≤C` 个动作，队列为 `Q_t=[a_t,…,a_{t+H-1}]`。本节固定了全文的讨论对象：自适应改变当前队列的实际执行长度，不要求每次改变生成块的长度 `C`。

**关键证据 / 图表 / 公式**：Eq. (1) 是记号定义。`C`、`H`、后文的预测间隔 `k` 和实际执行数 `h` 不能互换。

### §3 方法总览：生成、监控、截断与纠正

![[papers/images/pan2026vla-corrector-lightweight-detect/fig3_overview.png|780]]

**Figure 3 — Overview of VLA-Corrector.** Block A 为标准 chunked VLA；Block B 用 LVM 检测持续漂移并触发事件；Block C 将紧接中断的重规划切换到 OGG；Block D 表示预期潜动态与已发生潜动态之间的纠正几何。图中的流程解释模块关系，实验收益由 §4 验证。

本节的设计原则是 *“decouple action generation from execution monitoring”*。每个控制步可以更新监控信号，主策略只在 horizon 结束或中断时调用。LVM 与 OGG 共用 `M_φ`，但分别用于检测已执行动作的动态和预测候选动作的动态。

#### §3.1 Training the External Latent Dynamics Corrector

先取得在 benchmark 上微调的 VLA，再冻结骨干，用示范轨迹抽取训练转移。对于 `(o_t,a_t,o_{t+k})`：

$$
Z_t^{\mathrm{real}}=\mathcal E(o_t),\qquad
Z_{t+k}^{\mathrm{real}}=\mathcal E(o_{t+k}),\qquad
\Delta Z_{t+k}^{*}=Z_{t+k}^{\mathrm{real}}-Z_t^{\mathrm{real}}.\tag{2}
$$

校正器接收当前潜状态和动作，预测未来残差：

$$
\Delta\hat Z_{t+k}=M_\phi(Z_t^{\mathrm{real}},a_t).\tag{3}
$$

主文训练目标同时约束残差数值与方向：

$$
\mathcal L_{\mathrm{corr}}
=\|\Delta\hat Z_{t+k}-\Delta Z_{t+k}^{*}\|_2^2
+\beta\big[1-\operatorname{CosSim}(\Delta\hat Z_{t+k},\Delta Z_{t+k}^{*})\big].\tag{4}
$$

`φ` 为校正器参数，`β` 平衡两项。残差形式旨在弱化静态内容、关注动作相关变化；它没有保证潜空间差分能完全消除背景或只保留任务动态。示范主要来自成功执行，目标是局部 on-track consistency（在轨一致性），而非生成所有可能未来的完整世界模型。

**关键证据 / 图表 / 公式**：Eq. (2)–(4) 定义监督目标与损失；C.2 给出约 38–42M 的残差 MLP；Table 9 比较容量。

本文不属于整体 training-free（无需训练）系统，接入时不再重训 VLA 才是准确限定。

#### §3.2 Latent Visual Dynamics for Online Anomaly Detection

对于实际执行的 `a_t`，预测 `ΔZ_{t+k}^exp=M_φ(Z_t^real,a_t)`。等 `o_{t+k}` 到达后，计算 `ΔZ_{t+k}^real=Z_{t+k}^real−Z_t^real`，得到：

$$
E_t=1-\operatorname{CosSim}(\Delta Z_{t+k}^{\mathrm{exp}},\Delta Z_{t+k}^{\mathrm{real}}),\qquad
\operatorname{CosSim}(u,v)=\frac{u^\top v}{\|u\|\|v\|}.\tag{5}
$$

数值越大，说明预期变化和实际变化的方向越不一致。理论上非零向量的 `E_t` 位于 `[0,2]`；它不直接度量误差幅度，也不是校准后的失败概率。相同方向、不同幅度的变化可能得到低分。

时间索引需要留意：`E_t` 以预测起点 `t` 命名，但比较依赖 `t+k` 的观测。在线实现必须缓存过去预测与实际动作，再在未来帧到达时对齐，不能在 `t` 提前读取未来观测。

**关键证据 / 图表 / 公式**：Eq. (5) 给出监控信号；Figure 5 比较成功与失败 episode 的分布。论文未给出零范数处理、检测延迟分布或独立失败标注下的精确率与召回率。

#### §3.3 Event-Triggered Truncation under Robust Online Monitoring

近期分数窗口为 `E_W={E_{t-w+1},…,E_t}`，中位数为 `M_e`，尺度统计量为：

$$
\operatorname{MAD}=\operatorname{median}(|E_i-M_e|),\qquad E_i\in\mathbf E_W.\tag{6}
$$

双阈值按在线统计量变化：

$$
T_{\mathrm{on}}=M_e+\lambda_{\mathrm{on}}\operatorname{MAD},\qquad
T_{\mathrm{off}}=M_e+\lambda_{\mathrm{off}}\operatorname{MAD},\qquad
\lambda_{\mathrm{on}}>\lambda_{\mathrm{off}}.\tag{7}
$$

高阈值用于确认异常，低阈值用于恢复与复位。触发事件后清空剩余队列，立即进入新一轮生成。若原队列已执行 `h` 步，实际 horizon 为 `H_adaptive=h<H`；没有中断时执行上限仍为 `H`。

**关键证据 / 图表 / 公式**：Eq. (6)/(7) 说明鲁棒阈值，Figure 6 检查截断相位。

B.1 的 Eq. (12)/(13) 给出计数规则。提前截断是机制定义，但及时性取决于预测间隔、窗口、持续条件和冷却时间。

#### §3.4 Online Gradient Guidance for Corrective Inference

截断可以停止旧动作，恢复质量还取决于下一次生成。OGG 仅用于紧接中断的那一次策略调用，后续调用恢复普通推理，除非再次发生中断。

在 flow-matching denoising time（流匹配去噪时间）`τ`，噪声动作块为 `A^τ`，策略给出 `v_τ=π_θ(A^τ,Z_t^real,τ)`。估计干净动作块 `Â_0=A^τ−τv_τ`，取第一步 `â_t=Â_0[0]`，并预测其潜效果：

$$
\Delta\hat Z_{\mathrm{act}}=M_\phi(Z_t^{\mathrm{real}},\hat a_t).\tag{8}
$$

设论文指定的最后稳定参照时刻为 `t−k`，先前预期位移为 `ΔZ_exp=M_φ(Z_{t−k}^real,a_{t−k})`，已发生位移为 `ΔZ_dev=Z_t^real−Z_{t−k}^real`。纠正目标为：

$$
\Delta Z_{\mathrm{corr}}=\Delta Z_{\mathrm{exp}}-\Delta Z_{\mathrm{dev}}.\tag{9}
$$

这里 `ΔZ_dev` 的数学定义是实际位移，并非已经减去预测的误差。Eq. (9) 可等价写成 `Z_{t−k}^real+M_φ(Z_{t−k}^real,a_{t−k})−Z_t^real`，即从当前状态指向先前预测终点的潜方向。该方向不是动作空间中的手工回退量。

候选第一步动作的潜效果与纠正方向做余弦对齐：

$$
\mathcal L_{\mathrm{OGG}}=1-\operatorname{CosSim}(\Delta\hat Z_{\mathrm{act}},\Delta Z_{\mathrm{corr}}).\tag{10}
$$

随后对速度场做更新：

$$
v_\tau^{\mathrm{guide}}=v_\tau-\eta\nabla_{v_\tau}\mathcal L_{\mathrm{OGG}},\qquad
A^{\tau-\Delta\tau}=A^\tau-\Delta\tau\,v_\tau^{\mathrm{guide}}.\tag{11}
$$

`η` 是引导强度，`Δτ` 是积分步长。`t` 表示环境控制时间，`τ` 表示生成过程的去噪时间。梯度通过候选第一步动作和可微校正器作用于流速度，骨干参数 `θ` 与已训练校正器参数 `φ` 不在在线阶段更新。

**关键证据 / 图表 / 公式**：Eq. (8)–(11) 定义指导信号；Figure 7 和 Table 6 检查其增量收益。损失直接评估第一步的局部潜效果，不能视为对整个 chunk 的长期任务价值优化；平滑恢复轨迹也没有独立定量指标。

### §4.1 Main Results：成功率、数据比例与调用效率

本节从跨骨干效果、少样本骨干、校正器数据量、同 horizon 效率四个角度验证方法。所有成功率为 `%`，相减得到 percentage points（百分点）；效率增益另用相对百分比。

**Table 1 — Cross-architecture generalization on MetaWorld.**

| Backbone / Method | Easy | Medium | Hard | Very Hard | Avg. |
| --- | ---: | ---: | ---: | ---: | ---: |
| π0.5 Baseline | 70.5 | 45.0 | 38.3 | 41.0 | 48.70 |
| π0.5 + VLA-Corrector | 83.2 | 61.7 | 47.5 | 65.0 | 64.35 |
| SmolVLA Baseline | 81.3 | 53.6 | 51.7 | 61.0 | 61.90 |
| SmolVLA + VLA-Corrector | 83.4 | 56.0 | 64.2 | 63.0 | 66.65 |
| X-VLA Baseline | 72.5 | 46.4 | 48.3 | 55.0 | 55.55 |
| X-VLA + VLA-Corrector | 74.4 | 50.0 | 50.0 | 64.0 | 59.60 |

平均增加 15.65、4.75、4.05 个百分点。π0.5 的 Very Hard 增加 24.0 个百分点，但 SmolVLA 最大收益位于 Hard；不能概括为每个骨干均随难度递增。Table 1 未在表中列出各骨干 horizon，不能据相近 baseline 数值把它与 Table 4 的某一行视为同一实验。

**Table 2 — Sample efficiency on LIBERO.**

| π0.5 setting | Object | Spatial | Goal | Long | Avg. |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full Fine-tuned | 99.4 | 98.2 | 97.8 | 92.4 | 96.95 |
| Few-shot Fine-tuned | 97.8 | 95.4 | 96.2 | 86.6 | 94.00 |
| Few-shot + VLA-Corrector | 99.8 | 100.0 | 98.0 | 93.4 | 97.80 |

Few-shot 骨干来自公开 LeRobot checkpoint `pi05_libero_base`。接入纠正器后平均提高 3.80 个百分点，Long 提高 6.8 个百分点；平均超过 Full Fine-tuned 0.85 个百分点。作者认为少样本骨干已覆盖正常轨迹，但缺少偏离状态与恢复行为，这是对结果的解释；论文没有直接量化这类数据覆盖，也没有完整比较两条路线的总训练样本和计算成本。

**Table 3 — Data efficiency of corrector training on MetaWorld.** 该表明确使用 open-loop baseline `H=50`。`r` 是保留训练池的使用比例，不是完整原始数据的比例。

| Method / Ratio | Easy | Medium | Hard | Very Hard | Avg. | 相对 baseline，百分点 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 70.54 | 45.00 | 38.33 | 41.00 | 48.72 | 0 |
| `r=0.2` | 71.07 | 49.55 | 36.67 | 36.00 | 48.32 | −0.40 |
| `r=0.4` | 70.36 | 45.91 | 38.33 | 42.00 | 49.15 | +0.43 |
| `r=0.6` | 70.89 | 52.73 | 39.17 | 46.00 | 52.20 | +3.48 |
| `r=0.8` | 71.07 | 53.64 | 38.33 | 46.00 | 52.26 | +3.54 |
| `r=1.0` | 73.21 | 55.91 | 44.17 | 44.00 | 54.32 | +5.60 |

从 `r=0.6` 到 `0.8` 收益接近，但 `r=1.0` 仍比 `0.8` 高 2.06 个百分点。数据不足时 `r=0.2` 低于 baseline，Very Hard 随数据量也不严格单调。论文用 saturation（趋于饱和）描述整体趋势，表格不足以证明严格饱和阈值。此数据扫描的 54.32% 与 Table 4 同为 `H=50` 的 58.70% 不同，不能省略设置差异后合并数值。

**Table 4 — Full performance–efficiency trade-off across VLA backbones and action horizons.** 每行 baseline 与方法使用相同设定上限 `H`；方法内部可提前截断。

| Backbone | H | Baseline success % | Baseline calls | Ours success % | Ours calls | Δsuccess，百分点 | 相对效率增益 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| π0.5 | 10 | 64.50 | 20.41 | 72.40 | 17.64 | +7.90 | +29.9% |
| π0.5 | 20 | 61.40 | 10.77 | 69.10 | 9.95 | +7.70 | +21.8% |
| π0.5 | 30 | 56.10 | 7.97 | 63.50 | 7.92 | +7.40 | +13.9% |
| π0.5 | 40 | 54.45 | 5.96 | 60.80 | 6.04 | +6.35 | +10.2% |
| π0.5 | 50 | 48.72 | 5.15 | 58.70 | 4.98 | +9.98 | +24.6% |
| SmolVLA | 10 | 61.90 | 19.27 | 73.00 | 15.64 | +11.10 | +45.3% |
| SmolVLA | 20 | 58.90 | 11.32 | 68.90 | 9.50 | +10.00 | +39.4% |
| SmolVLA | 30 | 58.10 | 7.90 | 65.20 | 7.60 | +7.10 | +16.6% |
| SmolVLA | 40 | 56.80 | 5.64 | 67.20 | 5.13 | +10.40 | +30.0% |
| SmolVLA | 50 | 54.20 | 4.86 | 62.90 | 4.68 | +8.70 | +20.6% |
| X-VLA | 4 | 68.50 | 46.58 | 72.00 | 35.20 | +3.50 | +39.1% |
| X-VLA | 8 | 67.80 | 23.18 | 72.10 | 19.48 | +4.30 | +26.5% |
| X-VLA | 16 | 55.50 | 13.71 | 60.90 | 13.92 | +5.40 | +8.1% |
| X-VLA | 24 | 52.90 | 10.13 | 59.20 | 9.92 | +6.30 | +14.3% |
| X-VLA | 32 | 44.00 | 8.61 | 54.40 | 8.34 | +10.40 | +27.6% |

按论文口径，令 `s` 为成功率、`q` 为平均调用次数，则 `eff=s/q`，相对增益为 `(eff_ours/eff_base−1)×100%`。π0.5 的 `H=50` 对应约 +24.6%。这不是每次调用独立成功的概率，也不包含每次调用耗时。

15 行均提高成功率，13 行减少调用；π0.5 的 `H=40` 增加 0.08 calls，X-VLA 的 `H=16` 增加 0.21 calls。三个骨干最大的相对效率增益均在各自最短的所测 horizon，不能说效率增益随 `H` 单调增大。Episode 更早成功也可能减少总调用，表格没有把完成步数变化与截断频率的贡献分开。

**Figure 4 — Performance–efficiency analysis on π0.5.** 左图比较不同 horizon 的成功率与调用次数，右图比较 success-per-call 和相对增益；其数字对应 Table 4 的 π0.5 行。

**关键证据 / 图表 / 公式**：Table 1/2 检查平均收益，Table 3 检查训练数据需求，Figure 4 与 Table 4 检查同 horizon 的成功率/调用关系。表间 π0.5 的 64.35%、54.32%、58.70% 分属不同结果，复现时需保留各表设置。

### §4.2 Mechanism Analysis：检测相关性与恢复增量

**Figure 5 — LVM detection analysis.** 成功 episode 的 `E_t` 集中在较低值，失败 episode 高分尾部更重。图中成功/失败的平均中断次数分别为 Easy 0.82/2.26、Medium 1.86/5.07、Hard 1.21/4.65、Very Hard 1.23/4.13。它说明监测信号与失败相关，未给出独立标注下的检测正确率。

**Figure 6 — Task-phase analysis of LVM-triggered truncation.** 作者人工划分 precise grasping/alignment（精确抓取/对齐）等关键相位，以及稳定抓取后的容错搬运等非关键相位。关键相位占截断事件 83.7%，非关键占 16.3%，事件数比约 5.1。图未报告两类相位的时间占比，不能把事件数比直接解释成每个控制步的触发概率比，也不能据此断言没有误触发。

**Figure 7 — Post-interrupt recovery.** 同一中断截断后，对比 standard re-inference（普通重推理）与 OGG-guided re-inference（梯度引导重推理）。以未来 10 步内 `E_t<T_off` 定义恢复。图中恢复率增量依次为 Easy +0.28、Medium +0.13、Hard +0.22、Very Hard +0.30，Overall +0.23。Overall 是约 23 个百分点的绝对增量，不是相对提高 23%；恢复指标仍使用 LVM 自身信号，不等同于最终完成任务。

**Figure 8 — Controlled recovery case.** LIBERO 杯柄抓取案例使用相同初始状态和检测到的抓取错误。Baseline 仅由 LVM 记录误差，继续旧 chunk 后杯子掉落；完整方法截断并用 OGG 重规划后完成放置。这是代表性定性案例，OGG 的平均增量应结合 Figure 7 与 Table 6 判断。

**关键证据 / 图表 / 公式**：Figure 5/6 检查检测分布与事件位置，Figure 7 隔离重推理引导，Figure 8 展示完整过程。三个环节各有证据，但检测相关性、局部恢复与最终任务成功仍是不同指标。

### §4.3 Real-World Evaluation：扰动使旧 chunk 失效

平台为 AgileX PiPER 6-DoF 单臂，骨干为 π0.5。三个任务组各含三个任务，每任务每方法 20 次，故每组 60 次、每方法总计 180 次。Table 5 的 `±` 是论文报告的 95% binomial confidence intervals（二项置信区间），不是跨任务标准差。

**Table 5 — Real-world evaluation on AgileX PiPER.**

| Method | Pick-place | Alignment | Disturbance | Avg. |
| --- | ---: | ---: | ---: | ---: |
| π0.5 Baseline | 70.0±11.6 | 56.7±12.5 | 40.0±12.4 | 55.6±7.3 |
| + VLA-Corrector | 78.3±10.4 | 73.3±11.2 | 68.3±11.8 | 73.3±6.5 |
| Δsuccess，百分点 | +8.3 | +16.6 | +28.3 | +17.7 |

收益在普通抓取放置、对齐、扰动恢复三组中依次增加，符合旧队列在状态突变后更易失效的设定。**Figure 9 — Real-world disturbance recovery demo.** 人在执行中移动蓝碗，机器人需要重新适配放置目标。论文对扰动做了可见、可达和每次一次的限制，具体协议在 E.3。

**关键证据 / 图表 / 公式**：Table 5 给出组级成功率和区间，Table 15 给出九个任务，Figure 9 是扰动示例。小样本、单本体与人工扰动限制了对复杂装配、长期多扰动和其他本体的外推。

### §4.4 Ablation Studies：截断、引导与外置检测

**Table 6 — Component ablation on MetaWorld.**

| π0.5 variant | Easy | Medium | Hard | Very Hard | Avg. |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline Open-loop | 70.5 | 45.0 | 38.3 | 41.0 | 48.70 |
| + Truncation Only | 81.8 | 53.6 | 50.0 | 56.0 | 60.35 |
| + Truncation + OGG | 83.2 | 61.7 | 47.5 | 65.0 | 64.35 |

截断本身贡献平均 +11.65 个百分点，增加 OGG 后再提高 4.00 个百分点。Hard 从 50.0% 降至 47.5%，说明 OGG 并非逐子集都改善最终成功率，尽管 Figure 7 的局部恢复率在各难度均增加。

**Table 7 — Coupled vs. decoupled detection on MetaWorld.**

| Detector | Easy | Medium | Hard | Very Hard | Avg. |
| --- | ---: | ---: | ---: | ---: | ---: |
| Internal Head + OGG | 65.2 | 46.0 | 36.5 | 50.5 | 49.55 |
| Decoupled LVM + OGG | 83.2 | 61.7 | 47.5 | 65.0 | 64.35 |

内部 head 用末层最后 token 的隐藏状态与已执行动作预测同一种潜残差，并联合微调 π0.5。两种设置均在中断后使用 OGG，外置版本平均高 14.80 个百分点。作者认为辅助目标可能改变动作规划所依赖的骨干表征；表格支持所测架构比较，没有直接证明表征污染，也不能排除其他内部 head 的设计。

**关键证据 / 图表 / 公式**：Table 6 区分截断与引导的增量，Table 7 比较检测架构，D.1 补充引导强度与容量。主结果主要针对 π0.5/MetaWorld，不能视为所有骨干的架构结论。

### §5 Conclusion：结论适用的范围

结论指出小规模推理模块可在冻结 VLA 上提供针对性的鲁棒性改善。方法保留 action chunking，通过漂移事件缩短实际执行时域，并为下一次生成增加恢复方向。

**关键证据 / 图表 / 公式**：本节不增加实验，结论依赖 §4 与附录 D/E。最稳妥的表述是所测模型、基准与真实任务上的经验改善，不是无需训练、无需延迟或可保证恢复的通用控制器。

## 附录精读

### Appendix A Related Work

**A.1 Generative VLA Models** 解释 VLA 的视觉语言预训练与连续动作生成背景，涉及 RT-2、OpenVLA、π0、GR00T、Octo，以及 diffusion/flow matching。它把方法问题放在动作表达能力与推理成本之间，未增加独立实验。

**A.2 Action Chunk and Horizon Trade-off** 讨论 ACT、Diffusion Policy 等的动作分块，以及 Mixture of Horizons、Bidirectional Decoding、Adaptive Action Chunking 等相关方向。本文选择执行期间监控与事件截断；其 OGG 形式也引用 ACG: Action Coherence Guidance for Flow-Based VLA Models。相关方法被引用，不表示主实验包含与它们的直接比较。

**A.3 Failure Recovery in Visuomotor Policies** 区分通过交互/人工接管扩展训练分布，与显式恢复策略、搜索或分布约束两类路径。本文在已获得策略上训练外置动态模块，再在线检测和引导，与直接扩展骨干训练分布的路线不同。

**关键证据 / 图表 / 公式**：附录 A 提供文献位置，没有新增数值证据。比较创新性时，应继续检查实时 action-chunk correction 与 adaptive chunking 文献，而不能只比较普通固定 horizon baseline。

### Appendix B Method Details

**B.1 Details of Event-Triggered Truncation** 给出双阈值持续计数器：

$$
c_t=\begin{cases}
c_{t-1}+1,&E_t>T_{\mathrm{on}},\\
0,&E_t<T_{\mathrm{off}},\\
c_{t-1},&\text{otherwise}.
\end{cases}\tag{12}
$$

$$
c_t\ge p.\tag{13}
$$

Eq. (13) 是中断条件。触发后清空队列、清零计数器、标记下一次为纠正推理。Eq. (12) 在阈值中间区间保留计数，所以它表示迟滞下的持续性，不完全等同于任意一次未超高阈就清零的严格连续计数。

**B.2 LVM and OGG Runtime Parameters** 报告滑窗 `w=15`，`λ_on=3.0`，`λ_off=2.0`，`p=5`，连续 5 个安全步复位，冷却 10 步，OGG 默认 `η=1`，三骨干相同。OGG 只用于中断后的单次查询。

**关键证据 / 图表 / 公式**：Eq. (12)/(13) 和运行参数补全 §3.3。

主文及 B.2 的 *“p consecutive steps”* 与 Eq. (12) 保留中间区间计数的细节不完全一致；安全复位和冷却也没有全部展开在该公式中。实际复现需要核对实现的时间对齐、窗口更新和状态切换顺序。

### Appendix C Training and Implementation Details

**C.1 Benchmarks and Evaluation Protocol** 将 MetaWorld 分成四种难度，逐任务评估，每任务默认 20 个 episode。C.1 的数据扫描按 episode 划分 10% validation、10% test，其余为训练池；多种子划分使用 `{42,123,999}`，各分区要求至少 20 个 episode。

主文 §4.1 则写先保留 20% validation，再对其余 80% 做比例抽样。两种描述的训练池均为 80%，但验证/测试划分不同，不能当作同一协议。附录虽提及多种子，Table 3 未给出对应逐种子结果或方差。

**C.2 External Corrector Architecture** 将动作线性嵌入，与 `Z_t^real` 拼接后输入残差 MLP。四个隐藏层宽度为 `[2048,2048,2048,2048]`，输出潜残差。动作和视觉维数不同使参数量约 38–42M，论文统一简称约 40M。

**C.3 Corrector Training** 的超参数如下。

| 项目 | 论文设置 |
| --- | --- |
| 优化器 | AdamW |
| 初始学习率 | `3×10^−4` |
| Weight decay | `10^−4` |
| 调度 | Cosine annealing，最小学习率为初始值的 `0.01` 倍 |
| 训练周期 | 30 epochs，early stopping patience 为 5 |
| 比例扫描 batch | 训练 128，评估 256 |
| 部署 corrector batch | 512；文中命名为 `h1-k10` |
| 部署 loss 描述 | Cosine-based training loss |

训练预算按 `steps_per_epoch=ceil(N_train/B)`、`total_steps=30×steps_per_epoch` 给出，`N_train` 为样本数，`B` 为 batch size；若提前停止，实际步数可小于预算。正文 Eq. (4) 写平方误差加余弦项，C.3 仅描述部署配置用 cosine-based loss，未交代两者具体对应关系或 `β` 默认值。

**C.4 Compute Resources** 报告仿真主训练和评估服务器使用 8 张 NVIDIA A100-SXM4-40GB。校正器训练只优化外置 MLP，相比 VLA 微调范围较小；论文没有给出完整训练 GPU-hours 或端到端新增模块训练成本。

**关键证据 / 图表 / 公式**：C.1–C.4 给出复现条件，Table 3/9 支持数据量与容量比较。`h1-k10` 暗示部署使用局部动作/10 步预测配置，但论文没有完整解释命名、跨 chunk 的缓存及中断后重置方式，不能把缺省实现细节自行补成论文事实。

### Appendix D Additional Experimental Results

#### D.1 Ablation Sensitivity

此节保持 π0.5 与 MetaWorld 设置，比较 OGG 强度与监控器容量。

**Table 8 — Ablation on OGG guidance strength η.**

| η | Easy | Medium | Hard | Very Hard | Avg. |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0.1 | 82.7 | 56.8 | 45.2 | 66.0 | 62.68 |
| 1，默认 | 83.2 | 61.7 | 47.5 | 65.0 | 64.35 |
| 10 | 82.5 | 56.8 | 38.3 | 65.0 | 60.65 |
| 100 | 80.9 | 55.0 | 36.7 | 63.0 | 58.90 |

`η=1` 平均最好，强引导 `η=100` 比默认低 5.45 个百分点；Very Hard 则以 `η=0.1` 的 66.0% 最高，故默认并非每个子集最优。

**Table 9 — Ablation on LVM capacity.**

| Capacity | Easy | Medium | Hard | Very Hard | Avg. |
| --- | ---: | ---: | ---: | ---: | ---: |
| 10M | 78.5 | 52.4 | 39.8 | 55.6 | 56.58 |
| 40M，默认 | 83.2 | 61.7 | 47.5 | 65.0 | 64.35 |
| 160M | 82.8 | 62.1 | 48.0 | 64.2 | 64.28 |

40M 比 10M 高 7.77 个百分点，160M 比 40M 低 0.07 个百分点。该设置支持选用约 40M，但没有给出容量对应的检测校准、训练成本或置信区间。

**关键证据 / 图表 / 公式**：Table 8/9 说明引导强度和容量存在取舍，不是数值越大越好；未系统扫描 MAD 窗口、双阈系数、patience 或预测间隔。

#### D.2 Cross-Domain Corrector Generalization

使用同一 MetaWorld π0.5 baseline，分别接入 LIBERO 示范和 MetaWorld 示范训练的校正器。

**Table 10 — Cross-domain corrector generalization on MetaWorld.**

| Corrector source | Easy | Medium | Hard | Very Hard | Avg. |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 70.5 | 45.0 | 38.3 | 41.0 | 48.7 |
| LIBERO-trained | 70.9 | 50.5 | 40.7 | 45.0 | 51.8 |
| MetaWorld-trained | 74.1 | 53.8 | 52.9 | 54.0 | 58.7 |

跨域平均增加 3.1 个百分点，域匹配平均增加 10.0 个百分点。它支持部分迁移，也表明训练域影响效果。只测一个迁移方向与一个骨干，不能据此推断任意 benchmark 或本体的 zero-shot corrector transfer。

**关键证据 / 图表 / 公式**：Table 10 为直接跨域对照；其 58.7% 属于该表设置，不替代 Table 1 的 64.35%。

#### D.3 Inference-Time Overhead

此节区分 policy-call efficiency 与 wall-clock inference time。`w/o OGG` 是同一动作块推理流程禁用梯度引导，`w/ OGG` 是启用事件触发引导；不能把前者直接等同于不带任何监控模块的裸骨干总系统。

**Table 11 — Overall inference-time summary by backbone on MetaWorld.**

| Backbone | Episodes | Steps/episode | Calls/episode | w/o OGG，s/episode | w/ OGG，s/episode | 比值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| π0.5 | 1000 | 163.77 | 6.22 | 2.49 | 4.03 | 1.62× |
| SmolVLA | 1000 | 158.75 | 5.67 | 2.13 | 3.51 | 1.65× |
| X-VLA | 1000 | 177.92 | 10.30 | 1.54 | 2.59 | 1.68× |
| Overall | 3000 | 166.81 | 7.39 | 2.06 | 3.38 | 1.64× |

**Table 12 — Average per-step inference-time overhead.** 单位均为 ms/已执行环境步。

| Backbone | w/o OGG | w/ OGG | 新增耗时 | 比值 |
| --- | ---: | ---: | ---: | ---: |
| π0.5 | 15.23 | 24.62 | 9.39 | 1.62× |
| SmolVLA | 13.44 | 22.14 | 8.70 | 1.65× |
| X-VLA | 8.66 | 14.55 | 5.89 | 1.68× |
| Overall | 12.32 | 20.25 | 7.93 | 1.64× |

**Table 13 — Average inference time per MetaWorld task.** 每骨干 50 个任务，每任务 20 个 episode。

| Backbone | w/o OGG，s/task | w/ OGG，s/task | OGG events/task |
| --- | ---: | ---: | ---: |
| π0.5 | 49.87 | 80.63 | 71.28 |
| SmolVLA | 42.66 | 70.29 | 62.24 |
| X-VLA | 30.81 | 51.76 | 119.76 |

正文讨论给出标准单次动作块调用 278.01 ms，OGG 恢复调用 588.52 ms，约 2.12×。该比值属于单次恢复调用；Table 11 的约 1.64× 属于事件触发后按 episode 累计的推理时间。二者都不是机器人整任务物理完成时间，单步均摊数值也不能当作每次实时调用延迟。

**关键证据 / 图表 / 公式**：Table 11–13 支持 OGG 增加计算成本的判断。事件触发减少引导次数，但仍有计算开销；success-per-call 提高不意味着实际运行时间缩短，也不能据此判断系统是否满足特定控制频率。还需测量视觉编码、通信、执行阻塞和控制 deadline。

### Appendix E Real-World Details

#### E.1 Robot Platform and Task Suite

Baseline 与方法共享同一个微调 π0.5、RGB 相机、语言指令、配置 horizon 和初始条件。成功定义为执行开始后不需 human reset（人工重置）即可完成指定任务；预定扰动本身是评测输入，不是人工接管恢复。

**Table 14 — Real-world task suite on AgileX PiPER.**

| 组别 | Task | 操作与检验对象 |
| --- | --- | --- |
| Pick-and-place | Cube-to-region | 将方块放入标记区域。 |
| Pick-and-place | Cube-to-drawer-top | 将方块放到小抽屉平台顶部。 |
| Pick-and-place | Object-to-container | 将方块放入指定碗。 |
| Alignment | Corner placement | 精确放在抽屉顶面左上角。 |
| Alignment | Square-hole insertion | 对齐并插入方孔或槽。 |
| Alignment | Edge alignment | 对齐狭窄标记边或目标条带。 |
| Disturbance | Moving-object grasp | 即将抓取时移动物体。 |
| Disturbance | Moving-placement target | 已抓取后移动放置区域。 |
| Disturbance | Moving-insertion target | 对齐或插入前移动孔位或目标。 |

#### E.2 Per-Task Real-World Results

**Table 15 — Per-task real-world success rates.** 每任务每方法 20 次。组级和总体的 `±` 是跨任务 standard deviation（标准差），不同于 Table 5 的二项置信区间。

| Group / Task | Baseline % | Ours % | Δ，百分点 |
| --- | ---: | ---: | ---: |
| Cube-to-region | 75.0 | 85.0 | +10.0 |
| Cube-to-drawer-top | 70.0 | 80.0 | +10.0 |
| Object-to-container | 65.0 | 70.0 | +5.0 |
| Pick-place Group Avg. | 70.0±5.0 | 78.3±7.6 | +8.3 |
| Corner placement | 60.0 | 75.0 | +15.0 |
| Square-hole insertion | 50.0 | 70.0 | +20.0 |
| Edge alignment | 60.0 | 75.0 | +15.0 |
| Alignment Group Avg. | 56.7±5.8 | 73.3±2.9 | +16.6 |
| Moving-object grasp | 45.0 | 75.0 | +30.0 |
| Moving-placement target | 40.0 | 70.0 | +30.0 |
| Moving-insertion target | 35.0 | 60.0 | +25.0 |
| Disturbance Group Avg. | 40.0±5.0 | 68.3±7.6 | +28.3 |
| Overall，9 tasks | 55.6±13.8 | 73.3±7.1 | +17.7 |

任务层面的 5 个百分点相当于 20 次试验中的 1 次。结果支持限定任务集中的一致改善，但不宜把小差距视为已经完成统计显著性检验。

#### E.3 Real-World Protocol and Task Details

每任务先采集 10–30 条人类遥操作示范，用于微调该任务的 π0.5。两种方法复用同一骨干。初始物体位姿在小范围随机化，并保持任务对 6-DoF 手臂可行。

扰动按预定义任务相位施加，不按固定控制时间。抓取扰动在夹爪接近物体时发生；放置扰动在抓取后、释放前发生；插入扰动在接近对齐或插入时发生。每 trial 只施加一次，目标保持相机可见，位移受限于可物理恢复范围。Baseline 与方法采用相同相位规则和扰动范围，未说明每一 trial 的位移严格逐一配对。

#### E.4 Observed Real-World Failure Modes

作者报告四类剩余失败：目标超出可达范围或扰动过晚造成不利夹爪姿态；缺少力反馈下的接触几何、摩擦和微小高度误差；夹爪遮挡或目标对比度低造成视觉歧义；冻结 π0.5 不能表达所需恢复动作。OGG 只能偏置已有生成能力，不能创造骨干从未能表示的动作行为。

#### E.5 Real-World Demonstration Examples

**Figure 10 — Demo: Moving-object grasp.** 人移动方块，机器人重新抓取并放入白碗，展示抓取目标变化。

**Figure 11 — Demo: Moving-placement target.** 人移动蓝碗，机器人适配新的放置位置。图与主文 Figure 9 使用同一演示对象，不能视为额外独立统计试验。

**Figure 12 — Demo: Moving-insertion target.** 图题具体描述为移动抽屉后将方块放在抽屉顶面左上角。虽然标签为 moving-insertion target，该图不是方孔插入的成功率证据；方孔任务应按 Table 14/15 判断。

**关键证据 / 图表 / 公式**：Table 14/15 补全任务及逐项结果，E.3 限定扰动协议，E.4 给出作者观察到的失败，Figure 10–12 仅作过程示例。

## 方法细节

在线流程需要分别保存动作队列、潜状态/预测缓存、近期分数窗口、持续计数、恢复状态和冷却计时。普通 horizon 结束会重新生成 chunk；只有监测中断后的下一次生成启用 OGG。

复现的关键是时间对齐：`M_φ(Z_t,a_t)` 预测 `k` 步后的变化，评估时需拿对应未来观测比较。OGG 的 `t−k` 参照又被描述为最后稳定时刻，若长期异常或频繁中断，需要明确如何选参照，不能仅据符号假定所有 `t−k` 都稳定。

模型输入只显式包含当前动作 `a_t`，而目标跨越 `k` 步。这使学到的动态也可能依赖示范中后续动作的统计规律。它不是显式输入全部 `k` 步动作序列的预测器；改变策略或动态后，预测适用性需重新验证。

## 实验设置、数据集、基线、指标

| 项目 | 条件与解释 |
| --- | --- |
| MetaWorld | 50 个任务的统计见 Table 13；Easy/Medium/Hard/Very Hard 分组；默认每任务 20 episodes。 |
| LIBERO | Object/Spatial/Goal/Long 四个 suite；π0.5 few-shot checkpoint 与 fully fine-tuned baseline。 |
| 真实数据 | 九任务，每任务 10–30 条遥操示范，每方法每任务 20 trials。 |
| 主 baseline | 同骨干的固定 horizon chunked policy；Table 4 逐 horizon 匹配。 |
| 消融 baseline | 只截断不做 OGG；内部 residual head 加 OGG；不同 η、不同 LVM 容量。 |
| 未直接比较的路线 | 相关工作中的 adaptive chunking、实时纠正、ACG、搜索/恢复策略；引用不能代替同协议实验。 |
| 成功率 | 仿真按任务完成判据；真实任务要求执行开始后无需人工重置。 |
| Calls/episode | 每 episode 的策略调用次数；提前完成会改变总数。 |
| Success-per-call | `success rate / mean calls`；不包含梯度调用比普通调用更贵的差异。 |
| Post-interrupt recovery | 下一段 10 步内 `E_t<T_off`；用检测信号定义局部恢复。 |
| 耗时 | Table 11–13 的累计推理时间、每步均摊时间与每任务推理时间；非整任务物理时长。 |
| 不确定性 | Table 5 报二项 95% CI，Table 15 报跨任务 SD；仿真主表未展示完整多种子区间。 |

## 主要结果、消融或对比

最直接的方法证据是同 horizon 的 Table 4 与组件 Table 6。前者给出调用次数和成功率的共同变化，后者显示提前停止旧队列贡献了主要平均增量，OGG 进一步提高平均结果。

LIBERO 的 97.80% 支持所测 few-shot 骨干可被增强，尚不足以建立完整的训练样本成本优势。跨域结果支持有限迁移，域匹配数据仍有效。真实扰动组收益较大，同时执行条件被限定在可见、可恢复、单次扰动范围内。

## 图表、公式与表格线索

### Figure 图题与阅读线索

| 图号 / PDF 页 | English caption title | 解释与证据用途 |
| --- | --- | --- |
| Figure 1 / 2 | Open-loop vs. Closed-loop execution | 相同初态与偏离的抽屉示例；对比 `H=10` 与 `H=1`。 |
| Figure 2 / 2 | Performance–efficiency trade-off across fixed action horizons | 三骨干固定 horizon 的成功率/调用曲线。 |
| Figure 3 / 4 | Overview of VLA-Corrector | 生成、监控、截断、OGG 和潜几何四个 Block。 |
| Figure 4 / 7 | Performance–efficiency analysis on π0.5 | 左为成功率/调用关系，右为 success-per-call 与相对增益。 |
| Figure 5 / 9 | LVM detection analysis | 成功/失败分数分布及不同难度的中断次数。 |
| Figure 6 / 9 | Task-phase analysis of LVM-triggered truncation | 关键相位 83.7%、非关键 16.3% 的截断占比。 |
| Figure 7 / 9 | Post-interrupt recovery | OGG 与普通重推理；总体恢复率绝对增加 0.23。 |
| Figure 8 / 10 | Controlled recovery case | 相同初态与抓取误差的 LIBERO 杯子案例。 |
| Figure 9 / 10 | Real-world disturbance recovery demo | 人移动蓝碗后的重新放置过程。 |
| Figure 10 / 22 | Demo: Moving-object grasp | 人移动方块，机器人抓取并放入白碗。 |
| Figure 11 / 22 | Demo: Moving-placement target | 人移动蓝碗后的适应过程。 |
| Figure 12 / 22 | Demo: Moving-insertion target | 移动抽屉后精确放置；图题具体描述为顶面左上角放置。 |

### Equation / Table 检索线索

| 原文编号 | 内容与用途 |
| --- | --- |
| Eq. (1) | Chunk 长度 `C` 与执行 horizon `H` 的定义。 |
| Eq. (2)–(4) | 潜残差监督目标、预测器、数值/方向训练损失。 |
| Eq. (5) | 预测/实际变化方向的不一致分数。 |
| Eq. (6)/(7) | MAD 和高低阈值。 |
| Eq. (8)–(11) | 候选第一步效果、纠正方向、对齐损失与流速度更新。 |
| Eq. (12)/(13) | 持续计数器和触发条件。 |
| Table 1/2 | 跨架构与 LIBERO 数据有限骨干结果。 |
| Table 3/4 | 校正器数据比例与完整 horizon 扫描。 |
| Table 5/14/15 | 真实组级、任务定义与逐任务成功率。 |
| Table 6/7 | 截断/OGG 与外置/内置检测消融。 |
| Table 8/9/10 | 引导强度、容量、训练域。 |
| Table 11/12/13 | Episode、环境步、任务三个粒度的推理开销。 |

完整本地图片列表见 [[papers/images/pan2026vla-corrector-lightweight-detect/index.md]]。两张方法图分别说明研究问题和系统流程；其他图表的分析见对应章节。

## 主张-证据-边界矩阵

| 主张 | 直接证据 | 适用边界或尚缺证据 |
| --- | --- | --- |
| 固定 horizon 存在成功率/调用权衡 | Figure 2，Table 4 | 三骨干的经验趋势；未证明所有任务的最优静态上限。 |
| 外置局部动态可提供漂移信号 | Eq. (5)，Figure 5 | 信号与失败相关；缺少独立检测真值、ROC、延迟与零残差稳定性。 |
| 截断集中在敏感任务相位 | Figure 6 | 人工标注的事件占比；无相位时长归一化与误触发率。 |
| OGG 改善恢复 | Figure 7，Table 6 | 平均局部恢复与成功率增加；Hard 最终成功率下降，恢复定义复用 LVM。 |
| 外置 LVM 优于内部 head | Table 7 | 仅一个内部 head 配置；表征受损是可能解释。 |
| Few-shot 可超过全量微调 | Table 2 | 一个骨干/基准，平均差 0.85 个百分点；缺少总数据预算和显著性证据。 |
| 每次调用效率提高 | Table 4 | 所有行相对增益为正；两行调用更多，耗时没有降低保证。 |
| 事件触发降低 OGG 使用频次 | §3.4，B.2，Table 11–13 | 相对普通调用单次约 2.12×，累计推理约 1.64×；不能推导实时性。 |
| 校正器能跨域迁移 | Table 10 | LIBERO→MetaWorld 平均 +3.1 个百分点，域匹配 +10.0；无广泛跨本体验证。 |
| 真实扰动下更稳健 | Table 5/15，E.3/E.4 | 单次、可见、可恢复的人工扰动；无力反馈与骨干能力仍限制恢复。 |

## 局限与可追问点

### 作者报告的失败

E.4 的可达性、时机、接触几何、视觉歧义和骨干动作先验限制，使局部纠正无法保证任务恢复。特别是无力反馈的紧配合任务，即使视觉目标已修正，仍可能因摩擦或高度误差失败。

### 由公式和实验范围提出的追问

- 单一 `k` 的方向失配对慢漂移、等方向幅度误差和遮挡是否可靠？多间隔、幅度分数或触觉能否改善漏检，需要独立实验。
- 稳定动作导致近零残差时怎样计算余弦？MAD 接近零、启动窗口未满、长期高分使在线阈值升高时如何处理？论文未展开。
- `w`、`λ_on/off`、`p`、冷却和安全复位在不同任务/本体中是否需要重调？现有敏感性只覆盖 `η` 和容量。
- OGG 候选动作或 `ΔZ_corr` 处于示范未覆盖的区域时，校正器梯度是否可靠？文章没有给出梯度校准或潜方向与真实恢复方向的误差。
- 若同一 episode 持续发生多个扰动，单次引导、冷却与检测延迟会怎样影响控制？当前真实评测每 trial 仅一次扰动。
- 每秒成功任务数、能耗、视觉编码成本和控制 deadline 是否仍改善？当前 success-per-call 与推理时间回答不同问题。
- 与专门 adaptive chunking、实时 action-chunk correction、ACG 或恢复策略，在相同示范和计算预算下效果如何？主实验未覆盖这类直接对照。

### 复现时需保留的原文差异

| 问题 | 两处表述 | 影响 |
| --- | --- | --- |
| 数据划分 | §4.1 为 20% validation；C.1 为 10% validation + 10% test | 训练池相同，但验证、测试隔离方式需确认。 |
| 持续计数 | §3.3/B.2 写 consecutive；Eq. (12) 在中间阈值区间保持计数 | 严格连续与迟滞累积可能触发不同事件。 |
| 部署 loss | Eq. (4) 为平方误差加余弦项；C.3 为 cosine-based loss | 需明确具体目标、权重与部署配置。 |
| 不同主表成功率 | Table 1 为 64.35%；Table 3 `r=1` 为 54.32%；Table 4 `H=50` 为 58.70% | 不能假定全部为同一 horizon、训练配方或评测运行。 |

## 与当前库的连接

| 库内论文 | 共同问题与对照方式 |
| --- | --- |
| [[@yu2026wm-dagger|WM-DAgger]] | 处理误差累积与 OOD recovery。WM-DAgger 用世界模型合成恢复数据并训练策略，本文训练局部校正器后在执行期检测与引导；可比较新增数据成本与在线成本。 |
| [[@xiao2026enpire|ENPIRE]] | 通过物理反馈改进策略。ENPIRE 组织自动实验与训练改进流程，本文关注单次执行中的局部纠正机制；不是直接同协议竞争方法。 |
| [[@deng2026e2hil|E2HiL]] | 改善真实机器人学习与恢复。E2HiL 筛选 HiL-RL 更新样本，本文冻结骨干后引导推理；可比较人工接管数据如何发挥作用。 |
| [[@kang2026x-tokenizer|X-Tokenizer]] | 都涉及视觉/动作表征。X-Tokenizer 为预训练建立语义动作接口，本文用视觉潜变化判断已有动作队列的可靠性，作用阶段不同。 |

地图位置为 `#map/具身智能/VLA/推理期检测纠正与自适应动作时域`。当前库连接用于组织研究问题，不表示论文对这些方法做过实验比较。

## 精读路线 / 为什么需要回看

| 阅读目的 | 建议原文位置 | 要确认的问题 |
| --- | --- | --- |
| 理解核心机制 | Figure 1/3，§3.2–3.4 | 何时失配、何时截断、纠正方向如何进入动作生成？ |
| 实现监控器 | Eq. (2)–(7)，B.1/B.2，C.2/C.3 | 预测时间对齐、窗口与计数器、损失和部署配置。 |
| 评估实际收益 | Table 4/6/7，Figure 7 | 是否同 horizon、截断与 OGG 各贡献多少、局部恢复是否对应最终成功？ |
| 评估部署成本 | D.3，Table 11–13 | 每次调用成本、累计推理耗时和实时阻塞能否满足控制要求？ |
| 迁移到新任务 | Table 10，E.3/E.4 | 需要哪些域匹配示范，目标可见性与骨干恢复能力是否满足？ |

当需要为 chunked policy 选择重规划时机，或希望在冻结骨干上增加局部恢复能力时，回看 Eq. (5)–(13)。当比较推理纠正与训练期恢复数据时，结合校正器训练需求、Table 2/3 和实际 OGG 耗时，避免只按成功率或 calls 作成本判断。

## 一句话总结

VLA-Corrector 用示范训练的外置潜动态模块，在冻结 VLA 执行动作块时检测漂移、提前截断，并仅对紧接中断的重规划施加梯度引导。所测仿真与真实任务中的成功率和 success-per-call 得到改善，但在线计算成本、视觉可辨性、域匹配示范和骨干既有动作能力仍限定恢复效果。
