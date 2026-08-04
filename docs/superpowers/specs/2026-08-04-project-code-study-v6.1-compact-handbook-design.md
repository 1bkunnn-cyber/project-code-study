# Project Code Study v6.1 紧凑 Step 手册设计

## 目标

把 v6 的“逐 Step 教材章节”校正为“逐 Step 可检索学习手册”。用户应能只读
`PROJECT_STUDY_DOCUMENT.md`，快速定位一个 Step，理解该 Step 的问题、真实调用链、
关键源码、输入输出/Shape/状态、设计理由、重要 QA 与自测；文档不应复制完整聊天、
完整函数、全部 QA 或在多个 Step 重复同一段背景知识。

“完整”指学习闭环和证据闭环完整，不指材料复制完整。

## 基线问题

v6 schema 2.0 把 20 个语义要求展开为 15 个长小节，并为每节设置统一最低字符数。
这能挡住一句话摘要，却会产生三个反效果：

1. 模型通过扩写满足长度，而不是帮助查阅；
2. 共享机制在多个 Step 重复，文档随 Step 数量近似线性膨胀；
3. “精确源码证据”容易退化为整段函数复制，阅读路径反而被代码淹没。

## 调研与取舍

| 项目 | 可借鉴思想 | 本设计的采用方式 | 结论 |
| --- | --- | --- | --- |
| [Microsoft CodeTour](https://github.com/microsoft/codetour) | 有序导览、文件/行选择、primary tour | Step 顺序、精确源码锚点、下一跳 | 直接借鉴结构思想 |
| [Diátaxis](https://github.com/evildmp/diataxis-documentation-framework) | tutorial/how-to/reference/explanation 分工；先给最小解释，再按需深入 | Step 核心闭环、检索索引、共享深讲分层 | 直接借鉴信息架构 |
| [Material for MkDocs](https://github.com/squidfunk/mkdocs-material) | 搜索、目录、breadcrumbs、源码归属 | 单 Markdown 内的关键词索引、锚点和本地导航 | 只借鉴导航思想；不引入站点运行时 |
| [mdBook](https://github.com/rust-lang/mdBook) | 章节树、搜索、前后导航 | Step 索引与 previous/next 路径 | 只借鉴导航思想 |
| [Rust by Example](https://github.com/rust-lang/rust-by-example) | 小而完整的例子优先于大段复制 | 每 Step 一个项目最小例子 | 直接借鉴教学粒度 |
| [Log4brains](https://github.com/thomvaill/log4brains) | 轻量 Markdown、可搜索元数据、可折叠附加信息 | 精简正文、可选 `<details>` 深读、去重 | 借鉴思想 |
| [Docusaurus](https://github.com/facebook/docusaurus) | sidebar、版本化、站点检索 | 不引入；单文件是当前发布边界 | 不适合当前 Skill |

本仓库不复制上述项目代码或协议文本。许可证、活跃程度与适用性记录在
`GITHUB_RESEARCH_AND_ACKNOWLEDGEMENTS.md`。

## 备选方案

### 方案 1：保留 20 节，只降低最低长度

改动最小，但仍把字段数量当作阅读质量，无法阻止重复和完整源码复制。拒绝。

### 方案 2：紧凑分层 Step 手册（采用）

将 20 个语义要求收敛进 8 个稳定阅读槽位，增加阅读预算、源码摘录预算、重复检测、
关键词索引和文档内共享深讲。每个 Step 保持独立核心闭环，深入机制只写一次。

### 方案 3：输出多文件文档站

导航最好，但改变“一个正式 Markdown”的发布、hash、receipt、隐私和离线边界，还引入
构建依赖。当前不采用；未来可把已验证 Markdown 作为可选渲染源。

## schema 2.1 信息架构

正式发布使用 `schema_version: "2.1"`，并增加：

```yaml
handbook_mode: "layered-step-manual"
default_reading_profile: "standard"
```

文档新增“如何查阅”和“关键词/符号/错误/Shape/Q-ID 快速索引”。每个完成 Step 仍恰好
对应一个唯一 `CHAPTER-`，但用户界面称为“Step 手册条目”，不称“教材章节”。

每个 Step 条目使用 8 个槽位：

1. `30 秒定位`：问题、前置知识、运行位置、上游/下游和完成标准；
2. `调用链与数据边界`：RUN/NODE/micro-Step、调用顺序、I/O/Shape/状态；
3. `精选源码证据`：精确路径/行号、最小必要片段和对应解释；
4. `核心机制`：变量、参数、公式、状态变化和为什么这样设计；
5. `设计取舍与故障定位`：替代实现、取舍、常见错误与表现；
6. `项目例子与重要 QA`：一个具体例子和真正改变理解的 QA；
7. `自测与参考答案`：至少一题回忆和一题应用，答案紧邻；
8. `证据边界与下一跳`：已确认/可推断/待验证、前后 NODE、唯一继续方向。

20 项语义要求仍被覆盖，但 validator 不再要求 15 个等长小节。

## 渐进披露

每个 Step 的核心闭环必须在本条目内成立；不得用“详见聊天”“同上”或只给链接。
可复用的训练循环、YOLO Shape、评估指标和创新验证写入文档内唯一的
`DEEP-DIVE-*` 共享深讲。Step 条目先给足以回答本 Step 问题的局部解释，再链接到共享
深讲。可选推导、扩展源码和非关键 QA 可放进 `<details>`，但冷启动必答信息不能只藏
在折叠区。

## 阅读与摘录预算

每个 Step 明确 `阅读层级`：

| Profile | 正文字符预算 | 源码摘录 | 摘录总行数 | 适用 |
| --- | ---: | ---: | ---: | --- |
| `compact` | 450–1,200 | 1 | ≤ 24 | 地图、配置、简单桥接 |
| `standard` | 800–2,200 | 1–2 | ≤ 60 | 普通代码/概念 Step |
| `specialist` | 1,400–3,600 | 2–4 | ≤ 120 | Step 4.x、6、10 等核心机制 |

单个摘录最多 45 行。源文件不少于 20 行时，同一 Step 摘录不得覆盖该文件 35% 以上；
少于 20 行的小文件允许完整引用，但最多 12 行。validator 统计 fenced source excerpt，
而不是依赖模型自报。

预算是发布 gate：过薄说明不能独立学习，过长说明没有选择。若 specialist 机制仍超出
预算，应拆成多个真实 micro-Step 或唯一共享 deep dive，不能扩大整章。

## 去重与 QA 选择

- 对 Step 条目中的非代码段落做规范化；80 字以上段落不得在两个 Step 原样重复。
- 共享概念写一次，其他 Step 用一到两句本地桥接后链接到文档内锚点。
- 重要 QA 的完整规范答案只在最相关 Step 正文出现一次；“用户重要提问”区改为检索
  索引，记录 Q-ID、Step、主题、结论一句话和正文锚点。
- 未入选 QA 只保留 Q-ID、类别和排除理由，不复制完整答案。
- correction 仍必须全局传播；去重不能成为保留 stale wording 的理由。

## 专项深度

Step 4.x、6、10 仍保持 v6 的真实机制要求，但允许由“本 Step 核心解释 + 唯一共享
deep dive”共同满足：

- Step 4.x：训练/推理真实调用、`_do_train()`、`model(batch)`、
  `DetectionModel.forward()`、`v8DetectionLoss`、梯度累积、AMP、EMA、optimizer、
  epoch 收尾、验证/保存、`parse_model()` 与 `[8,3,640,640]` 的 YOLOv8n Shape；
- Step 6：TP/FP/FN、IoU、AP、mAP、阈值、`results.csv`、可视化和评估源码；
- Step 10：缝合、SE、baseline、消融、公平比较和创新验证。

Q-049、Q-063、Q-067、Q-068、Q-070 仍按学习影响选择，不能因为压缩而只留下编号。

## validator 与冷启动

schema 2.0 保持可读兼容，但 `--publication` 要求 2.1。新增机器 gate：

- 8 槽位和 Step metadata；
- profile 字符预算；
- 摘录数量、行数、源文件覆盖率和 exact-source；
- 跨 Step 长段落重复；
- 快速索引的 Step/关键词/源码/Q-ID 可定位性；
- deep-dive 锚点存在，且 Step 不以引用代替核心解释；
- 重要 QA 正文唯一吸收与索引链接；
- specialist profile 完整性。

冷启动报告升级为“检索 + 解释 + 应用”：

1. 给定 Step/Q-ID/符号/错误表现，能定位到正确锚点；
2. 不读聊天，在限定长度内解释调用链、源码、I/O/Shape/状态和证据边界；
3. 完成该 Step 的应用题。

静态 validator 不能替代 fresh-host。未运行真实 fresh-host 仍为 `not-run`。

## 不变边界

本次不修改状态机、QA 深度合同、memory 生命周期、统一 release receipt、claim guard、
readiness、consent、研究副本隔离或证据边界。样本项目保持只读。v6 的严格性从“要求
更长”改为“要求更会选、更好找、能复习且可验证”。

## 验收

- schema 2.1 紧凑 gold fixture 通过 publication；
- 浅摘要失败；
- 超预算、整文件复制、过多摘录、跨 Step 重复失败；
- 文档内共享 deep dive 通过，外部聊天引用失败；
- 每个完成 Step 可由冷启动报告定位、解释并完成练习；
- 现有 88 项回归不退化；
- README、研究致谢、CHANGELOG 与实现报告同步；
- 真实宿主、真实压缩和 pre-response hook 未执行时明确 `not-run`。
