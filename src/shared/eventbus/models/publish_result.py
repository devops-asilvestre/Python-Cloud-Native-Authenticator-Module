"""Result of a successful EventBridge publication."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PublishResult:
    """Non-sensitive identifiers returned by the EventBridge foundation."""

    message_id: str
    bus_name: str
    sequence_number: str | None = None
    success: bool = True
