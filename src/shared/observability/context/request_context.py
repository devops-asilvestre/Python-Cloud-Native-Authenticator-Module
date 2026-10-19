"""Request context model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from shared.observability.correlation.correlation_id import CorrelationId
from shared.observability.correlation.request_id import RequestId
from shared.observability.correlation.trace_id import TraceId


class RequestContext(BaseModel):
    """Context propagated across the request execution lifecycle."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    request_id: RequestId = Field(default_factory=RequestId)
    correlation_id: CorrelationId = Field(default_factory=CorrelationId)
    trace_id: TraceId = Field(default_factory=TraceId)
    tenant_id: str | None = None
    user_id: str | None = None
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)

    def to_log_fields(self) -> dict[str, str]:
        """Return correlation-safe fields for structured logging."""

        return {
            "request_id": str(self.request_id),
            "correlation_id": str(self.correlation_id),
            "trace_id": str(self.trace_id),
        }
