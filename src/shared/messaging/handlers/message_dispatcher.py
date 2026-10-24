"""Dispatch validated events to registered application handlers."""

from shared.events.envelope.event_envelope import EventEnvelope
from shared.events.exceptions.validation_exception import EventValidationException
from shared.events.validation.schema_validator import EventSchemaValidator
from shared.messaging.contracts.message_handler_contract import MessageHandlerContract
from shared.messaging.exceptions.sqs_exception import MessageConsumeException
from shared.messaging.idempotency.idempotency_validator import IdempotencyValidator
from shared.observability.logging.logger_contract import LoggerContract
from shared.observability.logging.structured_logger import StructuredLogger


class MessageDispatcher:
    """Resolve handlers by exact event type and validate before dispatch."""

    def __init__(
        self,
        schema_validator: EventSchemaValidator,
        idempotency_validator: IdempotencyValidator,
        *,
        logger: LoggerContract | None = None,
    ) -> None:
        self._schema_validator = schema_validator
        self._idempotency_validator = idempotency_validator
        self._handlers: dict[str, MessageHandlerContract] = {}
        self._logger = logger or StructuredLogger("shared-message-dispatcher")

    def register(self, event_type: str, handler: MessageHandlerContract) -> None:
        if not event_type.strip():
            raise ValueError("Event type cannot be empty.")
        if event_type in self._handlers:
            raise ValueError(f"A handler is already registered for {event_type!r}.")
        self._handlers[event_type] = handler

    async def dispatch(self, event: EventEnvelope, *, message_id: str | None = None) -> None:
        stable_message_id = message_id or str(event.event_id)
        handler = self._handlers.get(event.event_type)
        if handler is None:
            self._logger.error(
                "sqs_event_handler_missing",
                event_type=event.event_type,
                message_id=stable_message_id,
                event_id=str(event.event_id),
                correlation_id=str(event.correlation_id),
                trace_id=str(event.trace_id),
                success=False,
            )
            raise MessageConsumeException("No handler is registered for this event type.")
        try:
            self._schema_validator.validate(event)
        except EventValidationException as exc:
            self._logger.warning(
                "sqs_event_dispatch_rejected",
                event_type=event.event_type,
                message_id=stable_message_id,
                event_id=str(event.event_id),
                correlation_id=str(event.correlation_id),
                trace_id=str(event.trace_id),
            )
            raise MessageConsumeException("Event validation failed before dispatch.") from exc
        if await self._idempotency_validator.is_duplicate(
            message_id=stable_message_id,
            event_id=str(event.event_id),
            tenant_id=event.tenant_id,
        ):
            self._logger.info(
                "sqs_duplicate_event_skipped",
                event_type=event.event_type,
                message_id=stable_message_id,
                event_id=str(event.event_id),
                correlation_id=str(event.correlation_id),
                trace_id=str(event.trace_id),
                success=True,
            )
            return
        try:
            await handler.handle(event)
        except Exception:
            self._logger.error(
                "sqs_event_handler_failed",
                event_type=event.event_type,
                message_id=stable_message_id,
                event_id=str(event.event_id),
                correlation_id=str(event.correlation_id),
                trace_id=str(event.trace_id),
            )
            await self._idempotency_validator.release(
                message_id=stable_message_id,
                event_id=str(event.event_id),
                tenant_id=event.tenant_id,
            )
            raise
        await self._idempotency_validator.mark_processed(
            message_id=stable_message_id,
            event_id=str(event.event_id),
            tenant_id=event.tenant_id,
        )

        self._logger.info(
            "sqs_event_dispatched",
            event_type=event.event_type,
            message_id=stable_message_id,
            event_id=str(event.event_id),
            correlation_id=str(event.correlation_id),
            trace_id=str(event.trace_id),
            success=True,
        )
