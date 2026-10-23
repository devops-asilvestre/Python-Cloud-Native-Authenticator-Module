"""Common, non-sensitive metadata attached to events."""

import uuid
from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from shared.events.metadata.event_correlation import EventCorrelation
from shared.events.metadata.event_trace_context import EventTraceContext
from shared.observability.correlation.correlation_id import CorrelationId
from shared.observability.correlation.trace_id import TraceId


class EventMetadata(BaseModel):
    """Identity, tenant, source, and tracing metadata for a published event."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: UUID = Field(default_factory=uuid4)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: CorrelationId = Field(default_factory=CorrelationId)
    trace_id: TraceId = Field(default_factory=TraceId)
    tenant_id: str = Field(min_length=1)
    source_service: str = Field(min_length=1)
    request_id: str | None = None
    causation_id: UUID | None = None
    span_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16], pattern=r"^[0-9a-f]{16}$")
    parent_span_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{16}$")
    sampled: bool = True

    @field_validator("occurred_at")
    @classmethod
    def require_aware_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Event occurred_at must be timezone-aware.")
        return value.astimezone(UTC)

    @field_validator("tenant_id", "source_service")
    @classmethod
    def require_non_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Event tenant_id and source_service cannot be blank.")
        return value

    @property
    def correlation(self) -> EventCorrelation:
        """Return correlation identifiers as a cohesive value object."""

        return EventCorrelation(
            correlation_id=self.correlation_id,
            request_id=self.request_id,
            causation_id=self.causation_id,
        )

    @property
    def trace_context(self) -> EventTraceContext:
        """Return the trace identifier in the event tracing value object."""

        return EventTraceContext(
            trace_id=self.trace_id,
            span_id=self.span_id,
            parent_span_id=self.parent_span_id,
            sampled=self.sampled,
        )
