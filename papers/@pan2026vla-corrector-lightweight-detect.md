---
tags:
  - paper
  - cat/vla
  - cat/test-time
status: read
aliases:
  - "VLA-Corrector: Lightweight Detect-and-Correct Inference for Adaptive Action Horizon"
year: 2026
title: "VLA-Corrector: Lightweight Detect-and-Correct Inference for Adaptive Action Horizon"
doi: 
arxiv: "2607.01804v1"
url: "https://arxiv.org/abs/2607.01804"
venue: 
openalex: 
metadata_source: arxiv
metadata_confidence: high
reading_mode: full-close-reading
updated: 2026-10-02
pdf: "[[papers/pdfs/pan2026vla-corrector-lightweight-detect.pdf]]"
reading: "[[papers/bilingual/pan2026vla-corrector-lightweight-detect_中英混读.md]]"
images: "papers/images/pan2026vla-corrector-lightweight-detect/"
image_index: "[[papers/images/pan2026vla-corrector-lightweight-detect/index.md]]"
authors:
  - "[[Yi Pan]]"
  - "[[Miao Pan]]"
  - "[[Qi Lu]]"
  - "[[Jiaming Huang]]"
  - "[[Man Zhang]]"
  - "[[Siteng Huang]]"
  - "[[Xin Li]]"
  - "[[Jie Zhang]]"
  - "[[Yongliang Shen]]"
  - "[[Xuhong Zhang]]"
  - "[[Wenqi Zhang]]"
institutions:
topics:
---

# VLA-Corrector: Lightweight Detect-and-Correct Inference for Adaptive Action Horizon

- [x] PDF:: [[papers/pdfs/pan2026vla-corrector-lightweight-detect.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/pan2026vla-corrector-lightweight-detect_中英混读.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，`#map/具身智能/VLA/推理期检测纠正与自适应动作时域`
- [x] 阅读状态:: read

related:: [[@yu2026wm-dagger]], [[@xiao2026enpire]], [[@deng2026e2hil]], [[@kang2026x-tokenizer]]
affiliation:: [[Zhejiang University]], [[Alibaba DAMO Academy]]

## Abstract

Vision-Language-Action (VLA) foundation models have recently achieved strong progress in embodied intelligence. To reduce policy-call frequency while preserving temporal coherence, most generative policies adopt an action chunk mechanism, executing multiple future actions in an open-loop manner under a fixed action horizon. However, this "predict-then-blindly-execute" paradigm sacrifices closed-loop reactivity: in contact-rich physical interactions, even small local perturbations can rapidly amplify within the open-loop blind spot, leading to compounding errors and ultimately task failure. To address this limitation, we propose VLA-Corrector, a lightweight corrective inference framework for action-chunked VLA policies. Without modifying the backbone policy weights, VLA-Corrector introduces a lightweight Latent-space Vision Monitor (LVM) that continuously compares predicted and actual visual feature evolution, enabling online detection of visual dynamics deviations. Once persistent deviation is detected, the system triggers a truncation event, discards the remaining stale actions, and invokes corrective replanning via Online Gradient Guidance (OGG). The detect-and-correct mechanism of VLA-Corrector naturally induces an event-triggered adaptive action horizon: it preserves long-horizon execution when the current chunk remains reliable, and invokes short-horizon corrective replanning when execution begins to drift. In doing so, VLA-Corrector mitigates the trade-off imposed by static horizons between execution robustness and policy-call frequency. It can be integrated into different VLA models without further retraining the VLA backbone, interrupting compounding errors while preserving much of the efficiency benefit of action chunking and substantially improving robustness in long-horizon, contact-rich robotic manipulation tasks.

## 一句话定位

作者提出 VLA-Corrector，为 action-chunked VLA 增加视觉潜动态检测、事件触发截断和 Online Gradient Guidance（在线梯度引导），在执行发生漂移时提前重规划。骨干在接入纠正模块后保持冻结，外置约 40M 的动力学校正器仍需用示范训练；方法改善的是鲁棒性与每次策略调用的效率，附录同时报告了额外推理耗时。

## 方法 / 对象

- 对象是固定 action horizon（动作执行时域）的生成式 VLA，实验覆盖 π0.5、SmolVLA 和 X-VLA。
- 先取得已微调的 VLA，再冻结视觉编码器与策略，用示范训练残差 MLP `M_φ`，预测短程潜表示变化 `ΔZ`。
- Latent-space Vision Monitor（潜空间视觉监视器，LVM）以预测残差与观测残差的 cosine mismatch（余弦不一致）构造 `E_t`，用滑窗 MAD、双阈值和持续计数触发中断。
- 中断后丢弃当前队列剩余动作，使实际 horizon 从上限 `H` 缩短为 `h<H`；仅下一次策略调用启用 OGG，将候选动作的潜效果引向 `ΔZ_corr=ΔZ_exp−ΔZ_dev`。
- OGG 对 flow-matching velocity（流匹配速度场）求梯度，不更新骨干权重。全部公式及变量解释见完整精读稿的公式检索表。

## 证据

| 实验 | 对照及结果 | 解释范围 |
| --- | --- | --- |
| MetaWorld 跨骨干，Table 1 | π0.5 48.70%→64.35%，SmolVLA 61.90%→66.65%，X-VLA 55.55%→59.60% | 分别提高 15.65、4.75、4.05 个百分点；收益并非随任务难度严格递增。 |
| 同 horizon 对照，Table 4 | π0.5 的 `H=50` 为 48.72%/5.15 calls→58.70%/4.98 calls | 成功率提高 9.98 个百分点，success-per-call 相对提高 24.6%；不能把 Table 1 的 64.35% 移到此设置。 |
| LIBERO，Table 2 | Few-shot π0.5 94.00%→97.80%；Full fine-tuning 为 96.95% | 相对 few-shot 提高 3.80 个百分点，超过全量微调 0.85 个百分点；并非无示范训练。 |
| 组件，Table 6 | 48.70%→仅截断 60.35%→截断与 OGG 64.35% | 截断贡献 11.65 个百分点，OGG 再增加平均 4.00 个百分点；Hard 子集从 50.0% 降至 47.5%。 |
| 机理，Figure 6/7 | 83.7% 截断发生于人工标注的关键相位；OGG 平均恢复率增加 0.23 | 前者是事件占比，未按相位时长归一化；后者以中断后 10 步内 `E_t<T_off` 定义恢复。 |
| AgileX PiPER，Table 5 | 平均 55.6%→73.3%，扰动组 40.0%→68.3% | 分别提高 17.7、28.3 个百分点；9 个任务，每任务每方法 20 次。 |

## 局限

检测依赖 RGB 视觉特征与局部残差方向，视觉歧义、力觉缺失及骨干未能表示的恢复动作仍会导致失败。跨域校正器只取得有限改善，域匹配示范仍重要。

success-per-call（成功率除以平均调用次数）不等同于执行速度。附录 Table 11 的比较是同一推理流程关闭与开启 OGG：平均每 episode 推理耗时 2.06→3.38 秒，约 1.64×；标准单次 chunk 推理 278.01 ms，OGG 恢复调用 588.52 ms，约 2.12×，也不等同于整任务完成时间。

主文与附录对数据划分、持续计数和部署训练损失的描述存在差异。完整精读稿保留了这些差异，以及 Figure 1–12、Table 1–15、公式变量和可追问点。

## 我的阅读笔记

回看时优先对照 Table 4 和 Table 6，区分提前截断与 OGG 的收益，再结合 Table 11–13 判断推理成本。success-per-call 的提高需要与实际耗时分开评价。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
