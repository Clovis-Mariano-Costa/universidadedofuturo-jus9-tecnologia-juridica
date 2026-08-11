"""Sandbox offline da automação governada da Universidade do Futuro."""

from .core import (
    AdjudicationSandbox,
    ExtensionRegistry,
    NormativeRegistry,
    ResearchRegistry,
    SecurityGate,
    append_provenance_event,
    lint_norms,
    quarantine_source,
    scan_security,
    sha256_json,
)

__all__ = [
    "AdjudicationSandbox",
    "ExtensionRegistry",
    "NormativeRegistry",
    "ResearchRegistry",
    "SecurityGate",
    "append_provenance_event",
    "lint_norms",
    "quarantine_source",
    "scan_security",
    "sha256_json",
]
