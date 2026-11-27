"""Offline source review and dependency impact for the existing Work registry."""
from __future__ import annotations

import hashlib
import re
from collections import Counter
from collections.abc import Callable
from datetime import date
from pathlib import Path, PurePosixPath

from reconcile_public_bibliography import normalize_arxiv, normalize_doi

REVIEW_FIELDS = {
    "schema_version", "work_id", "trust_class", "data_class", "revision", "source_url",
    "local_path", "sha256", "reviewed_on", "expires_on", "status", "permitted_uses",
}
REVIEW_STATES = ("verified", "unconfirmed", "inaccessible", "revised", "retracted")
METADATA_USES = {"index", "search"}
PERMITTED_SCOPE = "bibliographic-metadata"
SHA256_RE = re.compile(r"[0-9a-f]{64}")
ARXIV_VERSION = re.compile(r"v[1-9][0-9]*$")
CITATION_LINKS = {
    "arxiv": re.compile(r"(?<![\w/])https?://arxiv\.org/(?:abs|pdf)/"
                        r"([0-9]{4}\.[0-9]{4,5})(?:v[1-9][0-9]*)?(?:\.pdf)?(?![0-9a-z/])", re.I),
    "doi": re.compile(r"(?<![\w/])https?://(?:dx\.)?doi\.org/(10\.[0-9]{4,9}/[-._;()/:a-z0-9+]+)", re.I),
}
NORMALIZE_CITATION = {"arxiv": normalize_arxiv, "doi": normalize_doi}
CORPUS_PILLARS = ("design-patterns", "ml-techniques", "adjacent-knowledge")
LiveReview = Callable[[dict], dict]
Citation = tuple[str, str]


def review_date(value: object) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("expected an ISO calendar date")
    return date.fromisoformat(value)


def _source_path(root: Path, value: object) -> Path:
    if not isinstance(value, str) or any(char in value for char in "\\:\r\n\x00"):
        raise ValueError("reviewed local source must be a normalized file under arxiv/")
    relative = PurePosixPath(value)
    if (
        len(relative.parts) != 2 or relative.parts[0] != "arxiv"
        or relative.suffix != ".pdf" or value != relative.as_posix()
    ):
        raise ValueError("reviewed local source must be a normalized file under arxiv/")
    path = root / value
    if path.is_symlink() or path.parent.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("reviewed local source must be an ordinary retained file")
    return path


def _pinned_identity(work: dict, review: dict) -> None:
    identifiers = work.get("canonical_identifiers")
    arxiv = identifiers.get("arxiv") if isinstance(identifiers, dict) else None
    revision = review["revision"]
    source_url = review["source_url"]
    digest = review["sha256"]
    if not isinstance(arxiv, str) or not isinstance(revision, str):
        raise ValueError("source review requires an exact version of the registered arXiv work")
    base = ARXIV_VERSION.sub("", arxiv)
    if (
        not re.fullmatch(r"[0-9]{4}\.[0-9]{4,5}", base)
        or not re.fullmatch(re.escape(base) + r"v[1-9][0-9]*", revision)
    ):
        raise ValueError("source review requires an exact version of the registered arXiv work")
    if source_url != f"https://arxiv.org/abs/{revision}":
        raise ValueError("source review URL must identify the exact primary version")
    if review["local_path"] != f"arxiv/{base}.pdf":
        raise ValueError("source review must bind the retained PDF for the registered arXiv work")
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        raise ValueError("source review requires the full SHA-256 of the retained source")


def _metadata_uses(value: object) -> None:
    if not isinstance(value, dict) or not set(value) <= METADATA_USES:
        raise ValueError("source review accepts only explicit metadata index and search decisions")
    if any(scope != PERMITTED_SCOPE for scope in value.values()):
        raise ValueError("source review accepts only bibliographic metadata use")


def _validate_source_review(root: Path, work: dict, review: dict) -> None:
    if not isinstance(review, dict) or set(review) != REVIEW_FIELDS:
        raise ValueError("source review has missing or unrecognized fields")
    if type(review["schema_version"]) is not int or review["schema_version"] != 1:
        raise ValueError("unsupported source review version")
    if review["trust_class"] != "primary" or review["data_class"] != "public":
        raise ValueError("this source-review profile requires a public primary source")
    if review["status"] not in REVIEW_STATES:
        raise ValueError("source review requires a recognized freshness or retraction state")
    if review_date(review["reviewed_on"]) > review_date(review["expires_on"]):
        raise ValueError("source review expiry precedes its review date")
    _pinned_identity(work, review)
    _source_path(root, review["local_path"])
    _metadata_uses(review["permitted_uses"])


def source_reviews(root: Path, works: list[dict], reviews: list[dict]) -> dict[str, dict]:
    by_id = {row["id"]: row for row in works}
    by_work = {}
    for row in reviews:
        work_id = row.get("work_id")
        if not isinstance(work_id, str) or work_id not in by_id or work_id in by_work:
            raise ValueError("duplicate source review or review without a registered Work")
        try:
            _validate_source_review(root, by_id[work_id], row)
        except ValueError as exc:
            raise ValueError(f"{work_id}: {exc}") from None
        by_work[work_id] = row
    return by_work


def _source_state(root: Path, work: dict, review: dict | None, as_of: date, superseded: set[str]) -> str:
    if work.get("status") != "ACTIVE" or work["id"] in superseded:
        return "superseded"
    if review is None:
        return "review-required"
    if review["status"] != "verified":
        return review["status"]
    if as_of < review_date(review["reviewed_on"]):
        return "review-not-yet-effective"
    if as_of > review_date(review["expires_on"]):
        return "expired"
    path = _source_path(root, review["local_path"])
    if not path.is_file():
        return "inaccessible"
    try:
        with path.open("rb") as handle:
            observed = hashlib.file_digest(handle, "sha256").hexdigest()
    except OSError:
        return "inaccessible"
    return "verified" if observed == review["sha256"] else "identity-mismatch"


def _corpus_citations(root: Path) -> dict[Citation, list[str]]:
    indexed: dict[Citation, list[str]] = {}
    for pillar in CORPUS_PILLARS:
        directory = root / "corpus" / pillar
        if directory.is_symlink() or not directory.resolve().is_relative_to(root.resolve()):
            raise ValueError("corpus citation directory must remain within the repository")
        for path in sorted(directory.glob("*.md")):
            if path.is_symlink():
                raise ValueError("corpus citation documents must be ordinary repository files")
            source = path.read_text(encoding="utf-8")
            identifiers = {(kind, NORMALIZE_CITATION[kind](match)) for kind, pattern in CITATION_LINKS.items()
                           for match in pattern.findall(source)}
            for identifier in identifiers:
                indexed.setdefault(identifier, []).append(path.relative_to(root).as_posix())
    return indexed


def _work_citations(work: dict) -> list[Citation]:
    identifiers = work.get("canonical_identifiers")
    if not isinstance(identifiers, dict):
        return []
    return [(kind, normalize(value)) for kind, normalize in NORMALIZE_CITATION.items()
            if isinstance(value := identifiers.get(kind), str) and value]


def _affected_documents(work: dict, citations: dict[Citation, list[str]]) -> list[str]:
    return sorted({path for key in _work_citations(work) for path in citations.get(key, ())})


def _coverage_state(matches: list[str], active: list[str]) -> str:
    if len(active) > 1:
        return "ambiguous-active-work"
    if active:
        return "active-work"
    return "no-active-work" if matches else "unregistered"


def _citation_coverage(
    citations: dict[Citation, list[str]], works: list[dict], source_states: dict[str, str],
) -> dict:
    registered: dict[Citation, list[str]] = {}
    for work in works:
        for citation in _work_citations(work):
            registered.setdefault(citation, []).append(work["id"])
    rows = []
    for (kind, identifier), paths in sorted(citations.items()):
        matches = sorted(registered.get((kind, identifier), []))
        active = [match for match in matches if source_states[match] != "superseded"]
        rows.append({"kind": kind, "identifier": identifier, "state": _coverage_state(matches, active),
                     "work_ids": matches, "active_work_ids": active, "documents": sorted(paths)})
    counts = Counter(row["state"] for row in rows)
    return {"identifier_count": len(rows), "by_state": dict(sorted(counts.items())), "citations": rows}


def review_report(
    root: Path, works: list[dict], claims: list[dict], evidence: list[dict],
    reviews: dict[str, dict], as_of: date,
    live_review: LiveReview | None = None,
) -> dict:
    """Report source states and use exclusions without rewriting historical records."""
    targets = {row["supersedes"] for row in works if row.get("status") == "ACTIVE" and row.get("supersedes")}
    claims_by_work: dict[str, list[str]] = {}
    evidence_by_claim: dict[str, list[str]] = {}
    for claim in claims:
        claims_by_work.setdefault(claim["work_id"], []).append(claim["id"])
    for item in evidence:
        evidence_by_claim.setdefault(item["claim_id"], []).append(item["id"])
    citations = _corpus_citations(root)
    results = []
    for work in works:
        work_id = work["id"]
        status = _source_state(root, work, reviews.get(work_id), as_of, targets)
        observation = None
        if status == "verified" and live_review is not None:
            observation = live_review(reviews[work_id])
            status = observation["state"]
        affected_claims, affected_evidence, affected_documents = [], [], []
        permitted_uses = {}
        if status == "verified":
            permitted_uses = reviews[work_id]["permitted_uses"]
        else:
            affected_claims = sorted(claims_by_work.get(work_id, []))
            affected_evidence = sorted(item for claim_id in affected_claims
                                       for item in evidence_by_claim.get(claim_id, []))
            affected_documents = _affected_documents(work, citations)
        results.append({
            "work_id": work_id,
            "state": status,
            "permitted_uses": permitted_uses,
            "claims_for_review": affected_claims,
            "evidence_for_review": affected_evidence,
            "documents_for_review": affected_documents,
            **({"live_check": observation} if observation is not None else {}),
        })
    states = {row["work_id"]: row["state"] for row in results}
    return {"as_of": as_of.isoformat(), "works": sorted(results, key=lambda item: item["work_id"]),
            "citation_coverage": _citation_coverage(citations, works, states)}


def reviewed_freshness(report: dict, reviews: dict[str, dict]) -> dict:
    """Count declared uses that still need fresh verified source evidence."""
    approved = {key for key, review in reviews.items()
                if review["status"] == "verified" and review["permitted_uses"]}
    fresh = {row["work_id"] for row in report["works"]
             if row.get("live_check", {}).get("state") == "verified"}
    blocked = sorted(approved - fresh)
    return {"state": "needs-review" if blocked else "current",
            "approved_sources": len(approved), "blocked_work_ids": blocked}
