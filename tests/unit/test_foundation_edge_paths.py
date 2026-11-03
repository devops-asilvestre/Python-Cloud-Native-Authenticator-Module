from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from botocore.exceptions import ClientError  # type: ignore[import-untyped]

from shared.aws.exceptions.aws_authentication_exception import AwsAuthenticationException
from shared.aws.exceptions.aws_configuration_exception import AwsConfigurationException
from shared.aws.factories.aws_client_factory import AwsClientFactory
from shared.aws.factories.aws_session_factory import AwsSessionFactory
from shared.aws.settings.aws_settings import AwsSettings
from shared.aws.testing.fake_clients import FakeSession
from shared.secrets.health.secret_health_check import SecretHealthCheck
from shared.secrets.validation.connection_validator import SecretConnectionValidator
from shared.secrets.versioning.secret_version_resolver import SecretVersionResolver


def _client_error() -> ClientError:
    return ClientError({"Error": {"Code": "AccessDenied", "Message": "denied"}}, "AssumeRole")


def test_secret_version_and_health_paths() -> None:
    assert SecretVersionResolver.resolve(
        response={"VersionId": "v1", "VersionStages": ["AWSPREVIOUS"]}
    ) == (
        "v1",
        "AWSPREVIOUS",
    )
    assert SecretVersionResolver.resolve(version_id="v2", version_stage="CUSTOM") == (
        "v2",
        "CUSTOM",
    )
    assert SecretVersionResolver.normalize_version_stage(None) == "AWSCURRENT"

    provider = Mock()
    provider.list_secrets.return_value = []
    check = SecretHealthCheck(provider)
    assert check.check()
    assert SecretConnectionValidator(check).is_connected()
    provider.list_secrets.side_effect = RuntimeError("offline")
    assert not check.check()


def test_session_factory_rejects_missing_credentials() -> None:
    class NoCredentialsSession:
        def get_credentials(self) -> None:
            return None

    with patch(
        "shared.aws.factories.aws_session_factory.boto3.Session",
        return_value=NoCredentialsSession(),
    ):
        with pytest.raises(AwsAuthenticationException):
            AwsSessionFactory(AwsSettings(region="us-east-1")).create()


def test_session_factory_assumes_role_and_wraps_client_error() -> None:
    class Sts:
        def assume_role(self, **_: str) -> dict[str, dict[str, str]]:
            return {
                "Credentials": {
                    "AccessKeyId": "key",
                    "SecretAccessKey": "secret",
                    "SessionToken": "token",
                }
            }

    session = FakeSession()
    session._clients["sts"] = Sts()
    settings = AwsSettings(region="us-east-1", role_arn="arn:aws:iam::1:role/app", assume_role=True)
    factory = AwsSessionFactory(settings)
    with patch("shared.aws.factories.aws_session_factory.boto3.Session", return_value=session):
        with patch(
            "shared.aws.factories.aws_session_factory.boto3.session.Session",
            return_value=session,
        ):
            assumed = factory.create()
    assert assumed is session

    failing = FakeSession()

    class FailingSts:
        def assume_role(self, **_: str) -> None:
            raise _client_error()

    failing._clients["sts"] = FailingSts()
    with patch("shared.aws.factories.aws_session_factory.boto3.Session", return_value=failing):
        with pytest.raises(AwsAuthenticationException):
            factory.create()


def test_aws_client_factory_validates_and_creates_resources() -> None:
    from botocore.exceptions import NoCredentialsError

    session = FakeSession()
    factory = AwsClientFactory(settings=AwsSettings(region="us-east-1"))
    assert factory.create_client("sts", session=session) is not None
    assert factory.create_resource("dynamodb", session=session) is not None
    with pytest.raises(AwsConfigurationException):
        factory.create_client("", session=session)

    class FailingSession(FakeSession):
        def client(self, *_: object, **__: object) -> object:
            raise NoCredentialsError()

        def resource(self, *_: object, **__: object) -> object:
            raise _client_error()

    failing = FailingSession()
    with pytest.raises(AwsAuthenticationException):
        factory.create_client("sts", session=failing)
    with pytest.raises(AwsConfigurationException):
        factory.create_resource("dynamodb", session=failing)
