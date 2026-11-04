"""Runtime configuration for DynamoDB integrations."""

from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DynamoDbSettings(BaseSettings):
    """DynamoDB endpoint and request settings without embedded credentials."""

    model_config = SettingsConfigDict(
        env_prefix="AUTHENTICATOR_DYNAMODB_",
        env_file=".env",
        extra="ignore",
    )

    region_name: str | None = None
    endpoint_url: str | None = None
    table_name: str | None = None
    connect_timeout_seconds: int = Field(default=5, gt=0)
    read_timeout_seconds: int = Field(default=10, gt=0)
    max_attempts: int = Field(default=3, gt=0)

    @field_validator("region_name", "endpoint_url", "table_name")
    @classmethod
    def strip_optional_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None
