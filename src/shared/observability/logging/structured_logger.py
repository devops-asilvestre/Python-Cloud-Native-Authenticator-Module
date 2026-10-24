"""Structured logger implementation using stdlib logging or structlog."""

from __future__ import annotations

import json
import logging
from typing import Any

from shared.observability.context.request_context import RequestContext
from shared.observability.context.telemetry_context import TelemetryContext
from shared.observability.logging.logger_contract import LoggerContract
from shared.observability.logging.structured_log_entry import StructuredLogEntry

structlog: Any | None = None
try:
    import structlog as structlog_module
except ModuleNotFoundError:  # pragma: no cover - exercised when dependency is absent.
    pass
else:
    structlog = structlog_module


class StructuredLogger(LoggerContract):
    """Structured logger with request and telemetry correlation."""

    def __init__(
        self,
        name: str,
        *,
        telemetry_context: TelemetryContext | None = None,
        request_context: RequestContext | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.name = name
        self.telemetry_context = telemetry_context or TelemetryContext(service_name=name)
        self.request_context = (
            request_context
            or self.telemetry_context.request_context
            or RequestContext()
        )
        self._logger = logger or logging.getLogger(name)
        self._structlog = structlog if structlog is not None else None

    def log(self, event: str, *, level: str = "INFO", **fields: Any) -> None:
        """Emit a structured log entry with contextual metadata."""

        entry = self._build_entry(event=event, level=level, **fields)
        if self._structlog is not None:
            bind = {
                "service": entry.service,
                "request_id": entry.request_id,
                "correlation_id": entry.correlation_id,
                "trace_id": entry.trace_id,
                **self._sanitize_fields(entry.attributes),
            }
            self._structlog.get_logger(self.name).bind(**bind).info(event)
            return

        payload = entry.sanitize().model_dump(mode="json")
        numeric_level = logging.getLevelNamesMapping().get(level.upper(), logging.INFO)
        self._logger.log(numeric_level, json.dumps(payload, default=str))

    def debug(self, event: str, **fields: Any) -> None:
        self.log(event, level="DEBUG", **fields)

    def info(self, event: str, **fields: Any) -> None:
        self.log(event, level="INFO", **fields)

    def warning(self, event: str, **fields: Any) -> None:
        self.log(event, level="WARNING", **fields)

    def error(self, event: str, **fields: Any) -> None:
        self.log(event, level="ERROR", **fields)

    def _build_entry(self, event: str, *, level: str, **fields: Any) -> StructuredLogEntry:
        context = self.request_context
        attributes = self._sanitize_fields(fields)
        return StructuredLogEntry(
            level=level.upper(),
            event=event,
            message=event,
            service=self.telemetry_context.service_name,
            request_id=str(context.request_id),
            correlation_id=str(context.correlation_id),
            trace_id=str(context.trace_id),
            attributes=attributes,
        )

    @staticmethod
    def _sanitize_fields(fields: dict[str, Any]) -> dict[str, Any]:
        return StructuredLogEntry._redact_attributes(fields)
