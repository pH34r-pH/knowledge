"""Read public arXiv source state without accepting upstream policy or text."""
from __future__ import annotations

import hashlib
import re
from html.parser import HTMLParser
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

ARXIV = "https://arxiv.org"
VERSION = re.compile(r"([0-9]{4}\.[0-9]{4,5})(v[1-9][0-9]*)")


class Unavailable(Exception):
    """The pinned publisher did not return source evidence."""


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
        state = "inaccessible" if exc.code in (404, 410) else "unconfirmed"
        return {"state": state, "reason": f"publisher returned HTTP {exc.code}"}
    except (URLError, HTTPException, TimeoutError, Unavailable, UnicodeError):
        return {"state": "unconfirmed", "reason": "publisher response was unavailable or incomplete"}
    if not pdf.startswith(b"%PDF-") or not pdf.rstrip().endswith(b"%%EOF"):
        return {"state": "unconfirmed", "reason": "publisher did not return a complete PDF"}
    observed_digest = hashlib.sha256(pdf).hexdigest()
    state = "verified" if observed_digest == review["sha256"] else "identity-mismatch"
    return {"state": state, "observed_revision": observed, "observed_sha256": observed_digest}
