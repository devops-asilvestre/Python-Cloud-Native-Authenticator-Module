from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from tenant_service.domain.aggregates import Tenant


class TenantSettingsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    timezone: str = "UTC"
    language: str = "en"
    country: str = "US"
    currency: str = "USD"
    branding_enabled: bool = False
    audit_enabled: bool = True
    mfa_required: bool = False


class TenantCreateRequest(TenantSettingsInput):
    name: str = Field(min_length=3, max_length=200)
    code: str = Field(min_length=3, max_length=20)
    slug: str = Field(min_length=1, max_length=100)
    domains: list[str] = Field(default_factory=list)
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class TenantUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None, min_length=3, max_length=200)
    slug: str | None = None
    settings: TenantSettingsInput | None = None
    domains: list[str] | None = None
    metadata: dict[str, str | int | float | bool | None] | None = None


class TenantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tenant_id: str
    name: str
    code: str
    slug: str
    status: str
    settings: TenantSettingsInput
    metadata: dict[str, str | int | float | bool | None]
    domains: list[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, tenant: Tenant) -> TenantResponse:
        return cls(
            tenant_id=str(tenant.tenant_id),
            name=str(tenant.tenant_name),
            code=str(tenant.tenant_code),
            slug=str(tenant.tenant_slug),
            status=str(tenant.tenant_status),
            settings=TenantSettingsInput(
                **{
                    field: getattr(tenant.settings, field)
                    for field in tenant.settings.__dataclass_fields__
                }
            ),
            metadata=dict(tenant.metadata.values),
            domains=[str(domain) for domain in tenant.domains],
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
        )
