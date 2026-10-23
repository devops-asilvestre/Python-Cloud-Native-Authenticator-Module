"""Optimistic item version metadata."""

from __future__ import annotations

from typing import Any

from shared.dynamodb.exceptions.dynamodb_exception import DynamoDbException


class VersionSupport:
    """Initialize and advance an integer version attribute."""

    def __init__(self, attribute_name: str = "version") -> None:
        if not attribute_name.strip():
            raise DynamoDbException("Version attribute name cannot be empty.")
        self.attribute_name = attribute_name

    def initialize(self, item: dict[str, Any]) -> dict[str, Any]:
        if self.attribute_name in item:
            raise DynamoDbException("Item already contains a version attribute.")
        result = dict(item)
        result[self.attribute_name] = 1
        return result

    def next_version(self, current_version: int) -> int:
        if current_version < 1:
            raise DynamoDbException("Current item version must be a positive integer.")
        return current_version + 1
