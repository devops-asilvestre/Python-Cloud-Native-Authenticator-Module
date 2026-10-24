"""Event schema registration and resolution."""

from shared.events.registry.event_registry import EventRegistry
from shared.events.registry.event_type_resolver import EventTypeResolver

__all__ = ["EventRegistry", "EventTypeResolver"]
