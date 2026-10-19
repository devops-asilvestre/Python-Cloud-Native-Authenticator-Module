"""Transport-neutral event contract."""

from collections.abc import Mapping
from typing import ClassVar, Protocol

from shared.events.metadata import EventMetadata
from shared.events.versioning import EventVersion


class EventContract(Protocol):
    """Public shape for an event published between bounded contexts."""

    event_type: ClassVar[str]
    version: ClassVar[EventVersion]
    metadata: EventMetadata
    payload: Mapping[str, object]
