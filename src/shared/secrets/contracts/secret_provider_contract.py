"""Contract implemented by concrete secret providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from shared.secrets.context.secret_metadata import SecretMetadata
from shared.secrets.contracts.secret_contract import SecretContract


class SecretProviderContract(ABC):
    """Infrastructure contract for reading secrets from a secret store."""

    @abstractmethod
    def get_secret(
        self,
        name: str,
        *,
        version_id: str | None = None,
        version_stage: str | None = None,
        region_name: str | None = None,
    ) -> SecretContract: ...

    @abstractmethod
    def get_metadata(self, name: str, *, region_name: str | None = None) -> SecretMetadata: ...

    @abstractmethod
    def list_secrets(
        self,
        *,
        region_name: str | None = None,
        max_results: int | None = None,
    ) -> list[str]: ...
