"""Инициализация Django Event Bus в составе Django-проекта."""

from django.apps import AppConfig


class EventsConfig(AppConfig):
    """Конфигурация Django-приложения событийной шины."""

    name = 'django_event_bus'
    verbose_name = 'Django Event Bus'

    def ready(self):
        """Проверить конфигурацию event bus при запуске Django."""
        from .settings import validate_event_bus_settings

        validate_event_bus_settings()
