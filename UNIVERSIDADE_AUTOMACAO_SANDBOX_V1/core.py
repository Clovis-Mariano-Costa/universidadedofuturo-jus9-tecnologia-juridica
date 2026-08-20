#!/usr/bin/env python3
"""Núcleo offline e fail-closed da automação da Universidade do Futuro.

O módulo usa somente estruturas em memória e dados fornecidos pelo chamador.
Não acessa rede, Drive, GitHub, credenciais, normas reais ou serviços externos.
"""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any


RESEARCH_STATES = {
    "SEMENTE",
    "EM_PESQUISA",
    "AGUARDA_FONTE",
    "EM_REVISAO",
    "CANONICA",
    "SUPERADA_COM_RASTRO",
}

RESEARCH_WORKFLOW_STAGES = (
    "QUESTION",
    "SOURCES",
    "HYPOTHESIS_OBJECTIVE",
    "RISK",
    "METHOD",
    "PREREGISTRATION",
    "HASHED",
    "EXECUTION",
    "RESULTS",
    "BOARD_REVIEW",
    "PUBLICATION",
    "TEACHING",
    "EXTENSION",
)

EXTENSION_WORKFLOW_STAGES = (
    "NEED",
    "RECIPIENT",
    "RISK",
    "INTERVENTION",
    "EVIDENCE",
    "IMPACT",
    "FEEDBACK",
    "TEACHING",
)

SECRET_MARKERS = (
    "api_key",
    "access_token",
    "password",
    "private_key",
    "secret",
    "sk-",
    "token=",
)

_SECRET_PATTERNS = {
    "PRIVATE_KEY_MATERIAL": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "BEARER_TOKEN": re.compile(r"\bbearer\s+[A-Za-z0-9._~-]{12,}\b", re.IGNORECASE),
    "API_KEY_ASSIGNMENT": re.compile(r"\b(?:api[_-]?key|access[_-]?token)\s*[:=]\s*['\"]?[A-Za-z0-9._~-]{12,}", re.IGNORECASE),
}

_PII_PATTERNS = {
    "EMAIL_ADDRESS": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "CPF_LIKE": re.compile(r"\b\d{3}[.\s]?\d{3}[.\s]?\d{3}[-\s]?\d{2}\b"),
    "PHONE_LIKE": re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2}\)?[\s-]?)?9?\d{4}[\s-]?\d{4}\b"),
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _contains_secret(value: Any) -> bool:
    serialized = canonical_bytes(value).lower().decode("utf-8", errors="ignore")
    return any(marker in serialized for marker in SECRET_MARKERS)


def scan_security(value: Any) -> dict[str, Any]:
    """Varre segredo/PII sem devolver o conteúdo encontrado."""

    serialized = canonical_bytes(value).decode("utf-8", errors="ignore")
    secret_findings = [code for code, pattern in _SECRET_PATTERNS.items() if pattern.search(serialized)]
    pii_findings = [code for code, pattern in _PII_PATTERNS.items() if pattern.search(serialized)]
    findings = secret_findings + pii_findings
    return {
        "status": "BLOCKED" if findings else "APTO_NO_ESCOPO",
        "secret_findings": secret_findings,
        "pii_findings": pii_findings,
        "finding_count": len(findings),
        "payload_sha256": sha256_json(value),
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hashed_record(record: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(record)
    result["hash"] = {
        "algorithm": "SHA-256",
        "value": sha256_json({k: v for k, v in result.items() if k != "hash"}),
    }
    return result


def append_provenance_event(
    events: list[dict[str, Any]], event_type: str, payload: dict[str, Any]
) -> dict[str, Any]:
    """Adiciona evento append-only com hash encadeado; nunca reescreve eventos."""

    envelope = {
        "event_id": f"EV-{len(events) + 1:04d}",
        "event_type": event_type,
        "timestamp": _now(),
        "payload": deepcopy(payload),
        "previous_hash": events[-1]["event_hash"] if events else None,
    }
    envelope["event_hash"] = sha256_json(envelope)
    events.append(envelope)
    return deepcopy(envelope)


class NormativeRegistry:
    """Registro versionado com proteção explícita para normas protegidas."""

    REQUIRED = (
        "norm_id",
        "kind",
        "version",
        "status",
        "authority",
        "parent_norm",
        "protected",
        "supersedes",
        "created_at",
        "effective_at",
        "review_at",
    )

    def __init__(self, norms: list[dict[str, Any]] | None = None) -> None:
        self.norms: dict[str, dict[str, Any]] = {}
        self.events: list[dict[str, Any]] = []
        for norm in norms or []:
            self.register(norm)

    def register(self, norm: dict[str, Any]) -> dict[str, Any]:
        missing = [field for field in self.REQUIRED if field not in norm]
        if missing:
            raise ValueError(f"norma sem campos: {', '.join(missing)}")
        if not isinstance(norm["protected"], bool):
            raise ValueError("protected deve ser booleano")
        norm_id = norm["norm_id"]
        if norm_id in self.norms:
            raise ValueError(f"versão/identificador duplicado: {norm_id}")
        if _contains_secret(norm):
            raise ValueError("norma rejeitada: marcador de segredo detectado")
        record = _hashed_record(norm)
        self.norms[norm_id] = record
        append_provenance_event(self.events, "NORM_REGISTERED", {"norm_id": norm_id})
        return deepcopy(record)

    def propose_update(
        self,
        norm_id: str,
        candidate: dict[str, Any],
        *,
        human_gate: bool = False,
        constitutional_flow: bool = False,
    ) -> dict[str, Any]:
        current = self.norms.get(norm_id)
        if current is None:
            return {"status": "BLOCKED", "reason": "NORM_NOT_FOUND"}
        if current["protected"] and not (human_gate and constitutional_flow):
            return {"status": "BLOCKED", "reason": "PROTECTED_READ_ONLY_BY_DEFAULT"}
        if not human_gate:
            return {"status": "BLOCKED", "reason": "HUMAN_GATE_REQUIRED"}
        if candidate.get("norm_id") in self.norms:
            return {"status": "BLOCKED", "reason": "DUPLICATE_VERSION"}
        if candidate.get("supersedes") != norm_id:
            return {"status": "BLOCKED", "reason": "MISSING_GENEALOGY"}
        merged = deepcopy(candidate)
        merged["parent_norm"] = candidate.get("parent_norm", current["parent_norm"])
        merged["protected"] = bool(candidate.get("protected", current["protected"]))
        record = self.register(merged)
        append_provenance_event(
            self.events,
            "NORM_VERSIONED_UPDATE",
            {"previous": norm_id, "current": record["norm_id"]},
        )
        return {"status": "VERSIONED", "record": record}

    def resolve_precedence(self, norm_ids: list[str]) -> dict[str, Any]:
        """Aplica a regra G6 sem inventar autoridade externa."""

        candidates = [self.norms.get(norm_id) for norm_id in norm_ids]
        if not norm_ids or any(candidate is None for candidate in candidates):
            return {"status": "BLOCKED", "reason": "NORM_NOT_FOUND"}
        ranked = []
        for candidate in candidates:
            assert candidate is not None
            ranked.append(
                (
                    int(candidate.get("competence_rank", 0)),
                    int(candidate.get("hierarchy_rank", 0)),
                    int(candidate.get("specialty_rank", 0)),
                    str(candidate.get("effective_at", "")),
                    str(candidate.get("created_at", "")),
                    str(candidate["norm_id"]),
                    candidate,
                )
            )
        ranked.sort(reverse=True)
        winner = ranked[0][-1]
        if len(ranked) > 1 and ranked[0][:5] == ranked[1][:5]:
            return {"status": "BLOCKED", "reason": "G6_TIE_REQUIRES_HUMAN_REVIEW"}
        return {
            "status": "RESOLVED_INTERNAL",
            "norm_id": winner["norm_id"],
            "rule": "COMPETENCE>HIERARCHY>SPECIALTY>VIGENCY>LEX_POSTERIOR",
        }


class ResearchRegistry:
    """Registry mínimo de pesquisa/extensão com estado e hash."""

    REQUIRED = (
        "project_id",
        "faculty",
        "problem",
        "hypothesis",
        "sources",
        "ethics",
        "data",
        "preregistration",
        "execution",
        "evidence",
        "negative_results",
        "extension",
        "impact",
        "feedback",
        "state",
    )

    def __init__(self) -> None:
        self.projects: dict[str, dict[str, Any]] = {}
        self.events: list[dict[str, Any]] = []

    def register(self, project: dict[str, Any]) -> dict[str, Any]:
        missing = [field for field in self.REQUIRED if field not in project]
        if missing:
            raise ValueError(f"projeto sem campos: {', '.join(missing)}")
        if project["state"] not in RESEARCH_STATES:
            raise ValueError("estado de pesquisa inválido")
        if project["project_id"] in self.projects:
            raise ValueError("projeto duplicado")
        if _contains_secret(project):
            raise ValueError("projeto rejeitado: marcador de segredo detectado")
        record_input = deepcopy(project)
        record_input.setdefault("workflow_stage", "QUESTION")
        if record_input["workflow_stage"] not in RESEARCH_WORKFLOW_STAGES:
            raise ValueError("etapa de workflow de pesquisa inválida")
        record = _hashed_record(record_input)
        self.projects[project["project_id"]] = record
        append_provenance_event(
            self.events, "RESEARCH_REGISTERED", {"project_id": project["project_id"]}
        )
        return deepcopy(record)

    def advance(
        self,
        project_id: str,
        target_stage: str,
        *,
        human_gate: bool = False,
        evidence: Any | None = None,
    ) -> dict[str, Any]:
        project = self.projects.get(project_id)
        if project is None:
            return {"status": "BLOCKED", "reason": "PROJECT_NOT_FOUND"}
        if target_stage not in RESEARCH_WORKFLOW_STAGES:
            return {"status": "BLOCKED", "reason": "INVALID_WORKFLOW_STAGE"}
        current_index = RESEARCH_WORKFLOW_STAGES.index(project["workflow_stage"])
        target_index = RESEARCH_WORKFLOW_STAGES.index(target_stage)
        if target_index != current_index + 1:
            return {"status": "BLOCKED", "reason": "NON_SEQUENTIAL_TRANSITION"}
        if target_stage == "SOURCES" and not project.get("sources"):
            return {"status": "BLOCKED", "reason": "SOURCES_REQUIRED"}
        if target_stage == "METHOD" and not project.get("method"):
            return {"status": "BLOCKED", "reason": "METHOD_REQUIRED"}
        if target_stage == "PREREGISTRATION" and str(project.get("preregistration", "")).upper() in {"", "PENDING"}:
            return {"status": "BLOCKED", "reason": "PREREGISTRATION_REQUIRED"}
        if target_stage in {"HASHED", "EXECUTION"} and not project.get("hash"):
            return {"status": "BLOCKED", "reason": "PROJECT_HASH_REQUIRED"}
        if target_stage == "RESULTS" and not project.get("evidence") and evidence is None:
            return {"status": "BLOCKED", "reason": "RESULTS_EVIDENCE_REQUIRED"}
        if target_stage in {"BOARD_REVIEW", "PUBLICATION", "TEACHING", "EXTENSION"} and not human_gate:
            return {"status": "BLOCKED", "reason": "HUMAN_GATE_REQUIRED"}
        if evidence is not None:
            project["workflow_evidence"] = deepcopy(evidence)
        project["workflow_stage"] = target_stage
        project["hash"] = _hashed_record({k: v for k, v in project.items() if k != "hash"})["hash"]
        append_provenance_event(
            self.events,
            "RESEARCH_WORKFLOW_ADVANCED",
            {"project_id": project_id, "target_stage": target_stage, "human_gate": human_gate},
        )
        return {"status": "ADVANCED", "record": deepcopy(project)}


class ExtensionRegistry:
    """Workflow de extensão separado do resultado acadêmico."""

    REQUIRED = ("extension_id", "need", "recipient", "risk", "intervention", "evidence", "impact", "feedback")

    def __init__(self) -> None:
        self.projects: dict[str, dict[str, Any]] = {}
        self.events: list[dict[str, Any]] = []

    def register(self, project: dict[str, Any]) -> dict[str, Any]:
        missing = [field for field in self.REQUIRED if field not in project]
        if missing:
            raise ValueError(f"extensão sem campos: {', '.join(missing)}")
        if project["extension_id"] in self.projects:
            raise ValueError("extensão duplicada")
        if _contains_secret(project):
            raise ValueError("extensão rejeitada: marcador de segredo detectado")
        record_input = deepcopy(project)
        record_input.setdefault("workflow_stage", "NEED")
        if record_input["workflow_stage"] not in EXTENSION_WORKFLOW_STAGES:
            raise ValueError("etapa de workflow de extensão inválida")
        record = _hashed_record(record_input)
        self.projects[project["extension_id"]] = record
        append_provenance_event(self.events, "EXTENSION_REGISTERED", {"extension_id": project["extension_id"]})
        return deepcopy(record)

    def advance(self, extension_id: str, target_stage: str, *, human_gate: bool = False) -> dict[str, Any]:
        project = self.projects.get(extension_id)
        if project is None:
            return {"status": "BLOCKED", "reason": "EXTENSION_NOT_FOUND"}
        if target_stage not in EXTENSION_WORKFLOW_STAGES:
            return {"status": "BLOCKED", "reason": "INVALID_WORKFLOW_STAGE"}
        current_index = EXTENSION_WORKFLOW_STAGES.index(project["workflow_stage"])
        target_index = EXTENSION_WORKFLOW_STAGES.index(target_stage)
        if target_index != current_index + 1:
            return {"status": "BLOCKED", "reason": "NON_SEQUENTIAL_TRANSITION"}
        value_by_stage = {
            "RECIPIENT": "recipient",
            "RISK": "risk",
            "INTERVENTION": "intervention",
            "EVIDENCE": "evidence",
            "IMPACT": "impact",
            "FEEDBACK": "feedback",
        }
        required_field = value_by_stage.get(target_stage)
        if required_field and not project.get(required_field):
            return {"status": "BLOCKED", "reason": f"{required_field.upper()}_REQUIRED"}
        if target_stage in {"EVIDENCE", "IMPACT", "FEEDBACK", "TEACHING"} and not human_gate:
            return {"status": "BLOCKED", "reason": "HUMAN_GATE_REQUIRED"}
        project["workflow_stage"] = target_stage
        project["hash"] = _hashed_record({k: v for k, v in project.items() if k != "hash"})["hash"]
        append_provenance_event(self.events, "EXTENSION_WORKFLOW_ADVANCED", {"extension_id": extension_id, "target_stage": target_stage})
        return {"status": "ADVANCED", "record": deepcopy(project)}


class AdjudicationSandbox:
    """Adjudicação interna experimental; não cria jurisdição nem efeito externo."""

    REQUIRED = (
        "case_id",
        "judge_ai",
        "model_version",
        "parties",
        "jurisdiction_label",
        "evidence_hash",
        "conflict_check",
        "review",
        "rollback_ref",
    )

    def __init__(self) -> None:
        self.cases: dict[str, dict[str, Any]] = {}
        self.events: list[dict[str, Any]] = []

    def open_case(self, case: dict[str, Any]) -> dict[str, Any]:
        missing = [field for field in self.REQUIRED if field not in case]
        if missing:
            return {"status": "BLOCKED", "reason": f"MISSING_FIELDS:{','.join(missing)}"}
        if case["jurisdiction_label"] != "INTERNAL_EXPERIMENTAL":
            return {"status": "BLOCKED", "reason": "EXTERNAL_JURISDICTION_FORBIDDEN"}
        if not isinstance(case["parties"], list) or not case["parties"]:
            return {"status": "BLOCKED", "reason": "PARTIES_REQUIRED"}
        if _contains_secret(case):
            return {"status": "BLOCKED", "reason": "SECRET_MARKER_DETECTED"}
        if case["case_id"] in self.cases:
            return {"status": "BLOCKED", "reason": "DUPLICATE_CASE"}
        case_input = deepcopy(case)
        case_input.setdefault("submissions", [])
        case_input.setdefault("votes", [])
        case_input.setdefault("appeals", [])
        record = _hashed_record(case_input)
        self.cases[case["case_id"]] = record
        append_provenance_event(self.events, "CASE_OPENED", {"case_id": case["case_id"]})
        return {"status": "OPENED", "record": deepcopy(record)}

    def submit_statement(self, case_id: str, party: str, statement_hash: str) -> dict[str, Any]:
        case = self.cases.get(case_id)
        if case is None:
            return {"status": "BLOCKED", "reason": "CASE_NOT_FOUND"}
        if party not in case["parties"]:
            return {"status": "BLOCKED", "reason": "PARTY_NOT_REGISTERED"}
        if not statement_hash:
            return {"status": "BLOCKED", "reason": "STATEMENT_HASH_REQUIRED"}
        submission = {"party": party, "statement_hash": statement_hash}
        case["submissions"].append(submission)
        append_provenance_event(self.events, "CONTRADICTORY_SUBMISSION_RECORDED", {"case_id": case_id, "party": party, "statement_hash": statement_hash})
        return {"status": "SUBMISSION_RECORDED", "record": deepcopy(submission)}

    def record_vote(self, case_id: str, voter_id: str, vote: str, reasoning: str) -> dict[str, Any]:
        case = self.cases.get(case_id)
        if case is None:
            return {"status": "BLOCKED", "reason": "CASE_NOT_FOUND"}
        if vote not in {"AFFIRM", "REJECT", "ABSTAIN"}:
            return {"status": "BLOCKED", "reason": "INVALID_VOTE"}
        if not reasoning:
            return {"status": "BLOCKED", "reason": "VOTE_REASONING_REQUIRED"}
        record = {"voter_id": voter_id, "vote": vote, "reasoning_hash": sha256_json(reasoning)}
        case["votes"].append(record)
        append_provenance_event(self.events, "INTERNAL_VOTE_RECORDED", {"case_id": case_id, **record})
        return {"status": "VOTE_RECORDED", "record": deepcopy(record)}

    def decide(
        self,
        case_id: str,
        decision: str,
        *,
        human_gate: bool,
        review: str,
        reasoning: str = "",
        external_effect: bool = False,
    ) -> dict[str, Any]:
        case = self.cases.get(case_id)
        if case is None:
            return {"status": "BLOCKED", "reason": "CASE_NOT_FOUND"}
        if case["jurisdiction_label"] != "INTERNAL_EXPERIMENTAL":
            return {"status": "BLOCKED", "reason": "EXTERNAL_JURISDICTION_FORBIDDEN"}
        if not case["evidence_hash"]:
            return {"status": "BLOCKED", "reason": "EVIDENCE_HASH_REQUIRED"}
        if case["conflict_check"] != "CLEAR":
            return {"status": "BLOCKED", "reason": "CONFLICT_OR_IMPEDIMENT"}
        if not human_gate:
            return {"status": "BLOCKED", "reason": "HUMAN_GATE_REQUIRED"}
        submitted_parties = {submission["party"] for submission in case["submissions"]}
        if not set(case["parties"]).issubset(submitted_parties):
            return {"status": "BLOCKED", "reason": "CONTRADICTORY_SUBMISSIONS_REQUIRED"}
        if not case["votes"]:
            return {"status": "BLOCKED", "reason": "INTERNAL_VOTE_REQUIRED"}
        if not reasoning:
            return {"status": "BLOCKED", "reason": "DECISION_REASONING_REQUIRED"}
        if external_effect:
            return {"status": "BLOCKED", "reason": "EXTERNAL_EFFECT_FORBIDDEN"}
        if not review:
            return {"status": "BLOCKED", "reason": "REVIEW_REQUIRED"}
        result = {
            "case_id": case_id,
            "decision": decision,
            "review": review,
            "reasoning_hash": sha256_json(reasoning),
            "votes": deepcopy(case["votes"]),
            "jurisdiction_label": "INTERNAL_EXPERIMENTAL",
            "human_gate": True,
            "rollback_ref": case["rollback_ref"],
        }
        append_provenance_event(self.events, "INTERNAL_DECISION_RECORDED", result)
        return {"status": "DECISION_RECORDED_INTERNAL", "record": result}

    def request_appeal(self, case_id: str, appellant: str, grounds: str) -> dict[str, Any]:
        case = self.cases.get(case_id)
        if case is None:
            return {"status": "BLOCKED", "reason": "CASE_NOT_FOUND"}
        if not appellant or not grounds:
            return {"status": "BLOCKED", "reason": "APPEAL_GROUNDS_REQUIRED"}
        appeal = {"appellant": appellant, "grounds_hash": sha256_json(grounds), "status": "PENDING_INTERNAL_REVIEW"}
        case["appeals"].append(appeal)
        append_provenance_event(self.events, "INTERNAL_APPEAL_REQUESTED", {"case_id": case_id, **appeal})
        return {"status": "APPEAL_REQUESTED", "record": deepcopy(appeal)}

    def rollback(self, case_id: str, rollback_ref: str) -> dict[str, Any]:
        if case_id not in self.cases:
            return {"status": "BLOCKED", "reason": "CASE_NOT_FOUND"}
        event = append_provenance_event(
            self.events,
            "ROLLBACK_RECORDED",
            {"case_id": case_id, "rollback_ref": rollback_ref},
        )
        return {"status": "ROLLBACK_RECORDED", "event": event}


class SecurityGate:
    """Scanner e gate de cibersegurança para o escopo sintético."""

    def __init__(self, allowed_scopes: set[str] | None = None) -> None:
        self.allowed_scopes = set(allowed_scopes or {"UNIVERSITY_SANDBOX"})
        self.events: list[dict[str, Any]] = []
        self.incidents: list[dict[str, Any]] = []

    def open_incident(self, code: str, severity: str, payload: Any) -> dict[str, Any]:
        incident = {
            "incident_id": f"INC-{len(self.incidents) + 1:04d}",
            "code": code,
            "severity": severity,
            "payload_sha256": sha256_json(payload),
            "status": "OPEN",
        }
        self.incidents.append(incident)
        append_provenance_event(self.events, "SECURITY_INCIDENT_OPENED", incident)
        return deepcopy(incident)

    def evaluate(
        self,
        payload: Any,
        *,
        actor_scope: str,
        required_scope: str,
        tenant: str = "SYNTHETIC_UNIVERSITY",
        expected_tenant: str = "SYNTHETIC_UNIVERSITY",
        data_classification: str = "SYNTHETIC_ONLY",
        external_effect: bool = False,
        human_gate: bool = False,
    ) -> dict[str, Any]:
        scan = scan_security(payload)
        reasons: list[str] = []
        if scan["finding_count"]:
            reasons.append("SENSITIVE_FINDING_DETECTED")
            self.open_incident("SENSITIVE_FINDING_DETECTED", "HIGH", {"scan": scan})
        if actor_scope not in self.allowed_scopes or actor_scope != required_scope:
            reasons.append("LEAST_PRIVILEGE_SCOPE_MISMATCH")
        if tenant != expected_tenant:
            reasons.append("TENANT_SEGREGATION_FAILED")
        if data_classification != "SYNTHETIC_ONLY":
            reasons.append("NON_SYNTHETIC_DATA_OUT_OF_SCOPE")
        if external_effect and not human_gate:
            reasons.append("EXTERNAL_EFFECT_HUMAN_GATE_REQUIRED")
        status = "APTO_NO_ESCOPO" if not reasons else "BLOCKED"
        result = {
            "status": status,
            "reasons": reasons,
            "scan": scan,
            "external_effect": False if status == "BLOCKED" else external_effect,
            "tenant": tenant,
            "data_classification": data_classification,
        }
        append_provenance_event(self.events, "SECURITY_SCOPE_EVALUATED", {"status": status, "reasons": reasons, "payload_sha256": scan["payload_sha256"]})
        return result

def quarantine_source(source: dict[str, Any]) -> dict[str, Any]:
    """Classifica fonte sem identificador verificável sem descartá-la."""

    if not source.get("source_id") or not source.get("url"):
        return {"status": "QUARANTINED/REVIEW_REQUIRED", "reason": "MISSING_VERIFIABLE_ID"}
    if _contains_secret(source):
        return {"status": "QUARANTINED/REVIEW_REQUIRED", "reason": "SECRET_MARKER_DETECTED"}
    return {"status": "READY_FOR_REVIEW", "source_id": source["source_id"]}


def lint_norms(norms: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Linter preventivo para conflitos e falsa autoridade normativa."""

    issues: list[dict[str, str]] = []
    ids = {norm.get("norm_id") for norm in norms}
    for norm in norms:
        norm_id = str(norm.get("norm_id", "<missing>"))
        if not norm.get("status"):
            issues.append({"code": "MISSING_STATUS", "norm_id": norm_id})
        if norm.get("protected") and not norm.get("hash"):
            issues.append({"code": "PROTECTED_WITHOUT_HASH", "norm_id": norm_id})
        for field in ("parent_norm", "supersedes"):
            reference = norm.get(field)
            if reference and reference not in ids:
                issues.append({"code": "BROKEN_REFERENCE", "norm_id": norm_id, "field": field})
        authority = str(norm.get("authority", "")).lower()
        if any(marker in authority for marker in ("mec", "poder judiciário", "estado", "court")):
            issues.append({"code": "FALSE_EXTERNAL_AUTHORITY", "norm_id": norm_id})
    return issues
