---
tags:
  - bilingual-reading
  - deep-reading
source_pdf: "[[papers/pdfs/han2026hil-umi.pdf]]"
paper: "[[@han2026hil-umi]]"
images: "papers/images/han2026hil-umi/"
image_index: "[[papers/images/han2026hil-umi/index.md]]"
created: 2026-10-02
reading_mode: full-close-reading
reading_standard: "bilingual full-reading"
source_pages: 9
source_version: "2609.20659v1"
---

# HIL-UMI：把人在环 VLA 后训练带到手持 UMI 采集

paper:: [[@han2026hil-umi]]
pdf:: [[papers/pdfs/han2026hil-umi.pdf]]
source:: [arXiv:2609.20659v1](https://arxiv.org/abs/2609.20659)
project:: [HIL-UMI](https://hil-umi.github.io)

## 核心词汇速查

| English / 缩写 | 中文与本文用法 |
| --- | --- |
| Vision-Language-Action / VLA（视觉语言动作模型） | 输入图像和任务指令，输出机器人动作；本文以 $\pi_{0.5}$ 为初始模型 |
| Human-in-the-Loop / HIL（人在环） | 人类示范与当前模型的预测共同决定下一批采集内容 |
| Universal Manipulation Interface / UMI（通用操作接口） | 手持夹爪采集与机器人兼容的观测、位姿和夹爪动作 |
| Supervised Fine-Tuning / SFT（监督微调） | 对示范动作应用常规模仿损失，是本文主要基线 |
| Out-of-Distribution / OOD（分布外） | 本文操作性定义为模型预测与人类示范不一致、训练覆盖不足的情境 |
| Action chunk（动作片段） | 同一观测下的一段未来动作，包含位置、旋转和夹爪命令 |
| Energy Score / ES（能量评分） | 用人类片段到策略样本的距离减去样本间分散修正，衡量分布预测与示范的差异 |
| Relative task progress（相对任务进度） | 两幅观测之间的进度变化，由时间线性标签监督 |
| Advantage-conditioned behavioral cloning / ACBC（优势条件行为克隆） | 将正、负优势标签附在任务指令中，推理时使用正标签 |
| Task Progress Score / TPS（任务进度分数） | 子任务累积分数，范围 0–100；与整条任务的成功率口径不同 |

## 摘要

通用 VLA 模型经过任务示范微调后仍可能失败。静态数据主要覆盖人类专家访问的状态，难以补充策略自身的薄弱情境；常规模仿损失又把推动任务的动作与停滞、低效动作同等处理。机器人上的交互式后训练可以补充纠错数据，但反复执行策略和接管机器人会增加采集时间，并限制多地并行采集。

HIL-UMI 让人使用手持 UMI 示范任务，同时在相同观测流上查询当前策略，策略输出不驱动机器人。第一条采集流程用 ES 比较人类动作与策略动作分布，保存分歧较大的子任务片段。另一条流程在进度模型低估人类示范进展时保存片段，用这些数据改进进度模型。之后，更新后的模型给基础数据提供优势标签，策略通过新旧数据混合和 ACBC 继续训练。

四个真实操作任务的结果支持这一组合的有效性。HIL-UMI 的最终四任务平均 TPS 从图中读得约 94.75，SFT 约 58。Clean Up Table 上，HIL-UMI 最终 TPS 约 96，HG-DAgger 约 91，采集时间分别为 73.40 与 412.99 ms/frame。这里的无机器人指采集不需要执行策略，效果评估仍在 Franka 机械臂上完成。

> “This design preserves the iterative and policy-aware nature of human-in-the-loop learning while decoupling data collection from robot deployment.”

这句话概括了论文的设计目标。是否能替代部署时的真实失败覆盖，还需要结合观测分布、进度标签和实验范围判断。

## 论文主线

作者提出一个由当前模型指导数据采集的后训练系统。其关键变化是将发现模型分歧的步骤放到人类手持示范过程中，从而减少为了采集而占用真实机器人。

1. 用基础 UMI 示范初始化进度模型，再通过优势条件训练得到基础策略。
2. 分别查询当前进度模型与当前策略，收集两种用途不同的数据。
3. 更新进度模型，重新标注基础策略数据；新增策略数据全部标为正优势。
4. 将新增数据与历史数据按固定比例混合，继续训练策略，再进入下一次采集。

完整系统同时改变了采集选择和策略训练目标。Figure 5 的最终差距包含基础 ACBC 初始化、后续定向采集和优势模型更新的共同效果。

## 贡献与结论对照

| 作者贡献 | 方法产物 | 对应证据 | 可支持的结论与范围 |
| --- | --- | --- | --- |
| 将人在环后训练移到 UMI | 当前策略并行推理，动作不执行；按分歧选择示范 | Figure 2、Section III-A、Franka 评估 | 在本文设备与任务上可进行不依赖机器人执行的数据采集 |
| 实时策略 OOD 检测与优势迭代 | ES 触发策略数据，低进度预测触发优势数据，随后 ACBC | Equations 2–17、Table III | 组合优于常规 SFT；阈值存在覆盖与选择性权衡 |
| 四任务验证与采集效率比较 | 长时程和精细操作、三次后训练更新 | Figures 5–6、Table IV | TPS 与相对 HG-DAgger 的采集效率改善；分布式多人采集仍是未来工作 |

## 结构地图

| 原文章节 | 本节解决的问题 | 阅读重点 |
| --- | --- | --- |
| I. Introduction | 为什么更多普通示范仍难以得到可靠部署策略 | 静态覆盖与示范效用是两项不同缺口 |
| II-A. VLA Post-Training and Interactive Policy Improvement | 现有纠错信号从哪里来 | 离线筛选与真实机器人交互的区别 |
| II-B. Robot-Free Data Collection with UMI | UMI 已经解决什么 | 便携采集与感知质量不等于策略薄弱点发现 |
| II-C. UMI-Based Human-in-the-Loop Post-Training | 与已有 UMI 闭环方案如何区分 | 当前策略条件的反馈与片段效用建模 |
| III. Method；III-A/B/C | 两条采集流程怎样连接到更新 | ES、相对进度标签、新旧数据混合、二值提示 |
| IV-A/B. Hardware Setup / Real-world Experiments | 系统怎样运行，效果怎样评估 | 30 Hz、推理延迟、固定数据量、10 次试验、TPS |
| IV-C/D/E. Ablations / Time Efficiency / HG-DAgger | 组件、阈值与采集成本是否值得 | 初始策略差异、阈值表、每保留帧成本 |
| V. Conclusion；Acknowledgment | 当前结论与下一步方向 | 分布式采集尚未被本实验验证；无独立局限或附录章节 |

## I. Introduction：后训练同时面对覆盖与效用

大规模预训练提供可复用操作技能，但目标机器人、观察角度、工作空间、动力学和精度要求都可能改变。长时程任务中，局部小误差会累积；精细任务中，一次对齐错误就可能影响最终完成。因此，问题是如何用有限的新增示范适应具体部署条件。

作者先区分两项 SFT 缺陷。第一项是 covariate shift（协变量偏移），专家示范覆盖的状态不一定覆盖学习策略偏离之后的状态。第二项是示范效用差异，常规 BC 会同等学习推动任务、停滞或较差的行为。RECAP 等工作用真实机器人经验、专家纠正和优势条件训练同时回应这两项缺口，但采集依赖机器人执行与接管。

UMI 允许直接用手示范动作。本文在此基础上加入当前策略与进度模型的反馈，把采集从普通示范扩展为针对模型分歧的片段采集。这里仍保留一个假设：人类访问的情境及模型分歧，能够提供对机器人策略有用的修正。

**关键证据 / 图表 / 公式**：Figure 1 对照真实机器人 HG-DAgger 与手持 HIL-UMI；5.63× 来自 Clean Up Table 的每帧采集时间比，不能解释为四任务平均值。

![[papers/images/han2026hil-umi/teaser_page1.png|800]]

*Figure 1. Teaser.* 图中的效率主张对应后文的具体比较；图示本身没有证明多机器人、多地点或多人同时运行的扩展效果。

## II. Related Work：当前策略反馈是主要区分轴

### II-A. VLA Post-Training and Interactive Policy Improvement

GR-RL 使用离线强化学习估计进度并筛选示范，$\chi_0$ 使用阶段优势和模型组合处理异质数据。DAgger 在学习策略访问的状态上查询专家；HIL-SERL 结合真实机器人强化学习与人工介入；RECAP 使用示范、机器人自主经验和遥操作纠正。这一组工作的区别在于监督来自静态数据，还是来自模型实际执行后暴露的状态。

HIL-UMI 延续迭代采集与优势条件训练，但取消采集时的策略执行。因此它获得的是人类示范观测上的模型分歧，并未直接获得机器人被自身动作带到的状态。这个区别决定了它与 DAgger 的联系及适用边界。

### II-B. Robot-Free Data Collection with UMI

UMI、FastUMI、MV-UMI 和 HiFi-UMI 分别强调便携示教、硬件简化、第三人称视角和轨迹保真。作者认为，这些方案主要改善数据可用性和一般覆盖，采集反馈尚未直接针对当前策略预测。HIL-UMI 继续采用兼容机器人动作的手持表示，同时把模型预测加入采集决策。

### II-C. UMI-Based Human-in-the-Loop Post-Training

RoboPocket 显示策略预测轨迹，让人判断并纠正，但识别薄弱点主要依赖人类解释。EgoGuide 用数据集层面的视觉几何新颖性引导初始状态覆盖，反馈不依赖当前策略。本文用 ES 自动比较人类轨迹与策略分布，同时学习片段进度用于 ACBC。

**关键证据 / 图表 / 公式**：Section II 的比较是机制层面的文献定位；实验只直接比较 SFT、去掉优势的变体和 HG-DAgger，没有与 RoboPocket、EgoGuide 或 HiFi-UMI 做同设备的定量比较。

## III. Method：两条采集流程与一个策略更新循环

### 初始化与更新顺序

任务指令为 $c$，基础数据 $\mathcal D_0=\{\tau_i\}_{i=1}^{M}$，一条轨迹是同步的观测和人类动作 $\tau_i=\{(o_{i,t},a_{i,t})\}_{t=0}^{L_i-1}$。先用进度标签训练 $f_{\psi_0}$，再为基础数据生成二值优势标签 $b$，得到基础策略。

$$
\theta_0=\arg\min_\theta\;\mathbb E_{(o,a,b)\sim\mathcal D_0}
\left[\ell_{\mathrm{BC}}\bigl(\pi_\theta(\cdot\mid o,c^b),a\bigr)\right].\tag{1}
$$

$c^b$ 是附加正或负标签的指令，$\ell_{\mathrm{BC}}$ 是策略原生动作预测损失。基础 HIL-UMI 策略已经使用 ACBC，因此不能默认其初始性能与普通 SFT 相同。

每次更新分别收集进度模型数据 $\mathcal D_r^A$ 与策略数据 $\mathcal D_r^P$，原文规定两者帧数相等。顺序是先用 $f_{\psi_{r-1}}$ 采集 $\mathcal D_r^A$，再用 $\pi_{\theta_{r-1}}$ 采集 $\mathcal D_r^P$；两种数据都采完后更新 $\psi_r$，最后继续 ACBC 得到 $\theta_r$。定义 $\mathcal D_0^P=\mathcal D_0$，$\mathcal D_0^A$ 是带进度标签的基础数据。

![[papers/images/han2026hil-umi/framework_page1.png|850]]

*Figure 2. Overview of HIL-UMI.* 框架图中两类 OOD 数据分别更新进度估计器和策略。它们不是同一批片段的两个名称，进度数据也没有在公式中直接并入策略训练集。

### III-A. Online Data Collection

本文将 OOD 定义为对应模型训练数据中覆盖不足的任务情境，通过预测与人类示范的不一致检测。它既不估计状态密度，也没有用带真值的 OOD 检测基准验证召回率或误报率。

#### III-A.1 Policy Data Collection：人类轨迹与策略分布的比较

在观测 $o_t$ 下，人类完成长度 $T$ 的动作片段 $H_t=(h_{t,1},\ldots,h_{t,T})$。策略在相同观测与指令下并行随机采样 $N=10$ 次，形成经验动作分布。

$$
A_t^{(n)}\sim\pi_{\theta_{r-1}}(\cdot\mid o_t,c),\qquad n=1,\ldots,N.\tag{2}
$$

策略采样与 UMI 采集同时进行，但必须等对应人类片段被观察到后才能比较。因而触发信号含有片段完成的等待时间，不能只用模型推理延迟解释端到端反馈速度。

动作 $a_k=(p_k,R_k,g_k)$ 包含末端位置、旋转和夹爪命令。在共同坐标系下定义片段距离，并对时间取平均。

$$
\rho^2(A,B)=\frac1T\sum_{k=1}^{T}\left[
\lambda_p\|p_k^A-p_k^B\|_2^2+
\lambda_R d_R(R_k^A,R_k^B)^2+
\lambda_g\|g_k^A-g_k^B\|_2^2\right].\tag{3}
$$

$$
d_R(R_1,R_2)=\arccos\left(\frac{\operatorname{tr}(R_1^\top R_2)-1}{2}\right).\tag{4}
$$

$d_R$ 是 $\mathrm{SO}(3)$ 上的旋转测地距离。实验权重为 $\lambda_p=0.5,\lambda_R=0.25,\lambda_g=0.25$。位置单位、夹爪幅度和旋转弧度会影响数值尺度，原文未给出动作归一化与共享阈值单位的完整细节。

$$
\operatorname{ES}(H_t)=\frac1N\sum_{n=1}^{N}\rho(A_t^{(n)},H_t)
-\frac{1}{2N(N-1)}\sum_{n\ne m}\rho(A_t^{(n)},A_t^{(m)}).\tag{5}
$$

第一项衡量策略样本到人类片段的距离。第二项扣除预测分布自身的分散，使评分同时考虑预测位置与分布范围。若所有样本都坍缩在远离示范的位置，第二项几乎为零，评分仍很高；若预测有多种合理模式，则不能只用平均动作与示范的距离评价。

ES 不要求高斯假设或显式似然，适用于基于流模型生成动作的策略。分散修正也不意味着任意增加方差都能降低评分，因为第一项会同时变化。本文用单个人类解决方案作为参考，因此高 ES 也可能来自有效策略与人类动作风格不同。

$$
\delta_t^P=\mathbb I[\operatorname{ES}(H_t)>\tau_P].\tag{6}
$$

$\tau_P$ 是各任务共享的策略阈值。已完成的片段超过阈值后，人类从当前状态继续记录专家示范，直到当前子任务完成；重复此过程得到 $\mathcal D_r^P$。这些状态来自人类示范流，策略预测没有改变物体位置，因此不能把它们等同于策略实际执行后的失败状态。

#### III-A.2 Advantage Data Collection：寻找进度估计的困难片段

在线进度模型比较当前帧与 $K$ 帧之前的观测。

$$
\widehat A_t^{\mathrm{online}}=f_{\psi_{r-1}}(o_{t-K},o_t,c),\quad
\delta_t^A=\mathbb I[\widehat A_t^{\mathrm{online}}<\tau_A],\qquad t\ge K.\tag{7}
$$

实验中 $K=50$，在 30 Hz 采集下对应约 1.67 秒。先用初始估计器在基础数据的固定 $K$ 间隔上计算预测，取最高 $\eta=0.3$ 比例的分界值 $\kappa_0$，设 $\tau_A=\kappa_0/2$。这一阈值按任务校准，用来适应不同任务的进度尺度。

这里假设人类示范正在推动任务。预测过低被解释为模型可能低估进度，触发后从当前状态录到子任务结束，形成 $\mathcal D_r^A$。如果人类本身在等待、调整或失败，低预测可能是正确判断，采集机制没有独立真值区分这些情形。

**关键证据 / 图表 / 公式**：Equations 2–7 给出两类触发器。策略流比较动作分布，优势流比较观测变化；高 ES 与低优势分别服务于不同模型。

### III-B. Advantage Model Training：用时间标签学习相对进度

估计器直接预测 $f_\psi(o_u,o_v,c)$，避免先独立估计两个状态值再相减。完整基础轨迹使用从 0 到 1 的线性时间标签。

$$
z_{i,t}=\frac{t}{L_i-1},\qquad
\overline L_0=\frac1M\sum_{i=1}^{M}L_i.\tag{8–9}
$$

新增片段在子任务结束时停止，未必包含完整任务。作者按片段长度与基础平均长度缩放其进度区间。

$$
z_{r,j,t}=\frac{t}{L_{r,j}-1}\frac{L_{r,j}}{\overline L_0},
\qquad t=0,\ldots,L_{r,j}-1.\tag{10}
$$

例如基础平均长度为 1,000 帧，新片段为 200 帧，该片段标签从 0 到 0.2。这个示例解释缩放方式，不是论文报告的轨迹长度。它避免把每个短片段都标成完整任务，但仍假设耗时可近似进度贡献；不同子任务难度、停顿和回退可能破坏该假设。若片段长于基础平均轨迹，终点标签也可能超过 1，公式没有说明裁剪方式。

从同一条轨迹或片段中均匀抽取两个不同帧，使用带符号标签 $y_{u,v}=z_v-z_u$，训练多个时间跨度。

$$
\mathcal L_A(\psi)=\mathbb E_{(o_u,o_v,y_{u,v})}
\left[(f_\psi(o_u,o_v,c)-y_{u,v})^2\right].\tag{11}
$$

反向帧对可以提供负目标，但标签仍由时间位置产生，没有对真实停滞、物体掉落或任务回退的显式标注。这里的 advantage 是作者使用的进度变化代理；论文没有通过 Bellman 方程学习 $Q-V$，也没有验证它是某个当前策略下的期望回报优势。

更新时通过固定混合比例保留历史数据。

$$
\operatorname{Mix}(\mathcal D_{\mathrm{new}},\mathcal D_{\mathrm{hist}})
=\alpha\operatorname{Unif}(\mathcal D_{\mathrm{new}})
+(1-\alpha)\operatorname{Unif}(\mathcal D_{\mathrm{hist}}),\tag{12}
$$

$$
\widetilde{\mathcal D}_r^A=\operatorname{Mix}\left(\mathcal D_r^A,\bigcup_{j<r}\mathcal D_j^A\right).\tag{13}
$$

$\alpha=0.5$ 使新增片段与累计历史各占一半采样概率。它不是将全部文件直接拼接后均匀采样；新增片段的权重不会随历史数据增长而被稀释。进度模型从 $\psi_{r-1}$ 继续训练得到 $\psi_r$，但原文没有报告估计误差曲线或独立进度预测测试集。

### III-C. Policy Update with ACBC：标签进入指令而非连续损失权重

策略使用同样的混合算子，历史集合含基础数据与过去新增策略数据。

$$
\widetilde{\mathcal D}_r^P=\operatorname{Mix}\left(\mathcal D_r^P,\bigcup_{j<r}\mathcal D_j^P\right).\tag{14}
$$

更新后的进度估计器在基础数据上预测固定未来间隔的变化，并以最高 $\eta$ 比例的分界 $\kappa_r$ 生成标签。

$$
\widehat A_{r,t}=f_{\psi_r}(o_t,o_{t+K},c),\qquad t+K<L.\tag{15}
$$

$$
b_{r,t}=\begin{cases}
\mathbb I[\widehat A_{r,t}\ge\kappa_r],&(o_t,a_t)\in\mathcal D_0,\\
1,&(o_t,a_t)\in\bigcup_{j=1}^{r}\mathcal D_j^P.
\end{cases}\tag{16}
$$

这一规则需要单独记住。基础数据每次依据新估计器重新划分正负；所有新增策略片段都直接标为正，包括此前更新中采集的片段。原文并未对每个新增片段使用预测优势进行筛选或连续加权。

$$
\mathcal L_{\mathrm{ACBC}}(\theta)=\mathbb E_{(o,a,b)\sim\widetilde{\mathcal D}_r^P}
\left[\ell_{\mathrm{BC}}\bigl(\pi_\theta(\cdot\mid o,c^b),a\bigr)\right].\tag{17}
$$

模型把正、负标签作为任务指令的一部分来学习两种条件行为；推理时只使用正优势指令。负标签样本仍参与训练，损失本身没有写成指数优势权重。论文没有给出标签的确切文本、进度模型结构、基础轨迹末尾不足 $K$ 帧的样本处理，以及采集时 Equation 2 的指令是否采用正标签的实现细节。

**关键证据 / 图表 / 公式**：Equations 8–17 连接进度监督与策略训练。读 Figure 2 时应同时核对 Equation 16，避免把所有数据都理解为进度模型逐帧打分后的训练样本。

## 方法细节：复现时需要保留的依赖关系

| 环节 | 输入 | 输出 | 决定下一步的条件 |
| --- | --- | --- | --- |
| 基础初始化 | 完整 UMI 轨迹、线性进度标签 | $f_{\psi_0}$、ACBC 基础策略 | 基础数据最高 30% 预测为正标签 |
| 进度数据采集 | 两帧观测、当前进度模型 | $\mathcal D_r^A$ | 预测低于任务校准阈值，录到子任务结束 |
| 策略数据采集 | 当前观测、人类片段、10 个策略样本 | $\mathcal D_r^P$ | ES 超过共享阈值，录到子任务结束 |
| 进度模型更新 | 新旧进度数据各占 50% | $f_{\psi_r}$ | 相对进度 MSE 继续优化 |
| 策略更新与推理 | 新旧策略数据、二值优势标签 | $\pi_{\theta_r}$ | ACBC 继续优化，推理选择正标签 |

两条采集流的目的不同，配额相同。固定 $K$ 用于在线判断和基础优势标注，训练进度估计器时则抽取多种帧间跨度。动作预测长度为 20，这与进度间隔 $K=50$ 是两个参数。

## IV. Experiments：实验设置、数据集、基线、指标

### IV-A. HIL-UMI Hardware Setup

手持设备通过定制连接件把 AgiBot OmniPicker 夹爪连接到 Meta Quest 3 控制器；头显与控制器追踪系统测量实时位姿。设备上装 Intel RealSense D405 采集腕部视角，固定 D455 提供第三人称视角。系统以 30 Hz 收集兼容机器人表示的动作和观测。

![[papers/images/han2026hil-umi/hardware_page1.png|800]]

*Figure 3. Hardware setup.* 设备同时记录人类动作和供模型推理的图像；本研究的硬件并非仅凭普通手机视频完成采集。

本地 NVIDIA RTX 4090D 工作站并行产生 10 个随机策略样本。策略 OOD 检测延迟为 112 ms，进度 OOD 检测为 93 ms，支持在线采集反馈。它们分别约相当于 3.36 和 2.79 个 30 Hz 帧周期；这说明模型反馈有延迟，不能将 30 Hz 记录频率解释为 30 Hz 检测频率。原文未报告训练用 GPU 数量、训练耗时或完整设备采购成本。

### IV-B. Real-world Experiments

#### IV-B.1 Real-world Tasks

全部评估使用单台 Franka Panda 机械臂。Fold Towel 与 Clean Up Table 是长时程任务；Stack Cube 与 Stamp 强调精细操作。

![[papers/images/han2026hil-umi/task-description_page1.png|850]]

*Figure 4. Real-world evaluation tasks.* 展示任务阶段与机器人工作台，证明评估确实涉及物理操作；四个任务不能代表跨本体或开放家庭环境的泛化。

#### IV-B.2 Evaluation Protocol

每个任务的每个策略 checkpoint 测试 10 次，在 $30\,\mathrm{cm}\times60\,\mathrm{cm}$ 工作区内改变物体初始位置。作者报告平均 TPS，按预定义子任务赋分。原文没有报告多随机种子、置信区间、显著性检验或评分者一致性。

| Table I：任务 | 得分项目 | 满分与扣分 |
| --- | --- | --- |
| Fold Towel | 铺平、第一次折叠、第二次折叠、放入篮子各 25 分 | 总分 100；每个子任务若有皱褶或错位扣 5 分 |
| Clean Up Table | 3 支笔进入对应颜色槽各 10；收好 3 个玩具各 10；正确打开两个抽屉各 10；正确关闭各 10 | 总分 100，包含 10 项动作 |
| Stack Cube | 抓住紫色方块 30；移到红色方块附近 30；叠到红色方块上 40 | 总分 100；只抓一个角扣 15 分 |
| Stamp | 抓取、移近标框、方向正确、接触纸面、印章本体在框内各 20 | 总分 100；框的长和宽均比印章本体大 1 cm |

TPS 允许任务未完成也得到较高分，不能把 TPS 96 写成成功率 96%。Stack Cube 和 Stamp 最终图示 TPS 100 接近该协议内全部评分项完成，但论文没有另行提供二值成功率表，也无法由其他平均分反推完整成功的试验数。

#### IV-B.3 Training Data and Comparisons

| 数据设置 | Fold Towel / Clean Up Table | Stack Cube / Stamp |
| --- | --- | --- |
| 基础示范数 | 每任务 50 条 | 每任务 80 条 |
| 每次后训练报告的新增帧量 | 12,000 帧 | 2,500 帧 |
| 更新次数 | Figure 5 的 Iter1–Iter3 | Figure 5 的 Iter1–Iter3 |
| 初始化模型 | 开源 $\pi_{0.5}$ | 开源 $\pi_{0.5}$ |

SFT 收集普通 UMI 示范再监督微调；完整 HIL-UMI 同时使用定向采集、进度模型迭代和 ACBC；去掉优势的 HIL-UMI 保留策略指导采集，改为混合数据上的普通微调。HG-DAgger 只在 Clean Up Table 上进行真实机器人比较。

原文没有明确新增帧数按单条采集流程计算，还是按两条流程合计。方法规定 $|\mathcal D_r^A|=|\mathcal D_r^P|$，实验又称每次新增数据量为 12,000 或 2,500 帧。后续引用同数据量结论时，应沿用作者所称的相同采集预算，并保留这一复现问题。

| Table II：实现参数 | 数值 |
| --- | --- |
| 输入图像 | $224\times224$ |
| Action horizon | 20 |
| Optimizer / schedule | AdamW / Cosine |
| 策略 / 进度模型学习率 | $1.0\times10^{-5}$ / $5.0\times10^{-5}$ |
| Warm-up / batch size | 500 steps / 128 |
| Weight decay / 每次更新步数 | $1.0\times10^{-10}$ / 5,000 |
| 随机策略样本 $N$ | 10 |
| $\lambda_p,\lambda_R,\lambda_g$ | 0.5、0.25、0.25 |
| 进度间隔 $K$ / 混合比例 $\alpha$ | 50 / 0.5 |
| 正优势比例 $\eta$ | 0.3 |

实验给出了训练超参数，但没有完整公开说明进度模型架构、各任务基础帧总数、片段长度分布及触发频次，也没有比较总体训练算力。

#### IV-B.4 Results and Analysis：主要结果

![[papers/images/han2026hil-umi/main_results_page1.png|1000]]

*Figure 5. Real-world Experiment Results.* 对比 Base 与三次更新后的 TPS，并在最右给出四任务均值。下表数值根据 Figure 5 的曲线估读，并非作者提供的原始统计表，均按近似值使用。

| 任务 | SFT：Base / Iter1 / Iter2 / Iter3 | 无优势：Base / Iter1 / Iter2 / Iter3 | 完整方法：Base / Iter1 / Iter2 / Iter3 |
| --- | --- | --- | --- |
| Fold Towel | ≈38 / 47 / 53 / 54 | ≈38 / 68 / 72 / 82 | ≈52 / 71 / 77 / 83 |
| Clean Up Table | ≈35 / 60 / 60 / 56 | ≈35 / 72 / 82 / 86 | ≈39 / 78 / 91 / 96 |
| Stack Cube | ≈48 / 49 / 52 / 64 | ≈48 / 72 / 78 / 90 | 84 / 86 / 90 / 100，与 Table III 一致 |
| Stamp | ≈56 / 56 / 54 / 58 | ≈56 / 82 / 82 / 94 | ≈74 / 89 / 96 / 100 |
| 四任务均值 | ≈44.25 / 53 / 54.75 / 58 | ≈44.25 / 73.5 / 78.5 / 88 | ≈62.25 / 81 / 88.5 / 94.75 |

完整方法的最终平均 TPS 比 SFT 高约 36.75 分，三次更新带来约 32.5 分净增加；SFT 从约 44.25 增至 58。去掉优势的变体也从约 44.25 增至 88，说明策略指导采集在这些实验中已有较大贡献。

优势模块的增益随任务不同。最终相对无优势变体的差值分别约为 1、10、10、6 分，均值约 6.75 分。Fold Towel 的最终差距较小，不能把四任务都概括为同等幅度的优势模块收益。

Base 时完整方法均值已高约 18 分，尤其 Stack Cube 为 84 对 48。最终优越性因而不能全部归因于后续三次采集。图没有误差条，每个 checkpoint 仅 10 次试验，应把结论表述为该协议下的观察结果。

### IV-C. Ablation Experiments：消融或对比

#### IV-C.1 Ablation on Advantage

作者移除进度模型，并把 ACBC 替换为混合数据上的普通微调。Figure 5 支持完整组合总体更好，但这项消融同时移除进度估计与条件训练，且 Base 性能不同。原文也没有单独说明去掉优势后两条采集流如何分配预算。它不能单独证明进度模型迭代、二值提示或基础初始化哪一项贡献最大。

#### IV-C.2 Ablation on Data Collection Thresholds

Stack Cube 固定另一个阈值，分别改变 $\tau_P$ 和 $\tau_A$。下面保留 Table III 的原始数值。

| $(\tau_P,\tau_A)$ | Base | Round 1 | Round 2 | Round 3 |
| --- | --- | --- | --- | --- |
| (1.2, 0.2) | 84 | **86** | **90** | **100** |
| (2.0, 0.2) | 84 | 76 | 86 | 96 |
| (0.5, 0.2) | 84 | 80 | 72 | 90 |
| (1.2, 0.3) | 84 | 76 | 82 | 96 |
| (1.2, 0.1) | 84 | 82 | 82 | 92 |

ES 触发条件是大于 $\tau_P$，所以较小 $\tau_P$ 更容易收集、较大阈值更严格。进度流触发条件是小于 $\tau_A$，方向相反，较大 $\tau_A$ 更容易触发。两者都存在冗余采集与遗漏有用片段的权衡。

选定设置最终达到 100，但阈值变化可导致中途下降，例如 $(0.5,0.2)$ 的 84、80、72、90。原文称所有测试设置优于 SFT，Figure 5 可供比较；该小表只覆盖一个任务、每次改变一个阈值，没有给出联合搜索或检测准确率。

### IV-D. Collection Time Efficiency Experiments

![[papers/images/han2026hil-umi/collection_time_efficiency_page1.png|850]]

*Figure 6. Collection-time efficiency and comparison with HG-DAgger.* (a) 横轴为累计平均采集时间，纵轴为四任务平均 TPS；(b) 是 Clean Up Table 的阶段比较。

| Table IV：任务 | SFT，ms/frame | HIL-UMI，ms/frame | HIL-UMI / SFT |
| --- | --- | --- | --- |
| Fold Towel | 69.43 | 91.92 | ≈1.32 |
| Clean Up Table | 41.70 | 73.40 | ≈1.76 |
| Stack Cube | 77.04 | 89.89 | ≈1.17 |
| Stamp | 64.30 | 101.02 | ≈1.57 |

最后一列是用原表计算的比值。HIL-UMI 在所有任务中每保留帧都比普通 UMI SFT 更慢，在线选择与寻找目标片段会增加采集开销。作者主张的是新增时间带来更多任务进展，Figure 6(a) 的曲线支持这种收益，而不是相对 SFT 的纯采集速度优势。

记录频率 30 Hz 对应约 33.3 ms/采样帧；表中更大的 ms/frame 说明该成本包含采集过程的额外时间，不能当作传感器周期或 GPU 推理延迟。原文没有给出操作者人数、各类等待和重置时间的详细分解。

### IV-E. Comparison with HG-DAgger

Clean Up Table 使用相同每阶段采集预算比较。Figure 6(b) 中 HG-DAgger 的 TPS 约为 35、75、80、91，HIL-UMI 约为 39、78、91、96。最终差距约 5 分，HIL-UMI 的基础 checkpoint 也已高约 4 分。

HG-DAgger 的采集成本是 412.99 ms/frame，HIL-UMI 是 73.40 ms/frame，$412.99/73.40\approx5.63$。这个比值衡量本任务每帧数据采集时间，不包含训练成本，也不是机器人执行任务的速度倍数。比较只覆盖一个任务，HG-DAgger 的其他实现细节和操作者差异没有充分展开。

## V. Conclusion 与 Acknowledgment

作者总结，手持 UMI 上的模型反馈能够支持迭代后训练，四任务 TPS 优于 SFT，并在 Clean Up Table 上获得优于 HG-DAgger 的 TPS 和更低采集时间。未来工作计划让多个操作者跨地点并发采集。现有实验支持当前系统原型，尚未测量分布式吞吐、异步模型更新或跨地点数据偏移。

Acknowledgment 列出北京自然科学基金与国家自然科学基金支持，以及讨论致谢。论文正文之后是参考文献，没有独立 Discussion、Limitations 或实验附录。

## 图表、公式与表格线索

| 位置 | 作用 | 回看时应核对什么 |
| --- | --- | --- |
| Figure 1 / Figure 2 | 采集方式对比与系统顺序 | 5.63× 的任务范围；两条采集流的先后与用途 |
| Figure 3 / Figure 4 | 设备和真实机器人任务 | 双视角、位姿追踪；单台 Franka 与工作区 |
| Figure 5 | 基础性能、三次迭代、优势消融 | Base 不相同；任务间收益不同；无误差条 |
| Figure 6 | 时间收益与 HG-DAgger 比较 | 横轴只统计采集时间；后者只评一个任务 |
| Table I / II | 评分与复现参数 | TPS 部分分、扣分；$K$ 与动作长度不同 |
| Table III / IV | 阈值与每帧成本 | 两类触发方向相反；HIL-UMI 比 SFT 每帧更慢 |
| Equations 1–7 | 初始化与检测 | 人类片段完成后比较；共同坐标与动作尺度 |
| Equations 8–13 | 进度标签与更新 | 时间代理、片段缩放、固定新旧混合 |
| Equations 14–17 | ACBC | 仅基础数据用预测阈值；新增策略数据全部正标签 |

完整图片清单见 [[papers/images/han2026hil-umi/index.md]]。

## 主张-证据-边界矩阵

| 主张 | 原文证据 | 证据含义 | 边界 |
| --- | --- | --- | --- |
| 不执行策略也可进行模型指导采集 | Section III-A、Figures 2–3 | 人类动作与预测可在同一观测流上比较 | 观测来自人类，不是策略执行后的状态分布 |
| ES 能定位有用的策略分歧 | Equations 3–6、定向采集消融、Table III | 基于预测分布与示范的评分可指导新增片段 | 无 OOD 真值或检测准确率；合理动作多样性也可能触发 |
| 进度模型与 ACBC 增加收益 | Equation 16、Figure 5 | 完整组合最终均值高于无优势约 6.75 分 | 同时移除多项组件；初始策略不同，缺少分项因果消融 |
| 四任务优于普通 SFT | Figure 5、10 次试验协议 | 在固定工作区、同源采集设备与任务中提高 TPS | 部分进度指标；不证明通用成功率或跨机器人泛化 |
| 比 HG-DAgger 采集效率更高 | Figure 6(b)、412.99 对 73.40 ms/frame | Clean Up Table 每保留帧采集约快 5.63× | 单任务；未计训练、设备采购和总系统成本 |
| 可以扩展到分布式人类数据 | Conclusion | 硬件便携与采集不占机器人提供设计可行性 | 多人多地点实验尚未开展 |

## 局限与可追问点

以下问题来自方法与证据范围，作者没有提供独立局限章节。

- **状态覆盖**：人类访问状态上的动作分歧是否能覆盖机器人真实执行错误后的接触、滑落和遮挡？需要将 UMI 选出的片段与真实 rollout 失败状态对齐比较。
- **时间进度代理**：线性时间标签怎样处理等待、动作回退、相同子任务不同速度？需要独立人工进度标签、排序准确率或估计误差评估。
- **新增数据全为正**：ES 高说明分歧大，不保证示范高效或可被机器人执行。需要对新增片段质量、正标签错误和跨本体可达性单独测试。
- **效用估计与策略目标**：进度模型只改变基础数据的正负划分。冻结进度模型、取消其独立采集、仅使用提示标签的分项消融，可以明确更新收益来自哪里。
- **预算与成本**：12,000 / 2,500 帧如何分配给两流，采集成本是否同时包含两流，需公开原始日志；还需统一训练算力与完整人工时间。
- **统计与评分**：只有 10 次试验，没有方差与失败轨迹分析。TPS 的部分分可能掩盖最终任务失败，适合补充成功率、完成时间和安全接管次数。
- **扩展性**：模型需要本地 RTX 4090D 推理，便携传感器不等于全部计算便携。跨操作者、任务、场景和机器人迁移以及分布式更新仍待验证。

## 与当前库的连接

| 库内文献 | 可比较的问题 | 本文提供的阅读角度 |
| --- | --- | --- |
| [[@intelligence2025pi06-vla-that-learns\|π*0.6 / RECAP]] | 纠错经验怎样进入优势条件策略 | HIL-UMI 把采集移到 UMI，却放弃了直接访问策略执行状态 |
| [[@luo2024precise-dexterous-robotic-manipulation\|HIL-SERL]]、[[@deng2026e2hil\|E2HiL]] | 真实机器人交互的成本与收益 | 比较人类示范分歧与真实失败纠正各自能提供的监督 |
| [[@murray2026flowdagger\|FlowDAgger]] | 当前策略与人类干预如何联系 | 重点核对状态由谁产生、采集反馈是否执行到机器人 |
| [[@kim2026ego-pi\|Ego-Pi]]、[[@liu2026last-hd\|LaST-HD]] | 人类数据怎样变成机器人可用监督 | UMI 提供显式位姿和夹爪动作，区别于仅从人类视频转移语义 |
| [[@zhao2026urvc\|UR-VC]]、[[@yu2026warp-rm\|WARP-RM]] | 进度代理与数据效用估计是否可靠 | 对照时间线性标签、相对进度学习、基础样本条件标注 |

这些连接用于组织后续比较；本文没有对这些库内工作逐项实验评测。分类对应 `cat/vla`、`cat/human-data`、`cat/data` 和 `cat/value-reward`。

## 精读路线 / 为什么需要回看

1. 若研究无机器人后训练，先读 Figure 2 与 III-A，明确模型仅推理、人类决定状态轨迹的采集方式。
2. 若复现 OOD 选择，回看 Equations 3–7 和 Table III，确认动作尺度、片段完成时机与两类阈值方向。
3. 若研究优势或奖励模型，重点读 Equations 8–17，区分时间进度代理、基础数据重标注和新增数据全正标签。
4. 若引用实验收益，同时核对 Figure 5 的 Base 差异、Table I 的 TPS 定义及每个 checkpoint 的 10 次试验。
5. 若引用 5.63×，回到 IV-E，保留 Clean Up Table、每帧采集成本与未计训练开销这三个条件。

本文最值得回看的问题是，能否用人类示范流上的模型分歧，在不执行策略的情况下收集对部署有用的纠错数据。现有结果支持这种采集与训练组合的可行性，后续研究需要进一步连接人类访问状态、进度代理质量与机器人真实失败分布。
