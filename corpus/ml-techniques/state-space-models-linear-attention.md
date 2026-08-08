---
title: "State-space models and linear attention: efficient sequence alternatives"
pillar: ml-techniques
method: deep-research + storm
sources: 7
confidence: medium
date: 2026-08-07
---

# State-space models and linear attention: efficient sequence alternatives

## What it is

State-space models (SSMs) and linear-attention variants pursue the same pressure point—softmax attention’s pairwise sequence interaction—but by different operators. Linear attention rewrites attention with kernel feature maps and uses matrix associativity to reduce its stated complexity from \(O(N^2)\) to \(O(N)\).[1] An SSM instead updates a finite hidden state through a transition/input/readout recurrence; S4 is a structured parameterization of that recurrence.[2]

They should not be collapsed into one “post-Transformer” category. They share goals—longer sequences, lower decode-state cost, and efficient training/inference formulations—but have different representations of history and different quality limits.

## When to reach for it

Evaluate these families when sequence length, decode memory, or throughput is the bottleneck and the workload can tolerate a compressed recurrent state rather than arbitrary pairwise access to every prior token. They are attractive for long streams, audio, genomic data, and some long-context language workloads. Keep softmax attention as the default when broad, established model quality and direct content-addressable interaction across the whole context matter more than asymptotic savings.

This is a benchmark-and-workload decision, not an ideological one. Gated Linear Attention notes that linear attention generally underperforms ordinary softmax attention even while proposing a more expressive gated variant.[5]

## How it works

Linear attention factorizes the attention computation so a running accumulator can summarize prior keys and values. The associative reordering permits a recurrent implementation: instead of retaining every previous key/value pair, inference updates bounded summaries.[1] RetNet makes the parallel/recurrent relationship explicit by giving one retention operator parallel, recurrent, and chunkwise-recurrent computation forms.[4]

An SSM maintains a state \(h_t\) using a transition governed by the current input and produces an output from that state. Classical structured SSM work obtains efficient long-sequence computation through a carefully parameterized transition.[2] Mamba changes the important limitation: fixed SSM parameters cannot select content well. It makes selected parameters input-dependent, enabling the model to propagate or forget information according to the current token, while using a hardware-aware parallel algorithm for training.[6]

The result is not arbitrary memory. Any finite state is a compression of history, so exact retrieval of a distant, particular token remains task- and state-size-dependent. State Space Duality further argues that Transformers and SSMs are structurally closer than the usual architecture labels imply; this is a reason to compare operators and implementations rather than slogans.[7]

## Trade-offs

“Linear time” is asymptotic, not a wall-clock guarantee. GPU memory movement, scan kernels, state size, chunking, sequence distribution, and highly optimized attention kernels determine the crossover point. Mamba reports strong results and linear scaling in its evaluated settings, but that does not establish a universal replacement for Transformers.[6]

Quality comparisons also need category hygiene. Hyena uses long implicit convolutions and data-controlled gating; it is related in goal but is neither ordinary linear attention nor an SSM.[3] Retention, gated linear attention, S4, and selective SSMs likewise change different aspects of the operator. A result for one is not evidence for all.

## In practice

Benchmark prefill and decode separately. Record latency, tokens/s, memory, recall on long-context tasks, quality at ordinary and extreme lengths, and behavior under real batch sizes. If using a recurrent form, test reset, chunk-boundary, and state-serialization behavior explicitly. Choose an alternative only when its measured workload advantage offsets its maturity and tooling costs.

The useful conclusion is narrower than “attention is obsolete”: SSMs and linear operators widen the design space for long sequences. They earn adoption where their actual operator and hardware behavior match the problem.

## Further reading

1. Katharopoulos et al. — *Transformers are RNNs: Fast Autoregressive Transformers with Linear Attention* — https://arxiv.org/abs/2006.16236
2. Gu, Goel & Ré — *Efficiently Modeling Long Sequences with Structured State Spaces* — https://arxiv.org/abs/2111.00396
3. Poli et al. — *Hyena Hierarchy* — https://arxiv.org/abs/2302.10866
4. Sun et al. — *Retentive Network* — https://arxiv.org/abs/2307.08621
5. Yang et al. — *Gated Linear Attention Transformers with Hardware-Efficient Training* — https://arxiv.org/abs/2312.06635
6. Gu & Dao — *Mamba: Linear-Time Sequence Modeling with Selective State Spaces* — https://arxiv.org/abs/2312.00752v2
7. Dao & Gu — *Transformers are SSMs* — https://arxiv.org/abs/2405.21060
