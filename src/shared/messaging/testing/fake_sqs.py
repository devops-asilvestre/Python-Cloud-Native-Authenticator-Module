"""In-memory SQS provider for isolated tests."""

from __future__ import annotations

from typing import Any

from shared.messaging.exceptions.sqs_exception import SqsException
from shared.messaging.queues.queue_metadata import QueueMetadata


class FakeSqsProvider:
    """Test provider recording API activity without contacting AWS."""

    def __init__(self) -> None:
        self.sent: list[dict[str, Any]] = []
        self.received: list[dict[str, Any]] = []
        self.deleted: list[tuple[QueueMetadata, str]] = []
        self.attributes: dict[str, Any] = {
            "QueueArn": "arn:aws:sqs:us-east-1:123456789012:auth-test-identity-events",
            "ApproximateNumberOfMessages": "0",
        }
        self.fail = False

    def send_message(
        self,
        queue: QueueMetadata,
        *,
        body: str,
        attributes: dict[str, dict[str, str]],
        group_id: str | None = None,
        deduplication_id: str | None = None,
        correlation_id: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        if self.fail:
            raise SqsException("Fake SQS send failure.")
        self.sent.append(
            {
                "queue": queue,
                "body": body,
                "attributes": attributes,
                "group_id": group_id,
                "deduplication_id": deduplication_id,
                "correlation_id": correlation_id,
                "trace_id": trace_id,
            }
        )
        return {"MessageId": "sqs-id", "SequenceNumber": "17"}

    def receive_messages(
        self,
        queue: QueueMetadata,
        *,
        max_number: int,
        wait_time: int,
        visibility_timeout: int,
    ) -> list[dict[str, Any]]:
        if self.fail:
            raise SqsException("Fake SQS receive failure.")
        return self.received

    def delete_message(
        self,
        queue: QueueMetadata,
        *,
        receipt_handle: str,
        message_id: str | None = None,
        correlation_id: str | None = None,
        trace_id: str | None = None,
    ) -> None:
        if self.fail:
            raise SqsException("Fake SQS delete failure.")
        self.deleted.append((queue, receipt_handle))

    def get_queue_attributes(self, queue: QueueMetadata) -> dict[str, Any]:
        if self.fail:
            raise SqsException("Fake SQS attribute failure.")
        return self.attributes

    def list_queues(self, *, name_prefix: str) -> list[str]:
        return [f"https://sqs.us-east-1.amazonaws.com/123456789012/{name_prefix}"]
