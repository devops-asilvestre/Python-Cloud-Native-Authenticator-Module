from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authentication_service.domain.aggregates import AuthenticationSession, Credential
from authentication_service.domain.repositories import CredentialRepository, SessionRepository
from authentication_service.domain.value_objects import (
    AuthenticationStatus,
    CredentialId,
    PasswordHash,
    SessionId,
    SessionMetadata,
)
from authentication_service.infrastructure.persistence.models import (
    AuthenticationSessionModel,
    CredentialModel,
)


class SqlAlchemyCredentialRepository(CredentialRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, credential: Credential) -> None:
        model = await self.session.get(CredentialModel, str(credential.credential_id))
        if model is None:
            model = CredentialModel(credential_id=str(credential.credential_id))
            self.session.add(model)
        model.tenant_id = credential.tenant_id
        model.user_id = credential.user_id
        model.email = credential.email
        model.password_hash = credential.password_hash.value
        model.status = credential.status.value
        model.failed_attempts = credential.failed_attempts
        model.locked_until = credential.locked_until
        model.created_at = credential.created_at
        model.updated_at = credential.updated_at
        await self.session.flush()

    async def get_by_id(self, tenant_id: str, credential_id: CredentialId) -> Credential | None:
        model = await self.session.scalar(
            select(CredentialModel).where(
                CredentialModel.tenant_id == tenant_id,
                CredentialModel.credential_id == str(credential_id),
            )
        )
        return self._read(model) if model else None

    async def get_by_email(self, tenant_id: str, email: str) -> Credential | None:
        model = await self.session.scalar(
            select(CredentialModel).where(
                CredentialModel.tenant_id == tenant_id,
                CredentialModel.email == email.strip().lower(),
            )
        )
        return self._read(model) if model else None

    @staticmethod
    def _read(model: CredentialModel) -> Credential:
        return Credential(
            CredentialId(model.credential_id), model.tenant_id, model.user_id, model.email,
            PasswordHash(model.password_hash), AuthenticationStatus(model.status),
            model.failed_attempts, model.locked_until, model.created_at, model.updated_at,
        )


class SqlAlchemySessionRepository(SessionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, session: AuthenticationSession) -> None:
        model = await self.session.get(AuthenticationSessionModel, str(session.session_id))
        if model is None:
            model = AuthenticationSessionModel(session_id=str(session.session_id))
            self.session.add(model)
        model.tenant_id = session.tenant_id
        model.user_id = session.user_id
        model.created_at = session.created_at
        model.expires_at = session.expires_at
        model.active = session.active
        model.user_agent = session.metadata.user_agent
        model.ip_address = session.metadata.ip_address
        await self.session.flush()

    async def get(self, tenant_id: str, session_id: SessionId) -> AuthenticationSession | None:
        model = await self.session.scalar(
            select(AuthenticationSessionModel).where(
                AuthenticationSessionModel.tenant_id == tenant_id,
                AuthenticationSessionModel.session_id == str(session_id),
            )
        )
        if model is None:
            return None
        return AuthenticationSession(
            SessionId(model.session_id), model.tenant_id, model.user_id, model.created_at,
            model.expires_at, SessionMetadata(model.user_agent, model.ip_address), model.active,
        )

    async def delete(self, tenant_id: str, session_id: SessionId) -> None:
        model = await self.session.scalar(
            select(AuthenticationSessionModel).where(
                AuthenticationSessionModel.tenant_id == tenant_id,
                AuthenticationSessionModel.session_id == str(session_id),
            )
        )
        if model is not None:
            model.active = False
            await self.session.flush()
