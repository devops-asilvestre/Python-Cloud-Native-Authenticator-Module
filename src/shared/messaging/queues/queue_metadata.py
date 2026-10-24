"""Logical queue metadata, without environment-specific queue URLs."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class QueueMetadata:
    """Resolved logical queue information."""

    bounded_context: str
    event_type: str
    queue_name: str
    fifo: bool = False
