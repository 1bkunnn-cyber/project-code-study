from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import memory_lifecycle


class MemoryLifecycleV6Tests(unittest.TestCase):
    def test_one_off_question_does_not_create_long_term_candidate(self) -> None:
        self.assertIsNone(
            memory_lifecycle.classify_memory_candidate(
                "这个卷积层的 stride 是多少？",
                candidate_id="M-001",
            )
        )

    def test_durable_triggers_create_typed_candidates(self) -> None:
        cases = [
            ("以后讲源码时请长期保留逐行解释和 Shape。", "message", "feedback"),
            ("纠正：这里不是转置卷积，而是最近邻上采样。", "message", "correction"),
            ("最终文档质量太低，必须能脱离聊天独立学习。", "message", "feedback"),
            ("本 Step 的持久规则：先沿真实调用链定位，再解释局部实现。", "step_complete", "project"),
        ]
        for index, (text, trigger, expected_kind) in enumerate(cases, 1):
            with self.subTest(text=text):
                candidate = memory_lifecycle.classify_memory_candidate(
                    text,
                    trigger=trigger,
                    candidate_id=f"M-{index:03d}",
                )
                self.assertIsNotNone(candidate)
                self.assertEqual(candidate["status"], "candidate")
                self.assertEqual(candidate["kind"], expected_kind)
                self.assertEqual(candidate["candidate_id"], f"M-{index:03d}")

    def test_rejection_is_terminal_and_redacts_original_content(self) -> None:
        candidate = memory_lifecycle.classify_memory_candidate(
            "以后所有教学都保留逐行源码解释。",
            candidate_id="M-010",
        )
        rejected = memory_lifecycle.transition_candidate(
            candidate,
            "rejected",
            reason="user declined persistence",
        )
        self.assertEqual(rejected["status"], "rejected")
        self.assertNotIn("content", rejected)
        self.assertIn("content_hash", rejected)
        with self.assertRaises(memory_lifecycle.MemoryLifecycleError):
            memory_lifecycle.transition_candidate(rejected, "approved")

    def test_saved_requires_approval_and_bound_release_transaction(self) -> None:
        candidate = memory_lifecycle.classify_memory_candidate(
            "纠正：Detect 的三个输出尺度不是四个。",
            candidate_id="M-011",
        )
        with self.assertRaises(memory_lifecycle.MemoryLifecycleError):
            memory_lifecycle.transition_candidate(candidate, "saved")
        approved = memory_lifecycle.transition_candidate(
            candidate,
            "approved",
            approved_by="user",
        )
        with self.assertRaises(memory_lifecycle.MemoryLifecycleError):
            memory_lifecycle.transition_candidate(approved, "saved")
        saved = memory_lifecycle.transition_candidate(
            approved,
            "saved",
            release_tx_id="TX-0042",
            receipt_hash="a" * 64,
        )
        self.assertEqual(saved["status"], "saved")
        self.assertEqual(saved["release_tx_id"], "TX-0042")
        stale = memory_lifecycle.transition_candidate(
            saved,
            "stale",
            reason="superseded by C-008",
        )
        self.assertEqual(stale["status"], "stale")

    def test_compaction_handoff_carries_memory_state_and_fails_closed_on_drift(self) -> None:
        state = {
            "current_step": "4.7",
            "current_run": "RUN-train",
            "current_node": "NODE-C2",
            "continuation_node": "NODE-C2",
            "completed_nodes": ["NODE-C1"],
            "open_questions": ["Q-063"],
            "pending_user_intents": ["retest"],
            "retest_due_questions": ["Q-063"],
            "recent_corrections": ["C-004"],
            "evidence_ids": ["SRC-008"],
            "unique_next_action": "retest Q-063",
            "active_input_event_id": "INPUT-0063",
            "question_queue_ids": ["Q-063"],
            "current_question_id": "Q-063",
            "question_queue_return_state": "AWAITING_RECALL",
        }
        handoff = memory_lifecycle.create_compaction_handoff(
            state,
            {"PROJECT_STUDY_LOG.md": "aaa", "PROJECT_STUDY_QA.md": "bbb"},
            memory_candidates=[
                {"candidate_id": "M-012", "status": "approved", "content_hash": "b" * 64}
            ],
        )
        self.assertEqual(handoff["memory_candidates"][0]["candidate_id"], "M-012")
        restored = memory_lifecycle.restore_compaction_handoff(
            handoff,
            {"PROJECT_STUDY_LOG.md": "aaa", "PROJECT_STUDY_QA.md": "changed"},
        )
        self.assertEqual(restored["status"], "REPAIR_REQUIRED")

    def test_candidate_journal_is_hash_checked_and_rejection_stays_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "candidates.json"
            candidate = memory_lifecycle.classify_memory_candidate(
                "以后每章都要有练习和答案。",
                candidate_id="M-013",
            )
            rejected = memory_lifecycle.transition_candidate(
                candidate,
                "rejected",
                reason="user declined",
            )
            memory_lifecycle.persist_candidate_journal(path, [rejected])
            loaded = memory_lifecycle.load_candidate_journal(path)
            self.assertNotIn("content", loaded["candidates"][0])
            path.write_text(path.read_text(encoding="utf-8").replace("user declined", "tampered"), encoding="utf-8")
            with self.assertRaises(memory_lifecycle.MemoryLifecycleError):
                memory_lifecycle.load_candidate_journal(path)


if __name__ == "__main__":
    unittest.main()
