# Corpus Research Ledger

Ledger of every `populate-corpus` run — one entry per topic written to `corpus/`. Mirrors the discipline of the vault's own `research-log.md`: consult this **before** researching a topic. If it's covered and still fresh, skip it or scope a new run to the delta; if stale, say so and re-run rather than trust it silently.

Status legend: **current** (trustworthy as-is) · **stale** (the field may have moved, re-check before reuse) · **superseded by …** (a later entry replaced it) · **extended by …** (a later entry built on it).

---

## Citation integrity

All 119 citations across the 10 articles below were audited on 2026-07-01 against the [citation-integrity gate](../.claude/skills/populate-corpus/references/citation-integrity.md) — independent per-article auditors resolved every reference (URL / arXiv id / DOI) and verified claim support, with a second independent re-check on every flag. **Zero fabricated sources; 6 over-citation/misattribution problems found and fixed, 5 false alarms dismissed.** Full report: [CITATION-AUDIT-2026-07-01.md](CITATION-AUDIT-2026-07-01.md).

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

### 2026-09-02 — Logarithmic and closed numerical representations for neural arithmetic
- **Status:** current
- **Pillar:** ml-techniques
- **Method:** deep-research
- **Sources:** 4 · **Confidence:** medium
- **File:** [corpus/ml-techniques/logarithmic-closed-numerical-representations.md](ml-techniques/logarithmic-closed-numerical-representations.md)
- **Citation audit:** 4/4 resolved · 4/4 URLs live or canonically resolved · full-text/primary-abstract claim spans independently re-checked; one CurveFP v2 internal percentage inconsistency bounded to its raw table values ([audit](CITATION-AUDIT-2026-09-02.md))
- **Vault cross-links:** none (public literature synthesis only)
- **Builds on / supersedes:** —
- **Open question:** whether closed-product savings survive memory, interconnect, scale transport, conversion, and realistic utilization in an independently reproduced accelerator.

### 2026-08-07 — Actor model versus CSP channels
- **Status:** current
- **Pillar:** design-patterns
- **Method:** storm
- **Sources:** 4 · **Confidence:** medium
- **File:** [corpus/design-patterns/actor-model-vs-csp.md](design-patterns/actor-model-vs-csp.md)
- **Citation audit:** 4/4 resolved · 4/4 URLs live · source pool independently retrieved with quote spans; recommendations limited to ownership, topology, and failure-model trade-offs
- **Vault cross-links:** none (protocol path unavailable on this host)
- **Builds on / supersedes:** —

### 2026-08-07 — Structured concurrency
- **Status:** current
- **Pillar:** design-patterns
- **Method:** deep-research + storm
- **Sources:** 5 · **Confidence:** high
- **File:** [corpus/design-patterns/structured-concurrency.md](design-patterns/structured-concurrency.md)
- **Citation audit:** 5/5 resolved · 5/5 URLs live · source pool independently retrieved with quote spans; Java version claims pinned to cited JEPs
- **Vault cross-links:** none (protocol path unavailable on this host)
- **Builds on / supersedes:** —

### 2026-08-07 — OpenTelemetry interoperability
- **Status:** current
- **Pillar:** adjacent-knowledge
- **Method:** deep-research
- **Sources:** 6 · **Confidence:** high
- **File:** [corpus/adjacent-knowledge/opentelemetry-interoperability.md](adjacent-knowledge/opentelemetry-interoperability.md)
- **Citation audit:** 6/6 resolved · 6/6 URLs live · source pool independently retrieved with quote spans; backend and storage claims deliberately excluded
- **Vault cross-links:** none (protocol path unavailable on this host)
- **Builds on / supersedes:** —

### 2026-08-07 — Software supply-chain security
- **Status:** current
- **Pillar:** adjacent-knowledge
- **Method:** deep-research
- **Sources:** 6 · **Confidence:** high
- **File:** [corpus/adjacent-knowledge/software-supply-chain-security.md](adjacent-knowledge/software-supply-chain-security.md)
- **Citation audit:** 6/6 resolved · 6/6 URLs live · source pool independently retrieved with quote spans; inventory, provenance, and enforcement claims kept separate
- **Vault cross-links:** none (protocol path unavailable on this host)
- **Builds on / supersedes:** —

### 2026-08-07 — Fine-tuning strategies
- **Status:** current
- **Pillar:** ml-techniques
- **Method:** deep-research + storm
- **Sources:** 6 · **Confidence:** high
- **File:** [corpus/ml-techniques/fine-tuning-strategies.md](ml-techniques/fine-tuning-strategies.md)
- **Citation audit:** 6/6 resolved · 6/6 URLs live · source pool independently retrieved with quote spans; reported quality gains scoped to their evaluated setups
- **Vault cross-links:** none (protocol path unavailable on this host)
- **Builds on / supersedes:** extends preference-optimization with parameter-surface and data-signal selection

### 2026-08-07 — Self-evolving agent systems
- **Status:** current
- **Pillar:** ml-techniques
- **Method:** vault-adapt + deep-research
- **Sources:** 5 · **Confidence:** medium
- **File:** [corpus/ml-techniques/self-evolving-agent-systems.md](ml-techniques/self-evolving-agent-systems.md)
- **Citation audit:** 5/5 resolved · 5/5 URLs live · source pool independently retrieved with quote spans; preprint results marked benchmark-specific
- **Vault cross-links:** none (protocol path unavailable on this host)
- **Builds on / supersedes:** —

### 2026-08-07 — Agent memory architectures
- **Status:** current
- **Pillar:** ml-techniques
- **Method:** deep-research + storm
- **Sources:** 6 · **Confidence:** medium
- **File:** [corpus/ml-techniques/agent-memory-architectures.md](ml-techniques/agent-memory-architectures.md)
- **Citation audit:** 6/6 resolved · 6/6 URLs live · source pool independently retrieved with quote spans; “memory” mechanisms kept as distinct architectural categories
- **Vault cross-links:** none (protocol path unavailable on this host)
- **Builds on / supersedes:** —

### 2026-08-07 — State-space models and linear attention
- **Status:** current
- **Pillar:** ml-techniques
- **Method:** deep-research + storm
- **Sources:** 7 · **Confidence:** medium
- **File:** [corpus/ml-techniques/state-space-models-linear-attention.md](ml-techniques/state-space-models-linear-attention.md)
- **Citation audit:** 7/7 resolved · 7/7 URLs live · source pool independently retrieved with quote spans; architecture categories and benchmark claims kept qualified
- **Vault cross-links:** none (protocol path unavailable on this host)
- **Builds on / supersedes:** extends attention-transformers with long-sequence alternatives

### 2026-08-07 — Mixture-of-Experts routing
- **Status:** current
- **Pillar:** ml-techniques
- **Method:** deep-research
- **Sources:** 6 · **Confidence:** high
- **File:** [corpus/ml-techniques/mixture-of-experts-routing.md](ml-techniques/mixture-of-experts-routing.md)
- **Citation audit:** 6/6 resolved · 6/6 URLs live · source pool independently retrieved with quote spans; total parameters, active computation, and serving cost distinguished
- **Vault cross-links:** none (protocol path unavailable on this host)
- **Builds on / supersedes:** —

### 2026-08-07 — Structured outputs and constrained decoding
- **Status:** current
- **Pillar:** ml-techniques
- **Method:** deep-research
- **Sources:** 3 · **Confidence:** high
- **File:** [corpus/ml-techniques/structured-outputs-constrained-decoding.md](ml-techniques/structured-outputs-constrained-decoding.md)
- **Citation audit:** 3/3 resolved via arXiv metadata · 3/3 URLs live · entailment checked against the fetched abstracts; claims are limited to syntax constraints, the practitioner study, and the schema-key experiment
- **Vault cross-links:** none (protocol path unavailable on this host)
- **Builds on / supersedes:** —
- **Open question:** how much grammar-constrained decoding latency varies by grammar complexity and serving runtime; the cited guided-generation result does not establish a universal cost bound.

### 2026-07-02 — Reasoning / test-time-compute models
- **Status:** current
- **Pillar:** ml-techniques
- **Method:** storm (3 perspectives: test-time-compute proponent / cost-generality skeptic / deployment practitioner)
- **Sources:** 22 · **Confidence:** high
- **File:** [corpus/ml-techniques/reasoning-models.md](ml-techniques/reasoning-models.md)
- **Citation audit:** 22/22 resolved · 20/22 directly fetchable (2 bot-blocked, confirmed real via search/mirror) · gate fixed 1 real misattribution (a rebuttal URL pointing at a *different* rebuttal — re-pointed to Opus & Lawsen arXiv:2506.09250), softened an overstated tracker annotation, corrected "Anthropic-led" to Anthropic Fellows program, pinned the R1 citation to v1 so its 71.0% figure stays checkable
- **Vault cross-links:** none
- **Builds on / supersedes:** —
- **Open question:** whether the overthinking/inverse-scaling failure modes are a fixable reward-design problem or structural — the field is not settled; the collapse-vs-measurement-artifact dispute (Apple vs the rebuttals) is live.

### 2026-07-02 — Preference optimization: RLHF vs DPO vs GRPO
- **Status:** current
- **Pillar:** ml-techniques
- **Method:** deep-research + storm (first dual-harness reconcile: mechanism from deep-research, DPO-vs-PPO contradiction map from STORM)
- **Sources:** 13 · **Confidence:** high
- **File:** [corpus/ml-techniques/preference-optimization.md](ml-techniques/preference-optimization.md)
- **Citation audit:** 13/13 resolved · 13/13 live · every load-bearing number checked against source full text · gate fixed 1 author misattribution (Yan et al., not Feng), 1 paraphrase-in-quotation-marks (replaced with the verbatim sentence), and an unsourced "16–64 samples" lower bound
- **Vault cross-links:** none
- **Builds on / supersedes:** —
- **Open question:** the DPO-vs-PPO gap itself — the re-runs favoring PPO lean on math/code evals where PPO's edge is biggest, and much of the disagreement traces to eval-suite and length-normalization choices rather than the optimizer.

### 2026-07-01 — Prompt injection and the lethal trifecta
- **Status:** current
- **Pillar:** adjacent-knowledge
- **Method:** deep-research
- **Sources:** 7 · **Confidence:** high
- **File:** [corpus/adjacent-knowledge/prompt-injection-lethal-trifecta.md](adjacent-knowledge/prompt-injection-lethal-trifecta.md)
- **Citation audit:** 7/7 resolved · 7/7 live · entailment clean (all verbatim quotes confirmed in-source; no circular sourcing)
- **Vault cross-links:** none (complements the llm-pentest-sop's runtime-enforcement rule)
- **Builds on / supersedes:** —
- **Open question:** whether CaMeL-style capability/taint runtimes can become ergonomic enough for real adoption — the AgentDojo utility figures and developer-authored policies are early evidence.

### 2026-07-01 — LLM inference optimization: continuous batching, paged KV-cache, speculative decoding
- **Status:** current
- **Pillar:** ml-techniques
- **Method:** deep-research
- **Sources:** 12 · **Confidence:** high
- **File:** [corpus/ml-techniques/llm-inference-optimization.md](ml-techniques/llm-inference-optimization.md)
- **Citation audit:** 12/12 unique resolved · all live (1 via bot-block workaround, USENIX) · gate cut an unsupported ~175% mis-tuning figure (traced to an uncited single-config Medium post) and merged a duplicate source entry
- **Vault cross-links:** none
- **Builds on / supersedes:** —
- **Open question:** the continuous-batching-vs-speculative-decoding architectural tension (high batch for throughput vs low batch for latency) — MagicDec-style resolutions unverified; exact PagedAttention gather overhead unquantified from a primary source.

### 2026-07-01 — Durable execution engines (Temporal, Restate, DBOS)
- **Status:** current
- **Pillar:** design-patterns
- **Method:** deep-research
- **Sources:** 13 · **Confidence:** high
- **File:** [corpus/design-patterns/durable-execution-engines.md](design-patterns/durable-execution-engines.md)
- **Citation audit:** 13/13 resolved · 13/13 live · all load-bearing numbers verified verbatim; gate fixed 1 over-attribution (saga-gap framing recast as explicit synthesis) and 2 paraphrased titles
- **Vault cross-links:** none
- **Builds on / supersedes:** answers the open question in [saga-pattern](design-patterns/saga-pattern.md) (where the durable layer under a saga lives)
- **Open question:** vendor-reported performance figures (Restate ~94K steps/s; DBOS ~25x vs Step Functions) have no independent reproduction; DBOS's exactly-once semantics for non-Postgres external calls not pinned from a single primary source.

### 2026-07-01 — Model Context Protocol (MCP): the agent–tool integration standard
- **Status:** current
- **Pillar:** adjacent-knowledge
- **Method:** deep-research
- **Sources:** 9 · **Confidence:** high
- **File:** [corpus/adjacent-knowledge/model-context-protocol.md](adjacent-knowledge/model-context-protocol.md)
- **Citation audit:** 9/9 resolved · 9/9 live · gate fixed 3 entailment problems (spec-version relabel; Willison "lethal trifecta" attribution corrected to his June-2025 post, added as a source; N×M arithmetic de-cited to the framing source's actual claim)
- **Vault cross-links:** none
- **Builds on / supersedes:** —
- **Open question:** how much of the self-reported adoption (10,000+ public servers, 97M+ monthly SDK downloads) reflects production use rather than experimentation — figures are Anthropic's own, no independent audit located.

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
