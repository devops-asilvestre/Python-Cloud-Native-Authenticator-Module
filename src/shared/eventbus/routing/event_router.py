"""Corporate routing for EventBridge events."""

from __future__ import annotations

from dataclasses import dataclass

from shared.events import EventEnvelope


@dataclass(frozen=True, slots=True)
class RoutingDecision:
    """The resolved distribution pattern for a given event."""

    category: str
    consumers: tuple[str, ...]
    routing_mode: str
    bus_name: str
    tenant_id: str | None = None


class EventRouter:
    """Classify, identify consumers and route an event to the correct bus."""

    default_consumers = {
        "identity": ("audit", "notification", "authorization"),
        "tenant": ("audit", "notification", "authorization"),
        "authentication": ("audit", "notification"),
        "authorization": ("audit", "notification"),
        "notification": ("audit", "notification"),
        "mfa": ("audit", "notification"),
    }

    def classify(self, event_type: str) -> str:
        normalized = event_type.strip().lower()
        category = normalized.split(".", 1)[0]
        if category not in self.default_consumers:
            return "shared"
        return category

    def identify_consumers(self, event_type: str) -> tuple[str, ...]:
        category = self.classify(event_type)
        if category in self.default_consumers:
            return self.default_consumers[category]
        return ("audit",)

    def route(
        self,
        event: EventEnvelope | str,
        *,
        bus_name: str = "shared-event-bus",
    ) -> RoutingDecision:
        if isinstance(event, str):
            event_type = event
            tenant_id = None
        else:
            event_type = event.event_type
            tenant_id = event.tenant_id
        category = self.classify(event_type)
        consumers = self.identify_consumers(event_type)
        if len(consumers) == 1:
            routing_mode = "unicast"
        elif len(consumers) <= 3:
            routing_mode = "multicast"
        else:
            routing_mode = "broadcast"
        return RoutingDecision(
            category=category,
            consumers=consumers,
            routing_mode=routing_mode,
            bus_name=bus_name,
            tenant_id=tenant_id,
        )
