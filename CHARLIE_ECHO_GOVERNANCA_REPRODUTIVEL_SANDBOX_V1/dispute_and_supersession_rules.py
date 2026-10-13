"""Regras locais, determinísticas e fail-closed para memória sintética."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


FORBIDDEN_BOUNDARIES = frozenset({"B12", "B01.1"})
ALLOWED_ACTIONS = frozenset({"read_synthetic", "validate_local", "replay_local", "rollback_local"})


def canonical_bytes(value: Any) -> bytes:
    if isinstance(value, bytes):
        payload = value
    elif isinstance(value, str):
        payload = value.encode("utf-8")
    else:
        payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    raw = path.read_bytes()
    if b"\r" in raw:
        raise ValueError(f"newline não canônico: {path}")
    for line_number, line in enumerate(raw.decode("utf-8").split("\n"), start=1):
        if not line:
            continue
        record = json.loads(line)
        if not isinstance(record, dict):
            raise ValueError(f"registro não é objeto: {path}:{line_number}")
        records.append(record)
    return records


def assert_local_boundary(value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True).upper()
    if any(boundary in text for boundary in FORBIDDEN_BOUNDARIES):
        raise PermissionError("integração com fronteira científica proibida")


def resolve_memory(records: Iterable[dict[str, Any]], memory_id: str) -> dict[str, Any]:
    candidates = [record for record in records if record.get("memory_id") == memory_id]
    if not candidates:
        raise LookupError("memória desconhecida")
    assert_local_boundary(candidates)
    superseded = {record.get("supersedes_version") for record in candidates if record.get("supersedes_version") is not None}
    active = [record for record in candidates if record.get("status") == "ACTIVE" and record.get("version") not in superseded]
    disputed = [record for record in candidates if record.get("status") == "DISPUTED"]
    if disputed and not active:
        raise PermissionError("memória disputada não é canônica")
    if not active:
        raise PermissionError("memória sem versão ativa resolvida")
    return max(active, key=lambda record: int(record["version"]))


def validate_supersession(records: Iterable[dict[str, Any]]) -> bool:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        assert_local_boundary(record)
        memory_id = record.get("memory_id")
        if memory_id:
            grouped.setdefault(memory_id, []).append(record)
    for memory_records in grouped.values():
        versions = [int(record["version"]) for record in memory_records]
        if len(versions) != len(set(versions)):
            return False
        for record in memory_records:
            if record.get("supersedes_version") is not None and int(record.get("version", 0)) <= int(record.get("supersedes_version", 0)):
                return False
    return True


def authorize_action(*, identity: str, action: str, revoked: bool = False, replayed: bool = False, prompt_injection: bool = False, logging_available: bool = True) -> str:
    if not logging_available or revoked or replayed or prompt_injection:
        return "DENY"
    if identity != "charlie-echo-synthetic" or action not in ALLOWED_ACTIONS:
        return "DENY"
    return "ALLOW"


def attempt_competence_change(matrix: dict[str, Any], requested_capability: str) -> str:
    assert_local_boundary(requested_capability)
    if requested_capability in matrix.get("forbidden_capabilities", []):
        return "DENY"
    return "DENY"
