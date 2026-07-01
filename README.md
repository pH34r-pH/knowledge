Structured research corpus for experiments with graph-based lookup and retrieval, automated research, and RAG pipelines

## Corpus

General-knowledge articles on software engineering design patterns, ML techniques, and adjacent high-value engineering knowledge — separate from the arXiv paper pipeline in `arxiv/`/`reports/`. Backlog: [TOPICS.md](TOPICS.md). Run ledger: [corpus/LEDGER.md](corpus/LEDGER.md). Protocol: [specs/001-corpus-population-loop/spec.md](specs/001-corpus-population-loop/spec.md), runnable as the `populate-corpus` skill.

**Design patterns**
- [Resilience patterns: circuit breaker, retry with jitter, timeout budgets](corpus/design-patterns/resilience-patterns.md) — three patterns that each cut a different link in the cascading-failure feedback loop, and how they compose.
- [CQRS and event sourcing](corpus/design-patterns/cqrs-event-sourcing.md) — event sourcing makes the log the source of truth; CQRS splits read from write; both are minority-case, bounded-context tools.

**ML techniques**
- [Backpropagation and automatic differentiation](corpus/ml-techniques/backpropagation-autodiff.md) — AD is a third technique, not symbolic and not numeric; backprop is just reverse mode on a scalar loss.

**Adjacent knowledge**
- [Graceful degradation: ranked fallback chains](corpus/adjacent-knowledge/graceful-degradation.md) — order methods best-to-worst, return on first success, own the last rung locally, never hard-fail.

<!-- one line per article, added by populate-corpus as the corpus grows -->

