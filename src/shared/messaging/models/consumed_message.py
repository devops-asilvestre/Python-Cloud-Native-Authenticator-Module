"""A decoded message and its SQS acknowledgement metadata."""

from dataclasses import dataclass

from shared.events.envelope.event_envelope import EventEnvelope


@dataclass(frozen=True, slots=True)
class ConsumedMessage:
    """Decoded event associated with a receipt handle."""

    event: EventEnvelope
    receipt_handle: str
    receive_count: int
    message_id: str
