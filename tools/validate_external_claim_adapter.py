#!/usr/bin/env python3
"""Validate the knowledge external-claim adapter without network access."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

WORK_RE = re.compile(r"^KWRK-[0-9]{6}$")
CLAIM_RE = re.compile(r"^KCLM-[0-9]{6}$")
EVID_RE = re.compile(r"^KEVD-[0-9]{6}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
OFFLINE_LEVELS = {
    "OFFLINE_FULL",
    "OFFLINE_CLAIM_EVIDENCE",
    "METADATA_ONLY",
    "ONLINE_REVALIDATION_REQUIRED",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{lineno}: expected an object")
        rows.append(row)
    return rows


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _accepted_evidence(evidence: dict[str, Any]) -> bool:
    if evidence.get("status") != "ACCEPTED":
        return False
    audit = evidence.get("audit")
    if not isinstance(audit, dict):
        return False
    return (
        audit.get("resolution") == "PASSED"
        and audit.get("support_span") == "PASSED"
        and audit.get("liveness") in {"PASSED", "ARCHIVED"}
        and audit.get("entailment") == "PASSED"
    )


def validate_adapter(root: Path) -> list[str]:
    errors: list[str] = []
    adapter = root / "references" / "external"
    works = load_jsonl(adapter / "works.jsonl")
    claims = load_jsonl(adapter / "claims.jsonl")
    evidence = load_jsonl(adapter / "evidence.jsonl")

    all_rows = works + claims + evidence
    seen: set[str] = set()
    for row in all_rows:
        rid = row.get("id")
        if not isinstance(rid, str):
            errors.append(f"record missing string id: {rid!r}")
            continue
        if rid in seen:
            errors.append(f"duplicate adapter id: {rid}")
        seen.add(rid)

    work_ids = {row.get("id") for row in works if isinstance(row.get("id"), str)}
    claim_ids = {row.get("id") for row in claims if isinstance(row.get("id"), str)}
    evidence_ids = {row.get("id") for row in evidence if isinstance(row.get("id"), str)}

    for row in works:
        rid = str(row.get("id", "<unknown>"))
        if not WORK_RE.fullmatch(rid) or row.get("type") != "ExternalWork":
            errors.append(f"{rid}: invalid ExternalWork identity/type")
        target = row.get("supersedes")
        if target is not None and (target not in work_ids or target == rid):
            errors.append(f"{rid}: invalid work supersedes target {target!r}")

    for row in claims:
        rid = str(row.get("id", "<unknown>"))
        if not CLAIM_RE.fullmatch(rid) or row.get("type") != "ExternalClaim":
            errors.append(f"{rid}: invalid ExternalClaim identity/type")
        work_id = row.get("work_id")
        if work_id not in work_ids:
            errors.append(f"{rid}: broken work_id {work_id!r}")
        target = row.get("supersedes")
        if target is not None and (target not in claim_ids or target == rid):
            errors.append(f"{rid}: invalid claim supersedes target {target!r}")

    evidence_by_claim: dict[str, list[dict[str, Any]]] = {}
    for row in evidence:
        rid = str(row.get("id", "<unknown>"))
        if not EVID_RE.fullmatch(rid) or row.get("type") != "KnowledgeEvidence":
            errors.append(f"{rid}: invalid KnowledgeEvidence identity/type")
        claim_id = row.get("claim_id")
        if claim_id not in claim_ids:
            errors.append(f"{rid}: broken claim_id {claim_id!r}")
        elif isinstance(claim_id, str):
            evidence_by_claim.setdefault(claim_id, []).append(row)
        target = row.get("supersedes")
        if target is not None and (target not in evidence_ids or target == rid):
            errors.append(f"{rid}: invalid evidence supersedes target {target!r}")

        level = row.get("offline_validation")
        if level not in OFFLINE_LEVELS:
            errors.append(f"{rid}: invalid offline_validation {level!r}")
        local_path = row.get("local_path")
        local_hash = row.get("local_content_sha256")
        if level == "OFFLINE_FULL" and not isinstance(local_path, str):
            errors.append(f"{rid}: OFFLINE_FULL requires local_path")
        if level in {"OFFLINE_FULL", "OFFLINE_CLAIM_EVIDENCE"}:
            support_hash = row.get("support_text_sha256")
            if not isinstance(support_hash, str) or not SHA256_RE.fullmatch(support_hash):
                errors.append(f"{rid}: {level} requires support_text_sha256")
        if local_path is not None:
            if not isinstance(local_path, str) or not local_path.strip():
                errors.append(f"{rid}: local_path must be a non-empty string")
            else:
                path = (root / local_path).resolve()
                try:
                    path.relative_to(root.resolve())
                except ValueError:
                    errors.append(f"{rid}: local_path escapes repository root")
                    path = None
                if path is not None:
                    if not path.is_file():
                        errors.append(f"{rid}: local evidence file missing: {local_path}")
                    elif not isinstance(local_hash, str) or not SHA256_RE.fullmatch(local_hash):
                        errors.append(f"{rid}: local_path requires local_content_sha256")
                    elif sha256_file(path) != local_hash:
                        errors.append(f"{rid}: local evidence hash mismatch: {local_path}")

    for row in claims:
        if row.get("status") != "ACCEPTED":
            continue
        rid = str(row.get("id"))
        accepted = [item for item in evidence_by_claim.get(rid, []) if _accepted_evidence(item)]
        if not accepted:
            errors.append(f"{rid}: ACCEPTED claim lacks ACCEPTED evidence with a fully passed citation audit")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    try:
        errors = validate_adapter(args.root.resolve())
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"FAILED: {len(errors)} adapter error(s)", file=sys.stderr)
        return 1
    print("OK: external claim adapter integrity valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
