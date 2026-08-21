"""Хранение и поиск метаданных событий, зарегистрированных декораторами."""

from django_event_bus.event_bus.events.metadata import EventDefinition

EVENT_REGISTRY: dict[str, EventDefinition] = {}


def register_event(
    definition: EventDefinition,
) -> None:
    """Добавить определение события в registry.

    Raises:
        ValueError: Событие с таким кодом уже зарегистрировано.
    """
    if definition.code in EVENT_REGISTRY:
        raise ValueError(
            f'Событие "{definition.code}" уже зарегистрировано.',
        )

    EVENT_REGISTRY[definition.code] = definition


def get_event(
    code: str,
) -> EventDefinition:
    """Вернуть определение события по уникальному коду.

    Raises:
        KeyError: Событие с указанным кодом не зарегистрировано.
    """
    return EVENT_REGISTRY[code]


def get_events() -> list[EventDefinition]:
    """Вернуть снимок всех определений из registry."""
    return list(
        EVENT_REGISTRY.values(),
    )


def has_event(
    code: str,
) -> bool:
    """Проверить наличие определения события с указанным кодом."""
    return code in EVENT_REGISTRY
