from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from starlette.requests import Request

from identity_service.application.dto import UserCreateRequest, UserUpdateRequest
from identity_service.application.handlers.user_handlers import (
    NullUserEventPublisher,
    UserHandlers,
)
from identity_service.domain.exceptions import (
    IdempotencyConflict,
    IdentityDomainError,
    InvalidUserTransition,
    UserAlreadyExists,
)
from identity_service.domain.value_objects import UserId
from identity_service.infrastructure.cache.in_memory_cache import InMemoryUserCache
from identity_service.infrastructure.persistence.in_memory_repository import (
    InMemoryUserRepository,
)
from identity_service.presentation.api import router as api


def _request(tenant_id: str = "tenant-a") -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/users",
            "headers": [],
            "state": {"tenant_context": SimpleNamespace(tenant_id=tenant_id)},
        }
    )


def _handlers() -> UserHandlers:
    return UserHandlers(InMemoryUserRepository(), InMemoryUserCache(), NullUserEventPublisher())


def _payload() -> UserCreateRequest:
    return UserCreateRequest(
        email="api@example.com",
        display_name="API User",
        given_name="Api",
        family_name="User",
        phone_number="+5511999999999",
        type="EMPLOYEE",
    )


def test_api_requires_trusted_tenant_and_rejects_mismatch() -> None:
    async def scenario() -> None:
        handlers = _handlers()
        missing = Request({"type": "http", "state": {}})
        try:
            await api.create_user(missing, _payload(), handlers, None, None)
        except Exception as exc:
            assert getattr(exc, "status_code", None) == 403
        else:
            raise AssertionError("missing trusted tenant context was accepted")

        try:
            await api.create_user(_request(), _payload(), handlers, "tenant-b", None)
        except Exception as exc:
            assert getattr(exc, "status_code", None) == 403
        else:
            raise AssertionError("mismatched tenant header was accepted")

    asyncio.run(scenario())


def test_api_validation_and_not_found_paths() -> None:
    async def scenario() -> None:
        handlers = _handlers()
        request = _request()
        try:
            await api.get_user(request, "not-a-uuid", handlers, None)
        except Exception as exc:
            assert getattr(exc, "status_code", None) == 422
        else:
            raise AssertionError("invalid user id was accepted")
        try:
            await api.search_users(request, None, None, None, None, -1, 10, handlers, None)
        except Exception as exc:
            assert getattr(exc, "status_code", None) == 422
        else:
            raise AssertionError("invalid offset was accepted")
        try:
            await api.get_user(request, str(UserId.generate()), handlers, None)
        except Exception as exc:
            assert getattr(exc, "status_code", None) == 404
        else:
            raise AssertionError("missing user was returned")

    asyncio.run(scenario())


def test_api_error_mapping_covers_conflict_and_validation_branches() -> None:
    assert api._error(UserAlreadyExists("duplicate")).status_code == 409
    assert api._error(IdempotencyConflict("conflict")).status_code == 409
    assert api._error(InvalidUserTransition("transition")).status_code == 409
    assert api._error(IdentityDomainError("invalid")).status_code == 422


def test_api_crud_and_transitions_use_trusted_scope() -> None:
    async def scenario() -> None:
        handlers = _handlers()
        request = _request()
        created = await api.create_user(request, _payload(), handlers, "tenant-a", "key")
        user_id = created.user_id
        fetched = await api.get_user(request, user_id, handlers, "tenant-a")
        assert fetched.email == "api@example.com"
        updated = await api.update_user(
            request, user_id, UserUpdateRequest(display_name="Updated User"), handlers, None
        )
        assert updated.display_name == "Updated User"
        assert (await api.activate_user(request, user_id, handlers, None)).status == "ACTIVE"
        assert (await api.suspend_user(request, user_id, handlers, None)).status == "SUSPENDED"
        assert (await api.activate_user(request, user_id, handlers, None)).status == "ACTIVE"
        assert (await api.deactivate_user(request, user_id, handlers, None)).status == "INACTIVE"
        assert await api.search_users(request, None, "Updated", None, None, 0, 10, handlers, None)
        response = await api.delete_user(request, user_id, handlers, None)
        assert response.status_code == 204

    asyncio.run(scenario())


def test_api_maps_handler_domain_errors_for_all_mutations_and_search() -> None:
    async def scenario() -> None:
        request = _request()
        user_id = str(UserId.generate())
        handlers = _handlers()

        handlers.create = AsyncMock(side_effect=IdentityDomainError("create"))  # type: ignore[method-assign]
        with pytest.raises(Exception) as create_error:
            await api.create_user(request, _payload(), handlers, None, None)
        assert getattr(create_error.value, "status_code", None) == 422

        handlers.search = AsyncMock(side_effect=IdentityDomainError("search"))  # type: ignore[method-assign]
        with pytest.raises(Exception) as search_error:
            await api.search_users(request, None, None, None, None, 0, 10, handlers, None)
        assert getattr(search_error.value, "status_code", None) == 422

        handlers.update = AsyncMock(side_effect=IdentityDomainError("update"))  # type: ignore[method-assign]
        with pytest.raises(Exception) as update_error:
            await api.update_user(
                request, user_id, UserUpdateRequest(display_name="Updated"), handlers, None
            )
        assert getattr(update_error.value, "status_code", None) == 422

        handlers.action = AsyncMock(side_effect=IdentityDomainError("action"))  # type: ignore[method-assign]
        with pytest.raises(Exception) as action_error:
            await api.activate_user(request, user_id, handlers, None)
        assert getattr(action_error.value, "status_code", None) == 422

        handlers.delete = AsyncMock(side_effect=IdentityDomainError("delete"))  # type: ignore[method-assign]
        with pytest.raises(Exception) as delete_error:
            await api.delete_user(request, user_id, handlers, None)
        assert getattr(delete_error.value, "status_code", None) == 422

    asyncio.run(scenario())


def test_identity_repository_sqlalchemy_mapping_and_queries() -> None:
    from collections.abc import Iterator

    from identity_service.domain.entities import User
    from identity_service.domain.value_objects import (
        DisplayName,
        EmailAddress,
        FamilyName,
        GivenName,
        PhoneNumber,
        UserMetadata,
        UserType,
    )
    from identity_service.infrastructure.persistence.models import UserModel
    from identity_service.infrastructure.persistence.sqlalchemy_repository import (
        SqlAlchemyUserRepository,
    )

    class Rows:
        def __init__(self, rows: list[UserModel]) -> None:
            self.rows = rows

        def __iter__(self) -> Iterator[UserModel]:
            return iter(self.rows)

    class Session:
        def __init__(self) -> None:
            self.models: dict[str, UserModel] = {}
            self.scalar_result: UserModel | None = None
            self.scalars_result = Rows([])
            self.get = AsyncMock(side_effect=lambda _type, key: self.models.get(key))
            self.scalar = AsyncMock(side_effect=lambda _statement: self.scalar_result)
            self.scalars = AsyncMock(side_effect=lambda _statement: self.scalars_result)
            self.flush = AsyncMock()

        def add(self, model: UserModel) -> None:
            self.models[model.user_id] = model

    async def scenario() -> None:
        session = Session()
        repository = SqlAlchemyUserRepository(session)  # type: ignore[arg-type]
        user = User.create(
            "tenant-a",
            EmailAddress("db@example.com"),
            DisplayName("Database User"),
            GivenName("Db"),
            FamilyName("User"),
            PhoneNumber("+5511999999999"),
            UserType.EMPLOYEE,
            UserMetadata({"department": "engineering"}),
        )
        await repository.save(user)
        session.scalar_result = session.models[str(user.user_id)]
        assert await repository.get_by_id("tenant-a", user.user_id) is not None
        assert await repository.get_by_email("tenant-a", user.email) is not None
        session.scalars_result = Rows([session.models[str(user.user_id)]])
        assert len(await repository.search("tenant-a", name="Database")) == 1
        assert len(await repository.search("tenant-b")) == 1

    asyncio.run(scenario())
