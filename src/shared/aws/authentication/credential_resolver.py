"""Resolve AWS credentials using the default credential chain."""

from __future__ import annotations

from typing import Any

import boto3  # type: ignore[import-untyped]

from shared.aws.exceptions.aws_authentication_exception import AwsAuthenticationException


class AwsCredentialResolver:
    """Resolve active AWS credentials from the environment or profile chain."""

    def __init__(self, session: boto3.session.Session | None = None) -> None:
        self._session = session or boto3.Session()

    def resolve(self) -> Any:
        credentials = self._session.get_credentials()
        if credentials is None:
            raise AwsAuthenticationException(
                "No AWS credentials were found in the configured credential chain."
            )
        return credentials

    @property
    def access_key_id(self) -> str | None:
        credentials = self.resolve()
        return getattr(credentials, "access_key", None)

    @property
    def secret_access_key(self) -> str | None:
        credentials = self.resolve()
        return getattr(credentials, "secret_key", None)

    @property
    def session_token(self) -> str | None:
        credentials = self.resolve()
        return getattr(credentials, "token", None)
