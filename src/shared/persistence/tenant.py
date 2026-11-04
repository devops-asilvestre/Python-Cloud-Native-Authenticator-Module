"""Utilities for tenant-aware persistence boundaries."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TenantContext:
    """Immutable tenant metadata associated with a database session."""

    tenant_id: str
    user_id: str | None = None
    metadata: dict[str, str | int | float | bool | None] = field(default_factory=dict)

    def as_session_info(self) -> dict[str, object]:
        info: dict[str, object] = {"tenant_id": self.tenant_id}
        if self.user_id is not None:
            info["user_id"] = self.user_id
        info.update(self.metadata)
        return info
