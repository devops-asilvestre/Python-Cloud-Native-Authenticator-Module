"""Provider abstraction for AWS client access."""

from __future__ import annotations

from typing import Any

from shared.aws.factories.aws_client_factory import AwsClientFactory


class AwsClientProvider:
    """Expose a client factory behind a simple provider interface."""

    def __init__(self, client_factory: AwsClientFactory | None = None) -> None:
        self._client_factory = client_factory or AwsClientFactory()

    def get_client(self, service_name: str, **kwargs: Any) -> Any:
        return self._client_factory.create_client(service_name, **kwargs)

    def __call__(self, service_name: str, **kwargs: Any) -> Any:
        return self.get_client(service_name, **kwargs)
