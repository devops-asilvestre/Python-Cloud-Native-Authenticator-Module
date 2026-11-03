from __future__ import annotations

import asyncio

import pytest

from identity_service.application.commands import CreateUser, UpdateUser, UserAction
from identity_service.application.dto import UserCreateRequest, UserUpdateRequest
from identity_service.application.handlers.user_handlers import NullUserEventPublisher, UserHandlers
from identity_service.application.queries import GetUser, SearchUsers
from identity_service.domain.entities import User
from identity_service.domain.exceptions import (
    IdempotencyConflict,
    IdentityDomainError,
    InvalidUserTransition,
)
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
from identity_service.infrastructure.cache.in_memory_cache import InMemoryUserCache
from identity_service.infrastructure.persistence.in_memory_repository import InMemoryUserRepository


def request(email: str = "User@Example.com") -> UserCreateRequest:
    return UserCreateRequest(
        email=email,
        display_name="Example User",
        given_name="Ex",
        family_name="User",
        phone_number="+5511999999999",
        type="EMPLOYEE",
    )


@pytest.fixture
def handlers() -> UserHandlers:
    return UserHandlers(InMemoryUserRepository(), InMemoryUserCache(), NullUserEventPublisher())


def test_value_objects_normalize_and_validate() -> None:
    assert str(EmailAddress(" User@Example.com ")) == "user@example.com"
    assert str(DisplayName(" Example ")) == "Example"
    with pytest.raises(IdentityDomainError):
        PhoneNumber("11999999999")


def test_status_transition_rules() -> None:
    assert (
        UserStatus.pending().transition_to(UserStatusValue.ACTIVE).value is UserStatusValue.ACTIVE
    )
    with pytest.raises(InvalidUserTransition):
        UserStatus.pending().transition_to(UserStatusValue.DELETED)


def test_user_lifecycle_and_soft_delete(handlers: UserHandlers) -> None:
    async def scenario() -> None:
        created = await handlers.create(CreateUser("tenant-a", request(), "key-1"))
        user_id = UserId(created.user_id)
        await handlers.action(UserAction("tenant-a", user_id), "activate")
        await handlers.action(UserAction("tenant-a", user_id), "suspend")
        await handlers.action(UserAction("tenant-a", user_id), "activate")
        await handlers.action(UserAction("tenant-a", user_id), "deactivate")
        await handlers.delete(UserAction("tenant-a", user_id))
        result = await handlers.get(GetUser("tenant-a", user_id))
        assert result.status == "DELETED"

    asyncio.run(scenario())


def test_handlers_isolate_tenants_and_search(handlers: UserHandlers) -> None:
    async def scenario() -> None:
        created = await handlers.create(CreateUser("tenant-a", request()))
        assert (await handlers.search(SearchUsers("tenant-b"))) == []
        with pytest.raises(IdentityDomainError):
            await handlers.get(GetUser("tenant-b", UserId(created.user_id)))

    asyncio.run(scenario())


def test_idempotency_rejects_changed_payload(handlers: UserHandlers) -> None:
    async def scenario() -> None:
        await handlers.create(CreateUser("tenant-a", request(), "same"))
        with pytest.raises(IdempotencyConflict):
            await handlers.create(CreateUser("tenant-a", request("other@example.com"), "same"))

    asyncio.run(scenario())


def test_update_and_cache(handlers: UserHandlers) -> None:
    async def scenario() -> None:
        created = await handlers.create(CreateUser("tenant-a", request()))
        user_id = UserId(created.user_id)
        updated = await handlers.update(
            UpdateUser("tenant-a", user_id, UserUpdateRequest(display_name="Changed User"))
        )
        assert updated.display_name == "Changed User"
        assert (await handlers.get(GetUser("tenant-a", user_id))).display_name == "Changed User"

    asyncio.run(scenario())


def test_user_aggregate_requires_tenant() -> None:
    with pytest.raises(IdentityDomainError):
        User(
            UserId.generate(),
            "",
            EmailAddress("a@example.com"),
            DisplayName("Example"),
            GivenName("Ab"),
            FamilyName("Cd"),
            PhoneNumber("+5511999999999"),
            UserStatus.pending(),
            UserType.EMPLOYEE,
            UserMetadata({}),
        )


def test_user_aggregate_updates_all_fields_and_ignores_repeated_delete() -> None:
    user = User.create(
        "tenant-a",
        EmailAddress("aggregate@example.com"),
        DisplayName("Aggregate User"),
        GivenName("Ag"),
        FamilyName("User"),
        PhoneNumber("+5511999999999"),
        UserType.EMPLOYEE,
        UserMetadata({}),
    )
    user.pull_events()
    user.activate()
    user.update(
        display_name=DisplayName("Updated User"),
        given_name=GivenName("Up"),
        family_name=FamilyName("Dated"),
        phone_number=PhoneNumber("+5511888888888"),
        metadata=UserMetadata({"updated": True}),
    )
    user.deactivate()
    user.activate()
    user.delete()
    user.delete()
    assert str(user.phone_number) == "+5511888888888"
    assert user.pull_events()
