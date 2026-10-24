"""KMS signature verification service."""

from __future__ import annotations

from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-untyped]

from shared.aws.exceptions.aws_exception import AwsException
from shared.kms.contracts.kms_provider_contract import KmsProviderContract
from shared.kms.exceptions.kms_configuration_exception import KmsConfigurationException
from shared.kms.exceptions.kms_signing_exception import KmsSigningException
from shared.kms.exceptions.kms_validation_exception import KmsValidationException
from shared.kms.metadata.kms_audit_metadata import KmsAuditMetadata
from shared.kms.models.key_identifier import KeyPurpose
from shared.kms.resolver.kms_key_resolver import KmsKeyResolver
from shared.observability.context.request_context import RequestContext
from shared.observability.logging.structured_logger import StructuredLogger


class VerificationService:
    """Verify signatures, returning False for invalid signatures only."""

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
            "shared-kms-verification",
            request_context=self._request_context,
        )

    def verify(self, payload: bytes, signature: bytes) -> bool:
        if not isinstance(payload, bytes) or not payload:
            raise KmsSigningException("Verification payload must be non-empty bytes.")
        if not isinstance(signature, bytes) or not signature:
            raise KmsSigningException("Signature must be non-empty bytes.")
        try:
            key = self._resolver.resolve(self._request_context.tenant_id, KeyPurpose.SIGNING)
        except (KmsConfigurationException, KmsValidationException) as exc:
            raise KmsSigningException("KMS verification key configuration is invalid.") from exc
        try:
            response = self._provider.verify(
                key_id=key.key_id,
                message=payload,
                signature=signature,
                signing_algorithm=self.SIGNING_ALGORITHM,
            )
            valid = response.get("SignatureValid")
            if not isinstance(valid, bool):
                raise KmsSigningException("AWS KMS returned no signature verification result.")
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code")
            if error_code in {"KMSInvalidSignatureException", "InvalidSignatureException"}:
                valid = False
            else:
                raise KmsSigningException(
                    "AWS KMS signature verification failed."
                ) from exc
        except (AwsException, BotoCoreError) as exc:
            raise KmsSigningException("AWS KMS signature verification failed.") from exc

        self._logger.info(
            "kms_verify_completed",
            valid=valid,
            **KmsAuditMetadata.from_request(
                operation="verify",
                key_id=key.key_id,
                key_alias=key.key_alias,
                account_id=key.account_id,
                region=key.region,
                request_context=self._request_context,
            ).to_log_fields(),
        )
        return valid
