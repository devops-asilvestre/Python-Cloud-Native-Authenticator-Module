"""Backward-compatible event serializer contract and JSON implementation."""

from typing import Protocol

from shared.events.contracts.event_contract import EventContract
from shared.events.serialization.event_serializer import (
    EventSerializer as EventEnvelopeSerializer,
)
from shared.events.serialization.event_serializer import (
    JsonEventSerializer,
)


class EventSerializer(Protocol):
    """Original serializer interface retained for existing adapters."""

    def serialize(self, event: EventContract) -> bytes: ...

    def deserialize(
        self,
        payload: bytes,
        *,
        event_type: str,
        version: int,
    ) -> EventContract: ...


__all__ = [
    "EventEnvelopeSerializer",
    "EventSerializer",
    "JsonEventSerializer",
]
