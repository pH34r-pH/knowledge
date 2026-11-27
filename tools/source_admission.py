"""Offline source review and dependency impact for the existing Work registry."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from collections.abc import Callable
from datetime import date
from pathlib import Path, PurePosixPath

from reconcile_public_bibliography import normalize_arxiv, normalize_doi
from source_readback import (
    ACL_FIELDS, ACL_KIND, ACL_ORIGINAL, anthology_id,
    ARXIV_FIELDS, ARXIV_ID, ARXIV_KIND, ARXIV_MODERN_ID, ARXIV_REVISION, ARXIV_VENUE,
    CROSSREF_FIELDS, CROSSREF_JOURNAL_KIND, CROSSREF_KINDS, VERSION, crossref_revision, crossref_url,
    metadata_bytes, valid_acl_pages, valid_journal_locator,
)

REVIEW_FIELDS = {
    "schema_version", "work_id", "trust_class", "data_class", "revision", "source_url",
    "local_path", "sha256", "reviewed_on", "expires_on", "status", "permitted_uses",
}
REVIEW_STATES = ("verified", "unconfirmed", "inaccessible", "revised", "retracted")
METADATA_USES = {"index", "search"}
PERMITTED_SCOPE = "bibliographic-metadata"
SHA256_RE = re.compile(r"[0-9a-f]{64}")
ARXIV_VERSION = re.compile(rf"{ARXIV_REVISION}$")
_ARXIV_ENTRY_URL = r"https?://(?:arxiv\.org/(?:abs|html|pdf)|ar5iv\.labs\.arxiv\.org/html)/"
ARXIV_VERSIONED_URL = re.compile(
    rf"{_ARXIV_ENTRY_URL}({ARXIV_ID}{ARXIV_REVISION})(?:\.pdf)?(?:[?#][^\s]*)?", re.I,
)
_ARXIV_LINK = re.compile(
    rf"(?<![\w/]){_ARXIV_ENTRY_URL}({ARXIV_ID})({ARXIV_REVISION})?(?:\.pdf)?(?![0-9a-z/])", re.I,
)
_DOI_LINK = re.compile(r"(?<![\w/])https?://(?:dx\.)?doi\.org/(10\.[0-9]{4,9}/[-._;()/:a-z0-9+]+)", re.I)
NORMALIZE_CITATION = {"arxiv": normalize_arxiv, "doi": normalize_doi}
CORPUS_PILLARS = ("design-patterns", "ml-techniques", "adjacent-knowledge")
LiveReview = Callable[[list[dict]], dict[str, dict]]
Citation = tuple[str, str]
ACL_VENUE_ALIASES = {
    "Findings of the Association for Computational Linguistics: ACL 2025": "Findings of ACL 2025",
    "Findings of the Association for Computational Linguistics: EMNLP 2024": "Findings of EMNLP 2024",
    "Proceedings of the 19th Conference of the European Chapter of the Association for Computational "
    "Linguistics (Volume 1: Long Papers)": "EACL 2026, Volume 1: Long Papers",
    "Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics "
    "(Volume 1: Long Papers)": "ACL 2024, Volume 1: Long Papers",
    "Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing": "EMNLP 2024",
    "Proceedings of the 2019 Conference of the North American Chapter of the Association for "
    "Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers)": "NAACL-HLT 2019",
}


def review_date(value: object) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("expected an ISO calendar date")
    return date.fromisoformat(value)


def _source_path(root: Path, value: object) -> Path:
    if not isinstance(value, str) or any(char in value for char in "\\:\r\n\x00"):
        raise ValueError("reviewed local source must use a normalized evidence path")
    relative = PurePosixPath(value)
    if (
        relative.parts[:-1] not in (("arxiv",), ("governance", "source-evidence"))
        or value != relative.as_posix() or relative.name in {"", ".."}
    ):
        raise ValueError("reviewed local source must use a normalized evidence path")
    path = root / value
    paths = [path, *(root / parent for parent in relative.parents if parent.parts)]
    if any(member.is_symlink() for member in paths) or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("reviewed local source must be an ordinary retained file")
    return path


def _pinned_arxiv(work: dict, review: dict) -> None:
    identifiers = work.get("canonical_identifiers")
    arxiv = identifiers.get("arxiv") if isinstance(identifiers, dict) else None
    revision = review["revision"]
    source_url = review["source_url"]
    if not isinstance(arxiv, str) or not isinstance(revision, str):
        raise ValueError("source review requires an exact version of the registered arXiv work")
    base = ARXIV_VERSION.sub("", arxiv)
    version = VERSION.fullmatch(revision)
    if version is None or version[1] != base:
        raise ValueError("source review requires an exact version of the registered arXiv work")
    if source_url != f"https://arxiv.org/abs/{revision}":
        raise ValueError("source review URL must identify the exact primary version")
    if review.get("source_kind") == ARXIV_KIND:
        _check_arxiv_work_version(work, arxiv, base, revision)
        _pinned_metadata_path(work, review)
    elif not re.fullmatch(ARXIV_MODERN_ID, base) or review["local_path"] != f"arxiv/{base}.pdf":
        raise ValueError("source review must bind the retained PDF for the registered arXiv work")


def _check_arxiv_work_version(work: dict, alias: str, base: str, revision: str) -> None:
    source_url = work.get("source_url")
    pinned_url = ARXIV_VERSIONED_URL.fullmatch(source_url) if isinstance(source_url, str) else None
    if alias not in (base, revision) or (pinned_url and pinned_url[1] != revision):
        raise ValueError("arXiv metadata review requires the registered Work's pinned version")


def _work_doi(work: dict) -> str:
    aliases = work.get("canonical_identifiers")
    doi = aliases.get("doi") if isinstance(aliases, dict) else None
    if not isinstance(doi, str):
        raise ValueError("source review needs a DOI in the registered Work")
    return normalize_doi(doi)


def _pinned_crossref(work: dict, review: dict) -> None:
    if review["source_url"] != crossref_url(_work_doi(work)):
        raise ValueError("Crossref source review must use the registered DOI URL")
    if not isinstance(review["revision"], str):
        raise ValueError("Crossref deposit revision must be an exact UTC timestamp")
    crossref_revision(review["revision"])
    _pinned_metadata_path(work, review)


def _pinned_acl_anthology(work: dict, review: dict) -> None:
    url = work.get("source_url")
    if not isinstance(url, str) or url != review["source_url"]:
        raise ValueError("ACL Anthology source review must bind the registered paper URL")
    identifier = anthology_id(url)
    doi = _work_doi(work)
    alias = work["canonical_identifiers"].get("anthology", identifier)
    if alias != identifier or doi != f"10.18653/v1/{identifier.lower()}":
        raise ValueError("ACL Anthology source review requires the matching Anthology ID and DOI")
    if review["revision"] != ACL_ORIGINAL:
        raise ValueError("ACL Anthology source review requires the original publication")
    _pinned_metadata_path(work, review)


def _pinned_metadata_path(work: dict, review: dict) -> None:
    if review["local_path"] != f"governance/source-evidence/{work['id']}.json":
        raise ValueError("source review must bind the registered Work's retained metadata")


IDENTITY_VALIDATORS = {
    ARXIV_KIND: _pinned_arxiv,
    ACL_KIND: _pinned_acl_anthology,
    **dict.fromkeys(CROSSREF_KINDS, _pinned_crossref),
}


def _metadata_uses(value: object) -> None:
    if not isinstance(value, dict) or not set(value) <= METADATA_USES:
        raise ValueError("source review accepts only explicit metadata index and search decisions")
    if any(scope != PERMITTED_SCOPE for scope in value.values()):
        raise ValueError("source review accepts only bibliographic metadata use")


def _validate_source_review(root: Path, work: dict, review: dict) -> None:
    if not isinstance(review, dict):
        raise ValueError("source review has missing or unrecognized fields")
    version = review.get("schema_version")
    if type(version) is not int or version not in (1, 2):
        raise ValueError("unsupported source review version")
    fields = REVIEW_FIELDS | {"source_kind"} if version == 2 else REVIEW_FIELDS
    if set(review) != fields:
        raise ValueError("source review has missing or unrecognized fields")
    if review["trust_class"] != "primary" or review["data_class"] != "public":
        raise ValueError("this source-review profile requires a public primary source")
    if review["status"] not in REVIEW_STATES:
        raise ValueError("source review requires a recognized freshness or retraction state")
    if review_date(review["reviewed_on"]) > review_date(review["expires_on"]):
        raise ValueError("source review expiry precedes its review date")
    kind = ARXIV_KIND if version == 1 else review["source_kind"]
    check_identity = IDENTITY_VALIDATORS.get(kind) if isinstance(kind, str) else None
    if check_identity is None:
        raise ValueError("unsupported metadata source kind")
    check_identity(work, review)
    if not isinstance(review["sha256"], str) or not SHA256_RE.fullmatch(review["sha256"]):
        raise ValueError("source review requires the full SHA-256 of the retained source")
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


def _journal_venues(metadata: dict) -> set[str]:
    venue, locator = metadata["venue"], metadata["journal_locator"]
    if not isinstance(venue, str) or not venue.strip() or not valid_journal_locator(locator):
        return set()
    volume = locator["volume"]
    volumes = (volume, f"{volume}({locator['issue']})") if "issue" in locator else (volume,)
    titles = (venue, venue.removeprefix("The "))
    addresses = [locator[field] for field in ("page", "article-number") if field in locator]
    rendered = {
        f"{title} {number}{separator}{address}".replace("\u2013", "-")
        for title in titles for number in volumes for separator in (", ", ":") for address in addresses
    }
    year = metadata["publication_date"].split("-")[0]
    return rendered | {f"{label} ({year})" for label in rendered}


def _matches_venue(metadata: dict, registered: object, kind: str) -> bool:
    observed = metadata["venue"]
    if kind == ARXIV_KIND:
        return observed == ARXIV_VENUE and registered in (None, "", ARXIV_VENUE)
    if kind == CROSSREF_JOURNAL_KIND:
        return isinstance(registered, str) and registered.replace("\u2013", "-") in _journal_venues(metadata)
    if kind == ACL_KIND:
        return isinstance(observed, str) and bool(observed) and (
            observed == registered or ACL_VENUE_ALIASES.get(observed, observed) == registered
        )
    return observed == registered


def _matches_publication_date(observed: object, registered: object, kind: str) -> bool:
    if kind not in CROSSREF_KINDS:
        return observed == registered
    if not isinstance(observed, str) or not isinstance(registered, str):
        return False
    suffix = {4: "-01-01", 7: "-01", 10: ""}
    for value in (observed, registered):
        review_date(value + suffix.get(len(value), ""))
    return observed == registered or observed.startswith(registered + "-")


def _matches_work_metadata(raw: bytes, work: dict, review: dict) -> bool:
    try:
        metadata = json.loads(raw)
        kind = review["source_kind"]
        if kind == ARXIV_KIND:
            fields, alias = ARXIV_FIELDS, "arxiv"
            identity = ARXIV_VERSION.sub("", work["canonical_identifiers"][alias])
        else:
            fields, alias = CROSSREF_FIELDS, "doi"
            identity = _work_doi(work)
        if kind == CROSSREF_JOURNAL_KIND:
            fields = fields | {"journal_locator"}
        elif kind == ACL_KIND:
            fields = ACL_FIELDS
        if not isinstance(metadata, dict) or set(metadata) != fields or raw != metadata_bytes(metadata):
            return False
        if kind == ACL_KIND and (
            metadata["anthology"] != anthology_id(review["source_url"])
            or not valid_acl_pages(metadata["first_page"], metadata["last_page"])
        ):
            return False
        return all((
            metadata[alias] == identity,
            metadata["revision"] == review["revision"],
            _matches_venue(metadata, work.get("venue"), kind),
            _matches_publication_date(metadata["publication_date"], work.get("publication_date"), kind),
            metadata["title"] == work.get("title"),
            metadata["authors"] == work.get("authors"),
        ))
    except (AttributeError, TypeError, ValueError):
        return False


def _evidence_state(path: Path, work: dict, review: dict) -> str:
    try:
        with path.open("rb") as handle:
            if review["schema_version"] == 2:
                raw = handle.read(65_537)
                match = (len(raw) <= 65_536 and hashlib.sha256(raw).hexdigest() == review["sha256"]
                         and _matches_work_metadata(raw, work, review))
            else:
                match = hashlib.file_digest(handle, "sha256").hexdigest() == review["sha256"]
    except OSError:
        return "inaccessible"
    return "verified" if match else "identity-mismatch"


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
    return _evidence_state(path, work, review)


def _corpus_citations(root: Path) -> tuple[dict[Citation, list[str]], dict[str, list[str]]]:
    indexed: dict[Citation, list[str]] = {}
    revisions: dict[str, list[str]] = {}
    for pillar in CORPUS_PILLARS:
        directory = root / "corpus" / pillar
        if directory.is_symlink() or not directory.resolve().is_relative_to(root.resolve()):
            raise ValueError("corpus citation directory must remain within the repository")
        for path in sorted(directory.glob("*.md")):
            if path.is_symlink():
                raise ValueError("corpus citation documents must be ordinary repository files")
            source = path.read_text(encoding="utf-8")
            document = path.relative_to(root).as_posix()
            arxiv = {(normalize_arxiv(base.lower()), version.lower()) for base, version in _ARXIV_LINK.findall(source)}
            identifiers = {("arxiv", base) for base, _ in arxiv}
            identifiers.update(("doi", normalize_doi(doi)) for doi in _DOI_LINK.findall(source))
            for identifier in identifiers:
                indexed.setdefault(identifier, []).append(document)
            for base, version in arxiv:
                if version:
                    revisions.setdefault(base + version, []).append(document)
    return indexed, revisions


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
    citations: dict[Citation, list[str]], works: list[dict], reports: dict[str, dict],
) -> dict:
    registered: dict[Citation, list[str]] = {}
    for work in works:
        for citation in _work_citations(work):
            registered.setdefault(citation, []).append(work["id"])
    rows = []
    for (kind, identifier), paths in sorted(citations.items()):
        matches = sorted(registered.get((kind, identifier), []))
        active = [match for match in matches if reports[match]["state"] != "superseded"]
        rows.append({"kind": kind, "identifier": identifier, "state": _coverage_state(matches, active),
                     "work_ids": matches, "active_work_ids": active, "documents": sorted(paths)})
    counts = Counter(row["state"] for row in rows)
    return {"identifier_count": len(rows), "by_state": dict(sorted(counts.items())), "citations": rows}


def _registered_arxiv_revision(work: dict, review: dict) -> str | None:
    """Use a declared Work revision, falling back to a review for an unversioned Work."""
    identifiers = work.get("canonical_identifiers")
    alias = identifiers.get("arxiv") if isinstance(identifiers, dict) else None
    if not isinstance(alias, str):
        return None
    base = normalize_arxiv(alias.lower())
    url = work.get("source_url")
    url_match = ARXIV_VERSIONED_URL.fullmatch(url) if isinstance(url, str) else None
    candidates = (alias, url_match[1] if url_match else "")
    declared = {match[0] for value in candidates if (match := VERSION.fullmatch(value.lower()))}
    if len(declared) > 1:
        return None
    revision = next(iter(declared), review.get("revision", ""))
    exact = VERSION.fullmatch(revision)
    return revision if exact and exact[1] == base else None


def _pinned_citation_state(revision: str, matches: list[str], active: list[str],
                           reports: dict[str, dict], reviews: dict[str, dict]) -> tuple[str, dict]:
    if not active:
        return ("superseded-revision" if matches else "unregistered-revision"), {}
    if len(active) != 1:
        return "ambiguous-active-revision", {}
    work_id = active[0]
    report = reports[work_id]
    if report["state"] != "verified":
        return report["state"], {}
    if reviews[work_id]["revision"] != revision:
        return "review-version-mismatch", {}
    return "verified", report["permitted_uses"]


def _revision_coverage(citations: dict[str, list[str]], works: list[dict], reports: dict[str, dict],
                       reviews: dict[str, dict]) -> dict:
    registered: dict[str, list[str]] = {}
    for work in works:
        work_id = work["id"]
        revision = _registered_arxiv_revision(work, reviews.get(work_id, {}))
        if revision:
            registered.setdefault(revision, []).append(work_id)

    rows = []
    needs_review = set()
    for revision, paths in sorted(citations.items()):
        matches = sorted(registered.get(revision, []))
        active = [work_id for work_id in matches if reports[work_id]["state"] != "superseded"]
        state, uses = _pinned_citation_state(revision, matches, active, reports, reviews)
        if state != "verified":
            needs_review.update(paths)
        rows.append({"revision": revision, "state": state, "work_ids": matches, "active_work_ids": active,
                     "permitted_uses": uses, "documents": sorted(paths)})
    counts = Counter(row["state"] for row in rows)
    return {"revision_count": len(rows), "by_state": dict(sorted(counts.items())), "citations": rows,
            "documents_for_review": sorted(needs_review)}


def _read_verified_sources(statuses: dict[str, str], reviews: dict[str, dict], read: LiveReview) -> dict[str, dict]:
    eligible = [reviews[work_id] for work_id, state in statuses.items() if state == "verified"]
    observations = read(eligible)
    return {row["work_id"]: observations.get(row["work_id"], {"state": "unconfirmed", "reason": "missing source readback"})
            for row in eligible}


def _current_claims_by_work(claims: list[dict]) -> dict[str, list[str]]:
    superseded = {row["supersedes"] for row in claims
                  if row.get("status") == "ACCEPTED" and row.get("supersedes")}
    grouped: dict[str, list[str]] = {}
    for claim in claims:
        if claim["id"] not in superseded:
            grouped.setdefault(claim["work_id"], []).append(claim["id"])
    return grouped


def review_report(
    root: Path, works: list[dict], claims: list[dict], evidence: list[dict],
    reviews: dict[str, dict], as_of: date,
    live_review: LiveReview | None = None,
) -> dict:
    """Report source states and use exclusions without rewriting historical records."""
    targets = {row["supersedes"] for row in works if row.get("status") == "ACTIVE" and row.get("supersedes")}
    claims_by_work = _current_claims_by_work(claims)
    evidence_by_claim: dict[str, list[str]] = {}
    for item in evidence:
        evidence_by_claim.setdefault(item["claim_id"], []).append(item["id"])
    citations, revisions = _corpus_citations(root)
    source_states = {work["id"]: _source_state(root, work, reviews.get(work["id"]), as_of, targets)
                     for work in works}
    observations = _read_verified_sources(source_states, reviews, live_review) if live_review is not None else {}
    reports = {}
    for work in works:
        work_id = work["id"]
        observation = observations.get(work_id)
        status = observation["state"] if observation is not None else source_states[work_id]
        affected_claims, affected_evidence, affected_documents = [], [], []
        permitted_uses = {}
        if status == "verified":
            permitted_uses = reviews[work_id]["permitted_uses"]
        else:
            affected_claims = sorted(claims_by_work.get(work_id, []))
            affected_evidence = sorted(item for claim_id in affected_claims
                                       for item in evidence_by_claim.get(claim_id, []))
            affected_documents = _affected_documents(work, citations)
        reports[work_id] = {
            "work_id": work_id,
            "state": status,
            "permitted_uses": permitted_uses,
            "claims_for_review": affected_claims,
            "evidence_for_review": affected_evidence,
            "documents_for_review": affected_documents,
            **({"live_check": observation} if observation is not None else {}),
        }
    return {"as_of": as_of.isoformat(), "works": [reports[work_id] for work_id in sorted(reports)],
            "citation_coverage": _citation_coverage(citations, works, reports),
            "arxiv_revision_coverage": _revision_coverage(revisions, works, reports, reviews)}


def reviewed_freshness(report: dict, reviews: dict[str, dict]) -> dict:
    """Count declared uses that still need fresh verified source evidence."""
    approved = {key for key, review in reviews.items()
                if review["status"] == "verified" and review["permitted_uses"]}
    fresh = {row["work_id"] for row in report["works"]
             if row.get("live_check", {}).get("state") == "verified"}
    blocked = sorted(approved - fresh)
    return {"state": "needs-review" if blocked else "current",
            "approved_sources": len(approved), "blocked_work_ids": blocked}
