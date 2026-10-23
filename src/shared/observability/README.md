# Shared Observability

This package defines the shared observability contract used across services. It
contains platform-level abstractions for correlation, request context, log
entry modeling, metrics and tracing without introducing any concrete runtime
component such as OpenTelemetry, CloudWatch or X-Ray.

## Scope

- Correlation identifiers
- Request and trace context propagation
- Structured JSON logging
- Metric contracts for counters, gauges and histograms
- Trace and span contracts
- Provider abstractions for implementation injection
- Security-first redaction of sensitive fields

## Design principles

- No direct dependency on vendor SDKs
- Provider-oriented abstraction layer
- No circular dependencies between bounded contexts
- Same contracts reused across all services
