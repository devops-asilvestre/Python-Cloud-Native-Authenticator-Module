"""Factory helpers for AWS foundation tests."""

from __future__ import annotations

from shared.aws.factories.aws_client_factory import AwsClientFactory
from shared.aws.factories.aws_session_factory import AwsSessionFactory
from shared.aws.settings.aws_settings import AwsSettings


def build_aws_client_factory(*, region: str = "us-east-1") -> AwsClientFactory:
    settings = AwsSettings(region=region)
    session_factory = AwsSessionFactory(settings)
    return AwsClientFactory(session_factory, settings=settings)
