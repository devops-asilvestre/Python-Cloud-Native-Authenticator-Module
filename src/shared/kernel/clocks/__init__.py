"""Clock abstraction and UTC system clock."""

from datetime import UTC, datetime
from typing import Protocol


class Clock(Protocol):
    """Source of current time, replaceable by deterministic test clocks."""

    def now(self) -> datetime: ...


class SystemClock:
    """Clock that returns the current timezone-aware UTC time."""

    def now(self) -> datetime:
        return datetime.now(UTC)
