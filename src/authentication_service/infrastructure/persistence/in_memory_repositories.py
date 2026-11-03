from __future__ import annotations

from authentication_service.domain.aggregates import AuthenticationSession, Credential
from authentication_service.domain.repositories import CredentialRepository, SessionRepository
from authentication_service.domain.value_objects import CredentialId, SessionId


class InMemoryCredentialRepository(CredentialRepository):
    def __init__(self) -> None:
        self.values: dict[tuple[str, str], Credential] = {}

    async def save(self, credential: Credential) -> None:
        self.values[(credential.tenant_id, str(credential.credential_id))] = credential

    async def get_by_id(self, tenant_id: str, credential_id: CredentialId) -> Credential | None:
        return self.values.get((tenant_id, str(credential_id)))

    async def get_by_email(self, tenant_id: str, email: str) -> Credential | None:
        normalized = email.strip().lower()
        return next(
            (value for (scope, _), value in self.values.items()
             if scope == tenant_id and value.email == normalized),
            None,
        )


class InMemorySessionRepository(SessionRepository):
    def __init__(self) -> None:
        self.values: dict[tuple[str, str], AuthenticationSession] = {}

    async def save(self, session: AuthenticationSession) -> None:
        self.values[(session.tenant_id, str(session.session_id))] = session

    async def get(self, tenant_id: str, session_id: SessionId) -> AuthenticationSession | None:
        return self.values.get((tenant_id, str(session_id)))

    async def delete(self, tenant_id: str, session_id: SessionId) -> None:
        self.values.pop((tenant_id, str(session_id)), None)
