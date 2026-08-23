"""CLI for the local Phase 1 normative inventory."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .inventory import build_report, write_outputs


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MJ9 deterministic read-only inventory")
    parser.add_argument("--config", required=True)
    parser.add_argument("--drive", required=True)
    parser.add_argument("--github", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--previous")
    parser.add_argument("--run-timestamp", default=datetime.now(timezone.utc).isoformat())
    parser.add_argument("--write", action="store_true", help="reserved; source writes are not implemented")
    args = parser.parse_args(argv)
    if args.write:
        parser.error("write mode is intentionally unavailable in Phase 1; use the read-only dry-run")
    config = _load(args.config)
    drive = _load(args.drive)
    github = _load(args.github)
    previous = _load(args.previous) if args.previous else None
    report = build_report(drive.get("items", []), github.get("items", []), config, previous)
    write_outputs(report, args.out, args.run_timestamp)
    print(json.dumps({"report_sha256": report["report_sha256"], "counts": report["counts"], "out": str(args.out)}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
