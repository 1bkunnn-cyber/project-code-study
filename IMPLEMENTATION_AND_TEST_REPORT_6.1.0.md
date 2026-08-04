# Project Code Study 6.1.0 实施与测试报告

日期：2026-08-04

## 结果

本次把 `PROJECT_STUDY_DOCUMENT.md` 从 v6 的“逐 Step 厚教材”修订为
schema 2.1“可检索、可跳读、不过度复制的 Step 学习手册”。没有修改授权
学习项目中的源码、QA、LOG、memory 或最终文档。

“完整”现在由学习闭环、证据闭环和冷启动行为证明，不再由 15 个小节的统一
最低字符数证明。

## 修改前后对应

| 修改前问题 | 6.1.0 机制 |
| --- | --- |
| 20 项要求展开成 15 个长小节，诱导扩写 | 20 项语义收敛进 8 个稳定阅读槽位 |
| 每个 Step 都像教材章节，难以跳读 | `30 秒定位` + 快速索引 + 明确下一跳 |
| 共享训练/Shape/指标知识跨 Step 重复 | 文档内唯一 `DEEP-DIVE-*`，Step 先给局部闭环再链接 |
| 精确源码容易退化为整函数复制 | profile 摘录数量/总行数/单段行数/文件覆盖率 gate |
| QA 正文和问题区重复完整答案 | 完整答案只在最相关 Step 出现一次；顶层只做 Q-ID 索引 |
| cold-start 只检查解释字段 | 增加 lookup、retrieval、explanation、application 结果 |
| schema 2.0 直接继续发布 | 2.0 只读迁移；新 publication 必须 2.1 |

## 新机制

### 阅读层级

| Profile | 非代码正文 | 摘录数 | 摘录总行数 |
| --- | ---: | ---: | ---: |
| `compact` | 450–1,200 | 1 | ≤ 24 |
| `standard` | 800–2,200 | 1–2 | ≤ 60 |
| `specialist` | 1,400–3,600 | 2–4 | ≤ 120 |

单个摘录最多 45 行。源文件不少于 20 行时，同一 Step 最多摘录 35%；
小于 20 行的文件最多完整引用 12 行。Step 4.x、6、10 必须使用
`specialist`，原有专项机制要求不变。

### 导航与去重

- 快速索引按 Step、关键词、源码/符号、Q-ID 和 CHAPTER 锚点定位，validator
  会拒绝缺失、非链接或无法解析的手册条目锚点；
- 80 个规范化字符以上的非代码段落不能跨 Step 原样重复；
- deep-dive 引用必须解析到同一份正式 Markdown 内的唯一锚点；
- 重要 QA 的完整答案只保留一份，问题区只保存检索信息。

### 冷启动

cold-start report schema 1.1 增加：

- `lookup_path`
- `retrieval_result`
- `explanation_result`
- `application_result`

CLI 新增 `--handbook-schema 2.1`。静态 fixture 通过只证明协议实现；
没有真实 fresh-host document-only 运行时仍必须标记 `not-run`。

## GitHub 调研与致谢

新增研究并致谢：

- Microsoft CodeTour：精确源码选择、有序 tour 和前后导航；
- Diátaxis：tutorial/how-to/reference/explanation 分层和按需深入；
- Material for MkDocs、mdBook：搜索、目录、锚点和导航；
- Rust by Example：小而完整的例子；
- Log4brains：轻量 Markdown、可搜索元数据和渐进披露；
- Docusaurus：仅比较 sidebar/版本化思想，因多文件站点/runtime 不采用。

许可证、GitHub API 活跃度和采用/拒绝结论见
`GITHUB_RESEARCH_AND_ACKNOWLEDGEMENTS.md`。没有复制这些项目的代码、
协议或文档文本。

## 测试结果

| 检查 | 结果 |
| --- | --- |
| Skill 静态结构 | PASS |
| schema 2.1 模板解析 | PASS |
| 全部单元/回归测试 | 98 tests：97 PASS / 1 SKIP |
| 紧凑 8 槽位 gold entry | PASS |
| 过长正文拒绝 | PASS |
| 高源码覆盖率拒绝 | PASS |
| 跨 Step 长段落重复拒绝 | PASS |
| lookup index / deep-dive 锚点 | PASS |
| schema 2.1 publication gold fixture | PASS |
| schema 2.1 cold-start CLI | PASS |
| schema 2.0 只读迁移 | PASS |

唯一 skip 是 `T31_real_host_golden_conversation`，测试本身明确禁止把静态
fixture 报告成真实宿主通过。

## 真实样本只读回归

项目：`D:\python program\Pedestrian detection system`

| 检查 | 结果 |
| --- | --- |
| QA/LOG strict validator | PASS |
| memory doctor | PASS |
| 现有 schema 1.2 document 只读 validator | PASS |
| 6.1 publication | 正确 FAIL：不是 schema 2.1；publication QA readiness 未通过；cold-start 未运行 |
| QA/LOG/document/MEMORY.md 前后 SHA-256 | 全部一致 |

旧文档通过旧 schema 只表示可读取，不表示达到 6.1 正式手册标准。

## 未运行

- 真实 fresh-session、document-only 的 6.1 手册冷启动：`not-run`；
- 多模型对同一手册的检索/解释/应用一致性：`not-run`；
- 真实上下文压缩触发和恢复：本次未重复运行；
- 宿主级 pre-response hook：`not-run`，仍依赖宿主集成；
- 对授权样本实际生成 schema 2.1 文档：未授权，未执行。

当前 Codex 宿主真实执行了 Skill 修改、测试、GitHub 调研和只读样本审计；
这不等于 fresh-host 冷启动通过。

## 风险

- 字符/行数预算是可执行的可读性代理，不是教育质量的充分条件；
- 中文、公式和表格的有效信息密度不同，未来需用更多真实手册校准 profile；
- 35% 源文件覆盖率对生成文件或超短关键函数可能偏严格，当前通过小文件
  12 行例外处理；
- 单 Markdown 的搜索体验依赖阅读器，当前只保证锚点和索引，不提供站点 UI；
- real-host cold-start 仍是发布外部能力，不能由本地测试替代。
