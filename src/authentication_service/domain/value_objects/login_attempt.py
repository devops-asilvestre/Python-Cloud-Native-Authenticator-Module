from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class LoginAttempt:
    succeeded: bool
    occurred_at: datetime
    ip_address: str | None = None

    def __post_init__(self) -> None:
        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise ValueError("LoginAttempt timestamp must be timezone-aware.")
        object.__setattr__(self, "occurred_at", self.occurred_at.astimezone(UTC))
