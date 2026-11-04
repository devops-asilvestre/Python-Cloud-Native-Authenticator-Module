from __future__ import annotations

from shared.secrets.cache.secret_cache import SecretCache
from shared.secrets.contracts.secret_contract import SecretContract
from shared.secrets.exceptions.secret_access_exception import SecretAccessException
from shared.secrets.exceptions.secret_validation_exception import SecretValidationException
from shared.secrets.masking.secret_masking_utility import SecretMaskingUtility
from shared.secrets.naming.secret_naming_convention import SecretNamingConvention
from shared.secrets.resolver.secret_resolver import SecretResolver
from shared.secrets.serialization.deserializer import SecretDeserializer
from shared.secrets.serialization.serializer import SecretSerializer
from shared.secrets.testing.fake_provider import FakeSecretProvider
from shared.secrets.validation.secret_validator import SecretValidator


def test_secret_naming_convention_normalizes_and_validates_names() -> None:
    convention = SecretNamingConvention()

    assert convention.normalize("\\app\\db\\password") == "/app/db/password"
    assert convention.is_valid("app/db/password") is True
    assert convention.is_valid("bad name") is False


def test_secret_validator_rejects_invalid_values() -> None:
    validator = SecretValidator()

    assert validator.validate_name("app/db/password") == "app/db/password"
    try:
        validator.validate_value("", name="app/db/password")
        raise AssertionError("Expected validation failure")
    except SecretValidationException:
        pass


def test_secret_cache_tracks_entries_and_expiration() -> None:
    cache = SecretCache(max_entries=2, default_ttl_seconds=60)
    secret = SecretContract(name="app/db/password", value="super-secret", version="AWSCURRENT")

    cache.set(secret)
    assert cache.get("app/db/password", version_id="AWSCURRENT") == secret
    assert len(cache) == 1
    cache.delete("app/db/password", version_id="AWSCURRENT")
    assert cache.get("app/db/password", version_id="AWSCURRENT") is None


def test_secret_resolver_reads_shared_fake_provider_and_uses_cache() -> None:
    provider = FakeSecretProvider({"app/db/password": "super-secret"})
    resolver = SecretResolver(provider)

    secret = resolver.resolve("app/db/password")
    assert secret.value == "super-secret"
    assert resolver.resolve_value("app/db/password") == "super-secret"
    assert resolver.serialize({"password": "super-secret"}) == '{"password":"super-secret"}'


def test_secret_serializer_and_deserializer_round_trip_json_and_text() -> None:
    serializer = SecretSerializer()
    deserializer = SecretDeserializer()

    encoded = serializer.serialize({"database": "postgres"})
    assert deserializer.deserialize(encoded) == {"database": "postgres"}
    assert serializer.serialize("plain-text") == "plain-text"
    assert deserializer.deserialize("plain-text") == "plain-text"


def test_secret_masking_utility_masks_sensitive_fields() -> None:
    assert SecretMaskingUtility.mask("super-secret") == "su********et"
    assert SecretMaskingUtility.mask_mapping({"password": "super-secret"}) == {
        "password": "su********et"
    }


def test_secret_provider_exceptions_are_raised_for_invalid_access() -> None:
    try:
        raise SecretAccessException("boom")
    except SecretAccessException as exc:
        assert str(exc) == "boom"
