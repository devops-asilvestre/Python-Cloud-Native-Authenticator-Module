from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from shared.cache.connection.redis_provider import RedisClientProvider
from shared.cache.exceptions.connection_exception import CacheConnectionException
from shared.secrets.exceptions.secret_not_found_exception import SecretNotFoundException
from shared.secrets.providers.aws_secrets_manager_provider import AwsSecretsManagerProvider


class FakeRedisClient:
    def __init__(self) -> None:
        self.ping = AsyncMock(return_value=True)
        self.aclose = AsyncMock()


class FakeFactory:
    def __init__(self) -> None:
        self.settings = Mock(host="redis")
        self.client = FakeRedisClient()

    def create(self) -> FakeRedisClient:
        return self.client


def test_redis_client_provider_lifecycle_and_failures() -> None:
    async def scenario() -> None:
        factory = FakeFactory()
        provider = RedisClientProvider(factory)  # type: ignore[arg-type]
        assert await provider.get_client() is not None
        assert await provider.get_client() is not None
        assert await provider.ping()
        await provider.close()
        assert provider.client is None

        failing = Mock()
        failing.create.side_effect = RuntimeError("offline")
        broken = RedisClientProvider(failing)
        with pytest.raises(CacheConnectionException):
            await broken.get_client()

    asyncio.run(scenario())


def test_aws_secrets_manager_provider_reads_string_binary_metadata_and_list() -> None:
    class Client:
        def get_secret_value(self, **_: object) -> dict[str, object]:
            return {"SecretString": "value", "VersionId": "v1"}

        def describe_secret(self, **_: object) -> dict[str, object]:
            return {
                "ARN": "arn:secret",
                "Description": "test",
                "VersionId": "v1",
                "VersionStages": ["AWSCURRENT"],
                "SecretString": "value",
                "CreatedDate": datetime.now(UTC),
                "Tags": {"team": "identity"},
                "RotationEnabled": True,
            }

        def list_secrets(self, **_: object) -> dict[str, object]:
            return {"SecretList": [{"Name": "app/db"}, {}]}

    factory = Mock()
    factory.create_client.return_value = Client()
    provider = AwsSecretsManagerProvider(client_factory=factory)
    secret = provider.get_secret("app/db")
    assert secret.value == "value"
    assert secret.metadata is not None
    assert secret.metadata.tags == {"team": "identity"}
    assert provider.list_secrets() == ["app/db"]


def test_aws_secrets_manager_provider_reads_binary_and_surfaces_missing_value() -> None:
    class Client:
        def __init__(self, response: dict[str, object]) -> None:
            self.response = response

        def get_secret_value(self, **_: object) -> dict[str, object]:
            return self.response

        def describe_secret(self, **_: object) -> dict[str, object]:
            return {}

    factory = Mock()
    factory.create_client.return_value = Client({"SecretBinary": b"YmluYXJ5", "VersionId": "v2"})
    provider = AwsSecretsManagerProvider(client_factory=factory)
    assert provider.get_secret("app/db").value == "binary"

    factory.create_client.return_value = Client({})
    with pytest.raises(SecretNotFoundException):
        provider.get_secret("app/db")
