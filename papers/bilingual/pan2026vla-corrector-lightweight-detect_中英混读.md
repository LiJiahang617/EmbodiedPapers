---
tags:
  - bilingual-reading
paper: "[[@pan2026vla-corrector-lightweight-detect]]"
source_pdf: "[[papers/pdfs/pan2026vla-corrector-lightweight-detect.pdf]]"
images: "papers/images/pan2026vla-corrector-lightweight-detect/"
image_index: "[[papers/images/pan2026vla-corrector-lightweight-detect/index.md]]"
created: 2026-07-07
---

# VLA-Corrector: Lightweight Detect-and-Correct Inference for Adaptive Action Horizon

paper:: [[@pan2026vla-corrector-lightweight-detect]]
pdf:: [[papers/pdfs/pan2026vla-corrector-lightweight-detect.pdf]]
images:: [[papers/images/pan2026vla-corrector-lightweight-detect/index.md]]

> 单位：Zhejiang University（OmniAI Group of ZJU ACES Lab） · Alibaba DAMO Academy ｜ arXiv:2607.01804v1（2026-07）｜ 代码：https://github.com/ZJU-OmniAI/vla-corrector

## 核心词汇速查

| English | 中文 | 在本文中的作用 |
| --- | --- | --- |
| Vision-Language-Action, VLA | 视觉-语言-动作模型 | 统一感知/语言/动作生成的机器人基础模型，是本文要“外挂增强”的对象。 |
| action chunk | 动作块 | 一次前向预测未来一整段动作 `A_t=[a_t,…,a_{t+C-1}]`，降低策略调用频率。 |
| action horizon, H | 动作时域 | 一个 chunk 里实际开环执行的前 H 步；本文主角就是要把它从固定变成自适应。 |
| open-loop blind spot | 开环盲区 | 执行 chunk 期间不再查询策略、忽略新观测的那段时间，是误差累积的温床。 |
| compounding errors | 误差累积 | 小偏差在盲区里不断放大，最终把机器人推到 OOD 状态、任务失败。 |
| closed-loop reactivity | 闭环反应性 | 每步都看新观测、重规划的能力；H=1 时最强但最贵。 |
| Latent-space Vision Monitor, LVM | 潜空间视觉监视器 | 本文检测模块：在线比较“预测视觉演化 vs 实际视觉演化”，输出偏离分数。 |
| external latent dynamics corrector, `M_φ` | 外置潜动态校正器 | 约 40M 的轻量 MLP，预测动作引起的短程潜空间残差演化，是 LVM 和 OGG 的共同引擎。 |
| residual latent evolution, `ΔZ` | 潜空间残差演化 | `Z_{t+k}-Z_t`，只建模“变化量”而非绝对未来帧，抑制静态背景、聚焦任务相关动态。 |
| inconsistency score, `E_t` | 不一致分数 | `1 - CosSim(ΔZ^exp, ΔZ^real)`，越大说明视觉动态偏离越严重。 |
| event-triggered truncation | 事件触发截断 | 偏离“持续”达标才中断 chunk、丢弃剩余动作、触发重规划。 |
| MAD (median absolute deviation) | 中位数绝对偏差 | 用鲁棒统计做动态阈值，抵抗瞬时视觉离群点导致的误触发。 |
| hysteresis (Ton/Toff) | 迟滞双阈值 | `Ton` 确认异常、`Toff` 确认恢复，防止在正常/异常间反复抖动。 |
| adaptive action horizon | 自适应动作时域 | 稳定时保留长时域效率、漂移时缩短为短时域纠正，本文的核心产物。 |
| Online Gradient Guidance, OGG | 在线梯度引导 | 截断后那**一次**重规划时，往 flow matching 速度场注入纠正梯度，主动把机器人拉回正轨。 |
| flow matching | 流匹配 | 生成式动作模型，学习速度场 `v_τ`；OGG 修改的是这个速度场而非动作坐标。 |
| corrective latent direction, `ΔZ_corr` | 纠正潜方向 | `ΔZ_exp - ΔZ_dev`，既保留原本该有的局部动态，又补偿开环累积的漂移。 |
| success-per-call efficiency | 单次调用成功率效率 | 成功率 / 平均策略调用次数，本文强调“每次调用更有用”，而非单纯多调用。 |
| MetaWorld / LIBERO | 两个仿真基准 | 前者测接触密集操作鲁棒性（4 难度档），后者测语言条件长时域任务。 |
| π0.5 / SmolVLA / X-VLA | 三个 VLA 骨干 | π0.5 是主骨干，另两个用于跨架构验证“即插即用不重训”。 |

## 摘要

VLA 基础模型在具身智能上进展很快。为降低策略调用频率、保持时间连贯性，多数生成式策略采用 **action chunk**：一次推理预测多步未来动作，并在固定 **action horizon** 下**开环**执行。但这种“predict-then-blindly-execute（先预测再盲执行）”范式牺牲了闭环反应性——在接触密集（contact-rich）交互中，即使很小的局部扰动，也会在开环盲区里迅速放大，造成误差累积直至任务失败。

作者提出 **VLA-Corrector**：一个面向 action-chunked VLA 策略的**轻量纠正式推理框架**，**不改动骨干策略权重**。它引入轻量的 **Latent-space Vision Monitor (LVM)**，持续比较“预测的视觉特征演化”与“实际的视觉特征演化”，在线检测视觉动态偏离；一旦偏离**持续**出现，系统触发截断事件（truncation event），丢弃剩余的过期动作（stale actions），并通过 **Online Gradient Guidance (OGG)** 触发纠正式重规划。这个 detect-and-correct 机制天然诱导出**事件触发的自适应动作时域**：chunk 可靠时保留长时域执行，执行开始漂移时切换到短时域纠正重规划，从而缓解固定时域在“执行鲁棒性 vs 策略调用频率”之间的静态权衡。方法可无重训接入不同 VLA，在长时域、接触密集操作任务上显著提升鲁棒性，同时保留 action chunking 的大部分效率收益。

## 论文主线

这篇论文的主线可以用一句话锚定：**在不动 VLA 骨干权重、不加真实机器人重训成本的前提下，用一个约 40M 的外置潜动态校正器，把“固定盲执行的动作时域”变成“检测到漂移就自动缩短并纠正的自适应时域”。**

![[papers/images/pan2026vla-corrector-lightweight-detect/fig1_openloop_vs_closedloop.png|760]]

**Figure 1 / 首页问题图。** 上排 `H=10` 开环：机器人在 `t_2` 出现偏离（Deviation）后仍从同一个旧 chunk `A_{t_0}` 里继续取 `a_{t_0+1}, a_{t_0+2}, …` 盲执行（No infer），偏差一路放大，最后卡死（Get Stuck / Failure）。下排 `H=1` 严格闭环：每步都 `infer` 新 chunk、只执行第一个动作，因此能 replan 回来、成功开抽屉。两排从**同一个初始状态、同一个 `t_2` 偏离**出发，唯一区别是“要不要、以及什么时候重规划”——这正是本文要自动化的决策。

作者的论证链条非常清晰：

1. **问题定位**：action chunking 是工程上的必要妥协（省算力、动作平滑），但它制造了 open-loop blind spot，带来两个复合风险——策略缺乏实时反应性（新观测被忽略到 horizon 结束）；误差可能累积到**连下一次重规划都救不回来**的 OOD 状态。而且 **horizon 越长，两个风险都越严重**。
2. **量化权衡**：在三个骨干上系统扫描 horizon（Fig 2）。以 π0.5 为例，增大 horizon 让策略调用减少约 4×，但成功率从约 64% 掉到 49% 以下；SmolVLA、X-VLA 同样。而且最优 horizon 依赖任务难度、环境动态、sim-to-real 失配，**没有一个静态 horizon 能全场景最优**。结论：关键不是“选一个更好的固定 horizon”，而是“决定**何时**当前 chunk 不该再被信任”。
3. **两个关键问题**：(1) 如何**及时检测**执行偏离并在误差不可逆前终止过期动作；(2) 截断后如何**纠正**——因为 naive replanning 常常不够，VLA 可能重新生成仍然逃不出偏离状态的动作，让机器人再次被困。
4. **两个机制回答**：LVM 触发的截断回答问题 (1)；OGG 引导的重规划回答问题 (2)。二者合起来把固定时域变成“带自纠正重规划的自适应时域”，同时保留长时域效率与短时域反应性。
5. **收益口径**：强调 **success-per-call efficiency**（每次调用的成功率），而非“多调用换成功率”。π0.5 在 horizon 50 时成功率 48.7%→58.7%，平均调用反而从 5.15 降到 4.98，效率净增 +24.6%。在 LIBERO 上，few-shot 微调 + VLA-Corrector 达到 97.8%，**反超全量微调 baseline 96.9%**。

## 贡献与结论对照

| 论文声称的贡献 | 方法位置 | 证据位置 | 结论强度 |
| --- | --- | --- | --- |
| 系统量化固定动作时域在 chunked VLA 中的性能-效率权衡，证明开环盲区一致地损害鲁棒性。 | Fig 2 的 horizon 扫描（§1）。 | 三个骨干横向对比（Fig 2、Table 4）。 | 证据充分，趋势跨骨干一致，是全文动机的经验支撑。 |
| 提出 VLA-Corrector：给冻结 VLA 外挂潜空间监控 + 事件触发截断 + 恢复导向的引导重规划。 | §3.1–3.4，Fig 3 总览。 | Table 1/2/4/5 全面提升。 | 强，方法自洽且即插即用（不重训骨干）。 |
| LVM 提供有用且**时机恰当**的漂移信号。 | §3.2–3.3，`E_t` + 鲁棒阈值。 | Fig 5（`E_t` 分布）、Fig 6（83.7% 截断落在关键相位）。 | 较强，Fig 6 直接支撑“自适应时域”而非“到处缩短”。 |
| OGG 在截断后进一步改善恢复质量，而非只靠 naive replan。 | §3.4，Eq (8)–(11)。 | Fig 7（各难度恢复率平均 +0.23）、Table 6 消融（+OGG 再涨 4 点）。 | 中到强，消融把截断与 OGG 的贡献拆开了。 |
| 把检测器与骨干**解耦**（外置）比耦合（内置 aux head）更好。 | §4.4，Table 7。 | Decoupled 64.35 vs Internal 49.55（同用 OGG）。 | 强，且给出机理解释（内置目标会污染 VLM-to-action 表征）。 |
| 提升 success-per-call 效率而非单纯多调用。 | §4.1，Table 4、Fig 4。 | π0.5 +29.9%、SmolVLA +45.3%、X-VLA +39.1%。 | 强，很多设置下调用次数还**下降**。 |
| 真实机器人上有效，尤其对在线扰动。 | §4.3，AgileX PiPER。 | Table 5：平均 55.6→73.3，扰动组 +28.3。 | 中，规模小（每任务 20 trial）但方向清晰、给了置信区间。 |

## 结构地图

- **§1 Introduction**：动机——open-loop blind spot、性能-效率权衡（Fig 1/2）、两个关键问题、方法概述、贡献。
- **§2 Preliminaries**：形式化 action chunk 与 action horizon（Eq 1），定义执行队列 `Q_t`。
- **§3 Method**：(3.1) 训练外置潜动态校正器 `M_φ`（Eq 2–4）；(3.2) LVM 在线异常检测（Eq 5）；(3.3) 事件触发截断与鲁棒阈值（Eq 6–7、附录 B.1 状态机 Eq 12–13）；(3.4) OGG 纠正推理（Eq 8–11）。总览见 Fig 3。
- **§4 Experiments**：(4.1) 主结果与性能-效率（Table 1–4、Fig 4）；(4.2) 机理分析（Fig 5–8）；(4.3) 真实世界（Table 5、Fig 9）；(4.4) 消融（Table 6–7，附录 D 的 Table 8–13）。
- **§5 Conclusion**：小推理时模块即可带来定向鲁棒性提升，不重训骨干；不是取代 chunking，而是让它自适应。
- **附录**：A 相关工作；B 方法细节（截断状态机、运行参数）；C 训练实现（架构、优化、算力）；D 额外实验（敏感性、跨域、推理开销）；E 真实世界细节（平台、任务、失败模式、demo）。

## 逐节精读

### §1 Introduction —— 把“盲执行”的代价量化出来

本节推进论证的方式是：先承认 action chunking 的合理性（省调用、动作平滑），再指出它的结构性代价，然后**用实验把代价量化**，逼出“自适应时域”这个命题。

两个复合风险讲得很到位：**第一，缺乏实时反应性**——每个控制步都有新观测到达，但系统要到 horizon 结束才理它，无法对突发滑移、碰撞、位姿漂移做出反应。**第二，误差可能累积到重规划也救不回**——如果偏离长时间不纠正，机器人会漂到训练时罕见的 OOD 状态，此时连下一次 replan 都无法把执行拉回预期轨迹。关键一句：**两个风险都随 horizon 增大而恶化**。

作者用一句话把命题收敛：*“the key is not to choose a better fixed horizon, but to decide when the current chunk should stop being trusted.”*（关键不是选更好的固定时域，而是决定何时不再信任当前 chunk。）随后把它拆成两个可操作的问题：**何时截断** 与 **如何纠正**，分别对应 LVM 和 OGG。

**关键证据 / 图表 / 公式**：Fig 1（开环 vs 闭环的失败/成功对照，直觉锚点）、Fig 2（三骨干的性能-效率曲线，量化“大 horizon 省调用但掉成功率”）。要注意的边界：Fig 2 说明“没有全场景最优的静态 horizon”，这是方法必要性的核心论据，但它本身不证明“自适应一定优于最优静态”——那要靠 Table 4 的逐 horizon 对比。

### §2 Preliminaries —— 形式化 chunk 与 horizon

视觉观测 `o_t` 先由编码器 `E` 编码为潜表示 `Z_t^real = E(o_t)`。生成式 VLA 策略 `π_θ` 一次推理预测一整块动作：

$$A_t = [a_t, a_{t+1}, \dots, a_{t+C-1}] \sim \pi_\theta(\cdot \mid Z_t^{real}, l) \tag{1}$$

其中 `l` 是语言指令，`C` 是 chunk 长度。部署时只顺序执行前 `H` 步（`H ≤ C`），这个窗口叫 **action horizon**；对应执行队列 `Q_t=[a_t,…,a_{t+H-1}]`，在此期间控制器**不再查询** VLA。本节的作用是把“盲区”精确化：盲区就是执行 `Q_t` 的这段时间。

### §3 VLA-Corrector 方法 —— 解耦“动作生成”与“执行监控”

![[papers/images/pan2026vla-corrector-lightweight-detect/fig3_overview.png|780]]

**Figure 3 / 方法总览。** Block A 是标准 chunked VLA（VLM + Action Expert + Flow Matching，全部冻结 ❄）。Block B 是 LVM：用 `M_φ`(40M) 算期望视觉演化 `ΔZ^exp`，与实际 `ΔZ^real` 比出 `E_t`，在 Dynamic Window 里做鲁棒阈值 `T_on/T_off`，连续 `p` 次超阈才 Interrupt（剪刀=截断，`h=H_adaptive`）。Block C 是 OGG：截断后那一次重规划，在 flow matching 速度场上注入梯度 `η∇L`（橙线=带 OGG 的 flow，偏离 baseline 的蓝线被拉向 Ideal Flow）。Block D 是 OGG 的几何直觉：观测轨迹在 `t` 出错（error），OGG 用 `t-k` 的期望方向补偿累积漂移，把 `Z^real` 导向 recover。

本节的总设计原则一句话：**decouple action generation from execution monitoring（把动作生成与执行监控解耦）**——VLA 骨干负责生成 chunk，VLA-Corrector 负责判断执行是否还在轨、只在漂移出现时介入。

#### §3.1 训练外置潜动态校正器 `M_φ`

先在基准训练集上微调 VLA 骨干，然后**冻结**它，用它的视觉编码器 `E` 从示范轨迹里抽潜表示。给定一个 transition `(o_t, a_t, o_{t+k})`：

$$Z_t^{real}=E(o_t),\quad Z_{t+k}^{real}=E(o_{t+k}),\quad \Delta Z_{t+k}^{*}=Z_{t+k}^{real}-Z_t^{real} \tag{2}$$

`ΔZ*_{t+k}` 是“已执行动作诱导的目标短程视觉潜演化”。训练一个轻量校正器预测这个**残差**演化：

$$\Delta \hat{Z}_{t+k}=M_\phi(Z_t^{real}, a_t) \tag{3}$$

**为什么预测残差而非绝对未来帧**：残差主动抑制静态场景内容，逼模型聚焦任务相关动态。训练目标同时约束幅度与方向：

$$\mathcal{L}_{corr}=\big\lVert \Delta\hat{Z}_{t+k}-\Delta Z_{t+k}^{*}\big\rVert_2^2 + \beta\big[1-\mathrm{CosSim}(\Delta\hat{Z}_{t+k}, \Delta Z_{t+k}^{*})\big] \tag{4}$$

`β` 平衡“残差幅度精度”与“方向一致性”。**可训练的不是 VLA 策略本身，而是建在冻结 VLA 特征之上的轻量潜动态模块**，因此可为每个基准单独重训/替换，无需重优化昂贵骨干。作者反复强调：`M_φ` 的目标**不是像 world model 那样建模所有可能未来**，而只是学“局部潜动态是否与在轨执行一致”。示范数据虽有遥操抖动/局部瑕疵，但仍能反映“让任务正确推进”的行为，足以做这个局部、低维预测任务——所以一个 40M MLP 就够、训练成本极低。

**要点边界**：这是全文最关键的设计取舍——用“局部一致性判别”替代“完整动力学预测”，是它 data-efficient、cheap 的根因，但也决定了它的天花板（见 §局限）。

#### §3.2 LVM 在线异常检测

训练好 `M_φ` 后在线使用。在控制步 `t`，用已执行动作 `a_t` 与当前潜态 `Z_t^real` 预测**期望**短程残差 `ΔZ^exp_{t+k}=M_φ(Z_t^real, a_t)`。执行过程中，最新观测其实一直可得（只是策略没被重新查询），于是编码未来观测、算出**实际**残差 `ΔZ^real_{t+k}=Z_{t+k}^real - Z_t^real`，再度量二者不一致：

$$E_t = 1 - \mathrm{CosSim}\big(\Delta Z_{t+k}^{exp}, \Delta Z_{t+k}^{real}\big),\quad \mathrm{CosSim}(u,v)=u^\top v/(\lVert u\rVert\,\lVert v\rVert) \tag{5}$$

`E_t` 越大=视觉动态失配越强，为后续事件触发截断提供**连续**信号。这里的巧思是：**盲区里其实不缺观测，缺的是“把观测和预期对齐”的判据**——LVM 补上的正是这个判据，代价只是一次 `M_φ` 前向。

#### §3.3 事件触发截断（鲁棒在线监控）

直接对 `E_t` 阈值化不稳定（瞬时视觉离群会误触发），所以用**鲁棒统计 + 持续性检查**。维护近期分数滑窗 `E_W={E_{t-w+1},…,E_t}`，计算中位数 `M_e` 与中位数绝对偏差：

$$\mathrm{MAD}=\mathrm{median}(|E_i - M_e|),\ E_i\in E_W \tag{6}$$

用它定义两个自适应阈值（迟滞）：

$$T_{on}=M_e+\lambda_{on}\mathrm{MAD},\quad T_{off}=M_e+\lambda_{off}\mathrm{MAD},\quad \lambda_{on}>\lambda_{off} \tag{7}$$

`T_on` 确认持续异常，`T_off` 提供恢复迟滞。**只有 `E_t>T_on` 连续 `p` 步成立才触发中断**，孤立尖峰被忽略。附录 B.1 给出完整状态机：持续计数器 `c_t`（超 `T_on` 累加、低于 `T_off` 清零、之间保持），`c_t≥p` 触发中断（Eq 12–13）。中断后丢弃当前队列剩余动作、计数器清零、以纠正模式重新查询策略。若已执行 `h` 个动作，则**实际时域 `H_adaptive = h < H`**——固定时域**只在**持续视觉漂移表明当前 chunk 已过期时才被缩短。

运行参数（附录 B.2）：滑窗 15、`λ_on=3.0`、`λ_off=2.0`、`p=5`（也要求连续 5 个安全步才复位）、中断冷却 10 步（避免介入后立刻反复触发）。

#### §3.4 OGG 纠正推理

截断只是“停掉过期动作”，恢复还得靠下一次 replan。**OGG 只作用于中断后紧接着的那一次策略调用**（源自 Park et al. 2025 的思路）。

- **候选动作的潜效果**：在 flow matching 的去噪步 `τ`，噪声动作块为 `A^τ`，VLA 预测速度场 `v_τ=π_θ(A^τ, Z_t^real, τ)`，据此估计干净块 `Â_0=A^τ-τ v_τ`，取首动作 `â_t=Â_0[0]`。校正器预测该候选动作的潜效果：`ΔẐ_act=M_φ(Z_t^real, â_t)`（Eq 8）。
- **纠正目标**：设 `t-k` 是中断前最后一个稳定步。期望残差 `ΔZ_exp=M_φ(Z_{t-k}^real, a_{t-k})`（由 `t-k` 预测出的“本该发生的局部动态”）；累积漂移 `ΔZ_dev=Z_t^real - Z_{t-k}^real`。纠正潜方向：

$$\Delta Z_{corr}=\Delta Z_{exp}-\Delta Z_{dev} \tag{9}$$

它**既保留原本该有的局部动态、又补偿开环期间累积的漂移**——这是 OGG 的核心几何（Fig 3-D）。
- **引导速度更新**：让候选动作的潜效果对齐 `ΔZ_corr`：

$$\mathcal{L}_{OGG}=1-\mathrm{CosSim}(\Delta\hat{Z}_{act}, \Delta Z_{corr}) \tag{10}$$

把梯度注入 flow-matching 速度场：

$$v_\tau^{guide}=v_\tau-\eta\nabla_{v_\tau}\mathcal{L}_{OGG},\quad A^{\tau-\Delta\tau}=A^\tau-\Delta\tau\,v_\tau^{guide} \tag{11}$$

`η` 控制引导强度（默认 `η=1`）。**因为 OGG 改的是速度场而非直接扰动动作坐标**，它与原始 flow-matching 过程兼容，纠正重规划更平滑。

**要点边界**：OGG 仍以冻结 π0.5 的动作先验为底座——它能把生成偏向更好的纠正方向，但**无法创造骨干本身表达不了的恢复行为**（作者在 E.4 明确承认）。

## 方法细节（实现口径）

- **`M_φ` 架构（C.2）**：残差 MLP。动作经线性 embedding，与当前视觉潜 `Z_t^real` 拼接，过若干 residual MLP block，预测短程潜残差（非绝对未来态）。四层隐藏、宽度 `[2048,2048,2048,2048]`；因动作维/潜维随设置不同，参数量约 38–42M，统称 “~40M MLP corrector”。
- **训练（C.3）**：冻结骨干抽帧后训练。AdamW，lr `3e-4`，weight decay `1e-4`，cosine annealing（`η_min=0.01×lr`），30 epoch + early stopping patience 5。部署用的 `h1-k10` 校正器 batch 512。
- **关键超参**：预测间隔 `k`（部署配置 h1-k10）；`β`（Eq 4 方向权重）；`λ_on=3, λ_off=2, w=15, p=5, cooldown=10`（LVM）；`η=1`（OGG）。
- **算力（C.4）**：仿真实验用 8×A100-40GB；校正器训练相对骨干微调极轻（只在冻结特征上优化 MLP）；在线时 LVM 仅加一次 `M_φ` 前向，OGG 只在中断后那次调用加梯度计算。

## 实验设置、数据集、基线、指标

- **基准**：MetaWorld（接触密集操作，4 难度档 Easy/Medium/Hard/Very Hard，每任务默认 20 episode）；LIBERO（语言条件长时域，Object/Spatial/Goal/Long）；真实 AgileX PiPER 6-DoF 机械臂。
- **骨干/基线**：π0.5（主）、SmolVLA、X-VLA；baseline 即“同一冻结骨干 + 固定 horizon 开环执行”。LIBERO 用 LeRobot 公开 few-shot checkpoint `pi05_libero_base`。
- **指标**：任务成功率（主）、平均策略调用次数 calls、**success-per-call efficiency**（成功率/调用）、post-interrupt recovery rate（中断后 10 步内 `E_t<T_off` 记为恢复）。
- **对照的公平性**：真实世界里 baseline 与 VLA-Corrector **共享同一微调骨干、同样的相机观测/指令/horizon/初始条件**，因此差异只归因于推理时纠正模块。

## 主要结果、消融与对比

**Table 1｜MetaWorld 跨架构泛化（成功率 %）**

| Backbone | Method | Easy | Medium | Hard | Very Hard | Avg. |
| --- | --- | --- | --- | --- | --- | --- |
| π0.5 | Baseline | 70.5 | 45.0 | 38.3 | 41.0 | 48.70 |
| π0.5 | +VLA-Corrector | 83.2 | 61.7 | 47.5 | **65.0** | **64.35 (↑15.65)** |
| SmolVLA | Baseline | 81.3 | 53.6 | 51.7 | 61.0 | 61.90 |
| SmolVLA | +VLA-Corrector | 83.4 | 56.0 | 64.2 | 63.0 | 66.65 (↑4.75) |
| X-VLA | Baseline | 72.5 | 46.4 | 48.3 | 55.0 | 55.55 |
| X-VLA | +VLA-Corrector | 74.4 | 50.0 | 50.0 | 64.0 | 59.60 (↑4.05) |

越难的任务收益越大，π0.5 的 Very Hard 从 41.0→65.0（+24.0）最亮眼。

**Table 2｜LIBERO 样本效率（成功率 %）**

| Model | Object | Spatial | Goal | Long | Avg. |
| --- | --- | --- | --- | --- | --- |
| π0.5（Full Fine-tuned） | 99.4 | 98.2 | 97.8 | 92.4 | 96.95 |
| π0.5（Few-shot Fine-tuned） | 97.8 | 95.4 | 96.2 | 86.6 | 94.00 |
| π0.5（Few-shot）+VLA-Corrector | 99.8 | 100.0 | 98.0 | 93.4 | **97.80 (↑3.80)** |

**few-shot + 推理纠正反超全量微调**。作者解读：few-shot 已学会大部分正常轨迹，缺的是“漂移状态及其恢复行为”的覆盖；与其在训练期喂更多罕见失败样本，不如**在推理期早截断误差、引导纠正**，从而降低对额外后训练数据的依赖。

**Table 4｜完整 horizon 扫描（节选，success%/calls/效率增益）**

| Model | Horizon | Base Succ | Base Calls | Ours Succ | Ours Calls | Eff. Gain |
| --- | --- | --- | --- | --- | --- | --- |
| π0.5 | 10 | 64.50 | 20.41 | 72.40 | 17.64 | +29.9% |
| π0.5 | 50 | 48.72 | 5.15 | 58.70 | 4.98 | +24.6% |
| SmolVLA | 10 | 61.90 | 19.27 | 73.00 | 15.64 | +45.3% |
| SmolVLA | 40 | 56.80 | 5.64 | 67.20 | 5.13 | +30.0% |
| X-VLA | 4 | 68.50 | 46.58 | 72.00 | 35.20 | +39.1% |
| X-VLA | 32 | 44.00 | 8.61 | 54.40 | 8.34 | +27.6% |

核心信息：**很多设置下成功率涨、调用次数还降**（`↓Calls`），说明收益不是“多调用换来的”，而是“每次调用更有用”。长 horizon 处增益尤其大——那正是过期动作最有时间累积误差的地方，支撑“自适应时域”假设。

**Table 3｜校正器数据效率**：随示范比例 `r` 上升而提升但边际递减，`r=0.6–0.8` 附近饱和（`r=1.0` 时 54.32，↑5.60）；印证“只需学局部在轨一致性，不需完整动力学模型”，因此 data-efficient。

**机理分析（§4.2）**：
- **LVM 检测**（Fig 5）：成功 episode 的 `E_t` 集中在低值，失败 episode 有更重的高分尾部、触发更多中断——`E_t` 确实捕捉了“易失败的视觉动态失配”。
- **截断时机**（Fig 6）：把 MetaWorld 轨迹人工分为关键相位（精确抓取/对齐）与非关键相位（稳定抓取后的容错搬运），**83.7% 的截断发生在关键相位**（比非关键多 5.1×）。这直接验证：方法**不是到处缩短时域**，而是在容错相位保留长时域效率、在误差敏感相位恢复短时域精度。
- **OGG 恢复**（Fig 7）：同样的中断截断后，比较 standard re-inference vs OGG-guided re-inference，OGG 在所有难度档都提升恢复率，平均 **+0.23**。
- **受控恢复案例**（Fig 8）：同一初始态、同一抓取误差下，仅被 LVM 监控但不截断的 baseline 继续执行原 chunk→杯子掉落失败；VLA-Corrector 截断 + OGG 重规划→稳定抓取并放置成功。

**真实世界（Table 5，AgileX PiPER，含 95% 二项置信区间）**

| Method | Pick-place | Alignment | Disturbance | Avg. |
| --- | --- | --- | --- | --- |
| π0.5 Baseline | 70.0±11.6 | 56.7±12.5 | 40.0±12.4 | 55.6±7.3 |
| +VLA-Corrector | 78.3±10.4 (↑8.3) | 73.3±11.2 (↑16.6) | 68.3±11.8 (↑28.3) | **73.3±6.5 (↑17.7)** |

增益梯度与设计意图完全吻合：pick-and-place（chunk 常仍有效）收益最小；alignment（小位姿误差不可容忍）中等；**disturbance recovery（人为在精确相位移动物体/目标，使剩余 chunk 过期）收益最大**（Fig 9 是移动蓝碗的 demo）。

**消融**：
- **组件（Table 6）**：Baseline 48.70 → 仅截断 60.35（↑11.65）→ 截断+OGG 64.35（↑15.65）。截断本身贡献最大，OGG 再补一刀。
- **解耦 vs 耦合检测（Table 7）**：同用 OGG，外置 LVM 64.35 vs 内置 aux head 49.55。机理解释：内置目标会更新“也被 VLM-to-action 规划使用”的骨干表征，可能损害原动作生成；外置在冻结特征上学监控信号，避免污染策略表征。
- **敏感性（附录 D，Table 8/9）**：`η=1` 最优（过强会拖累难任务）；LVM 从 10M→40M 大幅提升，40M→160M 几无额外增益。
- **跨域泛化（Table 10）**：LIBERO-trained 校正器仍能把 MetaWorld baseline 48.7→51.8（有限但非平凡的跨域迁移），域匹配的 MetaWorld-trained 则到 58.7——说明信号部分可迁移，但域匹配示范仍重要。
- **推理开销（Table 11–13）**：开 OGG 使壁钟推理时间 1.62–1.68×，但**事件触发**：仅中断后那次调用做梯度计算。单步平均从 12.32ms→20.25ms（+7.93ms）；单次标准 chunk 推理 278ms，一次 OGG 引导恢复 588ms（约 2.12×），但整段 rollout 被摊薄。

## 图表、公式与表格线索

- **Fig 1**：开环 vs 闭环失败/成功对照——问题的直觉锚点（本文档已嵌入）。
- **Fig 2**：三骨干性能-效率曲线——量化“无全场景最优静态 horizon”，方法必要性论据。
- **Fig 3**：四 Block 总览（A pipeline / B LVM / C OGG flow / D OGG 几何）——理解方法的主图（本文档已嵌入）。
- **Fig 5/6/7/8**：机理四联——`E_t` 判别性、截断落在关键相位、OGG 提升恢复率、受控案例。这几张是“为什么有效”的核心证据，回看时优先。
- **Eq 2–4**：残差目标 + 幅度/方向双损失，是 `M_φ` 的定义。
- **Eq 5**：`E_t` 不一致分数，检测信号本体。
- **Eq 6–7 + Eq 12–13**：MAD 鲁棒阈值 + 持续计数状态机，是“稳健触发”的关键。
- **Eq 8–11**：OGG 四步（候选潜效果→纠正方向 `ΔZ_corr`→`L_OGG`→速度场注入）。
- **Table 4**：全 horizon 扫描——“涨成功率且不涨（甚至降）调用”的最强证据。

## 主张-证据-边界矩阵

| 主张 | 证据 | 边界 / 可质疑处 |
| --- | --- | --- |
| 开环盲区一致损害鲁棒性，且随 horizon 恶化。 | Fig 2、Table 4 跨三骨干。 | 仅在 MetaWorld/LIBERO/单一真实臂；未覆盖双臂/移动操作/更长任务。 |
| 局部潜一致性判别足以及时检测漂移。 | Fig 5（`E_t` 分布）、Fig 6（时机）。 | `E_t` 依赖单一 `k` 的短程残差；对缓慢累积、非视觉可辨（如力/滑动）的漂移可能不敏感。 |
| 事件触发截断把固定时域变自适应且更省调用。 | Table 4（多处 `↓Calls`）、Fig 6（83.7% 落关键相位）。 | 阈值/持续参数（λ、p、window、cooldown）需调；论文只报默认值，跨任务鲁棒性未系统扫。 |
| OGG 比 naive replan 恢复更好。 | Fig 7（+0.23）、Table 6（+OGG 涨 4 点）。 | OGG 受限于冻结骨干先验，救不了骨干表达不了的行为（E.4 承认）。 |
| 外置解耦优于内置耦合检测。 | Table 7（64.35 vs 49.55）。 | 只在 π0.5/MetaWorld 验证一种耦合实现（aux head 用 last token 隐状态）。 |
| few-shot + 纠正可反超全量微调。 | Table 2（97.80 vs 96.95）。 | 只在 LIBERO 一个基准、π0.5 一个骨干；差距 <1 点。 |
| 开销可接受（事件触发摊薄）。 | Table 11–13。 | OGG 单次 2.12× 慢；高频反复中断的场景摊薄假设会变弱。 |

## 局限与可追问点

作者在 E.4 坦诚的失败模式：目标被移出可达区、扰动发生在夹爪已进入不利位姿之后，单次纠正重规划就没有足够工作空间/时间恢复；紧配合对齐任务在**无力反馈**的 6-DoF 臂上，即便视觉目标已纠正，仍可能因接触几何/摩擦/微小高度误差失败；视觉歧义（夹爪遮挡、物体与目标对比度差）也会致错；最后，**OGG 受限于冻结 π0.5 的动作先验**——只能偏置生成方向，无法创造骨干表达不了的恢复行为。

可继续追问：
1. `E_t` 只用单一预测间隔 `k`：对**缓慢累积**或**视觉难辨**（力觉/滑动/遮挡下）的漂移是否会漏检？多尺度 `k` 或引入触觉是否更稳？
2. 鲁棒阈值一堆超参（λ_on/off、p、window、cooldown）只报默认值——跨任务/跨本体是否需要重调？能否自适应？
3. OGG 只在“中断后一次”生效：如果一次纠正不够（连环扰动），是否该允许多次或滚动引导？其 2.12× 开销在高中断率场景会不会吃掉效率收益？
4. 校正器需域匹配示范才发挥最大价值（Table 10）：换新任务仍要采数据训 `M_φ`，虽轻但非零成本——能否做到真正 zero-shot 的在轨一致性判别？
5. 与真正的 world-model / 价值模型式纠正相比，“局部一致性判别”的天花板在哪里？在需要**长程重规划**而非局部拉回的失败上是否力不从心？

## 与当前库的连接

- 与 [[@yu2026wm-dagger|WM-DAgger]] 是**同一问题（compounding errors / OOD recovery）的两条不同路线**：WM-DAgger 在**训练期**用 world model 合成 recovery 数据扩分布；VLA-Corrector 在**推理期**不改骨干、只检测+引导纠正。两者可对照“把鲁棒性放训练还是放推理”。
- 与 [[@xiao2026enpire|ENPIRE]]（自改进/物理自动研究）、[[@deng2026e2hil|E2HiL]]（真实机器人 HiL RL）同属“如何让 VLA 更稳/自纠”，但本文强调**免重训、外挂式**，成本定位最轻。
- 与 [[@kang2026x-tokenizer|X-Tokenizer]]（VLA 动作表示）互补：一个管“动作怎么表示”，一个管“动作块执行到一半要不要停”。
- 地图归属：`#map/具身智能/VLA/推理期检测纠正与自适应动作时域`（本文新开轴）。相关工作里大量“adaptive action chunking / bidirectional decoding / speculative verification / closed-loop chunk correction”值得作为该轴的邻居继续入库。

## 精读路线 / 为什么需要回看

- **只想抓核心思想**：读 §1（Fig 1/2）→ Fig 3 总览 → §3.3 截断规则 + §3.4 OGG 的 `ΔZ_corr`（Eq 9）。
- **要复现/实现**：§3.1–3.4 全部公式 + 附录 B.2（运行参数）+ C.2/C.3（架构与训练）。`M_φ` 是残差 MLP、40M、cheap，是复现门槛最低处。
- **判断可信度**：Table 4（涨成功率不涨调用）+ Table 6/7（截断/OGG/解耦拆解）+ Fig 6（截断时机）+ Table 11–13（开销）。
- **回看触发条件**：当你要给别的 chunked 策略加“何时该重规划”的判据，或想在**推理期**而非训练期解决 OOD 恢复时，回到 §3.2–3.4；当质疑“自适应是否真优于最优静态 horizon”时，回到 Table 4 逐 horizon 对照。

## 一句话总结

作者先用跨骨干实验**测量并证明**了 action-chunked VLA 的“固定动作时域”在鲁棒性与调用频率间存在无法一劳永逸调好的静态权衡（开环盲区随 horizon 恶化），然后**构造**了一个不改骨干、约 40M 外置校正器驱动的 detect-and-correct 推理层（LVM 检测漂移触发截断 + OGG 引导纠正重规划），把固定时域变成事件触发的自适应时域——在仿真与真实机器人上一致提升 success-per-call 效率与鲁棒性，尤其在长时域、接触密集、有在线扰动的任务上收益最大。
