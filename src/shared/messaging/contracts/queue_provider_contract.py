"""SQS provider contract."""

from typing import Any, Protocol

from shared.messaging.queues.queue_metadata import QueueMetadata


class QueueProviderContract(Protocol):
    """The only boundary allowed to perform SQS API operations."""

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
    ) -> dict[str, Any]: ...

    def receive_messages(
        self,
        queue: QueueMetadata,
        *,
        max_number: int,
        wait_time: int,
        visibility_timeout: int,
    ) -> list[dict[str, Any]]: ...

    def delete_message(
        self,
        queue: QueueMetadata,
        *,
        receipt_handle: str,
        message_id: str | None = None,
        correlation_id: str | None = None,
        trace_id: str | None = None,
    ) -> None: ...

    def get_queue_attributes(self, queue: QueueMetadata) -> dict[str, Any]: ...

    def list_queues(self, *, name_prefix: str) -> list[str]: ...
