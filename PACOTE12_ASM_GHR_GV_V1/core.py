"""Núcleo verificável do Pacote 12 V2.

O módulo é deliberadamente local e sem efeitos transacionais: não publica,
move, apaga ou altera documentos externos. Ele valida estados, registra
genealogia/hash e bloqueia transições sem evidência suficiente.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
from typing import Any, Mapping
from zoneinfo import ZoneInfo

try:
    _SAO_PAULO = ZoneInfo("America/Sao_Paulo")
except Exception:  # pragma: no cover - depends on the host's tzdata package
    _SAO_PAULO = timezone(timedelta(hours=-3), name="America/Sao_Paulo")


ACADEMIC_STATES = tuple(
    f"M{i:02d}"
    for i in range(24)
)

_ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "M00": frozenset({"M01"}),
    "M01": frozenset({"M02", "M03"}),
    "M02": frozenset({"M03", "M04"}),
    "M03": frozenset({"M04"}),
    "M04": frozenset({"M05", "M06"}),
    "M05": frozenset({"M06"}),
    "M06": frozenset({"M07"}),
    "M07": frozenset({"M08"}),
    "M08": frozenset({"M09"}),
    "M09": frozenset({"M10"}),
    "M10": frozenset({"M11"}),
    "M11": frozenset({"M10", "M12"}),
    "M12": frozenset({"M13"}),
    "M13": frozenset({"M14"}),
    "M14": frozenset({"M15"}),
    "M15": frozenset({"M16", "M17"}),
    "M16": frozenset({"M17"}),
    "M17": frozenset({"M18"}),
    "M18": frozenset({"M19"}),
    "M19": frozenset({"M20"}),
    "M20": frozenset({"M21"}),
    "M21": frozenset({"M22"}),
    "M22": frozenset({"M23"}),
    # Revisão pós-publicação abre nova versão; não reescreve a versão publicada.
    "M23": frozenset({"M04"}),
}

_REQUIRED_EVIDENCE: dict[str, tuple[str, ...]] = {
    "M08": ("approval_evidence",),
    "M09": ("preregistration_evidence",),
    "M10": ("execution_protocol",),
    "M12": ("reproduction_evidence",),
    "M14": ("bank_evidence",),
    "M16": ("bank_approval_evidence", "bank_hashes_match"),
    "M17": ("correction_evidence",),
    "M18": ("homologation_evidence",),
    "M19": ("sanitization_evidence",),
    "M20": ("deposit_evidence",),
    "M21": ("publication_authorization",),
    "M22": ("publication_receipt",),
    "M23": ("post_publication_review",),
}


def format_timestamp(value: datetime | None = None) -> str:
    """Retorna timestamp local com cinco casas decimais de segundo."""

    instant = value or datetime.now(_SAO_PAULO)
    if instant.tzinfo is None:
        instant = instant.replace(tzinfo=_SAO_PAULO)
    offset = instant.strftime("%z")
    return instant.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-1] + offset[:3] + ":" + offset[3:]


def _json_default(value: Any) -> str:
    raise TypeError(f"valor não serializável: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode("utf-8")
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=_json_default,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def allowed_transitions(state: str) -> frozenset[str]:
    if state not in ACADEMIC_STATES:
        raise ValueError(f"estado acadêmico desconhecido: {state}")
    return _ALLOWED_TRANSITIONS.get(state, frozenset())


@dataclass(frozen=True)
class GateResult:
    allowed: bool
    code: str
    reason: str
    details: tuple[str, ...] = ()


def _blocked(code: str, reason: str, *details: str) -> GateResult:
    return GateResult(False, code, reason, tuple(details))


def _allowed(reason: str, *details: str) -> GateResult:
    return GateResult(True, "ALLOWED", reason, tuple(details))


def _is_present(value: Any) -> bool:
    return value is not None and value is not False and value != "" and value != []


def _validate_security(evidence: Mapping[str, Any]) -> GateResult:
    findings = evidence.get("security_findings", []) or []
    for finding in findings:
        severity = str(finding.get("severity", "")).upper() if isinstance(finding, Mapping) else ""
        accepted = bool(finding.get("human_acceptance")) if isinstance(finding, Mapping) else False
        if severity == "CRITICAL":
            return _blocked("SECURITY_CRITICAL_OPEN", "vulnerabilidade crítica aberta bloqueia o avanço")
        if severity == "HIGH" and not accepted:
            return _blocked("SECURITY_HIGH_UNACCEPTED", "vulnerabilidade alta sem aceitação humana específica")
    required_flags = ("tenant_isolation_tested", "authz_tested", "rollback_tested")
    for flag in required_flags:
        if flag in evidence and evidence[flag] is not True:
            return _blocked("SECURITY_FAIL_CLOSED", f"controle de segurança não comprovado: {flag}")
    return _allowed("controles de segurança presentes ou não exigidos neste caso")


def validate_transition(
    current_state: str,
    target_state: str,
    evidence: Mapping[str, Any] | None = None,
    *,
    actor_role: str | None = None,
) -> GateResult:
    """Valida ASM + GV com bloqueio fechado por padrão."""

    evidence = evidence or {}
    if current_state not in ACADEMIC_STATES or target_state not in ACADEMIC_STATES:
        return _blocked("UNKNOWN_STATE", "estado de origem ou destino não pertence a M00–M23")
    if evidence.get("force_terminal") is True:
        return _blocked("FORCED_TERMINAL", "não é permitido forçar estado terminal")
    if target_state not in allowed_transitions(current_state):
        return _blocked("TRANSITION_NOT_ALLOWED", f"transição {current_state} -> {target_state} não é permitida")
    if target_state == "M04" and current_state == "M23" and not _is_present(evidence.get("revision_reason")):
        return _blocked("REVISION_REASON_MISSING", "revisão pós-publicação exige justificativa registrada")
    if actor_role == "BIBLIOTECARIO_IA" and evidence.get("impediment"):
        return _blocked("ROLE_IMPEDIMENT", "impedimento registrado para o papel executor")
    for key in _REQUIRED_EVIDENCE.get(target_state, ()):
        if not _is_present(evidence.get(key)):
            return _blocked("EVIDENCE_MISSING", f"evidência obrigatória ausente: {key}")
    if target_state in {"M16", "M18", "M19", "M20", "M21", "M22", "M23"}:
        security = _validate_security(evidence)
        if not security.allowed:
            return security
    evaluator_hashes = evidence.get("evaluator_hashes")
    if evaluator_hashes is not None:
        hashes = list(evaluator_hashes)
        if len(hashes) < 2 or len(set(hashes)) != 1:
            return _blocked("HASH_DIVERGENCE", "hashes dos avaliadores não coincidem")
    if target_state in {"M20", "M21", "M22"} and not _is_present(evidence.get("same_version_hash")):
        return _blocked("VERSION_HASH_MISSING", "depósito/publicação exige versão e hash avaliados")
    return _allowed(f"transição {current_state} -> {target_state} validada em modo fail-closed")


def validate_change_version(
    previous_hash: str,
    current_hash: str,
    previous_version: int,
    current_version: int,
) -> GateResult:
    if current_hash != previous_hash and current_version <= previous_version:
        return _blocked("VERSION_REQUIRED", "alteração de conteúdo exige nova versão")
    if current_version < previous_version:
        return _blocked("VERSION_REGRESSION", "versão não pode retroceder")
    return _allowed("hash e versão são compatíveis")


class GenealogyHashRecord:
    """Registro append-only de hash, genealogia e eventos de proveniência."""

    @staticmethod
    def create(
        *,
        artifact_id: str,
        payload: Any,
        state: str,
        actor: str,
        origin: str,
        destination: str,
        classification: str = "INTERNAL_SYNTHETIC",
        version: int = 1,
        parent_id: str | None = None,
        parent_hash: str | None = None,
        event_result: str = "CREATED",
        rollback_ref: str | None = None,
    ) -> dict[str, Any]:
        if state not in ACADEMIC_STATES:
            raise ValueError(f"estado acadêmico desconhecido: {state}")
        if version > 1 and (not parent_id or not parent_hash):
            raise ValueError("versão posterior exige parent_id e parent_hash")
        content_hash = canonical_sha256(payload)
        event = {
            "event_id": f"{artifact_id}:v{version}:e1",
            "timestamp": format_timestamp(),
            "origin": origin,
            "rule": "GHR_CREATE",
            "transformation": "canonical_sha256",
            "destination": destination,
            "version": version,
            "hash": content_hash,
            "actor": actor,
            "result": event_result,
            "rollback": rollback_ref,
        }
        return {
            "artifact_id": artifact_id,
            "state": state,
            "version": version,
            "content_hash": content_hash,
            "parent_id": parent_id,
            "parent_hash": parent_hash,
            "classification": classification,
            "events": [event],
        }

    @staticmethod
    def evolve(
        previous: Mapping[str, Any],
        *,
        payload: Any,
        state: str,
        actor: str,
        origin: str,
        destination: str,
        rule: str,
        transformation: str,
        result: str = "UPDATED",
        rollback_ref: str | None = None,
    ) -> dict[str, Any]:
        next_version = int(previous["version"]) + 1
        current_hash = canonical_sha256(payload)
        version_check = validate_change_version(
            str(previous["content_hash"]), current_hash, int(previous["version"]), next_version
        )
        if not version_check.allowed:
            raise ValueError(version_check.reason)
        events = list(previous["events"])
        events.append(
            {
                "event_id": f"{previous['artifact_id']}:v{next_version}:e{len(events) + 1}",
                "timestamp": format_timestamp(),
                "origin": origin,
                "rule": rule,
                "transformation": transformation,
                "destination": destination,
                "version": next_version,
                "hash": current_hash,
                "actor": actor,
                "result": result,
                "rollback": rollback_ref,
            }
        )
        return {
            "artifact_id": previous["artifact_id"],
            "state": state,
            "version": next_version,
            "content_hash": current_hash,
            "parent_id": previous["artifact_id"],
            "parent_hash": previous["content_hash"],
            "classification": previous["classification"],
            "events": events,
        }

    @staticmethod
    def rollback(previous: Mapping[str, Any], *, actor: str, target_version: int, reason: str) -> dict[str, Any]:
        if target_version < 1 or target_version > int(previous["version"]):
            raise ValueError("versão alvo de rollback inexistente")
        payload = {
            "rollback_target_version": target_version,
            "reason": reason,
            "source_hash": previous["content_hash"],
        }
        return GenealogyHashRecord.evolve(
            previous,
            payload=payload,
            state=previous["state"],
            actor=actor,
            origin="rollback",
            destination="versioned_history",
            rule="GHR_ROLLBACK",
            transformation="append_rollback_event",
            result="ROLLBACK_APPLIED",
            rollback_ref=f"target_version:{target_version}",
        )
