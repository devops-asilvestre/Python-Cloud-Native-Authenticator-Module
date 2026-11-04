"""Tenant-aware key builder for Redis-backed caches."""

from __future__ import annotations

from shared.cache.keys.cache_key_builder import CacheKeyBuilder


class TenantAwareKeyBuilder:
    """Assemblies tenant bound keys such as tenant:<id>:session:<hash>."""

    def __init__(self, namespace: str = "tenant") -> None:
        self._namespace = namespace
        self._builder = CacheKeyBuilder(namespace=namespace)

    @property
    def namespace(self) -> str:
        return self._namespace

    def session_key(self, tenant_id: str, session_id: str) -> str:
        return self._builder.build(tenant_id, "session", session_id)

    def token_key(self, tenant_id: str, token_id: str) -> str:
        return self._builder.build(tenant_id, "token", token_id)

    def policy_key(self, tenant_id: str, policy_id: str) -> str:
        return self._builder.build(tenant_id, "policy", policy_id)

    def lock_key(self, tenant_id: str, name: str) -> str:
        return self._builder.build(tenant_id, "lock", name)

    def rate_limit_key(self, tenant_id: str, action: str) -> str:
        return self._builder.build(tenant_id, "ratelimit", action)

    def build(self, tenant_id: str, *parts: str) -> str:
        return self._builder.build(tenant_id, *parts)
