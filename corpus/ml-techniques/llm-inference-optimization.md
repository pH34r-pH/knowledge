---
title: "LLM Inference Optimization: Continuous Batching, Paged KV-Cache, and Speculative Decoding"
pillar: ml-techniques
method: deep-research
date: 2026-07-01
sources: 12
confidence: high
---

## What it is

Autoregressive decoding generates one token per forward pass, and each pass reloads the entire model's weights (plus the growing KV cache) from HBM into the compute cores. The arithmetic that matters is a ratio: it takes longer to move 1 MB of weights from HBM to the cores than for the cores to do the math on that 1 MB [6][9]. Decode is therefore **memory-bandwidth-bound, not compute-bound** — a single decode stream leaves most of the GPU's FLOPs idle while the memory bus is pinned. Every optimization here is a different way of attacking that waste.

Three techniques cover the serving-cost surface:

- **Continuous batching** (Orca's iteration-level scheduling) — fixes *scheduling* waste, where a batch idles because it's pinned to its slowest member.
- **Paged KV-cache** (PagedAttention / vLLM) — fixes *memory* waste, where fragmentation and over-reservation cap how large a batch you can even fit.
- **Speculative decoding** — trades compute for latency by verifying many draft tokens in one memory-bound pass.

The first two compound and are close to free; the third is a targeted latency play with a sharp failure mode.

## When to reach for it

Reach for **continuous batching and paged KV-cache always** — they are the baseline of any modern serving stack (vLLM, TGI, TensorRT-LLM), and there is essentially no serving-scale regime where static batching or contiguous KV reservation is the right call. If you are running raw HuggingFace `generate()` in production, this is the single highest-leverage change available: vLLM reports 14–24x throughput over HF Transformers for single completions [3][4].

Reach for **speculative decoding** only in a specific regime: **latency-bound, low-concurrency, decode-heavy** workloads with predictable output — code generation, structured extraction, templated text — where a small draft model agrees with the target often [10][11][12]. It is the wrong tool for a saturated, high-throughput server, for reasons that are the exact inverse of why continuous batching wins (see Trade-offs).

## How it works

### Continuous batching

Static (request-level) batching holds the whole batch until its **longest** sequence finishes. A request that hits end-of-sequence early leaves its GPU slot idle, and no queued request can take its place until the entire batch drains [1][6]. Under real traffic with heterogeneous output lengths, this scheduling waste is large.

Orca (OSDI 2022) introduced **iteration-level scheduling**: the scheduler advances the engine one model iteration at a time, so a finished sequence's slot is freed immediately and a waiting request is admitted before the next forward pass [1][2]. The batch stays full of live work.

The subtlety is that you cannot naively batch sequences at different positions: the **attention op cannot be batched across sequences of different lengths**, because it multiplies each request's queries against that request's own K/V cache, not a shared weight tensor. Orca's answer is **selective batching** — batch the non-attention Linear/GEMM ops (which *are* a shared weight multiply) and compute attention per-request [1][2]. That is what makes a mixed-position batch executable at all.

The payoff: Orca reported **36.9x** throughput at equal latency over FasterTransformer on GPT-3 175B [1][2] — treat the exact multiplier as paper-reported rather than independently re-derived. Anyscale's isolation benchmark (OPT-13B, single A100 40GB) decomposes it: ~8x from the scheduling change alone in TGI/Ray, up to **23x** with memory optimization stacked on top [6]. The mechanism shows where the waste lives: under high generation-length variance, static batching collapses from ~200 tok/s to ~81 tok/s while continuous batching holds steady [6]. The win grows precisely with output-length heterogeneity — the real-world serving regime.

### Paged KV-cache (PagedAttention)

Continuous batching keeps the batch full, but batch size is ultimately capped by KV-cache memory. Pre-vLLM systems reserved **one contiguous KV region per request, sized to the maximum possible length**. The result: 60–80% of KV memory lost to over-reservation plus internal and external fragmentation — only 20–38% of allocated KV memory held actual tokens [3][4]. Because KV memory caps batch size, that waste is directly a throughput cap. (Treat 60–80% as the vLLM authors' 2023 comparison against non-paged baselines, not a fresh benchmark.)

PagedAttention (vLLM, SOSP 2023) borrows OS virtual-memory paging: partition each sequence's KV cache into **fixed-size blocks** (default **16 tokens**) and map logical to non-contiguous physical blocks via a **block table** [3][4][7]. External fragmentation disappears; internal fragmentation is confined to the last partially-filled block; total KV waste drops **under 4%** [3][4][7]. More usable KV memory means larger feasible batches — and because decode is memory-bound, larger batches mean proportionally more throughput. The kernel receives a `physical_block_number` per block and walks a sequence's non-contiguous blocks, with a key-cache layout `[num_blocks, num_kv_heads, head_size/x, block_size, x]` chosen for memory coalescing [7].

Because the block is the unit of sharing, PagedAttention enables **copy-on-write**: identical prompts/prefixes and parallel samples share physical blocks until divergence forces a copy. vLLM reports up to ~55% memory reduction and up to **2.2x** throughput on parallel-sampling and beam-search workloads from sharing alone [4].

End to end, vLLM (continuous batching + PagedAttention) reports **14–24x** over HF Transformers and **2.2–2.5x** over HF TGI (3.3–3.5x with parallel completions); the SOSP paper frames it as 2–4x at equal latency over FasterTransformer and Orca [3][4].

### Speculative decoding

Speculative decoding (Leviathan et al., ICML 2023) exploits the memory-bound property directly. A small **draft model** `Mq` generates `γ` tokens autoregressively; the **target model** `Mp` then runs **once, in parallel**, scoring all `γ+1` positions [5][8]. Verifying N candidate tokens costs about the same HBM round-trip as decoding one token — up to `γ+1` tokens for the price of one target pass.

The trick is that the output stays **exactly** the target's distribution. For each drafted token `x`, accept if `r < min(1, p(x)/q(x))` with `r ~ U(0,1)`; otherwise resample from the normalized residual `norm(max(0, p(x) − q(x)))` [8]. The paper proves (Appendix A.1) the result equals `p(x)` exactly — lossless, not an approximation.

Speedup is governed by the **acceptance rate** `α = E[min(p, q)]`; expected tokens per target pass is `(1 − α^(γ+1)) / (1 − α)` [8]. Higher draft-target agreement and larger `γ` raise it, until rejections dominate. Reported results: **2–3x on T5-XXL with identical outputs** — 3.4x on En-De translation (α=0.75, T5-small drafter), 3.1x on summarization (α=0.65); LaMDA 137B tested with 100M–8B drafters [8]. AWS/vLLM production runs on structured, decode-heavy prompts showed ~15 ms/token vs ~45 ms baseline (~3x) at low batch [10].

## Trade-offs

- **Continuous batching:** scheduler complexity for throughput, essentially no downside [6]. The free lunch.
- **PagedAttention:** a small per-token indirection cost (non-contiguous gather vs contiguous read) plus block-table bookkeeping, for a large memory-efficiency — hence batch-size, hence throughput — win [4][7]. The exact gather overhead was not quantified from a primary source; vLLM frames it as negligible, but a hard percentage is unconfirmed.
- **Speculative decoding:** extra compute *and* the memory of hosting a second model, for lower single-request latency — a compute-for-latency trade that only pays while the system is memory-bandwidth-bound [9][11][12].

**The critical failure mode** is the mirror image of continuous batching's win. At large batch sizes the GPU is already **compute-bound and saturated** — the very state continuous batching drives toward. There, the extra draft+verify FLOPs, especially those spent on **rejected** tokens, are pure overhead, and speculation becomes little help or slower than plain decoding [11][12]. The 3–4x figures are **best-case batch-size-1 numbers**; they shrink as batch grows toward 128 [11][12]. The exact crossover is workload-, hardware-, and draft-quality-dependent — no universal threshold exists.

Mis-tuning compounds this: a too-large speculative token count (`γ`/`k`) inflates verification cost and rejection waste — verification can consume 42–95% of execution time in benchmark sweeps [11][12]. On open-ended natural language the draft diverges, `α` drops, and the technique degrades [11][12].

There is also an unresolved **architectural tension**: continuous batching pushes toward high batch for throughput; speculative decoding wants low batch for latency. Running both well in one server is active research (MagicDec and related long-context work claim to break the tradeoff, but that work was not verified here).

## In practice

- **Default stack:** continuous batching + PagedAttention (vLLM, TGI, TensorRT-LLM) is table stakes; migrating off raw `generate()` is the biggest single win.
- **Prefix sharing:** shared system prompts and parallel sampling get ~55% memory back and up to 2.2x via copy-on-write [4] — keep shared prefixes byte-identical.
- **Speculative decoding is a scalpel:** enable it on latency-sensitive, low-concurrency, decode-heavy routes with predictable output (code, JSON extraction, templated text) [10][12]. Measure `α` on *your* traffic first; low `α` means no win.
- **Benchmark at production batch size, not batch=1** — a saturated server can see the speculative gain vanish or invert [11][12].
- **Tune `γ`/`k` deliberately** — a mis-chosen value shifts spend from useful decode to rejected-token verification, and the degradation can be large [11].

## Further reading

1. Orca: A Distributed Serving System for Transformer-Based Generative Models (OSDI 2022), Yu et al. — https://www.usenix.org/system/files/osdi22-yu.pdf
2. Orca (OSDI'22) reading notes — iteration-level scheduling & selective batching — https://paper.lingyunyang.com/reading-notes/conference/osdi-2022/orca
3. Efficient Memory Management for Large Language Model Serving with PagedAttention (SOSP 2023), Kwon et al. — https://arxiv.org/abs/2309.06180
4. vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention (official vLLM blog, June 2023) — https://vllm.ai/blog/2023-06-20-vllm
5. Fast Inference from Transformers via Speculative Decoding (ICML 2023), Leviathan et al. (abstract) — https://arxiv.org/abs/2211.17192
6. How continuous batching enables 23x throughput in LLM inference — Anyscale — https://www.anyscale.com/blog/continuous-batching-llm-inference
7. PagedAttention kernel design — official vLLM documentation (block size 16, key-cache layout) — https://docs.vllm.ai/en/latest/design/paged_attention/
8. Fast Inference from Transformers via Speculative Decoding — full text (ar5iv HTML mirror) — https://ar5iv.labs.arxiv.org/html/2211.17192
9. Speculative decoding — BentoML LLM Inference Handbook (memory-bound vs compute-bound) — https://bentoml.com/llm/inference-optimization/speculative-decoding
10. Accelerating decode-heavy LLM inference with speculative decoding on AWS Trainium and vLLM — AWS ML Blog — https://aws.amazon.com/blogs/machine-learning/accelerating-decode-heavy-llm-inference-with-speculative-decoding-on-aws-trainium-and-vllm/
11. SpecDecode-Bench: Speculative Decoding — Performance or Illusion? (vLLM benchmark, batch 1–128) — https://specdecode-bench.github.io/
12. Decode Is Memory-Bound. Speculation Is the Arbitrage — batch-size sensitivity analysis — https://www.thesoftwarefrontier.com/p/decode-is-memory-bound-speculation
