"""HTTP-операции чтения зарегистрированных определений событий."""

from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from django_event_bus.api.serializers import EventDefinitionSerializer
from django_event_bus.event_bus.events import get_event, get_events


class EventViewSet(
    ViewSet,
):
    """Предоставляет зарегистрированные события."""

    def list(self, request):
        """Возвращает список зарегистрированных событий."""
        serializer = EventDefinitionSerializer(
            get_events(),
            many=True,
        )

        return Response(
            serializer.data,
        )

    def retrieve(
        self,
        request,
        pk=None,
    ):
        """Возвращает описание зарегистрированного события."""
        serializer = EventDefinitionSerializer(
            get_event(
                pk,
            ),
        )

        return Response(
            serializer.data,
        )
