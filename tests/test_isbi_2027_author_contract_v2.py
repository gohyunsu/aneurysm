import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "configs" / "isbi_2027_author_contract_v2.json"
AUDIT = ROOT / "docs" / "isbi-2027-author-contract-recheck-2026-08-13.md"


class Isbi2027AuthorContractV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.audit = AUDIT.read_text(encoding="utf-8")

    def test_official_sources_and_frozen_snapshots_are_explicit(self) -> None:
        sources = self.contract["official_sources"]
        self.assertEqual(sources["home"]["wordpress_page_id"], 1019)
        self.assertEqual(
            sources["author_instructions"]["wordpress_page_id"], 1026
        )
        self.assertEqual(
            sources["call_for_papers"]["sha256"],
            "0aed86f4a6cc6bf37fd867f869ca01e8c0c4e88c3e30eb83ad2f4dd771538a14",
        )
        for source in sources.values():
            self.assertTrue(source["url"].startswith("https://"))

    def test_deadline_page_limit_and_required_disclosures_fail_closed(self) -> None:
        venue = self.contract["venue"]
        pages = self.contract["page_contract"]
        disclosures = self.contract["mandatory_disclosures"]
        self.assertEqual(venue["regular_paper_deadline"], "2026-10-26T23:59:00-04:00")
        self.assertEqual(venue["review"], "single_blind")
        self.assertEqual(venue["submission_endpoint_status"], "coming_soon")
        self.assertEqual(pages["technical_pages_maximum"], 4)
        self.assertEqual(pages["absolute_pages_maximum"], 5)
        self.assertEqual(pages["optional_fifth_page_fee_usd"], 200)
        self.assertEqual(
            set(pages["fifth_page_allowed_content_only"]),
            {
                "compliance_with_ethical_standards",
                "acknowledgments_and_conflict_of_interest",
                "references",
            },
        )
        self.assertTrue(disclosures["ethics_statement_required_even_when_approval_not_needed"])
        self.assertTrue(disclosures["conflict_or_explicit_absence_disclosure_required"])

    def test_stricter_union_resolves_official_concurrent_review_wording(self) -> None:
        originality = self.contract["authorship_and_originality"]
        self.assertEqual(
            set(originality["aurora_conservative_concurrent_review_scope"]),
            {"conference", "workshop", "journal"},
        )
        self.assertEqual(originality["maximum_first_author_submissions_per_person"], 2)

    def test_legacy_template_is_not_mislabelled_as_2027_specific(self) -> None:
        template = self.contract["template_provenance"]
        self.assertEqual(
            template["archive_internal_readme_title"],
            "ISBI 2021 Paper Submission Templates",
        )
        self.assertTrue(template["organizer_linked_legacy_layout"])
        self.assertTrue(template["active_command_stream_equal"])
        self.assertFalse(template["organizer_published_2027_specific_template_verified"])
        self.assertFalse(template["may_call_archive_a_2027_specific_template"])

    def test_pre_evidence_shell_cannot_be_promoted_by_format_checks(self) -> None:
        manuscript = self.contract["current_private_manuscript_classification"]
        boundary = self.contract["research_boundary"]
        self.assertEqual(manuscript["current_bibliography_style"], "unsrt")
        self.assertFalse(manuscript["uses_upstream_ieeebib_style"])
        self.assertFalse(manuscript["may_be_called_final_isbi_submission_format"])
        self.assertFalse(manuscript["submission_manuscript_active"])
        self.assertEqual(boundary["real_p0_v3_checks_passed"], 0)
        self.assertEqual(boundary["real_p0_v3_checks_required"], 12)
        self.assertFalse(boundary["venue_compliance_is_scientific_evidence"])

    def test_human_readable_audit_exposes_the_same_boundary(self) -> None:
        for marker in (
            "ISBI 2021 Paper Submission Templates",
            "conference/workshop/journal",
            "`unsrt`",
            "0/12",
            "Coming Soon",
            "not a submission manuscript",
        ):
            self.assertIn(marker, self.audit)


if __name__ == "__main__":
    unittest.main()
