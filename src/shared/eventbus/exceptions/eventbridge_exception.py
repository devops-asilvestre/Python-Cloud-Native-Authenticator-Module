"""Exceptions raised by the shared EventBridge foundation."""


class EventBridgeException(Exception):
    """Base exception for EventBridge operations."""


class EventBridgeConfigurationException(EventBridgeException, ValueError):
    """Invalid EventBridge runtime configuration."""


class EventValidationException(EventBridgeException, ValueError):
    """Invalid event metadata, schema or tenant information."""


class EventBridgePublishException(EventBridgeException):
    """EventBridge rejected or could not accept an event publication."""
