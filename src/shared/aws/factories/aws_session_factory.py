"""Create authenticated boto3 sessions with AWS credential chain support."""

from __future__ import annotations

from typing import Any

import boto3
from botocore.exceptions import ClientError

from shared.aws.exceptions.aws_authentication_exception import AwsAuthenticationException
from shared.aws.exceptions.aws_configuration_exception import AwsConfigurationException
from shared.aws.observability.aws_observability import AwsObservability
from shared.aws.settings.aws_settings import AwsSettings


class AwsSessionFactory:
    """Build boto3 sessions for local development and production workloads."""

    def __init__(
        self,
        settings: AwsSettings | None = None,
        *,
        observability: AwsObservability | None = None,
    ) -> None:
        self.settings = settings or AwsSettings()
        self.observability = observability or AwsObservability(service_name="aws-session-factory")

    def create(
        self,
        *,
        region_name: str | None = None,
        profile_name: str | None = None,
        assume_role_arn: str | None = None,
        session_name: str | None = None,
    ) -> boto3.session.Session:
        session_kwargs: dict[str, str] = {}
        effective_region = region_name or self.settings.region
        if effective_region:
            session_kwargs["region_name"] = effective_region
        effective_profile = profile_name or self.settings.profile
        if effective_profile:
            session_kwargs["profile_name"] = effective_profile

        session = boto3.Session(**session_kwargs)
        credentials = session.get_credentials()
        if credentials is None:
            raise AwsAuthenticationException(
                "No AWS credentials were found in the configured credential chain."
            )

        self.observability.log_session_ready(
            region_name=effective_region,
            profile_name=effective_profile,
        )

        if assume_role_arn or (self.settings.assume_role and self.settings.role_arn):
            role_arn = assume_role_arn or self.settings.role_arn
            if role_arn is None:
                raise AwsConfigurationException("Assume role was requested but no role ARN was configured.")
            try:
                sts_client = session.client("sts", region_name=effective_region)
                response = sts_client.assume_role(
                    RoleArn=role_arn,
                    RoleSessionName=session_name or self.settings.session_name,
                )
            except ClientError as exc:
                self.observability.error(
                    "aws_role_assumption_failed",
                    role_arn=role_arn,
                    region_name=effective_region,
                )
                raise AwsAuthenticationException(
                    "Unable to assume the configured AWS role."
                ) from exc

            creds = response["Credentials"]
            return boto3.Session(
                aws_access_key_id=creds["AccessKeyId"],
                aws_secret_access_key=creds["SecretAccessKey"],
                aws_session_token=creds["SessionToken"],
                region_name=effective_region,
            )

        return session

    def __call__(self, **kwargs: Any) -> boto3.session.Session:
        return self.create(**kwargs)
