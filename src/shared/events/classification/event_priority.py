"""Priority classification for event processing policies."""

from enum import IntEnum


class EventPriority(IntEnum):
    """Relative event processing priority; transports decide how to apply it."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
