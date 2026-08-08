---
title: "Structured outputs and constrained decoding: syntax guarantees, semantic limits"
pillar: ml-techniques
method: deep-research
sources: 3
confidence: high
date: 2026-08-07
---

# Structured outputs and constrained decoding: syntax guarantees, semantic limits

## What it is

Structured generation constrains a language model's next-token choices so its output belongs to a required language: commonly JSON, a JSON Schema-shaped subset, a regular expression, or a context-free grammar. It turns “please return valid JSON” from an instruction the model may ignore into a decoding-time invariant. Willard and Louf formulate guided generation as transitions in a finite-state machine, allowing regular expressions and context-free grammars to constrain decoding while indexing the model vocabulary against the allowed language.[1]

That distinction matters operationally. Prompting can encourage a shape; constrained decoding can rule out an illegal next token. The result is useful at boundaries where another program consumes the output: tool arguments, records written to a database, extraction payloads, or a UI component tree. The goal is not to make a model truthful or business-correct. It is to make the wire format a property of the generation process rather than an optimistic parser-retry loop.

## When to reach for it

Use a constraint when a downstream component needs an unambiguous machine-readable contract and a rejection or repair cycle would be expensive or unsafe. Examples include an API call whose arguments must type-check, an event record that must satisfy a schema, or a classifier whose labels must be one of a closed set. The user study behind “We Need Structured Output” found 134 concrete constraint use cases among experienced practitioners, spanning low-level format/length requirements and higher-level semantic or stylistic requirements.[2]

Do not confuse this with validation of the underlying decision. A grammar can guarantee that `{"amount": 100}` parses; it cannot establish that the amount is authorized, that the selected enum is appropriate, or that a referenced identifier exists. Keep semantic validation, authorization, and domain checks outside the model. Likewise, use free-form generation when the value of the task is explanation, ideation, or prose rather than a machine-consumed record.

## How it works

At every decoding step, a conventional autoregressive model assigns probabilities over its whole token vocabulary. A constrained decoder carries parser state for the permitted language and masks tokens that cannot extend the current prefix into a valid string. The remaining tokens are sampled or selected normally. For a simple finite-state format the state might be “inside a JSON string after a field separator”; for a grammar it can represent the parser stack needed to complete nested objects or arrays. The decoder thereby produces a prefix that remains completable under the grammar, rather than discovering only at the end that it emitted an unmatched brace.[1]

The constraint language determines the guarantee. A regular expression can express a fixed lexical shape. A grammar can additionally represent recursively nested syntax. A JSON Schema-oriented runtime normally compiles the schema into a grammar or equivalent automaton, so its guarantee is only as strong as the schema and compiler support. It does not imply arbitrary cross-field predicates, database facts, or policies that depend on tool results. Design schemas to make invalid states hard to express—closed enums, explicit nullable fields, bounded arrays, and distinct variants—then run conventional validation after parsing.

Schemas also influence the model before they constrain it. Their literals, field names, descriptions, ordering, and examples all become part of the model’s context. A 2026 controlled study held prompt, model, output structure, and decoding setup fixed and found that changing only schema-key wording could substantially change mathematical-reasoning accuracy; the effect varied by model family and interacted non-additively with prompt-level instructions.[3] Treat names and descriptions as part of the task specification, not cosmetic metadata. This is a reason to version schemas and test them like prompts.

## Trade-offs

The primary gain is deterministic syntax. The costs are expressiveness, engineering effort, and a tempting false sense of correctness. A strict grammar prevents malformed output but may force the model into an awkward legal continuation when its intended response cannot be expressed by the schema. A permissive schema lowers that risk but gives downstream code less protection. The right contract describes stable invariants, not every incidental formatting preference.

Constraint design also creates a second instruction channel. A schema with vague keys such as `value` and `type` is structurally valid but leaves the task underspecified; one with overloaded prose descriptions can turn a data contract into a hidden prompt. The latter may boost an offline metric yet be brittle across models or schema versions.[3] Keep structural constraints compact, make semantic instructions explicit, and test both independently.

Finally, constrained decoding has runtime overhead: parser state must be updated and the vocabulary filtered for each generated token. The cited guided-generation work reports an efficient vocabulary index and little generation overhead for its approach, but exact cost depends on vocabulary, grammar complexity, batching, and the serving runtime.[1] Benchmark the schema and model you plan to ship rather than extrapolating a paper result.

## In practice

Start with a narrow output boundary. Define the smallest schema that a downstream consumer needs; use explicit discriminated variants instead of an all-purpose “payload” object. Compile that schema into the provider or local grammar runtime, and reject any response that fails ordinary JSON/Schema validation—this catches implementation mismatches as well as provider regressions.

Then add semantic guards outside the decoder: validate identifiers against the source of truth, enforce authorization before executing an action, bound resource-consuming values, and make tool calls idempotent. Log the original request, schema version, constrained result, and validation outcome. This separates three debuggable failures: the model chose the wrong legal value, the schema failed to represent a needed state, or the runtime failed to honor the constraint.

Test schema changes as behavior changes. Use representative prompts, adversarially long strings, optional-field combinations, and consumers running the real parser. Measure both syntax acceptance and task success. A 100% parsing rate with poor semantic selections is not reliability; it is only evidence that the transport layer is doing its job.

## Further reading

1. Willard & Louf — *Efficient Guided Generation for Large Language Models* (finite-state formulation; regex/CFG guidance; vocabulary index) — https://arxiv.org/abs/2307.09702v4
2. Liu et al. — *“We Need Structured Output”: Towards User-centered Constraints on Large Language Model Output* (51 practitioners; 134 use cases; low- and high-level constraints) — https://arxiv.org/abs/2404.07362v1
3. Le — *Schema Key Wording as an Instruction Channel in Structured Generation under Constrained Decoding* (schema keys affect accuracy while structure is fixed) — https://arxiv.org/abs/2604.14862v2
