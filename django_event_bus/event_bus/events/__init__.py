"""Объявление событий и доступ к их зарегистрированным метаданным."""

from .decorators import event
from .fields import event_field
from .registry import get_event, get_events

__all__ = [
    'event',
    'event_field',
    'get_event',
    'get_events',
]
