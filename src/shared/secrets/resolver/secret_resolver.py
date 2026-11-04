"""Resolve secrets through providers and cache while keeping access safe."""

from __future__ import annotations

from typing import Any

from shared.observability.context.request_context import RequestContext
from shared.observability.logging.structured_logger import StructuredLogger
from shared.secrets.cache.secret_cache import SecretCache
from shared.secrets.contracts.secret_contract import SecretContract
from shared.secrets.contracts.secret_provider_contract import SecretProviderContract
from shared.secrets.exceptions.secret_validation_exception import SecretValidationException
from shared.secrets.serialization.deserializer import SecretDeserializer
from shared.secrets.serialization.serializer import SecretSerializer
from shared.secrets.validation.secret_validator import SecretValidator


class SecretResolver:
    """Main entry point for resolving secrets via a provider and cache."""

    def __init__(
        self,
        provider: SecretProviderContract,
        *,
        cache: SecretCache | None = None,
        validator: SecretValidator | None = None,
        serializer: SecretSerializer | None = None,
        deserializer: SecretDeserializer | None = None,
        request_context: RequestContext | None = None,
        logger: StructuredLogger | None = None,
    ) -> None:
        self.provider = provider
        self.cache = cache or SecretCache()
        self.validator = validator or SecretValidator()
        self.serializer = serializer or SecretSerializer()
        self.deserializer = deserializer or SecretDeserializer()
        self.request_context = request_context or RequestContext()
        self.logger = logger or StructuredLogger(
            "shared-secrets-resolver",
            request_context=self.request_context,
        )

    def _log(self, event: str, **fields: Any) -> None:
        self.logger.info(event, **fields)

    def resolve(
        self,
        name: str,
        *,
        version_id: str | None = None,
        version_stage: str | None = None,
        use_cache: bool = True,
    ) -> SecretContract:
        resolved_name = self.validator.validate_name(name)
        self._log(
            "secret_resolution_requested",
            secret_name=resolved_name,
            operation="read",
            version_id=version_id,
            version_stage=version_stage,
            use_cache=use_cache,
        )

        if use_cache:
            cached = self.cache.get(
                resolved_name,
                version_id=version_id,
                version_stage=version_stage,
            )
            if cached is not None:
                self._log(
                    "secret_resolution_cache_hit",
                    secret_name=resolved_name,
                    operation="read",
                )
                return cached

        secret = self.provider.get_secret(
            resolved_name,
            version_id=version_id,
            version_stage=version_stage,
        )
        self.validator.validate_contract(secret)
        if use_cache:
            self.cache.set(secret)
        self._log(
            "secret_resolution_completed",
            secret_name=resolved_name,
            region=secret.region,
            account_id=secret.account_id,
            operation="read",
        )
        return secret

    def resolve_value(
        self,
        name: str,
        *,
        version_id: str | None = None,
        version_stage: str | None = None,
        use_cache: bool = True,
    ) -> str:
        return self.resolve(
            name,
            version_id=version_id,
            version_stage=version_stage,
            use_cache=use_cache,
        ).value

    def resolve_json(
        self,
        name: str,
        *,
        version_id: str | None = None,
        version_stage: str | None = None,
        use_cache: bool = True,
    ) -> Any:
        value = self.resolve_value(
            name,
            version_id=version_id,
            version_stage=version_stage,
            use_cache=use_cache,
        )
        deserialized = self.deserializer.deserialize(value)
        if isinstance(deserialized, (dict, list, int, float, bool)) or deserialized is None:
            return deserialized
        raise SecretValidationException(f"Secret '{name}' does not contain parseable JSON payload.")

    def serialize(self, payload: Any) -> str:
        return self.serializer.serialize(payload)
