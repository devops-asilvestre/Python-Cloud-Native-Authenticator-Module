"""Token cache contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TokenCacheContract(ABC):
    """Cache interface reserved for token-backed authentication artifacts."""

    @abstractmethod
    async def get_token(self, tenant_id: str, token_id: str) -> Any | None: ...

    @abstractmethod
    async def set_token(
        self,
        tenant_id: str,
        token_id: str,
        value: Any,
        *,
        ttl_seconds: int | None = None,
    ) -> bool: ...

    @abstractmethod
    async def delete_token(self, tenant_id: str, token_id: str) -> bool: ...
