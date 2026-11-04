from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status

from identity_service.application.commands import CreateUser, UpdateUser, UserAction
from identity_service.application.dto import UserCreateRequest, UserResponse, UserUpdateRequest
from identity_service.application.handlers.user_handlers import UserHandlers
from identity_service.application.queries import GetUser, SearchUsers
from identity_service.domain.exceptions import IdentityDomainError, UserNotFound
from identity_service.domain.value_objects import UserId, UserStatusValue, UserType
from identity_service.presentation.api.runtime import get_handlers

router = APIRouter(prefix="/users", tags=["users"])


def _id(value: str) -> UserId:
    try:
        return UserId(value)
    except IdentityDomainError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _error(exc: IdentityDomainError) -> HTTPException:
    if isinstance(exc, UserNotFound):
        return HTTPException(status_code=404, detail=str(exc))
    if exc.__class__.__name__ in {
        "UserAlreadyExists",
        "IdempotencyConflict",
        "InvalidUserTransition",
    }:
        return HTTPException(status_code=409, detail=str(exc))
    return HTTPException(status_code=422, detail=str(exc))


def _tenant(request: Request, value: str | None) -> str:
    trusted = getattr(request.state, "tenant_context", None)
    trusted_id = getattr(trusted, "tenant_id", None)
    if not isinstance(trusted_id, str) or not trusted_id.strip():
        raise HTTPException(status_code=403, detail="A trusted tenant context is required.2")
    if value is not None and value.strip() != trusted_id:
        raise HTTPException(status_code=403, detail="Tenant scope does not match trusted context.")
    return trusted_id


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request_context: Request,
    request: UserCreateRequest,
    handlers: UserHandlers = Depends(get_handlers),  # noqa: B008
    tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> UserResponse:
    try:
        return await handlers.create(
            CreateUser(_tenant(request_context, tenant_id), request, idempotency_key)
        )
    except IdentityDomainError as exc:
        raise _error(exc) from exc


@router.get("/search", response_model=list[UserResponse])
async def search_users(
    request_context: Request,
    email: str | None = None,
    name: str | None = None,
    status_filter: UserStatusValue | None = None,
    user_type: UserType | None = None,
    offset: int = 0,
    limit: int = 50,
    handlers: UserHandlers = Depends(get_handlers),  # noqa: B008
    tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> list[UserResponse]:
    if offset < 0 or not 1 <= limit <= 100:
        raise HTTPException(status_code=422, detail="Invalid pagination.")
    try:
        result = await handlers.search(
            SearchUsers(
                _tenant(request_context, tenant_id),
                email,
                name,
                status_filter,
                user_type,
                offset,
                limit,
            )
        )
        return list(result)
    except IdentityDomainError as exc:
        raise _error(exc) from exc


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    request_context: Request,
    user_id: str,
    handlers: UserHandlers = Depends(get_handlers),  # noqa: B008
    tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> UserResponse:
    try:
        return await handlers.get(GetUser(_tenant(request_context, tenant_id), _id(user_id)))
    except IdentityDomainError as exc:
        raise _error(exc) from exc


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    request_context: Request,
    user_id: str,
    request: UserUpdateRequest,
    handlers: UserHandlers = Depends(get_handlers),  # noqa: B008
    tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> UserResponse:
    try:
        return await handlers.update(
            UpdateUser(_tenant(request_context, tenant_id), _id(user_id), request)
        )
    except IdentityDomainError as exc:
        raise _error(exc) from exc


async def _transition(
    request_context: Request,
    user_id: str,
    action: str,
    handlers: UserHandlers,
    tenant_id: str | None,
) -> UserResponse:
    try:
        return await handlers.action(
            UserAction(_tenant(request_context, tenant_id), _id(user_id)), action
        )
    except IdentityDomainError as exc:
        raise _error(exc) from exc


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    request_context: Request,
    user_id: str,
    handlers: UserHandlers = Depends(get_handlers),  # noqa: B008
    tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> UserResponse:
    return await _transition(request_context, user_id, "activate", handlers, tenant_id)


@router.post("/{user_id}/suspend", response_model=UserResponse)
async def suspend_user(
    request_context: Request,
    user_id: str,
    handlers: UserHandlers = Depends(get_handlers),  # noqa: B008
    tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> UserResponse:
    return await _transition(request_context, user_id, "suspend", handlers, tenant_id)


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    request_context: Request,
    user_id: str,
    handlers: UserHandlers = Depends(get_handlers),  # noqa: B008
    tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> UserResponse:
    return await _transition(request_context, user_id, "deactivate", handlers, tenant_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    request_context: Request,
    user_id: str,
    handlers: UserHandlers = Depends(get_handlers),  # noqa: B008
    tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> Response:
    try:
        await handlers.delete(UserAction(_tenant(request_context, tenant_id), _id(user_id)))
    except IdentityDomainError as exc:
        raise _error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
