from __future__ import annotations

from collections.abc import Awaitable, Callable, MutableMapping, Sequence
from typing import Protocol

from identity_service.application.commands import CreateUser, UpdateUser, UserAction
from identity_service.application.dto import UserResponse
from identity_service.application.queries import GetUser, SearchUsers
from identity_service.domain.entities import User
from identity_service.domain.events import UserDomainEvent
from identity_service.domain.exceptions import (
    IdempotencyConflict,
    IdentityDomainError,
    UserAlreadyExists,
    UserNotFound,
)
from identity_service.domain.repositories import UserRepository
from identity_service.domain.value_objects import (
    DisplayName,
    EmailAddress,
    FamilyName,
    GivenName,
    PhoneNumber,
    UserId,
    UserMetadata,
    UserType,
)


class UserEventPublisher(Protocol):
    async def publish(self, event: UserDomainEvent, user: User) -> None: ...


class UserCache(Protocol):
    async def get(self, tenant_id: str, user_id: UserId) -> UserResponse | None: ...
    async def set(self, user: User) -> None: ...
    async def invalidate(self, tenant_id: str, user_id: UserId) -> None: ...


class NullUserEventPublisher:
    def __init__(self) -> None:
        self.events: list[UserDomainEvent] = []

    async def publish(self, event: UserDomainEvent, user: User) -> None:
        self.events.append(event)


class UserHandlers:
    def __init__(
        self,
        repository: UserRepository,
        cache: UserCache,
        publisher: UserEventPublisher,
        tenant_exists: Callable[[str], Awaitable[bool]] | None = None,
        idempotency: MutableMapping[str, tuple[UserId, str]] | None = None,
    ) -> None:
        self.repository = repository
        self.cache = cache
        self.publisher = publisher
        self.tenant_exists = tenant_exists
        self.idempotency = idempotency if idempotency is not None else {}

    async def create(self, command: CreateUser) -> UserResponse:
        if self.tenant_exists is not None and not await self.tenant_exists(command.tenant_id):
            raise IdentityDomainError("Tenant does not exist.")
        fingerprint = command.request.model_dump_json()
        if command.idempotency_key and command.idempotency_key in self.idempotency:
            existing_id, previous = self.idempotency[command.idempotency_key]
            if previous != fingerprint:
                raise IdempotencyConflict("Idempotency-Key was reused with a different request.")
            existing = await self.repository.get_by_id(command.tenant_id, existing_id)
            if existing is not None:
                return UserResponse.from_domain(existing)
        request = command.request
        email = EmailAddress(request.email)
        if await self.repository.get_by_email(command.tenant_id, email):
            raise UserAlreadyExists("Email already exists within this tenant.")
        user = User.create(
            command.tenant_id,
            email,
            DisplayName(request.display_name),
            GivenName(request.given_name),
            FamilyName(request.family_name),
            PhoneNumber(request.phone_number),
            UserType(request.type),
            UserMetadata(request.metadata),
        )
        await self.repository.save(user)
        if command.idempotency_key:
            self.idempotency[command.idempotency_key] = (user.user_id, fingerprint)
        await self._publish(user)
        return UserResponse.from_domain(user)

    async def get(self, query: GetUser) -> UserResponse:
        cached = await self.cache.get(query.tenant_id, query.user_id)
        if cached is not None:
            return cached
        user = await self._require(query.tenant_id, query.user_id)
        await self.cache.set(user)
        return UserResponse.from_domain(user)

    async def update(self, command: UpdateUser) -> UserResponse:
        user = await self._require(command.tenant_id, command.user_id)
        request = command.request
        user.update(
            display_name=(
                DisplayName(request.display_name) if request.display_name is not None else None
            ),
            given_name=GivenName(request.given_name) if request.given_name is not None else None,
            family_name=(
                FamilyName(request.family_name) if request.family_name is not None else None
            ),
            phone_number=(
                PhoneNumber(request.phone_number) if request.phone_number is not None else None
            ),
            metadata=UserMetadata(request.metadata) if request.metadata is not None else None,
        )
        await self.repository.save(user)
        await self.cache.invalidate(command.tenant_id, command.user_id)
        await self._publish(user)
        return UserResponse.from_domain(user)

    async def action(self, command: UserAction, action: str) -> UserResponse:
        user = await self._require(command.tenant_id, command.user_id)
        getattr(user, action)()
        await self.repository.save(user)
        await self.cache.invalidate(command.tenant_id, command.user_id)
        await self._publish(user)
        return UserResponse.from_domain(user)

    async def delete(self, command: UserAction) -> None:
        user = await self._require(command.tenant_id, command.user_id)
        user.delete()
        await self.repository.save(user)
        await self.cache.invalidate(command.tenant_id, command.user_id)
        await self._publish(user)

    async def search(self, query: SearchUsers) -> Sequence[UserResponse]:
        users = await self.repository.search(
            query.tenant_id,
            email=query.email,
            name=query.name,
            status=query.status,
            user_type=query.user_type,
            offset=query.offset,
            limit=query.limit,
        )
        return [UserResponse.from_domain(user) for user in users]

    async def _require(self, tenant_id: str, user_id: UserId) -> User:
        user = await self.repository.get_by_id(tenant_id, user_id)
        if user is None:
            raise UserNotFound(f"User {user_id} was not found.")
        return user

    async def _publish(self, user: User) -> None:
        for event in user.pull_events():
            await self.publisher.publish(event, user)
