"""Build DynamoDB partition keys with tenant isolation."""

from __future__ import annotations

from shared.dynamodb.exceptions.dynamodb_exception import DynamoDbException


class TenantAwarePartitionKeyBuilder:
    """Create partition keys in the required ``TENANT#{tenant_id}`` form."""

    def build(self, tenant_id: str) -> str:
        tenant = tenant_id.strip()
        if not tenant:
            raise DynamoDbException("Tenant ID cannot be empty.")
        return f"TENANT#{tenant}"
