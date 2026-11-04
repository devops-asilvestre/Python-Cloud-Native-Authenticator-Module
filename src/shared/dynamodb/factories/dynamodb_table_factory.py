"""Create table handles from a DynamoDB resource."""

from __future__ import annotations

from typing import Any

from shared.dynamodb.exceptions.dynamodb_exception import DynamoDbException
from shared.dynamodb.factories.dynamodb_resource_factory import DynamoDbResourceFactory


class DynamoDbTableFactory:
    """Resolve a table handle without provisioning or mutating table schemas."""

    def __init__(self, resource_factory: DynamoDbResourceFactory | None = None) -> None:
        self._resource_factory = resource_factory or DynamoDbResourceFactory()

    def create(self, table_name: str) -> Any:
        normalized_name = table_name.strip()
        if not normalized_name:
            raise DynamoDbException("DynamoDB table name cannot be empty.")
        return self._resource_factory.create().Table(normalized_name)
