"""Tenant-bound KMS encryption adapter for message payloads."""

from __future__ import annotations

import base64
import json
from typing import Any
from uuid import UUID

from shared.events.envelope.event_envelope import EventEnvelope
from shared.kms.contracts.kms_provider_contract import KmsProviderContract
from shared.kms.exceptions.kms_decryption_exception import KmsDecryptionException
from shared.kms.exceptions.kms_encryption_exception import KmsEncryptionException
from shared.kms.resolver.kms_key_resolver import KmsKeyResolver
from shared.kms.services.decryption_service import DecryptionService
from shared.kms.services.encryption_service import EncryptionService
from shared.messaging.exceptions.sqs_exception import MessageConsumeException
from shared.observability.context.request_context import RequestContext


class KmsMessageEncryption:
    """Encrypt serialized envelopes while leaving only routing metadata visible."""

    _purpose = "sqs-message-payload"

    def __init__(self, provider: KmsProviderContract, resolver: KmsKeyResolver) -> None:
        self._provider = provider
        self._resolver = resolver

    def encrypt(self, event: EventEnvelope, plaintext: bytes) -> str:
        request_context = RequestContext(
            tenant_id=event.tenant_id,
            correlation_id=event.correlation_id,
            trace_id=event.trace_id,
        )
        service = EncryptionService(self._provider, self._resolver, request_context=request_context)
        context = {"event_id": str(event.event_id), "purpose": self._purpose}
        try:
            encrypted = service.encrypt(plaintext, context=context)
        except KmsEncryptionException:
            raise
        return json.dumps(
            {
                "encrypted": True,
                "tenant_id": event.tenant_id,
                "event_id": str(event.event_id),
                "ciphertext": base64.b64encode(encrypted.ciphertext).decode("ascii"),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )

    def decrypt(self, body: str) -> bytes:
        try:
            wrapper: Any = json.loads(body)
            if (
                not isinstance(wrapper, dict)
                or set(wrapper) != {"encrypted", "tenant_id", "event_id", "ciphertext"}
                or wrapper.get("encrypted") is not True
                or not isinstance(wrapper.get("tenant_id"), str)
                or not isinstance(wrapper.get("event_id"), str)
                or not isinstance(wrapper.get("ciphertext"), str)
            ):
                raise MessageConsumeException("Encrypted SQS message wrapper is invalid.")
            event_id = UUID(wrapper["event_id"])
            ciphertext = base64.b64decode(wrapper["ciphertext"], validate=True)
            if not ciphertext:
                raise MessageConsumeException("Encrypted SQS message has no ciphertext.")
        except MessageConsumeException:
            raise
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            raise MessageConsumeException("Encrypted SQS message wrapper is invalid.") from exc

        tenant_id = wrapper["tenant_id"]
        service = DecryptionService(
            self._provider,
            self._resolver,
            request_context=RequestContext(tenant_id=tenant_id),
        )
        try:
            return service.decrypt(
                ciphertext,
                context={"event_id": str(event_id), "purpose": self._purpose},
            )
        except KmsDecryptionException as exc:
            raise MessageConsumeException("SQS message decryption failed.") from exc
