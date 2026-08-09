from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_skill_structure


class SkillStructureV6Tests(unittest.TestCase):
    def test_complete_v6_skill_structure_passes(self) -> None:
        self.assertEqual(validate_skill_structure.validate_structure(ROOT), [])

    def test_missing_control_script_is_reported(self) -> None:
        missing = ROOT / "scripts" / "does-not-exist.py"
        errors = validate_skill_structure.validate_required_paths(
            ROOT,
            [missing.relative_to(ROOT)],
        )
        self.assertTrue(any("does-not-exist.py" in error for error in errors))

    def test_published_repository_has_no_process_artifacts(self) -> None:
        self.assertEqual(validate_skill_structure.validate_repository_hygiene(ROOT), [])

    def test_hygiene_gate_reports_root_reports_and_superpowers_docs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "REMEDIATION_REPORT_9.9.9.md"
            process_doc = root / "docs" / "superpowers" / "specs" / "process.md"
            report.write_text("historical report", encoding="utf-8")
            process_doc.parent.mkdir(parents=True)
            process_doc.write_text("process design", encoding="utf-8")
            errors = validate_skill_structure.validate_repository_hygiene(root)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("REMEDIATION_REPORT_9.9.9.md" in error for error in errors))
        self.assertTrue(any("docs/superpowers/specs/process.md" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
