from rest_framework import serializers

from django_event_bus.event_bus.events.metadata import EventDefinition, EventField


class EventFieldSerializer(
    serializers.Serializer,
):
    """Сериализует поле события."""

    name = serializers.CharField()

    annotation = serializers.SerializerMethodField()

    required = serializers.BooleanField()

    default = serializers.JSONField(
        allow_null=True,
    )

    def get_annotation(
        self,
        obj: EventField,
    ) -> str | None:
        """Возвращает имя типа поля."""

        if obj.annotation is None:
            return None

        return getattr(
            obj.annotation,
            '__name__',
            str(obj.annotation),
        )


class EventDefinitionSerializer(
    serializers.Serializer,
):
    """Сериализует зарегистрированное событие."""

    code = serializers.CharField()

    title = serializers.CharField()

    description = serializers.CharField(
        allow_null=True,
        required=False,
    )

    target = serializers.SerializerMethodField()

    fields = EventFieldSerializer(
        many=True,
    )

    def get_target(
        self,
        obj: EventDefinition,
    ) -> str:
        """Возвращает полное имя класса события."""

        return f'{obj.target.__module__}.{obj.target.__qualname__}'
