from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from authentication_service.domain.events import (
    AuthenticationDomainEvent,
    AuthenticationFailed,
    PasswordChanged,
)
from authentication_service.domain.exceptions import AuthenticationBlocked, InvalidCredentialState
from authentication_service.domain.value_objects import (
    AuthenticationStatus,
    CredentialId,
    LoginAttempt,
    PasswordHash,
    PasswordPolicy,
)


@dataclass(slots=True)
class Credential:
    credential_id: CredentialId
    tenant_id: str
    user_id: str
    email: str
    password_hash: PasswordHash
    status: AuthenticationStatus = AuthenticationStatus.ACTIVE
    failed_attempts: int = 0
    locked_until: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _events: list[AuthenticationDomainEvent] = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls, tenant_id: str, user_id: str, email: str, password: str,
        policy: PasswordPolicy | None = None,
    ) -> Credential:
        normalized_email = email.strip().lower()
        if not tenant_id.strip() or not user_id.strip() or "@" not in normalized_email:
            raise InvalidCredentialState("Tenant, user and a valid email are required.")
        (policy or PasswordPolicy()).validate(password)
        return cls(
            CredentialId.generate(), tenant_id, user_id, normalized_email,
            PasswordHash.from_password(password),
        )

    def verify(
        self, password: str, *, now: datetime | None = None, max_attempts: int = 5,
        lock_duration: timedelta = timedelta(minutes=15),
    ) -> bool:
        current = (now or datetime.now(UTC)).astimezone(UTC)
        self._unlock_if_due(current)
        if self.status is AuthenticationStatus.DISABLED:
            self._events.append(
                AuthenticationFailed.create(
                    self.tenant_id, self.user_id, reason="credential_disabled"
                )
            )
            return False
        if self.locked_until is not None and current < self.locked_until:
            self._events.append(
                AuthenticationFailed.create(
                    self.tenant_id, self.user_id, reason="temporarily_locked"
                )
            )
            raise AuthenticationBlocked("Authentication is temporarily blocked.")
        valid = self.password_hash.verify(password)
        self.record_attempt(LoginAttempt(valid, current))
        if not valid:
            self._events.append(AuthenticationFailed.create(self.tenant_id, self.user_id))
            if self.failed_attempts >= max_attempts:
                self.status = AuthenticationStatus.LOCKED
                self.locked_until = current + lock_duration
        return valid

    def disable(self) -> None:
        self.status = AuthenticationStatus.DISABLED
        self.updated_at = datetime.now(UTC)

    def enable(self) -> None:
        self.status = AuthenticationStatus.ACTIVE
        self.locked_until = None
        self.failed_attempts = 0
        self.updated_at = datetime.now(UTC)

    def change_password(self, password: str, policy: PasswordPolicy | None = None) -> None:
        (policy or PasswordPolicy()).validate(password)
        self.password_hash = PasswordHash.from_password(password)
        self.updated_at = datetime.now(UTC)
        self._events.append(PasswordChanged.create(self.tenant_id, self.user_id))

    def unlock_if_due(self, now: datetime | None = None) -> None:
        self._unlock_if_due((now or datetime.now(UTC)).astimezone(UTC))

    def pull_events(self) -> tuple[AuthenticationDomainEvent, ...]:
        events = tuple(self._events)
        self._events.clear()
        return events

    def record_attempt(self, attempt: LoginAttempt) -> None:
        self.failed_attempts = 0 if attempt.succeeded else self.failed_attempts + 1
        self.updated_at = attempt.occurred_at

    def _unlock_if_due(self, now: datetime) -> None:
        if self.locked_until is not None and now >= self.locked_until:
            self.locked_until = None
            self.failed_attempts = 0
            self.status = AuthenticationStatus.ACTIVE
