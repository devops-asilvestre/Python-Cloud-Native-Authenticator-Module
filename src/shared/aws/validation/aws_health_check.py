"""Health-check abstraction for AWS connectivity."""

from __future__ import annotations

from typing import Any

import boto3

from shared.aws.exceptions.aws_configuration_exception import AwsConfigurationException
from shared.aws.observability.aws_observability import AwsObservability


class AwsHealthCheck:
    """Validate that the current AWS session can reach AWS STS."""

    def __init__(
        self,
        session: boto3.session.Session | None = None,
        *,
        region_name: str | None = None,
        observability: AwsObservability | None = None,
    ) -> None:
        self._session = session or boto3.Session(region_name=region_name)
        self._region_name = region_name
        self.observability = observability or AwsObservability(service_name="aws-health-check")

    def check(self, *, region_name: str | None = None) -> bool:
        effective_region = region_name or self._region_name or self._session.region_name
        try:
            response = self._session.client("sts", region_name=effective_region).get_caller_identity()
            success = bool(response.get("Account"))
            self.observability.log_health_check(success=success, region_name=effective_region)
            return success
        except Exception as exc:  # pragma: no cover - depends on AWS runtime availability.
            self.observability.error(
                "aws_health_check_failed",
                region_name=effective_region,
                error_type=type(exc).__name__,
            )
            raise AwsConfigurationException(
                "AWS health check failed because the STS identity endpoint could not be reached."
            ) from exc

    def __call__(self, **kwargs: Any) -> bool:
        return self.check(**kwargs)
