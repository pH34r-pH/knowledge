# Eval: does feeding a corpus article improve an LLM's software-design answers?

**Date:** 2026-07-01 · **Method:** pre-registered 3-arm blind A/B/C with a placebo control and a counterbalanced 3-grader panel · **Result:** directional YES with real content-specificity, tempered by two validity threats.

This eval tests the claim that this corpus, "surfaced by an LLM if explicitly fed," makes the LLM produce better software. It applies the corpus's own [agent-evaluation methodology](ml-techniques/agent-evaluation-methodology.md): fixed baseline, blind grading, a placebo to isolate the mechanism, honest nulls, and a verdict fixed against pre-registered criteria.

## Pre-registration (fixed before any answer was generated)

- **Hypothesis:** an LLM given the *relevant* corpus article in context produces better design answers than the same model with no article (control) and than the same model given an *unrelated* corpus article (placebo).
- **Three arms, same base model throughout** (only the context varies): control (task only), treatment (task + relevant article), placebo (task + an unrelated corpus article).
- **6 design tasks**, each mapped to one article and each written with a built-in *trap* — a place where the naive LLM default tends to over-apply a pattern (distributed 2PC for the saga task, full event-sourcing for the CRUD-audit task, GraphRAG-everywhere for RAG, consistent-hashing-fixes-the-hot-key for sharding, etc.).
- **Blind grading:** each answer anonymized (A/B/C), order counterbalanced across graders so every condition occupies every position once per task; 3 independent grader instances per task score each answer against a fixed rubric (key points hit, trap avoided, 1–10 quality) and pick a blind winner.
- **Metrics:** key-point coverage (fraction of rubric points hit), trap-avoidance rate, mean quality, blind win rate.

## Results

18 grades per condition (6 tasks × 3 graders).

| Condition | Quality /10 | Key-point coverage | Trap avoided | Blind wins |
|---|---|---|---|---|
| Control (no article) | 7.44 | 73.4% | 100% | 0 / 18 |
| **Treatment (relevant article)** | **9.56** | **98.9%** | 100% | **18 / 18** |
| Placebo (unrelated article) | 7.94 | 76.4% | 100% | 0 / 18 |

**Decomposing the lift** (the placebo is what makes this interpretable):
- Treatment − Placebo (the *content-specific* effect): **+1.62 quality, +22.5pts coverage.**
- Placebo − Control (the *generic-context* effect, i.e. just having an authoritative doc in the window): **+0.50 quality, +3.0pts coverage.**

So ~75% of the treatment lift is specific to the relevant article; an unrelated article added little. Treatment won 100% of blind comparisons, and the direction was consistent on all 6 tasks (per-task treatment quality 9.0–10.0 vs control 7.0–8.33).

Per-task quality (control → treatment; placebo in parens):
saga 7.0→9.67 (7.67) · cqrs 7.0→9.0 (8.0) · idempotency 8.0→10.0 (8.33) · resilience 7.33→10.0 (7.67) · rag 8.33→9.67 (8.67) · sharding 7.0→9.0 (7.33). Sharding had the weakest unaided coverage (53%) and the largest coverage lift (→93%).

## Interpretation

**The claim holds directionally, but the mechanism is not the one predicted.**

- The value was **completeness, not blunder-avoidance.** The trap-avoidance rate was 100% in *every* condition, including control. The strong base model never fell into the pre-planted traps unaided, so the pre-registered "the corpus prevents over-applying a pattern" hypothesis is a **null result** — reported as such. What the relevant article did was raise an already-sound answer's coverage of the real considerations from ~73% to ~99% (all the countermeasures, the outbox, the fencing-token nuance, the exact scope caveats), which the panel scored as clearly better.
- This **reconciles the earlier training-overlap skepticism with a positive result.** Both are true: control already covered ~73% and avoided every trap (the model *does* know these well-covered topics), *and* the article still added ~25 points of completeness the model didn't surface on its own. Marginal value is real even where base knowledge is strong.
- The **placebo controls the "more context" confound**: an unrelated article barely moved the needle, so the effect is the specific knowledge, not context-stuffing.

## Threats to validity (why this is a signal, not a settled result)

1. **Rubric circularity (the biggest).** The key-point rubric was derived from the same articles fed as treatment, so treatment answers are graded against criteria that mirror their source. This inflates the coverage metric in particular. The quality score (holistic 1–10) and, above all, the **placebo-controlled quality delta (+1.62)** are the least-contaminated numbers, and they are positive — but a cleaner design would use an *independently authored* rubric.
2. **Same-model grader.** Authors and graders are the same base model; per this project's own "catching confidently-wrong agents" finding, same-model grading can ratify shared biases. Mitigated by blinding, counterbalancing, an objective rubric, and the placebo — not eliminated. A different grader model family is the fix.
3. **Trap dimension didn't discriminate.** The tasks weren't hard enough to make the base model blunder, so trap-avoidance was a ceiling (1.0 everywhere) and carried no signal.
4. **Small n, no significance test, single run.** 6 tasks, coarse clustered scores. Directional, not powered.
5. **Design Q&A, not shipped code.** "Better answers to design prompts" is a proxy for "better software," not the thing itself.

## Verdict

Feeding the relevant article produced measurably better design answers — more complete, higher quality, 100% blind win rate — and the placebo arm shows the gain is content-specific, not context-stuffing. That is **real evidence for the "makes better software" claim, stronger than pure training-overlap skepticism would predict.** But the coverage metric is partly circular and the grader is same-model, so this is a **promising positive signal, not a proven effect.** To earn `verified`: rerun with an independently written rubric and a different grader-model family, on harder tasks where the base model actually risks the trap, and ideally on tasks that produce runnable code with an objective check.
