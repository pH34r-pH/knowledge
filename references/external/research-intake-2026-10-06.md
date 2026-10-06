# External research intake — 2026-10-06

## Scope and disposition

This bounded pass added 37 primary-source identities to the canonical [ExternalWork registry](works.jsonl): 34 research papers, Aleph Alpha's Kolibri technical report, and the dated W3C WebNN and WebGPU drafts. The new records span `KWRK-000026`–`KWRK-000062`. The detailed counts, source boundaries, context-only issue threads, crosswalk status, and unresolved leads are in [the machine-readable audit](research-intake-audit-2026-10-06.json).

No ExternalClaim or KnowledgeEvidence rows were added, and no new claims were accepted. The literature records preserve what authors or vendors report in their own evaluations; those reports are not independent replications or predictions for untested consumer applications.

| Registry | Before | Added | After |
| --- | ---: | ---: | ---: |
| ExternalWork | 25 | 37 | 62 |
| ExternalClaim | 26 | 0 | 26 |
| KnowledgeEvidence | 26 | 0 | 26 |

## Results kept within source boundaries

- **Multi-agent decision and debate:** the intake includes reports with mixed and protocol-sensitive outcomes. For example, Smit et al. report that untuned debate did not reliably outperform self-consistency or ensembling in their tests, while Kaesberg et al. report task-dependent effects across voting and consensus protocols. DART is specifically a vision-tool recruitment study. None establishes that more agents or more discussion is generally better.
- **Speculative decoding:** records distinguish method families and tested regimes. Mainardi et al. report that overhead can dominate for the evaluated 1–2B models; other papers report speedups on their own models, tasks, and serving configurations. Those measurements are not Kestrel or deployment estimates.
- **Model communication and looped models:** C2C, Dual-Cache Latent Space Communication, and Latent Cache Flow remain separate works. The primary title for the supplied “XKV” lead is *Dual-Cache Latent Space Communication between Heterogeneous Language Models*. The two looped-transformer papers using the shorthand “LoopCD” are separate records. The Looped Diffusion Transformer is an image-diffusion work and is not treated as an autoregressive language-model result. Choir concerns distributed multi-agent autoformalization, not general theorem scaling.
- **Kolibri:** the report and model cards are vendor-authored. The report describes 78.1B total parameters and 3.46B active parameters, and reports benchmarks on its stated hardware, including B200 testing. These are vendor reports; the intake does not describe Aleph Alpha as state-owned or treat the numbers as independent measurements.
- **WebNN and WebGPU:** the inspected W3C documents are dated Candidate Recommendation Drafts. The linked WebNN/WebGPU issues discuss supported-device queries, device selection, and resource interoperation. The intake records no general zero-copy guarantee, deployed-browser guarantee, or physical-VRAM discovery guarantee.

One paper crosswalk remains explicitly **inferred**: KWRK-000048 (*Speculative Decoding: Performance or Illusion?*) is a plausible match to an unlinked Long-Haul MLSys 2026 reference, but the match is not verified and no canonical relation is asserted. The public [C2C author-repository issue #23](https://github.com/thu-nics/C2C/issues/23) reports a Qwen3 pairing below the receiver on the issue author's stated evaluation. The issue also says the paper does not report that exact pair and the reporter may have missed a setting; this remains a user report, not a paper finding or independent replication.

## Unresolved leads

Sixteen source leads remain unpromoted across eight groups: zChunk has no verified paper identifier; “DSpark” is unresolved and kept separate from DFlash; DeepGEMM has no verified paper identifier; the cited Project MoMoE could not be matched to a stable source and is distinct from Tilde's MoE software; two Kolibri model-card citations (Merlin-Arthur and MergeMix) were not independently resolved; Kardashev 0.7 has no verified model card or paper and its vendor/self-reports lack independent support; seven MoE citation leads need exact primary-source resolution; and the spiking and PIXAR mentions lack enough metadata to identify their intended works. The audit lists each gap and its count.

Pain Axis was already present as a Knowledge source note and was not duplicated. Reflexion was already cited in the agent-memory article; its new Work row fills the machine-readable registry gap. This source pass is limited to the supplied and adjacent public leads and is not an exhaustive inventory. No private-project links or results are included.
