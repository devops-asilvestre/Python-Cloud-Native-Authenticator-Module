"""Pytest fixtures for DynamoDB foundation unit tests."""

from __future__ import annotations

import pytest

from shared.dynamodb.testing.fake_dynamodb import FakeDynamoDbResource


@pytest.fixture
def fake_dynamodb() -> FakeDynamoDbResource:
    """Provide an isolated fake DynamoDB resource."""
    return FakeDynamoDbResource()
