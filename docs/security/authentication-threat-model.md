# Authentication Foundation Threat Model

## Assets

- Password verifiers and credential state.
- Authenticated sessions.
- Tenant and user identity relationships.
- Authentication audit records.

## Threats and controls

| Threat | Control |
|---|---|
| Credential stuffing | Argon2id, distributed Redis limits, lockout and generic errors |
| User enumeration | Same public error for unknown email and wrong password |
| Cross-tenant access | Tenant-scoped repository queries and active-tenant resolver |
| Password disclosure | No password in models, logs or event payloads |
| Session replay | UUIDv7 sessions, expiry, explicit termination and Redis invalidation |
| Event data leakage | Explicit event payload allowlist and shared envelope validation |
| Audit tampering | Durable PostgreSQL audit records and tenant/event indexes |
| Trace loss | Correlation and trace fields in the shared event contract |

## Residual risks

External IAM permissions, database encryption at rest, Redis TLS, secret
rotation and production load limits must be validated in the deployment
environment. They are not certified by unit tests.
