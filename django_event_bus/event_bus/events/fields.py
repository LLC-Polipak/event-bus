"""Средства объявления метаданных полей событий."""

from collections.abc import Callable, Mapping
from dataclasses import MISSING, Field, field
from typing import Any

EVENT_FIELD_METADATA_KEY = 'django_event_bus'


def event_field(
    *,
    title: str | None = None,
    description: str = '',
    example: object = MISSING,
    default: object = MISSING,
    default_factory: Callable[[], Any] = MISSING,
) -> Field[Any]:
    """Создать dataclass-поле с каталоговыми метаданными события."""
    metadata: dict[str, Any] = {'title': title, 'description': description}
    if example is not MISSING:
        metadata['example'] = example
    return field(
        default=default,
        default_factory=default_factory,
        metadata={EVENT_FIELD_METADATA_KEY: metadata},
    )


def get_event_field_metadata(metadata: Mapping[str, Any]) -> Mapping[str, Any]:
    """Извлечь metadata event bus из обычного dataclass-поля."""
    value = metadata.get(EVENT_FIELD_METADATA_KEY, {})
    if not isinstance(value, Mapping):
        raise TypeError(f'metadata["{EVENT_FIELD_METADATA_KEY}"] должна быть mapping.')
    unknown = set(value) - {'title', 'description', 'example'}
    if unknown:
        names = ', '.join(sorted(map(str, unknown)))
        raise ValueError(f'Неизвестные metadata поля события: {names}.')
    return value
