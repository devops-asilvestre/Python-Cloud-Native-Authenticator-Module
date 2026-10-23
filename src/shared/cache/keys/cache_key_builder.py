"""Key builder for tenant and cache-scoped Redis entries."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CacheKeyBuilder:
    """Build stable, namespaced keys for cache values."""

    namespace: str = "cache"
    separator: str = ":"

    def build(self, *parts: str) -> str:
        filtered = [str(part) for part in parts if part not in (None, "")]
        if not filtered:
            raise ValueError("At least one key part is required.")
        return self.separator.join([self.namespace, *filtered])

    def with_namespace(self, namespace: str) -> CacheKeyBuilder:
        return CacheKeyBuilder(namespace=namespace, separator=self.separator)
