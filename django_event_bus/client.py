"""Создание event bus из конфигурации текущего Django-проекта."""

from django.conf import settings

from django_event_bus.event_bus.bus import EventBus
from django_event_bus.event_bus.config import EventBusConfig


def get_event_bus() -> EventBus:
    """Создать event bus с параметрами из Django settings."""
    conf = settings.EVENT_BUS
    config = EventBusConfig(
        host=conf.get('HOST', 'event-bus-rabbitmq'),
        port=conf.get('PORT', 5672),
        user=conf.get('USER', 'some_service'),
        password=conf.get('PASSWORD', '123456'),
        vhost=conf.get('VHOST', '/dev'),
        service_name=conf.get('SERVICE_NAME', 'some_service'),
        exchange=conf.get('EXCHANGE', 'events'),
        consumers=conf.get('CONSUMERS', []),
    )
    return EventBus(config=config)
