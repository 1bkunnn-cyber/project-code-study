#!/usr/bin/env python3
"""Fail-closed lifecycle for durable learning-memory candidates."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any

import study_events


class MemoryLifecycleError(ValueError):
    """Raised when a memory candidate transition is invalid or unbound."""


TERMINAL_STATUSES = {"rejected", "stale"}
ALLOWED_TRANSITIONS = {
    "candidate": {"approved", "rejected"},
    "approved": {"saved", "rejected"},
    "saved": {"stale"},
    "rejected": set(),
    "stale": set(),
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _candidate_kind(text: str, trigger: str) -> tuple[str, str] | None:
    normalized = text.strip().lower()
    if trigger == "step_complete":
        return "project", "durable rule extracted at Step completion"
    if re.search(r"(纠正|更正|原结论错误|不是.+而是|correction)", normalized):
        return "correction", "learner correction changes canonical knowledge"
    if re.search(
        r"(长期|以后|始终|每次|偏好|输出质量|文档质量|路线质量|教学质量|"
        r"必须能脱离|请记住|always|preference|quality)",
        normalized,
    ):
        return "feedback", "durable teaching or quality preference"
    return None


def classify_memory_candidate(
    text: str,
    *,
    trigger: str = "message",
    candidate_id: str,
) -> dict[str, Any] | None:
    """Return a typed candidate only for a durable trigger.

    A normal one-off question returns ``None`` and therefore cannot pollute the
    long-term store.
    """
    if not re.fullmatch(r"M-\d+", candidate_id):
        raise MemoryLifecycleError(f"invalid memory candidate ID: {candidate_id}")
    content = text.strip()
    if not content:
        return None
    classification = _candidate_kind(content, trigger)
    if classification is None:
        return None
    kind, reason = classification
    return {
        "schema_version": "6.0",
        "candidate_id": candidate_id,
        "kind": kind,
        "trigger": trigger,
        "status": "candidate",
        "content": content,
        "content_hash": _sha256(content),
        "reason": reason,
        "created_at": _now(),
        "updated_at": _now(),
    }


def transition_candidate(
    candidate: dict[str, Any] | None,
    target_status: str,
    *,
    approved_by: str | None = None,
    release_tx_id: str | None = None,
    receipt_hash: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    """Perform a legal memory lifecycle transition without mutating input."""
    if candidate is None:
        raise MemoryLifecycleError("cannot transition a missing candidate")
    current = str(candidate.get("status", ""))
    if target_status not in ALLOWED_TRANSITIONS.get(current, set()):
        raise MemoryLifecycleError(f"illegal memory transition: {current} -> {target_status}")

    updated = deepcopy(candidate)
    updated["status"] = target_status
    updated["updated_at"] = _now()

    if target_status == "approved":
        if approved_by not in {"user", "policy"}:
            raise MemoryLifecycleError("approval must identify user or policy")
        updated["approved_by"] = approved_by
        updated["approved_at"] = _now()
    elif target_status == "saved":
        if not re.fullmatch(r"TX-\d+", release_tx_id or ""):
            raise MemoryLifecycleError("saved memory requires a bound release TX-ID")
        if not re.fullmatch(r"[0-9a-f]{64}", receipt_hash or ""):
            raise MemoryLifecycleError("saved memory requires a SHA-256 receipt hash")
        updated["release_tx_id"] = release_tx_id
        updated["receipt_hash"] = receipt_hash
        updated["saved_at"] = _now()
    elif target_status in TERMINAL_STATUSES:
        if not reason:
            raise MemoryLifecycleError(f"{target_status} memory requires a reason")
        updated["reason"] = reason
        updated[f"{target_status}_at"] = _now()
        if target_status == "rejected":
            updated.pop("content", None)
            updated.pop("approved_by", None)
            updated.pop("approved_at", None)

    return updated


def create_compaction_handoff(
    state: dict[str, Any],
    artifact_hashes: dict[str, str],
    *,
    memory_candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create the complete pre-compaction handoff with safe memory snapshots."""
    payload = study_events.build_handoff(state, artifact_hashes)
    payload["handoff_kind"] = "pre-compaction"
    payload["memory_candidates"] = [
        {
            key: deepcopy(item[key])
            for key in ("candidate_id", "status", "kind", "content_hash")
            if key in item
        }
        for item in memory_candidates
    ]
    return payload


def restore_compaction_handoff(
    payload: dict[str, Any],
    current_artifact_hashes: dict[str, str],
) -> dict[str, Any]:
    """Restore only a hash-matching handoff; otherwise enter repair."""
    restored = study_events.validate_handoff(payload, current_artifact_hashes)
    if restored.get("status") != "ready":
        return restored
    candidates = payload.get("memory_candidates")
    if not isinstance(candidates, list):
        return {"status": "REPAIR_REQUIRED", "reason": "missing memory candidate state"}
    for item in candidates:
        if (
            not isinstance(item, dict)
            or not re.fullmatch(r"M-\d+", str(item.get("candidate_id", "")))
            or item.get("status") not in ALLOWED_TRANSITIONS
            or not re.fullmatch(r"[0-9a-f]{64}", str(item.get("content_hash", "")))
        ):
            return {"status": "REPAIR_REQUIRED", "reason": "invalid memory candidate state"}
    restored["memory_candidates"] = deepcopy(candidates)
    return restored


def _sanitize_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sanitized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for candidate in candidates:
        candidate_id = str(candidate.get("candidate_id", ""))
        status = str(candidate.get("status", ""))
        if not re.fullmatch(r"M-\d+", candidate_id) or candidate_id in seen:
            raise MemoryLifecycleError(f"invalid or duplicate candidate ID: {candidate_id}")
        if status not in ALLOWED_TRANSITIONS:
            raise MemoryLifecycleError(f"invalid candidate status: {status}")
        item = deepcopy(candidate)
        if status == "rejected":
            item.pop("content", None)
        if not re.fullmatch(r"[0-9a-f]{64}", str(item.get("content_hash", ""))):
            raise MemoryLifecycleError(f"candidate has no valid content hash: {candidate_id}")
        seen.add(candidate_id)
        sanitized.append(item)
    return sanitized


def persist_candidate_journal(
    path: Path,
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    """Atomically persist lifecycle state without retaining rejected content."""
    sanitized = _sanitize_candidates(candidates)
    payload: dict[str, Any] = {
        "schema_version": "6.0",
        "candidates": sanitized,
        "updated_at": _now(),
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload["journal_hash"] = _sha256(canonical)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    os.close(fd)
    stage = Path(raw)
    try:
        stage.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        os.replace(stage, path)
    finally:
        stage.unlink(missing_ok=True)
    return payload


def load_candidate_journal(path: Path) -> dict[str, Any]:
    """Load and integrity-check a persisted candidate lifecycle journal."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise MemoryLifecycleError(f"invalid candidate journal: {exc}") from exc
    expected = payload.get("journal_hash")
    unsigned = {key: value for key, value in payload.items() if key != "journal_hash"}
    canonical = json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if payload.get("schema_version") != "6.0" or expected != _sha256(canonical):
        raise MemoryLifecycleError("candidate journal hash mismatch")
    candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        raise MemoryLifecycleError("candidate journal candidates must be a list")
    _sanitize_candidates(candidates)
    return payload
