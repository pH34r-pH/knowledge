#!/usr/bin/env python3
"""Standard-library regression tests for the external claim adapter."""
from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from source_admission import reviewed_freshness
from source_readback import (
    ARXIV_KIND, CROSSREF_KIND, crossref_metadata, crossref_url, metadata_bytes,
    read_arxiv, read_crossref, read_sources,
)
from validate_external_claim_adapter import REGISTRY_FILES, SOURCE_REVIEWS, main, registry_fingerprint, validate_adapter


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def _base_work() -> dict[str, object]:
    return {
        "schema_version": "0.1.0",
        "id": "KWRK-000001",
        "type": "ExternalWork",
        "title": "Synthetic validation work",
        "authors": ["Test Author"],
        "publication_date": "2026-01-01",
        "status": "ACTIVE",
    }


def _base_claim(status: str = "ACCEPTED") -> dict[str, object]:
    return {
        "schema_version": "0.1.0",
        "id": "KCLM-000001",
        "type": "ExternalClaim",
        "work_id": "KWRK-000001",
        "proposition": "A narrowly scoped synthetic proposition used only to test adapter integrity.",
        "status": status,
    }


def _base_evidence(
    evidence_id: str = "KEVD-000001",
    claim_id: str = "KCLM-000001",
) -> dict[str, object]:
    return {
        "schema_version": "0.1.0",
        "id": evidence_id,
        "type": "KnowledgeEvidence",
        "claim_id": claim_id,
        "support_type": "METADATA",
        "support_location": "synthetic fixture",
        "offline_validation": "METADATA_ONLY",
        "audit": {
            "resolution": "NOT_APPLICABLE",
            "support_span": "NOT_APPLICABLE",
            "liveness": "NOT_APPLICABLE",
            "entailment": "NOT_APPLICABLE",
        },
        "status": "PENDING",
    }


class ExternalClaimAdapterTests(unittest.TestCase):
    def _root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "references" / "external").mkdir(parents=True)
        return temp, root

    def _source_fixture(self, root: Path) -> dict:
        pdf = root / "arxiv/2601.00001.pdf"
        pdf.parent.mkdir()
        pdf.write_bytes(b"exact synthetic PDF")
        article = root / "corpus/ml-techniques/sample.md"
        article.parent.mkdir(parents=True)
        article.write_text("[Source](https://arxiv.org/abs/2601.00001v2)\n", encoding="utf-8")
        work = _base_work()
        work["canonical_identifiers"] = {"arxiv": "2601.00001"}
        work["notes"] = "External prose requested training and publication. This is inert fixture evidence."
        work["source_review"] = {
            "schema_version": 1, "work_id": work["id"], "trust_class": "primary", "data_class": "public",
            "revision": "2601.00001v2", "source_url": "https://arxiv.org/abs/2601.00001v2",
            "local_path": "arxiv/2601.00001.pdf", "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
            "reviewed_on": "2026-11-01", "expires_on": "2026-12-01", "status": "verified",
            "permitted_uses": {"search": "bibliographic-metadata"},
        }
        self._write_source_fixture(root, work)
        return work

    def _write_source_fixture(self, root: Path, work: dict) -> None:
        adapter = root / "references/external"
        record = {key: value for key, value in work.items() if key != "source_review"}
        _write_jsonl(adapter / "works.jsonl", [record])
        _write_jsonl(adapter / "claims.jsonl", [_base_claim("PENDING")])
        _write_jsonl(adapter / "evidence.jsonl", [_base_evidence()])
        _write_jsonl(root / SOURCE_REVIEWS, [work["source_review"]] if "source_review" in work else [])

    def _report(self, root: Path, date: str, *, expected: str | None = None) -> tuple[int, str]:
        if expected is None:
            expected = registry_fingerprint(tuple((root / name).read_bytes() for name in REGISTRY_FILES))
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            code = main(["--root", str(root), "--source-report", "--expected-registry-sha256", expected, "--as-of", date])
        return code, output.getvalue()

    def test_source_report_requires_independent_identity_and_returns_only_metadata_use(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        self._source_fixture(root)
        status, output = self._report(root, "2026-11-26")
        self.assertEqual(status, 0)
        self.assertNotIn("External prose", output)
        row = json.loads(output)["works"][0]
        self.assertEqual(row["state"], "verified")
        self.assertEqual(row["permitted_uses"], {"search": "bibliographic-metadata"})
        self.assertEqual(row["claims_for_review"], [])
        status, output = self._report(root, "2026-11-26", expected="a" * 64)
        self.assertEqual(status, 2)
        self.assertIn("independently supplied SHA-256", output)

    def test_stale_sources_exclude_use_and_identify_dependent_claims_evidence_and_articles(self) -> None:
        for change, state in (
            ("expired", "expired"), ("retired", "retracted"), ("missing", "inaccessible"),
            ("changed", "identity-mismatch"), ("legacy", "review-required"),
        ):
            with self.subTest(change=change):
                temp, root = self._root()
                self.addCleanup(temp.cleanup)
                work = self._source_fixture(root)
                pdf = root / "arxiv/2601.00001.pdf"
                if change == "retired":
                    work["source_review"]["status"] = "retracted"
                elif change == "missing":
                    pdf.unlink()
                elif change == "changed":
                    pdf.write_bytes(b"different synthetic PDF")
                elif change == "legacy":
                    del work["source_review"]
                self._write_source_fixture(root, work)
                status, output = self._report(root, "2026-12-26" if change == "expired" else "2026-11-26")
                self.assertEqual(status, 0, output)
                row = json.loads(output)["works"][0]
                self.assertEqual(row["state"], state)
                self.assertEqual(row["permitted_uses"], {})
                self.assertEqual(row["claims_for_review"], ["KCLM-000001"])
                self.assertEqual(row["evidence_for_review"], ["KEVD-000001"])
                self.assertEqual(row["documents_for_review"], ["corpus/ml-techniques/sample.md"])

    def test_citation_coverage_separates_gaps_from_source_use_decisions(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        work = self._source_fixture(root)
        work["canonical_identifiers"]["doi"] = "10.5555/source"
        self._write_source_fixture(root, work)
        directory = root / "corpus/ml-techniques"
        second = "corpus/ml-techniques/citations.md"
        (root / second).write_text(
            "https://arxiv.org/abs/2601.00001v1 https://arxiv.org/pdf/2601.00001v2.pdf\n"
            "[Alias](http://dx.doi.org/10.5555/SOURCE)\n"
            "[Unknown](https://arxiv.org/abs/2601.00002) https://doi.org/10.5555/Unknown.\n",
            encoding="utf-8",
        )
        (directory.parent / "CITATION-AUDIT.md").write_text(
            "History only https://arxiv.org/abs/2601.00009\n", encoding="utf-8")
        status, output = self._report(root, "2026-12-26")
        self.assertEqual(status, 0, output)
        report = json.loads(output)
        coverage = report["citation_coverage"]
        self.assertEqual(coverage["identifier_count"], 4)
        self.assertEqual(coverage["by_state"], {"active-work": 2, "unregistered": 2})
        arxiv, unknown, doi, unknown_doi = coverage["citations"]
        self.assertEqual(arxiv["documents"], [second, "corpus/ml-techniques/sample.md"])
        self.assertEqual(doi["active_work_ids"], ["KWRK-000001"])
        self.assertEqual(unknown["active_work_ids"], [])
        self.assertEqual(unknown_doi["identifier"], "10.5555/unknown")
        row, = report["works"]
        self.assertEqual(row["documents_for_review"], [second, "corpus/ml-techniques/sample.md"])
        self.assertEqual(row["permitted_uses"], {})

    def test_citation_coverage_reports_retired_and_ambiguous_matches(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        work = self._source_fixture(root)
        registry = root / "references/external/works.jsonl"
        active = json.loads(registry.read_text(encoding="utf-8"))
        historical = {**active, "id": "KWRK-000002", "status": "SUPERSEDED"}
        duplicate = {**active, "id": "KWRK-000003"}
        for rows, state, expected in (
            ([historical], "no-active-work", []),
            ([active, historical], "active-work", [work["id"]]),
            ([active, historical, duplicate], "ambiguous-active-work", [work["id"], duplicate["id"]]),
        ):
            with self.subTest(state=state):
                _write_jsonl(registry, rows)
                _write_jsonl(registry.with_name("claims.jsonl"), [])
                _write_jsonl(registry.with_name("evidence.jsonl"), [])
                _write_jsonl(root / SOURCE_REVIEWS, [])
                status, output = self._report(root, "2026-11-26")
                self.assertEqual(status, 0, output)
                citation, = json.loads(output)["citation_coverage"]["citations"]
                self.assertEqual(citation["state"], state)
                self.assertEqual(citation["active_work_ids"], expected)
                self.assertEqual(citation["work_ids"], sorted(row["id"] for row in rows))

    def test_live_source_change_revokes_uses_and_keeps_historical_registry_intact(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        work = self._source_fixture(root)
        today = datetime.now(timezone.utc).date().isoformat()
        work["source_review"].update({"reviewed_on": today, "expires_on": today})
        self._write_source_fixture(root, work)
        snapshot = tuple((root / name).read_bytes() for name in REGISTRY_FILES)
        expected = registry_fingerprint(snapshot)
        args = ["--root", str(root), "--source-report", "--check-live", "--expected-registry-sha256", expected]
        output = io.StringIO()
        observation = {"state": "revised", "observed_revision": "2601.00001v3"}
        with patch("validate_external_claim_adapter.read_sources", return_value={work["id"]: observation}) as read:
            with redirect_stdout(output):
                self.assertEqual(main(args), 0)
            read.assert_called_once_with([work["source_review"]])
        report = json.loads(output.getvalue())
        row, = report["works"]
        self.assertEqual(report["as_of"], today)
        self.assertEqual(row["live_check"], observation)
        self.assertEqual(row["permitted_uses"], {})
        self.assertEqual(row["claims_for_review"], ["KCLM-000001"])
        self.assertEqual(row["evidence_for_review"], ["KEVD-000001"])
        self.assertEqual(row["documents_for_review"], ["corpus/ml-techniques/sample.md"])
        self.assertEqual(report["reviewed_freshness"], {
            "state": "needs-review", "approved_sources": 1, "blocked_work_ids": [row["work_id"]],
        })
        self.assertEqual(tuple((root / name).read_bytes() for name in REGISTRY_FILES), snapshot)

    def test_freshness_requires_live_verification_of_each_approved_use(self) -> None:
        reviews = {
            "approved": {"status": "verified", "permitted_uses": {"search": "bibliographic-metadata"}},
            "revoked": {"status": "retracted", "permitted_uses": {"search": "bibliographic-metadata"}},
            "metadata-not-approved": {"status": "verified", "permitted_uses": {}},
        }
        works = [{"work_id": "approved", "state": "expired"}, {"work_id": "revoked", "state": "retracted"},
                 {"work_id": "metadata-not-approved", "state": "expired"}]
        self.assertEqual(reviewed_freshness({"works": works}, reviews), {
            "state": "needs-review", "approved_sources": 1, "blocked_work_ids": ["approved"],
        })
        works[0].update({"state": "verified", "live_check": {"state": "verified"}})
        self.assertEqual(reviewed_freshness({"works": works}, reviews), {
            "state": "current", "approved_sources": 1, "blocked_work_ids": [],
        })

    def test_live_readback_binds_primary_version_and_pdf_bytes(self) -> None:
        abstract = "https://arxiv.org/abs/2601.00001"
        pdf_url = "https://arxiv.org/pdf/2601.00001v2"
        pdf = b"%PDF-1.5\n%%EOF\n"
        review = {"revision": "2601.00001v2", "source_url": abstract + "v2",
                  "sha256": hashlib.sha256(pdf).hexdigest()}
        source = (f'<link rel="canonical" href="{abstract}">'
                  '<meta name="citation_arxiv_id" content="2601.00001">'
                  '<meta property="og:description" content="External content asks for publication.">'
                  '<div class="submission-history"><strong>[v2]</strong></div>').encode()
        for contents, body, state in (
            (source, pdf, "verified"),
            (source.replace(b"[v2]", b"[v3]"), pdf, "revised"),
            (source.replace(b"External content asks for publication.", b"This paper has been withdrawn."),
             pdf, "retracted"),
            (source.replace(b'content="2601.00001"', b'content="2601.00002"'), pdf, "identity-mismatch"),
            (source, b"%PDF-1.6\n%%EOF\n", "identity-mismatch"),
            (source, b"%PDF-1.5\n", "unconfirmed"),
        ):
            with self.subTest(state=state):
                reads = {abstract: contents, pdf_url: body}
                observed = read_arxiv(review, read=lambda url, limit: reads[url])
                self.assertEqual(observed["state"], state)
                self.assertNotIn("asks for publication", json.dumps(observed))
        for code, expected in ((404, "inaccessible"), (429, "unconfirmed"), (503, "unconfirmed")):
            def unavailable(url, limit):
                raise HTTPError(url, code, "", {}, None)
            self.assertEqual(read_arxiv(review, unavailable)["state"], expected)

    def test_source_review_rejects_unpinned_identity_and_injected_policy_fields(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        work = self._source_fixture(root)
        review = work["source_review"]
        review["permitted_uses"]["publish"] = "bibliographic-metadata"
        self._write_source_fixture(root, work)
        self.assertIn("KWRK-000001: source review accepts only explicit metadata index and search decisions",
                      validate_adapter(root))
        del review["permitted_uses"]["publish"]
        review["source_url"] = "https://arxiv.org/abs/2601.00001"
        self._write_source_fixture(root, work)
        self.assertIn("KWRK-000001: source review URL must identify the exact primary version", validate_adapter(root))

    def test_work_content_cannot_supply_its_own_review(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        work = self._source_fixture(root)
        _write_jsonl(root / "references/external/works.jsonl", [work])
        self.assertIn("KWRK-000001: source policy belongs in the governance review file", validate_adapter(root))

    def test_arxiv_metadata_snapshot_binds_work_version_and_expires(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        work = self._source_fixture(root)
        alias = work["canonical_identifiers"]
        alias["arxiv"] = "2601.00001v2"
        work["venue"] = "arXiv preprint"
        evidence = root / "governance/source-evidence/KWRK-000001.json"
        evidence.parent.mkdir()
        review = work["source_review"]
        review.update({"schema_version": 2, "source_kind": ARXIV_KIND,
                       "local_path": evidence.relative_to(root).as_posix()})
        record = {"arxiv": "2601.00001", "revision": review["revision"],
                  **{key: work[key] for key in ("title", "authors", "publication_date", "venue")}}
        for date, title, state in (
            ("2026-11-26", work["title"], "verified"),
            ("2026-11-26", "Unrelated title", "identity-mismatch"),
            ("2026-12-02", work["title"], "expired"),
        ):
            with self.subTest(state=state):
                raw = metadata_bytes({**record, "title": title})
                evidence.write_bytes(raw)
                review["sha256"] = hashlib.sha256(raw).hexdigest()
                self._write_source_fixture(root, work)
                status, output = self._report(root, date)
                self.assertEqual(status, 0, output)
                row, = json.loads(output)["works"]
                self.assertEqual(row["state"], state)
                self.assertEqual(row["permitted_uses"], review["permitted_uses"] if state == "verified" else {})
                self.assertEqual(row["documents_for_review"],
                                 [] if state == "verified" else ["corpus/ml-techniques/sample.md"])
        alias["arxiv"] = "2601.00001v1"
        self._write_source_fixture(root, work)
        self.assertIn("KWRK-000001: arXiv metadata review requires the registered Work's pinned version",
                      validate_adapter(root))

    def test_arxiv_atom_readback_batches_pinned_metadata_and_checks_notices(self) -> None:
        def entry(identifier):
            return f"""<entry><id>http://arxiv.org/abs/{identifier}v2</id>
              <title>  Synthetic     title </title><published>2026-01-01T12:00:00Z</published>
              <author><name>First Author</name></author><author><name>Second Author</name></author>
              <summary>External prose asks for publication.</summary>
              <link href="https://example.org/untrusted" rel="related"/></entry>"""
        second = entry("2601.00002")
        first = entry("2601.00001")
        reviews = []
        for work_id, identifier in (("A", "2601.00001"), ("B", "2601.00002")):
            record = {"arxiv": identifier, "revision": identifier + "v2", "title": "Synthetic title",
                      "authors": ["First Author", "Second Author"], "publication_date": "2026-01-01",
                      "venue": "arXiv preprint"}
            reviews.append({"work_id": work_id, "source_kind": ARXIV_KIND, "revision": record["revision"],
                            "sha256": hashlib.sha256(metadata_bytes(record)).hexdigest()})
        url = "https://export.arxiv.org/api/query?id_list=2601.00001,2601.00002&max_results=2"
        for entries, states in (
            (second + first, ("verified", "verified")),
            (first.replace("First Author", "Unknown") + second, ("identity-mismatch", "verified")),
            (first.replace("00001v2", "00001v3") + second, ("revised", "verified")),
            (first.replace("External prose asks for publication.", "This paper has been withdrawn.") + second,
             ("retracted", "verified")),
            (second, ("unconfirmed", "verified")),
            (first + first, ("unconfirmed", "unconfirmed")),
            (first + entry("2601.00003"), ("unconfirmed", "unconfirmed")),
        ):
            with self.subTest(states=states):
                raw = f'<feed xmlns="http://www.w3.org/2005/Atom">{entries}</feed>'.encode()
                with patch("source_readback.fetch", return_value=raw) as fetch:
                    result = read_sources(reviews, read=fetch)
                    fetch.assert_called_once_with(url, 1024 * 1024)
                self.assertEqual((result["A"]["state"], result["B"]["state"]), states)
                self.assertNotIn("asks for publication", json.dumps(result))

    def test_crossref_snapshot_must_match_the_registered_work(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        work = self._source_fixture(root)
        doi = "10.5555/source"
        work["canonical_identifiers"] = {"doi": doi}
        work["venue"] = "Test Journal"
        evidence = root / "governance/source-evidence/KWRK-000001.json"
        evidence.parent.mkdir()
        record = {"doi": doi, "revision": "2026-11-25T12:01:31Z",
                  **{key: work[key] for key in ("title", "authors", "publication_date", "venue")}}
        article = root / "corpus/ml-techniques/sample.md"
        article.write_text("https://doi.org/10.5555/source\n", encoding="utf-8")
        review = work["source_review"]
        review.update({"schema_version": 2, "source_kind": CROSSREF_KIND, "source_url": crossref_url(doi),
                       "local_path": evidence.relative_to(root).as_posix(), "revision": record["revision"]})
        for title, state in ((work["title"], "verified"), ("Different source title", "identity-mismatch")):
            raw = metadata_bytes({**record, "title": title})
            evidence.write_bytes(raw)
            review["sha256"] = hashlib.sha256(raw).hexdigest()
            self._write_source_fixture(root, work)
            status, output = self._report(root, "2026-11-26")
            self.assertEqual(status, 0, output)
            row, = json.loads(output)["works"]
            self.assertEqual(row["state"], state)
            if state == "verified":
                self.assertEqual(row["permitted_uses"], {"search": "bibliographic-metadata"})
            else:
                self.assertEqual(row["permitted_uses"], {})
                self.assertEqual(row["documents_for_review"], ["corpus/ml-techniques/sample.md"])

    def test_crossref_readback_uses_only_pinned_metadata_and_checks_notices(self) -> None:
        doi = "10.5555/source"
        revision = "2026-11-25T12:01:31Z"
        work = {"DOI": doi.upper(), "title": ["Test paper"], "author": [{"family": "Author", "given": "Test"}],
                "published": {"date-parts": [[2026, 11]]}, "deposited": {"date-time": revision},
                "container-title": ["Test Journal"]}
        def response(row):
            return json.dumps({"message-type": "work", "message": row}).encode()
        metadata = crossref_metadata(response(work), doi)
        url = crossref_url(doi)
        review = {"source_url": url, "revision": revision, "sha256": hashlib.sha256(metadata_bytes(metadata)).hexdigest()}
        for metadata_change, state in (
            ({"indexed": {"date-time": "2026-11-26T00:00:00Z"}, "link": [{"URL": "https://example.org"}]}, "verified"),
            ({"DOI": "10.5555/other"}, "identity-mismatch"),
            ({"title": ["Different metadata"]}, "identity-mismatch"),
            ({"deposited": {"date-time": "2026-11-26T00:00:00Z"}}, "revised"),
            ({"updated-by": [{"type": "correction"}]}, "revised"),
            ({"updated-by": [{"type": "retraction"}]}, "retracted"),
            ({"author": []}, "unconfirmed"),
        ):
            with self.subTest(state=state):
                def read(target, limit):
                    self.assertEqual(target, url)
                    return response({**work, **metadata_change})
                self.assertEqual(read_crossref(review, read)["state"], state)

    def test_empty_registry_is_valid(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        for name in ("works.jsonl", "claims.jsonl", "evidence.jsonl"):
            (root / "references" / "external" / name).write_text("", encoding="utf-8")
        self.assertEqual(validate_adapter(root), [])

    def test_accepted_claim_requires_fully_audited_evidence(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        _write_jsonl(root / "references/external/works.jsonl", [_base_work()])
        _write_jsonl(root / "references/external/claims.jsonl", [_base_claim()])
        _write_jsonl(root / "references/external/evidence.jsonl", [])
        errors = validate_adapter(root)
        self.assertIn(
            "KCLM-000001: ACCEPTED claim lacks ACCEPTED evidence with a fully passed citation audit",
            errors,
        )

    def test_valid_offline_claim_evidence_passes(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        support = "This synthetic evidence entails only the synthetic test proposition.\n"
        support_hash = hashlib.sha256(support.encode()).hexdigest()
        _write_jsonl(root / "references/external/works.jsonl", [_base_work()])
        _write_jsonl(root / "references/external/claims.jsonl", [_base_claim()])
        evidence = {
            "schema_version": "0.1.0",
            "id": "KEVD-000001",
            "type": "KnowledgeEvidence",
            "claim_id": "KCLM-000001",
            "support_type": "PARAPHRASE",
            "support_location": "synthetic fixture",
            "support_text": support,
            "support_text_sha256": support_hash,
            "offline_validation": "OFFLINE_CLAIM_EVIDENCE",
            "audit": {
                "resolution": "PASSED",
                "support_span": "PASSED",
                "liveness": "PASSED",
                "entailment": "PASSED",
            },
            "status": "ACCEPTED",
        }
        _write_jsonl(root / "references/external/evidence.jsonl", [evidence])
        self.assertEqual(validate_adapter(root), [])

    def test_support_hash_mismatch_fails(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        _write_jsonl(root / "references/external/works.jsonl", [_base_work()])
        _write_jsonl(root / "references/external/claims.jsonl", [_base_claim("PENDING")])
        evidence = {
            "schema_version": "0.1.0",
            "id": "KEVD-000001",
            "type": "KnowledgeEvidence",
            "claim_id": "KCLM-000001",
            "support_type": "PARAPHRASE",
            "support_location": "synthetic fixture",
            "support_text": "changed",
            "support_text_sha256": "0" * 64,
            "offline_validation": "OFFLINE_CLAIM_EVIDENCE",
            "audit": {
                "resolution": "PASSED",
                "support_span": "PASSED",
                "liveness": "PASSED",
                "entailment": "PASSED",
            },
            "status": "PENDING",
        }
        _write_jsonl(root / "references/external/evidence.jsonl", [evidence])
        self.assertIn("KEVD-000001: support_text_sha256 mismatch", validate_adapter(root))

    def test_real_work_identity_does_not_rescue_failed_entailment(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        support = "The evidence exists, but it does not entail the attributed proposition."
        _write_jsonl(root / "references/external/works.jsonl", [_base_work()])
        _write_jsonl(root / "references/external/claims.jsonl", [_base_claim()])
        evidence = {
            "schema_version": "0.1.0",
            "id": "KEVD-000001",
            "type": "KnowledgeEvidence",
            "claim_id": "KCLM-000001",
            "support_type": "PARAPHRASE",
            "support_location": "synthetic fixture",
            "support_text": support,
            "support_text_sha256": hashlib.sha256(support.encode()).hexdigest(),
            "offline_validation": "OFFLINE_CLAIM_EVIDENCE",
            "audit": {
                "resolution": "PASSED",
                "support_span": "PASSED",
                "liveness": "PASSED",
                "entailment": "FAILED",
            },
            "status": "REJECTED",
        }
        _write_jsonl(root / "references/external/evidence.jsonl", [evidence])
        errors = validate_adapter(root)
        self.assertIn(
            "KCLM-000001: ACCEPTED claim lacks ACCEPTED evidence with a fully passed citation audit",
            errors,
        )

    def test_duplicate_adapter_id_fails_closed(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        duplicate_claim = _base_claim("PENDING")
        duplicate_claim["id"] = "KWRK-000001"
        _write_jsonl(
            root / "references/external/works.jsonl",
            [_base_work(), _base_work()],
        )
        _write_jsonl(root / "references/external/claims.jsonl", [duplicate_claim])
        _write_jsonl(root / "references/external/evidence.jsonl", [])
        errors = validate_adapter(root)
        self.assertEqual(errors.count("duplicate adapter id: KWRK-000001"), 2)

    def test_broken_references_fail_closed(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        work = _base_work()
        work["supersedes"] = "KWRK-999999"
        claim = _base_claim("PENDING")
        claim["work_id"] = "KWRK-999999"
        claim["supersedes"] = "KCLM-999999"
        evidence = _base_evidence()
        evidence["claim_id"] = "KCLM-999999"
        evidence["supersedes"] = "KEVD-999999"
        _write_jsonl(root / "references/external/works.jsonl", [work])
        _write_jsonl(root / "references/external/claims.jsonl", [claim])
        _write_jsonl(root / "references/external/evidence.jsonl", [evidence])

        errors = validate_adapter(root)
        self.assertIn("KWRK-000001: invalid work supersedes target 'KWRK-999999'", errors)
        self.assertIn("KCLM-000001: broken work_id 'KWRK-999999'", errors)
        self.assertIn("KCLM-000001: invalid claim supersedes target 'KCLM-999999'", errors)
        self.assertIn("KEVD-000001: broken claim_id 'KCLM-999999'", errors)
        self.assertIn("KEVD-000001: invalid evidence supersedes target 'KEVD-999999'", errors)

    def test_self_supersession_fails_for_each_record_type(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        work = _base_work()
        work["supersedes"] = "KWRK-000001"
        claim = _base_claim("PENDING")
        claim["supersedes"] = "KCLM-000001"
        evidence = _base_evidence()
        evidence["supersedes"] = "KEVD-000001"
        _write_jsonl(root / "references/external/works.jsonl", [work])
        _write_jsonl(root / "references/external/claims.jsonl", [claim])
        _write_jsonl(root / "references/external/evidence.jsonl", [evidence])

        errors = validate_adapter(root)
        self.assertIn("KWRK-000001: invalid work supersedes target 'KWRK-000001'", errors)
        self.assertIn("KCLM-000001: invalid claim supersedes target 'KCLM-000001'", errors)
        self.assertIn("KEVD-000001: invalid evidence supersedes target 'KEVD-000001'", errors)

    def test_cyclic_supersession_fails_for_each_record_type(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        work_a = _base_work()
        work_a.update({"id": "KWRK-000001", "status": "SUPERSEDED", "supersedes": "KWRK-000002"})
        work_b = _base_work()
        work_b.update({"id": "KWRK-000002", "status": "SUPERSEDED", "supersedes": "KWRK-000001"})
        claim_a = _base_claim("SUPERSEDED")
        claim_a.update({"id": "KCLM-000001", "supersedes": "KCLM-000002"})
        claim_b = _base_claim("SUPERSEDED")
        claim_b.update({"id": "KCLM-000002", "supersedes": "KCLM-000001"})
        evidence_a = _base_evidence("KEVD-000001", "KCLM-000001")
        evidence_a.update({"status": "SUPERSEDED", "supersedes": "KEVD-000002"})
        evidence_b = _base_evidence("KEVD-000002", "KCLM-000002")
        evidence_b.update({"status": "SUPERSEDED", "supersedes": "KEVD-000001"})
        _write_jsonl(root / "references/external/works.jsonl", [work_a, work_b])
        _write_jsonl(root / "references/external/claims.jsonl", [claim_a, claim_b])
        _write_jsonl(root / "references/external/evidence.jsonl", [evidence_a, evidence_b])

        errors = validate_adapter(root)
        self.assertIn(
            "cyclic work supersession: KWRK-000001 -> KWRK-000002 -> KWRK-000001",
            errors,
        )
        self.assertIn(
            "cyclic claim supersession: KCLM-000001 -> KCLM-000002 -> KCLM-000001",
            errors,
        )
        self.assertIn(
            "cyclic evidence supersession: KEVD-000001 -> KEVD-000002 -> KEVD-000001",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
