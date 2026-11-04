from __future__ import annotations

from authentication_service.application.ports import IdentityDirectory, TenantValidator
from authentication_service.domain.exceptions import InvalidCredentialState
from identity_service.domain.repositories import UserRepository
from identity_service.domain.value_objects import UserId, UserStatusValue
from tenant_service.domain.repositories import TenantRepository
from tenant_service.domain.value_objects import TenantId, TenantStatusValue


class TenantFoundationAdapter(TenantValidator):
    def __init__(self, repository: TenantRepository) -> None:
        self._repository = repository

    async def ensure_active(self, tenant_id: str) -> None:
        tenant = await self._repository.get_by_id(TenantId(tenant_id))
        if tenant is None or tenant.tenant_status.value is not TenantStatusValue.ACTIVE:
            raise ValueError("Tenant is not active.")


class IdentityDirectoryAdapter(IdentityDirectory):
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def ensure_active_user(self, tenant_id: str, user_id: str) -> None:
        user = await self._repository.get_by_id(tenant_id, UserId(user_id))
        if user is None or user.status.value is not UserStatusValue.ACTIVE:
            raise InvalidCredentialState("User is not active or does not exist.")
