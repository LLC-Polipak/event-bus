from django.urls import include, path

urlpatterns = [
    path(
        'api/',
        include(
            'event_bus.api.urls',
        ),
    ),
]
