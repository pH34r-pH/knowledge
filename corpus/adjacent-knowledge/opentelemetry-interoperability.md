---
title: "OpenTelemetry: telemetry interoperability, not an observability backend"
pillar: adjacent-knowledge
method: deep-research
sources: 6
confidence: high
date: 2026-08-07
---

# OpenTelemetry: telemetry interoperability, not an observability backend

## What it is

OpenTelemetry (OTel) is a shared instrumentation, data-model, and transport ecosystem for telemetry. It helps generate, collect, and export traces, metrics, and logs; it is explicitly **not** an observability backend.[1][2] That distinction prevents a common mistake: adopting an SDK does not choose storage, queries, alerting, ownership, or SLOs.

Its value is interoperability. W3C Trace Context describes the vendor-boundary propagation problem directly: without common identifiers, traces crossing vendor boundaries cannot be propagated.[3] OTel semantic conventions define shared names, while its Collector documentation defines receiver, processor, and exporter pipeline components.[4][6]

## When to reach for it

Use OTel for polyglot services, vendor migration, cross-service request paths, or any estate where local telemetry dialects make correlation expensive. Start with an important request path and a question the team intends to answer—latency attribution, dependency failure, or error correlation.

Do not treat OTel adoption as observability maturity. Unbounded attributes, no sampling policy, missing service ownership, and dashboards without decisions can generate large telemetry bills without reducing diagnosis time.

## How it works

Instrumentation creates signal records and attaches resource identity. Context propagation passes trace identifiers across process boundaries so newly created spans join the same trace. Semantic conventions standardize resource and attribute vocabulary, reducing the need for each library to invent its own query dialect.[4]

SDKs and exporters send records over the OpenTelemetry Protocol (OTLP). A Collector can receive, process, sample, transform, route, and export these records.[5][6] This separates application instrumentation from backend selection: applications emit a portable protocol while the operational pipeline handles enrichment and destination-specific export.

The guarantee is limited. Common wire formats and names improve portability only when producers and consumers follow them. Metrics, logs, and traces still have different storage/query models, and a backend may preserve or interpret them differently.

## Trade-offs

Cardinality and privacy are first-class design constraints. High-cardinality labels make metrics costly; logs and spans can expose sensitive identifiers; tail sampling needs buffering and can delay decisions. Collector transformations can improve signal quality but introduce operational state and failure modes.

Semantic conventions also evolve. Pin conventions in instrumentation contracts and test dashboards/alerts when upgrading. Custom attributes are sometimes necessary, but each one is a local dialect that reduces portability.

## In practice

Instrument one critical path with stable service/resource attributes, W3C propagation, bounded-cardinality dimensions, and explicit error status. Define sampling from the decisions you need to make, then verify that an intentionally injected failure can be found end-to-end. Route through a Collector when multiple backends, policy enforcement, or central redaction is useful; otherwise keep the first pipeline small.

Treat the telemetry schema as an API. Name service resources consistently, document ownership of every custom attribute, and prevent request bodies, secrets, and unbounded identifiers from entering default instrumentation. A portable trace is only useful if responders can join it to a runbook, an owner, and a bounded-cost query. That makes instrumentation review a product and security concern, not merely a library upgrade.

Operationally, test three paths after each significant change: a normal request, an error crossing a service boundary, and a sampled/unsampled request. Confirm parentage survives propagation, resource identity is stable, and the chosen backend still represents the fields used by alerts and dashboards. These tests catch the common failure where an SDK emits data successfully but the pipeline quietly drops or rewrites the signal that operators need.

Plan telemetry changes like any compatibility migration. Keep an inventory of instrumented services and propagation libraries, roll changes through one path before a fleet-wide update, and retain a short overlap period when dashboards or policies must recognize old and new field names. Use budget alerts for cardinality, export failures, and dropped records. Those controls turn portability from a theoretical standard property into a service the platform team can operate.

## Further reading

1. OpenTelemetry — *What is OpenTelemetry?* — https://opentelemetry.io/docs/what-is-opentelemetry/
2. OpenTelemetry — *Signals* — https://opentelemetry.io/docs/concepts/signals/
3. W3C — *Trace Context* — https://www.w3.org/TR/trace-context/
4. OpenTelemetry — *Semantic conventions* — https://opentelemetry.io/docs/specs/semconv/
5. OpenTelemetry — *OTLP specification* — https://opentelemetry.io/docs/specs/otel/protocol/
6. OpenTelemetry — *Collector documentation* — https://opentelemetry.io/docs/collector/
