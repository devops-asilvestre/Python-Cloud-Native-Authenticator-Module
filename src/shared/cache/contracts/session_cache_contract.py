"""Session cache contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SessionCacheContract(ABC):
    """Cache interface reserved for session-related data."""

    @abstractmethod
    async def get_session(self, tenant_id: str, session_id: str) -> Any | None: ...

    @abstractmethod
    async def set_session(
        self,
        tenant_id: str,
        session_id: str,
        value: Any,
        *,
        ttl_seconds: int | None = None,
    ) -> bool: ...

    @abstractmethod
    async def delete_session(self, tenant_id: str, session_id: str) -> bool: ...
