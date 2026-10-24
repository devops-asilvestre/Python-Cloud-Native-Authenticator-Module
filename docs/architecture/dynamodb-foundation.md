# DynamoDB Foundation

The shared DynamoDB package supplies SDK access and persistence primitives;
it does not own any bounded-context schema or provision tables.

## Architecture

Application adapter -> repository contract -> table provider -> DynamoDB
factory -> AWS `AwsClientFactory` -> boto3 -> DynamoDB

Domain types do not import boto3, AWS configuration, or the persistence
implementation. Repositories must derive tenant keys only from a tenant
identity validated by the server.

## Shared item conventions

- Partition key: `PK=TENANT#{tenant_id}`
- Sort key: `SK=ENTITY#{entity_id}`
- TTL uses a timezone-aware timestamp converted to epoch seconds.
- Version and metadata helpers create enriched copies and preserve caller data.
- Structured operation logs contain operation, table, and correlation context;
  they do not include item contents or key values.

Table schemas, indexes, TTL enablement and encryption are infrastructure
responsibilities. This foundation performs no table creation or migrations.

## Configuration and credentials

`DynamoDbSettings` reads `AUTHENTICATOR_DYNAMODB_*` variables. Optional endpoint
configuration supports DynamoDB Local. AWS credentials and account configuration
continue to be resolved by the AWS foundation; application code must not create
boto3 clients or resources directly.

## Operations

The table provider logs outcomes for get, put, update, delete, query and scan.
Health validation uses `DescribeTable` when a table is configured and a
non-data `ListTables` request otherwise. OpenTelemetry span creation remains
outside the scope of this foundation.
