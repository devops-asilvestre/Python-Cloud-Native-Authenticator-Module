"""Structural contract for AWS Foundation client/resource creation."""

from __future__ import annotations

from typing import Any, Protocol

from botocore.config import Config  # type: ignore[import-untyped]


class AwsDynamoDbFactoryContract(Protocol):
    """The minimal AWS factory surface required by DynamoDB adapters."""

    def create_client(
        self,
        service_name: str,
        *,
        region_name: str | None = None,
        endpoint_url: str | None = None,
        config: Config | None = None,
    ) -> Any: ...

    def create_resource(
        self,
        service_name: str,
        *,
        region_name: str | None = None,
        endpoint_url: str | None = None,
        config: Config | None = None,
    ) -> Any: ...
