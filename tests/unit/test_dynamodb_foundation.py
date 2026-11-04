from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pytest
from botocore.config import Config  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]

from shared.aws.factories.aws_client_factory import AwsClientFactory
from shared.aws.factories.aws_session_factory import AwsSessionFactory
from shared.aws.observability.aws_observability import AwsObservability
from shared.aws.settings.aws_settings import AwsSettings
from shared.aws.testing.fake_clients import FakeSession
from shared.dynamodb.context.dynamodb_context import DynamoDbContext
from shared.dynamodb.exceptions.dynamodb_connection_exception import (
    DynamoDbConnectionException,
)
from shared.dynamodb.exceptions.dynamodb_exception import DynamoDbException
from shared.dynamodb.exceptions.dynamodb_serialization_exception import (
    DynamoDbSerializationException,
)
from shared.dynamodb.factories.dynamodb_client_factory import DynamoDbClientFactory
from shared.dynamodb.factories.dynamodb_resource_factory import DynamoDbResourceFactory
from shared.dynamodb.factories.dynamodb_table_factory import DynamoDbTableFactory
from shared.dynamodb.keys.dynamodb_key_builder import DynamoDbKeyBuilder
from shared.dynamodb.keys.partition_key_builder import TenantAwarePartitionKeyBuilder
from shared.dynamodb.keys.sort_key_builder import TenantAwareSortKeyBuilder
from shared.dynamodb.metadata.metadata_support import MetadataSupport
from shared.dynamodb.metadata.ttl_support import TtlSupport
from shared.dynamodb.metadata.version_support import VersionSupport
from shared.dynamodb.observability.dynamodb_observability import DynamoDbObservability
from shared.dynamodb.providers.dynamodb_table_provider import DynamoDbTableProvider
from shared.dynamodb.serialization.dynamodb_deserializer import DynamoDbDeserializer
from shared.dynamodb.serialization.dynamodb_serializer import DynamoDbSerializer
from shared.dynamodb.settings.dynamodb_settings import DynamoDbSettings
from shared.dynamodb.testing.fake_dynamodb import FakeDynamoDbResource
from shared.dynamodb.validation.dynamodb_connection_validator import (
    DynamoDbConnectionValidator,
)
from shared.dynamodb.validation.dynamodb_health_check import DynamoDbHealthCheck


class FakeHealthClient:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def describe_table(self, **kwargs: Any) -> dict[str, Any]:
        return self._respond("describe_table", kwargs)

    def list_tables(self, **kwargs: Any) -> dict[str, Any]:
        return self._respond("list_tables", kwargs)

    def _respond(self, operation: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((operation, kwargs))
        if self.error is not None:
            raise self.error
        return {}


def test_dynamodb_settings_normalize_optional_values_and_validate_timeouts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AUTHENTICATOR_DYNAMODB_ENDPOINT_URL", " http://localhost:8000 ")
    settings = DynamoDbSettings(region_name=" eu-west-1 ", table_name=" items ")

    assert settings.endpoint_url == "http://localhost:8000"
    assert settings.region_name == "eu-west-1"
    assert settings.table_name == "items"
    with pytest.raises(ValueError):
        DynamoDbSettings(connect_timeout_seconds=0)


def test_context_exposes_only_non_sensitive_log_fields() -> None:
    context = DynamoDbContext(
        tenant_id="tenant-1",
        request_id="request-1",
        metadata={"private": "not logged"},
    )

    assert context.as_log_fields()["tenant_id"] == "tenant-1"
    assert "metadata" not in context.as_log_fields()


def test_client_and_resource_factories_use_aws_foundation() -> None:
    settings = DynamoDbSettings(
        region_name="eu-west-1",
        endpoint_url="http://localhost:8000",
    )

    class RecordingAwsFactory:
        def __init__(self) -> None:
            self.client_args: tuple[str, dict[str, Any]] | None = None
            self.resource_args: tuple[str, dict[str, Any]] | None = None

        def create_client(
            self,
            service_name: str,
            *,
            region_name: str | None = None,
            endpoint_url: str | None = None,
            config: Config | None = None,
        ) -> object:
            self.client_args = (
                service_name,
                {
                    "region_name": region_name,
                    "endpoint_url": endpoint_url,
                    "config": config,
                },
            )
            return object()

        def create_resource(
            self,
            service_name: str,
            *,
            region_name: str | None = None,
            endpoint_url: str | None = None,
            config: Config | None = None,
        ) -> FakeDynamoDbResource:
            self.resource_args = (
                service_name,
                {
                    "region_name": region_name,
                    "endpoint_url": endpoint_url,
                    "config": config,
                },
            )
            return FakeDynamoDbResource()

    aws_factory = RecordingAwsFactory()
    client = DynamoDbClientFactory(aws_factory, settings=settings)
    resource = DynamoDbResourceFactory(aws_factory, settings=settings)
    assert client.create() is not None
    assert isinstance(resource.create(), FakeDynamoDbResource)
    assert aws_factory.client_args is not None
    assert aws_factory.client_args[0] == "dynamodb"
    assert aws_factory.client_args[1]["endpoint_url"] == "http://localhost:8000"
    assert aws_factory.resource_args is not None
    assert aws_factory.resource_args[0] == "dynamodb"


def test_aws_client_factory_creates_resource_using_injected_session() -> None:
    factory = AwsClientFactory(
        session_factory=AwsSessionFactory(),
        settings=AwsSettings(),
    )

    resource = factory.create_resource("dynamodb", session=FakeSession())

    assert isinstance(resource, FakeDynamoDbResource)


def test_table_factory_and_provider_reuse_observed_table_handles() -> None:
    resource = FakeDynamoDbResource()

    class ResourceFactory:
        def create(self) -> FakeDynamoDbResource:
            return resource

    factory = DynamoDbTableFactory(ResourceFactory())  # type: ignore[arg-type]
    provider = DynamoDbTableProvider(
        factory,
        settings=DynamoDbSettings(table_name="items"),
        observability=DynamoDbObservability(AwsObservability(service_name="test")),
    )

    table = provider.get_table()
    assert table is provider.get_table("items")
    assert table.name == "items"
    assert table.put_item(Item={"id": "1"})["operation"] == "put_item"
    with pytest.raises(DynamoDbException):
        factory.create(" ")


def test_table_provider_requires_table_name() -> None:
    with pytest.raises(DynamoDbException):
        DynamoDbTableProvider(settings=DynamoDbSettings()).get_table()


def test_table_provider_passes_settings_to_its_default_resource_factory() -> None:
    settings = DynamoDbSettings(
        region_name="eu-west-1",
        endpoint_url="http://localhost:8000",
        table_name="items",
    )
    provider = DynamoDbTableProvider(settings=settings)

    assert provider._table_factory._resource_factory.settings is settings


def test_tenant_key_builders_require_nonempty_identifiers() -> None:
    assert TenantAwarePartitionKeyBuilder().build(" tenant-4 ") == "TENANT#tenant-4"
    assert TenantAwareSortKeyBuilder().build("session-2") == "ENTITY#session-2"
    assert DynamoDbKeyBuilder().build("tenant-4", "session-2") == {
        "PK": "TENANT#tenant-4",
        "SK": "ENTITY#session-2",
    }
    with pytest.raises(DynamoDbException):
        DynamoDbKeyBuilder().build(" ", "session-2")
    with pytest.raises(DynamoDbException):
        DynamoDbKeyBuilder().build("tenant-4", "")


def test_serializer_round_trips_nested_values_and_normalizes_float() -> None:
    serializer = DynamoDbSerializer()
    encoded = serializer.serialize(
        {"amount": 2.5, "nested": {"values": [True, "text"]}, "tags": {"a", "b"}}
    )
    decoded = DynamoDbDeserializer().deserialize(encoded)

    assert decoded["amount"] == Decimal("2.5")
    assert decoded["nested"] == {"values": [True, "text"]}
    assert decoded["tags"] == {"a", "b"}


def test_serializer_raises_domain_exception_for_unsupported_value() -> None:
    with pytest.raises(DynamoDbSerializationException):
        DynamoDbSerializer().serialize({"invalid": object()})
    with pytest.raises(DynamoDbSerializationException):
        DynamoDbDeserializer().deserialize({"invalid": {"UNKNOWN": "x"}})


def test_ttl_requires_timezone_aware_expiration_and_returns_copy() -> None:
    item = {"PK": "TENANT#one"}
    result = TtlSupport().add_ttl(item, datetime(2030, 1, 1, tzinfo=UTC))

    assert item == {"PK": "TENANT#one"}
    assert result["ttl"] == 1_893_456_000
    with pytest.raises(DynamoDbException):
        TtlSupport().add_ttl(item, datetime(2030, 1, 1))


def test_version_support_initializes_and_increments() -> None:
    support = VersionSupport()
    assert support.initialize({"PK": "x"}) == {"PK": "x", "version": 1}
    assert support.next_version(1) == 2
    with pytest.raises(DynamoDbException):
        support.initialize({"version": 2})
    with pytest.raises(DynamoDbException):
        support.next_version(0)


def test_metadata_support_adds_timestamps_and_preserves_existing_metadata() -> None:
    now = datetime(2030, 1, 1, tzinfo=UTC)
    original = {"metadata": {"existing": "value"}}
    result = MetadataSupport().add_metadata(original, {"source": "test"}, now=now)

    assert result["metadata"] == {"existing": "value", "source": "test"}
    assert result["created_at"] == "2030-01-01T00:00:00+00:00"
    assert result["updated_at"] == result["created_at"]
    assert original == {"metadata": {"existing": "value"}}
    with pytest.raises(DynamoDbException):
        MetadataSupport().add_metadata({}, {"version": 2})
    with pytest.raises(DynamoDbException):
        MetadataSupport().add_metadata({}, {}, now=datetime(2030, 1, 1))


def test_health_check_selects_non_data_validation_operation() -> None:
    client = FakeHealthClient()

    assert DynamoDbHealthCheck(client, settings=DynamoDbSettings()).check() is True
    assert client.calls == [("list_tables", {"Limit": 1})]

    client = FakeHealthClient()
    settings = DynamoDbSettings(table_name="items")
    assert DynamoDbHealthCheck(client, settings=settings).check() is True
    assert client.calls == [("describe_table", {"TableName": "items"})]


def test_health_check_wraps_service_errors_and_validator_delegates() -> None:
    error = ClientError({"Error": {"Code": "AccessDeniedException"}}, "ListTables")
    with pytest.raises(DynamoDbConnectionException):
        DynamoDbHealthCheck(FakeHealthClient(error)).check()

    class HealthCheck:
        def check(self) -> bool:
            return True

    assert DynamoDbConnectionValidator(HealthCheck()).validate() is True  # type: ignore[arg-type]


def test_observed_table_logs_all_supported_operations(capsys: pytest.CaptureFixture[str]) -> None:
    resource = FakeDynamoDbResource()

    class ResourceFactory:
        def create(self) -> FakeDynamoDbResource:
            return resource

    table = DynamoDbTableProvider(
        DynamoDbTableFactory(ResourceFactory()),  # type: ignore[arg-type]
        settings=DynamoDbSettings(table_name="items"),
        observability=DynamoDbObservability(
            AwsObservability(service_name="test"),
            context=DynamoDbContext(tenant_id="tenant-safe"),
        ),
    ).get_table()

    table.get_item(Key={"PK": "not-logged"})
    table.put_item(Item={"secret": "not-logged"})
    table.update_item(Key={"PK": "not-logged"})
    table.delete_item(Key={"PK": "not-logged"})
    table.query(KeyConditionExpression="PK = :pk")
    table.scan(Limit=1)

    assert len(resource.Table("items").calls) == 6
    log_output = capsys.readouterr().out
    assert "dynamodb_operation_succeeded" in log_output
    assert "not-logged" not in log_output
    assert "tenant-safe" in log_output


def test_observed_table_logs_failure_and_reraises(capsys: pytest.CaptureFixture[str]) -> None:
    resource = FakeDynamoDbResource()

    class ResourceFactory:
        def create(self) -> FakeDynamoDbResource:
            return resource

    table = DynamoDbTableProvider(
        DynamoDbTableFactory(ResourceFactory()),  # type: ignore[arg-type]
        settings=DynamoDbSettings(table_name="items"),
        observability=DynamoDbObservability(AwsObservability(service_name="test")),
    ).get_table()
    resource.Table("items").error = ValueError("expected failure")

    with pytest.raises(ValueError, match="expected failure"):
        table.get_item(Key={"PK": "not-logged"})
    log_output = capsys.readouterr().out
    assert "dynamodb_operation_failed" in log_output
    assert "not-logged" not in log_output
