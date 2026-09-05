---
tags:
  - paper
  - cat/wam
  - cat/vla
status: unread
aliases:
  - JEPA-WAM
  - "JEPA-WAM: Learning Vision-Language-Action Policies with Joint-Embedding World Modeling"
year: 2026
title: "JEPA-WAM: Learning Vision-Language-Action Policies with Joint-Embedding World Modeling"
doi: "10.48550/arXiv.2608.09381"
arxiv: "2608.09381v1"
url: "https://arxiv.org/abs/2608.09381"
venue: "arXiv preprint"
venue_short: "arXiv"
arxiv_url: "https://arxiv.org/abs/2608.09381"
arxiv_doi: "10.48550/arXiv.2608.09381"
pdf_url: "https://arxiv.org/pdf/2608.09381v1"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/lin2026jepa-wam.pdf]]"
reading: "[[papers/bilingual/lin2026jepa-wam_中英混读.md]]"
images: "papers/images/lin2026jepa-wam/"
image_index: "[[papers/images/lin2026jepa-wam/index.md]]"
map_axis: "世界模型/WAM/潜空间联合嵌入预测"
map_brief: "在冻结 V-JEPA 空间里建潜空间 WAM，预测目标是联合编码当前帧与未来帧的 patch 级转移表示，转移预测与动作生成共享同一个 Qwen2.5-0.5B 预测器，部署时预测分支整个摘掉，LIBERO-Plus 无预训练组第一（79.2），同一监督加到 π0.5 上全场第一（86.3）。"
map_role: "潜空间 WAM 的目标构造与监督位置这两个设计问题的参考答案，也是给现成 VLA 加世界建模辅助监督的现成配方。"
authors:
  - "[[Yihan Lin]]"
  - "[[Jiawei He]]"
  - "[[Shifeng Bao]]"
  - "[[Chen Zhao]]"
  - "[[Yang Li]]"
  - "[[Xiaobo Wang]]"
  - "[[Yan Wang]]"
  - "[[Cheng Chi]]"
  - "[[Jing Zhang]]"
institutions:
  - "[[Renmin University of China]]"
  - "[[XYZ Embodied AI]]"
  - "[[Shenzhen University of Advanced Technology]]"
  - "[[Tsinghua University]]"
topics:
  - latent world action model
  - V-JEPA
  - joint-embedding prediction
  - transition target
  - shared predictor
  - flow matching
  - LIBERO-Plus
  - RoboTwin
  - OOD generalization
  - auxiliary supervision
---

# JEPA-WAM: Learning Vision-Language-Action Policies with Joint-Embedding World Modeling

- [x] PDF:: [[papers/pdfs/lin2026jepa-wam.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/lin2026jepa-wam_中英混读.md]]
- [x] 图片索引:: [[papers/images/lin2026jepa-wam/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [ ] 阅读状态:: unread

related:: [[latent world action model]], [[V-JEPA]], [[transition prediction]], [[@gao2026fast-leworldmodel]], [[@zhang2026lingbot-va2]], [[@feng2026wam-ttt]], [[@qian2026wam-rl]], [[@fu2026lingbot-vision]], [[@liu2026last0-latent-spatio-temporal]], [[@yang2026dreamtrajectory]]
affiliation:: [[Renmin University of China]], [[XYZ Embodied AI]], [[Shenzhen University of Advanced Technology]], [[Tsinghua University]]

## Abstract

Robust robot control benefits from explicitly modeling state transitions, but video-generation world action models (WAMs) introduce substantial deployment cost. Existing latent WAMs avoid explicit future generation, but often compress predictive representations or separate predictive modeling from the representations used for action generation. We introduce JEPA-WAM, a latent WAM built in a pretrained V-JEPA space, which couples latent transition prediction with continuous action generation through a shared predictor. JEPA-WAM predicts a spatially structured joint current–future target that captures task-shared visual temporal structure between current and future observations, while preserving dense patch-level correspondence. Through the shared predictor, transition supervision directly shapes the backbone, from which dedicated representations are extracted for action prediction. The same design can also be instantiated in pretrained VLA policies while preserving their original perception and action pathways. On LIBERO-Plus, JEPA-WAM achieves 79.2%, the best result without large-scale robot-policy pretraining, while its pretrained π0.5 instantiation reaches 86.3%, achieving the best overall performance. Experiments on RoboTwin 2.0 and real-world bimanual manipulation further demonstrate strong generalization under visual and spatial shifts.

## 一句话定位

提出一个不生成未来帧的潜空间 WAM，用冻结 V-JEPA 联合编码当前与未来帧构造 patch 级转移目标（表示转移关系而非绝对未来），让转移预测和动作生成共享同一个 0.5B 预测器骨干，部署时摘掉预测分支，LIBERO-Plus 上 0.5B 拿下无预训练组第一（79.2%），同一监督塞进 π0.5 拿下全场第一（86.3%），真机 π0.5 版 ID/OOD 各涨约 12 个点。

## 方法 / 对象

- 表示空间，冻结 V-JEPA 2.1 ViT-L/16，384×384，每视角 24×24×1024 patch 特征，多视角固定顺序拼接不池化。
- 联合目标 $Y_{t,t+\delta}$，双帧沿时间堆叠联合编码加停梯度，V-JEPA 双帧管元恰好保持单帧网格，目标与当前表示逐 patch 对应；LIBERO $\delta=31$，RoboTwin $\delta=50$。
- 共享预测器 Qwen2.5-0.5B，一次前向同时输出视觉位置的 $Q^{wm}_t$（经 MLP 头映回 V-JEPA 空间做逐 patch 余弦对齐）和 64 个动作占位符的 $C_t$（喂 16 层 DiT-L 流匹配动作专家）。
- 训练 $\mathcal{L}=\mathcal{L}_{act}+0.5\,\mathcal{L}_{wm}$，只训 Qwen LoRA（r32）、预测头、动作专家；VL 接口先按 Prismatic 单阶段在 LLaVA v1.5 上初始化。
- π0.5 迁移，前缀加 64 可学习未来 token，隐状态排 8×8 网格、MLP 加双线性上采样到 24×24 对齐 ViT-G 联合目标，$\lambda_{wm}$ 升温到 0.1，动作 token 被掩蔽不可见未来 token，原动作通路不变，推理延迟只 +1ms。
- 部署摘掉目标分支与预测头，4 步 Euler 出动作块，RoboTwin 设定 85ms（11.76Hz）。

## 证据

- LIBERO-Plus，JEPA-WAM 79.2%（0.5B，无预训练组第一，只差预训练 VLA-JEPA 0.3 个点），π0.5+JEPA Obj. 86.3% 全场第一（π0.5 基线 84.5）。
- LIBERO ID 96.7%（追平 2B 的 ResVLA），π0.5 版 97.8% 组内第一。
- RoboTwin 2.0，Clean 79.9 / Random 36.9（无预训练组第一，Random 追平预训练 π0.5 的 37.2）；π0.5 版 Clean 75.4→84.6 但 Random 仅 37.2→37.5。
- 真机五任务，JEPA-WAM 59.8/54.2（ID/OOD）对 π0 的 51.8/22.5，π0.5 版 90.3/84.7 对 77.5/72.5。
- 消融，V-JEPA 表示本身 +3.8；联合目标对未来单编 +1.9、对端点差分 +8.3；patch 结构 +4.5（对 iREPA 变换）；末层监督 +2.7；动作读出隔离 +6.1（对 Full hidden）。
- 探针，固定未来帧的时间差六分类 67.2% 对端点差分 47.0%（+20.1，CI [18.3,21.9]）；未见时间差 MAE 8.88 对 13.32；去端点位移的残差轨迹 $R^2$ 0.582 对 0.485；反向对照里端点差分在直接位移预测上略优（0.740 对 0.718）。

## 局限

- 转移目标语言无关（作者自陈），代价已经在数字里，LIBERO-Plus 语言扰动类 68.2 是它七类里唯一垫底的，比 VLA-Adapter 还低。
- π0.5 迁移收益不均匀，LIBERO-Plus +1.8、真机 +12.8、RoboTwin Random 仅 +0.3，重度域随机化下失效，收益结构无分析；相机类还从 69.4 回退到 66.0。
- 「共享预测器优于独立世界模型」缺同规模受控对照，与 VLA-JEPA 的对比参数与预训练都不同，Full hidden 消融只证明读出要隔离。
- $\delta$ 每基准一个定值无扫描，而探针显示时间差信息确实被编码，$\delta$ 不太可能是无关变量。
- 真机每格 10 rollout 部分得分制，方差不小；消融全部只在 LIBERO-Plus。

## 我的阅读笔记

这篇把「潜空间 WAM 该学什么目标」这个问题拆解得很干净，联合编码、未来单编、端点差分三种目标构造摆在同一设置下比（79.2 对 77.3 对 70.9），再用三个冻结探针从表示层面解释差距在哪。探针那组实验是全文我最欣赏的部分，控制变量（固定未来帧）、泛化检验（未见时间差）、剥离混淆（减去直线位移）、还有一个对自己不利的反向对照（直接位移预测上端点差分更好），这套分析流程本身就值得抄。

管元那个细节说到点子上了。V-JEPA 的视频分词器每两帧组一个 tubelet，双帧输入正好产出与单帧相同的空间网格，联合目标与当前表示天然逐 patch 对应。整个方法能免掉任何池化或对齐插值，靠的是这个「白捡」的架构巧合，选表示空间时这种兼容性检查很值得学。

最实用的其实是 3.4 那份 π0.5 迁移配方，64 个未来 token、上采样对齐头、动作 token 掩蔽三件套，成本每步 1ms，真机 ID/OOD 各涨 12 个点。做 VLA 的人可以不管前面的 0.5B 模型，直接抄这一节。

要泼的冷水集中在收益的分布上。转移监督在 LIBERO-Plus 的视觉扰动类上很能打，在语言扰动类上垫底，在 RoboTwin 的域随机化上对预训练模型几乎无增益（+0.3）。这个辅助目标不是均匀增益，是在重排模型的鲁棒性分布，哪类扰动受益哪类受损跟「转移目标编码了什么、没编码什么」直接挂钩，语言无关就是语言类吃亏。引用这篇的数字时得带着扰动类别说。

## 摘录

> Rather than reconstructing a unique future observation, the joint target captures stable and changing regions and evolving local object and spatial relations, while preserving dense patch-level structure.

> By sharing the predictor, supervision from latent transition prediction updates the same backbone from which action relevant representations are extracted.

> Feature differencing provides a strong representation of first-order endpoint change, whereas joint encoding better preserves temporal relations and within-interval trajectory structure.

> it may be less expressive when the same observation leads to substantially different transitions under different instructions.

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
