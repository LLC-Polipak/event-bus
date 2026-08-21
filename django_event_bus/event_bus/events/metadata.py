"""Структуры метаданных зарегистрированных событий и их полей."""

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class EventField:
    """Метаданные поля зарегистрированного dataclass-события."""

    name: str
    annotation: Any
    required: bool
    default: Any


@dataclass(slots=True)
class EventDefinition:
    """Метаданные класса события, доступные в registry и API."""

    code: str
    title: str
    target: type
    fields: list[EventField]
    description: str | None = None
