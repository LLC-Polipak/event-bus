from typing import TYPE_CHECKING

from django_event_bus.event_bus.connection import create_connection
from django_event_bus.event_bus.consumer import Consumer
from django_event_bus.event_bus.publisher import Publisher

if TYPE_CHECKING:
    from django_event_bus.event_bus.message import Event
    from django_event_bus.event_bus.config import EventBusConfig

class EventBus:
    def __init__(self, config: "EventBusConfig"):
        self.config = config
        self.connection = create_connection(self.config)
        self.channel = self.connection.channel()

        self.publisher = Publisher(self.channel, self.config)
        self.consumer = Consumer(self.channel, self.config)

    def publish(self, event: "Event",  *, source=None):
        if source is None:
            source = self.config.service_name
        self.publisher.publish(source, event)

    def subscribe(self, source: str, event: str, handler):
        self.consumer.subscribe(source, event, handler)

    def run(self):
        self.consumer.start()
