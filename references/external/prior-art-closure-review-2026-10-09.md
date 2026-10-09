# Claim-level recurrent-dynamics prior-art review — 2026-10-09

## Scope and recorded outcome

This review incorporates the previously uncommitted 36-source audit and an additional 14-source backward-reference, counterexample, and calibration pass. The complete selected pool contains **50 paper identities**: **42 new canonical Works (KWRK-000201–KWRK-000242)** and **eight existing Works reused**. The canonical registry increases from 200 to 242 records. Existing registry bytes were preserved as a prefix; the [intake audit](prior-art-closure-audit-2026-10-09.json) records their hash and every review-to-Work mapping.

The [reviewed input](prior-art-closure-input-2026-10-09.json) preserves bibliographic metadata, source review depth, and source-attributed limits. It is a dated provenance input, not a second Work registry. [works.jsonl](works.jsonl) remains canonical. Earlier intakes remain historical records: [first dynamics intake](recurrent-dynamics-intake-2026-10-09.md) and [second pass](recurrent-dynamics-second-pass-2026-10-09.md).

This is a bounded prior-art review, **not** a claim that all world literature has been exhausted, a full independent entailment audit, or an independent replication. No ExternalClaim or KnowledgeEvidence was promoted. The amount of source inspection varies from full methods to indexed primary abstract; those levels must not be collapsed into one confidence label.

## Pass A — reuse existing computation-through-dynamics instruments

The [Computation-through-Dynamics Toolkit](https://www.biorxiv.org/content/10.1101/2025.02.07.637062v3), **KWRK-000201**, is an existing source of controlled neural dynamics, simulated observations, and model-evaluation machinery. Its author release citation and selected implementation were inspected at [v1.0.2](https://github.com/snel-repo/ComputationThroughDynamicsToolkit/tree/v1.0.2). The software release and manuscript are separate identities; software archive DOI 10.5281/zenodo.22238472 does not identify the paper.

The first action should be a narrow, known-ground-truth fixture adapter, not a replacement training/orchestration framework. Select necessary assets, inspect optional logging defaults, and do not disclose private data through external experiment tracking. Successful execution of author code is still not independent confirmation of every claim in the paper.

The existing Clark/Engelken/Vogt references remain the numerical anchors. [Covariant Lyapunov vectors](https://doi.org/10.1103/PhysRevLett.99.130601), **KWRK-000226**, add an important distinction: covariant directions, QR orthonormal frames, and finite-horizon singular vectors are not interchangeable. A scalar exponent or attractive spectrum does not identify a task-functional direction without separate perturbation/readout evidence.

**Comparison gate:** analytical tiny cases, finite differences, native autodiff, and a pinned upstream fixture must agree within declared tolerances before a new instrument is used to explain a trained model. When the actual transition is available, use it rather than fitting an unnecessary surrogate dynamical model.

## Pass B — compare function, not only state variance or apparent geometry

[Aligned and oblique dynamics](https://arxiv.org/abs/2307.07654v3), **KWRK-000202**, is a close predecessor for the question of whether low-variance directions preserve useful output information. Separate dominant activity variance, immediate decoder sensitivity, persistent dynamical effect, and task-end necessity. A large perturbation effect can be corrected by later recurrence; low-variance state can matter to the answer.

The [output-null preparation](https://doi.org/10.1038/nn.3643) and [communication-subspace](https://doi.org/10.1016/j.neuron.2019.01.026) papers, **KWRK-000220/219**, are biological-system precedents for a narrower methodological point. Silence at the present readout need not imply irrelevance to future computation. In a controlled linearized trajectory, `C_0 v = 0` does not imply `C_k Phi_k v = 0` at later horizons. Calling a direction nuisance requires a specified task, intervention time, and future horizon.

[CompreSSM](https://arxiv.org/abs/2510.02823v4), **KWRK-000212**, provides a controllability/observability-inspired state-reduction comparator. Compare variance-based reduction with finite-horizon output influence and input accessibility; do not import linear balanced-reduction guarantees into arbitrary selective or nonlinear models. The final pass also resolved the primary indexed abstract of [Empirical Minimal-Realisation Compression](https://arxiv.org/abs/2607.05457), **KWRK-000234**. Its authors describe actual reduced networks, not just projected diagnostics. Full methods and reported resource outcomes remain unverified in this review.

The [Jacobian lens](https://arxiv.org/abs/2607.15495v1), **KWRK-000213**, is an existing output-sensitive LM diagnostic. Its sparse local J-space construction is not one universal low-rank plane. Distinguish one transferable linear plane, example-specific planes, and sparse combinations of local directions. The reference implementation is explicitly unmaintained; no production dependency or subjective-experience conclusion follows.

[Grounding Representation Similarity Through Statistical Testing](https://arxiv.org/abs/2108.01661), **KWRK-000232**, adds a practical calibration requirement: a useful representation metric should react to known functional changes and tolerate declared irrelevant transformations. Neither CKA/CCA nor a new dynamical score earns a semantic interpretation merely by producing a plausible visualization.

## Pass C — dynamics comparison and latent-mechanism identification

[DSA](https://arxiv.org/abs/2306.10168v3), [InputDSA](https://arxiv.org/abs/2510.25943v2), [fastDSA](https://arxiv.org/abs/2511.22828v2), [noise-aware optimal transport](https://arxiv.org/abs/2412.14421v1), and [DYNAMO](https://arxiv.org/abs/2302.14078v1) are distinct existing comparators: **KWRK-000203/204/206/207/224**. The related [complex-system metric](https://www.biorxiv.org/content/10.64898/2026.07.16.738953v2) is **KWRK-000205**. They differ in fitting cost, invariances, observation assumptions, and available input information; they should not be treated as synonyms.

[DMD with control](https://doi.org/10.1137/15M1013857), **KWRK-000225**, is an older input-versus-recurrence predecessor. A few recurrent steps do not automatically provide enough data to identify a high-dimensional operator. Test coordinate changes, distinct dynamics with similar state geometry, identical recurrence under different inputs, noise, and partial observation before interpreting a fitted comparison.

The final pass resolved the primary indexed abstract of [Beyond DSA](https://arxiv.org/abs/2607.04493), **KWRK-000233**. The authors report that orthogonal Koopman alignment is neither necessary nor sufficient for topological conjugacy. The full proof remains unreviewed here. The justified change is to add explicit counterexamples and withhold an identical-computation claim, not to import an unread theorem as a project result.

Two further direct controls were recovered through backward references:

- [Partial observation can induce mechanistic mismatches](https://papers.nips.cc/paper_files/paper/2024/hash/7caf9d251b546bc78078b35b4a6f3b7e-Abstract-Conference.html), **KWRK-000236**. The primary abstract describes surrogate models with spurious attractor structure despite fitting observed activity. Its large full PDF exceeded the fetch limit in this pass; full methods were not reviewed.
- [ODIN: nonlinear injective readouts](https://proceedings.mlr.press/v228/versteeg24a.html), **KWRK-000238**. Readout capacity and injectivity provide a controlled latent-recovery comparison. A better observation fit is not independently a correct mechanism.

**Identification gate:** vary observation fraction and readout while holding ground-truth dynamics fixed. Report observation fit, recovered fixed points/subspaces, and out-of-sample perturbation prediction separately. [JacobianODE](https://arxiv.org/abs/2507.01946), **KWRK-000237**, supplies a nonlinear subsystem-control comparator when dynamics must be inferred; it does not replace exact autodiff when the model itself is accessible.

## Pass D — useful depth, stopping, and actual serving cost

Adaptive recurrent computation has established foundations in [ACT](https://arxiv.org/abs/1603.08983), [Universal Transformers](https://arxiv.org/abs/1807.03819), and [PonderNet](https://arxiv.org/abs/2107.05407): **KWRK-000221–223**. [Path Independent Equilibrium Models](https://arxiv.org/abs/2211.09961v1), **KWRK-000208**, is a particularly close 2022 causal predecessor for exploiting extra computation. Independence from initialization for the same input must not be confused with a fixed point that ignores the problem input.

[Adaptive Depth in Looped Transformers](https://arxiv.org/abs/2607.20519v1), **KWRK-000209**, separates training-time trajectory effects from inference-time readout rules. Compare policies on identical frozen trajectories before modifying training. [Prediction Dynamics](https://arxiv.org/abs/2609.21383v1), **KWRK-000210**, provides an especially relevant warning: a useful retrospective geometric explanation need not outperform simpler or richer output comparators in prefix-only prediction.

Always report three outcomes separately:

1. Retrospective oracle opportunity, using completed trajectories.
2. Prediction using only information available at the candidate stopping point.
3. Real online utility after paying for output heads, features, extra passes, cache handling, synchronization, and scheduling.

Preserving the model's eventual answer does not establish correctness. Teacher-forced or multiple-choice screening is not equivalent to free-running generation, where an early exit can change subsequent tokens and cached state.

[Continuous Depth Batching](https://arxiv.org/abs/2608.09444v2), **KWRK-000211**, is a direct recurrent-serving predecessor. Use its boundary-stage, queue/refill, and cache-policy decomposition before implementing another scheduler. Its H100 and controlled-replay results are not measurements on small edge devices. Cache sharing or state copying can change semantics as well as memory footprint.

### Final-pass additions: calibration assumptions and missing-state handling

[CALM](https://arxiv.org/abs/2207.07061v2), [FREE](https://aclanthology.org/2023.emnlp-main.362/), and [Fast yet Safe](https://arxiv.org/abs/2405.20915v2), **KWRK-000229–231**, add direct early-exit, calibration, and serving comparators. These are independent-layer early-exit methods, not automatically drop-in recurrent implementations.

CALM links local exit confidence to sequence-level risk/consistency control under its calibration assumptions. It does not guarantee that each answer is correct or that the bound survives arbitrary distribution shift. FREE supplies synchronized-decoding and missing-state/copying comparisons; fewer executed layers do not imply proportional latency savings.

Fast yet Safe distinguishes calibration methods with different risk assumptions. IID calibration/test sampling and the relevant policy-family marginal monotonicity must be checked rather than inferred from deeper execution. Learn-then-test differs from a monotone-risk procedure; multiplicity and uncertainty must remain explicit. A reported average exit count or FLOP reduction is not device energy evidence.

**Stopping gate:** fixed depth, calibrated task-family curves, margin/entropy/confidence, compatible risk-calibrated rules, and mean-centered/richer output comparators precede expensive spectral features. Promote only a held-out, prefix-valid improvement whose actual cost is charged.

## Pass E — causal state transfer and adversarial interventions

[Functional Alignment Can Mislead](https://proceedings.mlr.press/v267/smith25a.html), **KWRK-000214**, is a direct warning against inferring native shared algorithms from successful stitching. The [subspace-patching illusion](https://proceedings.iclr.cc/paper_files/paper/2024/hash/70b8505ac79e3e131756f793cd80eb8d-Abstract-Conference.html) and [methodological reply](https://arxiv.org/abs/2401.12631v1), **KWRK-000215/216**, should both be retained. A behavior-changing intervention and a faithful native-mechanism explanation are not the same claim.

The existing [When Does Latent Communication Pay?](https://arxiv.org/abs/2608.04893v2), **KWRK-000103**, is reused rather than duplicated. [Do Latent Channels Actually Communicate?](https://arxiv.org/abs/2607.26773v1), **KWRK-000217**, adds related message-content controls. The final pass resolved the initial primary indexed record for the [Pythia activation-transfer negative result](https://arxiv.org/abs/2606.03280v1), **KWRK-000235**. Later revision authorship and full methods remain a follow-up; the reported post-hoc linear-bridge failure is not a rejection of all C2C methods.

Use sender-private random information generated after weights and mapper selection are frozen. Require the receiver to need it. Compare the correct message with deranged cross-example messages, irrelevant/zero/matched-random messages, receiver-only matched-capacity adapters, and charged text/native-refill controls. Nonsignificance is not equivalence without a predeclared margin and adequate precision.

Only after content-dependent task utility qualifies should repeated-hop geometry or perturbation growth be interpreted. Shared-prompt cache enrichment, source-only continuation, and common latent coordinates are separate communication contracts. Practical fusion can be useful without proving identical internal algorithms.

### Final reference-chain addition: portable semantics and private dialects

The companion [Portable Semantics, Private Dialects](https://arxiv.org/abs/2609.11365), parent [What You Can't See Is What You Learn](https://arxiv.org/abs/2608.20054), and [sixty-society confirmation](https://arxiv.org/abs/2609.17637), **KWRK-000240–242**, supply particularly close interface-transfer controls. Primary indexed abstracts and the [author artifact](https://github.com/tokenosopher/populus-evidence-partitioning) were reviewed; models/checkpoints were not executed.

The companion distinguishes useful within-checkpoint value codes from raw interoperability across independently trained interfaces. Its frozen alignment ladder and inherited-versus-fresh interface comparison motivate explicit negative-transfer controls. The result is bounded to a 17-state near-transfer setting and shared-backbone cells, not arbitrary independently pretrained full models.

Preserve the parent release's formal preregistered floor failure. The later same-author confirmation reports a behavioral pass but unresolved usable-role attribution: marker availability does not demonstrate marker use. Success-conditioned finite packet interventions are not a complete causal mediation result. A later parent title variant, Slot-Selective Evidence Masking, remains a version-specific primary-source follow-up; the reviewed title and limitation are retained rather than asserting a latest-version full-text review.

The [supplement input](prior-art-closure-supplement-2026-10-09.json) records this family and primary-source metadata corrections: ACT's original submission is 29 March 2016; the ODIN proceedings are the 2nd NeurIPS Workshop on Symmetry and Geometry in Neural Representations. Reviewed ACT, Universal Transformer and PonderNet versions are pinned separately from original dates.

## Pass F — spiking and chaotic reconstruction boundaries

The existing [full spiking-spectrum study](https://doi.org/10.1103/PhysRevLett.105.268104), **KWRK-000227**, and [saltation-matrix reference](https://doi.org/10.1109/JPROC.2024.3440211), **KWRK-000228**, should precede interpreting spike/reset Jacobians. Validate event-time and reset composition against finite perturbations. A training surrogate gradient is not automatically the derivative of the actual hybrid trajectory.

[Dambre's information-processing capacity](https://www.nature.com/articles/srep00514), **KWRK-000218**, supports distinct delayed-linear and nonlinear input-history targets. Match leaky/gated/state-space and event-driven controllers on control quality, timing, memory, real skipped arithmetic, and measured energy. Instability itself is not the optimization target.

The final [chaotic-RNN learning paper](https://arxiv.org/abs/2110.07238), **KWRK-000239**, gives an important counterexample to indiscriminate stabilization: forcing stability can destroy the chaotic dynamics one is trying to reconstruct. That setting is not evidence that chaos improves language reasoning. Neither a Lyapunov statistic, perturbational complexity, nor a functional workspace analogy establishes subjective experience.

## Claim-level prior-art gate

Before a custom mechanism is promoted, record its exact model, inputs, intervention, outcome, task distribution, recurrence horizon, hardware, and charged cost. Identify the closest positive predecessor, a serious negative comparator, the primary version/method actually reviewed, an existing implementation or faithful reproduction, and the exact experimental difference.

Search neighboring terminology: task-preserving compression maps to observability and balanced reduction; state survivability to identification and causal message tests; more computation to adaptive depth and equilibrium models. Reproduction of known mechanisms is valuable, but it is not a novelty claim.

There are enough direct precedents to begin inexpensive instrument calibration and strongest-baseline reproduction. A claim that a new method or exact combination is unprecedented remains gated by its narrower source review. This review does not establish complete coverage of every neighboring architecture, hardware setup, or newly posted paper.

## Explicit exclusions and remaining review gaps

The three formerly unresolved leads for Beyond DSA, empirical minimal realization, and Pythia transfer now have primary indexed identities with limited review levels; this is not full-method validation. CtD and several other full manuscripts remain access-limited. The Partial Observation PDF was too large for this fetch path. No unavailable source was silently treated as read.

Two items remain excluded from accepted empirical prior art: the generated Gramian-balanced-neural-SSM application label associated with arXiv:2608.22406, and a generated Lacuna Lyapunov-halting hypothesis page. The former appears to refer to a Stein-equation numerical solver, not the application claim; its primary scope must be resolved before use. Both remain in the intake exclusion record rather than disappearing from the search history.

No model experiment, device benchmark, new runtime, or accepted theorem was produced in this literature intake. Registry validation establishes record integrity, not scientific correctness.
