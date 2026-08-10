---
tags:
  - paper
status: unread
aliases:
  - "Data Pyramid for Embodied Manipulation"
year: 2026
title: "Data Pyramid for Embodied Manipulation"
doi: "10.48550/arXiv.2607.24744"
arxiv: "2607.24744v1"
url: "https://arxiv.org/abs/2607.24744"
venue: "arXiv preprint"
project: "https://jasper-aaa.github.io/embodied-data-pyramid/"
github: "https://github.com/worldbench/awesome-embodied-data-pyramid"
pdf_url: "https://arxiv.org/pdf/2607.24744v1"
license: "CC BY 4.0"
openalex: 
metadata_source: arxiv
metadata_confidence: high
pdf: "[[papers/pdfs/ye2026data-pyramid-embodied-manipulation.pdf]]"
reading: "[[papers/bilingual/ye2026data-pyramid-embodied-manipulation_中英混读.md]]"
images: "papers/images/ye2026data-pyramid-embodied-manipulation/"
image_index: "[[papers/images/ye2026data-pyramid-embodied-manipulation/index.md]]"
authors:
  - "[[Yifan Ye]]"
  - "[[Yankai Fu]]"
  - "[[Yaoxu Lv]]"
  - "[[Bohan Hou]]"
  - "[[Jun Cen]]"
  - "[[Lingdong Kong]]"
  - "[[Duo Zheng]]"
  - "[[Tianxing Chen]]"
  - "[[Jiaming Liu]]"
  - "[[Ziang Cao]]"
  - "[[Yunfan Lou]]"
  - "[[Wei Chow]]"
  - "[[Xian Sun]]"
  - "[[Yingshuo Wang]]"
  - "[[Kuangzhi Ge]]"
  - "[[Xiaowei Chi]]"
  - "[[Xidong Zhang]]"
  - "[[Zhibo Pang]]"
  - "[[Yiwu Zhong]]"
  - "[[Sirui Han]]"
  - "[[Zhihe Lu]]"
  - "[[Weihao Yuan]]"
  - "[[Qifeng Chen]]"
  - "[[Michael Yu Wang]]"
  - "[[Yao Mu]]"
  - "[[Ziwei Liu]]"
  - "[[Jianfei Yang]]"
  - "[[Ping Luo]]"
  - "[[Shanghang Zhang]]"
institutions:
  - "[[Peking University]]"
  - "[[Nanyang Technological University]]"
  - "[[Hong Kong University of Science and Technology]]"
  - "[[National University of Singapore]]"
  - "[[The Chinese University of Hong Kong]]"
  - "[[The University of Hong Kong]]"
  - "[[Duke University]]"
  - "[[University of California, Berkeley]]"
  - "[[Great Bay University]]"
  - "[[Nanjing University]]"
  - "[[Shanghai Jiao Tong University]]"
topics:
  - survey
  - embodied data
  - data pyramid
  - robot learning
  - heterogeneous pretraining
  - cross-embodiment alignment
  - vision-language-action
  - world-action model
  - UMI
  - egocentric video
  - simulation
  - tactile and failure data
---

# Data Pyramid for Embodied Manipulation

- [x] PDF:: [[papers/pdfs/ye2026data-pyramid-embodied-manipulation.pdf]]
- [x] 元数据:: source=arxiv, confidence=high；标题、29 位作者、11 个机构、DOI 与许可由 arXiv v1 / PDF 标题页核对
- [x] 项目资源:: [Project](https://jasper-aaa.github.io/embodied-data-pyramid/) · [Awesome Embodied Data Pyramid](https://github.com/worldbench/awesome-embodied-data-pyramid)
- [x] 精读稿:: [[papers/bilingual/ye2026data-pyramid-embodied-manipulation_中英混读.md]]
- [x] 图片索引:: [[papers/images/ye2026data-pyramid-embodied-manipulation/index.md]]（arXiv source 主图 8 张）
- [x] 地图维护:: 已加入 [[论文地图]] 快速索引，`#map/具身智能/数据/数据金字塔与预训练配方`
- [ ] 阅读状态:: unread

related:: [[@qwen2026robotmanip]], [[@intelligence2026pi07-steerable-generalist-robotic]], [[@zhang2026lingbot-va2]], [[@wu2026lingbot-vla2]], [[@liu2026last-hd]], [[@kim2026ego-pi]], [[@paliwal2026do-i-dexterous-manipulation]], [[@wu2026tactile-wam]], [[@yu2026wm-dagger]], [[@gigaworld2026roadmap]]
affiliation:: [[Peking University]], [[Nanyang Technological University]], [[Hong Kong University of Science and Technology]], [[National University of Singapore]], [[The Chinese University of Hong Kong]], [[The University of Hong Kong]], [[Duke University]], [[University of California, Berkeley]], [[Great Bay University]], [[Nanjing University]], [[Shanghai Jiao Tong University]]

## Abstract

Multimodal foundation models learned to see and to speak by consuming the whole internet. Embodied agents admit no such shortcut, since they require data that couple observations with physical states and actions. These signals can be provided, to varying degrees, by multiple data sources. In this work, we organize the embodied data ecosystem as a "pyramid" spanning five complementary sources: real-robot data, UMI-style data, egocentric and exocentric data, simulation data, and general vision-language data. We organize the pyramid around the tension between scalability and robot alignment, and further characterize each source in terms of data quality, diversity, reusability, and physical fidelity. We then analyze recent embodied foundation models through the lens of their data recipes, examining how different sources are selected, aligned, and mixed during pretraining. For embodied brain models, vision-language-action models, and world-action models alike, we relate data composition to capabilities in perception, reasoning, planning, action generation, and world prediction. We close by discussing six open challenges: building large-scale tactile datasets, collecting failure and recovery data, developing scalable data-collection pipelines, aligning actions across embodiments, leveraging egocentric data for dexterous manipulation, and designing principled data recipes for robot learning. We hope this work paves the foundation for the design of next-generation embodied systems.

## 一句话定位

这是一篇面向具身操作的 data-centric survey（数据中心综述）：作者用 **Scalability（可扩展性）—Robot Alignment（机器人对齐）** 的张力，把 real-robot、UMI、ego/exo、simulation、general data 组织成五层金字塔，再解释这些数据如何进入 embodied brain、VLA 与 WAM；它提供的是共同坐标系与研究路线图，而不是一个新模型或“数据越多越好”的实验结论。

## 方法 / 对象

- **分类对象**：五类具身数据来源，另以 Quality、Diversity、Reusability、Physical Fidelity 四维补充刻画。
- **应用对象**：Embodied brain、Vision-Language-Action（VLA）与 World-Action Model（WAM）三类基础模型，以及 action-free / action-labeled supervision 在其中的不同作用。
- **关键接口**：跨本体 action structural alignment（专属投影、定长零填充、semantic action slots）与 geometric alignment（robot/base、camera、wrist frame）。
- **论文形态**：72 页、8 图、7 表、参考文献 453 项；正文是 taxonomy + literature synthesis，没有原创训练流程、损失函数、benchmark 或消融。

## 证据

- Tables 1–6 汇总 real-robot、UMI、ego/exo、simulation 与 general-data 资源；Fig. 2 描述各类别内部的规模增长，但跨类别分别使用 demonstrations、hours、QA pairs，不能直接横比。
- Fig. 3 / Table 7 显示训练配方由 robot-only 逐渐走向多源混合；作者同时明确指出 robot-only 模型仍可很强，最佳比例与阶段分配尚无 compute-matched 因果证据。
- Fig. 4 用启发式 action-keyframe 空间分布展示 trajectory diversity，支持“规模不等于多样性”，但它不是标准化 diversity metric 或统计检验。
- §7.2 给出动作对齐的六种代表策略；Qwen-RobotManip 的案例是 80-D canonical vector（$2\times29+22$），每个 arm block 为 $7+9+1+12$ 维。
- §8 将开放问题归为 tactile、failure/recovery、scalable collection、cross-embodiment alignment、ego→dexterous transfer 与 principled data recipes 六项。

## 局限

- 没有 systematic-review 检索协议、纳排标准或质量评分，453 篇覆盖很广，但完整性与选择偏差难以复核。
- 六个维度没有可计算定义；金字塔是 category-level synthesis，不是数据集排名或连续评分器。
- Tables 1–7 混合不同来源的 reported statistics；hours、episodes、clips、grasps、QA、训练阶段与过滤口径不统一。
- Table 7 只记录某类数据是否出现，不给 mixture ratio、采样权重、过滤规则、训练阶段或算力；不能用图标多少预测性能。
- 数据 provenance、license、wearable privacy / consent 等治理议题讨论不足；作为 2026-07 的 v1 快照也会快速过时，应结合官方持续更新仓库。

## 我的阅读笔记

最值得保留的抽象不是“越靠上越好”，而是**监督离可执行物理后果有多远**：real robot 的 action–consequence 链最短；general / ego 的覆盖最广，却要经过 reconstruction、retargeting 与 action grounding。UMI、ego、simulation 三个中间层本质上都是 interface engineering。下一阶段更有价值的增量可能不是继续堆成功 RGB 轨迹，而是补齐 tactile 的瞬时接触反馈、failure/recovery 的偏离轨迹，以及能被机器验证的 frame / unit / controller metadata。精读稿中的具体数字均是该综述转录的 reported values；若要用于研究结论，应继续回溯原始论文。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
