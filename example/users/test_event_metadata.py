"""Проверки расширенного каталога событий."""

# ruff: noqa: S101

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

import pytest

from django_event_bus.event_bus.events import event, event_field, get_event
from django_event_bus.event_bus.events.registry import EVENT_REGISTRY


@pytest.fixture(autouse=True)
def preserve_registry():
    """Не оставлять тестовые события в глобальном registry."""
    snapshot = EVENT_REGISTRY.copy()
    yield
    EVENT_REGISTRY.clear()
    EVENT_REGISTRY.update(snapshot)


def test_event_field_builds_complete_catalog_metadata() -> None:
    """Собрать документацию поля и не использовать example как default."""

    @event(code='claim.created', title='Претензия создана')
    @dataclass(frozen=True)
    class ClaimCreated:
        """Претензия успешно зарегистрирована."""

        claim_id: int = event_field(
            title='ID претензии',
            description='Идентификатор претензии.',
            example=123,
        )
        context_id: int | None = event_field(title='ID контекста')

    definition = get_event('claim.created')
    assert definition.description == 'Претензия успешно зарегистрирована.'
    assert definition.fields[0].title == 'ID претензии'
    assert definition.fields[0].description == 'Идентификатор претензии.'
    assert definition.fields[0].example == 123
    assert definition.fields[0].default is None
    assert definition.fields[0].type == 'integer'
    assert definition.fields[0].required is True
    assert definition.fields[1].nullable is True
    assert definition.fields[1].required is True

    with pytest.raises(TypeError):
        ClaimCreated()


@pytest.mark.parametrize(
    ('annotation', 'expected'),
    [
        (str, 'string'),
        (int, 'integer'),
        (float, 'number'),
        (Decimal, 'number'),
        (bool, 'boolean'),
        (datetime, 'datetime'),
        (date, 'date'),
        (UUID, 'uuid'),
        (dict, 'object'),
        (list[int], 'array'),
        (tuple[int, ...], 'array'),
    ],
)
def test_stable_catalog_types(annotation, expected) -> None:
    """Преобразовать поддерживаемые Python-аннотации в стабильный тип."""
    namespace = {'__annotations__': {'value': annotation}}
    target = dataclass(type(f'Event{expected}', (), namespace))
    event(code=f'type.{expected}.{annotation!r}')(target)
    assert target.__event_definition__.fields[0].type == expected


def test_explicit_description_wins_and_regular_field_metadata_is_allowed() -> None:
    """Уважать description декоратора и произвольную metadata dataclass."""

    @event(code='regular.metadata', description='Явное описание')
    @dataclass
    class RegularMetadata:
        """Docstring."""

        value: str = field(metadata={'application': 'value'})

    definition = RegularMetadata.__event_definition__
    assert definition.description == 'Явное описание'
    assert definition.fields[0].title == 'value'


def test_incompatible_example_fails_during_registration() -> None:
    """Отклонить неверный пример непосредственно в декораторе."""
    with pytest.raises(TypeError, match='несовместим'):

        @event(code='invalid.example')
        @dataclass
        class InvalidExample:
            value: int = event_field(example='not-an-int')


def test_unknown_annotation_is_diagnostic() -> None:
    """Сохранить имя неизвестной аннотации и вернуть unknown."""

    class DomainValue:
        pass

    @event(code='unknown.annotation')
    @dataclass
    class UnknownAnnotation:
        value: DomainValue

    event_field_definition = UnknownAnnotation.__event_definition__.fields[0]
    assert event_field_definition.annotation is DomainValue
    assert event_field_definition.type == 'unknown'
