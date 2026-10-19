"""Structured log entry model."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

_SENSITIVE_KEYS = {
    "password",
    "passwd",
    "secret",
    "token",
    "authorization",
    "api_key",
    "apikey",
    "cookie",
    "session",
    "credential",
    "private_key",
    "client_secret",
}


class StructuredLogEntry(BaseModel):
    """JSON-serializable representation of a structured log."""

    model_config = ConfigDict(extra="ignore")

    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    level: str = "INFO"
    event: str = ""
    message: str = ""
    service: str | None = None
    request_id: str | None = None
    correlation_id: str | None = None
    trace_id: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)

    def model_dump_json(self, **kwargs: Any) -> str:
        """Render the entry as a JSON payload with redacted sensitive fields."""

        return super().model_dump_json(**kwargs)

    def sanitize(self) -> "StructuredLogEntry":
        """Return a copy with sensitive values redacted."""

        sanitized = self.model_copy(deep=True)
        sanitized.attributes = self._redact_attributes(sanitized.attributes)
        return sanitized

    @staticmethod
    def _redact_attributes(attributes: dict[str, Any]) -> dict[str, Any]:
        redacted: dict[str, Any] = {}
        for key, value in attributes.items():
            normalized_key = str(key).lower()
            if any(token in normalized_key for token in _SENSITIVE_KEYS):
                redacted[key] = "[REDACTED]"
            elif isinstance(value, dict):
                redacted[key] = StructuredLogEntry._redact_attributes(value)
            elif isinstance(value, list):
                redacted[key] = [
                    StructuredLogEntry._redact_attributes(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                redacted[key] = value
        return redacted
