"""KMS encryption application service."""

from __future__ import annotations

from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-untyped]

from shared.aws.exceptions.aws_exception import AwsException
from shared.kms.context.kms_context import KmsContext
from shared.kms.contracts.kms_provider_contract import KmsProviderContract
from shared.kms.exceptions.kms_configuration_exception import KmsConfigurationException
from shared.kms.exceptions.kms_encryption_exception import KmsEncryptionException
from shared.kms.exceptions.kms_validation_exception import KmsValidationException
from shared.kms.metadata.kms_audit_metadata import KmsAuditMetadata
from shared.kms.models.encrypted_payload import EncryptedPayload
from shared.kms.models.key_identifier import KeyPurpose
from shared.kms.resolver.kms_key_resolver import KmsKeyResolver
from shared.observability.context.request_context import RequestContext
from shared.observability.logging.structured_logger import StructuredLogger


class EncryptionService:
    """Encrypt non-empty bytes and log metadata only."""

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
            "shared-kms-encryption",
            request_context=self._request_context,
        )

    def encrypt(
        self,
        plaintext: bytes,
        *,
        context: dict[str, str] | None = None,
    ) -> EncryptedPayload:
        if not isinstance(plaintext, bytes) or not plaintext:
            raise KmsEncryptionException("Plaintext must be non-empty bytes.")
        try:
            encryption_context = self._kms_context.encryption_context(context)
            key = self._resolver.resolve(self._request_context.tenant_id, KeyPurpose.ENCRYPTION)
        except (KmsConfigurationException, KmsValidationException) as exc:
            raise KmsEncryptionException(
                "KMS encryption configuration or context is invalid."
            ) from exc
        try:
            response = self._provider.encrypt(
                key_id=key.key_id,
                plaintext=plaintext,
                encryption_context=encryption_context,
            )
            ciphertext = response.get("CiphertextBlob")
            if not isinstance(ciphertext, bytes) or not ciphertext:
                raise KmsEncryptionException("AWS KMS returned no ciphertext.")
        except (AwsException, ClientError, BotoCoreError) as exc:
            raise KmsEncryptionException("AWS KMS encryption failed.") from exc

        self._logger.info(
            "kms_encrypt_succeeded",
            **KmsAuditMetadata.from_request(
                operation="encrypt",
                key_id=key.key_id,
                key_alias=key.key_alias,
                account_id=key.account_id,
                region=key.region,
                request_context=self._request_context,
            ).to_log_fields(),
        )
        return EncryptedPayload(
            ciphertext=ciphertext,
            key_id=key.key_id,
            encryption_context=encryption_context,
        )
