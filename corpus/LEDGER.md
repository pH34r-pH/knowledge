# Corpus Research Ledger

Ledger of every `populate-corpus` run — one entry per topic written to `corpus/`. Mirrors the discipline of the vault's own `research-log.md`: consult this **before** researching a topic. If it's covered and still fresh, skip it or scope a new run to the delta; if stale, say so and re-run rather than trust it silently.

Status legend: **current** (trustworthy as-is) · **stale** (the field may have moved, re-check before reuse) · **superseded by …** (a later entry replaced it) · **extended by …** (a later entry built on it).

---

## Entries

<!-- newest first. Template per run:

### YYYY-MM-DD — <topic>
- **Status:** current
- **Pillar:** design-patterns | ml-techniques | adjacent-knowledge
- **Method:** vault-adapt | deep-research | storm
- **Sources:** <count> · **Confidence:** high | medium | low
- **File:** [corpus/<pillar>/<slug>.md](<pillar>/<slug>.md)
- **Vault cross-links:** <links, or "none">
- **Builds on / supersedes:** — (or link to the prior entry)

-->

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
