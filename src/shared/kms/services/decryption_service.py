"""KMS decryption application service."""

from __future__ import annotations

from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-untyped]

from shared.aws.exceptions.aws_exception import AwsException
from shared.kms.context.kms_context import KmsContext
from shared.kms.contracts.kms_provider_contract import KmsProviderContract
from shared.kms.exceptions.kms_configuration_exception import KmsConfigurationException
from shared.kms.exceptions.kms_decryption_exception import KmsDecryptionException
from shared.kms.exceptions.kms_validation_exception import KmsValidationException
from shared.kms.metadata.kms_audit_metadata import KmsAuditMetadata
from shared.kms.models.key_identifier import KeyPurpose
from shared.kms.resolver.kms_key_resolver import KmsKeyResolver
from shared.observability.context.request_context import RequestContext
from shared.observability.logging.structured_logger import StructuredLogger


class DecryptionService:
    """Decrypt non-empty ciphertext with tenant-bound context."""

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
            "shared-kms-decryption",
            request_context=self._request_context,
        )

    def decrypt(
        self,
        ciphertext: bytes,
        *,
        context: dict[str, str] | None = None,
    ) -> bytes:
        if not isinstance(ciphertext, bytes) or not ciphertext:
            raise KmsDecryptionException("Ciphertext must be non-empty bytes.")
        try:
            encryption_context = self._kms_context.encryption_context(context)
            key = self._resolver.resolve(self._request_context.tenant_id, KeyPurpose.ENCRYPTION)
        except (KmsConfigurationException, KmsValidationException) as exc:
            raise KmsDecryptionException(
                "KMS decryption configuration or context is invalid."
            ) from exc
        try:
            response = self._provider.decrypt(
                ciphertext=ciphertext,
                encryption_context=encryption_context,
            )
            plaintext = response.get("Plaintext")
            if not isinstance(plaintext, bytes):
                raise KmsDecryptionException("AWS KMS returned no plaintext.")
        except (AwsException, ClientError, BotoCoreError) as exc:
            raise KmsDecryptionException("AWS KMS decryption failed.") from exc

        self._logger.info(
            "kms_decrypt_succeeded",
            **KmsAuditMetadata.from_request(
                operation="decrypt",
                key_id=key.key_id,
                key_alias=key.key_alias,
                account_id=key.account_id,
                region=key.region,
                request_context=self._request_context,
            ).to_log_fields(),
        )
        return plaintext
