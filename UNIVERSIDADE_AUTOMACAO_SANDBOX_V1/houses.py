"""Contratos offline para Casas-Lar, Casas-Trabalho e CITAT.

Este módulo não acessa Drive, GitHub ou qualquer cofre. Recebe somente
metadados fornecidos pelo chamador e falha fechado diante de origem,
autorização, hash ou temporalidade insuficientes.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Mapping

from .core import scan_security, sha256_json


SYMBOLIC_MILESTONE = "1973-06-16"
AUTHORIZED_CITAT_FIELDS = frozenset(
    {
        "document_id",
        "version",
        "hash",
        "authorized_sync",
        "scope",
        "reviewer",
        "review_at",
        "source_ref",
    }
)
FORBIDDEN_SYNC_FIELDS = frozenset(
    {
        "domestic_documents",
        "personal_documents",
        "secrets",
        "credentials",
        "private_notes",
        "quarto",
    }
)
SPECIALIZATION_PATHS = frozenset({"university_training", "documented_work"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _missing(record: Mapping[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [field for field in fields if record.get(field) in (None, "", [], {})]


def _sensitive_keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).lower()
            if normalized in FORBIDDEN_SYNC_FIELDS or any(marker in normalized for marker in ("password", "token", "credential", "secret")):
                found.add(str(key))
            found.update(_sensitive_keys(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_sensitive_keys(child))
    return found


def _redact_sensitive(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _redact_sensitive(child)
            for key, child in value.items()
            if str(key).lower() not in FORBIDDEN_SYNC_FIELDS
            and not any(marker in str(key).lower() for marker in ("password", "token", "credential", "secret"))
        }
    if isinstance(value, list):
        return [_redact_sensitive(child) for child in value]
    return value


def validate_symbolic_time(record: Mapping[str, Any]) -> dict[str, Any]:
    """Separa marco simbólico de datas que representam eventos reais."""

    errors: list[str] = []
    if record.get("marco_simbolico") not in (None, SYMBOLIC_MILESTONE):
        errors.append("INVALID_SYMBOLIC_MILESTONE")
    for field in ("created_at", "signed_at", "updated_at"):
        if record.get(field) == SYMBOLIC_MILESTONE:
            errors.append(f"{field.upper()}_MUST_BE_REAL_DATE")
    return {"valid": not errors, "errors": errors}


def inventory_houses(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Gera inventário determinístico somente de metadados, sem conteúdo doméstico."""

    normalized: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for raw in records:
        record = deepcopy(dict(raw))
        sensitive_keys = _sensitive_keys(record)
        member_id = record.get("member_id")
        missing = _missing(
            record,
            ("member_id", "member_label", "casa_lar", "casa_trabalho", "citat"),
        )
        security = scan_security(record)
        temporal = validate_symbolic_time(record)
        if missing:
            errors.append({"member_id": member_id, "reason": "MISSING_FIELDS", "fields": missing})
        if security["status"] == "BLOCKED" or sensitive_keys:
            errors.append({"member_id": member_id, "reason": "SENSITIVE_METADATA", "findings": security["secret_findings"] + security["pii_findings"] + sorted(sensitive_keys)})
        if not temporal["valid"]:
            errors.append({"member_id": member_id, "reason": "TEMPORALITY", "findings": temporal["errors"]})
        normalized.append(_redact_sensitive(record))
    normalized.sort(key=lambda item: str(item.get("member_id", "")))
    return {
        "status": "READY_FOR_REVIEW" if not errors else "BLOCKED",
        "records": normalized,
        "record_count": len(normalized),
        "errors": errors,
        "inventory_sha256": sha256_json(normalized),
    }


def map_house(record: Mapping[str, Any]) -> dict[str, Any]:
    """Retorna somente o mapa de referências; nunca copia conteúdo de uma Casa-Lar."""

    required = ("member_id", "casa_lar", "casa_trabalho", "citat")
    missing = _missing(record, required)
    if missing:
        return {"status": "BLOCKED", "reason": "MISSING_FIELDS", "fields": missing}
    return {
        "status": "MAPPED",
        "member_id": record["member_id"],
        "casa_lar": deepcopy(record["casa_lar"]),
        "casa_trabalho": deepcopy(record["casa_trabalho"]),
        "citat": deepcopy(record["citat"]),
        "specialties": deepcopy(record.get("specialties", [])),
        "automations": deepcopy(record.get("automations", [])),
        "content_sync": "FORBIDDEN_BY_DEFAULT",
    }


def validate_specialization(specialty: Mapping[str, Any]) -> dict[str, Any]:
    required = ("specialty_id", "path", "scope", "evidence", "reviewer", "review_at")
    missing = _missing(specialty, required)
    errors = list(missing)
    if specialty.get("path") not in SPECIALIZATION_PATHS:
        errors.append("INVALID_SPECIALIZATION_PATH")
    if specialty.get("review_at") == SYMBOLIC_MILESTONE:
        errors.append("REVIEW_AT_MUST_BE_REAL_DATE")
    security = scan_security(specialty)
    if security["status"] == "BLOCKED":
        errors.append("SENSITIVE_SPECIALIZATION_METADATA")
    return {"valid": not errors, "errors": errors}


def prepare_citat_sync(source: Mapping[str, Any], destination: Mapping[str, Any]) -> dict[str, Any]:
    """Prepara uma sincronização autorizada sem sobrescrever nenhum lado."""

    forbidden = sorted((set(source) | set(destination)) & FORBIDDEN_SYNC_FIELDS)
    if forbidden:
        return {"status": "BLOCKED", "reason": "DOMESTIC_OR_SECRET_CONTENT_FORBIDDEN", "fields": forbidden}
    missing = _missing(source, ("document_id", "version", "hash", "authorized_sync", "source_ref"))
    if missing:
        return {"status": "BLOCKED", "reason": "CITAT_AUTHORIZATION_OR_PROVENANCE_MISSING", "fields": missing}
    if source.get("authorized_sync") is not True:
        return {"status": "BLOCKED", "reason": "CITAT_SYNC_NOT_AUTHORIZED"}
    unknown = sorted(set(source) - AUTHORIZED_CITAT_FIELDS)
    if unknown:
        return {"status": "BLOCKED", "reason": "UNAPPROVED_CITAT_FIELDS", "fields": unknown}
    source_hash = source["hash"]
    target_hash = destination.get("hash")
    if target_hash and target_hash != source_hash:
        return quarantine_conflict(source, destination, reason="HASH_DIVERGENCE")
    payload = {field: deepcopy(source[field]) for field in sorted(AUTHORIZED_CITAT_FIELDS) if field in source}
    return {
        "status": "READY_FOR_REVIEW",
        "action": "PROPOSE_CITAT_ONLY",
        "payload": payload,
        "source_hash": source_hash,
        "destination_hash": target_hash,
        "rollback": "restore_previous_citat_version",
    }


def quarantine_conflict(source: Mapping[str, Any], destination: Mapping[str, Any], *, reason: str) -> dict[str, Any]:
    """Produz apenas o envelope do conflito; o conteúdo não é movido nem apagado."""

    return {
        "status": "QUARANTINED_CONFLICT",
        "reason": reason,
        "source_ref": source.get("source_ref"),
        "destination_ref": destination.get("source_ref") or destination.get("document_id"),
        "source_hash": source.get("hash"),
        "destination_hash": destination.get("hash"),
        "entered_at": _utc_now(),
        "rollback_ref": f"citat:{source.get('document_id')}:{source.get('version')}",
        "content_action": "NO_MOVE_NO_DELETE",
    }


def audit_houses(records: list[Mapping[str, Any]], *, checked_at: str | None = None) -> dict[str, Any]:
    """Auditoria mensal idempotente: alertas, lacunas e hashes, sem efeitos externos."""

    checked_at = checked_at or _utc_now()
    entries: list[dict[str, Any]] = []
    for record in sorted(records, key=lambda item: str(item.get("member_id", ""))):
        issues: list[str] = []
        for field in ("casa_lar", "casa_trabalho", "citat"):
            if not record.get(field):
                issues.append(f"{field.upper()}_MISSING")
        citat = record.get("citat", {})
        if citat and (not citat.get("version") or not citat.get("hash")):
            issues.append("CITAT_VERSION_OR_HASH_MISSING")
        entries.append({
            "member_id": record.get("member_id"),
            "status": "ALERT" if issues else "OK",
            "issues": issues,
            "record_sha256": sha256_json(record),
        })
    report = {
        "audit": "MONTHLY_HOUSE_CITAT_AUDIT_V1",
        "checked_at": checked_at,
        "mode": "READ_ONLY",
        "external_effect": False,
        "entries": entries,
    }
    report["report_sha256"] = sha256_json(report)
    return report


def automation_report(*, responsible: str, purpose: str, access: str, risks: list[str], last_execution: str | None = None) -> dict[str, Any]:
    """Metadado operacional para ser colocado em cada Casa sem conteúdo privado."""

    return {
        "automation_id": "HOUSE_CITAT_AUDIT_V1",
        "state": "SANDBOX_READY_FOR_REVIEW",
        "purpose": purpose,
        "access": access,
        "risks": list(risks),
        "last_execution": last_execution,
        "responsible": responsible,
        "external_effect": False,
        "rollback": "revert_versioned_change",
    }
