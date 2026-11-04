"""Validate connectivity to the configured secrets backend."""

from __future__ import annotations

from shared.secrets.health.secret_health_check import SecretHealthCheck


class SecretConnectionValidator:
    """Thin validation wrapper around the secrets health check."""

    def __init__(self, health_check: SecretHealthCheck | None = None) -> None:
        self._health_check = health_check or SecretHealthCheck()

    def validate(self) -> bool:
        return self._health_check.check()

    def is_connected(self) -> bool:
        return self.validate()
