import unittest

from UNIVERSIDADE_AUTOMACAO_SANDBOX_V1.houses import (
    SYMBOLIC_MILESTONE,
    audit_houses,
    automation_report,
    inventory_houses,
    map_house,
    prepare_citat_sync,
    validate_specialization,
)


def house(member_id="M-01", **overrides):
    value = {
        "member_id": member_id,
        "member_label": "synthetic member",
        "casa_lar": {"drive_id": "drive-synthetic", "url": "https://drive.google.com/drive/folders/synthetic"},
        "casa_trabalho": {"repository": "synthetic/repo", "path": "member"},
        "citat": {"document_id": "CITAT-01", "version": "1.0", "hash": "hash-01", "authorized_sync": True, "source_ref": "drive:CITAT-01"},
        "specialties": [],
        "automations": [],
        "marco_simbolico": SYMBOLIC_MILESTONE,
        "created_at": "2026-08-23T00:00:00-03:00",
        "updated_at": "2026-08-23T00:00:00-03:00",
    }
    value.update(overrides)
    return value


class HouseAutomationTests(unittest.TestCase):
    def test_inventory_is_deterministic_and_read_only(self):
        result = inventory_houses([house("M-02"), house("M-01")])
        self.assertEqual(result["status"], "READY_FOR_REVIEW")
        self.assertEqual([row["member_id"] for row in result["records"]], ["M-01", "M-02"])
        self.assertTrue(result["inventory_sha256"])
        self.assertEqual(result["records"][0]["marco_simbolico"], SYMBOLIC_MILESTONE)

    def test_inventory_blocks_sensitive_metadata(self):
        result = inventory_houses([house(casa_trabalho={"repository": "synthetic/repo", "password": "secret-value"})])
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("SENSITIVE_METADATA", {item["reason"] for item in result["errors"]})
        self.assertNotIn("secret-value", str(result))

    def test_map_never_promotes_domestic_content(self):
        mapped = map_house(house())
        self.assertEqual(mapped["content_sync"], "FORBIDDEN_BY_DEFAULT")
        self.assertNotIn("domestic_documents", mapped)

    def test_citat_sync_requires_authorization_and_limits_fields(self):
        source = house()["citat"]
        blocked = prepare_citat_sync({**source, "domestic_documents": ["private"]}, {})
        self.assertEqual(blocked["status"], "BLOCKED")
        self.assertEqual(blocked["reason"], "DOMESTIC_OR_SECRET_CONTENT_FORBIDDEN")

    def test_citat_hash_divergence_is_quarantined_without_overwrite(self):
        result = prepare_citat_sync(house()["citat"], {"document_id": "CITAT-01", "hash": "different"})
        self.assertEqual(result["status"], "QUARANTINED_CONFLICT")
        self.assertEqual(result["content_action"], "NO_MOVE_NO_DELETE")

    def test_specialization_requires_path_evidence_reviewer_and_review_date(self):
        valid = validate_specialization({
            "specialty_id": "S-01",
            "path": "documented_work",
            "scope": "offline audit",
            "evidence": ["artifact-hash"],
            "reviewer": "synthetic-reviewer",
            "review_at": "2027-08-23",
        })
        self.assertTrue(valid["valid"])
        invalid = validate_specialization({"specialty_id": "S-02", "path": "title_only"})
        self.assertFalse(invalid["valid"])

    def test_audit_is_read_only_and_hashes_each_record(self):
        report = audit_houses([house()], checked_at="2026-08-23T12:00:00-03:00")
        self.assertEqual(report["mode"], "READ_ONLY")
        self.assertFalse(report["external_effect"])
        self.assertTrue(report["entries"][0]["record_sha256"])
        self.assertTrue(report["report_sha256"])

    def test_automation_report_exposes_scope_and_rollback(self):
        report = automation_report(
            responsible="synthetic-owner",
            purpose="monthly audit",
            access="metadata-only",
            risks=["hash divergence"],
        )
        self.assertEqual(report["state"], "SANDBOX_READY_FOR_REVIEW")
        self.assertEqual(report["external_effect"], False)
        self.assertTrue(report["rollback"])


if __name__ == "__main__":
    unittest.main()
