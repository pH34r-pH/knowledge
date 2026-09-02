---
title: Logarithmic and closed numerical representations for neural arithmetic
pillar: ml-techniques
method: deep-research
date: 2026-09-02
sources: 4
confidence: medium
---

## What it is

A numerical format is part of the compute architecture, not merely a container for approximate real numbers. Ordinary fixed- and floating-point formats make addition convenient and leave multiplication to a multiplier. A logarithmic number system (LNS) makes the opposite trade: if a nonzero value is represented as

```text
x = (-1)^s b^e,
```

then multiplying two values reduces to sign XOR and exponent addition. This is why logarithmic quantization repeatedly reappears in neural-network hardware: quantized products can become shifts or small integer operations instead of general multiplications [1][2].

The catch is accumulation. A matrix product is a sum of products, and addition is not just exponent addition:

```text
log_b(x + y) = max(e_x, e_y) + log_b(1 + b^(-|e_x-e_y|))
```

for positive `x` and `y`. The correction term needs a lookup, approximation, or conversion back to a linear accumulator. Miyashita et al. explicitly compare linear-domain accumulation after log-coded products with approximate log-domain accumulation [1]. The durable lesson is therefore narrower than “LNS removes multipliers”: it simplifies **product formation**, while the cost and error model of **summation** must still be specified.

A *closed-product representation* sharpens that idea. Its representable nonzero values are arranged so the product of two encoded operands has an exact code-domain description on widened product coordinates. Closure does not mean a finite-width destination can never overflow, and it does not make addition free. It means no nearest-code projection is needed between operand decoding and product formation. CurveFP is a recent example that combines this property with a finite, explicit accumulation schedule [4].

## When to reach for it

Consider a logarithmic or closed-product format when all of the following are true:

- Matrix products dominate the target workload and the product-forming path is a meaningful part of area, latency, or energy.
- The deployment stack can co-design element encoding, shared scales, accumulation, and conversion boundaries. A format evaluated only as a fake-quantization function has not established a hardware win.
- Operand distributions need multiplicative rather than additive resolution: approximately constant relative spacing is more useful than constant absolute spacing.
- You can charge the full accumulation contract, including phase coefficients, accumulator width, scale metadata, reduction, requantization, and exceptional values.

Do not reach for it merely because a low-bit accuracy table looks favorable. A representation can reduce scalar reconstruction error yet make products or accumulators harder; conversely, a mathematically elegant product rule can lose its advantage once memory traffic, scale transport, conversions, or unsupported operators are included. The relevant comparison is a crossed **representation × arithmetic implementation** experiment, not a datatype-only ablation.

## How the design space evolved

### Power-of-two logarithmic quantization

Miyashita et al. quantize neural activations and weights on a base-2 logarithmic grid. A quantized exponent can turn multiplication by one log-coded operand into a bit shift; coding both operands makes the exponent of their product the sum of two quantized exponents [1]. Their experiments also expose the main range–resolution trade-off. Base 2 is shift-friendly but coarse. A finer base such as `sqrt(2)` supplies intermediate magnitudes and reduced convolution-weight error in their evaluated CNNs; the paper reports using the same log-domain accumulation equation for this case [1].

This work is useful as a mechanism demonstration, not as a present-day language-model benchmark. Its accuracy results are on AlexNet, VGG16, and a VGG-like CIFAR-10 model. For example, the reported 5-bit `sqrt(2)` log weights are much closer to floating-point top-5 accuracy than 5-bit base-2 weights in the evaluated convolutional layers, and the end-to-end 5-bit log training run outperforms the paper's 5-bit linear baseline [1]. Those findings establish that nonuniform spacing can matter; they do not establish a universal best base or bit width.

### Arbitrary and mixed bases

The next design question is whether the base itself should be fixed. Vogel et al. evaluate powers of arbitrary log bases for post-training CNN quantization and implement log-based processing elements in an FPGA accelerator [2]. Their construction is a precedent for treating the base as a quality–hardware parameter rather than assuming powers of two by default. It also keeps the evidence boundary clear: the method is presented for pretrained networks without retraining, so it does not answer how a model adapts when trained inside the numerical format.

Xu et al. make the trade-off layer-dependent. Their BRSLog design mixes base-2 and base-`sqrt(2)` encodings because different layer weight distributions prefer different ratios [3]. The publisher abstract reports 6.4× weight compression with a 1.66% top-5 accuracy drop on 5-bit AlexNet, and a 55 nm arithmetic element whose area and power are lower than the paper's 16-bit fixed-point reference [3]. Treat these as implementation-specific results, not portable constants: model, process node, reference circuit, and supported operation all define the comparison.

Together these papers reveal a recurring tension:

- Coarser bases produce fewer coefficient classes and cheaper product realization.
- Finer or mixed bases improve local representational resolution.
- The extra classes reappear somewhere—as fixed coefficients, shifts plus adds, lookup state, or accumulation phases.

### Closed products with an explicit phase law

CurveFP makes that last cost algebraic. Each element has a sign, an exponent `e`, and a curve index `k` under a shared power-of-two block scale. With `K = 2^C` curve indices and rational radix `r = 2^(p/q)`, a nonzero magnitude has the form

```text
|x| = 2^a r^(e + k/K).
```

Multiplication is exact on widened product coordinates: XOR the signs, add the curve indices, carry any wrap into the exponent, and add the block scales [4]. No general variable-by-variable multiplier or nearest-code projection is needed at this point. Explicit requantization to a finite destination can still saturate, which is why “closed product” should not be shortened to “closed finite datatype.”

The rational radix determines how many fractional binary-exponent classes a dot product must combine. CurveFP derives

```text
H = qK / gcd(p, qK)
```

phases [4]. Products route to signed integer counts within binary exponent bins; reduction then combines the `H` fixed phase weights. This turns a vague implementation concern into a visible contract: changing the radix changes both level spacing and the number of accumulation phases. A design point cannot claim finer resolution without also reporting the induced phase cost.

## What the evidence supports

The strongest current claim is that representation and product arithmetic can be co-designed without obviously sacrificing model quality—not that closed-product formats already improve end-to-end system efficiency.

CurveFP version 2 reports that its 7-bit inference format beats tensorwise FP8 perplexity on four 7B–9B models while staying within 1.32% of the corresponding native quality [4]. In three matched 3-billion-token pretraining triplets, its 8-bit format reaches mean BF16-runtime perplexity 22.5366 versus 22.5407 for FP8; the paper correctly describes this as parity rather than statistical superiority [4]. These are author-reported results from a recent single paper and need independent replication.

Its hardware evidence is deliberately narrower. In matched 4×4 output-stationary Nangate45 tiles at 500 MHz, the tabled areas imply that the no-product-register CurveFP8 tile is 4.6% smaller than the timing-closing FP8 tile, while the registered-to-registered comparison is 4.1% smaller [4]. The paper excludes memories, interconnect, scale handling, boundary conversion, larger scheduling, and workload utilization, and it reports one physical seed. Even within version 2, the introduction gives percentages inconsistent with the raw table, abstract, and conclusion; the table-derived 4.6% and 4.1% values are the defensible ones. This is feasibility evidence for the product path, not an accelerator-level speedup or energy claim.

The earlier CNN literature supplies independent support for two pieces of the mechanism: log grids can trade multiplication for shifts/additions [1][2], and mixing bases can recover resolution at a hardware cost [1][3]. It does not independently validate CurveFP's language-model quality, phase architecture, or routed-tile result.

## Trade-offs and failure modes

**Multiplication is only one line of the bill.** Dot products need signed accumulation, sufficient headroom, phase reduction, rounding, saturation, and conversion. A paper that reports multiplier savings without an accumulator and interface contract has not priced the operator.

**Closure has a width boundary.** Exact code-domain products live on widened coordinates. A bounded output format can still underflow or saturate when requantized [4]. Tests should distinguish product-formation exactness from end-to-end dot-product error.

**Relative spacing is not uniformly beneficial.** Log grids allocate dense levels near zero and sparse absolute levels at large magnitude. That can match heavy-tailed or multiplicative distributions, but the preferred base depends on layer and tensor statistics [1][3]. Shared block scales improve local range while adding metadata and scale-selection behavior.

**Coefficient classes move complexity rather than erase it.** Base 2 maps naturally to shifts; finer rational bases require fixed non-binary phase weights or approximations. Count the phase bank, reduction precision, coefficient storage, and routing activity.

**Training and inference are different contracts.** A post-training format can rely on calibration or fixed pretrained distributions; a training format must cover forward operands, backward gradients, optimizer interaction, and checkpoint transfer. Evidence from one contract should not be silently generalized to the other.

**Hardware comparisons are easy to mischarge.** Match process, clock target, throughput, accumulator semantics, pipeline freedom, interfaces, and included system components. Area saved in a product lane may be immaterial if memory or conversion dominates the deployed workload.

## A practical evaluation protocol

1. **Freeze semantics first.** Specify zero, signs, exponent range, scale selection, rounding, saturation, exceptional values, and widened product coordinates.
2. **Derive the arithmetic contract.** Enumerate product operations, phase or coefficient classes, accumulator width, reduction, and output requantization. Exhaustively test all operand code pairs when the format is small enough.
3. **Cross representation with implementation.** Compare each candidate format using its faithful arithmetic, and include a conventional-format reference with equal accumulator semantics and throughput.
4. **Separate numerical gates.** Measure scalar reconstruction, product error, dot-product error, and full-model quality independently. A win at one level must not stand in for the next.
5. **Charge integration.** Include block-scale metadata, conversion, unsupported layers, memory traffic, interconnect, buffering, and utilization before making system claims.
6. **Scope model evidence.** Use matched seeds, data, tokens, optimizer, and runtime formats. Report parity when uncertainty does not support superiority.
7. **Publish the contradiction surface.** Give raw tables, tool versions, netlists or kernels, test vectors, and every excluded component so independent work can reproduce—or falsify—the claimed advantage.

## Further reading

1. Daisuke Miyashita, Edward H. Lee, and Boris Murmann — *Convolutional Neural Networks using Logarithmic Data Representation* (2016), arXiv:1603.01025v2 — https://arxiv.org/abs/1603.01025v2
2. Sebastian Vogel, Mengyu Liang, Andre Guntoro, Walter Stechele, and Gerd Ascheid — *Efficient hardware acceleration of CNNs using logarithmic data representation with arbitrary log-base* (ICCAD 2018), DOI:10.1145/3240765.3240803 — https://portal.fis.tum.de/en/publications/efficient-hardware-acceleration-of-cnns-using-logarithmic-data-re/
3. Jiawei Xu, Yuxiang Huan, Yi Jin, Haoming Chu, Li-Rong Zheng, and Zhuo Zou — *Base-Reconfigurable Segmented Logarithmic Quantization and Hardware Design for Deep Neural Networks* (Journal of Signal Processing Systems, 2020), DOI:10.1007/s11265-020-01557-8 — https://doi.org/10.1007/s11265-020-01557-8
4. Ye Qiao — *CurveFP: Co-Designing Numerical Representation and Product Arithmetic for Language Models* (2026), arXiv:2608.10010v2 — https://arxiv.org/abs/2608.10010v2
