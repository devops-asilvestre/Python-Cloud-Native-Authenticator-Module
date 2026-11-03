from __future__ import annotations

import asyncio
from collections.abc import Callable

from authentication_service.domain.events import AuthenticationDomainEvent, event_payload
from shared.eventbus.publishers.eventbridge_publisher import EventBridgePublisher
from shared.events import EventEnvelope
from shared.events.metadata.event_context import EventContext
from shared.events.metadata.event_version import EventVersion


class EventBridgeAuthenticationPublisher:
    """Translate authentication events into the shared versioned envelope."""

    def __init__(
        self,
        publisher: EventBridgePublisher,
        context_factory: Callable[[str], EventContext],
        *,
        source_service: str = "authentication-service",
    ) -> None:
        self._publisher = publisher
        self._context_factory = context_factory
        self._source_service = source_service

    async def publish(self, event: AuthenticationDomainEvent) -> None:
        context = self._context_factory(event.tenant_id)
        envelope = EventEnvelope(
            event_id=event.event_id,
            event_type=self._event_type(event),
            event_version=EventVersion.parse("1.0.0"),
            correlation_id=context.correlation_id,
            trace_id=context.trace_id,
            tenant_id=event.tenant_id,
            occurred_at=event.occurred_at,
            source_service=self._source_service,
            request_id=context.request_id,
            causation_id=context.correlation.causation_id,
            span_id=context.span_id,
            parent_span_id=context.parent_span_id,
            sampled=context.sampled,
            payload=event_payload(event),
        )
        await asyncio.to_thread(self._publisher.publish, envelope)

    @staticmethod
    def _event_type(event: AuthenticationDomainEvent) -> str:
        names = {
            "AuthenticationSucceeded": "authentication.authentication.succeeded",
            "AuthenticationFailed": "authentication.authentication.failed",
            "SessionCreated": "authentication.session.created",
            "SessionTerminated": "authentication.session.terminated",
            "PasswordChanged": "authentication.credential.password-changed",
        }
        return names[event.event_type]
