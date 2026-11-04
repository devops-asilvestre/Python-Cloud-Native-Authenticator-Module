# ADR004: Tenant bounded context

- Status: Accepted
- Context: US023 - Tenant Foundation
- Date: 2026-11-03
- Validation: concluída em 2026-11-03; cobertura do contexto Tenant 97%,
  repositório SQLAlchemy 100%, Ruff aprovado, Mypy strict aprovado, Pytest
  aprovado e `git diff --check` aprovado.

## Decision

The Tenant aggregate is the first business bounded context. Its domain layer
contains the lifecycle rules and value objects; application handlers depend on
repository, cache, and event publisher ports. PostgreSQL, Redis, EventBridge,
and observability are accessed only through the existing shared foundations and
infrastructure adapters.

Tenant identifiers use UUIDv7. Codes and slugs are unique at both the
application and PostgreSQL constraint levels. Domain events are converted to
versioned US018 envelopes before the US022 publisher is called. The HTTP
composition root uses the same ports and can replace the default in-memory
adapters with configured production adapters without changing domain code.

## Consequences

The aggregate owns lifecycle transitions and emits six event types. Tenant
management does not implement users, groups, permissions, authentication, or
authorization. An outbox/transactional event relay remains a future
operational hardening item.
