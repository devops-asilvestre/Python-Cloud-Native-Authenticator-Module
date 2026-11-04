"""Asynchronous event publisher interface, independent of transport."""

from typing import Protocol

from shared.events.envelope.event_envelope import EventEnvelope


class EventPublisherContract(Protocol):
    """Port through which application code requests event publication."""

    async def publish(self, event: EventEnvelope) -> None: ...
