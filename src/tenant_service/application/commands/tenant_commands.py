from __future__ import annotations

from dataclasses import dataclass

from tenant_service.application.dto.tenant_dto import TenantCreateRequest, TenantUpdateRequest
from tenant_service.domain.value_objects import TenantId


@dataclass(frozen=True, slots=True)
class CreateTenant:
    request: TenantCreateRequest
    idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateTenant:
    tenant_id: TenantId
    request: TenantUpdateRequest


@dataclass(frozen=True, slots=True)
class ActivateTenant:
    tenant_id: TenantId


@dataclass(frozen=True, slots=True)
class SuspendTenant:
    tenant_id: TenantId


@dataclass(frozen=True, slots=True)
class DeactivateTenant:
    tenant_id: TenantId


@dataclass(frozen=True, slots=True)
class DeleteTenant:
    tenant_id: TenantId
