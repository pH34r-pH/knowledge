---
title: CQRS and event sourcing
pillar: design-patterns
method: storm
date: 2026-07-01
sources: 12
confidence: high
---

## What it is

Two patterns that ship together often enough to be confused, but are separable decisions.

**Event sourcing** makes the append-only log of domain events the system of record. Current state is not stored; it is *derived* by replaying events onto an empty aggregate. The consequence that matters: a state-only (CRUD) store is lossy in an irreversible way — it overwrites the transition and keeps only the result. Greg Young's design axiom is that "state transitions are an important part of our problem space and should be modelled within our domain," and that if you don't store intent "there are an entire series of questions you can no longer ask the data" [3].

**CQRS** (Command Query Responsibility Segregation) is the smaller decision to split the write model from one or more read models. Critically, this is a *code-level* separation, not a two-database mandate: "nothing prevents the Write Model and the Read Model from having the same structure or using the same tables," and message queues are optional — "you can start smaller with the tables and database views, in-memory queue or CDC" [4]. Event sourcing is "quite often conflated with CQRS," but "they are different patterns" [4].

The single most useful mental move is to hold three choices apart: CQRS (separate read/write models), event sourcing (log as source of truth), and async messaging (projections updated out-of-band). Much of the feared cost comes from adopting all three when the problem justified one.

## When to reach for it

The strongest cautions come from the pattern's own architects and the largest cloud vendor, not from CRUD traditionalists. Fowler, who documented CQRS, writes that "for most systems CQRS adds risky complexity" and the benefit is "very much the minority case" [5]. Microsoft leads its event-sourcing doc with a warning box: "For most systems and most parts of a system, traditional data management is sufficient," and notes the pattern is "costly to migrate to or from" and "constrains future design decisions" [6].

The dominant failure mode is **scope**. Fowler scopes CQRS to "a BoundedContext… and not the system as a whole" [5]; Young insists CQRS "is not a top level architecture" [3]. It is correct for a payment ledger or a reservation/order subsystem and catastrophic as a default persistence strategy for a whole CRUD app.

Reach for it when one of these is a *core product requirement*, not a nice-to-have: a complete, tamper-evident audit history; temporal queries ("what did state look like at time T"); or intent-capture where the sequence of decisions, not just the final value, is the asset (finance, ledgers, regulated or high-stakes domains). Absent one of those drivers, default to CRUD plus a well-designed audit table.

## How it works

**The log as source of truth.** Each command that mutates an aggregate appends one or more immutable events (`OrderPlaced`, `ItemShipped`). To load an aggregate you fetch its event stream and fold the events left-to-right into current state. Fowler names the three capabilities this buys [1]: **complete rebuild** — "discard the application state completely and rebuild it by re-running the events from the event log on an empty application"; **temporal query** — "determine the application state at any point in time… starting with a blank state and rerunning the events up to a particular time or event"; and **audit** — "it's easy to serialize the events to make an Audit Log." Because state is derived from events rather than tracked by a parallel audit table or trigger, the audit log cannot silently drift from reality: the event store *is* the audit log. Append-only ledgers are the oldest instance of the pattern.

**Snapshots and projections.** Replaying thousands of events per load is expensive, so long-lived aggregates persist a periodic snapshot — a materialized fold up to event N — and replay only what follows; a snapshot is a cache, never the source of truth. Read models are *projections*: consumers that fold the same stream into whatever shape a query needs (a denormalized table, a search index, a cache) and can be dropped and recreated by replaying. This is where async messaging usually enters — projections updated out-of-band from the write are what introduce eventual consistency (see Trade-offs).

**You never edit history.** Immutability is load-bearing and permanent. If a past event was wrong, you do not mutate it; you append a corrective one. Microsoft defines the mechanism: "a compensating event is a new event that reverses or corrects the effect of a previous event" [6]. Downstream consumers observe the fix by processing that event, so every projection converges without special-casing. Fowler frames the same move: "if we find a past event was incorrect, we can compute the consequences by reversing it and later events and then replaying the new event and later events" [1].

**Consistency and scaling.** Event sourcing does not force eventual consistency: commands run against current (replayed) state, so "eventual consistency and specifically separate database for reads is in no way a strict requirement" — you can even update the read side in the same transaction [11][4]. Eventual consistency is something you *opt into* by making projections async, not an intrinsic tax of the log. Append-only also scales well: immutable events "can be cached, copied and distributed without any problems" [2], and append-only writes "avoid the row-level lock contention that update-in-place systems create" [6] — which is what lets read and write sides scale independently.

## Trade-offs

The literature reads as paired claims where a booster and an operator describe the *same code* with opposite verdicts; the resolution is almost always scope and conflation, not a factual dispute.

**"Complexity is earned" vs. "an unwarranted amount of risk."** Proponents frame the log as the only way to make history and intent first-class. Fowler calls the reflexive version "a significant force for getting a software system into serious difficulties… even in the hands of a capable team" [5]. Both hold once you resolve scope: earned inside a bounded context with a real audit/temporal requirement, unwarranted as a system-wide default.

**"The audit log is a debugging superpower" vs. "oversold."** The pitch: replay to the exact state where a user hit a bug — impossible with state-only storage. Chris Kiehl's production postmortem counters: "99% of the time bad states were bad events caused by your standard run-of-the-mill human error" [10]. The superpower is real but exercised far less than advertised, and does nothing against the most common failure — a correctly-written event carrying wrong data. Fixing the bug in code "doesn't fix the historical events" [6]; you still owe a compensating event or an upcaster.

**"Just replay the log to rebuild any read model" vs. "rebuilds are a weekend job."** Rebuildability is genuine, but at volume it becomes an operational bottleneck. The Overeem et al. study of 19 systems / 25 engineers names rebuilding projections a leading challenge and reports mature teams must build tooling to recreate projections and snapshots up front [8]. One engineer schedules rebuilds on weekends rather than running them hot (a paraphrase from the paper body; the *named* "rebuilding projections" challenge is the verbatim, verified part) [8]. Kiehl adds the multiplier: "that first extra projection you add doubles the amount of code that touches your event stream" [10].

**Who owns eventual consistency?** Not event sourcing intrinsically — commands run against current state [11]. But the moment you add async CQRS read projections (the usual pairing), you inherit user-visible bugs: "newly created data will 404, deleted items will awkwardly stick around, duplicate items will be returned" [10], plus at-least-once delivery forcing idempotent consumers. The skeptic's UX warning survives the "it's optional" correction, because the optional thing is what everyone actually ships.

**Schema evolution is the standing tax.** The cost boosters gloss, and it is day-two not build-time: events outlive the code that wrote them, so the deserializer must forever tolerate old shapes — Postel's Law, "be conservative in what you send, be liberal in what you accept" [7]. The study names schema evolution the leading challenge and gives a five-rung maturity ladder — versioned events, weak schema, upcasting, in-place transformation, copy-and-transform — start with the first two, graduate to the last two only when forced [8][9]. Deployment compounds it: forward compatibility across versions is "extremely hard," rollback in an append-only system is often infeasible, and teams sometimes "accept downtime" instead [7] (medium confidence).

**Immutability collides with GDPR.** "The append-only, immutable nature of an event store conflicts with data protection regulations" [6]. Two resolutions: store personal data *outside* the event store and reference by ID so it deletes independently, or crypto-shred — encrypt PII per subject and delete the key, rendering it unrecoverable while leaving event structure intact [6]. Real teams split on anonymize-and-rewrite (breaking immutability) versus separating PII [8].

**What everyone agrees on:** apply it to a bounded context, never system-wide [5][3][6]; the genuine justifications are narrow (audit, temporal query, intent-capture as core requirements); fix state only by appending a compensating event; and adopting it before you understand the domain is a recognized trap [7].

**The blind spot no source closes.** Nobody gives a *quantitative* break-even — event volume, retention horizon, regulatory class, or team size that flips the decision. And no source costs full event sourcing against the middle option that likely wins most disputed cases: CRUD plus an append-only audit/history table, database temporal tables, or CDC. The debate is framed as event-sourcing-vs-naive-CRUD, skipping the thing in between.

## In practice

Nat Pryce's and Joris Kuipers' production postmortems catalog the anti-patterns teams ship, each of which "missed the whole point of event sourcing" and required rework [12][7]: persisting current state *outside* the event stream (so you can no longer rebuild); confusing event-*driven* with event-*sourced*; and using the event store as a message bus, which contaminates domain history with transient technical events. The recurring root cause is adopting the pattern "too early, before they really understand the domain" [7] — because you cannot cheaply reshape aggregate boundaries once events are written against them, an early wrong guess becomes a permanent migration burden.

A decision heuristic that respects the sources: pick one bounded context whose *product* is its history — a ledger, a reservation system, an approvals workflow. Start with event sourcing plus CQRS sharing one database (synchronous projection), so you get audit and rebuildability without inheriting eventual consistency, and add versioned events plus weak-schema deserialization from day one [8]. Introduce async projections and a separate read store only when a measured read-scaling or read-shape need appears — and treat the arrival of your second projection as the moment to build rebuild tooling, since that is when the maintenance surface doubles [10]. One caveat on currency: the "immature tooling" finding rests on 2019–2021 sources, so whether managed event stores and framework upcasting have since closed the gap is unverified here.

## Further reading

1. Event Sourcing — Martin Fowler — https://martinfowler.com/eaaDev/EventSourcing.html
2. The Basics of Event Sourcing and Some CQRS (Greg Young) — InfoQ — https://www.infoq.com/news/2014/09/greg-young-event-sourcing/
3. CQRS and Event Sourcing (Greg Young, Code on the Beach 2014 transcript) — Kurrent/EventStoreDB — https://www.kurrent.io/blog/transcript-of-greg-youngs-talk-at-code-on-the-beach-2014-cqrs-and-event-sourcing
4. CQRS facts and myths explained — Oskar Dudycz, Event-Driven.io — https://event-driven.io/en/cqrs_facts_and_myths_explained/
5. bliki: CQRS — Martin Fowler — https://martinfowler.com/bliki/CQRS.html
6. Event Sourcing Pattern — Azure Architecture Center, Microsoft Learn — https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing
7. Day Two Problems When Using CQRS and Event Sourcing (Joris Kuipers) — InfoQ — https://www.infoq.com/news/2019/09/cqrs-event-sourcing-production/
8. An Empirical Characterization of Event Sourced Systems and Their Schema Evolution (Overeem et al., 2021) — https://arxiv.org/abs/2104.01146
9. An empirical characterization of event sourced systems and their schema evolution — Journal of Systems and Software — https://www.sciencedirect.com/science/article/pii/S0164121221000674
10. Don't Let the Internet Dupe You, Event Sourcing is Hard — Chris Kiehl — https://chriskiehl.com/article/event-sourcing-is-hard
11. Things I wish I knew when I started with Event Sourcing — part 2, consistency — SoftwareMill — https://softwaremill.com/things-i-wish-i-knew-when-i-started-with-event-sourcing-part-2-consistency/
12. Mistakes and Recoveries When Building an Event Sourcing System (Nat Pryce) — InfoQ — https://www.infoq.com/news/2019/07/mistakes-recovery-event-sourcing/
