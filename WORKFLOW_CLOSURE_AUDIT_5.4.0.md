# project-code-study 5.4.0 工作流闭环审计

## 1. 审计目标

验证 Skill 在不同用户习惯、混合输入和突发中断下是否满足：

1. 每个入口都有明确处理路径；
2. 每个失败都有唯一下一动作；
3. 支线问题处理后能回到正确主线；
4. 最终问题阶段和 readiness 不能被旧 continue 穿透；
5. 记录失败不能被自然语言或状态默认值绕过；
6. 真实宿主尚未验证的行为不会被静态测试冒充通过。

## 2. 场景矩阵

| 用户习惯/突发情况 | 预期行为 | 实际结果 | 结论 |
| --- | --- | --- | --- |
| 一句话启动 | 确认项目根目录、询问记录和记忆许可，再进入 Step 0 | 协议和提示词有路径；没有宿主 E2E runner | `not-run` |
| 启用记忆 | 用户明确同意后创建 `.project-study-memory/` | 黑盒测试通过 | pass |
| 拒绝或不回答记忆许可 | 不创建目录；pending 阻断依赖记忆的推进 | 初始化测试和 pending gate 通过 | pass（代理） |
| 直接提问当前 NODE | 分配 Q-ID、完整回答、保存、停在等待 | 既有 T-04/T-22/T-23 覆盖 | pass |
| 在回忆题等待时直接提问 | 保存支线问题并保留回忆/主线锚点 | 状态机没有 `side-question` 转移 | fail |
| 回忆题回答错误/不完整 | `retest-due`，任何 continue 都阻断 | 既有 T-21 覆盖 | pass |
| 一次提出多个独立问题 | 独立 Q-ID，全部关闭前不推进 | 既有 T-23 覆盖 | pass |
| 用户发送旧的“继续” | 旧令牌失效，不推进 | 既有 T-04/T-22 覆盖 | pass |
| 最终问题阶段出现支线问题 | 回答后仍留在 `FINAL_QUESTION_PHASE` | 实际回到 `AWAITING_QUESTIONS_OR_CONTINUE` | fail |
| 最终 readiness 审计失败后用户继续 | 继续修复/审计，不恢复主线教学 | `audit-fail` 后可被 continue 推进 | fail |
| 用户拒绝正式文档 | 保持问题阶段，不生成文档 | `DOCUMENT_CONSENT → FINAL_QUESTION_PHASE` | pass（状态代理） |
| 上下文压缩/会话中断后恢复 | 先读 memory/LOG/QA/receipt，再恢复唯一下一动作 | 仅有协议和提示词，无真实宿主测试 | `not-run` |
| 宿主完全不调用控制工具 | 不能产生未经 receipt 的成功声明 | guard 可单独拒绝；宿主跳过时仍可自由输出 | known boundary |

## 3. 状态图结构检查

### 通过项

- `READY_TO_GENERATE` 是唯一无出边的终态；
- 所有枚举状态都存在到 `READY_TO_GENERATE` 的图路径；
- 非法事件会被 `transition()` 拒绝；
- `AWAITING_RECALL`、`FINAL_QUESTION_PHASE`、`DOCUMENT_CONSENT` 和 `READY_TO_GENERATE` 不接受普通 `continue`；
- `memory-consent-pending` 会阻断 `can_advance()`；
- `memory_status=disabled` 允许用户在不启用记忆时继续正常学习。

### 结构通过不代表语义闭环通过

状态图的静态可达性只能证明“存在路径”，不能证明每个用户行为都进入正确路径。本轮发现的两个旁路正是状态图语法有效、业务闭环不完整的例子。

## 4. 发现的问题

### PCS-WORKFLOW-001 — 最终问题阶段的支线问题可恢复主线教学

- **级别**：P0
- **复现路径**：

  ```text
  FINAL_QUESTION_PHASE
    --side-question--> ANSWERING_SIDE_QUESTION
    --answer-saved--> AWAITING_QUESTIONS_OR_CONTINUE
    --continue--> TEACHING_CURRENT_NODE
  ```

- **实际验证**：

  ```text
  PATH=FINAL_QUESTION_PHASE -> ANSWERING_SIDE_QUESTION
       -> AWAITING_QUESTIONS_OR_CONTINUE -> TEACHING_CURRENT_NODE
  ADVANCE=(True, 'advance permitted')
  ```

- **影响**：最终问题阶段本应只允许继续提问或显式关闭，却可能被一个新的 continue 重新带回主线教学，破坏最终化边界。
- **建议**：为最终阶段设置独立的 `FINAL_QUESTION_PHASE` 回返路径，或让 `ANSWERING_SIDE_QUESTION` 保存原返回状态；最终阶段不得使用普通 `AWAITING_QUESTIONS_OR_CONTINUE`。

### PCS-WORKFLOW-002 — readiness 审计失败后可被 continue 绕过

- **级别**：P0
- **复现路径**：

  ```text
  FINAL_AUDIT --audit-fail--> AWAITING_QUESTIONS_OR_CONTINUE
  AWAITING_QUESTIONS_OR_CONTINUE --continue--> TEACHING_CURRENT_NODE
  ```

- **实际验证**：

  ```text
  AUDIT_FAIL_STATE=AWAITING_QUESTIONS_OR_CONTINUE
  CONTINUE_AFTER_AUDIT_FAIL=(True, 'advance permitted')
  ```

- **影响**：审计失败原因没有进入 `can_advance()` 的硬门禁；调用方只要传入 `strict_validation_passed=True`，就可能继续主线，而不是修复 readiness blocker。
- **建议**：增加 `readiness_status`/`final_audit_pending` 硬字段；审计失败时唯一下一动作必须是 backfill/repair/re-audit。

### PCS-WORKFLOW-003 — 回忆题等待期间没有处理用户直接提问的状态转移

- **级别**：P1
- **复现**：

  ```text
  transition('AWAITING_RECALL', 'side-question')
  ```

- **实际结果**：抛出 `event 'side-question' is not allowed from AWAITING_RECALL`。
- **影响**：用户不按预期回答回忆题，而是直接提出问题时，协议没有定义“保存支线问题、保留回忆题待处理、回答后回到原状态”的闭环。
- **建议**：增加带返回状态的 question interruption，或把等待回忆题与等待问题统一为可排队的 `pending_user_intents`。

### PCS-WORKFLOW-004 — 混合消息没有可执行的意图队列

- **级别**：P1
- **场景**：用户在同一条消息中既回答回忆题，又提出一个新问题，或同时要求“继续 + 深讲 + 修改代码”。
- **问题**：提示词要求拆分意图，但状态机只有单事件转移，没有 `recall-answer + side-question` 或 `continue + request` 的原子排队模型。
- **影响**：真实宿主需要自行决定优先级，可能丢失一个意图、错误消费 continue，或把新问题误判为主线推进。
- **建议**：增加机器可验证的输入意图队列、优先级和逐项消费 receipt。

### PCS-WORKFLOW-005 — 记忆许可仍依赖调用方正确传递状态

- **级别**：P1
- **证据**：`can_advance()` 不传 `memory_status` 时默认按 `enabled` 处理；详见 [SELF_TEST_REPORT_5.4.0.md](SELF_TEST_REPORT_5.4.0.md) 的 PCS-SELF-001。
- **影响**：宿主漏传或模型忘传状态时，记忆许可可能被绕过。
- **建议**：将 `memory_status` 设为必填，或默认 `pending` 并要求显式传入 `enabled/disabled`。

### PCS-WORKFLOW-006 — 真实宿主尚未证明启动、恢复和发送前门禁闭环

- **级别**：P1（验证缺口）
- **未执行**：Claude/Codex golden conversation、上下文压缩恢复、跨模型行为、宿主 pre-response hook。
- **影响**：当前结论只能说明本地控制工具和静态协议代理通过，不能证明任何宿主都按顺序询问、调用工具、保存、暂停和恢复。

## 5. 闭环结论

当前工作流不是“所有路径都闭环通过”：

- 正常主线、普通支线问题、复合问题、错误回答、旧 continue 和记忆初始化的本地代理测试基本闭环；
- 最终问题阶段支线、readiness 失败恢复、回忆题期间插入问题和混合消息仍存在状态机缺口；
- 宿主层的自动询问、工具调用和响应拦截仍是外部验证项。

因此当前 Skill 应标记为：

```text
local_control_plane: partially_validated
normal_learning_loop: proxy_pass
finalization_branch: blocker_found
mixed_user_intents: not_closed
real_host_enforcement: not-run
```

本报告只记录审计结果，没有修改学习项目的 LOG、QA、最终文档或记忆目录，也没有将静态代理结果宣称为真实宿主通过。
