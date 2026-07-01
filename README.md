Structured research corpus for experiments with graph-based lookup and retrieval, automated research, and RAG pipelines

## Corpus

General-knowledge articles on software engineering design patterns, ML techniques, and adjacent high-value engineering knowledge — separate from the arXiv paper pipeline in `arxiv/`/`reports/`. Backlog: [TOPICS.md](TOPICS.md). Run ledger: [corpus/LEDGER.md](corpus/LEDGER.md). Protocol: [specs/001-corpus-population-loop/spec.md](specs/001-corpus-population-loop/spec.md), runnable as the `populate-corpus` skill.

**Design patterns**
- [Resilience patterns: circuit breaker, retry with jitter, timeout budgets](corpus/design-patterns/resilience-patterns.md) — three patterns that each cut a different link in the cascading-failure feedback loop, and how they compose.
- [The Saga pattern for distributed transactions](corpus/design-patterns/saga-pattern.md) — trade a distributed ACID transaction for local commits plus hand-written compensations, giving up Isolation.
- [Idempotency keys and exactly-once-effect APIs](corpus/design-patterns/idempotency-keys.md) — exactly-once delivery is impossible; at-least-once plus an idempotent receiver buys exactly-once effect.
- [CQRS and event sourcing](corpus/design-patterns/cqrs-event-sourcing.md) — event sourcing makes the log the source of truth; CQRS splits read from write; both are minority-case, bounded-context tools.

**ML techniques**
- [Attention and the Transformer architecture, internals](corpus/ml-techniques/attention-transformers.md) — scaled dot-product attention as content-addressed averaging, why √d_k, and the n² cost behind FlashAttention, GQA, and RoPE.
- [Backpropagation and automatic differentiation](corpus/ml-techniques/backpropagation-autodiff.md) — AD is a third technique, not symbolic and not numeric; backprop is just reverse mode on a scalar loss.
- [RAG retrieval architectures: vector, graph, and hybrid](corpus/ml-techniques/rag-retrieval-architectures.md) — retrieval splits into semantic matching and scale; graph and hybrid are what you add when the dense core provably runs out of mechanism.
- [Evaluating agents and models rigorously](corpus/ml-techniques/agent-evaluation-methodology.md) — the five-part discipline for not fooling yourself in evaluation, extended to agent-era trajectory grading and Pass^k reliability floors.

**Adjacent knowledge**
- [Graceful degradation: ranked fallback chains](corpus/adjacent-knowledge/graceful-degradation.md) — order methods best-to-worst, return on first success, own the last rung locally, never hard-fail.
- [System design fundamentals: load balancing, caching, sharding, consistent hashing](corpus/adjacent-knowledge/system-design-fundamentals.md) — four scaling primitives that are one stack, all fighting naive hash-mod-N remapping under topology change.

<!-- one line per article, added by populate-corpus as the corpus grows -->

