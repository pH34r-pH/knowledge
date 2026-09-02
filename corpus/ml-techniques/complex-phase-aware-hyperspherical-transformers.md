---
title: Complex, phase-aware, and hyperspherical Transformer computation
pillar: ml-techniques
method: deep-research + storm
date: 2026-09-02
sources: 11
confidence: medium
---

## What it is

“Geometric Transformer” is not one mechanism. At least four separable design axes are often grouped under that label:

1. **Positional rotation:** keep the model real-valued, but rotate pairs of query and key coordinates so attention scores encode relative position. RoPE is the canonical example [5].
2. **Complex-valued computation:** carry real and imaginary components through projections, attention, normalization, activations, and value aggregation. Complex Transformer, CAMEL, the Eilers–Jiang building blocks, and the Phase-Coherent Transformer make different choices at each of those interfaces [1][2][3][4].
3. **Hyperspherical state constraints:** constrain some or all learned vectors to fixed norm, so direction carries the representation and the update rule must return states to the sphere. nGPT and Hyper-SET are examples, but they do not implement the same update or depth semantics [7][8].
4. **Shared or implicit depth:** apply one transformation repeatedly, optionally with adaptive halting, or solve directly for its fixed point. Universal Transformers, ALBERT, and Deep Equilibrium Models occupy different points on this axis [9][10][11].

These axes can interact, but none implies another. RoPE uses two-dimensional rotation algebra without making the network complex-valued [5]. nGPT normalizes vectors throughout its Transformer, whereas Hyper-SET explicitly adds shared recurrent depth [7][8]. ALBERT shares parameters across a fixed stack without requiring its hidden states to converge [10]. Hyper-SET combines hyperspherical constraints with shared recurrent depth and an energy-derived operator, so its package result cannot identify which ingredient matters [8].

The durable design rule is:

> Name the state space, score map, normalization, update rule, and depth semantics separately. Then test the proposed combination against controls that change one axis at a time.

## When to reach for it

Consider **complex-valued blocks** when amplitude and phase are part of the input’s native semantics—for example, Fourier-domain audio or in-phase/quadrature radio measurements—and the intended operator should respect their coupling. The early Complex Transformer, CAMEL, and Eilers–Jiang experiments are concentrated in music and signal-recognition settings, which makes them relevant precedents but not general language-model evidence [1][2][3].

Consider **rotary phase at a narrow interface** when the need is relative positional structure rather than a complex-valued model. RoPE rotates projected queries and keys while the rest of the Transformer can remain real [5]. Selective RoPE is narrower still: it makes those rotations input-dependent inside gated linear or recurrent attention and composes them with an existing decay mechanism [6].

Consider **hyperspherical constraints** when scale variation is a suspected optimization nuisance or cosine-like geometry is the intended representation. nGPT places embeddings, hidden states, and vectors forming attention and MLP matrices on a unit hypersphere [7]. Hyper-SET instead derives token dynamics, symmetric attention, feed-forward updates, and RMS normalization from a constrained energy objective, while also tying parameters across recurrent depth [8].

Consider **shared or implicit depth** when the hypothesis is iterative refinement, parameter reuse, variable computation, or activation-memory reduction. Universal Transformers recur over revisions of all token positions in parallel and can halt per position [9]. ALBERT uses sharing primarily for parameter efficiency [10]. DEQs replace a finite unroll with a root solve for an equilibrium and use implicit differentiation [11].

Do not reach for the full package when the required inductive bias is local. A positional problem does not by itself justify complex activations and normalization; a parameter-budget problem does not establish a need for recurrence; and unit-normalized queries and keys do not imply that all hidden states should live on a sphere.

## How the mechanisms differ

### Complex state still needs real decisions

A complex vector can be stored as `z = a + ib`, and complex linear operations can be implemented with coupled real operations. The first Complex Transformer makes this explicit: it represents real and imaginary components separately, expands complex query–key–value products into real terms, and computes eight real multi-head-attention terms. Its attention subroutine uses min–max normalization rather than softmax [1]. This is a complex-valued computation graph implemented with real primitives, not an escape from real hardware.

The harder boundary is the attention weight. A standard softmax needs ordered real scores, but a complex similarity is not naturally ordered. CAMEL states the mathematical obstruction directly: a nonconstant map from `C` to `R` is non-analytic, so its complex attention uses complex-gradient rules and defines a generalized softmax as an ordinary real softmax applied after a chosen map such as magnitude, real part, or imaginary part [2]. That choice is part of the model’s inductive bias; “complex attention” alone does not specify it.

Eilers and Jiang turn this ambiguity into an explicit design space. They begin with the Hermitian dot product and note that its real part is invariant to jointly rotating query and key. They evaluate score variants based on the real part, magnitude, phase-preserving magnitude, and separate real/imaginary components. They also define complex layer normalization through the joint `2×2` covariance of real and imaginary parts rather than normalizing the two channels independently [3]. The paper therefore supplies building blocks, not one uniquely canonical complex Transformer.

The 2026 Phase-Coherent Transformer (PCT) changes the score-to-weight rule again. For complex queries and keys, it L2-normalizes each vector, takes the real part of their complex cosine similarity, and applies an element-wise sigmoid gate:

```text
q̄_i = q_i / ||q_i||₂
k̄_j = k_j / ||k_j||₂
s_ij = Re⟨q̄_i, k̄_j⟩ · √d
α_ij = sigmoid(s_ij + b)
out_i = W_o Σ_j α_ij v_j
```

Because the gate is applied independently, the weights in a row do not compete for a unit softmax mass. The paper compares this cell with real and complex softmax and screening variants under its parameter-fair setup, and reports no accuracy collapse over its tested depth range [4]. Those are author-reported results from a recent single-author preprint, not yet a general verdict on non-competing complex attention.

### Positional phase is a smaller commitment

RoPE partitions an even-dimensional projected query/key space into two-dimensional subspaces. At position `m`, each pair is multiplied by a rotation matrix with angle `mθ`. The dot product between a query at `m` and a key at `n` then contains the relative rotation `R(n−m)`, while the rotated vectors separately encode their absolute positions [5]. The complex-number notation is convenient, but the implementation remains real-valued block rotations.

Selective RoPE makes the rotation learned and input-dependent. Its authors analyze gated linear attention as a recurrence and argue that rotation and decay play complementary roles: rotation carries positional phase, while decay controls how past key–value associations persist. In their formulation, a rotation-only finite-state recurrence behaves like a spectral analyzer and suffers spectral leakage; the existing forget gate supplies the decay term. The proposed transition can still use ordinary RoPE-style query/key kernels rather than requiring a fully complex network [6]. This is evidence about the paper’s linear/recurrent constructions, not proof that every attention mechanism needs the same rotation-plus-decay decomposition.

### A hypersphere changes both representation and update

nGPT normalizes embeddings, hidden states, and vectors forming attention and MLP matrices to unit norm. Each attention or MLP block proposes a displacement, and the hidden-state update is normalized back to the sphere with learned component-wise step sizes [7]. The paper reports needing 4–20 times fewer optimization steps to reach the same accuracy in its evaluated language-model configurations, depending on sequence length [7]. That result bundles the spherical constraint with a particular update, normalization placement, parameterization, and training setup; it should not be paraphrased as a universal speedup from unit norms.

Hyper-SET starts from a different object: a constrained energy over token representations. One term promotes distributional spread in projected low-dimensional hyperspheres; another promotes alignment with learned directions in the ambient space. Discretizing its energy dynamics yields symmetric attention, a feed-forward update, skip connections, and RMS normalization. The same parameter set is reused across iterations, making the model recurrent in depth; reported tasks include Sudoku, image classification, and masked-image modeling [8]. Its evidence is therefore about a combined energy–geometry–operator–sharing design, not a clean comparison of sphere versus Euclidean state.

### Sharing weights is not the same as reaching equilibrium

Universal Transformers apply self-attention and a shared transition to every sequence position in parallel, then repeat the block over depth. The recurrence revises representations rather than stepping left-to-right through tokens. A fixed number of revisions can be used, or adaptive computation time can halt each position separately [9].

ALBERT also shares parameters across layers, but its motivation and execution are different. It combines factorized token embeddings with cross-layer parameter sharing to reduce parameter growth, while still evaluating a finite stack. The paper reports that its layer-to-layer embeddings oscillate rather than converge to a fixed point [10]. Parameter sharing is therefore a necessary control for parameter count, not evidence that the model performs equilibrium computation.

A Deep Equilibrium Model directly seeks a state `z*` satisfying `z* = fθ(z*; x)` with a root-finding method. It then differentiates implicitly through that fixed point instead of storing and backpropagating through every solver iteration. The construction is equivalent to the limit of an infinite-depth weight-tied network under the paper’s stability assumptions and has activation-memory cost independent of effective depth [11]. A DEQ is not merely a Universal Transformer with “more layers”: solver convergence, stopping tolerance, Jacobian behavior, and implicit gradients are part of the method.

## Trade-offs: three defensible perspectives

### Phase-first

The phase-first view starts from data whose amplitude and phase have physical or mathematical meaning. A complex substrate makes their coupling explicit, and Hermitian products offer joint-rotation invariance that independent real channels do not automatically express [3]. Complex Transformer, CAMEL, and PCT show several viable ways to carry complex values through attention [1][2][4].

Its weak point is the real-decision bottleneck. Attention weights, gates, losses, and many activations eventually require a choice about how complex state controls a real magnitude or decision. Magnitude, real-part, min–max, softmax, and sigmoid-gate choices discard or preserve different information [1][2][3][4]. A model is not “more phase-aware” merely because its tensors use a complex dtype.

### Geometry-first

The geometry-first view treats scale as a nuisance and direction as the useful state. nGPT makes this commitment throughout its Transformer, while Hyper-SET uses hyperspherical constraints inside an explicit energy-minimization story [7][8]. Bounded dot products and explicit renormalization can make state evolution easier to inspect.

Its weak point is causal attribution. nGPT and Hyper-SET alter more than radius: their updates, normalization, attention or feed-forward structure, and—in Hyper-SET—depth sharing also change [7][8]. A spherical package result is not evidence that removing radius alone caused the outcome.

### Control-first

The control-first view treats complex arithmetic, positional rotation, score normalization, radius constraints, weight sharing, step count, and equilibrium solving as independent experimental factors. RoPE demonstrates why this separation matters: useful rotation algebra can live only in query/key position encoding [5]. ALBERT shows that sharing need not imply convergence [10]. DEQ shows that equilibrium requires a solver and implicit-gradient semantics beyond tied weights [11].

This view gives up a single “geometric Transformer” leaderboard. In return, it produces claims that survive substitution: which benefit comes from the state space, which from the operator, which from compute allocation, and which only from their interaction.

## A matched-control protocol

Start with the smallest factorial design that can identify the intended mechanism. The complete Cartesian product may be too expensive, but every claimed causal axis needs at least one off-diagonal control.

| Axis | Control | Proposed condition | What the comparison identifies |
|---|---|---|---|
| State type | paired real channels | native complex operations | effect of coupled complex algebra |
| Position | fixed or no rotation | fixed RoPE or selective rotation | positional-phase contribution |
| Score map | softmax or matched real gate | complex-to-real score/gate | competition and score-map effect |
| Radius | unconstrained state | matched unit-sphere state | effect of radial degrees of freedom |
| Parameters over depth | untied | shared | parameter reuse versus added capacity |
| Computation depth | fixed unroll | adaptive steps or equilibrium solve | extra/conditional/implicit computation |

For each cell, report:

- real scalar parameter count, not just the number of complex tensors;
- training FLOPs, inference FLOPs, activation memory, and wall time;
- number of explicit refinement steps or root-function evaluations;
- state norms, query/key norms, and phase distributions where they are load-bearing;
- score entropy or gate activation statistics;
- solver residual and convergence failures for equilibrium models;
- results on both phase-native data and a matched task where phase should offer no special advantage;
- seeds, uncertainty, and the exact arXiv or software version behind any reproduced claim.

One useful progression is: real baseline → paired-real implementation → native complex projection with the same real score map → alternative score map → optional spherical constraint. For depth, hold the block fixed and compare untied finite depth, tied finite depth, adaptive finite depth, and equilibrium solving. Do not change both tables at once unless the interaction is the hypothesis.

## Common failure modes

**Treating RoPE as evidence for a fully complex model.** RoPE establishes a useful positional rotation inside projected queries and keys [5]. It does not validate complex activations, complex normalization, or complex value paths.

**Calling two real channels a sufficient control without matching operations.** Complex multiplication couples the channels in a particular way. A paired-real baseline must match parameter count and expose whether that coupling, rather than doubled width, matters [1][3].

**Hiding the `C → R` map.** “Complex softmax” is incomplete unless it states whether scores use magnitude, real part, imaginary part, or another function [2][3].

**Equating query/key normalization with a spherical network.** PCT L2-normalizes queries and keys for its cosine gate [4]. nGPT constrains embeddings, hidden states, and matrix vectors throughout the model [7]. These are different interventions.

**Equating sharing with recurrence or equilibrium.** ALBERT shares across a finite stack [10]; Universal Transformer explicitly recurs over depth and may halt dynamically [9]; DEQ solves a fixed-point equation [11]. They require separate compute and convergence accounting.

**Attributing a bundled result to geometry.** Hyper-SET combines energy objectives, symmetric modules, RMS normalization, shared recurrent depth, and hyperspherical constraints [8]. nGPT also changes its hidden-state update and parameter normalization [7]. Keep package claims at package scope.

**Exporting signal-domain evidence to language.** MusicNet, RadioML, and private IQ results establish feasibility in their evaluated domains, not general language-model superiority [1][2][3]. PCT broadens the tested task mix, but remains a recent author report [4].

## In practice: a decision sequence

Suppose a team wants a phase-aware recurrent language model.

1. **Specify the phase.** Is it physical phase, positional phase, or a learned binding coordinate? If only position is intended, begin with RoPE or a selective rotary control rather than a fully complex stack [5][6].
2. **Specify the real decision.** Write down the exact `C → R` score function and whether tokens compete through row normalization [2][3][4].
3. **Choose radius semantics independently.** Compare free-radius and unit-sphere states without changing depth sharing. If only queries and keys are normalized, say so.
4. **Choose depth semantics independently.** Compare an untied stack, a tied finite unroll, adaptive finite steps, and a fixed-point solve as separate systems [9][10][11].
5. **Charge the package honestly.** Count real parameters, solver or iteration work, memory, and kernel maturity—not just nominal layer count.
6. **Test the claimed boundary.** Include at least one phase-native workload and one negative control where phase should not help. Include an out-of-training-depth or convergence stress test only if variable or implicit depth is claimed.
7. **Narrow the conclusion.** A successful selective-rotation ablation supports selective rotation. A successful complex-plus-sphere-plus-recurrence package supports that package until the off-diagonal controls say more.

The point is not to insist on Euclidean, real-valued, fixed-depth Transformers. It is to make each departure legible enough that geometry becomes a testable mechanism rather than a label.

## Further reading

1. Muqiao Yang, Martin Q. Ma, Dongyu Li, Yao-Hung Hubert Tsai, and Ruslan Salakhutdinov — *Complex Transformer: A Framework for Modeling Complex-Valued Sequence* (2019 preprint; v2 revised 2021), arXiv:1910.10202v2 — https://arxiv.org/abs/1910.10202v2
2. Yihong Dong, Ying Peng, Muqiao Yang, Songtao Lu, and Qingjiang Shi — *Signal Transformer: Complex-valued Attention and Meta-Learning for Signal Recognition* (2021 preprint), arXiv:2106.04392v2 — https://arxiv.org/abs/2106.04392v2
3. Florian Eilers and Xiaoyi Jiang — *Building Blocks for a Complex-Valued Transformer Architecture* (2023 preprint), arXiv:2306.09827v1 — https://arxiv.org/abs/2306.09827v1
4. Leona Hioki — *Complex-Valued Phase-Coherent Transformer* (2026 preprint), arXiv:2605.10123v2 — https://arxiv.org/abs/2605.10123v2
5. Jianlin Su, Yu Lu, Shengfeng Pan, Ahmed Murtadha, Bo Wen, and Yunfeng Liu — *RoFormer: Enhanced Transformer with Rotary Position Embedding* (arXiv preprint; first posted 2021, v5 updated 2023), arXiv:2104.09864v5 — https://arxiv.org/abs/2104.09864v5
6. Sajad Movahedi, Timur Carstensen, Arshia Afzal, Frank Hutter, Antonio Orvieto, and Volkan Cevher — *Selective Rotary Position Embedding* (ICLR 2026), arXiv:2511.17388v3 — https://arxiv.org/abs/2511.17388v3
7. Ilya Loshchilov, Cheng-Ping Hsieh, Simeng Sun, and Boris Ginsburg — *nGPT: Normalized Transformer with Representation Learning on the Hypersphere* (ICLR 2025), arXiv:2410.01131v2 — https://arxiv.org/abs/2410.01131v2
8. Yunzhe Hu, Difan Zou, and Dong Xu — *Hyper-SET: Designing Transformers via Hyperspherical Energy Minimization* (2025 preprint), arXiv:2502.11646v3 — https://arxiv.org/abs/2502.11646v3
9. Mostafa Dehghani, Stephan Gouws, Oriol Vinyals, Jakob Uszkoreit, and Łukasz Kaiser — *Universal Transformers* (ICLR 2019), arXiv:1807.03819v3 — https://arxiv.org/abs/1807.03819v3
10. Zhenzhong Lan, Mingda Chen, Sebastian Goodman, Kevin Gimpel, Piyush Sharma, and Radu Soricut — *ALBERT: A Lite BERT for Self-supervised Learning of Language Representations* (ICLR 2020), arXiv:1909.11942v6 — https://arxiv.org/abs/1909.11942v6
11. Shaojie Bai, J. Zico Kolter, and Vladlen Koltun — *Deep Equilibrium Models* (NeurIPS 2019), arXiv:1909.01377v2 — https://arxiv.org/abs/1909.01377v2
