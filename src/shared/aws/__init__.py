"""Shared AWS foundation."""

from shared.aws.account.account_resolver import AwsAccountResolver
from shared.aws.account.region_resolver import AwsRegionResolver
from shared.aws.authentication.credential_resolver import AwsCredentialResolver
from shared.aws.authentication.identity_resolver import AwsIdentityResolver
from shared.aws.context.aws_context import AwsContext
from shared.aws.contracts.aws_service_contract import AwsServiceContract
from shared.aws.exceptions.aws_authentication_exception import AwsAuthenticationException
from shared.aws.exceptions.aws_configuration_exception import AwsConfigurationException
from shared.aws.exceptions.aws_exception import AwsException
from shared.aws.factories.aws_client_factory import AwsClientFactory
from shared.aws.factories.aws_session_factory import AwsSessionFactory
from shared.aws.observability.aws_observability import AwsObservability
from shared.aws.providers.aws_client_provider import AwsClientProvider
from shared.aws.settings.aws_settings import AwsSettings
from shared.aws.validation.aws_connection_validator import AwsConnectionValidator
from shared.aws.validation.aws_health_check import AwsHealthCheck

__all__ = [
    "AwsAccountResolver",
    "AwsAuthenticationException",
    "AwsClientFactory",
    "AwsClientProvider",
    "AwsConfigurationException",
    "AwsConnectionValidator",
    "AwsContext",
    "AwsCredentialResolver",
    "AwsException",
    "AwsHealthCheck",
    "AwsIdentityResolver",
    "AwsObservability",
    "AwsRegionResolver",
    "AwsServiceContract",
    "AwsSessionFactory",
    "AwsSettings",
]
