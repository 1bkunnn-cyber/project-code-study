from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import release_transaction
import response_claim_guard
import finalize_project_study
import project_study_transaction


class ReleaseTransactionV6Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.artifacts = {}
        for name, content in {
            "qa": "qa-v6",
            "log": "log-v6",
            "memory": "memory-v6",
            "document": "handbook-v6",
        }.items():
            path = self.root / f"{name}.md"
            path.write_text(content, encoding="utf-8")
            self.artifacts[name] = path
        self.wal = self.root / "release.wal.json"
        self.receipt = self.root / "release.receipt.json"
        self.response_text = "QA、LOG、memory 和正式文档已经保存并通过验证。"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _prepare(self) -> dict[str, object]:
        return release_transaction.prepare_release(
            tx_id="TX-0042",
            doc_tx_id="DOC-TX-0007",
            artifacts=self.artifacts,
            source_revision="git:abc1234",
            readiness_manifest={"ready": True, "manifest_id": "READY-0007"},
            validator_results={
                "qa_log": "pass",
                "memory": "pass",
                "document": "pass",
            },
            cold_start_result={
                "status": "pass",
                "report_id": "COLD-0007",
                "report_hash": "c" * 64,
            },
            not_run=["multi-model", "real-context-compaction"],
            current_step="10",
            current_node="NODE-10-SE",
            wal_path=self.wal,
            response_text=self.response_text,
        )

    def test_commit_binds_every_artifact_and_gate_to_one_receipt(self) -> None:
        prepared = self._prepare()
        self.assertEqual(prepared["state"], "PREPARED")
        committed = release_transaction.commit_release(self.wal, self.receipt)
        self.assertEqual(committed["state"], "COMMITTED")
        self.assertEqual(committed["tx_id"], "TX-0042")
        self.assertEqual(committed["doc_tx_id"], "DOC-TX-0007")
        self.assertEqual(set(committed["artifact_hashes"]), set(self.artifacts))
        self.assertEqual(committed["source_revision"], "git:abc1234")
        self.assertEqual(committed["readiness_manifest"]["ready"], True)
        self.assertEqual(committed["cold_start_result"]["status"], "pass")
        self.assertEqual(committed["not_run"], ["multi-model", "real-context-compaction"])
        self.assertEqual(committed["current_step"], "10")
        self.assertEqual(committed["current_node"], "NODE-10-SE")
        self.assertEqual(
            committed["response_hash"],
            hashlib.sha256(self.response_text.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(
            release_transaction.validate_release_receipt(
                self.receipt,
                self.artifacts,
                response_text=self.response_text,
            ),
            [],
        )

    def test_changed_artifact_aborts_prepared_release_and_never_writes_receipt(self) -> None:
        self._prepare()
        self.artifacts["qa"].write_text("changed-after-validation", encoding="utf-8")
        with self.assertRaises(release_transaction.ReleaseTransactionError):
            release_transaction.commit_release(self.wal, self.receipt)
        self.assertFalse(self.receipt.exists())
        wal = json.loads(self.wal.read_text(encoding="utf-8"))
        self.assertEqual(wal["state"], "ABORTED")

    def test_recovery_commits_unchanged_prepared_release(self) -> None:
        self._prepare()
        recovered = release_transaction.recover_release(self.wal, self.receipt)
        self.assertEqual(recovered["state"], "COMMITTED")
        self.assertEqual(
            release_transaction.recover_release(self.wal, self.receipt)["state"],
            "COMMITTED",
        )

    def test_claim_guard_requires_committed_receipt_and_exact_response_hash(self) -> None:
        self._prepare()
        release_transaction.commit_release(self.wal, self.receipt)
        self.assertEqual(
            response_claim_guard.validate(self.response_text, self.receipt),
            [],
        )
        self.assertTrue(
            response_claim_guard.validate(
                self.response_text + " 但宿主没有执行 control tool。",
                self.receipt,
            )
        )

    def test_failed_gate_cannot_be_prepared(self) -> None:
        with self.assertRaises(release_transaction.ReleaseTransactionError):
            release_transaction.prepare_release(
                tx_id="TX-0043",
                doc_tx_id="DOC-TX-0008",
                artifacts=self.artifacts,
                source_revision="git:abc1234",
                readiness_manifest={"ready": True},
                validator_results={"qa_log": "pass", "document": "fail"},
                cold_start_result={"status": "pass", "report_hash": "c" * 64},
                not_run=[],
                current_step="10",
                current_node="NODE-10-SE",
                wal_path=self.wal,
                response_text=self.response_text,
            )

    def test_publication_finalizer_cannot_claim_saved_before_release_commit(self) -> None:
        candidate = self.root / "candidate.md"
        target = self.root / "PROJECT_STUDY_DOCUMENT.md"
        candidate.write_text(
            """---
status: "complete"
readiness_status: "ready"
validation_status: "validated"
generated_at: "2026-08-04T12:00:00+08:00"
project_path: ""
---
handbook candidate
""",
            encoding="utf-8",
        )
        with (
            mock.patch.object(
                finalize_project_study.validate_finalization_bundle,
                "evaluate_bundle",
                return_value={"ready": True},
            ),
            mock.patch.object(
                finalize_project_study,
                "_run_document_validator",
                return_value=[],
            ),
        ):
            result = finalize_project_study.finalize(
                self.artifacts["log"],
                self.artifacts["qa"],
                candidate,
                target,
                publication=True,
                cold_start_report=self.root / "cold-start.json",
            )
        self.assertEqual(result["status"], "release-pending")
        self.assertNotEqual(result["status"], "saved")
        self.assertTrue(target.is_file())

    def test_q_m_c_and_tx_allocators_are_unique_across_all_records(self) -> None:
        records = (
            "Q-001 M-001 C-001 TX-001",
            "Q-002 M-003 C-004 TX-009",
        )
        self.assertEqual(project_study_transaction.allocate_id("Q", *records), "Q-003")
        self.assertEqual(project_study_transaction.allocate_id("M", *records), "M-004")
        self.assertEqual(project_study_transaction.allocate_id("C", *records), "C-005")
        self.assertEqual(project_study_transaction.allocate_id("TX", *records), "TX-010")


if __name__ == "__main__":
    unittest.main()
