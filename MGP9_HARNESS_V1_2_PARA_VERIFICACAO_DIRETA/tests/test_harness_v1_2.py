import tempfile
import unittest
from pathlib import Path

from MGP9_HARNESS_V1_2_PARA_VERIFICACAO_DIRETA.harness import (
    canonical_json,
    run,
    validate_b12_scientific_input,
    validate_execution_contract,
)


class HarnessV12Tests(unittest.TestCase):
    def test_execution_contract_requires_synthetic_for_development_and_smoke(self):
        validate_execution_contract("development", True)
        validate_execution_contract("smoke", True)
        with self.assertRaises(ValueError):
            validate_execution_contract("smoke", False)

    def test_b12_rejects_synthetic_and_non_confirmatory_records(self):
        with self.assertRaises(ValueError):
            validate_b12_scientific_input({"corpus_id": "B12", "is_synthetic": True, "execution_purpose": "smoke"})
        with self.assertRaises(ValueError):
            validate_b12_scientific_input({"corpus_id": "B12", "is_synthetic": False, "execution_purpose": "development"})
        self.assertTrue(validate_b12_scientific_input({"corpus_id": "B12", "is_synthetic": False, "execution_purpose": "poc_confirmatory"}))

    def test_deterministic_json_and_lf_outputs(self):
        self.assertEqual(canonical_json({"b": 2, "a": 1}), '{"a":1,"b":2}\n')
        with tempfile.TemporaryDirectory() as temp:
            first = run(Path(temp) / "first", seed=7, limit=1, execution_purpose="smoke")
            second = run(Path(temp) / "second", seed=7, limit=1, execution_purpose="smoke")
            self.assertEqual(first, second)
            for name in ("results.jsonl", "events.jsonl", "manifest.json", "input.sha256", "output.sha256", "results.csv", "ROLLBACK.md"):
                self.assertNotIn(b"\r", (Path(temp) / "first" / name).read_bytes())
                self.assertEqual((Path(temp) / "first" / name).read_bytes(), (Path(temp) / "second" / name).read_bytes())

    def test_smoke_is_explicitly_synthetic(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = run(Path(temp) / "smoke", seed=7, limit=1, execution_purpose="smoke")
            self.assertTrue(manifest["is_synthetic"])
            self.assertEqual(manifest["execution_purpose"], "smoke")

    def test_poc_and_60_limit_are_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                run(Path(temp) / "poc", execution_purpose="poc_confirmatory", is_synthetic=False)
            with self.assertRaises(ValueError):
                run(Path(temp) / "sixty", limit=60, execution_purpose="development")


if __name__ == "__main__":
    unittest.main()
