# project-code-study 5.0.0 优化修缮报告

## 一、范围与基线

- 权威任务依据：用户提供的 `PROJECT_CODE_STUDY_SKILL_OPTIMIZATION_HANDOFF.md`。
- 仓库基线：`6f0b6168e33895620db71ef143e8403538cdc55f`。
- 修改前工作区：干净，无未提交变更。
- 安全副本：修改前已在本机临时目录创建，未提交到仓库。
- DETR 学习记录：仅作为只读校验对象，未作修改。

## 二、问题修缮总览

| 问题编号 | Schema 4.1/1.1/1.2 状态 | 实现与验证证据 |
| --- | --- | --- |
| PERSIST-01 | 已关闭 | 引入 TX-ID 逻辑事务、Q&A 优先写入、精确回读、LOG 回读、跨文件对账与 fail-closed 回执；由 T-01/T-02 覆盖 |
| PERSIST-02 | 已关闭 | 引入权威 frontmatter/热状态字段、最后 Q/TX/时间对账，以及单事务派生状态；由严格校验器验证 |
| QA-01 | 已关闭 | Q 记录必须包含可独立阅读的完整字段；禁止隐藏聊天依赖与循环答案；由 T-02/T-08 覆盖 |
| FLOW-01 | 已关闭 | 引入可执行交互状态机、回答后暂停和单次继续令牌；由 T-03/T-04/T-05/T-15 覆盖 |
| STEP-01 | 已关闭 | 引入语义完成门槛、必需的 durable K 卡和成功事务；由 T-05/T-07/T-14 覆盖 |
| ROUTE-01 | 已关闭 | Step、微 Step 与 NODE 使用相互独立的状态枚举，并要求记录延后/跳过元数据；由 T-06/T-13 覆盖 |
| PROMPT-01 | 协议层已关闭；仍需跨宿主观察 | 将正常工作流不变量从用户长提示迁移到 Skill 与状态机；由 T-15 覆盖 |
| VISUAL-01 | 协议层已关闭；仍需跨模型观察渲染 | 确立线性链、表格、Mermaid、短 ASCII 的选用优先级，并要求保留 RUN/NODE 标签；由 T-16 覆盖 |
| ORIENT-01 | 已缓解；仍需多项目观察 | 概览类 Step 也必须包含可持久重学的知识与行为证据 |
| FINAL-01/02/10 | 已关闭 | 引入 fail-closed readiness manifest、严格记录 schema、显式问题阶段关闭与生成同意，以及真实的证据/掌握边界；由 T-07/T-12 覆盖 |
| FINAL-03/04/07/08 | 已关闭 | 引入 schema 1.2 独立 UNIT 契约、语义章节门槛、占位内容禁令和冷启动静态代理；由 T-10/T-14 覆盖 |
| FINAL-05/11 | 已关闭 | 要求 UNIT ID、标题和 anchor 唯一，代码围栏成对，时间戳/修订号真实，并通过临时文件一次性组装；由 T-09 覆盖 |
| FINAL-06 | 已关闭 | 重要问题按 NODE 解锁作用和学习影响筛选，并要求来源 Q&A 可独立阅读；由 T-08 覆盖 |
| FINAL-09 | 已关闭 | 在历史修正章节之外扫描 stale pattern，防止旧说法被重新提升；由 T-11 覆盖 |
| VALID-01 | 确定性校验已关闭；真实跨模型冷启动仍待运行 | 提供严格 LOG/QA 校验器、readiness 校验器、schema 1.2 校验器和 T-01～T-16 回归测试 |
| TECH-01 | 机制层已关闭；项目结论仍依赖证据 | 强制证据分类、源码定位，并禁止夸大论文或源码覆盖范围 |

## 三、修改文件

### 3.1 主工作流与记录协议

- `SKILL.md`：升级至 5.0.0，加入核心不变量、交互状态、事务、完成条件与 readiness 规则。
- `references/learning-ledger-protocol.md`：加入权威状态、TX 对账、K 卡与兼容性规则。
- `references/question-protocol.md`：加入独立 Q&A、问答后暂停、单次继续令牌与规范修正规则。
- `references/runtime-trace-protocol.md`：加入 NODE 枚举、跳过/延后审计、恢复与图示策略。
- `references/step-template.md`：加入验证暂停与 durable K 卡模板。
- `references/quality-rubric.md`：加入语义完成、文档质量与冷启动门槛。
- `references/user-prompts.md`：缩减为启动、恢复、审计和诊断提示。
- `references/final-summary-template.md`：明确其不是正式最终文档，并补充图示规则。
- `assets/PROJECT_STUDY_LOG.template.md`：升级为 schema 4.1。
- `assets/PROJECT_STUDY_QA.template.md`：升级为 schema 1.1。

### 3.2 可执行校验

- `scripts/interaction_state.py`：提供确定性的交互状态转换参考。
- `scripts/validate_learning_ledger.py`：提供兼容读取、严格语义校验与跨文件对账。
- `scripts/validate_finalization_bundle.py`：生成 readiness manifest 并作为最终化出口门禁。
- `tests/test_regressions.py`：提供可重复执行的 T-01～T-16 测试矩阵。

### 3.3 最终文档伴生 Skill

- `skills/project-study-document/SKILL.md`：升级至 2.0.0，加入 fail-closed 入口、原子生成流程和默认中文输出约束。
- `skills/project-study-document/references/document-generation-protocol.md`：加入唯一 UNIT 映射、临时文件组装、双阶段校验与原子替换。
- `skills/project-study-document/references/quality-gates.md`：加入语义、证据、修正、导航、持久化和冷启动门槛。
- `skills/project-study-document/references/important-question-selection.md`：加入按 NODE 解锁影响筛选问题的规则。
- `skills/project-study-document/assets/PROJECT_STUDY_DOCUMENT.template.md`：升级为 schema 1.2，使用中文正文结构、显式 UNIT anchor 与 readiness 身份字段。
- `skills/project-study-document/scripts/validate_study_document.py`：校验重复项、占位内容、stale 内容、覆盖关系、Q&A、readiness、preflight 与最终状态。

### 3.4 文档与维护

- `README.md`：提供以中文为主、英文为附录的 5.0 使用说明，涵盖行为、schema、命令、兼容性与限制。
- `REMEDIATION_REPORT_5.0.0.md`：使用中文记录本次优化范围、问题闭环、验证结果和剩余观察项。
- `agents/openai.yaml`：更新展示摘要。
- `.gitignore`：忽略 Python 缓存产物。

## 四、验证结果

```text
模板校验：3/3 通过
Python 编译检查：通过
T-01～T-16：16/16 通过
git diff --check：空白修复后通过
```

对 DETR 历史记录进行的只读复核证明了新机制会可靠地 fail-closed：

- 旧版 LOG 4.0 和 Q&A 1.0 仍可进行结构兼容读取；
- 因缺少严格的 4.1/1.1 状态、仍存在隐藏聊天依赖，且未记录显式的问题阶段关闭和生成同意，正式 readiness 校验失败；
- 既有最终文档因代码围栏不平衡、循环/占位表达及 UNIT ID/标题重复而被拒绝。

这说明校验器不会掩盖旧记录中的无效最终化，也没有为了“通过测试”而修改 DETR 历史产物。

## 五、剩余观察项

- 尚未执行真正的“无聊天上下文、全新会话或跨模型”冷启动重学测试。T-14 只是确定性的静态语义代理，已按真实状态记录，未宣称为真实运行通过。
- 虽然正常控制不变量已经进入可执行状态机并由 T-15 覆盖，仍需跨宿主 A/B 观察来确认用户不再需要提供控制型长提示。
- Mermaid 与其他图示的渲染质量仍应在不同文本宿主中抽样观察；T-16 只验证图示策略和必需的 RUN/NODE 标签。
- 既有 DETR 学习产物按要求未迁移、未修复，继续保留为新校验器拒绝旧版无效最终化的验证证据。

## 六、最终结论

`project-code-study` 5.0.0 已完成任务书中可确定性实现和验证的核心修缮：学习路线以真实运行证据为基础；问答、继续与节点推进受到显式状态控制；跨文件保存采用可审计事务；Step 完成需要语义与行为证据；最终文档生成受 readiness、用户同意、双阶段校验和原子写入共同约束。

面向学习者生成的 `PROJECT_STUDY_DOCUMENT.md` 默认使用简体中文。源码符号、命令、路径、公式、schema 字段、ID 和固定协议枚举保持原样，并在中文正文中解释。只有用户明确要求其他语言时才切换输出语言。
