"""Schema model for EventBridge event contracts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EventContractSchema:
    """Minimal contract definition used to validate event compatibility."""

    event_type: str
    version: str
    required_fields: tuple[str, ...] = (
        "event_id",
        "tenant_id",
        "event_type",
        "version",
    )

    def validate(
        self,
        *,
        tenant_id: str | None,
        correlation_id: str | None,
        trace_id: str | None,
    ) -> None:
        if not self.event_type or not self.event_type.strip():
            raise ValueError("event_type is required.")
        if not self.version or not self.version.strip():
            raise ValueError("version is required.")
        if not tenant_id or not tenant_id.strip():
            raise ValueError("tenant_id is required.")
        if not correlation_id or not str(correlation_id).strip():
            raise ValueError("correlation_id is required.")
        if not trace_id or not str(trace_id).strip():
            raise ValueError("trace_id is required.")
