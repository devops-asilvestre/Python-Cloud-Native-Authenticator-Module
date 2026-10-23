# AWS Foundation

This package provides the shared AWS integration foundation for the platform.

## Responsibilities

- Resolve configuration through `pydantic-settings`
- Use the AWS credential chain rather than hardcoded secrets
- Resolve region and account information centrally
- Create boto3 clients through factories
- Validate connectivity and health checks
- Keep services independent from concrete AWS SDK entry points

## Main components

- `AwsSettings`
- `AwsContext`
- `AwsSessionFactory`
- `AwsClientFactory`
- `AwsAccountResolver`
- `AwsRegionResolver`
- `AwsCredentialResolver`
- `AwsIdentityResolver`
- `AwsHealthCheck`
- `AwsConnectionValidator`
- `AwsObservability`

## Observability integration

The AWS foundation integrates with the shared observability contracts from the
platform foundation. Every session, client creation, and health-check flow emits
structured log events with request and telemetry correlation fields.

## Usage

```python
from shared.aws.factories.aws_client_factory import AwsClientFactory
from shared.aws.observability.aws_observability import AwsObservability
from shared.aws.settings.aws_settings import AwsSettings

settings = AwsSettings(region="us-east-1")
observability = AwsObservability(service_name="aws-foundation")
factory = AwsClientFactory(settings=settings, observability=observability)
client = factory.create_client("sts")
```
