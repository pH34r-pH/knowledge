# Knowledge Corpus — Project Context

## Purpose and authority

This repository is a structured, evidence-gated engineering and ML knowledge corpus. It is not a service or an application runtime.

- Read `BUILDING.md` for the operating loop.
- Before fresh research, read `TOPICS.md`, `corpus/LEDGER.md`, and the relevant existing corpus material.
- The detailed corpus procedure is `.claude/skills/populate-corpus/SKILL.md`. Read it before corpus mutation; do not assume its Claude slash command is automatically available in another agent runtime.

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
- After source or procedure changes, run `graphify update .`. Keep semantic corpus extraction local unless the operator explicitly approves a cloud disclosure route.
