from __future__ import annotations

import asyncio
import base64
from typing import Any

import pytest
from botocore.exceptions import ClientError  # type: ignore[import-untyped]
from pydantic import ValidationError

from shared.aws.factories.aws_client_factory import AwsClientFactory
from shared.events.exceptions.event_exception import EventException
from shared.events.serialization.event_deserializer import EventDeserializer
from shared.events.serialization.event_serializer import JsonEventSerializer
from shared.events.testing.fake_events import (
    FAKE_EVENT_TYPE,
    make_fake_event_registry,
    make_fake_user_created_event,
)
from shared.events.validation.schema_validator import EventSchemaValidator
from shared.kms.exceptions.kms_encryption_exception import KmsEncryptionException
from shared.kms.resolver.kms_key_resolver import KmsKeyResolver
from shared.kms.settings.kms_settings import KmsSettings
from shared.messaging.consumers.sqs_message_consumer import SqsMessageConsumer
from shared.messaging.dlq.dead_letter_metadata import DeadLetterMetadata
from shared.messaging.dlq.dead_letter_policy import DeadLetterPolicy
from shared.messaging.encryption.kms_message_encryption import KmsMessageEncryption
from shared.messaging.exceptions.sqs_exception import (
    IdempotencyException,
    MessageConsumeException,
    MessagePublishException,
    SqsConfigurationException,
    SqsException,
)
from shared.messaging.handlers.message_dispatcher import MessageDispatcher
from shared.messaging.idempotency.dynamodb_idempotency_store import DynamoDbIdempotencyStore
from shared.messaging.idempotency.idempotency_key import IdempotencyKey
from shared.messaging.idempotency.idempotency_validator import (
    IdempotencyValidator,
)
from shared.messaging.models.consumed_message import ConsumedMessage
from shared.messaging.models.publish_result import PublishResult
from shared.messaging.providers.aws_sqs_provider import AwsSqsProvider
from shared.messaging.publishers.sqs_message_publisher import SqsMessagePublisher
from shared.messaging.queues.queue_metadata import QueueMetadata
from shared.messaging.queues.queue_resolver import QueueResolver
from shared.messaging.retry.retry_metadata import RetryMetadata
from shared.messaging.retry.retry_policy import RetryPolicy
from shared.messaging.settings.sqs_settings import SqsSettings
from shared.messaging.testing.factories import (
    build_fake_sqs_provider,
    build_queue_metadata,
    build_sqs_settings,
)
from shared.messaging.testing.fake_sqs import FakeSqsProvider as FakeProvider
from shared.messaging.testing.fixtures import sqs_settings_fixture
from shared.messaging.validation.sqs_connection_validator import SqsConnectionValidator
from shared.messaging.validation.sqs_health_check import HealthStatus, SqsHealthCheck


def make_settings(**overrides: object) -> SqsSettings:
    values: dict[str, Any] = {
        "aws_region": "us-east-1",
        "account_id": "123456789012",
        "queue_prefix": "auth",
        "environment": "test",
    }
    values.update(overrides)
    return SqsSettings(**values)


def make_event_validator() -> EventSchemaValidator:
    return EventSchemaValidator(make_fake_event_registry())


def make_queue(fifo: bool = False) -> QueueMetadata:
    return QueueMetadata(
        bounded_context="identity",
        event_type=FAKE_EVENT_TYPE,
        queue_name=f"auth-test-identity-events{'.fifo' if fifo else ''}",
        fifo=fifo,
    )


class FakeIdempotencyStore:
    def __init__(self) -> None:
        self.claimed: dict[str, str] = {}
        self.completed: set[str] = set()

    def claim(self, key: IdempotencyKey) -> str | None:
        if key.value in self.claimed or key.value in self.completed:
            return None
        token = f"claim-{key.value}"
        self.claimed[key.value] = token
        return token

    def complete(self, key: IdempotencyKey, *, claim_token: str) -> None:
        assert self.claimed.pop(key.value) == claim_token
        self.completed.add(key.value)

    def release(self, key: IdempotencyKey, *, claim_token: str) -> None:
        assert self.claimed.pop(key.value) == claim_token


class FakeDynamoTable:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.failure: tuple[str, str] | None = None

    def _record(self, operation: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((operation, kwargs))
        if self.failure is not None and self.failure[0] == operation:
            raise ClientError(
                {"Error": {"Code": self.failure[1]}},
                operation,
            )
        return {}

    def put_item(self, **kwargs: Any) -> dict[str, Any]:
        return self._record("put_item", kwargs)

    def update_item(self, **kwargs: Any) -> dict[str, Any]:
        return self._record("update_item", kwargs)

    def delete_item(self, **kwargs: Any) -> dict[str, Any]:
        return self._record("delete_item", kwargs)


class FakeSqsClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.queue_urls = [
            "https://sqs.us-east-1.amazonaws.com/123456789012/auth-test-identity-events"
        ]
        self.queue_arn = "arn:aws:sqs:us-east-1:123456789012:auth-test-identity-events"
        self.pages = 0

    def list_queues(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("list_queues", kwargs))
        self.pages += 1
        if kwargs.get("NextToken") == "page-2":
            return {"QueueUrls": self.queue_urls}
        return {"QueueUrls": [], "NextToken": "page-2"}

    def get_queue_attributes(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("get_queue_attributes", kwargs))
        return {"Attributes": {"QueueArn": self.queue_arn, "ApproximateNumberOfMessages": "0"}}

    def send_message(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("send_message", kwargs))
        return {"MessageId": "id-1"}

    def receive_message(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("receive_message", kwargs))
        return {"Messages": []}

    def delete_message(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("delete_message", kwargs))
        return {}


class FakeAwsClientFactory(AwsClientFactory):
    def __init__(self, client: FakeSqsClient) -> None:
        self.client = client
        self.options: dict[str, Any] = {}

    def create_client(
        self,
        service_name: str,
        *,
        region_name: str | None = None,
        endpoint_url: str | None = None,
        session: Any = None,
        config: Any = None,
    ) -> FakeSqsClient:
        self.options = {
            "service_name": service_name,
            "region_name": region_name,
            "endpoint_url": endpoint_url,
        }
        return self.client


class FakeKms:
    def __init__(self) -> None:
        self.context: dict[str, str] = {}
        self.fail_encrypt = False
        self.fail_decrypt = False

    def describe_key(self, *, key_id: str) -> dict[str, Any]:
        return {
            "KeyMetadata": {
                "KeyId": "key-123",
                "Arn": "arn:aws:kms:us-east-1:123456789012:key/key-123",
                "KeyUsage": "ENCRYPT_DECRYPT",
                "KeyState": "Enabled",
            }
        }

    def encrypt(
        self, *, key_id: str, plaintext: bytes, encryption_context: dict[str, str]
    ) -> dict[str, Any]:
        if self.fail_encrypt:
            raise ClientError({"Error": {"Code": "InternalException"}}, "Encrypt")
        self.context = encryption_context
        return {"CiphertextBlob": bytes(reversed(plaintext))}

    def decrypt(self, *, ciphertext: bytes, encryption_context: dict[str, str]) -> dict[str, Any]:
        if self.fail_decrypt:
            raise ClientError({"Error": {"Code": "InternalException"}}, "Decrypt")
        assert encryption_context == self.context
        return {"Plaintext": bytes(reversed(ciphertext))}

    def generate_data_key(self, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def sign(self, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def verify(self, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


def test_settings_validate_required_values_and_limits() -> None:
    settings = make_settings(default_wait_time=0, default_visibility_timeout=43200)
    assert settings.endpoint_url is None
    assert make_settings(endpoint_url="http://localhost:4566").endpoint_url
    for invalid in (
        {"aws_region": "invalid"},
        {"account_id": "123"},
        {"queue_prefix": " "},
        {"environment": ""},
        {"default_wait_time": 21},
        {"default_visibility_timeout": 0},
        {"default_max_receive_count": 0},
        {"endpoint_url": " "},
    ):
        with pytest.raises((SqsConfigurationException, ValidationError)):
            make_settings(**invalid)


def test_testing_factories_build_isolated_messaging_fixtures() -> None:
    assert build_sqs_settings(queue_prefix="unit").queue_prefix == "unit"
    assert sqs_settings_fixture(environment="ci").environment == "ci"
    assert build_queue_metadata(queue_name="test-queue").queue_name == "test-queue"
    provider = build_fake_sqs_provider()
    assert isinstance(provider, FakeProvider)
    assert provider.list_queues(name_prefix="test") == [
        "https://sqs.us-east-1.amazonaws.com/123456789012/test"
    ]


def test_queue_resolver_maps_routes_prefixes_and_fifo_names() -> None:
    resolver = QueueResolver(make_settings())
    assert resolver.resolve("tenant", "tenant-created").queue_name == "auth-test-tenant-events"
    assert resolver.resolve("identity", "user-created").queue_name == "auth-test-identity-events"
    assert resolver.resolve("identity", FAKE_EVENT_TYPE).queue_name == "auth-test-identity-events"
    assert (
        QueueResolver(make_settings(), fifo=True).resolve("identity", FAKE_EVENT_TYPE).queue_name
        == "auth-test-identity-events.fifo"
    )
    with pytest.raises(SqsConfigurationException):
        resolver.resolve("unknown", "unmapped")


def test_aws_sqs_provider_resolves_queue_paginates_and_uses_only_allowed_calls() -> None:
    client = FakeSqsClient()
    factory = FakeAwsClientFactory(client)
    provider = AwsSqsProvider(make_settings(), factory)
    queue = make_queue()

    response = provider.send_message(
        queue,
        body="{}",
        attributes={},
    )
    assert response["MessageId"] == "id-1"
    assert factory.options["service_name"] == "sqs"
    assert client.pages == 2
    assert [name for name, _ in client.calls].count("get_queue_attributes") == 1
    assert client.calls[-1][0] == "send_message"
    assert (
        provider.receive_messages(
            queue,
            max_number=10,
            wait_time=20,
            visibility_timeout=30,
        )
        == []
    )
    provider.delete_message(queue, receipt_handle="receipt")
    assert provider.get_queue_attributes(queue)["QueueArn"] == client.queue_arn
    assert provider.list_queues(name_prefix="auth-test")
    fifo_client = FakeSqsClient()
    fifo_client.queue_urls = [
        "https://sqs.us-east-1.amazonaws.com/123456789012/auth-test-identity-events.fifo"
    ]
    fifo_client.queue_arn = "arn:aws:sqs:us-east-1:123456789012:auth-test-identity-events.fifo"
    fifo_provider = AwsSqsProvider(make_settings(), FakeAwsClientFactory(fifo_client))
    fifo_provider.send_message(
        make_queue(fifo=True),
        body="{}",
        attributes={},
    )
    send_args = [call for name, call in fifo_client.calls if name == "send_message"][0]
    assert send_args["MessageGroupId"] == "identity"
    assert send_args["MessageDeduplicationId"] == FAKE_EVENT_TYPE


def test_aws_sqs_provider_rejects_wrong_queue_identity_and_sdk_failures() -> None:
    client = FakeSqsClient()
    client.queue_arn = "arn:aws:sqs:us-east-1:999999999999:auth-test-identity-events"
    provider = AwsSqsProvider(make_settings(), FakeAwsClientFactory(client))
    with pytest.raises(SqsException, match="outside the configured"):
        provider.send_message(make_queue(), body="{}", attributes={})

    failing = FakeSqsClient()

    def fail_list(**kwargs: Any) -> dict[str, Any]:
        raise ClientError({"Error": {"Code": "AccessDenied"}}, "ListQueues")

    failing.list_queues = fail_list  # type: ignore[method-assign]
    with pytest.raises(SqsException, match="list_queues"):
        AwsSqsProvider(make_settings(), FakeAwsClientFactory(failing)).list_queues(
            name_prefix="auth"
        )


def test_aws_sqs_provider_audits_operation_failures_and_invalid_responses() -> None:
    queue = make_queue()
    client = FakeSqsClient()
    provider = AwsSqsProvider(make_settings(), FakeAwsClientFactory(client))

    def sdk_failure(**kwargs: Any) -> dict[str, Any]:
        raise ClientError({"Error": {"Code": "AccessDenied"}}, "SendMessage")

    client.send_message = sdk_failure  # type: ignore[method-assign]
    with pytest.raises(SqsException, match="send_message"):
        provider.send_message(queue, body="{}", attributes={})

    client = FakeSqsClient()
    provider = AwsSqsProvider(make_settings(), FakeAwsClientFactory(client))

    def receive_failure(**kwargs: Any) -> dict[str, Any]:
        raise ClientError({"Error": {"Code": "AccessDenied"}}, "ReceiveMessage")

    client.receive_message = receive_failure  # type: ignore[method-assign]
    with pytest.raises(SqsException, match="receive_message"):
        provider.receive_messages(
            queue,
            max_number=1,
            wait_time=1,
            visibility_timeout=30,
        )

    client = FakeSqsClient()
    provider = AwsSqsProvider(make_settings(), FakeAwsClientFactory(client))

    def delete_failure(**kwargs: Any) -> dict[str, Any]:
        raise ClientError({"Error": {"Code": "AccessDenied"}}, "DeleteMessage")

    client.delete_message = delete_failure  # type: ignore[method-assign]
    with pytest.raises(SqsException, match="delete_message"):
        provider.delete_message(queue, receipt_handle="receipt")

    client = FakeSqsClient()

    def malformed_receive(**kwargs: Any) -> dict[str, Any]:
        return {"Messages": None}

    client.receive_message = malformed_receive  # type: ignore[method-assign]
    provider = AwsSqsProvider(make_settings(), FakeAwsClientFactory(client))
    with pytest.raises(SqsException, match="invalid message batch"):
        provider.receive_messages(
            queue,
            max_number=1,
            wait_time=1,
            visibility_timeout=30,
        )

    client = FakeSqsClient()

    def invalid_page(**kwargs: Any) -> dict[str, Any]:
        return {"QueueUrls": "not-a-list"}

    client.list_queues = invalid_page  # type: ignore[method-assign]
    provider = AwsSqsProvider(make_settings(), FakeAwsClientFactory(client))
    with pytest.raises(SqsException, match="invalid queue listing"):
        provider.list_queues(name_prefix="auth")


def test_aws_sqs_provider_rejects_bad_pagination_and_missing_queue() -> None:
    client = FakeSqsClient()

    def repeated_token(**kwargs: Any) -> dict[str, Any]:
        return {"QueueUrls": [], "NextToken": "same"}

    client.list_queues = repeated_token  # type: ignore[method-assign]
    provider = AwsSqsProvider(make_settings(), FakeAwsClientFactory(client))
    with pytest.raises(SqsException, match="pagination token"):
        provider.list_queues(name_prefix="auth")

    client = FakeSqsClient()

    def no_queues(**kwargs: Any) -> dict[str, Any]:
        return {"QueueUrls": []}

    client.list_queues = no_queues  # type: ignore[method-assign]
    provider = AwsSqsProvider(make_settings(), FakeAwsClientFactory(client))
    with pytest.raises(SqsException, match="not found uniquely"):
        provider.send_message(make_queue(), body="{}", attributes={})
    client = FakeSqsClient()

    def invalid_token(**kwargs: Any) -> dict[str, Any]:
        return {"QueueUrls": [], "NextToken": 7}

    client.list_queues = invalid_token  # type: ignore[method-assign]
    provider = AwsSqsProvider(make_settings(), FakeAwsClientFactory(client))
    with pytest.raises(SqsException, match="pagination token"):
        provider.list_queues(name_prefix="auth")


def test_aws_sqs_provider_reads_trace_and_retry_attributes() -> None:
    client = FakeSqsClient()

    def receive_with_attributes(**kwargs: Any) -> dict[str, Any]:
        return {
            "Messages": [
                {
                    "MessageId": "msg-1",
                    "MessageAttributes": {
                        "correlation_id": {"StringValue": "corr"},
                        "trace_id": {"StringValue": "trace"},
                    },
                    "Attributes": {"ApproximateReceiveCount": "3"},
                },
                "bad-message-shape",
            ]
        }

    client.receive_message = receive_with_attributes  # type: ignore[method-assign]
    provider = AwsSqsProvider(make_settings(), FakeAwsClientFactory(client))
    result = provider.receive_messages(
        make_queue(),
        max_number=2,
        wait_time=1,
        visibility_timeout=30,
    )
    assert len(result) == 2


def test_publisher_and_consumer_round_trip_event_and_ack_after_handling(
    capsys: pytest.CaptureFixture[str],
) -> None:
    provider = FakeProvider()
    settings = make_settings()
    event = make_fake_user_created_event(user_id="private-user")
    validator = make_event_validator()
    publisher = SqsMessagePublisher(
        provider,
        JsonEventSerializer(validator),
        QueueResolver(settings),
        settings,
    )
    result = asyncio.run(publisher.publish(event))
    assert result == PublishResult(
        message_id="sqs-id",
        queue_name="auth-test-identity-events",
        sequence_number="17",
    )
    assert provider.sent[0]["attributes"]["correlation_id"]["StringValue"]
    consumer = SqsMessageConsumer(
        provider,
        EventDeserializer(validator),
        settings,
    )
    provider.received = [
        {
            "Body": provider.sent[0]["body"],
            "ReceiptHandle": "receipt-1",
            "MessageId": "sqs-id",
            "Attributes": {"ApproximateReceiveCount": "2"},
        }
    ]
    batch = asyncio.run(consumer.consume(make_queue()))
    assert len(batch.messages) == 1
    assert batch.messages[0].event == event
    assert batch.messages[0].receive_count == 2
    assert provider.deleted == []
    asyncio.run(consumer.acknowledge(make_queue(), batch.messages[0]))
    assert provider.deleted == [(make_queue(), "receipt-1")]
    assert "private-user" not in capsys.readouterr().out


def test_publish_failures_and_unmapped_routes_are_explicit() -> None:
    settings = make_settings()
    validator = make_event_validator()
    publisher = SqsMessagePublisher(
        FakeProvider(),
        JsonEventSerializer(validator),
        QueueResolver(settings),
        settings,
    )
    event = make_fake_user_created_event().model_copy(
        update={"event_type": "unknown.event.created"}
    )
    with pytest.raises(MessagePublishException):
        asyncio.run(publisher.publish(event))
    failing = FakeProvider()
    failing.fail = True
    publisher = SqsMessagePublisher(
        failing,
        JsonEventSerializer(validator),
        QueueResolver(settings),
        settings,
    )
    with pytest.raises(MessagePublishException):
        asyncio.run(publisher.publish(make_fake_user_created_event()))


def test_consumer_rejects_invalid_message_and_surfaces_receive_failures() -> None:
    provider = FakeProvider()
    settings = make_settings()
    consumer = SqsMessageConsumer(
        provider,
        EventDeserializer(make_event_validator()),
        settings,
    )
    provider.received = [{"Body": "not-json", "ReceiptHandle": "r", "MessageId": "m"}]
    with pytest.raises(MessageConsumeException):
        asyncio.run(consumer.consume(make_queue()))
    provider.received = [{"Body": "{}", "MessageId": "missing-receipt"}]
    with pytest.raises(MessageConsumeException, match="missing required"):
        asyncio.run(consumer.consume(make_queue()))
    provider.received = []
    provider.fail = True
    with pytest.raises(MessageConsumeException):
        asyncio.run(consumer.consume(make_queue()))
    with pytest.raises(MessageConsumeException):
        asyncio.run(
            consumer.acknowledge(
                make_queue(),
                ConsumedMessage(
                    event=make_fake_user_created_event(),
                    receipt_handle="r",
                    receive_count=1,
                    message_id="m",
                ),
            )
        )
    provider.fail = False
    provider.received = [None]  # type: ignore[list-item]
    with pytest.raises(MessageConsumeException, match="message must be an object"):
        asyncio.run(consumer.consume(make_queue()))
    serialized_event = (
        JsonEventSerializer(make_event_validator())
        .serialize(make_fake_user_created_event())
        .decode("utf-8")
    )
    provider.received = [
        {
            "Body": serialized_event,
            "ReceiptHandle": "r",
            "MessageId": "m",
            "Attributes": "invalid",
        }
    ]
    with pytest.raises(MessageConsumeException, match="attributes are invalid"):
        asyncio.run(consumer.consume(make_queue()))
    provider.received[0]["Attributes"] = {"ApproximateReceiveCount": "bad"}
    with pytest.raises(MessageConsumeException, match="receive count is invalid"):
        asyncio.run(consumer.consume(make_queue()))
    provider.received[0]["Attributes"] = {"ApproximateReceiveCount": "0"}
    with pytest.raises(MessageConsumeException, match="must be positive"):
        asyncio.run(consumer.consume(make_queue()))


def test_kms_message_encryption_round_trip_binds_tenant_and_event() -> None:
    provider = FakeKms()
    settings = KmsSettings(
        aws_region="us-east-1",
        account_id="123456789012",
        kms_key_id="key-123",
        environment="test",
    )
    encryption = KmsMessageEncryption(provider, KmsKeyResolver(provider, settings))
    event = make_fake_user_created_event()
    raw = b'{"safe":"payload"}'
    body = encryption.encrypt(event, raw)
    assert raw.decode() not in body
    assert base64.b64encode(bytes(reversed(raw))).decode() in body
    assert encryption.decrypt(body) == raw
    with pytest.raises(MessageConsumeException):
        encryption.decrypt('{"encrypted":true}')
    with pytest.raises(MessageConsumeException):
        encryption.decrypt(
            '{"encrypted":true,"tenant_id":"t","event_id":"not-a-uuid","ciphertext":"YQ=="}'
        )
    with pytest.raises(MessageConsumeException):
        encryption.decrypt(
            '{"encrypted":true,"tenant_id":"t","event_id":"00000000-0000-0000-0000-000000000001",'
            '"ciphertext":"!"}'
        )
    provider.fail_encrypt = True
    with pytest.raises(KmsEncryptionException):
        encryption.encrypt(event, raw)
    provider.fail_encrypt = False
    provider.fail_decrypt = True
    with pytest.raises(MessageConsumeException, match="decryption failed"):
        encryption.decrypt(body)
    provider.fail_decrypt = False
    sqs_provider = FakeProvider()
    event_body = encryption.encrypt(
        event,
        JsonEventSerializer(make_event_validator()).serialize(event),
    )
    sqs_provider.received = [
        {
            "Body": event_body,
            "ReceiptHandle": "receipt",
            "MessageId": "sqs-message",
            "Attributes": {"ApproximateReceiveCount": "1"},
        }
    ]
    consumer = SqsMessageConsumer(
        sqs_provider,
        EventDeserializer(make_event_validator()),
        make_settings(),
        encryption=encryption,
    )
    batch = asyncio.run(consumer.consume(make_queue()))
    assert batch.messages[0].event == event


def test_dispatcher_validates_registers_and_propagates_handler_errors() -> None:
    class Handler:
        calls = 0
        fail = False

        async def handle(self, event: Any) -> None:
            self.calls += 1
            if self.fail:
                raise RuntimeError("handler failed")

    idempotency_validator = IdempotencyValidator(FakeIdempotencyStore())
    dispatcher = MessageDispatcher(make_event_validator(), idempotency_validator)
    handler = Handler()
    with pytest.raises(MessageConsumeException, match="No handler"):
        asyncio.run(dispatcher.dispatch(make_fake_user_created_event()))
    with pytest.raises(ValueError):
        dispatcher.register(" ", handler)
    dispatcher.register(FAKE_EVENT_TYPE, handler)
    with pytest.raises(ValueError):
        dispatcher.register(FAKE_EVENT_TYPE, handler)
    invalid_event = make_fake_user_created_event().model_copy(update={"payload": {"unexpected": 1}})
    with pytest.raises(MessageConsumeException, match="validation failed"):
        asyncio.run(dispatcher.dispatch(invalid_event))
    event = make_fake_user_created_event()
    asyncio.run(dispatcher.dispatch(event))
    assert handler.calls == 1
    asyncio.run(dispatcher.dispatch(event, message_id="duplicate-sqs-message"))
    assert handler.calls == 1
    handler.fail = True
    with pytest.raises(RuntimeError, match="handler failed"):
        asyncio.run(dispatcher.dispatch(make_fake_user_created_event()))
    handler.fail = False
    retry_event = make_fake_user_created_event()
    with pytest.raises(RuntimeError, match="handler failed"):
        handler.fail = True
        asyncio.run(dispatcher.dispatch(retry_event))
    handler.fail = False
    asyncio.run(dispatcher.dispatch(retry_event))


def test_retry_policy_and_dead_letter_forwarding_preserve_order() -> None:
    policy = RetryPolicy(max_attempts=3, base_delay_seconds=2, max_delay_seconds=5)
    assert (
        policy.evaluate(RuntimeError(), RetryMetadata(attempt=1, max_attempts=3)).delay_seconds == 2
    )
    assert policy.evaluate(
        RuntimeError(), RetryMetadata(attempt=3, max_attempts=3)
    ).should_dead_letter
    assert policy.evaluate(
        EventException("bad event"), RetryMetadata(attempt=1, max_attempts=3)
    ).should_dead_letter
    with pytest.raises(ValueError):
        RetryMetadata(attempt=0, max_attempts=3)
    provider = FakeProvider()
    dlq_policy = DeadLetterPolicy(provider)
    assert dlq_policy.should_dead_letter(receive_count=3, max_receive_count=3, permanent=False)
    assert dlq_policy.should_dead_letter(receive_count=1, max_receive_count=3, permanent=True)
    metadata = DeadLetterMetadata(
        source_queue="source",
        message_id="message",
        event_id="event",
        failure_type="RuntimeError",
        receive_count=4,
    )
    asyncio.run(
        dlq_policy.forward(
            make_queue(),
            QueueMetadata("identity", FAKE_EVENT_TYPE, "auth-test-identity-dlq"),
            body='{"event":"safe"}',
            receipt_handle="receipt",
            metadata=metadata,
            correlation_id="correlation",
            trace_id="trace",
            account_id="123456789012",
            region="us-east-1",
        )
    )
    assert provider.sent[0]["attributes"]["failure_type"]["StringValue"] == "RuntimeError"
    assert provider.deleted == [(make_queue(), "receipt")]
    provider.fail = True
    with pytest.raises(SqsException):
        asyncio.run(
            dlq_policy.forward(
                make_queue(),
                QueueMetadata("identity", FAKE_EVENT_TYPE, "dlq"),
                body="body",
                receipt_handle="receipt",
                metadata=metadata,
                correlation_id="c",
                trace_id="t",
                account_id="123456789012",
                region="us-east-1",
            )
        )


def test_idempotency_claim_is_tenant_scoped_and_duplicates_are_reported() -> None:
    store = FakeIdempotencyStore()
    validator = IdempotencyValidator(store)

    async def exercise_validator() -> None:
        assert not await validator.is_duplicate(message_id="m-1", event_id="e-1", tenant_id="t-1")
        await validator.mark_processed(message_id="m-1", event_id="e-1", tenant_id="t-1")
        assert await validator.is_duplicate(message_id="m-2", event_id="e-1", tenant_id="t-1")
        assert not await validator.is_duplicate(message_id="m-3", event_id="e-1", tenant_id="t-2")
        await validator.release(message_id="m-3", event_id="e-1", tenant_id="t-2")
        with pytest.raises(IdempotencyException):
            await validator.is_duplicate(message_id="", event_id="e-1", tenant_id="t-1")

    asyncio.run(exercise_validator())


def test_dynamodb_idempotency_store_uses_conditional_leases() -> None:
    table = FakeDynamoTable()
    store = DynamoDbIdempotencyStore(table, lease_seconds=60, retention_seconds=3600)
    key = IdempotencyKey(tenant_id="tenant-1", event_id="event-1")
    token = store.claim(key)
    assert token is not None
    put_call = table.calls[-1][1]
    assert put_call["Item"]["claim_token"] == token
    assert "lease_expires_at" in put_call["Item"]
    assert "attribute_not_exists(id)" in put_call["ConditionExpression"]
    store.complete(key, claim_token=token)
    assert "completed_at" in table.calls[-1][1]["UpdateExpression"]
    store.release(key, claim_token=token)

    table.failure = ("put_item", "ConditionalCheckFailedException")
    assert store.claim(key) is None
    table.failure = ("put_item", "AccessDeniedException")
    with pytest.raises(IdempotencyException, match="acquire"):
        store.claim(key)
    table.failure = ("update_item", "ConditionalCheckFailedException")
    with pytest.raises(IdempotencyException, match="complete"):
        store.complete(key, claim_token=token)
    table.failure = ("delete_item", "ConditionalCheckFailedException")
    with pytest.raises(IdempotencyException, match="release"):
        store.release(key, claim_token=token)
    with pytest.raises(ValueError):
        DynamoDbIdempotencyStore(table, lease_seconds=0)


def test_sqs_health_check_and_connection_validator_report_status() -> None:
    settings = make_settings()
    provider = FakeProvider()
    health = SqsHealthCheck(provider, settings)
    assert health.check(make_queue()).status is HealthStatus.HEALTHY
    provider.attributes = {"QueueArn": "arn:queue"}
    assert health.check(make_queue()).status is HealthStatus.DEGRADED
    provider.fail = True
    assert health.check(make_queue()).status is HealthStatus.UNHEALTHY

    class AwsValidator:
        connected = True

        def validate(self, *, region_name: str | None = None) -> bool:
            return self.connected

    aws_validator = AwsValidator()
    provider.fail = False
    provider.attributes = {"QueueArn": "arn:aws:sqs:us-east-1:123456789012:q"}
    connection = SqsConnectionValidator(
        settings,
        provider,
        aws_validator=aws_validator,  # type: ignore[arg-type]
    )
    assert connection.validate(make_queue())
    aws_validator.connected = False
    assert not connection.validate(make_queue())
    aws_validator.connected = True
    provider.fail = True
    with pytest.raises(SqsException):
        connection.validate(make_queue())
