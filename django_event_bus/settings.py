"""Формирование и валидация конфигурации event bus из Django settings."""

from dataclasses import dataclass

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# Дефолтные настройки
DEFAULT_EVENT_BUS_CONFIG = {
    'HOST': 'localhost',
    'PORT': 5672,
    'USER': 'guest',
    'PASSWORD': 'guest',
    'VHOST': '/',
    'SERVICE_NAME': 'unknown_service',
    'EXCHANGE': 'events',
    'API_PATH': 'api/v1/events/',
    'CONSUMER_ENABLED': True,
    'CONSUMERS': [],
}


@dataclass(frozen=True)
class ConsumerSelection:
    """Validated global state and locally enabled/disabled subscriptions."""

    globally_enabled: bool
    enabled: list[dict]
    disabled: list[dict]


def get_event_bus_config():
    """Вернуть конфигурацию event bus со значениями по умолчанию."""
    user_config = getattr(settings, 'EVENT_BUS', {})

    # Мержим с дефолтами
    config = DEFAULT_EVENT_BUS_CONFIG.copy()
    config.update(user_config)

    return config


def validate_event_bus_settings():
    """Проверить наличие обязательных параметров event bus.

    Raises:
        ImproperlyConfigured: Обязательный парамет не задан.
    """
    config = get_event_bus_config()

    required_fields = ['HOST', 'PORT', 'USER', 'PASSWORD', 'SERVICE_NAME']

    for field in required_fields:
        if not config.get(field):
            raise ImproperlyConfigured(
                f"EVENT_BUS['{field}'] is required in Django settings"
            )


def get_consumer_selection(config) -> ConsumerSelection:
    """Validate consumer-only settings and classify subscriptions."""
    consumer_enabled = config.get('CONSUMER_ENABLED', True)
    if not isinstance(consumer_enabled, bool):
        raise ImproperlyConfigured("EVENT_BUS['CONSUMER_ENABLED'] must be a bool")

    if not consumer_enabled:
        return ConsumerSelection(False, [], [])

    consumers = config.get('CONSUMERS', [])
    if not isinstance(consumers, list):
        raise ImproperlyConfigured("EVENT_BUS['CONSUMERS'] must be a list")

    enabled_consumers = []
    disabled_consumers = []
    for index, consumer in enumerate(consumers):
        if not isinstance(consumer, dict):
            raise ImproperlyConfigured(
                f"EVENT_BUS['CONSUMERS'][{index}] must be a dict"
            )

        enabled = consumer.get('enabled', True)
        if not isinstance(enabled, bool):
            raise ImproperlyConfigured(
                f"EVENT_BUS['CONSUMERS'][{index}]['enabled'] must be a bool"
            )
        if not enabled:
            disabled_consumers.append(consumer)
            continue

        for field in ('source', 'routing_key', 'handler'):
            if not consumer.get(field):
                raise ImproperlyConfigured(
                    f"EVENT_BUS['CONSUMERS'][{index}]['{field}'] is required"
                )
        enabled_consumers.append(consumer)

    return ConsumerSelection(True, enabled_consumers, disabled_consumers)
