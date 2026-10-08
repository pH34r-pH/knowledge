# Public paper identity intake — 2026-10-08

## Scope

This identity-only supplement adds 11 public paper records to the canonical [ExternalWork registry](works.jsonl). It does not add article prose, findings, `ExternalClaim` or `KnowledgeEvidence` rows, or project adoption assertions. The `canonical_key` values in the [intake audit](research-intake-next-pass-2026-10-08.json) are a reconciliation map to Works, not a second registry.

| Identity | Version | Work | Record |
| --- | --- | --- | --- |
| [OrderMoE](https://arxiv.org/abs/2607.17154v2) | v2 | `KWRK-000131` | arXiv metadata |
| [HetRoute](https://arxiv.org/abs/2608.00577v2) | v2 | `KWRK-000132` | arXiv metadata |
| [Efficient Expert-Parallel Communication on PCIe-Connected Consumer GPUs](https://arxiv.org/abs/2609.40093v1) | v1 | `KWRK-000133` | arXiv metadata; issued DOI noted as pending registration |
| [UCCL-EP](https://arxiv.org/abs/2512.19849v2) | v2 | `KWRK-000134` | arXiv metadata |
| [Mixture-of-Experts Serving](https://arxiv.org/abs/2607.17880v1) | v1 | `KWRK-000135` | arXiv metadata |
| [FaaSMoE](https://arxiv.org/abs/2604.26881v1) | v1 | `KWRK-000136` | arXiv metadata; published DOI `10.1145/3812836.3814785` retained |
| [LIMINAL](https://arxiv.org/abs/2507.14397v2) | v2 | `KWRK-000137` | arXiv metadata |
| [Sample Count Is Not Enough](https://arxiv.org/abs/2609.19499v2) | v2 | `KWRK-000138` | arXiv metadata |
| [LatentPort](https://arxiv.org/abs/2609.25053v1) | v1 | `KWRK-000139` | arXiv metadata |
| [Semantic Parallelism](https://arxiv.org/abs/2503.04398v5) | v5 | `KWRK-000140` | arXiv metadata |
| [TokenWeave](https://arxiv.org/abs/2505.11329v5) | v5 | `KWRK-000141` | arXiv metadata; arXiv record lists acceptance to MLSys 2026 |

## Counts and boundaries

For these 11 paper leads, 11 were added, 0 were already in Works, and 0 were quarantined after primary identity checks. arXiv versions are pinned in source URLs and kept separate from stable arXiv identifiers; DOI aliases are retained where supplied by the source record. The `2609.40093` DOI is recorded with the source's pending-registration status.

The separately referenced government/vendor/repository URL set and four NSF links were not included in the reviewed transfer payload or the inspected Knowledge issues. Their identities and counts are therefore not represented here; no total-source count is implied. Add them only after receiving their exact public URLs and checking canonical identity, current Work matches, and source type.
