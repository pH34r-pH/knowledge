"""Read public source state without accepting upstream policy or instructions."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime
from html.parser import HTMLParser
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote
from urllib.request import HTTPRedirectHandler, Request, build_opener

ARXIV = "https://arxiv.org"
VERSION = re.compile(r"([0-9]{4}\.[0-9]{4,5})(v[1-9][0-9]*)")
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
    revision = metadata["revision"]
    observed = hashlib.sha256(metadata_bytes(metadata)).hexdigest()
    if revision != review["revision"]:
        return {"state": "revised", "observed_revision": revision, "observed_sha256": observed}
    state = "verified" if observed == review["sha256"] else "identity-mismatch"
    return {"state": state, "observed_revision": revision, "observed_sha256": observed}


def read_arxiv(review: dict, read=fetch) -> dict:
    match = VERSION.fullmatch(review.get("revision", ""))
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


def read_source(review: dict) -> dict:
    if review.get("source_kind") == CROSSREF_KIND:
        return read_crossref(review)
    return read_arxiv(review)
