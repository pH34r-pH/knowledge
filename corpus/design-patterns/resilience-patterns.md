---
title: Resilience patterns: circuit breaker, retry with jitter, timeout budgets
pillar: design-patterns
method: deep-research
date: 2026-07-01
sources: 12
confidence: high
---

## What it is

Cascading failure is the enemy these three patterns exist to defeat, and it is a positive-feedback loop. A backend that is a little overloaded slows or rejects requests; callers retry; retries add load; the added load pushes the backend further past its edge, producing more errors and thus more retries. A service rejecting 100 QPS sees retries push it to 200, then 300, and stacked retries across layers multiply — if a frontend, a backend, and a database each retry three times, one user action can become 4×4×4 = 64 attempts on the database [7]. Nothing external needs to worsen for the system to collapse; the retries are the amplifier.

Timeouts and deadlines, retry-with-jitter, and the circuit breaker each cut a different link in that loop. A **timeout** (ideally a *propagated deadline*, a "timeout budget") stops a caller from waiting on — and holding resources for — work that is already doomed, and stops servers from doing work no one is waiting for [1][7][10]. **Retry with exponential backoff and jitter** lets a transient error self-heal without synchronizing clients into a thundering herd; the jitter, not the backoff, is the load-bearing part [2][6]. The **circuit breaker** fails fast against a dependency that is already down, so the caller neither waits nor piles on more load [3][4]. None of the three is sufficient alone, and each has a failure mode where, misapplied, it *becomes* the amplifier.

## When to reach for it

Reach for these whenever a call crosses a process boundary you do not fully control and its failure is survivable — a remote API, a database, a downstream microservice. The preconditions are strict and worth stating up front, because getting them wrong turns the cure into the disease:

- **Retries require idempotency.** An operation with side effects is not safe to retry unless it provides idempotency — an idempotency token, a dedupe key, an `If-Match` precondition. This is a hard gate on the entire retry pattern, not a nicety [1].
- **Breakers require a fallback.** Tripping a breaker only helps if the caller has something to do when the call is refused: serve stale or cached data, queue the work, or degrade the feature. A breaker with no fallback just converts a slow failure into a fast one [3][4].
- **Timeouts require data.** A timeout you guessed is a timeout that manufactures failures (too tight) or ties up resources (too loose). Derive it: pick an acceptable false-timeout rate, say 0.1%, and set the timeout to the corresponding downstream latency percentile — p99.9 for that example [1].

If a degraded answer is worthless in your domain, or the operation is irreducibly non-idempotent, you want a clean visible failure instead — not a retry loop that corrupts state.

## How it works

**Timeouts and deadline propagation.** A per-hop timeout is the crude version: each call gets its own fixed budget, independent of how much time the overall request has already burned. The failure mode is that a deep call tree can blow the caller's real deadline many times over while every individual hop stays "within timeout." The better mechanism is a *propagated deadline*: set one absolute deadline high in the stack and pass the *remaining* budget down, subtracting elapsed time at each hop. gRPC implements exactly this — it converts the deadline to `timeout − elapsed` and transmits it in the `grpc-timeout` header, so every downstream inherits a shrinking budget and no service does work whose deadline has already passed [10]. Google's SRE book describes the same discipline: a 30-second deadline at the top becomes 23 seconds after 7 seconds of upstream work [7]. Without propagation, a server spends capacity on requests whose client already gave up — "doing work for which no credit will be granted" — and the client usually retries, feeding the cascade. This is why timeouts, deadlines, and retries are *one coupled system*, not three independent knobs [7][10].

**Retry with backoff and jitter.** Exponential backoff alone is insufficient because it *synchronizes* clients. A single perturbation — a brief network blip — makes every affected client fail at nearly the same instant, back off on the same schedule, and retry in a synchronized wave that re-overloads the recovering backend. Jitter, randomizing the delay, is what smears those retries into an approximately constant rate [2][7]. The three canonical algorithms from the AWS Architecture Blog:

- **Full Jitter:** `sleep = random(0, min(cap, base * 2^attempt))`
- **Equal Jitter:** `sleep = half + random(0, half)`, where `half = min(cap, base * 2^attempt) / 2`
- **Decorrelated Jitter:** `sleep = min(cap, random(base, prev_sleep * 3))`

In AWS's simulation with many contending clients, the jittered strategies cut total call volume by more than half versus backoff-without-jitter; Full Jitter did the least client work while staying competitive on completion time. AWS's own conclusion is that jittered backoff broadly "should be considered a standard approach," and it treats Full versus Decorrelated as roughly interchangeable rather than crowning a single winner [2]. Full Jitter is nonetheless the production default in the AWS SDKs [11], so the preference is defensible — just sourced from the implementation, not the simulation paper.

**Capping retries so they cannot amplify.** Backoff spreads retries in time; it does not bound their *count*. Google SRE prescribes three caps working together: randomized exponential backoff, a **server-wide retry budget** (e.g. only 60 retries/minute per process, then fail fast) [7], a **per-client retry ratio** (only ~10% of a client's requests may be retries) [6], and an explicit "overloaded; do not retry" status so upstream layers back off instead of piling on [7]. Two further rules: retries are only safe for idempotent operations [1], and you should **retry at exactly one layer** of the stack — retrying at every layer multiplies attempts geometrically, which is the 64-attempt example above. AWS states the single-point rule as a best practice; Google frames the same idea as thinking about the service holistically before adding retries at a given level [1][7].

**The circuit breaker.** Fowler's canonical mechanism: wrap the call; count failures; once failures cross a threshold the breaker *trips* to **OPEN** and rejects calls immediately without touching the downstream; after a reset timeout it moves to **HALF-OPEN** and lets a probe call through, closing on success and re-opening on failure [3]. Not every error should count — a business-logic 4xx is a normal outcome handled by ordinary code; the breaker should count only failures that indicate the dependency itself is unhealthy, such as timeouts and 5xx [3][4].

Two production implementations concretize this. **Hystrix** trips only when request volume in a rolling window exceeds a threshold (default 20 requests / 10s) *and* the error percentage exceeds a threshold (default >50%) [12]; after a sleep window it lets a single probe through. It also bundles the **bulkhead** pattern — each dependency gets its own thread pool, so latency in one dependency saturates only its pool and cannot exhaust the caller's threads — and fires fallbacks on any of four conditions: exception, open circuit, pool/semaphore rejection, or timeout [4]. **Resilience4j**, the modern successor to the now-dormant Hystrix, exposes the same state machine with defaults `failureRateThreshold` 50%, `minimumNumberOfCalls` 100 before the rate is computed, `waitDurationInOpenState` 60s, `permittedNumberOfCallsInHalfOpenState` 10, a count- or time-based sliding window, and adds **slow-call detection** (`slowCallRateThreshold` / `slowCallDurationThreshold`) so calls that succeed but are consistently slow can also trip the breaker [5].

## Trade-offs

The sharpest disagreement in this space is about the circuit breaker itself. Fowler [3], Hystrix [4], and Resilience4j [5] present it as a first-class primitive with detailed machinery to tune. Marc Brooker, an AWS Distinguished Engineer, argues the near-opposite: modern systems are *designed* to partially fail, and a circuit breaker is a **global binary switch**, so it "turns partial failures into complete failures" [8]. Consider a sharded backend where only shards A–H are overloaded. A single breaker must either trip globally — breaking calls to the healthy shards — or stay closed and do nothing about the sick ones. It cannot do both, and near the threshold it *flaps* between fully-retrying and fully-not [8].

The reconciliation none of the sources states outright is a **scope distinction**. A circuit breaker is genuinely good at two things everyone agrees on: failing fast to avoid wasted work against a dependency that is *wholly* down, and enabling graceful degradation via a fallback. Use it for that. But do *not* use a single global breaker as your **retry limiter** in a sharded or multi-tenant system — for that job, use a per-target **token-bucket retry budget**. Brooker's own simulation, importantly, frames this as a tradeoff rather than a rout: the token bucket performs better at low-to-moderate failure rates, while the circuit breaker adds no extra load at *very high* failure rates; both have drawbacks, and "choosing the right retry strategy depends on what we want to achieve" [9]. The mechanism, though, is clearly attractive: successful calls deposit fractional tokens, retries consume whole tokens, so at low failure rates it behaves like normal retries and as failure climbs it throttles retries smoothly instead of switching modes [9].

The under-addressed layer across nearly every source is **operational**: they specify thresholds and windows but say little about how an operator detects a *flapping* breaker, tunes `failureRateThreshold` / `minimumNumberOfCalls` without production traffic data, or avoids the well-known failure mode where a mis-tuned breaker — or an over-aggressive adaptive rate limiter — becomes the cause of the outage rather than the cure. Notably, the AWS timeout rule [1] gives a percentile-based derivation for one knob; there is no comparable published derivation for breaker thresholds.

## In practice

The token-bucket-over-breaker argument is not just theory: it is the production retry limiter in the AWS SDKs. **Standard** retry mode uses a retry-quota token bucket — retries deduct tokens, successes refill them, and when the bucket is empty the SDK fails fast instead of retrying, which structurally caps retry amplification. **Adaptive** mode adds a client-side rate limiter that can delay even the *initial* request when it detects throttling — with the documented caveat that in a multi-tenant client, throttling seen on one resource can wrongly slow requests to unaffected resources [11]. That caveat is likely why AWS still defaults to standard rather than adaptive.

Composed around a single outbound call, a resilient path layers the patterns roughly as **timeout (+ inherited deadline budget) → bulkhead / concurrency isolation → circuit breaker → retry-with-jitter under a budget**, with idempotency required on the retries and a fallback for the open-breaker and exhausted-budget cases [1][3][4][7][9]. Each layer closes a different link of the feedback loop, and each used alone has a signature failure mode: breakers flap on partial failure, unbudgeted retries amplify a brownout into an outage, and per-hop timeouts burn downstream capacity on work no one is waiting for. The authoritative composition *order* — and whether it should differ for control-plane versus data-plane calls — is settled by no single source; treat the layering above as a well-supported default, not gospel.

## Further reading

1. Amazon Builders' Library — Timeouts, Retries, and Backoff with Jitter (Marc Brooker) — https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
2. AWS Architecture Blog — Exponential Backoff And Jitter — https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
3. Martin Fowler — CircuitBreaker — https://martinfowler.com/bliki/CircuitBreaker.html
4. Netflix Hystrix Wiki — How it Works — https://github.com/netflix/hystrix/wiki/how-it-works
5. Resilience4j — CircuitBreaker docs — https://resilience4j.readme.io/docs/circuitbreaker
6. Google SRE Book — Handling Overload — https://sre.google/sre-book/handling-overload/
7. Google SRE Book — Addressing Cascading Failures — https://sre.google/sre-book/addressing-cascading-failures/
8. Marc Brooker — Will circuit breakers solve my problems? — https://brooker.co.za/blog/2022/02/16/circuit-breakers.html
9. Marc Brooker — Fixing retries with token buckets and circuit breakers — https://brooker.co.za/blog/2022/02/28/retries.html
10. gRPC Blog — gRPC and Deadlines — https://grpc.io/blog/deadlines/
11. AWS SDKs and Tools — Retry behavior — https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html
12. Netflix Hystrix Wiki — Configuration (default thresholds: requestVolumeThreshold 20, rolling window 10000ms, errorThresholdPercentage 50) — https://github.com/Netflix/Hystrix/wiki/Configuration
