# Citation audit — vector-symbolic representations and algebra-aware neural processing — 2026-09-02

Citation-integrity gate for [`ml-techniques/vector-symbolic-algebra-aware-neural-processing.md`](ml-techniques/vector-symbolic-algebra-aware-neural-processing.md). The writer was restricted to five publications already resolved in the domain-scaling-lab literature audit and evidenced in the source repository. No issue text, prior chatbot prose, private experiment, or topically plausible publication lacking source-repository provenance was used as scientific authority.

## Result

- **5/5 sources canonically resolved.** Titles, authors, venue/year, DOI or exact arXiv version match primary publisher records, paired local metadata, and primary PDFs where archived.
- **5/5 citation URLs passed the liveness gate.** Four returned their primary content directly. The IEEE URL for Plate 1995 returned the publisher's live JavaScript/bot-verification interstitial; its DOI, title, author, venue, pages, and abstract were independently confirmed through the canonical record and PubMed index, so it is bot-blocked rather than dead.
- **39/39 citation-bearing claim groups supported.** An independent verifier checked 48 citation tokens against the five sources and their permitted claim spans.
- **0 unrelated citations, 0 contradictions, and 0 residual overstatements.** One under-cited mechanism clause found by the verifier was split across the correct primary sources before the pass.
- **Synthesis is labeled as synthesis.** The 2×2 representation–operator grid, matched-control protocol, diagnostics, and decision sequence are recommendations introduced by the article, not findings attributed to the five publications.

Overall status: **PASS — 5/5 resolved, 5/5 liveness checks passed, 39/39 claim groups entailed, contradiction check clean after one citation correction.** Confidence remains medium because Hrrformer is the only algebra-aware neural operator in the provenance-backed pool, its evaluation is long-sequence classification rather than autoregressive language modeling, and the older HRR/HDC sources describe a family whose variants do not share every algebraic property.

## Canonical resolution and liveness

| Ref. | Canonical work | Resolution | Liveness on 2026-09-02 | Local archive |
|---|---|---|---|---|
| [1] | Plate, *Holographic reduced representations*, IEEE Transactions on Neural Networks 6(3), 623–641 (1995), DOI `10.1109/72.377968` | IEEE record, DOI metadata, and PubMed identity/abstract agree | canonical IEEE URL live behind JavaScript/bot verification; DOI and indexed abstract independently resolve | none; non-arXiv source, so no ad hoc raw archive |
| [2] | Plate, *Holographic Reduced Representation: Distributed Representation for Cognitive Structures*, CSLI Publications (2003) | CSLI publisher page confirms title, author, date, ISBNs, description, and contents | corrected primary CSLI publisher page live | none; book, so no ad hoc raw archive |
| [3] | Kanerva, *Hyperdimensional Computing: An Introduction to Computing in Distributed Representation with High-Dimensional Random Vectors*, Cognitive Computation 1(2), 139–159 (2009), DOI `10.1007/s12559-009-9009-8` | Springer publisher metadata and abstract confirm identity | primary Springer article page live | none; non-arXiv source, so no ad hoc raw archive |
| [4] | Kleyko et al., *Vector Symbolic Architectures as a Computing Framework for Emerging Hardware*, Proceedings of the IEEE 110(10), 1538–1571 (2022), DOI `10.1109/JPROC.2022.3209104`, `arXiv:2106.05268v2` | Paired metadata/PDF and live arXiv record agree on title, eleven authors, exact v2, journal reference, and DOI | exact v2 abstract and HTML pages live | `arxiv/2106.05268.pdf` + metadata |
| [5] | Alam et al., *Recasting Self-Attention with Holographic Reduced Representations*, ICML 2023, `arXiv:2305.19534v1` | Paired metadata/PDF and live arXiv record agree on identity/version and ICML status | exact v1 abstract page live | `arxiv/2305.19534.pdf` + metadata |

## Claim-support map

| Ref. | Article claim groups | Primary support | Entailment result |
|---|---|---|---|
| [1] | HRR as a canonical VSA; circular-convolution association; fixed-width variable bindings, short sequences, frame-like and reduced structures; noisy reconstruction; separate associative cleanup memory | Canonical 1995 abstract exposed through the resolved IEEE/PubMed record | Pass. The article does not infer detailed equations or empirical capacity numbers from the abstract. |
| [2] | Book-length development of circular convolution/correlation, superposition memories, frequency-domain HRR, and capacity limitations | CSLI publisher description and chapter/appendix table of contents | Pass. The book is used only for bibliographic scope visible on the publisher page, not for an unavailable verbatim technical derivation. |
| [3] | Canonical HDC tutorial framing; high-dimensional random-vector models manipulated by operations that yield new high-dimensional vectors | Springer publisher abstract and metadata | Pass. No claim exceeds the public abstract. |
| [4] | VSA/HDC as a family; vector-space variants; atomic vectors, similarity, binding, superposition, permutation, cleanup, crosstalk, and capacity; MAP-specific properties; HRR/FHRR distinctions; FHRR phasor algebra; computing in superposition; decoding/search limitations | Abstract; §§III-A–III-C, V-A, and VI of the exact v2 primary PDF | Pass. MAP properties are explicitly scoped to the survey's example and not generalized to every VSA. Capacity is qualified by representation, load, memory, and precision. |
| [5] | HRR binding/unbinding formula; key–value superposition; cosine scores and softmax cleanup; non-IID learned-vector caveat; cleanup necessity; `O(T H log H)` time and `O(T H)` space; EMBER/LRA evidence, 20-versus-200-epoch comparison, single/multi-layer scope, and Path-X failure | Abstract; §3 equations 1–4 and cleanup discussion; §4/Table 1; §5 of the exact v1 primary PDF | Pass. The construction is called not mathematically equivalent to standard attention, and reported classification results are not exported to autoregressive language modeling. |

## Quote-span and paraphrase checks

The deterministic pass anchored each technical paraphrase to retrievable source text:

- Plate 1995: canonical abstract clauses beginning “The method uses circular convolution…” and ending with the separate associative-memory cleanup statement.
- Plate 2003: publisher contents for §§3.1–3.8, chapter 4, and appendices B–H; no inaccessible chapter prose is paraphrased as a finding.
- Kanerva 2009: Springer abstract describing the named high-dimensional models and vector-to-vector operations.
- Kleyko et al. v2: local primary-PDF spans for the family definition; seed vectors; binding, superposition, permutation, item memory, crosstalk, capacity, FHRR, and model-specificity warnings.
- Alam et al. v1: local primary-PDF spans for equations 1–4, the softmax cleanup requirement, complexity analysis, and experiment table.

No direct quotation in the article exceeds the retrieved source text, and no quote-span is supplied by domain-scaling-lab issue prose.

## Correction required by the independent verifier

The first verification pass supported 38 of 39 claim groups and failed one under-cited clause. The draft had cited only [4] for a sentence that combined two claims: the survey's warning that MAP properties do not transfer to every VSA, and HRR's use of circular convolution. The survey supports the former and enumerates alternative VSA constructions, but its exact v2 text does not state the circular-convolution mechanism. The sentence now cites Plate's primary 1995 abstract [1] for HRR circular convolution and Kleyko et al. [4] for MAP and the variant boundary. The verifier re-checked only this correction and returned **PASS, 39/39 supported, with no new precision, scope, contradiction, or metadata problem**.

## Provenance-manifest correction

Resolution of [2] exposed a URL defect in the pre-existing literature audit. The book identity was correct, but the CSLI URL used a mismatched ISBN suffix, `1575863742`. The live publisher record is the paperback ISBN page ending `1575864304`, which confirms Plate, the full title, 2003 date, contents, and ISBN `9781575864303`. Both human- and machine-readable audit manifests were corrected and the change was recorded in their identity-correction section. No publication was added, removed, or reidentified, so bibliography and deduplication counts are unchanged.

## Contradiction and boundary checks

The sources describe related but non-identical systems. No source contradicts another claim as stated in the article; they do block stronger readings that the synthesis explicitly rejects:

- VSA/HDC is a family, not one vector datatype or one binding operator.
- MAP's self-inverse bipolar product does not establish exact inversion for HRR or every VSA.
- Fixed-width composition does not mean unlimited or lossless capacity.
- Cleanup and its candidate memory are part of the computational and storage cost.
- HRR is an algebraic representation system, not merely an FFT mixing layer.
- FHRR's complex phasors and phase-additive binding do not validate an arbitrary complex-valued Transformer.
- Hrrformer intentionally departs from classical independent-random-vector assumptions and relies on its softmax cleanup.
- Hrrformer's linear-in-`T` per-layer analysis still contains `H log H` work and does not imply constant-time retrieval.
- EMBER and Long Range Arena classification results do not demonstrate autoregressive language modeling or universal attention replacement.

No unresolved or mismatched reference remains in the article. No source was added merely to satisfy a topical checklist, and no private or unpublished domain-scaling-lab result appears in the synthesis.
