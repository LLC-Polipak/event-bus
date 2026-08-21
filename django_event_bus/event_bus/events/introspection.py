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

    return _get_event_fields(
        event,
        ancestors=frozenset({event}),
    )


def _get_event_fields(
    event: type,
    *,
    ancestors: frozenset[type],
) -> list[EventField]:
    """Рекурсивно собрать поля dataclass с защитой от циклических ссылок."""
    type_hints = get_type_hints(event)

    fields: list[EventField] = []

    for dataclass_field in dataclasses.fields(
        event,
    ):
        required = (
            dataclass_field.default is dataclasses.MISSING
            and dataclass_field.default_factory is dataclasses.MISSING
        )

        default = None

        if dataclass_field.default is not dataclasses.MISSING:
            default = dataclass_field.default

        annotation = type_hints.get(dataclass_field.name)
        nested_fields: list[EventField] = []

        if dataclasses.is_dataclass(annotation) and annotation not in ancestors:
            nested_fields = _get_event_fields(
                annotation,
                ancestors=ancestors | {annotation},
            )

        fields.append(
            EventField(
                name=dataclass_field.name,
                annotation=annotation,
                required=required,
                default=default,
                fields=nested_fields,
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
