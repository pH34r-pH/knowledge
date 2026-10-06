# External research intake — 2026-10-06

## Scope and disposition

This bounded pass and follow-up added 52 public source identities to the canonical [ExternalWork registry](works.jsonl), extending the batch range to `KWRK-000026`–`KWRK-000077`. The full count, 16 lead dispositions, source boundaries, context-only issue threads, crosswalk status, and remaining citation gaps are in [the machine-readable audit](research-intake-audit-2026-10-06.json). The additional follow-up batch is `KWRK-000063`–`KWRK-000077`: ten research papers, four pinned software repository snapshots, and one official vendor research page.

| Registry or source type | Before | Added | After |
| --- | ---: | ---: | ---: |
| ExternalWork | 25 | 52 | 77 |
| Research papers | — | 44 | — |
| Vendor reports or research pages | — | 2 | — |
| Standards | — | 2 | — |
| Pinned software repository snapshots | — | 4 | — |
| ExternalClaim | 26 | 0 | 26 |
| KnowledgeEvidence | 26 | 0 | 26 |

No ExternalClaim or KnowledgeEvidence rows were added, and no new claims were accepted. Research-paper and vendor findings remain attributed to their sources and their reported setups; software-repository records identify pinned code snapshots, not independent performance evidence.

## Results kept within source boundaries

- **Multi-agent decision and debate:** the intake includes reports with mixed and protocol-sensitive outcomes. For example, Smit et al. report that untuned debate did not reliably outperform self-consistency or ensembling in their tests, while Kaesberg et al. report task-dependent effects across voting and consensus protocols. DART is specifically a vision-tool recruitment study. None establishes that more agents or more discussion is generally better.
- **Speculative decoding:** records distinguish method families and tested regimes. Mainardi et al. report that overhead can dominate for the evaluated 1–2B models; other papers report speedups on their own models, tasks, and serving configurations. Those measurements are not Kestrel or deployment estimates. DSpark has its own resolved paper record (`KWRK-000063`) and remains separate from DFlash (`KWRK-000044`).
- **Model communication and looped models:** C2C, Dual-Cache Latent Space Communication, and Latent Cache Flow remain separate works. The primary title for the supplied “XKV” lead is *Dual-Cache Latent Space Communication between Heterogeneous Language Models*. The two looped-transformer papers using the shorthand “LoopCD” are separate records. The Looped Diffusion Transformer is an image-diffusion work and is not treated as an autoregressive language-model result. Choir concerns distributed multi-agent autoformalization, not general theorem scaling.
- **Mixture-of-experts sources:** the seven bibliography leads now resolve to primary source identities: Shazeer sparse MoE, Clark routed scaling, DeepSeekMoE, Krajewski et al. fine-grained MoE scaling, Abnar et al. optimal sparsity, Tian et al. efficient MoE scaling, and Kolibri's EQB/LEI routing. The latter is represented by Aleph Alpha's report (`KWRK-000060`) and its cited method paper (`KWRK-000072`). Identity resolution does not make their findings accepted claims or independent replications.
- **Kolibri:** the report and model cards are vendor-authored. The report describes 78.1B total parameters and 3.46B active parameters, reports benchmark results including B200 testing, and describes Exact Quantile Balancing and Load-Error Injection as routing components. These are vendor reports; the intake does not describe Aleph Alpha as state-owned or treat the numbers as independent measurements. Its Merlin-Arthur and MergeMix model-card citations are now separately resolved as `KWRK-000064` and `KWRK-000065`; those papers are not represented as Kolibri evaluations.
- **Software snapshots:** zchunk, DeepGEMM, the MALLM demo, and Tilde's MoMoE implementation are recorded as immutable GitHub commit snapshots (`KWRK-000073`–`KWRK-000076`). These source records make the identified software visible despite the lack of verified DOIs. Using zchunk in the speculative-decoding workstream is a proposed project application, not an evaluated relationship or result; DeepGEMM is not characterized as suitable for older GPUs. The MALLM demo is separate from the MALLM paper (`KWRK-000030`). Public Long-Haul issue #48 uses “Project MoMoE” for the project-local mixture-of-mixtures-of-experts concept: hierarchical outer model routing over inner MoEs. It is not an external-paper citation and requires no ExternalWork row; Tilde's MoMoE code remains a separate software source.
- **Kardashev 0.7:** the official Banbury Road research page is recorded as `KWRK-000077`. It reports a 16-model population and 288 held-out tasks; these are vendor-reported experiments, not independent results. A founder X post claiming a different population size was inaccessible and remains unverified.
- **WebNN and WebGPU:** the inspected W3C documents are dated Candidate Recommendation Drafts. The linked WebNN/WebGPU issues discuss supported-device queries, device selection, and resource interoperation. The intake records no general zero-copy guarantee, deployed-browser guarantee, or physical-VRAM discovery guarantee.

One paper crosswalk remains explicitly **inferred**: KWRK-000048 (*Speculative Decoding: Performance or Illusion?*) is a plausible match to an unlinked Long-Haul MLSys 2026 reference, but the match is not verified and no canonical relation is asserted. The public [C2C author-repository issue #23](https://github.com/thu-nics/C2C/issues/23) reports a Qwen3 pairing below the receiver on the issue author's stated evaluation. The issue also says the paper does not report that exact pair and the reporter may have missed a setting; this remains a user report, not a paper finding or independent replication.

## Lead coverage and remaining gaps

The audit records a disposition for each of the original 16 leads: 13 external source identities are resolved, the project-local MoMoE concept is resolved without an ExternalWork row, and two external citations remain unresolved: the exact “spiking” and PIXAR papers. The Tilde MoMoE software snapshot remains distinct. The official Kardashev page resolves the vendor research-page identity, while the separate founder social post remains inaccessible. zchunk is identified as software; its proposed use in the speculative-decoding workstream has not been evaluated. This is partial coverage of the supplied and adjacent public leads, not an exhaustive inventory.

Pain Axis was already present as a Knowledge source note and was not duplicated. Reflexion was already cited in the agent-memory article; its new Work row fills the machine-readable registry gap. No private-project links, private issue identifiers, or private results are included. The public C2C thread above is a context-only source.
