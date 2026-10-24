"""Transport-independent JSON event serializer interface and implementation."""

import json
import math
from typing import Protocol

from shared.events.envelope.event_envelope import EventEnvelope
from shared.events.exceptions.serialization_exception import EventSerializationException
from shared.events.validation.schema_validator import EventSchemaValidator


def _validate_json_numbers(value: object) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise EventSerializationException(
            "Event payload contains a non-finite number; valid JSON requires finite numbers."
        )
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise EventSerializationException("Event payload object keys must be strings.")
            _validate_json_numbers(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _validate_json_numbers(item)


class EventSerializer(Protocol):
    """Interface for encoding validated event envelopes."""

    def serialize(self, event: EventEnvelope) -> bytes: ...


class JsonEventSerializer:
    """Validate and serialize event envelopes as deterministic UTF-8 JSON."""

    def __init__(self, schema_validator: EventSchemaValidator) -> None:
        self._schema_validator = schema_validator

    def serialize(self, event: EventEnvelope) -> bytes:
        self._schema_validator.validate(event)
        try:
            _validate_json_numbers(event.payload)
            encoded = json.dumps(
                event.model_dump(mode="json"),
                allow_nan=False,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            return encoded.encode("utf-8")
        except (TypeError, ValueError, UnicodeEncodeError) as exc:
            raise EventSerializationException(
                "Event could not be serialized as valid JSON."
            ) from exc
