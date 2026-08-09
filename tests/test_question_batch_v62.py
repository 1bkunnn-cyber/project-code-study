from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import project_study_transaction as tx
import study_events
import validate_learning_ledger
from tests.test_regressions import make_bundle


def question_data(count: int, *, parent_id: str = "none") -> list[dict[str, str]]:
    return [
        {
            "title": f"问题 {index}",
            "question_type": "concept",
            "location": "4.2 / NODE-C2f",
            "anchor": "NODE-C2f",
            "parent_id": parent_id,
        }
        for index in range(1, count + 1)
    ]


def strict_pair(log_path: Path, qa_path: Path) -> list[str]:
    log_text = log_path.read_text(encoding="utf-8")
    qa_text = qa_path.read_text(encoding="utf-8")
    log_errors, log_fm, _ = validate_learning_ledger.validate_text(log_text, strict=True)
    qa_errors, qa_fm, _ = validate_learning_ledger.validate_text(qa_text, strict=True)
    cross: list[str] = []
    validate_learning_ledger.validate_cross(log_text, log_fm, qa_text, qa_fm, cross)
    return [*log_errors, *[f"QA: {error}" for error in qa_errors], *cross]


class QuestionBatchV62Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.log, self.qa = make_bundle(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _envelope(self, count: int, event_id: str = "INPUT-6200") -> dict[str, object]:
        text = "\n".join(f"{index}. 问题 {index} 是什么？" for index in range(1, count + 1))
        return study_events.build_input_event(text, event_id, "AWAITING_RECALL")

    def test_all_twenty_questions_are_registered_before_any_answer(self) -> None:
        receipt = self.root / "intake.json"
        result = tx.register_question_batch(
            self.log,
            self.qa,
            self._envelope(20),
            question_data(20),
            receipt_path=receipt,
            validator=lambda staged_log, staged_qa: [],
        )
        self.assertEqual(result["persistence_status"], "saved", result)
        self.assertEqual(len(result["qa_ids"]), 20)
        qa_text = self.qa.read_text(encoding="utf-8")
        for order, qid in enumerate(result["qa_ids"], 1):
            self.assertIn(f"### {qid} — 问题 {order}", qa_text)
            self.assertIn(f"- Intent 顺序：{order}", qa_text)
            block = qa_text.split(f"### {qid} —", 1)[1].split("### Q-", 1)[0]
            self.assertIn("- 回答状态：pending", block)
            self.assertNotIn("- 回答状态：answered", block)
        self.assertEqual(json.loads(receipt.read_text(encoding="utf-8"))["transaction_kind"], "question-intake")

    def test_answer_updates_existing_q_with_independent_transaction(self) -> None:
        intake = tx.register_question_batch(
            self.log,
            self.qa,
            self._envelope(3),
            question_data(3),
            validator=lambda staged_log, staged_qa: [],
        )
        target = intake["qa_ids"][0]
        answer_receipt = self.root / "answer.json"
        answered = tx.answer_question(
            self.log,
            self.qa,
            target,
            {
                "canonical_answer": "定义：C2f 是多分支特征模块。项目语境：它位于主干。类比：像并行道路。反例：单支路不是 C2f。相邻概念区别：C3 使用不同瓶颈组织。自测：分支在哪里合并？",
                "evidence": "src/model.py:10-30 / SRC-002 / E1",
                "status": "answered",
            },
            receipt_path=answer_receipt,
            validator=lambda staged_log, staged_qa: [],
        )
        self.assertEqual(answered["persistence_status"], "saved", answered)
        self.assertNotEqual(answered["tx_id"], intake["tx_id"])
        self.assertEqual(answered["qa_ids"], [target])
        text = self.qa.read_text(encoding="utf-8")
        self.assertEqual(text.count(f"### {target} —"), 1)
        self.assertIn("- 回答状态：answered", text)
        self.assertIn("- 回答状态：pending", text)
        payload = json.loads(answer_receipt.read_text(encoding="utf-8"))
        self.assertEqual(payload["transaction_kind"], "question-answer")

    def test_nth_answer_failure_preserves_earlier_answer_and_later_pending(self) -> None:
        intake = tx.register_question_batch(
            self.log,
            self.qa,
            self._envelope(3),
            question_data(3),
            validator=lambda staged_log, staged_qa: [],
        )
        common = {
            "canonical_answer": "定义：完整回答。项目语境：当前节点。类比：路径。反例：错误路径。相邻概念区别：相邻节点不同。自测：请复述。",
            "evidence": "src/model.py:10 / SRC-002 / E1",
            "status": "answered",
        }
        first = tx.answer_question(self.log, self.qa, intake["qa_ids"][0], common, validator=lambda a, b: [])
        self.assertEqual(first["persistence_status"], "saved")
        before_failure = self.qa.read_text(encoding="utf-8")
        failed = tx.answer_question(
            self.log,
            self.qa,
            intake["qa_ids"][1],
            common,
            validator=lambda a, b: ["injected validator failure"],
        )
        self.assertEqual(failed["persistence_status"], "unsaved-partial")
        self.assertEqual(self.qa.read_text(encoding="utf-8"), before_failure)
        self.assertIn("- 回答状态：answered", before_failure)
        self.assertGreaterEqual(before_failure.count("- 回答状态：pending"), 2)

    def test_follow_up_gets_new_q_and_parent_link(self) -> None:
        first = tx.register_question_batch(
            self.log,
            self.qa,
            self._envelope(1, "INPUT-6201"),
            question_data(1),
            validator=lambda a, b: [],
        )
        follow = tx.register_question_batch(
            self.log,
            self.qa,
            self._envelope(1, "INPUT-6202"),
            question_data(1, parent_id=first["qa_ids"][0]),
            validator=lambda a, b: [],
        )
        self.assertNotEqual(first["qa_ids"][0], follow["qa_ids"][0])
        self.assertIn(f"- Parent Q：{first['qa_ids'][0]}", self.qa.read_text(encoding="utf-8"))

    def test_publication_rejects_pending_batch(self) -> None:
        tx.register_question_batch(
            self.log,
            self.qa,
            self._envelope(1),
            question_data(1),
            validator=lambda a, b: [],
        )
        errors, _, _ = validate_learning_ledger.validate_text(
            self.qa.read_text(encoding="utf-8"),
            strict=True,
            publication=True,
        )
        self.assertTrue(any("pending" in error for error in errors), errors)

    def test_real_strict_validator_and_transaction_restore_captured_recall_state(self) -> None:
        envelope = self._envelope(1, "INPUT-6203")
        envelope["received_state"] = "AWAITING_RECALL"
        intake = tx.register_question_batch(
            self.log, self.qa, envelope, question_data(1), validator=strict_pair
        )
        self.assertEqual(intake["persistence_status"], "saved", intake)
        answered = tx.answer_question(
            self.log,
            self.qa,
            intake["qa_ids"][0],
            {
                "canonical_answer": "定义：C2f 是分支融合模块。项目语境：它在当前主干。类比：多路汇流。反例：单层卷积没有同样分支。相邻概念区别：C3 的瓶颈组织不同。自测：融合发生在哪里？",
                "evidence": "src/model.py:10-30 / SRC-002 / E1",
                "evidence_ids": "SRC-002",
                "status": "answered",
            },
            validator=strict_pair,
        )
        self.assertEqual(answered["persistence_status"], "saved", answered)
        self.assertIn('interaction_state: "AWAITING_RECALL"', self.log.read_text(encoding="utf-8"))

    def test_intake_rejects_tampered_envelope_without_writing(self) -> None:
        envelope = self._envelope(1, "INPUT-6204")
        envelope["intents"][0]["text"] = "被篡改的问题？"
        before_log = self.log.read_text(encoding="utf-8")
        before_qa = self.qa.read_text(encoding="utf-8")
        result = tx.register_question_batch(
            self.log,
            self.qa,
            envelope,
            question_data(1),
            validator=strict_pair,
        )
        self.assertEqual(result["persistence_status"], "unsaved-partial")
        self.assertTrue(any("source" in error for error in result["errors"]), result)
        self.assertEqual(self.log.read_text(encoding="utf-8"), before_log)
        self.assertEqual(self.qa.read_text(encoding="utf-8"), before_qa)


if __name__ == "__main__":
    unittest.main()
