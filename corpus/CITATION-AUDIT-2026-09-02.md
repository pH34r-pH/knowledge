# Citation audit — 2026-09-02

Citation-integrity gate for [`ml-techniques/logarithmic-closed-numerical-representations.md`](ml-techniques/logarithmic-closed-numerical-representations.md). The source pool was resolved before drafting and was restricted to the four publications with source-repository provenance in the domain-scaling-lab literature audit.

## Result

- **4/4 sources canonically resolved.** Titles, authors, years, identifiers, and venues match primary metadata.
- **4/4 article citation URLs live.** Both arXiv versioned pages, the Springer landing page, and the official TUM record for Vogel et al. are directly fetchable; the latter independently confirms the DOI and proceedings metadata because the ACM endpoint may return an automated-client 403.
- **All cited claim groups have full-text or primary-abstract support.** No issue text, prior chatbot prose, or unpublished experimental result is used as authority.
- **Independent entailment pass.** A second claim-by-claim pass against the source spans found no unsupported article claim.
- **Contradiction check found one source-internal numerical inconsistency.** CurveFP v2's introduction reports 4.4%/3.9% area differences, while its abstract, Table 6 values, and conclusion support 4.6%/4.1%. The article uses the table-derived values and discloses the discrepancy.
- **Verifier correction applied.** The first independent pass rejected an inferred “extra half-bit handling” cost for Miyashita et al.'s base-`sqrt(2)` case. That clause was replaced with the source-supported same-accumulation-equation statement, and the verifier's focused re-check passed.

Overall status: **PASS — 4/4 resolved, 4/4 live, entailment clean after one contradiction was bounded and documented.** Confidence remains medium because CurveFP is a recent single-author preprint with one-seed preliminary hardware evidence.

## Canonical resolution and liveness

| Ref. | Canonical work | Resolution | Liveness on 2026-09-02 | Local archive |
|---|---|---|---|---|
| [1] | Daisuke Miyashita, Edward H. Lee, and Boris Murmann, *Convolutional Neural Networks using Logarithmic Data Representation* (2016), `arXiv:1603.01025v2` | arXiv metadata and v2 full text agree on title/authors/version | `https://arxiv.org/abs/1603.01025v2` live | `arxiv/1603.01025.pdf` + metadata |
| [2] | Sebastian Vogel, Mengyu Liang, Andre Guntoro, Walter Stechele, and Gerd Ascheid, *Efficient hardware acceleration of CNNs using logarithmic data representation with arbitrary log-base* (ICCAD 2018), `10.1145/3240765.3240803` | DOI, ICCAD proceedings metadata, and official TUM publication record agree | Article links to the live official TUM record; DOI canonical and resolved; ACM endpoint bot-blocked for one automated fetch | non-arXiv; provenance/citation only per repository convention |
| [3] | Jiawei Xu, Yuxiang Huan, Yi Jin, Haoming Chu, Li-Rong Zheng, and Zhuo Zou, *Base-Reconfigurable Segmented Logarithmic Quantization and Hardware Design for Deep Neural Networks* (2020), `10.1007/s11265-020-01557-8` | Springer version-of-record metadata | canonical Springer DOI landing page live | non-arXiv; provenance/citation only per repository convention |
| [4] | Ye Qiao, *CurveFP: Co-Designing Numerical Representation and Product Arithmetic for Language Models* (2026), `arXiv:2608.10010v2` | arXiv v2 metadata and full text; version pinned because exact numerical and hardware claims are load-bearing | `https://arxiv.org/abs/2608.10010v2` and v2 HTML live | `arxiv/2608.10010.pdf` + metadata |

## Claim-support map

| Ref. | Article claim group | Supporting span | Entailment result |
|---|---|---|---|
| [1] | Base-2 log coding turns products into exponent additions/bit shifts; accumulation remains a separate linear- or log-domain operation | §3.1–§3.3, equations 1–4 | Pass. The article explicitly avoids claiming that summation becomes free. |
| [1] | Base-2 versus base-`sqrt(2)` is a range/resolution trade-off; the finer-base case uses the paper's same log-domain accumulation equation; reported CNN results are model-specific | §4.1–§4.4, especially §4.3, Table 5, and the end-to-end training comparison | Pass after removing an unsupported inference about extra half-bit handling. Results are scoped to AlexNet, VGG16, and the paper's CIFAR-10 model rather than generalized to LLMs. |
| [2] | Arbitrary-base quantization was evaluated on pretrained CNNs without retraining and implemented with FPGA log processing elements | Primary abstract in the official institutional record | Pass. The article does not import the paper's 22.3% power figure, avoiding an unnecessary implementation-specific load-bearing number. |
| [3] | Layer-varying mixtures of base 2 and base `sqrt(2)`; 6.4× compression/1.66% top-5 drop; 55 nm arithmetic-element comparison | Springer abstract | Pass. The article labels every numerical result implementation-specific and does not universalize it. |
| [4] | Element fields, rational radix, exact widened-coordinate product rule, and finite phase law `H = qK/gcd(p,qK)` | v2 §3.1–§3.2, equations 1–5 | Pass. “Closed product” is explicitly separated from finite-destination saturation. |
| [4] | 7-bit inference result and three matched 3B-token training triplets | v2 abstract and §4, Tables 2–5 | Pass. The article preserves the paper's parity interpretation rather than asserting statistical superiority. |
| [4] | 4×4 tile areas and exclusions | v2 Table 6, §5, Appendix C | Pass after arithmetic re-check and contradiction handling. `(51,646.8−49,282.9)/51,646.8 = 4.58%`; `(51,646.8−49,540.1)/51,646.8 = 4.08%`, rounded to 4.6% and 4.1%. |

## Contradiction and boundary checks

The four sources do not directly contradict one another: they test different models, bases, formats, and hardware contracts. Their results therefore cannot be ranked as if they were a shared benchmark. The synthesis limits the common conclusion to a mechanism: logarithmic spacing can simplify product formation, finer bases recover representational resolution at an arithmetic cost, and accumulation must be charged separately.

CurveFP v2 contains an internal mismatch. Its abstract and conclusion say the selected CurveFP tile is 4.6% smaller than timing-closing FP8; Table 6 supports that value. The introduction instead says 4.4%. Likewise, Table 6 supports 4.1% for the P1-to-P1 comparison, while the introduction says 3.9%. The audit treats Table 6's raw areas as controlling, records the discrepancy in the article, and makes no frequency-scaling, application-throughput, or system-energy claim.

The article also enforces these negative boundaries:

- no private or unpublished domain-scaling-lab result is described;
- no CNN result is presented as direct evidence for language-model training;
- no product-path area result is presented as an accelerator-level efficiency result;
- no fake-quantization quality result is treated as proof of hardware savings;
- no unresolved factor-lattice publication is cited.
