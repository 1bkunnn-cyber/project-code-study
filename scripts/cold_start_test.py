#!/usr/bin/env python3
"""Validate a fresh-model, no-chat study-document cold-start report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


REQUIRED_STEP_FIELDS = {
    "objective",
    "runtime_position",
    "call_chain",
    "source_explanation",
    "io_shape_state",
    "important_qa",
    "exercise_answer",
    "evidence_boundary",
    "result",
}
MIN_FIELD_LENGTHS = {
    "objective": 15,
    "runtime_position": 10,
    "call_chain": 12,
    "source_explanation": 20,
    "io_shape_state": 20,
    "important_qa": 15,
    "exercise_answer": 15,
    "evidence_boundary": 15,
}


def _document_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate_report(
    report_path: Path,
    document_path: Path,
    *,
    required_steps: set[str],
    handbook_schema: str | None = None,
) -> list[str]:
    """Check isolation metadata, document binding, and per-Step teaching recovery."""
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"cold-start report is unreadable: {exc}"]
    errors: list[str] = []
    expected_schema = "1.1" if handbook_schema == "2.1" else "1.0"
    if report.get("schema_version") != expected_schema:
        errors.append(f"cold-start report schema must be {expected_schema}")
    if report.get("mode") != "fresh-model-no-chat":
        errors.append("cold-start mode must prove a fresh model with no chat")
    if report.get("fresh_session") is not True:
        errors.append("cold-start report must declare fresh_session: true")
    if report.get("input_scope") != "document-only":
        errors.append("cold-start input_scope must be document-only")
    if not str(report.get("model", "")).strip():
        errors.append("cold-start report must identify the real host/model")
    if report.get("document_hash") != _document_hash(document_path):
        errors.append("cold-start report does not match current document hash")
    steps = report.get("steps")
    if not isinstance(steps, dict):
        return errors + ["cold-start report has no per-Step results"]
    missing_steps = sorted(required_steps - set(steps))
    if missing_steps:
        errors.append("cold-start report is missing Steps: " + ", ".join(missing_steps))
    for step in sorted(required_steps & set(steps)):
        result = steps[step]
        if not isinstance(result, dict):
            errors.append(f"cold-start Step {step} is not an object")
            continue
        missing_fields = sorted(
            field
            for field in REQUIRED_STEP_FIELDS
            if not str(result.get(field, "")).strip()
        )
        if missing_fields:
            errors.append(
                f"cold-start Step {step} missing fields: " + ", ".join(missing_fields)
            )
        for field, minimum in MIN_FIELD_LENGTHS.items():
            value = str(result.get(field, "")).strip()
            if value and len(value) < minimum:
                errors.append(
                    f"cold-start Step {step} field {field} is too thin "
                    f"({len(value)} < {minimum})"
                )
        if result.get("result") != "pass":
            errors.append(f"cold-start Step {step} did not pass")
        if handbook_schema == "2.1":
            retrieval_fields = {
                "lookup_path": None,
                "retrieval_result": "pass",
                "explanation_result": "pass",
                "application_result": "pass",
            }
            for field, expected in retrieval_fields.items():
                value = result.get(field)
                if expected is None and not str(value or "").strip():
                    errors.append(f"cold-start Step {step} missing field: {field}")
                elif expected is not None and value != expected:
                    errors.append(
                        f"cold-start Step {step} {field} must be {expected!r}"
                    )
    if report.get("overall_status") != "pass":
        errors.append("cold-start overall_status is not pass")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--document", type=Path, required=True)
    parser.add_argument("--step", action="append", dest="steps", required=True)
    parser.add_argument(
        "--handbook-schema",
        choices=("2.0", "2.1"),
        help="require schema-specific cold-start report fields",
    )
    args = parser.parse_args()
    errors = evaluate_report(
        args.report,
        args.document,
        required_steps=set(args.steps),
        handbook_schema=args.handbook_schema,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Cold-start report: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
