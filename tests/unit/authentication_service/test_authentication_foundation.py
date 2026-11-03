from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

import pytest

from authentication_service.application.authentication_service import (
    AuthenticationApplicationService,
)
from authentication_service.application.ports import InMemoryAuthenticationAuditSink
from authentication_service.domain.events import (
    AuthenticationFailed,
    AuthenticationSucceeded,
    SessionCreated,
    SessionTerminated,
)
from authentication_service.domain.exceptions import AuthenticationBlocked, CredentialNotFound
from authentication_service.domain.value_objects import PasswordPolicy, SessionId
from authentication_service.infrastructure.persistence.in_memory_repositories import (
    InMemoryCredentialRepository,
    InMemorySessionRepository,
)


@pytest.fixture
def repositories() -> tuple[InMemoryCredentialRepository, InMemorySessionRepository]:
    return InMemoryCredentialRepository(), InMemorySessionRepository()


def test_authentication_audits_success_and_session_lifecycle(
    repositories: tuple[InMemoryCredentialRepository, InMemorySessionRepository],
) -> None:
    credentials, sessions = repositories
    audit = InMemoryAuthenticationAuditSink()
    service = AuthenticationApplicationService(credentials, sessions, audit_sink=audit)

    async def scenario() -> None:
        await service.create_credential(
            "tenant-a", "user-a", "person@example.com", "StrongPass1!"
        )
        result = await service.authenticate("tenant-a", "person@example.com", "StrongPass1!")
        await service.terminate_session("tenant-a", SessionId(result.session_id))

    asyncio.run(scenario())

    assert any(isinstance(event, AuthenticationSucceeded) for event in audit.events)
    assert any(isinstance(event, SessionCreated) for event in audit.events)
    assert any(isinstance(event, SessionTerminated) for event in audit.events)
    assert all("password" not in repr(event).lower() for event in audit.events)


def test_failed_attempts_lock_and_unlock_credential(
    repositories: tuple[InMemoryCredentialRepository, InMemorySessionRepository],
) -> None:
    credentials, sessions = repositories
    service = AuthenticationApplicationService(credentials, sessions)
    async def scenario() -> None:
        credential = await service.create_credential(
            "tenant-a", "user-a", "person@example.com", "StrongPass1!"
        )
        for _ in range(5):
            with pytest.raises(CredentialNotFound):
                await service.authenticate("tenant-a", "person@example.com", "wrong")
        with pytest.raises(AuthenticationBlocked):
            await service.authenticate("tenant-a", "person@example.com", "wrong")
        credential.unlock_if_due(datetime.now(UTC) + timedelta(minutes=16))
        await credentials.save(credential)
        result = await service.authenticate("tenant-a", "person@example.com", "StrongPass1!")
        assert result.user_id == "user-a"

    asyncio.run(scenario())


def test_password_policy_rejects_weak_password() -> None:
    with pytest.raises(ValueError):
        PasswordPolicy().validate("weak")


def test_unknown_user_emits_generic_failure_event(
    repositories: tuple[InMemoryCredentialRepository, InMemorySessionRepository],
) -> None:
    credentials, sessions = repositories
    audit = InMemoryAuthenticationAuditSink()
    service = AuthenticationApplicationService(credentials, sessions, audit_sink=audit)

    async def scenario() -> None:
        with pytest.raises(CredentialNotFound):
            await service.authenticate("tenant-a", "unknown@example.com", "wrong")

    asyncio.run(scenario())

    assert len(audit.events) == 1
    assert isinstance(audit.events[0], AuthenticationFailed)
    assert audit.events[0].reason == "invalid_credentials"
