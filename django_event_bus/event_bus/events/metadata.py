from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class EventField:
    """Описывает поле зарегистрированного события."""

    name: str
    annotation: Any
    required: bool
    default: Any


@dataclass(slots=True)
class EventDefinition:
    """Описывает зарегистрированное событие."""

    code: str
    title: str
    target: type
    fields: list[EventField]
    description: str | None = None
