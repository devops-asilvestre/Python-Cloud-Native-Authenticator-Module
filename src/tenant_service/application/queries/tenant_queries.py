from dataclasses import dataclass

from tenant_service.domain.value_objects import TenantId


@dataclass(frozen=True, slots=True)
class GetTenant:
    tenant_id: TenantId


@dataclass(frozen=True, slots=True)
class ListTenants:
    pass
