"""Validated runtime settings for SQS."""

from __future__ import annotations

import re

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.aws.settings.aws_settings import AwsSettings
from shared.messaging.exceptions.sqs_exception import SqsConfigurationException


class SqsSettings(BaseSettings):
    """SQS configuration; queue URLs are always resolved from AWS."""

    model_config = SettingsConfigDict(
        env_prefix="AUTHENTICATOR_SQS_",
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )

    aws_region: str = Field(default_factory=lambda: AwsSettings().region)
    account_id: str
    queue_prefix: str
    environment: str
    endpoint_url: str | None = None
    default_visibility_timeout: int = 30
    default_wait_time: int = 20
    default_max_receive_count: int = 5

    @model_validator(mode="after")
    def validate_settings(self) -> SqsSettings:
        if not re.fullmatch(r"[a-z]{2,}(?:-[a-z0-9]+)+-[0-9]+", self.aws_region):
            raise SqsConfigurationException("A valid AWS region is required for SQS.")
        if not re.fullmatch(r"\d{12}", self.account_id):
            raise SqsConfigurationException("The AWS account ID must contain 12 digits.")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", self.queue_prefix):
            raise SqsConfigurationException("The SQS queue prefix contains invalid characters.")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,20}", self.environment):
            raise SqsConfigurationException("The SQS environment contains invalid characters.")
        if not 0 < self.default_visibility_timeout <= 43200:
            raise SqsConfigurationException("SQS visibility timeout must be between 1 and 43200.")
        if not 0 <= self.default_wait_time <= 20:
            raise SqsConfigurationException("SQS wait time must be between 0 and 20.")
        if self.default_max_receive_count < 1:
            raise SqsConfigurationException("SQS max receive count must be positive.")
        if self.endpoint_url is not None and not self.endpoint_url.strip():
            raise SqsConfigurationException("The SQS endpoint URL cannot be empty.")
        return self
