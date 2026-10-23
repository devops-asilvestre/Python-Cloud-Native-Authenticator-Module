"""Contracts for secrets access and resolution."""

from shared.secrets.contracts.secret_contract import SecretContract
from shared.secrets.contracts.secret_provider_contract import SecretProviderContract

__all__ = ["SecretContract", "SecretProviderContract"]
