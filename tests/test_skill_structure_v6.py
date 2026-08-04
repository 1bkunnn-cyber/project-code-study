from __future__ import annotations

import sys
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


if __name__ == "__main__":
    unittest.main()
