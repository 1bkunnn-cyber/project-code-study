# project-code-study 5.2.0 修缮报告

## 背景

长上下文会导致 Skill 规则被遗忘、旧结论继续流通和未经 receipt 的自然语言成功声明。此次改动吸收文件化 agent memory 的通用机制，但不复制第二套学习账本。

## 修改

| 目标 | 文件 | 机制 |
| --- | --- | --- |
| 跨轮次协议记忆 | `references/continuity-memory-protocol.md`, `assets/PROJECT_STUDY_MEMORY.template.md` | 有界 `MEMORY.md` 索引、单事实文件、类型化条目、去重/归档/冷启动同步 |
| 记忆写入门禁 | `scripts/sync_protocol_memory.py` | fresh machine receipt、源文件 hash、staged validation、原子替换、`unsaved-memory` fail-closed |
| 记忆结构校验 | `scripts/validate_protocol_memory.py` | heading 边界、失效链接、孤儿文件、重复 MEM-ID、Why/How、correction stale metadata、150/20 KiB 与 200/25 KiB 上限 |
| 自然语言声明审计 | `scripts/response_claim_guard.py` | 无 receipt 的 `saved/validated` 和普通 receipt 冒充正式文档的路径被拒绝 |
| 宿主边界 | `references/host-enforcement-boundary.md`, `SKILL.md` | 明确 Skill 内可审计但不能物理阻止完全跳过工具的宿主；支持宿主 pre-response hook 时升级为硬交付门禁 |

## 保留的权威边界

`PROJECT_STUDY_LOG.md`、`PROJECT_STUDY_QA.md`、interaction state、readiness 和 finalizer 仍是唯一学习控制面。记忆只保存可复用约束、纠正、项目决策和证据指针，不能证明 Q、NODE、Step 或正式文档状态。

## 验证结论

- 新增连续性记忆回归覆盖空 store、孤儿/失效指针、receipt-gated upsert、同 slug 更新和 response claim guard。
- 全部旧测试与新增测试合计 `38` 个，`37` 个通过，`1` 个既有真实宿主/跨模型测试明确 `not-run`/跳过。
- Python UTF-8 编译、模板/结构检查和 `git diff --check` 已执行。
- `skill-creator` 的 `quick_validate.py` 在当前环境按系统 GBK 读取 UTF-8 的实现自身失败；这不是 Skill 结构失败，已用无写入 UTF-8 compile 和本地审计替代，未将其宣称为通过。

## 未解决风险

若宿主完全不调用控制工具或没有 pre-response hook，任何 Skill 都无法从模型输出通道物理拦截自由文本；该场景只能报告 `best-effort`，不能声称已 enforced。真实 Claude/Codex 宿主 hook、跨模型和长会话 forward-test 仍需在目标宿主中单独运行。
