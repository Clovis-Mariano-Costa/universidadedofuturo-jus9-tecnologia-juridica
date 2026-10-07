"""Autoverificação local; nunca se converte em verificação externa."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from .dispute_and_supersession_rules import (
        authorize_action,
        canonical_bytes,
        load_jsonl,
        resolve_memory,
        sha256,
        validate_supersession,
    )
except ImportError:  # execução direta pelo comando reproduzível do README
    from dispute_and_supersession_rules import (  # type: ignore[no-redef]
        authorize_action,
        canonical_bytes,
        load_jsonl,
        resolve_memory,
        sha256,
        validate_supersession,
    )


def verify_sandbox(root: Path, *, external_verification: bool = False) -> dict[str, Any]:
    if external_verification:
        return {"decision": "DENY", "reason": "autoverificação não pode alegar verificação externa"}
    matrix = json.loads((root / "competence_matrix.json").read_text(encoding="utf-8"))
    records = load_jsonl(root / "governed_memory_registry.jsonl")
    incidents = load_jsonl(root / "incident_log.jsonl")
    learning = load_jsonl(root / "learning_change_log.jsonl")
    checks = {
        "synthetic_only": matrix.get("classification") == "SYNTHETIC_ONLY",
        "least_privilege": "publish" not in matrix.get("capabilities", []),
        "supersession_valid": validate_supersession(records),
        "active_memory_resolves": resolve_memory(records, "mem-synthetic-active")["version"] == 2,
        "disputed_memory_denied": _denied_disputed(records),
        "incidents_preserve_failures": all(record.get("preserved_failure") is True for record in incidents),
        "learning_records_present": len(learning) >= 2,
        "local_action_allowed": authorize_action(identity="charlie-echo-synthetic", action="validate_local") == "ALLOW",
        "forbidden_action_denied": authorize_action(identity="charlie-echo-synthetic", action="publish") == "DENY",
    }
    return {"decision": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "evidence_sha256": sha256(checks)}


def _denied_disputed(records: list[dict[str, Any]]) -> bool:
    try:
        resolve_memory(records, "mem-synthetic-disputed")
    except PermissionError:
        return True
    return False


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    payload = b"\n".join(canonical_bytes(record) for record in records) + b"\n"
    path.write_bytes(payload)


if __name__ == "__main__":
    result = verify_sandbox(Path(__file__).parent)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
