#!/usr/bin/env python3
"""Validador local dos registros mínimos do pedido MGP-9."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REGISTRIES = ROOT / "data" / "registries"
STATES = {"SEMENTE", "EM_PESQUISA", "AGUARDA_FONTE", "EM_REVISAO", "CANONICA", "SUPERADA_COM_RASTRO"}
KIND_FILES = {
    "academic": "academic_records.json",
    "research": "research_extension_projects.json",
    "dictionary": "dictionary_entries.json",
    "sources": "academic_sources.json",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def record_hash(record: dict[str, Any]) -> str:
    payload = {key: value for key, value in record.items() if key != "hash"}
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def validate_file(path: Path, required: tuple[str, ...], state_field: str | None = None) -> int:
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list) or not records:
        raise ValueError(f"{path.name}: esperado array não vazio")
    for index, record in enumerate(records, start=1):
        missing = [field for field in required if field not in record]
        if missing:
            raise ValueError(f"{path.name}[{index}]: campos ausentes: {', '.join(missing)}")
        declared = record["hash"]
        if not isinstance(declared, dict) or declared.get("algorithm") != "SHA-256":
            raise ValueError(f"{path.name}[{index}]: hash SHA-256 ausente")
        if declared.get("value") != record_hash(record):
            raise ValueError(f"{path.name}[{index}]: hash não corresponde ao registro")
        if state_field and record[state_field] not in STATES:
            raise ValueError(f"{path.name}[{index}]: estado inválido")
    return len(records)


def validate_all() -> dict[str, int]:
    return {
        "academic_records.json": validate_file(
            REGISTRIES / "academic_records.json",
            ("record_id", "faculty", "program", "curriculum_version", "component", "workload", "extension_hours", "extracurricular_hours", "evidence_ref", "completion_state", "hash", "supersedes"),
        ),
        "research_extension_projects.json": validate_file(
            REGISTRIES / "research_extension_projects.json",
            ("project_id", "question", "sources", "method", "preregistration", "execution", "evidence", "impact", "feedback", "state", "hash"),
            "state",
        ),
        "dictionary_entries.json": validate_file(
            REGISTRIES / "dictionary_entries.json",
            ("entry_id", "term", "definition", "state", "hash", "supersedes"),
            "state",
        ),
        "academic_sources.json": validate_file(
            REGISTRIES / "academic_sources.json",
            ("source_name", "url", "type", "specialty", "trust_level", "last_checked_at", "access_status", "notes", "hash"),
        ),
    }


def list_records(kind: str, state: str | None = None) -> list[dict[str, Any]]:
    """Retorna registros locais sem modificar a fonte; dicionários podem ser filtrados por estado."""
    if kind not in KIND_FILES:
        raise ValueError(f"tipo inválido: {kind}")
    if state is not None and state not in STATES:
        raise ValueError(f"estado inválido: {state}")
    records = json.loads((REGISTRIES / KIND_FILES[kind]).read_text(encoding="utf-8"))
    if state is not None:
        records = [record for record in records if record.get("state") == state]
    return records


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "validate" and len(sys.argv) == 2:
        try:
            print(json.dumps({"status": "PASS", "files": validate_all()}, ensure_ascii=False, indent=2))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            raise SystemExit(1)
        raise SystemExit(0)
    if len(sys.argv) >= 2 and sys.argv[1] == "list":
        import argparse

        parser = argparse.ArgumentParser(description="consulta somente leitura dos registries sintéticos")
        parser.add_argument("list", nargs="?")
        parser.add_argument("--kind", choices=sorted(KIND_FILES), required=True)
        parser.add_argument("--state", choices=sorted(STATES))
        args = parser.parse_args(sys.argv[2:])
        try:
            print(json.dumps(list_records(args.kind, args.state), ensure_ascii=False, indent=2))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            raise SystemExit(1)
        raise SystemExit(0)
    print("uso: python MGP9_POC_SANDBOX_V1/registry.py validate | list --kind KIND [--state STATE]", file=sys.stderr)
    raise SystemExit(2)
