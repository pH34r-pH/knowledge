---
name: populate-corpus
description: Run one iteration of the researcher loop that builds out this repo's knowledge corpus — software engineering design patterns, ML techniques, and other high-value knowledge for an ambitious, curious mid-career software engineer. Selects the highest-value uncovered topic, picks the right-weight research harness (reuse the vault, deep-research, or STORM), writes a sourced article, and updates the index/ledger. Use when asked to "populate the corpus", "grow the knowledge base", "add a topic", "run the research loop", or when this skill is re-invoked to keep building the repo.
---

# Populate Corpus — the researcher loop

You are acting as a researcher systematically building this repo into a corpus of durable, high-value technical knowledge — software engineering design patterns, machine learning techniques, and anything else you have real evidence is worth an ambitious, knowledge-hungry mid-career software engineer's time. Not a link dump, not a survey of whatever is trending this month — each article should be the kind of thing that still holds up in two years.

This skill defines **one atomic iteration** of that loop: pick a topic, research it at the right depth, write it up, update the index, commit. Re-invoke it (by hand, or wrapped in `/loop populate-corpus`) to keep building. Each run is self-contained and checkpointed — killing the loop mid-run never leaves the repo in a broken state, because the commit at the end of a run is the only state change.

Full rationale and requirements: [specs/001-corpus-population-loop/spec.md](../../../specs/001-corpus-population-loop/spec.md).

## Boundaries (read first)

- **Back up every run — this is a durable knowledge base, not a one-off artifact.** Each run ends by committing (pathspec-scoped, never a broad `git add`) *and pushing* to the canonical remote so the corpus is never stranded on one machine. Push to `origin` (`pH34r-pH/knowledge`) — collaborator access was granted 2026-07-01. A personal mirror also exists at `backup` (`github.com/haidmoham/knowledge-backup`) from before access landed; keep it as a secondary safety net but `origin` is now the source of truth (see Step 7).
- **Read from `~/brain`, never write to it.** The vault is a personal, curated knowledge base with its own ownership and gating rules (see `~/brain/CLAUDE.md`). This loop may read vault pages for grounding and cross-link to them, but a corpus article here must never cause a vault write — that direction of flow belongs to the vault's own `/paper` and `/librarian` skills, not to this one.
- **Quality over throughput.** One well-sourced, well-reasoned article beats five thin ones. If a candidate topic turns out to be too shallow, too faddish, or already well covered elsewhere in the corpus, say so in the output and pick the next one rather than force a low-value entry.

## Step 1 — Load state

Read, in order:
1. `TOPICS.md` at the repo root — the prioritized backlog across the three pillars. This is the menu; do not invent topics outside it without adding them here first (see Step 2).
2. `corpus/LEDGER.md` — every prior run: topic, method, sources, confidence, file. Skip anything already done and still fresh; if a done entry looks stale (the *field* moved, e.g. a technique got superseded — not the write itself), note it in the output but still prefer a fresh topic this run.
3. `README.md` — the current article index, so the new entry doesn't duplicate existing structure.
4. `/Users/haidmoham/brain/README.md` — the vault's master catalog. Grep it for the candidate topic's keywords before researching. If a mature, `experience`-tier `wiki/concepts/` or `wiki/entities/` page already covers it, that's a grounding source and possibly enough on its own — see Step 3.

## Step 2 — Select the topic

Pick exactly one unchecked topic from `TOPICS.md`, highest expected-value first, skipping anything already covered per the ledger.

**Rank by marginal value to an LLM, not by importance in the abstract.** The corpus exists to be fed to a model that already has a training cutoff, so the highest-EV topics are the ones the model knows *least*: recent and fast-moving material. A pre-registered eval ([corpus/EVAL-corpus-leverage-2026-07-01.md](../../../corpus/EVAL-corpus-leverage-2026-07-01.md)) found even well-covered foundational topics get a real completeness lift — but recent/post-cutoff topics are where the corpus adds knowledge the model doesn't already hold, so they carry the highest EV. Rank:

1. **Recency first (the steering bias).** Prefer topics whose load-bearing content is recent — roughly the last 12–18 months, and especially anything that postdates common model training cutoffs: new techniques, new tooling/protocol standards, shifted best practices, results that weren't settled at training time. Highest-EV band.
2. **Contested or newly-synthesized second.** Where no clean authoritative summary existed yet, or practitioners still disagree — the model's parametric take is thin or averaged-out.
3. **Foundational only with a fresh angle.** A canonical topic still earns a slot if it carries a genuinely contested trade-off, a recent development, or a synthesis the model won't reproduce cold; a plain "what is X" explainer on a saturated, stable topic is the *lowest* EV — deprioritize it.

Quality bars that still apply regardless of recency:
- recurs across multiple independent authoritative sources, not one blog's opinion;
- substantive enough to still matter in ~1–2 years (recent ≠ ephemeral — skip anything obsolete in six months);
- fills a vault ML gap (`/Users/haidmoham/brain/wiki/concepts/self-study-ml-engineering.md`, `/Users/haidmoham/brain/wiki/concepts/ml-pivot-diagnostic-2026-07-01.md`) or extends the live `arxiv/`/`reports/` research cluster where relevant.

**Recency and citation integrity reinforce each other.** Recent papers/tools are exactly where a model is most likely to misremember or fabricate, so a recent topic MUST go through a live-retrieval harness (`deep-research` or `storm`), never `vault-adapt`-from-memory, and its citations get the full Step 5 gate.

If a pillar has no unchecked topics left, propose 3–5 new candidates, **biased toward recent/post-cutoff material**, append them to `TOPICS.md` (one-line justification each), then pick one — keep the backlog self-sustaining rather than stalling the loop.

## Step 3 — Decide the research harness

Match the harness to the topic's shape. There are four modes; the two fresh-research methods (`deep-research` and `storm`) do genuinely different jobs, so don't default to one.

- **Vault-adapt (reuse).** The topic is already a mature, `experience`-tier page in `~/brain/wiki/`. Read it, generalize for this corpus (strip personal specifics — project names, individual decisions, companies), cite it as internal provenance, and corroborate with a few public sources. Use whenever it genuinely applies rather than re-researching owned, tested knowledge. You may layer a light fresh pass on top to extend it (e.g. grounding a vault methodology in this repo's own `arxiv/` papers).
- **deep-research (the built-in `/deep-research` skill).** The topic has a converged, mostly-agreed technical exposition — an algorithm, a mechanism, an established technique — where the value is breadth and correct sourcing, not adversarial framing. Invoke `/deep-research` with the topic as the question, **or** reproduce its method (fan-out search → adversarial verify → synthesize) as workflow stages; both count as this harness.
- **storm (the `storm` skill at `/Users/haidmoham/brain/agent-config/skills/storm/SKILL.md`).** The topic is genuinely contested — real practitioners disagree and the disagreement itself is the content (e.g. "when does CQRS earn its complexity", "RAG vs long-context vs fine-tuning"). Run STORM's multi-perspective, retrieval-grounded workflow, sized to 3–4 perspectives for a corpus article. Every claim still traces to a retrieved source — no answering from memory.
- **Dual-harness reconcile (deep-research AND storm).** For a topic that is BOTH mechanism-rich AND genuinely contested — real technical machinery to explain *and* a live practitioner debate over when/whether to use it — run both and reconcile. This mode is deliberately reserved for that overlap: running both on a clearly-converged topic just makes STORM invent perspectives that don't exist, and running only one on a both-shaped topic under-serves it. Reconciliation:
  1. deep-research → mechanism + breadth + sources (feeds *What it is* / *How it works*).
  2. STORM → perspectives + contradiction map + sources (feeds *Trade-offs*).
  3. Merge into ONE article: dedupe and renumber sources across both; take the mechanism from deep-research and the debate map from STORM. Where the two disagree on a *checkable* fact, surface the disagreement and prefer the better-sourced side with a confidence note — do not smooth it over.
  4. Record `method: deep-research + storm` and one ledger entry.

Decision signal, in order: mature tested vault page → vault-adapt; the debate is the point and the mechanism is thin → storm; substantial mechanism with no real camps → deep-research; substantial mechanism *and* a genuine debate → dual reconcile.

Before any fresh-research path, check `corpus/LEDGER.md` **and** `/Users/haidmoham/brain/wiki/meta/research-log.md` for a prior run on this or an adjacent question — extend it rather than re-pay for research that already exists and is still fresh.

## Step 4 — Write the article

File: `corpus/<pillar>/<topic-slug>.md`, where `<pillar>` is one of `design-patterns`, `ml-techniques`, `adjacent-knowledge` (create a new pillar directory only if a topic genuinely doesn't fit any of the three, and update `TOPICS.md`'s pillar headers to match).

Frontmatter:
```yaml
---
title: <topic>
pillar: design-patterns | ml-techniques | adjacent-knowledge
method: vault-adapt | deep-research | storm | deep-research + storm
date: <YYYY-MM-DD>
sources: <count>
confidence: high | medium | low
vault-links: [wiki/concepts/slug.md, ...]   # omit the key entirely if none
---
```

Body structure — adapt headers to fit the topic, but keep this shape:
- **What it is** — the mechanism in plain terms, no marketing language.
- **When to reach for it** — the concrete signal this is the right tool, and the signal it's the wrong one.
- **How it works** — the actual technical substance. This is the section that has to earn the article's existence.
- **Trade-offs** — what you give up. If the harness was STORM, this is where the contradiction map lives.
- **In practice** — a small worked example, or a pointer to where the pattern shows up in a real, citable system.
- **Further reading** — sources, numbered and linked, exactly as STORM/deep-research produced them. Every non-obvious claim in the body should trace to one of these.

**Cite only from the verified pool.** The article may cite *only* sources that the research stage already resolved and fetched — never introduce a reference at write time that the pipeline has not seen. Fabrication is induced by the instruction to cite, so grounding must be forced structurally, not hoped for. Each cited sentence should be traceable to a specific fetched passage, so the Step 5 gate can check it. See [references/citation-integrity.md](references/citation-integrity.md) for the evidence.

Write for the persona in this skill's description: someone who already codes well and wants the mechanism, not someone who needs the topic explained from zero.

## Step 5 — Citation integrity gate (run before committing)

The corpus is only as trustworthy as its citations; a fabricated or misgrounded reference is worse than no article. Before the article counts as done, audit every citation. The full evidence base and the ranked guard list are in [references/citation-integrity.md](references/citation-integrity.md) — this is the operational checklist. Run cheap deterministic checks first (they can't be gamed), then the model-based ones.

**Deterministic (MUST — no model judgment):**
1. **Resolve every reference.** DOI → `GET https://api.crossref.org/works/{doi}` (expect HTTP 200 + fuzzy-matching title); arXiv id → the arXiv abstract page; otherwise resolve the title via OpenAlex/Semantic Scholar or a direct fetch. Any reference that resolves to nothing — or to a *different* paper than cited — is a phantom: drop or replace it, never ship it.
2. **Quote-span match.** Each cited sentence must be backed by text that actually appears in the fetched source (exact substring for direct quotes; ~0.8 fuzzy for paraphrase). A claim whose support is not in the source is a misquote even if it reads perfectly — resolution alone will not catch this.
3. **URL liveness.** Every citation URL must fetch a live 200; on failure, check the Wayback Machine and repair a stale-but-real link, but block anything with no live and no archived copy.

**Model-based (MUST/SHOULD — catches misgrounding):**
4. **Entailment (MUST).** A verifier that is **not** the writer fetches each cited passage and answers, factored (without the draft in context), "does this source — and only this — support this exact statement?" Fail any sentence its citations do not entail. Do not let the writer grade its own citations.
5. **Contradiction check (SHOULD).** Instruct the verifier to distinguish supports / unrelated / *contradicts*, hard-fail a topically-relevant-but-refuting citation, and give claims hinging on specific numbers or dates a second look — that fine-grained slice is where automated checkers miss most.

**Record the result (SHOULD).** Emit a small audit tally — references resolved/unresolved, sentences entailed/not, URLs live/dead — and carry it into the ledger entry (Step 6). Gate the commit on it: zero unresolved references and zero dead URLs are hard blocks. If a topic cannot clear the gate, cut the unsupported claims rather than shipping them; report what was cut.

When running this loop as a workflow, implement these as pipeline stages: the research stage emits the resolved source pool, the write stage cites only from it, and a distinct verify/audit stage runs checks 1–5 before the writer's file is accepted.

## Step 6 — Update the index and ledger

1. Add or update the article's one-line entry under a `## Corpus` section in `README.md` (create the section on first run if it doesn't exist), mirroring the vault's own "one line per page, summary-first" convention: `- [title](corpus/<pillar>/<slug>.md) — one-line hook`.
2. Append an entry to `corpus/LEDGER.md` using the template already in that file, including the Step 5 citation-audit tally.
3. Check the box for this topic in `TOPICS.md` — keep the row; don't delete history.

## Step 7 — Commit and push

From the repo root, stage and commit only what this run touched, then push to the writable remote:
```bash
git pull --rebase --autostash origin main
git add -- corpus/<pillar>/<slug>.md README.md corpus/LEDGER.md TOPICS.md
git commit -m "corpus: add <topic>" -- corpus/<pillar>/<slug>.md README.md corpus/LEDGER.md TOPICS.md
git push origin main
```
Never `git add -A` or stage files this run didn't touch — this working tree may hold other in-progress changes. Pushing is part of the loop, not an optional extra: the run is not done until the corpus is backed up. Push to `origin` (the canonical `pH34r-pH/knowledge`, now write-accessible); `git pull --rebase --autostash` first since this is now a shared repo with another collaborator. If a push is rejected, report it plainly rather than silently dropping the backup.

## Output

Return to the user, concisely:
- the topic chosen and why (one line),
- the harness used and source count,
- the file path,
- one open question or weak point in the research, if any,
- a reminder that the commit is local only.

Keep chat short — the durable output is the file, not the chat summary.
