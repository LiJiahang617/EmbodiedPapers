---
tags:
  - paper
  - cat/agent
  - cat/wam
  - cat/human-data
  - cat/humanoid
status: unread
aliases:
  - DYNA-2.1
  - Dyna-2.1
  - "Dyna-2.1: A Physical Agent for End-to-End Workflows"
year: 2026
title: "Dyna-2.1: A Physical Agent for End-to-End Workflows"
published: 2026-09-29
doi:
arxiv:
url: "https://dyna.co/dyna-2.1"
venue: "Dyna Robotics 官方技术报告"
venue_short: "Tech Report"
openalex:
metadata_source: official-web
metadata_confidence: high
pdf: "[[papers/pdfs/dyna2026dyna21.pdf]]"
reading: "[[papers/bilingual/dyna2026dyna21_中英混读.md]]"
images: "papers/images/dyna2026dyna21/"
image_index: "[[papers/images/dyna2026dyna21/index.md]]"
map_axis: "具身智能/智能体/全身控制与小时级工作流"
authors:
  - "[[Dyna Robotics]]"
institutions:
  - "[[Dyna Robotics]]"
topics:
  - Physical Agent
  - Unified Robot Representation
  - Whole-Body Control
  - Workflow Orchestration
  - Human Video
created: 2026-10-02
updated: 2026-10-02
---

# Dyna-2.1: A Physical Agent for End-to-End Workflows

- [x] 本地文本快照 PDF:: [[papers/pdfs/dyna2026dyna21.pdf]]
- [x] 元数据:: source=official-web, confidence=high
- [x] 精读稿:: [[papers/bilingual/dyna2026dyna21_中英混读.md]]
- [x] 图片索引:: [[papers/images/dyna2026dyna21/index.md]]
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，`#map/具身智能/智能体/全身控制与小时级工作流`
- [ ] 阅读状态:: unread

related:: [[@dyna2026dyna2]]、[[@liu2026rapid]]、[[@han2026hil-umi]]、[[@pan2026vla-corrector-lightweight-detect]]、[[@dexmal2026dm05]]
affiliation:: [[Dyna Robotics]]
map_brief:: 用 URR 连接人类运动、WAM 策略与全身控制，再以带记忆的编排器组织洗衣工作流
map_role:: 研究动作接口、控制动态和跨步骤调度如何共同支撑长时间自主操作

> 💡 来源说明：这是 Dyna Robotics 于 2026 年 9 月 29 日发布的官方技术报告。本次收录以官方网页为来源，未取得对应的 arXiv 论文版本。本地 PDF 是官网正文的文本快照，不是官方排版 PDF。报告包含系统说明、视频演示和示意图，没有重复试验统计；元数据的高置信度不代表系统效果经过独立验证。

## Abstract

To be useful, a general-purpose robot needs to take over entire workflows without frequent human intervention. Dyna-2.1 introduces our physical agent, a semi-humanoid robot named Taku with a learning system that leverages human experience for enhanced teachability.

以上为官网导语，原报告没有单独的学术摘要。

## 一句话定位

DYNA-2.1 构造一套从本体到工作流调度的物理智能体，让机器人自行处理洗衣、烘干、折叠和上架之间的交接。核心是人类运动可复用的 URR 表示、学习全身控制器、DYNA-2 动作策略及带文本记忆的视觉语言编排器。

## 方法 / 对象

- Taku 采用四转向轮底盘和双 7 自由度机械臂，图中标注 21 自由度上半身与移动底盘。硬件覆盖多个工位及高低位置操作，报告没有完整载荷与工作空间参数。
- URR 用腕、肘、胸和底盘占位的任务空间姿态表示运动。它连接人类视频、UMI、机器人遥操作与策略训练，也为仿真控制器提供跟踪目标。
- 全身控制器在 Isaac Lab 中通过强化学习训练，以 100 Hz 输出关节目标和轮速；DYNA-2 策略约 5 Hz 输出 URR 轨迹。编排器以更低频率提供步骤指令。
- 策略混合使用 100 万小时人类视频和机器人机队数据。控制器条件化与异步未来命令上下文用于处理示范和部署时的控制动态差异。
- 编排器根据视觉、用户指令和文本记忆选择下一步。记忆保存设备状态、已完成步骤和折叠数量，支持离开当前工位后继续工作。

## 证据

- 官方提供一小时未剪辑的自主洗衣工作流视频，以及取饮料、服务器维护、全身操作和扰动恢复片段。它们是系统执行实例，没有配套多次试验完成率或置信区间。
- Figure 2.2 以约 79 个子步骤说明可靠性累积。在步骤独立且各自成功率为 95% 的示意条件下，无人工介入完成一周期的概率约为 1.7%。约 190 次每日干预同样是估算，不是 Taku 的实测记录。
- Figure 2.3 将洗衣流程组织为 13 个决策点。机器完成状态、篮筐是否为空及摞高是否达标决定切换与循环，恢复分支也包含在流程内。
- Figure 3.4 的 15 cm 阶跃响应是构造曲线，Figure 3.8 的编排时间线是示例。两图解释设计目标，不能用作控制精度或调度性能测量。
- 报告引用的 87% 对 46% 客户验收结果属于此前 DYNA-2 与 DYNA-1 的静态机器人对照；最快三天部署也属于旧折叠业务，不能归入本次 Taku 工作流结果。

## 局限

报告未披露本次策略规模、训练损失、数据比例、控制器奖励、编排器型号及记忆一致性机制。URR 统一目标格式仍受可达性、碰撞与控制动态约束，不能保证任意动作无损跨本体迁移。小时级视频尚不足以确定长期可靠性、吞吐或人工干预分布，需要重复运行、组件消融及失败记录。

## 我的阅读笔记

完整讲解见 [[papers/bilingual/dyna2026dyna21_中英混读.md]]，覆盖报告各节、接口关系、精选图表和主张的证据边界。回看重点是 URR 的表示条件、策略与控制器的职责，以及编排器如何处理跨步骤状态。与 DYNA-2 对照时，应区分模型预训练结果和这次完整系统的演示。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
