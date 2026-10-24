"""Correlation metadata for tracing an event's cause and request."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict

from shared.observability.context.request_context import RequestContext
from shared.observability.correlation.correlation_id import CorrelationId


class EventCorrelation(BaseModel):
    """Immutable correlation identifiers carried across asynchronous work."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    correlation_id: CorrelationId
    request_id: str | None = None
    causation_id: UUID | None = None

    @classmethod
    def from_request_context(cls, context: RequestContext) -> EventCorrelation:
        """Copy correlation identifiers from the active request context."""

        return cls(
            correlation_id=CorrelationId(str(context.correlation_id)),
            request_id=str(context.request_id),
        )
