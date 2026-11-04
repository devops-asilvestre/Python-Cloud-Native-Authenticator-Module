"""Safe metadata emitted for cryptographic operation audit events."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime

from shared.observability.context.request_context import RequestContext


@dataclass(frozen=True, slots=True)
class KmsAuditMetadata:
    """Audit fields that intentionally exclude cryptographic material."""

    operation: str
    key_id: str
    key_alias: str | None
    account_id: str | None
    region: str
    correlation_id: str
    trace_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def from_request(
        cls,
        *,
        operation: str,
        key_id: str,
        key_alias: str | None,
        account_id: str | None,
        region: str,
        request_context: RequestContext,
    ) -> KmsAuditMetadata:
        return cls(
            operation=operation,
            key_id=key_id,
            key_alias=key_alias,
            account_id=account_id,
            region=region,
            correlation_id=str(request_context.correlation_id),
            trace_id=str(request_context.trace_id),
        )

    def to_log_fields(self) -> dict[str, str | None]:
        fields = asdict(self)
        timestamp = fields["timestamp"]
        fields["timestamp"] = timestamp.isoformat() if isinstance(timestamp, datetime) else None
        return fields
