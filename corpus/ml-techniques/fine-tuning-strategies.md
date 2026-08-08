---
title: "Fine-tuning strategies: full updates, adapters, low-rank deltas, and preference objectives"
pillar: ml-techniques
method: deep-research + storm
sources: 6
confidence: high
date: 2026-08-07
---

# Fine-tuning strategies: full updates, adapters, low-rank deltas, and preference objectives

## What it is

Fine-tuning choices sit on two independent axes: **what parameters move** and **what learning signal is supplied**. Full supervised fine-tuning updates the whole base model. Many parameter-efficient fine-tuning (PEFT) methods freeze most or all of the base and train a small task-specific artifact. Preference optimization changes the objective from imitating target responses to preferring one response over another.

The right comparison is therefore not “which acronym wins?” It is how much adaptation freedom is needed, which feedback exists, how many task variants must be served, and what hardware/operational budget is acceptable.

## When to reach for it

Full fine-tuning is appropriate when substantial domain shift and a strong supervised dataset justify maintaining a complete derived checkpoint. It offers the most degrees of freedom but makes optimizer state, activations, checkpoint storage, and per-task deployment expensive.

Choose PEFT when one stable base must support many variants or training memory is constrained. LoRA freezes pretrained weights and injects trainable low-rank matrices into Transformer layers.[1] Adapters similarly retain the original network and add a small per-task module.[3] Neither paper establishes that PEFT matches full tuning on every model, rank, and distribution.

Use preference optimization when the available signal is a ranking or comparison rather than a single target answer. Environment-reward optimization is a related but distinct reinforcement-learning setting. Preference optimization does not itself establish truthfulness, safety, or broad competence; those remain evaluation questions.

## How it works

Full fine-tuning backpropagates through every parameter. PEFT constrains the update. LoRA represents a weight change with low-rank factors, reducing trainable state while retaining a frozen base.[1] QLoRA adds a frozen 4-bit quantized base and backpropagates into LoRA adapters, targeting a smaller memory footprint.[2] DoRA decomposes pretrained weights into magnitude and direction and applies low-rank adaptation to direction.[4]

The objective axis is separate. Supervised fine-tuning maximizes likelihood of demonstrations. Conventional RLHF collects demonstrations, then ranked outputs, fits a reward signal, and performs reinforcement learning from that feedback.[5] DPO derives a direct preference objective expressed as a classification loss, avoiding the standard reward-model-plus-online-RL pipeline in its cited formulation.[6]

## Trade-offs

PEFT makes multi-tenant storage and experimentation easier, but adapter rank, placement, quantization, and merge behavior affect quality and serving. QLoRA’s reported preservation of task performance and LoRA’s parity claims are evaluated results, not deployment guarantees.[1][2] Full tuning can better absorb large shifts but is harder to reproduce and compare fairly.

DPO is simpler than PPO-style RLHF for the paper’s setting, but not a universal replacement where online exploration, delayed reward, or multi-turn credit assignment matters. Evaluate task quality, preference win rate, safety behavior, regressions, calibration, training memory, and serving latency—not one chat benchmark.

## In practice

Begin with the smallest mutable surface that can pass a held-out evaluation: prompting or retrieval, then a PEFT pilot, then full tuning only if the gap warrants it. Version the base, data, training recipe, adapter, and evaluator together. Keep preference data separate from test data and audit how labelers, judges, and reward models bias the learned behavior.

Run an ablation before treating a tuning run as a model improvement. Compare the untouched base with the same prompt, a retrieval or prompt baseline if relevant, and the proposed update under equal decoding and evaluation budgets. Report task-level failures as well as aggregate scores: a small mean gain can hide regressions on safety, formatting, rare languages, or long inputs that matter to the intended deployment.

Deployment also changes the decision. Multiple adapters can be versioned, routed, and rolled back independently, whereas a full derived checkpoint carries a larger distribution and rollback unit. Conversely, a complicated adapter stack can obscure provenance and serving behavior. Choose the operational unit you are prepared to evaluate and retire, not merely the method that fits in one training run.

## Further reading

1. Hu et al. — *LoRA* — https://arxiv.org/abs/2106.09685
2. Dettmers et al. — *QLoRA* — https://arxiv.org/abs/2305.14314
3. Houlsby et al. — *Parameter-Efficient Transfer Learning for NLP* — https://arxiv.org/abs/1902.00751
4. Liu et al. — *DoRA* — https://arxiv.org/abs/2402.09353
5. Ouyang et al. — *Training Language Models to Follow Instructions with Human Feedback* — https://arxiv.org/abs/2203.02155
6. Rafailov et al. — *Direct Preference Optimization* — https://arxiv.org/abs/2305.18290
