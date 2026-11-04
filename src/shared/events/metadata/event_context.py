"""Observability context projected into an event without sharing mutable state."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from shared.events.metadata.event_correlation import EventCorrelation
from shared.events.metadata.event_trace_context import EventTraceContext
from shared.observability.context.request_context import RequestContext
from shared.observability.correlation.correlation_id import CorrelationId
from shared.observability.correlation.trace_id import TraceId
from shared.observability.tracing.trace_context import TraceContext

if TYPE_CHECKING:
    from shared.events.metadata.event_metadata import EventMetadata


class EventContext(BaseModel):
    """Immutable tenant and trace context used when constructing event metadata."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tenant_id: str = Field(min_length=1)
    correlation_id: CorrelationId = Field(default_factory=CorrelationId)
    trace_id: TraceId = Field(default_factory=TraceId)
    request_id: str | None = None
    causation_id: UUID | None = None
    span_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16], pattern=r"^[0-9a-f]{16}$")
    parent_span_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{16}$")
    sampled: bool = True

    @classmethod
    def from_observability(
        cls,
        request_context: RequestContext,
        trace_context: TraceContext | None = None,
    ) -> EventContext:
        """Copy stable IDs from existing observability contexts."""

        if request_context.tenant_id is None:
            raise ValueError("A tenant_id is required to create event context.")
        correlation = EventCorrelation.from_request_context(request_context)
        trace = EventTraceContext.from_trace_context(
            trace_context
            or TraceContext(trace_id=TraceId(str(request_context.trace_id)))
        )
        return cls(
            tenant_id=request_context.tenant_id,
            correlation_id=correlation.correlation_id,
            trace_id=trace.trace_id,
            request_id=correlation.request_id,
            span_id=trace.span_id,
            parent_span_id=trace.parent_span_id,
            sampled=trace.sampled,
        )

    @property
    def correlation(self) -> EventCorrelation:
        """Return the request correlation group represented by this context."""

        return EventCorrelation(
            correlation_id=self.correlation_id,
            request_id=self.request_id,
            causation_id=self.causation_id,
        )

    @property
    def trace_context(self) -> EventTraceContext:
        """Return the trace IDs represented by this context."""

        return EventTraceContext(
            trace_id=self.trace_id,
            span_id=self.span_id,
            parent_span_id=self.parent_span_id,
            sampled=self.sampled,
        )

    def to_metadata(
        self,
        *,
        source_service: str,
        causation_id: UUID | None = None,
    ) -> EventMetadata:
        """Create event metadata from trusted tenant and observability context."""

        from shared.events.metadata.event_metadata import EventMetadata

        return EventMetadata(
            correlation_id=self.correlation_id,
            trace_id=self.trace_id,
            tenant_id=self.tenant_id,
            source_service=source_service,
            request_id=self.request_id,
            causation_id=causation_id or self.causation_id,
            span_id=self.span_id,
            parent_span_id=self.parent_span_id,
            sampled=self.sampled,
        )
