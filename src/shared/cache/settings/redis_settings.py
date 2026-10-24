"""Redis settings for async, tenant-aware cache access."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    """Runtime settings for Redis local and managed deployments."""

    model_config = SettingsConfigDict(
        env_prefix="AUTHENTICATOR_REDIS_",
        env_file=".env",
        extra="ignore",
    )

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    username: str | None = None
    password: str | None = None
    ssl: bool = False
    decode_responses: bool = True
    socket_connect_timeout: int = 5
    socket_timeout: int = 5
    max_connections: int = 50
    health_check_interval: int = 30
    default_ttl_seconds: int = 300
    default_tenant_id: str | None = None

    @property
    def dsn(self) -> str:
        return self.url

    @property
    def url(self) -> str:
        prefix = "redis://"
        host = f"{self.host}:{self.port}"
        if self.username:
            credentials = self.username
            if self.password:
                credentials = f"{self.username}:{self.password}"
            prefix = f"redis://{credentials}@"
        if self.ssl:
            prefix = prefix.replace("redis://", "rediss://")
        return f"{prefix}{host}/{self.db}"

    @property
    def connection_kwargs(self) -> dict[str, object]:
        kwargs: dict[str, object] = {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "decode_responses": self.decode_responses,
            "socket_connect_timeout": self.socket_connect_timeout,
            "socket_timeout": self.socket_timeout,
            "max_connections": self.max_connections,
            "health_check_interval": self.health_check_interval,
        }
        if self.username is not None:
            kwargs["username"] = self.username
        if self.password is not None:
            kwargs["password"] = self.password
        if self.ssl:
            kwargs["ssl"] = True
        return kwargs
