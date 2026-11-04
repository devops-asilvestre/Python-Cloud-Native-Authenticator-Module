"""Validated runtime settings for AWS KMS."""

from __future__ import annotations

import os
import re
from typing import Any

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.aws.settings.aws_settings import AwsSettings
from shared.kms.exceptions.kms_configuration_exception import KmsConfigurationException
from shared.secrets.resolver.secret_resolver import SecretResolver


class KmsSettings(BaseSettings):
    """KMS settings; key selection must be configured by key ID or alias."""

    model_config = SettingsConfigDict(
        env_prefix="AUTHENTICATOR_KMS_",
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )

    aws_region: str = Field(default_factory=lambda: AwsSettings().region)
    account_id: str | None = None
    kms_key_id: str | None = Field(
        default=None,
        validation_alias="AUTHENTICATOR_KMS_KEY_ID",
    )
    kms_key_alias: str | None = Field(
        default=None,
        validation_alias="AUTHENTICATOR_KMS_KEY_ALIAS",
    )
    kms_signing_key_id: str | None = Field(
        default=None,
        validation_alias="AUTHENTICATOR_KMS_SIGNING_KEY_ID",
    )
    kms_signing_key_alias: str | None = Field(
        default=None,
        validation_alias="AUTHENTICATOR_KMS_SIGNING_KEY_ALIAS",
    )
    environment: str = Field(
        default_factory=lambda: os.getenv("AUTHENTICATOR_ENVIRONMENT", ""),
        validation_alias="AUTHENTICATOR_ENVIRONMENT",
    )
    endpoint_url: str | None = None

    @model_validator(mode="after")
    def validate_settings(self) -> KmsSettings:
        if not self.aws_region or not re.fullmatch(
            r"[a-z]{2,}(?:-[a-z0-9]+)+-[0-9]+",
            self.aws_region,
        ):
            raise KmsConfigurationException("A valid AWS region is required for KMS.")
        if not self.kms_key_id and not self.kms_key_alias:
            raise KmsConfigurationException("Configure a KMS key ID or alias.")
        if self.kms_key_id is not None and not self.kms_key_id.strip():
            raise KmsConfigurationException("The KMS key ID cannot be empty.")
        if self.kms_key_alias is not None and not self.kms_key_alias.strip():
            raise KmsConfigurationException("The KMS key alias cannot be empty.")
        if self.kms_signing_key_id is not None and not self.kms_signing_key_id.strip():
            raise KmsConfigurationException("The KMS signing key ID cannot be empty.")
        if self.kms_signing_key_alias is not None and not self.kms_signing_key_alias.strip():
            raise KmsConfigurationException("The KMS signing key alias cannot be empty.")
        if self.account_id is not None and not re.fullmatch(r"\d{12}", self.account_id):
            raise KmsConfigurationException("The AWS account ID must contain 12 digits.")
        if not self.environment.strip():
            raise KmsConfigurationException("The application environment cannot be empty.")
        return self

    @property
    def key_identifier(self) -> str:
        """Return the configured KMS identifier, preferring an explicit key ID."""

        identifier = self.kms_key_id or self.kms_key_alias
        if identifier is None:
            raise KmsConfigurationException("Configure a KMS key ID or alias.")
        return identifier

    def key_identifier_for_signing(self) -> str:
        """Return the signing key, requiring a distinct asymmetric key configuration."""

        identifier = self.kms_signing_key_id or self.kms_signing_key_alias
        if identifier is None:
            raise KmsConfigurationException(
                "Configure a KMS signing key ID or alias for signing operations."
            )
        return identifier

    @property
    def signing_key_alias(self) -> str | None:
        """Return the configured alias for the signing key, if one is used."""

        return self.kms_signing_key_alias

    @classmethod
    def from_secret_resolver(
        cls,
        resolver: SecretResolver,
        *,
        secret_name: str,
    ) -> KmsSettings:
        """Load KMS settings from a JSON secret through the shared secrets foundation."""

        payload: Any = resolver.resolve_json(secret_name)
        if not isinstance(payload, dict):
            raise KmsConfigurationException("The KMS configuration secret must be a JSON object.")
        allowed_fields = {
            "aws_region",
            "account_id",
            "kms_key_id",
            "kms_key_alias",
            "kms_signing_key_id",
            "kms_signing_key_alias",
            "environment",
            "endpoint_url",
        }
        if set(payload) - allowed_fields:
            raise KmsConfigurationException(
                "The KMS configuration secret contains unsupported settings."
            )
        for name, value in payload.items():
            if value is not None and not isinstance(value, str):
                raise KmsConfigurationException(
                    f"KMS configuration value '{name}' must be a string."
                )
        return cls(**payload)
