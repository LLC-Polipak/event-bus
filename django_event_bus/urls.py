"""Корневые URL-маршруты HTTP API пакета Django Event Bus."""

from django.urls import include, path

urlpatterns = [
    path(
        'api/v1/',
        include(
            'django_event_bus.api.urls',
        ),
    ),
]
