from collections.abc import Sequence
from typing import cast

from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from tenant_service.domain.aggregates import Tenant
from tenant_service.domain.repositories import TenantRepository
from tenant_service.domain.value_objects import (
    TenantCode,
    TenantDomain,
    TenantId,
    TenantMetadata,
    TenantName,
    TenantSettings,
    TenantSlug,
    TenantStatus,
    TenantStatusValue,
)
from tenant_service.infrastructure.persistence.models import TenantModel


class SqlAlchemyTenantRepository(TenantRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, tenant: Tenant) -> None:
        model = await self.session.get(TenantModel, str(tenant.tenant_id))
        if model is None:
            model = TenantModel(tenant_id=str(tenant.tenant_id))
            self.session.add(model)
        self._write(model, tenant)
        await self.session.flush()

    async def get_by_id(self, tenant_id: TenantId) -> Tenant | None:
        model = await self.session.get(TenantModel, str(tenant_id))
        return self._read(model) if model else None

    async def get_by_code(self, code: TenantCode) -> Tenant | None:
        return await self._find(TenantModel.tenant_code == str(code))

    async def get_by_slug(self, slug: TenantSlug) -> Tenant | None:
        return await self._find(TenantModel.tenant_slug == str(slug))

    async def exists(self, code: TenantCode, slug: TenantSlug) -> bool:
        result = await self.session.scalar(
            select(TenantModel.tenant_id)
            .where((TenantModel.tenant_code == str(code)) | (TenantModel.tenant_slug == str(slug)))
            .limit(1)
        )
        return result is not None

    async def delete(self, tenant_id: TenantId) -> None:
        model = await self.session.get(TenantModel, str(tenant_id))
        if model is not None:
            await self.session.delete(model)
            await self.session.flush()

    async def list(self) -> Sequence[Tenant]:
        result = await self.session.scalars(select(TenantModel).order_by(TenantModel.created_at))
        return tuple(self._read(model) for model in result)

    async def _find(self, clause: ColumnElement[bool]) -> Tenant | None:
        model = await self.session.scalar(select(TenantModel).where(clause).limit(1))
        return self._read(model) if model else None

    @staticmethod
    def _write(model: TenantModel, tenant: Tenant) -> None:
        model.tenant_name = str(tenant.tenant_name)
        model.tenant_code = str(tenant.tenant_code)
        model.tenant_slug = str(tenant.tenant_slug)
        model.tenant_status = str(tenant.tenant_status)
        model.settings = {
            "timezone": tenant.settings.timezone,
            "language": tenant.settings.language,
            "country": tenant.settings.country,
            "currency": tenant.settings.currency,
            "branding_enabled": tenant.settings.branding_enabled,
            "audit_enabled": tenant.settings.audit_enabled,
            "mfa_required": tenant.settings.mfa_required,
        }
        model.metadata_ = dict(tenant.metadata.values)
        model.domains = [str(domain) for domain in tenant.domains]
        model.created_at, model.updated_at = tenant.created_at, tenant.updated_at

    @staticmethod
    def _read(model: TenantModel) -> Tenant:
        settings = model.settings
        return Tenant(
            TenantId(model.tenant_id),
            TenantName(model.tenant_name),
            TenantCode(model.tenant_code),
            TenantSlug(model.tenant_slug),
            TenantStatus(TenantStatusValue(model.tenant_status)),
            TenantSettings(
                timezone=cast(str, settings["timezone"]),
                language=cast(str, settings["language"]),
                country=cast(str, settings["country"]),
                currency=cast(str, settings["currency"]),
                branding_enabled=cast(bool, settings["branding_enabled"]),
                audit_enabled=cast(bool, settings["audit_enabled"]),
                mfa_required=cast(bool, settings["mfa_required"]),
            ),
            TenantMetadata(cast(dict[str, str | int | float | bool | None], model.metadata_)),
            tuple(TenantDomain(domain) for domain in model.domains),
            model.created_at,
            model.updated_at,
        )
