"""Resolve event types to logical SQS queues."""

from shared.messaging.exceptions.sqs_exception import SqsConfigurationException
from shared.messaging.queues.queue_metadata import QueueMetadata
from shared.messaging.queues.queue_strategy import QueueStrategy
from shared.messaging.settings.sqs_settings import SqsSettings


class DefaultQueueStrategy:
    """Explicit allowlist for the event routes defined by the foundation."""

    _routes = {
        ("tenant", "tenant-created"): "tenant-events",
        ("tenant", "tenant.created"): "tenant-events",
        ("tenant", "tenant.tenant.created"): "tenant-events",
        ("identity", "user-created"): "identity-events",
        ("identity", "user.created"): "identity-events",
        ("identity", "identity.user.created"): "identity-events",
    }

    def resolve(self, bounded_context: str, event_type: str) -> str:
        try:
            return self._routes[(bounded_context, event_type)]
        except KeyError as exc:
            raise SqsConfigurationException(
                "No SQS queue route is configured for this context and event type."
            ) from exc


class QueueResolver:
    """Apply configured environment prefixes to allowlisted logical queues."""

    def __init__(
        self,
        settings: SqsSettings,
        strategy: QueueStrategy | None = None,
        *,
        fifo: bool = False,
    ) -> None:
        self._settings = settings
        self._strategy = strategy or DefaultQueueStrategy()
        self._fifo = fifo

    def resolve(self, bounded_context: str, event_type: str) -> QueueMetadata:
        name = self._strategy.resolve(bounded_context, event_type)
        if not name:
            raise SqsConfigurationException("Resolved SQS queue name is empty.")
        suffix = ".fifo" if self._fifo else ""
        queue_name = f"{self._settings.queue_prefix}-{self._settings.environment}-{name}{suffix}"
        base_name = queue_name.removesuffix(".fifo")
        valid_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        if (
            len(queue_name) > 80
            or not base_name
            or any(character not in valid_characters for character in base_name)
        ):
            raise SqsConfigurationException("Resolved SQS queue name is invalid.")
        return QueueMetadata(
            bounded_context=bounded_context,
            event_type=event_type,
            queue_name=queue_name,
            fifo=self._fifo,
        )
