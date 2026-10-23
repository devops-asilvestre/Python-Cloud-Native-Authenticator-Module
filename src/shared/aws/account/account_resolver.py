"""Resolve the active AWS account identifier."""

from __future__ import annotations

import boto3  # type: ignore[import-untyped]

from shared.aws.authentication.identity_resolver import AwsIdentityResolver
from shared.aws.exceptions.aws_configuration_exception import AwsConfigurationException


class AwsAccountResolver:
    """Resolve the active AWS account id using STS."""

    def __init__(self, session: boto3.session.Session | None = None) -> None:
        self._session = session or boto3.Session()

    def resolve(self) -> str:
        identity = AwsIdentityResolver(self._session).resolve()
        if identity.account_id is None:
            raise AwsConfigurationException("The active AWS account could not be resolved.")
        return identity.account_id
