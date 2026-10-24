"""Context object describing a secret access operation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SecretContext:
    """Operational context for secret resolution, audit, and tracing."""

    region: str = "us-east-1"
    account_id: str | None = None
    tenant_id: str | None = None
    request_id: str | None = None
    correlation_id: str | None = None
    operation: str = "read"
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "region": self.region,
            "account_id": self.account_id,
            "tenant_id": self.tenant_id,
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
            "operation": self.operation,
        }
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        return payload
