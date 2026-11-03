from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status

from tenant_service.application.commands import (
    ActivateTenant,
    CreateTenant,
    DeactivateTenant,
    DeleteTenant,
    SuspendTenant,
    UpdateTenant,
)
from tenant_service.application.dto.tenant_dto import (
    TenantCreateRequest,
    TenantResponse,
    TenantUpdateRequest,
)
from tenant_service.application.handlers.tenant_handlers import TenantHandlers
from tenant_service.application.queries import GetTenant, ListTenants
from tenant_service.domain.exceptions import (
    InvalidTenantTransition,
    TenantAlreadyExists,
    TenantDomainError,
    TenantNotFound,
)
from tenant_service.domain.value_objects import TenantId
from tenant_service.presentation.api.runtime import get_handlers

router = APIRouter(prefix="/tenants", tags=["tenants"])


def _tenant_id(value: str) -> TenantId:
    try:
        return TenantId(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _handle_error(exc: TenantDomainError) -> HTTPException:
    if isinstance(exc, TenantNotFound):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, TenantAlreadyExists):
        return HTTPException(status_code=409, detail=str(exc))
    if isinstance(exc, InvalidTenantTransition):
        return HTTPException(status_code=409, detail=str(exc))
    return HTTPException(status_code=422, detail=str(exc))


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    request: TenantCreateRequest,
    handlers: TenantHandlers = Depends(get_handlers),  # noqa: B008
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> TenantResponse:
    try:
        return await handlers.create(CreateTenant(request, idempotency_key))
    except TenantDomainError as exc:
        raise _handle_error(exc) from exc


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str, handlers: TenantHandlers = Depends(get_handlers),  # noqa: B008
) -> TenantResponse:
    try:
        return await handlers.get(GetTenant(_tenant_id(tenant_id)))
    except TenantDomainError as exc:
        raise _handle_error(exc) from exc


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    request: TenantUpdateRequest,
    handlers: TenantHandlers = Depends(get_handlers),  # noqa: B008
) -> TenantResponse:
    try:
        return await handlers.update(UpdateTenant(_tenant_id(tenant_id), request))
    except TenantDomainError as exc:
        raise _handle_error(exc) from exc


@router.post("/{tenant_id}/activate", response_model=TenantResponse)
async def activate_tenant(
    tenant_id: str, handlers: TenantHandlers = Depends(get_handlers),  # noqa: B008
) -> TenantResponse:
    try:
        return await handlers.activate(ActivateTenant(_tenant_id(tenant_id)))
    except TenantDomainError as exc:
        raise _handle_error(exc) from exc


@router.post("/{tenant_id}/suspend", response_model=TenantResponse)
async def suspend_tenant(
    tenant_id: str, handlers: TenantHandlers = Depends(get_handlers),  # noqa: B008
) -> TenantResponse:
    try:
        return await handlers.suspend(SuspendTenant(_tenant_id(tenant_id)))
    except TenantDomainError as exc:
        raise _handle_error(exc) from exc


@router.post("/{tenant_id}/deactivate", response_model=TenantResponse)
async def deactivate_tenant(
    tenant_id: str, handlers: TenantHandlers = Depends(get_handlers),  # noqa: B008
) -> TenantResponse:
    try:
        return await handlers.deactivate(DeactivateTenant(_tenant_id(tenant_id)))
    except TenantDomainError as exc:
        raise _handle_error(exc) from exc


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: str,
    handlers: TenantHandlers = Depends(get_handlers),  # noqa: B008
) -> Response:
    try:
        await handlers.delete(DeleteTenant(_tenant_id(tenant_id)))
    except TenantDomainError as exc:
        raise _handle_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("", response_model=list[TenantResponse])
async def list_tenants(
    handlers: TenantHandlers = Depends(get_handlers),  # noqa: B008
) -> list[TenantResponse]:
    return list(await handlers.list(ListTenants()))
