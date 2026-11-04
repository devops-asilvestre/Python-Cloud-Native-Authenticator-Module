"""AWS SQS adapter; queue URLs are discovered, never configured in code."""

from __future__ import annotations

from time import perf_counter
from typing import Any, cast

from botocore.config import Config  # type: ignore[import-untyped]
from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-untyped]

from shared.aws.factories.aws_client_factory import AwsClientFactory
from shared.messaging.exceptions.sqs_exception import SqsException
from shared.messaging.queues.queue_metadata import QueueMetadata
from shared.messaging.settings.sqs_settings import SqsSettings
from shared.observability.logging.logger_contract import LoggerContract
from shared.observability.logging.structured_logger import StructuredLogger


class AwsSqsProvider:
    """Allowlisted SQS operations implemented through the shared AWS foundation."""

    def __init__(
        self,
        settings: SqsSettings,
        client_factory: AwsClientFactory | None = None,
        *,
        logger: LoggerContract | None = None,
    ) -> None:
        self._settings = settings
        self._client_factory = client_factory or AwsClientFactory()
        self._client: Any = self._client_factory.create_client(
            "sqs",
            region_name=settings.aws_region,
            endpoint_url=settings.endpoint_url,
            config=Config(
                retries={"max_attempts": 3, "mode": "standard"},
                connect_timeout=3,
                read_timeout=25,
            ),
        )
        self._logger = logger or StructuredLogger("shared-aws-sqs-provider")

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
        request: dict[str, Any] = {
            "QueueUrl": self._queue_url(queue),
            "MessageBody": body,
            "MessageAttributes": attributes,
        }
        if queue.fifo:
            request["MessageGroupId"] = group_id or queue.bounded_context
            request["MessageDeduplicationId"] = deduplication_id or queue.event_type
        started = perf_counter()
        try:
            response = cast(dict[str, Any], self._client.send_message(**request))
        except (BotoCoreError, ClientError) as exc:
            self._audit(
                "send_message",
                queue.queue_name,
                started,
                success=False,
                correlation_id=correlation_id,
                trace_id=trace_id,
            )
            raise SqsException("SQS send_message operation failed.") from exc
        self._audit(
            "send_message",
            queue.queue_name,
            started,
            success=True,
            message_id=(
                response.get("MessageId") if isinstance(response.get("MessageId"), str) else None
            ),
            correlation_id=correlation_id,
            trace_id=trace_id,
        )
        return response

    def receive_messages(
        self,
        queue: QueueMetadata,
        *,
        max_number: int,
        wait_time: int,
        visibility_timeout: int,
    ) -> list[dict[str, Any]]:
        started = perf_counter()
        try:
            response = self._client.receive_message(
                QueueUrl=self._queue_url(queue),
                MaxNumberOfMessages=max_number,
                WaitTimeSeconds=wait_time,
                VisibilityTimeout=visibility_timeout,
                MessageAttributeNames=["All"],
                MessageSystemAttributeNames=["ApproximateReceiveCount", "SentTimestamp"],
            )
        except (BotoCoreError, ClientError) as exc:
            self._audit("receive_message", queue.queue_name, started, success=False)
            raise SqsException("SQS receive_message operation failed.") from exc
        messages = response.get("Messages", [])
        if not isinstance(messages, list):
            self._audit("receive_message", queue.queue_name, started, success=False)
            raise SqsException("SQS returned an invalid message batch.")
        if not messages:
            self._audit("receive_message", queue.queue_name, started, success=True)
        for message in messages:
            if not isinstance(message, dict):
                continue
            message_attributes = message.get("MessageAttributes")
            system_attributes = message.get("Attributes")
            self._audit(
                "receive_message",
                queue.queue_name,
                started,
                success=True,
                message_id=(
                    message.get("MessageId") if isinstance(message.get("MessageId"), str) else None
                ),
                correlation_id=self._message_attribute(message_attributes, "correlation_id"),
                trace_id=self._message_attribute(message_attributes, "trace_id"),
                retry_count=(
                    system_attributes.get("ApproximateReceiveCount")
                    if isinstance(system_attributes, dict)
                    else None
                ),
            )
        return messages

    def delete_message(
        self,
        queue: QueueMetadata,
        *,
        receipt_handle: str,
        message_id: str | None = None,
        correlation_id: str | None = None,
        trace_id: str | None = None,
    ) -> None:
        started = perf_counter()
        try:
            self._client.delete_message(
                QueueUrl=self._queue_url(queue),
                ReceiptHandle=receipt_handle,
            )
        except (BotoCoreError, ClientError) as exc:
            self._audit(
                "delete_message",
                queue.queue_name,
                started,
                success=False,
                message_id=message_id,
                correlation_id=correlation_id,
                trace_id=trace_id,
            )
            raise SqsException("SQS delete_message operation failed.") from exc
        self._audit(
            "delete_message",
            queue.queue_name,
            started,
            success=True,
            message_id=message_id,
            correlation_id=correlation_id,
            trace_id=trace_id,
        )

    def get_queue_attributes(self, queue: QueueMetadata) -> dict[str, Any]:
        started = perf_counter()
        try:
            response = self._client.get_queue_attributes(
                QueueUrl=self._queue_url(queue),
                AttributeNames=["QueueArn", "ApproximateNumberOfMessages"],
            )
        except (BotoCoreError, ClientError) as exc:
            self._audit(
                "get_queue_attributes",
                queue.queue_name,
                started,
                success=False,
            )
            raise SqsException("SQS get_queue_attributes operation failed.") from exc
        attributes = response.get("Attributes", {})
        if not isinstance(attributes, dict):
            self._audit("get_queue_attributes", queue.queue_name, started, success=False)
            raise SqsException("SQS returned invalid queue attributes.")
        self._audit("get_queue_attributes", queue.queue_name, started, success=True)
        return attributes

    def list_queues(self, *, name_prefix: str) -> list[str]:
        started = perf_counter()
        queue_urls: list[str] = []
        next_token: str | None = None
        seen_tokens: set[str] = set()
        while True:
            request: dict[str, str] = {"QueueNamePrefix": name_prefix}
            if next_token is not None:
                request["NextToken"] = next_token
            try:
                response = self._client.list_queues(**request)
            except (BotoCoreError, ClientError) as exc:
                self._audit("list_queues", name_prefix, started, success=False)
                raise SqsException("SQS list_queues operation failed.") from exc
            page = response.get("QueueUrls", [])
            if not isinstance(page, list) or not all(isinstance(url, str) for url in page):
                self._audit("list_queues", name_prefix, started, success=False)
                raise SqsException("SQS returned an invalid queue listing.")
            queue_urls.extend(page)
            token = response.get("NextToken")
            if token is None:
                self._audit("list_queues", name_prefix, started, success=True)
                return queue_urls
            if not isinstance(token, str) or not token or token in seen_tokens:
                self._audit("list_queues", name_prefix, started, success=False)
                raise SqsException("SQS returned an invalid queue pagination token.")
            seen_tokens.add(token)
            next_token = token

    def _queue_url(self, queue: QueueMetadata) -> str:
        urls = self.list_queues(name_prefix=queue.queue_name)
        matches = [
            url for url in urls if url.rstrip("/").rsplit("/", maxsplit=1)[-1] == queue.queue_name
        ]
        if len(matches) != 1:
            raise SqsException("The configured SQS queue was not found uniquely.")
        url = matches[0]
        attributes = self.get_queue_attributes_for_url(url)
        queue_arn = attributes.get("QueueArn")
        expected_arn = (
            f"arn:aws:sqs:{self._settings.aws_region}:"
            f"{self._settings.account_id}:{queue.queue_name}"
        )
        if queue_arn != expected_arn:
            raise SqsException("The resolved SQS queue is outside the configured AWS account.")
        return url

    def get_queue_attributes_for_url(self, queue_url: str) -> dict[str, Any]:
        """Validate queue identity before using its discovered URL."""

        queue_name = queue_url.rstrip("/").rsplit("/", maxsplit=1)[-1]
        started = perf_counter()
        try:
            response = self._client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=["QueueArn"],
            )
        except (BotoCoreError, ClientError) as exc:
            self._audit(
                "get_queue_attributes",
                queue_name,
                started,
                success=False,
            )
            raise SqsException("SQS get_queue_attributes operation failed.") from exc
        attributes = response.get("Attributes", {})
        if not isinstance(attributes, dict):
            self._audit("get_queue_attributes", queue_name, started, success=False)
            raise SqsException("SQS returned invalid queue attributes.")
        self._audit("get_queue_attributes", queue_name, started, success=True)
        return attributes

    @staticmethod
    def _message_attribute(attributes: Any, name: str) -> str | None:
        if not isinstance(attributes, dict):
            return None
        value = attributes.get(name)
        if not isinstance(value, dict):
            return None
        string_value = value.get("StringValue")
        return string_value if isinstance(string_value, str) else None

    def _audit(
        self,
        operation: str,
        queue_name: str,
        started: float,
        *,
        success: bool,
        message_id: str | None = None,
        correlation_id: str | None = None,
        trace_id: str | None = None,
        retry_count: Any = None,
    ) -> None:
        log = self._logger.info if success else self._logger.error
        log(
            "sqs_operation_succeeded" if success else "sqs_operation_failed",
            operation=operation,
            queue=queue_name,
            account_id=self._settings.account_id,
            region=self._settings.aws_region,
            correlation_id=correlation_id,
            trace_id=trace_id,
            message_id=message_id,
            latency_ms=round((perf_counter() - started) * 1000, 3),
            retry_count=retry_count,
            success=success,
        )
