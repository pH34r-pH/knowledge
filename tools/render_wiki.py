"""Render a deterministic, link-checked projection for the Knowledge GitHub Wiki.

This tool writes only to the path passed with ``--output-dir``. It never clones,
commits, or pushes; the canonical repository remains the source of every page.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

REPOSITORY = "pH34r-pH/knowledge"
MAIN_BLOB_URL = f"https://github.com/{REPOSITORY}/blob/main"
ARTICLE_LINE = re.compile(
    r"^- \[(?P<title>.+?)\]\((?P<path>corpus/[^)]+\.md)\)(?: — (?P<summary>.*))?$"
)
TOPIC_LINE = re.compile(r"^- \[ \] (?P<topic>.+)$")
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
MANIFEST_NAME = ".knowledge-wiki-sync.json"


def markdown_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]").replace("|", "\\|")


def blob_url(path: str, line: int | None = None) -> str:
    source_path, separator, fragment = path.partition("#")
    url = f"{MAIN_BLOB_URL}/{quote(source_path, safe="/._-")}"
    if line:
        return f"{url}#L{line}"
    return f"{url}#{fragment}" if separator else url


def source_articles(root: Path) -> list[dict[str, str]]:
    readme = (root / "README.md").read_text(encoding="utf-8").splitlines()
    try:
        start = readme.index("## Corpus") + 1
    except ValueError as error:
        raise ValueError("README.md must contain the canonical '## Corpus' index") from error

    category: str | None = None
    articles: list[dict[str, str]] = []
    for line in readme[start:]:
        if line.startswith("## "):
            break
        if line.startswith("**") and line.endswith("**"):
            category = line[2:-2]
            continue
        if not line.startswith("- ["):
            continue
        match = ARTICLE_LINE.fullmatch(line)
        if not match or category is None:
            raise ValueError(f"unrecognized corpus-index entry: {line}")
        path = match.group("path")
        if not (root / path).is_file():
            raise ValueError(f"README corpus entry points to a missing article: {path}")
        articles.append(
            {
                "title": match.group("title"),
                "path": path,
                "page": f"{Path(path).stem}.md",
                "category": category,
                "summary": match.group("summary") or "",
            }
        )
    if not articles:
        raise ValueError("README.md corpus index contains no articles")
    paths = [article["path"] for article in articles]
    pages = [article["page"] for article in articles]
    if len(paths) != len(set(paths)) or len(pages) != len(set(pages)):
        raise ValueError("corpus index has duplicate article paths or Wiki page names")
    corpus_roots = (
        root / "corpus/design-patterns",
        root / "corpus/ml-techniques",
        root / "corpus/adjacent-knowledge",
    )
    actual_articles = {
        path.relative_to(root).as_posix()
        for corpus_root in corpus_roots
        for path in corpus_root.glob("*.md")
    }
    unindexed = actual_articles - set(paths)
    if unindexed:
        raise ValueError(f"corpus articles missing from canonical README index: {sorted(unindexed)}")
    return articles


def source_works(root: Path) -> list[tuple[int, dict[str, object]]]:
    registry = root / "references/external/works.jsonl"
    records: list[tuple[int, dict[str, object]]] = []
    identifiers: set[str] = set()
    for line_number, line in enumerate(registry.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        identifier = record.get("id")
        if not isinstance(identifier, str) or identifier in identifiers:
            raise ValueError(f"invalid or duplicate Work id at line {line_number}: {identifier!r}")
        identifiers.add(identifier)
        records.append((line_number, record))
    return records


def strip_frontmatter(article: str, source_path: str) -> str:
    lines = article.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"article has no YAML frontmatter delimiter: {source_path}")
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as error:
        raise ValueError(f"article frontmatter is not closed: {source_path}") from error
    return "\n".join(lines[end + 1 :]).strip()


def planned_topics(root: Path) -> list[tuple[str, list[str]]]:
    topics = (root / "TOPICS.md").read_text(encoding="utf-8").splitlines()
    grouped: list[tuple[str, list[str]]] = []
    category: str | None = None
    for line in topics:
        if line.startswith("## "):
            category = line[3:].strip()
        match = TOPIC_LINE.fullmatch(line)
        if not match:
            continue
        if category is None:
            raise ValueError(f"planned topic appears before a section heading: {line}")
        raw = match.group("topic")
        title = raw.split(" — ", maxsplit=1)[0].strip()
        if not grouped or grouped[-1][0] != category:
            grouped.append((category, []))
        grouped[-1][1].append(title)
    return grouped


def rewrite_article_links(root: Path, article: dict[str, str], page_by_source: dict[str, str], body: str) -> str:
    source_file = root / article["path"]

    def rewrite(match: re.Match[str]) -> str:
        target = match.group(1)
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            return match.group(0)
        resolved = (source_file.parent / unquote(parsed.path)).resolve()
        try:
            relative = resolved.relative_to(root).as_posix()
        except ValueError:
            return match.group(0)
        if relative in page_by_source:
            page_target = page_by_source[relative]
        elif resolved.is_file():
            page_target = blob_url(relative)
        else:
            raise ValueError(f"article link points to a missing source file: {article['path']} -> {target}")
        if parsed.fragment:
            page_target = f"{page_target}#{unquote(parsed.fragment)}"
        return f"[{match.group(0).split('](', maxsplit=1)[0][1:]}]({page_target})"

    return MARKDOWN_LINK.sub(rewrite, body)


def render_pages(root: Path) -> dict[str, str]:
    articles = source_articles(root)
    page_by_source = {article["path"]: article["page"] for article in articles}
    pages: dict[str, str] = {}
    pages["Home.md"] = (root / "docs/wiki/Home.md").read_text(encoding="utf-8")
    pages["_Sidebar.md"] = (root / "docs/wiki/_Sidebar.md").read_text(encoding="utf-8")

    corpus_lines = [
        "# Completed corpus",
        "",
        "This index is generated from the canonical [README corpus index](" + blob_url("README.md#corpus") + "). Article pages below are readable projections of the canonical files; follow each source link for the repository record.",
        "",
    ]
    current_category: str | None = None
    for article in articles:
        if article["category"] != current_category:
            current_category = article["category"]
            corpus_lines.extend([f"## {current_category}", ""])
        summary = f" — {article['summary']}" if article["summary"] else ""
        canonical = blob_url(article["path"])
        corpus_lines.append(
            f"- [{markdown_text(article['title'])}]({article['page']}){summary} · "
            f"[canonical source]({canonical})"
        )
    corpus_lines.append("")
    pages["Corpus.md"] = "\n".join(corpus_lines)

    topic_groups = planned_topics(root)
    topic_lines = [
        "# Planned topics",
        "",
        f"Generated from [TOPICS.md]({blob_url('TOPICS.md')}). These are backlog proposals, not findings, accepted claims, or completed articles.",
        "",
    ]
    for category, titles in topic_groups:
        topic_lines.extend([f"## {category}", ""])
        topic_lines.extend(f"- **Planned** — {markdown_text(title)}" for title in titles)
        topic_lines.append("")
    if not topic_groups:
        topic_lines.extend(["No unchecked topics are currently listed in the canonical backlog.", ""])
    pages["Planned-topics.md"] = "\n".join(topic_lines)

    crosswalk_path = "reports/public-bibliography-identity-crosswalk-2026-10-07.json"
    audit_path = "reports/domain-scaling-lab-literature-audit-2026-09-01.md"
    source_lines = [
        "# Research sources",
        "",
        "The Works catalog is the canonical registry for Work IDs. The public identity crosswalk also preserves aliases and provisional leads; an identity by itself does not assert a finding, accepted claim, or adoption.",
        "",
        f"- [Works catalog](Works.md)",
        f"- [Canonical Works registry]({blob_url('references/external/works.jsonl')})",
        f"- [Public bibliography identity crosswalk]({blob_url(crosswalk_path)})",
        f"- [Dated public literature audit]({blob_url(audit_path)})",
        f"- [Source maintenance and validation](" + blob_url("BUILDING.md") + ")",
        "",
    ]
    pages["Research-sources.md"] = "\n".join(source_lines)

    works = source_works(root)
    work_lines = [
        "# Works catalog",
        "",
        f"Generated index of {len(works)} canonical Work records. Each record link points to its line in [works.jsonl]({blob_url('references/external/works.jsonl')}); bibliographic identity and status do not imply claim acceptance or article adoption.",
        "",
    ]
    for line_number, record in works:
        identifier = str(record["id"])
        title = markdown_text(str(record["title"]))
        status = markdown_text(str(record.get("status", "unspecified")))
        canonical_record = blob_url("references/external/works.jsonl", line_number)
        source = record.get("source_url")
        if isinstance(source, str) and source:
            parsed_source = urlsplit(source)
            if parsed_source.scheme.lower() in {"http", "https"} and parsed_source.netloc:
                title_link = f"[{title}]({quote(source, safe=":/?#[]@!$&'*+,;=%")})"
            else:
                title_link = title
        else:
            title_link = title
        work_lines.append(f"- [`{identifier}`]({canonical_record}) — {title_link} · {status}")
    work_lines.append("")
    pages["Works.md"] = "\n".join(work_lines)

    for article in articles:
        canonical = blob_url(article["path"])
        body = strip_frontmatter((root / article["path"]).read_text(encoding="utf-8"), article["path"])
        body = rewrite_article_links(root, article, page_by_source, body)
        page = (
            f"> Generated from the canonical [{article['path']}]({canonical}). "
            "Edit the repository source; this Wiki page is refreshed from it.\n\n"
            f"[Back to corpus index](Corpus.md)\n\n{body}\n"
        )
        pages[article["page"]] = page
    return pages


def validate_projection(root: Path, pages: dict[str, str]) -> list[str]:
    errors: list[str] = []
    required = {"Home.md", "_Sidebar.md", "Corpus.md", "Planned-topics.md", "Research-sources.md", "Works.md"}
    missing = required - pages.keys()
    if missing:
        errors.append(f"projection is missing pages: {sorted(missing)}")

    for page_name, text in pages.items():
        for target in MARKDOWN_LINK.findall(text):
            target = target.strip().split(maxsplit=1)[0].strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                if parsed.hostname == "github.com":
                    wiki_prefix = f"/{REPOSITORY}/wiki/"
                    if parsed.path.rstrip("/") == f"/{REPOSITORY}/wiki":
                        wiki_page = "Home"
                    elif parsed.path.startswith(wiki_prefix):
                        wiki_page = unquote(parsed.path[len(wiki_prefix) :]).split("/", maxsplit=1)[0]
                    else:
                        wiki_page = ""
                    if wiki_page:
                        if wiki_page and f"{wiki_page}.md" not in pages:
                            errors.append(f"{page_name}: missing Wiki destination {wiki_page}")
                    prefix = f"/{REPOSITORY}/blob/main/"
                    if parsed.path.startswith(prefix):
                        path = unquote(parsed.path[len(prefix) :])
                        if not (root / path).is_file():
                            errors.append(f"{page_name}: missing canonical repository target {path}")
                continue
            target_path = unquote(parsed.path)
            if target_path and target_path not in pages:
                errors.append(f"{page_name}: missing Wiki page target {target_path}")

    corpus_index = pages.get("Corpus.md", "")
    articles = source_articles(root)
    expected_articles = {article["page"] for article in articles}
    indexed_articles = {
        unquote(urlsplit(target).path)
        for target in MARKDOWN_LINK.findall(corpus_index)
        if not urlsplit(target).scheme and unquote(urlsplit(target).path) in expected_articles
    }
    if indexed_articles != expected_articles:
        errors.append("Corpus.md does not link every canonical README article exactly by its Wiki page")

    topics = planned_topics(root)
    expected_topics = sum(len(items) for _, items in topics)
    planned_entries = len(re.findall(r"^- \*\*Planned\*\* — ", pages.get("Planned-topics.md", ""), re.MULTILINE))
    if planned_entries != expected_topics:
        errors.append(f"Planned-topics.md contains {planned_entries} entries; TOPICS.md has {expected_topics}")

    works = source_works(root)
    work_entries = len(re.findall(r"^- \[`KWRK-[0-9]+`\]", pages.get("Works.md", ""), re.MULTILINE))
    if work_entries != len(works):
        errors.append(f"Works.md contains {work_entries} entries; works.jsonl has {len(works)}")
    return errors


def write_projection(root: Path, output_dir: Path, pages: dict[str, str]) -> None:
    destination = output_dir.resolve()
    source = root.resolve()
    if destination == source or source in destination.parents:
        raise ValueError("Wiki output must be outside the knowledge source checkout")
    if not destination.is_dir():
        raise ValueError(f"Wiki output directory must already exist: {destination}")

    manifest = destination / MANIFEST_NAME
    previous: set[str] = set()
    if manifest.is_symlink():
        raise ValueError(f"refusing to read or overwrite a symlinked Wiki manifest: {manifest}")
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("schema_version") != "1" or not isinstance(data.get("pages"), list):
            raise ValueError(f"invalid generated-Wiki manifest: {manifest}")
        for value in data["pages"]:
            if not isinstance(value, str) or Path(value).name != value or not value.endswith(".md"):
                raise ValueError(f"unsafe generated page in manifest: {value!r}")
            previous.add(value)

    current = set(pages)
    for stale in sorted(previous - current):
        stale_path = destination / stale
        if stale_path.is_file():
            stale_path.unlink()
    for page_name, content in pages.items():
        page_path = destination / page_name
        if page_path.is_symlink():
            raise ValueError(f"refusing to overwrite a symlink in Wiki checkout: {page_name}")
        if page_path.exists() and page_name not in previous:
            existing = page_path.read_text(encoding="utf-8")
            if page_name != "Home.md" or not content.startswith(existing):
                raise ValueError(f"refusing to overwrite an unmanaged Wiki page: {page_name}")
        page_path.write_text(content, encoding="utf-8")
    manifest.write_text(
        json.dumps({"schema_version": "1", "pages": sorted(current)}, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="existing Wiki clone or separate preview directory")
    parser.add_argument("--check", action="store_true", help="validate the deterministic projection without writing files")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        pages = render_pages(root)
        errors = validate_projection(root, pages)
        if errors:
            raise ValueError("\n".join(errors))
        if args.check:
            print(f"Wiki projection valid: {len(pages)} pages from README, TOPICS, corpus, and Works")
            return 0
        if args.output_dir is None:
            parser.error("pass --output-dir or --check")
        write_projection(root, args.output_dir, pages)
        print(f"Rendered {len(pages)} deterministic Wiki pages into {args.output_dir}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Wiki projection failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
