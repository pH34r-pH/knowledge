---
title: Idempotency keys and exactly-once-effect APIs
pillar: design-patterns
method: deep-research
date: 2026-07-01
sources: 9
confidence: high
---

## What it is

"Exactly-once delivery" is a thing you cannot build over an unreliable network, and the reason is older than any API. The Two Generals Problem says that when two parties communicate over a lossy channel, no finite exchange of messages can make both certain the other received the last one — any acknowledgment can itself be lost, so a sender can never *know* whether to stop retrying [8]. That impossibility propagates directly into distributed systems: a client fires a request, the network drops the response, and now the client is in the exact position of the first general — the charge may have gone through, or it may not have, and there is no signal that settles it. Its only safe move is to retry, which means the server must be prepared to see the same logical request more than once.

So the guarantee you actually ship is not exactly-once delivery but **at-least-once delivery plus an idempotent receiver**, which composes to exactly-once *effect*: the system's state converges to the same result no matter how many times a request arrives [8][9]. This delivery-versus-effect distinction is the whole game. You give up on making the network deliver each message precisely once — provably impossible — and instead make the *receiver* absorb duplicates so the observable outcome is as if the request ran once. The mechanism that does the absorbing is an **idempotency key**: a caller-supplied unique identifier attached to each logical request, which the server records so it can recognize a retry and refuse to do the work twice [1][4].

## When to reach for it

HTTP already bakes idempotency into its method semantics, and knowing where that coverage ends tells you exactly where you need the key. Under RFC 9110, `GET`/`HEAD`/`OPTIONS`/`TRACE` are *safe* (read-only) and idempotent; `PUT` and `DELETE` are unsafe but idempotent *by definition* — issuing N identical `PUT`s has the same effect as one [5]. `POST` is neither safe nor idempotent, which is precisely why `POST` endpoints — create-a-charge, create-a-customer, create-an-order — are the ones that need an explicit idempotency layer bolted on. Stripe follows this exactly: every `POST` accepts an `Idempotency-Key` header, while `GET` and `DELETE` are idempotent already and ignore the key [4].

Reach for idempotency keys whenever a mutating request crosses a boundary where the caller can retry but cannot observe whether the first attempt landed: payment APIs, resource-creation endpoints, and any consumer of an at-least-once event stream. The three delivery guarantees frame the design space [6][8][9]:

- **At-most-once** — no retries; may lose data, never duplicates.
- **At-least-once** — retries; may duplicate, never loses. This is the default for queues, webhooks, and event buses (SQS, EventBridge, and webhook delivery all give you this) [6][9].
- **Exactly-once** — achievable only as an *effect/processing* guarantee, never as a raw delivery guarantee.

If your infrastructure hands you at-least-once — and almost all of it does — the receiver *must* be idempotent. That is not optional hardening; it is the other half of the contract the delivery layer assumes you will hold up.

## How it works

**The atomic record-and-mutate is the load-bearing invariant.** The single non-negotiable correctness requirement is that recording the idempotency token and applying *all* of the request's mutations happen as one ACID all-or-nothing operation [1][2]. If they are separable, you get exactly the two partial states that break the retry contract: the token stored but the work never done (so the retry sees a "known" key and returns success for a charge that never happened), or the work done but the token never stored (so the retry re-runs and double-charges). Wrap the token insert and the business writes in a single transaction and both failure modes vanish — a crash either rolls back everything, leaving the retry to start clean, or commits everything, leaving the retry to recognize the key and short-circuit.

**Return the semantic response, not an error.** A naive implementation catches the duplicate and returns `ResourceAlreadyExists`. That is wrong, and the reasoning is subtle: even though the retry produced no side effect on the server, *returning an error is itself a side effect from the client's perspective*, because it forces the client down a different code path than the original success [1]. The correct behavior is to return a response reflecting the resource's current state — AWS's example is an EC2 instance that reads `pending` on the first call, `running` on a later retry, and `terminated` after deletion [1]. The retry is answered as if it were a fresh status query, not punished for being a retry.

**Concurrency: lock the key row.** The happy path is easy; the hard case is two retries racing in parallel before the first has committed. The fix is to lock the idempotency-key row — a `locked_at` timestamp under a `SERIALIZABLE` transaction. A concurrent retry that finds the key locked and recent gets a `409 Conflict` ("request in progress"); if two transactions genuinely race to lock the same key, Postgres aborts one of them. Brandur Leach's Postgres implementation uses `SERIALIZABLE` isolation for exactly this [2]. Stripe surfaces the same behavior at the API edge: concurrent requests on one key can conflict, and — importantly — those conflicts are *not* cached, so the loser can safely retry [4].

**Multi-step operations: a recovery-point state machine.** The genuinely hard case is a request that mixes local DB writes with foreign-state mutations — creating a local record, *then* calling Stripe, *then* sending an email. You cannot wrap a third-party HTTP call in your database transaction, so a single atomic operation is impossible. Brandur's answer is to split the request into **atomic phases** — runs of local mutations in transactions, separated by the foreign calls — driven by a persisted `recovery_point` column that acts as a state machine: `started → ride_created → charge_created → finished` [2]. Each phase commits its recovery point durably before the next foreign call, so a crash resumes from the last completed phase instead of restarting from zero.

**Idempotency composes across boundaries only if every hop is keyed.** The recovery-point machine still has a hole: if you crash *after* charging Stripe but *before* recording that you did, the resume re-issues the charge. The fix is to pass a stable, derived key on the downstream call — Brandur derives the Stripe `idempotency_key` deterministically from the local key, e.g. `rocket-rides-atomic-<key.id>` [2]. Now the foreign system dedupes the retry itself, and idempotency composes end-to-end. The general principle: idempotency crosses a service boundary only if the call across it is keyed with something stable across your own retries.

## Trade-offs

**The word "exactly-once" is a genuine terminological fight, and it resolves on the delivery/effect axis.** Confluent markets Kafka as delivering "exactly-once semantics," while the Two Generals literature insists exactly-once delivery is impossible [6][8][9]. Both are right once you scope them. Kafka's idempotent producer attaches a producer ID and a per-partition monotonic sequence number; the broker dedupes resends and persists the sequence number to the replicated log, so a new leader after failover still recognizes duplicates, and transactions extend this to atomic multi-partition writes [6][7]. That guarantee holds because Kafka's input, output, and state all live inside one closed system and commit as one operation. Confluent scopes its exactly-once claim to Kafka-internal processing; from that scoping it follows — as general distributed-systems reasoning, not a verbatim Confluent pronouncement — that extending EOS end-to-end to an *external* DB or API would require that external system to participate in a two-phase commit, which is generally impractical. So the two camps do not actually disagree: any guarantee that crosses the network to a system you don't control is at-least-once-plus-idempotent-effect, not true exactly-once.

**Fencing tokens cover a race that idempotency keys do not.** This is the trade-off most implementations miss. Idempotency keys protect against duplicate *requests*; they do nothing against a paused process resuming and clobbering newer state. Kleppmann's scenario: a client acquires a lock, stalls in a stop-the-world GC pause long enough for the lock to expire and be reassigned, then resumes and issues a write still believing it holds the lock [3]. The idempotency key is irrelevant — this is a *different* logical write arriving late, not a retry. The fix is a **fencing token**: a strictly monotonically increasing number issued on each lock acquisition, which the *storage service must actively check* and reject if it has gone backwards [3]. The token only works if the storage layer enforces it; a token nobody validates is decoration. Kleppmann's related point is that locks split into "efficiency" locks (a failure only wastes work) and "correctness" locks (a failure corrupts data), and he argues Redlock is both too heavyweight for the former and unsafe for the latter, because it generates no fencing token and so cannot prevent the delayed-client race even if its algorithm were otherwise perfect [3].

**Key retention is the underexplored cost.** Keys must be retained at least as long as a retry can plausibly arrive. Stripe stores keys for at least 24 hours, then may prune them — reusing a pruned key runs as a brand-new request [4]. AWS keeps token state for the resource's lifetime plus a grace interval, so a late retry arriving after deletion still gets a coherent response [1]. Neither vendor rigorously analyzes the collision risk when a genuinely new operation happens to reuse a pruned key, nor the storage-cost-versus-safety curve of a longer window; a too-short window trades storage for a real correctness hazard. The subtler failure mode no source fully addresses: a **client that generates a fresh key on every retry** silently defeats the entire mechanism, because the server sees every attempt as new. The key must be stable across the client's own retries — random-UUID-per-logical-operation, not random-UUID-per-HTTP-call.

## In practice

Stripe's API reference is the most precise citable specification of a production idempotency layer, and its documented edge cases are the ones worth internalizing [4]:

- Send the **same key with different request parameters** and you get an error — the server refuses to let one key mean two different operations.
- **Results are saved only after the endpoint begins execution**, so parameter-validation failures and concurrent-request conflicts are *not* cached; a client that hit one of those can safely retry rather than being permanently stuck with a cached failure.
- Keys may be **up to 255 characters**; the recommended format is a V4 UUID or a random string with enough entropy to avoid collisions [4][6]. Do not use sensitive data as a key — it is stored and logged.

Brandur's Postgres write-up is the companion piece: it shows the actual table design (an `idempotency_keys` table carrying the `recovery_point`, `locked_at`, and the serialized response), the `SERIALIZABLE` transaction discipline, and the atomic-phase state machine that makes the pattern survive crashes mid-flight against a foreign API [2]. AWS's Builders' Library article by Malcolm Featonby is the third leg — it names the primitive (`ClientToken` on EC2's `RunInstances`), states the ACID all-or-nothing requirement as the core invariant, and makes the "returning an error is itself a client-visible side effect" argument that reframes how you handle the duplicate case [1]. Read together, they give you the contract (AWS), the wire behavior (Stripe), and the storage-layer implementation (Brandur).

## Further reading

1. Making retries safe with idempotent APIs — Malcolm Featonby, Amazon Builders' Library — https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/
2. Implementing Stripe-like Idempotency Keys in Postgres — Brandur Leach — https://brandur.org/idempotency-keys
3. How to do distributed locking — Martin Kleppmann — https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html
4. Idempotent requests — Stripe API Reference — https://docs.stripe.com/api/idempotent_requests
5. RFC 9110: HTTP Semantics (safe and idempotent methods) — https://www.rfc-editor.org/info/rfc9110/
6. Exactly-Once Semantics Are Possible: Here's How Apache Kafka Does It — Confluent — https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/
7. Exactly-once semantics with Kafka transactions — Strimzi blog — https://strimzi.io/blog/2023/05/03/kafka-transactions/
8. Two Generals' Problem and Idempotency — Ali Gelenler — https://medium.com/@ali.gelenler/two-generals-problem-and-idempotency-4d28f4b07694
9. At-Least-Once vs. Exactly-Once Webhook Delivery Guarantees — Hookdeck — https://hookdeck.com/webhooks/guides/webhook-delivery-guarantees
