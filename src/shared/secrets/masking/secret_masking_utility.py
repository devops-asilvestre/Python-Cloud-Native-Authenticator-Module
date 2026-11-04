"""Mask sensitive values before they reach telemetry or logs."""

from __future__ import annotations

from typing import Any


class SecretMaskingUtility:
    """Apply reversible-like masking to sensitive secret strings."""

    @staticmethod
    def mask(
        value: str,
        *,
        visible_prefix: int = 2,
        visible_suffix: int = 2,
        mask_char: str = "*",
    ) -> str:
        if not value:
            return ""
        if len(value) <= visible_prefix + visible_suffix:
            return value[:1] + mask_char * max(len(value) - 1, 0)
        prefix = value[:visible_prefix]
        suffix = value[-visible_suffix:]
        hidden = max(len(value) - visible_prefix - visible_suffix, 0)
        return f"{prefix}{mask_char * hidden}{suffix}"

    @staticmethod
    def mask_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
        masked: dict[str, Any] = {}
        for key, value in mapping.items():
            lowered = key.lower()
            if (
                "secret" in lowered
                or "token" in lowered
                or "password" in lowered
                or "key" in lowered
            ):
                masked[key] = SecretMaskingUtility.mask(str(value))
            else:
                masked[key] = value
        return masked
