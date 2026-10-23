"""Resolve and validate configured KMS keys."""

from __future__ import annotations

import re

from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-untyped]

from shared.aws.exceptions.aws_exception import AwsException
from shared.kms.contracts.kms_provider_contract import KmsProviderContract
from shared.kms.exceptions.kms_configuration_exception import KmsConfigurationException
from shared.kms.exceptions.kms_validation_exception import KmsValidationException
from shared.kms.metadata.key_usage_metadata import KeyUsageMetadata
from shared.kms.models.key_identifier import KeyPurpose
from shared.kms.models.kms_key_metadata import KmsKeyMetadata
from shared.kms.settings.kms_settings import KmsSettings


class KmsKeyResolver:
    """Resolve an alias or key ID and enforce AWS key usage and state."""

    def __init__(self, provider: KmsProviderContract, settings: KmsSettings) -> None:
        self._provider = provider
        self._settings = settings

    def resolve(self, tenant_id: str | None, purpose: KeyPurpose) -> KmsKeyMetadata:
        if tenant_id is not None and not tenant_id.strip():
            raise KmsValidationException("Tenant ID cannot be empty.")
        try:
            key_identifier = (
                self._settings.key_identifier_for_signing()
                if purpose is KeyPurpose.SIGNING
                else self._settings.key_identifier
            )
            response = self._provider.describe_key(key_id=key_identifier)
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code")
            if error_code == "NotFoundException":
                raise KmsValidationException("The configured KMS key does not exist.") from exc
            raise KmsConfigurationException(
                "Unable to resolve the configured KMS key through the AWS foundation."
            ) from exc
        except (AwsException, BotoCoreError) as exc:
            raise KmsConfigurationException(
                "Unable to resolve the configured KMS key through the AWS foundation."
            ) from exc
        raw_metadata = response.get("KeyMetadata")
        if not isinstance(raw_metadata, dict):
            raise KmsValidationException("AWS KMS returned no key metadata.")

        key_id = raw_metadata.get("KeyId")
        arn = raw_metadata.get("Arn")
        usage = raw_metadata.get("KeyUsage")
        state = raw_metadata.get("KeyState")
        if not isinstance(key_id, str) or not key_id:
            raise KmsValidationException("AWS KMS returned incomplete key metadata.")
        if not isinstance(arn, str) or not arn:
            raise KmsValidationException("AWS KMS returned incomplete key metadata.")
        if not isinstance(usage, str) or not usage:
            raise KmsValidationException("AWS KMS returned incomplete key metadata.")
        if not isinstance(state, str) or not state:
            raise KmsValidationException("AWS KMS returned incomplete key metadata.")
        expected_usage = KeyUsageMetadata.for_purpose(purpose)
        if usage != expected_usage.aws_key_usage:
            raise KmsValidationException(
                f"KMS key usage '{usage}' is not valid for "
                f"purpose '{expected_usage.purpose.value}'."
            )
        if state != "Enabled":
            raise KmsValidationException(f"KMS key is not enabled (state: '{state}').")

        arn_parts = arn.split(":")
        if (
            len(arn_parts) != 6
            or arn_parts[0] != "arn"
            or arn_parts[2] != "kms"
            or not arn_parts[3]
            or not re.fullmatch(r"\d{12}", arn_parts[4])
            or not arn_parts[5].startswith("key/")
        ):
            raise KmsValidationException("AWS KMS returned an invalid key ARN.")
        region = arn_parts[3]
        account_id = arn_parts[4]
        if region != self._settings.aws_region:
            raise KmsValidationException("The resolved KMS key belongs to a different region.")
        if self._settings.account_id and account_id != self._settings.account_id:
            raise KmsValidationException("The resolved KMS key belongs to a different account.")
        return KmsKeyMetadata(
            key_id=key_id,
            arn=arn,
            key_usage=usage,
            key_state=state,
            region=region,
            account_id=account_id,
            key_alias=(
                self._settings.signing_key_alias
                if purpose is KeyPurpose.SIGNING
                else self._settings.kms_key_alias
            ),
        )
