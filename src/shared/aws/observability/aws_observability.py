"""Observability integration for the AWS shared foundation."""

from __future__ import annotations

from typing import Any

from shared.observability.context.request_context import RequestContext
from shared.observability.context.telemetry_context import TelemetryContext
from shared.observability.logging.structured_logger import StructuredLogger


class AwsObservability:
    """Bridge between AWS foundation components and the shared observability contract."""

    def __init__(
        self,
        *,
        service_name: str = "shared-aws",
        request_context: RequestContext | None = None,
        telemetry_context: TelemetryContext | None = None,
    ) -> None:
        self.service_name = service_name
        self.request_context = request_context or RequestContext()
        self.telemetry_context = telemetry_context or TelemetryContext(
            service_name=service_name,
            request_context=self.request_context,
        )
        self.logger = StructuredLogger(
            service_name,
            telemetry_context=self.telemetry_context,
            request_context=self.request_context,
        )

    def info(self, event: str, **fields: Any) -> None:
        self.logger.info(event, **fields)

    def warning(self, event: str, **fields: Any) -> None:
        self.logger.warning(event, **fields)

    def error(self, event: str, **fields: Any) -> None:
        self.logger.error(event, **fields)

    def debug(self, event: str, **fields: Any) -> None:
        self.logger.debug(event, **fields)

    def log_session_ready(self, *, region_name: str | None, profile_name: str | None) -> None:
        self.info(
            "aws_session_ready",
            region_name=region_name,
            profile_name=profile_name,
        )

    def log_client_created(self, *, service_name: str, region_name: str | None) -> None:
        self.info(
            "aws_client_created",
            service_name=service_name,
            region_name=region_name,
        )

    def log_health_check(self, *, success: bool, region_name: str | None) -> None:
        self.info(
            "aws_health_check_result",
            success=success,
            region_name=region_name,
        )
