---
tags:
  - paper
status: read
aliases:
  - FlowDAgger
  - "FlowDAgger: Human-in-the-Loop Adaptation of Generative Robot Policies in Latent Space"
  - "FlowDAgger 潜空间人在环适配"
year: 2026
title: "FlowDAgger: Human-in-the-Loop Adaptation of Generative Robot Policies in Latent Space"
doi:
arxiv: "2607.08877"
url: "https://arxiv.org/abs/2607.08877"
venue: "arXiv preprint; CoRL-style template"
venue_short: arXiv
pdf_url: "https://arxiv.org/pdf/2607.08877v1"
code: "https://github.com/microsoft/FlowDAgger"
project: "https://microsoft.github.io/FlowDAgger"
openalex:
metadata_source: "arXiv 2607.08877v1 and source package"
metadata_confidence: high
pdf: "[[papers/pdfs/murray2026flowdagger.pdf]]"
reading: "[[papers/bilingual/murray2026flowdagger_中英混读.md]]"
images: "papers/images/murray2026flowdagger/"
image_index: "[[papers/images/murray2026flowdagger/index.md]]"
map_axis: "具身智能/VLA/人类干预与潜空间策略适配"
map_brief: "用 action inversion 把人类纠正动作反演回冻结生成式策略的噪声空间，只训一个轻量 noise policy 去操纵基座，权重完全不动。"
map_role: "研究人在环纠正应该写进模型哪一层的入口，也提供少步 flow 动作头必须用逐步不动点反演的量化证据。"
authors:
  - "[[Michael Murray]]"
  - "[[Daphne Chen]]"
  - "[[Simran Bagaria]]"
  - "[[Dean Fortier]]"
  - "[[Tess Hellebrekers]]"
  - "[[Galen Mullins]]"
  - "[[Harshavardhan Gajarla]]"
  - "[[Oier Mees]]"
  - "[[Maya Cakmak]]"
  - "[[Andrey Kolobov]]"
institutions:
  - "[[Microsoft Research]]"
  - "[[Microsoft]]"
  - "[[ETH Zurich]]"
  - "[[University of Washington]]"
topics:
  - human-in-the-loop
  - interactive imitation learning
  - DAgger
  - flow matching
  - diffusion policy
  - latent space adaptation
  - action inversion
  - world-action model
  - vision-language-action
  - catastrophic forgetting
  - robot manipulation
---

# FlowDAgger: Human-in-the-Loop Adaptation of Generative Robot Policies in Latent Space

- [x] PDF:: [[papers/pdfs/murray2026flowdagger.pdf]]
- [x] 元数据:: source=arXiv 2607.08877v1 and source package, confidence=high
- [x] 代码:: [microsoft/FlowDAgger](https://github.com/microsoft/FlowDAgger)
- [x] 精读稿:: [[papers/bilingual/murray2026flowdagger_中英混读.md]]
- [x] 图片索引:: [[papers/images/murray2026flowdagger/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [x] 阅读状态:: read

related:: [[@yu2026wm-dagger]] · [[@luo2024precise-dexterous-robotic-manipulation]] · [[@deng2026e2hil]] · [[@xiao2026rove]] · [[@liu2026checkvla]]
affiliation:: [[Microsoft Research]] · [[Microsoft]] · [[ETH Zurich]] · [[University of Washington]]

> [!warning] 版本与开放状态
> 本笔记按 arXiv 2607.08877v1 与同版本源码整理，TeX 使用 CoRL 风格模板，正文没有声明录用状态。项目页是 microsoft.github.io/FlowDAgger，截至 2026-09-05 公开仓库已建但仍以介绍为主，没有训练代码与检查点。仿真结果报 3 seeds、每点 25 rollouts，真机报 30 rollouts 但不报 seed，附录两个补充实验只跑单 seed。

## Abstract

Pretrained generative robot policies based on flow matching and diffusion have achieved impressive results across a wide range of manipulation tasks. Yet real-world deployments routinely expose failure modes outside the pretraining distribution. Closing these gaps typically requires large-scale data collection or online reinforcement learning on physical hardware, which is impractical for rapid and safe adaptation. We present FlowDAgger, a sample- and compute-efficient method for adapting frozen generative robot policies from human interventions in latent space. Our key idea is action inversion: each human expert action is mapped to the noise that would have produced it under the frozen base policy, using reverse-time integration followed by local refinement. The resulting inverted noise provides supervision for a lightweight latent policy that steers the base model at deployment time, enabling rapid skill acquisition while preserving its behavioral priors. We evaluate FlowDAgger in simulation and on real-world bimanual and single-arm manipulation, adapting both action-head VLAs and world-action models from a handful of interventions. FlowDAgger outperforms supervised fine-tuning and latent-space RL baselines and preserves pretrained skills on held-out tasks, offering a practical path for adapting robot foundation models in the real world.

## 一句话定位

FlowDAgger 回答的是人类纠正该写进模型哪一层。作者把纠正动作反演成「本该被抽到的那个噪声」，用它监督一个轻量 noise policy 去操纵冻结基座，从而在同一批纠正下拿到比权重微调和动作残差更大的收益，且几乎不损失预训练技能。

## 方法 / 对象

- 适配面是噪声空间。观测固定后基座是确定性映射，动作分布完全由噪声分布决定，所以替换标准抽样就能改行为而不动参数。
- Action inversion 逐步反演 Euler 递推，每步解隐式方程 $x_k = x_{k+1} - \Delta t\, v_\theta(x_k, t_k, s)$，用不动点迭代（默认 $M=5$）求解，收敛条件是 $\Delta t L < 1$。
- 少步动作头（$K\approx 10$，$\Delta t = 0.1$）必须逐步反演。轨迹级方法校正的是无法归因到单步的全局残差，在这个 regime 下消不掉。
- WAM 分支反演整个联合过程。Cosmos-Policy 的联合潜张量是 $16\times 9\times 28\times 28$，目标用 minimal-delta swap 构造，只在动作帧加专家减基座的差。EDM 调度的终端去噪用短 Adam 求解。
- Noise policy 是观测编码器加 MLP，部署时确定性输出，训练是纯 L2 回归。高维联合噪声用 64 维 PCA 基回归。
- 双缓冲区防过拟合。反演纠正进 intervention buffer，成功自主 rollout 用过的噪声进第二个 buffer，每 batch 等比例抽。

## 证据

| 证据 | FlowDAgger 结果 | 关键对照 | 阅读边界 |
| --- | ---: | ---: | --- |
| MetaWorld 12 任务平均 SR | 0.78（+0.25） | SFT 0.71，LoRA-DAg 0.68，Res-DAg 0.64，DSRL 0.55 | 3 seeds 平均，无每格方差，Door Lock 反向 |
| 跨基座族均值 | $\pi_{0.5}$ +0.26，Cosmos-Policy +0.21 | 两个 Base 均值同为 0.53 | 7 个共享任务，每族一个代表模型 |
| 留出任务先验保持 | −0.08 | Res-DAg −0.27，LoRA-DAg −0.66，SFT −0.94 | 留出集 5 个近饱和任务，Push 从 0.96 掉到 0.56 |
| 真机 8 任务 | 全部改善，+0.10 到 +0.67 | 只对照 base 与 SFT | 30 rollouts，无 seed，干预 5 到 20 episode |
| 反演精度 | Action MSE 0.00168 | Euler reverse 0.0329，Trajectory FP 0.0228 | 只在 assembly 上测 |
| 反演精度的下游后果 | Assembly SR 0.87 | Euler-reverse 监督只有 0.59，低于基座 0.64 | 说明不准的反演在腐蚀而非引导 |
| 适配显存 | 约 8 GB | 与部署 $\pi_{0.5}$ 同量级 | 只测 Assembly 一个任务 |
| Gr00t N1.7 / diffusion policy | 分别逼近 100% 与约 97% | DSRL 停在约 70% 与约 80% | 单 seed，每点 15 rollouts |

## 局限

- 适配能力被基座支撑集限住，想要的行为若远在动作流形之外，反演只能恢复最接近的可表示行为。论文没有构造这样的反例任务。
- 只有给了纠正的状态区域才会改善，纠正里的系统性偏差会被原样学进适配策略。
- 高度多模态动作分布或条件很差的生成动力学会降低反演精度，论文只有 Euler-reverse 一行作为间接证据。
- 全文没有画「成功率对干预次数」的曲线，Figure 3 的横轴是 episode 而不是干预次数，两者在 human-gated 设定下不等价。
- 双缓冲区的等比例采样是唯一防过拟合手段，比例、自主 buffer 只收成功 rollout 的选择偏差都没有消融。
- 真机缺 Residual-DAgger、LoRA-DAgger 与 DSRL 三组对照，而真机恰恰是保先验最值钱的场景。
- 收敛条件 $\Delta t L<1$ 没有实测任何基座的 Lipschitz 常数，也没报不动点迭代的失败率。
- WAM 分支只在 7 个 MetaWorld 任务上验证，没上真机，Basis 与 Full 的对照只有定性一句话。

## 我的阅读笔记

这篇真正的贡献是把「适配接口」当成研究对象。同一批纠正，写进权重、写进动作残差、写进噪声，得到 +0.15、+0.11、+0.25 三个结果，留出任务的代价则是 −0.66、−0.27、−0.08。这组对照比任何单点 SOTA 都更有长期价值。

Table 5 比主表更能说服人。它把反演精度这个中间量与下游成功率直接连起来，还给了反向案例，Euler-reverse 的监督把 Assembly 压到 0.59，低于什么都不做的 0.64。有这条因果链，action inversion 才不只是一个技巧，而是一个可以被独立检验的组件。

隐忧在支撑集这条边界上。Toolbox Packing 从 13% 到 80% 之所以成立，是因为正确行为本来就在 $\pi_{0.5}$ 的流形上，只是被错误的噪声抽样掩盖。遇到基座压根没学过的技能，这套机制给不出增益。

和 [[@yu2026wm-dagger|WM-DAgger]] 对读最有意思。两者都在补 DAgger 的数据，一个用世界模型合成 recovery 轨迹，一个把真实人类纠正反演回噪声。前者省人力但要承担误监督风险，后者每条监督都是真的但要人在环。选哪条取决于瓶颈是人还是数据质量。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
