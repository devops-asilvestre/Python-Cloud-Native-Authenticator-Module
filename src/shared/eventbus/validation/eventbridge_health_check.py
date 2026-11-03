"""Health check result for the EventBridge foundation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from shared.eventbus.providers.eventbridge_provider import EventBridgeProvider
from shared.eventbus.settings.eventbridge_settings import EventBridgeSettings


class HealthStatus(StrEnum):
    """EventBridge dependency health status."""

    HEALTHY = "Healthy"
    DEGRADED = "Degraded"
    UNHEALTHY = "Unhealthy"


@dataclass(frozen=True, slots=True)
class EventBridgeHealthResult:
    """Health status and bus name; never includes payload data."""

    status: HealthStatus
    bus_name: str
    reason: str | None = None


class EventBridgeHealthCheck:
    """Check basic EventBridge connectivity and configuration."""

    def __init__(
        self,
        settings: EventBridgeSettings | None = None,
        *,
        provider: EventBridgeProvider | None = None,
    ) -> None:
        self.settings = settings or EventBridgeSettings(
            account_id="123456789012",
            bus_name="shared-event-bus",
        )
        self.provider = provider or EventBridgeProvider(self.settings)

    def check(self, *, region_name: str | None = None) -> EventBridgeHealthResult:
        _ = region_name
        try:
            response = self.provider.describe_bus()
        except Exception as exc:
            return EventBridgeHealthResult(
                status=HealthStatus.UNHEALTHY,
                bus_name=self.settings.bus_name,
                reason=f"EventBridge DescribeEventBus failed: {type(exc).__name__}.",
            )
        if response.get("Name") != self.settings.bus_name:
            return EventBridgeHealthResult(
                status=HealthStatus.DEGRADED,
                bus_name=self.settings.bus_name,
                reason="EventBridge returned an unexpected bus name.",
            )
        return EventBridgeHealthResult(
            status=HealthStatus.HEALTHY,
            bus_name=self.settings.bus_name,
        )
