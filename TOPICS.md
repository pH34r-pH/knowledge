# Corpus Topic Backlog

Living, prioritized queue for the `populate-corpus` loop (`.claude/skills/populate-corpus/SKILL.md`). Checked = written to `corpus/`; see [corpus/LEDGER.md](corpus/LEDGER.md) for the run record (method, sources, confidence). Add new candidates to the relevant pillar as they surface — the loop should not invent topics that aren't queued here first, and should append new candidates here (with a one-line reason) before picking one, once a pillar runs dry.

Each line: `- [ ] Topic — why it matters (harness: hint)`. The harness hint is a starting suggestion, not binding — Step 3 of the skill makes the real call.

## Prioritization: recent-first

Rank by **marginal value to an LLM with a training cutoff**, not importance in the abstract. The corpus is fed to a model that already knows the saturated, foundational material well (the [eval](corpus/EVAL-corpus-leverage-2026-07-01.md) confirmed even those get a completeness lift, but a smaller one). The **highest-EV topics are recent / post-cutoff** — new techniques, tooling standards, shifted best practices, unsettled results. Pick from the recent cluster below first; treat the foundational pillars as fill-in with a fresh angle. Recent topics are also the fabrication-prone ones, so they go through a live-retrieval harness (`deep-research`/`storm`), never `vault-adapt`.

## Recent & fast-moving (highest EV — post-cutoff)

- [x] Model Context Protocol (MCP): the agent–tool integration standard — client/server/transport model, and where it fits vs plain function-calling (harness: deep-research)
- [x] Reasoning / test-time-compute models (o1-style): what changed, when extended reasoning pays vs wastes tokens, how it reshapes prompting and evals (harness: storm)
- [x] LLM inference optimization: continuous batching, paged KV-cache (vLLM), speculative decoding — the serving-cost levers (harness: deep-research)
- [x] Preference optimization past RLHF: DPO, GRPO, and when RL beats plain SFT (harness used: dual deep-research + storm)
- [x] Prompt injection & the lethal trifecta: securing tool-using agents (private data + untrusted content + egress), scope enforced in the runtime not the prompt (harness: deep-research)
- [x] Structured outputs & constrained decoding: grammar/JSON-schema-guided generation and its reliability failure modes (harness: deep-research)
- [x] Durable execution engines (Temporal / Restate / DBOS): workflows-as-code, and how they absorb the saga "technical-failure" layer (extends the saga article's open question) (harness: deep-research)
- [x] State-space models & linear attention (Mamba et al.): the post-transformer challengers, where they win and lose (harness: storm)
- [x] Mixture-of-Experts routing: sparse activation, load-balancing losses, the serving trade-offs (harness: deep-research)
- [ ] Context engineering as a discipline: prompt-caching economics, long-context vs retrieval, context-rot; include the "prompting as programming / LLMs as compilers" framing (DSPy's compile-declarative-calls line, structured prompting) and pressure-test where the compiler metaphor holds vs leaks (deterministic spec vs stochastic model) (harness: storm)
- [x] Software supply-chain security: SBOM, SLSA, sigstore/provenance — post-xz-attack best practice (harness: deep-research)
- [x] OpenTelemetry as the observability standard: unified traces/metrics/logs, semantic conventions (harness: deep-research)

## Software Engineering Design Patterns

- [x] Saga pattern for distributed transactions — replaces two-phase commit across service boundaries; foundational to any service-decomposition project (harness: deep-research)
- [x] CQRS and event sourcing — the split only pays for itself past a specific complexity threshold; genuinely contested among practitioners (harness: storm)
- [x] Resilience patterns: circuit breaker, retry-with-jitter, timeout budgets — the three that actually stop cascading failure (harness: deep-research)
- [ ] Outbox pattern for reliable event publishing — the standard fix for the dual-write problem (harness: deep-research)
- [x] Idempotency keys and exactly-once-effect APIs — how to make retries safe at the API boundary (harness: deep-research)
- [x] Structured concurrency vs. thread pools and async callbacks — why the newer model composes better under cancellation and error propagation (harness: storm)
- [x] Actor model vs. CSP/channels for concurrent systems — two mature answers to the same problem, different tradeoffs (harness: storm)
- [ ] API pagination and versioning strategies at scale — cursor vs. offset, and how real APIs evolve without breaking clients (harness: deep-research)
- [ ] Agentic design patterns, extended — Gulli's 2025 catalog is already an authority prior in the vault; extend it with harness-layer patterns from this repo's own arxiv cluster (MOSS, SkillClaw, Meta-Harness) (harness: vault-adapt + deep-research)
- [ ] Bulkhead and backpressure patterns for resource isolation — containing failure blast radius under load (harness: deep-research)
- [ ] Strangler fig pattern for legacy migration — the vault already has a tested take on agentic migration discipline; generalize it (harness: vault-adapt + deep-research)

## Machine Learning Techniques

- [x] Backpropagation and automatic differentiation, from first principles — the mechanism, not just the name (harness: deep-research)
- [ ] PCA and eigendecomposition — the intuition behind the math and where it actually gets used (harness: deep-research)
- [ ] Regularization: L1/L2, dropout, early stopping — why each one works, not just what it does (harness: deep-research)
- [x] Attention and the Transformer architecture, internals — the mechanism the whole current wave is built on (harness: deep-research)
- [x] RAG architectures: vector vs. graph vs. hybrid retrieval — directly relevant to this repo's own stated purpose; genuinely contested tradeoffs (harness: storm)
- [x] Fine-tuning strategies: full fine-tune vs. LoRA/QLoRA vs. RLHF/DPO — when each is worth its cost (harness: storm)
- [x] Agent evaluation methodology — grounded in Claw-Eval, $OneMillion-Bench, Terminal-Bench already sitting in `arxiv/` (harness: vault-adapt + deep-research)
- [x] Agent memory architectures — grounded in MemEvolve and GenericAgent already sitting in `arxiv/` (harness: vault-adapt + deep-research)
- [ ] Bias-variance tradeoff and the double-descent wrinkle — the classical framing plus the part modern deep learning complicates (harness: deep-research)
- [x] Self-evolving agent systems: harness-layer vs. text-mutable-layer adaptation — this repo's own seed paper (MOSS) makes the core argument; write it up properly (harness: vault-adapt)
- [ ] Representation–architecture co-design for language models — tokenization, geometry, algebra, and compute allocation must be evaluated as crossed representation × operator choices rather than isolated swaps (harness: deep-research + storm)
- [ ] Complex/phase-aware and hyperspherical Transformer computation — separate useful phase algebra, unit-sphere normalization, recurrent depth, and retained-radius claims with matched controls (harness: deep-research + storm)
- [ ] Vector-symbolic representations and algebra-aware neural processing — HRR/FHRR binding, superposition, cleanup, and when Hrrformer-style operators add more than generic attention (harness: deep-research)
- [ ] Spectral graph methods as representation/operator co-design — Laplacian-induced bases, spectral attention, gauge ambiguity, and oversmoothing/oversquashing diagnostics (harness: deep-research + storm)
- [ ] Cellular sheaves and heterogeneous local representation spaces — sheaf Laplacians, restriction maps, neural sheaf diffusion, and interoperability without flattening every state into one geometry (harness: deep-research)
- [ ] Dynamic modular computation: MoE to module routing to problem-specific execution graphs — distinguish selecting one expert from assembling a typed one-pass computation DAG, including planner cost (harness: storm)
- [ ] Delayed generalization, grokking, and training-trajectory forecasting — distinguish descriptive curve fitting, mechanistic precursors, change points, and preregistered late-horizon forecasts (harness: deep-research + storm)
- [ ] Logarithmic and closed numerical representations for neural arithmetic — LNS quantization, CurveFP product closure, accumulation semantics, and which apparent hardware gains survive charged controls (harness: deep-research)
- [ ] Signal-processing views of learned representations and receiver-side decoding — matched analysis, despreading, equalization, source separation, synchronization, and the transmitter-versus-receiver diagnosis boundary (harness: storm)

## Adjacent High-Value Knowledge

- [x] System design fundamentals: load balancing, caching, sharding, consistent hashing — the vocabulary every scaling conversation assumes (harness: deep-research)
- [ ] Threat modeling and least privilege for engineers who aren't security specialists — the 20% that prevents 80% of incidents (harness: deep-research)
- [ ] Testing strategy: property-based testing, contract testing, mutation testing — past unit vs. integration (harness: deep-research)
- [ ] Analytics engineering patterns (staging → marts) — the vault already has a tested dbt-based take; generalize it (harness: vault-adapt)
- [ ] Observability: structured logging, distributed tracing, SLI/SLO design — what "instrument everything" actually means in practice (harness: deep-research)
- [ ] Monorepo vs. polyrepo and build system design (Bazel/Buck/Nx) — real tradeoffs, not tooling fashion (harness: storm)
- [ ] Secrets management and the point-of-use principle — the vault already has a tested take; generalize it (harness: vault-adapt)
- [x] Graceful degradation and fallback chains — the vault already has a tested take; generalize it (harness: vault-adapt)
- [ ] Incremental, idempotent ingestion for polling sources you don't control — the vault already has a tested take; generalize it (harness: vault-adapt)
- [ ] Cost-aware LLM system design: model routing, caching, fair-use caps — the vault has two tested product-specific takes; generalize past any one product (harness: vault-adapt + deep-research)
