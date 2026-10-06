#!/usr/bin/env python3
"""Standard-library regression tests for the external claim adapter."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from validate_external_claim_adapter import validate_adapter


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
