from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import interaction_state
import study_events


class EventStateAndHandoffTests(unittest.TestCase):
    def test_mixed_prose_intents_keep_question_feedback_continue_order(self) -> None:
        intents = study_events.split_intents(
            "请先解释 parse_model；另外，最终文档应该写成教材，这是长期质量要求；然后继续。",
            "INPUT-0007",
        )
        self.assertEqual(
            [(item["kind"], item["input_event_id"]) for item in intents],
            [
                ("question", "INPUT-0007"),
                ("quality_feedback", "INPUT-0007"),
                ("continue", "INPUT-0007"),
            ],
        )

    def test_continue_event_is_consumed_only_once(self) -> None:
        state = {"consumed_continue_event_ids": []}
        first = study_events.consume_continue(state, "INPUT-0008")
        self.assertEqual(first["consumed_continue_event_ids"], ["INPUT-0008"])
        with self.assertRaises(study_events.EventStateError):
            study_events.consume_continue(first, "INPUT-0008")

    def test_handoff_hash_mismatch_requires_repair(self) -> None:
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
        handoff = study_events.build_handoff(
            state,
            {"PROJECT_STUDY_LOG.md": "aaa", "PROJECT_STUDY_QA.md": "bbb"},
        )
        restored = study_events.validate_handoff(
            handoff,
            {"PROJECT_STUDY_LOG.md": "aaa", "PROJECT_STUDY_QA.md": "changed"},
        )
        self.assertEqual(restored["status"], "REPAIR_REQUIRED")
        self.assertIn("PROJECT_STUDY_QA.md", restored["mismatched_artifacts"])

    def test_question_batch_restores_exact_state_after_ordered_answers(self) -> None:
        context = interaction_state.begin_question_batch(
            "AWAITING_RECALL", "INPUT-0064", ["Q-064", "Q-065"]
        )
        self.assertEqual(context["state"], "REGISTERING_QUESTION_BATCH")
        context = interaction_state.question_batch_event(context, "intake-saved")
        self.assertEqual(context["current_question_id"], "Q-064")
        context = interaction_state.question_batch_event(context, "answer-saved", qid="Q-064")
        self.assertEqual(context["current_question_id"], "Q-065")
        context = interaction_state.question_batch_event(context, "answer-saved", qid="Q-065")
        self.assertEqual(context["state"], "AWAITING_RECALL")
        self.assertEqual(context["pending_question_ids"], [])

    def test_question_batch_failure_enters_repair_without_losing_queue(self) -> None:
        context = interaction_state.begin_question_batch(
            "TEACHING_CURRENT_NODE", "INPUT-0065", ["Q-066", "Q-067"]
        )
        context = interaction_state.question_batch_event(context, "intake-saved")
        failed = interaction_state.question_batch_event(context, "answer-failed", qid="Q-066")
        self.assertEqual(failed["state"], "QUESTION_BATCH_REPAIR")
        self.assertEqual(failed["pending_question_ids"], ["Q-066", "Q-067"])
        repaired = interaction_state.question_batch_event(failed, "repair-complete")
        self.assertEqual(repaired["state"], "ANSWERING_QUESTION_QUEUE")

    def test_any_state_mismatch_enters_repair_and_returns_to_recorded_state(self) -> None:
        repaired = interaction_state.transition("TEACHING_CURRENT_NODE", "state-mismatch")
        self.assertEqual(repaired, "REPAIR_REQUIRED")
        self.assertEqual(
            interaction_state.transition(
                repaired,
                "repair-complete:TEACHING_CURRENT_NODE",
            ),
            "TEACHING_CURRENT_NODE",
        )


if __name__ == "__main__":
    unittest.main()
