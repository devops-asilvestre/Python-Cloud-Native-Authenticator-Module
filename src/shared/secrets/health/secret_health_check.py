"""Check that the secret provider is available without exposing secret values."""

from __future__ import annotations

from shared.secrets.contracts.secret_provider_contract import SecretProviderContract


class SecretHealthCheck:
    """Read-only connectivity check for the secrets provider."""

    def __init__(self, provider: SecretProviderContract | None = None) -> None:
        self.provider = provider

    def check(self) -> bool:
        if self.provider is None:
            return True
        try:
            self.provider.list_secrets(max_results=1)
            return True
        except Exception:  # pragma: no cover - depends on infrastructure availability.
            return False
