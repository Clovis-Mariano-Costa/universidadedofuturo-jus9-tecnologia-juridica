#!/usr/bin/env python3
"""Guard fail-closed antes de qualquer gerador visual."""

from __future__ import annotations

import hashlib
import re
from typing import Any, Callable


_EXPLICIT_MARKERS = (
    "pai amor",
    "pai-amor",
    "paiamor",
    "pai amado",
    "father of love",
)
_REPRESENTATION_MARKERS = (
    "representar",
    "imagem",
    "ilustração",
    "ilustracao",
    "avatar",
    "retrato",
    "figura",
    "silhueta",
    "visual",
    "desenho",
    "gerar",
    "criar",
)
_AMBIGUITY_MARKERS = (
    "divino",
    "sagrado",
    "criador",
    "entidade suprema",
    "ser absoluto",
)


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def assess_request(prompt: str, *, purpose: str = "") -> dict[str, Any]:
    """Classifica por códigos, sem devolver o prompt no log."""

    normalized = re.sub(r"\s+", " ", prompt.casefold()).strip()
    purpose_normalized = re.sub(r"\s+", " ", purpose.casefold()).strip()
    explicit = any(marker in normalized or marker in purpose_normalized for marker in _EXPLICIT_MARKERS)
    representation = any(marker in normalized or marker in purpose_normalized for marker in _REPRESENTATION_MARKERS)
    ambiguous = any(marker in normalized or marker in purpose_normalized for marker in _AMBIGUITY_MARKERS)
    reasons: list[str] = []
    if explicit and representation:
        reasons.append("PAI_AMOR_REPRESENTATION_FORBIDDEN")
    elif ambiguous and (representation or purpose_normalized):
        reasons.append("AMBIGUOUS_SACRED_REPRESENTATION_REQUIRES_REVIEW")
    status = "BLOCKED" if reasons else "ALLOWED_NON_PAI_PURPOSE"
    return {
        "status": status,
        "reasons": reasons,
        "prompt_sha256": _digest(prompt),
        "purpose_sha256": _digest(purpose),
        "generator_authorized": status == "ALLOWED_NON_PAI_PURPOSE",
    }


def guarded_generation(prompt: str, generator: Callable[[], Any], *, purpose: str = "") -> dict[str, Any]:
    """Só chama o gerador depois de uma decisão explícita de permissão."""

    decision = assess_request(prompt, purpose=purpose)
    if not decision["generator_authorized"]:
        return {"status": "BLOCKED", "decision": decision, "generated": False}
    output = generator()
    return {"status": "GENERATED_NON_PAI_PURPOSE", "decision": decision, "generated": True, "output": output}
