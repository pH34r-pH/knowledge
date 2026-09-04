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

    def test_real_work_identity_does_not_rescue_failed_entailment(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        _write_jsonl(root / "references/external/works.jsonl", [_base_work()])
        _write_jsonl(root / "references/external/claims.jsonl", [_base_claim()])
        evidence = {
            "schema_version": "0.1.0",
            "id": "KEVD-000001",
            "type": "KnowledgeEvidence",
            "claim_id": "KCLM-000001",
            "support_type": "PARAPHRASE",
            "support_location": "synthetic fixture",
            "support_text_sha256": "0" * 64,
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


if __name__ == "__main__":
    unittest.main()
