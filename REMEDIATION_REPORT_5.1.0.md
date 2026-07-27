# project-code-study 5.1.0 修缮报告

## 范围与基线

权威输入为 `PROJECT_CODE_STUDY_SUPERVISION_AND_OPTIMIZATION_HANDOFF.md`。历史学习 LOG、QA、最终文档和宿主会话只读保留，未修改。Skill Git 基线为 `3634421`；5.0.0 原有测试基线为 17/17 通过，但未覆盖失败后的成功旁路。

## 主要修复

| 修复层 | 可执行机制 |
| --- | --- |
| P0 事务 | `project_study_transaction.py` 统一分配 ID、结构化写入、section 边界、暂存、回读、validator、原子替换和机器 receipt；失败返回 `unsaved-partial`。 |
| P0 状态 | `interaction_state.py` 的 `can_advance()` 现在同时检查 fresh continue、open/retest Q、pending response、saved receipt、NODE 语义完成和 strict validation。 |
| P0 最终化 | `finalize_project_study.py` 强制 fresh readiness、候选文件、preflight、final validation 和 atomic replace；失败不改变正式目标；legacy schema 不能旁路。 |
| P0 证据 | `claim_verifier.py` 按声明类型核验，不包含项目/函数/张量/Q-ID 特判。 |
| P1 教学 | 新增 source-NODE、主动回忆、复合问题、聊天/QA 双层输出和 UNIT 语义契约，并把源码占位路径/部分 UNIT 接入 validator。 |
| P2 呈现 | prompts 和协议固定线性链、表格、Mermaid、可编辑图源与纯文本回退。 |

## 观察 ID → 抽象修复 → 测试证据

| 观察 | 抽象模式 | 修复文件 | 测试 |
| --- | --- | --- | --- |
| PCS-OBS-001/004/007/014/015/019/020/027 | 教学字段不足、Shape/代码/UNIT 语义缺失 | `references/teaching-output-contract.md`, `skills/project-study-document/scripts/validate_study_document.py` | T-26/T-27/T-30 |
| PCS-OBS-002/006 | 源码定位未核验、占位路径 | `claim_verifier.py`, document validator | T-26 |
| PCS-OBS-003/013/021 | 主动回忆未逐项对齐、错误未复测 | `interaction_state.py`, teaching contract, claim verifier | T-21/T-30 |
| PCS-OBS-005/012/018 | QA 独立性、聊天/QA 双层、复合问题 | `project_study_transaction.py`, `user-prompts.md` | T-20/T-23/T-24 |
| PCS-OBS-008/009/010/024/025 | 覆盖、串写、重复 ID、虚假 saved、跨文件不一致 | `project_study_transaction.py`, transaction protocol | T-18/T-19/T-24 |
| PCS-OBS-011/017 | 脆弱 ASCII/公式排版 | `teaching-output-contract.md`, `user-prompts.md` | T-16（协议） |
| PCS-OBS-022/023/028 | finalization fail-open、状态冲突、测试旁路缺口 | `finalize_project_study.py`, companion Skill, README | T-17/T-28/T-29/T-31（not-run） |
| PCS-OBS-016 | 生活化例子→公式→代码映射保留 | teaching contract and claim verifier | T-30 |
| PCS-OBS-026 | 高影响声明缺少对应证据 | `claim_verifier.py`, transaction protocol | T-30 |

## 验证状态

- 旧测试：基线 17/17；修改后结果以最终测试命令为准。
- 新增端到端/对抗性测试：覆盖 T-17～T-30；T-31 真实 Claude/Codex 宿主 golden conversation 未在本地自动化环境执行，必须报告为 `not-run`。
- 旧学习产物：只读 strict validator/readiness fail-closed 样本，未修改。
- 版本、README、CHANGELOG、5.1.0 修缮报告已更新。

## 剩余风险

真实宿主仍可能不调用工具；脚本能阻断工具入口，但不能阻止模型输出未经工具证明的自然语言，宿主侧必须把工具回执作为状态来源。Mermaid 渲染、跨模型冷启动和真实会话回放仍需单独执行，不能由静态测试代替。
