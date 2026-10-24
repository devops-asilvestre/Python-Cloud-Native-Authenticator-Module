"""SQS health check using GetQueueAttributes."""

from dataclasses import dataclass
from enum import StrEnum

from shared.messaging.contracts.queue_provider_contract import QueueProviderContract
from shared.messaging.queues.queue_metadata import QueueMetadata
from shared.messaging.settings.sqs_settings import SqsSettings
from shared.observability.logging.logger_contract import LoggerContract
from shared.observability.logging.structured_logger import StructuredLogger


class HealthStatus(StrEnum):
    """Messaging dependency health status."""

    HEALTHY = "Healthy"
    DEGRADED = "Degraded"
    UNHEALTHY = "Unhealthy"


@dataclass(frozen=True, slots=True)
class SqsHealthResult:
    """Health status and queue name; never includes payload data."""

    status: HealthStatus
    queue_name: str
    reason: str | None = None


class SqsHealthCheck:
    """Check queue access and basic queue metrics."""

    def __init__(
        self,
        provider: QueueProviderContract,
        settings: SqsSettings,
        *,
        logger: LoggerContract | None = None,
    ) -> None:
        self._provider = provider
        self._settings = settings
        self._logger = logger or StructuredLogger("shared-sqs-health-check")

    def check(self, queue: QueueMetadata) -> SqsHealthResult:
        try:
            attributes = self._provider.get_queue_attributes(queue)
        except Exception as exc:
            self._logger.error(
                "sqs_health_check_failed",
                operation="get_queue_attributes",
                queue=queue.queue_name,
                account_id=self._settings.account_id,
                region=self._settings.aws_region,
                success=False,
                error_type=type(exc).__name__,
            )
            return SqsHealthResult(
                status=HealthStatus.UNHEALTHY,
                queue_name=queue.queue_name,
                reason="Queue attributes could not be retrieved.",
            )

        status = (
            HealthStatus.HEALTHY
            if isinstance(attributes.get("QueueArn"), str)
            and "ApproximateNumberOfMessages" in attributes
            else HealthStatus.DEGRADED
        )
        self._logger.info(
            "sqs_health_check_completed",
            operation="get_queue_attributes",
            queue=queue.queue_name,
            account_id=self._settings.account_id,
            region=self._settings.aws_region,
            success=status is HealthStatus.HEALTHY,
            status=status.value,
        )
        return SqsHealthResult(
            status=status,
            queue_name=queue.queue_name,
            reason=None if status is HealthStatus.HEALTHY else "Queue metrics are incomplete.",
        )
