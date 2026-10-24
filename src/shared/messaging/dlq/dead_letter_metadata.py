"""Audit-safe dead-letter metadata."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DeadLetterMetadata:
    """Origin and failure information attached to a dead-letter message."""

    source_queue: str
    message_id: str
    event_id: str
    failure_type: str
    receive_count: int

    def __post_init__(self) -> None:
        if not all((self.source_queue, self.message_id, self.event_id, self.failure_type)):
            raise ValueError("Dead-letter metadata fields cannot be empty.")
        if self.receive_count < 1:
            raise ValueError("Dead-letter receive count must be positive.")
