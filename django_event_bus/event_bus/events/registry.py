from django_event_bus.event_bus.events.metadata import EventDefinition

EVENT_REGISTRY: dict[str, EventDefinition] = {}


def register_event(
    definition: EventDefinition,
) -> None:
    """Регистрирует событие."""

    if definition.code in EVENT_REGISTRY:
        raise ValueError(
            f'Событие "{definition.code}" уже зарегистрировано.',
        )

    EVENT_REGISTRY[definition.code] = definition


def get_event(
    code: str,
) -> EventDefinition:
    """Возвращает зарегистрированное событие."""

    return EVENT_REGISTRY[code]


def get_events() -> list[EventDefinition]:
    """Возвращает все зарегистрированные события."""

    return list(
        EVENT_REGISTRY.values(),
    )


def has_event(
    code: str,
) -> bool:
    """Проверяет, зарегистрировано ли событие."""

    return code in EVENT_REGISTRY
