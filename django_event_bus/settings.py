"""Формирование и валидация конфигурации event bus из Django settings."""

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
    'CONSUMERS': [],
}


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
