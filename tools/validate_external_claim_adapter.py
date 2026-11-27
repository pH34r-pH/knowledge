#!/usr/bin/env python3
"""Validate the external-claim registry and optionally read public source state."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from source_admission import review_date, review_report, source_reviews
from source_readback import read_arxiv

WORK_RE = re.compile(r"^KWRK-[0-9]{6}$")
CLAIM_RE = re.compile(r"^KCLM-[0-9]{6}$")
EVID_RE = re.compile(r"^KEVD-[0-9]{6}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SOURCE_REVIEWS = "governance/source-reviews.jsonl"
REGISTRY_FILES = (
    "references/external/works.jsonl",
    "references/external/claims.jsonl",
    "references/external/evidence.jsonl",
    SOURCE_REVIEWS,
)
OFFLINE_LEVELS = {
    "OFFLINE_FULL",
    "OFFLINE_CLAIM_EVIDENCE",
    "METADATA_ONLY",
    "ONLINE_REVALIDATION_REQUIRED",
}


def _unique_json_fields(pairs: list[tuple[str, object]]) -> dict:
    fields = {}
    for key, value in pairs:
        if key in fields:
            raise ValueError("duplicate registry JSON field")
        fields[key] = value
    return fields


def load_jsonl(path: Path, raw_bytes: bytes | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    data = path.read_bytes() if raw_bytes is None else raw_bytes
    for lineno, raw in enumerate(data.decode("utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw, object_pairs_hook=_unique_json_fields)
        except ValueError as exc:
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


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _accepted_evidence(evidence: dict[str, Any]) -> bool:
    if evidence.get("status") != "ACCEPTED":
        return False
    audit = evidence.get("audit")
    if not isinstance(audit, dict):
        return False
    return (
        audit.get("resolution") == "PASSED"
        and audit.get("support_span") == "PASSED"
        and audit.get("liveness") in ("PASSED", "ARCHIVED")
        and audit.get("entailment") == "PASSED"
    )


def _supersession_cycles(
    rows: list[dict[str, Any]],
    object_ids: set[str],
    duplicate_ids: set[str],
) -> list[tuple[str, ...]]:
    """Return deterministic cycles in an unambiguous supersession graph."""
    targets: dict[str, str] = {}
    for row in rows:
        rid = row.get("id")
        target = row.get("supersedes")
        if (
            isinstance(rid, str)
            and rid not in duplicate_ids
            and rid in object_ids
            and isinstance(target, str)
            and target in object_ids
            and target != rid
        ):
            targets[rid] = target

    cycles: set[tuple[str, ...]] = set()
    visited: set[str] = set()
    for start in sorted(targets):
        path: list[str] = []
        positions: dict[str, int] = {}
        current = start
        while current in targets and current not in visited and current not in positions:
            positions[current] = len(path)
            path.append(current)
            current = targets[current]
        if current in positions:
            cycle = path[positions[current] :]
            first = min(range(len(cycle)), key=cycle.__getitem__)
            cycles.add(tuple(cycle[first:] + cycle[:first]))
        visited.update(path)
    return sorted(cycles)


def _snapshot_registry(root: Path) -> tuple[bytes, ...]:
    paths = [root / name for name in REGISTRY_FILES]
    if any(path.is_symlink() or not path.resolve().is_relative_to(root.resolve()) for path in paths):
        raise ValueError("canonical registry files must remain within the repository")
    return tuple(
        b"" if name == SOURCE_REVIEWS and not path.exists() else path.read_bytes()
        for name, path in zip(REGISTRY_FILES, paths, strict=True)
    )


def registry_fingerprint(snapshot: tuple[bytes, ...]) -> str:
    digest = hashlib.sha256()
    for name, data in zip(REGISTRY_FILES, snapshot, strict=True):
        digest.update(name.encode() + b"\0")
        digest.update(hashlib.sha256(data).digest())
    return digest.hexdigest()


def _registry_rows(root: Path, snapshot: tuple[bytes, ...]) -> tuple[list[dict], ...]:
    return tuple(load_jsonl(root / name, data) for name, data in zip(REGISTRY_FILES, snapshot, strict=True))


def _validate_rows(root: Path, works: list[dict], claims: list[dict], evidence: list[dict]) -> list[str]:
    errors: list[str] = []
    all_rows = works + claims + evidence
    seen: set[str] = set()
    duplicate_ids: set[str] = set()
    for row in all_rows:
        rid = row.get("id")
        if not isinstance(rid, str):
            errors.append(f"record missing string id: {rid!r}")
            continue
        if rid in seen:
            errors.append(f"duplicate adapter id: {rid}")
            duplicate_ids.add(rid)
        seen.add(rid)

    work_ids = {row.get("id") for row in works if isinstance(row.get("id"), str)}
    claim_ids = {row.get("id") for row in claims if isinstance(row.get("id"), str)}
    evidence_ids = {row.get("id") for row in evidence if isinstance(row.get("id"), str)}

    for row in works:
        rid = str(row.get("id", "<unknown>"))
        if not WORK_RE.fullmatch(rid) or row.get("type") != "ExternalWork":
            errors.append(f"{rid}: invalid ExternalWork identity/type")
        target = row.get("supersedes")
        if target is not None and (not isinstance(target, str) or target not in work_ids or target == rid):
            errors.append(f"{rid}: invalid work supersedes target {target!r}")
        if "source_review" in row or "permitted_uses" in row:
            errors.append(f"{rid}: source policy belongs in the governance review file")
    for cycle in _supersession_cycles(works, work_ids, duplicate_ids):
        errors.append(f"cyclic work supersession: {' -> '.join((*cycle, cycle[0]))}")

    for row in claims:
        rid = str(row.get("id", "<unknown>"))
        if not CLAIM_RE.fullmatch(rid) or row.get("type") != "ExternalClaim":
            errors.append(f"{rid}: invalid ExternalClaim identity/type")
        work_id = row.get("work_id")
        if not isinstance(work_id, str) or work_id not in work_ids:
            errors.append(f"{rid}: broken work_id {work_id!r}")
        target = row.get("supersedes")
        if target is not None and (not isinstance(target, str) or target not in claim_ids or target == rid):
            errors.append(f"{rid}: invalid claim supersedes target {target!r}")
    for cycle in _supersession_cycles(claims, claim_ids, duplicate_ids):
        errors.append(f"cyclic claim supersession: {' -> '.join((*cycle, cycle[0]))}")

    evidence_by_claim: dict[str, list[dict[str, Any]]] = {}
    for row in evidence:
        rid = str(row.get("id", "<unknown>"))
        if not EVID_RE.fullmatch(rid) or row.get("type") != "KnowledgeEvidence":
            errors.append(f"{rid}: invalid KnowledgeEvidence identity/type")
        claim_id = row.get("claim_id")
        if not isinstance(claim_id, str) or claim_id not in claim_ids:
            errors.append(f"{rid}: broken claim_id {claim_id!r}")
        elif isinstance(claim_id, str):
            evidence_by_claim.setdefault(claim_id, []).append(row)
        target = row.get("supersedes")
        if target is not None and (not isinstance(target, str) or target not in evidence_ids or target == rid):
            errors.append(f"{rid}: invalid evidence supersedes target {target!r}")

        level = row.get("offline_validation")
        if not isinstance(level, str) or level not in OFFLINE_LEVELS:
            errors.append(f"{rid}: invalid offline_validation {level!r}")
        local_path = row.get("local_path")
        local_hash = row.get("local_content_sha256")
        if level == "OFFLINE_FULL" and not isinstance(local_path, str):
            errors.append(f"{rid}: OFFLINE_FULL requires local_path")
        if level in ("OFFLINE_FULL", "OFFLINE_CLAIM_EVIDENCE"):
            support_text = row.get("support_text")
            support_hash = row.get("support_text_sha256")
            if not isinstance(support_text, str) or not support_text.strip():
                errors.append(f"{rid}: {level} requires support_text")
            if not isinstance(support_hash, str) or not SHA256_RE.fullmatch(support_hash):
                errors.append(f"{rid}: {level} requires support_text_sha256")
            elif isinstance(support_text, str) and sha256_text(support_text) != support_hash:
                errors.append(f"{rid}: support_text_sha256 mismatch")
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

    for cycle in _supersession_cycles(evidence, evidence_ids, duplicate_ids):
        errors.append(f"cyclic evidence supersession: {' -> '.join((*cycle, cycle[0]))}")

    for row in claims:
        if row.get("status") != "ACCEPTED":
            continue
        rid = str(row.get("id"))
        accepted = [item for item in evidence_by_claim.get(rid, []) if _accepted_evidence(item)]
        if not accepted:
            errors.append(f"{rid}: ACCEPTED claim lacks ACCEPTED evidence with a fully passed citation audit")

    return errors


def _validate_snapshot(root: Path, rows: tuple[list[dict], ...]) -> tuple[list[str], dict[str, dict]]:
    works, claims, evidence, policies = rows
    errors = _validate_rows(root, works, claims, evidence)
    if errors:
        return errors, {}
    try:
        return [], source_reviews(root, works, policies)
    except ValueError as exc:
        return [str(exc)], {}


def validate_adapter(root: Path) -> list[str]:
    errors, _ = _validate_snapshot(root, _registry_rows(root, _snapshot_registry(root)))
    return errors


def _arguments(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--source-report", action="store_true")
    modes.add_argument("--registry-sha256", action="store_true", help="Print the exact registry identity")
    parser.add_argument("--expected-registry-sha256")
    date_or_live = parser.add_mutually_exclusive_group()
    date_or_live.add_argument("--as-of")
    date_or_live.add_argument("--check-live", action="store_true")
    args = parser.parse_args(argv)
    if args.source_report and (not args.expected_registry_sha256 or not (args.as_of or args.check_live)):
        parser.error("--source-report requires --expected-registry-sha256 and --as-of or --check-live")
    if args.source_report and not SHA256_RE.fullmatch(args.expected_registry_sha256):
        parser.error("--expected-registry-sha256 requires a lowercase SHA-256")
    if not args.source_report and (args.expected_registry_sha256 or args.as_of or args.check_live):
        parser.error("source report options require --source-report")
    return args


def _run(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    snapshot = _snapshot_registry(root)
    fingerprint = registry_fingerprint(snapshot)
    if args.registry_sha256:
        print(fingerprint)
        return 0
    if args.source_report and not hmac.compare_digest(fingerprint, args.expected_registry_sha256):
        raise ValueError("registry differs from the independently supplied SHA-256")
    rows = _registry_rows(root, snapshot)
    errors, reviews = _validate_snapshot(root, rows)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"FAILED: {len(errors)} adapter error(s)", file=sys.stderr)
        return 1
    if args.source_report:
        works, claims, evidence, _ = rows
        observed_at = datetime.now(timezone.utc) if args.check_live else None
        as_of = observed_at.date() if observed_at else review_date(args.as_of)
        report = review_report(root, works, claims, evidence, reviews, as_of, read_arxiv if observed_at else None)
        if observed_at:
            report["observed_at"] = observed_at.isoformat()
        print(json.dumps({**report, "registry_sha256": fingerprint}, sort_keys=True))
    else:
        print("OK: external claim adapter integrity valid")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _arguments(argv)
    try:
        return _run(args)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
