"""Common, non-sensitive metadata attached to integration events."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class EventMetadata:
    """Event identity, UTC creation time, and optional correlation identifiers."""

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str | None = None
    request_id: str | None = None
    trace_id: str | None = None
