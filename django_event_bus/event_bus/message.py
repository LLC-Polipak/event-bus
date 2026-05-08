import json
import uuid
from datetime import datetime


def build_message(source: str, event: str, payload: dict) -> dict:
    return {
        'event_id': str(uuid.uuid4()),
        'event_name': f'{source}.{event}',
        'source': source,
        'event': event,
        'occurred_at': datetime.utcnow().isoformat(),
        'payload': payload,
    }


def serialize(message: dict) -> bytes:
    return json.dumps(message).encode()


def deserialize(body: bytes) -> dict:
    return json.loads(body.decode())
