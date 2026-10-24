"""Shared protocol for domain and integration event implementations."""

from collections.abc import Mapping
from typing import ClassVar, Protocol

from shared.events.metadata.event_metadata import EventMetadata
from shared.events.metadata.event_version import EventVersion


class EventContract(Protocol):
    """Transport-neutral shape implemented by a bounded context's event."""

    event_type: ClassVar[str]
    version: ClassVar[EventVersion]
    metadata: EventMetadata
    payload: Mapping[str, object]
