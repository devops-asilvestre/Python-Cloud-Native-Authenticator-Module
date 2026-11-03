"""Logical bus routing metadata."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EventBusMetadata:
    """Resolved EventBridge bus metadata for a tenant and event category."""

    bus_name: str
    region: str
    account_id: str
    environment: str
    tenant_id: str | None = None
    event_category: str | None = None
    event_type: str | None = None
    routing_mode: str = "broadcast"
    supports_filtering: bool = True
    supports_fanout: bool = True
