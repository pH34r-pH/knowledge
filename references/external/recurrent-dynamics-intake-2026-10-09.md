# Recurrent-state stability, Lyapunov methods and functional dynamics — public research intake (2026-10-09)

## Scope and status

This is a **bounded source-identity and methodological comparison intake**, not an independent replication or a promotion of external claims into the Knowledge `ExternalClaim`/`KnowledgeEvidence` registry. The canonical identities for 13 newly resolved papers are `KWRK-000175` through `KWRK-000187` in [works.jsonl](works.jsonl); existing C2C/looping/latent-transfer works remain unchanged. The [machine-readable intake audit](recurrent-dynamics-intake-audit-2026-10-09.json) identifies what was checked and left open.

**Central distinction:** random autonomous RNN Lyapunov theory, trained/input-driven RNN Lyapunov spectra, finite-horizon Jacobian singular gains in looped LMs, static activation-rank statistics, and behavioral task sufficiency are **five different objects**. Published findings in one do not transfer automatically to the others.

## Research pass A — establish the numerical reference

- **Clark (2026)**, [Lyapunov spectrum of random neural networks](https://arxiv.org/abs/2610.12426v1), `KWRK-000175`. Derives a large-network spectral distribution for a random asymmetric nonlinear autonomous RNN using a finite-network response identity and cavity method. [Author code/data](https://github.com/davidclark1/rnn-lyapunov). Reproduce low-cost cases first; record the assumptions behind large-N and any limit exchange. This is **not** evidence that increasing chaos or recurrent depth improves reasoning.
- **Engelken, Wolf & Abbott (2023)**, [Lyapunov spectra of chaotic recurrent neural networks](https://doi.org/10.1103/PhysRevResearch.5.043044), `KWRK-000176`. The most directly overlapping published full-spectrum numerical study. Includes input-drive and trained-RNN analyses and convergence controls; unlike Clark's new result it does **not** supply the same claimed exact large-N self-consistent analytic law. Reuse its numerical control ladder and compare conditions, not headline conclusions.
- **Vogt, Puelma Touzel, Shlizerman & Lajoie (2022)**, [On Lyapunov Exponents for RNNs](https://doi.org/10.3389/fams.2022.818799), `KWRK-000177`. Implements spectrum computation for **non-autonomous/data-driven** RNNs, illustrated on character prediction and motion capture. Reference for input-conditioned QR reorthogonalization and averaging across trials.

**Proposed minimal reference matrix:** stable/near-critical/unstable random tanh RNNs; small N/large N; increasing burn-in and horizon; seed and precision ladder; analytic/autodiff/finite-difference tangent checks; compare QR long-time exponents with finite-horizon singular-value growth **without conflating them**. Calculate static participation-ratio rank and Kaplan–Yorke dimension separately. No new solver/runtime until existing libraries are demonstrably insufficient.

## Research pass B — determine when internal dynamics preserve useful computation

- **Mastrogiuseppe & Ostojic (2018)**, [Low-rank recurrent networks](https://doi.org/10.1016/j.neuron.2018.07.003), `KWRK-000181`. Random-plus-low-rank connectivity provides a controlled setting where structure is related to low-dimensional task dynamics. [Figure reproduction code](https://github.com/fmastrogiuseppe/LowRank).
- **Pollock & Jazayeri (2020)**, [Engineering task-relevant manifolds](https://doi.org/10.1371/journal.pcbi.1008128), `KWRK-000182`. Constructs task-specified dynamics over a ring manifold and constrains their local Jacobians. [EMPJ notebook](https://github.com/elipollock/EMPJ) gives a good **known-positive** synthetic functional-subspace baseline.
- **Sussillo & Barak (2013)**, [Opening the Black Box](https://doi.org/10.1162/NECO_a_00409), `KWRK-000183`. Standard fixed-/slow-point optimization and local linearization method. Gate expensive slow-point search behind cheaper finite-horizon perturbation evidence.
- **Clark et al. (2026)**, [Structure, disorder, and dynamics in task-trained recurrent neural circuits](https://doi.org/10.64898/2026.03.02.708943), `KWRK-000184` (preprint). Same Clark, different and crucially more task-oriented model: random heterogeneity and task-related learned structure coexist, with experiments involving temporal generalization and low-dimensional responses. [Reproduction code](https://github.com/davidclark1/RNN-Learning-Theory). Do not treat either Clark work as showing a general trained-Transformer result.

**Proposed matrix:** frozen recurrent models; predeclared depth horizon; task-output Jacobian vs matched-random/null subspaces; finite-time direction growth; held-out NLL/accuracy and logit sensitivity; joint vs per-example active plane; static rank, common-mode, norm and depth-only predictors. A compressed manifold is not necessarily task-sufficient; subspace agreement alone is not causal behavioral evidence.

## Research pass C — explain recurrent-depth benefit and collapse

- **Yang et al. (2026)**, [STARS — Stabilizing Recurrent Dynamics for Test-Time Scalable Latent Reasoning](https://proceedings.mlr.press/v306/yang26t.html), `KWRK-000179`. This is our strongest **interventional** template. Training-time Jacobian spectral-radius regularization and random loop sampling are reported to reduce deeper-loop collapse. [Author code](https://github.com/njuyxw/STARS). It tests a mechanism Clark does not: modifying recurrent stability and measuring task consequences. Unlike offline Lyapunov diagnosis, its intervention alters training and requires a properly charged training budget.
- **Chen, Pennington & Schoenholz (2018)**, [Dynamical isometry and RNN mean-field theory](https://proceedings.mlr.press/v80/chen18i.html), `KWRK-000185`. Controls forward signal/gradient propagation and gating at initialization, useful to distinguish desirable Jacobian singular-value distributions from positive asymptotic Lyapunov exponents.
- **Can, Krishnamurthy & Schwab (2020)**, [Gating creates slow modes in GRUs/LSTMs](https://proceedings.mlr.press/v107/can20a.html), `KWRK-000186`. Good explicit time-constant/gate control for recurrent-control or spiking-controller proposals; slow/long-lived state is not inherently useful reasoning.
- **Lai et al. (2026)**, [Fractal basins trap latent reasoning](https://arxiv.org/abs/2609.04963), `KWRK-000180` (preprint). Interesting transient-dynamics analysis of reasoning traces, but do not equate observable token-level paths with internal-state asymptotic Lyapunov spectra or accept a necessary-hardness explanation without stronger controls.
- **Vogt, Zheng & Shlizerman (2024)**, [Lyapunov-guided representation of RNN performance](https://doi.org/10.1007/s00521-024-09824-6), `KWRK-000178`. [AeLLE code](https://github.com/shlizee/LyapunovAutoEncode) learns features of spectra predictive of trained RNN performance on the investigated setups; use as a *stronger predictive benchmark* only after simpler fixed-depth, static-rank and confidence features. The publisher issued a 2024 correction replacing an incorrect supplementary file; use the corrected material.

**Proposed crossed design:** same recurrent checkpoints/tasks, loop count K and any existing boundary/normalization/guidance ablation; offline spectral features measured at fixed calibrated depths; held-out accuracy, NLL, sensitivity, latency/energy and predictor regret. Favor feature ablation over heavy new training. STARS training experiments are a **separate, later, matched-budget causal test** if frozen-model diagnostics are genuinely predictive.

## Research pass D — cross-model state translation and repeat handoff

The Knowledge registry **already contains** [Cache-to-Cache](https://arxiv.org/abs/2510.03215) (`KWRK-000036`), [Dual-Cache XKV](https://arxiv.org/abs/2608.20617) (`KWRK-000051`), [Latent Cache Flow](https://arxiv.org/abs/2605.22863) (`KWRK-000055`), [Mixture-of-Translators](https://arxiv.org/abs/2607.28979) (`KWRK-000111`), [CacheBridge](https://arxiv.org/abs/2609.00891) (`KWRK-000101`), and the causally motivated [When Does Latent Communication Pay?](https://arxiv.org/abs/2608.04893) (`KWRK-000103`). Do not make duplicate Work identities for these papers.

The new hypothesis is narrower: do finite-horizon perturbation and task-aligned directional measures predict loss across **actual** learned mapper + injection + receiver paths better than ordinary hop-count, output or exact-state drift baselines? Nonstationary cross-architecture mappings are not Clark's iid autonomous RNN. Preserve shared-prompt KV cache enrichment vs true independent source-only handoff as distinct protocols; charge mapper training, simultaneous residency, cache copies and prefill cost. **Do not** gate the existing tiny dense C2C reference work on unproven spectral diagnostics.

## Research pass E — spiking/affective controllers and conceptual boundary

- **Can et al. (2020)** supplies conventional GRU/LSTM slow-mode controls; first compare leaky, gated, state-space and event-driven controllers at matched latency, memory and task outcome, before attempting spiking-LLM conversion.
- **Mastrovito et al. (2024)**, [Transition to chaos separates learning regimes and relates to measure of consciousness in recurrent neural networks](https://doi.org/10.1101/2024.05.15.594236), `KWRK-000187` (preprint), tests chaos/learning and a perturbational-complexity *proxy* in particular trained RNNs. The proxy is not machine phenomenology, feelings or evidence that trained models are conscious. Use at most for perturbation-protocol comparison.

## Priority by reusable method and evidential value

1. **Cheap and immediate:** Clark reference code + Engelken numerical/convergence controls + Vogt nonautonomous QR estimator.
2. **High value without model retraining:** Pollock known-ground-truth manifolds; frozen task-sensitive Jacobian probes; Sussillo slow-point gate.
3. **Direct language-model bridge:** STARS recurrence-depth collapse controls; compare with already planned guided/unguided looped LM depth sweeps.
4. **Conditional:** spectral performance predictor against depth/confidence/static-rank controls.
5. **Later:** repeated heterogeneous C2C perturbation study, only after functional handoff works.
6. **Independent exploratory:** event-driven temporal controller vs leaky/gated/SSM baselines. No consciousness inference.

## Explicit unresolved questions

- No new paper in this intake independently demonstrates that an asymptotic Lyapunov metric identifies productive hidden reasoning in large language models.
- No reviewed source establishes a practical online full-spectrum estimator inside an 8 GB inference vessel that improves scheduler utility after overhead.
- Existing C2C papers examine translation utility and some trajectory drift; they do not certify the new cross-model dynamical-invariant hypothesis.
- Not every linked author implementation has been executed here; source identities and described methods have been inspected, **not reproduced**.
- No PDF files, code, external theorem imports, accepted `ExternalClaim`, `KnowledgeEvidence`, or corpus article were created by this intake. These are candidate methods requiring exact-source pinning and independent validation before promotion.

## Publication and provenance convention

Peer-reviewed publication, arXiv/bioRxiv preprint, and computational implementation are recorded separately. Versioned preprint IDs are not mistaken for a publication date or model evidence. No private experiment outcomes or unpublished repository details enter this public intake. The original external-source claims belong to their authors; the proposed experiment designs above are hypotheses and are not the results of this review.
