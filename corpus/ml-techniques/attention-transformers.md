---
title: Attention and the Transformer architecture, internals
pillar: ml-techniques
method: deep-research
date: 2026-07-01
sources: 12
confidence: high
---

## What it is

Attention is a learned, content-addressed lookup over a set of vectors. Each position in a sequence emits a *query*; every position also exposes a *key* and a *value*. The query is compared against all keys to produce compatibility scores, those scores are normalized into weights, and the output for that position is the weighted mix of the values. The Transformer builds its entire representation stack out of this one primitive plus a position-wise feed-forward network, and it was introduced specifically to *dispense with recurrence and convolutions entirely* [1].

The exact mechanism is scaled dot-product attention:

```
Attention(Q, K, V) = softmax(QKᵀ / √d_k) · V
```

Q and K have dimension d_k, V has dimension d_v [1]. Read the shapes: `QKᵀ` is an n×n matrix of query-key dot products (one score per ordered pair of positions), the softmax normalizes each row into a probability distribution, and multiplying by V returns, for each position, a *convex combination* of the value vectors — a softmax-weighted average whose weights are the query-key compatibilities [1]. Nothing more exotic is happening: attention is a differentiable, data-dependent averaging operation.

## When to reach for it

You almost never implement this primitive yourself anymore; you reach for it by choosing an architecture. The decision that matters is *why* attention displaced the recurrent and convolutional layers it replaced, because that reasoning tells you when it is the right tool and when its costs bite.

The paper's own "Why Self-Attention" table is the argument [1]. A self-attention layer connects any two positions in **O(1) sequential operations** with a **maximum path length of O(1)** between them, at a per-layer cost of **O(n²·d)**. A recurrent layer costs **O(n·d²)** per layer but needs **O(n) sequential operations** and has an **O(n) path length** between distant positions [1]. Two consequences follow. First, the constant path length makes long-range dependencies structurally easy to learn — the gradient signal between two positions traverses one hop, not n. Second, and more decisive in practice, O(1) sequential operations mean the whole sequence is processed in parallel; an RNN's O(n) sequential dependency is the property that structurally forbids parallelizing across the time axis [1]. Attention traded a *quadratic* per-layer cost for *full parallelism*, and on modern accelerators that was overwhelmingly the right trade.

Reach for attention when you need global, content-based mixing and can afford (or engineer around) the n² cost. The regime where it hurts is exactly the one the complexity table hides: the O(n²·d) vs O(n·d²) crossover depends on the n-vs-d ratio, and for long contexts the n² term dominates everything. That single term is why nearly all production work since 2020 attacks the *cost* of attention rather than the formula.

## How it works

**The √d_k scaling is not cosmetic.** Assume the components of a query and key are independent random variables with mean 0 and variance 1. Then their dot product `q·k = Σ qᵢkᵢ` has mean 0 and **variance d_k** [1]. So as d_k grows, the raw logits fed into softmax grow in magnitude proportional to √d_k. Large-magnitude logits push softmax into a saturated regime where one weight approaches 1, the rest approach 0, and the gradient of softmax with respect to its inputs becomes vanishingly small — the paper states this rationale directly in a footnote [1]. Dividing by √d_k rescales the logit variance back to ~1, keeping the softmax in its responsive region and the gradients healthy. This is also why the authors chose dot-product attention over additive (Bahdanau) attention: the two are similar in theoretical complexity, but dot-product attention maps onto highly optimized matrix multiplication and is far faster and more memory-efficient; additive attention actually *outperforms* unscaled dot-product for large d_k — which is precisely the gap the √d_k scaling closes [1].

One honest caveat: the variance argument assumes unit-variance, zero-mean, independent query and key components. That holds at initialization by construction, but learned projections after training need not preserve it. How tightly the normalization argument holds for real trained weights is not established by the primary source — treat √d_k as a well-motivated default, not a theorem about converged models.

**Multi-head attention** runs h attention functions in parallel instead of one. The Transformer base uses **h = 8** heads with **d_k = d_v = d_model / h = 64** and **d_model = 512** [1]. Q, K, V are each linearly projected into h lower-dimensional subspaces, attention runs independently in each, and the h outputs are concatenated and projected back. The motivation is a limitation of the single head: a lone softmax-weighted average *inhibits* attending to information from multiple representation subspaces at once, because averaging collapses them; multiple heads let the model jointly attend to different subspaces at different positions [1][4]. Because each head operates at d_model/h instead of d_model, total compute stays close to that of a single full-dimension head — you get the expressiveness of several attention patterns for roughly the price of one [1].

**Three placements, one mechanism.** The Transformer wires the same operation three ways [1]:
- *Encoder self-attention*: Q, K, V all come from the previous encoder layer — every position attends to every position.
- *Decoder masked self-attention*: identical, but future positions are set to **−∞** before the softmax, which zeroes their weights and preserves autoregression (a position cannot see tokens it hasn't generated yet) [1].
- *Encoder-decoder attention*: queries come from the decoder, keys and values from the encoder output — this is where the decoder reads the source sequence [1].

**Position has to be injected**, because self-attention is permutation-invariant: shuffle the input positions and the set of outputs is merely shuffled, since the mechanism sees an unordered set. The original paper adds fixed sinusoidal encodings, `PE(pos,2i) = sin(pos/10000^(2i/d_model))` and `PE(pos,2i+1) = cos(pos/10000^(2i/d_model))`, chosen partly so that for any fixed offset k, `PE(pos+k)` is a *linear* function of `PE(pos)` — the stated hope being that this lets the model attend by relative position [1]. That justification is partly heuristic: the paper does not empirically isolate how much the linear-offset property actually helped, and production practice later largely superseded this design (see Trade-offs).

**The other half of every layer** is a position-wise feed-forward network applied identically at each position: `FFN(x) = max(0, xW₁ + b₁)W₂ + b₂`, with inner dimension **d_ff = 2048** and input/output dimension **d_model = 512** [1]. Attention moves information *between* positions; the FFN transforms each position *independently*. The pair, stacked with residual connections and layer norm, is the whole encoder/decoder block.

## Trade-offs

The sources are complementary rather than contradictory — this is a converged area — but there is a real *design-drift* tension: the 2017 defaults have been displaced in production on two fronts, both driven by the n² cost and its inference-time consequences.

**The n² time-and-memory cost is the architecture's central scaling weakness**, and the dominant response is FlashAttention: an **IO-aware, exact** (not approximate) attention algorithm that uses tiling to avoid ever materializing the full n×n score matrix in GPU high-bandwidth memory, reducing reads/writes between HBM and on-chip SRAM [5]. It reports a **3× speedup on GPT-2** at sequence length 1K, **2.4× on Long-Range Arena**, and enables previously infeasible regimes — **Path-X (16K) at 61.4%** and **Path-256 (64K) at 63.1%** accuracy [5]. The key point is that it changes *nothing* about the math — same outputs, better memory choreography. (The internal trick that makes tiling exact is an online-softmax scheme that carries running max/sum statistics across tiles so the normalization is correct without seeing all scores at once; that mechanism lives in the full paper body, not in the NeurIPS abstract cited here, so treat it as background rather than a sourced claim.)

**At inference, the KV cache is the bottleneck.** In autoregressive decoding, the keys and values for all previous tokens are computed once and cached so each new token doesn't recompute them; the cache's footprint therefore grows **linearly with sequence length** (and with the number of layers and heads) [6], becoming a dominant memory cost for long-context or high-concurrency serving. This is the cost the original full multi-head design created, and it motivated a second displacement. **Grouped-Query Attention (GQA)** shrinks the cache by sharing key/value heads across *groups* of query heads — an intermediate point between full MHA (one KV head per query head) and Multi-Query Attention (a single shared KV head) [7]. Uptrained GQA reaches quality close to MHA at speed comparable to MQA, and existing multi-head checkpoints can be converted using only **~5% of original pre-training compute** [7]. GQA was introduced because MQA can cause **quality degradation** [7]; the paper also reports *training instability*, but that finding is scoped in its appendix to fine-tuning with long-input tasks, not offered as the headline motivation — so treat quality degradation as the primary reason and instability as a narrower, conditional one. **Llama 3 70B** uses 64 query heads and 8 KV heads, an 8× KV-cache reduction versus the equivalent 64-KV-head MHA; Llama 2 70B was the first major model to adopt GQA [8].

**RoPE displaced sinusoidal encodings.** Rotary Position Embedding encodes absolute position with a *rotation matrix* and thereby folds explicit **relative** position dependency directly into the self-attention dot product — multiplicative rather than additive [9]. Its stated properties are sequence-length flexibility, inter-token dependency that *decays* with relative distance, and compatibility with linear attention [9][10]. Modern LLMs overwhelmingly use RoPE, which quietly reverses the paper's original additive-sinusoidal choice.

The shared blind spot across every retrieved source: none rigorously establishes whether attention's learned weights are *semantically* "attending" versus performing a statistically convenient mixing. The closest mechanistic account is the induction head (below), and even that is only causally established at small scale.

## In practice

The cleanest evidence that attention implements a legible algorithm — not just a useful blur — is the **induction head**. Anthropic's mechanistic-interpretability work identifies a two-layer circuit: a *previous-token head* in an earlier layer feeds a later *induction head* via composition, and together they implement pattern completion `[A][B]…[A] → [B]` — find an earlier occurrence of the current token A, look at what followed it (B), and predict B [11][12]. The work argues induction heads form in an abrupt training **phase change** that coincides with a sharp jump in in-context-learning ability, and presents **six lines of evidence** that they are the mechanistic source of most in-context learning [11].

The scope discipline here is the useful part for an engineer: the evidence is **causal** for small attention-only models and only **correlational** for larger models with MLPs [11][12]. Whether induction heads remain *the* dominant in-context-learning mechanism at frontier scale, or are one contributor among many, is not settled — a good reminder that a clean circuit story validated at small scale is a hypothesis, not a proof, about the model on your GPU. Still, if you want a concrete handle on what a head can *be*, the previous-token → induction-head pair is the canonical worked example: two attention layers composing into a copy-the-continuation algorithm, extracted and verified, not merely visualized.

## Further reading

1. Vaswani et al. — Attention Is All You Need (2017), arXiv HTML v7 (formulas, √d_k footnote, complexity table, sinusoidal PE, FFN, multi-head config) — https://arxiv.org/html/1706.03762v7
2. Vaswani et al. — Attention Is All You Need, NeurIPS 2017 official PDF — https://papers.neurips.cc/paper/7181-attention-is-all-you-need.pdf
3. Scaled Dot-Product Attention Mechanism (variance / softmax-saturation walkthrough) — APXML — https://apxml.com/courses/introduction-to-transformer-models/chapter-2-self-attention-multi-head-attention/scaled-dot-product-attention
4. Multi-Head Attention — Dive into Deep Learning (d2l.ai) — https://d2l.ai/chapter_attention-mechanisms-and-transformers/multihead-attention.html
5. Dao et al. — FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness (NeurIPS 2022) — https://proceedings.neurips.cc/paper_files/paper/2022/hash/67d57c32e20fd0a7a302cb81d36e40d5-Abstract-Conference.html
6. Transformer KV Cache: Methods & Limits — Emergent Mind — https://www.emergentmind.com/topics/transformer-kv-cache
7. Ainslie et al. — GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints (2023) — https://arxiv.org/abs/2305.13245
8. Grouped-Query Attention (GQA): shrinking the KV cache (Llama 2 head counts) — ZeroEntropy — https://zeroentropy.dev/concepts/grouped-query-attention/
9. Su et al. — RoFormer: Enhanced Transformer with Rotary Position Embedding (2021) — https://arxiv.org/abs/2104.09864
10. Rotary Embeddings: A Relative Revolution — EleutherAI blog — https://blog.eleuther.ai/rotary-embeddings/
11. Olsson et al. — In-context Learning and Induction Heads (Anthropic, 2022) — https://arxiv.org/pdf/2209.11895
12. Induction Heads and In-Context Learning — Learn Mechanistic Interpretability — https://learnmechinterp.com/topics/induction-heads/
