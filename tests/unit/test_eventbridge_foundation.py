from __future__ import annotations

import pytest

from shared.eventbus import (
    ArchiveMetadata,
    AuditRecord,
    EventAuditor,
    EventBridgeConnectionValidator,
    EventBridgeHealthCheck,
    EventBridgeProvider,
    EventBridgePublisher,
    EventBridgeSettings,
    EventBusResolver,
    EventFilter,
    EventRouter,
    EventSchemaEnforcer,
    FanoutEngine,
    ReplayMetadata,
    RetryDecision,
    RetryMetadata,
    RetryPolicy,
)
from shared.eventbus.exceptions.eventbridge_exception import EventBridgePublishException
from shared.eventbus.metadata.event_bus_metadata import EventBusMetadata
from shared.eventbus.observability.event_observability import EventObservability
from shared.eventbus.schema.event_contract_schema import EventContractSchema
from shared.eventbus.testing import make_eventbridge_settings
from shared.events.metadata.event_version import EventVersion
from shared.events.testing.fake_events import make_fake_user_created_event


class FakeEventBridgeClient:
    def describe_event_bus(self, **kwargs: object) -> dict[str, object]:
        return {"Name": kwargs["Name"]}

    def put_events(self, **kwargs: object) -> dict[str, object]:
        return {"FailedEntryCount": 0, "Entries": [{"EventId": "eventbridge-1"}]}


class FailingProvider:
    def __init__(self, response: dict[str, object] | None = None) -> None:
        self.response = response

    def put_events(self, _: list[dict[str, object]]) -> dict[str, object]:
        if self.response is None:
            raise RuntimeError("offline")
        return self.response


def make_provider(settings: EventBridgeSettings) -> EventBridgeProvider:
    return EventBridgeProvider(settings, client=FakeEventBridgeClient())


def test_eventbridge_settings_valid_and_invalid() -> None:
    settings = EventBridgeSettings(
        aws_region="us-east-1",
        account_id="123456789012",
        bus_name="shared-event-bus",
        environment="prod",
        archive_enabled=True,
        replay_enabled=True,
    )
    assert settings.aws_region == "us-east-1"
    assert settings.is_local_endpoint is False
    assert str(EventVersion(major=1)) == "1.0.0"

    with pytest.raises(ValueError):
        EventBridgeSettings(aws_region="invalid", account_id="123456789012", bus_name="shared")

    with pytest.raises(ValueError):
        EventBridgeSettings(aws_region="us-east-1", account_id="123", bus_name="shared")

    with pytest.raises(ValueError):
        EventBridgeSettings(aws_region="us-east-1", account_id="123456789012", bus_name="")

    local = EventBridgeSettings(
        aws_region="us-east-1",
        account_id="123456789012",
        bus_name="shared-event-bus",
        endpoint_url="http://localhost:4566",
    )
    assert local.is_local_endpoint is True
    with pytest.raises(ValueError):
        EventBridgeSettings(
            aws_region="us-east-1",
            account_id="123456789012",
            bus_name="shared",
            retention_days=0,
        )
    with pytest.raises(ValueError):
        EventBridgeSettings(
            aws_region="us-east-1",
            account_id="123456789012",
            bus_name="bad bus",
        )
    with pytest.raises(ValueError):
        EventBridgeSettings(
            aws_region="us-east-1",
            account_id="123456789012",
            bus_name="shared",
            environment="bad environment",
        )
    with pytest.raises(ValueError):
        EventBridgeSettings(
            aws_region="us-east-1",
            account_id="123456789012",
            bus_name="shared",
            endpoint_url=" ",
        )
    assert make_eventbridge_settings().archive_enabled is True


def test_event_bus_resolver_and_router() -> None:
    settings = EventBridgeSettings(
        aws_region="us-east-1",
        account_id="123456789012",
        bus_name="shared-event-bus",
    )
    resolver = EventBusResolver(settings)
    bus = resolver.resolve("tenant-1", "identity", "identity.user.created")

    assert isinstance(bus, EventBusMetadata)
    assert bus.bus_name == "shared-event-bus"
    assert bus.tenant_id == "tenant-1"

    router = EventRouter()
    decision = router.route("identity.user.created", bus_name="shared-event-bus")
    assert decision.category == "identity"
    assert decision.routing_mode == "multicast"
    assert "audit" in decision.consumers
    assert (
        EventBusResolver(settings)
        .resolve("tenant-1", "authentication", "authentication.session.started")
        .bus_name
        == "authentication-bus"
    )
    assert (
        EventBusResolver(settings).resolve("tenant-1", "tenant", "tenant.tenant.created").bus_name
        == "tenant-bus"
    )
    with pytest.raises(ValueError):
        EventBusResolver(settings).resolve("", "identity", "identity.user.created")
    assert EventRouter().identify_consumers("other.event.type") == ("audit",)
    assert EventRouter().route("other.event.type").routing_mode == "unicast"


def test_event_filter_matches_multiple_criteria() -> None:
    event = make_fake_user_created_event(
        tenant_id="tenant-42",
        source_service="identity-directory-service",
    )
    gate = EventFilter(
        source="identity-directory-service",
        tenant_id="tenant-42",
        event_type="identity.user.created",
        event_version="1.0.0",
        category="identity",
    )
    assert gate.matches(event)

    assert not EventFilter(tenant_id="tenant-99").matches(event)
    assert not EventFilter(source="other").matches(event)
    assert EventFilter(event_version=EventVersion(major=1)).matches(event)
    assert EventFilter(category="identity").filter_events([event]) == [event]
    assert not EventFilter(event_type="other.event.type").matches(event)
    assert not EventFilter(event_version="2.0.0").matches(event)
    assert not EventFilter(category="other").matches(event)


def test_schema_enforcer_and_publisher_require_mandatory_fields() -> None:
    event = make_fake_user_created_event()
    enforcer = EventSchemaEnforcer()
    assert enforcer.validate(event) is event

    settings = EventBridgeSettings(
        aws_region="us-east-1",
        account_id="123456789012",
        bus_name="shared-event-bus",
    )
    provider = make_provider(settings)
    encrypted: list[bytes] = []

    def encrypt(payload: bytes) -> bytes:
        encrypted.append(payload)
        return b"ciphertext"

    publisher = EventBridgePublisher(
        settings,
        provider=provider,
        payload_encryptor=encrypt,
    )
    result = publisher.publish(event)
    assert result.success is True
    assert result.bus_name == "shared-event-bus"
    assert encrypted
    assert publisher.auditor.records
    assert publisher.last_replay_metadata is not None
    assert publisher.archive_metadata.archive_enabled is False
    assert publisher.last_observability.publish_success is True

    with pytest.raises(ValueError):
        EventSchemaEnforcer().validate("not-an-envelope")
    assert publisher.validate_schema(event) is event
    assert publisher.validate_version(event) is event
    assert publisher.validate_tenant(event) is event
    assert publisher.publish_many([event])[0].success is True
    with pytest.raises(ValueError):
        publisher.publish_raw(payload={}, event=None)


def test_eventbridge_publisher_surfaces_provider_failures() -> None:
    event = make_fake_user_created_event()
    settings = EventBridgeSettings(
        aws_region="us-east-1",
        account_id="123456789012",
        bus_name="shared-event-bus",
    )
    for response in (
        {"FailedEntryCount": 1},
        {"FailedEntryCount": 0, "Entries": []},
        {"FailedEntryCount": 0, "Entries": [{}]},
    ):
        publisher = EventBridgePublisher(settings, provider=FailingProvider(response))  # type: ignore[arg-type]
        with pytest.raises(EventBridgePublishException):
            publisher.publish(event)
    publisher = EventBridgePublisher(settings, provider=FailingProvider())  # type: ignore[arg-type]
    with pytest.raises(EventBridgePublishException):
        publisher.publish(event)


def test_fanout_and_retry_and_audit() -> None:
    event = make_fake_user_created_event()
    fanout = FanoutEngine()
    assert fanout.fanout(event, ["audit", "notification"]) == {
        "audit": "identity.user.created",
        "notification": "identity.user.created",
    }
    assert fanout.distribute(event, ["audit"]) == [("audit", "identity.user.created")]

    retry = RetryPolicy(max_attempts=3, base_delay_seconds=1, max_delay_seconds=10)
    decision = retry.evaluate(RuntimeError("transient"), RetryMetadata(attempt=2, max_attempts=3))
    assert isinstance(decision, RetryDecision)
    assert decision.should_retry is True
    assert decision.should_dead_letter is False

    auditor = EventAuditor()
    record = auditor.audit(event)
    assert isinstance(record, AuditRecord)
    assert record.tenant_id == "tenant-test"

    archive = ArchiveMetadata(archive_enabled=True, retention_days=90)
    replay = ReplayMetadata(
        event_id=str(event.event_id),
        event_type=event.event_type,
        version="1.0.0",
        timestamp="2026-01-01T00:00:00Z",
        tenant=event.tenant_id,
    )
    assert archive.archive_enabled is True
    assert replay.tenant == "tenant-test"
    assert EventObservability().to_dict()["publish_success"] is True
    with pytest.raises(ValueError):
        RetryPolicy(jitter_ratio=2)
    assert (
        RetryPolicy(max_attempts=1)
        .evaluate(RuntimeError("permanent"), RetryMetadata(attempt=1))
        .should_dead_letter
        is True
    )


def test_provider_schema_and_publisher_failures() -> None:
    settings = EventBridgeSettings(
        aws_region="us-east-1",
        account_id="123456789012",
        bus_name="shared-event-bus",
    )
    client = FakeEventBridgeClient()
    provider = make_provider(settings)
    assert provider.get_bus_name() == "shared-event-bus"
    assert provider.describe_bus()["Name"] == "shared-event-bus"
    assert provider.put_events([{"Detail": "{}"}])["FailedEntryCount"] == 0

    schema = EventContractSchema("identity.user.created", "1.0.0")
    schema.validate(tenant_id="tenant", correlation_id="correlation", trace_id="trace")
    with pytest.raises(ValueError):
        schema.validate(tenant_id="", correlation_id="correlation", trace_id="trace")
    with pytest.raises(ValueError):
        EventContractSchema("", "1.0.0").validate(
            tenant_id="tenant", correlation_id="correlation", trace_id="trace"
        )
    with pytest.raises(ValueError):
        EventContractSchema("identity.user.created", "").validate(
            tenant_id="tenant", correlation_id="correlation", trace_id="trace"
        )
    with pytest.raises(ValueError):
        schema.validate(tenant_id="tenant", correlation_id="", trace_id="trace")
    with pytest.raises(ValueError):
        schema.validate(tenant_id="tenant", correlation_id="correlation", trace_id="")

    class FailedClient(FakeEventBridgeClient):
        def put_events(self, **kwargs: object) -> dict[str, object]:
            return {"FailedEntryCount": 1, "Entries": [{"ErrorCode": "InternalFailure"}]}

    publisher = EventBridgePublisher(
        settings,
        provider=EventBridgeProvider(settings, client=FailedClient()),
    )
    with pytest.raises(EventBridgePublishException):
        publisher.publish(make_fake_user_created_event())
    assert client.describe_event_bus(Name="shared-event-bus")["Name"] == "shared-event-bus"

    class EmptyClient(FakeEventBridgeClient):
        def put_events(self, **kwargs: object) -> dict[str, object]:
            return {"FailedEntryCount": 0, "Entries": []}

    with pytest.raises(EventBridgePublishException):
        EventBridgePublisher(
            settings,
            provider=EventBridgeProvider(settings, client=EmptyClient()),
        ).publish(make_fake_user_created_event())


def test_health_check_and_connection_validator() -> None:
    settings = EventBridgeSettings(
        aws_region="us-east-1",
        account_id="123456789012",
        bus_name="shared-event-bus",
    )
    provider = make_provider(settings)
    health = EventBridgeHealthCheck(settings, provider=provider)
    assert health.check().status.value == "Healthy"

    validator = EventBridgeConnectionValidator(settings, provider=provider)
    assert validator.validate() is True
    assert validator.is_connected() is True

    class BrokenClient(FakeEventBridgeClient):
        def describe_event_bus(self, **kwargs: object) -> dict[str, object]:
            return {"Name": "other-bus"}

    degraded = EventBridgeHealthCheck(
        settings,
        provider=EventBridgeProvider(settings, client=BrokenClient()),
    )
    assert degraded.check().status.value == "Degraded"
