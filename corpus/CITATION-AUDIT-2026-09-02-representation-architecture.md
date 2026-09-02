# Citation audit — representation–architecture co-design — 2026-09-02

Citation-integrity gate for [`ml-techniques/representation-architecture-co-design-language-models.md`](ml-techniques/representation-architecture-co-design-language-models.md). The writer was restricted to eight publications already resolved in the domain-scaling-lab literature audit and evidenced in the source repository. Publications mentioned only as issue #1 candidates without source-repository provenance were excluded.

## Result

- **8/8 sources canonically resolved.** Titles, authors, and exact arXiv versions match the paired local metadata and live arXiv records.
- **8/8 exact versioned citation URLs live.** Each `arxiv.org/abs/<id>v<version>` page resolved on 2026-09-02.
- **19/19 citation-bearing claim groups supported.** The independent verifier checked 39 citation tokens against the eight local primary PDFs.
- **0 unrelated citations, 0 contradictions, and 0 residual overstatements.** Six wording or metadata problems found during verification were corrected before the pass.
- **Synthesis is labeled as synthesis.** The 2×2 crossed design, interaction expression, matched-budget checklist, and practical decision protocol are recommendations introduced by the article, not attributed to the eight papers.

Overall status: **PASS — 8/8 resolved, 8/8 live, 19/19 claim groups entailed, contradiction check clean after corrections.** Confidence remains medium because several results are configuration-bound author reports and the cited papers do not run one common crossed benchmark.

## Canonical resolution and liveness

| Ref. | Canonical work | Resolution | Liveness on 2026-09-02 | Local archive |
|---|---|---|---|---|
| [1] | Clark et al., *CANINE: Pre-training an Efficient Tokenization-Free Encoder for Language Representation*, `arXiv:2103.06874v4` | Paired metadata and primary PDF agree on identity/version | exact v4 abstract page live | `arxiv/2103.06874.pdf` + metadata |
| [2] | Xue et al., *ByT5: Towards a token-free future with pre-trained byte-to-byte models*, `arXiv:2105.13626v3` | Paired metadata and primary PDF agree on identity/version | exact v3 abstract page live | `arxiv/2105.13626.pdf` + metadata |
| [3] | Tay et al., *Charformer: Fast Character Transformers via Gradient-based Subword Tokenization*, `arXiv:2106.12672v3` | Paired metadata and primary PDF agree on identity/version | exact v3 abstract page live | `arxiv/2106.12672.pdf` + metadata |
| [4] | Yu et al., *MEGABYTE: Predicting Million-byte Sequences with Multiscale Transformers*, `arXiv:2305.07185v2` | Paired metadata and primary PDF agree on identity/version | exact v2 abstract page live | `arxiv/2305.07185.pdf` + metadata |
| [5] | Pagnoni et al., *Byte Latent Transformer: Patches Scale Better Than Tokens*, `arXiv:2412.09871v1` | Paired metadata and primary PDF agree on identity/version | exact v1 abstract page live | `arxiv/2412.09871.pdf` + metadata |
| [6] | Su et al., *RoFormer: Enhanced Transformer with Rotary Position Embedding*, `arXiv:2104.09864v5` | Paired metadata and primary PDF agree on identity/version | exact v5 abstract page live | `arxiv/2104.09864.pdf` + metadata |
| [7] | Loshchilov et al., *nGPT: Normalized Transformer with Representation Learning on the Hypersphere*, `arXiv:2410.01131v2` | Paired metadata and primary PDF agree on identity/version | exact v2 abstract page live | `arxiv/2410.01131.pdf` + metadata |
| [8] | Alam et al., *Recasting Self-Attention with Holographic Reduced Representations*, `arXiv:2305.19534v1` | Paired metadata and primary PDF agree on identity/version | exact v1 abstract page live | `arxiv/2305.19534.pdf` + metadata |

## Claim-support map

| Ref. | Article claim groups | Primary support | Entailment result |
|---|---|---|---|
| [1] | Unicode-character input; local processing and strided downsampling before a deep Transformer; reconstruction to character-level output | Abstract and §3.1 model/downsampling/upsampling description | Pass. No CANINE quality number is used. |
| [2] | Minimal-change byte Transformer counterexample; longer byte sequences; competitiveness and robustness; parameter/FLOP/speed accounting; moving vocabulary-associated parameters into layers | Abstract, model comparison, parameter-allocation discussion, and speed section | Pass after distinguishing the essentially FLOP-free input lookup from the output softmax and Transformer computation. |
| [3] | GBST enumerates contiguous candidates, learns position-wise scores, constructs latent subwords, and downsamples before deeper processing | Abstract and §2.1 GBST description | Pass. The article does not equate “token-free” with absence of internal aggregation. |
| [4] | Fixed patches with local and global models; shorter sequence for global attention; different capacity allocation | Abstract and architecture description | Pass. Claims are mechanism-level and do not import a universal benchmark ranking. |
| [5] | Next-byte-entropy dynamic patches; predictability-dependent compute; FLOP-controlled scaling as a comparison precedent | Abstract and architecture/scaling description | Pass. BLT is described as a 2024 preprint for the exact cited version. |
| [6] | Two-dimensional projected query/key subspaces; position-dependent rotations; absolute-position encoding and relative-position interaction | §3 formulation and 2D/general derivation | Pass after tightening “hidden dimensions” to projected query/key subspaces. |
| [7] | Unit-normalized embeddings, hidden states, and attention/MLP vectors; layer displacement on a hypersphere; optimization evidence bounded to configurations | Abstract and architecture/optimization description | Pass. No universal hyperspherical speed claim is made. |
| [8] | HRR binding, superposition, unbinding, similarity/softmax cleanup; recast query–key–value goal; `O(T H log H)` time and `O(T H)` space | §3 equations 1–4 and complexity discussion | Pass. Malware/LRA evidence is explicitly not generalized to autoregressive language modeling. |

## Corrections required by the independent verifier

The verifier initially failed the draft and required these changes before returning PASS:

1. Replaced “bytes or characters remove a fixed vocabulary” with the precise claim that they remove a **corpus-learned subword vocabulary and external segmentation**, while retaining finite byte/character symbol inventories.
2. Replaced “removing a tokenizer does not remove segmentation-like work” with a computational-burden statement that preserves ByT5 as a genuine no-learned-segmentation counterexample.
3. Corrected the ByT5 parameter explanation: an input embedding lookup is essentially FLOP-free, the output softmax is distinct, and reallocation into Transformer layers means equal parameters do not imply equal FLOPs.
4. Scoped the 2×2 crossed design to proposals that change both representation and operator, and labeled it as this article's causal-audit recommendation rather than a result established by the sources.
5. Tightened the RoPE description from generic hidden dimensions to two-dimensional subspaces of the projected query/key space.
6. Removed nonessential venue/DOI labels not established by the exact mapped PDF/metadata pair; retained only locally supported venue labels.

## Contradiction and boundary checks

The eight papers do not form one shared benchmark. They cover encoders, encoder–decoders, autoregressive decoders, positional encoding, normalization, and long-sequence classification with different budgets and tasks. Their results therefore cannot be ranked as if they isolate one common representation effect. The article limits the common conclusion to experimental method: specify the representation–operator package, charge compute consistently, and use crossed controls when both axes change.

No paper contradicts the mechanism attributed to another. ByT5 does contradict a stronger narrative that byte inputs always require learned patching or a new operator; the article uses it explicitly as that counterexample. The following negative boundaries are enforced:

- no private or unpublished domain-scaling-lab result is described;
- no issue text or prior chatbot prose is used as scientific authority;
- no issue #1 candidate lacking source-repository provenance enters the source pool;
- no classification or encoder result is generalized to autoregressive generation;
- no author-reported efficiency result is presented as a universal systems result;
- no complex, hyperspherical, or HRR precedent is treated as endorsement of a broader untested architecture.

One non-blocking source-package discrepancy remains: the paired CANINE v4 metadata abstract reports 2.8 F1 and 28% fewer parameters, while the local v4 PDF abstract reports 5.7 F1 and only says fewer parameters. The article uses neither figure. Those numbers remain excluded until the source-package discrepancy is reconciled.
