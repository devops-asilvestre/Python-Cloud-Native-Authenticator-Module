"""Fixture builders for KMS foundation tests."""

from __future__ import annotations

from shared.kms.settings.kms_settings import KmsSettings
from shared.kms.testing.factories import build_kms_settings


def kms_settings_fixture(
    *,
    region: str = "us-east-1",
    key_alias: str = "alias/test-key",
    signing_key_alias: str = "alias/test-signing-key",
) -> KmsSettings:
    return build_kms_settings(
        region=region,
        key_alias=key_alias,
        signing_key_alias=signing_key_alias,
    )
