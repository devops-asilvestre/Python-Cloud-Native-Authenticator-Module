"""DynamoDB connection validation."""

from __future__ import annotations

from shared.dynamodb.validation.dynamodb_health_check import DynamoDbHealthCheck


class DynamoDbConnectionValidator:
    """Expose health-check validation to application startup and probes."""

    def __init__(self, health_check: DynamoDbHealthCheck | None = None) -> None:
        self._health_check = health_check or DynamoDbHealthCheck()

    def validate(self) -> bool:
        return self._health_check.check()
