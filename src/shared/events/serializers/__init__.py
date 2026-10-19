"""Serializer interface; concrete formats belong to integration adapters."""

from typing import Protocol

from shared.events.contracts import EventContract


class EventSerializer(Protocol):
    """Transport-neutral interface for encoding and decoding event contracts."""

    def serialize(self, event: EventContract) -> bytes: ...

    def deserialize(
        self,
        payload: bytes,
        *,
        event_type: str,
        version: int,
    ) -> EventContract: ...
