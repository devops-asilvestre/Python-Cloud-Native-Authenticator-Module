from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from time import perf_counter
from uuid import uuid4

from authentication_service.application.ports import (
    AllowAllAuthenticationRateLimiter,
    AuthenticationAuditSink,
    AuthenticationEventPublisher,
    AuthenticationLogger,
    AuthenticationMetrics,
    AuthenticationRateLimiter,
    IdentityDirectory,
    NullAuthenticationEventPublisher,
    NullAuthenticationMetrics,
    NullIdentityDirectory,
    NullTenantValidator,
    TenantValidator,
)
from authentication_service.domain.aggregates import AuthenticationSession, Credential
from authentication_service.domain.events import (
    AuthenticationDomainEvent,
    AuthenticationFailed,
    AuthenticationSucceeded,
)
from authentication_service.domain.exceptions import (
    AuthenticationBlocked,
    CredentialNotFound,
    SessionNotFound,
)
from authentication_service.domain.repositories import CredentialRepository, SessionRepository
from authentication_service.domain.value_objects import PasswordPolicy, SessionId, SessionMetadata
from shared.cache.contracts.session_cache_contract import SessionCacheContract


@dataclass(frozen=True, slots=True)
class AuthenticationResult:
    session_id: str
    user_id: str
    expires_at: str


class AuthenticationApplicationService:
    def __init__(
        self,
        credentials: CredentialRepository,
        sessions: SessionRepository,
        *,
        publisher: AuthenticationEventPublisher | None = None,
        tenant_validator: TenantValidator | None = None,
        identity_directory: IdentityDirectory | None = None,
        audit_sink: AuthenticationAuditSink | None = None,
        logger: AuthenticationLogger | None = None,
        session_cache: SessionCacheContract | None = None,
        metrics: AuthenticationMetrics | None = None,
        rate_limiter: AuthenticationRateLimiter | None = None,
        password_policy: PasswordPolicy | None = None,
        session_ttl: timedelta = timedelta(hours=8),
    ) -> None:
        self._credentials = credentials
        self._sessions = sessions
        self._publisher = publisher or NullAuthenticationEventPublisher()
        self._tenant_validator = tenant_validator or NullTenantValidator()
        self._identity_directory = identity_directory or NullIdentityDirectory()
        self._audit_sink = audit_sink
        self._logger = logger
        self._session_cache = session_cache
        self._metrics = metrics or NullAuthenticationMetrics()
        self._rate_limiter = rate_limiter or AllowAllAuthenticationRateLimiter()
        self._password_policy = password_policy or PasswordPolicy()
        self._session_ttl = session_ttl

    async def create_credential(
        self, tenant_id: str, user_id: str, email: str, password: str
    ) -> Credential:
        await self._tenant_validator.ensure_active(tenant_id)
        await self._identity_directory.ensure_active_user(tenant_id, user_id)
        credential = Credential.create(
            tenant_id, user_id, email, password, self._password_policy
        )
        await self._credentials.save(credential)
        await self._publish(credential)
        return credential

    async def authenticate(
        self, tenant_id: str, email: str, password: str, *,
        metadata: SessionMetadata | None = None,
        ip_address: str | None = None,
    ) -> AuthenticationResult:
        await self._tenant_validator.ensure_active(tenant_id)
        started = perf_counter()
        allowed = await self._rate_limiter.allow(tenant_id, email, ip_address)
        if not allowed:
            self._metrics.observe("authentication.rate_limited", 1.0, tenant_id=tenant_id)
            raise CredentialNotFound("Invalid credentials.")
        credential = await self._credentials.get_by_email(tenant_id, email)
        if credential is None:
            await self._emit(AuthenticationFailed.create(tenant_id, reason="invalid_credentials"))
            self._metrics.observe("authentication.failed", 1.0, tenant_id=tenant_id)
            raise CredentialNotFound("Invalid credentials.")
        try:
            valid = credential.verify(password)
        except AuthenticationBlocked:
            await self._credentials.save(credential)
            await self._publish(credential)
            raise
        if not valid:
            await self._credentials.save(credential)
            await self._publish(credential)
            self._metrics.observe("authentication.failed", 1.0, tenant_id=tenant_id)
            raise CredentialNotFound("Invalid credentials.")
        session = AuthenticationSession.create(
            tenant_id, credential.user_id, ttl=self._session_ttl, metadata=metadata
        )
        await self._credentials.save(credential)
        await self._sessions.save(session)
        if self._session_cache is not None:
            await self._session_cache.set_session(
                tenant_id, str(session.session_id), session,
                ttl_seconds=int(self._session_ttl.total_seconds()),
            )
        await self._publish(credential)
        await self._publish(session)
        await self._emit(
            AuthenticationSucceeded(
                tenant_id,
                datetime.now(UTC),
                uuid4(),
                credential.user_id,
                str(session.session_id),
            )
        )
        self._metrics.observe(
            "authentication.succeeded",
            1.0,
            tenant_id=tenant_id,
        )
        self._metrics.observe(
            "authentication.duration_ms",
            (perf_counter() - started) * 1000,
            tenant_id=tenant_id,
        )
        return AuthenticationResult(
            str(session.session_id), session.user_id, session.expires_at.isoformat()
        )

    async def terminate_session(self, tenant_id: str, session_id: SessionId) -> None:
        session = await self._sessions.get(tenant_id, session_id)
        if session is None:
            raise SessionNotFound("Session not found.")
        session.terminate()
        await self._sessions.save(session)
        if self._session_cache is not None:
            await self._session_cache.delete_session(tenant_id, str(session_id))
        await self._publish(session)

    async def get_session(self, tenant_id: str, session_id: SessionId) -> AuthenticationSession:
        session = await self._sessions.get(tenant_id, session_id)
        if session is None and self._session_cache is not None:
            cached = await self._session_cache.get_session(tenant_id, str(session_id))
            if isinstance(cached, AuthenticationSession):
                session = cached
        if session is None or not session.is_valid():
            raise SessionNotFound("Session not found.")
        return session

    async def change_password(self, tenant_id: str, credential_id: str, password: str) -> None:
        from authentication_service.domain.value_objects import CredentialId

        credential = await self._credentials.get_by_id(tenant_id, CredentialId(credential_id))
        if credential is None:
            raise CredentialNotFound("Credential not found.")
        credential.change_password(password, self._password_policy)
        await self._credentials.save(credential)
        await self._publish(credential)

    async def _publish(self, aggregate: Credential | AuthenticationSession) -> None:
        for event in aggregate.pull_events():
            await self._emit(event)

    async def _emit(self, event: AuthenticationDomainEvent) -> None:
        await self._publisher.publish(event)
        if self._audit_sink is not None:
            await self._audit_sink.record(event)
        if self._logger is not None:
            self._logger.info(
                "authentication_event",
                event_type=event.event_type,
                tenant_id=event.tenant_id,
                user_id=event.user_id,
            )
