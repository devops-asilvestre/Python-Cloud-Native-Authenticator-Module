"""Public contract for events shared between bounded contexts."""

from typing import Protocol

from shared.events.contracts.event_contract import EventContract


class IntegrationEventContract(EventContract, Protocol):
    """Versioned contract safe to publish across bounded-context boundaries."""
