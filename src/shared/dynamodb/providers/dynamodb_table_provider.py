"""Provide and cache read/write table handles."""

from __future__ import annotations

from shared.dynamodb.exceptions.dynamodb_exception import DynamoDbException
from shared.dynamodb.factories.dynamodb_resource_factory import DynamoDbResourceFactory
from shared.dynamodb.factories.dynamodb_table_factory import DynamoDbTableFactory
from shared.dynamodb.observability.dynamodb_observability import DynamoDbObservability
from shared.dynamodb.providers.observed_dynamodb_table import ObservedDynamoDbTable
from shared.dynamodb.settings.dynamodb_settings import DynamoDbSettings


class DynamoDbTableProvider:
    """Resolve table handles lazily and reuse them within the provider."""

    def __init__(
        self,
        table_factory: DynamoDbTableFactory | None = None,
        *,
        settings: DynamoDbSettings | None = None,
        observability: DynamoDbObservability | None = None,
    ) -> None:
        self.settings = settings or DynamoDbSettings()
        self._table_factory = table_factory or DynamoDbTableFactory(
            DynamoDbResourceFactory(settings=self.settings)
        )
        self._observability = observability or DynamoDbObservability()
        self._tables: dict[str, ObservedDynamoDbTable] = {}

    def get_table(self, table_name: str | None = None) -> ObservedDynamoDbTable:
        effective_name = table_name or self.settings.table_name
        if effective_name is None or not effective_name.strip():
            raise DynamoDbException("A DynamoDB table name must be configured.")
        normalized_name = effective_name.strip()
        if normalized_name not in self._tables:
            self._tables[normalized_name] = ObservedDynamoDbTable(
                self._table_factory.create(normalized_name),
                observability=self._observability,
            )
        return self._tables[normalized_name]

    def __call__(self, table_name: str | None = None) -> ObservedDynamoDbTable:
        return self.get_table(table_name)
