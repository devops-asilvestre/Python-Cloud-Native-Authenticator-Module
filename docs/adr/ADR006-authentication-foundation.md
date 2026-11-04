# ADR006 — Authentication Foundation Runtime Composition

## Status

Accepted — implementation in progress until external integration evidence is
attached.

## Context

Authentication must not use process-local state in a deployed environment.
Credentials and sessions require PostgreSQL durability, Redis-backed session
lookup/rate limiting, and versioned EventBridge publication. Tenant and user
validity belong to the Tenant Foundation and Identity Directory bounded
contexts.

## Decision

- The authentication domain depends only on repository and integration ports.
- The runtime composes SQLAlchemy repositories, Redis cache/rate limiter,
  persistent audit storage, OpenTelemetry metrics, structured logging and an
  EventBridge publisher.
- The API accepts a tenant header only as an input to a resolver; the resolver
  validates tenant existence and active status through the Tenant Foundation.
- User creation validates active user and tenant ownership through the
  Identity Directory contract.
- Authentication events use the shared `EventEnvelope` and semantic version
  `1.0.0`; payloads are explicitly allowlisted.
- Missing external configuration is a deployment error, never a fallback to
  in-memory storage or a null publisher.

## Consequences

Local API execution requires PostgreSQL, Redis and EventBridge configuration.
In-memory adapters remain available only for isolated unit tests.
