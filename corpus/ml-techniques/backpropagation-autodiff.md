---
title: Backpropagation and automatic differentiation
pillar: ml-techniques
method: deep-research
date: 2026-07-01
sources: 8
confidence: high
---

## What it is

Automatic differentiation (AD) is a distinct, third way to compute derivatives of a program, sitting alongside — not inside — symbolic and numeric differentiation. The canonical survey by Baydin, Pearlmutter, Radul & Siskind sorts derivative computation into four categories: manual derivation, numerical differentiation via finite differences, symbolic differentiation via expression manipulation (computer-algebra systems such as Mathematica, Maxima, and Maple), and automatic differentiation [1]. AD is the fourth, and it is routinely confused with the other three.

The mechanistic definition is the whole point. AD computes derivatives "through accumulation of values during code execution to generate numerical derivative evaluations rather than derivative expressions" [1]. It treats your program as a trace of elementary operations, attaches known local derivative rules to each one, and propagates derivative *values* through that trace via the chain rule. The result is exact to machine precision — no approximation step — at only a small constant-factor overhead over running the function itself [1].

Backpropagation is not a separate algorithm. It is precisely reverse-mode AD applied to a function whose output is a scalar loss [1][2]. Everything the deep-learning world calls "backprop" is a special case of the reverse mode, and the reverse mode generalizes it to arbitrary programs.

## When to reach for it

Reach for reverse-mode AD whenever you need the gradient of a scalar objective with respect to a large number of inputs — the exact shape of a neural-network loss over millions or billions of parameters. This is the regime where the reverse mode's defining property pays off: the cost of the full gradient is a small multiple of the forward pass and is *independent of the number of inputs* [1][3].

That independence is what rules out the naive alternatives. Numerical differentiation costs O(n) function evaluations for an n-dimensional gradient — one perturbation per input — which is unusable when n is in the millions [1]. Symbolic differentiation is out for a different reason: it needs the model expressed as a closed-form formula and cannot handle general control flow, and it suffers "expression swell," where the derivative expression grows explosively larger than the original because the product rule duplicates shared subexpressions [1].

Forward-mode AD is the tool for the mirror-image case: few inputs, many outputs (a "tall" Jacobian, f: R → R^m). If you find yourself wanting the sensitivity of many outputs to one or two inputs, forward mode computes that in a single pass where reverse mode would need one pass per output [1][3]. The choice between modes is dictated by the shape of the Jacobian, not by taste.

## How it works

Start with the representation. AD records the computation as an *evaluation trace* — a Wengert list, after Wengert's 1964 formulation — of elementary operations, each with a known local derivative [1]. Drawn as a graph, this is the "computational graph." Crucially, AD only needs the numeric trace of the execution path that actually ran. It is therefore blind to any operation, including branches, loops, and recursion, that does not itself change a numeric value: it differentiates arbitrary programs, not just closed-form math [1]. That blindness is the source of AD's generality and, later, some of its hazards.

**Forward mode** augments every intermediate value v_i with a tangent v̇_i = ∂v_i/∂x and evaluates primals and tangents in lockstep [1]. One forward pass yields a Jacobian-vector product (a Jvp) — one *column* of the Jacobian — so the full Jacobian of f: R^n → R^m takes n passes [1][3]. The clean way to see why the chain rule falls out for free is dual numbers: evaluate with v + v̇ε where ε² = 0 but ε ≠ 0, and because each elementary op is implemented to satisfy f(v + v̇ε) = f(v) + f'(v)v̇ε, the ε-coefficient of f(v + 1ε) is exactly f'(v) [1]. This is why forward mode is implementable by plain operator overloading.

**Reverse mode** is two phases. Phase one runs the function forward, populating every intermediate and recording dependencies in the graph. Phase two propagates *adjoints* v̄_i = ∂y/∂v_i backward from output to inputs, seeded with v̄_output = ∂y/∂y = 1 [1][2]. A variable that feeds several downstream variables accumulates their contributions: v̄_0 = Σ_j v̄_j · ∂v_j/∂v_0 [1]. The adjoint is exactly the "sensitivity" of the scalar output to that variable, and one reverse sweep produces the gradient with respect to *every* input and parameter simultaneously [1][2]. That is backpropagation.

The asymmetry between the modes is fundamental, not an implementation detail. Forward mode is a *pushforward* computing Jacobian-vector products (∂f(x)·v); reverse mode is a *pullback* computing vector-Jacobian products (∂f(x)ᵀv, a VJP) [1][3]. Reverse builds the Jacobian one *row* at a time (cheap for wide, many-input/few-output Jacobians); forward builds it one column at a time (cheap for tall ones) [1][3].

The cost bound makes the tradeoff precise. To compute an m×n Jacobian, forward mode costs about n·c·ops(f) and reverse mode about m·c·ops(f), where c is a constant guaranteed below 6 and typically between 2 and 3 (Griewank & Walther 2008) [1]. For a scalar loss, m = 1: reverse mode delivers the entire gradient in roughly 2–3× the cost of the forward pass regardless of n [1]. An empirical benchmark on the Helmholtz free energy shows reverse-mode gradient time holding near 2× the function evaluation as n grows, while numerical differentiation scales roughly linearly — about 28× at n = 50 [1].

What makes AD "neither symbolic nor numeric" is its two-sided nature: it applies symbolic differentiation rules at the *level of each elementary operation* but keeps derivative *values* rather than building derivative expressions (Griewank 2003) [1]. It borrows the exactness of symbolic diff without the expression swell, and the numeric-value handling of finite differences without the truncation and round-off error.

## Trade-offs

The sources are technically convergent — this is a mature area with no factual clashes on the mechanism. The real tension is one of emphasis. The survey and the framework docs [1][2][3] present reverse mode as the near-universal answer for ML (m ≪ n), while a whole body of work exists precisely because reverse mode's two headline weaknesses bite hard at production scale.

**Memory is the price of the reverse mode.** Its efficiency is bought with storage that grows, in the worst case, in proportion to the number of operations — the depth of the computation — because the forward-pass intermediates must be retained until the backward pass consumes them [1][3]. This is the dominant *production* failure mode: out-of-memory on deep or long-sequence models. It is a resource problem, not a correctness one. The standard mitigation is gradient checkpointing (rematerialization): discard activations on the forward pass and recompute them during the backward pass, trading compute for memory and reducing storage from O(n) toward O(√n) for n uniform layers (Chen et al. 2016) [6]. The technique is a rediscovery — it originates in Griewank's 1990s checkpointing work in scientific computing [6].

**Non-differentiability is a genuine correctness hazard.** ReLU, |x|, min/max, argmax, sort, and indicator functions are non-differentiable at isolated points. Frameworks silently return a convention-chosen subgradient at those kinks. The theoretical backing for "this is fine almost everywhere" comes from Lee et al., who prove AD is correct for a broad class (PAP functions) except on a measure-zero set [7]. But that paper establishes *almost-everywhere correctness*, not the specific per-framework convention: the widely-cited detail that PyTorch returns 0 for ∂ReLU/∂x at x = 0 is correct (it is the minimum-norm subgradient) but should be confirmed against current framework source before being cited as authoritative, since it is not what [7] itself asserts. The practical risk — how often SGD actually stalls on a kink during a real run — is not quantified in the sources here; the standard mitigation when it matters is smoothing (softplus, √(x²+ε²), log-sum-exp) [7].

**On history, the popular attribution is wrong.** Reverse-mode AD was reinvented repeatedly. Linnainmaa (1970) gave the first published description of the reverse mode, and Speelpenning (1980) the first truly automatic reverse-mode implementation from general-purpose code [1][5]. Rumelhart et al. (1986) made it famous in ML but did not originate it. The survey states Werbos (1974) cast the reverse mode with dependency-ordered discrete-time variables [1]; note that Schmidhuber [5] explicitly qualifies the neural-network-specific 1974 date, placing Werbos's first NN application in 1982 "not yet in his 1974 thesis, as is sometimes claimed." The two sources agree the mode predates 1986 and was independently rediscovered across the control-theory and connectionist communities; they differ on the precise NN milestone.

The blind spot none of the retrieved sources covers well: the numerical-stability interaction between reverse-mode accumulation order and low/mixed precision (fp16/bf16). The classic vanishing/exploding-gradient pathology is a property of the *composed Jacobian*, not of the AD algorithm itself, and was out of scope for every source here.

## In practice

Production frameworks never materialize the full Jacobian. PyTorch's autograd extends the graph *during* the forward pass, stores per-op VJP rules (in `tools/autograd/derivatives.yaml`), and in the backward pass repeatedly multiplies the incoming gradient by each local VJP following the chain rule — computing the equivalent of a vector-Jacobian product without ever building the matrix [2]. This is "define-by-run": the graph is recreated on each forward pass, which is exactly what permits data-dependent Python control flow that changes shapes and ops per iteration [2].

JAX exposes the same primitives more explicitly — `jax.grad` is built on the VJP primitive, `jax.jvp` on the JVP primitive, and a gradient of f: R^n → R costs about 3× the cost of evaluating f [3]. One nuance worth flagging: JAX is trace-based, and its performant path (`jit`) traces once and caches an XLA-compiled graph rather than recreating the graph per forward pass; under `jit`, data-dependent control flow requires `lax` primitives (`cond`, `scan`) because Python control flow is traced away. Pure "define-by-run" describes eager PyTorch more faithfully than idiomatic compiled JAX [2][3].

Finally, when you hand-write a derivative (a custom kernel, a fused op), validate it with a gradient check: compare the analytic gradient against a *centered* finite difference (f(x+h) − f(x−h))/2h, whose error is O(h²) versus the one-sided O(h), using relative error |f'_a − f'_n| / max(|f'_a|, |f'_n|) [8]. Stanford's CS231n rule of thumb: > 1e-2 is probably a bug, 1e-4 to 1e-2 is uncomfortable, < 1e-4 is acceptable for objectives with kinks, and < 1e-7 is happy [8]. This is the one place finite differences remain the right tool — not to train, but to check the exact machinery against a crude independent oracle.

## Further reading

1. Baydin, Pearlmutter, Radul & Siskind — Automatic Differentiation in Machine Learning: a Survey (JMLR 18, 2018) — https://arxiv.org/abs/1502.05767
2. Overview of the PyTorch Autograd Engine — PyTorch engineering blog — https://pytorch.org/blog/overview-of-pytorch-autograd-engine/
3. The Autodiff Cookbook — JAX official documentation — https://docs.jax.dev/en/latest/notebooks/autodiff_cookbook.html
4. Forward- and reverse-mode autodiff in JAX (JVP/VJP) — JAX official documentation — https://docs.jax.dev/en/latest/jacobian-vector-products.html
5. Schmidhuber — Who Invented Backpropagation? (Linnainmaa 1970, Werbos, Speelpenning) — https://people.idsia.ch/~juergen/who-invented-backpropagation.html
6. Chen, Xu, Zhang & Guestrin — Training Deep Nets with Sublinear Memory Cost (the O(√n) checkpointing result, crediting Griewank's checkpointing origins) — https://arxiv.org/abs/1604.06174
7. Lee et al. — On Correctness of Automatic Differentiation for Non-Differentiable Functions (NeurIPS 2020) — https://arxiv.org/abs/2006.06903
8. Stanford CS231n — Neural Networks Part 3: gradient checks — https://cs231n.github.io/neural-networks-3/
