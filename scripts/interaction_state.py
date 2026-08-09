#!/usr/bin/env python3
"""Deterministic reference model for project-code-study turn transitions.

The Markdown protocol remains the portable authority. This helper makes the
advance/pause rules executable so regressions can be tested without relying on
prompt wording alone.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import sys
from typing import Any


STATES = {
    "TEACHING_CURRENT_NODE",
    "AWAITING_RECALL",
    "ANSWERING_RECALL",
    "ANSWERING_SIDE_QUESTION",
    "ANSWERING_RECALL_SIDE_QUESTION",
    "AWAITING_QUESTIONS_OR_CONTINUE",
    "FINAL_QUESTION_PHASE",
    "ANSWERING_FINAL_SIDE_QUESTION",
    "FINAL_AUDIT",
    "FINAL_AUDIT_REPAIR",
    "DOCUMENT_CONSENT",
    "READY_TO_GENERATE",
    "REPAIR_REQUIRED",
    "REGISTERING_QUESTION_BATCH",
    "ANSWERING_QUESTION_QUEUE",
    "QUESTION_BATCH_REPAIR",
}


def begin_question_batch(state: str, input_event_id: str, qids: list[str]) -> dict[str, Any]:
    """Capture the exact return state and initialize an ordered, unbounded Q queue."""
    if state not in STATES or state in {"REGISTERING_QUESTION_BATCH", "ANSWERING_QUESTION_QUEUE", "QUESTION_BATCH_REPAIR", "REPAIR_REQUIRED"}:
        raise ValueError(f"cannot begin question batch from {state}")
    if not qids or len(qids) != len(set(qids)):
        raise ValueError("question batch requires unique ordered Q IDs")
    return {
        "state": "REGISTERING_QUESTION_BATCH",
        "input_event_id": input_event_id,
        "return_state": state,
        "pending_question_ids": list(qids),
        "answered_question_ids": [],
        "current_question_id": None,
    }


def question_batch_event(context: dict[str, Any], event: str, *, qid: str | None = None) -> dict[str, Any]:
    """Advance one batch event while preserving queue order and repair state."""
    updated = deepcopy(context)
    state = updated.get("state")
    pending = updated.get("pending_question_ids")
    if not isinstance(pending, list):
        raise ValueError("question batch context has no pending queue")
    if state == "REGISTERING_QUESTION_BATCH" and event == "intake-saved":
        updated["state"] = "ANSWERING_QUESTION_QUEUE"
        updated["current_question_id"] = pending[0]
        return updated
    if state == "REGISTERING_QUESTION_BATCH" and event == "intake-failed":
        updated["state"] = "QUESTION_BATCH_REPAIR"
        return updated
    if state == "ANSWERING_QUESTION_QUEUE" and event == "answer-failed":
        if qid != updated.get("current_question_id"):
            raise ValueError("failed answer does not match current Q")
        updated["state"] = "QUESTION_BATCH_REPAIR"
        return updated
    if state == "QUESTION_BATCH_REPAIR" and event == "repair-complete":
        updated["state"] = "ANSWERING_QUESTION_QUEUE" if pending else updated["return_state"]
        updated["current_question_id"] = pending[0] if pending else None
        return updated
    if state == "ANSWERING_QUESTION_QUEUE" and event == "answer-saved":
        if not pending or qid != pending[0] or qid != updated.get("current_question_id"):
            raise ValueError("answers must commit in registered queue order")
        pending.pop(0)
        updated.setdefault("answered_question_ids", []).append(qid)
        if pending:
            updated["current_question_id"] = pending[0]
        else:
            return_state = updated.get("return_state")
            if return_state not in STATES or return_state in {"REGISTERING_QUESTION_BATCH", "ANSWERING_QUESTION_QUEUE", "QUESTION_BATCH_REPAIR", "REPAIR_REQUIRED"}:
                raise ValueError("invalid captured question-batch return state")
            updated["state"] = return_state
            updated["current_question_id"] = None
        return updated
    raise ValueError(f"event {event!r} is not allowed from {state}")

TRANSITIONS = {
    ("TEACHING_CURRENT_NODE", "teaching-complete"): "AWAITING_RECALL",
    ("AWAITING_RECALL", "learner-recall"): "ANSWERING_RECALL",
    ("AWAITING_RECALL", "side-question"): "ANSWERING_RECALL_SIDE_QUESTION",
    ("ANSWERING_RECALL_SIDE_QUESTION", "answer-saved"): "AWAITING_RECALL",
    ("ANSWERING_RECALL", "answer-saved"): "AWAITING_QUESTIONS_OR_CONTINUE",
    ("AWAITING_QUESTIONS_OR_CONTINUE", "side-question"): "ANSWERING_SIDE_QUESTION",
    ("ANSWERING_SIDE_QUESTION", "answer-saved"): "AWAITING_QUESTIONS_OR_CONTINUE",
    ("AWAITING_QUESTIONS_OR_CONTINUE", "continue"): "TEACHING_CURRENT_NODE",
    ("AWAITING_QUESTIONS_OR_CONTINUE", "route-complete"): "FINAL_QUESTION_PHASE",
    ("FINAL_QUESTION_PHASE", "side-question"): "ANSWERING_FINAL_SIDE_QUESTION",
    ("ANSWERING_FINAL_SIDE_QUESTION", "answer-saved"): "FINAL_QUESTION_PHASE",
    ("FINAL_QUESTION_PHASE", "no-more-questions"): "FINAL_AUDIT",
    ("FINAL_AUDIT", "audit-pass"): "DOCUMENT_CONSENT",
    ("FINAL_AUDIT", "audit-fail"): "FINAL_AUDIT_REPAIR",
    ("FINAL_AUDIT_REPAIR", "repair-complete"): "FINAL_AUDIT",
    ("DOCUMENT_CONSENT", "consent"): "READY_TO_GENERATE",
    ("DOCUMENT_CONSENT", "decline"): "FINAL_QUESTION_PHASE",
}


def transition(state: str, event: str) -> str:
    """Return the next state or raise when an event would bypass a gate."""
    if state not in STATES:
        raise ValueError(f"unknown state: {state}")
    if event == "state-mismatch" and state != "REPAIR_REQUIRED":
        return "REPAIR_REQUIRED"
    if state == "REPAIR_REQUIRED" and event.startswith("repair-complete:"):
        target = event.split(":", 1)[1]
        if target not in STATES or target == "REPAIR_REQUIRED":
            raise ValueError(f"invalid repair target: {target}")
        return target
    try:
        return TRANSITIONS[(state, event)]
    except KeyError as exc:
        raise ValueError(f"event {event!r} is not allowed from {state}") from exc


def advance_decision(
    state: str,
    *,
    fresh_continue: bool = False,
    open_questions: list[str] | None = None,
    retest_due_questions: list[str] | None = None,
    pending_user_response: bool = False,
    persistence_status: str = "saved",
    node_complete: bool = True,
    strict_validation_passed: bool = True,
    memory_status: str = "pending",
    pending_user_intents: list[str] | None = None,
) -> tuple[bool, str]:
    """Evaluate every hard gate before a route transition.

    ``fresh_continue`` is intentionally not sufficient by itself. The caller
    must prove that the question queue, retest queue, records, current NODE,
    and strict validator are all clear.
    """
    if state != "AWAITING_QUESTIONS_OR_CONTINUE":
        return False, "interaction state is not awaiting a fresh continue"
    if memory_status == "pending":
        return False, "memory consent is pending"
    if memory_status not in {"enabled", "disabled"}:
        return False, "memory status must be enabled or disabled"
    if pending_user_intents:
        return False, "unresolved user intents block advancement"
    if not fresh_continue:
        return False, "fresh continue is required"
    if open_questions:
        return False, "open questions block advancement"
    if retest_due_questions:
        return False, "retest-due questions block advancement"
    if pending_user_response:
        return False, "pending user response must be persisted and closed"
    if persistence_status != "saved":
        return False, "machine persistence receipt is not saved"
    if not node_complete:
        return False, "current NODE is not semantically complete"
    if not strict_validation_passed:
        return False, "strict LOG/QA validation has not passed"
    return True, "advance permitted"


def can_advance(
    state: str,
    fresh_continue: bool = False,
    *,
    open_questions: list[str] | None = None,
    retest_due_questions: list[str] | None = None,
    pending_user_response: bool = False,
    persistence_status: str = "saved",
    node_complete: bool = True,
    strict_validation_passed: bool = True,
    memory_status: str = "pending",
    pending_user_intents: list[str] | None = None,
) -> bool:
    """Return true only when every fail-closed advancement gate passes."""
    return advance_decision(
        state,
        fresh_continue=fresh_continue,
        open_questions=open_questions,
        retest_due_questions=retest_due_questions,
        pending_user_response=pending_user_response,
        persistence_status=persistence_status,
        node_complete=node_complete,
        strict_validation_passed=strict_validation_passed,
        memory_status=memory_status,
        pending_user_intents=pending_user_intents,
    )[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", choices=sorted(STATES))
    parser.add_argument("event")
    args = parser.parse_args()
    try:
        print(transition(args.state, args.event))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
