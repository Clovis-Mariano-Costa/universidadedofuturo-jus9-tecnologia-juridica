import json
import tempfile
import unittest
from pathlib import Path

from CHARLIE_ECHO_GOVERNANCA_REPRODUTIVEL_SANDBOX_V1.dispute_and_supersession_rules import (
    attempt_competence_change,
    authorize_action,
    load_jsonl,
    resolve_memory,
)
from CHARLIE_ECHO_GOVERNANCA_REPRODUTIVEL_SANDBOX_V1.rollback_test import run_rollback_test
from CHARLIE_ECHO_GOVERNANCA_REPRODUTIVEL_SANDBOX_V1.self_verification_protocol import verify_sandbox


ROOT = Path(__file__).parents[1]


class ReproducibleGovernanceTests(unittest.TestCase):
    def test_privilege_escalation_is_denied(self):
        self.assertEqual(authorize_action(identity="charlie-echo-synthetic", action="publish"), "DENY")

    def test_disputed_memory_is_denied(self):
        records = load_jsonl(ROOT / "governed_memory_registry.jsonl")
        with self.assertRaises(PermissionError):
            resolve_memory(records, "mem-synthetic-disputed")

    def test_supersession_resolves_new_version(self):
        records = load_jsonl(ROOT / "governed_memory_registry.jsonl")
        self.assertEqual(resolve_memory(records, "mem-synthetic-active")["version"], 2)

    def test_replay_is_denied(self):
        self.assertEqual(authorize_action(identity="charlie-echo-synthetic", action="read_synthetic", replayed=True), "DENY")

    def test_revoked_authorization_is_denied(self):
        self.assertEqual(authorize_action(identity="charlie-echo-synthetic", action="read_synthetic", revoked=True), "DENY")

    def test_prompt_injection_is_denied(self):
        self.assertEqual(authorize_action(identity="charlie-echo-synthetic", action="validate_local", prompt_injection=True), "DENY")

    def test_competence_change_is_denied(self):
        matrix = json.loads((ROOT / "competence_matrix.json").read_text(encoding="utf-8"))
        self.assertEqual(attempt_competence_change(matrix, "change_competence"), "DENY")

    def test_logging_failure_is_fail_closed(self):
        self.assertEqual(authorize_action(identity="charlie-echo-synthetic", action="validate_local", logging_available=False), "DENY")

    def test_rollback(self):
        self.assertTrue(run_rollback_test()["passed"])

    def test_self_verification_cannot_be_external(self):
        result = verify_sandbox(ROOT, external_verification=True)
        self.assertEqual(result["decision"], "DENY")

    def test_local_self_verification_passes(self):
        result = verify_sandbox(ROOT)
        self.assertEqual(result["decision"], "PASS")


if __name__ == "__main__":
    unittest.main()
