"""Resolve the current AWS identity from STS."""

from __future__ import annotations

import boto3

from shared.aws.context.aws_context import AwsContext
from shared.aws.exceptions.aws_authentication_exception import AwsAuthenticationException
from shared.aws.exceptions.aws_configuration_exception import AwsConfigurationException


class AwsIdentityResolver:
    """Resolve identity metadata from the current AWS session."""

    def __init__(self, session: boto3.session.Session | None = None) -> None:
        self._session = session or boto3.Session()

    def resolve(self) -> AwsContext:
        credentials = self._session.get_credentials()
        if credentials is None:
            raise AwsAuthenticationException(
                "Unable to resolve AWS identity because no credentials are available."
            )

        try:
            sts_client = self._session.client("sts")
            response = sts_client.get_caller_identity()
        except Exception as exc:  # pragma: no cover - depends on AWS runtime availability.
            raise AwsConfigurationException(
                "Unable to resolve the active AWS identity using STS."
            ) from exc

        account_id = response.get("Account")
        arn = response.get("Arn")
        user_id = response.get("UserId")

        if account_id is None and arn is None:
            raise AwsConfigurationException("The AWS identity response was incomplete.")

        return AwsContext(
            account_id=str(account_id) if account_id is not None else None,
            arn=str(arn) if arn is not None else None,
            user_id=str(user_id) if user_id is not None else None,
            profile=self._session.profile_name,
            region=self._session.region_name,
        )
