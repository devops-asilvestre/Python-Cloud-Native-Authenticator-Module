"""Convert DynamoDB attribute values to Python values."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from boto3.dynamodb.types import TypeDeserializer  # type: ignore[import-untyped]

from shared.dynamodb.exceptions.dynamodb_serialization_exception import (
    DynamoDbSerializationException,
)


class DynamoDbDeserializer:
    """Deserialize DynamoDB attribute maps using boto3's type rules."""

    def __init__(self) -> None:
        self._deserializer = TypeDeserializer()

    def deserialize(self, item: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
        try:
            return {
                key: self._deserializer.deserialize(value)
                for key, value in item.items()
            }
        except (TypeError, ValueError, KeyError) as exc:
            raise DynamoDbSerializationException("Unable to deserialize DynamoDB item.") from exc
