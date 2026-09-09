"""Извлечение метаданных из dataclass-классов доменных событий."""

import dataclasses
import types
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Union, get_args, get_origin, get_type_hints
from uuid import UUID

from django_event_bus.event_bus.events.fields import get_event_field_metadata
from django_event_bus.event_bus.events.metadata import EventField


def get_event_fields(event: type) -> list[EventField]:
    """Вернуть и провалидировать описания dataclass-полей события."""
    if not dataclasses.is_dataclass(event):
        name = getattr(event, '__qualname__', repr(event))
        raise TypeError(f'"{name}" должен быть dataclass.')
    return _get_event_fields(event, ancestors=frozenset({event}))


def _get_event_fields(
    event: type,
    *,
    ancestors: frozenset[type],
) -> list[EventField]:
    try:
        type_hints = get_type_hints(event)
    except (NameError, TypeError):
        type_hints = dict(getattr(event, '__annotations__', {}))

    result: list[EventField] = []
    for dataclass_field in dataclasses.fields(event):
        annotation = type_hints.get(dataclass_field.name, dataclass_field.type)
        metadata = get_event_field_metadata(dataclass_field.metadata)
        title = metadata.get('title') or _build_field_title(dataclass_field.name)
        if not title:
            raise ValueError(
                f'Невозможно сформировать title для поля "{dataclass_field.name}".',
            )

        required = (
            dataclass_field.default is dataclasses.MISSING
            and dataclass_field.default_factory is dataclasses.MISSING
        )
        default = None
        if dataclass_field.default is not dataclasses.MISSING:
            default = dataclass_field.default

        json_type, nullable, effective_annotation = describe_annotation(annotation)
        example = metadata.get('example', None)
        if 'example' in metadata and not _matches_annotation(example, annotation):
            raise TypeError(
                f'Пример поля "{dataclass_field.name}" несовместим '
                f'с аннотацией {annotation!r}.',
            )

        nested_fields: list[EventField] = []
        if (
            dataclasses.is_dataclass(effective_annotation)
            and effective_annotation not in ancestors
        ):
            nested_fields = _get_event_fields(
                effective_annotation,
                ancestors=ancestors | {effective_annotation},
            )

        result.append(
            EventField(
                name=dataclass_field.name,
                annotation=annotation,
                required=required,
                default=default,
                title=title,
                description=metadata.get('description', ''),
                example=example,
                type=json_type,
                nullable=nullable,
                fields=nested_fields,
            ),
        )
    return result


def describe_annotation(annotation: Any) -> tuple[str, bool, Any]:  # noqa: C901
    """Вернуть каталоговый тип, nullable и аннотацию без ``None``."""
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin in (Union, types.UnionType) and type(None) in args:
        non_none = tuple(item for item in args if item is not type(None))
        if len(non_none) == 1:
            json_type, _, effective = describe_annotation(non_none[0])
            return json_type, True, effective
        return 'unknown', True, annotation

    if annotation is str:
        return 'string', False, annotation
    if annotation is int:
        return 'integer', False, annotation
    if annotation in (float, Decimal):
        return 'number', False, annotation
    if annotation is bool:
        return 'boolean', False, annotation
    if annotation is datetime:
        return 'datetime', False, annotation
    if annotation is date:
        return 'date', False, annotation
    if annotation is UUID:
        return 'uuid', False, annotation
    if dataclasses.is_dataclass(annotation) or annotation is dict or origin is dict:
        return 'object', False, annotation
    if annotation in (list, tuple) or origin in (list, tuple):
        return 'array', False, annotation
    return 'unknown', False, annotation


def _matches_annotation(value: Any, annotation: Any) -> bool:  # noqa: C901
    if annotation is Any:
        return True
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin in (Union, types.UnionType):
        return any(_matches_annotation(value, item) for item in args)
    if value is None:
        return annotation is type(None)
    if annotation is bool:
        return type(value) is bool
    if annotation is int:
        return type(value) is int
    if annotation in (float, Decimal):
        return type(value) in (int, float, Decimal) and type(value) is not bool
    if annotation in (str, datetime, date, UUID):
        return isinstance(value, annotation)
    if dataclasses.is_dataclass(annotation):
        return isinstance(value, annotation)
    if origin in (list, tuple):
        if not isinstance(value, origin):
            return False
        if not args:
            return True
        return all(_matches_annotation(item, args[0]) for item in value)
    if origin is dict:
        if not isinstance(value, dict) or not args:
            return isinstance(value, dict)
        key_type, value_type = args
        return all(
            _matches_annotation(key, key_type) and _matches_annotation(item, value_type)
            for key, item in value.items()
        )
    if annotation in (list, tuple, dict):
        return isinstance(value, annotation)
    return True


def _build_field_title(name: str) -> str:
    return name.strip()


def build_event_code(event: type) -> str:
    """Преобразовать CamelCase-имя класса события в точечный код."""
    name = event.__name__
    parts: list[str] = []
    current = ''
    for char in name:
        if char.isupper() and current:
            parts.append(current.lower())
            current = char
        else:
            current += char
    if current:
        parts.append(current.lower())
    return '.'.join(parts)


def build_event_title(event: type) -> str:
    """Вернуть имя класса как отображаемое название события."""
    return event.__name__
