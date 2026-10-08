#!/usr/bin/env python3
"""Validate the 2026-10-08 public research intake and registry links."""
from __future__ import annotations

import json
import re
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "references" / "external"
ARXIV_VERSION = re.compile(r"v\d+$", re.IGNORECASE)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class ResearchIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.works = read_jsonl(EXTERNAL / "works.jsonl")
        cls.by_id = {row["id"]: row for row in cls.works}
        cls.audit = json.loads((EXTERNAL / "research-intake-audit-2026-10-08.json").read_text(encoding="utf-8"))
        cls.intake = [row for row in cls.works if 84 <= int(row["id"].split("-")[1]) <= 130]

    def test_ingestion_counts_and_semantic_boundaries(self) -> None:
        counts = self.audit["ingestion"]
        self.assertEqual(counts, {
            "work_records_before": 83,
            "work_records_added": 47,
            "work_records_after": 130,
            "arxiv_papers_added": 34,
            "other_publications_added": 3,
            "pinned_software_snapshots_added": 4,
            "official_vendor_or_model_pages_added": 6,
            "external_claim_rows_before": 26,
            "external_claim_rows_after": 26,
            "knowledge_evidence_rows_before": 26,
            "knowledge_evidence_rows_after": 26,
            "accepted_claims_added": 0,
        })
        self.assertEqual(len(self.intake), 47)
        self.assertEqual(len(read_jsonl(EXTERNAL / "claims.jsonl")), 26)
        self.assertEqual(len(read_jsonl(EXTERNAL / "evidence.jsonl")), 26)
        self.assertFalse(self.audit["semantic_boundaries"]["articles_added"])
        self.assertFalse(self.audit["semantic_boundaries"]["research_findings_added_to_articles"])
        self.assertFalse(self.audit["semantic_boundaries"]["adoption_relationships_asserted"])
        self.assertEqual(self.audit["semantic_boundaries"]["accepted_claims_added"], 0)

    def test_intake_audit_is_a_public_identity_crosswalk_not_a_second_registry(self) -> None:
        self.assertEqual(self.audit["canonical_registry"], "works.jsonl")
        expected_fields = {"work_id", "identity_type", "identity_value", "source_group", "verification_level"}
        self.assertEqual(len(self.audit["records"]), 47)
        self.assertTrue(all(set(row) == expected_fields for row in self.audit["records"]))
        self.assertTrue(all("private" not in row["identity_value"].lower() for row in self.audit["records"]))
        self.assertNotIn("issue_crosswalk", self.audit)
        self.assertNotIn("adoption", self.audit)
        self.assertIn("not a novelty claim or proof of nonexistence", self.audit["coverage_statement"])
        self.assertIn("not world-literature coverage", self.audit["source_data_gaps"][-1])

    def test_all_audit_identities_resolve_to_matching_canonical_work(self) -> None:
        self.assertEqual({row["work_id"] for row in self.audit["records"]}, {row["id"] for row in self.intake})
        for identity in self.audit["records"]:
            work = self.by_id[identity["work_id"]]
            identifiers = work["canonical_identifiers"]
            value = identity["identity_value"]
            kind = identity["identity_type"]
            if kind == "arxiv":
                self.assertEqual(identifiers["arxiv"], value)
                self.assertRegex(work["source_url"], rf"/abs/{re.escape(value)}v\d+$")
                self.assertIsNone(ARXIV_VERSION.search(identifiers["arxiv"]))
            elif kind in {"anthology", "pmlr", "usenix", "model-docs", "website"}:
                field = {"model-docs": "model", "website": "website"}.get(kind, kind)
                self.assertEqual(identifiers[field], value)
            elif kind in {"github", "huggingface"}:
                repo, revision = value.rsplit("@", 1)
                field = "github" if kind == "github" else "huggingface"
                self.assertEqual(identifiers[field], repo)
                self.assertEqual(identifiers["git_commit" if kind == "github" else "revision"], revision)
                self.assertIn(revision, work["source_url"])
            else:
                self.fail(f"unexpected identity type {kind!r}")

    def test_work_ids_and_canonical_aliases_are_unique_and_versions_retained(self) -> None:
        self.assertEqual(len(self.by_id), len(self.works))
        expected_ids = {f"KWRK-{number:06d}" for number in range(84, 131)}
        self.assertEqual({row["id"] for row in self.intake}, expected_ids)

        for field in ("arxiv", "doi", "anthology", "pmlr", "usenix", "github"):
            aliases: dict[str, str] = {}
            for work in self.works:
                value = work.get("canonical_identifiers", {}).get(field)
                if not value:
                    continue
                normalized = value.casefold()
                if field == "arxiv":
                    normalized = ARXIV_VERSION.sub("", normalized)
                self.assertNotIn(normalized, aliases, f"{field} alias duplicated by {work['id']} and {aliases.get(normalized)}")
                aliases[normalized] = work["id"]

        for work in self.intake:
            self.assertEqual(work["status"], "ACTIVE")
            self.assertEqual(work["type"], "ExternalWork")
        self.assertEqual(self.by_id["KWRK-000096"]["canonical_identifiers"]["arxiv"], "2410.03529")
        self.assertEqual(self.by_id["KWRK-000036"]["canonical_identifiers"]["arxiv"], "2510.03215")
        self.assertEqual(self.by_id["KWRK-000055"]["canonical_identifiers"]["arxiv"], "2605.22863")
        self.assertEqual(self.by_id["KWRK-000051"]["canonical_identifiers"]["arxiv"], "2608.20617")
        self.assertEqual(self.by_id["KWRK-000060"]["canonical_identifiers"]["report"], "Aleph Alpha technical report; no arXiv identifier verified")
        self.assertEqual(self.by_id["KWRK-000076"]["canonical_identifiers"]["github"], "tilde-research/momoe-release")

    def test_identity_type_totals_match_the_intake_classification(self) -> None:
        self.assertEqual(Counter(row["identity_type"] for row in self.audit["records"]), {
            "arxiv": 34,
            "anthology": 1,
            "usenix": 1,
            "github": 4,
            "pmlr": 1,
            "website": 3,
            "model-docs": 1,
            "huggingface": 2,
        })


if __name__ == "__main__":
    unittest.main(verbosity=2)
