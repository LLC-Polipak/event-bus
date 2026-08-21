"""Структуры метаданных зарегистрированных событий и их полей."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class EventField:
    """Метаданные поля зарегистрированного dataclass-события."""

    name: str
    annotation: Any
    required: bool
    default: Any
    fields: list['EventField'] = field(default_factory=list)


@dataclass(slots=True)
class EventDefinition:
    """Метаданные класса события, доступные в registry и API."""

    code: str
    title: str
    target: type
    fields: list[EventField]
    description: str | None = None
