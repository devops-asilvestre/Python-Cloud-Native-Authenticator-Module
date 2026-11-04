"""Base exception for event contract failures."""


class EventException(Exception):
    """Base class for safe, explicit event-related errors."""

    def __init__(self, message: str, *, code: str = "EVENT_ERROR") -> None:
        super().__init__(message)
        self.code = code
