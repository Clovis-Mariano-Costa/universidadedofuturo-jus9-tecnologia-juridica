import json
import tempfile
import unittest
from pathlib import Path

from MGP9_POC_SANDBOX_V1.harness import run
from MGP9_POC_SANDBOX_V1.registry import list_records, validate_all


class Mgp9HarnessTests(unittest.TestCase):
    def test_smoke_and_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = run(Path(temp) / "smoke", seed=7, limit=1)
            self.assertEqual(manifest["pair_count"], 1)
            self.assertEqual(len((Path(temp) / "smoke" / "results.jsonl").read_text(encoding="utf-8").splitlines()), 1)
            self.assertEqual(len((Path(temp) / "smoke" / "events.jsonl").read_text(encoding="utf-8").splitlines()), 3)
            self.assertTrue((Path(temp) / "smoke" / "output.sha256").read_text(encoding="utf-8").strip())

    def test_default_pairing_is_72_and_preserves_statuses(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = run(Path(temp) / "full")
            self.assertEqual(manifest["pair_count"], 72)
            self.assertEqual(sum(manifest["status_counts"].values()), 72)
            rows = [json.loads(line) for line in (Path(temp) / "full" / "results.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len({row["config_id"] for row in rows}), 6)
            self.assertEqual(len({row["scenario_id"] for row in rows}), 12)
            self.assertTrue(all(row["input_sha256"] and row["output_sha256"] for row in rows))

    def test_legacy_limit_of_60_is_available(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(run(Path(temp) / "legacy", limit=60)["pair_count"], 60)

    def test_registry_fixtures(self):
        counts = validate_all()
        self.assertEqual(counts["academic_records.json"], 1)
        self.assertEqual(counts["academic_sources.json"], 2)
        self.assertEqual(len(list_records("dictionary", "SEMENTE")), 1)
        self.assertEqual(len(list_records("dictionary", "CANONICA")), 0)


if __name__ == "__main__":
    unittest.main()
