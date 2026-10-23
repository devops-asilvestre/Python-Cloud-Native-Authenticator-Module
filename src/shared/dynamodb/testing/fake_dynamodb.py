"""Small DynamoDB fakes for unit tests that do not require AWS or DynamoDB Local."""

from __future__ import annotations

from typing import Any


class FakeDynamoDbTable:
    """Record supported table operations and return deterministic responses."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.error: Exception | None = None

    def get_item(self, **kwargs: Any) -> dict[str, Any]:
        return self._run("get_item", **kwargs)

    def put_item(self, **kwargs: Any) -> dict[str, Any]:
        return self._run("put_item", **kwargs)

    def update_item(self, **kwargs: Any) -> dict[str, Any]:
        return self._run("update_item", **kwargs)

    def delete_item(self, **kwargs: Any) -> dict[str, Any]:
        return self._run("delete_item", **kwargs)

    def query(self, **kwargs: Any) -> dict[str, Any]:
        return self._run("query", **kwargs)

    def scan(self, **kwargs: Any) -> dict[str, Any]:
        return self._run("scan", **kwargs)

    def _run(self, operation: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append((operation, kwargs))
        if self.error is not None:
            raise self.error
        return {"operation": operation, "kwargs": kwargs}


class FakeDynamoDbResource:
    """Return stable fake table handles."""

    def __init__(self) -> None:
        self.tables: dict[str, FakeDynamoDbTable] = {}

    def Table(self, name: str) -> FakeDynamoDbTable:
        if name not in self.tables:
            self.tables[name] = FakeDynamoDbTable(name)
        return self.tables[name]
