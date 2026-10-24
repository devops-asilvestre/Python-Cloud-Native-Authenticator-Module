# ADR002: Shared AWS KMS Foundation

## Status

Accepted

## Context

Bounded contexts must not access AWS KMS directly. Cryptographic operations
need consistent tenant binding, key-usage checks, audit metadata, and safe
structured logging while reusing the existing AWS credentials and
observability foundations.

## Decision

- Provide KMS contracts, application services, and a single AWS provider under
  `src/shared/kms`.
- Create clients through `shared.aws.AwsClientFactory`.
- Expose only key description, encryption, decryption, data-key generation,
  signing, and verification operations. Key lifecycle and policy mutations are
  out of scope.
- Resolve a configured key by ID or alias and validate its enabled state,
  usage, and configured account.
- Bind tenant operations to the server-provided tenant ID via AWS KMS
  encryption context; reject conflicting caller context.
- Use AWS's `RSASSA_PSS_SHA_256` signing algorithm. Never include plaintext,
  ciphertext, signatures, or plaintext data keys in logs.

## Consequences

KMS direct encryption remains limited to payloads supported by AWS. Larger data
must use envelope encryption, and callers must immediately discard plaintext
data keys after their in-memory use.
