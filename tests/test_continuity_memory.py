from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_protocol_memory import validate_store
import response_claim_guard
import sync_protocol_memory


class ContinuityMemoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.memory = self.root / "memory"
        self.memory.mkdir()
        (self.memory / "MEMORY.md").write_text("# Memory Index\n\n## feedback\n\n## correction\n\n## project\n\n## reference\n", encoding="utf-8")
        self.ledger = self.root / "LOG.md"
        self.qa = self.root / "QA.md"
        self.ledger.write_text("ledger", encoding="utf-8")
        self.qa.write_text("qa", encoding="utf-8")
        self.source_receipt = self.root / "source-receipt.json"
        self.source_receipt.write_text(json.dumps({
            "persistence_status": "saved", "validator": "pass", "tx_id": "TX-0007",
            "hashes": {
                str(self.ledger.resolve()): sync_protocol_memory.sha256_text("ledger"),
                str(self.qa.resolve()): sync_protocol_memory.sha256_text("qa"),
            },
        }), encoding="utf-8")
        self.body = self.root / "body.md"
        self.body.write_text("Why: it prevents protocol drift.\nHow to apply: reload the rule before answering.", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_empty_store_is_valid(self) -> None:
        self.assertEqual(validate_store(self.memory), [])

    def test_orphan_and_missing_pointer_fail(self) -> None:
        (self.memory / "orphan.md").write_text("orphan", encoding="utf-8")
        (self.memory / "MEMORY.md").write_text((self.memory / "MEMORY.md").read_text(encoding="utf-8") + "- [Missing](missing.md) — Missing\n", encoding="utf-8")
        errors = validate_store(self.memory)
        self.assertTrue(any("missing memory target" in error for error in errors))
        self.assertTrue(any("orphan memory file" in error for error in errors))

    def test_guard_rejects_saved_without_receipt(self) -> None:
        self.assertTrue(response_claim_guard.validate("QA 已保存成功。", None))

    def test_guard_accepts_matching_receipt(self) -> None:
        receipt = self.root / "receipt.json"
        receipt.write_text(json.dumps({"persistence_status": "saved", "validator": "pass"}), encoding="utf-8")
        self.assertEqual(response_claim_guard.validate("Persistence saved.", receipt), [])

    def test_upsert_requires_receipt_and_updates_same_slug(self) -> None:
        args = type("Args", (), {
            "memory_root": self.memory, "receipt": self.source_receipt,
            "source_files": [self.ledger, self.qa], "name": "reload-protocol",
            "description": "Reload protocol before answering", "kind": "feedback",
            "source_path": "LOG.md / QA.md", "body_file": self.body, "receipt_out": None,
        })()
        first = sync_protocol_memory.upsert(args)
        self.body.write_text("Why: it prevents forgotten gates.\nHow to apply: reload before every response.", encoding="utf-8")
        args.description = "Reload gates before every response"
        second = sync_protocol_memory.upsert(args)
        self.assertEqual(first["action"], "added")
        self.assertEqual(second["action"], "updated")
        self.assertEqual((self.memory / "MEMORY.md").read_text(encoding="utf-8").count("reload-protocol.md"), 1)
        self.assertEqual(validate_store(self.memory), [])

    def test_formal_document_claim_cannot_use_plain_persistence_receipt(self) -> None:
        receipt = self.root / "plain-receipt.json"
        receipt.write_text(json.dumps({"persistence_status": "saved", "validator": "pass"}), encoding="utf-8")
        self.assertTrue(response_claim_guard.validate("正式文档已生成。", receipt))


if __name__ == "__main__":
    unittest.main()
