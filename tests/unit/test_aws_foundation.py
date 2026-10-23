import pytest

from shared.aws import AwsAccountResolver, AwsClientFactory, AwsConnectionValidator, AwsContext
from shared.aws.account.region_resolver import AwsRegionResolver
from shared.aws.authentication.credential_resolver import AwsCredentialResolver
from shared.aws.authentication.identity_resolver import AwsIdentityResolver
from shared.aws.factories.aws_session_factory import AwsSessionFactory
from shared.aws.observability import AwsObservability
from shared.aws.settings.aws_settings import AwsSettings
from shared.aws.testing.fake_clients import FakeSession


def test_aws_settings_are_loaded_from_env_defaults() -> None:
    settings = AwsSettings(region="eu-central-1", profile="team-profile")

    assert settings.region == "eu-central-1"
    assert settings.profile == "team-profile"
    assert settings.session_kwargs["region_name"] == "eu-central-1"


def test_aws_identity_and_account_resolution_from_fake_session() -> None:
    session = FakeSession(region_name="ap-southeast-2")

    identity = AwsIdentityResolver(session).resolve()
    assert identity.account_id == "123456789012"
    assert identity.region == "ap-southeast-2"

    account_id = AwsAccountResolver(session).resolve()
    assert account_id == "123456789012"


def test_aws_region_resolver_prefers_explicit_region() -> None:
    resolver = AwsRegionResolver(session=FakeSession(region_name="us-west-2"))

    assert resolver.resolve(explicit_region="sa-east-1") == "sa-east-1"
    assert resolver.resolve() == "us-west-2"


def test_aws_credential_resolver_reads_session_credentials() -> None:
    resolver = AwsCredentialResolver(FakeSession())

    assert resolver.resolve() is not None


def test_aws_client_factory_uses_configured_session() -> None:
    session = FakeSession(region_name="us-east-1")
    factory = AwsClientFactory(session_factory=AwsSessionFactory(), settings=AwsSettings(region="us-east-1"))

    client = factory.create_client("sts", session=session)
    assert client is not None


def test_aws_connection_validator_wraps_health_check() -> None:
    validator = AwsConnectionValidator()

    session = FakeSession()
    validator._health_check._session = session

    assert validator.validate() is True


def test_aws_context_serializes_metadata() -> None:
    context = AwsContext(account_id="42", region="us-east-1", metadata={"tenant": "tenant-9"})

    assert context.as_dict()["tenant"] == "tenant-9"
    assert context.as_dict()["account_id"] == "42"


def test_aws_observability_integrates_with_structured_logger() -> None:
    observability = AwsObservability(service_name="aws-tests")

    observability.info("aws_test_event", region_name="us-east-1")

    assert observability.logger is not None
    assert observability.request_context.request_id is not None
