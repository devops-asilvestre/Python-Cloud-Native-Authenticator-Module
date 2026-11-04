"""Configuration settings for shared AWS integrations."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class AwsSettings(BaseSettings):
    """Runtime settings for AWS integrations using the AWS credential chain."""

    model_config = SettingsConfigDict(
        env_prefix="AUTHENTICATOR_AWS_",
        env_file=".env",
        extra="ignore",
    )

    region: str = "us-east-1"
    account_id: str | None = None
    profile: str | None = None
    role_arn: str | None = None
    session_name: str = "authenticator-aws-session"
    default_output: str = "json"
    assume_role: bool = False
    use_fips_endpoint: bool = False
    use_dualstack_endpoint: bool = False

    @property
    def session_kwargs(self) -> dict[str, str | bool]:
        kwargs: dict[str, str | bool] = {"region_name": self.region}
        if self.profile:
            kwargs["profile_name"] = self.profile
        return kwargs
