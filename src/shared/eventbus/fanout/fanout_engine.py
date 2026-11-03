"""Deliver the same event to multiple consumers via fanout."""

from __future__ import annotations

from collections.abc import Iterable

from shared.events import EventEnvelope


class FanoutEngine:
    """One event -> N consumers distribution for EventBridge-based fanout."""

    def fanout(self, event: EventEnvelope, consumers: Iterable[str]) -> dict[str, str]:
        return {consumer: event.event_type for consumer in consumers}

    def distribute(self, event: EventEnvelope, consumers: Iterable[str]) -> list[tuple[str, str]]:
        return [(consumer, event.event_type) for consumer in consumers]
