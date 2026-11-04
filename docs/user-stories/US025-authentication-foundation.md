# US025 — Authentication Foundation

## Status

Implemented in the `authentication_service` bounded context. The service
provides local credentials, Argon2id verification, temporary lockout,
authenticated sessions, audit events, tenant isolation, Redis cache and
EventBridge adapters.

The PostgreSQL migration is present but requires a reachable PostgreSQL
instance for deployment validation.

## Requirement coverage

| Requirement | Implementation |
|---|---|
| RF001–RF008 | `Credential`, `AuthenticationSession` and all authentication value objects under [`src/authentication_service/domain`](../../src/authentication_service/domain) |
| RF009–RF014 | `Credential.create`, `change_password`, `PasswordHash` and `PasswordPolicy` |
| RF015–RF017 | Consecutive failure counter, temporary lock and automatic unlock in [`credential.py`](../../src/authentication_service/domain/aggregates/credential.py) |
| RF018–RF021 | Session creation, validation, termination, repository and REST query |
| RF022–RF024 | `AuthenticationAuditSink`, success/failure/termination/password events and generic public errors |
| RF025–RF028 | Explicit `TenantValidator`, `IdentityDirectory`, EventBridge and shared cache ports/adapters |
| RF029–RF033 | Versioned domain events in [`authentication_events.py`](../../src/authentication_service/domain/events/authentication_events.py) |
| RF034 | [`EventBridgeAuthenticationPublisher`](../../src/authentication_service/infrastructure/events/eventbridge_publisher.py) |
| RF035–RF036 | `SessionCache` adapter and cache-first session lookup with invalidation on logout |
| RF037 | `AuthenticationLogger` port and structured-event emission |
| RF038–RF039 | FastAPI routes and Pydantic OpenAPI schemas in [`router.py`](../../src/authentication_service/presentation/api/router.py) |
| RF040 | This document and service README |

## Security controls

- Passwords are never persisted or published in clear text.
- Only Argon2id hashes are accepted by `PasswordHash`.
- Unknown email and invalid password use the same public error.
- Tenant identity is taken from a trusted request context; `X-Tenant-Id`
  cannot establish a tenant by itself.
- Every repository lookup includes `tenant_id`.
- Session identifiers are UUIDv7 values with finite expiry.
- Event payloads are explicitly allowlisted and contain no password material.
- Correlation and trace identifiers are carried by the shared event envelope.

## REST surface

- `POST /authentication/credentials`
- `POST /authentication/login`
- `GET /authentication/sessions/{session_id}`
- `POST /authentication/sessions/{session_id}/logout`
- `POST /authentication/credentials/{credential_id}/password`

The API intentionally rejects requests without an upstream trusted tenant
context with HTTP 403. A gateway or tenant foundation middleware must populate
`request.state.tenant_context` after validating the caller.

## Validation

- `pytest -q`: 193 passed.
- `pytest -q tests/unit/authentication_service/test_authentication_foundation.py`: 4 passed.
- `ruff check src/authentication_service src/identity_service/main.py tests/unit/authentication_service`: passed.
- `mypy src/authentication_service src/identity_service/main.py tests/unit/authentication_service --strict`: passed.
- `alembic check`: not executed successfully because PostgreSQL is unavailable in
  the local environment.
