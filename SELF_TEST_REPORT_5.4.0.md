# project-code-study 5.4.0 自测与问题记录

## 1. 测试范围

本轮测试以真实使用习惯为中心，不只验证单个函数返回值。覆盖以下习惯：

1. 用户只给一句启动指令；
2. 用户提供完整学习目标、深度和运行场景；
3. 用户选择讲解方式后再开始学习；
4. 用户在当前 NODE 中直接提问；
5. 用户一次提出多个问题；
6. 用户回答主动回忆题时只回答一部分或回答错误；
7. 用户回答后直接发送“继续”；
8. 用户使用旧的“继续”或在问题未关闭时继续；
9. 用户中断会话、压缩上下文后恢复；
10. 用户启用、拒绝或不回答连续性记忆确认；
11. 用户要求纠正旧结论、修复链接或诊断记录；
12. 用户关闭问题阶段并要求正式文档或阶段性草稿；
13. 宿主完全跳过控制工具，仅输出自然语言。

## 2. 已执行测试

| 测试 | 结果 | 证据 |
| --- | --- | --- |
| 既有回归与对抗测试 | 48 个通过，1 个真实宿主测试跳过 | `python -m unittest discover -s tests -p 'test_*.py' -v` |
| Skill 结构校验 | 通过 | `quick_validate.py` |
| Skill 质量审计 | 通过，`missing_refs=0` | `skill-audit.py` |
| Python 静态编译 | 通过 | 不写 `.pyc` 的 `compile()` 检查 |
| 用户同意后初始化记忆 | 通过 | 临时目录黑盒测试 |
| 未同意时不创建记忆目录 | 通过 | 临时目录黑盒测试 |
| `memory-consent-pending` 阻断推进 | 通过 | `interaction_state.advance_decision()` |
| 用户拒绝记忆后继续学习 | 通过 | `memory_status=disabled` 的状态代理测试 |
| 无 receipt 的 `saved/validated` 声明 | 通过 | `response_claim_guard.py` 黑盒测试 |
| 混合“未保存 + 已保存”声明 | 通过拒绝 | response guard 黑盒测试 |
| `git diff --check` | 通过 | 当前 Skill 工作区 |

## 3. 用户习惯场景结果

### 已有可执行覆盖

- 直接提问不会推进主线；
- 复合问题会拆成独立 Q-ID；
- 错误或部分正确回答进入 `retest-due`；
- 未保存问题、旧 continue、缺少新 continue 都不能推进；
- 正式文档在 readiness 失败后保持目标文件不变；
- 记忆初始化没有 `--user-consent` 时不会创建目录；
- 用户拒绝记忆后可以继续学习，但不会创建记忆目录；
- 没有机器 receipt 时不能产生正向保存或最终化声明。

### 只能作为静态代理、尚未完成真实宿主测试

- 用户只输入“继续”时，真实宿主是否正确识别为一次 fresh continue；
- 用户一句话中同时表达“继续、顺便解释、修改代码”时，宿主是否正确拆分优先级；
- 用户在长回复中插入新问题、纠正旧答案或改变学习深度时，宿主是否保持当前状态；
- 上下文压缩后，宿主是否真的先读取 memory/LOG/QA 再恢复；
- 宿主是否在首次启动时自动询问记忆许可；
- 宿主是否在发送最终自然语言前执行 response claim guard；
- 不同模型是否都会遵守“回答后停在等待状态”。

## 4. 发现的问题

### PCS-SELF-001 — `memory_status` 缺省值允许绕过记忆许可

- **级别**：P1
- **复现**：

  ```powershell
  python -c "import sys; sys.path.insert(0, 'scripts'); import interaction_state as s; print(s.advance_decision('AWAITING_QUESTIONS_OR_CONTINUE', fresh_continue=True))"
  ```

- **实际结果**：`(True, 'advance permitted')`。
- **问题**：调用方不传 `memory_status` 时默认为 `enabled`。即使项目根目录没有 `.project-study-memory/`，也可能允许继续推进。
- **影响**：记忆确认目前依赖宿主正确传入 `pending` 或 `disabled`，不是由推进工具根据项目文件状态自动推导。
- **建议**：将 `memory_status` 设为必填，或将默认值改为 `pending`，只有显式 `enabled/disabled` 才允许推进。

### PCS-SELF-002 — `--user-consent` 是调用方自报字段

- **级别**：P1
- **问题**：`--user-consent` 能阻止普通误调用，但无法证明真实用户确实回答了“启用”。任意宿主或模型都可以自行传入该标志。
- **影响**：它是 Skill 内部的 fail-closed 保护，不是密码学意义的用户授权证明。
- **建议**：由宿主保存用户原始响应并生成 consent receipt；初始化工具校验 receipt，而不是只接受布尔开关。

### PCS-SELF-003 — Skill 没有宿主无关的自动询问执行器

- **级别**：P1
- **问题**：当前“先询问、再初始化”主要由 `SKILL.md` 和 `user-prompts.md` 规定；仓库没有一个能够在所有宿主中自动拦截首次启动、显示问题并等待回答的通用 runner。
- **影响**：支持 Skill 但不执行控制工具的宿主，仍可能跳过询问或直接输出自然语言。
- **建议**：提供可选 host adapter/pre-response hook，并把宿主能力标记为 `enforced`、`best-effort` 或 `not-run`。

### PCS-SELF-004 — 归档目前是协议要求，不是完整自动化功能

- **级别**：P2
- **问题**：初始化会创建 `archive/`，协议要求压缩时归档过时条目，但当前 `sync_protocol_memory.py` 没有独立的 archive/compact 命令，也没有自动判断 stale 条目的实现。
- **影响**：长期记忆的去重和更新已有机械路径，过时条目的归档仍依赖宿主或模型正确执行协议。
- **建议**：增加显式 `compact/archive` 工具，要求输入旧条目、影响范围和授权，并在移动后重新校验索引、孤儿文件和活跃结论引用。

### PCS-SELF-005 — 长会话与自然语言行为流尚未在真实宿主中闭环

- **级别**：P1（验证缺口）
- **问题**：现有测试验证了状态机和工具，但没有真正驱动 Claude/Codex 宿主执行“启动 → 询问记忆 → 启用/拒绝 → 教学 → 提问 → 复测 → 继续 → 恢复”的完整对话。
- **影响**：不能据此宣称多模型、多轮用户习惯已经通过。
- **当前状态**：明确记录为 `not-run`，没有把静态代理测试宣称为真实宿主通过。

## 5. 结论

当前 Skill 的机器协议和本地工具在测试范围内通过，尤其是记忆目录的“明确同意后创建”行为已经有黑盒覆盖。但对用户习惯最关键的三个边界仍然依赖宿主：

1. 宿主是否真的询问用户；
2. 宿主是否把用户回答转换为 `memory_status` 和真实 consent receipt；
3. 宿主是否在最终响应前执行 response claim guard。

本报告只记录自测结果和问题，没有修改任何被学习项目的 LOG、QA、最终文档或记忆目录。
