"""EventBridge provider interface."""

from __future__ import annotations

from typing import Any

from shared.aws.factories.aws_client_factory import AwsClientFactory
from shared.eventbus.settings.eventbridge_settings import EventBridgeSettings


class EventBridgeProvider:
    """AWS EventBridge adapter centralized behind the foundation boundary."""

    def __init__(
        self,
        settings: EventBridgeSettings,
        *,
        client_factory: AwsClientFactory | None = None,
        client: Any | None = None,
    ) -> None:
        self.settings = settings
        self._client_factory = client_factory or AwsClientFactory()
        self._provided_client = client

    def _client(self) -> Any:
        if self._provided_client is not None:
            return self._provided_client
        return self._client_factory.create_client(
            "events",
            region_name=self.settings.aws_region,
            endpoint_url=self.settings.endpoint_url,
        )

    def get_bus_name(self) -> str:
        return self.settings.bus_name

    def describe_bus(self) -> dict[str, Any]:
        response = self._client().describe_event_bus(Name=self.settings.bus_name)
        if not isinstance(response, dict):
            raise TypeError("AWS EventBridge returned a non-dictionary response.")
        return response

    def put_events(self, entries: list[dict[str, str]]) -> dict[str, Any]:
        response = self._client().put_events(Entries=entries)
        if not isinstance(response, dict):
            raise TypeError("AWS EventBridge returned a non-dictionary response.")
        return response
