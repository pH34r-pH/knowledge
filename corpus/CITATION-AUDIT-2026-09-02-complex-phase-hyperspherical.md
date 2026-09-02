# Citation audit — complex, phase-aware, and hyperspherical Transformer computation — 2026-09-02

Citation-integrity gate for [`ml-techniques/complex-phase-aware-hyperspherical-transformers.md`](ml-techniques/complex-phase-aware-hyperspherical-transformers.md). The writer was restricted to eleven publications already resolved in the domain-scaling-lab literature audit and evidenced in the source repository. No issue text, prior chatbot prose, private experimental result, or issue #1 candidate lacking source-repository provenance was used as scientific authority.

## Result

- **11/11 sources canonically resolved.** Titles, authors, and exact arXiv versions match the paired local metadata, primary PDFs, and live arXiv records.
- **11/11 exact versioned citation URLs live.** Each `arxiv.org/abs/<id>v<version>` page resolved on 2026-09-02.
- **35/35 citation-bearing claim groups supported.** An independent verifier checked 76 citation tokens against the eleven local primary PDFs.
- **0 unrelated citations, 0 contradictions, and 0 residual overstatements.** One unsupported negative inference and one version-date label found by the verifier were corrected before the pass.
- **Synthesis is labeled as synthesis.** The factor table, matched-control protocol, measurement checklist, and practical decision sequence are recommendations introduced by the article, not findings attributed to the eleven papers.

Overall status: **PASS — 11/11 resolved, 11/11 live, 35/35 claim groups entailed, contradiction check clean after two corrections.** Confidence remains medium because the papers do not share one matched benchmark, several mechanisms are tested mainly in signal or vision settings, and PCT is a recent single-author preprint.

## Canonical resolution and liveness

| Ref. | Canonical work | Resolution | Liveness on 2026-09-02 | Local archive |
|---|---|---|---|---|
| [1] | Yang et al., *Complex Transformer: A Framework for Modeling Complex-Valued Sequence*, `arXiv:1910.10202v2` | Paired metadata and primary PDF agree on identity/version | exact v2 abstract page live | `arxiv/1910.10202.pdf` + metadata |
| [2] | Dong et al., *Signal Transformer: Complex-valued Attention and Meta-Learning for Signal Recognition*, `arXiv:2106.04392v2` | Paired metadata and primary PDF agree on identity/version | exact v2 abstract page live | `arxiv/2106.04392.pdf` + metadata |
| [3] | Eilers and Jiang, *Building Blocks for a Complex-Valued Transformer Architecture*, `arXiv:2306.09827v1` | Paired metadata and primary PDF agree on identity/version | exact v1 abstract page live | `arxiv/2306.09827.pdf` + metadata |
| [4] | Hioki, *Complex-Valued Phase-Coherent Transformer*, `arXiv:2605.10123v2` | Paired metadata and primary PDF agree on identity/version | exact v2 abstract page live | `arxiv/2605.10123.pdf` + metadata |
| [5] | Su et al., *RoFormer: Enhanced Transformer with Rotary Position Embedding*, `arXiv:2104.09864v5` | First posted 2021; paired PDF/metadata agree that exact v5 was updated in 2023 | exact v5 abstract page live | `arxiv/2104.09864.pdf` + metadata |
| [6] | Movahedi et al., *Selective Rotary Position Embedding*, `arXiv:2511.17388v3` | Paired metadata and primary PDF agree on identity/version | exact v3 abstract page live | `arxiv/2511.17388.pdf` + metadata |
| [7] | Loshchilov et al., *nGPT: Normalized Transformer with Representation Learning on the Hypersphere*, `arXiv:2410.01131v2` | Paired metadata and primary PDF agree on identity/version | exact v2 abstract page live | `arxiv/2410.01131.pdf` + metadata |
| [8] | Hu et al., *Hyper-SET: Designing Transformers via Hyperspherical Energy Minimization*, `arXiv:2502.11646v3` | Paired metadata and primary PDF agree on identity/version | exact v3 abstract page live | `arxiv/2502.11646.pdf` + metadata |
| [9] | Dehghani et al., *Universal Transformers*, `arXiv:1807.03819v3` | Paired metadata and primary PDF agree on identity/version | exact v3 abstract page live | `arxiv/1807.03819.pdf` + metadata |
| [10] | Lan et al., *ALBERT: A Lite BERT for Self-supervised Learning of Language Representations*, `arXiv:1909.11942v6` | Paired metadata and primary PDF agree on identity/version | exact v6 abstract page live | `arxiv/1909.11942.pdf` + metadata |
| [11] | Bai, Kolter, and Koltun, *Deep Equilibrium Models*, `arXiv:1909.01377v2` | Paired metadata and primary PDF agree on identity/version | exact v2 abstract page live | `arxiv/1909.01377.pdf` + metadata |

## Claim-support map

| Ref. | Article claim groups | Primary support | Entailment result |
|---|---|---|---|
| [1] | Complex query/key/value paths; real/imaginary expansion; eight real multi-head terms; min–max rather than softmax; MusicNet and IQ scope | §3.1–3.3, equations 2–6, and §4 experiments | Pass. No private IQ result is reproduced; the non-public dataset is used only to bound evidence scope. |
| [2] | `C → R` non-analyticity; complex-gradient rules; generalized complex softmax using magnitude, real part, or imaginary part; few-shot signal scope | §2 motivation and §3.2 complex-valued attention | Pass. The article presents these as CAMEL's mathematical and implementation choices, not the sole possible complex formulation. |
| [3] | Conjugate complex dot product; joint-rotation invariance of its real part; alternative score maps; joint real/imaginary covariance layer normalization; MusicNet evidence | §4.1–4.2 and §5 | Pass. “Hermitian dot product” names the displayed conjugate inner product; the article does not claim the paper uses that word. |
| [4] | L2-normalized complex queries/keys; real sigmoid gate on complex cosine score; token non-competition; matched cells; depth-sweep result | Abstract, §3.2–3.6, and §4.7 | Pass. Results are explicitly labeled author-reported evidence from a recent single-author preprint. |
| [5] | Two-dimensional query/key rotations; absolute-position encoding and relative-position interaction; real block-rotation implementation | §3.1–3.2 derivation | Pass after pinning first-posted and exact-v5 update dates separately. No full-complex-network conclusion is drawn. |
| [6] | Input-dependent learned rotation; composition with decay gates; gated-linear/recurrent interpretation; spectral-leakage argument; RoPE-kernel implementation | Abstract and §2–3 | Pass. Rotation-plus-decay is scoped to the paper's construction and theoretical framing. |
| [7] | Unit-normalized embeddings, hidden states, and attention/MLP vectors; hyperspherical displacement and normalized update; 4–20× optimization-step report | Abstract and §1–2 | Pass. The numeric result is configuration-bound and not presented as a universal unit-sphere speedup. |
| [8] | Hyperspherical energy with alignment and uniformity terms; symmetric attention/feed-forward/RMSNorm/skip derivation; shared recurrent depth; evaluated task families | Abstract and §3–4 | Pass. Package evidence is not attributed to the spherical constraint alone. |
| [9] | Parallel-in-time recurrence over representation depth; shared transition; fixed or adaptive per-position halting | Abstract and §2.1–2.2 | Pass. The article distinguishes recurrence over depth from recurrence over token positions. |
| [10] | Factorized embeddings; cross-layer parameter sharing; parameter-efficiency motivation; finite configurations; observed oscillation rather than equilibrium convergence | §1 and §3.1 | Pass. Sharing is used as a parameter-control precedent, not as equilibrium evidence. |
| [11] | Fixed-point root solve; infinite-depth weight-tied equivalence; implicit differentiation; memory independent of effective depth; solver-specific semantics | Abstract and §3 | Pass. DEQ is kept distinct from finite shared-depth unrolling. |

## Corrections required by the independent verifier

The verifier initially failed the draft and required these changes before returning PASS:

1. Replaced “nGPT normalizes vectors without sharing layer parameters” with the source-supported contrast that nGPT documents normalization throughout its Transformer, whereas Hyper-SET explicitly adds shared recurrent depth. The nGPT PDF does not itself make the negative parameter-sharing claim.
2. Replaced RoFormer's ambiguous “2021 preprint” label with “first posted 2021, v5 updated 2023,” matching both the paired metadata and the exact v5 PDF title page.

## Contradiction and boundary checks

The eleven papers do not form one model family or shared leaderboard. They intervene at different surfaces and evaluate different tasks, budgets, parameterizations, and depth semantics. No paper contradicts another mechanism as stated in the article; several do block stronger narratives that the article explicitly rejects:

- RoPE's useful rotation algebra does not entail a fully complex-valued network.
- A complex tensor representation does not specify the required real score or gating map.
- PCT's query/key L2 normalization is not equivalent to nGPT's model-wide hyperspherical constraint.
- nGPT's normalized geometry is not evidence for shared or recurrent depth.
- Hyper-SET bundles geometry, energy, operator, normalization, and sharing, so its result cannot isolate radius alone.
- ALBERT's sharing does not establish recurrence-to-equilibrium; the paper reports non-convergent oscillation across its finite stack.
- Universal Transformer's finite or adaptively halted recurrence is not a DEQ fixed-point solve.
- Music, radio, image, Sudoku, or synthetic evidence is not generalized to broad autoregressive language-model superiority.
- PCT and Selective RoPE claims are pinned to the exact recent versions and kept at author-reported scope.

No unresolved or mismatched reference remains in the article. No source used here is cited only from domain-scaling-lab issue text, and no private or unpublished domain-scaling-lab conclusion appears in the synthesis.
