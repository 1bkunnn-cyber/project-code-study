# project-code-study 用户提示词

这些模板只负责表达学习意图、选择讲解方式、请求恢复或诊断。Q-ID、QA/LOG 写入、完整答案、暂停、重测、receipt、推进门禁和 finalizer 都由 Skill 与控制工具负责，正常工作流不要求用户反复提醒。

## 0. 使用方法：先路由，再闭环

每轮只选择一个用户意图：

| 用户意图 | 使用模板 | Skill 应完成的闭环 |
| --- | --- | --- |
| 新项目 | 1 | 读取规则与证据 → 建立 RUN/NODE 路线 → 完成 Step 0 → 等待 |
| 连续性记忆初始化 | 1A（Skill 自动询问） | 检查项目根目录 → 询问一次 → 用户同意后初始化 `.project-study-memory/`；拒绝则不创建 |
| 选择学习方式 | 2 | 记录偏好 → 不改变当前 NODE → 按所选方式讲解 |
| 恢复会话 | 3 | 记忆/LOG/QA/readiness 预检 → 修复或报告唯一下一动作 |
| 正常继续 | 4 | 消费一次新 continue → 只教一个 NODE → 回忆题 → 等待 |
| 提问/复合问题 | 5 | 拆分 Q-ID → 独立回答与保存 → 全部关闭前不推进 |
| 回忆题中插入问题/混合指令 | 5A | 排队每个意图 → 先处理当前优先级 → 未解析意图阻断 continue |
| 回答回忆题 | 6 | 复述 → 逐项判定 → 规范答案/证据 → 必要时 retest → 等待 |
| 深讲/Shape/论文映射 | 7–9 | 留在当前锚点，补齐对应输出契约并记录 |
| 纠错/定位/记录异常 | 10–12 | 只修复证据或记录 → 回读/校验 → 不推进 |
| 暂停/压缩/切换会话 | 13 | 安全边界同步 → 写入可复用记忆 → 报告可恢复状态 |
| 关闭问题/最终化 | 14–16 | readiness 审计 → 用户确认 → 唯一 finalizer 或 incomplete-draft |
| 最小诊断 | 17 | 只报告机器状态，不教学、不猜测、不修改 |

闭环状态始终按以下顺序理解：

```text
启动/恢复
  → preflight 与证据边界
  → 项目路线与当前 RUN/NODE
  → 讲解一个 NODE
  → 回忆题或支线问题
  → 完整回答、写入、回读、校验
  → AWAITING_QUESTIONS_OR_CONTINUE
  → 用户发送新的“继续”
  → 下一 NODE；或进入修复 / retest / finalization 分支
```

如果任一控制工具失败，唯一闭环是报告 `unsaved-partial`、`unsaved-memory` 或 blocker 并修复；不得用自然语言补写成功状态。

## 1. 首次启动：建立学习合同

```text
请使用 $project-code-study 带我学习当前项目。
目标：<读懂 / 复现 / 修改 / 研究扩展>
基础：<一句话说明已有知识>
重点运行场景：<训练 / 推理 / 评估 / 部署 / 其他；可留空>
深度：<快速建立地图 / 按调用链深入 / Shape 与数据流 / 论文—代码对照；可留空>
本轮先完成启动预检、记录权限确认、证据边界和项目专属路线，只完成 Step 0，完成后等待。
```

## 1A. 项目连续性记忆初始化：先询问，再创建

这是 Skill 在首次识别项目根目录且 `.project-study-memory/` 不存在时自动执行的确认步骤，不要求用户额外粘贴提示词：

```text
是否启用当前项目的连续性记忆？
启用后将在项目根目录创建 .project-study-memory/，用于保存可复用规则、纠正和恢复指针；拒绝则不创建。
请回答：启用 / 不启用。
```

执行规则：

- 用户明确回答“启用”后，调用 `scripts/sync_protocol_memory.py init <PROJECT_ROOT>/.project-study-memory --template assets/PROJECT_STUDY_MEMORY.template.md --user-consent`，再读取并严格校验 `MEMORY.md`；
- 用户明确回答“不启用”后，记录 `memory_status: disabled`，不创建目录，不执行记忆同步；
- 用户未回答、回答含糊或工具失败时，保持 `memory-consent-pending`，不得静默创建，也不得声称记忆已启用；
- 目录已经存在时不重新创建，先运行 memory doctor；校验失败时报告 blocker 并修复。

## 2. 选择讲解方式：只改变呈现，不改变状态机

```text
当前目标是：<快速建立地图 / 苏格拉底式预测与回忆 / 深讲一个 NODE / Shape 逐轴追踪 / 论文—代码对照 / 运行复现>。
请保持当前 RUN/NODE 和所有记录门禁不变，只按这个方式安排本轮讲解；不要因为换方式而跳过证据、回忆题或等待状态。
```

## 3. 恢复已有学习：先恢复事实，再决定是否教学

```text
请使用 $project-code-study 恢复当前项目学习。
先读取并严格校验 .project-study-memory/MEMORY.md（若存在）、PROJECT_STUDY_LOG.md、PROJECT_STUDY_QA.md 和最近一次成功事务。
报告：当前 Step、RUN、NODE、interaction state、继续位置、未关闭/重测 Q、最近修正、记录异常和唯一下一动作。
若记忆、LOG/QA、receipt 或 readiness 不一致，先修复或报告 blocker，不开始新教学。
```

## 4. 正常继续：只消费一个新的继续令牌

```text
继续主线。本轮只学习精确继续位置对应的一个 NODE；遵循 Skill 内部 preflight、证据、主动回忆、记录和等待规则。
```

## 5. 提出问题：支持单问题和复合问题

单问题：

```text
我有一个关于当前 NODE 的问题：<问题>
请保留主线锚点，回答并记录这个问题；回答闭环后停在等待状态，不开始下一个 NODE。
```

复合问题：

```text
我有多个独立问题：
1. <问题一>
2. <问题二>
3. <问题三>

请先按独立意图拆分并为每个意图分配独立 Q-ID；每题在 QA 中保存完整、可独立阅读的规范答案，聊天中给出问题索引、结论、证据摘要和 QA 位置。可以分批展示，但全部问题关闭前不要推进主线。
```

## 5A. 回忆题中插入问题或一条消息包含多个意图

```text
这条消息可能包含多个意图，请不要丢弃任何一项：
<回忆题回答 / 新问题 / 继续 / 纠正 / 修改要求>
请先建立 pending_user_intents 队列，逐项分配处理顺序和状态；保存并关闭当前意图后再处理下一项。没有全部处理完之前不要消费“继续”，不要推进 NODE。
```

如果当前正在等待回忆题，用户先提出支线问题时，先保存并回答支线问题，再回到 `AWAITING_RECALL` 等待原回忆题；不得把支线问题回答后直接变成普通 `AWAITING_QUESTIONS_OR_CONTINUE`。

## 6. 回答主动回忆或复测题：不要替我补全

```text
这是我的回答：<回答>
请先复述你理解的答案，再按每个问题意图分别指出正确、错误、缺失、表达不足或证据不足的部分；不要虚构我没有说过的错误。
随后给出完整参考答案、原因、源码/运行/论文证据和当前掌握判定。若错误或部分正确，请换一个角度讲解并给出复测题；复测通过、记录成功并回到等待状态前不要推进。
```

## 7. 深讲当前 NODE：完整教学输出

```text
请停留在当前 RUN/NODE 重新深讲，不推进。
必须包含：当前节点及上下游、已核验可点击源码位置、当前问题所需的最小源码、按执行顺序的代码组、输入/输出/Shape/状态变化、每个维度的语义/来源/变化原因、设计原因/替代方案/取舍/失败模式、证据边界、一个自测和完整参考答案。
结束时提出回忆题并等待，不提前讲下一个 NODE。
```

## 8. 只问 Shape、字段或状态映射

```text
我只想理解 <张量 / 字段 / 状态> 的映射：<对象或 Shape>
请逐轴或逐字段说明语义、当前值来源、变化原因、生成代码、下游用途，并区分 tensor、config、parameter、metadata 和状态字段。请引用真实源码位置；无法确认的部分标为待验证。本轮不推进主线。
```

## 9. 论文—代码、配置和运行证据对照

```text
请核对当前结论：<结论>
按声明类型选择对应 verifier，分别给出源码/配置/运行/数学/论文证据、适用范围和未验证边界；区分建议命令、已执行命令和观察结果。证据不足时标为待验证，不要用背景知识填空。本轮只核验，不推进。
```

## 10. 修复代码定位或链接

```text
当前代码位置缺失或跳转不正确：<现有位置或问题>
请重新确认 repository root，核验文件存在、符号存在和实际行号；在聊天和 QA 中使用同一个真实可点击 Markdown 链接，不使用 ... 或占位路径。本轮只修复定位、证据和记录，不推进主线。
```

## 11. 修复 QA/LOG 或 receipt 异常

```text
暂停教学，只执行记录恢复：<异常描述>
检查 frontmatter 与热状态、Q-ID/Parent Q、完整答案、证据、heading 边界、重复 ID、串写、旧说法、TX 对账、机器 receipt 和 strict validator。
修复后精确回读全部受影响字段。成功只能来自机器 receipt；否则报告 unsaved-partial、已写入/缺失部分和唯一下一修复动作。
```

## 12. 纠正旧结论并传播修正

```text
请纠正这条旧结论：<旧结论>
先用当前证据核验；若确实错误，建立 correction transaction，保存旧说法、规范说法、证据、影响范围、stale patterns 和 retest，并扫描 LOG、QA、摘要、知识卡和最终文档中的旧说法。本轮不推进主线。
```

## 13. 暂停、压缩上下文或切换会话

```text
请在当前安全边界暂停，不开始新 NODE。
先完成已产生事务的精确回读和校验；再执行连续性同步：读取并去重 .project-study-memory、更新可复用 feedback/correction/project/reference、归档过时条目、检查索引容量和孤儿文件。
最后报告可恢复的 RUN/NODE、interaction state、未关闭 Q、最后成功 TX、记忆同步结果和唯一下一动作。没有 receipt 的内容标为未保存。
```

## 14. 重建项目专属路线

```text
请暂停当前教学，按真实训练、推理、评估、导出或部署入口重新审计 RUN/NODE 路线。
列出未教、blocked、review、retest、stale 和被错误标为 done 的节点，补齐调用者/被调用者、证据位置、依赖和影响。路线与记录校准前不要开始新教学。
```

## 15. 关闭问题阶段

```text
我当前没有更多问题。请检查所有 Q、retest、修正、事务、Step/NODE、场景覆盖、durable K card、证据边界、pending_user_intents 和记忆同步状态。
只有全部通过才记录问题阶段关闭；否则列出 blocker，不要声称学习完成，也不要生成正式文档。
```

## 16. 最终化或阶段性草稿

正式文档：

```text
我同意生成正式 PROJECT_STUDY_DOCUMENT.md。
请先运行 fresh readiness manifest；只有 ready=true 才能调用唯一 finalizer。任何校验失败都不得创建、覆盖或声称 complete/validated 正式文件。
```

阶段性草稿：

```text
我明确要求生成阶段性草稿，不是正式完成文档。
请使用独立目标和 status: incomplete-draft，列出所有 blocker、未完成 Step/NODE、未关闭 Q、未验证结论和与正式文档的差异；不得覆盖已有正式文档。
```

## 17. 最小机器诊断

```text
请只报告机器状态，不教学、不修改记录、不补写推断：实际 Skill 路径、README 版本、LOG/QA schema 与 strict validation、memory doctor、current Step/RUN/NODE、interaction state、last successful TX、open/retest Q、pending_user_intents、route/scenario readiness、receipt 状态、是否允许推进及唯一原因。
```

## 18. 宿主或工具异常

```text
当前宿主可能没有执行必要控制工具，或响应中出现了未经 receipt 证明的 saved/validated/complete 声明。
请停止教学，重新读取 Skill 和 Required resources，运行相关 validator、response claim guard 与最近成功事务检查；在得到真实 receipt 前只报告 unverified/unsaved，不得继续推进。
```
