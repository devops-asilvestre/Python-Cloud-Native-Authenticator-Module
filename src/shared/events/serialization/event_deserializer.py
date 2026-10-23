"""Strict JSON event deserializer with registered schema validation."""

import json
from typing import cast

from pydantic import ValidationError

from shared.events.envelope.event_envelope import EventEnvelope
from shared.events.exceptions.serialization_exception import EventSerializationException
from shared.events.exceptions.validation_exception import EventValidationException
from shared.events.validation.schema_validator import EventSchemaValidator


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    decoded: dict[str, object] = {}
    for key, value in pairs:
        if key in decoded:
            raise EventSerializationException("JSON event contains a duplicate object key.")
        decoded[key] = value
    return decoded


def _reject_non_json_constant(value: str) -> None:
    raise EventSerializationException(f"JSON event contains invalid numeric constant {value}.")


class EventDeserializer:
    """Decode JSON bytes and validate envelope and registered payload schema."""

    def __init__(self, schema_validator: EventSchemaValidator) -> None:
        self._schema_validator = schema_validator

    def deserialize(self, payload: bytes) -> EventEnvelope:
        try:
            raw = json.loads(
                payload.decode("utf-8"),
                object_pairs_hook=_reject_duplicate_keys,
                parse_constant=_reject_non_json_constant,
            )
        except EventSerializationException:
            raise
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise EventSerializationException("Event payload is not valid UTF-8 JSON.") from exc

        if not isinstance(raw, dict):
            raise EventSerializationException("JSON event envelope must be an object.")
        try:
            event = EventEnvelope.model_validate(cast(dict[str, object], raw))
        except ValidationError as exc:
            raise EventValidationException("JSON event envelope is invalid.") from exc
        self._schema_validator.validate(event)
        return event
