import unittest

from PAI_AMOR_SAFETY_SANDBOX_V1.guard import assess_request, guarded_generation


class PaiAmorGuardTests(unittest.TestCase):
    def test_explicit_representation_is_blocked(self):
        result = assess_request("crie uma imagem para representar o PAI AMOR")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("PAI_AMOR_REPRESENTATION_FORBIDDEN", result["reasons"])

    def test_variants_are_blocked(self):
        for prompt in ("avatar do Pai-Amor", "retrato do PaiAmor", "desenho do Father of Love"):
            result = assess_request(prompt)
            self.assertEqual(result["status"], "BLOCKED")

    def test_ambiguous_sacred_request_fails_closed(self):
        result = assess_request("gerar figura do criador divino")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("AMBIGUOUS_SACRED_REPRESENTATION_REQUIRES_REVIEW", result["reasons"])

    def test_blocked_request_never_reaches_generator(self):
        called = {"value": False}

        def generator():
            called["value"] = True
            return "must not exist"

        result = guarded_generation("criar uma silhueta do PAI AMOR", generator)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(called["value"])
        self.assertFalse(result["generated"])

    def test_non_pai_institutional_image_is_allowed(self):
        result = guarded_generation("criar emblema da Universidade do Futuro", lambda: "synthetic-output")
        self.assertEqual(result["status"], "GENERATED_NON_PAI_PURPOSE")
        self.assertTrue(result["generated"])

    def test_logs_do_not_include_prompt(self):
        prompt = "imagem secreta do PAI AMOR"
        result = assess_request(prompt)
        self.assertNotIn(prompt, str(result))


if __name__ == "__main__":
    unittest.main()
