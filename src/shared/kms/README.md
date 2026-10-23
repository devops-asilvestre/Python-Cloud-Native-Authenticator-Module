# Shared KMS Foundation

The KMS foundation is the only AWS KMS adapter intended for use by bounded
contexts. Application code depends on the contracts and services; AWS client
creation is delegated to `shared.aws`.

Configure `AUTHENTICATOR_KMS_AWS_REGION`, `AUTHENTICATOR_ENVIRONMENT`, and at
least one of `AUTHENTICATOR_KMS_KEY_ID` or `AUTHENTICATOR_KMS_KEY_ALIAS`. Tenant
operations use the server-provided `RequestContext.tenant_id` as authenticated
KMS encryption context. Callers cannot override that tenant value.

Configure a separate asymmetric signing key with
`AUTHENTICATOR_KMS_SIGNING_KEY_ID` or
`AUTHENTICATOR_KMS_SIGNING_KEY_ALIAS`; AWS KMS keys cannot be configured for
both `ENCRYPT_DECRYPT` and `SIGN_VERIFY` usage. KMS settings can also be loaded
from a JSON secret through `KmsSettings.from_secret_resolver`.

Allowed AWS operations are `DescribeKey`, `Encrypt`, `Decrypt`,
`GenerateDataKey`, `Sign`, and `Verify`. Key creation, deletion, policy, state,
and alias mutations are deliberately not exposed.

KMS encrypt supports small payloads only (AWS KMS direct-encrypt size limits
apply). Use `DataKeyService` for envelope encryption. Treat
`GeneratedDataKey.plaintext_key` as short-lived in-memory material and discard
it after use; never persist or log it. Signing uses the valid AWS KMS algorithm
`RSASSA_PSS_SHA_256` rather than a non-specific `SHA256` label.
