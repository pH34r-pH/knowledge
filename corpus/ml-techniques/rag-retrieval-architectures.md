---
title: RAG retrieval architectures — vector, graph, and hybrid, and when each stops working
pillar: ml-techniques
method: storm
date: 2026-07-01
sources: 20
confidence: medium
---

## What it is

The retrieval half of RAG is a single job — put the right evidence in the model's context window — but it decomposes into two problems that were solved separately and are still, mostly, solved separately.

The first is **semantic matching**: given a query, score every candidate passage by relevance. Dense Passage Retrieval (DPR) turned this into a learned inner product — a dual encoder maps queries and passages into the same vector space, and relevance is `q·p` — and beat a strong Lucene-BM25 baseline by **9–19% absolute in top-20 retrieval accuracy** across open-domain QA [1][2]. The second is **scale**: an exact inner-product search over billions of vectors is infeasible, so approximate nearest-neighbor (ANN) indexes trade a sliver of recall for orders of magnitude of speed. HNSW gives ANN with logarithmic search complexity via layered navigable-small-world proximity graphs [3][4]; FAISS pushes the same idea to billion-scale, sub-millisecond GPU search using IVF+PQ quantization [5].

These two results compose cleanly, and that composition is the reason dense retrieval is the default: because relevance *is* an inner product, retrieval *is* maximum-inner-product search, which is exactly what ANN indexes are built to do. The whole dense pipeline is two primitives — one embedding model, one ANN index. Graph and hybrid architectures are what you add when the dense core provably runs out of mechanism, and the interesting question is not "which is best" but "on which query distribution does each stop working."

## When to reach for it

- **Dense (or hybrid) + reranker is the default.** Fact-seeking and single-hop "find documents about X" queries — the bulk of production RAG — are semantic-similarity problems, and that is what bi-encoders are trained for. Reach here first for almost everything.
- **Graph** earns its cost on two specific query classes: **multi-hop relational chains** whose evidence is never co-located in one chunk, and **global sensemaking / query-focused summarization** questions that are properties of the whole corpus rather than any passage [8]. On simple single-hop queries, graph adds only indexing overhead — a point the graph camp itself concedes.
- **Long-context (stuff everything in the window)** is viable only when the working set stays *left of the inverted-U* (below, in How it works) — small enough that you are not injecting distractors [17][18].

The honest framing is a router, not a winner: dense-hybrid+rerank as the default, graph for provable multi-hop/global, long-context for small working sets.

## How it works

**Semantic matching, and where it structurally fails.** DPR's dual encoder is the mechanism: two BERT towers, contrastive training with in-batch negatives, relevance as a dot product [1]. This is superb on semantic similarity and fails *structurally* — not by mis-tuning — when relevance requires reasoning rather than surface similarity. BRIGHT (ICLR 2025) is the clean demonstration: strong embedding models that post high scores on standard benchmarks collapse to **~18.3 nDCG@10** on reasoning-intensive retrieval [6]. (The often-quoted "~59.0" contrast figure is that model's *MTEB leaderboard average*, not a BEIR nDCG@10 — the point is the gap between easy-benchmark strength and reasoning-retrieval collapse, not a same-metric before/after.) MTEB's own conclusion reinforces the ceiling: no single embedding method dominates all tasks [7]. So the defensible dense claim is "best default," not "universal winner."

The failure has a precise shape. Vector top-k has **no mechanism** for (a) a multi-hop chain whose links live in different chunks, or (b) an aggregate property of the corpus. Raising `k` does not help — you add more locally-similar passages, never the missing hop and never a summary of the whole [8]. This is a capability the geometry categorically lacks, not a region you tune into.

**Graph fills exactly that gap.** Microsoft's GraphRAG mechanism: an LLM extracts an entity–relationship graph from chunks; Leiden hierarchical community detection clusters related entities; community summaries are pre-generated per level. A global query is then answered map-reduce over community summaries instead of raw chunks [8][9]. On a **~1M-token podcast corpus and a ~1.7M-token news corpus**, GraphRAG beat naive vector RAG on comprehensiveness (**72–83% win rate**) and on diversity (**62–71% on news, 75–82% on podcast**), and root-level community summarization used **9–43× fewer query-time tokens** than summarizing source text [8]. It also produces an auditable trail: each hop is an explicit typed edge, not an opaque similarity score.

**The multi-hop advantage replicates across independent groups.** HippoRAG (NeurIPS'24) builds a schemaless OpenIE knowledge graph and runs Personalized PageRank seeded on query concepts — single-step multi-hop retrieval that beats prior SOTA by **up to 20%** while being **10–30× cheaper and 6–13× faster** than iterative retrieval (IRCoT) [10][11]. The independent 2026 "Do We Still Need GraphRAG?" benchmark — not a pro-graph paper — reports GraphRAG beating dense retrieval by **+27.23 average across HotpotQA / 2Wiki / MuSiQue under single-shot inference**, while dense's edge on general QA is a marginal **+0.47** [12]. Carry that "single-shot" qualifier: the paper's central finding is that **agentic (iterative) search substantially narrows** the dense-vs-graph gap, so the +27.23 headline is the single-shot ceiling, not a universal law.

**The cost objection was real, and was mostly engineered away.** Full GraphRAG's upfront LLM summarization is expensive. LazyGraphRAG defers all LLM use to query time and uses cheap NLP noun-phrase co-occurrence at index time, giving indexing cost identical to vector RAG (**~0.1%** of full GraphRAG) and **>700× lower global-query cost** at comparable or better quality [13]. That this optimization exists concedes the original cost complaint was legitimate.

**The lever that dominates the architecture label: recall engineering.** BM25 is not a legacy baseline you outgrow. On BEIR (18 datasets), early dense dual-encoders *underperformed BM25 out-of-domain*, because lexical matching generalizes to unseen vocabulary, IDs, and rare tokens where in-domain-trained embeddings silently fail [14]. Dense and BM25 fail on **disjoint** query sets — that disjointness is the mechanistic reason hybrid raises recall, and why every serious stack keeps BM25.

Two mechanisms make hybrid+rerank work:
- **Reciprocal Rank Fusion (RRF)** merges dense and sparse result lists by rank alone: `score(d) = Σ 1/(k + rank_i(d))`, with `k ≈ 60` [16]. Fusing by rank sidesteps the scale mismatch between BM25's unbounded scores and cosine's [0,1] range with near-zero tuning — a robust default.
- **A cross-encoder reranker** re-scores the fused candidates by jointly attending to query and passage (no independent embedding), which is why it is the single largest quality lever. On BEIR, reranking / late-interaction models like ColBERT achieve the best average zero-shot performance, at higher compute [14].

Anthropic's Contextual Retrieval ablation on a fixed corpus stacks these additively: contextual embeddings alone cut top-20 retrieval failures **35% (5.7% → 3.7%)**; adding contextual BM25 reached **49% (→ 2.9%)**; adding a cross-encoder reranker reached **67% (→ 1.9%)** [15]. The reranker step is the largest single marginal jump (49% → 67%), which is why the pragmatist locates the credit in the reranker rather than the choice of base retriever.

**Long-context is not free retrieval.** Three results give it a failure taxonomy. OP-RAG (NVIDIA) shows answer quality vs number of retrieved chunks is an **inverted-U** — past a sweet spot, more context injects distractors and *hurts* — and order-preserving retrieval beats full-context stuffing with far fewer tokens [17]. Databricks shows accuracy is **non-monotonic in context length** (Llama-3.1-405B degrades after ~32K tokens, GPT-4-0125 after ~64K) [18]. "Lost in the Middle" shows a **U-shaped positional bias**: accuracy drops sharply when the relevant passage sits in the middle versus at the ends [19]. Long context still needs retrieval to *select and order* chunks.

## Trade-offs

This topic's value is that three credible camps produce results that are each true on the slice they measured and do not reconcile against a single held-out workload. The disagreements are about scope, not correctness.

**Clash 1 — is graph a marginal patch or a structural necessity?** The dense camp frames graph as a targeted patch on a dense core that "already delivers 80% of retrieval quality." The graph camp denies the framing: the failure is a whole capability vector similarity lacks, not a tunable region. The evidence adjudicates *by query type*: on general/single-hop QA, dense's own edge is marginal (**+0.47**) and graph adds only indexing cost — both camps concede this. On multi-hop QA, graph's gain is large (**+27.23** single-shot; HippoRAG up to 20%). So "marginal patch" is true for the majority distribution and false for the multi-hop tail. The real dispute is *which distribution is "the real workload."*

**Clash 2 — does quality come from the base retriever or the reranker?** The dense camp treats the embedding model as load-bearing. The pragmatist relocates the credit to the reranker, and Anthropic's ablation supports the pragmatist ordering — the cross-encoder step adds the largest marginal failure-rate cut [15]. Reconciliation: dense is load-bearing for *candidate generation*, but the top *marginal* lever is a cross-encoder rerank, not a better bi-encoder.

**Clash 3 — does long-context threaten RAG at all?** Self-Route (Google DeepMind / UMich) concedes long-context consistently beats RAG on **average quality when sufficiently resourced** — a genuine quality loss for RAG [20]. OP-RAG and Databricks push back that *naive* long-context degrades via the inverted-U and non-monotonic accuracy [17][18]. The coherent-but-hedged synthesis: RAG's edge is **cost, not quality**, and long-context wins only left of the inverted-U.

**What all three concede (so it is probably robust):** no architecture is a universal winner (MTEB, the single-hop-comparability boundary, "measure recall@k not the label"); on simple fact-seeking queries dense/hybrid and graph are comparable and graph only adds overhead; BM25 is the out-of-domain generalizer dense silently fails against (BEIR); and more context is not free — selection and ordering still matter (OP-RAG, Lost-in-the-Middle).

**The blind spot none of them close:** every result here is measured on a *static* academic corpus. None price the total cost of ownership of keeping the index correct and fresh in a live system — graph/community-summary rebuilds on every corpus mutation (a per-write tax a vector upsert avoids), LazyGraphRAG trading index cost for recurring per-query cost, embedding-model drift and re-embedding on upgrades, and multi-tenant per-document permission filtering at query time. The whole debate optimizes retrieval quality on a frozen corpus.

## In practice

The most citable worked example is Anthropic's Contextual Retrieval writeup [15], because it is a full ablation on one fixed corpus rather than a cross-paper comparison, so the deltas are attributable. The build order it validates is the router's default rung:

1. **Dense embeddings** over chunks — but prepend a short LLM-generated context blurb to each chunk before embedding (contextual embeddings), which alone cuts failures 35%.
2. **Add BM25** over the same contextualized chunks and fuse with RRF (`k ≈ 60`) — failures down to 49% reduction. This is the cheap, near-zero-tuning recall win.
3. **Add a cross-encoder reranker** over the top ~150 fused candidates, keep the top ~20 — failures down to 67% reduction, the largest single step.

Only past that, and only for the two query classes dense structurally cannot serve, do you reach for graph: HippoRAG-style PPR over an entity graph for multi-hop [10], or GraphRAG/LazyGraphRAG community summaries for global sensemaking [8][13]. And you choose long-context over retrieval only when the working set is small enough to sit left of the inverted-U [17]. Self-Route operationalizes the last decision as a self-reflection router: send to RAG first, escalate to full long-context only when RAG's answer is judged insufficient, recovering long-context quality while cutting tokens by roughly **39% (GPT-4O) to 61–65% (Gemini-1.5-Pro)** [20]. (Reported as percentages in the source; absolute per-model token counts are not given — treat any specific token figures with caution.)

The unifying rule: pick the retriever by the *query distribution you actually serve*, and spend your first engineering budget on recall (hybrid + rerank), not on the vector-vs-graph label.

## Further reading

1. Karpukhin et al. — Dense Passage Retrieval for Open-Domain Question Answering (EMNLP 2020) — https://arxiv.org/abs/2004.04906
2. Dense Passage Retrieval for Open-Domain Question Answering — ACL Anthology — https://aclanthology.org/2020.emnlp-main.550/
3. Malkov & Yashunin — Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs — https://arxiv.org/abs/1603.09320
4. HNSW — IEEE Transactions on Pattern Analysis and Machine Intelligence (2018) — https://dl.acm.org/doi/10.1109/TPAMI.2018.2889473
5. facebookresearch/faiss — A library for efficient similarity search and clustering of dense vectors — https://github.com/facebookresearch/faiss
6. BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval (ICLR 2025) — https://proceedings.iclr.cc/paper_files/paper/2025/file/7a0f8055c838df8e62329a76c7c6403d-Paper-Conference.pdf
7. Muennighoff et al. — MTEB: Massive Text Embedding Benchmark — https://arxiv.org/abs/2210.07316
8. Edge et al. (Microsoft Research) — From Local to Global: A GraphRAG Approach to Query-Focused Summarization — https://arxiv.org/html/2404.16130v2
9. From Local to Global: A Graph RAG Approach to Query-Focused Summarization — Microsoft Research publication page — https://www.microsoft.com/en-us/research/publication/from-local-to-global-a-graph-rag-approach-to-query-focused-summarization/
10. Gutiérrez et al. — HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models (NeurIPS 2024) — https://arxiv.org/abs/2405.14831
11. HippoRAG — NeurIPS 2024 proceedings (abstract & PPR multi-hop mechanism) — https://papers.nips.cc/paper_files/paper/2024/hash/6ddc001d07ca4f319af96a3024f6dbd1-Abstract-Conference.html
12. Do We Still Need GraphRAG? Benchmarking RAG and GraphRAG for Agentic Search Systems — https://arxiv.org/html/2604.09666v1
13. LazyGraphRAG: Setting a new standard for quality and cost — Microsoft Research blog — https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/
14. Thakur et al. — BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models (NeurIPS 2021) — https://arxiv.org/abs/2104.08663
15. Anthropic Engineering — Introducing Contextual Retrieval — https://www.anthropic.com/engineering/contextual-retrieval
16. OpenSearch — Introducing Reciprocal Rank Fusion for Hybrid Search — https://opensearch.org/blog/introducing-reciprocal-rank-fusion-hybrid-search/
17. In Defense of RAG in the Era of Long-Context Language Models (OP-RAG, NVIDIA) — https://arxiv.org/abs/2409.01666
18. The Long Context RAG Capabilities of OpenAI o1 and Google Gemini — Databricks — https://www.databricks.com/blog/long-context-rag-capabilities-openai-o1-and-google-gemini
19. Liu et al. — Lost in the Middle: How Language Models Use Long Contexts — https://arxiv.org/abs/2307.03172
20. Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach (Self-Route) — https://arxiv.org/abs/2407.16833
