"""Формирование транспортных сообщений event bus и их JSON-кодирование."""

import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol


class Event(Protocol):
    """Контракт доменного события, допустимого к публикации."""

    event_name: str

    def payload(self) -> dict:
        """Вернуть данные события для транспортного сообщения."""
        ...


@dataclass(slots=True)
class EventMessage:
    """Транспортное сообщение с метаданными и payload доменного события."""

    event_id: uuid.UUID
    event: str
    event_name: str
    source: str
    occurred_at: datetime
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать сообщение в JSON-совместимый словарь."""
        return {
            'event_id': str(self.event_id),
            'occurred_at': self.occurred_at.isoformat(),
            'source': self.source,
            'event': self.event,
            'event_name': self.event_name,
            'payload': self.payload,
        }


def build_message(source: str, event: Event) -> EventMessage:
    """Создать транспортное сообщение из доменного события и источника."""
    return EventMessage(
        event_id=uuid.uuid4(),
        occurred_at=datetime.now(UTC),
        source=source,
        event=f'{source}.{event.event_name}',
        event_name=event.event_name,
        payload=event.payload(),
    )


def serialize(message: dict) -> bytes:
    """Закодировать словарь транспортного сообщения в JSON-байты."""
    return json.dumps(message).encode()


def deserialize(body: bytes) -> dict:
    """Декодировать JSON-байты RabbitMQ-сообщения в словарь."""
    return json.loads(body.decode())
