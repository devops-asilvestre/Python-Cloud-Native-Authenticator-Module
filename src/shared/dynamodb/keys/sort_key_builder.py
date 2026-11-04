"""Build DynamoDB entity sort keys."""

from __future__ import annotations

from shared.dynamodb.exceptions.dynamodb_exception import DynamoDbException


class TenantAwareSortKeyBuilder:
    """Create entity sort keys in the required ``ENTITY#{entity_id}`` form."""

    def build(self, entity_id: str) -> str:
        entity = entity_id.strip()
        if not entity:
            raise DynamoDbException("Entity ID cannot be empty.")
        return f"ENTITY#{entity}"
