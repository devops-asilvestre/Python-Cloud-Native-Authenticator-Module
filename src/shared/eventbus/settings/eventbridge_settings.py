"""Validated runtime settings for AWS EventBridge."""

from __future__ import annotations

import re

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.aws.settings.aws_settings import AwsSettings
from shared.eventbus.exceptions.eventbridge_exception import EventBridgeConfigurationException


class EventBridgeSettings(BaseSettings):
    """AWS EventBridge configuration for corporate event routing."""

    model_config = SettingsConfigDict(
        env_prefix="AUTHENTICATOR_EVENTBRIDGE_",
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )

    aws_region: str = Field(default_factory=lambda: AwsSettings().region)
    account_id: str
    bus_name: str
    environment: str = "dev"
    endpoint_url: str | None = None
    archive_enabled: bool = False
    replay_enabled: bool = False
    retention_days: int = 30

    @model_validator(mode="after")
    def validate_settings(self) -> EventBridgeSettings:
        if not re.fullmatch(r"[a-z]{2,}(?:-[a-z0-9]+)+-[0-9]+", self.aws_region):
            raise EventBridgeConfigurationException(
                "A valid AWS region is required for EventBridge."
            )
        if not re.fullmatch(r"\d{12}", self.account_id):
            raise EventBridgeConfigurationException(
                "The AWS account ID must contain 12 digits."
            )
        if not self.bus_name or not self.bus_name.strip():
            raise EventBridgeConfigurationException("The EventBridge bus name is required.")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", self.bus_name.strip()):
            raise EventBridgeConfigurationException(
                "The EventBridge bus name contains invalid characters."
            )
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,20}", self.environment):
            raise EventBridgeConfigurationException(
                "The EventBridge environment contains invalid characters."
            )
        if self.endpoint_url is not None and not self.endpoint_url.strip():
            raise EventBridgeConfigurationException(
                "The EventBridge endpoint URL cannot be empty."
            )
        if self.retention_days < 1:
            raise EventBridgeConfigurationException(
                "EventBridge retention days must be positive."
            )
        return self

    @property
    def is_local_endpoint(self) -> bool:
        if self.endpoint_url is None:
            return False
        return "localhost" in self.endpoint_url or "127.0.0.1" in self.endpoint_url
