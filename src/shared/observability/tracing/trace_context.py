"""Trace context model for propagation across service boundaries."""

from __future__ import annotations

import uuid
from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, Field

from shared.observability.correlation.trace_id import TraceId


class TraceContext(BaseModel):
    """Distributed tracing metadata that can be propagated via headers."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    trace_id: TraceId = Field(default_factory=TraceId)
    span_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    parent_span_id: str | None = None
    sampled: bool = True
    baggage: dict[str, str] = Field(default_factory=dict)

    def to_headers(self) -> dict[str, str]:
        """Transform the trace context into a propagation-safe dictionary."""

        status = "01" if self.sampled else "00"
        headers = {
            "traceparent": f"00-{str(self.trace_id)}-{self.span_id}-{status}",
            "x-trace-id": str(self.trace_id),
            "x-span-id": self.span_id,
        }
        if self.parent_span_id is not None:
            headers["x-parent-span-id"] = self.parent_span_id
        return headers

    @classmethod
    def from_headers(cls, headers: Mapping[str, str] | None = None) -> TraceContext:
        """Construct a trace context from propagation headers."""

        mapped = dict(headers or {})
        trace_id = mapped.get("x-trace-id") or mapped.get("traceparent", "").split("-")[1]
        span_id = mapped.get("x-span-id") or uuid.uuid4().hex[:16]
        parent_span_id = mapped.get("x-parent-span-id")
        sampled = mapped.get("traceparent", "").split("-")[-1] == "01"
        return cls(
            trace_id=TraceId(trace_id) if trace_id else TraceId(),
            span_id=span_id,
            parent_span_id=parent_span_id,
            sampled=sampled if mapped.get("traceparent") else True,
        )
