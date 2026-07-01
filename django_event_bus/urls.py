from django.urls import include, path

urlpatterns = [
    path(
        'api/',
        include(
            'dango_event_bus.api.urls',
        ),
    ),
]
