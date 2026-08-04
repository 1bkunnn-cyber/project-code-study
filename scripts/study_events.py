#!/usr/bin/env python3
"""Typed input events and compaction handoffs for project-code-study."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
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


def split_intents(text: str, input_event_id: str) -> list[dict[str, str]]:
    """Split mixed prose without detaching intents from their source event."""
    if not re.fullmatch(r"INPUT-\d+", input_event_id):
        raise EventStateError(f"invalid input event id: {input_event_id}")
    segments = [
        segment.strip(" \t\r\n，,")
        for segment in re.split(r"(?:\r?\n+|[；;])", text)
        if segment.strip(" \t\r\n，,")
    ]
    return [
        {
            "intent_id": f"{input_event_id}-I{index:02d}",
            "input_event_id": input_event_id,
            "kind": _intent_kind(segment),
            "text": segment,
            "status": "pending",
        }
        for index, segment in enumerate(segments, 1)
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
