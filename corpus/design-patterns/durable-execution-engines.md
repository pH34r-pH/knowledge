---
title: Durable execution engines (Temporal, Restate, DBOS)
pillar: design-patterns
method: deep-research
date: 2026-07-01
sources: 13
confidence: high
---

## What it is

Durable execution lets you write a multi-step workflow as ordinary linear code — call service A, sleep three days, call service B — while the engine guarantees a crash anywhere in the middle resumes from the last completed step instead of restarting or stranding a half-finished operation [1]. The engine persists every step's outcome to durable storage as it happens; on recovery it re-runs the code from the top, but each already-completed step returns its recorded result instead of re-executing, walking program state back to the crash point [1][2]. In one sentence: your program's execution state — local variables, position in the code, which calls returned — becomes a durable, crash-recoverable artifact rather than volatile process memory.

This absorbs the **technical-failure** layer a saga alone cannot reach. Sagas as described in [9] define business compensation for a completed step (refund the charge, release the reservation); crash recovery — an orchestrator dying, a worker lost mid-step, a transient network fault — is outside that pattern's scope. Durable execution handles exactly that layer via the persisted log plus automatic retries, timeouts, and heartbeats [1][7]; compensation stays application code [7][9]. It is the durable substrate the saga pattern quietly assumes underneath it.

## When to reach for it

Reach for an engine when a workflow is long-lived, multi-step, cross-service, and failure-sensitive: payments, provisioning, order fulfillment, human-in-the-loop approvals, agentic pipelines chaining expensive LLM calls you cannot afford to redo. The defining property is that losing progress mid-flight is costly and the flow lives long enough that a deploy or crash *will* hit it in flight.

The sharper discipline is knowing when a hand-rolled orchestrator plus transactional outbox is right instead. An outbox guarantees events are not lost — it does *not* guarantee the system reaches a correct end state, and it degrades once workflows grow long, span services, and need coordination, retries, timeouts, and compensation [9]. For short, mostly single-service flows where "events aren't lost" is the whole requirement, the outbox is enough and you avoid running a new stateful system; where flows need durable *coordination* across services, the engine starts earning its operational cost [9].

A useful tell: if you are hand-building a `workflow_state` table, a poller that advances stuck workflows, per-step retry counters, and timeout sweeps, you are reimplementing a durable execution engine badly.

## How it works

**The shared core is an append-only log plus deterministic replay.** Everything in a workflow's lifecycle is appended to durable storage; on crash the workflow is reconstructed by replaying that history, substituting recorded results for completed work [1][2]. The engines differ in what gets logged, where it lives, and how strict the replay contract is.

**Replay imposes a determinism contract.** Because state is rebuilt by re-executing code against recorded history, workflow code must issue the same command sequence given the same input and history; any value not in the history — system clock, `random()`, direct I/O — differs between original run and replay and throws a non-determinism error [2][3]. Temporal takes the strict end: workflow code re-executes fully, so all non-deterministic and I/O work is quarantined into **Activities**, which run outside the replay path, may fail or time out, and are retried automatically [2][3][7]. Restate's journal-of-results model appears more permissive, though a source-backed enumeration of which code changes are safe there was not established in this pass (open question).

**Temporal — the heavy, mature end.** A separate cluster (Frontend, History, Matching services plus a persistence store) fronting a separately deployed worker fleet [11]. It distinguishes technical from application failure via four Activity timeouts — schedule-to-start, start-to-close, schedule-to-close, heartbeat: silent heartbeat cessation signals a crashed or hung worker (technical), a returned error signals application failure; both trigger retries per the Retry Policy [7]. Defaults: initial interval 1s, backoff coefficient 2.0, maximum interval 100x the initial, *unlimited* attempts; Activities carry a policy by default, Workflows do not, and an `ApplicationFailure` with `nonRetryable=true` fails immediately [8]. Temporal also enforces hard history limits — warning at 10,240 events, termination past 51,200 (or >2,000 Updates, >10,000 Signals) — with **Continue-as-New** closing the execution and starting fresh with carried-over state to stay under the cap [2].

**DBOS — the light end.** An embedded library, no separate process. It checkpoints workflow inputs, step outputs, and the final outcome into your *existing* Postgres (one write per step plus two per workflow); on restart it scans for `PENDING` workflows and re-runs them, skipping steps whose output is already checkpointed [5][6]. Its distinctive guarantee: when a step writes to the same Postgres storing workflow state, the data write and durability checkpoint commit in a **single transaction** — the step fully commits, checkpoint included, or rolls back entirely: genuine transactional exactly-once for that step [6]. The caveat: this holds specifically for Postgres-touching steps; for external systems DBOS falls back to at-least-once plus idempotency like everyone else (exact external-call semantics were not pinned from a single primary source — open question) [6].

**Restate — the middle.** A single self-contained Rust binary with no external DB. Events (invocations, journal entries, state updates) append to an embedded replicated log, **Bifrost**; partition-local processors tail it, materialize state into RocksDB (snapshotted to object storage), and can be rebuilt deterministically from the log [4]. Every external interaction is recorded *before* its result is observed, so completed steps replay rather than re-execute; invocations suspend while awaiting a promise, any healthy worker can recover an in-flight execution with no checkpoint code, and **epoch numbers** fence old leaders against split-brain [1][4].

## Trade-offs

**Operational weight is the real decision.** Production Temporal is three services plus a persistence store, a metrics pipeline, and a worker fleet, with shard rebalancing and retention tuning to manage [11]. DBOS adds no separate process but is throughput-bounded by one Postgres — WAL and lock pressure under heavy fan-out — and lacks a first-class event-history UI out of the box [11]. Restate sits between: one binary, but its own replicated log to operate. You are choosing a stateful system to keep alive at 3 a.m., not just an API.

**Code evolution is a production hazard, sharpest in Temporal.** Changing running-workflow code — reordering activities or timers, adding a non-deterministic call, removing a step — throws a non-determinism exception on replay [3][12]. Safe evolution requires patching APIs (`Patched`/`GetVersion`) or Worker Versioning, plus replay testing against recorded histories before deploy [3][12]. The outbox approach never levies this tax, and it is easy to underweight until one bad deploy breaks every in-flight workflow.

**Performance numbers are directionally useful but vendor-reported.** DBOS claims sub-millisecond per-step overhead; its own open-source benchmark runs a 5-step DB-transaction workflow in ~40ms versus over 1s in AWS Step Functions (~25x), with a ~$40/month vs ~$25K/month cost illustration at 100 workflows/s [10]. Restate reports median step latency ~3ms at low load, ~10ms at high load (p99 ~54ms/~98ms), and ~94K steps/second [4]. No independent reproduction was located; each vendor's benchmark flatters its own architecture (open question).

**One disambiguation.** The widely-cited 2022 VLDB paper "DBOS: A DBMS-oriented Operating System" (Skiadopoulos, Stonebraker, Zaharia, et al.) is about building OS services — scheduling, file management, IPC — on a distributed transactional DBMS. It is *not* about durable workflow execution; that capability is the later DBOS Transact library, and mechanism claims belong to the Transact docs, not the paper [13].

## In practice

The choice reduces to three postures. **DBOS** when you already run Postgres, want zero new infrastructure, and workflows fit one database's throughput — transactional exactly-once for Postgres-touching steps is a real correctness win you get for free [5][6]. **Temporal** when workflows are large, long-lived, and fleet-spanning, and the mature timeout/retry/versioning machinery and event-history observability justify running the cluster and paying the determinism tax [2][7][8][11]. **Restate** when you want one self-contained binary with log-grade per-step throughput and no external database, accepting a younger ecosystem [4].

Across all three the contract matches a hand-rolled orchestrator's: steps must be idempotent, external calls are at-least-once, compensation is your code. What the engine buys is a durable coordinator and retry machinery, so a mid-flight crash resumes cleanly rather than stranding the flow in a state no compensation can reach [1][9][11]. Honest gaps: named production postmortems were not retrieved (operational-pain claims lean on comparison writeups), and the Temporal Cloud vs self-hosted cost crossover comes from one comparison piece — re-verify against current pricing before quoting.

## Further reading

1. What is Durable Execution? A Definitive Guide (Restate) — https://www.restate.dev/what-is-durable-execution
2. Events and Event History | Temporal Platform Documentation — https://docs.temporal.io/workflow-execution/event
3. Temporal Workflow Definition (determinism constraints) | Temporal Docs — https://docs.temporal.io/workflow-definition
4. Building a modern Durable Execution Engine from First Principles (Restate) — https://www.restate.dev/blog/building-a-modern-durable-execution-engine-from-first-principles
5. DBOS Architecture / How Workflows Recover | DBOS Docs — https://docs.dbos.dev/architecture
6. Why You Should Build Durable Workflows With Postgres (DBOS, Peter Kraft) — https://www.dbos.dev/blog/why-postgres-durable-execution
7. Detecting Activity failures (four timeout types, heartbeats) | Temporal Docs — https://docs.temporal.io/encyclopedia/detecting-activity-failures
8. What is a Temporal Retry Policy? (defaults, non-retryable) | Temporal Docs — https://docs.temporal.io/encyclopedia/retry-policies
9. System Design Series: Transactions in a Distributed Architecture — SAGAs, Outbox, Durable Execution — https://medium.com/@sanilkhurana7/system-design-series-the-story-and-present-of-durable-execution-and-how-to-use-it-in-your-52509b94d01e
10. DBOS vs. AWS Step Functions Performance Benchmark (DBOS) — https://www.dbos.dev/blog/dbos-vs-aws-step-functions-benchmark
11. DBOS vs Temporal: When Postgres Is Enough for Durable Workflow Execution (Tiarê Balbi Bonamini, 2026) — https://www.tiarebalbi.com/en/blog/dbos-vs-temporal-postgres-durable-execution
12. Replay Testing To Avoid Non-Determinism in Temporal Workflows (Bitovi) — https://www.bitovi.com/blog/replay-testing-to-avoid-non-determinism-in-temporal-workflows
13. DBOS: A DBMS-oriented Operating System (PVLDB Vol 15, 2022) — https://vldb.org/pvldb/vol15/p21-skiadopoulos.pdf
