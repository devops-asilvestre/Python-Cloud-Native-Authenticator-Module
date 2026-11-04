"""Durable idempotency claims using the shared DynamoDB table foundation."""

from __future__ import annotations

from time import time
from typing import Any, Protocol
from uuid import uuid4

from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-untyped]

from shared.messaging.exceptions.sqs_exception import IdempotencyException
from shared.messaging.idempotency.idempotency_key import IdempotencyKey


class IdempotencyDynamoTableContract(Protocol):
    """Subset of the shared observed table API required by the store."""

    def put_item(self, **kwargs: Any) -> Any: ...

    def update_item(self, **kwargs: Any) -> Any: ...

    def delete_item(self, **kwargs: Any) -> Any: ...


class DynamoDbIdempotencyStore:
    """Lease-based atomic claims on a pre-provisioned shared DynamoDB table."""

    def __init__(
        self,
        table: IdempotencyDynamoTableContract,
        *,
        lease_seconds: int = 300,
        retention_seconds: int = 7_776_000,
    ) -> None:
        if lease_seconds < 1 or retention_seconds < lease_seconds:
            raise ValueError("Idempotency retention must be at least the positive lease duration.")
        self._table = table
        self._lease_seconds = lease_seconds
        self._retention_seconds = retention_seconds

    def claim(self, key: IdempotencyKey) -> str | None:
        now = int(time())
        claim_token = uuid4().hex
        try:
            self._table.put_item(
                Item={
                    "id": key.value,
                    "status": "processing",
                    "claim_token": claim_token,
                    "lease_expires_at": now + self._lease_seconds,
                    "expires_at": now + self._retention_seconds,
                },
                ConditionExpression=(
                    "attribute_not_exists(id) OR "
                    "(#status = :processing AND lease_expires_at <= :now)"
                ),
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={":processing": "processing", ":now": now},
            )
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
                return None
            raise IdempotencyException("DynamoDB could not acquire the idempotency claim.") from exc
        except BotoCoreError as exc:
            raise IdempotencyException("DynamoDB could not acquire the idempotency claim.") from exc
        return claim_token

    def complete(self, key: IdempotencyKey, *, claim_token: str) -> None:
        now = int(time())
        try:
            self._table.update_item(
                Key={"id": key.value},
                UpdateExpression=(
                    "SET #status = :completed, completed_at = :now, expires_at = :expires "
                    "REMOVE lease_expires_at"
                ),
                ConditionExpression="#status = :processing AND claim_token = :claim_token",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":completed": "completed",
                    ":processing": "processing",
                    ":claim_token": claim_token,
                    ":now": now,
                    ":expires": now + self._retention_seconds,
                },
            )
        except (BotoCoreError, ClientError) as exc:
            raise IdempotencyException(
                "DynamoDB could not complete the idempotency claim."
            ) from exc

    def release(self, key: IdempotencyKey, *, claim_token: str) -> None:
        try:
            self._table.delete_item(
                Key={"id": key.value},
                ConditionExpression="#status = :processing AND claim_token = :claim_token",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":processing": "processing",
                    ":claim_token": claim_token,
                },
            )
        except (BotoCoreError, ClientError) as exc:
            raise IdempotencyException("DynamoDB could not release the idempotency claim.") from exc
