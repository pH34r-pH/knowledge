# Recurrent dynamics — second literature pass (2026-10-09)

## Scope

Continuation of [the Clark/13-source intake](recurrent-dynamics-intake-2026-10-09.md), deliberately searching beyond the original random-RNN Lyapunov neighborhood. This pass adds 13 public **ExternalWork identities** `KWRK-000188`–`KWRK-000200` to the canonical [works.jsonl](works.jsonl). It does **not** create a new source registry, accepted ExternalClaims, KnowledgeEvidence, a new architecture, or successful experiment claims. [Machine-readable source/identity audit](recurrent-dynamics-second-pass-audit-2026-10-09.json). Bibliographic and method summaries reflect the cited sources; no independent full-paper replication was performed.

## Research pass 1 — transients challenge the stable/chaotic binary

1. **Bondanelli & Ostojic (2020)**, [Coding with transient trajectories in recurrent neural networks](https://doi.org/10.1371/journal.pcbi.1007655), `KWRK-000198`: a stable linear recurrent system with **non-normal** connectivity can selectively amplify input directions before ultimately decaying. The symmetric part of its generator and singular gain of its finite-time propagator are more informative about those excursions than eigenvalue stability alone. This supplies an analytically tractable **positive** task/trajectory control.
2. **Kerg et al. (2019)**, [Non-normal RNN](https://arxiv.org/abs/1905.12080), `KWRK-000197`: Schur-based parameterization combines controlled eigenvalue spectra with transient signal amplification and trained sequential tasks; do not mistake architecture effectiveness for a theorem about arbitrary LM hidden-state dynamics.
3. **Bertschinger, Natschläger & Legenstein (2004)**, [At the Edge of Chaos](https://papers.neurips.cc/paper_files/paper/2004/hash/f8da71e562ff44a2bc7edf3578c593da-Abstract.html), `KWRK-000200`: classical reservoir/time-series result whose computational proxies favor near-critical dynamics for selected temporal tasks.
4. **Haruna & Nakajima (2019)**, [Optimal short-term memory *before* the edge of chaos](https://doi.org/10.1103/PhysRevE.100.062312), `KWRK-000196`: under specified driven-RNN mean-field/small-input assumptions, short-term-memory measures peak in a stable input-driven regime **before** the unforced model's chaos boundary. Together with (3), it falsifies a blanket “maximize chaos or sit exactly at the edge” policy.

### Control proposed
Construct two 2x2 maps with the **same stable eigenvalues**, one normal and one non-normal, and validate their transient singular-value amplification and corresponding output readouts. Then use a tiny driven nonlinear reservoir to distinguish autonomous vs conditional Lyapunov behavior and memory/readout efficacy. Freeze task, step size, horizon, seed, input statistics and energy before fitting interpretations. No unusual network or hardware required; NumPy/SciPy/PyTorch suffice. **Do not call positive short-horizon gain 'asymptotic chaos'.**

## Research pass 2 — input-dependent convergence and architecture-conditioned stability

5. **Labovich (2026)**, [Stability and Generalization in Looped Transformers](https://arxiv.org/abs/2604.15259v2), `KWRK-000189`: fixed-point reachability, **input dependence** and geometry are separate constraints; recall placement and outer normalization affect meaningful convergence in studied architectures and chess/sudoku/prefix-sum tasks. A stable but input-independent fixed point is of little use for solving distinct problems.
6. **Bai, Koltun & Kolter (2021)**, [Stabilizing Equilibrium Models by Jacobian Regularization](https://proceedings.mlr.press/v139/bai21b.html), `KWRK-000194`: [upstream DEQ reference implementation](https://github.com/locuslab/deq) and fixed-point Jacobian regularization for convergence. **Train-time intervention** and implicit differentiation differ from measuring a frozen finite-horizon recurrent core.
7. **Godin (2026)**, [SCORE](https://arxiv.org/abs/2603.10544v1), `KWRK-000190`: a step-size-controlled recurrent residual update in GNN/MLP/nanoGPT. Compare if a minimal Euler/identity-biased control is enough before importing higher-order solvers or novel architectures.
8. **Fu et al. (2026)**, [Fully Looped Transformer](https://arxiv.org/abs/2605.18797v2), `KWRK-000191`: source attributes loop instability to **gradient oscillation and residual explosion** and tests parameter-free all-layer signal routing/attention injection. Training stability is not inference-time task sufficiency, and the tested training budgets must be charged.

### Control proposed
Under matched compute/model size and frozen data, separate `normalization`, `early-state recall`, `history/input injection`, `nonrecurrent coda`, and `step-size/gate` as disjoint ablations; isolate which changes require retraining. Measure (a) fixed-point reachability, (b) input/answer distinguishability, (c) finite-horizon task-relevant gain, (d) NLL/accuracy across recurrent depths, and (e) FLOPs/memory/time. No assumption that fixed-point contraction is desirable for every intermediate reasoning step.

## Research pass 3 — direct positive and negative depth scaling in 2026 LMs

9. **Zhuang et al. (2026)**, [What Makes Recurrence Effective in Looped Language Models?](https://arxiv.org/abs/2609.36636v1), `KWRK-000188`: especially relevant. Tested gains in reasoning beyond trained recurrence depth coincide with **degraded factual/knowledge performance**. Harder items do not monotonically benefit more; they compare nonrecurrent output stages and history-state/time-step-conditioned injection. Implication: **always report reasoning and factual strata separately**, and compare on each requested depth rather than aggregate into one score.
10. **Capps (2026)**, [CART](https://arxiv.org/abs/2606.01495v2), `KWRK-000192`: unusually valuable negative result from experiments on consumer GPUs. A learned stable gate and tied recurrent core still underperform parameter-parity dense baseline; tests changing recurrent depth away from trained R degrade. Paper points to [public experiment scripts/database](https://arxiv.org/abs/2606.01495v2). A stability statistic, resident-byte saving or 3,000-step screening win is **not** an end-to-end quality/cost win.
11. **Chen (2026)**, [Thinking Deeper, Not Longer](https://arxiv.org/abs/2603.21676v2), `KWRK-000193`: frozen output supervision and an identity-biased recurrent block in verifiable graph reachability, nested Boolean logic and relational text. Structured graph signals show a compute-depth threshold; the unstructured text task is less favorable. Strong **synthetic training/eval positive control**, not empirical proof small models universally generalize in open-domain reasoning.
12. **Williams, Russakovsky & Tureci (2026)**, [Rewarding Latent Thought Trajectories](https://proceedings.mlr.press/v306/williams26b.html), `KWRK-000199`: published ICML 2026 intervention distributes RL reward through a looped LM's latent trajectory, with source-reported improvements over outcome-only GRPO on Ouro 1.4B/2.6B math evaluations; [upstream code](https://github.com/jonwill8/RLTT). Training-heavy follow-up **only after** cheap depth/dynamical controls; does not demonstrate a readable or naturally occurring “thought” vocabulary.
13. **Kornblith et al. (2019)**, [CKA and representational similarity](https://proceedings.mlr.press/v97/kornblith19a.html), `KWRK-000195`: basis/rotation-invariant CKA is a better descriptive similarity control than arbitrary coordinate distance, but even CKA/CCA agreement **does not imply** semantic sufficiency, causal handoff or equivalent predictions.

### Control proposed
Use standard frozen held-out probes with `K=1,2,4,8,16` where supported. Split reasoning vs factual vs compositional/OOD tasks. Include fixed-depth controls, an equal-memory conventional LM, untied compute/parameter comparisons where feasible, training-horizon metadata, actual elapsed/energy costs and per-task oracle vs cheap confidence-classifier depth policies. No patch to serving stack until a trained model **demonstrates** operating points with acceptable quality/latency/energy rather than stable-looking internal state.

## Additional cross-model state-transfer lesson

Combining the Kornblith invariance caveat with the existing canonical C2C studies (`KWRK-000036`, `KWRK-000051`, `KWRK-000101`, `KWRK-000103`, `KWRK-000111`) suggests a new **test**, not a result: propagate a declared source-state perturbation through the *learned, actual mapper/injection* and a frozen receiver, and measure output-level retention/error as hops accumulate. Alignment of raw source/receiver coordinates is not well-defined without the adapter. CKA plus output-level controls can characterize, **not prove**, interoperability. Such work is conditional on useful baseline C2C already qualifying.

## Priority recommendations and failure routes

| Sequence | Low-cost test | Winning signal | Stop signal |
| --- | --- | --- | --- |
| A | Stable non-normal 2x2 transient vs normal control | Correct numerical transient and output alignment | Failed analytic/finite-difference checks |
| B | Driven memory vs autonomous criticality | Conditional memory peak is reproducible under fixed signal regime | No reproducible input-memory advantage |
| C | Fixed-point recall/normalization/step-size controls | Input-sensitive stable attractors predict held-out task changes | Stable but functionally collapsed fixed points |
| D | Reasoning vs knowledge recurrence sweeps | Some K improves task quality at charged cost | Factual regressions or no matched-budget improvement |
| E | CKA/task-output handoff controls | Added causal predictor beyond simple drift proxies | Similarity only / no held-out incremental value |
| F | Train-time stabilization or trajectory reward | **Only later**, matched-budget gain after A–E | Computational expense or no qualified benefit |

**Scientific conclusion of this pass:** “maximize stability” and “maximize chaos” are both poorly specified optimization targets. Useful computation may require **stable input-dependent convergence with selectively amplified task information**, and the optimal recurrence horizon can depend on the task and metric. These are experimental hypotheses derived from cited **limited model families**, not a demonstrated general recipe for LLMs.

## Integrity and status
New `ExternalWork` rows are verified **source identities** with source-attributed method summaries. The existing Lyapunov intake, C2C records, and work-history snapshots remain intact. This is not an independent full-text/quote-span verification, model replication, new accepted claim/evidence, or a request to promote a theorem. Exact implementation SHA, numerical environment, dataset/split provenance and any artifact hashes belong to the later experiment runs.
