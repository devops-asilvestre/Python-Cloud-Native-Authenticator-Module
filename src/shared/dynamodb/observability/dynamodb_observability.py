"""Structured DynamoDB operation logging via the shared observability foundation."""

from __future__ import annotations

from shared.aws.observability.aws_observability import AwsObservability
from shared.dynamodb.context.dynamodb_context import DynamoDbContext


class DynamoDbObservability:
    """Emit operation logs without recording keys, values, or credentials."""

    def __init__(
        self,
        observability: AwsObservability | None = None,
        *,
        context: DynamoDbContext | None = None,
    ) -> None:
        self._observability = observability or AwsObservability(
            service_name="shared-dynamodb"
        )
        request_context = self._observability.request_context
        self.context = context or DynamoDbContext(
            tenant_id=request_context.tenant_id,
            request_id=str(request_context.request_id),
            correlation_id=str(request_context.correlation_id),
            trace_id=str(request_context.trace_id),
        )

    def operation_succeeded(self, operation: str, *, table_name: str | None) -> None:
        self._observability.info(
            "dynamodb_operation_succeeded",
            operation=operation,
            **{
                **self._context_log_fields(),
                "table_name": table_name or self.context.table_name,
            },
        )

    def operation_failed(
        self,
        operation: str,
        *,
        table_name: str | None,
        error: Exception,
    ) -> None:
        self._observability.error(
            "dynamodb_operation_failed",
            operation=operation,
            error_type=type(error).__name__,
            **{
                **self._context_log_fields(),
                "table_name": table_name or self.context.table_name,
            },
        )

    def _context_log_fields(self) -> dict[str, str | None]:
        request_context = self._observability.request_context
        return {
            "tenant_id": self.context.tenant_id or request_context.tenant_id,
            "request_id": self.context.request_id or str(request_context.request_id),
            "correlation_id": self.context.correlation_id
            or str(request_context.correlation_id),
            "trace_id": self.context.trace_id or str(request_context.trace_id),
        }
