"""Django-команда запуска потребителя событий."""

from django.core.management.base import BaseCommand

from django_event_bus.consumer import start_consumer


class Command(BaseCommand):
    """Запускает consumer для подписок из Django settings."""

    help = 'Run event bus consumer'

    def handle(self, *args, **options):
        """Запустить блокирующее потребление событий."""
        start_consumer()
