"""Result of a successful message publication."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PublishResult:
    """Non-sensitive identifiers returned by SQS after publishing."""

    message_id: str
    queue_name: str
    sequence_number: str | None = None
