"""Message handler contract."""

from typing import Protocol

from shared.events.envelope.event_envelope import EventEnvelope


class MessageHandlerContract(Protocol):
    """Handle one validated event."""

    async def handle(self, event: EventEnvelope) -> None: ...
