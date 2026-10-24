"""Idempotency validation over an atomic persistence port."""

import asyncio
from contextvars import ContextVar
from typing import Protocol

from shared.messaging.exceptions.sqs_exception import IdempotencyException
from shared.messaging.idempotency.idempotency_key import IdempotencyKey


class IdempotencyStoreContract(Protocol):
    """Atomic, durable claim lifecycle backed by shared persistence."""

    def claim(self, key: IdempotencyKey) -> str | None:
        """Return a claim token, or None if a completed/active claim exists."""
        ...

    def complete(self, key: IdempotencyKey, *, claim_token: str) -> None:
        """Persist successful processing for the claimed key."""
        ...

    def release(self, key: IdempotencyKey, *, claim_token: str) -> None:
        """Release an unsuccessful claim so SQS redelivery may retry it."""
        ...


class IdempotencyValidator:
    """Prevent duplicate handling through a durable atomic key claim."""

    def __init__(self, store: IdempotencyStoreContract) -> None:
        self._store = store
        self._claims: ContextVar[dict[str, str] | None] = ContextVar(
            "messaging_idempotency_claims",
            default=None,
        )

    async def is_duplicate(self, *, message_id: str, event_id: str, tenant_id: str) -> bool:
        key = self._key(message_id=message_id, event_id=event_id, tenant_id=tenant_id)
        claim_token = await asyncio.to_thread(self._store.claim, key)
        if claim_token is None:
            return True
        claims = self._claims.get() or {}
        self._claims.set({**claims, key.value: claim_token})
        return False

    async def mark_processed(self, *, message_id: str, event_id: str, tenant_id: str) -> None:
        key = self._key(message_id=message_id, event_id=event_id, tenant_id=tenant_id)
        claim_token = self._claim_token(key)
        await asyncio.to_thread(self._store.complete, key, claim_token=claim_token)
        self._remove_claim(key)

    async def release(self, *, message_id: str, event_id: str, tenant_id: str) -> None:
        key = self._key(message_id=message_id, event_id=event_id, tenant_id=tenant_id)
        claim_token = self._claim_token(key)
        await asyncio.to_thread(self._store.release, key, claim_token=claim_token)
        self._remove_claim(key)

    def _claim_token(self, key: IdempotencyKey) -> str:
        claims = self._claims.get() or {}
        claim_token = claims.get(key.value)
        if claim_token is None:
            raise IdempotencyException("No active idempotency claim exists for this event.")
        return claim_token

    def _remove_claim(self, key: IdempotencyKey) -> None:
        claims = self._claims.get() or {}
        self._claims.set({value: token for value, token in claims.items() if value != key.value})

    @staticmethod
    def _key(*, message_id: str, event_id: str, tenant_id: str) -> IdempotencyKey:
        if not message_id.strip() or not event_id.strip() or not tenant_id.strip():
            raise IdempotencyException("Message, event, and tenant identifiers are required.")
        return IdempotencyKey(tenant_id=tenant_id, event_id=event_id)
