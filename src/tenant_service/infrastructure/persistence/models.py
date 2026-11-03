from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class TenantBase(DeclarativeBase):
    pass


class TenantModel(TenantBase):
    __tablename__ = "tenants"
    __table_args__ = (UniqueConstraint("tenant_code"), UniqueConstraint("tenant_slug"))

    tenant_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_name: Mapped[str] = mapped_column(String(200), nullable=False)
    tenant_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    tenant_slug: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tenant_status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    settings: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", JSON, nullable=False)
    domains: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
