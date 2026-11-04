"""Asynchronous event handler interface."""

from typing import Protocol

from shared.events.envelope.event_envelope import EventEnvelope


class EventHandlerContract(Protocol):
    """Application handler invoked for a validated event envelope."""

    async def handle(self, event: EventEnvelope) -> None: ...
