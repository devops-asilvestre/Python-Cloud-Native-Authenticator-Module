# Secrets Management Foundation

This module provides a secure, reusable foundation for reading secrets from AWS Secrets Manager without exposing raw values in logs or application code.

## Responsibilities

- Accept AWS Secrets Manager inputs only through the shared AWS foundation.
- Validate names, versions, and payloads before use.
- Cache resolved values in memory with safe expiration.
- Mask sensitive values in logs and exceptions.
- Integrate observability and auditing for read-only secret operations.

## Dependencies

- `shared.aws`
- `shared.observability`
- `shared.security`

## Read-only contract

This foundation never creates, updates, or deletes secrets. It only supports read-only operations (`GetSecretValue`, `DescribeSecret`, `ListSecrets`).
