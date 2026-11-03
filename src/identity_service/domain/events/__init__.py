"""Domain events."""

from identity_service.domain.events.user_events import (
    UserActivated,
    UserCreated,
    UserDeactivated,
    UserDeleted,
    UserDomainEvent,
    UserSuspended,
    UserUpdated,
)

__all__ = [
    "UserActivated",
    "UserCreated",
    "UserDeactivated",
    "UserDeleted",
    "UserDomainEvent",
    "UserSuspended",
    "UserUpdated",
]
