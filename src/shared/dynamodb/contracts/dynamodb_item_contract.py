"""Structural contract for objects that can be persisted in DynamoDB."""

from __future__ import annotations

from typing import Any, Protocol


class DynamoDbItemContract(Protocol):
    """Expose an item representation without coupling domain objects to boto3."""

    def to_dynamodb_item(self) -> dict[str, Any]:
        """Return an attribute map suitable for DynamoDB serialization."""
        ...
