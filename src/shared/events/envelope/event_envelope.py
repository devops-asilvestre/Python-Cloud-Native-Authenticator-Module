"""Transport-independent event envelope."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from shared.events.metadata.event_context import EventContext
from shared.events.metadata.event_metadata import EventMetadata
from shared.events.metadata.event_version import EventVersion
from shared.events.validation.naming_validator import EventNamingConvention
from shared.observability.correlation.correlation_id import CorrelationId
from shared.observability.correlation.trace_id import TraceId
from shared.observability.logging.logger_contract import LoggerContract

if TYPE_CHECKING:
    from shared.events.contracts.domain_event_contract import DomainEventContract


class EventEnvelope(BaseModel):
    """Versioned event data with mandatory tenant and traceability fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: UUID
    event_type: str = Field(min_length=1)
    event_version: EventVersion
    correlation_id: CorrelationId
    trace_id: TraceId
    tenant_id: str = Field(min_length=1)
    occurred_at: datetime
    source_service: str = Field(min_length=1)
    payload: dict[str, object]
    request_id: str | None = None
    causation_id: UUID | None = None
    span_id: str = Field(default_factory=lambda: uuid4().hex[:16], pattern=r"^[0-9a-f]{16}$")
    parent_span_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{16}$")
    sampled: bool = True

    @field_validator("occurred_at")
    @classmethod
    def require_aware_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Event occurred_at must be timezone-aware.")
        return value.astimezone(UTC)

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value: str) -> str:
        return EventNamingConvention.validate(value)

    @field_validator("tenant_id", "source_service")
    @classmethod
    def require_non_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Event tenant_id and source_service cannot be blank.")
        return value

    @property
    def metadata(self) -> EventMetadata:
        """Return common metadata for code using the legacy event contract."""

        return EventMetadata(
            event_id=self.event_id,
            occurred_at=self.occurred_at,
            correlation_id=self.correlation_id,
            trace_id=self.trace_id,
            tenant_id=self.tenant_id,
            source_service=self.source_service,
            request_id=self.request_id,
            causation_id=self.causation_id,
            span_id=self.span_id,
            parent_span_id=self.parent_span_id,
            sampled=self.sampled,
        )

    @classmethod
    def from_metadata(
        cls,
        *,
        event_type: str,
        event_version: EventVersion,
        metadata: EventMetadata,
        payload: dict[str, object],
    ) -> EventEnvelope:
        return cls(
            event_id=metadata.event_id,
            event_type=event_type,
            event_version=event_version,
            correlation_id=metadata.correlation_id,
            trace_id=metadata.trace_id,
            tenant_id=metadata.tenant_id,
            occurred_at=metadata.occurred_at,
            source_service=metadata.source_service,
            request_id=metadata.request_id,
            causation_id=metadata.causation_id,
            span_id=metadata.span_id,
            parent_span_id=metadata.parent_span_id,
            sampled=metadata.sampled,
            payload=payload,
        )

    @classmethod
    def from_domain_event(
        cls,
        event: DomainEventContract,
        *,
        event_type: str,
        event_version: EventVersion,
        context: EventContext,
        source_service: str,
        payload: dict[str, object],
    ) -> EventEnvelope:
        """Map a shared-kernel event using an explicit allowlisted payload."""

        return cls(
            event_id=event.event_id,
            event_type=event_type,
            event_version=event_version,
            correlation_id=context.correlation_id,
            trace_id=context.trace_id,
            tenant_id=context.tenant_id,
            occurred_at=event.occurred_at,
            source_service=source_service,
            request_id=context.request_id,
            causation_id=context.correlation.causation_id,
            span_id=context.span_id,
            parent_span_id=context.parent_span_id,
            sampled=context.sampled,
            payload=payload,
        )

    def log(self, logger: LoggerContract, *, action: str = "event.processed") -> None:
        """Log traceability fields only; the event payload is never logged."""

        logger.info(
            action,
            event_id=str(self.event_id),
            event_type=self.event_type,
            event_version=str(self.event_version),
            correlation_id=str(self.correlation_id),
            trace_id=str(self.trace_id),
            source_service=self.source_service,
        )
