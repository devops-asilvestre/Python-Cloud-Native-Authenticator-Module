"""Fixtures for EventBridge unit tests."""

from __future__ import annotations

from shared.eventbus.settings.eventbridge_settings import EventBridgeSettings


def make_eventbridge_settings(
    *,
    aws_region: str = "us-east-1",
    account_id: str = "123456789012",
    bus_name: str = "shared-event-bus",
) -> EventBridgeSettings:
    return EventBridgeSettings(
        aws_region=aws_region,
        account_id=account_id,
        bus_name=bus_name,
        environment="dev",
        archive_enabled=True,
        replay_enabled=True,
    )
