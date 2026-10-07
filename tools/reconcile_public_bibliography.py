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
    "deduplication_aliases",
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
        "metadata_variants": {},
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


def _metadata_source_ref(row: dict[str, Any], kind: str) -> dict[str, str]:
    if kind == "work":
        return {"type": "ExternalWork", "id": row["id"]}
    if kind == "audit":
        return {"type": "public_audit_record", "id": row["record_id"]}
    key = row.get("canonical_key") or canonical_key(row)
    return {"type": "reviewed_transfer_payload", "canonical_key": key}


def _record_metadata_variants(group: dict[str, Any], row: dict[str, Any], kind: str) -> None:
    date = row.get("publication_date") or row.get("arxiv_published") or (str(row["year"]) if row.get("year") else None)
    variants = {
        "title": row.get("title") or row.get("canonical_title"),
        "authors": row.get("authors"),
        "publication_date": date,
        "venue": row.get("venue"),
    }
    source_ref = _metadata_source_ref(row, kind)
    for field, value in variants.items():
        if value is None or value == "" or value == []:
            continue
        field_rows = group["metadata_variants"].setdefault(field, [])
        match = next((item for item in field_rows if item["value"] == value), None)
        if match is None:
            field_rows.append({"value": value, "sources": [source_ref]})
        elif source_ref not in match["sources"]:
            match["sources"].append(source_ref)


def _merge_title_author_dates(group: dict[str, Any], row: dict[str, Any]) -> None:
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


def _merge_canonical_identifiers(group: dict[str, Any], row: dict[str, Any]) -> None:
    for name, value in source_identifiers(row).items():
        if name not in group["canonical_identifiers"]:
            group["canonical_identifiers"][name] = value


def _merge_versions_and_urls(group: dict[str, Any], row: dict[str, Any]) -> None:
    versions = source_versions(row)
    _append_unique(group["arxiv_versions"], versions)
    source_url = row.get("source_url") or row.get("canonical_public_url")
    _append_unique(group["source_urls"], [source_url] if isinstance(source_url, str) else [])


def _merge_publication_metadata(group: dict[str, Any], row: dict[str, Any], kind: str) -> None:
    _record_metadata_variants(group, row, kind)
    _merge_title_author_dates(group, row)
    _merge_canonical_identifiers(group, row)
    _merge_versions_and_urls(group, row)


def _merge_catalog_context(group: dict[str, Any], row: dict[str, Any], kind: str) -> None:
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


def _merge_identity_aliases(group: dict[str, Any], row: dict[str, Any]) -> None:
    stable_aliases, title_alias = identity_aliases(row)
    group["aliases"].update(stable_aliases)
    if title_alias:
        group["title_author_aliases"].add(title_alias)


def _merge_row(group: dict[str, Any], row: dict[str, Any], kind: str) -> None:
    _merge_publication_metadata(group, row, kind)
    _merge_catalog_context(group, row, kind)
    _merge_identity_aliases(group, row)


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
    result = {
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
    discrepancies = [
        {
            "field": field,
            "variants": variants,
            "resolution": "Both public metadata values are retained; the difference is not adjudicated by this identity crosswalk.",
        }
        for field, variants in sorted(group["metadata_variants"].items())
        if len(variants) > 1
    ]
    if discrepancies:
        result["field_discrepancies"] = discrepancies
    return result


def _snapshot(path: Path, count: int) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "record_count": count,
    }


def _add_source_record(
    row: dict[str, Any],
    kind: str,
    groups: list[dict[str, Any]],
    stable_alias_map: dict[str, int],
    title_alias_map: dict[str, int],
) -> None:
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


def _build_source_groups(
    works: list[dict[str, Any]], audit_rows: list[dict[str, Any]], payload: dict[str, Any]
) -> tuple[list[dict[str, Any]], int, int]:
    groups: list[dict[str, Any]] = []
    stable_alias_map: dict[str, int] = {}
    title_alias_map: dict[str, int] = {}
    for row in works:
        _add_source_record(_work_row(row), "work", groups, stable_alias_map, title_alias_map)
    for row in audit_rows:
        _add_source_record(_audit_row(row), "audit", groups, stable_alias_map, title_alias_map)
    baseline_matches = sum(bool(group["work_records"] and group["public_audit_records"]) for group in groups)
    union_count = len(groups)
    for row in payload.get("identity_leads", []):
        _add_source_record(_supplemental_row(row, "identity_lead"), "identity_lead", groups, stable_alias_map, title_alias_map)
    for row in payload.get("supplemental_bibliography_only_sources", []):
        _add_source_record(_supplemental_row(row, "bibliography_only"), "bibliography_only", groups, stable_alias_map, title_alias_map)
    return groups, baseline_matches, union_count


def _assemble_source_summary(
    works: list[dict[str, Any]],
    audit_rows: list[dict[str, Any]],
    payload: dict[str, Any],
    snapshots: list[dict[str, Any]],
) -> dict[str, Any]:
    reported = payload["reported_counts"]
    groups, baseline_matches, current_work_audit_union_count = _build_source_groups(works, audit_rows, payload)
    sources = sorted((_source_row(group) for group in groups), key=lambda item: item["canonical_key"])
    field_discrepancies = [
        {"canonical_key": row["canonical_key"], "fields": row.pop("field_discrepancies")}
        for row in sources
        if row.get("field_discrepancies")
    ]
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
        "DLS_audit_records": len(audit_rows),
        "matched_identity_count": baseline_matches,
        "baseline_union_rows": reported["baseline_union_rows"],
        "current_work_audit_union_rows_before_supplement": current_work_audit_union_count,
        "extra_identity_leads": len(payload.get("identity_leads", [])),
        "supplemental_bibliography_only_sources": len(supplemental),
        "unique_source_identities": len(sources),
        "nonpaper_source_pointers": len(payload.get("nonpaper_source_pointers", [])),
        "unresolved_names_only": len(payload.get("unresolved_names_only", [])),
        "provisional_influence_unverified_candidates": len(candidates),
        "metadata_field_discrepancies": sum(len(item["fields"]) for item in field_discrepancies),
    }
    return {
        "coverage": coverage,
        "field_discrepancies": field_discrepancies,
        "sources": sources,
        "candidates": candidates,
        "input_snapshots": snapshots,
    }


def _crosswalk_document(payload: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
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
        "coverage": summary["coverage"],
        "field_discrepancies": summary["field_discrepancies"],
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
        "input_snapshots": summary["input_snapshots"],
        "sources": summary["sources"],
        "nonpaper_source_pointers": payload.get("nonpaper_source_pointers", []),
        "unresolved_names_only": payload.get("unresolved_names_only", []),
        "provisional_candidate_register": summary["candidates"],
    }


def build_crosswalk(root: Path = ROOT) -> dict[str, Any]:
    works_path = root / WORKS_PATH.relative_to(ROOT)
    audit_path = root / AUDIT_PATH.relative_to(ROOT)
    input_path = root / INPUT_PATH.relative_to(ROOT)
    works = read_jsonl(works_path)
    audit_rows = read_json(audit_path).get("resolved_publications", [])
    payload = read_json(input_path)
    supplemental_count = len(payload.get("identity_leads", [])) + len(payload.get("supplemental_bibliography_only_sources", []))
    snapshots = [
        _snapshot(works_path, len(works)),
        _snapshot(audit_path, len(audit_rows)),
        _snapshot(input_path, supplemental_count),
    ]
    summary = _assemble_source_summary(works, audit_rows, payload, snapshots)
    return _crosswalk_document(payload, summary)


def _required_source_errors(index: int, row: dict[str, Any]) -> list[str]:
    missing = sorted(REQUIRED_SOURCE_FIELDS - set(row))
    if missing:
        return [f"sources[{index}] missing schema fields: {', '.join(missing)}"]
    return []


def _source_identity_errors(index: int, row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    key = row["canonical_key"]
    if not isinstance(key, str) or not key:
        errors.append(f"sources[{index}] canonical_key must be a non-empty string")
    if not isinstance(row["canonical_identifiers"], dict):
        errors.append(f"sources[{index}] canonical_identifiers must be an object")
    else:
        try:
            if key != canonical_key(row):
                errors.append(f"sources[{index}] canonical_key must follow DOI/arXiv/title-author priority")
        except ValueError as exc:
            errors.append(f"sources[{index}] has no valid canonical key: {exc}")

    return errors


def _source_metadata_errors(index: int, row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    authors = row["authors"]
    if not isinstance(authors, list) or not all(isinstance(author, str) for author in authors):
        errors.append(f"sources[{index}] authors must be an array of strings")
    versions = row["arxiv_versions"]
    if not isinstance(versions, list) or not all(isinstance(value, str) and re.fullmatch(r"v[0-9]+", value) for value in versions):
        errors.append(f"sources[{index}] arxiv_versions must contain explicit vN strings")
    if row["adoption_status"] != "not_asserted":
        errors.append(f"sources[{index}] must not assert adoption")
    if not isinstance(row["work_records"], list) or not isinstance(row["public_audit_records"], list):
        errors.append(f"sources[{index}] work_records and public_audit_records must be arrays")
    if not isinstance(row["deduplication_aliases"], list):
        errors.append(f"sources[{index}] deduplication_aliases must be an array")
    return errors


def _source_shape_errors(index: int, row: dict[str, Any]) -> list[str]:
    errors = _required_source_errors(index, row)
    if errors:
        return errors
    errors.extend(_source_identity_errors(index, row))
    errors.extend(_source_metadata_errors(index, row))
    return errors


def _source_key_and_alias_errors(
    index: int,
    row: dict[str, Any],
    keys: set[str],
    stable_aliases: set[str],
    title_aliases: dict[str, set[str]],
) -> list[str]:
    errors: list[str] = []
    key = row["canonical_key"]
    if isinstance(key, str) and key:
        if key in keys:
            errors.append(f"duplicate canonical_key: {key}")
        keys.add(key)
    for alias in row.get("deduplication_aliases", []):
        if not isinstance(alias, str):
            errors.append(f"sources[{index}] deduplication aliases must be strings")
            continue
        if alias.startswith(("doi:", "arxiv:")):
            if alias in stable_aliases:
                errors.append(f"duplicate stable alias across source rows: {alias}")
            stable_aliases.add(alias)
        elif alias.startswith("title-author:") and isinstance(key, str):
            title_aliases.setdefault(alias, set()).add(key)
    return errors


def _work_reference_errors(index: int, row: dict[str, Any], work_ids: set[str]) -> list[str]:
    errors: list[str] = []
    for ref in row.get("work_records", []):
        work_id = ref.get("id") if isinstance(ref, dict) else None
        if not isinstance(work_id, str):
            errors.append(f"sources[{index}] has invalid Work reference")
            continue
        if work_id in work_ids:
            errors.append(f"Work ID appears on multiple source rows: {work_id}")
        work_ids.add(work_id)
    return errors


def _source_rows_errors(sources: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(sources, list):
        return ["sources must be an array"]
    keys: set[str] = set()
    stable_aliases: set[str] = set()
    work_ids: set[str] = set()
    title_aliases: dict[str, set[str]] = {}
    for index, row in enumerate(sources):
        if not isinstance(row, dict):
            errors.append(f"sources[{index}] must be an object")
            continue
        errors.extend(_source_shape_errors(index, row))
        if REQUIRED_SOURCE_FIELDS.issubset(row):
            errors.extend(_source_key_and_alias_errors(index, row, keys, stable_aliases, title_aliases))
            if isinstance(row["work_records"], list):
                errors.extend(_work_reference_errors(index, row, work_ids))
    for alias, alias_keys in title_aliases.items():
        if len(alias_keys) > 1:
            errors.append(f"unreconciled title+first-author alias: {alias}")
    return errors


def _coverage_errors(document: dict[str, Any], coverage: Any, sources: Any) -> list[str]:
    if not isinstance(coverage, dict) or not isinstance(sources, list):
        return ["coverage and sources must be objects/arrays"]
    errors: list[str] = []
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
    discrepancy_fields = sum(len(item.get("fields", [])) for item in document.get("field_discrepancies", []) if isinstance(item, dict))
    if coverage.get("metadata_field_discrepancies") != discrepancy_fields:
        errors.append("coverage.metadata_field_discrepancies does not match retained metadata variants")
    return errors


def _candidate_errors(candidates: Any) -> list[str]:
    if not isinstance(candidates, list):
        return ["provisional_candidate_register must be an array"]
    errors: list[str] = []
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            errors.append(f"provisional_candidate_register[{index}] must be an object")
            continue
        if candidate.get("influence_status") != "unverified" or candidate.get("adoption_status") != "not_asserted" or candidate.get("claim_status") != "not_accepted":
            errors.append(f"provisional_candidate_register[{index}] status boundary changed")
        if candidate.get("work_records") != []:
            errors.append(f"provisional_candidate_register[{index}] must not map to a canonical Work")
    return errors


def _semantic_boundary_errors(semantics: Any) -> list[str]:
    if not isinstance(semantics, dict):
        return ["semantic_boundaries must be an object"]
    if semantics.get("findings_added") is not False or semantics.get("articles_added") is not False or semantics.get("accepted_claims_added") != 0 or semantics.get("adoption_relationships_asserted") is not False:
        return ["semantic boundaries must keep findings, adoption, claims, and articles unchanged"]
    return []


def _field_discrepancy_errors(entries: Any, sources: Any) -> list[str]:
    if not isinstance(entries, list) or not isinstance(sources, list):
        return ["field_discrepancies and sources must be arrays"]
    errors: list[str] = []
    source_keys = {row["canonical_key"] for row in sources if isinstance(row, dict) and isinstance(row.get("canonical_key"), str)}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"field_discrepancies[{index}] must be an object")
            continue
        if entry.get("canonical_key") not in source_keys:
            errors.append(f"field_discrepancies[{index}] references an unknown source")
        fields = entry.get("fields")
        if not isinstance(fields, list) or not fields:
            errors.append(f"field_discrepancies[{index}].fields must be a non-empty array")
            continue
        for discrepancy in fields:
            if not isinstance(discrepancy, dict) or not _field_discrepancy_is_valid(discrepancy):
                errors.append(f"field_discrepancies[{index}] contains an invalid discrepancy")
    return errors


def _field_discrepancy_is_valid(discrepancy: dict[str, Any]) -> bool:
    variants = discrepancy.get("variants")
    if discrepancy.get("field") not in {"title", "authors", "publication_date", "venue"}:
        return False
    if not isinstance(variants, list) or len(variants) < 2 or not discrepancy.get("resolution"):
        return False
    values: set[str] = set()
    for variant in variants:
        if not isinstance(variant, dict) or not isinstance(variant.get("sources"), list) or not variant["sources"]:
            return False
        values.add(json.dumps(variant.get("value"), ensure_ascii=False, sort_keys=True))
    return len(values) == len(variants)


def validate_crosswalk(document: dict[str, Any]) -> list[str]:
    required = {"schema_version", "title", "generated_at", "coverage", "sources", "field_discrepancies", "nonpaper_source_pointers", "unresolved_names_only", "provisional_candidate_register"}
    missing = sorted(required - set(document))
    if missing:
        return [f"missing top-level schema fields: {', '.join(missing)}"]
    errors = []
    if document.get("schema_version") != "1.0.0":
        errors.append("unsupported crosswalk schema_version")
    sources = document["sources"]
    errors.extend(_source_rows_errors(sources))
    errors.extend(_coverage_errors(document, document["coverage"], sources))
    errors.extend(_field_discrepancy_errors(document["field_discrepancies"], sources))
    errors.extend(_candidate_errors(document["provisional_candidate_register"]))
    errors.extend(_semantic_boundary_errors(document.get("semantic_boundaries")))
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
