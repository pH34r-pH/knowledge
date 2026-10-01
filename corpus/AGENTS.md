# Corpus boundary

This directory is the living, human-readable knowledge surface. Articles are grouped
by pillar; `LEDGER.md` and the dated `CITATION-AUDIT-*.md` files retain the procedure's
history and evidence.

## Flow and ownership

```text
TOPICS.md -> resolved source pool -> corpus/<pillar>/<article>.md
                                  -> README.md index + LEDGER.md audit entry
```

- Change an article in `design-patterns/`, `ml-techniques/`, or `adjacent-knowledge/`
  when the mechanism or scope changes. Keep the article's frontmatter and source list
  synchronized with its evidence.
- Change [`../TOPICS.md`](../TOPICS.md) for backlog state and [`LEDGER.md`](LEDGER.md)
  for completed research/audit state; do not delete checked history to make the
  backlog look current.
- A dated audit or evaluation is retained evidence. It is not a living article and is
  not superseded without an explicit scope/date and supporting evidence.
- Keep private vault material out of this directory; generalize it before any public
  corpus entry.

Validation from the repository root:

```bash
python tools/test_external_claim_adapter.py
python tools/validate_external_claim_adapter.py --root .
git diff --check
```
