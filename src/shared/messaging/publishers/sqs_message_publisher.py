"""Publish validated event envelopes to SQS."""

from __future__ import annotations

import asyncio
from time import perf_counter

from shared.events.envelope.event_envelope import EventEnvelope
from shared.events.exceptions.event_exception import EventException
from shared.events.serialization.event_serializer import EventSerializer
from shared.kms.exceptions.kms_encryption_exception import KmsEncryptionException
from shared.messaging.contracts.queue_provider_contract import QueueProviderContract
from shared.messaging.encryption.kms_message_encryption import KmsMessageEncryption
from shared.messaging.exceptions.sqs_exception import (
    MessagePublishException,
    SqsException,
)
from shared.messaging.models.publish_result import PublishResult
from shared.messaging.queues.queue_resolver import QueueResolver
from shared.messaging.settings.sqs_settings import SqsSettings
from shared.observability.logging.logger_contract import LoggerContract
from shared.observability.logging.structured_logger import StructuredLogger


class SqsMessagePublisher:
    """Serialize, route, audit, and publish event envelopes."""

    def __init__(
        self,
        provider: QueueProviderContract,
        serializer: EventSerializer,
        queue_resolver: QueueResolver,
        settings: SqsSettings,
        *,
        encryption: KmsMessageEncryption | None = None,
        logger: LoggerContract | None = None,
    ) -> None:
        self._provider = provider
        self._serializer = serializer
        self._queue_resolver = queue_resolver
        self._settings = settings
        self._encryption = encryption
        self._logger = logger or StructuredLogger("shared-sqs-publisher")

    async def publish(self, event: EventEnvelope) -> PublishResult:
        started = perf_counter()
        queue_name = "unresolved"
        try:
            bounded_context = self._bounded_context(event.event_type)
            queue = self._queue_resolver.resolve(bounded_context, event.event_type)
            queue_name = queue.queue_name
            body_bytes = self._serializer.serialize(event)
            body = (
                await asyncio.to_thread(self._encryption.encrypt, event, body_bytes)
                if self._encryption is not None
                else body_bytes.decode("utf-8")
            )
            response = await asyncio.to_thread(
                self._provider.send_message,
                queue,
                body=body,
                attributes={
                    "event_id": {"DataType": "String", "StringValue": str(event.event_id)},
                    "event_type": {"DataType": "String", "StringValue": event.event_type},
                    "tenant_id": {"DataType": "String", "StringValue": event.tenant_id},
                    "correlation_id": {
                        "DataType": "String",
                        "StringValue": str(event.correlation_id),
                    },
                    "trace_id": {"DataType": "String", "StringValue": str(event.trace_id)},
                },
                group_id=event.tenant_id,
                deduplication_id=str(event.event_id),
                correlation_id=str(event.correlation_id),
                trace_id=str(event.trace_id),
            )
            message_id = response.get("MessageId")
            if not isinstance(message_id, str) or not message_id:
                raise SqsException("SQS did not return a message identifier.")
            result = PublishResult(
                message_id=message_id,
                queue_name=queue.queue_name,
                sequence_number=(
                    response.get("SequenceNumber")
                    if isinstance(response.get("SequenceNumber"), str)
                    else None
                ),
            )
        except (
            EventException,
            KmsEncryptionException,
            SqsException,
            UnicodeDecodeError,
        ) as exc:
            self._log_operation(event, queue_name, started, success=False)
            raise MessagePublishException("Event publication failed.") from exc

        self._log_operation(event, queue_name, started, success=True, message_id=result.message_id)
        return result

    @staticmethod
    def _bounded_context(event_type: str) -> str:
        aliases = {"tenant-created": "tenant", "user-created": "identity"}
        return aliases.get(event_type, event_type.split(".", maxsplit=1)[0])

    def _log_operation(
        self,
        event: EventEnvelope,
        queue_name: str,
        started: float,
        *,
        success: bool,
        message_id: str | None = None,
    ) -> None:
        self._logger.info(
            "sqs_message_published" if success else "sqs_message_publish_failed",
            operation="send_message",
            queue=queue_name,
            account_id=self._settings.account_id,
            region=self._settings.aws_region,
            correlation_id=str(event.correlation_id),
            trace_id=str(event.trace_id),
            event_id=str(event.event_id),
            message_id=message_id or str(event.event_id),
            latency_ms=round((perf_counter() - started) * 1000, 3),
            success=success,
        )
