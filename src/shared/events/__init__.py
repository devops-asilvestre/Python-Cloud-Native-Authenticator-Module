"""Versionable event contracts independent of any transport provider."""

from shared.events.classification import EventCategory, EventPriority
from shared.events.envelope import EventEnvelope
from shared.events.exceptions import (
    EventException,
    EventSerializationException,
    EventValidationException,
)
from shared.events.metadata import (
    EventContext,
    EventCorrelation,
    EventMetadata,
    EventTraceContext,
    EventVersion,
)
from shared.events.registry import EventRegistry, EventTypeResolver
from shared.events.serialization import EventDeserializer, EventSerializer, JsonEventSerializer
from shared.events.validation import EventNamingConvention, EventSchemaValidator

__all__ = [
    "EventCategory",
    "EventContext",
    "EventCorrelation",
    "EventDeserializer",
    "EventEnvelope",
    "EventException",
    "EventMetadata",
    "EventNamingConvention",
    "EventPriority",
    "EventRegistry",
    "EventSchemaValidator",
    "EventSerializationException",
    "EventSerializer",
    "EventTypeResolver",
    "EventTraceContext",
    "EventValidationException",
    "EventVersion",
    "JsonEventSerializer",
]
