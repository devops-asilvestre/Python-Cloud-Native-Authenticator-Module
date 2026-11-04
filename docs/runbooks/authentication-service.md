# Authentication Service Runbook

## Required configuration

- `AUTHENTICATOR_DB_*` for PostgreSQL.
- `AUTHENTICATOR_REDIS_*` for Redis.
- `AUTHENTICATOR_EVENTBRIDGE_AWS_REGION`.
- `AUTHENTICATOR_EVENTBRIDGE_ACCOUNT_ID`.
- `AUTHENTICATOR_EVENTBRIDGE_BUS_NAME`.

## Startup validation

1. Verify PostgreSQL health and run `alembic upgrade head`.
2. Verify Redis with the configured health check.
3. Verify the EventBridge bus and IAM permission for `PutEvents`.
4. Verify the active tenant and user records.
5. Execute the authentication integration suite before traffic.

## Incident checks

- `authentication.failed` and `authentication.rate_limited` metrics.
- `authentication.duration_ms` latency histogram.
- `authentication_audit` records by tenant and event type.
- Redis session key and rate-limit TTL.
- EventBridge delivery failures and publisher logs.

Never inspect or log passwords, password hashes, session secrets or raw
authentication payloads.
