#!/usr/bin/env python3
"""Validate the 2026-10-08 public research intake and registry links."""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path

from source_readback import ACL, anthology_id


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
        historical_prefixes = {
            "claims.jsonl": "376faf391ddbe227e6c52c7dcb6ec98249050de14bf9925b79428792c2614442",
            "evidence.jsonl": "8109d52759db87f6a72846f9e6a63329dd60e0a5ab2d4f540d8e8b20522516ad",
        }
        for name, expected in historical_prefixes.items():
            # The intake owned these bytes. Later append-only corrections have their own scope.
            lines = (EXTERNAL / name).read_bytes().replace(b"\r\n", b"\n").splitlines(keepends=True)
            self.assertEqual(hashlib.sha256(b"".join(lines[:26])).hexdigest(), expected)
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
                previous_id = aliases.get(normalized)
                if previous_id is not None:
                    self._assert_alias_successor(work, self.by_id[previous_id], field)
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

    def test_cachebridge_v2_preserves_the_v1_identity(self) -> None:
        old, current = self.by_id["KWRK-000101"], self.by_id["KWRK-000359"]
        self.assertEqual(current["supersedes"], old["id"])
        self.assertTrue(old["source_url"].endswith("2609.00891v1"))
        self.assertTrue(current["source_url"].endswith("2609.00891v2"))
        self.assertNotEqual(old["title"], current["title"])
        self.assertEqual(old["authors"], current["authors"])

    def test_revised_recurrent_sources_preserve_prior_identity(self) -> None:
        for old_id, new_id in (("KWRK-000189", "KWRK-000362"),
                               ("KWRK-000191", "KWRK-000363"),
                               ("KWRK-000193", "KWRK-000364")):
            with self.subTest(work=old_id):
                old, current = self.by_id[old_id], self.by_id[new_id]
                self.assertEqual(current["supersedes"], old_id)
                self.assertTrue(old["source_url"].endswith("v2"))
                self.assertTrue(current["source_url"].endswith("v3"))
                self.assertEqual(old["authors"], current["authors"])
                self.assertEqual(old["canonical_identifiers"]["arxiv"], current["canonical_identifiers"]["arxiv"])
        self.assertNotEqual(self.by_id["KWRK-000193"]["title"], self.by_id["KWRK-000364"]["title"])

    def test_activation_transfer_v2_preserves_v1_author_history(self) -> None:
        old, current = self.by_id["KWRK-000235"], self.by_id["KWRK-000365"]
        self.assertEqual(current["supersedes"], old["id"])
        self.assertTrue(old["source_url"].endswith("2606.03280v1"))
        self.assertTrue(current["source_url"].endswith("2606.03280v2"))
        self.assertEqual(old["authors"], ["Peiyan Zhang"])
        self.assertEqual(current["authors"], ["Peiyan Zhang", "Jason Xin"])

    def test_journal_metadata_successors_preserve_day_level_history(self) -> None:
        for old_id, new_id, old_date, month in (
            ("KWRK-000181", "KWRK-000366", "2018-08-08", "2018-08"),
            ("KWRK-000183", "KWRK-000367", "2013-03-01", "2013-03"),
            ("KWRK-000219", "KWRK-000368", "2019-02-12", "2019-04"),
        ):
            with self.subTest(work=old_id):
                old, current = self.by_id[old_id], self.by_id[new_id]
                self.assertEqual(current["supersedes"], old_id)
                self.assertEqual(old["publication_date"], old_date)
                self.assertEqual(current["publication_date"], month)
                self.assertEqual(current["canonical_identifiers"], {"doi": old["canonical_identifiers"]["doi"].lower()})
                self.assertEqual(current["authors"], old["authors"])

    def test_crossref_initials_do_not_replace_historical_author_names(self) -> None:
        for old_id, new_id in (("KWRK-000220", "KWRK-000369"), ("KWRK-000226", "KWRK-000370")):
            with self.subTest(work=old_id):
                old, current = self.by_id[old_id], self.by_id[new_id]
                self.assertEqual(current["supersedes"], old_id)
                self.assertNotEqual(old["authors"], current["authors"])
                self.assertEqual(current["canonical_identifiers"]["doi"], old["canonical_identifiers"]["doi"].lower())
                self.assertEqual(len(old["authors"]), len(current["authors"]))

    def _assert_alias_successor(self, work: dict, previous: dict, field: str) -> None:
        self.assertIn(field, ("arxiv", "doi", "pmlr", "anthology"), f"{field} alias duplicated by {work['id']} and {previous['id']}")
        self.assertEqual(work.get("supersedes"), previous["id"])
        if field == "anthology":
            self.assertEqual(work["source_url"], previous["source_url"])
            identifier = anthology_id(work["source_url"])
            self.assertEqual(work["canonical_identifiers"]["doi"], f"10.18653/v1/{identifier.lower()}")
            self.assertEqual(work["canonical_identifiers"]["doi"], previous["canonical_identifiers"]["doi"])
        if field != "arxiv":
            return
        prior = ARXIV_VERSION.search(previous["source_url"])
        current = ARXIV_VERSION.search(work["source_url"])
        identifiers = work["canonical_identifiers"]
        proceedings = identifiers.get("pmlr")
        if prior is None and current is None and proceedings and proceedings == previous["canonical_identifiers"].get("pmlr"):
            self.assertEqual(work["source_url"], f"https://proceedings.mlr.press/{proceedings}.html")
            return
        if prior is None and current is None and work["source_url"].startswith(ACL):
            identifier = anthology_id(work["source_url"])
            self.assertEqual(work["source_url"], previous["source_url"])
            self.assertEqual(identifiers["anthology"], identifier)
            self.assertEqual(identifiers["doi"], f"10.18653/v1/{identifier.lower()}")
            self.assertEqual(identifiers["doi"], previous["canonical_identifiers"]["doi"])
            return
        if previous["id"] == "KWRK-000083":
            self.assertIsNone(prior)
            self.assertIn("(v1)", previous["notes"])
            self.assertEqual(current.group(), "v2")
            return
        self.assertIsNotNone(prior, previous["id"])
        self.assertIsNotNone(current, work["id"])
        self.assertGreater(int(current[0][1:]), int(prior[0][1:]))

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
