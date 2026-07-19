---
document_type: project-code-study-qa
schema_version: "1.1"
project_name: "{{PROJECT_NAME}}"
project_path: "{{PROJECT_PATH_OR_URL}}"
ledger_path: "PROJECT_STUDY_LOG.md"
created_at: "{{CREATED_AT}}"
updated_at: "{{UPDATED_AT}}"
write_authorized: "yes"
last_question_id: "none"
last_transaction_id: "TX-0001"
---

<!--
PROJECT CODE STUDY Q&A CONTRACT

1. Preserve the user's substantive wording; do not turn this into a full chat transcript.
2. Every substantive new or follow-up question receives a unique Q-ID.
3. Every active-recall response receives a complete reference answer after the learner responds.
4. Link corrections to M-/C- records in PROJECT_STUDY_LOG.md.
5. Answers must be standalone; hidden-chat references and circular placeholders are forbidden.
6. Prefer append-only entries and small status patches. Verify both files and strict validation before `saved`.
-->

# {{PROJECT_NAME}} 用户问答与学习反馈

## 1. 问题索引

| Q ID | 日期 | Step / Node | 类型 | 问题摘要 | Parent Q | 状态 | 回答位置 | 修正 ID | Transaction ID |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

类型：`concept` / `code` / `syntax` / `shape` / `paper` / `runtime` / `comparison` / `review`。

## 2. 详细问答

<!--
### Q-xxx — <简短标题>

- 日期：
- Step / Node：
- Parent Q：无
- 主线继续位置：
- 用户问题原意：
- 直接结论：
- 判断：正确 / 部分正确 / 错误 / 证据不足 / 不适用
- 用户回答中正确的部分：
- 缺失或需要纠正的部分：
- 完整参考答案：
- 项目 / 论文 / 背景证据：
- 是否改变旧结论：
- 关联 M-/C-/SRC- ID：
- 最小验证动作：
- 回到主线：
- 状态：open / answered / retest-due / closed / deferred / stale
- Transaction ID：
- Persistence receipt：
-->

## 3. 用户心得与学习感受

| NOTE ID | 日期 | Step / Node | 用户原文 | 自信度 1-5 | 希望如何调整 | AI 已读取 / 调整 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |

## 4. 用户反馈

| FB ID | 日期 | Step / Node | 类型 | 用户反馈原文 | 为什么不满意 / 困难 | 希望得到什么 | 评分 1-5 | AI 回应摘要 | 调整动作 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

状态：`new` / `in-progress` / `answered` / `retest-due` / `closed`。

## 5. 维护与归档

| 项目 | 当前值 |
| --- | --- |
| 最近一次写入回读验证 | `尚未执行` |
| 最近一个 Q ID | `无` |
| 最近成功事务 ID | `TX-0001` |
| 建议归档 | `no` |
| 用户授权归档 | `no` |
