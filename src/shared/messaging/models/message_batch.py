"""Batch returned by a queue consumer."""

from dataclasses import dataclass

from shared.messaging.models.consumed_message import ConsumedMessage


@dataclass(frozen=True, slots=True)
class MessageBatch:
    """Messages received from one logical queue."""

    queue_name: str
    messages: tuple[ConsumedMessage, ...]
