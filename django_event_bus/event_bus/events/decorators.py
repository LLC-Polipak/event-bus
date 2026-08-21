"""Декораторы для объявления и регистрации dataclass-событий."""

from collections.abc import Callable

from django_event_bus.event_bus.events.introspection import (
    build_event_title,
    get_event_fields,
)
from django_event_bus.event_bus.events.metadata import EventDefinition
from django_event_bus.event_bus.events.registry import register_event


def event(
    *,
    code: str,
    title: str | None = None,
) -> Callable[[type], type]:
    """Создать декоратор, регистрирующий dataclass как событие.

    Args:
        code: Уникальный код события в registry.
        title: Отображаемое название; по умолчанию имя класса.

    Returns:
        Декоратор, добавляющий метаданные классу и в registry.

    Raises:
        TypeError: Декорируемый класс не является dataclass.
        ValueError: Событие с таким кодом уже зарегистрировано.
    """

    def decorator(
        target: type,
    ) -> type:
        definition = EventDefinition(
            code=code,
            title=title
            or build_event_title(
                target,
            ),
            description=target.__doc__,
            target=target,
            fields=get_event_fields(
                target,
            ),
        )

        target.__event_definition__ = definition

        register_event(
            definition,
        )

        return target

    return decorator
