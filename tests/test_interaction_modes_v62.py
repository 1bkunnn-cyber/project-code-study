from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import study_events


class IntentEnvelopeV62Tests(unittest.TestCase):
    def test_empty_input_has_no_intents(self) -> None:
        envelope = study_events.build_input_event("   ", "INPUT-0062", "AWAITING_RECALL")
        self.assertEqual(envelope["schema_version"], "6.2")
        self.assertEqual(envelope["intents"], [])

    def test_complex_single_question_is_not_fragmented(self) -> None:
        text = "请解释为什么 C2f 会影响梯度流，以及 shortcut 如何参与？"
        envelope = study_events.build_input_event(text, "INPUT-0063", "TEACHING_CURRENT_NODE")
        questions = [item for item in envelope["intents"] if item["kind"] == "question"]
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]["text"], text)

    def test_unnumbered_questions_are_separate_and_source_bound(self) -> None:
        text = "Conv 为什么改变通道数？C2f 的分支从哪里来？最后输出 Shape 是多少？"
        envelope = study_events.build_input_event(text, "INPUT-0064", "AWAITING_QUESTIONS_OR_CONTINUE")
        questions = [item for item in envelope["intents"] if item["kind"] == "question"]
        self.assertEqual(len(questions), 3)
        for order, item in enumerate(questions, 1):
            start, end = item["source_span"]
            source = text[start:end]
            self.assertEqual(item["source_order"], order)
            self.assertEqual(item["text"], source)
            self.assertEqual(item["source_text_hash"], hashlib.sha256(source.encode()).hexdigest())

    def test_twenty_numbered_questions_have_no_implicit_limit(self) -> None:
        text = "\n".join(f"{index}. 第 {index} 个问题是什么？" for index in range(1, 21))
        envelope = study_events.build_input_event(text, "INPUT-0065", "TEACHING_CURRENT_NODE")
        questions = [item for item in envelope["intents"] if item["kind"] == "question"]
        self.assertEqual(len(questions), 20)
        self.assertEqual([item["source_order"] for item in questions], list(range(1, 21)))

    def test_question_or_correction_expires_continue_from_same_event(self) -> None:
        text = "原来的 Shape 结论不对；请解释 Concat 的通道来源？；继续"
        envelope = study_events.build_input_event(text, "INPUT-0066", "AWAITING_QUESTIONS_OR_CONTINUE")
        self.assertEqual(
            [(item["kind"], item["status"]) for item in envelope["intents"]],
            [("correction", "pending"), ("question", "pending"), ("continue", "expired-by-question")],
        )

    def test_envelope_rejects_tampered_source_binding(self) -> None:
        text = "第一个问题？第二个问题？"
        envelope = study_events.build_input_event(text, "INPUT-0067", "AWAITING_RECALL")
        envelope["intents"][0]["source_span"] = [1, 3]
        errors = study_events.validate_intent_envelope(envelope, text)
        self.assertTrue(any("source" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
