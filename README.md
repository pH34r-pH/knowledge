Structured research corpus for experiments with graph-based lookup and retrieval, automated research, and RAG pipelines

**Continue building:** [BUILDING.md](BUILDING.md) — how to run the loop, the four research harnesses, and where all state lives.

## Citation integrity: how the corpus avoids hallucinated references

Every citation in this corpus passes a gate before it is committed, because a fabricated or misgrounded reference is worse than no article. Deterministic, un-gameable checks run first; model-based checks catch the rest. Full evidence base and guard list: [citation-integrity.md](.claude/skills/populate-corpus/references/citation-integrity.md).

- **Resolve every reference** *(deterministic)* — each DOI / arXiv id / URL is mechanically resolved (CrossRef, arXiv, OpenAlex); anything resolving to nothing, or to a *different* work than cited, is dropped. Fabrication is prompt-induced, so this is the highest-leverage guard.
- **Quote-span match** *(deterministic)* — the supporting text must actually appear in the fetched source; a plausible claim absent from the source is a misquote, however well it reads.
- **URL liveness** *(deterministic)* — every link must resolve live (or via the Wayback Machine); a `403` from a canonical host such as ACM or USENIX is treated as bot-blocking and re-checked via DOI, never called dead.
- **Entailment by a separate verifier** *(model-based)* — a checker that is **not** the writer, answering factored (without the draft in context), confirms each source genuinely supports its claim; this catches the "real source, wrong claim" misgrounding the deterministic layer can't.
- **Writer constrained to a verified pool** *(process)* — the writer may cite only sources the pipeline has already resolved, so fabrication is structurally impossible at write time rather than something to catch afterward.

First full audit (119 citations across all 10 articles, 2026-07-01): **zero fabricated sources**; 6 over-citation / misattribution issues found and fixed. Report: [corpus/CITATION-AUDIT-2026-07-01.md](corpus/CITATION-AUDIT-2026-07-01.md).

## Corpus

General-knowledge articles on software engineering design patterns, ML techniques, and adjacent high-value engineering knowledge — separate from the arXiv paper pipeline in `arxiv/`/`reports/`. Backlog: [TOPICS.md](TOPICS.md). Run ledger: [corpus/LEDGER.md](corpus/LEDGER.md). Protocol: [specs/001-corpus-population-loop/spec.md](specs/001-corpus-population-loop/spec.md), runnable as the `populate-corpus` skill.

**Design patterns**
- [Resilience patterns: circuit breaker, retry with jitter, timeout budgets](corpus/design-patterns/resilience-patterns.md) — three patterns that each cut a different link in the cascading-failure feedback loop, and how they compose.
- [Durable execution engines (Temporal, Restate, DBOS)](corpus/design-patterns/durable-execution-engines.md) — your program's execution state becomes a durable, crash-recoverable artifact; the log-plus-replay layer that absorbs the technical failures a saga can't.
- [The Saga pattern for distributed transactions](corpus/design-patterns/saga-pattern.md) — trade a distributed ACID transaction for local commits plus hand-written compensations, giving up Isolation.
- [Idempotency keys and exactly-once-effect APIs](corpus/design-patterns/idempotency-keys.md) — exactly-once delivery is impossible; at-least-once plus an idempotent receiver buys exactly-once effect.
- [CQRS and event sourcing](corpus/design-patterns/cqrs-event-sourcing.md) — event sourcing makes the log the source of truth; CQRS splits read from write; both are minority-case, bounded-context tools.

**ML techniques**
- [Attention and the Transformer architecture, internals](corpus/ml-techniques/attention-transformers.md) — scaled dot-product attention as content-addressed averaging, why √d_k, and the n² cost behind FlashAttention, GQA, and RoPE.
- [LLM inference optimization: continuous batching, paged KV-cache, speculative decoding](corpus/ml-techniques/llm-inference-optimization.md) — decode is memory-bandwidth-bound; two techniques recover the waste, the third trades compute for latency with a sharp failure mode.
- [Backpropagation and automatic differentiation](corpus/ml-techniques/backpropagation-autodiff.md) — AD is a third technique, not symbolic and not numeric; backprop is just reverse mode on a scalar loss.
- [RAG retrieval architectures: vector, graph, and hybrid](corpus/ml-techniques/rag-retrieval-architectures.md) — retrieval splits into semantic matching and scale; graph and hybrid are what you add when the dense core provably runs out of mechanism.
- [Preference optimization: RLHF vs DPO vs GRPO](corpus/ml-techniques/preference-optimization.md) — one axis: how much RL machinery you keep; route on the reward signal and data you actually have, not on which paper is newest.
- [Reasoning / test-time-compute models](corpus/ml-techniques/reasoning-models.md) — inference-time reasoning is a real, separate scaling axis, but the gains concentrate in verifiable domains and more thinking is not monotonically better.
- [Evaluating agents and models rigorously](corpus/ml-techniques/agent-evaluation-methodology.md) — the five-part discipline for not fooling yourself in evaluation, extended to agent-era trajectory grading and Pass^k reliability floors.

**Adjacent knowledge**
- [Graceful degradation: ranked fallback chains](corpus/adjacent-knowledge/graceful-degradation.md) — order methods best-to-worst, return on first success, own the last rung locally, never hard-fail.
- [Model Context Protocol (MCP): the agent–tool integration standard](corpus/adjacent-knowledge/model-context-protocol.md) — tool schema and execution move behind a runtime-discoverable wire protocol; N×M collapses to M+N, and every strength is the flip side of a documented attack.
- [Prompt injection and the lethal trifecta](corpus/adjacent-knowledge/prompt-injection-lethal-trifecta.md) — private data + untrusted content + an egress channel is exploitable in plain English; the only sound fix is deterministic enforcement in the runtime.
- [System design fundamentals: load balancing, caching, sharding, consistent hashing](corpus/adjacent-knowledge/system-design-fundamentals.md) — four scaling primitives that are one stack, all fighting naive hash-mod-N remapping under topology change.

<!-- one line per article, added by populate-corpus as the corpus grows -->

