"""Event envelope and registered payload schema validation."""

from pydantic import BaseModel, ValidationError

from shared.events.envelope.event_envelope import EventEnvelope
from shared.events.exceptions.validation_exception import EventValidationException
from shared.events.registry.event_registry import EventRegistry
from shared.events.validation.naming_validator import EventNamingConvention


class EventSchemaValidator:
    """Validate event names, envelope shape, and versioned payload schemas."""

    def __init__(self, registry: EventRegistry) -> None:
        self._registry = registry

    def validate(self, event: EventEnvelope) -> BaseModel:
        """Validate the payload and return its typed model without exposing input data."""

        try:
            EventEnvelope.model_validate(event.model_dump(mode="python"))
        except ValidationError as exc:
            raise EventValidationException("Event envelope is invalid.") from exc
        EventNamingConvention.validate(event.event_type)
        schema = self._registry.resolve(event.event_type, event.event_version)
        try:
            return schema.model_validate(event.payload)
        except ValidationError as exc:
            raise EventValidationException(
                "Event payload does not match its registered schema."
            ) from exc
