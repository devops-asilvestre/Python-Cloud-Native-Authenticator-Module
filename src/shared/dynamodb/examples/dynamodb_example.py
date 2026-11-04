"""Minimal example of tenant-aware DynamoDB access."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from shared.dynamodb.keys.dynamodb_key_builder import DynamoDbKeyBuilder
from shared.dynamodb.metadata.metadata_support import MetadataSupport
from shared.dynamodb.metadata.ttl_support import TtlSupport
from shared.dynamodb.providers.dynamodb_table_provider import DynamoDbTableProvider
from shared.dynamodb.settings.dynamodb_settings import DynamoDbSettings


def put_temporary_item(
    *,
    tenant_id: str,
    entity_id: str,
    payload: dict[str, Any],
    table_provider: DynamoDbTableProvider | None = None,
) -> None:
    """Persist one temporary item without including domain-specific behavior."""
    settings = DynamoDbSettings()
    provider = table_provider or DynamoDbTableProvider(settings=settings)
    item = {
        **DynamoDbKeyBuilder().build(tenant_id, entity_id),
        **payload,
    }
    item = MetadataSupport().add_metadata(item, {"source": "example"})
    item = TtlSupport().add_ttl(item, expires_at=datetime.now(UTC) + timedelta(hours=1))
    provider.get_table().put_item(Item=item)
