# Shared messaging foundation

`shared.messaging` provides the transport adapter and application-facing
contracts for asynchronous `EventEnvelope` delivery through AWS SQS.
Bounded contexts should depend on the publisher/consumer/handler contracts and
must not create SQS clients or configure queue URLs themselves.

## Configuration

Configure `AUTHENTICATOR_SQS_ACCOUNT_ID`, `AUTHENTICATOR_SQS_QUEUE_PREFIX`,
`AUTHENTICATOR_SQS_ENVIRONMENT`, and optionally `AUTHENTICATOR_SQS_AWS_REGION`,
`AUTHENTICATOR_SQS_ENDPOINT_URL`, `AUTHENTICATOR_SQS_DEFAULT_VISIBILITY_TIMEOUT`,
`AUTHENTICATOR_SQS_DEFAULT_WAIT_TIME`, and
`AUTHENTICATOR_SQS_DEFAULT_MAX_RECEIVE_COUNT`. Queue URLs are discovered using
`ListQueues` and checked against the configured AWS account and region.

The queues and DLQs must already exist. This package does not provision or
administratively modify AWS queues. Keep production IAM permissions limited to
the required SQS data operations and queue discovery.

## Delivery behavior

The publisher serializes schema-validated event envelopes as JSON UTF-8. The
consumer long-polls and validates each envelope but does not acknowledge it;
call `acknowledge` only after successful dispatch. Retry decisions are
calculated by `RetryPolicy`. `DeadLetterPolicy.forward` sends the original body
and audit metadata to the pre-provisioned DLQ before deleting the source.

`IdempotencyValidator` requires a durable implementation of the atomic
`IdempotencyStoreContract` claim/complete/release lifecycle. Claims must be
leased or otherwise recoverable after worker crashes. The foundation
intentionally supplies no in-memory production fallback because it cannot
provide cross-process correctness. `MessageDispatcher` claims before invoking a
handler, records completion only after success, and releases failed claims for
redelivery. `DynamoDbIdempotencyStore` provides this lifecycle through the
shared DynamoDB table adapter; its table must be provisioned with string
partition key `id` before use. Enable DynamoDB TTL on numeric attribute
`expires_at` to expire completed idempotency records after the configured
retention period.

Optional KMS body encryption uses the existing shared KMS provider/resolver.
Structured audit and operational logs contain identifiers, queue metadata,
latency, and outcomes only; message payloads and ciphertext are never logged.
The current direct KMS `Encrypt` integration is subject to the AWS KMS 4 KiB
plaintext limit; larger bodies fail explicitly and require a future envelope
encryption/data-key integration.

See [ADR003](../../../docs/adr/ADR003-sqs-messaging-foundation.md) for the
architectural decision and operational constraints.
