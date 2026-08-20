#!/usr/bin/env python3
"""Contrato dry-run entre MGP9, Pacote 12 e automação universitária.

O contrato é somente de composição em memória. Não grava arquivos, não chama
rede e não promove nenhuma evidência a aprovação acadêmica ou efeito externo.
"""

from __future__ import annotations

from typing import Any, Mapping

from .core import append_provenance_event, sha256_json


def _gate_allowed(gate: Any) -> bool:
    if isinstance(gate, Mapping):
        return bool(gate.get("allowed"))
    return bool(getattr(gate, "allowed", False))


def _gate_code(gate: Any) -> str:
    if isinstance(gate, Mapping):
        return str(gate.get("code", "UNKNOWN"))
    return str(getattr(gate, "code", "UNKNOWN"))


def compose_dry_run(
    mgp9_manifest: Mapping[str, Any],
    package12_gate: Any,
    university_decision: Mapping[str, Any],
    provenance_record: Mapping[str, Any],
) -> dict[str, Any]:
    """Compõe os três sandboxes e falha fechado diante de qualquer lacuna."""

    reasons: list[str] = []
    if mgp9_manifest.get("harness") != "MGP9_POC_SANDBOX_V1":
        reasons.append("MGP9_MANIFEST_INVALID")
    if mgp9_manifest.get("data_classification") != "SYNTHETIC_ONLY":
        reasons.append("MGP9_NON_SYNTHETIC_DATA")
    for field in ("input_sha256", "output_sha256", "pair_count"):
        if not mgp9_manifest.get(field):
            reasons.append(f"MGP9_FIELD_MISSING:{field}")
    if not _gate_allowed(package12_gate):
        reasons.append(f"PACKAGE12_GATE_BLOCKED:{_gate_code(package12_gate)}")
    if university_decision.get("status") != "DECISION_RECORDED_INTERNAL":
        reasons.append("UNIVERSITY_DECISION_NOT_INTERNAL")
    record = university_decision.get("record", {})
    if record.get("jurisdiction_label") != "INTERNAL_EXPERIMENTAL":
        reasons.append("UNIVERSITY_JURISDICTION_INVALID")
    if record.get("human_gate") is not True:
        reasons.append("UNIVERSITY_HUMAN_GATE_MISSING")
    if not provenance_record.get("events"):
        reasons.append("PROVENANCE_EVENTS_MISSING")
    if provenance_record.get("classification") != "INTERNAL_SYNTHETIC":
        reasons.append("PROVENANCE_CLASSIFICATION_INVALID")

    status = "READY_FOR_HUMAN_REVIEW" if not reasons else "BLOCKED"
    payload = {
        "bridge": "UNIVERSIDADE_AUTOMACAO_BRIDGE_V1",
        "status": status,
        "reasons": reasons,
        "external_effect": False,
        "mgp9": {
            "harness": mgp9_manifest.get("harness"),
            "pair_count": mgp9_manifest.get("pair_count"),
            "output_sha256": mgp9_manifest.get("output_sha256"),
        },
        "package12": {"gate_code": _gate_code(package12_gate)},
        "university": {
            "case_id": record.get("case_id"),
            "jurisdiction_label": record.get("jurisdiction_label"),
        },
        "provenance_event_count": len(provenance_record.get("events", [])),
    }
    payload["bridge_sha256"] = sha256_json(payload)
    return payload


def append_bridge_event(events: list[dict[str, Any]], result: Mapping[str, Any]) -> dict[str, Any]:
    """Registra o resultado do dry-run em uma trilha fornecida pelo chamador."""

    return append_provenance_event(
        events,
        "BRIDGE_DRY_RUN",
        {
            "status": result.get("status"),
            "bridge_sha256": result.get("bridge_sha256"),
            "external_effect": result.get("external_effect"),
        },
    )
