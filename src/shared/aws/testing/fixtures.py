"""Fixtures for AWS foundation tests."""

from __future__ import annotations

from shared.aws.settings.aws_settings import AwsSettings


def aws_settings_fixture(*, region: str = "us-east-1", profile: str | None = None) -> AwsSettings:
    return AwsSettings(region=region, profile=profile)
