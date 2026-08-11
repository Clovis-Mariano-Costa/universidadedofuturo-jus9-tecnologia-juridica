#!/usr/bin/env python3
"""Registro fail-closed de exercícios, respostas e reavaliações."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from UNIVERSIDADE_AUTOMACAO_SANDBOX_V1.core import append_provenance_event, sha256_json


RESULT_STATES = {
    "NAO_TESTADO",
    "TESTADO_INSUFICIENTE",
    "TESTADO_APROVADO",
    "PRECISA_REVISAO",
}


class LearningRegistry:
    REQUIRED = ("lesson_id", "source", "version", "exercise", "criteria")

    def __init__(self) -> None:
        self.lessons: dict[str, dict[str, Any]] = {}
        self.attempts: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []

    def register_lesson(self, lesson: dict[str, Any]) -> dict[str, Any]:
        missing = [field for field in self.REQUIRED if field not in lesson]
        if missing:
            raise ValueError(f"aula sem campos: {', '.join(missing)}")
        if not lesson["source"] or not lesson["version"] or not lesson["exercise"] or not lesson["criteria"]:
            raise ValueError("aula exige fonte, versão, exercício e critério")
        if lesson["lesson_id"] in self.lessons:
            raise ValueError("aula duplicada")
        record = deepcopy(lesson)
        record["source_sha256"] = sha256_json(lesson["source"])
        record["status"] = "ACTIVE"
        self.lessons[lesson["lesson_id"]] = record
        append_provenance_event(self.events, "LESSON_REGISTERED", {"lesson_id": lesson["lesson_id"], "version": lesson["version"]})
        return deepcopy(record)

    def submit_attempt(self, lesson_id: str, response: Any) -> dict[str, Any]:
        if lesson_id not in self.lessons:
            return {"status": "BLOCKED", "reason": "LESSON_NOT_FOUND"}
        attempt = {
            "attempt_id": f"ATT-{len(self.attempts) + 1:04d}",
            "lesson_id": lesson_id,
            "response": deepcopy(response),
            "response_sha256": sha256_json(response),
            "result": "NAO_TESTADO",
            "review": None,
        }
        self.attempts.append(attempt)
        append_provenance_event(self.events, "LEARNING_ATTEMPT_RECORDED", {"attempt_id": attempt["attempt_id"], "lesson_id": lesson_id, "response_sha256": attempt["response_sha256"]})
        return {"status": "ATTEMPT_RECORDED", "record": deepcopy(attempt)}

    def evaluate(
        self,
        attempt_id: str,
        *,
        result: str,
        review: str,
        human_review: bool = False,
        substantive: bool = False,
        literal_repetition: bool = False,
    ) -> dict[str, Any]:
        attempt = next((item for item in self.attempts if item["attempt_id"] == attempt_id), None)
        if attempt is None:
            return {"status": "BLOCKED", "reason": "ATTEMPT_NOT_FOUND"}
        if result not in RESULT_STATES - {"NAO_TESTADO"}:
            return {"status": "BLOCKED", "reason": "INVALID_RESULT_STATE"}
        if not review:
            return {"status": "BLOCKED", "reason": "REVIEW_REQUIRED"}
        if result == "TESTADO_APROVADO" and (not human_review or not substantive or literal_repetition):
            return {"status": "BLOCKED", "reason": "APPROVAL_REQUIRES_HUMAN_SUBSTANTIVE_REVIEW"}
        if not human_review and result in {"TESTADO_APROVADO", "PRECISA_REVISAO"}:
            return {"status": "BLOCKED", "reason": "HUMAN_REVIEW_REQUIRED"}
        attempt["result"] = result
        attempt["review"] = review
        attempt["human_review"] = human_review
        attempt["substantive"] = substantive
        attempt["literal_repetition"] = literal_repetition
        append_provenance_event(self.events, "LEARNING_ATTEMPT_EVALUATED", {"attempt_id": attempt_id, "result": result, "review": review})
        return {"status": "EVALUATED", "record": deepcopy(attempt)}

    def reassess(self, lesson_id: str, response: Any) -> dict[str, Any]:
        """Cria uma nova tentativa; nunca sobrescreve a tentativa anterior."""

        return self.submit_attempt(lesson_id, response)

    def history(self, lesson_id: str) -> list[dict[str, Any]]:
        return deepcopy([attempt for attempt in self.attempts if attempt["lesson_id"] == lesson_id])
