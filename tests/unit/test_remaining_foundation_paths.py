from __future__ import annotations

import asyncio

import pytest

from shared.aws.authentication.credential_resolver import AwsCredentialResolver
from shared.aws.exceptions.aws_authentication_exception import AwsAuthenticationException
from shared.aws.testing.fake_clients import FakeSession
from shared.cache.testing.fixtures import FakeRedisClient
from shared.secrets.cache.secret_cache import SecretCache
from shared.secrets.contracts.secret_contract import SecretContract
from shared.secrets.resolver.secret_resolver import SecretResolver
from shared.secrets.testing.fake_provider import FakeSecretProvider


def test_fake_redis_fixture_covers_storage_and_expiration() -> None:
    async def scenario() -> None:
        redis = FakeRedisClient()
        assert await redis.set("key", "value", ex=10)
        assert await redis.get("key") == "value"
        assert await redis.exists("key") == 1
        assert await redis.incr("counter") == 1
        assert await redis.expire("counter", 5)
        assert await redis.delete("key") == 1
        assert await redis.delete("missing") == 0
        await redis.flushdb()
        await redis.aclose()
        assert redis.closed

    asyncio.run(scenario())


def test_credential_resolver_exposes_all_credential_fields() -> None:
    class Credentials:
        access_key = "access"
        secret_key = "secret"
        token = "token"

    session = FakeSession()
    session._credentials = Credentials()
    resolver = AwsCredentialResolver(session)
    assert resolver.resolve() is not None
    assert resolver.access_key_id == "access"
    assert resolver.secret_access_key == "secret"
    assert resolver.session_token == "token"

    class NoCredentials:
        def get_credentials(self) -> None:
            return None

    with pytest.raises(AwsAuthenticationException):
        AwsCredentialResolver(NoCredentials()).resolve()


def test_secret_cache_capacity_and_resolver_cache_hit() -> None:
    cache = SecretCache(max_entries=1, default_ttl_seconds=60)
    first = SecretContract(name="first", value="one")
    second = SecretContract(name="second", value="two")
    cache.set(first)
    cache.set(second)
    assert cache.get("first") is None
    assert cache.get("second") == second

    provider = FakeSecretProvider({"app/key": "value"})
    resolver = SecretResolver(provider)
    assert resolver.resolve("app/key").value == "value"
    provider._secrets["app/key"] = "changed"
    assert resolver.resolve("app/key").value == "value"
