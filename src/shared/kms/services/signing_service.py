"""KMS digital signing service."""

from __future__ import annotations

from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-untyped]

from shared.aws.exceptions.aws_exception import AwsException
from shared.kms.contracts.kms_provider_contract import KmsProviderContract
from shared.kms.exceptions.kms_configuration_exception import KmsConfigurationException
from shared.kms.exceptions.kms_signing_exception import KmsSigningException
from shared.kms.exceptions.kms_validation_exception import KmsValidationException
from shared.kms.metadata.kms_audit_metadata import KmsAuditMetadata
from shared.kms.models.digital_signature import DigitalSignature
from shared.kms.models.key_identifier import KeyPurpose
from shared.kms.resolver.kms_key_resolver import KmsKeyResolver
from shared.observability.context.request_context import RequestContext
from shared.observability.logging.structured_logger import StructuredLogger


class SigningService:
    """Sign non-empty messages using AWS KMS asymmetric signing."""

    SIGNING_ALGORITHM = "RSASSA_PSS_SHA_256"

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
        self._logger = logger or StructuredLogger(
            "shared-kms-signing",
            request_context=self._request_context,
        )

    def sign(self, payload: bytes) -> DigitalSignature:
        if not isinstance(payload, bytes) or not payload:
            raise KmsSigningException("Signing payload must be non-empty bytes.")
        try:
            key = self._resolver.resolve(self._request_context.tenant_id, KeyPurpose.SIGNING)
        except (KmsConfigurationException, KmsValidationException) as exc:
            raise KmsSigningException("KMS signing key configuration is invalid.") from exc
        try:
            response = self._provider.sign(
                key_id=key.key_id,
                message=payload,
                signing_algorithm=self.SIGNING_ALGORITHM,
            )
            signature = response.get("Signature")
            if not isinstance(signature, bytes) or not signature:
                raise KmsSigningException("AWS KMS returned no signature.")
        except (AwsException, ClientError, BotoCoreError) as exc:
            raise KmsSigningException("AWS KMS signing failed.") from exc

        self._logger.info(
            "kms_sign_succeeded",
            **KmsAuditMetadata.from_request(
                operation="sign",
                key_id=key.key_id,
                key_alias=key.key_alias,
                account_id=key.account_id,
                region=key.region,
                request_context=self._request_context,
            ).to_log_fields(),
        )
        return DigitalSignature(signature, key.key_id, self.SIGNING_ALGORITHM)
