"""Trace metadata for event propagation across asynchronous boundaries."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from shared.observability.correlation.trace_id import TraceId
from shared.observability.tracing.trace_context import TraceContext


class EventTraceContext(BaseModel):
    """Immutable trace identifiers and sampling state carried by an event."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    trace_id: TraceId
    span_id: str = Field(pattern=r"^[0-9a-f]{16}$")
    parent_span_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{16}$")
    sampled: bool = True

    @classmethod
    def from_trace_context(cls, context: TraceContext) -> EventTraceContext:
        """Copy trace propagation data without sharing mutable baggage."""

        return cls(
            trace_id=TraceId(str(context.trace_id)),
            span_id=context.span_id,
            parent_span_id=context.parent_span_id,
            sampled=context.sampled,
        )

    def to_trace_context(self) -> TraceContext:
        """Reconstruct the observability trace context carried by this event."""

        return TraceContext(
            trace_id=TraceId(str(self.trace_id)),
            span_id=self.span_id,
            parent_span_id=self.parent_span_id,
            sampled=self.sampled,
        )
