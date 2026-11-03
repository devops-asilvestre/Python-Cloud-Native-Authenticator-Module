from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SessionMetadata:
    user_agent: str | None = None
    ip_address: str | None = None
