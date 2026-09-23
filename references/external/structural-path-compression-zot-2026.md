# Navier–Stokes: Recovering Minimal Structure from Representation-Induced Complexity

## Source
Zot, Michael. 2026. *Navier–Stokes: Recovering Minimal Structure from Representation-Induced Complexity*. Working preprint, dated 2026-09-22.

Canonical research repository: https://github.com/mikecreation/ZotBot/tree/main/research/navier-stokes-spc

Manuscript source: https://github.com/mikecreation/ZotBot/blob/main/research/navier-stokes-spc/paper/main.tex

Audit crosswalk: https://github.com/mikecreation/ZotBot/blob/main/research/navier-stokes-spc/audit/source_crosswalk.md

Verification checklist: https://github.com/mikecreation/ZotBot/blob/main/research/navier-stokes-spc/audit/verification_checklist.md

## Why this is in the knowledge corpus
This preprint is a useful theorem-proving and representation-search methodology reference for domain-scaling-lab. Its transferable proposal is **Structural Path Compression (SPC)**: after a successful reasoning trajectory exists, separate the theorem's dependency structure from work induced by the representation and historical route used to discover it.

The paper's Navier–Stokes result is a proposed reconstruction of part of another proof, not an independently established theorem imported into DSL. The value here is therefore methodological and experimental: it suggests concrete tests for whether DSL's proof-first campaigns contain repeated obligations that can be generated from a smaller typed dependency architecture.

Tracking experiments: domain-scaling-lab #351–#356.

## Method
The paper analyzes the residual-improvement machinery in Section 9 of OpenAI's 2026 *Finite Time Blowup for Navier–Stokes* preprint. It keeps the local correction machinery from Sections 7–8 but attempts to replace a repeated synchronized stage schedule with a filtered, target-accuracy-indexed compiler.

The central diagnostic separates:
1. **same-grade dependency**, which should form an acyclic graph solvable by finite forward substitution; from
2. **higher-grade feedback**, whose return edges should have strictly positive filtration degree.

The proposed pattern is summarized as "acyclic horizontally, increasing vertically."

For the analyzed construction, Zot defines an admissible filtered error state with wave, averaged-mean, zero-average-mean, and compatibility sectors. The proposed reduction depends on two load-bearing estimates: a positive linear return margin and a positive nonlinear difference gain. With the source paper's fixed loss parameter, the manuscript reports margins 0.49996 and 0.19998 respectively.

Given those estimates, a requested finite target grade determines a finite Neumann polynomial and finite filtered Picard calculation. In this representation, target accuracy replaces the historical stage counter as the driver of how many fixed primitive correction blocks are required.

## What is actually claimed
The manuscript does **not** claim to compress the complete 166-page Navier–Stokes proof into a short proof. It targets the repeated residual-improvement architecture of Section 9 while retaining the local inverse, stress, mean, compatibility, pressure, common-domain, derivative-loss, cutoff, and final-realization machinery.

The broader methodological claim is that a successful proof trajectory can contain obligations introduced by its representation. A faithful recoding may make some of those obligations derived rather than independently maintained while preserving the theorem and downstream interface.

A useful operational distinction from the paper is therefore: discovery cost; intrinsic structural/dependency cost; representation-induced cost; and verification cost. Observed reasoning length need not measure intrinsic theorem structure.

## Strongest feature: explicit falsification
For DSL, the paper's audit discipline may be at least as useful as its proposed compression. The accompanying verification checklist says the reconstruction should be treated as broken if an audit finds, among other failures:

- a hidden same-grade cycle;
- an illegal typed use of a primitive;
- loss of admissibility or a missed nonlinear interaction;
- mismatch between the abstract compiler and source-legal operations;
- target-dependent domain collapse or exponent loss;
- hidden dependence on historical genealogy;
- a non-nested accuracy family;
- coefficients incorrectly treated as fixed;
- a primitive family that must grow with requested accuracy.

This is a good template for hostile review of any compressed theorem representation: complexity has not been removed if it was merely moved into an unverified compiler, an implicit type assumption, or a hidden history-dependent interface.

## Domain-scaling-lab mapping
DSL already maintains theorem-ledger claims, boundary witnesses, provenance, and formal validation, so it can test SPC more cleanly than an unconstrained reasoning trace.

The immediate experimental question is not "is SPC true?" but whether it produces measurable value beyond ordinary dependency-DAG cleanup and theorem-ledger deduplication.

The staged validation program is tracked in:
- #351 — pilot: theorem structure vs representation-induced proof work;
- #352 — same-grade DAG vs positive-return feedback;
- #353 — target-indexed finite proof generator with a held-out target;
- #354 — hostile compression audit;
- #355 — predictive test on unseen later theorem structure;
- #356 — bounded automated search over equivalent theorem representations.

Issue #338 is a particularly useful representation-change test case. Raw bases contain gauge-dependent detail, whereas projectors/Grassmann points encode the invariant subspace. A representation search can test whether moving to invariant objects genuinely deletes recurring coordinate obligations while preserving the project's critical boundaries: low rank does not imply a shared subspace, and a shared dynamic subspace does not imply functional sufficiency.

## Experimental acceptance boundary
Do not promote SPC into the standard DSL formal workflow merely because a historical proof can be rewritten more compactly.

A useful result should preserve accepted conclusions, assumptions, counterexamples, provenance, and formal checks; eliminate at least one independently maintained proof obligation; and expose a fixed reusable structural rule that regenerates multiple steps.

A stronger result should survive a held-out target: freeze the primitive family before evaluation and show that a new target can be compiled without inventing another primitive. This separates prospective structural extraction from retrospective compression.

## Citation / provenance status
- The named repository resolves and contains the manuscript source, compiled-paper path, source crosswalk, and explicit verification checklist.
- Version recorded here: working preprint / repository state reviewed 2026-09-22.
- This record reports the author's proposed reconstruction and does not treat it as an independent verification of either the reconstruction or the underlying Navier–Stokes proof.
- The numerical margins above are claims of the manuscript's source-addressed bookkeeping and should remain scoped to that construction.
- No arXiv identifier or DOI was identified in the reviewed repository; the canonical source for this record is the author's research repository.
