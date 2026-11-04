"""Table handle that records DynamoDB operation outcomes."""

from __future__ import annotations

from typing import Any

from shared.dynamodb.observability.dynamodb_observability import DynamoDbObservability


class ObservedDynamoDbTable:
    """Delegate common table operations while logging safe operation metadata."""

    def __init__(
        self,
        table: Any,
        *,
        observability: DynamoDbObservability | None = None,
    ) -> None:
        self._table = table
        self._observability = observability or DynamoDbObservability()

    @property
    def name(self) -> str:
        return str(self._table.name)

    def get_item(self, **kwargs: Any) -> Any:
        return self._execute("get_item", **kwargs)

    def put_item(self, **kwargs: Any) -> Any:
        return self._execute("put_item", **kwargs)

    def update_item(self, **kwargs: Any) -> Any:
        return self._execute("update_item", **kwargs)

    def delete_item(self, **kwargs: Any) -> Any:
        return self._execute("delete_item", **kwargs)

    def query(self, **kwargs: Any) -> Any:
        return self._execute("query", **kwargs)

    def scan(self, **kwargs: Any) -> Any:
        return self._execute("scan", **kwargs)

    def _execute(self, operation: str, **kwargs: Any) -> Any:
        try:
            result = getattr(self._table, operation)(**kwargs)
        except Exception as exc:
            self._observability.operation_failed(
                operation,
                table_name=self.name,
                error=exc,
            )
            raise
        self._observability.operation_succeeded(operation, table_name=self.name)
        return result
