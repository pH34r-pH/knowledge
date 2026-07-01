---
title: The Saga pattern for distributed transactions
pillar: design-patterns
method: deep-research
date: 2026-07-01
sources: 13
confidence: high
---

## What it is

A saga replaces a single ACID transaction that would span multiple services with a sequence of local transactions `T1..Tn`, each committing independently in its own service and its own database. If step `Ti` fails on a business rule, the saga runs compensating transactions `Ci-1..C1` in reverse order to semantically undo the work already committed by the preceding steps [1]. It maintains data consistency across services *without* a distributed two-phase-commit transaction [1][2].

The formal pattern predates microservices by decades. Garcia-Molina and Salem introduced it in 1987 (SIGMOD, "Sagas") to attack a different problem: Long-Lived Transactions that hold database locks for extended periods and block shorter transactions. Their move was to break the LLT into interleavable sub-transactions `T1..Tn` with compensations `C1..Cn-1`, guaranteeing that either the full forward sequence completes, or a prefix runs and is then compensated in reverse [8]. The paper is candid that this is a deliberate downgrade — "a sequence of two transactions is not a transaction" — it trades the strict atomicity and isolation of the whole LLT for the ability to interleave and to release locks early [8]. (The 1987 formal notation here is cross-checked against Temporal's secondary summary; the source PDF returned as binary, so treat the precise wording as medium-confidence.)

The one sentence that captures the mechanism: a saga gives you Atomicity, Consistency, and Durability but explicitly gives up **Isolation** [1][4].

## When to reach for it

Reach for a saga when a business operation must update state in several independently owned services — the classic "database per service" microservices constraint — and you have accepted eventual, not strong, consistency [1][5]. Order placement that must touch order, payment, and inventory services is the canonical case: no single database, no shared transaction manager, so the only atomicity you can offer is logical.

The more useful discipline is knowing when **not** to reach for one. A distributed transaction across a *few* services is often evidence of wrong service boundaries, not a saga-shaped problem — the best saga is frequently the one you avoid by drawing the boundary so the transaction stays local [4][11]. Skip it inside a monolith or wherever the participants aren't genuinely independent (that is over-engineering); skip it when the workflow is tightly coupled, when compensations would have to fire in already-completed earlier participants in a way that can't be cleanly reversed, or when the business genuinely requires strong consistency rather than a convergent end state [4][5][11]. The vendor docs treat the service decomposition as given and optimize within it; the sharper critique questions the decomposition itself.

The classical alternative — two-phase commit — is generally rejected for microservices for concrete reasons: it is a blocking protocol where participants hold locks awaiting the coordinator's decision; the coordinator is a single point of failure that can leave participants indefinitely locked if it crashes after the prepare phase; and the database-per-service model has no single controller able to run the prepare/commit handshake across heterogeneous stores [5][12]. Sagas plus eventual consistency are the pragmatic answer to exactly those failure modes.

## How it works

**Steps come in three kinds, and design is mostly about the pivot.** Every step is a *compensable* transaction (it has a hand-written compensation that can undo it), the single *pivot* transaction (the point of no return — the last compensable step or the first retriable one; once it commits, the saga must roll forward), or a *retriable* transaction (post-pivot, no compensation, idempotent, retried until it succeeds) [4][6]. Designing a saga is largely deciding where the pivot lives and ensuring every pre-pivot step has a real compensation [4][6].

**Compensations do not roll back — they reverse.** There is no automatic ACID rollback across services. A compensating transaction does not restore the exact prior bytes; it semantically reverses the business operation to an acceptable approximation of the prior state, and the developer writes each one by hand [1][4][8]. "Refund the charge" and "release the reserved inventory" are compensations; they leave a visible history (a refund is not the same row-state as never having charged), which is usually fine and occasionally not.

**You gave up Isolation, so partial results leak.** Because each service commits independently, an in-flight saga's partial results are visible to concurrent sagas, producing the classic anomalies: lost updates, dirty reads, and fuzzy (non-repeatable) reads [1][4][5]. To recover isolation-like safety you apply application-level countermeasures. The enumerated taxonomy — reproduced verbatim on Microsoft's page, which attributes it to Richardson's *Microservices Patterns* — is: **semantic lock** (an app-level flag such as `PENDING`/`LOCKED` on the record), **commutative updates** (order-independent operations, so reordering is harmless), **pessimistic view** (reorder steps so risky updates land in retriable steps to avoid dirty reads), **reread value** (re-check the record is unchanged before writing, to catch lost updates), and **version file** (log operations so they can be reordered) [4]. None of these is free; each is code you write and test.

**Coordination is the central design axis.** Two styles:

*Choreography* — services react to each other's events, no central brain. Clean for simple workflows with few services and no single point of failure. It degrades badly with scale: it becomes hard to track which service reacts to which event, it risks cyclic dependencies (participants consuming each other's events or commands, possibly deadlocking), and it makes global timeouts, retries, and end-to-end observability much harder to implement — integration testing requires all services running [4][5].

*Orchestration* — a central coordinator drives each step and each compensation. It avoids cyclic dependencies, gives clear separation of responsibilities and far easier debugging and observability, and makes adding a participant easier. The cost is the extra coordination logic plus a coordinator that is itself a potential single point of failure — one that must be made durable [4][5][7].

**Two supporting mechanisms are non-negotiable.**

First, the *dual-write problem*. Each step must atomically (a) commit its DB update and (b) publish its event. Do those as two independent operations and you get inconsistency: the DB commits but the event is lost, or the event fires but the DB rolls back. The fix is the **transactional outbox**: write the event into an outbox table *inside the same local DB transaction*, then a separate relay/poller — or CDC, or event sourcing — reads committed outbox rows and publishes them, giving at-least-once delivery [1][9][5].

Second, *idempotency*. Because outbox and broker delivery are at-least-once, duplicates are guaranteed, so every step and every compensation must be idempotent [10][9][4]. The standard mechanism is a client-supplied idempotency key: the service records the token, and on a retry with the same token it returns the stored result instead of re-executing the side effect. The Amazon Builders' Library frames the guarantee this buys as "at most once" — the effect happens only once even if the call is made repeatedly [10]. ("Effectively exactly-once" is a common industry paraphrase of the same idea, but the primary source's own wording is "at most once.")

## Trade-offs

The primary sources converge on the mechanism; the real clash is **scope**, not fact.

Richardson, Microsoft, and AWS present the saga as the default answer to cross-service consistency and largely stop at "it lacks isolation — add countermeasures" [1][4][5]. Friedrichsen pushes back that this framing oversells it. His load-bearing distinction: a saga can only logically roll back **business** errors (rule violations — expired card, insufficient inventory). It fundamentally does **not** solve **technical** errors — a crashed service, a timeout, a lost or corrupted message, or a compensating transaction that itself fails [11]. You cannot write "compensating compensations" indefinitely. Technical failures must be handled by a separate durable / eventual-completion layer underneath the saga: persistent retries with escalation, durable workflow state [11]. A saga sitting on top of an unreliable substrate is a false comfort. (This business-vs-technical split rests on a single critical source; treat it as medium-confidence but load-bearing.)

All parties agree on the non-negotiables — idempotent steps, atomic commit-plus-publish via outbox or CDC, and that you are buying *eventual*, not strong, consistency [1][4][5][9]. The blind spot none of the vendor docs squarely confront is domain design: needing a distributed transaction across a few services is often the symptom, and redrawing the boundary is often the cure [4][11].

Honest open questions the sources do not settle: how real systems bound the isolation-anomaly window in practice (the countermeasure taxonomy is well-documented in theory, but production incident data on lost-update/dirty-read frequency was not in the fetched sources); how two sagas that semantically lock each other's records detect and resolve the deadlock; and a quantified latency comparison of saga (extra compensation round-trips) versus 2PC (blocking locks) under contention, which is asserted qualitatively but not measured in these sources.

## In practice

Two production shapes are worth pointing at.

**Durable-execution engines** (Temporal) implement orchestration-style sagas where the workflow's own execution history *is* the saga state — there is no separate `saga_state` table. That history is persisted via event sourcing, so the coordinator survives crashes; the developer only writes the compensations [13]. This is exactly the "durable layer underneath the saga" that Friedrichsen argues you need, folded into the orchestrator itself — which is why the hand-rolled-orchestrator-plus-outbox approach and the durable-workflow-engine approach differ most sharply on the *technical*-error axis, not the business one. (These four are genuine Temporal customers per Temporal's own case studies — ANZ Bank, Maersk, DigitalOcean, Netflix — though not from the saga blog post specifically.)

**Managed orchestrators** (AWS Step Functions) give you the same shape as a state machine with explicit compensation branches — literally named transitions like *Revert Payment*, *Revert Inventory*, *Remove Order* — and AWS notes the managed service mitigates the coordinator-as-SPOF concern via built-in fault tolerance across Availability Zones [7].

The through-line: whether you hand-roll or adopt an engine, the saga contract is the same — local transactions, hand-written compensations, a pivot, idempotent steps, and an outbox. The engine's value is making the coordinator and its retry machinery durable so that technical failures don't quietly leave you in a state no compensation can reach.

## Further reading

1. Pattern: Saga — microservices.io (Chris Richardson) — https://microservices.io/patterns/data/saga.html
2. What is the Saga pattern and when should you use it? — DesignGurus — https://www.designgurus.io/answers/detail/what-is-the-saga-pattern-for-managing-distributed-transactions-and-when-should-you-use-it
3. Sagas — Garcia-Molina & Salem, ACM SIGMOD Record 1987 — https://dl.acm.org/doi/10.1145/38714.38742
4. Saga Design Pattern — Azure Architecture Center (Microsoft Learn) — https://learn.microsoft.com/en-us/azure/architecture/patterns/saga
5. Saga choreography pattern — AWS Prescriptive Guidance — https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-choreography.html
6. Saga Pattern Explained: compensable/pivot/retriable transactions — Ajit Singh — https://singhajit.com/saga-pattern-distributed-transactions/
7. Saga orchestration pattern (Step Functions) — AWS Prescriptive Guidance — https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html
8. Paper Summary: Sagas (1987 Garcia-Molina & Salem) — Temporal / Dominik Tornow — https://dev.to/temporalio/paper-summary-sagas-4bb6
9. Transactional outbox pattern — AWS Prescriptive Guidance — https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html
10. Making retries safe with idempotent APIs — Amazon Builders' Library — https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/
11. The limits of the Saga pattern — Uwe Friedrichsen — https://www.ufried.com/blog/limits_of_saga_pattern/
12. Two-Phase Commit: The Good, the Bad, and the Blocking — Sylvain Tiset — https://medium.com/@sylvain.tiset/two-phase-commit-the-good-the-bad-and-the-blocking-eee29e1f5a84
13. Saga design pattern explained: Benefits, use cases, and implementation — Temporal — https://temporal.io/blog/saga-pattern-made-easy
