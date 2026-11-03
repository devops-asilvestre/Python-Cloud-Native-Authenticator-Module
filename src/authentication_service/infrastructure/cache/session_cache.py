from __future__ import annotations

from datetime import datetime

from authentication_service.domain.aggregates import AuthenticationSession
from shared.cache.contracts.session_cache_contract import SessionCacheContract


class SessionCache(SessionCacheContract):
    def __init__(self, cache: SessionCacheContract) -> None:
        self._cache = cache

    async def get_session(self, tenant_id: str, session_id: str) -> AuthenticationSession | None:
        value = await self._cache.get_session(tenant_id, session_id)
        if not isinstance(value, dict):
            return None
        expires_at = value.get("expires_at")
        if not isinstance(expires_at, str):
            return None
        return AuthenticationSession.restore(
            session_id=session_id,
            tenant_id=tenant_id,
            user_id=str(value["user_id"]),
            created_at=datetime.fromisoformat(str(value["created_at"])),
            expires_at=datetime.fromisoformat(expires_at),
            active=bool(value["active"]),
        )

    async def set_session(
        self, tenant_id: str, session_id: str, value: AuthenticationSession, *,
        ttl_seconds: int | None = None,
    ) -> bool:
        return await self._cache.set_session(tenant_id, session_id, {
            "user_id": value.user_id,
            "created_at": value.created_at.isoformat(),
            "expires_at": value.expires_at.isoformat(),
            "active": value.active,
        }, ttl_seconds=ttl_seconds)

    async def delete_session(self, tenant_id: str, session_id: str) -> bool:
        return await self._cache.delete_session(tenant_id, session_id)
