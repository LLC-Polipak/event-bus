"""Корневые URL-маршруты HTTP API пакета Django Event Bus."""

from django.urls import include, path

from django_event_bus.settings import get_event_bus_config


def get_api_path() -> str:
    """Вернуть нормализованный полный путь HTTP API событий из конфигурации."""
    configured_path = get_event_bus_config()['API_PATH'].strip('/')
    return f'{configured_path}/' if configured_path else ''


def build_urlpatterns():
    """Подключить маршруты списка и детализации по настроенному полному пути."""
    return [
        path(
            get_api_path(),
            include(
                'django_event_bus.api.urls',
            ),
        ),
    ]


urlpatterns = build_urlpatterns()
