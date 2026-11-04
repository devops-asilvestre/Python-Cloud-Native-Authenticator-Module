"""Generic base for immutable domain event records."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import ClassVar
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Base event metadata; concrete events are defined by their owning domain."""

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    version: ClassVar[int] = 1

    @property
    def event_type(self) -> str:
        return type(self).__name__
