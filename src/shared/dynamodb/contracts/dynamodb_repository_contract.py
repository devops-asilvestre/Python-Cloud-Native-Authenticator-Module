"""Tenant-aware repository contract for DynamoDB persistence adapters."""

from __future__ import annotations

from typing import Any, Protocol


class DynamoDbRepositoryContract(Protocol):
    """Base operations shared by context-specific DynamoDB repositories."""

    def get_item(self, tenant_id: str, entity_id: str) -> dict[str, Any] | None: ...

    def put_item(self, tenant_id: str, item: dict[str, Any]) -> None: ...

    def update_item(
        self,
        tenant_id: str,
        entity_id: str,
        updates: dict[str, Any],
        *,
        expected_version: int,
    ) -> dict[str, Any] | None: ...

    def delete_item(self, tenant_id: str, entity_id: str) -> None: ...

    def query_items(
        self,
        tenant_id: str,
        *,
        sort_key_prefix: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]: ...

    def scan_items(self, tenant_id: str, *, limit: int | None = None) -> list[dict[str, Any]]: ...
