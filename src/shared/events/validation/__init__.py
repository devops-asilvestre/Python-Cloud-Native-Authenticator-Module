"""Event contract validators."""

from typing import TYPE_CHECKING

from shared.events.validation.naming_validator import EventNamingConvention

if TYPE_CHECKING:
    from shared.events.validation.schema_validator import EventSchemaValidator

__all__ = ["EventNamingConvention", "EventSchemaValidator"]


def __getattr__(name: str) -> object:
    if name == "EventSchemaValidator":
        from shared.events.validation.schema_validator import EventSchemaValidator

        return EventSchemaValidator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
