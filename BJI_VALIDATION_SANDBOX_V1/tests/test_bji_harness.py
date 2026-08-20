import unittest

from BJI_VALIDATION_SANDBOX_V1.harness import BJIRegistry


def experiment(experiment_id="BJI-SYN-01"):
    return {
        "experiment_id": experiment_id,
        "agent_version": "synthetic-agent-v1",
        "criteria": {"expected": "pre-registered synthetic criterion"},
        "inputs": [{"input_id": "I-01", "content": "synthetic"}],
        "expected_output": {"schema": "synthetic"},
        "state": "NAO_EXECUTADO",
        "results": [],
        "conclusion": None,
    }


class BJIHarnessTests(unittest.TestCase):
    def test_preregistration_has_no_results_or_conclusion(self):
        registry = BJIRegistry()
        record = registry.register(experiment())
        self.assertEqual(record["state"], "NAO_EXECUTADO")
        self.assertEqual(record["results"], [])
        self.assertIsNone(record["conclusion"])

    def test_prefilled_result_is_rejected(self):
        registry = BJIRegistry()
        invalid = experiment()
        invalid["results"] = [{"fabricated": True}]
        with self.assertRaises(ValueError):
            registry.register(invalid)

    def test_round_tracks_inputs_and_keeps_output_empty(self):
        registry = BJIRegistry()
        registry.register(experiment())
        result = registry.register_round("BJI-SYN-01", "R-01", [{"prompt": "synthetic"}], {"expected": "criterion"})
        self.assertEqual(result["status"], "ROUND_REGISTERED")
        self.assertIsNone(result["record"]["output"])
        self.assertIsNone(result["record"]["result"])

    def test_report_is_metadata_only(self):
        registry = BJIRegistry()
        registry.register(experiment())
        registry.register_round("BJI-SYN-01", "R-01", [{"prompt": "synthetic"}], {"expected": "criterion"})
        report = registry.reproducibility_report("BJI-SYN-01")
        self.assertEqual(report["status"], "REPORT_READY")
        self.assertEqual(report["state"], "NAO_EXECUTADO")
        self.assertEqual(report["results"], [])
        self.assertIsNone(report["conclusion"])

    def test_sensitive_input_is_blocked_without_leaking_value(self):
        registry = BJIRegistry()
        registry.register(experiment())
        result = registry.register_round("BJI-SYN-01", "R-02", [{"email": "person@example.com"}], {"expected": "criterion"})
        self.assertEqual(result["status"], "BLOCKED")
        self.assertNotIn("person@example.com", str(result))


if __name__ == "__main__":
    unittest.main()
