import unittest

from PACOTE12_ASM_GHR_GV_V1.core import (
    GenealogyHashRecord,
    canonical_sha256,
    validate_change_version,
    validate_transition,
)


class Package12Tests(unittest.TestCase):
    def test_valid_transition_does_not_false_block(self):
        result = validate_transition("M00", "M01")
        self.assertTrue(result.allowed, result)

    def test_forbidden_transition_is_fail_closed(self):
        result = validate_transition("M00", "M22", {"force_terminal": True})
        self.assertFalse(result.allowed)
        self.assertEqual(result.code, "FORCED_TERMINAL")

    def test_hash_divergence_between_evaluators_blocks(self):
        evidence = {"bank_evidence": "bank-1", "evaluator_hashes": ["aaa", "bbb"]}
        result = validate_transition("M13", "M14", evidence)
        self.assertFalse(result.allowed)
        self.assertEqual(result.code, "HASH_DIVERGENCE")

    def test_deposit_before_evidence_blocks(self):
        evidence = {"deposit_evidence": "deposit-1"}
        result = validate_transition("M19", "M20", evidence)
        self.assertFalse(result.allowed)
        self.assertEqual(result.code, "VERSION_HASH_MISSING")

    def test_homologation_without_evidence_blocks(self):
        result = validate_transition("M17", "M18")
        self.assertFalse(result.allowed)
        self.assertEqual(result.code, "EVIDENCE_MISSING")

    def test_content_change_requires_new_version(self):
        result = validate_change_version("a", "b", 2, 2)
        self.assertFalse(result.allowed)
        self.assertEqual(result.code, "VERSION_REQUIRED")

    def test_ghr_parent_hash_and_append_only_rollback(self):
        first = GenealogyHashRecord.create(
            artifact_id="artifact-synthetic-1",
            payload={"title": "rascunho"},
            state="M00",
            actor="CODEX_TECNICO",
            origin="synthetic",
            destination="sandbox",
        )
        second = GenealogyHashRecord.evolve(
            first,
            payload={"title": "rascunho revisado"},
            state="M01",
            actor="CODEX_TECNICO",
            origin="sandbox",
            destination="sandbox",
            rule="ASM_M00_M01",
            transformation="version",
        )
        rollback = GenealogyHashRecord.rollback(
            second, actor="CODEX_TECNICO", target_version=1, reason="teste de restauração"
        )
        self.assertEqual(second["parent_hash"], first["content_hash"])
        self.assertEqual(rollback["version"], 3)
        self.assertEqual(len(rollback["events"]), 3)
        self.assertEqual(rollback["events"][-1]["result"], "ROLLBACK_APPLIED")
        self.assertEqual(canonical_sha256({"title": "rascunho"}), first["content_hash"])

    def test_valid_terminal_path_requires_complete_evidence(self):
        evidence = {
            "publication_receipt": "pub-1",
            "same_version_hash": "sha256:abc",
            "tenant_isolation_tested": True,
            "authz_tested": True,
            "rollback_tested": True,
        }
        result = validate_transition("M21", "M22", evidence)
        self.assertTrue(result.allowed, result)

    def test_security_high_without_acceptance_blocks(self):
        evidence = {
            "publication_receipt": "pub-1",
            "same_version_hash": "sha256:abc",
            "security_findings": [{"severity": "HIGH"}],
        }
        result = validate_transition("M21", "M22", evidence)
        self.assertFalse(result.allowed)
        self.assertEqual(result.code, "SECURITY_HIGH_UNACCEPTED")


if __name__ == "__main__":
    unittest.main()
