#!/usr/bin/env python3
"""Build and validate the public bibliography identity crosswalk."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKS_PATH = ROOT / "references/external/works.jsonl"
AUDIT_PATH = ROOT / "reports/domain-scaling-lab-literature-audit-2026-09-01.json"
INPUT_PATH = ROOT / "reports/research-identity-reconciliation-input-2026-10-07.json"
OUTPUT_PATH = ROOT / "reports/public-bibliography-identity-crosswalk-2026-10-07.json"
VERSION_RE = re.compile(r"v([0-9]+)$", re.IGNORECASE)
ARXIV_URL_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/([^?#]+)", re.IGNORECASE)
REQUIRED_SOURCE_FIELDS = {
    "canonical_key",
    "title",
    "authors",
    "publication_date",
    "venue",
    "canonical_identifiers",
    "arxiv_versions",
    "source_urls",
    "work_records",
    "public_audit_records",
    "supplemental_statuses",
    "identity_status",
    "adoption_status",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: expected JSON object")
        rows.append(value)
    return rows


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return " ".join(re.findall(r"[a-z0-9]+", decomposed.lower()))


def normalize_doi(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^doi:\s*", "", value, flags=re.IGNORECASE)
    return value.rstrip(" .;,)").lower()


def normalize_arxiv(value: str) -> str:
    value = value.strip()
    match = ARXIV_URL_RE.search(value)
    if match:
        value = match.group(1).removesuffix(".pdf")
    return VERSION_RE.sub("", value)


def arxiv_version(value: str) -> str | None:
    value = value.strip().removesuffix(".pdf")
    match = VERSION_RE.search(value)
    return f"v{match.group(1)}" if match else None


def source_identifiers(row: dict[str, Any]) -> dict[str, str]:
    identifiers = row.get("canonical_identifiers", {})
    if not isinstance(identifiers, dict):
        raise ValueError("canonical_identifiers must be an object")
    result: dict[str, str] = {}
    for name, value in identifiers.items():
        if not isinstance(value, str) or not value.strip():
            continue
        if name.lower() == "doi":
            result["doi"] = normalize_doi(value)
        elif name.lower() == "arxiv":
            result["arxiv"] = normalize_arxiv(value)
        else:
            result[name] = value.strip()
    arxiv_id = row.get("arxiv_id")
    if isinstance(arxiv_id, str) and arxiv_id.strip():
        result.setdefault("arxiv", normalize_arxiv(arxiv_id))
    return result


def source_versions(row: dict[str, Any]) -> list[str]:
    versions = {str(value) for value in row.get("versions", []) if isinstance(value, str)}
    identifiers = row.get("canonical_identifiers", {})
    arxiv_id = identifiers.get("arxiv") if isinstance(identifiers, dict) else None
    if isinstance(arxiv_id, str):
        version = arxiv_version(arxiv_id)
        if version:
            versions.add(version)
    row_arxiv = row.get("arxiv_id")
    if isinstance(row_arxiv, str):
        version = arxiv_version(row_arxiv)
        if version:
            versions.add(version)
    source_url = row.get("source_url") or row.get("canonical_public_url")
    if isinstance(source_url, str):
        match = ARXIV_URL_RE.search(source_url)
        if match:
            version = arxiv_version(match.group(1))
            if version:
                versions.add(version)
    return sorted(versions, key=lambda value: int(value[1:]) if value.startswith("v") and value[1:].isdigit() else value)


def title_author_alias(title: str, authors: list[str]) -> str | None:
    if not title or not authors or not authors[0]:
        return None
    title_key = normalize_text(title)
    author_key = normalize_text(authors[0])
    if not title_key or not author_key:
        return None
    return f"title-author:{title_key}|{author_key}"


def identity_aliases(row: dict[str, Any]) -> tuple[set[str], str | None]:
    identifiers = source_identifiers(row)
    aliases: set[str] = set()
    if identifiers.get("doi"):
        aliases.add(f"doi:{identifiers['doi']}")
    if identifiers.get("arxiv"):
        aliases.add(f"arxiv:{identifiers['arxiv']}")
    title = str(row.get("title") or row.get("canonical_title") or "")
    authors = row.get("authors") or []
    author_alias = title_author_alias(title, authors)
    return aliases, author_alias


def canonical_key(row: dict[str, Any]) -> str:
    identifiers = source_identifiers(row)
    if identifiers.get("doi"):
        return f"doi:{identifiers['doi']}"
    if identifiers.get("arxiv"):
        return f"arxiv:{identifiers['arxiv']}"
    title = str(row.get("title") or row.get("canonical_title") or "")
    authors = row.get("authors") or []
    alias = title_author_alias(title, authors)
    if alias:
        return alias
    raise ValueError(f"identity lacks DOI, arXiv ID, and title+first-author key: {title!r}")


def _new_group(row: dict[str, Any]) -> dict[str, Any]:
    title = str(row.get("title") or row.get("canonical_title") or "")
    return {
        "title": title,
        "title_aliases": [],
        "authors": [],
        "publication_date": None,
        "venue": None,
        "canonical_identifiers": {},
        "arxiv_versions": [],
        "source_urls": [],
        "work_records": [],
        "public_audit_records": [],
        "supplemental_statuses": [],
        "source_kinds": [],
        "aliases": set(),
        "title_author_aliases": set(),
        "has_work": False,
        "has_audit": False,
    }


def _identities_conflict(group: dict[str, Any], row: dict[str, Any]) -> bool:
    existing = group["canonical_identifiers"]
    incoming = source_identifiers(row)
    return any(existing.get(key) and incoming.get(key) and existing[key] != incoming[key] for key in ("doi", "arxiv"))


def _find_group(
    row: dict[str, Any],
    groups: list[dict[str, Any]],
    stable_alias_map: dict[str, int],
    title_alias_map: dict[str, int],
) -> int | None:
    stable_aliases, title_alias = identity_aliases(row)
    matching = {stable_alias_map[alias] for alias in stable_aliases if alias in stable_alias_map}
    if len(matching) > 1:
        raise ValueError(f"stable identifiers bridge conflicting groups for {canonical_key(row)}")
    if matching:
        return next(iter(matching))
    if title_alias and title_alias in title_alias_map:
        index = title_alias_map[title_alias]
        if not _identities_conflict(groups[index], row):
            return index
    return None


def _append_unique(target: list[Any], values: list[Any]) -> None:
    for value in values:
        if value is not None and value != "" and value not in target:
            target.append(value)


def _merge_row(group: dict[str, Any], row: dict[str, Any], kind: str) -> None:
    title = str(row.get("title") or row.get("canonical_title") or "")
    if title and title != group["title"]:
        _append_unique(group["title_aliases"], [title])
    authors = row.get("authors") or []
    if not group["authors"] and authors:
        group["authors"] = list(authors)
    if not group["publication_date"]:
        group["publication_date"] = row.get("publication_date") or row.get("arxiv_published") or (str(row["year"]) if row.get("year") else None)
    if not group["venue"]:
        group["venue"] = row.get("venue") or None
    for name, value in source_identifiers(row).items():
        if name not in group["canonical_identifiers"]:
            group["canonical_identifiers"][name] = value
    versions = source_versions(row)
    _append_unique(group["arxiv_versions"], versions)
    source_url = row.get("source_url") or row.get("canonical_public_url")
    _append_unique(group["source_urls"], [source_url] if isinstance(source_url, str) else [])
    source_kind = row.get("source_kind") or row.get("source_type") or kind
    _append_unique(group["source_kinds"], [source_kind])
    catalog_status = row.get("catalog_status")
    _append_unique(group["supplemental_statuses"], [catalog_status] if catalog_status else [])
    if kind == "work":
        group["has_work"] = True
        ref = {"id": row["id"], "status": row["status"]}
        _append_unique(group["work_records"], [ref])
    elif kind == "audit":
        group["has_audit"] = True
        ref = {"id": row["record_id"], "status": row.get("resolution_status", "resolved")}
        _append_unique(group["public_audit_records"], [ref])
    stable_aliases, title_alias = identity_aliases(row)
    group["aliases"].update(stable_aliases)
    if title_alias:
        group["title_author_aliases"].add(title_alias)


def _work_row(row: dict[str, Any]) -> dict[str, Any]:
    return {**row, "record_kind": "work"}


def _audit_row(row: dict[str, Any]) -> dict[str, Any]:
    identifiers: dict[str, str] = {}
    if row.get("doi"):
        identifiers["doi"] = row["doi"]
    if row.get("arxiv_id"):
        identifiers["arxiv"] = row["arxiv_id"]
    return {
        **row,
        "title": row.get("canonical_title", ""),
        "canonical_identifiers": identifiers,
        "source_url": row.get("canonical_public_url"),
        "record_kind": "audit",
    }


def _supplemental_row(row: dict[str, Any], kind: str) -> dict[str, Any]:
    return {**row, "record_kind": kind}


def _source_row(group: dict[str, Any]) -> dict[str, Any]:
    identifiers = dict(sorted(group["canonical_identifiers"].items()))
    aliases = sorted(group["aliases"] | group["title_author_aliases"])
    best = {
        "title": group["title"],
        "authors": group["authors"],
        "canonical_identifiers": identifiers,
    }
    status = "recorded_in_works_and_audit" if group["has_work"] and group["has_audit"] else (
        "recorded_in_works" if group["has_work"] else "recorded_in_public_audit" if group["has_audit"] else "supplemental_identity_only"
    )
    return {
        "canonical_key": canonical_key(best),
        "title": group["title"],
        "title_aliases": sorted(group["title_aliases"]),
        "authors": group["authors"],
        "publication_date": group["publication_date"],
        "venue": group["venue"],
        "canonical_identifiers": identifiers,
        "arxiv_versions": sorted(group["arxiv_versions"], key=lambda value: int(value[1:]) if value.startswith("v") and value[1:].isdigit() else value),
        "source_urls": group["source_urls"],
        "work_records": sorted(group["work_records"], key=lambda item: item["id"]),
        "public_audit_records": sorted(group["public_audit_records"], key=lambda item: item["id"]),
        "supplemental_statuses": sorted(group["supplemental_statuses"]),
        "source_kinds": sorted(group["source_kinds"]),
        "identity_status": status,
        "adoption_status": "not_asserted",
        "deduplication_aliases": aliases,
    }


def _snapshot(path: Path, count: int) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "record_count": count,
    }


def build_crosswalk(root: Path = ROOT) -> dict[str, Any]:
    works_path = root / WORKS_PATH.relative_to(ROOT)
    audit_path = root / AUDIT_PATH.relative_to(ROOT)
    input_path = root / INPUT_PATH.relative_to(ROOT)
    output_path = root / OUTPUT_PATH.relative_to(ROOT)
    works = read_jsonl(works_path)
    audit = read_json(audit_path)
    payload = read_json(input_path)
    reported = payload["reported_counts"]
    groups: list[dict[str, Any]] = []
    stable_alias_map: dict[str, int] = {}
    title_alias_map: dict[str, int] = {}

    def add(row: dict[str, Any], kind: str) -> None:
        index = _find_group(row, groups, stable_alias_map, title_alias_map)
        if index is None:
            index = len(groups)
            groups.append(_new_group(row))
        _merge_row(groups[index], row, kind)
        for alias in groups[index]["aliases"]:
            prior = stable_alias_map.get(alias)
            if prior is not None and prior != index:
                raise ValueError(f"duplicate stable identity alias {alias}")
            stable_alias_map[alias] = index
        for alias in groups[index]["title_author_aliases"]:
            title_alias_map.setdefault(alias, index)

    for row in works:
        add(_work_row(row), "work")
    for row in audit.get("resolved_publications", []):
        add(_audit_row(row), "audit")
    baseline_matches = sum(bool(group["work_records"] and group["public_audit_records"]) for group in groups)
    current_work_audit_union_count = len(groups)
    for row in payload.get("identity_leads", []):
        add(_supplemental_row(row, "identity_lead"), "identity_lead")
    for row in payload.get("supplemental_bibliography_only_sources", []):
        add(_supplemental_row(row, "bibliography_only"), "bibliography_only")

    sources = sorted((_source_row(group) for group in groups), key=lambda item: item["canonical_key"])
    supplemental = payload.get("supplemental_bibliography_only_sources", [])
    candidates = [
        {
            **row,
            "influence_status": "unverified",
            "work_records": [],
            "adoption_status": "not_asserted",
            "claim_status": "not_accepted",
        }
        for row in payload.get("provisional_influence_unverified_candidates", [])
    ]
    work_additions = max(0, len(works) - reported["KWRK_records_before_reconciliation"])
    coverage = {
        "KWRK_records_before_reconciliation": reported["KWRK_records_before_reconciliation"],
        "KWRK_records_current": len(works),
        "KWRK_records_added_after_identity_checks": work_additions,
        "DLS_audit_records": len(audit.get("resolved_publications", [])),
        "matched_identity_count": baseline_matches,
        "baseline_union_rows": reported["baseline_union_rows"],
        "current_work_audit_union_rows_before_supplement": current_work_audit_union_count,
        "extra_identity_leads": len(payload.get("identity_leads", [])),
        "supplemental_bibliography_only_sources": len(supplemental),
        "unique_source_identities": len(sources),
        "nonpaper_source_pointers": len(payload.get("nonpaper_source_pointers", [])),
        "unresolved_names_only": len(payload.get("unresolved_names_only", [])),
        "provisional_influence_unverified_candidates": len(candidates),
    }
    return {
        "schema_version": "1.0.0",
        "title": "Public bibliography identity crosswalk",
        "generated_at": payload["generated_at"],
        "scope": payload["scope"],
        "relation_to_canonical_works": "This generated map links public bibliographic identities to canonical ExternalWork IDs and public audit record IDs. The Works registry remains authoritative for Work rows; the historical audit remains authoritative for its audit records. Unregistered leads stay leads here and are not a second Work registry.",
        "deduplication": {
            "priority": ["DOI", "arXiv ID normalized without version", "canonical title + first author"],
            "arxiv_versions_preserved": True,
            "stable_aliases_are_unique_across_source_rows": True,
        },
        "coverage": coverage,
        "semantic_boundaries": {
            "findings_added": False,
            "articles_added": False,
            "accepted_claims_added": 0,
            "adoption_relationships_asserted": False,
            "candidate_influence_status": "unverified",
        },
        "coverage_gaps": [
            "This is a reconciliation of the reviewed public transfer payload and the cited repository records, not a claim of complete world literature coverage.",
            "PR review threads and the inaccessible Notion corpus remain gaps; private provenance is not copied into this public artifact.",
            "This identity crosswalk does not recompute archive status, article citation coverage, research findings, or project adoption.",
        ],
        "input_snapshots": [
            _snapshot(works_path, len(works)),
            _snapshot(audit_path, len(audit.get("resolved_publications", []))),
            _snapshot(input_path, len(payload.get("identity_leads", [])) + len(supplemental)),
        ],
        "sources": sources,
        "nonpaper_source_pointers": payload.get("nonpaper_source_pointers", []),
        "unresolved_names_only": payload.get("unresolved_names_only", []),
        "provisional_candidate_register": candidates,
    }


def validate_crosswalk(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"schema_version", "title", "generated_at", "coverage", "sources", "nonpaper_source_pointers", "unresolved_names_only", "provisional_candidate_register"}
    missing = sorted(required - set(document))
    if missing:
        errors.append(f"missing top-level schema fields: {', '.join(missing)}")
        return errors
    if document.get("schema_version") != "1.0.0":
        errors.append("unsupported crosswalk schema_version")
    coverage = document.get("coverage", {})
    sources = document.get("sources", [])
    if not isinstance(sources, list):
        errors.append("sources must be an array")
        return errors
    keys: set[str] = set()
    stable_aliases: set[str] = set()
    work_ids: set[str] = set()
    title_aliases: dict[str, set[str]] = {}
    for index, row in enumerate(sources):
        if not isinstance(row, dict):
            errors.append(f"sources[{index}] must be an object")
            continue
        missing_fields = sorted(REQUIRED_SOURCE_FIELDS - set(row))
        if missing_fields:
            errors.append(f"sources[{index}] missing schema fields: {', '.join(missing_fields)}")
            continue
        key = row["canonical_key"]
        if not isinstance(key, str) or not key:
            errors.append(f"sources[{index}] canonical_key must be a non-empty string")
        elif key in keys:
            errors.append(f"duplicate canonical_key: {key}")
        keys.add(key)
        if not isinstance(row["authors"], list) or not all(isinstance(author, str) for author in row["authors"]):
            errors.append(f"sources[{index}] authors must be an array of strings")
        if not isinstance(row["canonical_identifiers"], dict):
            errors.append(f"sources[{index}] canonical_identifiers must be an object")
        else:
            try:
                expected_key = canonical_key(row)
                if key != expected_key:
                    errors.append(f"sources[{index}] canonical_key must follow DOI/arXiv/title-author priority")
            except ValueError as exc:
                errors.append(f"sources[{index}] has no valid canonical key: {exc}")
        if not isinstance(row["arxiv_versions"], list) or not all(re.fullmatch(r"v[0-9]+", value) for value in row["arxiv_versions"]):
            errors.append(f"sources[{index}] arxiv_versions must contain explicit vN strings")
        if row["adoption_status"] != "not_asserted":
            errors.append(f"sources[{index}] must not assert adoption")
        if not isinstance(row["work_records"], list) or not isinstance(row["public_audit_records"], list):
            errors.append(f"sources[{index}] work_records and public_audit_records must be arrays")
        for ref in row.get("work_records", []):
            work_id = ref.get("id") if isinstance(ref, dict) else None
            if not isinstance(work_id, str):
                errors.append(f"sources[{index}] has invalid Work reference")
            elif work_id in work_ids:
                errors.append(f"Work ID appears on multiple source rows: {work_id}")
            work_ids.add(work_id)
        for alias in row.get("deduplication_aliases", []):
            if not isinstance(alias, str):
                errors.append(f"sources[{index}] deduplication aliases must be strings")
                continue
            if alias.startswith(("doi:", "arxiv:")) and alias in stable_aliases:
                errors.append(f"duplicate stable alias across source rows: {alias}")
            if alias.startswith(("doi:", "arxiv:")):
                stable_aliases.add(alias)
            if alias.startswith("title-author:"):
                title_aliases.setdefault(alias, set()).add(key)
    for alias, alias_keys in title_aliases.items():
        if len(alias_keys) > 1:
            errors.append(f"unreconciled title+first-author alias: {alias}")
    for field, expected in (
        ("unique_source_identities", len(sources)),
        ("nonpaper_source_pointers", len(document["nonpaper_source_pointers"])),
        ("unresolved_names_only", len(document["unresolved_names_only"])),
        ("provisional_influence_unverified_candidates", len(document["provisional_candidate_register"])),
    ):
        if coverage.get(field) != expected:
            errors.append(f"coverage.{field}={coverage.get(field)!r}, expected {expected}")
    expected_total = coverage.get("baseline_union_rows", 0) + coverage.get("extra_identity_leads", 0) + coverage.get("supplemental_bibliography_only_sources", 0)
    if coverage.get("unique_source_identities") != expected_total:
        errors.append(f"reconciled identity count does not equal baseline + supplemental: {expected_total}")
    if coverage.get("baseline_union_rows") != coverage.get("KWRK_records_before_reconciliation", 0) + coverage.get("DLS_audit_records", 0) - coverage.get("matched_identity_count", 0):
        errors.append("baseline union count does not equal Works + audit - matched identities")
    for index, candidate in enumerate(document["provisional_candidate_register"]):
        if candidate.get("influence_status") != "unverified" or candidate.get("adoption_status") != "not_asserted" or candidate.get("claim_status") != "not_accepted":
            errors.append(f"provisional_candidate_register[{index}] status boundary changed")
        if candidate.get("work_records") != []:
            errors.append(f"provisional_candidate_register[{index}] must not map to a canonical Work")
    semantics = document.get("semantic_boundaries", {})
    if semantics.get("findings_added") is not False or semantics.get("articles_added") is not False or semantics.get("accepted_claims_added") != 0 or semantics.get("adoption_relationships_asserted") is not False:
        errors.append("semantic boundaries must keep findings, adoption, claims, and articles unchanged")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write the deterministic generated crosswalk")
    mode.add_argument("--check", action="store_true", help="check the committed crosswalk against current inputs")
    args = parser.parse_args(argv)
    try:
        document = build_crosswalk()
        errors = validate_crosswalk(document)
        if args.check:
            existing = read_json(OUTPUT_PATH)
            if existing != document:
                errors.append("committed crosswalk differs from generated inputs; run --write")
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            print(f"FAILED: {len(errors)} crosswalk error(s)", file=sys.stderr)
            return 1
        if args.write:
            OUTPUT_PATH.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"OK: {len(document['sources'])} public source identities; {len(document['provisional_candidate_register'])} provisional candidates; {len(document['nonpaper_source_pointers'])} nonpaper pointers")
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
