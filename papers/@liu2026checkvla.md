---
tags:
  - paper
status: read
aliases:
  - CheckVLA
  - "CheckVLA: Execution-Time Verification with Action-Conditioned World Model for Long-Horizon Mobile Manipulation"
  - "CheckVLA 执行期验证"
year: 2026
title: "CheckVLA: Execution-Time Verification with Action-Conditioned World Model for Long-Horizon Mobile Manipulation"
doi:
arxiv: "2607.26789"
url: "https://arxiv.org/abs/2607.26789"
venue: "arXiv preprint; AAAI-style template"
venue_short: arXiv
pdf_url: "https://arxiv.org/pdf/2607.26789v1"
openalex:
metadata_source: "arXiv 2607.26789v1 and source package"
metadata_confidence: high
pdf: "[[papers/pdfs/liu2026checkvla.pdf]]"
reading: "[[papers/bilingual/liu2026checkvla_中英混读.md]]"
images: "papers/images/liu2026checkvla/"
image_index: "[[papers/images/liu2026checkvla/index.md]]"
map_axis: "世界模型/WAM/执行期验证与失败干预"
map_brief: "把已提交的 action chunk 当成可检验的近未来观测预测，用冻结的动作条件世界模型加 conformal 校准阈值决定何时打断，再按超阈幅度改写延迟可行的后缀。"
map_role: "研究开环分块执行怎样恢复反馈的入口，也提供 confidently-wrong 象限这一失败模式的量化证据。"
authors:
  - "[[Yushan Liu]]"
  - "[[Peibo Sun]]"
  - "[[Xintao Chao]]"
  - "[[Zhenyang Yang]]"
  - "[[Yifan Xie]]"
  - "[[Lingfeng Zhang]]"
  - "[[Shoujie Li]]"
  - "[[Chenyu Tang]]"
  - "[[Fang Chen]]"
  - "[[Xiao-Ping Zhang]]"
  - "[[Wenbo Ding]]"
institutions:
  - "[[Tsinghua University]]"
  - "[[Shanghai Jiao Tong University]]"
  - "[[Peking University]]"
  - "[[Nanyang Technological University]]"
  - "[[Xspark AI]]"
topics:
  - execution-time verification
  - action-conditioned world model
  - conformal prediction
  - action chunking
  - failure detection
  - replanning
  - latency-aware control
  - episodic memory
  - mobile manipulation
  - RoboCasa365
  - vision-language-action
---

# CheckVLA: Execution-Time Verification with Action-Conditioned World Model for Long-Horizon Mobile Manipulation

- [x] PDF:: [[papers/pdfs/liu2026checkvla.pdf]]
- [x] 元数据:: source=arXiv 2607.26789v1 and source package, confidence=high
- [x] 精读稿:: [[papers/bilingual/liu2026checkvla_中英混读.md]]
- [x] 图片索引:: [[papers/images/liu2026checkvla/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引
- [x] 阅读状态:: read

related:: [[@pan2026vla-corrector-lightweight-detect]] · [[@murray2026flowdagger]] · [[@yu2026wm-dagger]] · [[@liu2026confal-wm]] · [[@qwen2026robotmanip]] · [[@feng2026wam-ttt]]
affiliation:: [[Tsinghua University]] · [[Shanghai Jiao Tong University]] · [[Peking University]] · [[Nanyang Technological University]] · [[Xspark AI]]

> [!warning] 版本与开放状态
> 本笔记按 arXiv 2607.26789v1 与同版本源码整理，模板看格式是 AAAI 系预印本，正文没有声明录用状态，也没有给出公开代码或项目页。全部证据来自 RoboCasa365 仿真，没有真机实验，作者在 Discussion 里写明了这一点。Table 2 的公开对照被作者自标为 descriptive positioning，因为 CheckVLA 额外用训练侧 rollout 训了验证器。

## Abstract

Vision-language-action (VLA) policies commonly execute long-horizon mobile manipulation through open-loop action chunks, issuing multiple actions without receiving new high-level visual input. A committed chunk therefore implies how observations should evolve, but accidental deviations can violate this expectation while the remaining actions continue to propagate the error: commit-time policy confidence cannot react to a deviation that occurs after dispatch, and observation-only anomaly scores lack an action-conditioned reference for separating expected effects from unexplained changes. We propose CheckVLA, which verifies execution with a separately trained, frozen action-conditioned world model. A conformally calibrated risk threshold bounds the episode-level probability of an unnecessary first intervention and determines when to intervene, its exceedance controls how strongly the rewritten suffix retains the superseded chunk, latency-aware hard prefixing restricts replacement to actions that remain deployable, and an event-driven keyframe bank preserves evidence of prior progress across repairs. On RoboCasa365, under a common training recipe and a matched invocation budget, CheckVLA attains a 36.1% average success rate against 27.6% for periodic replanning (+8.5 points). At a matched 5% episode-level false-alarm target, action conditioning raises timely recall to 77.9%, against 48.6% for an observation-only control and 37.9% for an action-shuffled control.

## 一句话定位

CheckVLA 把一个已提交的 action chunk 重新定义成一条可被检验的预测，即按这些动作执行下去观测应该这样演化。作者用单独训练且冻结的动作条件世界模型在执行期做这个检验，用 conformal 校准的阈值决定何时打断，用超阈幅度决定改写强度，用延迟约束决定能改哪一段。

## 方法 / 对象

- 滚动预测。冻结的 V-JEPA 2-AC 编出观测特征，世界模型 $\Psi$ 在仍有效的已提交动作与名义本体 rollout 条件下只预测接下来 $k$ 步（$k\ll H$），每帧观测重新锚定，改写后作废旧条件的预测。训练先 teacher forcing 再在自己的 rollout 上跑，全程在特征空间，不做像素解码。
- 校准触发。逐步差异用跨度相关的留出成功统计量标准化，因果风险头在窗口上聚合 $(\tilde d, \ell/k, h/H, \Delta_{sw})$ 加 episodic 摘要。函数型 conformal 给出在线阈值 $\delta_t = \mu_{r,t}+\hat q_\alpha\tilde\sigma_{r,t}$，保证名义成功轨迹上至少一次误干预的概率不超过 $\alpha$。
- 风险头训练用三类轨迹，名义成功、开环骨干的自然失败、带起点标注的物理扰动。扰动作用在物理层面，从不直接注入差异序列。
- 后缀改写。$h<d_{\text{lat}}$ 的位置在每个 flow 积分步被钳制到已执行前缀，超阈幅度 $e_{t^*}$ 决定基础保留权重 $w_0(e)=w_{\min}+(1-w_{\min})e^{-\beta e}$，再按位置与通道指数衰减混进 flow 速度场。硬钳制是经验投影而非精确条件采样。
- Episodic 记忆。事件驱动关键帧库用关节位移的延迟确认局部极小值加多样性判据写入，策略通过门控交叉注意力读整个库，风险头只读紧凑摘要。
- 实例化用 $\pi_{0.5}$ flow-matching 骨干，移动与操作专家参数分离，只经共享 VLM 前缀的联合自注意力交互，stop-gradient 阻断动作损失回传 VLM。

## 证据

| 证据 | CheckVLA 结果 | 关键对照 | 阅读边界 |
| --- | ---: | ---: | --- |
| RoboCasa365 平均成功 | 36.1 | Qwen-RobotManip 35.9，WorldDreamer 35.3 | 描述性定位，验证器多用训练侧数据 |
| 匹配调用预算 | 36.1（10.2 次调用） | 周期重规划 27.6（10.1 次） | 受控内部对照，+8.5 点 |
| 可归因增益拆分 | 验证触发 +3.9，自适应引导 +2.6，记忆 +2.0 | 容量匹配 +3.7，解耦 +0.7，常规引导 +1.5，周期重规划 +4.5 | 总增益里与验证无关的占 +10.4 |
| 及时召回 | 77.9% | 只看观测 48.6%，动作打乱 37.9% | 打乱动作比不看动作更差 |
| 校准 | 实测 FWER 4.8% 对目标 5% | 验证集调的固定阈值 7.1% | 只保首次误干预 |
| confidently-wrong 象限 | 占 25.0% episode，贡献 48.4% 失败 | 76.0% 仍可及时恢复，31.0% 被救回 | 留出自然执行，预注册决策窗口 |
| 改写规则 | 救回 16.9%，伤害 2.8%，跳变 0.072 | 固定权重 12.8 / 3.7，超阈打乱 14.4 / 3.6 | 单次修复，后续触发关闭 |
| 记忆 | 完成子目标回退 1.34 降到 0.18 | 因子实验重训策略读取器 | 重训代价未报 |
| 部署代价 | +88.4M 参数，16.9 GFLOPs/步，1.18$\times$ wall-clock | 监控 p95 16.4 ms 对 100 ms 控制周期 | 仿真时序，非真机硬件 |
| 逐种子 | 35.6 / 36.9 / 35.8 | 与第二名差距 0.2 点 | 种子极差 1.3 点大于该差距 |

## 局限

- Table 2 的 SOTA 只领先 0.2 个点，而自身三个种子的极差是 1.3 个点。作者用 descriptive positioning 措辞准确，但摘要与引言的 setting the state of the art 容易被误读。
- 没有真机。conformal 校准依赖可交换性，而真机部署恰恰是可交换性最容易失效的地方，光照、硬件磨损与场景漂移都会让校准集与部署分布不一致。
- 保证范围窄。只覆盖名义成功 episode 上的首次误干预，不覆盖召回、修复后安全、重复干预与分布偏移，后面这几项才是部署时最关心的。
- 扰动族是人为注入的三类，起点由标注确定。真实失败可能是缓慢累积的定位漂移或传感器退化，形态完全不同。
- 及时召回依赖的不可逆时刻 $\tau_{\text{irrev}}$ 是操作性定义，与被评估的修复集合绑定。换一套更强的修复规则，所有方法的及时召回都会变，跨论文比较要格外小心。
- 硬钳制是经验投影，改写后的块在概率意义上不是从条件分布里采出来的，切换跳变 0.072 是经验上的小而非理论上的零。
- 主文强调的策略侧领先 9.3 个点对应的是不刷新版本。补充材料显示观测刷新的探针能到 73.1%，差距收窄到 4.8 个点，代价是每 episode 多 382.2 次 VLA 求值。
- 验证器所需辅助 rollout 的总采集成本、记忆因子实验的重训成本都没有折算。

## 我的阅读笔记

最值得画出来的是 Table 5 那个象限。低策略不确定、高世界模型风险的 episode 占四分之一却贡献将近一半的失败。做 VLA 的很多人都有「策略自己不知道自己错了」的体感，但很少有人把它切成一张 2$\times$2 表并给出失败份额。

第二个值得记的是 action-shuffled 这个对照。保留动作 token 边缘分布但打乱配对，结果比完全不看动作还差 10.7 个点。这条说明验证器学到的不是动作 token 的统计规律，而是这些动作与这段未来的对应关系。少了这个对照，只看观测的基线不足以证明动作条件的价值。

第三个是超阈到保留的配对实验。Table 6 里 shuffled exceedance 与正确配对的对比，加上附录的分桶扫描，两组合起来证明的是「风险大小与修正强度应该配对」这条原则，而不只是「变权重比固定权重好」。这条原则可以迁移到别的系统上。

短板集中在证据的外部有效性上。全仿真、单基准、人为扰动族、conformal 只覆盖首次误干预。这些作者都写进了 Discussion，态度诚实，但不改变一个事实，这套机制在真机上是否还成立完全没有证据。

和 [[@pan2026vla-corrector-lightweight-detect|VLA-Corrector]] 对读会更清楚。两篇都在做推理期的检测与纠正，前者走轻量检测加自适应动作时域，后者走外挂世界模型加校准触发加后缀改写。选哪条取决于失败模式是「该刷新了」还是「已经错了」。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
