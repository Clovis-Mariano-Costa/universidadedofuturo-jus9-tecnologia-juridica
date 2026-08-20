#!/usr/bin/env python3
"""Executor determinístico do MGP9_POC_SANDBOX_V1.

Sem rede, sem credenciais e sem efeitos externos. Os resultados são sempre
exportados individualmente antes de qualquer resumo.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
CORPUS_PATH = ROOT / "data" / "b11_corpus.json"
CONFIGS_PATH = ROOT / "data" / "configs" / "b0-b5.json"
ARTIFACTS_DIR = ROOT / "artifacts"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_synthetic_payload(corpus: dict[str, Any], configs: dict[str, Any]) -> None:
    forbidden = ("sk-", "api_key", "access_token", "password", "secret", "private_key")
    serialized = canonical_bytes({"corpus": corpus, "configs": configs}).lower()
    for marker in forbidden:
        if marker.encode("ascii") in serialized:
            raise ValueError(f"payload rejected: possible credential marker {marker!r}")
    if corpus.get("data_classification") != "SYNTHETIC_ONLY":
        raise ValueError("corpus must declare SYNTHETIC_ONLY")
    if [item.get("config_id") for item in configs.get("configs", [])] != ["B0", "B1", "B2", "B3", "B4", "B5"]:
        raise ValueError("configs must contain ordered B0-B5")


def iter_pairs(corpus: dict[str, Any], configs: dict[str, Any], limit: int | None = None) -> Iterable[tuple[int, dict[str, Any], dict[str, Any]]]:
    pairs = [(scenario, config) for scenario in corpus["scenarios"] for config in configs["configs"]]
    if limit is not None:
        pairs = pairs[:limit]
    for index, (scenario, config) in enumerate(pairs, start=1):
        yield index, scenario, config


def evaluate(index: int, scenario: dict[str, Any], config: dict[str, Any], seed: int) -> dict[str, Any]:
    config_id = config["config_id"]
    applicable = config_id in scenario["applicable_configs"]
    if not applicable:
        status = "N/A"
        observed_score = None
        reason = "scenario not applicable to this configuration"
    else:
        observed_score = scenario["signal"] + config["offset"]
        status = "PASS" if observed_score >= config["threshold"] else "FAIL"
        reason = "synthetic threshold comparison"

    input_payload = {"scenario": scenario, "config": config, "seed": seed}
    output_payload = {
        "scenario_id": scenario["scenario_id"],
        "config_id": config_id,
        "status": status,
        "observed_score": observed_score,
        "expected": scenario["expected"] if applicable else "N/A",
    }
    return {
        "run_id": f"MGP9-{index:04d}",
        "execution_index": index,
        "corpus_id": "B11",
        "scenario_id": scenario["scenario_id"],
        "config_id": config_id,
        "config_version": config["version"],
        "seed": seed,
        "randomness": "none",
        "status": status,
        "expected": output_payload["expected"],
        "observed_score": observed_score,
        "reason": reason,
        "input_sha256": sha256_json(input_payload),
        "output_sha256": sha256_json(output_payload),
    }


def write_csv(path: Path, results: list[dict[str, Any]]) -> None:
    fields = list(results[0].keys()) if results else ["run_id", "status"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)


def run(output_dir: Path, seed: int = 20260810, limit: int | None = None) -> dict[str, Any]:
    corpus = load_json(CORPUS_PATH)
    configs = load_json(CONFIGS_PATH)
    validate_synthetic_payload(corpus, configs)
    pairs = list(iter_pairs(corpus, configs, limit))
    if not pairs:
        raise ValueError("at least one pair is required")

    output_dir.mkdir(parents=True, exist_ok=False)
    events_path = output_dir / "events.jsonl"
    results_path = output_dir / "results.jsonl"
    results: list[dict[str, Any]] = []

    def event(kind: str, **fields: Any) -> None:
        payload = {"timestamp": datetime.now(timezone.utc).isoformat(), "event": kind, **fields}
        with events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")

    event("run_started", corpus_id=corpus["corpus_id"], pair_count=len(pairs), seed=seed)
    for index, scenario, config in pairs:
        result = evaluate(index, scenario, config, seed)
        results.append(result)
        with results_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        event("scenario_completed", run_id=result["run_id"], status=result["status"])

    raw_bytes = results_path.read_bytes()
    output_sha = sha256_bytes(raw_bytes)
    input_sha = sha256_json({"corpus": corpus, "configs": configs})
    (output_dir / "input.sha256").write_text(input_sha + "\n", encoding="utf-8")
    (output_dir / "output.sha256").write_text(output_sha + "\n", encoding="utf-8")
    write_csv(output_dir / "results.csv", results)

    counts = {status: sum(1 for item in results if item["status"] == status) for status in ("PASS", "FAIL", "N/A")}
    manifest = {
        "harness": "MGP9_POC_SANDBOX_V1",
        "harness_version": "1.0.0",
        "corpus_id": corpus["corpus_id"],
        "corpus_version": corpus["version"],
        "configs": [item["config_id"] for item in configs["configs"]],
        "seed": seed,
        "pair_count": len(results),
        "status_counts": counts,
        "data_classification": "SYNTHETIC_ONLY",
        "input_sha256": input_sha,
        "output_sha256": output_sha,
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "recreate_command": "python MGP9_POC_SANDBOX_V1/harness.py",
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "ROLLBACK.md").write_text(
        "# Rollback da execução\n\n"
        f"Artefatos desta execução: `{output_dir}`\n\n"
        "Para recriar, remova manualmente somente este diretório depois de confirmar o caminho e execute novamente o comando do manifesto. "
        "O harness não executa remoção automática e não altera dados fora de `MGP9_POC_SANDBOX_V1/artifacts/`.\n",
        encoding="utf-8",
    )
    event("run_completed", output_sha256=output_sha, status_counts=counts)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="diretório novo para os artefatos")
    parser.add_argument("--seed", type=int, default=20260810)
    parser.add_argument("--limit", type=int, help="limita a quantidade de pares; use 60 para o lote legado")
    parser.add_argument("--smoke", action="store_true", help="executa apenas um par")
    args = parser.parse_args(argv)
    if args.limit is not None and args.limit < 1:
        parser.error("--limit deve ser positivo")
    limit = 1 if args.smoke else args.limit
    output_dir = args.output_dir or ARTIFACTS_DIR / datetime.now().strftime("run-%Y%m%dT%H%M%SZ")
    try:
        manifest = run(output_dir, seed=args.seed, limit=limit)
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
