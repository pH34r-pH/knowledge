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
        cls.by_arxiv = {str(row["identity_value"]): row for row in cls.records}

    def test_paper_counts_and_source_scope_are_explicit(self) -> None:
        self.assertEqual(
            self.audit["summary"],
            {
                "paper_leads_reviewed": 11,
                "added_to_works": 11,
                "already_present": 0,
                "quarantined": 0,
            },
        )
        self.assertEqual(len(self.records), 11)
        self.assertEqual(self.audit["other_source_input"]["status"], "awaiting_exact_public_urls")
        self.assertIsNone(self.audit["other_source_input"]["government_vendor_repository_pages"])
        self.assertIsNone(self.audit["other_source_input"]["nsf_official_links"])
        self.assertIn("not a total-source count", self.audit["other_source_input"]["note"])

    def test_all_paper_identities_link_to_the_expected_work_and_version(self) -> None:
        self.assertEqual(set(self.by_arxiv), set(EXPECTED))
        for arxiv, (work_id, version) in EXPECTED.items():
            record = self.by_arxiv[arxiv]
            work = self.by_id[work_id]
            identifiers = work["canonical_identifiers"]
            self.assertEqual(record["work_id"], work_id)
            self.assertEqual(record["arxiv_version"], version)
            self.assertEqual(record["source_url"], f"https://arxiv.org/abs/{arxiv}{version}")
            self.assertEqual(work["source_url"], record["source_url"])
            self.assertEqual(identifiers["arxiv"], arxiv)
            self.assertIsNone(ARXIV_VERSION.search(identifiers["arxiv"]))
            self.assertEqual(record["disposition"], "added")
            self.assertEqual(record["verification_level"], "PRIMARY_ARXIV_METADATA")

    def test_work_ids_are_contiguous_and_prior_registry_has_no_matches(self) -> None:
        self.assertEqual(len(self.works), 141)
        self.assertEqual([row["id"] for row in self.works], [f"KWRK-{number:06d}" for number in range(1, 142)])
        prior_ids = {str(row["id"]) for row in self.works[:130]}
        self.assertFalse(prior_ids.intersection(row["work_id"] for row in self.records))

    def test_stable_arxiv_and_doi_aliases_are_unique(self) -> None:
        aliases: dict[tuple[str, str], str] = {}
        for work in self.works:
            identifiers = work.get("canonical_identifiers", {})
            for field in ("arxiv", "doi"):
                value = identifiers.get(field)
                if not value:
                    continue
                normalized = str(value).casefold()
                if field == "arxiv":
                    normalized = ARXIV_VERSION.sub("", normalized)
                alias = (field, normalized)
                self.assertNotIn(alias, aliases, f"duplicate {field} alias on {work['id']} and {aliases.get(alias)}")
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
