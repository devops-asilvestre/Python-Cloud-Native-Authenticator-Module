"""Event metadata and schema versioning."""

from shared.events.metadata.event_context import EventContext
from shared.events.metadata.event_correlation import EventCorrelation
from shared.events.metadata.event_metadata import EventMetadata
from shared.events.metadata.event_trace_context import EventTraceContext
from shared.events.metadata.event_version import EventVersion

__all__ = [
    "EventContext",
    "EventCorrelation",
    "EventMetadata",
    "EventTraceContext",
    "EventVersion",
]
