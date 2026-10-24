"""Receive and deserialize SQS messages."""

from __future__ import annotations

import asyncio
from time import perf_counter
from typing import Any

from shared.events.exceptions.event_exception import EventException
from shared.events.serialization.event_deserializer import EventDeserializer
from shared.messaging.contracts.queue_provider_contract import QueueProviderContract
from shared.messaging.encryption.kms_message_encryption import KmsMessageEncryption
from shared.messaging.exceptions.sqs_exception import MessageConsumeException, SqsException
from shared.messaging.models.consumed_message import ConsumedMessage
from shared.messaging.models.message_batch import MessageBatch
from shared.messaging.queues.queue_metadata import QueueMetadata
from shared.messaging.settings.sqs_settings import SqsSettings
from shared.observability.logging.logger_contract import LoggerContract
from shared.observability.logging.structured_logger import StructuredLogger


class SqsMessageConsumer:
    """Long-poll an SQS queue and return validated events without acknowledging them."""

    def __init__(
        self,
        provider: QueueProviderContract,
        deserializer: EventDeserializer,
        settings: SqsSettings,
        *,
        encryption: KmsMessageEncryption | None = None,
        logger: LoggerContract | None = None,
    ) -> None:
        self._provider = provider
        self._deserializer = deserializer
        self._settings = settings
        self._encryption = encryption
        self._logger = logger or StructuredLogger("shared-sqs-consumer")

    async def consume(self, queue: QueueMetadata) -> MessageBatch:
        started = perf_counter()
        try:
            received = await asyncio.to_thread(
                self._provider.receive_messages,
                queue,
                max_number=10,
                wait_time=self._settings.default_wait_time,
                visibility_timeout=self._settings.default_visibility_timeout,
            )
            messages = tuple(
                await asyncio.gather(
                    *(asyncio.to_thread(self._decode_message, message) for message in received)
                )
            )
            for message in messages:
                self._logger.info(
                    "sqs_message_received",
                    operation="receive_message",
                    queue=queue.queue_name,
                    account_id=self._settings.account_id,
                    region=self._settings.aws_region,
                    message_id=message.message_id,
                    event_id=str(message.event.event_id),
                    correlation_id=str(message.event.correlation_id),
                    trace_id=str(message.event.trace_id),
                    retry_count=message.receive_count,
                    success=True,
                )
        except MessageConsumeException:
            self._log_batch(queue, started, success=False, message_count=0)
            raise
        except EventException as exc:
            self._log_batch(queue, started, success=False, message_count=0)
            raise MessageConsumeException(
                "SQS event validation or deserialization failed."
            ) from exc
        except SqsException as exc:
            self._log_batch(queue, started, success=False, message_count=0)
            raise MessageConsumeException("SQS message consumption failed.") from exc
        except (KeyError, TypeError, ValueError) as exc:
            self._log_batch(queue, started, success=False, message_count=0)
            raise MessageConsumeException("SQS returned a malformed message.") from exc

        self._log_batch(queue, started, success=True, message_count=len(messages))
        return MessageBatch(queue_name=queue.queue_name, messages=messages)

    async def acknowledge(self, queue: QueueMetadata, message: ConsumedMessage) -> None:
        """Delete a message only after its handler completes successfully."""

        try:
            await asyncio.to_thread(
                self._provider.delete_message,
                queue,
                receipt_handle=message.receipt_handle,
                message_id=message.message_id,
                correlation_id=str(message.event.correlation_id),
                trace_id=str(message.event.trace_id),
            )
        except SqsException as exc:
            self._logger.error(
                "sqs_message_acknowledgement_failed",
                operation="delete_message",
                queue=queue.queue_name,
                account_id=self._settings.account_id,
                region=self._settings.aws_region,
                message_id=message.message_id,
                event_id=str(message.event.event_id),
                correlation_id=str(message.event.correlation_id),
                trace_id=str(message.event.trace_id),
                success=False,
            )
            raise MessageConsumeException("SQS message acknowledgement failed.") from exc
        self._logger.info(
            "sqs_message_acknowledged",
            operation="delete_message",
            queue=queue.queue_name,
            account_id=self._settings.account_id,
            region=self._settings.aws_region,
            message_id=message.message_id,
            event_id=str(message.event.event_id),
            correlation_id=str(message.event.correlation_id),
            trace_id=str(message.event.trace_id),
            success=True,
        )

    def _decode_message(self, raw: dict[str, Any]) -> ConsumedMessage:
        if not isinstance(raw, dict):
            raise MessageConsumeException("SQS message must be an object.")
        body = raw.get("Body")
        receipt_handle = raw.get("ReceiptHandle")
        message_id = raw.get("MessageId")
        if (
            not isinstance(body, str)
            or not body
            or not isinstance(receipt_handle, str)
            or not receipt_handle
            or not isinstance(message_id, str)
            or not message_id
        ):
            raise MessageConsumeException("SQS message is missing required fields.")

        if self._encryption is not None and self._is_encrypted(body):
            encoded = self._encryption.decrypt(body)
        else:
            encoded = body.encode("utf-8")
        event = self._deserializer.deserialize(encoded)
        attributes = raw.get("Attributes", {})
        if not isinstance(attributes, dict):
            raise MessageConsumeException("SQS message attributes are invalid.")
        try:
            receive_count = int(attributes.get("ApproximateReceiveCount", "1"))
        except (TypeError, ValueError) as exc:
            raise MessageConsumeException("SQS receive count is invalid.") from exc
        if receive_count < 1:
            raise MessageConsumeException("SQS receive count must be positive.")
        return ConsumedMessage(
            event=event,
            receipt_handle=receipt_handle,
            receive_count=receive_count,
            message_id=message_id,
        )

    @staticmethod
    def _is_encrypted(body: str) -> bool:
        import json

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            return False
        return isinstance(parsed, dict) and parsed.get("encrypted") is True

    def _log_batch(
        self,
        queue: QueueMetadata,
        started: float,
        *,
        success: bool,
        message_count: int,
    ) -> None:
        self._logger.info(
            "sqs_message_batch_received" if success else "sqs_message_batch_failed",
            operation="receive_message",
            queue=queue.queue_name,
            account_id=self._settings.account_id,
            region=self._settings.aws_region,
            latency_ms=round((perf_counter() - started) * 1000, 3),
            message_count=message_count,
            success=success,
        )
