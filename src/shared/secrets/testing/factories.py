"""Factories for building secrets test artifacts."""

from __future__ import annotations

from shared.secrets.context.secret_metadata import SecretMetadata
from shared.secrets.contracts.secret_contract import SecretContract
from shared.secrets.testing.fake_provider import FakeSecretProvider


def build_secret_contract(
    *,
    name: str = "app/db/password",
    value: str = "super-secret",
    region: str = "us-east-1",
) -> SecretContract:
    return SecretContract(
        name=name,
        value=value,
        version="AWSCURRENT",
        region=region,
        account_id="123456789012",
        metadata=SecretMetadata(name=name, version_id="AWSCURRENT"),
    )


def build_fake_secret_provider(*, secrets: dict[str, str] | None = None) -> FakeSecretProvider:
    return FakeSecretProvider(secrets or {"app/db/password": "super-secret"})
