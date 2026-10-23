"""Convert Python values to DynamoDB attribute values."""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any

from boto3.dynamodb.types import TypeSerializer  # type: ignore[import-untyped]

from shared.dynamodb.exceptions.dynamodb_serialization_exception import (
    DynamoDbSerializationException,
)


class DynamoDbSerializer:
    """Serialize Python item maps using boto3's DynamoDB type rules."""

    def __init__(self) -> None:
        self._serializer = TypeSerializer()

    def serialize(self, item: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
        try:
            return {
                key: self._serializer.serialize(self._normalize(value))
                for key, value in item.items()
            }
        except (TypeError, ValueError, ArithmeticError) as exc:
            raise DynamoDbSerializationException("Unable to serialize DynamoDB item.") from exc

    @classmethod
    def _normalize(cls, value: Any) -> Any:
        if isinstance(value, float):
            return Decimal(str(value))
        if isinstance(value, Mapping):
            return {key: cls._normalize(nested) for key, nested in value.items()}
        if isinstance(value, list):
            return [cls._normalize(nested) for nested in value]
        if isinstance(value, tuple):
            return [cls._normalize(nested) for nested in value]
        if isinstance(value, (set, frozenset)):
            return {cls._normalize(nested) for nested in value}
        return value
