"""Message consumer contract."""

from typing import Protocol

from shared.messaging.models.message_batch import MessageBatch
from shared.messaging.queues.queue_metadata import QueueMetadata


class MessageConsumerContract(Protocol):
    """Receive and decode events from a logical queue."""

    async def consume(self, queue: QueueMetadata) -> MessageBatch: ...
