"""Asynchronous event subscriber interface, independent of transport."""

from typing import Protocol

from shared.events.contracts.event_handler_contract import EventHandlerContract


class EventSubscriberContract(Protocol):
    """Port for registering and removing event handlers."""

    async def subscribe(self, event_type: str, handler: EventHandlerContract) -> None: ...

    async def unsubscribe(self, event_type: str, handler: EventHandlerContract) -> None: ...
