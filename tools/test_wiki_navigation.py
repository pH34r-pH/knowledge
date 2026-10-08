"""Validate link-only wiki navigation and representative canonical routes."""

from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
WIKI_INDEX = ROOT / "docs/wiki/README.md"
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEADING_PATTERN = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
ARXIV_ID = "1701.06538"
EXPECTED_PATHS = {
    "README.md",
    "TOPICS.md",
    "BUILDING.md",
    "corpus/LEDGER.md",
    "corpus/design-patterns/saga-pattern.md",
    "corpus/ml-techniques/mixture-of-experts-routing.md",
    "corpus/ml-techniques/rag-retrieval-architectures.md",
    "corpus/adjacent-knowledge/opentelemetry-interoperability.md",
    "references/external/works.jsonl",
    "reports/public-bibliography-identity-crosswalk-2026-10-07.json",
    "reports/domain-scaling-lab-literature-audit-2026-09-01.md",
}


def markdown_slug(heading: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", heading)
    text = re.sub(r"[`*_~]", "", unescape(text)).strip().lower()
    text = text.replace("&", "")
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text)


def markdown_anchors(path: Path) -> set[str]:
    counts: dict[str, int] = {}
    anchors: set[str] = set()
    for heading in HEADING_PATTERN.findall(path.read_text(encoding="utf-8")):
        slug = markdown_slug(heading)
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        anchors.add(slug if count == 0 else f"{slug}-{count}")
    return anchors


def local_target(markdown: Path, target: str) -> tuple[Path | None, str | None]:
    target = target.strip().split(maxsplit=1)[0].strip("<>")
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return None, None
    path_text = unquote(parsed.path)
    candidate = (markdown.parent / path_text).resolve() if path_text else markdown.resolve()
    return candidate, unquote(parsed.fragment) or None


def check_local_links(markdown: Path) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    targets: set[str] = set()
    text = markdown.read_text(encoding="utf-8")
    for target in LINK_PATTERN.findall(text):
        candidate, fragment = local_target(markdown, target)
        if candidate is None:
            continue
        try:
            relative = candidate.relative_to(ROOT).as_posix()
        except ValueError:
            errors.append(f"link escapes repository: {target}")
            continue
        if not candidate.is_file():
            errors.append(f"missing local link target: {target}")
            continue
        targets.add(relative)
        if fragment and candidate.suffix.lower() in {".md", ".markdown", ".mdx"}:
            if fragment not in markdown_anchors(candidate):
                errors.append(f"missing Markdown heading #{fragment} in {relative}")
    return errors, targets


def load_works() -> dict[str, dict[str, object]]:
    registry = ROOT / "references/external/works.jsonl"
    records: dict[str, dict[str, object]] = {}
    for line_number, line in enumerate(registry.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        identifier = record.get("id")
        if not isinstance(identifier, str) or identifier in records:
            raise ValueError(f"invalid or duplicate Work id on line {line_number}: {identifier!r}")
        records[identifier] = record
    return records


def check_representative_routes(wiki_targets: set[str], homepage_targets: set[str]) -> list[str]:
    errors: list[str] = []
    missing = EXPECTED_PATHS - wiki_targets
    if missing:
        errors.append(f"wiki index must link representative canonical paths: {sorted(missing)}")
    if "docs/wiki/README.md" not in homepage_targets:
        errors.append("repository README must link to the wiki navigation entry point")

    article_path = "corpus/ml-techniques/mixture-of-experts-routing.md"
    article = (ROOT / article_path).read_text(encoding="utf-8")
    if not re.search(rf"arxiv\.org/abs/{ARXIV_ID}(?:v\d+)?", article):
        errors.append(f"representative article does not cite arXiv:{ARXIV_ID}")

    crosswalk_path = ROOT / "reports/public-bibliography-identity-crosswalk-2026-10-07.json"
    crosswalk = json.loads(crosswalk_path.read_text(encoding="utf-8"))
    matches = [row for row in crosswalk["sources"] if row.get("canonical_key") == f"arxiv:{ARXIV_ID}"]
    if len(matches) != 1:
        errors.append(f"crosswalk must have one canonical identity for arXiv:{ARXIV_ID}")
        return errors

    work_records = matches[0].get("work_records", [])
    work_ids = [row.get("id") for row in work_records if isinstance(row, dict)]
    if work_ids != ["KWRK-000066"]:
        errors.append(f"crosswalk route for arXiv:{ARXIV_ID} changed unexpectedly: {work_ids!r}")
        return errors

    works = load_works()
    work = works.get("KWRK-000066")
    if not work or work.get("canonical_identifiers", {}).get("arxiv") != ARXIV_ID:
        errors.append("KWRK-000066 does not resolve to the representative arXiv source in Works")

    topics = (ROOT / "TOPICS.md").read_text(encoding="utf-8")
    if not re.search(r"^- \[ \] Context engineering as a discipline\b", topics, re.MULTILINE):
        errors.append("the planned-topic example must remain an unchecked TOPICS.md backlog item")

    return errors


def main() -> int:
    if not WIKI_INDEX.is_file():
        print(f"missing wiki navigation entry point: {WIKI_INDEX.relative_to(ROOT)}", file=sys.stderr)
        return 1
    errors: list[str] = []
    wiki_targets: set[str] = set()
    markdown_files = sorted((ROOT / "docs/wiki").rglob("*.md"))
    for markdown in markdown_files:
        link_errors, link_targets = check_local_links(markdown)
        errors.extend(f"{markdown.relative_to(ROOT)}: {error}" for error in link_errors)
        wiki_targets.update(link_targets)
    homepage_errors, homepage_targets = check_local_links(ROOT / "README.md")
    errors.extend(f"README.md: {error}" for error in homepage_errors)
    errors.extend(check_representative_routes(wiki_targets, homepage_targets))
    if errors:
        print("wiki navigation check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"wiki navigation checks passed: {len(wiki_targets)} wiki targets and representative article, backlog, crosswalk, and Works routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
