"""Create DynamoDB clients through the shared AWS foundation."""

from __future__ import annotations

from typing import Any

from botocore.config import Config  # type: ignore[import-untyped]

from shared.aws.factories.aws_client_factory import AwsClientFactory
from shared.dynamodb.contracts.aws_factory_contract import AwsDynamoDbFactoryContract
from shared.dynamodb.settings.dynamodb_settings import DynamoDbSettings


class DynamoDbClientFactory:
    """Create DynamoDB low-level clients without bypassing AWS configuration."""

    def __init__(
        self,
        aws_client_factory: AwsDynamoDbFactoryContract | None = None,
        *,
        settings: DynamoDbSettings | None = None,
    ) -> None:
        self.settings = settings or DynamoDbSettings()
        self._aws_client_factory = aws_client_factory or AwsClientFactory()

    def create(self) -> Any:
        config = Config(
            connect_timeout=self.settings.connect_timeout_seconds,
            read_timeout=self.settings.read_timeout_seconds,
            retries={"max_attempts": self.settings.max_attempts},
        )
        return self._aws_client_factory.create_client(
            "dynamodb",
            region_name=self.settings.region_name,
            endpoint_url=self.settings.endpoint_url,
            config=config,
        )
