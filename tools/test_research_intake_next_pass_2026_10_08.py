#!/usr/bin/env python3
"""Regression tests for the public paper identity intake supplement."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKS_PATH = ROOT / "references/external/works.jsonl"
AUDIT_PATH = ROOT / "references/external/research-intake-next-pass-2026-10-08.json"
ARXIV_VERSION = re.compile(r"v([0-9]+)$", re.IGNORECASE)

EXPECTED = {
    "2607.17154": ("KWRK-000131", "v2"),
    "2608.00577": ("KWRK-000132", "v2"),
    "2609.40093": ("KWRK-000133", "v1"),
    "2512.19849": ("KWRK-000134", "v2"),
    "2607.17880": ("KWRK-000135", "v1"),
    "2604.26881": ("KWRK-000136", "v1"),
    "2507.14397": ("KWRK-000137", "v2"),
    "2609.19499": ("KWRK-000138", "v2"),
    "2609.25053": ("KWRK-000139", "v1"),
    "2503.04398": ("KWRK-000140", "v5"),
    "2505.11329": ("KWRK-000141", "v5"),
    "2607.13080": ("KWRK-000155", "v1"),
    "2609.08307": ("KWRK-000156", "v1"),
    "2606.21428": ("KWRK-000106", "v3"),
}


def read_works() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in WORKS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class ResearchIntakeNextPassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.works = read_works()
        cls.by_id = {str(row["id"]): row for row in cls.works}
        cls.audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
        cls.records = cls.audit["records"]
        cls.by_arxiv = {
            str(row["identity_value"]): row
            for row in cls.records
            if row.get("identity_type") == "arxiv"
        }

    def test_paper_counts_and_source_scope_are_explicit(self) -> None:
        summary = self.audit["summary"]
        self.assertEqual(summary["prior_paper_leads_reviewed"], 11)
        self.assertEqual(summary["new_source_urls_reviewed"], 35)
        self.assertEqual(summary["new_paper_leads_reviewed"], 3)
        self.assertEqual(summary["new_nonpaper_pointers_reviewed"], 32)
        self.assertEqual(summary["new_source_identities_added_to_works"], 33)
        self.assertEqual(summary["already_present_in_works"], 1)
        self.assertEqual(summary["quarantined"], 1)
        self.assertEqual(summary["total_records"], 46)
        self.assertEqual(summary["works_rows_before_new_source_batch"], 141)
        self.assertEqual(summary["works_rows_after_new_source_batch"], 174)
        self.assertEqual(len(self.records), 46)
        nsf = self.audit["input_groups"]["official_nsf_urls"]
        extra = self.audit["input_groups"]["additional_public_urls"]
        self.assertEqual((len(nsf), len(extra)), (5, 30))
        self.assertEqual(len(set(nsf + extra)), 35)
        batch_records = self.records[11:]
        self.assertEqual(len(batch_records), 35)
        self.assertEqual({row["source_url"] for row in batch_records}, set(nsf + extra))
        retrieval_contract = " ".join(self.audit["maintenance_contract"]["incremental_retrieval"]).casefold()
        self.assertIn("complete every page", retrieval_contract)
        self.assertFalse(self.audit["maintenance_contract"]["service_or_schedule_added"])
        self.assertIn("not claim complete world literature coverage", " ".join(self.audit["coverage_limitations"]))

    def test_all_paper_identities_link_to_the_expected_work_and_version(self) -> None:
        self.assertEqual(set(self.by_arxiv), set(EXPECTED))
        for arxiv, (work_id, version) in EXPECTED.items():
            record = self.by_arxiv[arxiv]
            work = self.by_id[work_id]
            identifiers = work["canonical_identifiers"]
            self.assertEqual(record["work_id"], work_id)
            self.assertEqual(record["arxiv_version"], version)
            if arxiv not in {"2607.13080", "2609.08307", "2606.21428"}:
                self.assertEqual(record["source_url"], f"https://arxiv.org/abs/{arxiv}{version}")
            self.assertEqual(record["canonical_source_url"], f"https://arxiv.org/abs/{arxiv}{version}")
            self.assertEqual(work["source_url"], record["canonical_source_url"])
            self.assertEqual(identifiers["arxiv"], arxiv)
            self.assertIsNone(ARXIV_VERSION.search(identifiers["arxiv"]))
            expected_disposition = "already_present" if arxiv == "2606.21428" else "added"
            self.assertEqual(record["disposition"], expected_disposition)
            self.assertEqual(record["verification_level"], "PRIMARY_ARXIV_METADATA")

    def test_work_ids_are_contiguous_and_prior_registry_has_no_matches(self) -> None:
        self.assertEqual(len(self.works), 174)
        self.assertEqual([row["id"] for row in self.works], [f"KWRK-{number:06d}" for number in range(1, 175)])
        prior_ids = {str(row["id"]) for row in self.works[:130]}
        added_ids = {row["work_id"] for row in self.records if row.get("work_id") and row["disposition"] == "added"}
        self.assertFalse(prior_ids.intersection(added_ids))

    def test_every_nonquarantined_pointer_is_deduplicated_and_linked(self) -> None:
        keys = [row["canonical_key"] for row in self.records if row.get("canonical_key")]
        self.assertEqual(len(keys), len(set(keys)))
        for row in self.records:
            if row["disposition"] == "quarantined":
                self.assertIsNone(row["work_id"])
                self.assertIsNone(row["canonical_key"])
                self.assertIn("page body was not available", row["quarantine_reason"])
            else:
                self.assertIn(row["work_id"], self.by_id)
                self.assertEqual(self.by_id[row["work_id"]]["source_url"], row["canonical_source_url"])

    def test_github_sources_are_commit_pinned(self) -> None:
        snapshots = [row for row in self.records if row["identity_type"] == "github_snapshot"]
        self.assertEqual(len(snapshots), 8)
        for record in snapshots:
            work = self.by_id[record["work_id"]]
            identifiers = work["canonical_identifiers"]
            self.assertRegex(identifiers["git_commit"], r"^[0-9a-f]{40}$")
            self.assertIn(identifiers["git_commit"], work["source_url"])
            self.assertEqual(record["verification_level"], "GITHUB_REPOSITORY_COMMIT")

    def test_vendor_material_is_attributed_without_independent_result_inference(self) -> None:
        boundaries = self.audit["semantic_boundaries"]
        self.assertFalse(boundaries["independent_results_inferred_from_vendor_material"])
        vendor_classes = {
            "vendor_study_press_release",
            "vendor_documentation",
            "vendor_terms",
            "vendor_blog",
            "vendor_page",
            "vendor_explainer",
            "vendor_press_release",
        }
        vendor_rows = [row for row in self.records if row.get("source_class") in vendor_classes]
        self.assertGreaterEqual(len(vendor_rows), 10)
        for row in vendor_rows:
            work = self.by_id[row["work_id"]]
            self.assertIn("vendor", work["notes"].lower())

    def test_stable_source_aliases_are_unique(self) -> None:
        aliases: dict[tuple[str, ...], str] = {}
        for work in self.works:
            identifiers = work.get("canonical_identifiers", {})
            for field in ("arxiv", "doi", "url"):
                value = identifiers.get(field)
                if not value:
                    continue
                normalized = str(value).casefold()
                if field == "arxiv":
                    normalized = ARXIV_VERSION.sub("", normalized)
                alias = (field, normalized)
                self.assertNotIn(alias, aliases, f"duplicate {field} alias on {work['id']} and {aliases.get(alias)}")
                aliases[alias] = str(work["id"])
            repo = identifiers.get("github")
            commit = identifiers.get("git_commit")
            if repo and commit:
                alias = ("github", str(repo).casefold(), str(commit).casefold())
                self.assertNotIn(alias, aliases, f"duplicate GitHub snapshot on {work['id']} and {aliases.get(alias)}")
                aliases[alias] = str(work["id"])

    def test_publisher_doi_and_pending_doi_status_are_preserved(self) -> None:
        faasmoe = self.by_id["KWRK-000136"]
        self.assertEqual(faasmoe["canonical_identifiers"]["doi"], "10.1145/3812836.3814785")
        pending = self.by_id["KWRK-000133"]
        self.assertEqual(pending["canonical_identifiers"]["doi"], "10.48550/arXiv.2609.40093")
        self.assertIn("pending registration", pending["notes"])

    def test_identity_intake_does_not_accept_claims_or_adoption(self) -> None:
        boundaries = self.audit["semantic_boundaries"]
        self.assertFalse(boundaries["research_findings_added_to_articles"])
        self.assertEqual(boundaries["claims_added"], 0)
        self.assertFalse(boundaries["adoption_relationships_asserted"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
