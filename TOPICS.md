# Corpus Topic Backlog

Living, prioritized queue for the `populate-corpus` loop (`.claude/skills/populate-corpus/SKILL.md`). Checked = written to `corpus/`; see [corpus/LEDGER.md](corpus/LEDGER.md) for the run record (method, sources, confidence). Add new candidates to the relevant pillar as they surface — the loop should not invent topics that aren't queued here first, and should append new candidates here (with a one-line reason) before picking one, once a pillar runs dry.

Each line: `- [ ] Topic — why it matters (harness: hint)`. The harness hint is a starting suggestion, not binding — Step 3 of the skill makes the real call.

## Software Engineering Design Patterns

- [ ] Saga pattern for distributed transactions — replaces two-phase commit across service boundaries; foundational to any service-decomposition project (harness: deep-research)
- [ ] CQRS and event sourcing — the split only pays for itself past a specific complexity threshold; genuinely contested among practitioners (harness: storm)
- [ ] Resilience patterns: circuit breaker, retry-with-jitter, timeout budgets — the three that actually stop cascading failure (harness: deep-research)
- [ ] Outbox pattern for reliable event publishing — the standard fix for the dual-write problem (harness: deep-research)
- [ ] Idempotency keys and exactly-once-effect APIs — how to make retries safe at the API boundary (harness: deep-research)
- [ ] Structured concurrency vs. thread pools and async callbacks — why the newer model composes better under cancellation and error propagation (harness: storm)
- [ ] Actor model vs. CSP/channels for concurrent systems — two mature answers to the same problem, different tradeoffs (harness: storm)
- [ ] API pagination and versioning strategies at scale — cursor vs. offset, and how real APIs evolve without breaking clients (harness: deep-research)
- [ ] Agentic design patterns, extended — Gulli's 2025 catalog is already an authority prior in the vault; extend it with harness-layer patterns from this repo's own arxiv cluster (MOSS, SkillClaw, Meta-Harness) (harness: vault-adapt + deep-research)
- [ ] Bulkhead and backpressure patterns for resource isolation — containing failure blast radius under load (harness: deep-research)
- [ ] Strangler fig pattern for legacy migration — the vault already has a tested take on agentic migration discipline; generalize it (harness: vault-adapt + deep-research)

## Machine Learning Techniques

- [ ] Backpropagation and automatic differentiation, from first principles — the mechanism, not just the name (harness: deep-research)
- [ ] PCA and eigendecomposition — the intuition behind the math and where it actually gets used (harness: deep-research)
- [ ] Regularization: L1/L2, dropout, early stopping — why each one works, not just what it does (harness: deep-research)
- [ ] Attention and the Transformer architecture, internals — the mechanism the whole current wave is built on (harness: deep-research)
- [ ] RAG architectures: vector vs. graph vs. hybrid retrieval — directly relevant to this repo's own stated purpose; genuinely contested tradeoffs (harness: storm)
- [ ] Fine-tuning strategies: full fine-tune vs. LoRA/QLoRA vs. RLHF/DPO — when each is worth its cost (harness: storm)
- [ ] Agent evaluation methodology — grounded in Claw-Eval, $OneMillion-Bench, Terminal-Bench already sitting in `arxiv/` (harness: vault-adapt + deep-research)
- [ ] Agent memory architectures — grounded in MemEvolve and GenericAgent already sitting in `arxiv/` (harness: vault-adapt + deep-research)
- [ ] Bias-variance tradeoff and the double-descent wrinkle — the classical framing plus the part modern deep learning complicates (harness: deep-research)
- [ ] Self-evolving agent systems: harness-layer vs. text-mutable-layer adaptation — this repo's own seed paper (MOSS) makes the core argument; write it up properly (harness: vault-adapt)

## Adjacent High-Value Knowledge

- [ ] System design fundamentals: load balancing, caching, sharding, consistent hashing — the vocabulary every scaling conversation assumes (harness: deep-research)
- [ ] Threat modeling and least privilege for engineers who aren't security specialists — the 20% that prevents 80% of incidents (harness: deep-research)
- [ ] Testing strategy: property-based testing, contract testing, mutation testing — past unit vs. integration (harness: deep-research)
- [ ] Analytics engineering patterns (staging → marts) — the vault already has a tested dbt-based take; generalize it (harness: vault-adapt)
- [ ] Observability: structured logging, distributed tracing, SLI/SLO design — what "instrument everything" actually means in practice (harness: deep-research)
- [ ] Monorepo vs. polyrepo and build system design (Bazel/Buck/Nx) — real tradeoffs, not tooling fashion (harness: storm)
- [ ] Secrets management and the point-of-use principle — the vault already has a tested take; generalize it (harness: vault-adapt)
- [ ] Graceful degradation and fallback chains — the vault already has a tested take; generalize it (harness: vault-adapt)
- [ ] Incremental, idempotent ingestion for polling sources you don't control — the vault already has a tested take; generalize it (harness: vault-adapt)
- [ ] Cost-aware LLM system design: model routing, caching, fair-use caps — the vault has two tested product-specific takes; generalize past any one product (harness: vault-adapt + deep-research)
