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

## Article shape

Frontmatter: `title`, `pillar`, `method`, `date`, `sources` (count), `confidence` (high/medium/low), optional `vault-links`. Body sections: **What it is · When to reach for it · How it works · Trade-offs · In practice · Further reading** (numbered, every non-obvious claim traceable to one). Write mechanism-first, senior-engineer register, ~700–1500 words.

## Repo & backup

- `origin` → `pH34r-pH/knowledge` (canonical, write access granted 2026-07-01). Shared repo — `git pull --rebase --autostash` before every push.
- `backup` → `github.com/haidmoham/knowledge-backup` (personal mirror, kept in sync as a secondary safety net).
- Read from `~/brain` for grounding, but **never write to it** — that vault has its own ownership and gating.

## Does feeding the corpus actually help?

A pre-registered blind eval ([corpus/EVAL-corpus-leverage-2026-07-01.md](corpus/EVAL-corpus-leverage-2026-07-01.md)) tested whether giving an LLM the relevant article improves its design answers, against a no-article control and an unrelated-article placebo. Result: **directional yes** — treatment won 100% of blind comparisons and beat the placebo by +1.62 quality, so the lift is content-specific, not context-stuffing. Caveats kept it from "proven": the rubric was corpus-derived (partly circular), the grader was the same model family, and the value was *completeness* (coverage 73%→99%), not the predicted blunder-avoidance (the base model avoided every trap unaided). Treat it as a promising signal to harden, not a settled result.

## Current state (2026-07-02)

14 articles committed (5 design-patterns, 5 ml-techniques, 4 adjacent-knowledge), all citation-audited — the first two batches retroactively (119 citations, zero fabricated; see `corpus/CITATION-AUDIT-2026-07-01.md`), batch 3 through the gate as in-pipeline stages. Two more batch-3 articles (reasoning-models, preference-optimization — the first dual-harness run) are written but held back pending their citation audits. Backlog in `TOPICS.md`: the rest of the recent/post-cutoff cluster (DPO/GRPO and reasoning models in flight; MoE, SSMs, structured outputs, context engineering, supply-chain security, OTel remaining) plus the foundational fill-ins (outbox, actor model, structured concurrency, PCA, regularization, observability, threat modeling, testing strategy, and the vault-adapt generalizations).
