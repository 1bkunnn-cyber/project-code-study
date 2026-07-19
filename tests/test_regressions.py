from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "project-study-document" / "scripts"))

import interaction_state
import validate_finalization_bundle
import validate_learning_ledger
import validate_study_document


STAMP = "2026-07-19T12:00:00+08:00"


def replace_placeholders(text: str, mapping: dict[str, str]) -> str:
    for key, value in mapping.items():
        text = text.replace("{{" + key + "}}", value)
    return re.sub(r"\{\{[A-Z0-9_]+\}\}", "initialized", text)


def make_bundle(root: Path, question_count: int = 1) -> tuple[Path, Path]:
    last_q = f"Q-{question_count:03d}" if question_count else "none"
    last_tx = f"TX-{question_count + 1:04d}"
    log = (ROOT / "assets" / "PROJECT_STUDY_LOG.template.md").read_text(encoding="utf-8")
    log = replace_placeholders(log, {
        "PROJECT_NAME": "Demo", "PROJECT_PATH_OR_URL": "D:/demo", "BRANCH_OR_UNKNOWN": "main",
        "COMMIT_OR_UNKNOWN": "abc1234", "CREATED_AT": STAMP, "UPDATED_AT": STAMP,
        "TARGET_OUTCOME": "understand", "USER_CURRENT_CONCERN": "runtime path",
    })
    replacements = {
        'current_step: "0"': 'current_step: "0"',
        'current_scenario: "map"': 'current_scenario: "RUN-main"',
        'current_node_id: "NODE-pending"': 'current_node_id: "NODE-001"',
        'continuation_node_id: "NODE-pending"': 'continuation_node_id: "NODE-001"',
        'interaction_state: "TEACHING_CURRENT_NODE"': 'interaction_state: "READY_TO_GENERATE"',
        'last_question_id: "none"': f'last_question_id: "{last_q}"',
        'last_transaction_id: "TX-0001"': f'last_transaction_id: "{last_tx}"',
        'learner_closed_question_phase: false': 'learner_closed_question_phase: true',
        'learner_consented_to_generation: false': 'learner_consented_to_generation: true',
        '| 当前场景 | `map` |': '| 当前场景 | `RUN-main` |',
        '| 当前节点 | `NODE-pending` |': '| 当前节点 | `NODE-001` |',
        '| 继续节点 ID | `NODE-pending` |': '| 继续节点 ID | `NODE-001` |',
        '| 交互状态 | `TEACHING_CURRENT_NODE` |': '| 交互状态 | `READY_TO_GENERATE` |',
        '| 最近 Q ID | `none` |': f'| 最近 Q ID | `{last_q}` |',
        '| 最近事务 ID | `TX-0001` |': f'| 最近事务 ID | `{last_tx}` |',
        '| 最近成功事务 ID | `TX-0001` |': f'| 最近成功事务 ID | `{last_tx}` |',
    }
    for old, new in replacements.items():
        log = log.replace(old, new)
    route = """| Step | 主题 | Required | 状态 | 完成标准 | 当前行为证据 | K ID | Transaction ID | 下一决策 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 项目地图与证据边界 | `yes` | `done` | 能定位入口 | 已完成调用追踪 | K-001 | {tx} | 最终化 |
""".format(tx=last_tx)
    log = re.sub(r"\| Step \| 主题 \| Required .*?(?=\n### 3\.2)", route.rstrip(), log, flags=re.S)
    scenario = """| Scenario ID | 场景 | Required | 入口 / 命令 | 目标输出 | 静态或运行验证 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| RUN-main | main | yes | src/main.py | output | runtime | verified |"""
    log = re.sub(r"\| Scenario ID \| 场景 \| Required .*?(?=\n### 3\.3)", scenario, log, flags=re.S)
    nodes = """| 顺序 | 场景 | 微 Step | Node ID | 调用者 | 当前类 / 函数 | 下游节点 | 输入 / 输出 | 前置依赖 | 状态 | Reason | Impact | Revisit condition | Learner acceptance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | RUN-main | 0.1 | NODE-001 | entry | main | end | input/output | none | verified | none | none | none | yes |"""
    log = re.sub(r"\| 顺序 \| 场景 \| 微 Step .*?(?=\n### 3\.4)", nodes, log, flags=re.S)
    k_index = f"""| K ID | Step | Node ID | 核心结论 | 调用 / Shape 边界 | 证据 ID | 修正 ID | 掌握行为证据 | Transaction ID | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| K-001 | 0 | NODE-001 | entry calls main | input -> output | SRC-001 | none | learner traced call | {last_tx} | verified |"""
    log = re.sub(r"\| K ID \| Step \| Node ID .*?(?=\n### 4\.1\.1)", k_index, log, flags=re.S)
    card = f"""
### K-001 — Step 0 / NODE-001

- Transaction ID: {last_tx}
- Prerequisites: repository layout
- Learning objective: trace the representative entry
- Runtime position: RUN-main / NODE-001
- Complete explanation: The entry validates input, invokes the main operation, and returns the verified output artifact.
- Source locations: src/main.py:1-20 / SRC-001
- Inputs / outputs / Shapes / states: input object becomes one output object with validated state
- Rationale / alternatives / trade-offs: a single entry centralizes validation; alternate direct calls trade clarity for coupling
- Important Q IDs: {last_q}
- Canonical M/C IDs and wording: none; no correction was required
- Evidence status and remaining boundary: 已确认 E3; deployment is outside this fixture
- Self-check: reconstruct the caller, operation, and output
- Complete reference answer: entry validates input, calls main, and returns output in that order
- Next connection: final evidence audit
- Mastery behavior evidence: learner reconstructed the call boundary
"""
    log = log.replace("### 4.2 掌握度地图", card + "\n### 4.2 掌握度地图")
    q_rows = "\n".join(
        f"| Q-{i:03d} | 0 / NODE-001 | question {i} | none | closed | no | SRC-001 | none |"
        for i in range(1, question_count + 1)
    )
    q_header = "| Q ID | Step / Node | 问题摘要 | Parent Q | 状态 | 是否阻塞 | 修正 / 证据 ID | 下一动作 |\n| --- | --- | --- | --- | --- | --- | --- | --- |"
    log = re.sub(r"\| Q ID \| Step / Node \| 问题摘要 .*?(?=\n---\n\n## 9)", q_header + ("\n" + q_rows if q_rows else ""), log, flags=re.S)
    tx_table = f"""| Transaction ID | 时间 | QA delta | LOG delta | 精确回读 | Strict validation | Receipt |
| --- | --- | --- | --- | --- | --- | --- |
| {last_tx} | {STAMP} | questions | state and knowledge | pass | pass | saved |"""
    log = re.sub(r"\| Transaction ID \| 时间 \| QA delta .*?(?=\n---\n\n## 13)", tx_table, log, flags=re.S)

    qa = (ROOT / "assets" / "PROJECT_STUDY_QA.template.md").read_text(encoding="utf-8")
    qa = replace_placeholders(qa, {"PROJECT_NAME": "Demo", "PROJECT_PATH_OR_URL": "D:/demo", "CREATED_AT": STAMP, "UPDATED_AT": STAMP})
    qa = qa.replace('last_question_id: "none"', f'last_question_id: "{last_q}"')
    qa = qa.replace('last_transaction_id: "TX-0001"', f'last_transaction_id: "{last_tx}"')
    index_rows = []
    details = []
    for i in range(1, question_count + 1):
        qid, txid = f"Q-{i:03d}", f"TX-{i + 1:04d}"
        index_rows.append(f"| {qid} | 2026-07-19 | 0 / NODE-001 | code | question {i} | none | closed | detail | none | {txid} |")
        details.append(f"""### {qid} — question {i}

- 日期：2026-07-19
- Step / Node：0 / NODE-001
- Parent Q：none
- 主线继续位置：NODE-001
- 用户问题原意：Why does the entry call the main operation?
- 直接结论：It preserves one validated runtime boundary.
- 判断：正确
- 用户回答中正确的部分：The caller and callee were located.
- 缺失或需要纠正的部分：The validation boundary also needed explanation.
- 完整参考答案：The entry validates the input first, calls the main operation second, and returns the verified output last.
- 项目 / 论文 / 背景证据：src/main.py:1-20 / SRC-001 / E3
- 是否改变旧结论：no
- 关联 M-/C-/SRC- ID：SRC-001
- 最小验证动作：trace input to output
- 回到主线：NODE-001
- 状态：closed
- Transaction ID：{txid}
- Persistence receipt：saved after exact LOG/QA readback and strict validation
""")
    qa_header = "| Q ID | 日期 | Step / Node | 类型 | 问题摘要 | Parent Q | 状态 | 回答位置 | 修正 ID | Transaction ID |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"
    qa = re.sub(r"\| Q ID \| 日期 \| Step / Node .*?(?=\n类型：)", qa_header + ("\n" + "\n".join(index_rows) if index_rows else ""), qa, flags=re.S)
    qa = qa.replace("## 3. 用户心得与学习感受", "\n".join(details) + "\n## 3. 用户心得与学习感受")
    qa = qa.replace("| 最近一个 Q ID | `无` |", f"| 最近一个 Q ID | `{last_q}` |")
    qa = qa.replace("| 最近成功事务 ID | `TX-0001` |", f"| 最近成功事务 ID | `{last_tx}` |")

    log_path, qa_path = root / "PROJECT_STUDY_LOG.md", root / "PROJECT_STUDY_QA.md"
    log_path.write_text(log, encoding="utf-8")
    qa_path.write_text(qa, encoding="utf-8")
    return log_path, qa_path


def make_document(root: Path, validation_status: str = "validated") -> Path:
    explanation = "This unit teaches the verified runtime boundary in complete execution order. The entry checks the input contract, invokes the primary operation, preserves the returned state, and exposes one traceable output for downstream audit."
    document = f"""---
document_type: project-study-document
schema_version: "1.2"
status: "complete"
project_name: "Demo"
project_path: "D:/demo"
repository_revision: "abc1234"
source_transaction_id: "TX-0002"
readiness_transaction_id: "TX-0002"
readiness_status: "pass"
learning_goal: "understand"
audience: "learner"
language: "zh-CN"
generated_at: "{STAMP}"
source_ledger: "PROJECT_STUDY_LOG.md"
source_qa: "PROJECT_STUDY_QA.md"
validation_status: "{validation_status}"
cold_start_status: "static-proxy-pass"
---
# Demo 项目学习文档
## 1. 文档身份与证据范围
Revision abc1234; source transaction TX-0002; readiness pass.
## 2. 学习成果摘要
已确认：the representative runtime boundary is traceable from source and runtime evidence.
## 3. 项目、任务与问题定义
The project transforms one validated input into one auditable output.
## 4. 动态学习路线、知识覆盖与掌握情况
| 指标 | 数量或结论 |
| --- | --- |
| 已完成 Step / 微 Step | 1 |
| 已映射到复习单元 | 1 |
| 已明确跳过 | 0 |
| 未映射 Step | 无 |

| Step / 微 Step | 状态 | 本 Step 学到的知识 | RUN / NODE / K | 掌握证据 | 重要 Q / 修正 | 复习单元 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | done | trace the entry boundary | RUN-main / NODE-001 / K-001 | learner reconstructed caller and output | Q-001 | [UNIT-001](#unit-001) |
## 5. 运行场景与真实调用链
RUN-main: NODE-001 entry -> validated output.
## 6. 可重新学习的核心知识单元
<a id="unit-001"></a>

### UNIT-001 — Representative runtime boundary
- 覆盖 Step：0
- 前置知识：repository layout and function calls
- 本单元解决的问题：how the real entry validates input and produces the representative output
- 学习目标：reconstruct caller, operation, state transition, and downstream result
- 运行位置与上游 / 下游：RUN-main / NODE-001; upstream external input; downstream output audit
- 源码、配置、公式或论文位置：src/main.py:1-20 / SRC-001
- 证据状态：已确认 E3 from source and runtime trace
- 未验证边界：deployment adapters were outside the studied route

#### 核心讲解
{explanation}

#### 关键源码执行顺序
First validate the input contract; second invoke the primary operation; third preserve the returned state; finally emit the output artifact for downstream inspection.

#### 输入、输出、Shape、公式与状态变化
One input object enters an unchecked state, becomes validated, passes through the main operation, and exits as one output object with an auditable success state.

#### 设计原因、替代方案与取舍
Centralizing validation creates one reliable boundary and simpler evidence collection. Direct calls reduce indirection but duplicate validation and weaken auditability.

#### 重要提问、误区与规范修正
Q-001 asked why the entry exists. The canonical answer is that it owns validation and the observable runtime boundary; no M/C correction was required.

#### 自测
Reconstruct the caller, validation, main call, output state, and the evidence that supports this order.

#### 参考答案
The external caller enters NODE-001; NODE-001 validates input, calls the main operation, preserves its result, and emits the verified output. SRC-001 and runtime evidence confirm the order.

#### 与下一知识单元的连接
The output and evidence receipt connect to the final coverage and reproducibility audit.
## 7. 数据、Shape 与状态流
Input object -> validated object -> output object.
## 8. 目标函数、训练、推理与评估
This fixture contains one inference-style runtime boundary; training objectives are outside the declared evidence scope.
## 9. 论文—代码映射与设计解释
| 论文或设计概念 | 论文/设计证据 | 当前代码证据 | 状态 | 复现影响 |
| --- | --- | --- | --- | --- |
| validated entry | design contract | SRC-001 | 已确认 | defines minimum run |
## 10. 用户重要提问
### Q-001 — Why the entry boundary exists
- 学习位置：Step 0 / RUN-main / NODE-001
- 用户问题：Why does the entry call the main operation?
- 为什么重要：It unlocks the representative runtime route.
- 规范答案：It validates input, invokes the operation, and exposes the verified output boundary.
- 证据：src/main.py:1-20 / SRC-001 / E3
- 改变了什么理解：The entry is an evidence boundary, not only a wrapper.
- 关联修正：none
- 当前状态：confirmed
## 11. 误区、规范修正与认知变化
| M/C ID | 原问题或旧说法 | 规范表述 | 证据 | 影响范围 | Stale pattern |
| --- | --- | --- | --- | --- | --- |
| none | no historical correction | current explanation remains canonical | SRC-001 | UNIT-001 | none |
## 12. 相关方法、相似思想与模块组合
A direct-call alternative trades auditability for fewer layers; this is an engineering comparison, not a research contribution.
## 13. 实验、失败、局限与未解决事项
The runtime path passed. Deployment and multi-scenario behavior remain outside the declared fixture.
## 14. 复现、验证与修改指南
Run the entry with one valid input and verify one output plus the evidence receipt.
## 15. 后续行动
Review the output contract before extending another scenario. Cold-start static proxy passed; real cross-model run remains not-run.
## 16. 证据与产物索引
| ID / 类型 | 路径或位置 | 支持的结论 | 状态 |
| --- | --- | --- | --- |
| SRC-001 | src/main.py:1-20 | runtime boundary | E3 |
"""
    path = root / "PROJECT_STUDY_DOCUMENT.md"
    path.write_text(document, encoding="utf-8")
    return path


class RegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def strict_errors(self, log: Path, qa: Path) -> list[str]:
        log_text = log.read_text(encoding="utf-8")
        qa_text = qa.read_text(encoding="utf-8")
        errors, log_fm, _ = validate_learning_ledger.validate_text(log_text, strict=True)
        qa_errors, qa_fm, _ = validate_learning_ledger.validate_text(qa_text, strict=True)
        errors.extend(qa_errors)
        validate_learning_ledger.validate_cross(log_text, log_fm, qa_text, qa_fm, errors)
        return errors

    def test_T01_partial_transaction_cannot_validate_as_saved(self) -> None:
        log, qa = make_bundle(self.root)
        qa.write_text(qa.read_text(encoding="utf-8").replace('last_transaction_id: "TX-0002"', 'last_transaction_id: "TX-9999"'), encoding="utf-8")
        self.assertTrue(any("transaction" in item.lower() for item in self.strict_errors(log, qa)))

    def test_T02_three_followups_persist_with_unique_ids(self) -> None:
        log, qa = make_bundle(self.root, question_count=3)
        self.assertEqual(self.strict_errors(log, qa), [])
        self.assertEqual(set(re.findall(r"(?m)^### (Q-\d+)", qa.read_text(encoding="utf-8"))), {"Q-001", "Q-002", "Q-003"})

    def test_T03_recall_answer_pauses(self) -> None:
        self.assertEqual(interaction_state.transition("ANSWERING_RECALL", "answer-saved"), "AWAITING_QUESTIONS_OR_CONTINUE")
        self.assertFalse(interaction_state.can_advance("AWAITING_QUESTIONS_OR_CONTINUE"))

    def test_T04_old_continue_cannot_survive_question(self) -> None:
        state = interaction_state.transition("AWAITING_QUESTIONS_OR_CONTINUE", "side-question")
        state = interaction_state.transition(state, "answer-saved")
        self.assertFalse(interaction_state.can_advance(state, fresh_continue=False))

    def test_T05_interrupted_node_is_not_done(self) -> None:
        with self.assertRaises(ValueError):
            interaction_state.transition("ANSWERING_SIDE_QUESTION", "continue")

    def test_T06_invalid_or_mixed_node_state_fails(self) -> None:
        log, qa = make_bundle(self.root)
        log.write_text(log.read_text(encoding="utf-8").replace("| verified | none | none | none | yes |", "| skipped or tracked | none | none | none | yes |"), encoding="utf-8")
        self.assertTrue(any("NODE state" in item for item in self.strict_errors(log, qa)))

    def test_T07_planned_step_blocks_finalization(self) -> None:
        log, qa = make_bundle(self.root)
        log.write_text(log.read_text(encoding="utf-8").replace("| `done` | 能定位入口", "| `planned` | 能定位入口"), encoding="utf-8")
        manifest = validate_finalization_bundle.evaluate_bundle(log, qa)
        self.assertFalse(manifest["ready"])
        self.assertIn("0", manifest["nonfinal_steps"])

    def test_T08_hidden_chat_answer_blocks_finalization(self) -> None:
        log, qa = make_bundle(self.root)
        qa.write_text(qa.read_text(encoding="utf-8").replace("The entry validates the input first", "详见 chat。The entry validates the input first"), encoding="utf-8")
        manifest = validate_finalization_bundle.evaluate_bundle(log, qa)
        self.assertFalse(manifest["ready"])
        self.assertTrue(manifest["qa_hidden_chat_dependencies"])

    def test_T09_duplicate_unit_id_and_anchor_fail(self) -> None:
        log, qa = make_bundle(self.root)
        doc = make_document(self.root)
        text = doc.read_text(encoding="utf-8")
        block = re.search(r"(?ms)(<a id=\"unit-001\"></a>.*?)(?=^## 7\.)", text).group(1)
        doc.write_text(text.replace("## 7.", block + "\n## 7.", 1), encoding="utf-8")
        errors = validate_study_document.validate(doc, allow_template=False, ledger_path=log, qa_path=qa, preflight=False)
        self.assertTrue(any("duplicate UNIT" in item for item in errors))

    def test_T10_placeholder_filler_fails(self) -> None:
        log, qa = make_bundle(self.root)
        doc = make_document(self.root)
        doc.write_text(doc.read_text(encoding="utf-8").replace("This unit teaches", "本单元为概念层，无具体张量。 This unit teaches"), encoding="utf-8")
        errors = validate_study_document.validate(doc, allow_template=False, ledger_path=log, qa_path=qa, preflight=False)
        self.assertTrue(any("forbidden placeholder" in item for item in errors))

    def test_T11_stale_correction_in_summary_fails(self) -> None:
        log, qa = make_bundle(self.root)
        old = "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n\n旧表述需标记"
        row = "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n| M-001 | old | imprecise | canonical | SRC-001 | summary | 旧说法 | retest | TX-0002 | canonical |\n\n旧表述需标记"
        log.write_text(log.read_text(encoding="utf-8").replace(old, row), encoding="utf-8")
        doc = make_document(self.root)
        doc.write_text(doc.read_text(encoding="utf-8").replace("已确认：", "已确认：旧说法；"), encoding="utf-8")
        errors = validate_study_document.validate(doc, allow_template=False, ledger_path=log, qa_path=qa, preflight=False)
        self.assertTrue(any("stale pattern" in item for item in errors))

    def test_T12_validated_flag_does_not_hide_errors(self) -> None:
        log, qa = make_bundle(self.root)
        doc = make_document(self.root, validation_status="validated")
        doc.write_text(doc.read_text(encoding="utf-8").replace("#### 参考答案", "#### Missing answer heading"), encoding="utf-8")
        errors = validate_study_document.validate(doc, allow_template=False, ledger_path=log, qa_path=qa, preflight=False)
        self.assertTrue(errors)

    def test_T13_step_and_node_statuses_are_separate(self) -> None:
        log, qa = make_bundle(self.root)
        self.assertEqual(self.strict_errors(log, qa), [])
        self.assertIn("NODE-001", log.read_text(encoding="utf-8"))

    def test_T14_cold_start_static_proxy_passes_complete_unit(self) -> None:
        log, qa = make_bundle(self.root)
        doc = make_document(self.root, validation_status="pending")
        self.assertEqual(validate_study_document.validate(doc, allow_template=False, ledger_path=log, qa_path=qa, preflight=True), [])
        doc.write_text(doc.read_text(encoding="utf-8").replace('validation_status: "pending"', 'validation_status: "validated"'), encoding="utf-8")
        self.assertEqual(validate_study_document.validate(doc, allow_template=False, ledger_path=log, qa_path=qa, preflight=False), [])

    def test_T15_invariants_work_without_control_prompt(self) -> None:
        self.assertEqual(interaction_state.transition("ANSWERING_SIDE_QUESTION", "answer-saved"), "AWAITING_QUESTIONS_OR_CONTINUE")
        self.assertNotIn("prompt", interaction_state.TRANSITIONS)

    def test_T16_visual_protocol_prefers_mermaid_and_run_node_labels(self) -> None:
        text = (ROOT / "references" / "runtime-trace-protocol.md").read_text(encoding="utf-8")
        self.assertIn("Mermaid", text)
        self.assertIn("RUN/NODE", text)
        self.assertIn("Avoid large shaded character art", text)


if __name__ == "__main__":
    unittest.main()
