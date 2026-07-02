---
title: "Preference Optimization: RLHF vs DPO vs GRPO — Mechanism, Trade-offs, and Failure Modes"
pillar: ml-techniques
method: deep-research + storm
date: 2026-07-01
sources: 13
confidence: high
---

# Preference Optimization: RLHF vs DPO vs GRPO — Mechanism, Trade-offs, and Failure Modes

## What it is

Preference optimization is the family of methods that push a language model past supervised fine-tuning (SFT) by training on *comparisons* — "this response is better than that one" — instead of, or on top of, "reproduce this target." The three methods everyone argues about sit on a single axis: **how much reinforcement-learning machinery you keep.**

- **RLHF/PPO** (InstructGPT) keeps all of it: SFT, a learned reward model, an online RL loop, and a separate critic network [1].
- **DPO** throws almost all of it away: it reparameterizes the reward into the policy itself and trains a single classification loss on preference pairs, fully offline [2].
- **GRPO** (DeepSeekMath) keeps online RL but deletes only the critic, replacing it with a group-relative baseline [3].

The honest framing up front: there is **no universal winner.** The choice is a routing decision driven by the data and reward signal you actually have. What has changed since 2022 is the burden of proof — it has flipped from "why would you use DPO instead of full RLHF?" to "what about my task justifies paying the online-RL tax at all?"

## When to reach for it

Route on your **reward signal** and your **data**, not on which paper is newest.

- **Verifiable, programmatically-checkable reward** (math answers, code that compiles and passes tests) → **GRPO / RLVR.** A rule-based checker sidesteps the learned reward model entirely, and dodging the reward model dodges reward hacking (see Trade-offs) [3][5].
- **A static preference dataset and no appetite for an RL loop** → **DPO.** But you own one condition: the data must cover the response distribution your policy will actually produce, or you inherit the off-policy failure mode below [2][8].
- **Neither** — no verifiable reward, no good preference data → **fix your SFT data first.** LIMA is the load-bearing result here: 1,000 curated SFT examples, no RL and no preference modeling at all, reached parity-or-better with strong models in a large fraction of head-to-heads [10]. For many tasks the preference-optimization slice is the last few points on top of SFT, not the main event.
- **Top of the quality curve with a real tuning budget** → **PPO.** A well-tuned PPO holds a real edge, but "well-tuned" is doing heavy lifting (see below) [4].

## How it works

**RLHF/PPO (three stages).** InstructGPT is the canonical pipeline [1]. Stage one is SFT on labeler demonstrations (~13k prompts). Stage two trains a reward model with a Bradley-Terry pairwise loss over ranked human comparisons (~33k prompts):

```
loss(θ) = −(1 / (K choose 2)) · E[ log σ( r(x, y_w) − r(x, y_l) ) ]
```

where `y_w` is the preferred and `y_l` the dispreferred completion. Stage three is PPO maximizing the PPO-ptx objective:

```
E[ r_θ(x,y) − β·log( π_RL(y|x) / π_SFT(y|x) ) ]  +  γ·E_pretrain[ log π_RL(x) ]
```

The `β` term is a **per-token KL penalty** pulling the policy back toward the SFT model so it doesn't drift into reward-model blind spots. The `γ` term mixes pretraining gradients back in; `γ = 0` recovers standard PPO [1]. PPO also needs a **separately-trained value/critic network** for advantage estimation — a second trainable model of roughly policy size. That critic, not the reward or reference models (which are inference-only), is the single biggest driver of RLHF's memory footprint [3][7]. The headline payoff: the 1.3B InstructGPT model was preferred over 175B GPT-3, a 100× parameter gap, at the cost of an "alignment tax" — regressions on public NLP benchmarks that the `γ` pretraining-mix term partially buys back [1].

**DPO (collapse two stages into one loss).** DPO's move is a proof, not a heuristic. It shows the KL-constrained RLHF objective has a *closed-form* optimal policy, which lets you reparameterize the reward in terms of the policy itself as an implicit reward `r̂(x,y) = β·log(π_θ(y|x) / π_ref(y|x))`. Substitute that into the Bradley-Terry model and preference learning collapses to a single binary-cross-entropy loss on `(prompt, chosen, rejected)` triplets [2]:

```
L = −E[ log σ( β·log(π_θ(y_w|x)/π_ref(y_w|x)) − β·log(π_θ(y_l|x)/π_ref(y_l|x)) ) ]
```

The language model is its own implicit reward model. This deletes **four** pieces of machinery at once: the reward model, the online sampling loop, the critic, and PPO's hyperparameter fragility. The paper's own claim is that DPO is "stable, performant, and computationally lightweight, eliminating the need for sampling from the LM during fine-tuning or performing significant hyperparameter tuning," and "exceeds PPO-based RLHF in ability to control sentiment... and matches or improves response quality in summarization and single-turn dialogue" [2]. `β` plays the same role it did in RLHF — it controls the KL leash to the reference.

**GRPO (drop only the critic).** GRPO keeps online RL but eliminates the critic. For each prompt it samples a **group** of G outputs, scores them, and sets each output's advantage to its *group-normalized* reward, applied to every token of that output [3]:

```
A_i = (r_i − mean(r)) / std(r)
```

This "foregoes the critic model, instead estimating the baseline from group scores, significantly reducing training resources" [3]. GRPO also moves the KL penalty **out of the reward and directly into the loss** via Schulman's unbiased positive KL estimator. DeepSeekMath's settings: 64 outputs per question, KL coefficient 0.04, policy learning rate 1e-6 [3]. The concrete gain: DeepSeekMath-RL 7B reached 88.2% on GSM8K and 51.7% on MATH (chain-of-thought, no tools), up from the Instruct model's 82.9% / 46.8%, trained only on GSM8K/MATH CoT data [3]. DeepSeek-R1 then scaled the same algorithm from a base model using **rule-based rewards only** — an accuracy reward checking correctness plus a format reward enforcing `<think></think>` tags — driving AIME 2024 pass@1 from 15.6% to 71.0% (86.7% with majority voting over 64 samples) [5]. Critically, the authors *deliberately avoided* a neural reward model because it "may suffer from reward hacking in the large-scale reinforcement learning process" [5]. That is the whole argument for verifiable rewards: at scale, a learned RM is a surface to be gamed.

## Trade-offs

**The central dispute — does DPO match PPO?** This is a genuine, unresolved clash. The DPO paper claims parity-or-better with far less machinery [2], and AI2's Tulu 3 found the two "roughly similar" with good tuning [12]. But Xu et al. (ICML 2024) directly rebut it: a well-tuned PPO "is able to surpass other alignment methods in all cases," and their CodeLlama-34B PPO beat AlphaCode-41B on CodeContest (10@1k improving 16.4% → 22.4%). They argue DPO "may find biased solutions that exploit out-of-distribution responses" [4]. The reconciliation that survives scrutiny is Ivison et al.'s measured magnitude: "PPO outperforms DPO by up to 2.5% in math and 1.2% in general domains" [6]. So both camps are partly right because they weight different task mixes — **PPO holds a real but modest edge, largest on verifiable/reasoning tasks, shrinking toward parity on general alignment.** Note the methodological wrinkle: the independent re-runs that favor PPO also lean on math/code evals, exactly where PPO's edge is biggest [4][6].

**Why PPO wins is a tuning problem.** Xu et al. isolate three factors that make PPO beat DPO: advantage normalization, large-batch training, and updating the reference model with an exponential moving average [4]. This is precisely why practitioners default to the simpler SFT+DPO — the edge is real but you have to *earn* it with tuning most teams won't do.

**DPO's owned failure mode is being offline.** Because DPO trains on a fixed preference set it never samples from, it can place probability mass on out-of-distribution responses. The 3D-Properties paper (ICLR 2025) formalizes three pathologies of offline DPO: a **D**rastic drop in rejected-response likelihood, **D**egradation into response suppression, and **D**ispersion to unseen responses, arising from the interaction of the chosen and rejected gradients [8]. The steelman — that these are "less pronounced in on-policy DPO," and that when rejected-likelihood collapses the chosen gradient fails too because they share tokens — is the argument for on-policy/iterative variants, but that specific claim lives in the full paper and I could only confirm the three properties and the gradient-interaction framing from the abstract; treat it as low-confidence [8].

**GRPO's "canonical" objective is already contested.** Vanilla GRPO's normalization injects two biases: dividing the advantage by `std(r)` introduces a question-difficulty bias, and per-response length normalization introduces a length bias. Dr. GRPO and DAPO correct these with token-level or constant-length normalization. TRL now flags both biases, exposes the corrected loss variants, and **defaults `β = 0` (no KL term)**, citing evidence that the KL term isn't essential for reasoning training [9]. GRPO's cost is also real: it needs many samples per prompt for a stable group-relative gradient (DeepSeekMath used 64), raising generation cost, and it works best with verifiable rewards rather than a neural RM [3][9]. R1-Zero (pure RL, no SFT) also shipped with poor readability and language mixing — evidence that plain online RL, even when it maxes verifiable benchmarks, is not a deployable assistant on its own [5].

**Learned RM vs rule-based reward is a real fork, not a contradiction.** InstructGPT centers a learned Bradley-Terry RM [1]; DeepSeek-R1 refuses one to avoid reward hacking [5]. Both are correct for their domain: subjective-quality alignment needs a learned RM; verifiable-reasoning RL can and should drop it.

## In practice

The blind spot in all three research-frame debates is that they argue at frontier scale and under-weight what dominates real outcomes: **preference-data quality and evaluation validity.** Llama 3's post-training combines SFT, rejection sampling, PPO, *and* DPO — the methods coexist — and its own writeup says the "quality of the prompts... and the preference rankings... has an outsized influence on the performance of aligned models" [13]. That plausibly swamps the optimizer choice. Much of the DPO-vs-PPO disagreement itself traces to different eval suites and length-normalization choices [6][12].

- **Default to SFT + DPO.** It's the simplest thing that works, and production teams ship it — Tulu 3 used "DPO throughout the development process... in lieu of more costly investigations into PPO-based methods" [12].
- **When you use DPO, audit data coverage.** The OOD/3D failure is a data problem before it is an algorithm problem; ensure your preference pairs cover the policy's output distribution, and consider an on-policy/iterative loop if they don't [8].
- **Reach for GRPO only when reward is cheaply verifiable.** The critic-free memory win is real, but the many-generations-per-prompt sample cost (64 in DeepSeekMath) and the normalization biases are real too — use the Dr. GRPO/DAPO variants and start with `β = 0` [3][9].
- **Consider PPO only with a tuning budget** for advantage normalization, batch size, and reference-model EMA [4].
- **Don't over-invest in the optimizer before the data.** Fix SFT data (LIMA) and preference-annotation quality (Llama 3) first; the RL slice plateaus — more response-samples-per-prompt "boost performance initially but quickly plateau," and RLHF scales less efficiently than pretraining [10][11][13].

## Further reading

1. Training language models to follow instructions with human feedback (InstructGPT / RLHF-PPO) — Ouyang et al. 2022 (Bradley-Terry RM loss, PPO-ptx objective, 1.3B-preferred-over-175B, alignment tax) — https://ar5iv.labs.arxiv.org/html/2203.02155
2. Direct Preference Optimization: Your Language Model is Secretly a Reward Model — Rafailov et al. 2023, NeurIPS (closed-form optimal policy, implicit reward reparameterization, BCE loss) — https://arxiv.org/abs/2305.18290
3. DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models — Shao et al. 2024 (introduces GRPO: group-relative advantage, critic removal, KL-in-loss, GSM8K/MATH gains) — https://arxiv.org/html/2402.03300v3
4. Is DPO Superior to PPO for LLM Alignment? A Comprehensive Study — Xu et al. 2024, ICML (PPO surpasses other alignment methods in all their cases; CodeContest SOTA, OOD-exploitation, three PPO factors) — https://arxiv.org/html/2404.10719v3
5. DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning — DeepSeek-AI 2025 (rule-based rewards, AIME 15.6%→71.0%, reward-hacking rationale, R1-Zero readability/language-mixing) — https://arxiv.org/html/2501.12948v1
6. Unpacking DPO and PPO: Disentangling Best Practices for Learning from Preference Feedback — Ivison et al. 2024 (measured gap: PPO ahead by up to 2.5% math / 1.2% general) — https://arxiv.org/abs/2406.09279
7. Group Relative Policy Optimization (GRPO) — Cameron R. Wolfe (engineering deep-dive on critic-free RL and the memory savings from dropping the value network) — https://cameronrwolfe.substack.com/p/grpo
8. 3D-Properties: Identifying Challenges in DPO and Charting a Path Forward — Yan et al. 2024, ICLR 2025 (Drastic-drop / Degradation / Dispersion pathologies of offline DPO; gradient interaction) — https://arxiv.org/abs/2406.07327
9. GRPO Trainer — HuggingFace TRL docs (std-difficulty + length bias flags, Dr. GRPO/DAPO loss variants, β=0 default, online/reward-function mechanics) — https://huggingface.co/docs/trl/main/en/grpo_trainer
10. LIMA: Less Is More for Alignment — Zhou et al. 2023, NeurIPS (Superficial Alignment Hypothesis; 1,000 SFT prompts, no RL, 43%/58%/65% head-to-heads) — https://arxiv.org/abs/2305.11206
11. Does RLHF Scale? Exploring the Impacts from Data, Model, and Method — Hou et al. 2024 (response-samples-per-prompt plateau; RLHF scales less efficiently than pretraining) — https://arxiv.org/abs/2412.06000
12. Tulu 3: The next era in open post-training — Ai2 (DPO-first justification: DPO/PPO "roughly similar," prioritized simplicity, DPO for final models) — https://allenai.org/blog/tulu-3-technical
13. Llama 3 and Scaling Open LLMs — Nathan Lambert, Interconnects (SFT+rejection-sampling+PPO+DPO stack; data-quality "outsized influence") — https://www.interconnects.ai/p/llama-3-and-scaling-open-llms
