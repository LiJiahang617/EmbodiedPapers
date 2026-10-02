---
tags:
  - paper
status: read
aliases:
  - ERVLA
  - Embodied Reasoning VLA
  - "Revisiting Embodied Chain-of-Thought for Generalizable Robot Manipulation"
  - "ERVLA 具身推理 VLA"
year: 2026
title: "Revisiting Embodied Chain-of-Thought for Generalizable Robot Manipulation"
doi:
arxiv: "2606.03784"
url: "https://arxiv.org/abs/2606.03784"
venue: "arXiv preprint; NeurIPS 2026 preprint template"
venue_short: arXiv
pdf_url: "https://arxiv.org/pdf/2606.03784v2"
openalex:
metadata_source: "arXiv 2606.03784v2 and source package"
metadata_confidence: high
pdf: "[[papers/pdfs/sun2026revisiting-embodied-chain-thought.pdf]]"
reading: "[[papers/bilingual/sun2026revisiting-embodied-chain-thought_中英混读.md]]"
images: "papers/images/sun2026revisiting-embodied-chain-thought/"
image_index: "[[papers/images/sun2026revisiting-embodied-chain-thought/index.md]]"
map_axis: "具身智能/VLA/具身CoT表征监督"
map_brief: "ERVLA 把具身 CoT 由测试时必经前缀改为训练期表征监督，并用 reasoning dropout、choice policy 与 knowledge-truncated KV 条件将语义推理接到连续动作生成。"
map_role: "用于比较显式、潜式与训练期具身推理接口，也提供 CoT 污染和推理数据缩放失效的系统消融。"
authors:
  - "[[Nan Sun]]"
  - "[[Yuan Zhang]]"
  - "[[Yongkun Yang]]"
  - "[[Wentao Zhao]]"
  - "[[Peiyan Li]]"
  - "[[Jun Guo]]"
  - "[[Wenxuan Song]]"
  - "[[Pengxiang Ding]]"
  - "[[Runze Suo]]"
  - "[[Yifei Su]]"
  - "[[Xin Xiao]]"
  - "[[Xinghang Li]]"
  - "[[Huaping Liu]]"
institutions:
  - "[[Tsinghua University]]"
  - "[[Xiaomi Robotics]]"
  - "[[Peking University]]"
  - "[[CASIA]]"
  - "[[HKUST(GZ)]]"
  - "[[Zhejiang University]]"
  - "[[Fudan University]]"
  - "[[Wuhan University]]"
  - "[[Shanghai Innovation Institute]]"
topics:
  - vision-language-action
  - embodied chain-of-thought
  - embodied reasoning
  - representation shaping
  - reasoning dropout
  - CoT contamination
  - choice policy
  - knowledge truncation
  - diffusion transformer
  - flow matching
  - robot manipulation
---

# Revisiting Embodied Chain-of-Thought for Generalizable Robot Manipulation

- [x] PDF:: [[papers/pdfs/sun2026revisiting-embodied-chain-thought.pdf]]
- [x] 元数据:: source=arXiv 2606.03784v2 and source package, confidence=high
- [x] 精读稿:: [[papers/bilingual/sun2026revisiting-embodied-chain-thought_中英混读.md]]
- [x] 图片索引:: [[papers/images/sun2026revisiting-embodied-chain-thought/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [x] 阅读状态:: read

related:: [[@liu2026last0-latent-spatio-temporal]] · [[@liu2026last-hd]] · [[@li2026zr0]] · [[@zhong2025action-tokenization-survey]] · [[@intelligence2025pi06-vla-that-learns]]
affiliation:: [[Tsinghua University]] · [[Xiaomi Robotics]] · [[Peking University]] · [[CASIA]] · [[HKUST(GZ)]] · [[Zhejiang University]] · [[Fudan University]] · [[Wuhan University]] · [[Shanghai Innovation Institute]]

> [!warning] 版本与开放状态
> 本笔记按 arXiv 2606.03784v2 与同版本源码整理。TeX 使用 NeurIPS 2026 preprint 模板，论文没有在正文中声明已录用。作者写明代码、数据和权重将公开，但截至 2026-08-20，公开项目仓库只有项目页、论文和展示资源，没有训练代码、数据集或模型检查点。

## Abstract

Embodied chain-of-thought (CoT) aims to bridge linguistic reasoning and robotic control, but its effective form and integration strategy remain underexplored. In this paper, we revisit embodied CoT for vision-language-action (VLA) models at large scale. We construct the largest embodied CoT corpus to date, comprising 978,743 trajectories, 226.3M samples, and 2592.5 hours of robot data. Through extensive experiments, we find that effective embodied CoT should ground high-level semantic understanding into concrete action guidance, such as end-effector movement descriptions and image-space trajectories, while high-level reasoning alone brings only marginal gains. We further show that explicit CoT does not scale reliably when used as an autoregressive action prefix, as it suffers from compounding inference errors and unstable reasoning-action coupling. To address these limitations, we propose ERVLA, a VLA model that uses embodied CoT as representation-shaping supervision rather than mandatory test-time reasoning. ERVLA is trained with a reasoning-dropout strategy, enabling the model to absorb rich reasoning traces during training while predicting actions directly without CoT decoding during inference. This design improves scalability with increasing pre-training data and avoids autoregressive instability. ERVLA achieves state-of-the-art performance on LIBERO-Plus with an 86.9% success rate and reaches 53.2% success rate on VLABench, demonstrating strong out-of-distribution generalization. In real-robot experiments, ERVLA further outperforms competitive state-of-the-art baselines, especially on tasks requiring semantic disambiguation and long-horizon execution.

## 一句话定位

ERVLA 重新回答了具身 CoT 应该放在哪里。作者先用 978,743 条轨迹证明高层解释若接不到动作会失效，再把 CoT 从测试时必须生成的动作前缀改成训练期表征监督，由 reasoning dropout、choice policy、knowledge truncation 和 DiT 连成可扩展的推理到动作接口。

## 方法 / 对象

- 数据来自 AgiBot World、DROID、Fractal、BridgeData V2 与 MolmoAct，共 226.3M 帧级样本和 2592.5 小时，覆盖单臂、双臂、单视角与多视角。
- ECoT 字段分为 Understanding、Grounding、Planning 与 Acting。Acting 里的 movement description 和 image-space point trajectory 对动作学习最直接。
- Qwen3-VL-4B 负责图像、指令、可选 CoT 与机器人状态。choice policy 从查询 token 预测 5 个候选动作块及其误差分数。
- 36 层 DiT 用 flow matching 生成连续动作。knowledge truncation 只向 DiT 暴露语义前缀的逐层 KV cache，不让它偷看训练期控制查询 token。
- reasoning dropout 以 0.5 概率在 /cot 与 /no_cot 之间切换。部署时不必解码 CoT，动作损失仍可反向更新 VLM。

## 证据

| 证据 | ERVLA 结果 | 关键对照 | 阅读边界 |
| --- | ---: | ---: | --- |
| LIBERO-Plus 总成功率 | 86.9 | π0.5 为 85.5 | 只高 1.4 个点，且若干子项仍落后 |
| VLABench 平均 SR / PS / IS | 53.2 / 65.9 / 70.4 | π0.5 为 48.1 / 62.3 / 64.9 | commonsense 的 PS 与 IS 不占优 |
| 真机平均 SR / PS | 55 / 67 | π0.5 为 53 / 60 | 每方法 20 个任务各 5 次，共 100 次 |
| 真机 Semantic SR / PS | 42 / 58 | π0.5 为 31 / 45 | 主要收益来自语义消歧 |
| 真机 Long-horizon SR / PS | 38 / 55 | π0.5 为 35 / 38 | 完整成功率只多 3 点，过程分提升更大 |
| CoT 字段直接训练 | full ECoT 相对基线 +8.2 | movement +4.1，point trajectory +4.8 | 使用固定 AR CoT+FAST 接口 |
| CoT 污染 | gripper -5.6，box -6.1 | dropout 后收窄到 -0.8 与 -1.0 | 噪声来自大规模自动标注，不是概念本身无效 |

## 局限

- 论文把训练数据称为迄今最大具身 CoT 语料，但代码、标注产物与权重仍未公开，数据清洗和自动标注误差无法外部审计。
- LIBERO-Plus 的总分领先 π0.5 只有 1.4 个点。Object、Goal、Robot、Light、Background 与 Layout 等子项并非全胜，SOTA 不能读成全面碾压。
- VLABench 的 commonsense 结果有明显混合信号。ERVLA 的 SR 略高，PS 与 IS 却低于 π0.5。
- 真机只覆盖抽屉收纳和桌面清理两族任务，场景由十小时同分布示范适配。每种方法 100 次 rollout 足以比较当前设置，不能外推到开放家庭环境。
- reasoning dropout 缓解 CoT 污染，但没有显式建模每个标注字段的不确定度，也没有解释何时应在执行中重新开启显式推理。
- 训练规模曲线主要来自图，没有公开每个缩放点的完整数值、计算量和随机种子方差。

## 我的阅读笔记

这篇最有分量的部分不是又做了一个更强 VLA，而是把具身推理拆成信号内容、耦合接口和数据规模三个问题。高层 goal 与 planning 单独用会掉点，movement 和 point trajectory 才把语义落到控制上，这组受控消融把「推理越多越好」直接否掉了。

说到底，ERVLA 的推理并没有消失。它从部署时可见的文字序列搬到了训练后的隐藏状态和 KV memory。这样做省掉了自回归前缀的延迟与误差传播，也牺牲了逐步解释的可观察性。与 [[@liu2026last0-latent-spatio-temporal|LaST₀]] 对照时，一个把推理压进时空潜变量，一个把显式 CoT 当训练脚手架，两者都在回避逐 token 边说边做。

值得画出来的是 CoT contamination。坐标监督比语言更接近动作，却也更怕 detector jitter 和 calibration bias。作者用稀疏标注、几何投影与 dropout 补救，已经说到点子上了，但还没有把置信度写进损失。若后续版本能按字段、视角和时间动态调权，这条线会比继续拉长 CoT 更有研究价值。

~~~dataviewjs
const {Research} = customJS
Research.topic(dv)
~~~
