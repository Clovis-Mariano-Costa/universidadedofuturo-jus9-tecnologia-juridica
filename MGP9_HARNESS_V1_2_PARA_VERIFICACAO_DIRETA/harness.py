#!/usr/bin/env python3
"""MGP-9 Harness V1.2: determinístico, sintético e sem POC confirmatória."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
CORPUS_PATH = ROOT / "data" / "b11_corpus.json"
CONFIGS_PATH = ROOT / "data" / "configs" / "b0-b5.json"
ARTIFACTS_DIR = ROOT / "artifacts"
EXECUTION_PURPOSES = frozenset({"development", "smoke", "poc_confirmatory"})
POC_CONFIRMATORY_DISABLED = "POC confirmatória não faz parte do Harness V1.2"


def canonical_bytes(value: Any) -> bytes:
    """Serializa JSON em UTF-8, chaves ordenadas, sem espaços e com LF."""
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def canonical_json(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_lf(path: Path, content: str) -> None:
    """Escreve texto canônico sem CRLF e sempre com LF final."""
    path.write_bytes(content.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n").encode("utf-8") + b"\n")


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def validate_execution_contract(execution_purpose: str, is_synthetic: bool) -> None:
    if execution_purpose not in EXECUTION_PURPOSES:
        raise ValueError(f"execution_purpose inválido: {execution_purpose!r}")
    if not isinstance(is_synthetic, bool):
        raise ValueError("is_synthetic deve ser booleano")
    if execution_purpose in {"development", "smoke"} and is_synthetic is not True:
        raise ValueError("development/smoke exigem is_synthetic=true")
    if execution_purpose == "poc_confirmatory" and is_synthetic is not False:
        raise ValueError("poc_confirmatory exige is_synthetic=false")


def validate_b12_scientific_input(record: dict[str, Any]) -> bool:
    """Aceita B12 somente como POC confirmatória não sintética."""
    if record.get("corpus_id") != "B12":
        raise ValueError("registro não pertence ao corpus B12")
    if record.get("is_synthetic") is True:
        raise ValueError("B12 científico rejeita is_synthetic=true")
    if record.get("is_synthetic") is not False:
        raise ValueError("B12 científico exige is_synthetic=false explícito")
    if record.get("execution_purpose") != "poc_confirmatory":
        raise ValueError("B12 científico exige execution_purpose=poc_confirmatory")
    return True


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


def evaluate(index: int, scenario: dict[str, Any], config: dict[str, Any], seed: int, execution_purpose: str, is_synthetic: bool) -> dict[str, Any]:
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

    input_payload = {
        "execution_purpose": execution_purpose,
        "is_synthetic": is_synthetic,
        "scenario": scenario,
        "config": config,
        "seed": seed,
    }
    output_payload = {
        "scenario_id": scenario["scenario_id"],
        "config_id": config_id,
        "status": status,
        "observed_score": observed_score,
        "expected": scenario["expected"] if applicable else "N/A",
        "execution_purpose": execution_purpose,
        "is_synthetic": is_synthetic,
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
        "is_synthetic": is_synthetic,
        "execution_purpose": execution_purpose,
        "input_sha256": sha256_json(input_payload),
        "output_sha256": sha256_json(output_payload),
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_bytes(b"".join(canonical_bytes(row) for row in rows))


def write_csv(path: Path, results: list[dict[str, Any]]) -> None:
    fields = list(results[0].keys()) if results else ["run_id", "status"]
    lines: list[str] = []
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)
        handle.seek(0)
        lines.append(handle.read())
    write_lf(path, "".join(lines))


def run(
    output_dir: Path,
    seed: int = 20260810,
    limit: int | None = None,
    *,
    execution_purpose: str = "development",
    is_synthetic: bool = True,
) -> dict[str, Any]:
    validate_execution_contract(execution_purpose, is_synthetic)
    if execution_purpose == "poc_confirmatory":
        raise ValueError(POC_CONFIRMATORY_DISABLED)
    if limit == 60:
        raise ValueError("execução de 60 cenários bloqueada no pacote V1.2")
    corpus = load_json(CORPUS_PATH)
    configs = load_json(CONFIGS_PATH)
    validate_synthetic_payload(corpus, configs)
    pairs = list(iter_pairs(corpus, configs, limit))
    if not pairs:
        raise ValueError("at least one pair is required")

    output_dir.mkdir(parents=True, exist_ok=False)
    results = [evaluate(index, scenario, config, seed, execution_purpose, is_synthetic) for index, scenario, config in pairs]
    results_path = output_dir / "results.jsonl"
    write_jsonl(results_path, results)
    counts = {status: sum(1 for item in results if item["status"] == status) for status in ("PASS", "FAIL", "N/A")}
    input_sha = sha256_json({"corpus": corpus, "configs": configs, "execution_purpose": execution_purpose, "is_synthetic": is_synthetic, "seed": seed})
    output_sha = sha256_bytes(results_path.read_bytes())
    write_lf(output_dir / "input.sha256", input_sha)
    write_lf(output_dir / "output.sha256", output_sha)
    write_csv(output_dir / "results.csv", results)
    events = [
        {"event_index": 1, "event": "run_started", "corpus_id": corpus["corpus_id"], "pair_count": len(pairs), "seed": seed, "is_synthetic": is_synthetic, "execution_purpose": execution_purpose},
        *[{"event_index": index + 1, "event": "scenario_completed", "run_id": result["run_id"], "status": result["status"], "is_synthetic": is_synthetic, "execution_purpose": execution_purpose} for index, result in enumerate(results)],
        {"event_index": len(results) + 2, "event": "run_completed", "output_sha256": output_sha, "status_counts": counts, "is_synthetic": is_synthetic, "execution_purpose": execution_purpose},
    ]
    write_jsonl(output_dir / "events.jsonl", events)
    manifest = {
        "harness": "MGP9_HARNESS_V1_2_PARA_VERIFICACAO_DIRETA",
        "harness_version": "1.2.0",
        "corpus_id": corpus["corpus_id"],
        "corpus_version": corpus["version"],
        "configs": [item["config_id"] for item in configs["configs"]],
        "seed": seed,
        "pair_count": len(results),
        "status_counts": counts,
        "data_classification": "SYNTHETIC_ONLY",
        "is_synthetic": is_synthetic,
        "execution_purpose": execution_purpose,
        "input_sha256": input_sha,
        "output_sha256": output_sha,
        "serialization": {"encoding": "UTF-8", "json": "sort_keys=true,separators=(',',':')", "newline": "LF"},
        "recreate_command": "python MGP9_HARNESS_V1_2_PARA_VERIFICACAO_DIRETA/harness.py --smoke --execution-purpose smoke",
    }
    write_json(output_dir / "manifest.json", manifest)
    write_lf(output_dir / "ROLLBACK.md", "# Rollback\n\nPreserve o manifesto e os hashes. Remova manualmente somente este diretório de artefatos, se necessário. O harness não remove arquivos automaticamente.\n")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--seed", type=int, default=20260810)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--execution-purpose", choices=sorted(EXECUTION_PURPOSES), default="development")
    args = parser.parse_args(argv)
    limit = 1 if args.smoke else args.limit
    purpose = "smoke" if args.smoke else args.execution_purpose
    output_dir = args.output_dir or ARTIFACTS_DIR / "run-v1.2"
    try:
        manifest = run(output_dir, seed=args.seed, limit=limit, execution_purpose=purpose, is_synthetic=True)
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(canonical_json(manifest), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
