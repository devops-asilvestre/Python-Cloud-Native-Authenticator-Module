"""Providers that integrate with external secret stores."""

from shared.secrets.providers.aws_secrets_manager_provider import AwsSecretsManagerProvider

__all__ = ["AwsSecretsManagerProvider"]
