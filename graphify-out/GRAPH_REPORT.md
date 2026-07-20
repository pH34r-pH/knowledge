# Graph Report - knowledge  (2026-07-12)

## Corpus Check
- 80 files · ~430,762 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 496 nodes · 518 edges · 55 communities (51 shown, 4 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- common.sh
- create-new-feature.sh
- create-new-feature.ps1
- common.ps1
- Tasks: [FEATURE NAME]
- analyze.md
- Blue Swallow Society Constitution
- check-prerequisites.sh
- setup-plan.sh
- setup-tasks.sh
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
- plan.md
- specify.md
- tasks.md
- graceful-degradation.md
- model-context-protocol.md
- prompt-injection-lethal-trifecta.md
- system-design-fundamentals.md
- cqrs-event-sourcing.md
- durable-execution-engines.md
- idempotency-keys.md
- resilience-patterns.md
- saga-pattern.md
- agent-evaluation-methodology.md
- attention-transformers.md
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
- constitution.md
- taskstoissues.md
- implement.md

## God Nodes (most connected - your core abstractions)
1. `Entries` - 18 edges
2. `Tasks: [FEATURE NAME]` - 13 edges
3. `Tasks: Corpus Population Research Loop` - 11 edges
4. `Populate Corpus — the researcher loop` - 10 edges
5. `Building the corpus` - 10 edges
6. `Execution Steps` - 7 edges
7. `4. Detection Passes (Token-Efficient Analysis)` - 7 edges
8. `Preference Optimization: RLHF vs DPO vs GRPO — Mechanism, Trade-offs, and Failure Modes` - 7 edges
9. `Reasoning / Test-Time-Compute Models: Mechanism, Trade-offs, and Failure Modes` - 7 edges
10. `Implementation Plan: Corpus Population Research Loop` - 7 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (55 total, 4 thin omitted)

### Community 0 - "common.sh"
Cohesion: 0.12
Nodes (4): get_current_branch(), get_feature_paths(), has_git(), common.sh script

### Community 1 - "create-new-feature.sh"
Cohesion: 0.25
Nodes (3): _extract_highest_number(), get_highest_from_branches(), create-new-feature.sh script

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

### Community 13 - "Blue Swallow Society Constitution"
Cohesion: 0.10
Nodes (20): Additional Security Requirements, API Security, Authentication and Authorization, Blue Swallow Society Constitution, Code Review Security Focus, Core Principles, Data Protection, Dependency Management (+12 more)

### Community 14 - "Entries"
Cohesion: 0.10
Nodes (20): 2026-07-01 — Attention and the Transformer architecture, internals, 2026-07-01 — Backpropagation and automatic differentiation, 2026-07-01 — CQRS and event sourcing, 2026-07-01 — Durable execution engines (Temporal, Restate, DBOS), 2026-07-01 — Evaluating agents and models rigorously (baselines, significance, honest reporting), 2026-07-01 — Graceful degradation: ranked fallback chains, 2026-07-01 — Idempotency keys and exactly-once-effect APIs, 2026-07-01 — LLM inference optimization: continuous batching, paged KV-cache, speculative decoding (+12 more)

### Community 15 - "Tasks: Corpus Population Research Loop"
Cohesion: 0.11
Nodes (17): Dependencies & Execution Order, Format: `[ID] [P?] [Story] Description`, Implementation for User Story 1, Implementation for User Story 2, Implementation for User Story 3 (recurring — not a one-time checklist), Implementation for User Story 4, Notes, Phase 1: Setup (Shared Infrastructure) (+9 more)

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
Nodes (10): Article shape, Building the corpus, Citation integrity is non-negotiable, Current state (2026-07-02), Does feeding the corpus actually help?, How to run one iteration, Repo & backup, The four research harnesses (+2 more)

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

### Community 28 - "plan.md"
Cohesion: 0.25
Nodes (7): Key rules, Outline, Phase 0: Outline & Research, Phase 1: Design & Contracts, Phases, Pre-Execution Checks, User Input

### Community 29 - "specify.md"
Cohesion: 0.25
Nodes (7): For AI Generation, Outline, Pre-Execution Checks, Quick Guidelines, Section Requirements, Success Criteria Guidelines, User Input

### Community 30 - "tasks.md"
Cohesion: 0.25
Nodes (7): Checklist Format (REQUIRED), Outline, Phase Structure, Pre-Execution Checks, Task Generation Rules, Task Organization, User Input

### Community 31 - "graceful-degradation.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 32 - "model-context-protocol.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 33 - "prompt-injection-lethal-trifecta.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 34 - "system-design-fundamentals.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 35 - "cqrs-event-sourcing.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 36 - "durable-execution-engines.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 37 - "idempotency-keys.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 38 - "resilience-patterns.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 39 - "saga-pattern.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 40 - "agent-evaluation-methodology.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

### Community 41 - "attention-transformers.md"
Cohesion: 0.29
Nodes (6): Further reading, How it works, In practice, Trade-offs, What it is, When to reach for it

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

### Community 52 - "constitution.md"
Cohesion: 0.40
Nodes (4): Outline, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 53 - "taskstoissues.md"
Cohesion: 0.40
Nodes (4): Outline, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 54 - "implement.md"
Cohesion: 0.50
Nodes (3): Outline, Pre-Execution Checks, User Input

## Knowledge Gaps
- **337 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+332 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Corpus Research Ledger` connect `Entries` to `README.md`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `Feature Specification: Corpus Population Research Loop` connect `User Scenarios & Testing *(mandatory)*` to `README.md`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **What connects `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script` to the rest of the system?**
  _337 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `common.sh` be split into smaller, more focused modules?**
  _Cohesion score 0.12418300653594772 - nodes in this community are weakly interconnected._
- **Should `Tasks: [FEATURE NAME]` be split into smaller, more focused modules?**
  _Cohesion score 0.07407407407407407 - nodes in this community are weakly interconnected._
- **Should `analyze.md` be split into smaller, more focused modules?**
  _Cohesion score 0.07692307692307693 - nodes in this community are weakly interconnected._
- **Should `Blue Swallow Society Constitution` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._