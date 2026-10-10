"""Check the Wiki projection, links, statuses, and canonical source routes."""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

from render_wiki import (
    MANIFEST_NAME,
    REPOSITORY,
    render_pages,
    source_articles,
    source_works,
    validate_projection,
    write_projection,
)

ROOT = Path(__file__).resolve().parents[1]
ARXIV_ID = "1701.06538"


def check_readme_links() -> list[str]:
    errors: list[str] = []
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    if "docs/wiki/Home.md" not in text:
        errors.append("repository README must link to docs/wiki/Home.md")
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        parsed = urlsplit(target.strip().split(maxsplit=1)[0].strip("<>"))
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        path = (ROOT / unquote(parsed.path)).resolve()
        if not path.exists():
            errors.append(f"README.md links to a missing path: {target}")
        if parsed.fragment == "corpus" and path.is_file() and "## Corpus" not in path.read_text(encoding="utf-8"):
            errors.append(f"README.md links to a missing heading: {target}")
    return errors


def check_article_citation(pages: dict[str, str]) -> list[str]:
    article = next((row for row in source_articles(ROOT) if row["path"].endswith("mixture-of-experts-routing.md")), None)
    if article is None:
        return ["MoE article is missing from the canonical README index"]
    article_page = pages[article["page"]]
    if not re.search(rf"arxiv\.org/abs/{ARXIV_ID}(?:v\d+)?", article_page):
        return [f"generated MoE page does not preserve its arXiv:{ARXIV_ID} citation"]
    return []


def check_crosswalk_mapping() -> list[str]:
    crosswalk_path = ROOT / "reports/public-bibliography-identity-crosswalk-2026-10-07.json"
    crosswalk = json.loads(crosswalk_path.read_text(encoding="utf-8"))
    matches = [row for row in crosswalk["sources"] if row.get("canonical_key") == f"arxiv:{ARXIV_ID}"]
    if len(matches) != 1:
        return [f"crosswalk must contain one public identity for arXiv:{ARXIV_ID}"]
    work_ids = [row.get("id") for row in matches[0].get("work_records", []) if isinstance(row, dict)]
    if work_ids != ["KWRK-000066"]:
        return [f"arXiv:{ARXIV_ID} no longer maps to the expected Work ID: {work_ids!r}"]
    return []


def check_registry_route(pages: dict[str, str]) -> list[str]:
    works = {record.get("id"): record for _, record in source_works(ROOT)}
    work = works.get("KWRK-000066")
    errors: list[str] = []
    if not work or work.get("canonical_identifiers", {}).get("arxiv") != ARXIV_ID:
        errors.append(f"KWRK-000066 does not resolve to arXiv:{ARXIV_ID} in Works")
    if "KWRK-000066" not in pages["Works.md"]:
        errors.append("generated Works page is missing the representative Work ID")
    if "public-bibliography-identity-crosswalk" not in pages["Research-sources.md"]:
        errors.append("generated Research-sources page is missing the identity crosswalk")
    return errors


def check_source_route(pages: dict[str, str]) -> list[str]:
    return check_article_citation(pages) + check_crosswalk_mapping() + check_registry_route(pages)


def check_sync_preserves_unmanaged_pages(pages: dict[str, str]) -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="knowledge-wiki-projection-") as temporary:
        output = Path(temporary)
        write_projection(ROOT, output, pages)
        for page, contents in pages.items():
            if (output / page).read_text(encoding="utf-8") != contents:
                errors.append(f"renderer output differs for {page}")

        owner_page = output / "Owner-notes.md"
        owner_page.write_text("Owner-authored page\n", encoding="utf-8")
        stale_page = output / "Old-generated-article.md"
        stale_page.write_text("Old generated output\n", encoding="utf-8")
        manifest_path = output / MANIFEST_NAME
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["pages"].append(stale_page.name)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        write_projection(ROOT, output, pages)
        if not owner_page.is_file():
            errors.append("Wiki sync deleted an unmanaged owner page")
        if stale_page.exists():
            errors.append("Wiki sync did not remove a stale page it had previously managed")

    with tempfile.TemporaryDirectory(prefix="knowledge-wiki-conflict-") as temporary:
        output = Path(temporary)
        conflict = output / "Corpus.md"
        conflict.write_text("Owner-authored Corpus page\n", encoding="utf-8")
        try:
            write_projection(ROOT, output, pages)
        except ValueError as error:
            if "unmanaged Wiki page" not in str(error):
                errors.append(f"unexpected managed-page conflict: {error}")
        else:
            errors.append("Wiki sync overwrote an unmanaged page with a generated page name")
        if conflict.read_text(encoding="utf-8") != "Owner-authored Corpus page\n":
            errors.append("Wiki sync changed an unmanaged page before reporting its conflict")

    with tempfile.TemporaryDirectory(prefix="knowledge-wiki-manifest-") as temporary:
        temporary_path = Path(temporary)
        output = temporary_path / "wiki"
        output.mkdir()
        target = temporary_path / "outside-manifest.json"
        target.write_text('{"schema_version":"1","pages":[]}\n', encoding="utf-8")
        (output / MANIFEST_NAME).symlink_to(target)
        try:
            write_projection(ROOT, output, pages)
        except ValueError as error:
            if "symlinked Wiki manifest" not in str(error):
                errors.append(f"unexpected symlinked-manifest error: {error}")
        else:
            errors.append("Wiki sync accepted a symlinked generated-page manifest")
        if target.read_text(encoding="utf-8") != '{"schema_version":"1","pages":[]}\n':
            errors.append("Wiki sync changed a manifest target outside the Wiki checkout")
    return errors


def main() -> int:
    try:
        pages = render_pages(ROOT)
        errors = validate_projection(ROOT, pages)
        errors.extend(check_readme_links())
        errors.extend(check_source_route(pages))
        errors.extend(check_sync_preserves_unmanaged_pages(pages))
        if "Welcome to the knowledge wiki!" not in pages["Home.md"]:
            errors.append("the Wiki Home page created by the owner was not preserved")
        if "**Planned**" not in pages["Planned-topics.md"]:
            errors.append("planned backlog entries are not visibly marked as planned")
        if f"https://github.com/{REPOSITORY}/blob/main" not in pages["Works.md"]:
            errors.append("Works entries must link back to the canonical registry")
        if errors:
            print("wiki navigation check failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        print(
            f"wiki navigation checks passed: {len(pages)} generated pages, "
            f"{len(source_articles(ROOT))} articles, {len(source_works(ROOT))} Works records; "
            "links and owner-page preservation verified"
        )
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"wiki navigation check failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
