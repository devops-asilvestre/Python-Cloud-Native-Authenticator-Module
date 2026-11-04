"""DynamoDB TTL attributes."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from shared.dynamodb.exceptions.dynamodb_exception import DynamoDbException


class TtlSupport:
    """Attach DynamoDB's epoch-seconds TTL attribute to an item."""

    def __init__(self, attribute_name: str = "ttl") -> None:
        if not attribute_name.strip():
            raise DynamoDbException("TTL attribute name cannot be empty.")
        self.attribute_name = attribute_name

    def add_ttl(self, item: dict[str, Any], expires_at: datetime) -> dict[str, Any]:
        if expires_at.tzinfo is None:
            raise DynamoDbException("TTL expiration must be timezone-aware.")
        result = dict(item)
        result[self.attribute_name] = int(expires_at.astimezone(UTC).timestamp())
        return result
