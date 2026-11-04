from __future__ import annotations

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from authentication_service.domain.events import AuthenticationDomainEvent
from authentication_service.infrastructure.persistence.models import AuthenticationAuditModel


class SqlAlchemyAuthenticationAuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(self, event: AuthenticationDomainEvent) -> None:
        reason = getattr(event, "reason", None)
        self._session.add(
            AuthenticationAuditModel(
                audit_id=str(uuid4()),
                tenant_id=event.tenant_id,
                event_id=str(event.event_id),
                event_type=event.event_type,
                user_id=event.user_id,
                occurred_at=event.occurred_at,
                reason=reason,
                source="authentication-service",
            )
        )
        await self._session.flush()
