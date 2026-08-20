import tempfile
import unittest
from pathlib import Path

from MGP9_POC_SANDBOX_V1.harness import run as run_mgp9
from PACOTE12_ASM_GHR_GV_V1.core import GenealogyHashRecord, validate_transition

from UNIVERSIDADE_AUTOMACAO_SANDBOX_V1.bridge import append_bridge_event, compose_dry_run
from UNIVERSIDADE_AUTOMACAO_SANDBOX_V1.core import AdjudicationSandbox, sha256_json


def synthetic_case(case_id="BRIDGE-01"):
    return {
        "case_id": case_id,
        "judge_ai": "synthetic-judge",
        "model_version": "fixture-1",
        "parties": ["synthetic-a", "synthetic-b"],
        "jurisdiction_label": "INTERNAL_EXPERIMENTAL",
        "evidence_hash": sha256_json({"case": case_id}),
        "conflict_check": "CLEAR",
        "review": "pending",
        "rollback_ref": f"{case_id}:initial",
    }


class BridgeTests(unittest.TestCase):
    def _valid_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            mgp9 = run_mgp9(Path(temp) / "mgp9", limit=1)
            gate = validate_transition(
                "M20",
                "M21",
                {
                    "publication_authorization": "synthetic-review",
                    "same_version_hash": "synthetic-hash",
                    "tenant_isolation_tested": True,
                    "authz_tested": True,
                    "rollback_tested": True,
                },
            )
            adjudication = AdjudicationSandbox()
            adjudication.open_case(synthetic_case())
            adjudication.submit_statement("BRIDGE-01", "synthetic-a", "statement-a")
            adjudication.submit_statement("BRIDGE-01", "synthetic-b", "statement-b")
            adjudication.record_vote("BRIDGE-01", "synthetic-reviewer", "AFFIRM", "synthetic vote reasoning")
            decision = adjudication.decide(
                "BRIDGE-01", "ALLOW_INTERNAL_ONLY", human_gate=True, review="human-review", reasoning="synthetic decision reasoning"
            )
            provenance = GenealogyHashRecord.create(
                artifact_id="BRIDGE-ARTIFACT-01",
                payload={"synthetic": True},
                state="M20",
                actor="synthetic-agent",
                origin="synthetic-origin",
                destination="synthetic-destination",
            )
            return mgp9, gate, decision, provenance

    def test_valid_composition_is_only_ready_for_human_review(self):
        mgp9, gate, decision, provenance = self._valid_inputs()
        result = compose_dry_run(mgp9, gate, decision, provenance)
        self.assertEqual(result["status"], "READY_FOR_HUMAN_REVIEW")
        self.assertFalse(result["external_effect"])
        self.assertTrue(result["bridge_sha256"])

    def test_missing_mgp9_hash_blocks(self):
        mgp9, gate, decision, provenance = self._valid_inputs()
        mgp9 = dict(mgp9)
        mgp9["output_sha256"] = None
        result = compose_dry_run(mgp9, gate, decision, provenance)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("MGP9_FIELD_MISSING:output_sha256", result["reasons"])

    def test_blocked_package12_gate_blocks_bridge(self):
        mgp9, _gate, decision, provenance = self._valid_inputs()
        result = compose_dry_run(
            mgp9,
            {"allowed": False, "code": "HASH_DIVERGENCE"},
            decision,
            provenance,
        )
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("PACKAGE12_GATE_BLOCKED:HASH_DIVERGENCE", result["reasons"])

    def test_external_decision_is_never_composed(self):
        mgp9, gate, _decision, provenance = self._valid_inputs()
        external = {
            "status": "DECISION_RECORDED_INTERNAL",
            "record": {"jurisdiction_label": "STATE_COURT", "human_gate": True},
        }
        result = compose_dry_run(mgp9, gate, external, provenance)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("UNIVERSITY_JURISDICTION_INVALID", result["reasons"])

    def test_bridge_event_is_append_only(self):
        mgp9, gate, decision, provenance = self._valid_inputs()
        result = compose_dry_run(mgp9, gate, decision, provenance)
        events = []
        event = append_bridge_event(events, result)
        self.assertEqual(event["event_type"], "BRIDGE_DRY_RUN")
        self.assertEqual(len(events), 1)


if __name__ == "__main__":
    unittest.main()
