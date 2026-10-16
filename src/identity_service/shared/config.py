from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AUTHENTICATOR_",
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "Python Cloud Native Authenticator Module"
    environment: Literal["local", "test", "staging", "production"] = "local"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
