"""Construct reusable test fixtures for the messaging foundation."""

from typing import Any

from shared.messaging.queues.queue_metadata import QueueMetadata
from shared.messaging.settings.sqs_settings import SqsSettings
from shared.messaging.testing.fake_sqs import FakeSqsProvider


def build_sqs_settings(**overrides: Any) -> SqsSettings:
    """Build valid local SQS settings, applying explicit test overrides."""

    values: dict[str, Any] = {
        "aws_region": "us-east-1",
        "account_id": "123456789012",
        "queue_prefix": "auth",
        "environment": "test",
    }
    values.update(overrides)
    return SqsSettings(**values)


def build_fake_sqs_provider() -> FakeSqsProvider:
    """Return an isolated fake provider."""

    return FakeSqsProvider()


def build_queue_metadata(
    *,
    bounded_context: str = "identity",
    event_type: str = "identity.user.created",
    queue_name: str = "auth-test-identity-events",
    fifo: bool = False,
) -> QueueMetadata:
    """Build logical queue metadata without a URL."""

    return QueueMetadata(
        bounded_context=bounded_context,
        event_type=event_type,
        queue_name=queue_name,
        fifo=fifo,
    )
