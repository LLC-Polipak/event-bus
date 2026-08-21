"""Команда публикации примера события user.created."""

from django.core.management.base import BaseCommand

from django_event_bus.client import get_event_bus
from users.events import UserCreated


class Command(BaseCommand):
    """Публикует событие UserCreated с переданными аргументами."""

    help = 'Публикует пример события user.created'

    def add_arguments(self, parser) -> None:
        """Добавляет аргументы примера события."""
        parser.add_argument('--user-id', type=int, default=123)
        parser.add_argument('--email', default='user@example.com')

    def handle(self, *args, **options) -> None:
        """Создаёт и публикует пример события."""
        event = UserCreated(
            user_id=options['user_id'],
            email=options['email'],
        )

        event_bus = get_event_bus()
        event_bus.publish(event)

        self.stdout.write(
            self.style.SUCCESS(
                f'Событие {event.event_name} опубликовано: {event.payload()}',
            ),
        )
