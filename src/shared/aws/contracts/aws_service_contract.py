"""Abstract contract for AWS-backed services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AwsServiceContract(ABC):
    """Contract that every AWS-integrated service must satisfy."""

    @property
    @abstractmethod
    def service_name(self) -> str:
        """The AWS service name used to create the underlying client."""

    @abstractmethod
    def create_client(self, **kwargs: Any) -> Any:
        """Create the service client or dependency from the shared AWS factory."""
