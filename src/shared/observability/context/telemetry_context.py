"""Telemetry context for log and tracing metadata."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from shared.observability.context.request_context import RequestContext


class TelemetryContext(BaseModel):
    """Cross-cutting telemetry metadata for a service or request."""

    model_config = ConfigDict(extra="ignore")

    service_name: str = "unknown-service"
    component: str | None = None
    environment: str = "local"
    request_context: RequestContext | None = None
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)

    def to_log_fields(self) -> dict[str, str | int | float | bool | None]:
        """Convert the telemetry context into a log-safe payload."""

        request_fields = self.request_context.to_log_fields() if self.request_context else {}
        return {
            "service_name": self.service_name,
            "component": self.component,
            "environment": self.environment,
            **request_fields,
            **self.metadata,
        }
