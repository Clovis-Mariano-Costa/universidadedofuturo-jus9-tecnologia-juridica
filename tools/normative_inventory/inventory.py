"""Core for the Phase 1 normative inventory.

The module consumes metadata fixtures exported by an authorised adapter. It
does not call Drive or GitHub, does not mutate sources, and never emits source
content in reports.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


SCHEMA_VERSION = "MJ9-INVENTORY-V1"
UNKNOWN_STATE = "SEM ESTADO CONFIRMADO"
ALLOWED_STATES = {
    "VIGENTE",
    "VIGENTE EM TRANSIÇÃO",
    "PARA VISTAS",
    "APROVADO E NÃO PROMULGADO",
    "HISTÓRICO",
    "SUPERADO COM RASTRO",
    "REVOGADO",
    "QUARENTENA",
    "RASCUNHO",
    UNKNOWN_STATE,
}

SENSITIVE_MARKERS = re.compile(
    r"(?<![A-Za-z0-9])(?:cpf|rg|passaporte|endereco|endereço|telefone|email|senha|password|token|secret|"
    r"private|civil|saude|saúde|health|documento[_ -]?pessoal)(?![A-Za-z0-9])",
    re.IGNORECASE,
)

CLASSIFICATION_RULES = (
    ("norma_geral_candidata", re.compile(r"\b(constituicao|constituição|emenda|regulamento|regimento|lei|norma|codigo|código)\b")),
    ("ato_individual_candidato", re.compile(r"\b(ato|resolucao|resolução|determinacao|determinação)\b")),
    ("parecer", re.compile(r"\b(parecer|opiniao|opinião|relatorio|relatório)\b")),
    ("proposta_ou_estudo", re.compile(r"\b(proposta|rascunho|estudo|minuta|plano)\b")),
    ("historico_ou_registro", re.compile(r"\b(historico|histórico|registro|certidao|certidão|ata)\b")),
    ("anexo", re.compile(r"\b(anexo|apendice|apêndice)\b")),
    ("codigo_ou_artefato_tecnico", re.compile(r"\.(?:py|js|mjs|ts|json|csv|html|css|yml|yaml|gs)$")),
)


def canonical_json(value: Any) -> str:
    """Return stable UTF-8 JSON with LF and recursively sorted object keys."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.casefold()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def _content_bytes(raw: Mapping[str, Any]) -> bytes | None:
    if raw.get("content") is not None:
        return str(raw["content"]).replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    if raw.get("content_b64") is not None:
        return base64.b64decode(str(raw["content_b64"]), validate=True)
    return None


def _classify(name: str) -> str:
    normalized = normalize_name(name)
    for label, pattern in CLASSIFICATION_RULES:
        if pattern.search(normalized):
            return label
    return "SEM CLASSIFICAÇÃO CONFIRMADA"


def _extract_metadata(raw: Mapping[str, Any]) -> dict[str, Any]:
    metadata = dict(raw.get("metadata") or {})
    state = metadata.get("state", UNKNOWN_STATE)
    if state not in ALLOWED_STATES:
        state = UNKNOWN_STATE
    return {
        "code": metadata.get("code"),
        "version": metadata.get("version"),
        "state": state,
        "authority": metadata.get("authority"),
        "date": metadata.get("date"),
        "scope": metadata.get("scope"),
        "foundation": metadata.get("foundation"),
        "successor": metadata.get("successor"),
        "revokes": sorted(metadata.get("revokes") or []),
        "sources": sorted(metadata.get("sources") or []),
    }


def _normalize_item(raw: Mapping[str, Any], source: str, config: Mapping[str, Any]) -> dict[str, Any]:
    item_id = str(raw.get("id") or "").strip()
    if not item_id:
        raise ValueError("inventory item requires id")
    name = str(raw.get("name") or raw.get("title") or "").strip()
    if not name:
        raise ValueError(f"inventory item {item_id} requires name")
    content = _content_bytes(raw)
    provided_hash = raw.get("sha256")
    content_hash = sha256_bytes(content) if content is not None else provided_hash
    hash_status = "computed" if content is not None else ("provided_metadata" if provided_hash else "unavailable")
    metadata = _extract_metadata(raw)
    classification = _classify(name)
    sensitive = bool(SENSITIVE_MARKERS.search(name) or SENSITIVE_MARKERS.search(str(raw.get("path") or "")))
    ref = f"{source}:{item_id}"
    return {
        "ref": ref,
        "source": source,
        "source_root": raw.get("source_root") or config.get(f"{source}_root"),
        "source_item_id": item_id,
        "name": "[OMITIDO_POR_RISCO]" if sensitive else name,
        "path": "[OMITIDO_POR_RISCO]" if sensitive else str(raw.get("path") or name),
        "normalized_name": normalize_name(name),
        "mime_type": raw.get("mime_type"),
        "size": raw.get("size"),
        "modified_time": raw.get("modified_time"),
        "version": raw.get("version") or metadata.get("version"),
        "metadata": metadata,
        "classification_candidate": classification,
        "possible_normative": classification in {"norma_geral_candidata", "ato_individual_candidato"},
        "sensitive_candidate": sensitive,
        "sensitive_action": "OMITIR_CONTEUDO_E_REVISAR" if sensitive else None,
        "content_sha256": content_hash,
        "hash_status": hash_status,
        "content_available": content is not None,
        "source_metadata": dict(raw.get("source_metadata") or {}),
    }


def _material_item(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: item[key]
        for key in (
            "ref", "source", "source_root", "source_item_id", "name", "path", "normalized_name",
            "mime_type", "size", "modified_time", "version", "metadata", "classification_candidate",
            "possible_normative", "sensitive_candidate", "content_sha256", "hash_status", "content_available",
        )
    }


def _duplicate_groups(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_hash: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        if item["content_sha256"]:
            by_hash[item["content_sha256"]].append(item)
    exact = [
        {"sha256": digest, "refs": sorted(item["ref"] for item in group), "decision": "PRESERVAR_ORIGINAIS"}
        for digest, group in sorted(by_hash.items())
        if len(group) > 1
    ]
    exact_refs = {ref for group in exact for ref in group["refs"]}
    by_signature: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        if item["ref"] not in exact_refs and item["normalized_name"]:
            by_signature[(item["normalized_name"], item["size"], item["mime_type"])].append(item)
    probable = [
        {
            "signature": {"normalized_name": key[0], "size": key[1], "mime_type": key[2]},
            "refs": sorted(item["ref"] for item in group),
            "decision": "REVISAR_SEM_CONCLUIR_IDENTIDADE",
        }
        for key, group in sorted(by_signature.items(), key=lambda pair: pair[0])
        if len(group) > 1
    ]
    return exact, probable


def _incremental(items: list[dict[str, Any]], previous: Mapping[str, Any] | None) -> dict[str, Any]:
    current = {item["ref"]: _material_item(item) for item in items}
    old = {item["ref"]: item for item in (previous or {}).get("inventory", [])}
    added = sorted(set(current) - set(old))
    removed = sorted(set(old) - set(current))
    changed = sorted(ref for ref in set(current) & set(old) if current[ref] != old[ref])
    return {"previous_report_hash": (previous or {}).get("report_sha256"), "added": added, "removed": removed, "changed": changed}


def build_report(
    drive_items: Iterable[Mapping[str, Any]],
    github_items: Iterable[Mapping[str, Any]],
    config: Mapping[str, Any],
    previous: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the deterministic material inventory without changing any source."""

    items = [
        _normalize_item(item, "drive", config) for item in drive_items
    ] + [
        _normalize_item(item, "github", config) for item in github_items
    ]
    items.sort(key=lambda item: (item["source"], item["path"], item["source_item_id"]))
    exact, probable = _duplicate_groups(items)
    normative = [
        {
            "ref": item["ref"],
            "classification": item["classification_candidate"],
            "state": item["metadata"]["state"],
            "code": item["metadata"]["code"],
            "version": item["version"],
            "authority": item["metadata"]["authority"],
            "status": "CANDIDATO_NORMATIVO",
        }
        for item in items
        if item["possible_normative"]
    ]
    sensitive = [
        {
            "ref": item["ref"],
            "source": item["source"],
            "source_item_id": item["source_item_id"],
            "risk_class": "POTENCIALMENTE_SENSIVEL",
            "recommended_action": item["sensitive_action"],
        }
        for item in items
        if item["sensitive_candidate"]
    ]
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "mode": "DRY_RUN_READ_ONLY",
        "no_source_writes": True,
        "configured_roots": {
            "drive": sorted(config.get("drive_roots") or []),
            "github": {"repository": config.get("github_repository"), "branch": config.get("github_branch")},
        },
        "source_limits": sorted(config.get("source_limits") or []),
        "counts": {
            "total": len(items),
            "drive": sum(item["source"] == "drive" for item in items),
            "github": sum(item["source"] == "github" for item in items),
            "hash_computed": sum(item["hash_status"] == "computed" for item in items),
            "hash_unavailable": sum(item["hash_status"] == "unavailable" for item in items),
            "normative_candidates": len(normative),
            "sensitive_candidates": len(sensitive),
        },
        "inventory": [_material_item(item) for item in items],
        "exact_duplicate_groups": exact,
        "probable_duplicate_groups": probable,
        "normative_matrix": normative,
        "sensitive_findings": sensitive,
        "incremental": _incremental(items, previous),
    }
    report["report_sha256"] = sha256_bytes(canonical_json(report).encode("utf-8"))
    return report


def report_csv(report: Mapping[str, Any]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=["ref", "source", "source_item_id", "name", "path", "state", "classification", "sha256", "hash_status", "sensitive_candidate"], lineterminator="\n")
    writer.writeheader()
    for item in report.get("inventory", []):
        writer.writerow({
            "ref": item["ref"], "source": item["source"], "source_item_id": item["source_item_id"],
            "name": item["name"], "path": item["path"], "state": item["metadata"]["state"],
            "classification": item["classification_candidate"], "sha256": item["content_sha256"] or "",
            "hash_status": item["hash_status"], "sensitive_candidate": item["sensitive_candidate"],
        })
    return output.getvalue()


def report_markdown(report: Mapping[str, Any]) -> str:
    counts = report["counts"]
    lines = [
        "# Inventário normativo MJ9 — relatório sanitizado",
        "",
        f"- Schema: `{report['schema_version']}`",
        f"- Modo: `{report['mode']}`",
        f"- Escrita em fontes: `{report['no_source_writes']}`",
        f"- Hash do relatório: `{report['report_sha256']}`",
        "",
        "## Contagens",
        "",
        f"`{counts['total']}` itens (`{counts['drive']}` Drive + `{counts['github']}` GitHub); `{counts['hash_computed']}` hashes calculados e `{counts['hash_unavailable']}` indisponíveis.",
        f"Candidatos normativos: `{counts['normative_candidates']}`. Achados potencialmente sensíveis: `{counts['sensitive_candidates']}`.",
        "",
        "## Duplicatas",
        "",
        f"Duplicatas exatas: `{len(report['exact_duplicate_groups'])}` grupos; prováveis: `{len(report['probable_duplicate_groups'])}` grupos.",
        "Nenhum grupo autoriza exclusão ou sobrescrita; a decisão registrada é preservar e revisar.",
        "",
        "## Matriz normativa",
        "",
        "| Referência | Classe candidata | Estado | Código | Versão |",
        "|---|---|---|---|---|",
    ]
    for row in report["normative_matrix"]:
        lines.append(f"| `{row['ref']}` | {row['classification']} | {row['state']} | {row['code'] or ''} | {row['version'] or ''} |")
    lines += ["", "## Achados sensíveis", "", "Nenhum conteúdo detectado é reproduzido; somente referência interna, classe de risco e ação recomendada são mantidas.", ""]
    for finding in report["sensitive_findings"]:
        lines.append(f"- `{finding['ref']}` — `{finding['risk_class']}` — `{finding['recommended_action']}`")
    lines += ["", "## Limites", "", "Este relatório não declara vigência normativa, não substitui análise humana ou jurídica, não usa fonte externa ao conjunto configurado e não altera Drive ou GitHub.", ""]
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], output_dir: str | Path, run_timestamp: str) -> None:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "inventory.json").write_text(canonical_json(report), encoding="utf-8", newline="\n")
    (destination / "inventory.csv").write_text(report_csv(report), encoding="utf-8", newline="\n")
    (destination / "REPORT.md").write_text(report_markdown(report), encoding="utf-8", newline="\n")
    history_line = canonical_json({
        "timestamp": run_timestamp,
        "report_sha256": report["report_sha256"],
        "counts": report["counts"],
        "mode": report["mode"],
    })
    history_path = destination / "history.jsonl"
    with history_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(history_line)
