"""Factory helpers for DynamoDB unit tests."""

from __future__ import annotations

from shared.dynamodb.testing.fake_dynamodb import FakeDynamoDbResource


def fake_dynamodb_resource() -> FakeDynamoDbResource:
    """Create an isolated fake resource."""
    return FakeDynamoDbResource()
