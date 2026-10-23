import json
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import pytest
from pydantic import BaseModel, ConfigDict, Field

from shared.events import (
    EventCategory,
    EventContext,
    EventCorrelation,
    EventDeserializer,
    EventEnvelope,
    EventException,
    EventMetadata,
    EventNamingConvention,
    EventPriority,
    EventRegistry,
    EventSchemaValidator,
    EventSerializationException,
    EventTraceContext,
    EventTypeResolver,
    EventValidationException,
    EventVersion,
    JsonEventSerializer,
)
from shared.events.contracts import (
    DomainEventContract,
    EventContract,
    EventHandlerContract,
    EventPublisherContract,
    EventSubscriberContract,
    IntegrationEventContract,
)
from shared.events.serializers import EventSerializer as LegacyEventSerializer
from shared.events.testing import (
    FAKE_EVENT_TYPE,
    FAKE_EVENT_VERSION,
    FakeUserCreatedPayload,
    make_event,
    make_fake_event_registry,
    make_fake_user_created_event,
)
from shared.events.versioning import EventVersion as LegacyEventVersion
from shared.observability.context.request_context import RequestContext
from shared.observability.tracing.trace_context import TraceContext


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(min_length=1)


def test_semver_round_trips_as_a_string_and_orders_versions() -> None:
    version = EventVersion.parse("1.2.3")

    assert str(version) == "1.2.3"
    assert EventVersion.model_validate("1.2.3") == version
    assert EventVersion(major=1, minor=2) < EventVersion(major=1, minor=2, patch=1)
    assert version.__lt__(object()) is NotImplemented
    assert LegacyEventVersion is EventVersion
    with pytest.raises(ValueError, match="major version"):
        EventVersion(major=0)
    with pytest.raises(ValueError, match="cannot be negative"):
        EventVersion(major=1, patch=-1)
    with pytest.raises(ValueError, match="Invalid event version"):
        EventVersion.parse("01.2.3")
    with pytest.raises(ValueError, match="Invalid event version"):
        EventVersion.model_validate("v1")


def test_metadata_requires_tenant_and_source_and_normalizes_utc() -> None:
    local_time = datetime(2026, 1, 1, 12, tzinfo=UTC) + timedelta(hours=3)
    metadata = EventMetadata(
        tenant_id="tenant-1",
        source_service="identity-service",
        occurred_at=local_time,
    )

    assert metadata.occurred_at.tzinfo == UTC
    assert metadata.occurred_at.hour == 15
    assert str(metadata.correlation_id)
    assert str(metadata.trace_id)
    with pytest.raises(ValueError, match="timezone-aware"):
        EventMetadata(
            tenant_id="tenant-1",
            source_service="identity-service",
            occurred_at=datetime(2026, 1, 1),
        )
    with pytest.raises(ValueError):
        EventMetadata(tenant_id=" ", source_service="identity-service")
    with pytest.raises(ValueError):
        EventMetadata(tenant_id="tenant-1", source_service="")


def test_event_envelope_exposes_required_metadata_and_validates_names() -> None:
    metadata = EventMetadata(tenant_id="tenant-1", source_service="identity-service")
    event = EventEnvelope.from_metadata(
        event_type="identity.user.created",
        event_version=EventVersion(major=1),
        metadata=metadata,
        payload={"user_id": "user-1"},
    )

    assert event.event_id == metadata.event_id
    assert event.metadata == metadata
    assert event.tenant_id == "tenant-1"
    assert event.payload == {"user_id": "user-1"}
    with pytest.raises(EventValidationException, match="Event type must follow"):
        make_event(event_type="identity.user.created.v1")
    with pytest.raises(ValueError, match="timezone-aware"):
        EventEnvelope(
            event_id=uuid4(),
            event_type="identity.user.created",
            event_version=EventVersion(major=1),
            correlation_id=metadata.correlation_id,
            trace_id=metadata.trace_id,
            tenant_id="tenant-1",
            occurred_at=datetime(2026, 1, 1),
            source_service="identity-service",
            payload={},
        )


def test_event_context_copies_observability_ids_and_requires_tenant() -> None:
    request = RequestContext(tenant_id="tenant-1")
    trace = TraceContext()
    context = EventContext.from_observability(request, trace)

    assert context.tenant_id == "tenant-1"
    assert context.correlation_id == request.correlation_id
    assert context.trace_id == trace.trace_id
    assert context.correlation.request_id == str(request.request_id)
    assert context.trace_context.span_id == trace.span_id
    assert context.trace_context.sampled is trace.sampled
    metadata = context.to_metadata(source_service="identity-service")
    assert metadata.trace_context.span_id == trace.span_id
    correlation = EventCorrelation.from_request_context(request)
    assert correlation.correlation_id == request.correlation_id
    assert correlation.request_id == str(request.request_id)
    event_trace = EventTraceContext.from_trace_context(trace)
    assert event_trace.to_trace_context() == trace
    with pytest.raises(ValueError, match="tenant_id"):
        EventContext.from_observability(RequestContext())


def test_domain_event_maps_to_allowlisted_envelope_and_structured_log(
    capsys: pytest.CaptureFixture[str],
) -> None:
    from shared.kernel import DomainEvent
    from shared.observability.logging.structured_logger import StructuredLogger

    request = RequestContext(tenant_id="tenant-1")
    trace = TraceContext()
    context = EventContext.from_observability(request, trace)
    domain_event = DomainEvent()
    event = EventEnvelope.from_domain_event(
        domain_event,
        event_type="identity.user.created",
        event_version=EventVersion(major=1),
        context=context,
        source_service="identity-service",
        payload={"user_id": "user-1"},
    )

    assert event.event_id == domain_event.event_id
    assert event.occurred_at == domain_event.occurred_at
    assert event.correlation_id == request.correlation_id
    assert event.trace_id == trace.trace_id
    assert event.span_id == trace.span_id
    assert event.payload == {"user_id": "user-1"}

    event.log(StructuredLogger("event-test", request_context=request))
    logged = capsys.readouterr().out
    assert "identity.user.created" in logged
    assert str(event.correlation_id) in logged
    assert str(event.trace_id) in logged
    assert "user-1" not in logged


def test_naming_convention_accepts_only_three_lowercase_segments() -> None:
    assert EventNamingConvention.is_valid("identity.user.created")
    assert EventNamingConvention.validate("oauth-client.client.revoked")
    assert not EventNamingConvention.is_valid("Identity.user.created")
    assert not EventNamingConvention.is_valid("identity.created")
    assert not EventNamingConvention.is_valid("identity.user.created.v1")


def test_registry_resolves_exact_event_and_schema_version() -> None:
    registry = EventRegistry()
    registry.register(FAKE_EVENT_TYPE, FAKE_EVENT_VERSION, FakeUserCreatedPayload)

    assert registry.resolve(FAKE_EVENT_TYPE, FAKE_EVENT_VERSION) is FakeUserCreatedPayload
    with pytest.raises(EventValidationException, match="already registered"):
        registry.register(FAKE_EVENT_TYPE, FAKE_EVENT_VERSION, FakeUserCreatedPayload)
    with pytest.raises(EventValidationException, match="No schema registered"):
        registry.resolve(FAKE_EVENT_TYPE, EventVersion(major=2))
    with pytest.raises(EventValidationException, match="Event type must follow"):
        registry.register("bad-name", FAKE_EVENT_VERSION, FakeUserCreatedPayload)
    assert (
        EventTypeResolver(registry).resolve(FAKE_EVENT_TYPE, FAKE_EVENT_VERSION)
        is FakeUserCreatedPayload
    )


def test_registry_rejects_schemas_that_allow_unlisted_fields() -> None:
    class UnsafePayload(BaseModel):
        user_id: str

    with pytest.raises(EventValidationException, match="forbid undeclared"):
        EventRegistry().register(
            "identity.user.created",
            EventVersion(major=1),
            UnsafePayload,
        )

    class NestedPayload(BaseModel):
        identity: UnsafePayload

        model_config = ConfigDict(extra="forbid")

    with pytest.raises(EventValidationException, match="forbid undeclared"):
        EventRegistry().register(
            "identity.user.created",
            EventVersion(major=1),
            NestedPayload,
        )


def test_additive_minor_version_keeps_the_previous_schema_usable() -> None:
    class UserCreatedV1(BaseModel):
        model_config = ConfigDict(extra="forbid")

        user_id: str

    class UserCreatedV1_1(BaseModel):
        model_config = ConfigDict(extra="forbid")

        user_id: str
        display_name: str | None = None

    registry = EventRegistry()
    v1 = EventVersion(major=1)
    v1_1 = EventVersion(major=1, minor=1)
    registry.register("identity.user.created", v1, UserCreatedV1)
    registry.register("identity.user.created", v1_1, UserCreatedV1_1)

    assert registry.resolve("identity.user.created", v1) is UserCreatedV1
    assert registry.resolve("identity.user.created", v1_1) is UserCreatedV1_1
    validated = EventSchemaValidator(registry).validate(
        make_event(
            event_version=v1_1,
            payload={"user_id": "user-1"},
        )
    )
    assert isinstance(validated, UserCreatedV1_1)
    assert validated.display_name is None


def test_schema_validator_returns_typed_payload_and_rejects_invalid_data() -> None:
    registry = EventRegistry()
    registry.register("identity.user.created", EventVersion(major=1), Payload)
    validator = EventSchemaValidator(registry)

    validated = validator.validate(make_event(payload={"user_id": "user-1"}))
    assert isinstance(validated, Payload)
    assert validated.user_id == "user-1"
    with pytest.raises(EventValidationException, match="does not match"):
        validator.validate(make_event(payload={"password": "do-not-leak"}))
    with pytest.raises(EventValidationException, match="No schema registered"):
        validator.validate(make_event(event_version=EventVersion(major=2)))
    forged = make_event().model_copy(update={"tenant_id": " "})
    with pytest.raises(EventValidationException, match="Event envelope is invalid"):
        validator.validate(forged)


def test_json_serializer_and_deserializer_round_trip_registered_event() -> None:
    event = make_fake_user_created_event()
    registry = make_fake_event_registry()
    validator = EventSchemaValidator(registry)
    serializer = JsonEventSerializer(validator)
    deserializer = EventDeserializer(validator)

    serialized = serializer.serialize(event)
    deserialized = deserializer.deserialize(serialized)

    assert b'"event_version":"1.0.0"' in serialized
    assert deserialized == event


@pytest.mark.parametrize(
    ("payload", "error_type", "message"),
    [
        (b"\xff", EventSerializationException, "UTF-8 JSON"),
        (b"{", EventSerializationException, "UTF-8 JSON"),
        (b"[]", EventSerializationException, "must be an object"),
        (b'{"key":1,"key":2}', EventSerializationException, "duplicate"),
        (b'{"value":NaN}', EventSerializationException, "numeric constant"),
        (b'{"event_type":"identity.user.created"}', EventValidationException, "envelope"),
    ],
)
def test_deserializer_rejects_invalid_json_and_envelopes(
    payload: bytes, error_type: type[Exception], message: str
) -> None:
    deserializer = EventDeserializer(EventSchemaValidator(make_fake_event_registry()))

    with pytest.raises(error_type, match=message):
        deserializer.deserialize(payload)


def test_deserializer_rejects_unregistered_or_invalid_payload_schema() -> None:
    validator = EventSchemaValidator(make_fake_event_registry())
    deserializer = EventDeserializer(validator)
    event = make_fake_user_created_event()

    unknown = event.model_copy(update={"event_type": "identity.user.updated"})
    with pytest.raises(EventValidationException, match="No schema registered"):
        deserializer.deserialize(
            json.dumps(unknown.model_dump(mode="json")).encode("utf-8")
        )

    invalid = event.model_copy(update={"payload": {"secret": "redact-me"}})
    with pytest.raises(EventValidationException, match="does not match"):
        deserializer.deserialize(
            json.dumps(invalid.model_dump(mode="json")).encode("utf-8")
        )


def test_serializer_rejects_values_that_are_not_json_serializable() -> None:
    class TemperaturePayload(BaseModel):
        model_config = ConfigDict(extra="forbid")

        temperature: float

    registry = EventRegistry()
    registry.register("sensor.temperature.recorded", EventVersion(major=1), TemperaturePayload)
    serializer = JsonEventSerializer(EventSchemaValidator(registry))
    event = make_event(
        event_type="sensor.temperature.recorded",
        payload={"temperature": float("nan")},
    )

    with pytest.raises(EventSerializationException, match="valid JSON"):
        serializer.serialize(event)

    class ArbitraryPayload(BaseModel):
        model_config = ConfigDict(extra="forbid")

        value: Any

    arbitrary_registry = EventRegistry()
    arbitrary_registry.register(
        "sensor.payload.recorded",
        EventVersion(major=1),
        ArbitraryPayload,
    )
    arbitrary_serializer = JsonEventSerializer(
        EventSchemaValidator(arbitrary_registry)
    )
    non_string_key = make_event(
        event_type="sensor.payload.recorded",
        payload={"value": {1: "invalid-json-object-key"}},
    )
    with pytest.raises(EventSerializationException, match="keys must be strings"):
        arbitrary_serializer.serialize(non_string_key)

    nested_non_finite = make_event(
        event_type="sensor.payload.recorded",
        payload={"value": [float("inf")]},
    )
    with pytest.raises(EventSerializationException, match="non-finite number"):
        arbitrary_serializer.serialize(nested_non_finite)


def test_exception_hierarchy_and_classifications_are_stable() -> None:
    error = EventSerializationException("encoding failed")

    assert isinstance(error, EventException)
    assert error.code == "EVENT_SERIALIZATION_ERROR"
    assert EventCategory.INTEGRATION.value == "integration"
    assert EventPriority.CRITICAL > EventPriority.NORMAL


def test_contract_protocols_and_testing_factories_are_available() -> None:
    event = make_event()

    assert isinstance(event, EventEnvelope)
    assert EventContract.__name__ == "EventContract"
    assert DomainEventContract.__name__ == "DomainEventContract"
    assert IntegrationEventContract.__name__ == "IntegrationEventContract"
    assert EventPublisherContract.__name__ == "EventPublisherContract"
    assert EventSubscriberContract.__name__ == "EventSubscriberContract"
    assert EventHandlerContract.__name__ == "EventHandlerContract"
    assert LegacyEventSerializer.__name__ == "EventSerializer"
    assert make_fake_event_registry().resolve(
        FAKE_EVENT_TYPE, FAKE_EVENT_VERSION
    ) is FakeUserCreatedPayload
