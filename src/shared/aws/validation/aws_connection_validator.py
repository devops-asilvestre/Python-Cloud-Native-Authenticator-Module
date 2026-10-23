"""Validate connectivity to AWS using the shared health-check abstraction."""

from __future__ import annotations

from shared.aws.validation.aws_health_check import AwsHealthCheck


class AwsConnectionValidator:
    """Thin validation wrapper around the AWS health check."""

    def __init__(self, health_check: AwsHealthCheck | None = None) -> None:
        self._health_check = health_check or AwsHealthCheck()

    def validate(self, *, region_name: str | None = None) -> bool:
        result = self._health_check.check(region_name=region_name)
        self._health_check.observability.info(
            "aws_connection_validation_completed",
            region_name=region_name,
            connected=result,
        )
        return result

    def is_connected(self, *, region_name: str | None = None) -> bool:
        return self.validate(region_name=region_name)
