"""Read-only AWS Secrets Manager adapter for the secrets foundation."""

from __future__ import annotations

import base64
from datetime import datetime
from typing import Any

from shared.aws.factories.aws_client_factory import AwsClientFactory
from shared.aws.settings.aws_settings import AwsSettings
from shared.observability.context.request_context import RequestContext
from shared.observability.logging.structured_logger import StructuredLogger
from shared.secrets.context.secret_metadata import SecretMetadata
from shared.secrets.contracts.secret_contract import SecretContract
from shared.secrets.contracts.secret_provider_contract import SecretProviderContract
from shared.secrets.exceptions.secret_access_exception import SecretAccessException
from shared.secrets.exceptions.secret_not_found_exception import SecretNotFoundException
from shared.secrets.validation.secret_validator import SecretValidator


class AwsSecretsManagerProvider(SecretProviderContract):
    """Read-only adapter for AWS Secrets Manager."""

    def __init__(
        self,
        *,
        client_factory: AwsClientFactory | None = None,
        settings: AwsSettings | None = None,
        validator: SecretValidator | None = None,
        region_name: str | None = None,
        request_context: RequestContext | None = None,
        logger: StructuredLogger | None = None,
    ) -> None:
        self._client_factory = client_factory or AwsClientFactory(
            settings=settings or AwsSettings()
        )
        self.settings = settings or AwsSettings()
        self.region_name = region_name or self.settings.region
        self.validator = validator or SecretValidator()
        self.request_context = request_context or RequestContext()
        self.logger = logger or StructuredLogger(
            "shared-secrets-provider",
            request_context=self.request_context,
        )

    def _client(self, *, region_name: str | None = None) -> Any:
        return self._client_factory.create_client(
            "secretsmanager",
            region_name=region_name or self.region_name,
        )

    def get_secret(
        self,
        name: str,
        *,
        version_id: str | None = None,
        version_stage: str | None = None,
        region_name: str | None = None,
    ) -> SecretContract:
        resolved_name = self.validator.validate_name(name)
        client = self._client(region_name=region_name or self.region_name)
        try:
            response = client.get_secret_value(
                SecretId=resolved_name,
                VersionId=version_id,
                VersionStage=version_stage,
            )
        except Exception as exc:  # pragma: no cover - dependency on AWS runtime.
            raise SecretAccessException(
                f"Unable to read secret '{resolved_name}' from AWS Secrets Manager."
            ) from exc

        secret_value = response.get("SecretString")
        if secret_value is None:
            secret_binary = response.get("SecretBinary")
            if secret_binary is None:
                raise SecretNotFoundException(
                    f"Secret '{resolved_name}' does not contain a readable value."
                )
            if isinstance(secret_binary, (bytes, bytearray)):
                secret_value = base64.b64decode(secret_binary).decode("utf-8")
            else:
                secret_value = str(secret_binary)

        metadata = self.get_metadata(resolved_name, region_name=region_name or self.region_name)
        return SecretContract(
            name=resolved_name,
            value=str(secret_value),
            version=str(response.get("VersionId") or version_id or "AWSCURRENT"),
            region=region_name or self.region_name,
            account_id=self.settings.account_id,
            metadata=metadata,
            source="aws-secrets-manager",
        )

    def get_metadata(self, name: str, *, region_name: str | None = None) -> SecretMetadata:
        resolved_name = self.validator.validate_name(name)
        client = self._client(region_name=region_name or self.region_name)
        try:
            response = client.describe_secret(SecretId=resolved_name)
        except Exception as exc:  # pragma: no cover - dependency on AWS runtime.
            raise SecretAccessException(
                f"Unable to describe secret '{resolved_name}' in AWS Secrets Manager."
            ) from exc

        created_date = response.get("CreatedDate")
        changed_date = response.get("LastChangedDate")
        last_accessed = response.get("LastAccessedDate")
        return SecretMetadata(
            name=resolved_name,
            arn=response.get("ARN"),
            description=response.get("Description"),
            version_id=str(response.get("VersionId") or "AWSCURRENT"),
            version_stage=response.get("VersionStages", [None])[0],
            secret_type="string" if response.get("SecretString") is not None else "binary",
            created_date=created_date if isinstance(created_date, datetime) else None,
            last_changed_date=changed_date if isinstance(changed_date, datetime) else None,
            last_accessed_date=last_accessed if isinstance(last_accessed, datetime) else None,
            tags=dict(response.get("Tags", {})),
            rotation_enabled=bool(response.get("RotationEnabled", False)),
            rotation_lambda_arn=response.get("RotationLambdaARN"),
            owning_service=response.get("OwningService"),
        )

    def list_secrets(
        self,
        *,
        region_name: str | None = None,
        max_results: int | None = None,
    ) -> list[str]:
        client = self._client(region_name=region_name or self.region_name)
        try:
            response = client.list_secrets(MaxResults=max_results)
        except Exception as exc:  # pragma: no cover - dependency on AWS runtime.
            raise SecretAccessException("Unable to list secrets from AWS Secrets Manager.") from exc
        return [
            str(secret.get("Name", ""))
            for secret in response.get("SecretList", [])
            if secret.get("Name")
        ]
