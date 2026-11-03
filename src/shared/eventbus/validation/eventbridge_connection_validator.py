"""Validate AWS credentials and EventBridge access."""

from __future__ import annotations

from shared.eventbus.providers.eventbridge_provider import EventBridgeProvider
from shared.eventbus.settings.eventbridge_settings import EventBridgeSettings
from shared.eventbus.validation.eventbridge_health_check import EventBridgeHealthCheck, HealthStatus


class EventBridgeConnectionValidator:
    """Validate access to the configured EventBridge bus."""

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
        self.health_check = EventBridgeHealthCheck(self.settings, provider=provider)

    def validate(self, *, region_name: str | None = None) -> bool:
        _ = region_name
        return self.health_check.check(region_name=region_name).status is HealthStatus.HEALTHY

    def is_connected(self, *, region_name: str | None = None) -> bool:
        return self.validate(region_name=region_name)
