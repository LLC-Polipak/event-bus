"""Django-команда запуска потребителя событий."""

import logging

from django.core.management.base import BaseCommand

from django_event_bus.consumer import start_consumer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Запускает consumer для подписок из Django settings."""

    help = 'Run event bus consumer'

    def handle(self, *args, **options):
        """Запустить блокирующее потребление событий."""
        print('Running event bus consumer')
        start_consumer()
