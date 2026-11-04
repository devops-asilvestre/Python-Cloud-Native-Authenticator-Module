"""Resolve event names and versions to registered payload schemas."""

from pydantic import BaseModel

from shared.events.metadata.event_version import EventVersion
from shared.events.registry.event_registry import EventRegistry


class EventTypeResolver:
    """Small resolver facade for event deserializers and consumers."""

    def __init__(self, registry: EventRegistry) -> None:
        self._registry = registry

    def resolve(self, event_type: str, version: EventVersion) -> type[BaseModel]:
        return self._registry.resolve(event_type, version)
