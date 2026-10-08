# Knowledge Corpus — Project Context

## Purpose and authority

This repository is a structured, evidence-gated engineering and ML knowledge corpus. It is not a service or an application runtime.

- Read `BUILDING.md` for the operating loop.
- Before fresh research, read `TOPICS.md`, `corpus/LEDGER.md`, and the relevant existing corpus material.
- The detailed corpus procedure is `.claude/skills/populate-corpus/SKILL.md`. Read it before corpus mutation; do not assume its Claude slash command is automatically available in another agent runtime.

## Repository map

This repository is a research corpus and evidence store, not an application runtime.
The primary downward flow is:

```text
TOPICS.md / existing corpus
        -> source-resolution and audit records
        -> corpus/<pillar>/*.md
        -> README.md index and corpus/LEDGER.md
        -> docs/wiki/ link-only navigation
```

| Boundary | Change here | Ownership and invariants |
| --- | --- | --- |
| `corpus/` | Sourced, mechanism-first articles, audit records, and the append-only ledger; see [`corpus/AGENTS.md`](corpus/AGENTS.md). | Article claims stay within their resolved evidence; history is retained and dated. |
| `arxiv/` | Downloaded paper PDFs and matching metadata; see [`arxiv/AGENTS.md`](arxiv/AGENTS.md). | The metadata/PDF pair is a retained source identity; do not rewrite a historical source to make a current claim fit. |
| `references/external/` | Machine-readable claims, works, evidence, schemas, and scoped import audits; see [`references/AGENTS.md`](references/AGENTS.md). | Registry records are provenance, not prose; preserve exact IDs, URLs, digests, and audit scope. |
| `specs/` | Spec Kit plans and acceptance records for corpus procedures. | Preserve the `spec.md → plan.md → tests.md → tasks.md` authority chain and historical evidence. |
| `docs/wiki/` | Link-only entry points into canonical guides, corpus articles, backlog, and source records. | Keep article and source content at its canonical path; wiki navigation must not create a parallel article or source registry. |
| `.claude/skills/` | The executable research procedure and its references. | Update the procedure only when the operating loop changes; do not use it as a substitute for source evidence. |

The living Markdown surface is the root guides, scoped `AGENTS.md` maps, `docs/wiki/`
navigation, `corpus/LEDGER.md`, and current articles under
`corpus/{design-patterns,ml-techniques,adjacent-knowledge}/`. Dated citation audits,
reports, spec plans, arXiv inputs, and registry records are retained history/evidence; a
newer document supersedes one only when it states the scope and provides evidence for
that change. Documentation CI selects only that living surface; it does not treat every
retained artifact as current prose.

## Research integrity gates

- Select one uncovered, high-value topic per iteration. Do not duplicate current ledger-covered work.
- Choose the research harness from the topic shape: vault-adapt, deep research, STORM, or the documented dual-harness path.
- Write only from a pre-resolved source pool. Every non-obvious claim must have a source that passed resolution, quote-span, liveness, and independent-entailment checks.
- A plausible but ungrounded citation is a failure. Drop unresolved, mismatched, dead, or unsupported references.
- Preserve article frontmatter and the required mechanism-first structure.
- Record the audit result, method, confidence, and source counts in `corpus/LEDGER.md`; update `README.md` and `TOPICS.md` in the same iteration.

## Vault, privacy, and provenance boundaries

- `~/brain` is read-only grounding material. Never write to it from this repository.
- Generalize private or personal material before it enters this corpus. Do not add PII, client-specific details, secrets, or unpublished private evidence.
- Preserve canonical URLs, DOIs, arXiv IDs, quotations, dates, and uncertainty. Do not silently rewrite historical findings; record staleness in the ledger.

## Spec Kit contract

Use the existing feature convention in `specs/<NNN-feature>/`.

```text
spec.md → plan.md → tests.md → tasks.md
```

- For this Markdown corpus, `tests.md` can define manual or deterministic content-validation evidence when no executable test harness applies.
- `spec.md` owns corpus behavior and acceptance; `plan.md` owns the operating mechanism; `tests.md` owns validation; `tasks.md` owns executable work.
- The inherited security-oriented `.specify` constitution is not the corpus operating procedure. Treat `BUILDING.md`, the corpus skill, and the feature package as the relevant local authority unless a corpus-specific constitution replaces it.

## Git and verification discipline

- Verify article frontmatter, citation evidence, index, backlog, and ledger consistency before commit.
- Use explicit pathspec-scoped commits. Do not use broad staging in this shared repository.
- Before push, run `git pull --rebase --autostash origin main`; report a rejected push or merge conflict plainly rather than masking it.
- A corpus iteration is not complete until its approved changed paths are committed and pushed, unless external authorization or connectivity blocks that final step.
- After source or procedure changes, run the deterministic schema, citation, index, and documentation checks relevant to the changed paths. The corpus has no generated semantic index to refresh.

## Documentation changes and validation

- Put corpus content in `corpus/<pillar>/`, source evidence in `arxiv/` or
  `references/external/`, and procedural explanations in `BUILDING.md` or the
  relevant spec. Do not create a second inventory just for a map.
- Use descriptive names for new living Markdown. Single-word names such as `README.md`,
  `AGENTS.md`, and `STYLE.md` are valid; new numeric-only or issue-number-only
  living docs such as `123.md` and `issue-123.md` are not. Meaningful numbered
  article/evidence IDs remain valid in their historical or machine-readable locations.
- Keep Markdown links relative when they point into this repository so the link
  checker exercises the map references.
- Keep `docs/wiki/` pages as a navigation surface over canonical repository files.
  Local links and representative corpus-to-source routes are checked by
  `python tools/test_wiki_navigation.py`.

Exact local checks for a documentation-only change are:

```bash
git diff --check
git fetch origin main
python tools/check_documentation_hygiene.py --base origin/main --head HEAD --self-test
python tools/test_wiki_navigation.py
python tools/test_external_claim_adapter.py
python tools/validate_external_claim_adapter.py --root .
DOCS_FILE="$(mktemp)"
python tools/check_documentation_hygiene.py --base origin/main --head HEAD --print-docs > "$DOCS_FILE"
if test -s "$DOCS_FILE"; then mapfile -t DOCS < "$DOCS_FILE"; npx --yes markdownlint-cli2@0.18.1 --config .markdownlint-cli2.mjs "${DOCS[@]}"; lychee --offline --verbose --no-progress "${DOCS[@]}"; fi
```
