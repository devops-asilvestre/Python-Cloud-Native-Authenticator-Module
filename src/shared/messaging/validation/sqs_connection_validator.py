"""Validate AWS identity and access to a configured SQS queue."""

from shared.aws.validation.aws_connection_validator import AwsConnectionValidator
from shared.messaging.contracts.queue_provider_contract import QueueProviderContract
from shared.messaging.exceptions.sqs_exception import SqsException
from shared.messaging.queues.queue_metadata import QueueMetadata
from shared.messaging.settings.sqs_settings import SqsSettings
from shared.observability.logging.logger_contract import LoggerContract
from shared.observability.logging.structured_logger import StructuredLogger


class SqsConnectionValidator:
    """Validate credentials through the AWS foundation and queue access."""

    def __init__(
        self,
        settings: SqsSettings,
        provider: QueueProviderContract,
        *,
        aws_validator: AwsConnectionValidator | None = None,
        logger: LoggerContract | None = None,
    ) -> None:
        self._settings = settings
        self._provider = provider
        self._aws_validator = aws_validator or AwsConnectionValidator()
        self._logger = logger or StructuredLogger("shared-sqs-connection-validator")

    def validate(self, queue: QueueMetadata) -> bool:
        if not self._aws_validator.validate(region_name=self._settings.aws_region):
            self._logger.warning(
                "sqs_connection_validation_failed",
                operation="get_caller_identity",
                queue=queue.queue_name,
                account_id=self._settings.account_id,
                region=self._settings.aws_region,
                success=False,
            )
            return False
        try:
            attributes = self._provider.get_queue_attributes(queue)
        except SqsException:
            self._logger.error(
                "sqs_connection_validation_failed",
                operation="get_queue_attributes",
                queue=queue.queue_name,
                account_id=self._settings.account_id,
                region=self._settings.aws_region,
                success=False,
            )
            raise
        if not isinstance(attributes.get("QueueArn"), str):
            raise SqsException("SQS queue identity could not be validated.")
        self._logger.info(
            "sqs_connection_validation_succeeded",
            operation="get_queue_attributes",
            queue=queue.queue_name,
            account_id=self._settings.account_id,
            region=self._settings.aws_region,
            success=True,
        )
        return True
