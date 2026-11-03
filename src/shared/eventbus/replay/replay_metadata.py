"""Replay metadata for future EventBridge replay support."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReplayMetadata:
    """Capture event identifiers for future replay or recovery workflows."""

    event_id: str
    event_type: str
    version: str
    timestamp: str
    tenant: str
