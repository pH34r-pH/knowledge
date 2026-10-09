#!/usr/bin/env python3
"""Regression checks for the dated 50-source prior-art intake."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "references/external"


def read_json(name: str) -> dict:
    return json.loads((EXTERNAL / name).read_text(encoding="utf-8"))


class PriorArtClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = (EXTERNAL / "works.jsonl").read_bytes()
        cls.works = [json.loads(line) for line in cls.raw.splitlines() if line.strip()]
        cls.by_id = {work["id"]: work for work in cls.works}
        cls.intake = read_json("prior-art-closure-input-2026-10-09.json")
        cls.audit = read_json("prior-art-closure-audit-2026-10-09.json")
        cls.supplement = read_json("prior-art-closure-supplement-2026-10-09.json")
        cls.review = {row["review_id"]: row for row in cls.audit["records"]}

    def test_all_selected_sources_are_accounted_for_once(self) -> None:
        self.assertEqual(len(self.audit["records"]), 50)
        self.assertEqual(set(self.review), {f"R{i:02d}" for i in range(1, 51)})
        self.assertEqual(self.intake["reviewed_pool_size"], 50)
        self.assertEqual(len(self.intake["candidates"]), 42)
        self.assertEqual(len(self.intake["existing_records"]), 8)
        added = {row["work_id"] for row in self.review.values() if row["disposition"] == "added"}
        self.assertEqual(added, {f"KWRK-{i:06d}" for i in range(201, 243)})
        self.assertEqual(len({row["work_id"] for row in self.review.values()}), 50)

    def test_original_registry_and_dated_snapshot_hashes_are_preserved(self) -> None:
        lines = self.raw.splitlines(keepends=True)
        self.assertGreaterEqual(len(lines), 242)
        original = hashlib.sha256(b"".join(lines[:200])).hexdigest()
        snapshot = hashlib.sha256(b"".join(lines[:242])).hexdigest()
        self.assertEqual(original, self.intake["expected_registry_before"]["sha256"])
        self.assertEqual(original, self.audit["original_registry_prefix_sha256"])
        self.assertEqual(snapshot, self.audit["updated_registry_sha256"])
        self.assertEqual(self.audit["work_records_before"], 200)
        self.assertEqual(self.audit["work_records_added"], 42)
        self.assertEqual(self.audit["work_records_after"], 242)

    def test_candidate_metadata_matches_canonical_works(self) -> None:
        for item in self.intake["candidates"]:
            with self.subTest(review_id=item["review_id"]):
                record = self.review[item["review_id"]]
                work = self.by_id[record["work_id"]]
                for field in ("title", "authors", "publication_date", "venue", "canonical_identifiers", "source_url"):
                    self.assertEqual(work.get(field), item["work"].get(field))
                self.assertTrue(item["review_depth"])
                self.assertEqual(record["primary_url"], work["source_url"])
                self.assertIn(item["review_depth"], work["notes"])

    def test_metadata_corrections_and_communication_family_are_retained(self) -> None:
        self.assertEqual(self.by_id["KWRK-000221"]["publication_date"], "2016-03-29")
        self.assertTrue(self.by_id["KWRK-000221"]["source_url"].endswith("v6"))
        self.assertIn("Symmetry and Geometry", self.by_id["KWRK-000238"]["venue"])
        self.assertEqual(self.audit["metadata_corrections"], self.supplement["metadata_corrections"])
        expected = {"R48": "2609.11365", "R49": "2608.20054", "R50": "2609.17637"}
        for review_id, arxiv_id in expected.items():
            work = self.by_id[self.review[review_id]["work_id"]]
            self.assertEqual(work["canonical_identifiers"]["arxiv"], arxiv_id)
        parent = self.by_id["KWRK-000241"]["notes"]
        self.assertIn("verification remains pending", parent)
        self.assertIn("floor failure", parent)

    def test_source_identity_does_not_promote_scientific_claims(self) -> None:
        boundaries = self.audit["semantic_boundaries"]
        self.assertEqual(boundaries["accepted_claims_added"], 0)
        self.assertEqual(boundaries["knowledge_evidence_added"], 0)
        self.assertEqual(boundaries["independent_replications_completed"], 0)
        self.assertFalse(boundaries["complete_world_literature_coverage_claimed"])
        self.assertFalse(boundaries["private_provenance_included"])
        self.assertEqual(len(self.audit["unresolved_or_excluded"]), 2)

    def test_authoring_helpers_are_not_permanent_workflows(self) -> None:
        workflows = ROOT / ".github/workflows"
        self.assertFalse((workflows / "prepare-prior-art-intake.yml").exists())
        self.assertFalse((workflows / "prepare-prior-art-supplement.yml").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
