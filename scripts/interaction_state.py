#!/usr/bin/env python3
"""Deterministic reference model for project-code-study turn transitions.

The Markdown protocol remains the portable authority. This helper makes the
advance/pause rules executable so regressions can be tested without relying on
prompt wording alone.
"""

from __future__ import annotations

import argparse
import sys


STATES = {
    "TEACHING_CURRENT_NODE",
    "AWAITING_RECALL",
    "ANSWERING_RECALL",
    "ANSWERING_SIDE_QUESTION",
    "AWAITING_QUESTIONS_OR_CONTINUE",
    "FINAL_QUESTION_PHASE",
    "FINAL_AUDIT",
    "DOCUMENT_CONSENT",
    "READY_TO_GENERATE",
}

TRANSITIONS = {
    ("TEACHING_CURRENT_NODE", "teaching-complete"): "AWAITING_RECALL",
    ("AWAITING_RECALL", "learner-recall"): "ANSWERING_RECALL",
    ("ANSWERING_RECALL", "answer-saved"): "AWAITING_QUESTIONS_OR_CONTINUE",
    ("AWAITING_QUESTIONS_OR_CONTINUE", "side-question"): "ANSWERING_SIDE_QUESTION",
    ("ANSWERING_SIDE_QUESTION", "answer-saved"): "AWAITING_QUESTIONS_OR_CONTINUE",
    ("AWAITING_QUESTIONS_OR_CONTINUE", "continue"): "TEACHING_CURRENT_NODE",
    ("AWAITING_QUESTIONS_OR_CONTINUE", "route-complete"): "FINAL_QUESTION_PHASE",
    ("FINAL_QUESTION_PHASE", "side-question"): "ANSWERING_SIDE_QUESTION",
    ("FINAL_QUESTION_PHASE", "no-more-questions"): "FINAL_AUDIT",
    ("FINAL_AUDIT", "audit-pass"): "DOCUMENT_CONSENT",
    ("FINAL_AUDIT", "audit-fail"): "AWAITING_QUESTIONS_OR_CONTINUE",
    ("DOCUMENT_CONSENT", "consent"): "READY_TO_GENERATE",
    ("DOCUMENT_CONSENT", "decline"): "FINAL_QUESTION_PHASE",
}


def transition(state: str, event: str) -> str:
    """Return the next state or raise when an event would bypass a gate."""
    if state not in STATES:
        raise ValueError(f"unknown state: {state}")
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
    memory_status: str = "enabled",
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
    memory_status: str = "enabled",
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
