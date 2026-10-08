# Public source identity intake — 2026-10-08

## Scope and disposition

This supplement reconciles 35 newly supplied public URLs against canonical [ExternalWork records](works.jsonl). It adds 33 identity-verified Works, maps one arXiv pointer to existing `KWRK-000106`, and quarantines one NSF page whose title is visible but whose body could not be retrieved. The earlier 11-paper batch remains included in the audit. The dated [JSON intake audit](research-intake-next-pass-2026-10-08.json) is the complete URL-to-Work crosswalk; it is not a second source registry.

No article prose, findings, `ExternalClaim`, `KnowledgeEvidence`, accepted claims, or project-adoption relationships were added. Bibliographic identity is kept separate from research findings and adoption. Vendor reports, product pages, release notes, documentation, and repository descriptions remain attributed to their publishers/maintainers; none is treated as an independent evaluation. The Census CES working paper itself says it has not undergone the review accorded Census Bureau publications and that no agency endorsement should be inferred. The Canadian privacy survey is identified as government-commissioned public opinion research.

## Earlier paper batch

| Identity | Version | Work | Metadata check |
| --- | --- | --- | --- |
| [OrderMoE: An expert similarity driven distributed edge MoE inference](https://arxiv.org/abs/2607.17154v2) | v2 | `KWRK-000131` | Primary arXiv metadata |
| [HetRoute Heterogeneous and Cost-aware Collaborative Routing Framework for Distributed Edge MoE Inference](https://arxiv.org/abs/2608.00577v2) | v2 | `KWRK-000132` | Primary arXiv metadata |
| [Efficient Expert-Parallel Communication on PCIe-Connected Consumer GPUs](https://arxiv.org/abs/2609.40093v1) | v1 | `KWRK-000133` | Primary arXiv metadata |
| [UCCL-EP: Portable Expert-Parallel Communication](https://arxiv.org/abs/2512.19849v2) | v2 | `KWRK-000134` | Primary arXiv metadata |
| [Mixture-of-Experts Serving](https://arxiv.org/abs/2607.17880v1) | v1 | `KWRK-000135` | Primary arXiv metadata |
| [FaaSMoE: A Serverless Framework for Multi-Tenant Mixture-of-Experts Serving](https://arxiv.org/abs/2604.26881v1) | v1 | `KWRK-000136` | Primary arXiv metadata |
| [LIMINAL: Exploring The Frontiers of LLM Decode Performance](https://arxiv.org/abs/2507.14397v2) | v2 | `KWRK-000137` | Primary arXiv metadata |
| [Sample Count Is Not Enough: Candidate-Generation Strategy Shapes the Energy and Performance of LLM Test-Time Scaling](https://arxiv.org/abs/2609.19499v2) | v2 | `KWRK-000138` | Primary arXiv metadata |
| [LatentPort: Beyond KV Cache - Cross-Model Transfer of Recurrent Memory in Hybrid Language Models: A 4B-to-9B Hybrid-State Handoff Without Target Prefix Replay](https://arxiv.org/abs/2609.25053v1) | v1 | `KWRK-000139` | Primary arXiv metadata |
| [Semantic Parallelism: Redefining Efficient MoE Inference via Model-Data Co-Scheduling](https://arxiv.org/abs/2503.04398v5) | v5 | `KWRK-000140` | Primary arXiv metadata |
| [TokenWeave: Efficient Compute-Communication Overlap for Distributed LLM Inference](https://arxiv.org/abs/2505.11329v5) | v5 | `KWRK-000141` | Primary arXiv metadata |

## Newly supplied URLs

| Supplied URL | Resolved identity | Source class | Disposition |
| --- | --- | --- | --- |
| [supplied page](https://seedfund.nsf.gov/project-pitch/) | [Project Pitch](https://seedfund.nsf.gov/project-pitch/) | `official_program_page` | Added as `KWRK-000142` |
| [supplied page](https://www.nsf.gov/funding/opportunities/small-business-innovation-research-small-business-technology/nsf26-510/solicitation) | [NSF 26-510: Small Business Innovation Research / Small Business Technology Transfer Phase I, Phase II, Fast-Track Programs SBIR/STTR: Developing Deep Technologies that Advance U.S. Competitiveness and Security](https://www.nsf.gov/funding/opportunities/small-business-innovation-research-small-business-technology/nsf26-510/solicitation) | `government_solicitation` | Added as `KWRK-000143` |
| [supplied page](https://seedfund.nsf.gov/apply/project-pitch/) | [Project Pitch Information — NSF SBIR application process](https://seedfund.nsf.gov/apply/project-pitch-information/) | `official_program_page` | Added as `KWRK-000144` |
| [supplied page](https://seedfund.nsf.gov/apply/full-proposal/) | [Key information for submitting a full SBIR/STTR proposal to NSF](https://seedfund.nsf.gov/apply/full-proposal/) | `official_program_page` | Added as `KWRK-000145` |
| [supplied page](https://www2.census.gov/library/working-papers/2026/adrm/ces/CES-WP-26-25.pdf) | [The Microstructure of AI Diffusion: Evidence from Firms, Business Functions, and Worker Tasks](https://www2.census.gov/library/working-papers/2026/adrm/ces/CES-WP-26-25.pdf) | `government_working_paper` | Added as `KWRK-000146` |
| [supplied page](https://www.census.gov/library/stories/2026/05/ai-use-businesses.html) | [Large Firms With at Least 20 Employees Biggest AI Users](https://www.census.gov/library/stories/2026/05/ai-use-businesses.html) | `government_publication` | Added as `KWRK-000147` |
| [supplied page](https://www.gao.gov/assets/gao-26-107828.pdf) | [Artificial Intelligence: Uses and Risks for Small Business Contracting and Innovation Research](https://www.gao.gov/assets/gao-26-107828.pdf) | `government_report` | Added as `KWRK-000148` |
| [supplied page](https://www.priv.gc.ca/en/opc-actions-and-decisions/research/explore-privacy-research/2026/por_bus_2025-26/) | [2025-2026 Survey of Canadian businesses on privacy-related issues](https://www.priv.gc.ca/en/opc-actions-and-decisions/research/explore-privacy-research/2026/por_bus_2025-26/) | `government_commissioned_public_opinion_research` | Added as `KWRK-000149` |
| [supplied page](https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2025/m04/cisco-2025-data-privacy-benchmark-study-privacy-landscape-grows-increasingly-complex-in-the-age-of-ai.html) | [Cisco’s 2025 Data Privacy Benchmark Study: Privacy landscape grows increasingly complex in the age of AI](https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2025/m04/cisco-2025-data-privacy-benchmark-study-privacy-landscape-grows-increasingly-complex-in-the-age-of-ai.html) | `vendor_study_press_release` | Added as `KWRK-000150` |
| [supplied page](https://developers.openai.com/api/docs/guides/your-data) | [Data controls in the OpenAI platform](https://developers.openai.com/api/docs/guides/your-data) | `vendor_documentation` | Added as `KWRK-000151` |
| [supplied page](https://ai.google.dev/gemini-api/terms.md) | [Gemini API Additional Terms of Service](https://ai.google.dev/gemini-api/terms.md) | `vendor_terms` | Added as `KWRK-000152` |
| [supplied page](https://ai.google.dev/gemini-api/docs/pricing) | [Gemini Developer API pricing](https://ai.google.dev/gemini-api/docs/pricing) | `vendor_documentation` | Added as `KWRK-000153` |
| [supplied page](https://ai.google.dev/gemini-api/docs/optimization) | [Gemini API optimization and inference](https://ai.google.dev/gemini-api/docs/optimization) | `vendor_documentation` | Added as `KWRK-000154` |
| [supplied page](https://arxiv.org/html/2607.13080v1) | [Inference Economics of Enterprise Coding Agents: A Case Study of Cloud vs. On-Premise LLMs](https://arxiv.org/abs/2607.13080v1) | `independent_research_preprint` | Added as `KWRK-000155` |
| [supplied page](https://arxiv.org/html/2609.08307v1) | [A Measurement Study of LLM Inference Trade-offs Across Edge Continuum Hardware](https://arxiv.org/abs/2609.08307v1) | `independent_research_preprint` | Added as `KWRK-000156` |
| [supplied page](https://docs.nvidia.com/local-ai/nvpair/getting-started/) | [Getting Started with NVIDIA Personal AI Router](https://docs.nvidia.com/local-ai/nvpair/getting-started/) | `vendor_documentation` | Added as `KWRK-000157` |
| [supplied page](https://developer.nvidia.com/blog/nvidia-pair-virtual-inference-router-expands-available-compute-on-your-local-network/) | [NVIDIA PAIR Virtual Inference Router Expands Available Compute on Your Local Network](https://developer.nvidia.com/blog/nvidia-pair-virtual-inference-router-expands-available-compute-on-your-local-network/) | `vendor_blog` | Added as `KWRK-000158` |
| [supplied page](https://localai.io/docs/features/distributed-mode/index.print.html) | [Distributed Mode](https://localai.io/docs/features/distributed-mode/index.print.html) | `maintainer_documentation` | Added as `KWRK-000159` |
| [supplied page](https://github.com/mudler/LocalAI/blob/master/docs/content/getting-started/troubleshooting.md) | [LocalAI Troubleshooting documentation](https://github.com/mudler/LocalAI/blob/89a0955b5b2dc2ccbcf7706b1bb64cd13f10ee97/docs/content/getting-started/troubleshooting.md) | `software_repository_documentation` | Added as `KWRK-000160` |
| [supplied page](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md) | [llama.cpp RPC backend documentation](https://github.com/ggml-org/llama.cpp/blob/9c2e0e491a822adae1f0b1c831adb4160057d24f/tools/rpc/README.md) | `software_repository_documentation` | Added as `KWRK-000161` |
| [supplied page](https://github.com/exo-explore/exo/blob/main/README.md) | [exo](https://github.com/exo-explore/exo/tree/21a54c5ea0230a3bec1e1a786d200126c7e34ec6) | `software_repository` | Added as `KWRK-000162` |
| [supplied page](https://github.com/b4rtaz/distributed-llama) | [distributed-llama](https://github.com/b4rtaz/distributed-llama/tree/59af889085c6c0316a4524a92b42f04caa4bcc6d) | `software_repository` | Added as `KWRK-000163` |
| [supplied page](https://docs.gpustack.ai/latest/faq/) | [FAQ](https://docs.gpustack.ai/latest/faq/) | `maintainer_documentation` | Added as `KWRK-000164` |
| [supplied page](https://docs.gpustack.ai/latest/tutorials/running-distributed-vllm-with-multiprocessing/) | [Running Distributed vLLM with the MultiProcessing Backend](https://docs.gpustack.ai/latest/tutorials/running-distributed-vllm-with-multiprocessing/) | `maintainer_documentation` | Added as `KWRK-000165` |
| [supplied page](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.5/pdf/managing_and_monitoring_models/Red_Hat_OpenShift_AI_Self-Managed-3.5-Managing_and_monitoring_models-en-US.pdf) | [Red Hat OpenShift AI Self-Managed 3.5: Managing and monitoring models](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.5/pdf/managing_and_monitoring_models/Red_Hat_OpenShift_AI_Self-Managed-3.5-Managing_and_monitoring_models-en-US.pdf) | `vendor_documentation` | Added as `KWRK-000166` |
| [supplied page](https://www.locailabs.com/ai-assistants) | [Official Information for AI Assistants](https://www.locailabs.com/ai-assistants) | `vendor_page` | Added as `KWRK-000167` |
| [supplied page](https://www.locailabs.com/local-ai) | [What is Local AI? On-Prem AI Explained](https://www.locailabs.com/local-ai) | `vendor_explainer` | Added as `KWRK-000168` |
| [supplied page](https://github.com/locai-co-uk/locai-link) | [locai-link](https://github.com/locai-co-uk/locai-link/tree/1ac5bed23f45dd0edd779ad89b941c5e87dfe7b7) | `software_repository` | Added as `KWRK-000169` |
| [supplied page](https://www.dell.com/en-us/dt/corporate/newsroom/announcements/detailpage.press-releases~usa~2026~05~dell-technologies-delivers-production-ready-agentic-ai-from-deskside-to-data-center.htm) | [Dell Technologies Delivers Production-Ready Agentic AI from Deskside to Data Center](https://www.dell.com/en-us/dt/corporate/newsroom/announcements/detailpage.press-releases~usa~2026~05~dell-technologies-delivers-production-ready-agentic-ai-from-deskside-to-data-center.htm) | `vendor_press_release` | Added as `KWRK-000170` |
| [supplied page](https://docs.nvidia.com/dgx/dgx-spark/hardware.html) | [Hardware Overview](https://docs.nvidia.com/dgx/dgx-spark/hardware.html) | `vendor_documentation` | Added as `KWRK-000171` |
| [supplied page](https://github.com/mikeshallop/caic) | [cAIc](https://github.com/mikeshallop/caic/tree/aecd3330fd0f7826dc77fda66155c89d067f47ca) | `software_repository` | Added as `KWRK-000172` |
| [supplied page](https://github.com/janit/viiwork) | [viiwork](https://github.com/janit/viiwork/tree/6aab7dc94f3863514f5214ea5c10ea6bf13ec4dd) | `software_repository` | Added as `KWRK-000173` |
| [supplied page](https://github.com/Kikobuf/hivelink) | [hivelink](https://github.com/Kikobuf/hivelink/tree/2621fe1a1468721b97f2cb530cced28da5367d97) | `software_repository` | Added as `KWRK-000174` |
| [supplied page](https://arxiv.org/abs/2606.21428) | [Does Mixture-of-Experts Actually Help Inference on Consumer and Edge Hardware? An Empirical Study](https://arxiv.org/abs/2606.21428v3) | `independent_research_preprint` | Already present: `KWRK-000106` |
| [supplied page](https://seedfund.nsf.gov/critical-information/) | [Critical Information](https://seedfund.nsf.gov/critical-information/) | `official_program_page` | Quarantined: page body unavailable |

## Counts and identity checks

- 35 new public URLs reviewed: 5 NSF pages and 30 additional sources.
- The 3 paper pointers resolve to 2 new arXiv Works and 1 existing Work; submitted arXiv versions remain pinned in `source_url`.
- The 32 nonpaper pointers resolve to 31 new Works and 1 quarantined NSF page.
- 33 new Works were added (`KWRK-000142`–`KWRK-000174`); 1 source was already represented as `KWRK-000106`; 1 was quarantined.
- The Works IDs and input URLs are deduplicated; GitHub repository/file snapshots use verified commit SHAs. Mutable web documentation keeps the supplied canonical page URL and a verification date in the audit/notes.
- No private issue crosswalk or private provenance was supplied or copied. This is bounded metadata intake, not complete world-literature coverage; PR review threads and the inaccessible Notion corpus remain gaps.

## Incremental update contract

For follow-on maintenance, retrieve deltas from each source using its revision or update time when available. Finish every page of a paginated result before advancing its checkpoint, and record page counts plus the terminal cursor or page marker. For issue/comment sources, detect edits with each public comment ID and a SHA-256 hash of its complete normalized content; keep private issue provenance outside this public repository. Record the source revision/update-time boundary and the last verified successful checkpoint. Advance that checkpoint only after retrieval, pagination, canonical-identity checks, and audit validation all succeed; otherwise retry from the prior checkpoint. Resolve aliases in order: DOI, arXiv ID without version, title plus first author, then stable URL or repository plus commit for nonpaper material. Preserve arXiv versions separately. Add a canonical Work only when primary metadata and deduplication checks pass; otherwise retain the lead as quarantined. Identity alone does not create findings, claims, or adoption. This contract is a manual update procedure; it adds no new service or scheduled job.

## Semantic boundaries

- Research findings added to articles: no.
- Claims added or accepted: 0.
- Adoption relationships asserted: no.
- Independent results inferred from vendor material: no.
