#!/usr/bin/env python3
"""Static structure and parse audit for project-code-study v6.2."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
import re
import sys


REQUIRED_PATHS = [
    Path("SKILL.md"),
    Path("README.md"),
    Path("CHANGELOG.md"),
    Path("GITHUB_RESEARCH_AND_ACKNOWLEDGEMENTS.md"),
    Path("PROJECT_CODE_STUDY_V6_2_IMPLEMENTATION_REPORT.md"),
    Path("assets/NODE_TEACHING_CONTRACT.md"),
    Path("references/interaction-mode-protocol.md"),
    Path("assets/PROJECT_STUDY_HANDOFF.template.json"),
    Path("assets/PROJECT_STUDY_MEMORY_CANDIDATES.template.json"),
    Path("assets/PROJECT_STUDY_RELEASE_MANIFEST.template.json"),
    Path("assets/PROJECT_STUDY_COLD_START_REPORT.template.json"),
    Path("scripts/study_events.py"),
    Path("scripts/memory_lifecycle.py"),
    Path("scripts/release_transaction.py"),
    Path("scripts/cold_start_test.py"),
    Path("scripts/validate_teaching_response.py"),
    Path("scripts/validate_learning_ledger.py"),
    Path("scripts/validate_protocol_memory.py"),
    Path("skills/project-study-document/SKILL.md"),
    Path("skills/project-study-document/assets/PROJECT_STUDY_DOCUMENT.template.md"),
    Path("skills/project-study-document/scripts/validate_study_document.py"),
    Path("tests/test_event_state_and_handoff.py"),
    Path("tests/test_memory_lifecycle_v6.py"),
    Path("tests/test_release_transaction_v6.py"),
    Path("tests/test_document_handbook_v6.py"),
    Path("tests/test_compact_handbook_v61.py"),
    Path("tests/test_interaction_modes_v62.py"),
    Path("tests/test_question_batch_v62.py"),
]


def validate_required_paths(root: Path, required: list[Path]) -> list[str]:
    return [
        f"missing required Skill path: {relative.as_posix()}"
        for relative in required
        if not (root / relative).is_file()
    ]


def validate_structure(root: Path) -> list[str]:
    errors = validate_required_paths(root, REQUIRED_PATHS)
    if errors:
        return errors
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    if not re.search(r"(?m)^version:\s*6\.2\.0\s*$", skill):
        errors.append("SKILL.md version must be 6.2.0")
    description = re.search(r"(?m)^description:\s*(.+)$", skill)
    if not description or not description.group(1).startswith("Use when"):
        errors.append("SKILL.md description must start with 'Use when'")
    template = (
        root
        / "skills"
        / "project-study-document"
        / "assets"
        / "PROJECT_STUDY_DOCUMENT.template.md"
    ).read_text(encoding="utf-8")
    if (
        'schema_version: "2.1"' not in template
        or 'handbook_mode: "layered-step-manual"' not in template
        or "## 6. 逐 Step 手册" not in template
    ):
        errors.append("document template must use compact handbook schema 2.1")
    readme = (root / "README.md").read_text(encoding="utf-8")
    if "version-6.2.0" not in readme:
        errors.append("README version badge is not 6.2.0")
    if "GITHUB_RESEARCH_AND_ACKNOWLEDGEMENTS.md" not in readme:
        errors.append("README does not link the research acknowledgements")
    for path in sorted((root / "scripts").glob("*.py")):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"Python parse error in {path.name}: {exc}")
    companion = (
        root
        / "skills"
        / "project-study-document"
        / "scripts"
        / "validate_study_document.py"
    )
    try:
        ast.parse(companion.read_text(encoding="utf-8"), filename=str(companion))
    except SyntaxError as exc:
        errors.append(f"Python parse error in companion validator: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_root", type=Path, nargs="?", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate_structure(args.skill_root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Static Skill structure: pass ({args.skill_root.resolve()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
