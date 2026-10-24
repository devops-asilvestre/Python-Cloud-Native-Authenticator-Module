"""Validated encryption context construction."""

from __future__ import annotations

from shared.kms.exceptions.kms_validation_exception import KmsValidationException


def build_encryption_context(
    values: dict[str, str] | None,
    *,
    tenant_id: str | None,
) -> dict[str, str]:
    """Validate context values and bind operations to the active tenant."""

    context = dict(values or {})
    if any(
        not isinstance(key, str)
        or not key.strip()
        or not isinstance(value, str)
        or not value
        for key, value in context.items()
    ):
        raise KmsValidationException("Encryption context must contain non-empty string pairs.")
    if tenant_id is not None:
        existing_tenant = context.get("tenant_id")
        if existing_tenant is not None and existing_tenant != tenant_id:
            raise KmsValidationException("Encryption context tenant does not match request tenant.")
        context["tenant_id"] = tenant_id
    return context
