"""Settings for secret resolution and cache configuration."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class SecretsSettings(BaseSettings):
    """Runtime settings used by the shared Secrets Manager foundation."""

    model_config = SettingsConfigDict(
        env_prefix="AUTHENTICATOR_SECRETS_",
        env_file=".env",
        extra="ignore",
    )

    region: str = "us-east-1"
    account_id: str | None = None
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    default_version_stage: str = "AWSCURRENT"
    mask_visible_prefix: int = 2
    mask_visible_suffix: int = 2
    default_timeout_seconds: int = 30
    max_cache_entries: int = 256
