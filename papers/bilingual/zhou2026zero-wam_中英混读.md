---
tags:
  - bilingual-reading
  - deep-reading
source_pdf: "[[papers/pdfs/zhou2026zero-wam.pdf]]"
paper: "[[@zhou2026zero-wam]]"
images: "papers/images/zhou2026zero-wam/"
image_index: "[[papers/images/zhou2026zero-wam/index.md]]"
created: 2026-09-01
source_version: "arXiv 2608.26103v2, 2026-08-27"
reading_standard: "full bilingual reading"
---

# Zero-WAM: In-Context World-Action Modeling from Human Videos for Open-Ended Task Generalization

paper:: [[@zhou2026zero-wam]]
pdf:: [[papers/pdfs/zhou2026zero-wam.pdf]]
images:: [[papers/images/zhou2026zero-wam/index.md]]
reading:: [[papers/bilingual/zhou2026zero-wam_中英混读.md]]

## 核心词汇速查

| English | 中文 | 在本文中的含义 |
| --- | --- | --- |
| zero-shot cross-task generalization | task-level 零样本泛化 | 目标任务没有机器人训练示范，模型仍要完成操作 |
| WAM, world-action model | 世界动作模型 | 联合预测未来视觉状态和可执行动作 |
| ICL, in-context learning | 上下文学习 | 用部署时输入的示范指定新任务，不更新参数 |
| task specification | 任务规范 | 描述要发生什么状态变化，而不只是一句动作命令 |
| HumanGen | 合成人类视频数据集 | 从机器人轨迹自动生成与任务语义匹配的人类视频及配对轨迹 |
| Task-diverse VA | 任务多样视频动作数据 | 按任务重采样的机器人视频动作预训练语料 |
| causal video-action model | 因果视频动作模型 | 逐 chunk 预测下一段机器人视频，再解码动作 |
| MoT, Mixture-of-Transformers | Transformer 混合结构 | 视频和动作有独立参数，但共享一条 attention sequence |
| inverse dynamics | 逆动力学 | 从预测的下一段机器人视频反推应执行的动作 |
| RoPE offset | 旋转位置编码偏移 | 将 human latent 与 robot latent 的坐标区间分开 |
| IFP, in-context future chunk prediction | 上下文未来片段预测 | 训练时预测更远的多个未来视频 chunk，抑制 shortcut |
| flow matching | 流匹配 | 从噪声连续生成视频或动作 latent |
| seen / unseen task | 已见 / 未见任务 | RoboTwin 按任务划分训练和评测，不按轨迹随机切分 |

## 摘要

### 原文摘要

> Zero-shot cross-task generalization, where a policy must execute manipulation tasks never seen during training, remains a central challenge in robot learning. In large language models, a novel task can be performed simply by specifying it in the context, without any parameter update. We bring this paradigm to robotic manipulation and argue that the natural task specification for manipulation is a human video, because it provides rich visual cues about intended task evolution. We present Zero-WAM, a causal video-action model that executes unseen tasks by following in-context human video guidance. An automatic pipeline converts task-sampled robot trajectories into semantically matched human videos, yielding HumanGen with 74.2K human-robot ICL pairs across 8.6K tasks. An in-context future chunk prediction objective discourages shortcuts. On seven unseen RoboTwin tasks, Zero-WAM reaches 47.0% average success.

### 中文解读

论文把问题重新命名为 task specification。语言能说出目标，却常常漏掉空间约束、中间状态和操作顺序。human video 虽然没有机器人 action label，却把这些状态变化直接摆在上下文里。Zero-WAM 让 video Transformer 先预测机器人未来画面，再让 action Transformer 从这段预测画面解码动作，因此人类视频只需提供任务演化线索，不需要和机器人关节轨迹逐帧对齐。

数据和模型是同时设计的。HumanGen 解决配对人机示范稀缺，Task-diverse VA 解决机器人预训练被少数高频任务淹没，IFP 解决模型在 seen task 上只看机器人历史而忽略 human prompt。三者共同支撑 cross-task 结论，不能把 46.95% 只归因于视频输入。

## 论文主线

```text
多源机器人轨迹
   ├─ 按 action + object 划成 6000+ tasks
   │      └─ Task-diverse VA，约 400K robot trajectories / epoch
   └─ HumanGen pipeline
          └─ VLM 分析 → 首帧编辑 → 视频生成 → 语义与物理筛选
                    ↓
          human video + robot trajectory ICL pairs
                    ↓
Wan-2.2-TI2V-5B → MoT causal WAM
   human video 作为 prefix memory
   video branch 预测未来 robot video
   action branch 从预测视频做 inverse dynamics
   IFP 训练时预测更远 future chunks
                    ↓
部署时缓存 human video，直接执行 unseen task，不更新参数
```

可以确定的是，作者把「任务语义」放进未来视频，把「本体可执行性」留在机器人轨迹和 action decoder。这样做绕开了 human hand motion 到 robot joint action 的硬重定向，却把风险转移到合成人类视频质量和视频预测误差。

## 贡献与结论对照

| 论文主张 | 方法位置 | 证据 | 仍然受限的地方 |
| --- | --- | --- | --- |
| human video 是比语言更丰富的 task specification | Introduction、Human video as task specification | unseen RoboTwin 任务上 ICL 变体平均 36.36%，高于 text-only WAN-Action 的 10.98% | human video 由对应 robot trajectory 合成，任务先验并不缺席 |
| HumanGen 能规模化提供人机 ICL pair | Data Curation | 74.2K pairs、8.6K tasks、超过 45 embodiments | 生成质量筛选和人工审计未报告 |
| IFP 迫使模型读取 human prompt | IFP、Ablation | 7-task 平均 28.55% → 46.95%，Stack blocks three 0% → 9% | 未系统扫描 $K$、stride 和权重 |
| task-balanced robot data 改善跨任务迁移 | Task-diverse VA、Ablation | text-only 变体 39.44%，比 LingBot-VA 高 21.99 个百分点 | 变体仍保留了部分 HumanGen 样本，只遮掉视频条件 |
| Zero-WAM 能执行未见任务 | RoboTwin 与真机 | 46.95% 平均成功率，7 个 unseen task 全部胜出；三类真机任务也胜出 | 真机输入与基线不对称，样本量小 |

## 结构地图

| 原文 section | 作者在做什么 | 与主线的关系 | 关键图表或公式 |
| --- | --- | --- | --- |
| Abstract | 给出问题、数据、模型和主结果 | 建立全文承诺 | Fig. 1、47.0% |
| 1 Introduction | 说明语言任务接口的缺口并提出 human video ICL | 回答为什么需要新接口 | Fig. 1 |
| 2 Data Curation | 建立 Task-diverse VA 和 HumanGen | 回答训练数据从哪里来 | Fig. 2、Table 1 |
| 2.1 Task-Diverse Video-Action Data | 按任务平衡多源机器人轨迹 | 避免高频 teleoperation 主导预训练 | 6000+ tasks、400K/epoch |
| 2.2 Human Video Generation Pipeline | 把机器人视频转成语义匹配人类视频 | 扩大 ICL pair 覆盖 | VLM、image editor、video generator 流程 |
| 2.3 In-Context HumanGen Dataset | 统计四类 ICL 子集 | 把规模和视觉对齐变化量化 | 74.2K pairs、8.6K tasks |
| 3 Zero-WAM | 定义 WAM、human prompt 和 IFP 模型 | 回答怎么把视频转动作 | Flow matching、MoT、RoPE、IFP |
| 3.1 Preliminaries | 给出视频流匹配和因果 video-action factorization | 固定概率建模接口 | Eq. flow、Eq. factorization |
| 3.2 Human Video as Task Specification | 说明 human latent 如何进入 video branch | 让视频承担任务语义 | RoPE offset、prefix memory |
| 3.3 In-Context Future Chunk Prediction | 预测 strided future chunks | 防止只用 local history 的 shortcut | $j_k$、$ℒ_{ifp}$ |
| 3.4 Training and Inference | 写出 VA、ICL loss 和部署模式 | 连接训练和测试 | $\mathcal L_{VA}$、$\mathcal L_{ICL}$ |
| 4 Experiments | 仿真、真机、消融 | 回答是否有效 | Table 2、Table 3、Fig. 4–6 |
| 5 Conclusions and Discussions | 总结收益与开放环境边界 | 回答适用范围 | stationary tabletop 限制 |
| 6 Related Works | 对比 cross-task、WAM 和 human video 路线 | 定位论文差异 | AGNOSTOS、WAM-TTT 等 |

## 按原文 section 精读

### 1. Introduction

#### 问题定义

作者讨论的不是换背景或换物体的 visual generalization，而是 cross-task generalization。目标任务的机器人示范不在训练集，部署时只能通过上下文指定意图。作者借用 LLM 的 ICL 观点，把「泛化」转成「怎样给模型足够的任务规范」。

语言接口的不足被写成三个可观测缺口。空间关系不容易完整表达，中间状态常被省略，长时序顺序即使写出来也缺乏视觉 grounding。human video 直接展示物体如何移动、何时接触以及先后关系，因而更像 task evolution 的证据。它不提供机器人动作，所以策略必须学习从视觉状态变化到本体动作的对应关系。

#### 两个训练难题

大规模人机配对昂贵，现有 human-robot datasets 任务数有限。另一方面，seen task 的 next-chunk prediction 可以只靠机器人历史和文字完成，模型会学到 shortcut，部署到 unseen task 时反而不读 human prompt。数据管线和 IFP 分别回应这两个难题。

![[papers/images/zhou2026zero-wam/framework_v1.0.png|760]]

Fig. 1 `Overview of Zero-WAM` 把数据、模型和评测放在同一张图里。读图时要区分两件事，human video 是 task instruction，robot trajectory 仍是 action supervision。Zero-WAM 不是直接模仿人的手部轨迹。

### 2. Data Curation

#### 2.1 Task-Diverse Video-Action Data

Task-diverse VA 来自 AgiBot、InternData-A1、Open-X-Embodiment、RoboCOIN 和 RoboMIND，这些也是 LingBot-VA 使用的公开 VA 预训练来源。作者按 manipulation action 与 object 重划任务，从元数据或轨迹解析得到 task label，再按任务采样并限制每个任务的轨迹数，限制幅度随源数据的 intra-task diversity 调整。

每个 epoch 约采样 400K robot trajectories，覆盖超过 6000 tasks。这个处理不是简单增加数据量，而是改变任务频率分布，降低同一 teleoperation 模式重复出现的权重。后面的 text-only ablation 用来检验这个数据层面的变化是否本身带来迁移。

#### 2.2 In-Context Human Video Generation Pipeline

HumanGen 的单条样本流程可以写成一条语义保持链。

```text
task-balanced robot video
 → VLM 提取 task name、初始状态、状态变化、终态
 → 生成 image-editing prompt
 → image editor 改写 robot 首帧为 human scene
 → VLM 根据状态信息写 video-generation prompt
 → Wan 2.7 或 Kling AI 3.0 生成 human manipulation video
 → VLM 评估 semantic preservation 与 physical plausibility
 → 合格 human video 与原 robot trajectory 配对
```

VLM 选用 Gemini 3.1 Pro 或 Qwen3.6-Plus，图像编辑器选 Nano Banana 2 或 Qwen-Image-2.0。作者主动改变 background、viewpoint、environment style、object instance 和 object placement，同时保持 task semantics。这样配对不要求人和机器人看到同一张桌子，也不要求动作逐帧一致。

这一步的假设很强。语义保持和物理合理性由另一个 VLM 判断，论文没有给出人工抽查比例、生成失败率、运动伪影分布或自然采集视频对照。HumanGen 是可扩展的工程方案，不能直接当作真实人类数据的无偏替代。

![[papers/images/zhou2026zero-wam/data_combine_v1.1.png|760]]

Fig. 2 `Data construction and in-context human video generation` 同时展示 VA data 和 HumanGen。它最重要的阅读点是两条数据线在训练时扮演不同角色，VA 提供机器人动力学，HumanGen 提供任务规范。

#### 2.3 In-Context HumanGen Dataset

| 子集 | pairs | tasks | 用途 |
| --- | ---: | ---: | --- |
| Pre-train ICL, External | 41,188 | 5,062 | 五个公开机器人数据源，强视觉对齐变化 |
| Pre-train ICL, In-house | 30,247 | 3,522 | 多本体内部数据，较高视觉对齐 |
| Simulation ICL | 2,500 | 50 | RoboTwin 50 tasks，每 task 50 对 |
| Real-world ICL | 252 | 3 个 task families | Franka 本体适配和真机评测 |
| 合计 | 74,187，约 74.2K | 约 8.6K | 超过 45 个 robot embodiments |

External 子集的任务覆盖分别来自 AgiBot 3354、InternData-A1 261、Open-X 438、RoboCOIN 512 和 RoboMIND 497 个任务。In-house 子集包含 bimanual Franka、Galaxea R1 Pro 等本体。Simulation ICL 中 43 tasks 用于 post-training，7 tasks 留作 unseen evaluation。Real-world ICL 的 252 对包括 120、96 和 36 对，分别对应三类任务。

![[papers/images/zhou2026zero-wam/robotwin_unseen_v1.1.png|700]]

Table 1 把 HumanGen 与 MIME、EgoMimic、BC-Z、RH20T、EgoScale 等数据集比较。HumanGen 的优势是多源、自动生成、双视角和任务数，代价是生成模型链条成为新的质量瓶颈。

### 3. Zero-WAM, In-Context World-Action Modeling

#### 3.1 Preliminaries

##### Video flow matching

给定干净视频 $\mathbf{x}_0$、噪声 $\boldsymbol\epsilon$ 和 flow time $t$，

$$
\mathbf{x}_t=(1-t)\mathbf{x}_0+t\boldsymbol\epsilon,
\qquad \mathbf v_t^*=\boldsymbol\epsilon-\mathbf{x}_0.
$$

训练 velocity field 的目标是

$$
\mathcal L_{fm}=\mathbb E\left[\|\mathbf v_\theta(\mathbf x_t,t,c)-\mathbf v_t^*\|_2^2\right].
$$

推理时从噪声出发，沿学到的 velocity 积分回干净视频。动作 chunk 使用同样形式的 flow matching。

##### Causal video-action factorization

轨迹被切成 $(\mathbf x^i,\mathbf a^i)$ chunks。给定历史和任务条件 $c$，模型预测下一段视频与动作

$$
p_\theta(\mathbf x^{i+1},\mathbf a^{i+1}\mid\mathbf x^{\le i},\mathbf a^{\le i},c)
$$

并分解为

$$
p_\theta^{vid}(\mathbf x^{i+1}\mid\mathbf x^{\le i},\mathbf a^{\le i},c)
\;p_\theta^{act}(\mathbf a^{i+1}\mid\mathbf x^{\le i},\mathbf a^{\le i},\mathbf x^{i+1},c).
$$

action branch 读取未来 robot video，扮演 inverse dynamics。训练时 $\mathbf x^{i+1}$ 用 ground truth teacher forcing，推理时换成 video branch 生成的 chunk。这个接口把视频预测错误直接暴露给动作解码，也让动作分支不必直接理解 human pixel。

##### MoT 与骨干

video Transformer 和 action Transformer 使用 MoT。每种 modality 有独立 QKV、FFN 和 output head，表示仍在一条 attention sequence 中交互。action chunk 放在 future video representation 之后，保证 action 能读到预测视频。模型由 Wan-2.2-TI2V-5B 改造而来。

#### 3.2 Human Video as Task Specification

训练时 human video $\mathbf h$ 被 prepend 到 robot trajectory 前，作为 video branch 的 prefix memory。video context 是

$$
\mathcal C^{vid,i}=[[\mathbf h,\mathbf x^{\le i}],\mathbf a^{\le i},\ell].
$$

因此 video branch 可以从人类示范吸收任务语义和未来状态变化。action branch 的 context 则是

$$
\mathcal C^{act,i}=[\mathbf x^{\le i},\mathbf a^{\le i},\mathbf x^{i+1},\ell],
$$

它不直接 attend to human video。作者的理由是 human semantics 已经压进 predicted robot video，action decoding 只需做 inverse dynamics。这个信息瓶颈让 IFP 能监督主 video representation，而不是绕过主干另学一条 human-to-action shortcut。

ICL human video 和 robot multi-view video 共用 Wan VAE latent space。为防止两类视觉 token 的位置语义混淆，robot 使用原始坐标，人类 token 沿 height 轴平移

$$
pos_{robot}(q,y,x)=(q,y,x),
\qquad pos_{human}(q,y,x)=(q,y+\Delta_H,x),
$$

其中实现取 $\Delta_H=32$，大于 robot multi-view layout 的高度。

#### 3.3 In-Context Future Chunk Prediction

普通 next-chunk loss 很容易由最近的 robot history 预测，尤其是训练中反复出现的 seen tasks。IFP 从当前 robot-video representation 预测多个更远的 strided chunks。第 $k$ 个目标索引为

$$
j_k=(i+1)+1+(k-1)s,\qquad k=1,\ldots,K.
$$

主 video Transformer 的 $M$ 个中间层表示先 concat，再由 $P_{fuse}$ 投影成 $\boldsymbol\phi^{i+1}$。每个 IFP module $G_k$ 与单个 video Transformer layer 同构，并从主干最后一层初始化。各个未来目标并行预测，不在 IFP 支路内串联未来 chunk。每个模块用 $\boldsymbol\phi^{i+1}$ 预测 $\mathbf x^{j_k}$，损失为

$$
\mathcal L_{ifp}=\sum_{k=1}^{K}w_k\mathcal L_{fm}(\mathbf x^{j_k};\boldsymbol\phi^{i+1},\mathbf x^{\le i},\mathbf a^{\le i},\ell).
$$

IFP 不直接接收 $\mathbf h$，只接收已经和 human video 交互过的 $\boldsymbol\phi$。若让 IFP 直接看 human video，辅助支路可以独立学会 future prediction，而主支路仍然不读 prompt。IFP 只在训练时存在，推理时移除，所以它的作用是塑造主干表示，不是增加部署计算。

#### 3.4 Training and Inference

VA data 使用 language-only 条件 $c=\ell$，损失为

$$
\mathcal L_{VA}=\mathbb E[\mathcal L_{fm}^{i+1}(\ell)+\lambda_a\mathcal L_a^{i+1}(\ell)].
$$

HumanGen data 使用 $c=\{\mathbf h,\ell\}$，增加 IFP

$$
\mathcal L_{ICL}=\mathbb E[\mathcal L_{fm}^{i+1}(c)+\lambda_a\mathcal L_a^{i+1}(\ell)+\lambda_{ifp}\mathcal L_{ifp}].
$$

推理时有两种模式。language-only 只给文本，ICL mode 将 human video 编码一次并缓存 prefix memory，语言可以省略。两种模式都先生成下一段 robot video，再解码 action chunk。

### 4. Experiments

#### 4.1 Implementation

模型隐藏维度 $d_v=d_a=3072$，video Transformer 有 30 层，action branch 从 video branch 初始化。Wan VAE 编码人类和机器人视频，T5 编码语言。IFP 默认 $K=4$、$s=2$，权重 $(0.5,0.25,0.15,0.15)$。

预训练使用 AdamW，峰值学习率 $10^{-4}$、weight decay 0.01。VA 与 HumanGen 的 sampling ratio 是 1:5。非 ICL 样本 language dropout 为 0.1，ICL 样本 human-video latent dropout 为 0.1，language dropout 提高到 0.4。robot video chunk size 随机取 1 到 4，预训练耗费 15,360 GPU hours。RoboTwin post-training 用 64 GPUs、4000 steps，VA、HumanGen、RoboTwin 比例为 2:10:3。

#### 4.2 RoboTwin simulation 设置

RoboTwin 2.0 有 50 个 bimanual tasks，每 task 50 条 robot trajectories。按 task 切分，43 tasks 用于 post-training，7 tasks 完全留作 unseen evaluation。评测任务是 Place object on scale、Stamp seal、Open microwave、Move stapler to pad、Place bread in basket、Place empty cup 和 Stack blocks three。每个 unseen task、每个 seed 跑 100 个 closed-loop rollouts，三个 seed 取均值和标准差。

基线 WAN-Action 从同一个 Wan-2.2-TI2V-5B 初始化，只用 43 个 seen tasks 训练。LingBot-VA 使用公开预训练 checkpoint，再在同一 seen-task split 上 post-train。Zero-WAM 额外拥有 task-balanced VA 和大规模 HumanGen pretraining，比较应理解为完整训练配方对比，而非只换一个输入模态。

#### 4.3 主要仿真结果

| Task | WAN-Action | LingBot-VA | Zero-WAM |
| --- | ---: | ---: | ---: |
| Place object on scale | 3.00 ± 2.16 | 6.17 ± 4.87 | **24.67 ± 2.05** |
| Stamp seal | 7.33 ± 1.25 | 3.67 ± 2.49 | **47.00 ± 4.55** |
| Open microwave | 2.26 ± 1.60 | 29.33 ± 10.66 | **59.00 ± 2.83** |
| Move stapler to pad | 10.67 ± 1.70 | 23.33 ± 8.22 | **69.14 ± 2.93** |
| Place bread in basket | 15.26 ± 2.55 | 17.33 ± 6.18 | **35.00 ± 3.74** |
| Place empty cup | 38.33 ± 2.05 | 42.33 ± 7.85 | **84.87 ± 0.18** |
| Stack blocks three | 0.00 ± 0.00 | 0.00 ± 0.00 | **9.00 ± 2.16** |
| Average | 10.98 ± 1.07 | 17.45 ± 1.40 | **46.95 ± 0.72** |

Zero-WAM 相对 LingBot-VA 提升 29.50 个百分点，相对 WAN-Action 提升 35.97 个百分点，并在七个任务逐项胜出。Open microwave 和 Stamp seal 代表 articulated-object 与少见 relocation dynamics，Place empty cup 达到 84.87% 是最醒目的单项结果。Stack blocks three 仍只有 9%，说明长时程规划和误差积累没有被 IFP 完全解决。

![[papers/images/zhou2026zero-wam/ablation_icl_v1.1.png|760]]

#### 4.4 Real-world experiments

真机使用 bimanual Franka，三类 task family 各 30 次。Zero-WAM 在测试时只看 human video，语言可省略。LingBot-VA 则获得 detailed text instruction。每类任务都用少量 seen-task robot demonstrations 做本体适配，再把 object、container、顺序或插入位置留给测试组合。

| Task family | 训练组合 | 训练 demos | LingBot-VA | Zero-WAM |
| --- | ---: | ---: | ---: | ---: |
| Object-to-container placement | 30 | 120 | 43.3 | **53.3** |
| Three-object sequential manipulation | 16 | 96 | 10.0 | **33.3** |
| Two-table-leg insertion | n/a | 36 | 0.0 | **16.7** |

Object-to-container 测试至少包含一个未见 object 或 container。Three-object sequential manipulation 检验 human video 指定任意操作顺序的能力。Two-table-leg insertion 要从视频中读取颜色对应的孔位，绝对成功率低，但 Zero-WAM 在未见颜色和类型上仍有非零结果。

![[papers/images/zhou2026zero-wam/realworld_demo_v1.0.png|760]]

真机结果支持视觉任务规范的方向，却不支持严格的架构归因。Zero-WAM 看到一段视频，LingBot-VA 看到详细文字，输入信息量和表达形式都不同。

#### 4.5 Ablation Studies

所有消融都使用相同的 43 seen tasks、7 unseen tasks 和 RoboTwin 闭环协议。

##### Human video ICL

只用 43 seen tasks 训练时，WAN-Action 的平均成功率为 10.98%，Zero-WAM w/o pretrain 但加入 human video ICL 后为 36.36%，LingBot-VA 为 17.45%。这说明 ICL video 提供了 text-only 条件之外的 task information。三者在 Stack blocks three 都为 0，完整 Zero-WAM 的 9% 来自大规模 task-diverse pretraining 与 IFP 的组合，而不是少量 ICL 就足够。

##### IFP

完整模型平均 46.95%，去掉 IFP 后为 28.55%。Open microwave、Stamp seal 的提升尤其大，Stack blocks three 从 0 到 9%。这组对照直接回应 shortcut 假设，说明让模型预测更远未来确实能把 human prompt 的语义压进主 video representation。

##### Task-balanced robotic pretraining

text-only Zero-WAM variant 把 HumanGen pair 中的 human condition mask 掉，只保留机器人视频动作和文本。它达到 39.44%，比 LingBot-VA 高 21.99 个百分点。这个结果支持按任务重采样的价值，但不能把 39.44% 解释成纯人类视频收益。

![[papers/images/zhou2026zero-wam/ablation_data_and_ifp_v1.0.png|760]]

### 5. Conclusions and Discussions

作者的结论是，human video、task-balanced robot data 和 causal WAM 可以组成一个部署时不更新参数的 task interface。人类示范提供状态变化，机器人轨迹提供可执行监督，未来视频把二者连接起来。论文也承认当前实验主要是 stationary tabletop manipulation，下一步要扩展到 mobile manipulation、动态环境和更长时序。

这里最需要保留的是「zero-shot」的定义。仿真 unseen task 没有目标任务 robot demonstrations，但生成 HumanGen prompt 的源轨迹来自这些 task。真机还有 252 对 Real-world ICL 用于 Franka 适配。因此它是没有目标任务机器人示范和不更新部署参数，不是没有任何任务相关信息或本体数据。

### 6. Related Works

Cross-task work 如 AGNOSTOS 需要在测试时提供 unseen task 的 robot trajectory 作为 reference，Zero-WAM 试图把 reference 换成 human video。WAM 系列通过预测 future visual states 再解码动作，把泛化难点从直接语言到动作转成视频生成。WAM-TTT 在部署时更新轻量 memory，Zero-WAM 则把 human-robot ICL pair 放进预训练和 post-training，推理时不做 test-time adaptation。Human video data 方向还包括 EgoMimic、BC-Z、EgoScale 和 EgoWAM，它们或依赖手工采集，或使用不同的 representation supervision，Zero-WAM 的差异在于自动生成大任务覆盖的 ICL pair。

## 方法细节汇总

| 组件 | 输入 | 输出 | 训练时机 | 部署时机 |
| --- | --- | --- | --- | --- |
| Task-diverse VA | 多源 robot trajectories | 平衡采样的 video-action corpus | 预训练和 post-training | 不直接输入 |
| HumanGen | robot video、VLM 状态解析 | human video + paired robot trajectory | 生成 ICL 数据 | human video 作为 prompt |
| Video Transformer | robot history、action history、human prefix、text | 下一段 robot video | flow-matching 训练 | autoregressive chunk generation |
| Action Transformer | robot history、预测 robot video、text | 下一段 action chunk | flow-matching 训练 | inverse dynamics decoding |
| RoPE offset | human 与 robot visual latent | 分离的位置坐标 | 固定结构 | 固定结构 |
| IFP modules | fused current video representation | 多个 strided future video chunks | 辅助训练 | 删除 |

### 训练配置速查

| 项目 | 值 |
| --- | --- |
| Backbone | Wan-2.2-TI2V-5B |
| Video / action hidden dim | 3072 / 3072 |
| Video Transformer layers | 30 |
| IFP | $K=4$，$s=2$ |
| IFP weights | 0.5、0.25、0.15、0.15 |
| VA : HumanGen sampling | 1 : 5 |
| Language dropout | 非 ICL 0.1，ICL 0.4 |
| Human latent dropout | 0.1 |
| Pretraining compute | 15,360 GPU hours |
| RoboTwin post-training | 64 GPUs，4000 steps，2:10:3 |
| Inference chunk size | 2 |
| Video CFG / ICL CFG | 5 / 5 |
| Action CFG | 1.0 |

## 实验设置、数据集、基线、指标

主仿真是 task-level split，不是随机轨迹 split。43 个 seen tasks 用于 post-training，7 个 unseen tasks 只在评测出现。每个 seed 每 task 100 次 closed-loop rollout，报告 success rate 的均值和标准差。真机三类任务各 30 次，报告二值 success rate，没有同时给出置信区间。

基线强度并不完全对齐。WAN-Action 只有 Wan backbone 和 seen-task post-training，LingBot-VA 有公开机器人 video-action pretraining，Zero-WAM 还加入 74.2K HumanGen pairs 与 task-balanced VA。真机方面，Zero-WAM 用 human video，LingBot-VA 用 detailed text。这些条件必须写在结果旁边，否则容易把数据、输入接口和架构收益混为一谈。

## 主要结果、消融或对比

最有说服力的主结果是七个 unseen task 全部胜出，且平均标准差只有 0.72 个百分点。最能说明机制的消融是 IFP 28.55% 到 46.95%，以及 ICL-only 36.36% 对 text-only 10.98%。最重要的反例是 Stack blocks three 只有 9%，表明 human video 不能自动解决长时程 credit assignment 和视频生成误差。

## 图表、公式与表格线索

| 图表 | 读图重点 | 证据级别 |
| --- | --- | --- |
| Fig. 1 framework | 数据管线、human prompt、未来视频和动作解码的总览 | 方法示意 |
| Fig. 2 data composition | VA 与 HumanGen 的来源和比例 | 数据构造 |
| Table 1 dataset comparison | 任务数、视角、自动生成和视觉对齐多样性 | 规模对照 |
| Fig. 3 unseen tasks | 七个 RoboTwin task 的类型 | 评测覆盖 |
| Table 2 RoboTwin main | 7 task success 与均值标准差 | 主闭环证据 |
| Table 3 real world | 三类 task family 的 30-trial 结果 | 小规模真机证据 |
| Fig. 4 ICL ablation | 只用 seen tasks 时 human video 的增益 | 接口消融 |
| Fig. 5 data/IFP ablation | task-balanced data 与 IFP 的独立作用 | 机制消融 |
| Eq. flow matching | 视频和动作的生成目标 | 训练定义 |
| Eq. factorization | 未来视频到动作的概率分解 | 架构接口 |
| Eq. RoPE offset | 人类与机器人 latent 的位置分离 | 表示设计 |
| Eq. IFP | strided future chunk 的监督路径 | shortcut 抑制 |

## 主张-证据-边界矩阵

| 主张 | 证据 | 边界 |
| --- | --- | --- |
| human video 比 text-only 更能指定 unseen task | ICL-only 36.36% 对 WAN-Action 10.98% | ICL prompt 是从对应 task trajectory 生成的 |
| Zero-WAM 优于 video-action baseline | 46.95% 对 LingBot-VA 17.45% | Zero-WAM 训练数据和输入接口都更丰富 |
| IFP 解决 human prompt 被忽略的问题 | 46.95% 对 28.55%，Stack blocks three 9% 对 0% | 只在一个 $K,s,w$ 配置上验证 |
| task-balanced VA 有独立收益 | text-only 39.44% 对 LingBot-VA 17.45% | 变体保留其他 Zero-WAM 训练设计 |
| 能迁移到真机未见配置 | 三类任务 53.3%、33.3%、16.7% | 每类 30 次，且基线使用 text |
| 自动生成 HumanGen 可规模化 | 74.2K pairs、8.6K tasks | 没有公开质量审计、真实视频对照和发布材料 |

## 局限与可追问点

论文明确承认环境主要是 stationary tabletop，真实部署还需要更动态、更长的任务。阅读时还应追问以下边界。

- HumanGen 的 VLM、image editor 和 video generator 都可能把源 robot trajectory 的答案带进 prompt。生成视频是否真的提供了额外信息，还是把已有标签换一种外观，需要真实人类视频或严格的 source-held-out 对照。
- 论文没有报告生成视频的 rejection rate、人工评分一致性、物理伪影和时间连续性。VLM 自评不等于独立质量标注。
- unseen task 的准确含义是没有目标任务 robot demonstrations。源轨迹被用于生成 human prompt，不能写成完全无任务信息的 zero-shot。
- 真机输入不对称，Zero-WAM 用 video，LingBot-VA 用 detailed text。需要同一模型同时比较 text-only 与 human-video，才能隔离接口和骨干的贡献。
- Real-world ICL 有 252 对，且用于 Franka embodiment adaptation。部署时不更新参数不等于训练阶段没有本体适配。
- action branch 依赖预测 robot video，autoregressive video error 会逐 chunk 累积。Stack blocks three 的 9% 是这个风险的直接信号。
- IFP 的未来跨度、模块数和权重没有完整 sensitivity study。更远预测可能强化长期语义，也可能增加不必要的视觉负担。
- 15,360 GPU hours、5B backbone 和外部生成模型使复现困难。截至 2026-09-01，GitHub 尚未公开完整 code、weights 和 datasets，README 预计 2026-09-15 前发布。

说真的，这篇论文最扎实的贡献是把 human video 变成一个可训练的 task interface，而不是宣称视频本身解决了泛化。数据平衡、IFP 和 video-to-action factorization 各自有证据，生成数据的真实性和真机比较的公平性仍在摸索。

## 与当前库的连接

与 [[@feng2026wam-ttt]] 相比，Zero-WAM 把 human video 的使用前移到预训练和 post-training，部署时不更新 memory；WAM-TTT 则用测试时快权重适配未标注人类视频。与 [[@dyna2026dyna2]] 的人类视频规模化路线相近，但 Zero-WAM 关注的是视频作为 task prompt，Dyna-2 更关注跨本体预训练的 scaling law。与 [[@zhang2026lingbot-va2]] 相比，Zero-WAM 在模型里显式保留 human prefix 和 IFP。与 [[@generalist2026gen15]]、[[@paliwal2026do-i-dexterous-manipulation]] 的 human demonstration 接口相邻，但这里的评测核心是 task-level unseen，而不是已知任务的视觉变体。

把它和 [[@tan2026rl2-vla]] 放在一起时，两个问题不要混为一谈。RL$^2$-VLA 在已知 task 上处理 prompt、environment 和 object shift，改的是推理时 action candidate 分布。Zero-WAM 没有目标 task 的机器人训练示范，改的是训练期 task interface 和 WAM 结构。前者回答「什么时候增加动作多样性」，后者回答「怎样把新任务说明交给机器人」。

## 精读路线 / 为什么需要回看

回看可以沿数据、接口、辅助目标和证据四个切面推进。先看 Fig. 2 和 HumanGen 子集，确认哪些数据是真实机器人轨迹、哪些是生成视频。再沿 Eq. factorization 读 human video 到 predicted robot video 到 action 的信息流，核对 action branch 是否直接看 human prompt。接着重算 IFP 和 ICL ablation，判断增益来自 prompt、数据平衡还是 shortcut 抑制。最后把 RoboTwin 和真机表格放在输入不对称、任务级切分和 30-trial 统计的条件下解释。

如果要复现，优先固定 task split、HumanGen 生成模型、RoPE offset、IFP 的 $K/s/w$、CFG scale 和 post-training 数据比例。缺少这些细节时，复现出来的模型可能只是普通 video-action policy，不再是论文定义的 Zero-WAM。

```dataviewjs
const {Research} = customJS
Research.topic(dv)
```
