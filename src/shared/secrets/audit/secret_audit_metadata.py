"""Audit details recorded after a secret is read."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class SecretAuditMetadata:
    """Audit metadata for a secret read operation."""

    secret_name: str
    operation: str = "read"
    requested_by: str | None = None
    region: str = "us-east-1"
    account_id: str | None = None
    request_id: str | None = None
    correlation_id: str | None = None
    tenant_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def as_dict(self) -> dict[str, Any]:
        return {
            "secret_name": self.secret_name,
            "operation": self.operation,
            "requested_by": self.requested_by,
            "region": self.region,
            "account_id": self.account_id,
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
            "tenant_id": self.tenant_id,
            "created_at": self.created_at.isoformat(),
        }
