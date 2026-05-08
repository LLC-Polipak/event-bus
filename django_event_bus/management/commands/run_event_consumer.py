import logging

from django.core.management.base import BaseCommand

from django_event_bus.consumer import start_consumer

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run event bus consumer'

    def handle(self, *args, **options):
        print('Running event bus consumer')
        start_consumer()
