"""In-memory fake provider for secret resolution tests."""

from __future__ import annotations

from shared.secrets.context.secret_metadata import SecretMetadata
from shared.secrets.contracts.secret_contract import SecretContract
from shared.secrets.contracts.secret_provider_contract import SecretProviderContract


class FakeSecretProvider(SecretProviderContract):
    """Read-only fake provider suitable for tests and examples."""

    def __init__(self, secrets: dict[str, str] | None = None) -> None:
        self._secrets = dict(secrets or {})

    def get_secret(
        self,
        name: str,
        *,
        version_id: str | None = None,
        version_stage: str | None = None,
        region_name: str | None = None,
    ) -> SecretContract:
        value = self._secrets.get(name)
        if value is None:
            raise KeyError(name)
        return SecretContract(
            name=name,
            value=value,
            version=version_id or version_stage or "AWSCURRENT",
            region=region_name or "us-east-1",
            account_id="123456789012",
            metadata=SecretMetadata(
                name=name,
                version_id=version_id or version_stage or "AWSCURRENT",
            ),
        )

    def get_metadata(self, name: str, *, region_name: str | None = None) -> SecretMetadata:
        return SecretMetadata(name=name, version_id="AWSCURRENT")

    def list_secrets(
        self,
        *,
        region_name: str | None = None,
        max_results: int | None = None,
    ) -> list[str]:
        return list(self._secrets.keys())
