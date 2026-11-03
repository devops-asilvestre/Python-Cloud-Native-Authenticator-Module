from __future__ import annotations

import builtins
from dataclasses import dataclass, field
from datetime import UTC, datetime

from identity_service.domain.events import (
    UserActivated,
    UserCreated,
    UserDeactivated,
    UserDeleted,
    UserDomainEvent,
    UserSuspended,
    UserUpdated,
)
from identity_service.domain.exceptions import IdentityDomainError
from identity_service.domain.value_objects import (
    DisplayName,
    EmailAddress,
    FamilyName,
    GivenName,
    PhoneNumber,
    UserId,
    UserMetadata,
    UserStatus,
    UserStatusValue,
    UserType,
)


@dataclass(slots=True)
class User:
    user_id: UserId
    tenant_id: str
    email: EmailAddress
    display_name: DisplayName
    given_name: GivenName
    family_name: FamilyName
    phone_number: PhoneNumber
    status: UserStatus
    type: UserType
    metadata: UserMetadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _events: list[UserDomainEvent] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        if not self.tenant_id.strip():
            raise IdentityDomainError("tenant_id is required.")

    @classmethod
    def create(
        cls,
        tenant_id: str,
        email: EmailAddress,
        display_name: DisplayName,
        given_name: GivenName,
        family_name: FamilyName,
        phone_number: PhoneNumber,
        user_type: UserType,
        metadata: UserMetadata,
    ) -> User:
        user = cls(
            UserId.generate(),
            tenant_id,
            email,
            display_name,
            given_name,
            family_name,
            phone_number,
            UserStatus.pending(),
            user_type,
            metadata,
        )
        user._events.append(UserCreated.for_user(user.user_id, user.tenant_id))
        return user

    def update(
        self,
        *,
        display_name: DisplayName | None = None,
        given_name: GivenName | None = None,
        family_name: FamilyName | None = None,
        phone_number: PhoneNumber | None = None,
        metadata: UserMetadata | None = None,
    ) -> None:
        if self.status.value is UserStatusValue.DELETED:
            raise IdentityDomainError("A deleted user cannot be updated.")
        if display_name is not None:
            self.display_name = display_name
        if given_name is not None:
            self.given_name = given_name
        if family_name is not None:
            self.family_name = family_name
        if phone_number is not None:
            self.phone_number = phone_number
        if metadata is not None:
            self.metadata = metadata
        self.updated_at = datetime.now(UTC)
        self._events.append(UserUpdated.for_user(self.user_id, self.tenant_id))

    def activate(self) -> None:
        self._transition(UserStatusValue.ACTIVE, UserActivated)

    def suspend(self) -> None:
        self._transition(UserStatusValue.SUSPENDED, UserSuspended)

    def deactivate(self) -> None:
        self._transition(UserStatusValue.INACTIVE, UserDeactivated)

    def delete(self) -> None:
        if self.status.value is UserStatusValue.DELETED:
            return
        self.status = self.status.transition_to(UserStatusValue.DELETED)
        self.updated_at = datetime.now(UTC)
        self._events.append(UserDeleted.for_user(self.user_id, self.tenant_id))

    def pull_events(self) -> tuple[UserDomainEvent, ...]:
        events = tuple(self._events)
        self._events.clear()
        return events

    def _transition(
        self,
        target: UserStatusValue,
        event_factory: builtins.type[UserDomainEvent],
    ) -> None:
        self.status = self.status.transition_to(target)
        self.updated_at = datetime.now(UTC)
        self._events.append(event_factory.for_user(self.user_id, self.tenant_id))
