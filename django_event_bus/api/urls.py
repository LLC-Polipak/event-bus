from rest_framework.routers import DefaultRouter

from django_event_bus.api.viewsets import EventViewSet

router = DefaultRouter()

router.register(
    'events',
    EventViewSet,
    basename='event-bus-event',
)

urlpatterns = router.urls
