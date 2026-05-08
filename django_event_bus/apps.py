from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = 'django_event_bus'
    verbose_name = 'Django Event Bus'

    def ready(self):
        """Загружаем настройки при старте"""
        from .settings import validate_event_bus_settings

        validate_event_bus_settings()
