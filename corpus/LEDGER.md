# Corpus Research Ledger

Ledger of every `populate-corpus` run — one entry per topic written to `corpus/`. Mirrors the discipline of the vault's own `research-log.md`: consult this **before** researching a topic. If it's covered and still fresh, skip it or scope a new run to the delta; if stale, say so and re-run rather than trust it silently.

Status legend: **current** (trustworthy as-is) · **stale** (the field may have moved, re-check before reuse) · **superseded by …** (a later entry replaced it) · **extended by …** (a later entry built on it).

---

## Entries

<!-- newest first. Template per run:

### YYYY-MM-DD — <topic>
- **Status:** current
- **Pillar:** design-patterns | ml-techniques | adjacent-knowledge
- **Method:** vault-adapt | deep-research | storm | deep-research + storm
- **Sources:** <count> · **Confidence:** high | medium | low
- **File:** [corpus/<pillar>/<slug>.md](<pillar>/<slug>.md)
- **Citation audit:** <refs resolved>/<total> resolved · <urls live>/<total> URLs live · entailment <pass note> (Step 5 gate)
- **Vault cross-links:** <links, or "none">
- **Builds on / supersedes:** — (or link to the prior entry)

-->

### 2026-07-01 — Evaluating agents and models rigorously (baselines, significance, honest reporting)
- **Status:** current
- **Pillar:** ml-techniques
- **Method:** vault-adapt (generalized from `~/brain/wiki/concepts/agent-evaluation-methodology.md`; extended with public reproducibility/leakage literature + this repo's local Claw-Eval / Terminal-Bench / OneMillion-Bench papers)
- **Sources:** 13 · **Confidence:** high
- **File:** [corpus/ml-techniques/agent-evaluation-methodology.md](ml-techniques/agent-evaluation-methodology.md)
- **Vault cross-links:** wiki/concepts/agent-evaluation-methodology.md (internal provenance)
- **Builds on / supersedes:** —
- **Open question:** no source gives a cost/benefit rule for how much eval rigor a decision justifies — when a cheap single-outcome check beats expensive trajectory-aware Pass^k grading with a human-calibrated judge is left to the reader.

### 2026-07-01 — System design fundamentals: load balancing, caching, sharding, consistent hashing
- **Status:** current
- **Pillar:** adjacent-knowledge
- **Method:** deep-research
- **Sources:** 15 · **Confidence:** high (one figure — Facebook memcache 17k→1.3k qps — softened to medium; NSDI PDF 403'd, sourced via secondary summaries)
- **File:** [corpus/adjacent-knowledge/system-design-fundamentals.md](adjacent-knowledge/system-design-fundamentals.md)
- **Vault cross-links:** none
- **Builds on / supersedes:** —
- **Open question:** rebalancing/data-streaming mechanics under consistent-hashing ring membership change (Dynamo/Cassandra operational cost) were not deep-dived and warrant a dedicated source.

### 2026-07-01 — RAG retrieval architectures: vector, graph, and hybrid
- **Status:** current
- **Pillar:** ml-techniques
- **Method:** storm (3 perspectives: dense-vector proponent / GraphRAG proponent / hybrid-retrieval-quality pragmatist)
- **Sources:** 20 · **Confidence:** medium (genuinely contested; each camp's results hold only on the slice it measured)
- **File:** [corpus/ml-techniques/rag-retrieval-architectures.md](ml-techniques/rag-retrieval-architectures.md)
- **Vault cross-links:** none
- **Builds on / supersedes:** —
- **Open question:** no cited result runs dense-hybrid+rerank, GraphRAG/LazyGraphRAG, and long-context+router on one held-out mixed workload, nor prices total cost of ownership (index freshness, re-embedding, permission filtering) on a live, mutating, permissioned corpus.

### 2026-07-01 — Attention and the Transformer architecture, internals
- **Status:** current
- **Pillar:** ml-techniques
- **Method:** deep-research
- **Sources:** 12 · **Confidence:** high
- **File:** [corpus/ml-techniques/attention-transformers.md](ml-techniques/attention-transformers.md)
- **Vault cross-links:** none
- **Builds on / supersedes:** —
- **Open question:** whether induction heads remain the dominant in-context-learning mechanism at frontier scale (causal only for small attention-only models), and how well the √d_k unit-variance assumption survives real trained weights.

### 2026-07-01 — Idempotency keys and exactly-once-effect APIs
- **Status:** current
- **Pillar:** design-patterns
- **Method:** deep-research
- **Sources:** 9 · **Confidence:** high
- **File:** [corpus/design-patterns/idempotency-keys.md](design-patterns/idempotency-keys.md)
- **Vault cross-links:** none
- **Builds on / supersedes:** — (tight cluster with saga-pattern and resilience-patterns)
- **Open question:** when mutations need fencing tokens on top of idempotency keys, and what the key should be derived from (client UUID vs content hash) to survive a client's own retries.

### 2026-07-01 — The Saga pattern for distributed transactions
- **Status:** current
- **Pillar:** design-patterns
- **Method:** deep-research
- **Sources:** 13 · **Confidence:** high
- **File:** [corpus/design-patterns/saga-pattern.md](design-patterns/saga-pattern.md)
- **Vault cross-links:** none
- **Builds on / supersedes:** — (relates to idempotency-keys and resilience-patterns)
- **Open question:** where the boundary sits between saga-level business recovery and the underlying durable-execution layer for technical failures, and how durable engines like Temporal blur it.

### 2026-07-01 — Backpropagation and automatic differentiation
- **Status:** current
- **Pillar:** ml-techniques
- **Method:** deep-research
- **Sources:** 8 · **Confidence:** high
- **File:** [corpus/ml-techniques/backpropagation-autodiff.md](ml-techniques/backpropagation-autodiff.md)
- **Vault cross-links:** none
- **Builds on / supersedes:** —
- **Open question:** reverse-mode accumulation order under fp16/bf16 mixed precision — no retrieved source covers the numerical-stability interaction (vanishing/exploding gradients are a property of the composed Jacobian, not the AD algorithm).

### 2026-07-01 — CQRS and event sourcing
- **Status:** current
- **Pillar:** design-patterns
- **Method:** storm (3 perspectives: proponent / pragmatist-skeptic / production operator)
- **Sources:** 12 · **Confidence:** high
- **File:** [corpus/design-patterns/cqrs-event-sourcing.md](design-patterns/cqrs-event-sourcing.md)
- **Vault cross-links:** none
- **Builds on / supersedes:** —
- **Open question:** no source gives a quantitative break-even (event volume, retention horizon, regulatory class, team size) for event sourcing over CRUD-plus-audit-table, nor costs it against temporal tables / CDC as the middle option.

### 2026-07-01 — Resilience patterns: circuit breaker, retry with jitter, timeout budgets
- **Status:** current
- **Pillar:** design-patterns
- **Method:** deep-research
- **Sources:** 11 · **Confidence:** high
- **File:** [corpus/design-patterns/resilience-patterns.md](design-patterns/resilience-patterns.md)
- **Vault cross-links:** none
- **Builds on / supersedes:** —
- **Open question:** the authoritative composition order (timeout/bulkhead/breaker/budgeted-retry) and whether it should differ for control-plane vs data-plane calls is settled by no single source; no published percentile-style derivation exists for breaker thresholds comparable to AWS's timeout rule.

### 2026-07-01 — Graceful degradation: ranked fallback chains
- **Status:** current
- **Pillar:** adjacent-knowledge
- **Method:** vault-adapt (generalized from `~/brain/wiki/concepts/graceful-degradation.md`, corroborated with public sources)
- **Sources:** 6 · **Confidence:** high
- **File:** [corpus/adjacent-knowledge/graceful-degradation.md](adjacent-knowledge/graceful-degradation.md)
- **Vault cross-links:** wiki/concepts/graceful-degradation.md (internal provenance)
- **Builds on / supersedes:** —
- **Open question:** when a visible hard-fail is preferable to a silently-degraded answer — for money movement, safety, or auto-consumed output, a plausible-but-wrong last rung is more dangerous than an error, making "never hard-fail" an anti-pattern.
