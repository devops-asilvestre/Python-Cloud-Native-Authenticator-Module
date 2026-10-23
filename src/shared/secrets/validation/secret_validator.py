"""Validation rules for secret names, payloads, and contracts."""

from __future__ import annotations

from shared.secrets.contracts.secret_contract import SecretContract
from shared.secrets.exceptions.secret_validation_exception import SecretValidationException
from shared.secrets.naming.secret_naming_convention import SecretNamingConvention


class SecretValidator:
    """Validates secret names and resolved secret payloads."""

    def __init__(self, naming_convention: SecretNamingConvention | None = None) -> None:
        self.naming_convention = naming_convention or SecretNamingConvention()

    def validate_name(self, name: str) -> str:
        normalized = self.naming_convention.normalize(name)
        if not normalized:
            raise SecretValidationException("Secret name cannot be empty.")
        if not self.naming_convention.is_valid(normalized):
            raise SecretValidationException(
                f"Secret name '{normalized}' is invalid. Use AWS-compatible characters only."
            )
        return normalized

    def validate_value(self, value: str | None, *, name: str | None = None) -> str:
        if value is None or not value.strip():
            raise SecretValidationException(
                f"Secret '{name or 'unknown'}' has an empty or null value."
            )
        return value

    def validate_contract(self, secret: SecretContract) -> SecretContract:
        if not isinstance(secret, SecretContract):
            raise SecretValidationException("The supplied secret contract is invalid.")
        self.validate_name(secret.name)
        self.validate_value(secret.value, name=secret.name)
        return secret
