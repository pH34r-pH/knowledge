# Research intake follow-up — source identities — 2026-10-06

## Scope

This addendum follows [the 2026-10-06 intake audit](research-intake-audit-2026-10-06.json) without rewriting that historical record. It resolves the PIXAR and spiking paper identities, adds the machine-readable source row for Mamba already cited in the state-space article, and verifies the publication venue for existing Work `KWRK-000048`. No ExternalClaim or KnowledgeEvidence is accepted.

| Change | Work | Source identity |
| --- | --- | --- |
| PIXAR citation resolved | `KWRK-000078` | [PIXAR: Auto-Regressive Language Modeling in Pixel Space](https://arxiv.org/abs/2401.03321v2); [official repository](https://github.com/april-tools/pixar) |
| Spiking paper identity recorded | `KWRK-000079` | [SpikingBrain2.0: Brain-Inspired Foundation Models for Efficient Long-Context and Cross-Platform Inference](https://arxiv.org/abs/2604.22575v1); [official implementation](https://github.com/BICLab/SpikingBrain2.0) |
| Existing prose citation added to registry | `KWRK-000080` | [Mamba: Linear-Time Sequence Modeling with Selective State Spaces](https://arxiv.org/abs/2312.00752v2) |
| Existing MLSys paper venue verified | `KWRK-000048` | [Official MLSys 2026 proceedings page](https://proceedings.mlsys.org/paper_files/paper/2026/hash/554e056fe2b6d9fd27ffcd3367ae1267-Abstract-Conference.html) |

## Boundaries

- **PIXAR** is a decoder-only autoregressive language model operating on pixel representations of rendered text. Its paper reports text-generation results on LAMBADA and bAbI. This does not make it a general page-understanding result or establish a connection to spiking models.
- **SpikingBrain2.0** reports 5B models and long-context inference on up to eight A100 GPUs, including the authors’ vLLM evaluation. Those results stay within the paper’s tested setup; they do not establish performance on Kestrel, in a browser, or in a PIXAR combination.
- **Public Long-Haul issue #153** mentions an SNN comparison but gives no direct paper citation. SpikingBrain2.0’s source identity is recorded, while its exact correspondence to that issue sentence remains unverified.
- **Public Long-Haul issue #165** has an uncited sentence about recent MLSys 2026 speculative-decoding evidence. The official proceedings confirm the title and authors of `KWRK-000048`, and the topic/evaluation description is a plausible match. Since issue #165 does not link the paper, the crosswalk remains inferred; the paper’s vLLM workloads are not Kestrel measurements.
- **Mamba** was already cited as source 6 in `corpus/ml-techniques/state-space-models-linear-attention.md`; the new Work row fills the registry identity gap without changing the article or accepting a new claim.
- **Project MoMoE** remains a project-local concept from public [Long-Haul issue #48](https://github.com/pH34r-pH/long-haul/issues/48), not an external paper. Tilde’s MoMoE software (`KWRK-000076`) is separate. zchunk (`KWRK-000073`) remains a proposed project application, not a demonstrated decoding result.

The official arXiv version pages and MLSys proceedings page supply the metadata above. The full scope, counts, lead dispositions, and remaining relation uncertainties are in [the machine-readable follow-up audit](research-intake-source-gap-followup-2026-10-06.json). No private-project pointers or results are included.
