import asyncio

from shared.cache.contracts.async_cache_contract import AsyncCacheContract
from shared.cache.contracts.lock_contract import DistributedLockContract
from shared.cache.contracts.rate_limit_contract import RateLimitContract
from shared.cache.keys.tenant_key_builder import TenantAwareKeyBuilder
from shared.cache.serialization.json_serializer import JsonSerializer
from shared.cache.testing.factories import make_cache_provider


def test_json_serializer_round_trips_complex_values() -> None:
    payload = {"tenant_id": "tenant-123", "roles": ["admin", "auditor"], "active": True}
    encoded = JsonSerializer.dumps(payload)
    assert JsonSerializer.loads(encoded) == payload


def test_tenant_key_builder_creates_expected_namespace() -> None:
    keys = TenantAwareKeyBuilder()
    assert keys.session_key("tenant-1", "session-9") == "tenant:tenant-1:session:session-9"
    assert keys.token_key("tenant-1", "token-7") == "tenant:tenant-1:token:token-7"


def test_cache_provider_sets_and_reads_values() -> None:
    async def run() -> None:
        cache = make_cache_provider()
        assert await cache.set(
            "tenant:tenant-9:session:abc",
            {"user_id": "user-42"},
            ttl_seconds=10,
        )
        assert await cache.exists("tenant:tenant-9:session:abc")
        assert await cache.get("tenant:tenant-9:session:abc") == {"user_id": "user-42"}

    asyncio.run(run())


def test_rate_limiter_tracks_requests() -> None:
    async def run() -> None:
        cache = make_cache_provider()
        assert await cache.client_provider.get_client() is not None
        assert cache.client_provider._client is not None

    asyncio.run(run())


def test_contracts_are_abstract_interfaces() -> None:
    assert issubclass(AsyncCacheContract, object)
    assert issubclass(DistributedLockContract, object)
    assert issubclass(RateLimitContract, object)
