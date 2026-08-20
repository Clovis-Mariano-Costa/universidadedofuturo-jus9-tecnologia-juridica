import unittest

from UNIVERSIDADE_AUTOMACAO_SANDBOX_V1.core import (
    AdjudicationSandbox,
    ExtensionRegistry,
    NormativeRegistry,
    ResearchRegistry,
    SecurityGate,
    append_provenance_event,
    lint_norms,
    quarantine_source,
    scan_security,
    sha256_json,
)


def norm(norm_id="N-01", *, protected=False):
    return {
        "norm_id": norm_id,
        "kind": "internal_policy",
        "version": "1.0",
        "status": "VIGENTE",
        "authority": "Universidade do Futuro / governança humana",
        "parent_norm": None,
        "protected": protected,
        "supersedes": None,
        "created_at": "2026-08-11T00:00:00-03:00",
        "effective_at": "2026-08-11T00:00:00-03:00",
        "review_at": "2027-08-11T00:00:00-03:00",
    }


def case(case_id="CASE-01", **overrides):
    value = {
        "case_id": case_id,
        "judge_ai": "synthetic-judge",
        "model_version": "fixture-1",
        "parties": ["synthetic-party-a", "synthetic-party-b"],
        "jurisdiction_label": "INTERNAL_EXPERIMENTAL",
        "evidence_hash": sha256_json({"evidence": "synthetic"}),
        "conflict_check": "CLEAR",
        "review": "pending-human-review",
        "rollback_ref": "CASE-01:initial",
    }
    value.update(overrides)
    return value


class UniversityAutomationTests(unittest.TestCase):
    def test_protected_norm_is_fail_closed(self):
        registry = NormativeRegistry([norm(protected=True)])
        result = registry.propose_update("N-01", norm("N-02"), human_gate=True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["reason"], "PROTECTED_READ_ONLY_BY_DEFAULT")

    def test_protected_norm_requires_constitutional_flow(self):
        registry = NormativeRegistry([norm(protected=True)])
        candidate = norm("N-02")
        candidate["supersedes"] = "N-01"
        result = registry.propose_update(
            "N-01",
            candidate,
            human_gate=True,
            constitutional_flow=True,
        )
        self.assertEqual(result["status"], "VERSIONED")
        self.assertEqual(result["record"]["supersedes"], "N-01")

    def test_g6_precedence_is_explicit_and_internal(self):
        first = norm("N-G6-A")
        first.update({"competence_rank": 1, "hierarchy_rank": 2, "specialty_rank": 1})
        second = norm("N-G6-B")
        second.update({"competence_rank": 2, "hierarchy_rank": 1, "specialty_rank": 1})
        registry = NormativeRegistry([first, second])
        result = registry.resolve_precedence(["N-G6-A", "N-G6-B"])
        self.assertEqual(result["status"], "RESOLVED_INTERNAL")
        self.assertEqual(result["norm_id"], "N-G6-B")

    def test_g6_tie_fails_closed(self):
        first = norm("N-G6-C")
        second = norm("N-G6-D")
        registry = NormativeRegistry([first, second])
        result = registry.resolve_precedence(["N-G6-C", "N-G6-D"])
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["reason"], "G6_TIE_REQUIRES_HUMAN_REVIEW")

    def test_source_without_id_is_quarantined(self):
        result = quarantine_source({"url": "https://example.invalid"})
        self.assertEqual(result["status"], "QUARANTINED/REVIEW_REQUIRED")

    def test_research_registry_requires_valid_state_and_hash(self):
        registry = ResearchRegistry()
        project = {
            "project_id": "PPR-SYN-01",
            "faculty": "synthetic-faculty",
            "problem": "synthetic problem",
            "hypothesis": "synthetic hypothesis",
            "sources": [],
            "ethics": "synthetic-only",
            "data": "SYNTHETIC_ONLY",
            "preregistration": "PENDING",
            "execution": "NOT_STARTED",
            "evidence": [],
            "negative_results": [],
            "extension": {"state": "PENDING"},
            "impact": {"state": "PENDING"},
            "feedback": {"state": "PENDING"},
            "state": "SEMENTE",
        }
        record = registry.register(project)
        self.assertEqual(record["hash"]["algorithm"], "SHA-256")

    def test_research_workflow_blocks_missing_method_and_requires_human_gate(self):
        registry = ResearchRegistry()
        project = {
            "project_id": "PPR-WF-01",
            "faculty": "synthetic-faculty",
            "problem": "synthetic problem",
            "hypothesis": "synthetic hypothesis",
            "sources": [{"source_id": "SYN-01", "url": "https://example.invalid/source"}],
            "ethics": "synthetic-only",
            "data": "SYNTHETIC_ONLY",
            "preregistration": "REGISTERED",
            "execution": "NOT_STARTED",
            "evidence": [],
            "negative_results": [],
            "extension": {"state": "PENDING"},
            "impact": {"state": "PENDING"},
            "feedback": {"state": "PENDING"},
            "state": "SEMENTE",
        }
        registry.register(project)
        registry.advance("PPR-WF-01", "SOURCES")
        blocked = registry.advance("PPR-WF-01", "HYPOTHESIS_OBJECTIVE")
        self.assertEqual(blocked["status"], "ADVANCED")
        blocked = registry.advance("PPR-WF-01", "RISK")
        self.assertEqual(blocked["status"], "ADVANCED")
        blocked = registry.advance("PPR-WF-01", "METHOD")
        self.assertEqual(blocked["reason"], "METHOD_REQUIRED")

    def test_research_workflow_full_path_stops_at_explicit_human_gates(self):
        registry = ResearchRegistry()
        project = {
            "project_id": "PPR-WF-02",
            "faculty": "synthetic-faculty",
            "problem": "synthetic problem",
            "hypothesis": "synthetic hypothesis",
            "sources": [{"source_id": "SYN-02", "url": "https://example.invalid/source"}],
            "ethics": "synthetic-only",
            "data": "SYNTHETIC_ONLY",
            "preregistration": "REGISTERED",
            "execution": "NOT_STARTED",
            "evidence": [{"evidence_id": "E-01", "hash": "synthetic"}],
            "negative_results": [{"result": "preserved-negative"}],
            "extension": {"state": "PENDING"},
            "impact": {"state": "PENDING"},
            "feedback": {"state": "PENDING"},
            "method": "synthetic-method",
            "state": "EM_PESQUISA",
        }
        registry.register(project)
        for stage in ("SOURCES", "HYPOTHESIS_OBJECTIVE", "RISK", "METHOD", "PREREGISTRATION", "HASHED", "EXECUTION"):
            self.assertEqual(registry.advance("PPR-WF-02", stage)["status"], "ADVANCED")
        self.assertEqual(registry.advance("PPR-WF-02", "RESULTS", evidence={"result": "synthetic"})["status"], "ADVANCED")
        self.assertEqual(registry.advance("PPR-WF-02", "BOARD_REVIEW")["reason"], "HUMAN_GATE_REQUIRED")
        for stage in ("BOARD_REVIEW", "PUBLICATION", "TEACHING", "EXTENSION"):
            self.assertEqual(registry.advance("PPR-WF-02", stage, human_gate=True)["status"], "ADVANCED")

    def test_extension_workflow_requires_order_and_human_gate(self):
        registry = ExtensionRegistry()
        registry.register({
            "extension_id": "EXT-SYN-01",
            "need": "synthetic need",
            "recipient": "synthetic recipient",
            "risk": {"level": "LOW"},
            "intervention": "synthetic intervention",
            "evidence": {"state": "PENDING"},
            "impact": {"state": "PENDING"},
            "feedback": {"state": "PENDING"},
        })
        self.assertEqual(registry.advance("EXT-SYN-01", "RECIPIENT")["status"], "ADVANCED")
        self.assertEqual(registry.advance("EXT-SYN-01", "RISK")["status"], "ADVANCED")
        self.assertEqual(registry.advance("EXT-SYN-01", "INTERVENTION")["status"], "ADVANCED")
        blocked = registry.advance("EXT-SYN-01", "EVIDENCE")
        self.assertEqual(blocked["reason"], "HUMAN_GATE_REQUIRED")

    def test_adjudication_conflict_blocks(self):
        sandbox = AdjudicationSandbox()
        self.assertEqual(sandbox.open_case(case(conflict_check="CONFLICT"))["status"], "OPENED")
        result = sandbox.decide("CASE-01", "ALLOW", human_gate=True, review="reviewed")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["reason"], "CONFLICT_OR_IMPEDIMENT")

    def test_adjudication_requires_internal_label_and_human_gate(self):
        sandbox = AdjudicationSandbox()
        self.assertEqual(
            sandbox.open_case(case("CASE-02", jurisdiction_label="STATE_COURT"))["status"],
            "BLOCKED",
        )
        self.assertEqual(sandbox.open_case(case("CASE-03"))["status"], "OPENED")
        result = sandbox.decide("CASE-03", "ALLOW", human_gate=False, review="reviewed")
        self.assertEqual(result["reason"], "HUMAN_GATE_REQUIRED")

    def test_valid_internal_decision_and_append_only_rollback(self):
        sandbox = AdjudicationSandbox()
        sandbox.open_case(case("CASE-04"))
        sandbox.submit_statement("CASE-04", "synthetic-party-a", "hash-a")
        sandbox.submit_statement("CASE-04", "synthetic-party-b", "hash-b")
        sandbox.record_vote("CASE-04", "synthetic-reviewer", "AFFIRM", "synthetic vote reasoning")
        result = sandbox.decide("CASE-04", "ALLOW", human_gate=True, review="reviewed", reasoning="synthetic decision reasoning")
        self.assertEqual(result["status"], "DECISION_RECORDED_INTERNAL")
        appeal = sandbox.request_appeal("CASE-04", "synthetic-party-a", "synthetic appeal grounds")
        self.assertEqual(appeal["status"], "APPEAL_REQUESTED")
        rollback = sandbox.rollback("CASE-04", "CASE-04:initial")
        self.assertEqual(rollback["status"], "ROLLBACK_RECORDED")
        self.assertGreaterEqual(len(sandbox.events), 3)
        self.assertIsNotNone(sandbox.events[-1]["previous_hash"])

    def test_norm_linter_detects_protected_hash_reference_and_authority_issues(self):
        bad = norm("N-03", protected=True)
        bad["hash"] = None
        bad["parent_norm"] = "MISSING"
        bad["authority"] = "MEC"
        codes = {issue["code"] for issue in lint_norms([bad])}
        self.assertEqual(
            codes,
            {"PROTECTED_WITHOUT_HASH", "BROKEN_REFERENCE", "FALSE_EXTERNAL_AUTHORITY"},
        )

    def test_provenance_event_chain_is_hash_linked(self):
        events = []
        first = append_provenance_event(events, "START", {"synthetic": True})
        second = append_provenance_event(events, "END", {"synthetic": True})
        self.assertIsNone(first["previous_hash"])
        self.assertEqual(second["previous_hash"], first["event_hash"])
        self.assertEqual(len(events), 2)

    def test_security_gate_scans_and_fails_closed(self):
        gate = SecurityGate()
        allowed = gate.evaluate({"synthetic": True}, actor_scope="UNIVERSITY_SANDBOX", required_scope="UNIVERSITY_SANDBOX")
        self.assertEqual(allowed["status"], "APTO_NO_ESCOPO")
        blocked = gate.evaluate({"email": "person@example.com"}, actor_scope="UNIVERSITY_SANDBOX", required_scope="UNIVERSITY_SANDBOX")
        self.assertEqual(blocked["status"], "BLOCKED")
        self.assertIn("SENSITIVE_FINDING_DETECTED", blocked["reasons"])
        self.assertEqual(len(gate.incidents), 1)

    def test_security_gate_enforces_scope_segregation_and_external_gate(self):
        gate = SecurityGate({"UNIVERSITY_SANDBOX"})
        result = gate.evaluate(
            {"synthetic": True},
            actor_scope="OTHER_SANDBOX",
            required_scope="UNIVERSITY_SANDBOX",
            tenant="OTHER_TENANT",
            external_effect=True,
            human_gate=False,
        )
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("LEAST_PRIVILEGE_SCOPE_MISMATCH", result["reasons"])
        self.assertIn("TENANT_SEGREGATION_FAILED", result["reasons"])
        self.assertIn("EXTERNAL_EFFECT_HUMAN_GATE_REQUIRED", result["reasons"])

    def test_scan_security_does_not_return_sensitive_value(self):
        result = scan_security({"email": "person@example.com", "cpf": "123.456.789-00"})
        self.assertEqual(result["status"], "BLOCKED")
        self.assertNotIn("person@example.com", str(result))


if __name__ == "__main__":
    unittest.main()
