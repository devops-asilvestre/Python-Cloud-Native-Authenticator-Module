"""Fixture helpers for messaging foundation tests."""

from shared.messaging.settings.sqs_settings import SqsSettings
from shared.messaging.testing.factories import build_sqs_settings


def sqs_settings_fixture(**overrides: str | int | None) -> SqsSettings:
    """Return valid test settings with optional field overrides."""

    return build_sqs_settings(**overrides)
