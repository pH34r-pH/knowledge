# Citation audit — 2026-07-01

Retroactive run of the [citation-integrity gate](../.claude/skills/populate-corpus/references/citation-integrity.md) against the entire corpus (all 10 articles) after the gate was codified. Method: one independent auditor per article (not the writer) resolved every reference — WebFetch the URL, resolve the arXiv id / DOI, confirm title + authors + venue — and checked that the source actually supports the claims keyed to it; every flagged citation then went through a **second independent re-check** before being treated as a real problem.

## Headline

- **119 citations audited across 10 articles. Zero fabricated sources.** Every source resolves to a real work that exists.
- **6 confirmed problems**, all fixed — each was an *over-citation* or *misattribution* (a real source cited for a claim it doesn't make, or the wrong venue/model attached to a real figure), never an invented reference.
- **5 false alarms** correctly dismissed by the independent re-check (a source flagged by the first auditor that the second confirmed was fine).

That the failures are all over-citation/misattribution rather than fabrication is the expected signature of a pipeline that already fetched its sources at write time; the gate's value here is catching the residual "real source, slightly wrong claim" class.

## Confirmed problems fixed

| Article | Source | Problem | Fix |
|---|---|---|---|
| resilience-patterns | [4] Hystrix "How it Works" | Default numbers (20 req/10s, >50%) are on the Configuration wiki, not this page | Added [12] Hystrix Configuration wiki; cited it for the defaults |
| idempotency-keys | [6] Confluent/Kafka | Over-cited on key-length/UUID and on the SQS/EventBridge/webhook claim — neither is in a Kafka-internal article | Dropped [6] from both; kept [4] (Stripe) and [9] (webhook guide) which do support them |
| attention-transformers | [6] KV-cache page | Supports linear growth, but not the "batch size" or "overtakes model weights" specifics | Reworded to only what [6] supports (linear in sequence length, layers, heads) |
| attention-transformers | [8] GQA/ZeroEntropy | The 64/8-head, 8× figure is attributed by the source to Llama **3** 70B, not Llama 2 | Re-attributed to Llama 3 70B; noted Llama 2 as the first GQA adopter |
| system-design-fundamentals | [10] DDIA notes repo | The random-prefix hot-key mitigation is from the DDIA **book**, not the notes repo | Added [16] (the book) and re-attributed the mitigation; kept [10] for the celebrity-problem framing |
| agent-evaluation-methodology | [7][8] | The "held-out test sets / data-provenance / rotating benchmarks" defenses appear in neither cited source | Reworded to what [7] and [8] actually propose (transparency, uniform testing, diverse signals, gaming-resistant graders) |

## False alarms dismissed by the re-check (no change to the claim)

- **resilience-patterns [10]** (grpc.io deadlines): the page *does* support the deadline→timeout-minus-elapsed and shrinking-downstream-budget claims. Left as-is.
- **system-design-fundamentals [6]** (memcache NSDI PDF): real paper; the direct PDF 403s automated fetchers but resolves in browsers, and the qps figure is already flagged medium-confidence. Swapped the URL to the canonical USENIX landing page so it won't trip the URL-liveness guard.
- **agent-evaluation-methodology [2]** (Kapoor & Narayanan): resolves correctly; no issue.
- **saga-pattern [3]** (Garcia-Molina & Salem 1987): ACM returns 403 to bots, but DOI 10.1145/38714.38742 resolves to the real "Sagas" paper with correct authors/venue/year. Left as-is (canonical DOI). Note: this bot-block is why the URL-liveness guard must treat a 403-with-valid-DOI as live-via-resolution, not dead.
- **saga-pattern [13]** (Temporal blog): live and on-topic; tightened the cited title to the article's real title as a pure accuracy improvement.

## Per-article result

| Article | Citations | Confirmed problems | Status |
|---|---|---|---|
| graceful-degradation | 6 | 0 | clean |
| resilience-patterns | 12 | 1 | fixed |
| cqrs-event-sourcing | 12 | 0 | clean |
| backpropagation-autodiff | 8 | 0 | clean |
| saga-pattern | 13 | 0 | clean (2 false alarms; 1 title polish) |
| idempotency-keys | 9 | 1 | fixed |
| attention-transformers | 12 | 2 | fixed |
| rag-retrieval-architectures | 20 | 0 | clean |
| system-design-fundamentals | 16 | 1 | fixed |
| agent-evaluation-methodology | 13 | 1 | fixed |
| **total** | **119** | **6** | **all resolved** |

## Residual notes

- The audit checked existence + attribution + support of the *load-bearing* claims per source, not every sentence. It did not re-derive numeric figures the original writing already flagged as medium-confidence (the memcache 17k→1.3k qps, the saga 1987-wording) — those remain honestly caveated in the articles.
- Two robustness lessons fed back into practice: (1) a `403` from a canonical DOI/paper host (ACM, USENIX) is bot-blocking, not a dead link — the liveness guard must resolve via DOI/search before calling a citation dead; (2) prefer a source's canonical landing page over a direct PDF that automated fetchers can't reach.
