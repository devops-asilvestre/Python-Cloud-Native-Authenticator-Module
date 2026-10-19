"""Aggregate root abstraction with explicit domain event collection."""

from shared.kernel.domain_events import DomainEvent
from shared.kernel.entities import Entity


class AggregateRoot[EntityId](Entity[EntityId]):
    """Entity that owns and exposes domain events raised during its lifetime."""

    __slots__ = ("_domain_events",)

    def __init__(self, entity_id: EntityId) -> None:
        super().__init__(entity_id)
        self._domain_events: list[DomainEvent] = []

    @property
    def domain_events(self) -> tuple[DomainEvent, ...]:
        return tuple(self._domain_events)

    def add_domain_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        self._domain_events.clear()

    def pull_domain_events(self) -> tuple[DomainEvent, ...]:
        events = self.domain_events
        self.clear_domain_events()
        return events
