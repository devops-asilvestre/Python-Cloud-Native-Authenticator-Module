"""Time-bounded cache entry for a previously resolved secret."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from shared.secrets.contracts.secret_contract import SecretContract


@dataclass(slots=True)
class SecretCacheEntry:
    """Cache entry with TTL metadata."""

    secret: SecretContract
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ttl_seconds: int = 300

    @property
    def expires_at(self) -> datetime:
        return self.created_at + timedelta(seconds=self.ttl_seconds)

    def is_expired(self, *, now: datetime | None = None) -> bool:
        current_time = now or datetime.now(UTC)
        return current_time >= self.expires_at
