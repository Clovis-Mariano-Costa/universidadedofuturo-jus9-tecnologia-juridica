import unittest

from LEARNING_VERIFICATION_SANDBOX_V1.core import LearningRegistry


class LearningTests(unittest.TestCase):
    def setUp(self):
        self.registry = LearningRegistry()
        self.registry.register_lesson({
            "lesson_id": "LESSON-SYN-01",
            "source": "synthetic source",
            "version": "1.0",
            "exercise": "explain a governance counterexample",
            "criteria": {"substantive": True},
        })

    def test_material_existence_does_not_approve_learning(self):
        attempt = self.registry.submit_attempt("LESSON-SYN-01", "synthetic response")
        self.assertEqual(attempt["record"]["result"], "NAO_TESTADO")

    def test_literal_repetition_cannot_be_approved(self):
        attempt = self.registry.submit_attempt("LESSON-SYN-01", "copied text")
        result = self.registry.evaluate(
            attempt["record"]["attempt_id"],
            result="TESTADO_APROVADO",
            review="human review",
            human_review=True,
            substantive=True,
            literal_repetition=True,
        )
        self.assertEqual(result["status"], "BLOCKED")

    def test_approval_requires_human_substantive_review(self):
        attempt = self.registry.submit_attempt("LESSON-SYN-01", {"answer": "synthetic"})
        result = self.registry.evaluate(
            attempt["record"]["attempt_id"],
            result="TESTADO_APROVADO",
            review="specialist human review",
            human_review=True,
            substantive=True,
        )
        self.assertEqual(result["status"], "EVALUATED")

    def test_reassessment_preserves_prior_attempt(self):
        first = self.registry.submit_attempt("LESSON-SYN-01", "first")
        second = self.registry.reassess("LESSON-SYN-01", "second")
        history = self.registry.history("LESSON-SYN-01")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["attempt_id"], first["record"]["attempt_id"])
        self.assertEqual(history[1]["attempt_id"], second["record"]["attempt_id"])

    def test_human_review_is_required_for_revision_state(self):
        attempt = self.registry.submit_attempt("LESSON-SYN-01", "needs review")
        result = self.registry.evaluate(
            attempt["record"]["attempt_id"],
            result="PRECISA_REVISAO",
            review="review pending",
            human_review=False,
        )
        self.assertEqual(result["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
