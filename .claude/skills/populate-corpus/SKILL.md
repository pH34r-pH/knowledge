---
name: populate-corpus
description: Run one iteration of the researcher loop that builds out this repo's knowledge corpus — software engineering design patterns, ML techniques, and other high-value knowledge for an ambitious, curious mid-career software engineer. Selects the highest-value uncovered topic, picks the right-weight research harness (reuse the vault, deep-research, or STORM), writes a sourced article, and updates the index/ledger. Use when asked to "populate the corpus", "grow the knowledge base", "add a topic", "run the research loop", or when this skill is re-invoked to keep building the repo.
---

# Populate Corpus — the researcher loop

You are acting as a researcher systematically building this repo into a corpus of durable, high-value technical knowledge — software engineering design patterns, machine learning techniques, and anything else you have real evidence is worth an ambitious, knowledge-hungry mid-career software engineer's time. Not a link dump, not a survey of whatever is trending this month — each article should be the kind of thing that still holds up in two years.

This skill defines **one atomic iteration** of that loop: pick a topic, research it at the right depth, write it up, update the index, commit. Re-invoke it (by hand, or wrapped in `/loop populate-corpus`) to keep building. Each run is self-contained and checkpointed — killing the loop mid-run never leaves the repo in a broken state, because the commit at the end of a run is the only state change.

Full rationale and requirements: [specs/001-corpus-population-loop/spec.md](../../../specs/001-corpus-population-loop/spec.md).

## Boundaries (read first)

- **This repo is not yours yet.** Access here is read-only pending a pending collaborator invite from the owner. Commit locally at the end of every run (pathspec-scoped, never a broad `git add`) but never push without being explicitly asked — same discipline the vault itself uses for ad-hoc commits.
- **Read from `~/brain`, never write to it.** The vault is a personal, curated knowledge base with its own ownership and gating rules (see `~/brain/CLAUDE.md`). This loop may read vault pages for grounding and cross-link to them, but a corpus article here must never cause a vault write — that direction of flow belongs to the vault's own `/paper` and `/librarian` skills, not to this one.
- **Quality over throughput.** One well-sourced, well-reasoned article beats five thin ones. If a candidate topic turns out to be too shallow, too faddish, or already well covered elsewhere in the corpus, say so in the output and pick the next one rather than force a low-value entry.

## Step 1 — Load state

Read, in order:
1. `TOPICS.md` at the repo root — the prioritized backlog across the three pillars. This is the menu; do not invent topics outside it without adding them here first (see Step 2).
2. `corpus/LEDGER.md` — every prior run: topic, method, sources, confidence, file. Skip anything already done and still fresh; if a done entry looks stale (the *field* moved, e.g. a technique got superseded — not the write itself), note it in the output but still prefer a fresh topic this run.
3. `README.md` — the current article index, so the new entry doesn't duplicate existing structure.
4. `/Users/haidmoham/brain/README.md` — the vault's master catalog. Grep it for the candidate topic's keywords before researching. If a mature, `experience`-tier `wiki/concepts/` or `wiki/entities/` page already covers it, that's a grounding source and possibly enough on its own — see Step 3.

## Step 2 — Select the topic

Pick exactly one unchecked topic from `TOPICS.md`, highest-value first, skipping anything already covered per the ledger. Prioritize topics that:
- recur across multiple independent authoritative sources, not one blog's opinion,
- are foundational rather than tied to one vendor or one framework version,
- either fill a gap in the vault's own stated ML weak spots (`/Users/haidmoham/brain/wiki/concepts/self-study-ml-engineering.md`, `/Users/haidmoham/brain/wiki/concepts/ml-pivot-diagnostic-2026-07-01.md`) or extend the live research cluster already sitting in `arxiv/`/`reports/` (agent harnesses, self-evolving agents, agent evaluation methodology),
- have staying power — prefer the durable mechanism over the fast-moving tool built on top of it.

If a pillar has no unchecked topics left, propose 3-5 new candidates for that pillar (one-line justification each), append them to `TOPICS.md` as new unchecked items, then pick one — keep the backlog self-sustaining rather than stalling the loop.

## Step 3 — Decide the research harness

Not every topic deserves the same weight. Pick one path:

- **Vault-adapt (no fresh research).** The topic is already a mature, `experience`-tier page in `~/brain/wiki/`. Read it, generalize it for this corpus's audience (strip anything personal — project names, individual decisions, company specifics), and cite it as the source. Use this whenever it genuinely applies rather than re-researching something already owned and tested.
- **`deep-research` skill (built in).** The topic has a converged, mostly-agreed technical exposition — an algorithm, a mechanism, an established technique — where the value is breadth and correct sourcing, not adversarial framing. Invoke it with the topic as the research question.
- **`storm` skill** (`/Users/haidmoham/brain/agent-config/skills/storm/SKILL.md`). The topic is genuinely contested — real practitioners disagree, and the disagreement is itself the valuable content (e.g. "when does CQRS earn its complexity", "monolith vs. microservices for a team of N", "RAG vs. long-context vs. fine-tuning for this class of problem"). Follow STORM's own workflow, sized to 3-4 perspectives for a corpus article (lighter than a full briefing) unless the topic clearly needs more. STORM's non-negotiable rule still applies: every claim in the final article must trace to a retrieved source — no answering from memory.

Before either fresh-research path, check `corpus/LEDGER.md` **and** `/Users/haidmoham/brain/wiki/meta/research-log.md` for a prior run on this or a closely adjacent question — extend it instead of re-paying for research that already exists and is still fresh.

## Step 4 — Write the article

File: `corpus/<pillar>/<topic-slug>.md`, where `<pillar>` is one of `design-patterns`, `ml-techniques`, `adjacent-knowledge` (create a new pillar directory only if a topic genuinely doesn't fit any of the three, and update `TOPICS.md`'s pillar headers to match).

Frontmatter:
```yaml
---
title: <topic>
pillar: design-patterns | ml-techniques | adjacent-knowledge
method: vault-adapt | deep-research | storm
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

Write for the persona in this skill's description: someone who already codes well and wants the mechanism, not someone who needs the topic explained from zero.

## Step 5 — Update the index and ledger

1. Add or update the article's one-line entry under a `## Corpus` section in `README.md` (create the section on first run if it doesn't exist), mirroring the vault's own "one line per page, summary-first" convention: `- [title](corpus/<pillar>/<slug>.md) — one-line hook`.
2. Append an entry to `corpus/LEDGER.md` using the template already in that file.
3. Check the box for this topic in `TOPICS.md` — keep the row; don't delete history.

## Step 6 — Commit

From the repo root:
```bash
git add -- corpus/<pillar>/<slug>.md README.md corpus/LEDGER.md TOPICS.md
git commit -m "corpus: add <topic>" -- corpus/<pillar>/<slug>.md README.md corpus/LEDGER.md TOPICS.md
```
Never `git add -A` or stage files this run didn't touch — this working tree may have other in-progress changes. Do not push: push access is pending; remind the user at the end of the run instead.

## Output

Return to the user, concisely:
- the topic chosen and why (one line),
- the harness used and source count,
- the file path,
- one open question or weak point in the research, if any,
- a reminder that the commit is local only.

Keep chat short — the durable output is the file, not the chat summary.
