"""Read public source state without accepting upstream policy or instructions."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import date, datetime
from html.parser import HTMLParser
from http.client import HTTPException
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener
from xml.etree import ElementTree

ARXIV = "https://arxiv.org"
ARXIV_MODERN_ID = r"[0-9]{4}\.[0-9]{4,5}"
ARXIV_ID = rf"(?:{ARXIV_MODERN_ID}|[a-z]+(?:-[a-z]+)*/[0-9]{{7}})"
ARXIV_REVISION = r"v[1-9][0-9]*"
VERSION = re.compile(rf"({ARXIV_ID})({ARXIV_REVISION})")
PDF_VERSION = re.compile(rf"({ARXIV_MODERN_ID})({ARXIV_REVISION})")
ATOM_ID = re.compile(rf"https?://arxiv\.org/abs/({ARXIV_ID})({ARXIV_REVISION})")
ARXIV_VENUE = "arXiv preprint"
ARXIV_API = "https://export.arxiv.org/api/query?"
ARXIV_KIND = "arxiv-bibliographic-metadata"
ARXIV_FIELDS = {"arxiv", "title", "authors", "publication_date", "venue", "revision"}
ARXIV_BATCH_SIZE = 64
ATOM_NAMES = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
WITHDRAWAL = re.compile(
    r"(?:withdrawn\b|(?:this|the) (?:paper|article|submission|manuscript|work) "
    r"(?:(?:has been|was|is) )?(?:withdrawn|retracted)\b)", re.I,
)
CROSSREF = "https://api.crossref.org/works/"
CROSSREF_FIELDS = {"doi", "title", "authors", "publication_date", "venue", "revision"}
CROSSREF_KIND = "crossref-bibliographic-metadata"


class Unavailable(Exception):
    """The pinned publisher did not return source evidence."""


class SourceFinding(ValueError):
    def __init__(self, state: str, reason: str):
        super().__init__(reason)
        self.state = state


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


class AbstractMetadata(HTMLParser):
    def __init__(self, contents: bytes):
        super().__init__()
        self.canonical = ""
        self.identity = ""
        self.description = ""
        self.feed(contents.decode("utf-8"))

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical = values.get("href") or ""
        if tag == "meta" and values.get("name") == "citation_arxiv_id":
            self.identity = values.get("content") or ""
        if tag == "meta" and values.get("property") == "og:description":
            self.description = values.get("content") or ""


def fetch(url: str, limit: int) -> bytes:
    request = Request(url, headers={"User-Agent": "Knowledge-Source-Readback/1.0"})
    with build_opener(NoRedirects()).open(request, timeout=8) as response:
        body = response.read(limit + 1)
        if response.status != 200 or len(body) > limit:
            raise Unavailable("incomplete or oversized response")
        return body


def _http_failure(exc: HTTPError) -> dict:
    state = "inaccessible" if exc.code in (404, 410) else "unconfirmed"
    return {"state": state, "reason": f"publisher returned HTTP {exc.code}"}


def crossref_url(doi: str) -> str:
    if not re.fullmatch(r"10\.[0-9]{4,9}/[-._;()/:+a-z0-9]+", doi):
        raise ValueError("source review requires a normalized Crossref DOI")
    if any(part in {"", ".", ".."} for part in doi.split("/")):
        raise ValueError("source review requires a normalized Crossref DOI")
    return CROSSREF + quote(doi, safe="/")


def crossref_revision(value: str) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value):
        raise ValueError("Crossref deposit revision must be an exact UTC timestamp")
    datetime.fromisoformat(value)
    return value


def _publication_date(work: dict) -> str:
    parts = (work.get("published-online") or work["published"])["date-parts"][0]
    if not 1 <= len(parts) <= 3 or not all(type(part) is int for part in parts):
        raise ValueError("invalid Crossref publication date")
    exact = date(*(parts + [1] * (3 - len(parts))))
    return exact.isoformat()[:{1: 4, 2: 7, 3: 10}[len(parts)]]


def crossref_metadata(raw: bytes, doi: str) -> dict:
    """Project the bibliographic data covered by a Crossref source review."""
    response = json.loads(raw)
    work = response["message"]
    if response["message-type"] != "work" or work["DOI"].lower() != doi:
        raise SourceFinding("identity-mismatch", "Crossref returned a different DOI")
    title = " ".join(work["title"][0].split())
    notices = [update["type"].lower() for update in work.get("updated-by", [])]
    if "retraction" in notices or title.lower().startswith("retracted:"):
        raise SourceFinding("retracted", "Crossref reports a retraction")
    if notices:
        raise SourceFinding("revised", "Crossref reports an editorial update")
    authors = [author.get("name") or " ".join(filter(None, (author.get("given"), author.get("family"))))
               for author in work["author"]]
    if not title or not authors or not all(authors):
        raise ValueError("Crossref record lacks bibliographic metadata")
    return {"doi": doi, "title": title, "authors": authors, "publication_date": _publication_date(work),
            "venue": work.get("container-title", [""])[0],
            "revision": crossref_revision(work["deposited"]["date-time"])}


def metadata_bytes(metadata: dict) -> bytes:
    return (json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _metadata_observation(review: dict, metadata: dict) -> dict:
    revision = metadata["revision"]
    observed = hashlib.sha256(metadata_bytes(metadata)).hexdigest()
    if revision != review["revision"]:
        return {"state": "revised", "observed_revision": revision, "observed_sha256": observed}
    state = "verified" if observed == review["sha256"] else "identity-mismatch"
    return {"state": state, "observed_revision": revision, "observed_sha256": observed}


def read_crossref(review: dict, read=fetch) -> dict:
    url = review["source_url"]
    try:
        doi = unquote(url.removeprefix(CROSSREF))
        if url != crossref_url(doi):
            return {"state": "unconfirmed", "reason": "invalid pinned Crossref URL"}
        metadata = crossref_metadata(read(url, 512 * 1024), doi)
    except SourceFinding as exc:
        return {"state": exc.state, "reason": str(exc)}
    except HTTPError as exc:
        return _http_failure(exc)
    except (KeyError, IndexError, TypeError, AttributeError, ValueError, URLError, HTTPException, TimeoutError, Unavailable):
        return {"state": "unconfirmed", "reason": "Crossref metadata was unavailable or incomplete"}
    return _metadata_observation(review, metadata)


def _atom_text(item, name: str, *, required: bool = True) -> str:
    fields = item.findall(name, ATOM_NAMES)
    if not fields and not required:
        return ""
    if len(fields) != 1 or len(fields[0]) or fields[0].text is None:
        raise ValueError("arXiv entry has missing or ambiguous metadata")
    value = " ".join(unicodedata.normalize("NFC", fields[0].text).split())
    if required and not value:
        raise ValueError("arXiv entry has empty metadata")
    return value


def _arxiv_item(entry, identifier: str, revision: str) -> dict:
    try:
        title = _atom_text(entry, "a:title")
        notices = (title, _atom_text(entry, "a:summary", required=False),
                   _atom_text(entry, "arxiv:comment", required=False))
        if any(WITHDRAWAL.match(notice) for notice in notices):
            return {"state": "retracted", "reason": "arXiv reports a withdrawal", "observed_revision": revision}
        published = datetime.fromisoformat(_atom_text(entry, "a:published"))
        authors = [_atom_text(author, "a:name") for author in entry.findall("a:author", ATOM_NAMES)]
        if published.tzinfo is None or not authors:
            raise ValueError("arXiv entry lacks a publication date or authors")
    except ValueError:
        return {"state": "unconfirmed", "reason": "arXiv entry lacks exact bibliographic fields"}
    return {"metadata": {"arxiv": identifier, "revision": revision, "title": title, "authors": authors,
                         "publication_date": published.date().isoformat(), "venue": ARXIV_VENUE}}


def arxiv_atom_catalog(raw: bytes, identifiers: set[str]) -> dict[str, dict]:
    """Read a bounded arXiv ID-list response without resolving XML definitions or links."""
    contents = raw.decode("utf-8")
    if "<!DOCTYPE" in contents.upper() or "<!ENTITY" in contents.upper():
        raise ValueError("arXiv response contains XML definitions")
    feed = ElementTree.fromstring(contents)
    if feed.tag != f"{{{ATOM_NAMES['a']}}}feed":
        raise ValueError("arXiv response is not an Atom feed")
    catalog = {}
    for entry in feed.findall("a:entry", ATOM_NAMES):
        url = _atom_text(entry, "a:id")
        version = ATOM_ID.fullmatch(url)
        if version is None or version[1] not in identifiers or version[1] in catalog:
            raise ValueError("arXiv response has unexpected or duplicate identity")
        identifier, suffix = version.groups()
        catalog[identifier] = _arxiv_item(entry, identifier, identifier + suffix)
    return catalog


def _arxiv_catalog(identifiers: list[str], read) -> dict[str, dict]:
    catalog = {}
    for first in range(0, len(identifiers), ARXIV_BATCH_SIZE):
        if first:
            sleep(3)
        batch = identifiers[first:first + ARXIV_BATCH_SIZE]
        query = urlencode({"id_list": ",".join(batch), "max_results": len(batch)}, safe=",")
        try:
            catalog.update(arxiv_atom_catalog(read(ARXIV_API + query, 1024 * 1024), set(batch)))
        except HTTPError as exc:
            catalog.update(dict.fromkeys(batch, _http_failure(exc)))
        except (ValueError, ElementTree.ParseError, URLError, HTTPException, TimeoutError, Unavailable):
            catalog.update(dict.fromkeys(batch, {"state": "unconfirmed", "reason": "arXiv Atom readback failed"}))
    return catalog


def read_arxiv(review: dict, read=fetch) -> dict:
    match = PDF_VERSION.fullmatch(review.get("revision", ""))
    if match is None or review.get("source_url") != f"{ARXIV}/abs/{match[0]}":
        return {"state": "unconfirmed", "reason": "invalid pinned publisher identity"}
    identifier, version = match.groups()
    abstract_url = f"{ARXIV}/abs/{identifier}"
    try:
        contents = read(abstract_url, 512 * 1024)
        page = AbstractMetadata(contents)
        if page.canonical != abstract_url or page.identity != identifier:
            return {"state": "identity-mismatch", "reason": "publisher abstract identity changed"}
        if re.match(r"(?:this|the) (?:paper|article|submission|manuscript|work) "
                    r"(?:has been|was|is) (?:withdrawn|retracted)\b", page.description.strip(), re.I):
            return {"state": "retracted", "reason": "publisher abstract announces a withdrawal or retraction"}
        history = contents.partition(b'class="submission-history"')[2]
        current = re.search(rb"<strong>\[(v[0-9]+)\]</strong>", history)
        if current is None:
            return {"state": "unconfirmed", "reason": "publisher did not identify the current revision"}
        observed_version = current[1].decode("ascii")
        observed = identifier + observed_version
        if observed_version != version:
            return {"state": "revised", "observed_revision": observed}
        pdf = read(f"{ARXIV}/pdf/{match[0]}", 16 * 1024 * 1024)
    except HTTPError as exc:
        return _http_failure(exc)
    except (URLError, HTTPException, TimeoutError, Unavailable, UnicodeError):
        return {"state": "unconfirmed", "reason": "publisher response was unavailable or incomplete"}
    if not pdf.startswith(b"%PDF-") or not pdf.rstrip().endswith(b"%%EOF"):
        return {"state": "unconfirmed", "reason": "publisher did not return a complete PDF"}
    observed_digest = hashlib.sha256(pdf).hexdigest()
    state = "verified" if observed_digest == review["sha256"] else "identity-mismatch"
    return {"state": state, "observed_revision": observed, "observed_sha256": observed_digest}


def read_sources(reviews: list[dict], read=fetch) -> dict[str, dict]:
    """Read the eligible source reviews and return observations keyed by Work ID."""
    arxiv_ids = {review["work_id"]: VERSION.fullmatch(review["revision"])[1]
                 for review in reviews if review.get("source_kind") == ARXIV_KIND}
    catalog = _arxiv_catalog(sorted(set(arxiv_ids.values())), read)
    observations = {}
    for review in reviews:
        work_id = review["work_id"]
        if work_id in arxiv_ids:
            item = catalog.get(arxiv_ids[work_id],
                               {"state": "unconfirmed", "reason": "arXiv entry is missing"})
            observation = _metadata_observation(review, item["metadata"]) if "metadata" in item else item
        elif review.get("source_kind") == CROSSREF_KIND:
            observation = read_crossref(review, read=read)
        else:
            observation = read_arxiv(review, read=read)
        observations[work_id] = observation
    return observations
