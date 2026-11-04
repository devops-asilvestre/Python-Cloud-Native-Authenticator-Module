"""Factory that assembles the platform connection URI."""

from __future__ import annotations

from shared.persistence.database_settings import DatabaseSettings


class ConnectionFactory:
    """Builds and stores the configured database URL."""

    def __init__(self, settings: DatabaseSettings | None = None) -> None:
        self._settings = settings or DatabaseSettings()

    @property
    def settings(self) -> DatabaseSettings:
        return self._settings

    def build_url(self) -> str:
        return self._settings.database_url

    def create(self) -> str:
        return self.build_url()

    def __str__(self) -> str:
        return self.build_url()
