---
title: "Agent memory architectures: retrieval, distillation, and bounded context"
pillar: ml-techniques
method: deep-research + storm
sources: 6
confidence: medium
date: 2026-08-07
---

# Agent memory architectures: retrieval, distillation, and bounded context

## What it is

Agent memory is the system around fixed model weights that decides which experience survives an interaction, how it is transformed, and what is returned to the next prompt. It is not one mechanism. A raw episode log, a reflection buffer, a tiered virtual context, and an executable skill library store different representations and support different decisions.

The useful decomposition is: encode an observation or trajectory; select what to retain; index/store it; retrieve and rerank it for a later task; inject a bounded subset into context; then validate, revise, expire, or discard it after outcomes. The central constraint is not storage capacity alone. It is decision-relevant information under a finite context budget.

## When to reach for it

Use an explicit memory architecture when tasks span sessions, require learning from prior failures, or exceed the model’s usable prompt window. MemGPT frames the basic problem as limited context and proposes virtual context management through movement between fast and slow memory tiers.[1]

Do not add durable memory merely because a chatbot has conversations. If the task has no repeatable state, reliable write signal, or retrieval criterion, retained text can create stale instructions, privacy exposure, and misleading confidence. Start with external source-of-truth state for facts; add learned/episodic memory only when it demonstrably improves a measured task.

## How it works

Tiered context systems move information between prompt-visible working memory and external storage. MemGPT explicitly borrows the virtual-memory analogy: a limited fast context presents the appearance of larger memory through controlled movement.[1] Episodic systems retain experiences, synthesize them into reflections, and dynamically retrieve them for planning; Generative Agents describes exactly that store–reflect–retrieve loop.[2]

Reflection systems retain compact lessons rather than a complete transcript. Reflexion converts task feedback into reflective text in an episodic buffer so later trials can make different choices without changing model weights.[3] Skill memory goes further: Voyager maintains an ever-growing library of executable code for storing and retrieving complex behaviors.[4] This changes the artifact from advice to callable procedure, with correspondingly higher validation and safety requirements.

Recent proposals make memory policy itself mutable. MemEvolve jointly evolves experiential knowledge and memory architecture.[5] GenericAgent combines hierarchical on-demand memory with context compression, a small tool interface, and a mechanism that turns verified trajectories into procedures/code.[6] These are proposals with promising reported results, not evidence that self-modifying memory is generally reliable.

## Trade-offs

More history is not necessarily better. Raw logs preserve detail but consume retrieval/indexing budget; summaries compress but can erase qualifications; reflections can encode incorrect causal stories; executable skills can fossilize obsolete or unsafe behavior. Retrieval failures are often selection failures: irrelevant recency can crowd out a crucial older fact, and an untrusted retrieved instruction can alter tool use.

“Memory” benchmarks are also hard to compare. Paging, episodic retrieval, reflection, and skills change prompts, tools, policies, and evaluation tasks at the same time. Treat claimed gains as system-specific unless an ablation isolates the representation and selection policy.[5][6]

## In practice

Make writes explicit and attributable. Store source, time, task, confidence, scope, and invalidation rules; separate untrusted content from policies. Retrieve a small ranked set with diversity and token budgets, then log what was injected and whether it helped. Evaluate long-context recall, cross-episode transfer, task success, token cost, stale-memory regressions, and harmful-action rate separately.

A good first implementation is often boring: durable domain state plus a reviewed lesson store and bounded retrieval. Add automatic reflection, skill promotion, or architecture evolution only behind evidence gates, replay tests, and rollback.

Design retrieval as a policy with observable failure modes. A useful record needs a stable key or embedding/index representation, a scope boundary, retention/expiry rules, and a reason it was selected. The prompt assembly step should be able to say which records won, which were omitted for budget, and which source authorized them. Without that trace, a bad downstream answer cannot be separated into bad model reasoning, stale state, or irrelevant recall.

Write policies deserve the same care. Store raw user text only when it is permitted and necessary; distinguish immutable facts from provisional hypotheses; and prevent an arbitrary retrieved document from becoming an instruction with tool authority. A memory layer can amplify prompt-injection risk precisely because it makes content durable and repeatedly available. The safest baseline is explicit provenance plus a small, reviewable retrieval budget.

## Further reading

1. Packer et al. — *MemGPT: Towards LLMs as Operating Systems* — https://arxiv.org/abs/2310.08560
2. Park et al. — *Generative Agents* — https://arxiv.org/abs/2304.03442
3. Shinn et al. — *Reflexion* — https://arxiv.org/abs/2303.11366
4. Wang et al. — *Voyager* — https://arxiv.org/abs/2305.16291
5. Zhang et al. — *MemEvolve* — https://arxiv.org/abs/2512.18746
6. Liang et al. — *GenericAgent* — https://arxiv.org/abs/2604.17091
