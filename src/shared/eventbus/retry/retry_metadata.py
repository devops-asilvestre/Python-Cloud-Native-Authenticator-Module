"""Retry metadata for transient EventBridge publishing failures."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetryMetadata:
    """Retry context used by EventBridge policies."""

    attempt: int = 1
    max_attempts: int = 5
    event_type: str | None = None
    tenant_id: str | None = None
