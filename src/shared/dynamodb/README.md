# DynamoDB Foundation

Shared, tenant-aware DynamoDB integration for application adapters. The package
does not create tables or define business entities; table provisioning belongs
to infrastructure and repository implementations belong to their bounded
contexts.

## Components

- `DynamoDbSettings`: endpoint, region, retry and timeout configuration via
  `AUTHENTICATOR_DYNAMODB_*` environment variables.
- Client, resource and table factories: route SDK creation through
  `AwsClientFactory` and reuse named table handles.
- `DynamoDbRepositoryContract` and `DynamoDbItemContract`: persistence-facing
  protocols that keep domain models independent from boto3.
- Serializer/deserializer: boto3 AttributeValue conversion, including safe
  float-to-Decimal normalization.
- Key builders: `PK=TENANT#{tenant_id}` and `SK=ENTITY#{entity_id}`.
- TTL, version and metadata helpers: return enriched copies instead of
  mutating caller-owned dictionaries.
- `DynamoDbHealthCheck`: validates table access (or service access if no table
  is configured) without reading item data.
- `DynamoDbTableProvider`: returns table handles with structured operation
  outcomes for get, put, update, delete, query and scan.

## Configuration

```dotenv
AUTHENTICATOR_DYNAMODB_REGION_NAME=us-east-1
AUTHENTICATOR_DYNAMODB_ENDPOINT_URL=http://localhost:8000
AUTHENTICATOR_DYNAMODB_TABLE_NAME=application-items
```

Do not store AWS credentials in this configuration. Credentials are resolved
through the AWS foundation's standard credential chain. Leave the endpoint
unset for AWS DynamoDB.

## Usage

```python
from shared.dynamodb import DynamoDbKeyBuilder, DynamoDbSettings
from shared.dynamodb.providers.dynamodb_table_provider import DynamoDbTableProvider

settings = DynamoDbSettings()
table = DynamoDbTableProvider(settings=settings).get_table()
keys = DynamoDbKeyBuilder().build(tenant_id="tenant-42", entity_id="session-9")
table.get_item(Key=keys, ConsistentRead=True)
```

Repository methods must derive tenant keys from a server-validated tenant
context. A caller-supplied tenant identifier must not be treated as an
authorization decision.

## Local testing

Unit tests use the package fakes. Integration testing against DynamoDB Local
can use its endpoint through settings and AWS test credentials supplied via
the environment; no table is provisioned by this foundation.

Run:

```powershell
ruff check src/shared/dynamodb tests/unit/test_dynamodb_foundation.py
mypy --strict src/shared/dynamodb tests/unit/test_dynamodb_foundation.py
pytest -q tests/unit/test_dynamodb_foundation.py
```
