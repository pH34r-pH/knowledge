# arXiv source boundary

`arxiv/` retains paper inputs for the corpus's research and provenance workflows.
Each paper is represented by a PDF and a matching `*-meta.json` record.

- Treat the PDF/metadata pair as one immutable source identity.
- Add a new source with its resolved identifier and metadata; do not rename or
  rewrite an older source merely to match a newer interpretation.
- Article prose belongs in [`../corpus/`](../corpus/); machine-readable evidence belongs
  in [`../references/external/`](../references/external/).
- This is retained evidence/history, not a generated cache. Do not delete files because
  they are not linked from the current README index.

The repository-wide citation and registry checks are documented in [`../AGENTS.md`](../AGENTS.md)
and [`../BUILDING.md`](../BUILDING.md).
