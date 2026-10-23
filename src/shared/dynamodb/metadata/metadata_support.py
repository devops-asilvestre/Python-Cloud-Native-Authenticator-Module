"""Add standard timestamps and caller-provided metadata to DynamoDB items."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from shared.dynamodb.exceptions.dynamodb_exception import DynamoDbException


class MetadataSupport:
    """Create metadata-enriched copies while protecting reserved attributes."""

    RESERVED_ATTRIBUTES = frozenset(
        {"PK", "SK", "ttl", "version", "created_at", "updated_at", "metadata"}
    )

    def add_metadata(
        self,
        item: dict[str, Any],
        metadata: dict[str, Any],
        *,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        conflicts = self.RESERVED_ATTRIBUTES.intersection(metadata)
        if conflicts:
            raise DynamoDbException(
                f"Metadata cannot overwrite reserved attributes: {', '.join(sorted(conflicts))}."
            )
        current_time = now or datetime.now(UTC)
        if current_time.tzinfo is None:
            raise DynamoDbException("Metadata timestamp must be timezone-aware.")
        timestamp = current_time.astimezone(UTC).isoformat()
        result = dict(item)
        result.setdefault("created_at", timestamp)
        result["updated_at"] = timestamp
        previous_metadata = result.get("metadata", {})
        if not isinstance(previous_metadata, dict):
            raise DynamoDbException("Existing item metadata must be a dictionary.")
        result["metadata"] = {**previous_metadata, **metadata}
        return result
