#!/usr/bin/env python3
"""Independent cases for spec/features/external-claim-adapter/index.md (ECA-FR-001..012).

Expected behavior comes from the specification text, not from the validator's output.
Run with: python tools/test_external_claim_adapter_spec.py
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import socket
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from validate_external_claim_adapter import main, validate_adapter

OK_LINE = "OK: external claim adapter integrity valid"
ACCEPTED_AUDIT = {"resolution": "PASSED", "support_span": "PASSED", "liveness": "PASSED", "entailment": "PASSED"}


def jsonl(rows: list[dict]) -> str:
    return "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)


def work(identifier: str = "KWRK-000001", **extra: object) -> dict:
    return {"id": identifier, "type": "ExternalWork", "title": "Synthetic work", "status": "ACTIVE", **extra}


def claim(identifier: str = "KCLM-000001", work_id: str = "KWRK-000001", status: str = "PENDING", **extra: object) -> dict:
    return {"id": identifier, "type": "ExternalClaim", "work_id": work_id, "proposition": "A synthetic proposition.",
            "status": status, **extra}


def evidence(identifier: str = "KEVD-000001", claim_id: str = "KCLM-000001", level: str = "METADATA_ONLY",
             status: str = "PENDING", audit: dict | None = None, **extra: object) -> dict:
    return {"id": identifier, "type": "KnowledgeEvidence", "claim_id": claim_id, "status": status,
            "offline_validation": level, "audit": audit if audit is not None else dict.fromkeys(ACCEPTED_AUDIT, "NOT_APPLICABLE"),
            **extra}


def support(text: str = "Synthetic supporting text.\n") -> dict:
    return {"support_text": text, "support_text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}


class AdapterSpecCases(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "references/external").mkdir(parents=True)

    def write(self, works=None, claims=None, evidence_rows=None, reviews=None) -> None:
        base = self.root / "references/external"
        (base / "works.jsonl").write_text(jsonl([work()] if works is None else works), encoding="utf-8")
        (base / "claims.jsonl").write_text(jsonl([claim()] if claims is None else claims), encoding="utf-8")
        (base / "evidence.jsonl").write_text(jsonl([] if evidence_rows is None else evidence_rows), encoding="utf-8")
        if reviews is not None:
            (self.root / "governance").mkdir(exist_ok=True)
            (self.root / "governance/source-reviews.jsonl").write_text(jsonl(reviews), encoding="utf-8")

    def run_main(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(["--root", str(self.root), *args])
        return code, out.getvalue(), err.getvalue()

    def errors(self) -> list[str]:
        return validate_adapter(self.root)

    def test_eca_001_registry_files_are_loaded_from_inside_the_root(self) -> None:
        self.write()
        self.assertEqual(self.errors(), [], "an absent source-review file reads as empty")
        (self.root / "references/external/claims.jsonl").unlink()
        code, _, err = self.run_main()
        self.assertEqual(code, 2)
        self.assertIn("ERROR:", err)
        self.write()
        outside = self.root.parent / (self.root.name + "-outside.jsonl")
        outside.write_text("", encoding="utf-8")
        self.addCleanup(outside.unlink)
        (self.root / "references/external/works.jsonl").unlink()
        try:
            os.symlink(outside, self.root / "references/external/works.jsonl")
        except (OSError, NotImplementedError):
            self.skipTest("symbolic links are unavailable on this platform")
        code, _, err = self.run_main()
        self.assertEqual(code, 2)
        self.assertIn("ERROR:", err)

    def test_eca_002_each_line_is_one_strict_json_object(self) -> None:
        self.write()
        works = self.root / "references/external/works.jsonl"
        valid = json.dumps(work())
        cases = {"invalid JSON": valid + "\n{not json}\n", "not an object": valid + "\n[1, 2]\n",
                 "duplicate field": valid + '\n{"id": "KWRK-000002", "id": "KWRK-000003"}\n'}
        for name, text in cases.items():
            with self.subTest(name=name):
                works.write_text(text, encoding="utf-8")
                code, _, err = self.run_main()
                self.assertEqual(code, 2)
                self.assertIn("works.jsonl:2", err)
        works.write_text("\n" + valid + "\n\n   \n", encoding="utf-8")
        self.assertEqual(self.errors(), [], "blank lines are skipped")
        works.write_text("", encoding="utf-8")
        self.write(works=[], claims=[], evidence_rows=[])
        self.assertEqual(self.errors(), [], "empty registries are valid")

    def test_eca_003_identity_type_and_uniqueness(self) -> None:
        for bad in ("KWRK-12", "KWRK-0000001", "kwrk-000001", "KCLM-000001", "KWRK-00000A"):
            with self.subTest(identifier=bad):
                self.write(works=[work(bad)], claims=[])
                self.assertTrue(any(error.startswith(f"{bad}:") for error in self.errors()), self.errors())
        self.write(works=[work(type="ExternalClaim")], claims=[])
        self.assertTrue(any("KWRK-000001:" in error for error in self.errors()))
        self.write(works=[{"type": "ExternalWork", "title": "no id"}], claims=[])
        self.assertTrue(self.errors())
        def duplicates() -> int:
            return sum("KWRK-000001" in error and "duplicate" in error for error in self.errors())

        self.write(works=[work()], claims=[claim("KWRK-000001", status="PENDING")])
        self.assertEqual(duplicates(), 1, "an ID shared across registries is reported once for the second occurrence")
        self.write(works=[work(), work()], claims=[claim("KWRK-000001", status="PENDING")])
        self.assertEqual(duplicates(), 2, "each occurrence after the first is reported")

    def test_eca_005_supersession_is_same_kind_and_acyclic(self) -> None:
        self.write(works=[work("KWRK-000001", status="SUPERSEDED"), work("KWRK-000002", supersedes="KWRK-000001")], claims=[])
        self.assertEqual(self.errors(), [], "a superseded record stays valid")
        self.write(works=[work("KWRK-000001")], claims=[claim(supersedes="KWRK-000001")])
        self.assertTrue(any("KCLM-000001:" in error and "supersedes" in error for error in self.errors()),
                        "a claim cannot supersede a work")
        self.write(works=[work("KWRK-000002", supersedes="KWRK-000003"), work("KWRK-000003", supersedes="KWRK-000004"),
                          work("KWRK-000004", supersedes="KWRK-000002")], claims=[])
        cycles = [error for error in self.errors() if error.startswith("cyclic")]
        self.assertEqual(cycles, ["cyclic work supersession: KWRK-000002 -> KWRK-000003 -> KWRK-000004 -> KWRK-000002"])

    def test_eca_006_offline_levels_and_support_text_binding(self) -> None:
        for level in ("OFFLINE", "offline_full", "", None, 3):
            with self.subTest(level=level):
                self.write(evidence_rows=[evidence(level=level)])
                self.assertTrue(any("KEVD-000001:" in error for error in self.errors()))
        for level in ("METADATA_ONLY", "ONLINE_REVALIDATION_REQUIRED"):
            self.write(evidence_rows=[evidence(level=level)])
            self.assertEqual(self.errors(), [], level)
        self.write(evidence_rows=[evidence(level="OFFLINE_CLAIM_EVIDENCE", **support())])
        self.assertEqual(self.errors(), [])
        for name, fields in {"blank text": support("   \n"), "missing text": {}, "bad hash": {**support(), "support_text_sha256": "0" * 64},
                             "uppercase hash": {**support(), "support_text_sha256": support()["support_text_sha256"].upper()},
                             "short hash": {**support(), "support_text_sha256": "abc"}}.items():
            with self.subTest(name=name):
                self.write(evidence_rows=[evidence(level="OFFLINE_CLAIM_EVIDENCE", **fields)])
                self.assertTrue(any("KEVD-000001:" in error for error in self.errors()), self.errors())
        self.write(evidence_rows=[evidence(level="OFFLINE_FULL", **support())])
        self.assertTrue(any("local_path" in error for error in self.errors()), "full offline needs a local file")

    def test_eca_007_local_evidence_is_bound_to_a_file_inside_the_root(self) -> None:
        (self.root / "evidence").mkdir()
        data = b"exact preserved bytes"
        (self.root / "evidence/source.bin").write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()

        def check(**fields: object) -> list[str]:
            self.write(evidence_rows=[evidence(level="OFFLINE_FULL", **support(), **fields)])
            return self.errors()

        self.assertEqual(check(local_path="evidence/source.bin", local_content_sha256=digest), [])
        bad = {"wrong hash": {"local_path": "evidence/source.bin", "local_content_sha256": "0" * 64},
               "missing hash": {"local_path": "evidence/source.bin"},
               "malformed hash": {"local_path": "evidence/source.bin", "local_content_sha256": digest.upper()},
               "missing file": {"local_path": "evidence/absent.bin", "local_content_sha256": digest},
               "escaping path": {"local_path": "../outside.bin", "local_content_sha256": digest},
               "absolute path": {"local_path": str(self.root.parent / "elsewhere.bin"), "local_content_sha256": digest},
               "blank path": {"local_path": "  ", "local_content_sha256": digest},
               "directory": {"local_path": "evidence", "local_content_sha256": digest}}
        for name, fields in bad.items():
            with self.subTest(name=name):
                self.assertTrue(any("KEVD-000001:" in error for error in check(**fields)), name)

    def test_eca_008_acceptance_needs_one_fully_passed_audit(self) -> None:
        def accepted(**audit: str) -> dict:
            return evidence(level="OFFLINE_CLAIM_EVIDENCE", status="ACCEPTED", audit={**ACCEPTED_AUDIT, **audit}, **support())

        lacking = "KCLM-000001: ACCEPTED claim lacks ACCEPTED evidence with a fully passed citation audit"
        self.write(claims=[claim(status="ACCEPTED")], evidence_rows=[accepted()])
        self.assertEqual(self.errors(), [])
        self.write(claims=[claim(status="ACCEPTED")], evidence_rows=[accepted(liveness="ARCHIVED")])
        self.assertEqual(self.errors(), [], "an archived source satisfies liveness")
        for audit in ({"liveness": "FAILED"}, {"liveness": "NOT_APPLICABLE"}, {"resolution": "FAILED"},
                      {"support_span": "FAILED"}, {"entailment": "FAILED"}, {"entailment": "passed"}):
            with self.subTest(audit=audit):
                self.write(claims=[claim(status="ACCEPTED")], evidence_rows=[accepted(**audit)])
                self.assertIn(lacking, self.errors())
        for fields in ({"status": "PENDING"}, {"status": "REJECTED"}, {"audit": None}):
            with self.subTest(fields=fields):
                row = {**accepted(), **fields}
                if row.get("audit") is None:
                    row.pop("audit")
                self.write(claims=[claim(status="ACCEPTED")], evidence_rows=[row])
                self.assertIn(lacking, self.errors())
        failed = accepted(entailment="FAILED")
        failed["id"], failed["status"] = "KEVD-000002", "REJECTED"
        self.write(claims=[claim(status="ACCEPTED")], evidence_rows=[failed, accepted()])
        self.assertEqual(self.errors(), [], "one qualifying record is enough")
        self.write(claims=[claim(status="PENDING")], evidence_rows=[])
        self.assertEqual(self.errors(), [], "a claim that is not accepted needs no evidence")

    def test_eca_010_command_line_result(self) -> None:
        self.write()
        code, out, err = self.run_main()
        self.assertEqual((code, out.strip(), err), (0, OK_LINE, ""))
        self.write(works=[work("bad-id")], claims=[claim(work_id="KWRK-999999")], evidence_rows=[evidence(level="NOPE")])
        code, out, err = self.run_main()
        self.assertEqual(code, 1)
        lines = err.strip().splitlines()
        errors = [line for line in lines if line.startswith("ERROR: ")]
        self.assertGreaterEqual(len(errors), 3, "all errors from the three registries are reported in one run")
        self.assertEqual(lines[-1], f"FAILED: {len(errors)} adapter error(s)")
        self.assertNotIn(OK_LINE, out)
        (self.root / "references/external/works.jsonl").write_text("{broken\n", encoding="utf-8")
        code, _, err = self.run_main()
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("ERROR: "))

    def test_eca_011_registry_identity_is_a_defined_digest(self) -> None:
        self.write(reviews=[])
        names = ("references/external/works.jsonl", "references/external/claims.jsonl",
                 "references/external/evidence.jsonl", "governance/source-reviews.jsonl")

        def expected() -> str:
            digest = hashlib.sha256()
            for name in names:
                path = self.root / name
                data = path.read_bytes() if path.exists() else b""
                digest.update(name.encode() + b"\0" + hashlib.sha256(data).digest())
            return digest.hexdigest()

        code, out, _ = self.run_main("--registry-sha256")
        self.assertEqual((code, out.strip()), (0, expected()))
        (self.root / "governance/source-reviews.jsonl").unlink()
        self.assertEqual(self.run_main("--registry-sha256")[1].strip(), expected(), "an absent review file counts as empty")
        self.write(works=[work("bad-id")])
        code, out, _ = self.run_main("--registry-sha256")
        self.assertEqual((code, out.strip()), (0, expected()), "the identity is printed without validating records")
        before = out.strip()
        (self.root / "references/external/claims.jsonl").write_text(jsonl([claim(proposition="changed")]), encoding="utf-8")
        self.assertNotEqual(self.run_main("--registry-sha256")[1].strip(), before)

    def test_eca_012_validation_makes_no_network_request(self) -> None:
        self.write(claims=[claim(status="ACCEPTED")],
                   evidence_rows=[evidence(level="OFFLINE_CLAIM_EVIDENCE", status="ACCEPTED", audit=ACCEPTED_AUDIT, **support())])

        def forbidden(*args: object, **kwargs: object) -> None:
            raise AssertionError("network access attempted")

        with patch.object(socket, "socket", forbidden), patch.object(socket, "create_connection", forbidden), \
                patch.object(socket, "getaddrinfo", forbidden):
            code, out, _ = self.run_main()
        self.assertEqual((code, out.strip()), (0, OK_LINE))


if __name__ == "__main__":
    unittest.main()
