from django.core.management.base import BaseCommand

from django_event_bus import start_consumer


class Command(BaseCommand):
    help = 'Run event bus consumer'

    def handle(self, *args, **options):
        start_consumer()
