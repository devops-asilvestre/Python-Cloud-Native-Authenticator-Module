"""Event exception hierarchy."""

from shared.events.exceptions.event_exception import EventException
from shared.events.exceptions.serialization_exception import EventSerializationException
from shared.events.exceptions.validation_exception import EventValidationException

__all__ = [
    "EventException",
    "EventSerializationException",
    "EventValidationException",
]
