"""Event naming, schema, and registry validation failures."""

from shared.events.exceptions.event_exception import EventException


class EventValidationException(EventException):
    """Raised when an event or its schema violates the shared contract."""

    def __init__(self, message: str, *, code: str = "EVENT_VALIDATION_ERROR") -> None:
        super().__init__(message, code=code)
