"""Validation of bounded-context event names."""

import re

from shared.events.exceptions.validation_exception import EventValidationException

_EVENT_NAME_PATTERN = re.compile(
    r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*\."
    r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\."
    r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*$"
)


class EventNamingConvention:
    """Validates ``<bounded_context>.<aggregate>.<event>`` names."""

    @staticmethod
    def is_valid(event_type: str) -> bool:
        return _EVENT_NAME_PATTERN.fullmatch(event_type) is not None

    @classmethod
    def validate(cls, event_type: str) -> str:
        if not cls.is_valid(event_type):
            raise EventValidationException(
                "Event type must follow <bounded_context>.<aggregate>.<event> "
                "using lowercase letters, digits, and hyphens."
            )
        return event_type
