#!/usr/bin/env python3
"""Unified WAL and commit receipt for a project-study publication."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any


class ReleaseTransactionError(ValueError):
    """Raised when a release cannot be proven as one coherent version."""


REQUIRED_ARTIFACTS = {"qa", "log", "memory", "document"}
REQUIRED_VALIDATORS = {"qa_log", "memory", "document"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _sha256_text(content: str) -> str:
    return _sha256_bytes(content.encode("utf-8"))


def _hash_path(path: Path) -> str:
    if path.is_file():
        return _sha256_bytes(path.read_bytes())
    if path.is_dir():
        digest = hashlib.sha256()
        for child in sorted(item for item in path.rglob("*") if item.is_file()):
            relative = child.relative_to(path).as_posix().encode("utf-8")
            digest.update(len(relative).to_bytes(8, "big"))
            digest.update(relative)
            content = child.read_bytes()
            digest.update(len(content).to_bytes(8, "big"))
            digest.update(content)
        return digest.hexdigest()
    raise ReleaseTransactionError(f"artifact path does not exist: {path}")


def _payload_hash(payload: dict[str, Any], *, omit: set[str] | None = None) -> str:
    stripped = {key: value for key, value in payload.items() if key not in (omit or set())}
    return _sha256_text(_canonical_json(stripped))


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
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


def _validate_gates(
    readiness_manifest: dict[str, Any],
    validator_results: dict[str, str],
    cold_start_result: dict[str, Any],
) -> None:
    if readiness_manifest.get("ready") is not True:
        raise ReleaseTransactionError("readiness manifest is not ready")
    if not REQUIRED_VALIDATORS <= set(validator_results):
        raise ReleaseTransactionError("publication validators are incomplete")
    if any(value != "pass" for value in validator_results.values()):
        raise ReleaseTransactionError("every publication validator must pass")
    if cold_start_result.get("status") != "pass":
        raise ReleaseTransactionError("document cold-start test must pass")
    if not re.fullmatch(r"[0-9a-f]{64}", str(cold_start_result.get("report_hash", ""))):
        raise ReleaseTransactionError("cold-start result must bind the report SHA-256")


def prepare_release(
    *,
    tx_id: str,
    doc_tx_id: str,
    artifacts: dict[str, Path],
    source_revision: str,
    readiness_manifest: dict[str, Any],
    validator_results: dict[str, str],
    cold_start_result: dict[str, Any],
    not_run: list[str],
    current_step: str,
    current_node: str,
    wal_path: Path,
    response_text: str,
    previous_receipt_hash: str | None = None,
) -> dict[str, Any]:
    """Persist a PREPARED record after all gates pass and before success claims."""
    if not re.fullmatch(r"TX-\d+", tx_id):
        raise ReleaseTransactionError("invalid TX-ID")
    if not re.fullmatch(r"DOC-TX-\d+", doc_tx_id):
        raise ReleaseTransactionError("invalid DOC-TX-ID")
    if set(artifacts) != REQUIRED_ARTIFACTS:
        raise ReleaseTransactionError(
            "release artifacts must be exactly qa, log, memory, and document"
        )
    if not re.fullmatch(
        r"(?:git:[0-9a-f]{7,40}|uncommitted:[0-9a-f]{64})",
        source_revision.strip(),
    ):
        raise ReleaseTransactionError("source revision must be immutable")
    if not current_step.strip() or not current_node.strip():
        raise ReleaseTransactionError("source revision, current Step, and current NODE are required")
    if not response_text:
        raise ReleaseTransactionError("a response draft is required for claim binding")
    if len(not_run) != len(set(not_run)):
        raise ReleaseTransactionError("not_run capability names must be unique")
    if previous_receipt_hash is not None and not re.fullmatch(
        r"[0-9a-f]{64}",
        previous_receipt_hash,
    ):
        raise ReleaseTransactionError("previous receipt hash must be SHA-256")
    _validate_gates(readiness_manifest, validator_results, cold_start_result)
    for path in artifacts.values():
        if not path.exists():
            raise ReleaseTransactionError(f"release artifact is missing: {path}")
    if wal_path.exists():
        existing = json.loads(wal_path.read_text(encoding="utf-8"))
        if existing.get("state") == "PREPARED":
            raise ReleaseTransactionError("an unresolved PREPARED release already exists")

    artifact_paths = {
        name: str(path.resolve())
        for name, path in sorted(artifacts.items())
    }
    payload: dict[str, Any] = {
        "schema_version": "6.0",
        "state": "PREPARED",
        "tx_id": tx_id,
        "doc_tx_id": doc_tx_id,
        "artifact_paths": artifact_paths,
        "artifact_hashes": {
            name: _hash_path(Path(path))
            for name, path in artifact_paths.items()
        },
        "source_revision": source_revision,
        "readiness_manifest": readiness_manifest,
        "readiness_manifest_hash": _sha256_text(_canonical_json(readiness_manifest)),
        "validator_results": validator_results,
        "cold_start_result": cold_start_result,
        "not_run": list(not_run),
        "current_step": current_step,
        "current_node": current_node,
        "response_hash": _sha256_text(response_text),
        "previous_receipt_hash": previous_receipt_hash,
        "prepared_at": _now(),
    }
    payload["prepared_hash"] = _payload_hash(payload)
    _write_json_atomic(wal_path, payload)
    return payload


def _load_wal(wal_path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(wal_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ReleaseTransactionError(f"invalid release WAL: {exc}") from exc
    return payload


def _verify_prepared(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != "6.0":
        errors.append("unsupported release schema")
    if payload.get("state") != "PREPARED":
        errors.append("release WAL is not PREPARED")
    if payload.get("prepared_hash") != _payload_hash(payload, omit={"prepared_hash"}):
        errors.append("prepared WAL hash mismatch")
    try:
        _validate_gates(
            payload["readiness_manifest"],
            payload["validator_results"],
            payload["cold_start_result"],
        )
    except (KeyError, ReleaseTransactionError) as exc:
        errors.append(str(exc))
    paths = payload.get("artifact_paths")
    hashes = payload.get("artifact_hashes")
    if not isinstance(paths, dict) or not isinstance(hashes, dict):
        errors.append("artifact paths or hashes are missing")
        return errors
    for name in REQUIRED_ARTIFACTS:
        raw = paths.get(name)
        expected = hashes.get(name)
        path = Path(raw) if isinstance(raw, str) else None
        if path is None or not path.exists():
            errors.append(f"artifact missing at commit: {name}")
        elif expected != _hash_path(path):
            errors.append(f"artifact hash changed after validation: {name}")
    return errors


def commit_release(wal_path: Path, receipt_path: Path) -> dict[str, Any]:
    """Commit an unchanged PREPARED release and emit the sole success receipt."""
    prepared = _load_wal(wal_path)
    errors = _verify_prepared(prepared)
    if errors:
        aborted = dict(prepared)
        aborted["state"] = "ABORTED"
        aborted["aborted_at"] = _now()
        aborted["errors"] = errors
        _write_json_atomic(wal_path, aborted)
        raise ReleaseTransactionError("; ".join(errors))

    receipt = dict(prepared)
    receipt["state"] = "COMMITTED"
    receipt["committed_at"] = _now()
    receipt["receipt_hash"] = _payload_hash(receipt)
    _write_json_atomic(receipt_path, receipt)

    committed_wal = dict(prepared)
    committed_wal["state"] = "COMMITTED"
    committed_wal["committed_at"] = receipt["committed_at"]
    committed_wal["receipt_path"] = str(receipt_path.resolve())
    committed_wal["receipt_hash"] = receipt["receipt_hash"]
    _write_json_atomic(wal_path, committed_wal)
    return receipt


def validate_release_receipt(
    receipt_path: Path,
    artifacts: dict[str, Path],
    *,
    response_text: str | None = None,
) -> list[str]:
    """Validate receipt integrity, current artifacts, and optional response text."""
    try:
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"release receipt is unreadable: {exc}"]
    errors: list[str] = []
    if payload.get("schema_version") != "6.0" or payload.get("state") != "COMMITTED":
        errors.append("release receipt is not COMMITTED schema 6.0")
    if payload.get("receipt_hash") != _payload_hash(payload, omit={"receipt_hash"}):
        errors.append("release receipt hash mismatch")
    try:
        _validate_gates(
            payload["readiness_manifest"],
            payload["validator_results"],
            payload["cold_start_result"],
        )
    except (KeyError, ReleaseTransactionError) as exc:
        errors.append(str(exc))
    expected = payload.get("artifact_hashes", {})
    paths = payload.get("artifact_paths", {})
    if set(artifacts) != REQUIRED_ARTIFACTS:
        errors.append("current artifact set is incomplete")
    for name, path in artifacts.items():
        if str(path.resolve()) != paths.get(name):
            errors.append(f"artifact path mismatch: {name}")
        if not path.exists() or expected.get(name) != _hash_path(path):
            errors.append(f"artifact hash mismatch: {name}")
    if response_text is not None and payload.get("response_hash") != _sha256_text(response_text):
        errors.append("response hash does not match committed release")
    return errors


def recover_release(wal_path: Path, receipt_path: Path) -> dict[str, Any]:
    """Recover idempotently from a PREPARED or receipt-written transaction."""
    wal = _load_wal(wal_path)
    if receipt_path.is_file():
        try:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise ReleaseTransactionError(f"invalid existing receipt: {exc}") from exc
        if (
            receipt.get("state") == "COMMITTED"
            and receipt.get("receipt_hash") == _payload_hash(receipt, omit={"receipt_hash"})
            and receipt.get("prepared_hash") == wal.get("prepared_hash")
        ):
            return receipt
        raise ReleaseTransactionError("existing receipt does not match release WAL")
    if wal.get("state") == "PREPARED":
        return commit_release(wal_path, receipt_path)
    raise ReleaseTransactionError(f"release cannot be recovered from state {wal.get('state')}")


def _artifacts_from_manifest(payload: dict[str, Any]) -> dict[str, Path]:
    raw = payload.get("artifact_paths")
    if not isinstance(raw, dict):
        raise ReleaseTransactionError("manifest artifact_paths must be an object")
    return {name: Path(path) for name, path in raw.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--manifest", type=Path, required=True)
    prepare.add_argument("--wal", type=Path, required=True)
    prepare.add_argument("--response-file", type=Path, required=True)
    commit = sub.add_parser("commit")
    commit.add_argument("--wal", type=Path, required=True)
    commit.add_argument("--receipt", type=Path, required=True)
    recover = sub.add_parser("recover")
    recover.add_argument("--wal", type=Path, required=True)
    recover.add_argument("--receipt", type=Path, required=True)
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("--receipt", type=Path, required=True)
    validate_parser.add_argument("--response-file", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
            result = prepare_release(
                tx_id=manifest["tx_id"],
                doc_tx_id=manifest["doc_tx_id"],
                artifacts=_artifacts_from_manifest(manifest),
                source_revision=manifest["source_revision"],
                readiness_manifest=manifest["readiness_manifest"],
                validator_results=manifest["validator_results"],
                cold_start_result=manifest["cold_start_result"],
                not_run=manifest.get("not_run", []),
                current_step=manifest["current_step"],
                current_node=manifest["current_node"],
                wal_path=args.wal,
                response_text=args.response_file.read_text(encoding="utf-8"),
                previous_receipt_hash=manifest.get("previous_receipt_hash"),
            )
        elif args.command == "commit":
            result = commit_release(args.wal, args.receipt)
        elif args.command == "recover":
            result = recover_release(args.wal, args.receipt)
        else:
            receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
            artifacts = _artifacts_from_manifest(receipt)
            response = (
                args.response_file.read_text(encoding="utf-8")
                if args.response_file
                else None
            )
            errors = validate_release_receipt(
                args.receipt,
                artifacts,
                response_text=response,
            )
            if errors:
                raise ReleaseTransactionError("; ".join(errors))
            result = {"state": "COMMITTED", "receipt": str(args.receipt)}
    except (OSError, ValueError, KeyError, ReleaseTransactionError) as exc:
        print(json.dumps({"state": "FAILED", "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
