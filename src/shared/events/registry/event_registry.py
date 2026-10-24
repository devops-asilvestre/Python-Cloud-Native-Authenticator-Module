"""Version-aware registry of event payload schemas."""

from collections.abc import Mapping
from threading import RLock

from pydantic import BaseModel

from shared.events.exceptions.validation_exception import EventValidationException
from shared.events.metadata.event_version import EventVersion
from shared.events.validation.naming_validator import EventNamingConvention


def _has_open_object_schemas(schema: object) -> bool:
    if isinstance(schema, Mapping):
        if (
            schema.get("type") == "object"
            and schema.get("additionalProperties") is not False
        ):
            return True
        return any(_has_open_object_schemas(value) for value in schema.values())
    if isinstance(schema, list):
        return any(_has_open_object_schemas(value) for value in schema)
    return False


class EventRegistry:
    """Thread-safe registry keyed by stable event type and schema version."""

    def __init__(self) -> None:
        self._schemas: dict[tuple[str, EventVersion], type[BaseModel]] = {}
        self._lock = RLock()

    def register(
        self,
        event_type: str,
        version: EventVersion,
        payload_schema: type[BaseModel],
    ) -> None:
        """Register one immutable schema; duplicate registrations fail explicitly."""

        EventNamingConvention.validate(event_type)
        json_schema = payload_schema.model_json_schema()
        if _has_open_object_schemas(json_schema):
            raise EventValidationException(
                "Event payload schemas must forbid undeclared object fields."
            )
        key = (event_type, version)
        with self._lock:
            if key in self._schemas:
                raise EventValidationException(
                    f"Schema already registered for event {event_type!r} version {version}."
                )
            self._schemas[key] = payload_schema

    def resolve(self, event_type: str, version: EventVersion) -> type[BaseModel]:
        """Return the schema registered for an exact event type and version."""

        key = (event_type, version)
        with self._lock:
            schema = self._schemas.get(key)
        if schema is None:
            raise EventValidationException(
                f"No schema registered for event {event_type!r} version {version}."
            )
        return schema
