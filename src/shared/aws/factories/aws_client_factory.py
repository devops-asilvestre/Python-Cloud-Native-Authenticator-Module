"""Create AWS SDK clients from the shared session factory."""

from __future__ import annotations

from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

from shared.aws.exceptions.aws_authentication_exception import AwsAuthenticationException
from shared.aws.exceptions.aws_configuration_exception import AwsConfigurationException
from shared.aws.factories.aws_session_factory import AwsSessionFactory
from shared.aws.observability.aws_observability import AwsObservability
from shared.aws.settings.aws_settings import AwsSettings


class AwsClientFactory:
    """Centralized client creation for AWS services."""

    def __init__(
        self,
        session_factory: AwsSessionFactory | None = None,
        *,
        settings: AwsSettings | None = None,
        observability: AwsObservability | None = None,
    ) -> None:
        self.settings = settings or AwsSettings()
        self.observability = observability or AwsObservability(service_name="aws-client-factory")
        self._session_factory = session_factory or AwsSessionFactory(self.settings, observability=self.observability)

    def create_client(
        self,
        service_name: str,
        *,
        region_name: str | None = None,
        session: boto3.session.Session | None = None,
        config: Config | None = None,
    ) -> Any:
        if not service_name:
            raise AwsConfigurationException("The AWS service name cannot be empty.")

        credential_session = session or self._session_factory.create(
            region_name=region_name or self.settings.region,
            profile_name=self.settings.profile,
            assume_role_arn=self.settings.role_arn if self.settings.assume_role else None,
        )

        try:
            client = credential_session.client(
                service_name,
                region_name=region_name or credential_session.region_name or self.settings.region,
                config=config,
            )
            self.observability.log_client_created(
                service_name=service_name,
                region_name=region_name or credential_session.region_name or self.settings.region,
            )
            return client
        except NoCredentialsError as exc:
            self.observability.error(
                "aws_client_creation_failed",
                service_name=service_name,
                region_name=region_name or self.settings.region,
            )
            raise AwsAuthenticationException(
                "AWS credentials are not available for the current session."
            ) from exc
        except ClientError as exc:
            self.observability.error(
                "aws_client_creation_failed",
                service_name=service_name,
                region_name=region_name or self.settings.region,
            )
            raise AwsConfigurationException(
                f"Unable to create the AWS client for service '{service_name}'."
            ) from exc
