"""Migration foundation for the platform database layer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from shared.persistence.database_settings import DatabaseSettings


class MigrationFoundation:
    """Keeps migration metadata aligned with the database connection settings."""

    def __init__(
        self,
        settings: DatabaseSettings | None = None,
        directory: str | Path = "src/shared/persistence/alembic",
    ) -> None:
        self._settings = settings or DatabaseSettings()
        self._directory_raw = str(directory)
        self._directory = Path(directory)

    @property
    def settings(self) -> DatabaseSettings:
        return self._settings

    @property
    def directory(self) -> Path:
        return self._directory

    @property
    def database_url(self) -> str:
        return self._settings.database_url

    @property
    def alembic_ini_path(self) -> Path:
        return Path("alembic.ini")

    def build_config(self, **overrides: Any) -> dict[str, Any]:
        config: dict[str, Any] = {
            "script_location": self._directory_raw,
            "sqlalchemy.url": self.database_url,
        }
        config.update(overrides)
        return config

    def create_alembic_config(self, **overrides: Any) -> dict[str, Any]:
        return self.build_config(**overrides)
