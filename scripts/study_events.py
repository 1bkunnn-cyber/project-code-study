#!/usr/bin/env python3
"""Typed input events and compaction handoffs for project-code-study."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import re
from typing import Any


class EventStateError(ValueError):
    """Raised when an input event would be replayed or is malformed."""


HANDOFF_FIELDS = {
    "current_step",
    "current_run",
    "current_node",
    "continuation_node",
    "completed_nodes",
    "open_questions",
    "pending_user_intents",
    "retest_due_questions",
    "recent_corrections",
    "evidence_ids",
    "unique_next_action",
    "active_input_event_id",
    "question_queue_ids",
    "current_question_id",
    "question_queue_return_state",
}


def _intent_kind(text: str) -> str:
    normalized = text.strip().lower()
    if re.search(r"(?:^|\s|然后|再)(继续|continue)[。.!！]?$", normalized):
        return "continue"
    if any(token in normalized for token in ("纠正", "更正", "不对", "原结论错误")):
        return "correction"
    if any(token in normalized for token in ("长期", "质量要求", "文档应该", "路线应该", "输出质量", "教学质量")):
        return "quality_feedback"
    if any(token in normalized for token in ("？", "?", "解释", "为什么", "如何", "怎么")):
        return "question"
    return "statement"


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _trimmed_span(text: str, start: int, end: int) -> tuple[int, int] | None:
    while start < end and text[start] in " \t\r\n，,":
        start += 1
    while end > start and text[end - 1] in " \t\r\n，,":
        end -= 1
    return (start, end) if start < end else None


def _intent_spans(text: str) -> list[tuple[int, int]]:
    """Return exact, ordered source spans without imposing a question-count limit."""
    coarse: list[tuple[int, int]] = []
    cursor = 0
    for separator in re.finditer(r"(?:\r?\n+|[；;])", text):
        span = _trimmed_span(text, cursor, separator.start())
        if span:
            coarse.append(span)
        cursor = separator.end()
    tail = _trimmed_span(text, cursor, len(text))
    if tail:
        coarse.append(tail)

    spans: list[tuple[int, int]] = []
    for start, end in coarse:
        fragment = text[start:end]
        question_marks = list(re.finditer(r"[？?]", fragment))
        if len(question_marks) <= 1:
            spans.append((start, end))
            continue
        local_start = 0
        for mark in question_marks:
            local_end = mark.end()
            span = _trimmed_span(text, start + local_start, start + local_end)
            if span:
                spans.append(span)
            local_start = local_end
        remainder = _trimmed_span(text, start + local_start, end)
        if remainder:
            spans.append(remainder)
    return spans


def validate_intent_envelope(payload: dict[str, Any], source_text: str) -> list[str]:
    """Validate that an intent envelope remains exactly bound to its source input."""
    errors: list[str] = []
    if payload.get("schema_version") != "6.2":
        errors.append("unsupported intent envelope schema")
    input_event_id = payload.get("input_event_id")
    if not isinstance(input_event_id, str) or not re.fullmatch(r"INPUT-\d+", input_event_id):
        errors.append("invalid input event id")
    if payload.get("raw_text_hash") != _sha256(source_text):
        errors.append("raw source text hash mismatch")
    intents = payload.get("intents")
    if not isinstance(intents, list):
        return [*errors, "intents must be a list"]
    previous_end = -1
    for order, item in enumerate(intents, 1):
        if not isinstance(item, dict):
            errors.append(f"intent {order} is not an object")
            continue
        if item.get("source_order") != order:
            errors.append(f"intent {order} source order mismatch")
        span = item.get("source_span")
        if (
            not isinstance(span, list)
            or len(span) != 2
            or not all(isinstance(value, int) for value in span)
        ):
            errors.append(f"intent {order} has invalid source span")
            continue
        start, end = span
        if start < 0 or end <= start or end > len(source_text) or start < previous_end:
            errors.append(f"intent {order} source span is out of range or unordered")
            continue
        bound_text = source_text[start:end]
        if item.get("text") != bound_text:
            errors.append(f"intent {order} source text mismatch")
        if item.get("source_text_hash") != _sha256(bound_text):
            errors.append(f"intent {order} source text hash mismatch")
        previous_end = end
    return errors


def build_input_event(
    text: str,
    input_event_id: str,
    received_state: str,
    *,
    proposed_intents: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a source-bound v6.2 input event for routing and persistence."""
    if not re.fullmatch(r"INPUT-\d+", input_event_id):
        raise EventStateError(f"invalid input event id: {input_event_id}")
    spans = (
        [tuple(item.get("source_span", ())) for item in proposed_intents]
        if proposed_intents is not None
        else _intent_spans(text)
    )
    intents: list[dict[str, Any]] = []
    for order, span in enumerate(spans, 1):
        if len(span) != 2 or not all(isinstance(value, int) for value in span):
            raise EventStateError(f"invalid proposed source span at intent {order}")
        start, end = span
        source = text[start:end]
        proposed = proposed_intents[order - 1] if proposed_intents is not None else {}
        kind = proposed.get("kind") or _intent_kind(source)
        intents.append(
            {
                "intent_id": f"{input_event_id}-I{order:02d}",
                "input_event_id": input_event_id,
                "kind": kind,
                "text": source,
                "source_order": order,
                "source_span": [start, end],
                "source_text_hash": _sha256(source),
                "target": proposed.get("target", "current-anchor"),
                "parent_intent_id": proposed.get("parent_intent_id"),
                "question_id": proposed.get("question_id"),
                "status": proposed.get("status", "pending"),
            }
        )
    if any(item["kind"] in {"question", "correction"} for item in intents):
        for item in intents:
            if item["kind"] == "continue":
                item["status"] = "expired-by-question"
    envelope = {
        "schema_version": "6.2",
        "input_event_id": input_event_id,
        "received_state": received_state,
        "raw_text": text,
        "raw_text_hash": _sha256(text),
        "intents": intents,
    }
    errors = validate_intent_envelope(envelope, text)
    if errors:
        raise EventStateError("; ".join(errors))
    return envelope


def split_intents(text: str, input_event_id: str) -> list[dict[str, str]]:
    """Split mixed prose without detaching intents from their source event."""
    envelope = build_input_event(text, input_event_id, "unknown")
    return [
        {
            "intent_id": item["intent_id"],
            "input_event_id": item["input_event_id"],
            "kind": item["kind"],
            "text": item["text"],
            "status": item["status"],
        }
        for item in envelope["intents"]
    ]


def consume_continue(state: dict[str, Any], input_event_id: str) -> dict[str, Any]:
    """Return a new state with one continue event irreversibly consumed."""
    consumed = list(state.get("consumed_continue_event_ids", []))
    if input_event_id in consumed:
        raise EventStateError(f"continue event already consumed: {input_event_id}")
    if not re.fullmatch(r"INPUT-\d+", input_event_id):
        raise EventStateError(f"invalid input event id: {input_event_id}")
    updated = deepcopy(state)
    updated["consumed_continue_event_ids"] = [*consumed, input_event_id]
    return updated


def build_handoff(
    state: dict[str, Any],
    artifact_hashes: dict[str, str],
) -> dict[str, Any]:
    """Build the complete, source-bound handoff used before compaction."""
    missing = sorted(HANDOFF_FIELDS - set(state))
    if missing:
        raise EventStateError(f"handoff state missing fields: {', '.join(missing)}")
    if not state["unique_next_action"]:
        raise EventStateError("handoff requires exactly one next action")
    return {
        "schema_version": "6.0",
        "status": "ready",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "state": {field: deepcopy(state[field]) for field in sorted(HANDOFF_FIELDS)},
        "artifact_hashes": dict(sorted(artifact_hashes.items())),
    }


def validate_handoff(
    payload: dict[str, Any],
    current_artifact_hashes: dict[str, str],
) -> dict[str, Any]:
    """Validate a handoff against current artifacts and fail closed on drift."""
    if payload.get("schema_version") != "6.0":
        return {"status": "REPAIR_REQUIRED", "reason": "unsupported handoff schema"}
    expected = payload.get("artifact_hashes")
    if not isinstance(expected, dict):
        return {"status": "REPAIR_REQUIRED", "reason": "missing artifact hashes"}
    mismatched = sorted(
        name
        for name in set(expected) | set(current_artifact_hashes)
        if expected.get(name) != current_artifact_hashes.get(name)
    )
    if mismatched:
        return {
            "status": "REPAIR_REQUIRED",
            "reason": "handoff artifact hash mismatch",
            "mismatched_artifacts": mismatched,
        }
    state = payload.get("state")
    if not isinstance(state, dict) or HANDOFF_FIELDS - set(state):
        return {"status": "REPAIR_REQUIRED", "reason": "incomplete handoff state"}
    return {"status": "ready", "state": deepcopy(state), "mismatched_artifacts": []}
