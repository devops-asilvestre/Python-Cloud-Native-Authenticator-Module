"""Dead-letter decisions and safe message forwarding."""

import asyncio

from shared.messaging.contracts.queue_provider_contract import QueueProviderContract
from shared.messaging.dlq.dead_letter_metadata import DeadLetterMetadata
from shared.messaging.exceptions.sqs_exception import SqsException
from shared.messaging.queues.queue_metadata import QueueMetadata
from shared.observability.logging.logger_contract import LoggerContract
from shared.observability.logging.structured_logger import StructuredLogger


class DeadLetterPolicy:
    """Forward a failed body before deleting its source message."""

    def __init__(
        self,
        provider: QueueProviderContract,
        *,
        logger: LoggerContract | None = None,
    ) -> None:
        self._provider = provider
        self._logger = logger or StructuredLogger("shared-sqs-dlq")

    @staticmethod
    def should_dead_letter(*, receive_count: int, max_receive_count: int, permanent: bool) -> bool:
        if receive_count < 1 or max_receive_count < 1:
            raise ValueError("DLQ receive counts must be positive.")
        return permanent or receive_count >= max_receive_count

    async def forward(
        self,
        source: QueueMetadata,
        destination: QueueMetadata,
        *,
        body: str,
        receipt_handle: str,
        metadata: DeadLetterMetadata,
        correlation_id: str,
        trace_id: str,
        account_id: str,
        region: str,
    ) -> None:
        try:
            await asyncio.to_thread(
                self._provider.send_message,
                destination,
                body=body,
                attributes={
                    "source_queue": {
                        "DataType": "String",
                        "StringValue": metadata.source_queue,
                    },
                    "original_message_id": {
                        "DataType": "String",
                        "StringValue": metadata.message_id,
                    },
                    "event_id": {"DataType": "String", "StringValue": metadata.event_id},
                    "failure_type": {
                        "DataType": "String",
                        "StringValue": metadata.failure_type,
                    },
                    "receive_count": {
                        "DataType": "Number",
                        "StringValue": str(metadata.receive_count),
                    },
                },
                group_id=metadata.event_id if destination.fifo else None,
                deduplication_id=metadata.event_id if destination.fifo else None,
                correlation_id=correlation_id,
                trace_id=trace_id,
            )
            await asyncio.to_thread(
                self._provider.delete_message,
                source,
                receipt_handle=receipt_handle,
                message_id=metadata.message_id,
                correlation_id=correlation_id,
                trace_id=trace_id,
            )
        except SqsException:
            self._logger.error(
                "sqs_dead_letter_forward_failed",
                operation="dead_letter",
                queue=destination.queue_name,
                account_id=account_id,
                region=region,
                correlation_id=correlation_id,
                trace_id=trace_id,
                message_id=metadata.message_id,
                success=False,
            )
            raise
        self._logger.warning(
            "sqs_message_dead_lettered",
            operation="dead_letter",
            queue=destination.queue_name,
            account_id=account_id,
            region=region,
            correlation_id=correlation_id,
            trace_id=trace_id,
            message_id=metadata.message_id,
            event_id=metadata.event_id,
            failure_type=metadata.failure_type,
            receive_count=metadata.receive_count,
            success=True,
        )
