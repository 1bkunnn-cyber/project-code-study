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


def can_advance(state: str, fresh_continue: bool = False) -> bool:
    """Only a fresh continue event from the explicit pause state advances."""
    return state == "AWAITING_QUESTIONS_OR_CONTINUE" and fresh_continue


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
