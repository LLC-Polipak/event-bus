import dataclasses
from typing import get_type_hints

from event_bus.events.metadata import EventField


def get_event_fields(
    event: type,
) -> list[EventField]:
    """Возвращает поля события."""

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
    """Строит код события."""

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
    """Строит название события."""

    return event.__name__
