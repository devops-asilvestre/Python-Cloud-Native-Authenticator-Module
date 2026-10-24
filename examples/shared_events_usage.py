"""Executable example of registering, validating, and round-tripping an event."""

from pydantic import BaseModel, ConfigDict, Field

from shared.events import (
    EventDeserializer,
    EventRegistry,
    EventSchemaValidator,
    EventVersion,
    JsonEventSerializer,
)
from shared.events.testing import make_fake_user_created_event


class UserCreatedPayload(BaseModel):
    """Allowlisted payload for a user-created event."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    user_id: str = Field(min_length=1)


def main() -> None:
    registry = EventRegistry()
    registry.register(
        "identity.user.created",
        EventVersion(major=1),
        UserCreatedPayload,
    )
    validator = EventSchemaValidator(registry)
    event = make_fake_user_created_event()
    encoded = JsonEventSerializer(validator).serialize(event)
    decoded = EventDeserializer(validator).deserialize(encoded)
    print(decoded.model_dump_json())


if __name__ == "__main__":
    main()
