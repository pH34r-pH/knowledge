---
title: Representation–architecture co-design for language models
pillar: ml-techniques
method: deep-research + storm
date: 2026-09-02
sources: 8
confidence: medium
---

## What it is

A language model does not receive language directly. A **representation** maps text into model-visible units and coordinates; an **architecture** decides how information and compute move across those units. Changing one often changes the problem faced by the other.

This coupling is easiest to see in tokenization. Replacing learned subwords with bytes or characters removes a corpus-learned subword vocabulary and its external segmentation step, but it also makes sequences longer. A standard dense-attention stack now sees more positions, so the experiment has changed both the input representation and the cost profile. The successful token-free systems in the literature respond in different ways: CANINE downsamples characters before its deep Transformer stack [1]; Charformer learns latent subword blocks inside the model [3]; MEGABYTE splits byte sequences between local and global models [4]; and BLT makes patch length depend on next-byte entropy [5]. These are not four implementations of the same representation-only swap. Each is a representation–operator package.

The coupling is not absolute. ByT5 is the important counterexample: it processes bytes with a largely standard Transformer and reports competitive results after minimal architectural modification, while explicitly measuring parameters, training FLOPs, and inference speed [2]. The durable claim is therefore not “a new representation always requires a new architecture.” It is narrower:

> A representation claim is incomplete until it states which operator consumes the representation, how the pairing allocates compute, and—when both axes change—which controls distinguish representation, operator, and interaction effects.

This framing also applies beyond token boundaries. RoPE inserts rotation algebra into attention to couple absolute position with relative-position interactions [6]. nGPT constrains embeddings, hidden states, and weight vectors to a unit hypersphere, so normalization and layer updates become part of the state-transition rule [7]. Hrrformer recasts query–key–value matching through holographic binding and unbinding rather than treating HRR vectors as ordinary features passed to unchanged attention [8]. These works alter different interfaces and should not be collapsed into one “geometric model” category, but each shows why coordinates and operators must be specified together.

## When to reach for it

Use a co-design analysis when a proposal changes any model-facing interface:

- token or patch granularity;
- positional, complex, polar, hyperspherical, or hyperbolic coordinates;
- a binding or composition algebra;
- a latent bottleneck or other compression boundary;
- the placement of local versus global compute;
- numerical representation in a way that changes faithful arithmetic.

It is especially useful when an apparent quality gain could be caused by extra depth, a larger effective context, different parameter placement, altered FLOPs, or a new optimization path. In those cases, a one-axis ablation answers the wrong question.

Do not force the framing onto changes that leave the model-visible tensor and operator contract unchanged. Replacing one equivalent tokenizer implementation with another for compatibility, or optimizing a kernel without changing its mathematical operator, can usually be evaluated on its own axis. Co-design is a demand for identifiable causes, not a license to make every experiment combinatorial.

## How the coupling works

### Granularity changes both information and cost

A subword tokenizer performs two jobs before learning begins: it selects boundaries and compresses character sequences into fewer positions. Bytes and Unicode characters avoid a corpus-learned subword lexicon and externally imposed subword boundaries, but they still use finite symbol inventories and expose longer sequences. ByT5 describes exactly this tension: byte models remove a preprocessing dependency and gain robustness to spelling-sensitive or noisy inputs, while longer sequences change training and inference cost [2].

The architecture can respond at several points:

1. **Compress before the expensive stack.** CANINE embeds Unicode characters, applies local processing and strided convolution, then sends a shorter sequence through the deep Transformer stack; its full sequence output is reconstructed afterward [1]. The character interface and the downsample–encode–upsample path are one design.
2. **Learn soft boundaries.** Charformer's GBST module enumerates candidate contiguous blocks and learns position-wise scores, producing latent subwords that are then downsampled for deeper processing [3]. It removes an external hard tokenizer, not the inductive bias that nearby characters should sometimes be grouped.
3. **Separate local from global modeling.** MEGABYTE uses fixed patches, a local model within each patch, and a global model between patches. The split reduces the sequence length seen by global attention and changes where feed-forward capacity can be spent [4].
4. **Allocate compute by predictability.** BLT forms dynamically sized byte patches using next-byte entropy: predictable spans can be longer, while difficult spans receive finer-grained patches and therefore more model capacity [5]. Here segmentation is explicitly a compute-allocation policy.

ByT5 prevents overgeneralizing from this progression. It shows that useful byte-level modeling does not logically require learned segmentation or a multiscale operator [2]. The right question is empirical: under the target budget and workload, does an adapted operator add value beyond the representation itself?

### Coordinates define which operations are cheap and meaningful

Changing coordinates can make a particular relation native to the operator.

RoPE divides the projected query/key space into two-dimensional subspaces and applies position-dependent rotations. In the attention inner product, the resulting interaction depends on relative position while each vector also carries its absolute position [6]. This is a limited but important precedent: complex phase algebra can be useful at one interface without making the entire network complex-valued.

nGPT makes a stronger geometric commitment. It normalizes embeddings, hidden states, and the vectors forming attention and MLP matrices to unit norm, and describes each layer as a displacement along a hyperspherical representation space [7]. Its reported training-step reductions are evidence for the evaluated configurations, not proof that “hyperspherical is faster” independent of optimizer, normalization rule, or sequence length. A fair control must separate the unit-sphere state constraint from the other update and parameterization changes that implement it.

Hrrformer makes an algebraic commitment instead. It uses holographic reduced-representation binding, superposition, unbinding, and a cleanup-like similarity step to reproduce the high-level query–key–value goal. The paper derives per-layer time `O(T H log H)` and space `O(T H)`, rather than standard attention's quadratic dependence on sequence length [8]. That is evidence that a representation-specific operator can change asymptotics; its malware and Long Range Arena results do not establish a universal replacement for attention or for autoregressive language modeling.

### The experiment is a crossed design

Let `R0` be the established representation, `R1` the proposed one, `O0` the established operator, and `O1` the adapted operator. When a proposal changes both representation and operator, this article recommends a 2×2 causal-audit grid:

| | Established operator `O0` | Adapted operator `O1` |
|---|---|---|
| Established representation `R0` | deployment baseline | architecture-only control |
| Proposed representation `R1` | representation-only control | co-designed system |

For a metric `M`, the interaction can be summarized as

```text
I = [M(R1,O1) - M(R0,O1)] - [M(R1,O0) - M(R0,O0)]
```

This is not a universal score; it is a bookkeeping device. A large `I` says the adapted operator helps the proposed representation more than it helps the established one under this experiment. It does not say why, and it is meaningless if the four cells do not share a defensible budget.

At minimum, match or report:

- trainable and total parameters, including vocabulary or patch modules;
- training examples, raw bytes, optimizer steps, and total training FLOPs;
- inference prefill/decode work, memory, and wall-clock throughput;
- raw-context coverage, not merely the number of model-visible units;
- output contract and evaluation granularity;
- seeds and uncertainty;
- robustness slices that the representation is supposed to improve.

ByT5 is instructive because it moves parameters associated with the input embedding and output softmax into Transformer layers. The paper notes that an input embedding lookup is essentially free in FLOP accounting, so equal parameter count does not imply equal FLOPs after this reallocation [2]. BLT's FLOP-controlled scaling study likewise treats compute as a first-class comparison axis rather than assuming equal model size is sufficient [5].

## Trade-offs: three defensible perspectives

### Representation-first

The representation-first case is that fixed subword vocabularies bake language- and corpus-specific choices into preprocessing. Character and byte interfaces avoid out-of-vocabulary behavior, can preserve spelling-level information, and let grouping be learned downstream. CANINE, ByT5, and Charformer each motivate their designs from some part of this case [1][2][3].

Its blind spot is cost displacement. Removing a tokenizer does not eliminate its computational burden; depending on the model, the burden may appear as longer sequences, or be mitigated by downsampling, patch construction, local encoders, or deeper stacks. “Token-free” describes the external interface and does not by itself imply the absence of internal aggregation.

### Architecture-first

The architecture-first case is that long fine-grained sequences are primarily a compute-routing problem. MEGABYTE and BLT make the global operator work on patches while keeping local byte processing near the input or output [4][5]. Charformer similarly learns and downsamples blocks before its deep stack [3]. From this view, the important innovation is where global capacity is spent.

Its blind spot is semantic leakage from the grouping rule. Fixed patch width, learned block scores, or entropy thresholds each impose a boundary policy. Those policies may improve efficiency while losing, shifting, or obscuring the very representation advantage being claimed.

### Control-first

The control-first case asks a narrower causal question: when both `R` and `O` change, a package-only comparison cannot separate a representation effect, an operator effect, and their interaction. The 2×2 grid above is this article's recommended audit for that question. ByT5 shows that a minimal-change byte Transformer is a real baseline, not a straw model [2]. CANINE, Charformer, MEGABYTE, and BLT use different tasks, training budgets, model families, and segmentation mechanisms [1][3][4][5]; their headline results cannot be ranked as one shared leaderboard. RoPE, nGPT, and Hrrformer intervene at still different surfaces [6][7][8].

This perspective gives up a simple winner, but gains transportability. It asks which interaction survives when parameters, compute, context, optimization, and output semantics are charged consistently.

## Common failure modes

**Calling an internal patcher “no tokenization.”** A model can have no external learned subword or patch vocabulary—and no external tokenizer—while still using a finite byte inventory and inducing latent blocks. State the distinctions.

**Matching parameter count but not compute.** A vocabulary parameter count combines an input embedding lookup with an output softmax. ByT5 notes that the lookup is essentially FLOP-free and that moving vocabulary-associated parameters into Transformer layers typically increases FLOPs [2]. Report both budgets.

**Matching positions but not raw context.** One subword position and one byte position cover different amounts of text. Compare raw bytes or characters covered as well as model-visible length.

**Attributing a package result to one component.** A gain from `R1+O1` is not evidence that `R1` alone caused it. Run the off-diagonal cells or narrow the claim.

**Treating an algebraic precedent as endorsement.** RoPE proves that rotation algebra can implement positional interactions [6]; it does not validate a fully complex Transformer. Hrrformer proves a particular HRR recasting can be evaluated [8]; it does not establish that every VSA representation needs that operator.

**Universalizing author-reported benchmarks.** BLT's scaling results, nGPT's optimization results, and Hrrformer's efficiency results are important primary evidence [5][7][8]. They remain conditional on the reported workloads and implementations until independently reproduced across matched settings.

## In practice: a decision protocol

Suppose a team wants to replace a 32k subword vocabulary with entropy-patched bytes.

1. **Write the claimed mechanism.** Is the expected gain vocabulary coverage, robustness, better allocation of compute, or all three? Give each a separate metric.
2. **Freeze the four cells.** Train subword/standard, subword/patched, byte/standard, and byte/patched variants. If a cell is technically impossible, that is an architectural dependency to report, not a reason to omit the limitation.
3. **Choose two budgets.** Run a parameter-matched comparison and a training-FLOP-matched comparison. If deployment matters, add a latency- or memory-matched frontier.
4. **Measure the interface.** Record raw bytes per context, visible positions, patch-length distribution, vocabulary/patch parameters, and compute by module.
5. **Measure intended and adverse slices.** Include clean quality, noisy text, spelling-sensitive tasks, multilingual or code data if relevant, long-tail bytes, and throughput.
6. **Report main and interaction effects.** Say whether bytes help with both operators, whether patching helps with both representations, and whether their pairing adds a specific interaction.
7. **Keep claims at the tested boundary.** A classification encoder result does not establish autoregressive decode efficiency; a scaling preprint does not settle production serving cost; a geometric optimization result does not establish semantic benefit.

The goal is not to prohibit co-adaptation. Co-adaptation is often the point. The goal is to make it visible enough that another researcher can reproduce the package, substitute either half, and learn which conclusion survives.

## Further reading

1. Jonathan H. Clark, Dan Garrette, Iulia Turc, and John Wieting — *CANINE: Pre-training an Efficient Tokenization-Free Encoder for Language Representation* (TACL 2022), arXiv:2103.06874v4 — https://arxiv.org/abs/2103.06874v4
2. Linting Xue, Aditya Barua, Noah Constant, Rami Al-Rfou, Sharan Narang, Mihir Kale, Adam Roberts, and Colin Raffel — *ByT5: Towards a token-free future with pre-trained byte-to-byte models* (2021 preprint), arXiv:2105.13626v3 — https://arxiv.org/abs/2105.13626v3
3. Yi Tay et al. — *Charformer: Fast Character Transformers via Gradient-based Subword Tokenization* (ICLR 2022), arXiv:2106.12672v3 — https://arxiv.org/abs/2106.12672v3
4. Lili Yu, Dániel Simig, Colin Flaherty, Armen Aghajanyan, Luke Zettlemoyer, and Mike Lewis — *MEGABYTE: Predicting Million-byte Sequences with Multiscale Transformers* (2023), arXiv:2305.07185v2 — https://arxiv.org/abs/2305.07185v2
5. Artidoro Pagnoni et al. — *Byte Latent Transformer: Patches Scale Better Than Tokens* (2024 preprint), arXiv:2412.09871v1 — https://arxiv.org/abs/2412.09871v1
6. Jianlin Su, Yu Lu, Shengfeng Pan, Ahmed Murtadha, Bo Wen, and Yunfeng Liu — *RoFormer: Enhanced Transformer with Rotary Position Embedding* (2021 preprint), arXiv:2104.09864v5 — https://arxiv.org/abs/2104.09864v5
7. Ilya Loshchilov, Cheng-Ping Hsieh, Simeng Sun, and Boris Ginsburg — *nGPT: Normalized Transformer with Representation Learning on the Hypersphere* (ICLR 2025), arXiv:2410.01131v2 — https://arxiv.org/abs/2410.01131v2
8. Mohammad Mahmudul Alam, Edward Raff, Stella Biderman, Tim Oates, and James Holt — *Recasting Self-Attention with Holographic Reduced Representations* (ICML 2023), arXiv:2305.19534v1 — https://arxiv.org/abs/2305.19534v1
