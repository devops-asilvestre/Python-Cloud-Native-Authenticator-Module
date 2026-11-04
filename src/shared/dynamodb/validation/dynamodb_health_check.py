"""DynamoDB connectivity health check."""

from __future__ import annotations

from typing import Any

from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-untyped]

from shared.aws.observability.aws_observability import AwsObservability
from shared.dynamodb.exceptions.dynamodb_connection_exception import (
    DynamoDbConnectionException,
)
from shared.dynamodb.factories.dynamodb_client_factory import DynamoDbClientFactory
from shared.dynamodb.settings.dynamodb_settings import DynamoDbSettings


class DynamoDbHealthCheck:
    """Validate access to DynamoDB without listing or reading user data."""

    def __init__(
        self,
        client: Any | None = None,
        *,
        client_factory: DynamoDbClientFactory | None = None,
        settings: DynamoDbSettings | None = None,
        observability: AwsObservability | None = None,
    ) -> None:
        self.settings = settings or DynamoDbSettings()
        self._client = client
        self._client_factory = client_factory or DynamoDbClientFactory(settings=self.settings)
        self._observability = observability or AwsObservability(
            service_name="dynamodb-health-check"
        )

    def check(self) -> bool:
        client = self._client or self._client_factory.create()
        try:
            if self.settings.table_name:
                client.describe_table(TableName=self.settings.table_name)
            else:
                client.list_tables(Limit=1)
        except (BotoCoreError, ClientError) as exc:
            self._observability.error(
                "dynamodb_health_check_failed",
                error_type=type(exc).__name__,
                table_name=self.settings.table_name,
            )
            raise DynamoDbConnectionException("DynamoDB health check failed.") from exc
        self._observability.info(
            "dynamodb_health_check_succeeded",
            table_name=self.settings.table_name,
        )
        return True

    def __call__(self) -> bool:
        return self.check()
