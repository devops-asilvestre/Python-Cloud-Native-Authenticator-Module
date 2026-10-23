"""Utility fake clients used while testing AWS foundations."""

from __future__ import annotations


class FakeSTSClient:
    """Simple STS-like client with a caller identity response."""

    def __init__(self, *, account_id: str = "123456789012", arn: str = "arn:aws:sts::123456789012:assumed-role/test-role") -> None:
        self.account_id = account_id
        self.arn = arn

    def get_caller_identity(self) -> dict[str, str]:
        return {"Account": self.account_id, "Arn": self.arn, "UserId": "fake-user"}


class FakeSession:
    """Minimal boto3 session clone for tests."""

    def __init__(self, *, region_name: str = "us-east-1", profile_name: str | None = None) -> None:
        self.region_name = region_name
        self.profile_name = profile_name
        self._credentials = object()
        self._clients: dict[str, object] = {"sts": FakeSTSClient()}

    def get_credentials(self) -> object | None:
        return self._credentials

    def client(self, service_name: str, *, region_name: str | None = None, config: object | None = None) -> object:
        if service_name not in self._clients:
            self._clients[service_name] = FakeSTSClient()
        return self._clients[service_name]
