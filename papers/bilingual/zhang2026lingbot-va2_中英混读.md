---
tags:
  - bilingual-reading
  - deep-reading
  - video-action-model
  - world-action-model
paper: "[[@zhang2026lingbot-va2]]"
source_pdf: "[[papers/pdfs/zhang2026lingbot-va2.pdf]]"
images: "papers/images/zhang2026lingbot-va2/"
image_index: "[[papers/images/zhang2026lingbot-va2/index.md]]"
created: 2026-07-15
reading_mode: 复现级人工精读（全文 + 公式 + 表格 + 系统链路）
---

# Native Video-Action Pretraining for Generalizable Robot Control

paper:: [[@zhang2026lingbot-va2]]
pdf:: [[papers/pdfs/zhang2026lingbot-va2.pdf]]
images:: [[papers/images/zhang2026lingbot-va2/index.md]]

## 核心词汇速查

| English | 中文 | 在本文中的精确作用 |
| --- | --- | --- |
| Video-Action (VA) model | 视频—动作模型 | 联合建模未来视觉 latent $z_{t+1}$ 与促成该转移的动作 chunk $a_t$；不是只从当前图像直接回归动作。 |
| native pretraining | 原生预训练 | tokenizer 和 causal DiT 从头按控制需求训练，而非把双向视频生成器事后改成因果策略。 |
| semantic visual-action tokenizer | 语义视觉—动作 tokenizer | SemVAE 同时优化像素重建、foundation-feature alignment 和无标签 latent action tokenization。 |
| latent action $\ell_t$ | 潜动作 | IDM 从 $(z_t,z_{t+1})$ 压缩出低维转移变量；FDM 用它重建前/后 visual latents。 |
| Mixture-of-Transformers (MoT) | Transformer 混合流 | video/action 两条 expert stream 共享 causal self-attention，但拥有不同宽度、FFN、归一化与输出头。 |
| sparse video MoE | 稀疏视频专家 | video FFN 使用 128 routed experts、Top-8 + shared expert；action FFN 保持 dense。 |
| Multi-Chunk Prediction (MCP) | 多块预测 | 三个辅助模块从主干中间特征预测 next1/2/3 chunks，防止高帧率下仅复制相邻外观。 |
| in-context video prompt | 上下文视频提示 | 完整人类演示 latent $z_{icl}$ 作为外部 task prompt，供每个 robot chunk cross-condition。 |
| HCT | 人—机器人协同训练 | 将人手 6-DoF root + finger joints 映射到双臂 EEF + scalar gripper layout，骨干共享、action heads 分域。 |
| Foresight Reasoning | 前瞻推理 | 机器人执行当前 chunk 时并行想象其结果并生成下一 chunk；真实观察返回后覆写 imagined cache。 |
| consistency distillation | 一致性蒸馏 | 将 video 5-step、action 10-step flow samplers 均压到 2-step，降低每 chunk 延迟。 |
| asynchronous control frequency | 异步控制频率 | $1000/t_{chunk}\times K$；衡量 chunk 生成被执行摊薄后的控制步率，不等同于传感—动作端到端 latency。 |

## 摘要

LingBot-VA 2.0 认为第一代 video-action policy 的根本问题在“出生方式”：通用视频生成模型以 reconstruction VAE 压缩画面，再以 bidirectional video diffusion 生成数字内容；之后才用稀缺机器人数据改成 causal attention 并外挂 action module。这会产生三类错位：latent 保留像素外观但缺乏动作/物理语义；双向预训练与只能向前闭环的控制方向相反，continued training 可能 catastrophic forgetting；高维视频 token + 多步 denoising 使机器人必须等待模型，推理延迟直接变成控制停顿。

作者从头训练两阶段 stack。第一阶段 Semantic Visual-Action Tokenizer：ViT autoencoder 负责 video compression，同时把 temporally pooled latent 对齐冻结 Perception Encoder；再冻结视觉 tokenizer，用 inverse dynamics model 从相邻 visual latents 提取低维 latent action $\ell_t$，用 forward/reverse dynamics 重建下一/上一 latent。第二阶段 15.3B causal video-action DiT：video/action 两流共享 causal attention，video stream 是 13B 总参数、1.9B active 的 sparse MoE，action stream 约 0.6B dense；模型用 flow matching 联合预测 future video latent 与 action。

为了从“预测下一帧”升级到“理解轨迹动力学”，MCP 从主干多层特征预测额外 1--3 个 future chunks；人类演示视频可作为 ICL task prompt；ego human actions 通过 hand-to-gripper retargeting 与 robot data 共训。部署时 Foresight Reasoning 将 prediction stream 与 execution stream 并行：当前动作执行期间先用 policy FDM imagined $\hat z_{t+1}$ 生成 $a_{t+1}$，真实 $z_{t+1}$ 到达后覆写 KV cache，保持 closed loop。配合 2-step consistency distillation、FP8 TensorRT、paged/ragged KV cache 和 runtime amortization，chunk latency 927→142 ms，论文按 $K=32$ 计算 async frequency 35→225 Hz。

## 论文主线

```text
Raw images / web videos / robot videos / ego-human videos
→ [Semantic Visual Tokenizer] reconstruction + foundation alignment
→ visual latents z
→ [Latent Action Tokenizer] IDM(z_t,z_{t+1}) + FDM/reverse-FDM
→ paired (z_t, latent action ℓ_t)
→ [Causal MoT: video-MoE + dense action stream]
→ future latent z_{t+1} + action chunk a_t
   ↘ MCP(next1,next2,next3) / ICL(z_icl) / HCT
→ [Consistency distillation + TensorRT/KV optimization]
→ [Foresight] imagine ahead while executing → real observation re-ground
```

核心区别是：**future video 不只是给人看的可视化，而是 action 的中间因果变量。** Eq.(5) 先建模 $p(z_{t+1}|history)$，再建模 $p(a_t|history,z_{t+1})$，后者是 inverse dynamics：知道“世界应到哪里”，再解码“要做什么动作到那里”。

## 1. 🎯 核心思想与动机（The “Aha!” Moment）

### 痛点与动机

把通用视频生成器改成机器人策略，相当于让一个“会补全漂亮视频、可偷看前后帧”的模型临时学习“只能看过去、还必须实时输出动作”；它的 latent、attention 因果结构和计算预算都不是为控制设计的。

### 核心思想

大白话说，作者把“眼睛看到的世界”和“手做的动作”先翻译进同一种语义 latent 语言，再训练一个只能从过去向未来写的世界—动作模型。执行时不让机器人干等：模型一边让机器人做当前 chunk，一边根据当前 action 预演下一状态并准备下一动作；等真实摄像头回来，立刻用真实状态改掉预演草稿。这样既隐藏推理时间，又不把长期 rollout 变成脱离现实的幻想。

## 2. ✨ 核心贡献梳理（Contributions）

- 提出 native video-action pretraining：从头训练 semantic visual-action tokenizer 与 causal DiT，使 web-scale image/video 的外观、动态和 latent-action 监督在原生因果结构中获得，而不是 bidirectional-to-causal retrofit。
- 构建共享语义 visual-action latent：visual tokenizer 用 reconstruction + Perception Encoder alignment；latent-action IDM/FDM 在无动作标签视频上从转移自监督发现紧凑动作变量。
- 设计大容量高效 causal VA architecture：MoT 共享 joint attention，video stream 使用 128 experts Top-8 MoE；MCP 在三个 horizon 提供密集未来监督；ICL/HCT 将人类视频作为 task context 与低成本 embodied data。
- 提出 Foresight Reasoning 与完整加速栈：预测/执行并行、每 chunk 真实观测重接地；two-step consistency、FP8 TensorRT、paged KV/FlashInfer 和 runtime cache 使 async control frequency 达 225 Hz。

## 贡献与结论对照

| 主张 | 方法位置 | 证据 | 结论边界 |
| --- | --- | --- | --- |
| semantic tokenizer 比 reconstruction VAE 更适合控制。 | §2.2，Eq.(9)--(14)。 | Table 2：50 tasks average 78.0/76.0→86.6/83.1（Easy/Hard）。 | 1.3B 下游模型；alignment 与 latent action 的贡献未分别消融。 |
| MCP 促进长时预测和训练效率。 | §2.3.3，Eq.(20)--(23)。 | Fig.10：50 FPS random 5k 时 +29.7 pp；20k 匹配 baseline 45k，2.3×。 | 训练曲线证据强；部署时 MCP 默认丢弃。 |
| native VA 提升通用控制。 | §4.2--4.3。 | RoboTwin 93.6 avg；真实四任务均高于 baselines。 | 真实 benchmark 内部，缺少置信区间。 |
| 实时异步控制。 | §2.3.7/2.4，Table 3。 | 927→142 ms/chunk，35→225 async Hz。 | Hz 是 chunk amortized，不能当单步响应延迟。 |

## 结构地图

| 原文 section | 作用 | 关键线索 |
| --- | --- | --- |
| §1 | 反驳“视频生成器 + action head”范式。 | Fig.1。 |
| §2.1 | 用概率分解定义 video generation、causality、action injection。 | Eq.(1)--(8)。 |
| §2.2 | SemVAE 与 latent action tokenizer。 | Eq.(9)--(14)，Fig.2。 |
| §2.3.1 | 2Hz VLM planner 与 JSON subtask interface。 | Fig.3。 |
| §2.3.2 | asymmetric MoT + 128-expert video MoE。 | Eq.(15)--(19)，Fig.4。 |
| §2.3.3 | MCP 预测 3 个 future chunks。 | Eq.(20)--(23)，Fig.5。 |
| §2.3.4--2.3.6 | ICL、human-robot co-training、五任务 curriculum。 | Eq.(24)--(28)，Fig.7。 |
| §2.3.7--2.4 | 异步 predict-correct、distillation、推理优化。 | Eq.(29)--(32)，Fig.6。 |
| §3--4 | 数据、架构超参、真实/仿真/消融。 | Tables 1--3，Figs.8--11。 |

## 3. ⚙️ 方法论全景与精细拆解（Detailed Pipeline & Module Breakdown）

### 模块 1：Semantic Visual Tokenizer（SemVAE 视觉分支）

**物理/数学意义。** 将 raw video 压成可生成的 latent，同时让 latent 携带 foundation model 的语义，而不是只保留像素纹理。

**输入。** video clip $o_{1:T}\in\mathbb R^{T\times H\times W\times3}$。首帧切成 $16\times16$ spatial patches；后续帧切成 $4\times16\times16$ spatiotemporal tubelets。

**内部机制。** causal ViT encoder $E$ 允许 frame 内 full spatial attention、frame 间 causal attention，输出 $z=E(o)\in\mathbb R^{T'\times h\times w\times c}$；symmetric decoder $D$ 重建 $\hat o$。重建目标：

$$\mathcal L_{rec}=\lambda_1\|o-\hat o\|_1+\lambda_{perc}\mathcal L_{perc}(o,\hat o)+\lambda_{gan}\mathcal L_{gan}(\hat o).\tag{9}$$

冻结 Perception Encoder $G$ 提取 teacher features，投影 $W_{align}z$ 后做 temporal average，以 L2 对齐：

$$\mathcal L_{align}=\|\operatorname{avg}(W_{align}z)-\operatorname{avg}(G(o))\|_2^2,\quad
\mathcal L_{vis}=\mathcal L_{rec}+\lambda_{align}\mathcal L_{align}.\tag{10--11}$$

temporal pooling 只约束 clip-level semantic，不直接牺牲 frame-wise reconstruction。

**输出。** 96-channel semantic visual latents $z_{0:N}$，传给 latent-action tokenizer 和第二阶段 causal DiT。

### 模块 2：Latent Action Tokenizer（IDM + FDM）

**物理/数学意义。** 从“前后状态差”中抽取低维、控制相关的 transition variable，使没有 robot action label 的 web/human video 也能提供 action-like supervision。

**输入。** 冻结 visual tokenizer 输出的相邻 $z_t,z_{t+1}$。

**内部机制。** inverse dynamics model：

$$\ell_t=q_\phi(z_t,z_{t+1})\in\mathbb R^{d_\ell},\qquad d_\ell\ll\dim z_t.\tag{12}$$

低维 bottleneck 防止 $\ell_t$ 偷拷完整视觉状态。forward dynamics 将 $\ell_t$ 解码成 transport map $K_t$ 和 residual $\delta_t$：

$$\hat z_{t+1}=f_\psi(z_t,\ell_t)=K_tz_t+\delta_t.\tag{13}$$

$K_t$ 搬运 spatial token information，$\delta_t$ 表达无法由 transport 解释的 appearance/state changes；reverse FDM $\bar f_\psi(z_{t+1},\ell_t)$ 重建 $z_t$：

$$\mathcal L_\ell=\sum_t\left(\|\hat z_{t+1}-z_{t+1}\|_2^2+\|\hat z_t-z_t\|_2^2\right).\tag{14}$$

**输出。** paired $(z_{0:N},\ell_{0:N-1})$；第二阶段记 $a_t\equiv\ell_t$。注意：在真正 robot policy post-training 中还需解码 raw robot actions，latent action 不是直接下发控制量。

### 模块 3：Chunk-aligned Video-Action Probabilistic Factorization

**物理/数学意义。** 让视觉时间分辨率与机器人高频 action 对齐。tokenizer temporal downsample factor 为 $f_t$，两个 visual latents 间的 $f_t$ 个低层动作组成一个 chunk：

$$a_t=u_{tf_t:(t+1)f_t-1}.\tag{3}$$

**输入。** initial visual latent $z_0$，历史 $z_{\le t},a_{<t}$，语言条件。

**内部机制。** block-causal factorization：

$$p_\theta(z_{1:N},a_{0:N-1}|z_0)=\prod_{t=0}^{N-1}
p_\theta(z_{t+1}|z_{\le t},a_{<t})
p_\theta(a_t|z_{\le t},a_{<t},z_{t+1}).\tag{5}$$

第一项是 forward world dynamics；第二项是 inverse dynamics action decoding。两流分别以 rectified flow training：对 $x\in\{z_{t+1},a_t\}$ 采噪声 $\epsilon$ 和 $s\in[0,1]$，$x^{(s)}=(1-s)\epsilon+sx$，预测 velocity $x-\epsilon$。总 $\mathcal L_{VA}=\mathcal L_{vid}+\lambda_{act}\mathcal L_{act}$。

**输出。** denoised future visual chunk 与对应 raw/latent action chunk。

### 模块 4：Hierarchical VLM Planner

**物理/数学意义。** 低层 VA 只执行一个 subtask；长任务需要显式状态机判断“当前子任务完成了吗、下一步是什么”。

**输入。** 三个 keyframes $I_{t^*-2s},I_{t^*-1s},I_{t^*}$、episode goal、已完成 segment 文本历史 $g_0\ldots g_{i-1}$，以及 done=false 时的 current subtask。

**内部机制。** 冻结 vision tower，对 pretrained VLM 做 LoRA；task-balanced boundary-crossing sampling 生成两类样本：在 segment 内 target `done=false` 并复述 $g_i$；刚跨 $g_i\to g_{i+1}$ 时 target `done=true` 并预测 $g_{i+1}$。输出 JSON 包含 `done`, `instruction`, `generation_instruction`, `local_scene_description`。planner 约 2 Hz 后台运行，通过 async shared buffer 写 context；policy 每个 action-chunk boundary 读取最新值。

**输出。** 三个低层 text conditioning fields；`done` 仅供 scheduler，不直接输入 policy。schema 必须与 policy 训练文本严格一致，否则 inference condition OOD。

### 模块 5：Causal MoT 与 Sparse Video MoE

**物理/数学意义。** video dynamics 需要大容量，action decoding 更窄；两流共享“看同一历史”的 attention，却不强迫相同 FFN/宽度。

**输入。** video tokens hidden 2048D、action tokens hidden 768D、text tokens、video/action independent diffusion timesteps。

**内部机制。** 30 transformer blocks。video/action QKV 分别从 2048/768 投影到 shared 3072D（24 heads×128），做 block-causal joint self-attention，再投回各自宽度。cross-attention 的 action 有独立 Q/output，但与 video 共享 text K/V。video FFN 使用 $N_e=128$ routed SwiGLU experts + 1 shared expert，Top-$k=8$：

$$r_i(h)=\sigma(g_i^\top h),\quad R(h)=\operatorname{GroupTopK}(r(h)+b,k),\tag{15--16}$$
$$\alpha_i(h)=\gamma\frac{r_i(h)}{\sum_{j\in R(h)}r_j(h)},\quad
\operatorname{MoE}(h)=E_{shared}(h)+\sum_{i\in R(h)}\alpha_iE_i(h).\tag{17--18}$$

每 expert intermediate 512。bias 只选 expert，不改权重；按 token count $c_i$ 做 centered sign update：

$$b_i\leftarrow b_i-\eta_{lb}\left[\operatorname{sign}(c_i-\bar c)-\frac1{N_e}\sum_j\operatorname{sign}(c_j-\bar c)\right].\tag{19}$$

action FFN dense 3072D。video backbone 约 13B total/1.9B active，action expert 0.6B，标准 inference active 约 2.5B/token。

**输出。** video/action hidden states，分别进入 96×4 latent-channel video head 与 30D action head。

### 模块 6：Multi-Chunk Prediction（MCP）

**物理/数学意义。** 高 FPS 时 $z_{t+1}\approx z_t$，只预测 next chunk 可以靠 appearance copying 降 loss；MCP 强迫当前 representation 对更远轨迹状态有预测力。

**输入。** main DiT layers {3,11,19,29} 的 hidden states，clean history，next1/2/3 的 noisy visual latent targets。

**内部机制。** 四层特征 concat 后经两层 SiLU MLP $4\times2048\to2048\to2048$。三个 horizon modules 各含 3 transformer blocks；第 $k$ 个不看 clean/predicted intermediate future，而看前一个 MCP feature $h_t^{(k-1)}$ 与自己的强噪声 target：

$$p(z_{t+1:t+K}|history)\approx\prod_{k=1}^Kp_{\theta,k}(z_{t+k}|h_t^{(k-1)}).\tag{21}$$

每个 horizon 用同一 flow-matching loss $\mathcal L_k^{MCP}$，$K=3$，总权重 $(w_1,w_2,w_3)=(0.5,0.2,0.1)$：

$$\mathcal L_{MCP}=\sum_{k=1}^3w_k\mathcal L_k^{MCP}.\tag{23}$$

更大的 timestep shift 让 module 不能从 noisy target 自己恢复，必须利用主干 representation。梯度通过 fusion 回主干；默认 inference 丢弃 MCP heads，零额外成本。

**输出。** 训练期三个 future velocity predictions；推理期只留下被未来监督塑形的 backbone。

### 模块 7：Video ICL 与 Human–Robot Co-training

**物理/数学意义。** 语言难完整描述 rare-object、多物体和长程序；人类视频能展示 procedure。与此同时，人类 ego data 便宜，但动作空间和运动学不同，需共享 world model、隔离低层 action heads。

**输入。** ICL：完整 human demo 经 tokenizer 得 $z_{icl}$，robot trajectory $(z_{0:N},a_{0:N-1})$。HCT：robot set $D_R=(o,a_R)$ 与 human set $D_H=(o,\tilde a_H)$；人手每侧 6-DoF root + 22 finger joints。

**内部机制。** ICL 中 $z_{icl}$ 对每个 robot chunk 全可见，它来自独立 demo，不是 robot future，因此不违反 robot causal mask：

$$\prod_t p(z_{t+1}|z_{\le t},a_{<t},z_{icl})p(a_t|z_{\le t},a_{<t},z_{t+1},z_{icl}).\tag{24}$$

HCT 映射 $a_H=\Phi(\tilde a_H)$：保留两手 6-DoF roots，以 virtual parallel gripper 将 thumb 与四指 envelope 沿 closing direction 的距离变成 metric aperture，并按数据集 quantile normalize；其余 30D layout 缺失维 padding+mask。共享 video/action experts，但人/机器人各自使用 $E_d,P_d$：

$$\hat a_t^{(d)}=P_d\,v^{act}(z_{\le t},E_d(a_{<t}),\hat z_{t+1}),\tag{26}$$
$$\mathcal L_{co-train}=\mathbb E_{D_R}[\mathcal L_{vid}+\mathcal L_{act}^R]+\mathbb E_{D_H}[\mathcal L_{vid}+\mathcal L_{act}^H].\tag{27}$$

**输出。** ICL-conditioned robot action；HCT 训练后的共享 backbone。部署只保留 robot branch，无 HCT 推理开销。

### 模块 8：五任务 Joint Curriculum

**物理/数学意义。** 纯 staged T2I→T2V→robot 容易在稀缺机器人阶段忘掉 web priors；让所有任务始终存在，只平滑改变采样概率。

**输入。** T2I、T2V、TI2VA、ICL、HCT 五类 batch。

**内部机制。** 进度 $\tau\in[0,1]$ 时：

$$\mathcal L(\tau)=\sum_{i\in\mathcal T}\pi_i(\tau)\mathcal L_i,\quad\sum_i\pi_i(\tau)=1.\tag{28}$$

早期 $\pi$ 偏 T2I，随后偏 T2V，晚期偏 TI2VA/ICL/HCT；早期任务后期仍有小的非零概率。所有任务共享 semantic latent 和 causal DiT。

**输出。** 同时保留语言—图像、一般视频动态和 embodied control 的 pretrained checkpoint。

### 模块 9：Foresight Reasoning（异步 Predict–Correct）

**物理/数学意义。** 将模型 latency 隐藏在机器人当前 chunk 的物理执行时间里，同时每轮用真实 observation 阻止 imagined rollout 累积漂移。

**输入。** feedback-grounded KV cache $C_t=(z_{\le t},a_{<t})$、正在执行的 $a_t$、异步 observation queue。

**内部机制。** 执行 $a_t$ 时临时 append 到 cache：$C_{tmp}=C_t\cup\{a_t\}$；policy video expert 作为在线 FDM：

$$\hat z_{t+1}=v_\theta^{vid}(z_{\le t},a_{\le t}).\tag{29}$$

action expert 以 $C_{tmp},\hat z_{t+1}$ 先生成 $a_{t+1}$。真实 observation 返回后编码成 $z_{t+1}$，覆写 stale $\hat z_{t+1}$，连同已执行 $a_t$ 形成 $C_{t+1}$。post-training 用额外 $\mathcal L_{FDM}$ 训练 video expert，使条件从标准 $a_{<t}$ 改为含 executed $a_t$ 的 $a_{\le t}$（Eq.30）。

**输出。** 在当前 chunk 完成前准备好的下一 action chunk；cache 始终周期性 grounded 到真实世界。

### 模块 10：Consistency Distillation 与部署加速

**物理/数学意义。** 原 video/action samplers 分别 5/10 denoise steps，无法实时；一致性模型直接将 PF-ODE 上任意噪声点映射到同一 clean endpoint。

**输入。** frozen teacher velocity $v_\theta$、clean $x$（video latent 或 action chunk）、noise $\epsilon$、相邻 grid $s_n,s_{n+1}$。

**内部机制。** 构造 $x(s_n)=(1-s_n)\epsilon+s_nx$，teacher Euler 一步：

$$\hat x(s_{n+1})=x(s_n)+(s_{n+1}-s_n)v_\theta(x(s_n),s_n).\tag{31}$$

student $f_\xi$ 与 EMA stop-gradient target $f_{\xi^-}$ 做 squared-L2 consistency：

$$\mathcal L_{CD}=\mathbb E[d(f_\xi(x(s_n),s_n),f_{\xi^-}(\hat x(s_{n+1}),s_{n+1}))].\tag{32}$$

两流都蒸馏为 2 steps。随后 DiT 转 ONNX/TensorRT；block linear FP8、head/tail BF16；显式输入输出 KV cache；paged/ragged preallocated cache + FlashInfer attention；缓存 binding/shape/tensor/text-KV/frame-id/scheduler metadata，并去 CPU-GPU sync。

**输出。** 142 ms/chunk 的部署 engine；按 $K=32$ 低层控制步折算 225 async Hz。

## 4. 🎬 端到端运行实例（End-to-End Running Example）

### 场景设定

机器人执行 Plate Handover：先把盘子推到桌中央，拿起纸垫放到盘中，再拿目标物放在纸垫上。当前 RGB 显示盘子偏左、纸垫在右前、目标物靠后；robot state 是统一 30D action layout，对本体有效的双臂 EEF 6-DoF×2、双 gripper 等槽位有值。planner 收到总目标。

### 数据流转推演

**Step 1：高层规划。** 2Hz planner 读取 $t-2s,t-1s,t$ 三帧、task goal 和已完成历史，输出 JSON：`done=false`, `instruction="Push the plate to the center"`, `generation_instruction="Use the right gripper to contact the rim and translate the plate..."`, `local_scene_description="Plate is left of center..."`。policy 在下一个 chunk boundary 读入三段文本。

**Step 2：视觉 tokenization。** 当前 observation 进入 SemVAE，首帧 16×16 patches 编码为 96-channel visual latents $z_t$。训练时 $\mathcal L_{rec}$ 保证可解码，$\mathcal L_{align}$ 让盘子、纸垫等对象语义在 latent 中清晰；推理只运行 encoder。

**Step 3：构造两流 token。** video latent 以 $1\times2\times2$ patch embedding 变成 2048D video tokens；30D quantile-normalized robot state/action context 经 bias-free linear 变成 768D action tokens；UMT 将三段 planner 文本编码为最多 512 个 4096D tokens，再投影进入 cross-attention。

**Step 4：Causal MoT Forward。** 30 blocks 中 video/action QKV 各自升到 3072D，在最多 64 chunks 的 block-causal window 做 joint attention。每个 video token 由 router 在 128 experts 里选 8 个，加 shared expert；action token 走 dense FFN。video head 通过 2-step sampler想象“右夹爪接触并推动后，盘子位于中央”的 $\hat z_{t+1}$。

**Step 5：Inverse-dynamics action decoding。** action stream 以 history 和 $\hat z_{t+1}$ 为条件，2-step sampler 输出一个 $K=32$ 的 raw action chunk $a_t\in\mathbb R^{32\times30}$。反 quantile normalization 后，有效维具体成为左右 EEF 的 6-DoF 增量与 gripper aperture；padding/masked 维不下发。

**Step 6：Foresight 并行。** robot 开始执行 $a_t$。同时 inference branch 把 $a_t$ append 到 grounded cache，用 Eq.(29) 预测执行后的 visual latent，并预先生成 $a_{t+1}$；机器人不必在当前 chunk 后停 142 ms 等模型。

**Step 7：真实观测纠偏。** 若盘子因摩擦只移动了计划距离的 70%，新 camera frame 编码成真实 $z_{t+1}$，覆盖 cache 中“已到中心”的 $\hat z_{t+1}$。下一 action 基于真实偏差追加小推，而不会沿错误想象继续去抓纸垫。

**Step 8：子任务切换。** planner 新一轮看见盘子已居中，在 boundary-crossing 逻辑下输出 `done=true` 和下一 instruction “Pick up the paper pad”。同一 low-level checkpoint继续执行放纸垫和放目标物，最终以完整 task success 和阶段 progress 评估。

## 实验设置、数据集、基线、指标

### 数据

- General image/video：复用 LingBot-Video web-scale corpora，支持 T2I/T2V。
- Robot：AgiBot、RoboMind、InternData-A1、OXE/DROID、UMI、RoboCOIN 与新增数千小时内部 demo；Qwen3.5-397B 重切 atomic clips 并重标 task/instruction。
- Ego human：数千小时、65.4k episodes、600+ operators、3.0k+ scene-task combinations、五类桌面环境；每帧双手 6-DoF world roots + 每手 22 finger joints。
- ICL：10+ robot datasets、5k+ tasks、50k+ human-robot pairs；VLM 解析/编辑首帧/生成 prompt，WAN-2.6 或 Kling-V3 合成人类 demo，再按 semantics/physics filter。

### 训练超参

DiT 30 blocks；video hidden 2048；joint attention 3072；24×128 heads；video MoE 128 Top-8 + shared，expert intermediate 512；action hidden 768、FFN 3072；MCP 1.7B；总 15.3B，inference active 约 2.5B。chunk size 训练随机 1--4 latent frames、window 1--64，评估用 chunk 2/window 64；history 以 0.5 概率加小 context noise。Muon 更新 transformer 2D matrices（lr $2\times10^{-3}$），其余 AdamW（lr $10^{-4}$）；warmup 2000、grad clip 1.0、text dropout 0.1。

### 评估

真实四任务每任务 20 teleop demos，单一 multi-task policy：Pen Collection、Fruit Sorting、Drawer Tidying、Plate Handover；基线 $\pi_{0.5}$ 和 LingBot-VA。仿真 RoboTwin 50 tasks：clean 2500 demos（50/task）+ randomized 25k（500/task），基线 X-VLA、$\pi_{0.5}$、Motus、LingBot-VA。

## 主要结果、消融或对比

### 真实任务（Fig.8）

| Task | VA 2.0 success | VA 1.0 | $\pi_{0.5}$ | VA 2.0 progress |
| --- | ---: | ---: | ---: | ---: |
| Pen Collection | 85 | 77 | 75 | 95 |
| Fruit Sorting | 67 | 50 | 42 | 90 |
| Drawer Tidying | 82 | 64 | 64 | 89 |
| Plate Handover | 64 | 55 | 45 | 84 |

progress 全面高于 success，说明模型往往能完成多阶段的大部分，但最终收尾仍可能失败。论文把提升归于 future visual grounding/native pretraining；但四任务没有公开 trial count/置信区间，且 baseline finetuning 细节需与代码核对。

### RoboTwin（Table 1）

LingBot-VA 2.0 clean/randomized/avg = 93.8/93.4/93.6；LingBot-VA 92.9/91.6/92.2；Motus 88.7/87.0/87.9；$\pi_{0.5}$ 82.7/76.8/79.8。对 VLA baseline 平均 +13.8（正文写 14.0，源于四舍五入口径）；对前代 VA +1.4。clean-random gap 仅 0.4（正文称 0.6，按表值为 0.4），引用时应以表格算术为准并注明文本不一致。

### Tokenizer 消融（Table 2）

同 1.3B downstream architecture、同 token budget：WAN2.2 VAE 的 Average50 Tasks Easy/Hard 为 78.0/76.0，本文 tokenizer 为 86.6/83.1。horizon 3 提升尤其大：67.2/68.0→92.0/85.4，支持 semantic/action latent 对长视预测更有效，而非只改善单步重建。

### MCP（Fig.10）

12/50 FPS、clean/random 都更快收敛。50 FPS randomized 在 5k steps 领先 29.7 pp；20k steps 匹配 no-MCP 45k accuracy，2.3× optimization speedup。高 FPS 相邻 chunk 更相似，因此此处恰是“copy appearance”最严重、MCP 最有用的设置。

### 加速（Table 3）

| 阶段 | ms/chunk | Async Hz |
| --- | ---: | ---: |
| BF16 PyTorch async baseline | 927 | 35 |
| + consistency distillation | 466 | 69 |
| + FP8 compiled execution | 369 | 87 |
| + paged/ragged KV + attention | 272 | 118 |
| + runtime overhead reduction | 142 | 225 |

总加速 6.5×。这里 Async Hz = $(1000/t_{chunk})\times32$：142 ms 内生成 32 个低层 steps，平均吞吐 225 steps/s；单 chunk 仍需 142 ms，因此遇到突发事件的响应上限还取决于 chunk 执行与 observation re-grounding 时机。

## 图表、公式与表格线索

| 线索 | 精读问题 |
| --- | --- |
| Fig.1 / Eq.(5) | future visual latent 是 action 前的因果中间变量还是并行装饰？ |
| Fig.2 / Eq.(9)--(14) | visual semantics 与 latent action 如何分别训练？ |
| Fig.3 | planner schema 如何与 low-level training conditions 对齐？ |
| Eq.(15)--(19) | video MoE 为何稀疏、action 为何 dense、bias 如何 balance？ |
| Fig.5 / Eq.(20)--(23) | MCP 是否看到了 clean future；梯度如何回主干？ |
| Eq.(24)--(28) | ICL 与 HCT 如何在不破坏 robot causality 的情况下引入 human video？ |
| Fig.6 / Eq.(29)(30) | imagined latent 何时被真实 latent 覆写？ |
| Table 2 / Fig.10 / Table 3 | representation、训练 objective、部署系统三层收益必须分开引用。 |

## 主张—证据—边界矩阵

| 主张 | 证据 | 解释 | 边界 |
| --- | --- | --- | --- |
| native causal pretraining 优于 retrofit。 | 对前代 VA 和 VLA 的结果。 | 方向一致，真实/仿真均提升。 | 没有“同数据同容量，只改 bidirectional→native causal”的严格对照。 |
| tokenizer 提供 action-relevant state。 | Table 2，长 horizon 增益更大。 | 比 reconstruction VAE 更适合未来/控制。 | semantic alignment 与 IDM/FDM 未拆开。 |
| web/human video 扩展控制知识。 | ICL demo、HCT 设计。 | 可无参数更新迁移 procedure。 | ICL 主要定性；HCT 独立消融不足。 |
| Foresight 保持 closed loop 且隐藏 latency。 | Fig.6、Eq.(29)(30)、Table 3。 | predict ahead + overwrite cache。 | 真实 observation 频率、queue delay、严重模型偏差下稳定性未量化。 |
| 225Hz real-time。 | Table 3 公式。 | 32-step chunk 摊薄吞吐。 | 不是 225 次独立视觉重规划/秒，表述需谨慎。 |

## 局限与可追问点

1. **归因耦合。** tokenizer、causal scratch pretraining、规模、MoE、MCP、数据、ICL/HCT、distillation 和系统优化同时改变；除了 tokenizer/MCP/speed，核心“native”主张缺少严格单变量实验。
2. **世界模型多模态未来。** Flow matching 可表达分布，但 deployment 只采有限 trajectory；对接触不确定性、遮挡和不可逆错误没有 uncertainty-aware replanning。
3. **Imagined cache 风险。** $a_{t+1}$ 在真实 $z_{t+1}$ 到来前已生成；若 $a_t$ 执行结果偏差大，预生成 chunk 是否作废、截断或重算，论文系统描述需更多安全细节。
4. **Human retargeting。** 6-DoF hand root 不经转换、finger envelope 压成一维 aperture，会丢失灵巧手姿态；域专属 head 不能保证共享 dynamics 不受错误人类动作污染。
5. **ICL 数据合成闭环。** 人类 prompt 视频由 image editing + generative video 产生，可能带非物理 motion；虽有 VLM 评分，但评分器偏差和真实人类 demo 对照未详报。
6. **真实评测透明度。** 四任务 demo 数明确为 20，但 rollout 次数、误差条、硬件和失败类型不足，无法判断百分点差异的统计显著性。
7. **频率指标。** 225 Hz 是 amortized low-level step throughput；真正闭环 update rate 由 142 ms chunk、sensor queue、planner 2 Hz 与执行 chunk duration共同决定。

## 与当前库的连接

- 与 [[@wu2026lingbot-vla2]]：VLA 2.0 直接生成动作，并以 future depth/video feature 做 auxiliary distillation；VA 2.0 显式生成 future visual latent 再由 inverse dynamics 解码 action。前者更轻、更接近 policy，后者更强 world-action factorization。
- 与 [[@fu2026lingbot-vision]]：Vision 解决 patch latent 的边界/几何保真；VA 解决 visual latent 与 action transition 的语义/因果对齐。一个好的 future world state 同时需要两者。
- 与 [[@qian2026wam-rl]] / [[@wang2026wvm]]：共同把 future prediction 变成 action/value/planning 的中间变量；本文重点是大规模原生预训练和实时异步部署，而不是在线 RL。
- 与 [[@intelligence2025pi06-vla-that-learns]]：后者通过经验/价值反馈改进 policy；本文通过 web/human video 与 world-action modeling 获得先验，二者可以形成“预训练 world-action model + 经验后训练”组合。

## 精读路线 / 为什么需要回看

第一遍：Fig.1 → Eq.(5) → Fig.2/Eq.(12)--(14) → Fig.5 → Fig.6 → Tables 1--3。复现 tokenizer：重点看 tubelet shape、96 channels、alignment teacher、transport map 和 bottleneck。复现 policy：核对 30-block MoT、2048/768/3072 widths、128 Top-8 MoE、chunk/window sampling、MCP layer taps/weights、五任务 $\pi(\tau)$。复现部署：必须区分 standard video loss $a_{<t}$ 与 FDM grounding loss $a_{\le t}$，实现 cache overwrite、stale prediction invalidation、2-step consistency、TensorRT explicit KV I/O 和 paged cache；这些环节任何一个写成同步都会失去 Foresight 的意义。
