"""Message publisher contract."""

from typing import Protocol

from shared.events.envelope.event_envelope import EventEnvelope
from shared.messaging.models.publish_result import PublishResult


class MessagePublisherContract(Protocol):
    """Publish validated integration events."""

    async def publish(self, event: EventEnvelope) -> PublishResult: ...
