"""Configuration settings for the platform database."""

from __future__ import annotations

from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration loaded from environment variables or .env."""

    model_config = SettingsConfigDict(
        env_prefix="AUTHENTICATOR_DB_",
        env_file=".env",
        extra="ignore",
    )

    driver: str = "postgresql+asyncpg"
    host: str = "localhost"
    port: int = 5432
    username: str = "authenticator"
    password: str = "authenticator"
    database: str = "authenticator"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 1800
    use_ssl: bool = False
    default_tenant_id: str | None = None
    tenant_field_name: str = "tenant_id"
    default_schema: str = "public"

    @property
    def dsn(self) -> str:
        return self.database_url

    @property
    def database_url(self) -> str:
        return self._build_url()

    @property
    def async_database_url(self) -> str:
        return self._build_url()

    @property
    def connection_string(self) -> str:
        return self._build_url()

    @property
    def async_url(self) -> str:
        return self._build_url()

    def _build_url(self) -> str:
        username = quote_plus(self.username)
        password = quote_plus(self.password)
        netloc = username
        if self.password:
            netloc = f"{username}:{password}"

        url = f"{self.driver}://{netloc}@{self.host}:{self.port}/{self.database}"
        if self.use_ssl:
            separator = "?" if "?" not in url else "&"
            url = f"{url}{separator}sslmode=require"
        return url
