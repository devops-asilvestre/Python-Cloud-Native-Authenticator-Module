"""Compose tenant-aware DynamoDB primary keys."""

from __future__ import annotations

from shared.dynamodb.keys.partition_key_builder import TenantAwarePartitionKeyBuilder
from shared.dynamodb.keys.sort_key_builder import TenantAwareSortKeyBuilder


class DynamoDbKeyBuilder:
    """Build the shared ``PK`` and ``SK`` key attributes."""

    def __init__(
        self,
        partition_key_builder: TenantAwarePartitionKeyBuilder | None = None,
        sort_key_builder: TenantAwareSortKeyBuilder | None = None,
    ) -> None:
        self._partition_key_builder = partition_key_builder or TenantAwarePartitionKeyBuilder()
        self._sort_key_builder = sort_key_builder or TenantAwareSortKeyBuilder()

    def build(self, tenant_id: str, entity_id: str) -> dict[str, str]:
        return {
            "PK": self._partition_key_builder.build(tenant_id),
            "SK": self._sort_key_builder.build(entity_id),
        }
