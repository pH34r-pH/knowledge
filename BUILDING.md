# Building the corpus

Everything needed to continue growing this knowledge corpus, in one place. The `corpus/` tree holds general-knowledge articles — software engineering design patterns, ML techniques, and adjacent high-value engineering knowledge — written for an ambitious mid-career engineer who wants the mechanism, not a 101. This file is the durable "how to continue"; the full executable protocol lives in the `populate-corpus` skill.

## How to run one iteration

Invoke the skill: **`/populate-corpus`** (from a Claude Code session with this repo as the working directory). One invocation = one atomic iteration: pick a topic → research it at the right depth → write a sourced article → audit its citations → update the index/ledger → commit and push. Re-invoke to keep building; wrap in `/loop populate-corpus` to run continuously.

The authoritative step-by-step is [.claude/skills/populate-corpus/SKILL.md](.claude/skills/populate-corpus/SKILL.md). The summary below is enough to continue without loading the skill.

## The loop, in seven steps

1. **Load state** — read [TOPICS.md](TOPICS.md) (backlog), [corpus/LEDGER.md](corpus/LEDGER.md) (what's done + how), the README index, and `~/brain/README.md` (the vault, for grounding — read-only).
2. **Select one topic** — highest expected-value unchecked item in `TOPICS.md`, **biased toward recent / post-cutoff material** (that's where a model with a training cutoff gains the most; see the eval below). Skip anything already in the ledger and still fresh. If a pillar's backlog is empty, propose 3–5 new candidates (recent-leaning), append them, then pick one.
3. **Choose a harness** (see below).
4. **Write the article** to `corpus/<pillar>/<slug>.md` — cite **only** from the sources the research stage already resolved.
5. **Citation integrity gate** (see below) — audit every citation before the article counts as done.
6. **Update the index and ledger** — one line in the README `## Corpus` list, one entry in `corpus/LEDGER.md`, check the box in `TOPICS.md`.
7. **Commit and push** — pathspec-scoped commit, `git pull --rebase --autostash origin main`, then `git push origin main`. Pushing is part of the loop; a run isn't done until it's backed up.

## The four research harnesses

Match the harness to the topic's shape — don't default to one:

| Topic shape | Harness | `method:` value |
|---|---|---|
| Already a mature, tested page in `~/brain/wiki/` | **vault-adapt** — generalize it (strip personal specifics), corroborate with public sources | `vault-adapt` |
| Converged technical exposition, no real camps | **deep-research** (built-in `/deep-research`, or reproduce its fan-out→verify→synthesize as workflow stages) | `deep-research` |
| Genuinely contested — the disagreement *is* the content | **storm** (`~/brain/agent-config/skills/storm/SKILL.md`), 3–4 perspectives | `storm` |
| Mechanism-rich **and** genuinely contested | **dual reconcile** — run both; deep-research → mechanism, STORM → contradiction map, merged into one article | `deep-research + storm` |

Do not run both on a clearly-converged topic — STORM will manufacture perspectives that don't exist. Before any fresh-research path, check `corpus/LEDGER.md` and `~/brain/wiki/meta/research-log.md` so you extend prior work instead of re-paying for it.

## Citation integrity is non-negotiable

The corpus is only as trustworthy as its citations; a fabricated or misgrounded reference is worse than no article. Every citation passes a gate before commit — deterministic checks first (they can't be gamed), then model-based. The full evidence base and guard list: [.claude/skills/populate-corpus/references/citation-integrity.md](.claude/skills/populate-corpus/references/citation-integrity.md). The gate is summarized in the [README](README.md#citation-integrity-how-the-corpus-avoids-hallucinated-references) as top-level information. Retroactive audit of the existing corpus: [corpus/CITATION-AUDIT-2026-07-01.md](corpus/CITATION-AUDIT-2026-07-01.md).

## Where everything lives

| Path | What it is |
|---|---|
| `corpus/<pillar>/*.md` | the articles (`design-patterns`, `ml-techniques`, `adjacent-knowledge`) |
| [TOPICS.md](TOPICS.md) | prioritized backlog, three pillars; the menu the loop picks from |
| [corpus/LEDGER.md](corpus/LEDGER.md) | one entry per completed article — method, sources, confidence, citation-audit tally |
| [.claude/skills/populate-corpus/SKILL.md](.claude/skills/populate-corpus/SKILL.md) | the full executable protocol |
| `.claude/skills/populate-corpus/references/citation-integrity.md` | citation-hallucination evidence base + guard list |
| `.claude/skills/populate-corpus/references/harness-options.md` | evaluation of external harnesses/skills (skillsmp.com) — what was adopted, deferred, or skipped and why |
| [specs/001-corpus-population-loop/](specs/001-corpus-population-loop/) | spec / plan / tasks (spec-kit) for the loop |
| `corpus/CITATION-AUDIT-*.md` | dated citation-audit reports |

## Public research identity maintenance

[`references/external/works.jsonl`](references/external/works.jsonl) remains the canonical Work registry. The dated literature audit keeps its historical rows and statuses; the generated [public bibliography identity crosswalk](reports/public-bibliography-identity-crosswalk-2026-10-07.json) maps public identities to those records without becoming another registry. Its companion [reviewed input](reports/research-identity-reconciliation-input-2026-10-07.json) retains unresolved identity leads, manuscript-bibliography-only sources, provisional candidates, nonpaper pointers, and names-only leads.

The bounded reconciliation contains 186 unique identities: 153 in the baseline union of 80 prior Works and 75 audit rows (two matches), plus 31 identity leads and two manuscript-bibliography sources. Three Work rows were added only for identities marked verified. A Work identity does not assert a finding, article adoption, or accepted claim. The 12 provisional candidates remain influence-unverified. This is not complete world-literature coverage; PR review threads and inaccessible Notion material remain gaps.

The dated [2026-10-08 research intake](references/external/research-intake-2026-10-08.md) adds 47 verified public source identities to `works.jsonl`; its companion audit maps those identities to canonical Work IDs and records unresolved technical-scope checks. The 186-identity reconciliation payload remains a reviewed snapshot rather than an expanding second registry. The intake adds no claims, evidence, articles, or adoption assertions.

The [2026-10-09 recurrent-dynamics intake](references/external/recurrent-dynamics-intake-2026-10-09.md) adds 13 public paper identities (`KWRK-000175`–`KWRK-000187`) around Lyapunov spectra, driven RNNs, task-relevant manifolds, looped-model stability and dynamical controls. It reuses existing C2C/Parcae/latent-transfer identities, with [scope/verification audit](references/external/recurrent-dynamics-intake-audit-2026-10-09.json). It adds **no** accepted claims, KnowledgeEvidence records, article or adoption assertions.

A [second 2026-10-09 recurrent-dynamics research pass](references/external/recurrent-dynamics-second-pass-2026-10-09.md) cross-checks non-normal transients, input-driven memory away from criticality, fixed-point recall, test-time loop-depth positives/negatives and representational invariance. Its [audit](references/external/recurrent-dynamics-second-pass-audit-2026-10-09.json) maps 13 additional verified public works (`KWRK-000188`–`KWRK-000200`) into the existing canonical registry. This is an identity/method intake, not accepted claims, evidence, articles, or a replication.

One metadata discrepancy is retained and tested: `KWRK-000001` lists the nGPT venue as ICLR 2025, while `dsl-pub-013` labels it an arXiv preprint (2024). The crosswalk records both values with their record IDs without adjudicating the difference.

For incremental updates, record the public source revision and update time, complete pagination for each selected issue and comment collection, and retain stable comment IDs with SHA-256 hashes of their complete normalized content so edits are detected. Record page counts and the terminal cursor/page marker. Advance the last verified successful checkpoint only after all pagination completes, identity validation passes, and the commit identifies that validated snapshot; otherwise retain the prior checkpoint and retry from it. Pin arXiv versions while deduplicating by DOI, arXiv ID without version, then canonical title plus first author. Add Work IDs only when the existing schema and identity checks pass.

Keep private provenance, private identifiers, and inferred private crosswalks in access-controlled maintainer notes; do not copy them into the public input or report. The 2026-10-07 transfer contained no issue-level comment manifest, so no comment IDs, hashes, or source cursors are fabricated here. Validate an update with `python tools/test_research_identity_crosswalk.py`, `python tools/reconcile_public_bibliography.py --check`, `python tools/test_external_claim_adapter.py`, and `python tools/validate_external_claim_adapter.py --root .`.

## Article shape

Frontmatter: `title`, `pillar`, `method`, `date`, `sources` (count), `confidence` (high/medium/low), optional `vault-links`. Body sections: **What it is · When to reach for it · How it works · Trade-offs · In practice · Further reading** (numbered, every non-obvious claim traceable to one). Write mechanism-first, senior-engineer register, ~700–1500 words.

## Repo & backup

- `origin` → `pH34r-pH/knowledge` (canonical, write access granted 2026-07-01). Shared repo — `git pull --rebase --autostash` before every push.
- `backup` → `github.com/haidmoham/knowledge-backup` (personal mirror, kept in sync as a secondary safety net).
- Read from `~/brain` for grounding, but **never write to it** — that vault has its own ownership and gating.

## Does feeding the corpus actually help?

A pre-registered blind eval ([corpus/EVAL-corpus-leverage-2026-07-01.md](corpus/EVAL-corpus-leverage-2026-07-01.md)) tested whether giving an LLM the relevant article improves its design answers, against a no-article control and an unrelated-article placebo. Result: **directional yes** — treatment won 100% of blind comparisons and beat the placebo by +1.62 quality, so the lift is content-specific, not context-stuffing. Caveats kept it from "proven": the rubric was corpus-derived (partly circular), the grader was the same model family, and the value was *completeness* (coverage 73%→99%), not the predicted blunder-avoidance (the base model avoided every trap unaided). Treat it as a promising signal to harden, not a settled result.

## Current state (2026-08-07)

26 articles are present (7 design-patterns, 13 ml-techniques, 6 adjacent-knowledge). The original 10-article corpus was retroactively audited (119 citations, zero fabricated; see `corpus/CITATION-AUDIT-2026-07-01.md`); later articles record their own source/audit status in `corpus/LEDGER.md`. The current expansion adds ten arXiv-grounded articles on constrained decoding, MoE routing, state-space/linear-attention alternatives, agent memory, self-evolving agents, fine-tuning strategy, supply-chain provenance, OpenTelemetry, structured concurrency, and actor/CSP coordination. Backlog in `TOPICS.md` now prioritizes context engineering and remaining foundational gaps such as outbox, PCA, regularization, testing strategy, observability practice, threat modeling, and vault-adapt generalizations.

## Claim-level recurrent-dynamics prior-art audit

The [2026-10-09 closure review](references/external/prior-art-closure-review-2026-10-09.md) connects the full 47-source review pool to its closest methodological predecessors and counterexamples. The [intake audit](references/external/prior-art-closure-audit-2026-10-09.json) maps 39 new identities and eight reused identities into the canonical Work registry, preserving all 200 prior records unchanged. Review depth and unresolved source limitations remain explicit; no independent replication, accepted scientific claim, or exhaustive-coverage assertion is made.
