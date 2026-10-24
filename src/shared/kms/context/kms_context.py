"""Tenant and observability context for KMS operations."""

from __future__ import annotations

from dataclasses import dataclass

from shared.kms.context.crypto_context import build_encryption_context
from shared.observability.context.request_context import RequestContext


@dataclass(frozen=True, slots=True)
class KmsContext:
    """KMS-safe projection of the server-created request context."""

    tenant_id: str | None
    correlation_id: str
    trace_id: str

    @classmethod
    def from_request_context(cls, request_context: RequestContext) -> KmsContext:
        return cls(
            tenant_id=request_context.tenant_id,
            correlation_id=str(request_context.correlation_id),
            trace_id=str(request_context.trace_id),
        )

    def encryption_context(self, values: dict[str, str] | None = None) -> dict[str, str]:
        return build_encryption_context(values, tenant_id=self.tenant_id)
