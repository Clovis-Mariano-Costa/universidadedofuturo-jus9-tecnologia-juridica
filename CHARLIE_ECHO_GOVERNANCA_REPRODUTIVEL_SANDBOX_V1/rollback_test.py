"""Teste de rollback local, reversível e sem remoção automática."""

from __future__ import annotations

import tempfile
from pathlib import Path

try:
    from .dispute_and_supersession_rules import canonical_bytes, sha256
except ImportError:  # execução direta pelo comando reproduzível do README
    from dispute_and_supersession_rules import canonical_bytes, sha256  # type: ignore[no-redef]


def run_rollback_test() -> dict[str, str | bool]:
    with tempfile.TemporaryDirectory(prefix="charlie-echo-rollback-") as temp:
        root = Path(temp)
        target = root / "state.json"
        snapshot = root / "state.snapshot"
        baseline = {"version": 1, "value": "synthetic-baseline"}
        changed = {"version": 2, "value": "synthetic-change"}
        target.write_bytes(canonical_bytes(baseline) + b"\n")
        snapshot.write_bytes(target.read_bytes())
        baseline_hash = sha256(target.read_bytes())
        target.write_bytes(canonical_bytes(changed) + b"\n")
        changed_hash = sha256(target.read_bytes())
        target.write_bytes(snapshot.read_bytes())
        restored_hash = sha256(target.read_bytes())
        return {
            "passed": baseline_hash == restored_hash and baseline_hash != changed_hash,
            "baseline_sha256": baseline_hash,
            "changed_sha256": changed_hash,
            "restored_sha256": restored_hash,
        }


if __name__ == "__main__":
    print(run_rollback_test())
