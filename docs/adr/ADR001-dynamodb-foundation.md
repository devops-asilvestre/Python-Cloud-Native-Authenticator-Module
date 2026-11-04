# ADR001: Shared DynamoDB Foundation

- Status: Accepted
- Date: 2026-10-23

## Context

Multiple bounded contexts require DynamoDB persistence with consistent AWS
credential handling, tenant partitioning, serialization, TTL, version metadata
and structured operation logging.

## Decision

Use boto3 behind shared client/resource/table factories routed through the
AWS foundation. Keep the shared persistence package free of business tables and
domain models. Use tenant-prefixed partition keys (`TENANT#{tenant_id}`) and
entity-prefixed sort keys (`ENTITY#{entity_id}`). Keep endpoint configuration
optional for local DynamoDB, and never configure credentials in DynamoDB
settings.

## Consequences

- Bounded contexts implement their own repositories against shared protocols.
- Infrastructure remains responsible for table schemas, TTL activation and
  capacity/index configuration.
- The shared package centralizes structured operation outcomes but does not
  create OpenTelemetry spans.
- Tenant isolation still depends on server-validated tenant context at every
  repository boundary.
