---
title: Evaluating agents and models rigorously — baselines, significance, honest reporting
pillar: ml-techniques
method: vault-adapt
date: 2026-07-01
sources: 13
confidence: high
vault-links: ["wiki/concepts/agent-evaluation-methodology.md"]
---

## What it is

This is the discipline for not fooling yourself when you measure a model or an agent. It has five load-bearing parts, each closing a specific channel through which optimism leaks into your numbers:

1. **A fixed, strong, equally-tuned baseline** — a line in the sand measured up front, itself a strong method tuned to the same degree as your new one [1][2][4].
2. **A separated iterate signal and validate signal** — tune on a dev set; partition a test set at the project's start and touch it exactly once [1][2].
3. **Trials with uncertainty, not a point estimate** — models are stochastic, so report spread across seeds and use a significance test to decide a difference is real [1][5].
4. **Honest nulls and negatives** — a bigger headline number is not a better model when splits or tuning budgets differ [1].
5. **A ship criterion fixed before you look**, so the goalposts cannot move once the results are in.

The dominant failure mode across all five is *optimism injection*: weak baselines, test-set leakage, cherry-picked seeds, and selective reporting each manufacture improvements that evaporate — or reverse — under honest comparison [4]. LLM-agent evaluation does not replace this discipline; it extends it, because an agent can reach a correct answer by an unsafe path or once by luck, so two new instruments appear: trajectory-aware grading and consistency metrics like Pass^k [8][11].

## When to reach for it

Any time a number will drive a decision — merge, ship, publish. Rigor should scale with the cost of being wrong, and the sources give no clean rule for that scaling (see Trade-offs). The floor is non-negotiable: comparing two methods by a single accuracy number each, with no baseline discipline and no variance, is not measuring — it is guessing with extra steps.

Reach for the *agent-era* extensions — trace audits, Pass^k — when the output is consumed directly rather than reviewed by a human, when a single failure is costly, or when the dimension you care about (safety, robustness, tool efficiency) lives in the *path* and not the final artifact [8][10][11].

## How it works

**The baseline is the whole game.** McGreivy & Hakim audited ML-for-fluid-PDE papers and found **79% (60 of 76)** of speedup claims violated a fair-comparison rule — a weak/undertuned baseline, or speed and accuracy compared on unequal footing [4]. Re-run with properly tuned baselines, the results did not shrink, they *reversed*: a claimed **24× speedup became 10× slower**, and a separate claimed **1000× speedup became 10× slower** [4]. An undertuned baseline is a free source of entirely artificial gain: it must be frozen up front, strong, and tuned with the same budget you spent on your method — anything less and the delta measures your tuning asymmetry, not your idea.

**The iterate/validate separation stops sequential overfitting.** You need a signal you look at constantly (the dev set) and one you look at once (the held-out test set) [1]. The trap is reusing the test set to pick between candidates: each peek leaks a little test-set information into your selection, and over dozens of comparisons you overfit it through your own decisions without ever training on it [1][2]. Leakage generalizes — no clean split, preprocessing or feature selection on combined data, duplicates across splits, and distribution mismatch are all leakage [2][3]. Kapoor & Narayanan documented this as a live reproducibility crisis — **41 papers across 30 fields were found to contain leakage, collectively affecting 648 papers downstream** — with a *model info sheet* as the remedy: it forces the author to justify, per leakage type, that no leakage occurred [2][3].

**One run is not a measurement.** Henderson et al.'s *Deep RL That Matters* shows stochastic systems produce wildly different results across random seeds, so a single run — or worse, cherry-picking the best seed or max reward — is malpractice [5]. Evaluate multiple times, report a standard deviation or 95% CI, and use a significance test suited to the data (McNemar's for paired classifier decisions, Mann-Whitney U or bootstrap for reward distributions) to establish a difference is real, not seed noise [1][5]. The NeurIPS reproducibility program — code-submission policy, reproducibility challenge, ML Reproducibility Checklist — institutionalizes fixed seeds, consistent logging, and reported variance as structural defenses [6].

**Benchmarks decay under their own success.** Once a public benchmark becomes prestigious it becomes a target, and Goodhart's law applies: contamination, task-specific tricks, and selective reporting inflate scores without improving capability [7]. Defenses [7] center on transparency — permanent publication of results, uniform private-testing policies, diverse evaluation signals, and independent audits — paired with graders built to resist gaming [8]; the shared goal is a score that reflects generalization rather than memorization of a static bank.

**The agent extension: consistency, not just capability.** Mean success rate and Pass@k both hide reliability. Pass@k measures whether *at least one* of k trials succeeds — a capability ceiling, useful when a human reviews each output. **Pass^k measures whether *all* k trials succeed** — a reliability floor, the right metric when output is consumed directly and a single failure is costly [8][10]. Pass^k decays roughly as p^k, so a 90%-per-trial agent is only about **43% consistent at k=8** (0.9^8 ≈ 0.43) — reliability collapses far faster than the headline rate suggests. The metric originates in tau-bench (Yao et al., Sierra), where agents were "quite inconsistent (pass^8 < 25% in retail)": a respectable-looking per-trial rate, a consistency floor that is not [9][10].

**The agent extension: grade the trace, not just the output.** Claw-Eval records three independent evidence channels — execution traces, service-side audit logs, environment snapshots — into **2,159 rubric items across 300 tasks**, and shows a *trajectory-opaque* judge (seeing only the final output) **misses 44% of safety violations and 13% of robustness failures** its evidence-grounded pipeline catches [11]. For those dimensions the failure is invisible in a correct-looking answer — the agent did something dangerous or fragile *en route* — so an outcome-only judge is structurally blind to it. Under error injection, **Pass@3 stayed stable while Pass^3 dropped by up to 24 percentage points** [11]: peak capability barely moved, deployability cratered, and a benchmark reporting only peak or average would miss the regression entirely.

## Trade-offs

The sharpest tension is **what to grade**, and it is a real disagreement, not a wording gap. Anthropic's practitioner guidance says **grade the outcome, not the path**: rigid step-by-step grading "unnecessarily punishes creativity" when an agent reaches a valid answer by an unanticipated route, so outcome grading is more robust and less brittle [8]. Claw-Eval pushes the opposite way for safety-critical dimensions: an outcome-opaque judge is "systematically unreliable," missing the 44%/13% of failures that only the trajectory reveals [11].

They agree on more than they disagree: both reject naive step-sequence matching, both want evidence-grounded rubrics, both distrust a single headline number. The reconciliation — which neither states cleanly — is that **the grading target depends on the dimension**: grade the final artifact for task completion (so you do not punish valid unanticipated solutions), but audit the trace for safety, robustness, and tool-use efficiency, *because for those dimensions the path is the outcome*.

A quieter agreement runs under everything: every serious source distrusts a bare point estimate. Classical work insists on variance, CIs, and significance [1][5][6]; agent work insists on Pass^k floors and multi-trial consistency [8][9][11] — the same "report uncertainty, not a point" instinct in two eras.

The **blind spot none of the sources close is cost**. Trajectory-aware grading, Pass^k over k trials, private held-out test sets, and human-calibrated judges are all far more expensive than a single outcome check, and no source gives a principled rule for how much rigor a decision warrants. tau-bench and Claw-Eval report specific k values (8, 3) without deriving them. When a cheap eval is good enough is left to you.

## In practice

The most actionable practitioner playbook is Anthropic's [8]:

- **Do not trust eval scores until someone reads the transcripts.** The headline number routinely hides broken tasks, a gamed grader, or a judge favoring verbose output. Reading a handful of traces is the highest-leverage act in the loop.
- **Calibrate the LLM-as-judge against human experts** before you trust it, because judges show self-preference and verbosity bias.
- **Separate capability evals from regression evals.** Capability evals have a low pass rate and you hill-climb them; regression evals sit near 100% and run as CI against backsliding.
- **Make the grader resistant to gaming** so the agent cannot cheat the eval instead of solving the task.

For task construction, Terminal-Bench 2.0 sets the verifiability bar: each of its 89 tasks must be **well-specified** (unit tests pass iff the task is correctly completed) and **solvable** (a reference/oracle solution making all tests pass), run through a neutral harness — and even so, frontier models score **under 65%**, so hard *verified* tasks still discriminate at the frontier [12]. For process-dependent expert domains, OneMillion-Bench grades along multiple rubric dimensions — factual accuracy, logical coherence, practical feasibility, professional compliance — across five domains (Law, Finance, Industry, Healthcare, Natural Science), because a single binary pass cannot differentiate expert-level agents where correctness lives in the reasoning [13].

The unifying principle, classical and agent-era alike: **credibility is the product.** Express performance as an estimate plus its uncertainty — a CI, a credible interval, a Pass^k reliability floor — not a point, and instrument the evaluation so the system honestly reports its own failures [1][9].

## Further reading

1. Michael A. Lones — How to avoid machine learning pitfalls: a guide for academic researchers — https://arxiv.org/html/2108.02497v5
2. Kapoor & Narayanan — Leakage and the Reproducibility Crisis in ML-based Science — https://arxiv.org/pdf/2207.07048
3. Princeton — Leakage and the Reproducibility Crisis in ML-based Science (project page: leakage taxonomy, model info sheets, 648 affected papers) — https://reproducible.cs.princeton.edu/
4. McGreivy & Hakim — Weak baselines and reporting biases lead to overoptimism in ML for fluid-related PDEs — https://arxiv.org/html/2407.07218v1
5. Henderson et al. — Deep Reinforcement Learning that Matters — https://arxiv.org/abs/1709.06560
6. Pineau et al. — Improving Reproducibility in ML Research (NeurIPS 2019 Reproducibility Program) — https://arxiv.org/abs/2003.12206
7. Collinear AI — Gaming the System: Goodhart's Law Exemplified in AI Leaderboard Controversy — https://blog.collinear.ai/p/gaming-the-system-goodharts-law-exemplified-in-ai-leaderboard-controversy
8. Anthropic Engineering — Demystifying evals for AI agents — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
9. Yao et al. (Sierra) — tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains — https://arxiv.org/abs/2406.12045
10. AgentPatterns.ai — pass@k and pass^k: Capability and Consistency Metrics — https://agentpatterns.ai/verification/pass-at-k-metrics/
11. Ye et al. — Claw-Eval: Towards Trustworthy Evaluation of Autonomous Agents — https://arxiv.org/abs/2604.06132
12. Merrill et al. — Terminal-Bench: Benchmarking Agents on Hard, Realistic Tasks in Command Line Interfaces — https://arxiv.org/abs/2601.11868
13. Yang et al. — OneMillion-Bench: How Far are Language Agents from Human Experts? — https://arxiv.org/abs/2603.07980
