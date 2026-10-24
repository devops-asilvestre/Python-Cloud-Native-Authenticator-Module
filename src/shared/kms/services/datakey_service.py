"""KMS envelope-encryption data key service."""

from __future__ import annotations

from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-untyped]

from shared.aws.exceptions.aws_exception import AwsException
from shared.kms.context.kms_context import KmsContext
from shared.kms.contracts.kms_provider_contract import KmsProviderContract
from shared.kms.exceptions.kms_configuration_exception import KmsConfigurationException
from shared.kms.exceptions.kms_encryption_exception import KmsEncryptionException
from shared.kms.exceptions.kms_validation_exception import KmsValidationException
from shared.kms.metadata.kms_audit_metadata import KmsAuditMetadata
from shared.kms.models.generated_datakey import GeneratedDataKey
from shared.kms.models.key_identifier import KeyPurpose
from shared.kms.resolver.kms_key_resolver import KmsKeyResolver
from shared.observability.context.request_context import RequestContext
from shared.observability.logging.structured_logger import StructuredLogger


class DataKeyService:
    """Generate envelope-encryption keys without persisting plaintext material."""

    def __init__(
        self,
        provider: KmsProviderContract,
        resolver: KmsKeyResolver,
        *,
        request_context: RequestContext | None = None,
        logger: StructuredLogger | None = None,
    ) -> None:
        self._provider = provider
        self._resolver = resolver
        self._request_context = request_context or RequestContext()
        self._kms_context = KmsContext.from_request_context(self._request_context)
        self._logger = logger or StructuredLogger(
            "shared-kms-datakey",
            request_context=self._request_context,
        )

    def generate(self, *, context: dict[str, str] | None = None) -> GeneratedDataKey:
        try:
            encryption_context = self._kms_context.encryption_context(context)
            key = self._resolver.resolve(self._request_context.tenant_id, KeyPurpose.DATA_KEY)
        except (KmsConfigurationException, KmsValidationException) as exc:
            raise KmsEncryptionException(
                "KMS data key configuration or context is invalid."
            ) from exc
        try:
            response = self._provider.generate_data_key(
                key_id=key.key_id,
                key_spec="AES_256",
                encryption_context=encryption_context,
            )
            plaintext = response.get("Plaintext")
            ciphertext = response.get("CiphertextBlob")
            if (
                not isinstance(plaintext, bytes)
                or not plaintext
                or not isinstance(ciphertext, bytes)
                or not ciphertext
            ):
                raise KmsEncryptionException("AWS KMS returned an incomplete data key.")
        except (AwsException, ClientError, BotoCoreError) as exc:
            raise KmsEncryptionException("AWS KMS data key generation failed.") from exc

        self._logger.info(
            "kms_datakey_generated",
            **KmsAuditMetadata.from_request(
                operation="generate_data_key",
                key_id=key.key_id,
                key_alias=key.key_alias,
                account_id=key.account_id,
                region=key.region,
                request_context=self._request_context,
            ).to_log_fields(),
        )
        return GeneratedDataKey(plaintext, ciphertext, key.key_id)
