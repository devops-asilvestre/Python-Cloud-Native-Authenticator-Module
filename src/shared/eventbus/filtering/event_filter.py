"""Filter EventEnvelope instances using routing metadata."""

from __future__ import annotations

from collections.abc import Iterable

from shared.events import EventEnvelope, EventVersion


class EventFilter:
    """Support source, tenant, event_type, event_version and category filters."""

    def __init__(
        self,
        *,
        source: str | None = None,
        tenant: str | None = None,
        tenant_id: str | None = None,
        event_type: str | None = None,
        event_version: str | EventVersion | None = None,
        category: str | None = None,
    ) -> None:
        self.source = source
        self.tenant = tenant or tenant_id
        self.event_type_filter = event_type
        self.event_version_filter = event_version
        self.category_filter = category

    def _category_for(self, event: EventEnvelope) -> str:
        return event.event_type.split(".", 1)[0]

    def matches(self, event: EventEnvelope) -> bool:
        if self.source is not None and event.source_service != self.source:
            return False
        if self.tenant is not None and event.tenant_id != self.tenant:
            return False
        if self.event_type_filter is not None and event.event_type != self.event_type_filter:
            return False
        if self.event_version_filter is not None:
            if isinstance(self.event_version_filter, EventVersion):
                if event.event_version != self.event_version_filter:
                    return False
            elif str(event.event_version) != str(self.event_version_filter):
                return False
        if self.category_filter is not None and self._category_for(event) != self.category_filter:
            return False
        return True

    def filter(self, events: Iterable[EventEnvelope]) -> list[EventEnvelope]:
        return [event for event in events if self.matches(event)]

    def filter_events(self, events: Iterable[EventEnvelope]) -> list[EventEnvelope]:
        return self.filter(events)
