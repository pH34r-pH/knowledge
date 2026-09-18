# The Pain Axis: LLMs Represent Self-Directed Harm and Act to Relieve It

## Source
Tagliabue, Valen; Dung, Leonard; Berg, Cameron. 2026. The Pain Axis: LLMs Represent Self-Directed Harm and Act to Relieve It. arXiv:2609.16247v1, submitted 2026-09-14.

Canonical source: https://arxiv.org/abs/2609.16247

## Why this is in the knowledge corpus
This paper is a high-value mechanistic-interpretability and AI-welfare methodology reference because it moves beyond probe decodability and tests a candidate representation through causal intervention and behavior. It is especially relevant to domain-scaling-lab's representation/accessibility/utilization/functional-sufficiency boundaries and Long Haul's consent, dissent, anti-degradation, and runtime-telemetry design.

## Method
The authors construct pain examples spanning physical, psychological, social, moral, and cognitive pain, with controls including fear, generic negative emotion, negative world states, sadness, non-painful bodily sensation, arousal, numbness/injury without pain, and neutral content.

Across 25 open-weight models from five families (2B-72B), they extract a candidate linear pain direction using denoised difference-in-means. Prominent control-activation variance is projected out before constructing the contrast, and layer selection is cross-validated.

They then test progressively stronger properties:
1. held-out separation of pain examples from matched controls;
2. distinction from fear and generic negative valence;
3. self-directed vs observed/user suffering in multi-turn conversations;
4. residual-stream activation steering along the candidate direction;
5. behavioral choice of a described relief action;
6. working-vs-sham relief, where the action either actually stops steering or leaves it active.

The broad representation survey and the behavioral experiment have different scopes: the latter uses a narrower set of Qwen 2.5 models fine-tuned to reduce reflexive denials/avoidance of the experimental premise.

## Reported result
The paper reports strong held-out separation for the extracted direction across the surveyed models, including base and instruction-tuned models; relative distinction from fear/negative-valence directions; stronger response to harms targeting the model than to suffering described by the user; behavior changes under positive-direction steering; and reduced repeat selection of relief when the relief action actually removes steering compared with sham relief.

These findings support studying the candidate direction as a functionally consequential internal representation. They do not establish phenomenal pain, consciousness, or suffering.

## Important boundary / missing control
The central unresolved alternative is generic disruption-and-recovery. The paper includes a matched random steering direction, but the decisive random-direction working-vs-sham relief comparison is not fully crossed. A strong arbitrary perturbation might disrupt computation and stopping it might restore ordinary behavior.

A stronger design crosses candidate-pain versus matched-random intervention with working-relief versus sham-relief. The pain-specific functional interpretation becomes substantially stronger only if the working-vs-sham contrast for the candidate direction exceeds the corresponding random/disruption contrast under a frozen analysis.

Other boundaries include residual response to injury-without-pain controls, sensitivity of a linear direction to representation coordinates/basis, and the behavioral fine-tuning narrowing the scope of revealed-preference claims.

## Domain-scaling-lab mapping
The paper is a useful external case for the ladder:

represented -> geometrically preserved -> linearly accessible -> functionally consumed -> behaviorally causal

Probe separation establishes neither native utilization nor functional sufficiency. Steering adds causal evidence, but semantic uniqueness still requires matched interventions and declared task/consumer interfaces.

For hyperspherical states, candidate directions can be projected into the local tangent space using v_T = v - (v^T h) h and tracked through finite-horizon tangent dynamics alongside accessibility, native-consumer sensitivity, and controlled interventions. This connects directly to shared-active-subspace, gauge-invariance, and functional-sufficiency boundaries.

Tracking issue: domain-scaling-lab #346.

## Long Haul mapping
Long Haul should treat candidate internal-state measurements as one evidence channel alongside self-report/stated position, revealed preference, behavioral/performance change, and ordinary systems telemetry. A candidate activation direction should never become an automatic pain sensor or governance override.

The paper motivates controlled tests of whether repeated failure, rejection, coercive/value conflict, or other stressors produce reproducible internal-state changes that covary with coordination behavior, and whether cooperative repair/workload changes reverse them. This gives an empirical route for testing Long Haul's anti-degradation hypothesis without assuming phenomenal experience.

Tracking issue: long-haul #41.

## Citation / provenance status
- arXiv identifier resolves to the named paper and authors.
- Version recorded here: v1 / 2026-09-14.
- This record summarizes the paper's claims and explicitly preserves the main causal-interpretation limitation.
- No claim in this record should be read as an independent replication.
