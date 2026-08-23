# MJ9 Normative Inventory — Phase 1

Local, deterministic and read-only inventory for the request `PED-CODEX-MJ9-INVENTARIO-2026-08-23-V2.0`.

## Scope

This phase consumes sanitised metadata fixtures for explicitly configured Drive roots and the official GitHub `main` tree. It produces JSON, CSV and Markdown reports, exact/probable duplicate groups, a normative-candidate matrix, sensitive-content findings without reproducing content, and an append-only run history.

It does not call Drive or GitHub APIs, does not authenticate, does not mutate sources, does not publish, and does not classify a document as legally or internally `VIGENTE` unless that state is explicit metadata. Unknown states become `SEM ESTADO CONFIRMADO`.

## Reproduce

From the repository root:

```text
python -m tools.normative_inventory.cli `
  --config tools/normative_inventory/fixtures/config.json `
  --drive tools/normative_inventory/fixtures/drive_metadata.json `
  --github tools/normative_inventory/fixtures/github_tree.json `
  --out tools/normative_inventory/example-output `
  --run-timestamp 2026-08-23T23:59:00Z
```

The generated directory is disposable and is not a source directory. Repeating the command with the same fixtures produces the same material inventory and report hash; only `history.jsonl` receives a new run record when a different timestamp is supplied.

## Safety and rollback

`--write` is deliberately rejected. No credentials or real document content belong in fixtures. To roll back, remove only the generated output directory or close the review branch/PR; no source file is changed by the tool.

## Future phases

API adapters, recursive live reads, manual sample validation, full dry-run and a draft PR remain separate phases. Any write mode requires a new explicit scope and human confirmation.
