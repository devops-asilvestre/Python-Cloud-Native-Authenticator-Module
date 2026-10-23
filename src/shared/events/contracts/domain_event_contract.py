"""Public contract for events raised within a domain."""

from datetime import datetime
from typing import Protocol
from uuid import UUID


class DomainEventContract(Protocol):
    """Domain event contract without infrastructure or observability dependencies."""

    @property
    def event_id(self) -> UUID: ...

    @property
    def occurred_at(self) -> datetime: ...

    @property
    def event_type(self) -> str: ...
