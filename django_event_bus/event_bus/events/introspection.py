"""Извлечение метаданных из dataclass-классов доменных событий."""

import dataclasses
from typing import get_type_hints

from django_event_bus.event_bus.events.metadata import EventField


def get_event_fields(
    event: type,
) -> list[EventField]:
    """Вернуть описания dataclass-полей события.

    Raises:
        TypeError: Переданный класс не является dataclass.
    """
    if not dataclasses.is_dataclass(
        event,
    ):
        raise TypeError(
            f'"{event.__qualname__}" должен быть dataclass.',
        )

    type_hints = get_type_hints(
        event,
    )

    fields: list[EventField] = []

    for field in dataclasses.fields(
        event,
    ):
        required = (
            field.default is dataclasses.MISSING
            and field.default_factory is dataclasses.MISSING
        )

        default = None

        if field.default is not dataclasses.MISSING:
            default = field.default

        fields.append(
            EventField(
                name=field.name,
                annotation=type_hints.get(
                    field.name,
                ),
                required=required,
                default=default,
            ),
        )

    return fields


def build_event_code(
    event: type,
) -> str:
    """Преобразовать CamelCase-имя класса события в точечный код."""
    name = event.__name__

    parts: list[str] = []
    current = ''

    for char in name:
        if char.isupper() and current:
            parts.append(
                current.lower(),
            )
            current = char
        else:
            current += char

    if current:
        parts.append(
            current.lower(),
        )

    return '.'.join(parts)


def build_event_title(
    event: type,
) -> str:
    """Вернуть имя класса как отображаемое название события."""
    return event.__name__
