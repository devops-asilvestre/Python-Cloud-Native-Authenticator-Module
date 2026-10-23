"""Stable high-level event categories."""

from enum import StrEnum


class EventCategory(StrEnum):
    """Semantic category used for classification, not transport routing."""

    DOMAIN = "domain"
    INTEGRATION = "integration"
    AUDIT = "audit"
    SECURITY = "security"
    OPERATIONAL = "operational"
