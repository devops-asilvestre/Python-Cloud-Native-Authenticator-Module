"""Factories for isolated KMS foundation tests."""

from __future__ import annotations

from shared.kms.settings.kms_settings import KmsSettings
from shared.kms.testing.fake_kms import FakeKmsProvider


def build_kms_settings(
    *,
    region: str = "us-east-1",
    key_alias: str = "alias/test-key",
    signing_key_alias: str = "alias/test-signing-key",
) -> KmsSettings:
    return KmsSettings(
        aws_region=region,
        kms_key_alias=key_alias,
        kms_signing_key_alias=signing_key_alias,
        environment="test",
    )


def build_fake_kms_provider(
    *,
    key_usage: str = "ENCRYPT_DECRYPT",
    error: Exception | None = None,
) -> FakeKmsProvider:
    return FakeKmsProvider(key_usage=key_usage, error=error)
