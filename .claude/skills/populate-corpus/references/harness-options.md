---
title: Harness & skill options — evaluation of skillsmp.com against the populate-corpus flow
date: 2026-07-01
method: scouted skillsmp.com (6 capability areas, grounded in real marketplace results) → skeptical evaluation against existing stages
---

# Harness & skill options

A review of the [skillsmp.com](https://skillsmp.com/) agent-skills marketplace (2M+ open-source skills) for research harnesses and pipeline skills worth adding to this flow. The bar: *adds a capability the flow genuinely lacks, or does an existing stage measurably better.* Most candidates failed it — the marketplace is full of reimplementations of deep-research, STORM, fact-checking, and citation-audit that this pipeline already does more rigorously, and crucially without our verified-source-pool constraint or a separate deterministic gate. The value is in a few genuine gaps.

**Governing caveat.** Importing an unvetted third-party skill into a pipeline whose entire value is verifiable trust injects exactly the unaudited dependency the flow exists to guard against. A skill that reshapes search results, summarizes a source before you cite it, or fabricates a plausible reference is a supply-chain vector aimed straight at the gate. So: **prefer adapting the idea over taking the dependency**, especially for anything touching the source pool or the verifier. Marketplace presence is not vetting (heavy fork duplication; repo-level star counts that aren't skill-level quality signals; many anonymous solo repos).

## Adopted (codified into the protocol)

1. **Cross-model-family verification** *(citation gate — the top pick).* The gate's entailment/contradiction verifier is "not the writer" but still the same base model, so it shares systematic blind spots. This is the flow's biggest real gap and is self-named in [citation-integrity.md](citation-integrity.md) residual risk #2 and [EVAL-corpus-leverage](../../../corpus/EVAL-corpus-leverage-2026-07-01.md) threats #1/#2, and it matches the standing method-diversity rule (catch systematic LLM errors with a *different model/method/oracle*, not same-model skepticism). Fix: when a second model family is available (e.g. Codex/GPT), run the Step-5 entailment check with it too and hard-fail only on cross-family agreement, surfacing disagreements. A config/wiring change, not a dependency. *(Idea adapted from a cross-model adversarial-review skill; the technique, not the skill.)*
2. **Evidence tiering** *(Step 2 / citation gate).* Rank sources by authority — peer-reviewed > official standard/docs > vendor blog > forum post — so the "recurs across multiple independent authoritative sources" bar is checkable, not asserted. *(Adapted from ngpestelos/skills evidence tiers + jamditis journalism source-credibility.)*
3. **Anti-circular verification** *(citation gate).* Explicitly guard against the verifier fetching a page that merely echoes the claim (an SEO mirror, or a source quoting the model's own output) and counting it as support. *(Adapted from ngpestelos/skills "prevents circular verification via WebFetch".)*

## Recommended, deferred to your call (external services — egress/key/cost)

These add real capability but route data through third parties, so they're your decision, not something to silently wire into a provenance-focused flow:

4. **Academic-DB retrieval at research time** — Semantic Scholar / bioRxiv / PubMed as *retrieval* sources (not just the gate's CrossRef/arXiv/OpenAlex *resolution*), to surface peer-reviewed primaries the web fan-out misses. Value concentrated in the ML-techniques pillar. You already have `~/brain/bin/openalex`; adding Semantic Scholar via a vetted MCP would extend it. *(K-Dense-AI/scientific-agent-skills literature-review.)*
5. **arXiv citation-graph following** — traverse a paper's reference graph to find the next primary source and corroborate a claim across independent works (serves the consensus-source guard). *(blazickjp/arxiv-mcp-server — via a vetted arXiv path, not by pinning a community MCP.)*
6. **Neural/semantic search (Exa)** — complements keyword WebSearch for finding recent, conceptually-related primaries; directly serves the recency-first selection bias where keyword search is weakest on newly-coined terms. One vetted provider (official Exa MCP), invoked deterministically — not a multi-provider router. *(Multi-provider routers like web-search-plus/9router were rated skip-risky: opaque backend selection can return SEO-gamed results upstream of the gate.)*
7. **JS-capable fallback fetcher (Firecrawl)** — for the bot-blocked/403 sources the [retroactive audit](../../../corpus/CITATION-AUDIT-2026-07-01.md) hit (ACM, USENIX PDFs) that tripped URL-liveness as false-dead. Use narrowly as a fallback when WebFetch fails, for liveness/retrieval only; never let its extracted text be the sole basis for a quote-span match without the deterministic check re-confirming. Hosted service — egress + key + cost.

## Considered and skipped (redundant with existing stages)

- **deep-research variants** (deer-flow, ruflo, 13-agent academic, NotebookLM, instructor-workflow) and **standalone/Co-STORM** — reimplementations of harnesses already in Step 3, none with a verified-pool constraint or a downstream gate; several add heavy external deps for zero integrity gain. Co-STORM's human-in-the-loop turn is at odds with the autonomous loop design.
- **citation-audit / reference-checking / fact-check / hallucination-guard / hallucination-risk-reviewer** — all a subset of the Step-5 gate, which already does factored zero-context entailment, atomic decomposition, supports/unrelated/contradicts, and deterministic DOI/arXiv/URL resolution, grounded in the primary literature (ALCE, AIS, FActScore, AttrScore). Several are vibe-scorers, which guard 10 ("report a rate, not a vibe") explicitly rejects.
- **whole competing research pipelines** (Auto-claude-in-sleep, vexjoy 5-phase) — the corpus already *is* a gated, spec'd, evaluated pipeline; adopting one means replacing a mature flow with an unvetted one.
- **PDF/doc-extraction skills** (openai/skills pdf, LandingAI ADE) — the first-party anthropic pdf skill already covers reading source papers; no reason to add a third-party (some egress) reader to a trust-critical flow.
- **prose editors / technical-writing rubrics** — the write stage already has a fixed house structure, a defined persona, and the user's global writing-style rules; generic editors blur that voice rather than sharpen it.
- **code-review adversarial-reviewers, strategy red-team, eval-framework skills** — aimed at code diffs / strategy docs / generic eval; the corpus's adversarial need is over claims and citations (covered by the gate) and it already authored its own agent-evaluation methodology and ran a pre-registered eval. The one transferable technique (hostile-persona diversity) is better realized as the cross-vendor check above.

## One genuine non-integrity gap noted

- **Figure/diagram generation** — the article template is text-only; a How-it-works section (attention, a saga flow) would land better with a diagram, and an SVG path is available. Low priority and orthogonal to the integrity mission; an auto-generated diagram is itself an unverified visual the citation gate does not check, so keep any figure clearly derived from cited text and out of the verification path.
