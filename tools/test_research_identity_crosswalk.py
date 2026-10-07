#!/usr/bin/env python3
"""Regression tests for the public bibliography identity crosswalk."""
from __future__ import annotations

import copy
import unittest

from reconcile_public_bibliography import build_crosswalk, canonical_key, validate_crosswalk


class CrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = build_crosswalk()

    def test_reconciled_counts_match_the_reviewed_payload(self) -> None:
        coverage = self.document["coverage"]
        self.assertEqual(coverage["KWRK_records_before_reconciliation"], 80)
        self.assertEqual(coverage["KWRK_records_current"], 83)
        self.assertEqual(coverage["DLS_audit_records"], 75)
        self.assertEqual(coverage["matched_identity_count"], 2)
        self.assertEqual(coverage["baseline_union_rows"], 153)
        self.assertEqual(coverage["extra_identity_leads"], 31)
        self.assertEqual(coverage["supplemental_bibliography_only_sources"], 2)
        self.assertEqual(coverage["unique_source_identities"], 186)
        self.assertEqual(coverage["nonpaper_source_pointers"], 14)
        self.assertEqual(coverage["unresolved_names_only"], 14)
        self.assertEqual(coverage["provisional_influence_unverified_candidates"], 12)

    def test_only_two_historical_audit_rows_match_preexisting_works(self) -> None:
        matches = [row for row in self.document["sources"] if row["public_audit_records"] and row["work_records"]]
        self.assertEqual(len(matches), 2)
        self.assertEqual({row["work_records"][0]["id"] for row in matches}, {"KWRK-000001", "KWRK-000066"})

    def test_venue_metadata_difference_is_retained_with_public_sources(self) -> None:
        self.assertEqual(self.document["coverage"]["metadata_field_discrepancies"], 1)
        entry = self.document["field_discrepancies"][0]
        self.assertEqual(entry["canonical_key"], "arxiv:2410.01131")
        venue = entry["fields"][0]
        self.assertEqual(venue["field"], "venue")
        self.assertEqual({item["value"] for item in venue["variants"]}, {"ICLR 2025", "arXiv preprint (2024)"})
        source_ids = {source["id"] for item in venue["variants"] for source in item["sources"] if "id" in source}
        self.assertEqual(source_ids, {"KWRK-000001", "dsl-pub-013"})

    def test_metadata_difference_requires_attributed_variants(self) -> None:
        invalid = copy.deepcopy(self.document)
        del invalid["field_discrepancies"][0]["fields"][0]["variants"][0]["sources"]
        self.assertTrue(any("invalid discrepancy" in error for error in validate_crosswalk(invalid)))

    def test_verified_identity_additions_link_to_canonical_works(self) -> None:
        refs = {
            work["id"]: row["canonical_key"]
            for row in self.document["sources"]
            for work in row["work_records"]
        }
        self.assertIn("KWRK-000081", refs)
        self.assertIn("KWRK-000082", refs)
        self.assertIn("KWRK-000083", refs)

    def test_arxiv_versions_are_preserved_separately_from_identity_keys(self) -> None:
        by_key = {row["canonical_key"]: row for row in self.document["sources"]}
        self.assertEqual(by_key["arxiv:2609.16247"]["arxiv_versions"], ["v2"])
        self.assertEqual(by_key["doi:10.1162/tacl_a_00448"]["arxiv_versions"], ["v4"])
        self.assertEqual(by_key["arxiv:1908.08962"]["arxiv_versions"], ["v1"])

    def test_provisional_candidates_remain_unverified_and_outside_work_registry(self) -> None:
        candidates = self.document["provisional_candidate_register"]
        self.assertEqual(len(candidates), 12)
        self.assertTrue(all(row["influence_status"] == "unverified" for row in candidates))
        self.assertTrue(all(row["work_records"] == [] for row in candidates))
        self.assertTrue(all(row["claim_status"] == "not_accepted" for row in candidates))

    def test_crosswalk_schema_and_identity_contract_validate(self) -> None:
        self.assertEqual(validate_crosswalk(self.document), [])
        invalid = copy.deepcopy(self.document)
        del invalid["sources"][0]["canonical_identifiers"]
        self.assertTrue(any("missing schema fields" in error for error in validate_crosswalk(invalid)))

    def test_count_drift_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.document)
        invalid["coverage"]["unique_source_identities"] = 185
        self.assertTrue(any("unique_source_identities" in error for error in validate_crosswalk(invalid)))

    def test_duplicate_identity_alias_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.document)
        duplicate = copy.deepcopy(invalid["sources"][0])
        invalid["sources"].append(duplicate)
        self.assertTrue(any("duplicate canonical_key" in error for error in validate_crosswalk(invalid)))
        self.assertTrue(any("duplicate stable alias" in error for error in validate_crosswalk(invalid)))

    def test_title_and_author_fallback_collision_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.document)
        duplicate = copy.deepcopy(invalid["sources"][0])
        duplicate["canonical_key"] = "doi:10.9999/different"
        duplicate["canonical_identifiers"] = {"doi": "10.9999/different"}
        duplicate["deduplication_aliases"] = [alias for alias in duplicate["deduplication_aliases"] if alias.startswith("title-author:")]
        invalid["sources"].append(duplicate)
        self.assertTrue(any("unreconciled title+first-author alias" in error for error in validate_crosswalk(invalid)))

    def test_canonical_key_priority_and_arxiv_version_normalization(self) -> None:
        row = {
            "title": "Example",
            "authors": ["First Author"],
            "canonical_identifiers": {"doi": "10.1000/ABC", "arxiv": "2301.01234v7"},
        }
        self.assertEqual(canonical_key(row), "doi:10.1000/abc")
        row["canonical_identifiers"].pop("doi")
        self.assertEqual(canonical_key(row), "arxiv:2301.01234")


if __name__ == "__main__":
    unittest.main(verbosity=2)
