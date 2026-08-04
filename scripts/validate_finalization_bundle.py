#!/usr/bin/env python3
"""Fail-closed readiness audit for a project-code-study LOG/Q&A bundle."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import validate_learning_ledger as ledger_validator


FINAL_STEP = {"done", "skipped", "stale"}
FINAL_SCENARIO = {"verified", "traced", "done", "complete", "skipped"}
FINAL_NODE = {"verified", "traced", "skipped", "stale"}
FINAL_QUESTION = {"closed", "deferred", "stale"}
FINAL_CORRECTION = {"canonical", "resolved", "closed", "stale"}


def truth(value: str | None) -> bool:
    return ledger_validator.norm(value) in {"true", "yes", "1"}


def evaluate_bundle(
    ledger_path: Path,
    qa_path: Path,
    *,
    publication: bool = False,
) -> dict[str, object]:
    log_text = ledger_path.read_text(encoding="utf-8-sig")
    qa_text = qa_path.read_text(encoding="utf-8-sig")
    log_errors, log_fm, _ = ledger_validator.validate_text(log_text, strict=True)
    qa_errors, qa_fm, _ = ledger_validator.validate_text(
        qa_text,
        strict=True,
        publication=publication,
    )
    cross_errors: list[str] = []
    ledger_validator.validate_cross(log_text, log_fm, qa_text, qa_fm, cross_errors)

    log_tables = ledger_validator.tables_of(log_text)
    qa_tables = ledger_validator.tables_of(qa_text)
    route = ledger_validator.find_table(log_tables, {"Step", "Required", "状态", "K ID", "Transaction ID"}) or []
    required_route = [row for row in route if ledger_validator.norm(row.get("Required")) in {"yes", "true", "1"}]
    nonfinal_steps = [ledger_validator.clean(row.get("Step")) for row in required_route if ledger_validator.norm(row.get("状态")) not in FINAL_STEP]

    scenarios = ledger_validator.find_table(log_tables, {"Scenario ID", "Required", "状态"}) or []
    required_scenarios = [row for row in scenarios if ledger_validator.norm(row.get("Required")) in {"yes", "true", "1"}]
    incomplete_scenarios = [ledger_validator.clean(row.get("Scenario ID")) for row in required_scenarios if ledger_validator.norm(row.get("状态")) not in FINAL_SCENARIO]
    scenario_complete = bool(required_scenarios) and not incomplete_scenarios

    nodes = ledger_validator.find_table(log_tables, {"Node ID", "状态", "Reason", "Impact", "Revisit condition", "Learner acceptance"}) or []
    missing_nodes = [ledger_validator.clean(row.get("Node ID")) for row in nodes if ledger_validator.norm(row.get("状态")) not in FINAL_NODE]

    q_rows = ledger_validator.find_table(qa_tables, {"Q ID", "状态", "Parent Q", "Transaction ID"}) or []
    open_questions = [ledger_validator.clean(row.get("Q ID")) for row in q_rows if ledger_validator.norm(row.get("状态")) not in FINAL_QUESTION]
    retest_due = [ledger_validator.clean(row.get("Q ID")) for row in q_rows if ledger_validator.norm(row.get("状态")) == "retest-due"]

    correction_rows = ledger_validator.find_table(log_tables, {"ID", "Stale pattern", "Transaction ID", "状态"}) or []
    stale_corrections = [ledger_validator.clean(row.get("ID")) for row in correction_rows if ledger_validator.norm(row.get("状态")) not in FINAL_CORRECTION]

    k_blocks = ledger_validator.detail_blocks(log_text, "K")
    steps_without_knowledge: list[str] = []
    for row in route:
        if ledger_validator.norm(row.get("状态")) == "done":
            kid = ledger_validator.clean(row.get("K ID")).upper()
            if kid not in k_blocks:
                steps_without_knowledge.append(ledger_validator.clean(row.get("Step")))

    hidden = [pattern for pattern in ledger_validator.HIDDEN_CHAT_PATTERNS if pattern.lower() in qa_text.lower()]
    record_errors = [f"LOG: {item}" for item in log_errors] + [f"QA: {item}" for item in qa_errors] + cross_errors

    manifest: dict[str, object] = {
        "route_final": bool(required_route) and not nonfinal_steps,
        "nonfinal_steps": nonfinal_steps,
        "scenario_coverage_complete": scenario_complete,
        "incomplete_scenarios": incomplete_scenarios,
        "missing_core_nodes": missing_nodes,
        "open_questions": open_questions,
        "retest_due_questions": retest_due,
        "pending_user_response": truth(log_fm.get("pending_user_response")),
        "stale_corrections": stale_corrections,
        "steps_without_durable_knowledge": steps_without_knowledge,
        "qa_hidden_chat_dependencies": hidden,
        "learner_closed_question_phase": truth(log_fm.get("learner_closed_question_phase")),
        "learner_consented_to_generation": truth(log_fm.get("learner_consented_to_generation")),
        "record_validation_errors": record_errors,
        "qa_depth_contract": "pass" if publication and not qa_errors else (
            "not-run" if not publication else "fail"
        ),
    }
    manifest["ready"] = (
        bool(manifest["route_final"])
        and bool(manifest["scenario_coverage_complete"])
        and not missing_nodes
        and not open_questions
        and not retest_due
        and not bool(manifest["pending_user_response"])
        and not stale_corrections
        and not steps_without_knowledge
        and not hidden
        and bool(manifest["learner_closed_question_phase"])
        and bool(manifest["learner_consented_to_generation"])
        and not record_errors
    )
    return manifest


def yaml_like(manifest: dict[str, object]) -> str:
    lines = ["readiness_manifest:"]
    for key, value in manifest.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif isinstance(value, list):
            rendered = "[]" if not value else json.dumps(value, ensure_ascii=False)
        else:
            rendered = json.dumps(value, ensure_ascii=False)
        lines.append(f"  {key}: {rendered}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--qa", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--publication", action="store_true")
    args = parser.parse_args()
    for path in (args.ledger, args.qa):
        if not path.is_file():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            return 2
    try:
        manifest = evaluate_bundle(
            args.ledger,
            args.qa,
            publication=args.publication,
        )
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, ensure_ascii=False, indent=2) if args.json else yaml_like(manifest))
    return 0 if manifest["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
