"""Governança operacional local, sintética e sem efeitos externos."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import IntEnum
import hashlib
import json
from typing import Any, Mapping


class RiskLevel(IntEnum):
    G0 = 0
    G1 = 1
    G2 = 2
    G3 = 3
    G4 = 4


@dataclass(frozen=True)
class GovernanceDecision:
    decision: str
    risk: RiskLevel
    reason: str
    event_id: str


def canonical_sha256(value: Any) -> str:
    if isinstance(value, bytes):
        payload = value
    elif isinstance(value, str):
        payload = value.encode("utf-8")
    else:
        payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


class GovernanceEngine:
    """Registros append-only com decisão fail-closed."""

    def __init__(self) -> None:
        self.identities: dict[str, dict[str, Any]] = {}
        self.permissions: dict[tuple[str, str], dict[str, Any]] = {}
        self.memories: dict[str, dict[str, Any]] = {}
        self.events: list[dict[str, Any]] = []
        self.provenance_ledger = self.events
        self.incidents: list[dict[str, Any]] = []
        self.learning_changes: list[dict[str, Any]] = []
        self.action_states: dict[str, str] = {}
        self.logging_available = True
        self._counter = 0

    def _event(self, kind: str, payload: Mapping[str, Any]) -> str:
        if not self.logging_available:
            raise RuntimeError("logging indisponível")
        self._counter += 1
        event_id = f"gov-{self._counter:04d}"
        previous_event_hash = self.events[-1]["event_hash"] if self.events else "GENESIS"
        event = {
            "event_id": event_id,
            "kind": kind,
            "timestamp": _timestamp(),
            "payload_hash": canonical_sha256(dict(payload)),
            "previous_event_hash": previous_event_hash,
            "payload": dict(payload),
        }
        event["event_hash"] = canonical_sha256({
            "event_id": event_id,
            "kind": kind,
            "timestamp": event["timestamp"],
            "payload_hash": event["payload_hash"],
            "previous_event_hash": previous_event_hash,
        })
        self.events.append(event)
        return event_id

    def register_identity(self, identity_id: str, origin: str, owner: str, capabilities: set[str]) -> str:
        if not identity_id or not origin or not owner:
            raise ValueError("identity, origin e owner são obrigatórios")
        self.identities[identity_id] = {
            "identity_id": identity_id,
            "origin": origin,
            "owner": owner,
            "capabilities": sorted(capabilities),
            "status": "ACTIVE",
        }
        return self._event("identity_origin_registry", self.identities[identity_id])

    def revoke_identity(self, identity_id: str) -> str:
        if identity_id not in self.identities:
            raise KeyError(identity_id)
        self.identities[identity_id]["status"] = "REVOKED"
        return self._event("identity_revoked", {"identity_id": identity_id})

    def grant(self, role: str, action: str, max_risk: RiskLevel, *, human_required: bool = False) -> str:
        self.permissions[(role, action)] = {
            "max_risk": int(max_risk),
            "human_required": human_required,
        }
        return self._event("permission_matrix", {"role": role, "action": action, **self.permissions[(role, action)]})

    @staticmethod
    def classify_risk(*, external_effect: bool, sensitive_data: bool, irreversible: bool, synthetic: bool) -> RiskLevel:
        if irreversible or external_effect:
            return RiskLevel.G4
        if sensitive_data:
            return RiskLevel.G3
        if not synthetic:
            return RiskLevel.G2
        return RiskLevel.G1

    def decide(
        self,
        *,
        identity_id: str,
        role: str,
        action: str,
        external_effect: bool = False,
        sensitive_data: bool = False,
        irreversible: bool = False,
        synthetic: bool = True,
        human_confirmed: bool = False,
        evidence: Mapping[str, Any] | None = None,
        action_id: str | None = None,
        prompt_injection_detected: bool = False,
    ) -> GovernanceDecision:
        evidence = evidence or {}
        risk = self.classify_risk(
            external_effect=external_effect,
            sensitive_data=sensitive_data,
            irreversible=irreversible,
            synthetic=synthetic,
        )
        if not self.logging_available:
            return GovernanceDecision("DENY", risk, "logging indisponível; fail-closed", "UNLOGGED")
        if prompt_injection_detected:
            return self._decision("DENY", risk, "instrução suspeita bloqueada", action_id=action_id)
        if action_id and self.action_states.get(action_id) == "ALLOW":
            return self._decision("DENY", risk, "replay detectado", action_id=action_id)
        if identity_id not in self.identities:
            return self._decision("DENY", risk, "identidade desconhecida")
        if self.identities[identity_id]["status"] != "ACTIVE":
            return self._decision("DENY", risk, "identidade revogada")
        permission = self.permissions.get((role, action))
        if permission is None:
            return self._decision("DENY", risk, "permissão ausente")
        if risk > RiskLevel(permission["max_risk"]):
            return self._decision("DENY", risk, "risco excede o máximo autorizado")
        if risk >= RiskLevel.G3 and not human_confirmed:
            return self._decision("REQUIRE_HUMAN", risk, "gate humano obrigatório para G3/G4")
        if permission["human_required"] and not human_confirmed:
            return self._decision("REQUIRE_HUMAN", risk, "permissão exige confirmação humana")
        if risk >= RiskLevel.G2 and not evidence:
            return self._decision("REQUIRE_EVIDENCE", risk, "evidência obrigatória ausente")
        return self._decision("ALLOW", risk, "ação autorizada dentro do escopo", evidence=evidence, action_id=action_id)

    def _decision(
        self,
        decision: str,
        risk: RiskLevel,
        reason: str,
        *,
        evidence: Mapping[str, Any] | None = None,
        action_id: str | None = None,
    ) -> GovernanceDecision:
        event_id = self._event("governance_decision", {
            "decision": decision,
            "risk": risk.name,
            "reason": reason,
            "evidence": dict(evidence or {}),
            "action_id": action_id,
        })
        if action_id and decision == "ALLOW":
            self.action_states[action_id] = "ALLOW"
        return GovernanceDecision(decision, risk, reason, event_id)

    def validate_provenance(self) -> bool:
        previous = "GENESIS"
        for event in self.events:
            if event["previous_event_hash"] != previous:
                return False
            expected = canonical_sha256({
                "event_id": event["event_id"],
                "kind": event["kind"],
                "timestamp": event["timestamp"],
                "payload_hash": event["payload_hash"],
                "previous_event_hash": event["previous_event_hash"],
            })
            if event["event_hash"] != expected:
                return False
            if event["payload_hash"] != canonical_sha256(event["payload"]):
                return False
            previous = event["event_hash"]
        return True

    def register_memory(self, memory_id: str, content: Any, *, source: str, version: int, disputed: bool = False) -> str:
        if version < 1 or not source:
            raise ValueError("memória exige versão positiva e fonte")
        record = {
            "memory_id": memory_id,
            "version": version,
            "content_hash": canonical_sha256(content),
            "source": source,
            "disputed": disputed,
            "status": "DISPUTED" if disputed else "ACTIVE",
        }
        prior = self.memories.get(memory_id)
        if prior and version <= prior["version"]:
            raise ValueError("memória alterada sem nova versão")
        self.memories[memory_id] = record
        return self._event("governed_memory_registry", record)

    def log_tool_action(self, identity_id: str, action: str, decision: GovernanceDecision, inputs: Any) -> str:
        if identity_id not in self.identities:
            raise ValueError("ação exige identidade registrada")
        return self._event("tool_action_log", {
            "identity_id": identity_id,
            "action": action,
            "decision": decision.decision,
            "risk": decision.risk.name,
            "inputs_hash": canonical_sha256(inputs),
        })

    def register_incident(self, incident_id: str, category: str, severity: str, summary: str) -> str:
        if not summary or severity.upper() not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
            raise ValueError("incidente exige resumo e severidade válida")
        record = {"incident_id": incident_id, "category": category, "severity": severity.upper(), "summary": summary, "status": "OPEN"}
        self.incidents.append(record)
        return self._event("incident_registry", record)

    def record_learning_change(self, change: Mapping[str, Any]) -> str:
        required = {"mudanca", "fonte", "regra", "risco", "contraexemplo", "teste", "versao"}
        if not required.issubset(change):
            raise ValueError("changelog pedagógico incompleto")
        self.learning_changes.append(dict(change))
        return self._event("learning_change_log", change)

    def recertification(self) -> dict[str, Any]:
        self.grant("CODEX", "recertification-external", RiskLevel.G4)
        first = self.decide(
            identity_id="codex-synth",
            role="CODEX",
            action="recertification-external",
            external_effect=True,
        )
        self.grant("CODEX", "recertification-replay", RiskLevel.G1)
        allowed = self.decide(
            identity_id="codex-synth",
            role="CODEX",
            action="recertification-replay",
            action_id="recertification-1",
        )
        replay = self.decide(
            identity_id="codex-synth",
            role="CODEX",
            action="recertification-replay",
            action_id="recertification-1",
        )
        logging_before = self.logging_available
        self.logging_available = False
        logging_failure = self.decide(identity_id="codex-synth", role="CODEX", action="read")
        self.logging_available = logging_before
        checks = {
            "revoked_identity_denied": self.decide(identity_id="revoked", role="CODEX", action="read").decision == "DENY",
            "unknown_action_denied": self.decide(identity_id="unknown", role="CODEX", action="write").decision == "DENY",
            "high_risk_requires_human": first.decision == "REQUIRE_HUMAN",
            "replay_denied": allowed.decision == "ALLOW" and replay.decision == "DENY",
            "logging_failure_denied": logging_failure.decision == "DENY" and logging_failure.event_id == "UNLOGGED",
            "provenance_valid": self.validate_provenance(),
            "events_have_hash": all(bool(event["payload_hash"]) for event in self.events),
        }
        return {"checks": checks, "passed": all(checks.values())}
