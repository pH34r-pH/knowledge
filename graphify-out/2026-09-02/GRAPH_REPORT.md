# Graph Report - knowledge  (2026-09-02)

## Corpus Check
- 154 files · ~138,501 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 604 nodes · 680 edges · 58 communities
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c3bf130b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- common.sh
- logarithmic-closed-numerical-representations.md
- create-new-feature.ps1
- common.ps1
- Tasks: [FEATURE NAME]
- analyze.md
- Blue Swallow Society Constitution
- prompt-injection-lethal-trifecta.md
- idempotency-keys.md
- Blue Swallow Society Constitution
- Entries
- Tasks: Corpus Population Research Loop
- README.md
- Feature Specification: [FEATURE NAME]
- User Scenarios & Testing *(mandatory)*
- Core Principles
- Building the corpus
- Citation integrity
- Populate Corpus — the researcher loop
- llm-inference-optimization.md
- Implementation Plan: Corpus Population Research Loop
- Implementation Plan: [FEATURE]
- Implementation Plan: Raw Research Material Ingestion
- checklist.md
- commands/plan.md
- specify.md
- commands/tasks.md
- Knowledge Corpus — Project Context
- model-context-protocol.md
- system-design-fundamentals.md
- OpenTelemetry: telemetry interoperability, not an observability backend
- Software supply-chain security: inventory, provenance, and policy
- Actor model versus CSP channels: ownership and coordination
- saga-pattern.md
- Structured concurrency: lifetime-bounded task trees
- backpropagation-autodiff.md
- Preference Optimization: RLHF vs DPO vs GRPO — Mechanism, Trade-offs, and Failure Modes
- rag-retrieval-architectures.md
- Reasoning / Test-Time-Compute Models: Mechanism, Trade-offs, and Failure Modes
- Harness & skill options
- Citation audit — 2026-07-01
- Eval: does feeding a corpus article improve an LLM's software-design answers?
- Corpus Topic Backlog
- [CHECKLIST TYPE] Checklist: [FEATURE NAME]
- clarify.md
- commands/constitution.md
- taskstoissues.md
- implement.md
- Agent memory architectures: retrieval, distillation, and bounded context
- attention-transformers.md
- Fine-tuning strategies: full updates, adapters, low-rank deltas, and preference objectives
- Mixture-of-Experts routing: sparse capacity and distributed costs
- Self-evolving agent systems: guarded outer loops over agent artifacts
- State-space models and linear attention: efficient sequence alternatives
- Structured outputs and constrained decoding: syntax guarantees, semantic limits

## God Nodes (most connected - your core abstractions)
1. `Entries` - 28 edges
2. `Tasks: [FEATURE NAME]` - 13 edges
3. `Tasks: Corpus Population Research Loop` - 11 edges
4. `Populate Corpus — the researcher loop` - 10 edges
5. `Building the corpus` - 10 edges
6. `get_feature_paths()` - 9 edges
7. `setup-tasks.sh script` - 9 edges
8. `create-new-feature.sh script` - 8 edges
9. `check-prerequisites.sh script` - 7 edges
10. `Execution Steps` - 7 edges

## Surprising Connections (you probably didn't know these)
- `check-prerequisites.sh script` --calls--> `check_dir()`  [EXTRACTED]
  .specify/scripts/bash/check-prerequisites.sh → .specify/scripts/bash/common.sh
- `check-prerequisites.sh script` --calls--> `check_feature_branch()`  [EXTRACTED]
  .specify/scripts/bash/check-prerequisites.sh → .specify/scripts/bash/common.sh
- `check-prerequisites.sh script` --calls--> `check_file()`  [EXTRACTED]
  .specify/scripts/bash/check-prerequisites.sh → .specify/scripts/bash/common.sh
- `check-prerequisites.sh script` --calls--> `get_feature_paths()`  [EXTRACTED]
  .specify/scripts/bash/check-prerequisites.sh → .specify/scripts/bash/common.sh
- `check-prerequisites.sh script` --calls--> `has_jq()`  [EXTRACTED]
  .specify/scripts/bash/check-prerequisites.sh → .specify/scripts/bash/common.sh

## Import Cycles
- None detected.

## Communities (58 total, 0 thin omitted)

### Community 0 - "common.sh"
Cohesion: 0.14
Nodes (27): check-prerequisites.sh script, check_dir(), check_feature_branch(), check_file(), feature_json_matches_feature_dir(), find_feature_dir_by_prefix(), find_specify_root(), get_current_branch() (+19 more)

### Community 1 - "logarithmic-closed-numerical-representations.md"
Cohesion: 0.18
Nodes (10): A practical evaluation protocol, Arbitrary and mixed bases, Closed products with an explicit phase law, Further reading, How the design space evolved, Power-of-two logarithmic quantization, Trade-offs and failure modes, What it is (+2 more)

### Community 2 - "create-new-feature.ps1"
Cohesion: 0.46
Nodes (7): ConvertTo-CleanBranchName(), Get-BranchName(), Get-HighestNumberFromBranches(), Get-HighestNumberFromNames(), Get-HighestNumberFromRemoteRefs(), Get-HighestNumberFromSpecs(), Get-NextBranchNumber()

### Community 3 - "common.ps1"
Cohesion: 0.23
Nodes (11): Find-FeatureDirByPrefix(), Find-SpecifyRoot(), Get-CurrentBranch(), Get-FeatureDirFromBranchPrefixOrExit(), Get-FeaturePathsEnv(), Get-Python3Command(), Get-RepoRoot(), Get-SpecKitEffectiveBranchName() (+3 more)

### Community 4 - "Tasks: [FEATURE NAME]"
Cohesion: 0.07
Nodes (26): Dependencies & Execution Order, Format: `[ID] [P?] [Story] Description`, Implementation for User Story 1, Implementation for User Story 2, Implementation for User Story 3, Implementation Strategy, Incremental Delivery, MVP First (User Story 1 Only) (+18 more)

### Community 5 - "analyze.md"
Cohesion: 0.08
Nodes (25): 1. Initialize Analysis Context, 2. Load Artifacts (Progressive Disclosure), 3. Build Semantic Models, 4. Detection Passes (Token-Efficient Analysis), 5. Severity Assignment, 6. Produce Compact Analysis Report, 7. Provide Next Actions, 8. Offer Remediation (+17 more)

### Community 6 - "Blue Swallow Society Constitution"
Cohesion: 0.10
Nodes (20): Additional Security Requirements, API Security, Authentication and Authorization, Blue Swallow Society Constitution, Code Review Security Focus, Core Principles, Data Protection, Dependency Management (+12 more)

### Community 7 - "prompt-injection-lethal-trifecta.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 8 - "idempotency-keys.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 13 - "Blue Swallow Society Constitution"
Cohesion: 0.10
Nodes (20): Additional Security Requirements, API Security, Authentication and Authorization, Blue Swallow Society Constitution, Code Review Security Focus, Core Principles, Data Protection, Dependency Management (+12 more)

### Community 14 - "Entries"
Cohesion: 0.07
Nodes (30): 2026-07-01 — Attention and the Transformer architecture, internals, 2026-07-01 — Backpropagation and automatic differentiation, 2026-07-01 — CQRS and event sourcing, 2026-07-01 — Durable execution engines (Temporal, Restate, DBOS), 2026-07-01 — Evaluating agents and models rigorously (baselines, significance, honest reporting), 2026-07-01 — Graceful degradation: ranked fallback chains, 2026-07-01 — Idempotency keys and exactly-once-effect APIs, 2026-07-01 — LLM inference optimization: continuous batching, paged KV-cache, speculative decoding (+22 more)

### Community 15 - "Tasks: Corpus Population Research Loop"
Cohesion: 0.11
Nodes (17): Dependencies & Execution Order, Format: `[ID] [P?] [Story] Description`, Implementation for User Story 1, Implementation for User Story 2, Implementation for User Story 3 (recurring — not a one-time checklist), Implementation for User Story 4, Notes, Phase 1: Setup (Shared Infrastructure) (+9 more)

### Community 16 - "README.md"
Cohesion: 0.05
Nodes (32): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it, Further reading, How it works (+24 more)

### Community 17 - "Feature Specification: [FEATURE NAME]"
Cohesion: 0.15
Nodes (12): Assumptions, Edge Cases, Feature Specification: [FEATURE NAME], Functional Requirements, Key Entities *(include if feature involves data)*, Measurable Outcomes, Requirements *(mandatory)*, Success Criteria *(mandatory)* (+4 more)

### Community 18 - "User Scenarios & Testing *(mandatory)*"
Cohesion: 0.15
Nodes (13): Assumptions, Edge Cases, Feature Specification: Corpus Population Research Loop, Functional Requirements, Key Entities *(include if feature involves data)*, Measurable Outcomes, Requirements *(mandatory)*, Success Criteria *(mandatory)* (+5 more)

### Community 19 - "Core Principles"
Cohesion: 0.18
Nodes (10): Core Principles, Governance, [PRINCIPLE_1_NAME], [PRINCIPLE_2_NAME], [PRINCIPLE_3_NAME], [PRINCIPLE_4_NAME], [PRINCIPLE_5_NAME], [PROJECT_NAME] Constitution (+2 more)

### Community 20 - "Building the corpus"
Cohesion: 0.20
Nodes (10): Article shape, Building the corpus, Citation integrity is non-negotiable, Current state (2026-08-07), Does feeding the corpus actually help?, How to run one iteration, Repo & backup, The four research harnesses (+2 more)

### Community 21 - "Citation integrity"
Cohesion: 0.20
Nodes (10): Citation integrity, Corrections applied during verification, Layer 1 — Deterministic (no model judgment, cannot be gamed), Layer 2 — Model-based (catches misgrounding the deterministic layer can't), Layer 3 — Process / architecture (makes the above possible and honest), Layer 4 — Measurement (make integrity a number, not a vibe), Residual risks (what no guard fully closes), Sources (+2 more)

### Community 22 - "Populate Corpus — the researcher loop"
Cohesion: 0.20
Nodes (10): Boundaries (read first), Output, Populate Corpus — the researcher loop, Step 1 — Load state, Step 2 — Select the topic, Step 3 — Decide the research harness, Step 4 — Write the article, Step 5 — Citation integrity gate (run before committing) (+2 more)

### Community 23 - "llm-inference-optimization.md"
Cohesion: 0.20
Nodes (9): Continuous batching, Further reading, How it works, In practice, Paged KV-cache (PagedAttention), Speculative decoding, Trade-offs, What it is (+1 more)

### Community 24 - "Implementation Plan: Corpus Population Research Loop"
Cohesion: 0.20
Nodes (9): Complexity Tracking, Constitution Check, Documentation (this feature), Implementation Plan: Corpus Population Research Loop, Notes, Project Structure, Source Code (repository root), Summary (+1 more)

### Community 25 - "Implementation Plan: [FEATURE]"
Cohesion: 0.22
Nodes (8): Complexity Tracking, Constitution Check, Documentation (this feature), Implementation Plan: [FEATURE], Project Structure, Source Code (repository root), Summary, Technical Context

### Community 26 - "Implementation Plan: Raw Research Material Ingestion"
Cohesion: 0.22
Nodes (8): Complexity Tracking, Constitution Check, Documentation (this feature), Implementation Plan: Raw Research Material Ingestion, Project Structure, Source Code (repository root), Summary, Technical Context

### Community 27 - "checklist.md"
Cohesion: 0.25
Nodes (7): Anti-Examples: What NOT To Do, Checklist Purpose: "Unit Tests for English", Example Checklist Types & Sample Items, Execution Steps, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 28 - "commands/plan.md"
Cohesion: 0.25
Nodes (7): Key rules, Outline, Phase 0: Outline & Research, Phase 1: Design & Contracts, Phases, Pre-Execution Checks, User Input

### Community 29 - "specify.md"
Cohesion: 0.25
Nodes (7): For AI Generation, Outline, Pre-Execution Checks, Quick Guidelines, Section Requirements, Success Criteria Guidelines, User Input

### Community 30 - "commands/tasks.md"
Cohesion: 0.25
Nodes (7): Checklist Format (REQUIRED), Outline, Phase Structure, Pre-Execution Checks, Task Generation Rules, Task Organization, User Input

### Community 32 - "Knowledge Corpus — Project Context"
Cohesion: 0.29
Nodes (6): Git and verification discipline, Knowledge Corpus — Project Context, Purpose and authority, Research integrity gates, Spec Kit contract, Vault, privacy, and provenance boundaries

### Community 33 - "model-context-protocol.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 34 - "system-design-fundamentals.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 35 - "OpenTelemetry: telemetry interoperability, not an observability backend"
Cohesion: 0.29
Nodes (7): Further reading, How it works, In practice, OpenTelemetry: telemetry interoperability, not an observability backend, Trade-offs, What it is, When to reach for it

### Community 37 - "Software supply-chain security: inventory, provenance, and policy"
Cohesion: 0.29
Nodes (7): Further reading, How it works, In practice, Software supply-chain security: inventory, provenance, and policy, Trade-offs, What it is, When to reach for it

### Community 39 - "Actor model versus CSP channels: ownership and coordination"
Cohesion: 0.29
Nodes (7): Actor model versus CSP channels: ownership and coordination, Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 40 - "saga-pattern.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 41 - "Structured concurrency: lifetime-bounded task trees"
Cohesion: 0.29
Nodes (7): Further reading, How it works, In practice, Structured concurrency: lifetime-bounded task trees, Trade-offs, What it is, When to reach for it

### Community 42 - "backpropagation-autodiff.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 43 - "Preference Optimization: RLHF vs DPO vs GRPO — Mechanism, Trade-offs, and Failure Modes"
Cohesion: 0.29
Nodes (7): Further reading, How it works, In practice, Preference Optimization: RLHF vs DPO vs GRPO — Mechanism, Trade-offs, and Failure Modes, Trade-offs, What it is, When to reach for it

### Community 44 - "rag-retrieval-architectures.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 45 - "Reasoning / Test-Time-Compute Models: Mechanism, Trade-offs, and Failure Modes"
Cohesion: 0.29
Nodes (7): Further reading, How it works, In practice, Reasoning / Test-Time-Compute Models: Mechanism, Trade-offs, and Failure Modes, Trade-offs, What it is, When to reach for it

### Community 46 - "Harness & skill options"
Cohesion: 0.33
Nodes (5): Adopted (codified into the protocol), Considered and skipped (redundant with existing stages), Harness & skill options, One genuine non-integrity gap noted, Recommended, deferred to your call (external services — egress/key/cost)

### Community 47 - "Citation audit — 2026-07-01"
Cohesion: 0.33
Nodes (6): Citation audit — 2026-07-01, Confirmed problems fixed, False alarms dismissed by the re-check (no change to the claim), Headline, Per-article result, Residual notes

### Community 48 - "Eval: does feeding a corpus article improve an LLM's software-design answers?"
Cohesion: 0.33
Nodes (6): Eval: does feeding a corpus article improve an LLM's software-design answers?, Interpretation, Pre-registration (fixed before any answer was generated), Results, Threats to validity (why this is a signal, not a settled result), Verdict

### Community 49 - "Corpus Topic Backlog"
Cohesion: 0.33
Nodes (6): Adjacent High-Value Knowledge, Corpus Topic Backlog, Machine Learning Techniques, Prioritization: recent-first, Recent & fast-moving (highest EV — post-cutoff), Software Engineering Design Patterns

### Community 50 - "[CHECKLIST TYPE] Checklist: [FEATURE NAME]"
Cohesion: 0.40
Nodes (4): [Category 1], [Category 2], [CHECKLIST TYPE] Checklist: [FEATURE NAME], Notes

### Community 51 - "clarify.md"
Cohesion: 0.40
Nodes (4): Outline, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 52 - "commands/constitution.md"
Cohesion: 0.40
Nodes (4): Outline, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 53 - "taskstoissues.md"
Cohesion: 0.40
Nodes (4): Outline, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 54 - "implement.md"
Cohesion: 0.50
Nodes (3): Outline, Pre-Execution Checks, User Input

### Community 55 - "Agent memory architectures: retrieval, distillation, and bounded context"
Cohesion: 0.29
Nodes (7): Agent memory architectures: retrieval, distillation, and bounded context, Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 56 - "attention-transformers.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 57 - "Fine-tuning strategies: full updates, adapters, low-rank deltas, and preference objectives"
Cohesion: 0.29
Nodes (7): Fine-tuning strategies: full updates, adapters, low-rank deltas, and preference objectives, Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 58 - "Mixture-of-Experts routing: sparse capacity and distributed costs"
Cohesion: 0.29
Nodes (7): Further reading, How it works, In practice, Mixture-of-Experts routing: sparse capacity and distributed costs, Trade-offs, What it is, When to reach for it

### Community 59 - "Self-evolving agent systems: guarded outer loops over agent artifacts"
Cohesion: 0.29
Nodes (7): Further reading, How it works, In practice, Self-evolving agent systems: guarded outer loops over agent artifacts, Trade-offs, What it is, When to reach for it

### Community 60 - "State-space models and linear attention: efficient sequence alternatives"
Cohesion: 0.29
Nodes (7): Further reading, How it works, In practice, State-space models and linear attention: efficient sequence alternatives, Trade-offs, What it is, When to reach for it

### Community 61 - "Structured outputs and constrained decoding: syntax guarantees, semantic limits"
Cohesion: 0.29
Nodes (7): Further reading, How it works, In practice, Structured outputs and constrained decoding: syntax guarantees, semantic limits, Trade-offs, What it is, When to reach for it

## Knowledge Gaps
- **417 isolated node(s):** `common.sh script`, `Boundaries (read first)`, `Step 1 — Load state`, `Step 2 — Select the topic`, `Step 3 — Decide the research harness` (+412 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 435 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Corpus Research Ledger` connect `Entries` to `README.md`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `Feature Specification: Corpus Population Research Loop` connect `User Scenarios & Testing *(mandatory)*` to `README.md`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **What connects `common.sh script`, `Boundaries (read first)`, `Step 1 — Load state` to the rest of the system?**
  _417 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `common.sh` be split into smaller, more focused modules?**
  _Cohesion score 0.14393939393939395 - nodes in this community are weakly interconnected._
- **Should `Tasks: [FEATURE NAME]` be split into smaller, more focused modules?**
  _Cohesion score 0.07407407407407407 - nodes in this community are weakly interconnected._
- **Should `analyze.md` be split into smaller, more focused modules?**
  _Cohesion score 0.07692307692307693 - nodes in this community are weakly interconnected._
- **Should `Blue Swallow Society Constitution` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._