from __future__ import annotations

import asyncio

from shared.cache.provider.cache_provider import CacheProvider
from shared.observability.tracing.trace_context import TraceContext
from shared.secrets.context.secret_metadata import SecretMetadata
from shared.secrets.contracts.secret_contract import SecretContract


class FakeCacheClient:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.values.get(key)

    async def set(self, key: str, value: str, **_: int) -> bool:
        self.values[key] = value
        return True

    async def delete(self, key: str) -> int:
        return int(self.values.pop(key, None) is not None)

    async def exists(self, key: str) -> int:
        return int(key in self.values)

    async def flushdb(self) -> bool:
        self.values.clear()
        return True


class FakeClientProvider:
    def __init__(self) -> None:
        self.client = FakeCacheClient()

    async def get_client(self) -> FakeCacheClient:
        return self.client


def test_cache_provider_covers_generic_session_token_and_flush_operations() -> None:
    async def scenario() -> None:
        provider = CacheProvider(FakeClientProvider())  # type: ignore[arg-type]
        assert await provider.set("key", {"value": 1})
        assert await provider.get("key") == {"value": 1}
        assert await provider.exists("key")
        assert await provider.delete("key")
        assert await provider.set("key", "value", ttl_seconds=10)
        assert await provider.set_session("tenant", "session", {"ok": True})
        assert await provider.get_session("tenant", "session") == {"ok": True}
        assert await provider.delete_session("tenant", "session")
        assert await provider.set_token("tenant", "token", {"ok": True})
        assert await provider.get_token("tenant", "token") == {"ok": True}
        assert await provider.delete_token("tenant", "token")
        assert await provider.flush()

    asyncio.run(scenario())


def test_secret_contract_masks_and_serializes_optional_metadata() -> None:
    contract = SecretContract(
        name="app/db/password",
        value="super-secret",
        version="v1",
        metadata=SecretMetadata(name="app/db/password", tags={"team": "identity"}),
        tags={"environment": "test"},
    )
    payload = contract.as_dict()
    assert payload["value"] == "su********et"
    assert payload["metadata"]["name"] == "app/db/password"
    assert payload["tags"] == {"environment": "test"}
    assert "super-secret" not in str(contract)


def test_trace_context_round_trips_propagation_headers() -> None:
    context = TraceContext(sampled=False, parent_span_id="parent")
    headers = context.to_headers()
    restored = TraceContext.from_headers(headers)
    assert str(restored.trace_id) == str(context.trace_id)
    assert restored.span_id == context.span_id
    assert restored.parent_span_id == "parent"
    assert not restored.sampled
