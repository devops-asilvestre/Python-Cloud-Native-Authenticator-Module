"""Memory cache for secret values and metadata."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

from shared.secrets.cache.secret_cache_entry import SecretCacheEntry
from shared.secrets.contracts.secret_contract import SecretContract


class SecretCache:
    """Simple in-memory cache for resolved secrets."""

    def __init__(self, *, max_entries: int = 256, default_ttl_seconds: int = 300) -> None:
        self._entries: dict[str, SecretCacheEntry] = {}
        self.max_entries = max_entries
        self.default_ttl_seconds = default_ttl_seconds

    def _key(
        self,
        name: str,
        *,
        version_id: str | None = None,
        version_stage: str | None = None,
    ) -> str:
        variant = version_id or version_stage or "AWSCURRENT"
        return f"{name}:{variant}"

    def get(
        self,
        name: str,
        *,
        version_id: str | None = None,
        version_stage: str | None = None,
    ) -> SecretContract | None:
        key = self._key(name, version_id=version_id, version_stage=version_stage)
        entry = self._entries.get(key)
        if entry is None:
            return None
        if entry.is_expired(now=datetime.now(UTC)):
            self._entries.pop(key, None)
            return None
        return entry.secret

    def set(self, secret: SecretContract, *, ttl_seconds: int | None = None) -> None:
        key = self._key(secret.name, version_id=secret.version, version_stage=None)
        if len(self._entries) >= self.max_entries and key not in self._entries:
            self._entries.pop(next(iter(self._entries)))
        self._entries[key] = SecretCacheEntry(
            secret=secret,
            ttl_seconds=ttl_seconds or self.default_ttl_seconds,
        )

    def delete(
        self,
        name: str,
        *,
        version_id: str | None = None,
        version_stage: str | None = None,
    ) -> bool:
        key = self._key(name, version_id=version_id, version_stage=version_stage)
        return self._entries.pop(key, None) is not None

    def clear(self) -> None:
        self._entries.clear()

    def __contains__(self, key: str) -> bool:
        return key in self._entries

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[str]:
        return iter(self._entries)
