"""Resolve the active AWS region with a clear precedence order."""

from __future__ import annotations

import os

import boto3

from shared.aws.exceptions.aws_configuration_exception import AwsConfigurationException


class AwsRegionResolver:
    """Resolve the effective AWS region from settings, session, or environment."""

    def __init__(self, session: boto3.session.Session | None = None, *, default_region: str = "us-east-1") -> None:
        self._session = session or boto3.Session()
        self._default_region = default_region

    def resolve(self, *, explicit_region: str | None = None) -> str:
        candidates = [
            explicit_region,
            os.getenv("AWS_DEFAULT_REGION"),
            os.getenv("AWS_REGION"),
            getattr(self._session, "region_name", None),
            self._default_region,
        ]
        for candidate in candidates:
            if candidate and str(candidate).strip():
                return str(candidate).strip()
        raise AwsConfigurationException("No AWS region could be resolved from settings or environment.")
