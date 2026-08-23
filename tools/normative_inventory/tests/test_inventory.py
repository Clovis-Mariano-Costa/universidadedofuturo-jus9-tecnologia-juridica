import json
import tempfile
import unittest
from pathlib import Path

from tools.normative_inventory.cli import main
from tools.normative_inventory.inventory import build_report, canonical_json, normalize_name, write_outputs


ROOT = Path(__file__).parents[1]


def fixture(name):
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.config = fixture("config.json")
        self.drive = fixture("drive_metadata.json")["items"]
        self.github = fixture("github_tree.json")["items"]

    def test_normalizes_accents_and_separators(self):
        self.assertEqual(normalize_name("Constituição — V1.0"), "constituicao v1 0")

    def test_builds_cross_source_exact_duplicate_groups(self):
        report = build_report(self.drive, self.github, self.config)
        self.assertEqual(report["counts"]["total"], 7)
        self.assertGreaterEqual(len(report["exact_duplicate_groups"]), 2)
        refs = {ref for group in report["exact_duplicate_groups"] for ref in group["refs"]}
        self.assertIn("drive:drive-ato-001", refs)
        self.assertIn("github:github-ato-001", refs)

    def test_unknown_normative_state_is_not_promoted(self):
        report = build_report(self.drive, self.github, self.config)
        row = next(row for row in report["normative_matrix"] if row["ref"] == "github:github-proposta-001")
        self.assertEqual(row["state"], "SEM ESTADO CONFIRMADO")
        self.assertEqual(row["status"], "CANDIDATO_NORMATIVO")

    def test_sensitive_names_are_redacted_without_content(self):
        report = build_report(self.drive, self.github, self.config)
        item = next(item for item in report["inventory"] if item["ref"] == "drive:drive-civil-001")
        self.assertEqual(item["name"], "[OMITIDO_POR_RISCO]")
        self.assertEqual(item["path"], "[OMITIDO_POR_RISCO]")
        self.assertEqual(len(report["sensitive_findings"]), 1)

    def test_material_report_is_idempotent(self):
        first = build_report(self.drive, self.github, self.config)
        second = build_report(self.drive, self.github, self.config)
        self.assertEqual(first["report_sha256"], second["report_sha256"])
        self.assertEqual(canonical_json(first), canonical_json(second))

    def test_outputs_are_lf_and_history_has_timestamp(self):
        report = build_report(self.drive, self.github, self.config)
        with tempfile.TemporaryDirectory() as directory:
            write_outputs(report, directory, "2026-08-23T23:59:00Z")
            output = Path(directory)
            self.assertIn("\n", (output / "REPORT.md").read_text(encoding="utf-8"))
            self.assertNotIn("\r\n", (output / "REPORT.md").read_bytes().decode("utf-8"))
            history = json.loads((output / "history.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(history["timestamp"], "2026-08-23T23:59:00Z")
            self.assertEqual(history["report_sha256"], report["report_sha256"])

    def test_write_mode_is_rejected(self):
        with self.assertRaises(SystemExit):
            main([
                "--config", str(ROOT / "fixtures" / "config.json"),
                "--drive", str(ROOT / "fixtures" / "drive_metadata.json"),
                "--github", str(ROOT / "fixtures" / "github_tree.json"),
                "--out", "unused-output",
                "--write",
            ])


if __name__ == "__main__":
    unittest.main()
