"""Resolve the appropriate EventBridge bus for a tenant and event category."""

from __future__ import annotations

from shared.eventbus.exceptions.eventbridge_exception import EventBridgeConfigurationException
from shared.eventbus.metadata.event_bus_metadata import EventBusMetadata
from shared.eventbus.settings.eventbridge_settings import EventBridgeSettings


class DefaultEventBusStrategy:
    """Corporate routing strategy for tenant and application events."""

    _routes = {
        "authentication": "authentication-bus",
        "tenant": "tenant-bus",
        "audit": "audit-bus",
    }

    def resolve(
        self,
        tenant_id: str,
        event_category: str | None,
        event_type: str | None,
    ) -> str:
        if not tenant_id or not tenant_id.strip():
            raise EventBridgeConfigurationException(
                "A valid tenant_id is required to resolve the bus."
            )
        if event_category is None:
            return "shared-event-bus"
        route = self._routes.get(event_category.lower())
        if route is not None:
            return route
        if event_type is not None and event_type.lower().startswith("tenant."):
            return "tenant-bus"
        return "shared-event-bus"


class EventBusResolver:
    """Resolve the logical bus a tenant and event should use."""

    def __init__(
        self,
        settings: EventBridgeSettings,
        strategy: DefaultEventBusStrategy | None = None,
    ) -> None:
        self.settings = settings
        self.strategy = strategy or DefaultEventBusStrategy()

    def resolve(
        self,
        tenant_id: str,
        event_category: str | None,
        event_type: str | None,
    ) -> EventBusMetadata:
        resolved_bus = self.strategy.resolve(tenant_id, event_category, event_type)
        category = (event_category or "shared").lower()
        bus_name = self.settings.bus_name if resolved_bus == "shared-event-bus" else resolved_bus
        return EventBusMetadata(
            bus_name=bus_name,
            region=self.settings.aws_region,
            account_id=self.settings.account_id,
            environment=self.settings.environment,
            tenant_id=tenant_id,
            event_category=category,
            event_type=event_type,
            routing_mode="broadcast",
        )
