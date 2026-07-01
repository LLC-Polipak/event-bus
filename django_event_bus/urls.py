from django.urls import include, path

urlpatterns = [
    path(
        'api/',
        include(
            'django_event_bus.api.urls',
        ),
    ),
]
