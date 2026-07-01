---
title: Citation integrity — how populate-corpus guards against reference hallucination
purpose: Evidence base and guard checklist for the citation-integrity gate in SKILL.md Step 5
date: 2026-07-01
method: deep-research (4 angles) → adversarial verify (every load-bearing paper fetched) → synthesis
sources: 11
confidence: high
---

# Citation integrity

This corpus is only as trustworthy as its citations. A fluent article with a fabricated or misgrounded reference is *worse* than no article — it lends false authority to a wrong claim. This doc records what the evidence says about reference hallucination and the concrete guards the loop runs to defend against it. It is the "why" behind the citation-integrity gate in [SKILL.md](../SKILL.md) Step 5.

The findings below were produced by a research → adversarial-verify → synthesize workflow; the verify pass fetched every load-bearing paper to confirm it exists, is by the claimed authors, and says what is claimed (four overstatements were caught and corrected before this doc was written — a small live demonstration of the problem).

## The problem is real, severe, and prompt-induced

- **Fabrication is common.** Walters & Wilder verified 636 GPT-generated citations across 42 topics against Google Scholar / PubMed / Scopus / WorldCat: **55% of GPT-3.5 and 18% of GPT-4 citations were fabricated**, and of the *genuine* citations, 43% (GPT-3.5) / 24% (GPT-4) still contained substantive errors [2]. A cross-model audit of **69,557 citations** found **11.4–56.8% unverifiable** against CrossRef/OpenAlex/Semantic Scholar depending on model [1].
- **It gets worse in high-stakes domains.** General LLMs hallucinated on **58% (GPT-4) to 88% (Llama-2)** of 800k+ verifiable legal queries [9]. Even purpose-built legal RAG tools marketed as "hallucination-free" still misground **17–33%** of the time on 202 preregistered queries [8].
- **It is induced by the instruction to cite.** The audit's most useful control: when models were *not* prompted to cite, **zero** parseable citations appeared — fabrication is a response to being asked for references, not a background rate [1]. That means grounding must be *forced*, not hoped for.
- **"True" and "grounded" are different axes.** A claim can be factually correct yet cite a source that does not support it (misgrounding). Rigorous evaluation scores both and fails a claim if *either* fails [8]. Correctness-only checks are blind to the most authority-lending failure mode.

## The layered defense

The evidence supports a defense where **cheap, un-gameable deterministic checks run first and carry the most weight**, model-based entailment catches the residual "real source, wrong claim" errors, and process discipline makes both possible. A persuasive generator cannot talk its way past a DOI that does not resolve.

### Layer 1 — Deterministic (no model judgment, cannot be gamed)

1. **Resolve every reference** [MUST]. Mechanically resolve each citation: DOI → `GET https://api.crossref.org/works/{doi}` (require HTTP 200 with a title that fuzzy-matches); arXiv id → arXiv API/abstract; else query OpenAlex/Semantic Scholar by title. No matching record → phantom → drop or replace. This is the single highest-leverage guard; it is exactly the method the primary studies used to measure fabrication [1][2].
2. **Quote-span exact match** [MUST]. Every cited sentence carries the exact span it draws from; string-match that span against the fetched source (normalized whitespace; exact-substring for direct quotes, ~0.8 Jaccard for paraphrase). A span not present in the source is a misquote regardless of plausibility. This catches the "real, resolvable DOI, but the paper never said this" failure that resolution alone cannot [1][3].
3. **URL liveness** [MUST]. Any citation URL gets an HTTP fetch requiring a live 200; on failure, check the Wayback Machine before rejecting (repair stale-but-real links), but no-live-and-no-archive → hallucinated → block. An HTTP+Wayback health check cuts non-resolving URLs from 5–18% to under 1% [4].

### Layer 2 — Model-based (catches misgrounding the deterministic layer can't)

4. **NLI entailment per claim** [MUST]. A verifier subagent fetches each cited passage and answers the AIS test — "According to the source, does this passage (and only this) support this exact statement?" — computing citation recall (sentence fully entailed) and precision (each citation is actually needed) [3][5]. Even ChatGPT/GPT-4 leave ~50% of long-form answers not fully supported by their own citations [3], so this is not optional.
5. **Atomic-fact decomposition** [SHOULD]. Decompose each paragraph into atomic single-fact statements before entailment-checking, and report per-paragraph support % rather than one whole-text pass/fail, so an unsupported claim buried in fluent prose is localized [6].
6. **Distinguish supports / unrelated / contradicts** [SHOULD]. Instruct the verifier to hard-fail a citation that is topically relevant but *contradicts* the claim, and to flag claims hinging on specific numbers/dates for a second look. Even GPT-4-as-judge collapses to 45 F1 on contradictory citations, and ~31% of its errors are insensitivity to fine-grained detail (numbers, dates) — this is exactly where automated checkers miss most [10].

### Layer 3 — Process / architecture (makes the above possible and honest)

7. **Constrain the writer to a verified pool** [MUST]. The research stage emits a numbered pool of pre-resolved sources (id + resolved DOI/URL + fetched passage text); the writer is forced via structured output to cite **only** ids from that pool. A citation id outside the pool is a hard schema-validation failure. This makes fabrication structurally impossible at write time instead of something to catch after [1][3][5].
8. **The verifier is not the writer** [MUST]. Run verification as a separate agent, answering its checks *factored* — without the original draft in context — so it cannot re-affirm the writer's own hallucination. Chain-of-Verification shows factored verification beats joint precisely because attending to the prior generation makes a model repeat its own errors; self-preference bias makes a model grading its own output systematically optimistic [7].

### Layer 4 — Measurement (make integrity a number, not a vibe)

9. **Prefer consensus sources** [NICE]. Prefer references surfaced by more than one independent search; flag single-source load-bearing citations for extra scrutiny. Requiring ≥3 models to cite the same work yields 95.6% accuracy because fabrications are idiosyncratic and rarely survive cross-source agreement [1]. A prior, not a gate — a niche-but-real source may legitimately appear only once.
10. **Report a rate, not a vibe** [SHOULD]. The audit emits a structured report per article — references resolved/unresolved, sentences entailed/not, URLs live/dead — recorded in the ledger on commit, with hard gate thresholds (zero unresolved references, 100% live URLs, entailment recall above a set bar). "The corpus is well-cited" becomes a checkable number [1][9].

## Residual risks (what no guard fully closes)

- **Real-but-irrelevant DOI:** a citation resolves cleanly to a genuine paper that does not support the claim. Layers 1→2 stack against this, but the *composed* false-negative rate of resolution + quote-span + NLI is not measured in any single source.
- **The model layer shares blind spots with the generator.** AttrScore shows the topical-but-contradicting case is exactly where even a strong judge fails — a fraction of misgrounded citations will pass even a separate verifier [10].
- **Threshold tuning is unsolved.** Quote-span similarity and long-PDF passage chunking have no universally-correct threshold; too loose admits paraphrase drift, too tight rejects light editing, and a claim supported on page 30 can be scored unsupported if the wrong chunk is fetched.
- **Calibration drift.** Most primary rates are from 2023-era models; absolute thresholds set from them may be miscalibrated for the actual writer model with native web retrieval.

## Sources

1. Naser — How LLMs Cite and Why It Matters: A Cross-Model Audit of Reference Fabrication (arXiv:2603.03299, 2026) — https://arxiv.org/abs/2603.03299
2. Walters & Wilder — Fabrication and errors in the bibliographic citations generated by ChatGPT (Scientific Reports, 2023; DOI 10.1038/s41598-023-41032-5) — https://www.nature.com/articles/s41598-023-41032-5
3. Gao, Yen, Yu & Chen — Enabling LLMs to Generate Text with Citations (ALCE, EMNLP 2023; arXiv:2305.14627) — https://aclanthology.org/2023.emnlp-main.398/
4. Rao, Wong & Callison-Burch — Detecting and Correcting Reference Hallucinations in Commercial LLMs and Deep Research Agents (arXiv:2604.03173, 2026) — https://arxiv.org/abs/2604.03173
5. Rashkin, Nikolaev, Lamm et al. — Measuring Attribution in Natural Language Generation Models (AIS, Computational Linguistics 2023; arXiv:2112.12870) — https://arxiv.org/abs/2112.12870
6. Min, Krishna, Lyu et al. — FActScore: Fine-grained Atomic Evaluation of Factual Precision (EMNLP 2023; arXiv:2305.14251) — https://aclanthology.org/2023.emnlp-main.741/
7. Dhuliawala, Komeili, Xu et al. — Chain-of-Verification Reduces Hallucination (arXiv:2309.11495; Findings of ACL 2024) — https://arxiv.org/abs/2309.11495
8. Magesh, Surani, Dahl, Suzgun, Manning & Ho — Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools (JELS 2025; arXiv:2405.20362) — https://arxiv.org/abs/2405.20362
9. Dahl, Magesh, Suzgun & Ho — Large Legal Fictions: Profiling Legal Hallucinations in LLMs (Journal of Legal Analysis 2024; arXiv:2401.01301) — https://academic.oup.com/jla/article/16/1/64/7699227
10. Yue et al. — Automatic Evaluation of Attribution by LLMs (AttrScore, Findings of EMNLP 2023; arXiv:2305.06311) — https://arxiv.org/abs/2305.06311
11. Weller et al. — "According to..." Prompting LMs Improves Quoting from Pre-Training Data (QUIP-Score, arXiv:2305.13252) — https://arxiv.org/abs/2305.13252

## Corrections applied during verification

The adversarial verify pass caught and this doc corrected: a Bhattacharyya medical-citation study whose cited medRxiv URL resolved to a *different* paper (dropped in favor of the exactly-verified Walters & Wilder / Naser figures); an overstated URL-nonresolution upper bound and an unconfirmed ExpertQA figure from source [4] (using only its confirmed 3–13% / 5–18% / <1% numbers); an unconfirmed "over 50%" effort-reduction figure (method kept, number dropped); and Dahl's GPT-3.5 mid-value (using the confirmed 58–88% range endpoints instead). No fully fabricated papers were found in the research — but the misattributions are precisely the failure class the guards above exist to catch.
