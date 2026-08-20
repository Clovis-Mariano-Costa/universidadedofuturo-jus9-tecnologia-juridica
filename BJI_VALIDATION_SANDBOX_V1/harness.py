#!/usr/bin/env python3
"""Registro reprodutível de rodadas BJI sem executar experimento real."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from UNIVERSIDADE_AUTOMACAO_SANDBOX_V1.core import append_provenance_event, scan_security, sha256_json


class BJIRegistry:
    """Mantém pré-registro, entradas e critérios; saídas permanecem vazias."""

    REQUIRED = (
        "experiment_id",
        "agent_version",
        "criteria",
        "inputs",
        "expected_output",
        "state",
    )

    def __init__(self) -> None:
        self.experiments: dict[str, dict[str, Any]] = {}
        self.rounds: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []

    def register(self, experiment: dict[str, Any]) -> dict[str, Any]:
        missing = [field for field in self.REQUIRED if field not in experiment]
        if missing:
            raise ValueError(f"experimento sem campos: {', '.join(missing)}")
        if experiment["state"] != "NAO_EXECUTADO":
            raise ValueError("pré-registro deve iniciar em NAO_EXECUTADO")
        if not experiment["criteria"]:
            raise ValueError("critério esperado deve ser definido antes da avaliação")
        if experiment.get("results") not in (None, [], {}):
            raise ValueError("resultado não pode ser pré-preenchido")
        if experiment.get("conclusion") not in (None, ""):
            raise ValueError("conclusão não pode ser pré-preenchida")
        if experiment["experiment_id"] in self.experiments:
            raise ValueError("experimento duplicado")
        scan = scan_security(experiment)
        if scan["finding_count"]:
            raise ValueError("experimento rejeitado por scanner de segurança")
        record = deepcopy(experiment)
        record.setdefault("results", [])
        record.setdefault("conclusion", None)
        record["input_sha256"] = sha256_json(record["inputs"])
        record["preregistration_sha256"] = sha256_json(record)
        self.experiments[record["experiment_id"]] = record
        append_provenance_event(self.events, "BJI_PREREGISTERED", {"experiment_id": record["experiment_id"], "state": record["state"]})
        return deepcopy(record)

    def register_round(self, experiment_id: str, round_id: str, inputs: Any, criteria: Any) -> dict[str, Any]:
        experiment = self.experiments.get(experiment_id)
        if experiment is None:
            return {"status": "BLOCKED", "reason": "EXPERIMENT_NOT_FOUND"}
        if experiment["state"] != "NAO_EXECUTADO":
            return {"status": "BLOCKED", "reason": "EXECUTION_STATE_ALREADY_CHANGED"}
        if not round_id or inputs in (None, [], {}):
            return {"status": "BLOCKED", "reason": "ROUND_INPUTS_REQUIRED"}
        if not criteria:
            return {"status": "BLOCKED", "reason": "ROUND_CRITERIA_REQUIRED"}
        scan = scan_security(inputs)
        if scan["finding_count"]:
            return {"status": "BLOCKED", "reason": "SENSITIVE_INPUT_OUT_OF_SCOPE", "scan": scan}
        record = {
            "experiment_id": experiment_id,
            "round_id": round_id,
            "input_sha256": sha256_json(inputs),
            "criteria_sha256": sha256_json(criteria),
            "state": "NAO_EXECUTADO",
            "output": None,
            "result": None,
        }
        self.rounds.append(record)
        append_provenance_event(self.events, "BJI_ROUND_REGISTERED", {"experiment_id": experiment_id, "round_id": round_id, "input_sha256": record["input_sha256"]})
        return {"status": "ROUND_REGISTERED", "record": deepcopy(record)}

    def reproducibility_report(self, experiment_id: str) -> dict[str, Any]:
        experiment = self.experiments.get(experiment_id)
        if experiment is None:
            return {"status": "BLOCKED", "reason": "EXPERIMENT_NOT_FOUND"}
        rounds = [round_record for round_record in self.rounds if round_record["experiment_id"] == experiment_id]
        return {
            "status": "REPORT_READY",
            "experiment_id": experiment_id,
            "state": experiment["state"],
            "agent_version": experiment["agent_version"],
            "criteria": deepcopy(experiment["criteria"]),
            "input_sha256": experiment["input_sha256"],
            "rounds": deepcopy(rounds),
            "results": [],
            "conclusion": None,
            "reproducible_metadata_sha256": sha256_json({"experiment": experiment, "rounds": rounds}),
        }
