"""Event serialization and deserialization failures."""

from shared.events.exceptions.event_exception import EventException


class EventSerializationException(EventException):
    """Raised when an event cannot be encoded or decoded safely."""

    def __init__(self, message: str, *, code: str = "EVENT_SERIALIZATION_ERROR") -> None:
        super().__init__(message, code=code)
