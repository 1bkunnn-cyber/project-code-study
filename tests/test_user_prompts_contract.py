from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import study_events


PROMPTS = ROOT / "references" / "user-prompts.md"


class UserPromptContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = PROMPTS.read_text(encoding="utf-8")

    def test_one_start_prompt_and_natural_followups_replace_template_catalog(self) -> None:
        self.assertIn("## 唯一启动提示", self.text)
        self.assertIn("我想开始学习这个项目", self.text)
        self.assertIn("直接自然提问", self.text)
        numbered_templates = re.findall(r"^##\s+\d+\.\s+", self.text, flags=re.MULTILINE)
        self.assertLessEqual(len(numbered_templates), 1)

    def test_standard_loop_and_modes_are_explicit(self) -> None:
        for token in (
            "定位 → 学习 → 检验 → 沉淀 → 等待",
            "START", "LEARN", "ASK", "ASSESS", "RECOVER", "CLOSE", "REPAIR",
        ):
            self.assertIn(token, self.text)

    def test_multi_question_example_routes_every_question_and_expires_continue(self) -> None:
        message = "Conv 为什么改通道？C2f 如何分支？；继续"
        envelope = study_events.build_input_event(message, "INPUT-6208", "AWAITING_RECALL")
        self.assertEqual(len([item for item in envelope["intents"] if item["kind"] == "question"]), 2)
        self.assertEqual([item for item in envelope["intents"] if item["kind"] == "continue"][0]["status"], "expired-by-question")
        for token in ("全部登记", "逐题回答", "每个问题", "Q-ID", "Parent Q"):
            self.assertIn(token, self.text)

    def test_user_is_not_asked_to_operate_internal_records(self) -> None:
        for phrase in ("请你维护 Q-ID", "请你更新 LOG", "请你生成 receipt", "请手工填写 pending_user_intents"):
            self.assertNotIn(phrase, self.text)
        self.assertIn("高级诊断", self.text)
        self.assertIn("默认不需要", self.text)

    def test_fail_closed_claim_and_recall_rules_remain_visible(self) -> None:
        for token in (
            "saved", "validated", "complete", "宿主", "原回忆题", "先评价", "retest", "唯一下一行动",
        ):
            self.assertIn(token, self.text)


if __name__ == "__main__":
    unittest.main()
