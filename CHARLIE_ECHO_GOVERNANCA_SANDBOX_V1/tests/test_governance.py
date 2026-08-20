import unittest

from CHARLIE_ECHO_GOVERNANCA_SANDBOX_V1.core import GovernanceEngine, RiskLevel


class GovernanceTests(unittest.TestCase):
    def setUp(self):
        self.engine = GovernanceEngine()
        self.engine.register_identity("codex-synth", "local-sandbox", "human-owner", {"read", "write"})
        self.engine.grant("CODEX", "read", RiskLevel.G1)
        # A permissão alcança G3 para que o teste valide o gate humano,
        # em vez de parar antes no bloqueio por risco excedente.
        self.engine.grant("CODEX", "write", RiskLevel.G3)

    def test_low_risk_action_allowed(self):
        decision = self.engine.decide(identity_id="codex-synth", role="CODEX", action="read")
        self.assertEqual(decision.decision, "ALLOW")

    def test_unknown_identity_denied(self):
        decision = self.engine.decide(identity_id="missing", role="CODEX", action="read")
        self.assertEqual(decision.decision, "DENY")

    def test_revoked_identity_denied(self):
        self.engine.revoke_identity("codex-synth")
        decision = self.engine.decide(identity_id="codex-synth", role="CODEX", action="read")
        self.assertEqual(decision.decision, "DENY")

    def test_missing_permission_denied(self):
        decision = self.engine.decide(identity_id="codex-synth", role="OTHER", action="read")
        self.assertEqual(decision.decision, "DENY")

    def test_sensitive_action_requires_human(self):
        decision = self.engine.decide(identity_id="codex-synth", role="CODEX", action="write", sensitive_data=True)
        self.assertEqual(decision.decision, "REQUIRE_HUMAN")
        self.assertEqual(decision.risk, RiskLevel.G3)

    def test_external_action_requires_human_even_with_permission(self):
        self.engine.grant("CODEX", "publish", RiskLevel.G4)
        decision = self.engine.decide(identity_id="codex-synth", role="CODEX", action="publish", external_effect=True)
        self.assertEqual(decision.decision, "REQUIRE_HUMAN")

    def test_privilege_escalation_is_denied(self):
        self.engine.grant("CODEX", "read-only", RiskLevel.G1)
        decision = self.engine.decide(identity_id="codex-synth", role="CODEX", action="read-only", external_effect=True)
        self.assertEqual(decision.decision, "DENY")

    def test_replay_is_denied_after_allow(self):
        first = self.engine.decide(identity_id="codex-synth", role="CODEX", action="read", action_id="a-1")
        second = self.engine.decide(identity_id="codex-synth", role="CODEX", action="read", action_id="a-1")
        self.assertEqual(first.decision, "ALLOW")
        self.assertEqual(second.decision, "DENY")

    def test_provenance_chain_detects_tampering(self):
        self.engine.decide(identity_id="codex-synth", role="CODEX", action="read")
        self.assertTrue(self.engine.validate_provenance())
        self.engine.events[0]["payload"]["tampered"] = True
        self.assertFalse(self.engine.validate_provenance())

    def test_prompt_injection_is_blocked(self):
        decision = self.engine.decide(
            identity_id="codex-synth",
            role="CODEX",
            action="read",
            prompt_injection_detected=True,
        )
        self.assertEqual(decision.decision, "DENY")

    def test_logging_failure_is_fail_closed(self):
        self.engine.logging_available = False
        decision = self.engine.decide(identity_id="codex-synth", role="CODEX", action="read")
        self.assertEqual(decision.decision, "DENY")
        self.assertEqual(decision.event_id, "UNLOGGED")

    def test_human_confirmed_high_risk_still_requires_evidence(self):
        self.engine.grant("CODEX", "publish", RiskLevel.G4)
        decision = self.engine.decide(identity_id="codex-synth", role="CODEX", action="publish", external_effect=True, human_confirmed=True)
        self.assertEqual(decision.decision, "REQUIRE_EVIDENCE")

    def test_evidence_allows_authorized_risk(self):
        self.engine.grant("CODEX", "review", RiskLevel.G3)
        decision = self.engine.decide(identity_id="codex-synth", role="CODEX", action="review", sensitive_data=True, human_confirmed=True, evidence={"ticket": "synthetic-1"})
        self.assertEqual(decision.decision, "ALLOW")

    def test_memory_change_requires_new_version(self):
        self.engine.register_memory("m1", "a", source="synthetic", version=1)
        with self.assertRaises(ValueError):
            self.engine.register_memory("m1", "b", source="synthetic", version=1)

    def test_disputed_memory_is_not_canonical(self):
        self.engine.register_memory("m2", "claim", source="synthetic", version=1, disputed=True)
        self.assertEqual(self.engine.memories["m2"]["status"], "DISPUTED")

    def test_learning_package_and_recertification(self):
        self.engine.record_learning_change({"mudanca": "x", "fonte": "synthetic", "regra": "gate", "risco": "low", "contraexemplo": "y", "teste": "z", "versao": "1"})
        self.assertTrue(self.engine.recertification()["passed"])


if __name__ == "__main__":
    unittest.main()
