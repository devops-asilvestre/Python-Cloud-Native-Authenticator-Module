"""Mask sensitive values in structured data before display or logging."""

from collections.abc import Mapping

MASK = "***"
DEFAULT_SENSITIVE_FIELDS = frozenset(
    {
        "access_token",
        "api_key",
        "authorization",
        "client_secret",
        "password",
        "private_key",
        "refresh_token",
        "secret",
        "token",
    }
)


def mask_sensitive_data(
    value: object,
    *,
    sensitive_fields: frozenset[str] = DEFAULT_SENSITIVE_FIELDS,
) -> object:
    """Return a recursively copied structure with known sensitive fields masked."""
    normalized_fields = {field.casefold().replace("-", "_") for field in sensitive_fields}

    if isinstance(value, Mapping):
        masked: dict[object, object] = {}
        for key, item in value.items():
            normalized_key = str(key).casefold().replace("-", "_")
            masked[key] = MASK if normalized_key in normalized_fields else mask_sensitive_data(
                item,
                sensitive_fields=sensitive_fields,
            )
        return masked
    if isinstance(value, list):
        return [mask_sensitive_data(item, sensitive_fields=sensitive_fields) for item in value]
    if isinstance(value, tuple):
        return tuple(mask_sensitive_data(item, sensitive_fields=sensitive_fields) for item in value)
    return value
