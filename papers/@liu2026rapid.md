---
tags:
  - paper
  - cat/agent
  - cat/human-data
  - cat/action-repr
status: unread
aliases:
  - RAPID
  - "RAPID: Robot Agentic Programming from Demonstrations"
year: 2026
title: "RAPID: Robot Agentic Programming from Demonstrations"
doi: "10.48550/arXiv.2609.30249"
arxiv: "2609.30249v1"
url: "https://arxiv.org/abs/2609.30249"
venue: "arXiv preprint"
openalex:
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/liu2026rapid.pdf]]"
reading: "[[papers/bilingual/liu2026rapid_中英混读.md]]"
images: "papers/images/liu2026rapid/"
image_index: "[[papers/images/liu2026rapid/index.md]]"
website: "https://yuyaoliu.me/projects/rapid"
authors:
  - "[[Yuyao Liu]]"
  - "[[Jiayuan Mao]]"
  - "[[David Hsu]]"
  - "[[Leslie Pack Kaelbling]]"
  - "[[Tomás Lozano-Pérez]]"
institutions:
  - "[[Massachusetts Institute of Technology]]"
  - "[[National University of Singapore]]"
  - "[[University of Pennsylvania]]"
  - "[[NVIDIA]]"
topics:
  - agentic programming
  - learning from human demonstrations
  - nonprehensile manipulation
  - object-centric relational programs
  - trajectory optimization
  - real-to-sim reconstruction
  - program verification
---

# RAPID: Robot Agentic Programming from Demonstrations

- [x] PDF:: [[papers/pdfs/liu2026rapid.pdf]]
- [x] 元数据:: source=arxiv, confidence=high
- [x] 精读稿:: [[papers/bilingual/liu2026rapid_中英混读.md]]
- [x] 图片索引:: [[papers/images/liu2026rapid/index.md]]
- [x] 项目页:: [RAPID](https://yuyaoliu.me/projects/rapid)
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，`#map/具身智能/智能体/单示范关系程序与仿真迭代`
- [ ] 阅读状态:: unread

related:: [[@xiao2026enpire]], [[@zhou2026holoagent0]], [[@jiang2026robottt]]
affiliation:: [[Massachusetts Institute of Technology]], [[National University of Singapore]], [[University of Pennsylvania]], [[NVIDIA]]

## Abstract

Coding agents have demonstrated enormous success in solving complex programming problems.
To leverage their potential for robot systems, this work introduces Robot Agentic Programming from Demonstrations (RAPID), which automatically generates, verifies, and refines robot programs, given a single visual human demonstration.
The iterative agentic loop of code refinement requires several key ingredients: (i) a testable task specification,
(ii) action primitives for robot execution, and
(iii) an interactive environment for program execution and verification.
RAPID infers all three from the demonstration automatically.
To make the resulting program reusable beyond the demonstration setting, RAPID uses an object-centric relational program representation that focuses on the underlying structure of the demonstrated strategy rather than the specific motion per se: it expresses the action primitives as trajectory-optimization programs that realize object-level motion effects, while composing them through relational constraints that capture scene-specific geometry at run time.
We evaluated RAPID in simulation on eight challenging contact-rich nonprehensile manipulation tasks as well as general prehensile manipulation tasks in the LIBERO-Pro benchmark.
We also successfully deployed it on a real Franka arm and evaluated on all eight nonprehensile tasks.
In all experiments, RAPID demonstrated strong performance, with generalization over object pose, shape, material, and environment.
Website: https://yuyaoliu.me/projects/rapid.

## 一句话定位

RAPID 从一次人类视觉示范和语言描述中构造成功判据、操作原语与仿真验证环境，让 coding agent（编程智能体）反复执行和修改机器人程序。它把原语写成局部轨迹优化程序，再用对象关系连接各阶段，使同一任务策略能够适应新的物体和场景。

## 方法 / 对象

- 问题范围是 quasi-static rigid-body manipulation（准静态刚体操作），重点是初始无法被平行夹爪直接抓取的物体。
- Object-centric relational program（以对象为中心的关系程序）同时声明目标、语义角色、关系要求、效果参数、几何解析器、成功判据和优化代价。
- 原语通过 cross-entropy method（CEM，交叉熵方法）在 MuJoCo 中优化动作；策略根据上一阶段的状态计算下一阶段的效果参数。
- Real-to-sim（真实到仿真）重建使用 VLM、SAM 3、SAM 3D 和 FoundationPose；coding agent 在重建场景及筛选后的扰动场景中验证并修订程序。
- 新场景中冻结原语和策略，只重新绑定语义角色并优化轨迹。几秒的开销指角色绑定，全文没有报告完整部署耗时。

## 证据

- 八项非抓持操作任务，每项一次示范、50 个新测试场景，重复三次实验；Table II 报告 success rate（成功率）的 mean±std（均值±标准差）。
- RAPID 平均 0.759±0.024，去除 scene variants（场景变体）后为 0.532±0.071；CaP-Agent0 为 0.146±0.025。
- LIBERO-Pro 使用无示范、一个 debug scene（调试场景）的设置。RAPID 在六个设置中四项单独最高、一项并列最高；LIBERO-Goal 的位置扰动上低于 ASPIRE，0.67 对 0.81。
- 真机为 Franka Research 3、平行夹爪和 RealSense L515，每项十个测试场景。Fig. 5 中 RAPID 的 T1–T8 成功率为 0.9、0.8、0.7、0.6、0.7、0.4、0.7、0.6。
- 按 Fig. 5 的等量试验计算，RAPID 合计 54/80 成功，CaP-Agent0 为 7/80；这两个合计值是图中数据的计算结果。

## 局限

- 主实验检验同一任务族内的场景泛化，不能据此推断新任务结构、跨本体或可变形物体操作能力。
- 成功判据与场景过滤器由 agent 生成。独立隐藏判据用于最终测试，但正文没有量化生成判据的正确率或过滤造成的任务分布变化。
- OReP 同时包含关系接口、几何解析、优化代价和 CEM。现有对比支持整体表示的作用，未分别识别这些组件的贡献。
- 每项程序构造需要几十分钟；重建与每场景轨迹优化的总耗时、token 消耗和失败重试上限未报告。
- 真机每项十次，未报告重复实验或置信区间。较弱的 T6 为 4/10，但没有分阶段失败分析。

## 我的阅读笔记

最值得回看的是 Fig. 3 和 Sec. IV-B。连接约束根据翻转后的物体位置、夹具轴向以及障碍物与夹具形成的通道计算位移，说明可复用的是对象关系与阶段依赖，而非示范中的具体坐标。

Table II 也限制了对方法的解释。仅给 CaP 加 OReP 后平均成功率仍接近零；闭环验证使表示能够被构造出来，变体测试再迫使程序适应场景变化。与 ENPIRE 对读可以比较两种反馈来源，RAPID 在重建仿真中修订操作程序，ENPIRE 在真实机器人实验循环中改进策略。

完整公式、三张原文表格、八项任务、真机数值与证据边界见 [[papers/bilingual/liu2026rapid_中英混读]]。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
