"""Tenant and correlation context for DynamoDB operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class DynamoDbContext:
    """Non-secret context fields attached to DynamoDB operation logs."""

    tenant_id: str | None = None
    request_id: str | None = None
    correlation_id: str | None = None
    trace_id: str | None = None
    table_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_log_fields(self) -> dict[str, Any]:
        """Return operation context without exposing item data."""
        return {
            "tenant_id": self.tenant_id,
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "table_name": self.table_name,
        }
