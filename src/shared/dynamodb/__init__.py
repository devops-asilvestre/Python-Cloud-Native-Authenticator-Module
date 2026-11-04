"""Shared DynamoDB persistence foundation."""

from shared.dynamodb.context.dynamodb_context import DynamoDbContext
from shared.dynamodb.contracts.dynamodb_item_contract import DynamoDbItemContract
from shared.dynamodb.contracts.dynamodb_repository_contract import (
    DynamoDbRepositoryContract,
)
from shared.dynamodb.exceptions.dynamodb_connection_exception import DynamoDbConnectionException
from shared.dynamodb.exceptions.dynamodb_exception import DynamoDbException
from shared.dynamodb.exceptions.dynamodb_serialization_exception import (
    DynamoDbSerializationException,
)
from shared.dynamodb.factories.dynamodb_client_factory import DynamoDbClientFactory
from shared.dynamodb.factories.dynamodb_resource_factory import DynamoDbResourceFactory
from shared.dynamodb.factories.dynamodb_table_factory import DynamoDbTableFactory
from shared.dynamodb.keys.dynamodb_key_builder import DynamoDbKeyBuilder
from shared.dynamodb.keys.partition_key_builder import TenantAwarePartitionKeyBuilder
from shared.dynamodb.keys.sort_key_builder import TenantAwareSortKeyBuilder
from shared.dynamodb.metadata.metadata_support import MetadataSupport
from shared.dynamodb.metadata.ttl_support import TtlSupport
from shared.dynamodb.metadata.version_support import VersionSupport
from shared.dynamodb.observability.dynamodb_observability import DynamoDbObservability
from shared.dynamodb.providers.dynamodb_table_provider import DynamoDbTableProvider
from shared.dynamodb.serialization.dynamodb_deserializer import DynamoDbDeserializer
from shared.dynamodb.serialization.dynamodb_serializer import DynamoDbSerializer
from shared.dynamodb.settings.dynamodb_settings import DynamoDbSettings
from shared.dynamodb.validation.dynamodb_connection_validator import (
    DynamoDbConnectionValidator,
)
from shared.dynamodb.validation.dynamodb_health_check import DynamoDbHealthCheck

__all__ = [
    "DynamoDbClientFactory",
    "DynamoDbConnectionException",
    "DynamoDbConnectionValidator",
    "DynamoDbContext",
    "DynamoDbDeserializer",
    "DynamoDbException",
    "DynamoDbHealthCheck",
    "DynamoDbItemContract",
    "DynamoDbKeyBuilder",
    "DynamoDbObservability",
    "DynamoDbResourceFactory",
    "DynamoDbRepositoryContract",
    "DynamoDbSerializationException",
    "DynamoDbSerializer",
    "DynamoDbSettings",
    "DynamoDbTableFactory",
    "DynamoDbTableProvider",
    "MetadataSupport",
    "TenantAwarePartitionKeyBuilder",
    "TenantAwareSortKeyBuilder",
    "TtlSupport",
    "VersionSupport",
]
