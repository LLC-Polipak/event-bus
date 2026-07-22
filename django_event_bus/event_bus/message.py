import json
import uuid
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Any, Protocol


class Event(Protocol):
    event_name: str
    
    def payload(self) -> dict: ...
    

@dataclass(slots=True)
class EventMessage:
    event_id: uuid.UUID
    event: str
    event_name: str
    source: str
    occurred_at: datetime
    payload: dict[str, Any]
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "occurred_at": self.occurred_at.isoformat(),
            "source": self.source,
            "event": self.event,
            "event_name": self.event_name,
            "payload": self.payload,
        }


def build_message(source: str, event: Event) -> EventMessage:
    return EventMessage(
        event_id=uuid.uuid4(),
        occurred_at=datetime.now(UTC),
        source=source,
        event=f"{source}.{event.event_name}",
        event_name=event.event_name,
        payload=event.payload(),
    )

def serialize(message: dict) -> bytes:
    return json.dumps(message).encode()


def deserialize(body: bytes) -> dict:
    return json.loads(body.decode())
