#!/usr/bin/env python3
"""Registry of generic evidence verifiers.

The registry is deliberately claim-type based. It contains no project,
function, tensor, formula, or question-specific exception.
"""

from __future__ import annotations

import ast
import json
import math
import operator
import re
from pathlib import Path
from typing import Any, Callable


class ClaimVerificationError(ValueError):
    pass


def _source(claim: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    path = claim.get("path")
    if not path or "..." in str(path) or Path(str(path)).is_absolute() and not str(Path(str(path))).startswith(str(repo_root)):
        raise ClaimVerificationError("source claim requires a non-placeholder repository-relative path")
    file = (repo_root / str(path)).resolve()
    if not file.is_file():
        raise ClaimVerificationError(f"source path not found: {path}")
    lines = file.read_text(encoding="utf-8", errors="replace").splitlines()
    line = claim.get("line")
    if line is not None and (not isinstance(line, int) or line < 1 or line > len(lines)):
        raise ClaimVerificationError("source line is outside the file")
    symbol = claim.get("symbol")
    if symbol and not any(re.search(rf"\b{re.escape(str(symbol))}\b", text) for text in lines):
        raise ClaimVerificationError(f"source symbol not found: {symbol}")
    return {"claim_type": "source", "status": "verified", "path": str(file), "symbol": symbol, "line": line}


def _configuration(claim: dict[str, Any], _: Path) -> dict[str, Any]:
    resolved = claim.get("resolved_config")
    expected = claim.get("expected")
    if not isinstance(resolved, dict) or not isinstance(expected, dict):
        raise ClaimVerificationError("configuration claim requires resolved_config and expected mappings")
    missing = {key: value for key, value in expected.items() if resolved.get(key) != value}
    if missing:
        raise ClaimVerificationError(f"resolved configuration mismatch: {missing}")
    return {"claim_type": "configuration", "status": "verified", "keys": sorted(expected)}


def _runtime(claim: dict[str, Any], _: Path) -> dict[str, Any]:
    required = ("command", "log", "artifacts", "observation")
    missing = [key for key in required if not claim.get(key)]
    if missing:
        raise ClaimVerificationError("runtime claim missing: " + ", ".join(missing))
    if claim.get("observation") not in {"observed", "verified"}:
        raise ClaimVerificationError("runtime claim must identify an observed result")
    return {"claim_type": "runtime", "status": "verified", "command": claim["command"], "artifacts": claim["artifacts"]}


def _safe_numeric(expression: str) -> float:
    tree = ast.parse(expression, mode="eval")
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd, ast.Mod)
    if any(not isinstance(node, allowed) for node in ast.walk(tree)):
        raise ClaimVerificationError("mathematical expression contains unsupported syntax")
    return float(eval(compile(tree, "<claim>", "eval"), {"__builtins__": {}}, {}))


def _mathematical(claim: dict[str, Any], _: Path) -> dict[str, Any]:
    if "lhs" not in claim or "rhs" not in claim:
        raise ClaimVerificationError("mathematical claim requires lhs and rhs")
    lhs = _safe_numeric(str(claim["lhs"]))
    rhs = _safe_numeric(str(claim["rhs"]))
    if not math.isclose(lhs, rhs, rel_tol=float(claim.get("rel_tol", 1e-9)), abs_tol=float(claim.get("abs_tol", 1e-9))):
        raise ClaimVerificationError(f"mathematical mismatch: {lhs} != {rhs}")
    return {"claim_type": "mathematical", "status": "verified", "lhs": lhs, "rhs": rhs}


def _paper(claim: dict[str, Any], _: Path) -> dict[str, Any]:
    if not claim.get("locator") or not claim.get("scope") or not claim.get("title"):
        raise ClaimVerificationError("paper claim requires title, exact locator, and scope")
    return {"claim_type": "paper", "status": "verified", "locator": claim["locator"], "scope": claim["scope"]}


def _comparison(claim: dict[str, Any], _: Path) -> dict[str, Any]:
    required = ("baseline", "new_value", "unit", "scope")
    if any(key not in claim for key in required):
        raise ClaimVerificationError("comparison claim requires baseline, new_value, unit, and scope")
    baseline, new_value = float(claim["baseline"]), float(claim["new_value"])
    if baseline == 0 and claim.get("relative_delta") is not None:
        raise ClaimVerificationError("relative delta is undefined for a zero baseline")
    absolute = new_value - baseline
    relative = None if baseline == 0 else absolute / baseline
    if "absolute_delta" in claim and not math.isclose(float(claim["absolute_delta"]), absolute):
        raise ClaimVerificationError("absolute delta does not match baseline and new value")
    return {"claim_type": "comparison", "status": "verified", "absolute_delta": absolute, "relative_delta": relative, "unit": claim["unit"], "scope": claim["scope"]}


def _learner_verdict(claim: dict[str, Any], _: Path) -> dict[str, Any]:
    intents = claim.get("intents")
    answers = claim.get("answers")
    if not isinstance(intents, list) or not isinstance(answers, list) or len(intents) != len(answers) or not intents:
        raise ClaimVerificationError("learner verdict requires one answer span per question intent")
    for answer in answers:
        if not isinstance(answer, dict) or not answer.get("span"):
            raise ClaimVerificationError("learner answer span is missing")
        if answer.get("verdict") == "wrong" and not answer.get("conflicting_evidence"):
            raise ClaimVerificationError("wrong verdict requires explicit conflicting evidence")
    return {"claim_type": "learner_verdict", "status": "verified", "aligned_items": len(intents)}


REGISTRY: dict[str, Callable[[dict[str, Any], Path], dict[str, Any]]] = {
    "source": _source,
    "configuration": _configuration,
    "runtime": _runtime,
    "mathematical": _mathematical,
    "paper": _paper,
    "comparison": _comparison,
    "learner_verdict": _learner_verdict,
}


def verify_claim(claim_type: str, claim: dict[str, Any], *, repo_root: Path | str = ".") -> dict[str, Any]:
    try:
        verifier = REGISTRY[claim_type]
    except KeyError as exc:
        raise ClaimVerificationError(f"unsupported claim type: {claim_type}") from exc
    return verifier(claim, Path(repo_root).resolve())


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("claim_type", choices=sorted(REGISTRY))
    parser.add_argument("claim_json")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        result = verify_claim(args.claim_type, json.loads(args.claim_json), repo_root=args.repo_root)
    except (ClaimVerificationError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
