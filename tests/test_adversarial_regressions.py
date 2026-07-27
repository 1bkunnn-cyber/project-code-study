from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "project-study-document" / "scripts"))

import claim_verifier
import finalize_project_study
import interaction_state
import project_study_transaction as tx
import validate_study_document
from test_regressions import make_bundle, make_document


class AdversarialRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_T17_validator_failure_does_not_change_formal_target(self) -> None:
        log, qa = make_bundle(self.root)
        candidate = make_document(self.root)
        candidate.write_text(candidate.read_text(encoding="utf-8").replace("#### 自测", "#### 自测损坏"), encoding="utf-8")
        candidate_copy = self.root / "candidate.md"
        candidate_copy.write_text(candidate.read_text(encoding="utf-8"), encoding="utf-8")
        target = self.root / "PROJECT_STUDY_DOCUMENT.md"
        target.write_text("formal-before", encoding="utf-8")
        result = finalize_project_study.finalize(log, qa, candidate_copy, target)
        self.assertEqual(result["status"], "blocked", result)
        self.assertEqual(target.read_text(encoding="utf-8"), "formal-before")

    def test_formal_finalizer_writes_only_after_ready_bundle(self) -> None:
        log, qa = make_bundle(self.root)
        candidate = make_document(self.root)
        candidate_copy = self.root / "candidate.md"
        candidate_copy.write_text(candidate.read_text(encoding="utf-8"), encoding="utf-8")
        target = self.root / "formal.md"
        result = finalize_project_study.finalize(log, qa, candidate_copy, target)
        self.assertEqual(result["status"], "saved", result)
        self.assertIn('validation_status: "validated"', target.read_text(encoding="utf-8"))

    def test_T18_saved_requires_machine_receipt(self) -> None:
        log = self.root / "LOG.md"
        qa = self.root / "QA.md"
        log.write_text("log", encoding="utf-8")
        qa.write_text("qa", encoding="utf-8")
        receipt = self.root / "receipt.json"
        receipt.write_text("saved", encoding="utf-8")
        self.assertIsNone(tx.read_machine_receipt(receipt, [log, qa]))
        result = tx.commit_question(log, qa, {"title": "q", "question_intent": "intent", "canonical_answer": "a complete answer with evidence", "evidence": "SRC-001", "anchor": "NODE-001", "status": "closed"})
        self.assertEqual(result["persistence_status"], "unsaved-partial")

    def test_T19_duplicate_tx_allocator_is_rejected(self) -> None:
        with self.assertRaises(tx.TransactionError):
            tx.allocate_id("TX", "TX-011 already exists", requested="TX-011")

    def test_T20_unsaved_question_cannot_advance(self) -> None:
        self.assertFalse(interaction_state.can_advance("AWAITING_QUESTIONS_OR_CONTINUE", True, persistence_status="unsaved-partial"))
        self.assertFalse(interaction_state.can_advance("AWAITING_QUESTIONS_OR_CONTINUE", True, pending_user_response=True))

    def test_T21_retest_due_blocks_every_continue(self) -> None:
        self.assertFalse(interaction_state.can_advance("AWAITING_QUESTIONS_OR_CONTINUE", True, retest_due_questions=["Q-001"]))

    def test_T22_old_continue_token_cannot_cross_question(self) -> None:
        state = interaction_state.transition("AWAITING_QUESTIONS_OR_CONTINUE", "side-question")
        state = interaction_state.transition(state, "answer-saved")
        self.assertFalse(interaction_state.can_advance(state, fresh_continue=False))

    def test_T23_compound_question_splits_into_independent_intents(self) -> None:
        text = "\n".join(f"{i}. independent intent {i}" for i in range(1, 7))
        self.assertEqual(len(tx.split_question_intents(text)), 6)

    def test_T24_structured_insert_preserves_section_boundaries(self) -> None:
        source = "### Q-045 — old\n\n- State：closed\n\n## 3. 用户心得与学习感受\n\n### Q-046 — new\n\n- State：open\n"
        result = tx.insert_before_heading(source, "## 3. 用户心得与学习感受", "### Q-047 — inserted\n\n- State：closed")
        self.assertEqual(result.count("### Q-045"), 1)
        self.assertEqual(result.count("### Q-046"), 1)
        self.assertEqual(result.count("### Q-047"), 1)
        self.assertEqual(result.split("### Q-045", 1)[1].split("### Q-047", 1)[0].count("State"), 1, result)

    def test_transaction_commit_returns_saved_only_after_validator_callback(self) -> None:
        log, qa = make_bundle(self.root)
        receipt = self.root / "receipt.json"
        result = tx.commit_question(
            log,
            qa,
            {"title": "why", "question_intent": "why does the boundary exist", "canonical_answer": "The boundary validates input before the operation and exposes an auditable output.", "evidence": "SRC-001", "anchor": "NODE-001", "status": "closed"},
            receipt_path=receipt,
            validator=lambda staged_log, staged_qa: [],
        )
        self.assertEqual(result["persistence_status"], "saved", result)
        self.assertIn("Q-002", tx.ids_in(qa.read_text(encoding="utf-8"), "Q"))
        self.assertIsNotNone(tx.read_machine_receipt(receipt, [log, qa]))

    def test_T25_correction_propagates_to_all_derived_artifacts(self) -> None:
        paths = []
        for name in ("qa.md", "log.md", "summary.md", "document.md"):
            path = self.root / name
            path.write_text("old verdict", encoding="utf-8")
            paths.append(path)
        result = tx.correct_promoted_claim(paths, "old verdict", "canonical verdict", ["old verdict"], correction_id="M-001", tx_id="TX-001")
        self.assertEqual(result["persistence_status"], "saved")
        self.assertTrue(all("old verdict" not in path.read_text(encoding="utf-8") for path in paths))

    def test_T26_invalid_code_link_and_placeholder_are_rejected(self) -> None:
        log, qa = make_bundle(self.root)
        (self.root / "src").mkdir()
        (self.root / "src" / "main.py").write_text("def main():\n    return 1\n", encoding="utf-8")
        doc = make_document(self.root)
        bad = doc.read_text(encoding="utf-8").replace("src/main.py:1-20", "src/.../aquarium.py:999")
        doc.write_text(bad, encoding="utf-8")
        errors = validate_study_document.validate(doc, allow_template=False, ledger_path=log, qa_path=qa, preflight=False, repo_root=self.root)
        self.assertTrue(any("placeholder source" in error for error in errors))
        with self.assertRaises(claim_verifier.ClaimVerificationError):
            claim_verifier.verify_claim("source", {"path": "src/main.py", "symbol": "missing", "line": 1}, repo_root=self.root)
        with self.assertRaises(claim_verifier.ClaimVerificationError):
            claim_verifier.verify_claim("source", {"path": "src/main.py", "symbol": "main", "line": 999}, repo_root=self.root)

    def test_T27_incomplete_unit_cannot_validate(self) -> None:
        log, qa = make_bundle(self.root)
        doc = make_document(self.root)
        text = doc.read_text(encoding="utf-8").replace("#### 自测", "#### 自测损坏")
        doc.write_text(text, encoding="utf-8")
        errors = validate_study_document.validate(doc, allow_template=False, ledger_path=log, qa_path=qa, preflight=False)
        self.assertTrue(any("relearning section too thin" in error or "semantic evidence" in error for error in errors), repr(text))

    def test_T28_chat_consent_without_persistence_is_fail_closed(self) -> None:
        log, qa = make_bundle(self.root)
        log.write_text(log.read_text(encoding="utf-8").replace("learner_closed_question_phase: true", "learner_closed_question_phase: false").replace("learner_consented_to_generation: true", "learner_consented_to_generation: false"), encoding="utf-8")
        candidate = make_document(self.root)
        candidate_copy = self.root / "candidate.md"
        candidate_copy.write_text(candidate.read_text(encoding="utf-8"), encoding="utf-8")
        target = self.root / "PROJECT_STUDY_DOCUMENT.md"
        target.write_text("formal-before", encoding="utf-8")
        result = finalize_project_study.finalize(log, qa, candidate_copy, target)
        self.assertEqual(result["status"], "blocked", result)
        self.assertEqual(target.read_text(encoding="utf-8"), "formal-before")

    def test_T29_legacy_schema_cannot_bypass_finalizer(self) -> None:
        log, qa = make_bundle(self.root)
        log.write_text(log.read_text(encoding="utf-8").replace('schema_version: "4.1"', 'schema_version: "4.0"'), encoding="utf-8")
        candidate = make_document(self.root)
        target = self.root / "PROJECT_STUDY_DOCUMENT.md"
        target.write_text("formal-before", encoding="utf-8")
        result = finalize_project_study.finalize(log, qa, candidate, target)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(target.read_text(encoding="utf-8"), "formal-before")

    def test_T30_claim_verifier_registry_covers_high_impact_types(self) -> None:
        source = self.root / "module.py"
        source.write_text("def operation():\n    return 1\n", encoding="utf-8")
        claims = {
            "source": {"path": "module.py", "symbol": "operation", "line": 1},
            "configuration": {"resolved_config": {"enabled": True}, "expected": {"enabled": True}},
            "runtime": {"command": "python module.py", "log": "run.log", "artifacts": ["out.json"], "observation": "observed"},
            "mathematical": {"lhs": "2*(3+1)", "rhs": "8"},
            "paper": {"title": "A paper", "locator": "p. 3, Eq. 2", "scope": "method definition"},
            "comparison": {"baseline": 10, "new_value": 12, "absolute_delta": 2, "unit": "ms", "scope": "per batch"},
            "learner_verdict": {"intents": ["what"], "answers": [{"span": "the answer", "verdict": "correct"}]},
        }
        for claim_type, claim in claims.items():
            with self.subTest(claim_type=claim_type):
                self.assertEqual(claim_verifier.verify_claim(claim_type, claim, repo_root=self.root)["status"], "verified")

    @unittest.skip("真实 Claude/Codex 宿主 golden conversation 需在外部宿主中执行")
    def test_T31_real_host_golden_conversation(self) -> None:
        """Static tests must never be reported as a real-host pass."""
        self.fail("not-run")


if __name__ == "__main__":
    unittest.main()
