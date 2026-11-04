"""Publish validated event envelopes to EventBridge."""

from __future__ import annotations

import json
from base64 import b64encode
from collections.abc import Callable
from time import perf_counter
from typing import Any

from shared.eventbus.archive.archive_metadata import ArchiveMetadata
from shared.eventbus.audit.event_auditor import EventAuditor
from shared.eventbus.exceptions.eventbridge_exception import (
    EventBridgePublishException,
    EventValidationException,
)
from shared.eventbus.fanout.fanout_engine import FanoutEngine
from shared.eventbus.filtering.event_filter import EventFilter
from shared.eventbus.models.publish_result import PublishResult
from shared.eventbus.observability.event_observability import EventObservability
from shared.eventbus.providers.eventbridge_provider import EventBridgeProvider
from shared.eventbus.replay.replay_metadata import ReplayMetadata
from shared.eventbus.routing.event_bus_resolver import EventBusResolver
from shared.eventbus.routing.event_router import EventRouter
from shared.eventbus.settings.eventbridge_settings import EventBridgeSettings
from shared.eventbus.validation.event_schema_enforcer import EventSchemaEnforcer
from shared.events import EventEnvelope
from shared.observability.logging.structured_logger import StructuredLogger


class EventBridgePublisher:
    """Corporate EventBridge publisher that validates and routes events before publication."""

    def __init__(
        self,
        settings: EventBridgeSettings,
        *,
        router: EventRouter | None = None,
        filter_: EventFilter | None = None,
        enforcer: EventSchemaEnforcer | None = None,
        auditor: EventAuditor | None = None,
        fanout: FanoutEngine | None = None,
        provider: EventBridgeProvider | None = None,
        payload_encryptor: Callable[[bytes], bytes] | None = None,
        bus_resolver: EventBusResolver | None = None,
        logger: StructuredLogger | None = None,
    ) -> None:
        self.settings = settings
        self.router = router or EventRouter()
        self.filter = filter_
        self.enforcer = enforcer or EventSchemaEnforcer()
        self.auditor = auditor or EventAuditor()
        self.fanout = fanout or FanoutEngine()
        self.provider = provider or EventBridgeProvider(settings)
        self.bus_resolver = bus_resolver or EventBusResolver(settings)
        self.payload_encryptor = payload_encryptor
        self.last_observability = EventObservability()
        self.last_replay_metadata: ReplayMetadata | None = None
        self.archive_metadata = ArchiveMetadata(
            archive_enabled=settings.archive_enabled,
            retention_days=settings.retention_days,
        )
        self.logger = logger or StructuredLogger("shared-eventbridge-publisher")

    def validate_envelope(self, event: EventEnvelope) -> EventEnvelope:
        return self.enforcer.validate(event)

    def validate_schema(self, event: EventEnvelope) -> EventEnvelope:
        return self.enforcer.validate_schema(event)

    def validate_version(self, event: EventEnvelope) -> EventEnvelope:
        return self.enforcer.validate_version(event)

    def validate_tenant(self, event: EventEnvelope) -> EventEnvelope:
        return self.enforcer.validate_tenant(event)

    def publish(self, event: EventEnvelope) -> PublishResult:
        started = perf_counter()
        self.validate_envelope(event)
        if self.filter is not None and not self.filter.matches(event):
            raise EventValidationException(
                "Event does not satisfy the configured EventBridge filters."
            )
        routing_started = perf_counter()
        preliminary = self.router.route(event, bus_name=self.settings.bus_name)
        bus = self.bus_resolver.resolve(
            event.tenant_id,
            preliminary.category,
            event.event_type,
        )
        decision = self.router.route(event, bus_name=bus.bus_name)
        routing_latency_ms = int((perf_counter() - routing_started) * 1000)
        if not event.tenant_id or not event.tenant_id.strip():
            raise EventValidationException(
                "Tenant isolation is mandatory for EventBridge publication."
            )
        if decision.routing_mode not in {"unicast", "multicast", "broadcast"}:
            raise EventValidationException("Routing decision is invalid.")
        self.auditor.audit(event)
        self.fanout.fanout(event, decision.consumers)
        detail = json.dumps(
            event.model_dump(mode="json"),
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        if self.payload_encryptor is not None:
            detail = json.dumps(
                {"encrypted_payload": b64encode(self.payload_encryptor(detail)).decode("ascii")},
                separators=(",", ":"),
            ).encode("utf-8")
        entry = {
            "Source": event.source_service,
            "DetailType": event.event_type,
            "Detail": detail.decode("utf-8"),
            "EventBusName": decision.bus_name,
        }
        try:
            response = self.provider.put_events([entry])
        except Exception as exc:
            self.logger.error(
                "eventbridge_publish_failed",
                event_id=str(event.event_id),
                event_type=event.event_type,
                tenant_id=event.tenant_id,
                error_type=type(exc).__name__,
            )
            raise EventBridgePublishException(
                "EventBridge PutEvents failed."
            ) from exc
        if response.get("FailedEntryCount", 0) != 0:
            raise EventBridgePublishException("EventBridge rejected the event entry.")
        entries = response.get("Entries")
        if not isinstance(entries, list) or not entries or not isinstance(entries[0], dict):
            raise EventBridgePublishException("EventBridge returned no publication result.")
        event_id = entries[0].get("EventId")
        if not isinstance(event_id, str) or not event_id:
            raise EventBridgePublishException("EventBridge returned no event ID.")
        elapsed_ms = int((perf_counter() - started) * 1000)
        self.last_observability = EventObservability(
            publish_latency_ms=elapsed_ms,
            routing_latency_ms=routing_latency_ms,
            publish_success=True,
            retry_count=0,
        )
        self.logger.info(
            "eventbridge_publish_succeeded",
            event_id=str(event.event_id),
            event_type=event.event_type,
            event_version=str(event.event_version),
            tenant_id=event.tenant_id,
            correlation_id=str(event.correlation_id),
            trace_id=str(event.trace_id),
            publish_latency_ms=elapsed_ms,
            routing_latency_ms=routing_latency_ms,
        )
        self.last_replay_metadata = ReplayMetadata(
            event_id=str(event.event_id),
            event_type=event.event_type,
            version=str(event.event_version),
            timestamp=event.occurred_at.isoformat(),
            tenant=event.tenant_id,
        )
        return PublishResult(
            message_id=event_id,
            bus_name=decision.bus_name,
            sequence_number=event_id,
            success=True,
        )

    def publish_many(self, events: list[EventEnvelope]) -> list[PublishResult]:
        return [self.publish(event) for event in events]

    def publish_raw(
        self,
        *,
        payload: dict[str, Any],
        event: EventEnvelope | None = None,
    ) -> PublishResult:
        if event is None:
            raise EventValidationException(
                "Event envelope is required for EventBridge publication."
            )
        _ = payload
        return self.publish(event)
