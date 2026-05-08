from apps.events.event_bus.connection import create_connection
from apps.events.event_bus.consumer import Consumer
from apps.events.event_bus.publisher import Publisher


class EventBus:
    def __init__(self, config):
        self.config = config
        self.connection = create_connection(self.config)
        self.channel = self.connection.channel()

        self.publisher = Publisher(self.channel, self.config)
        self.consumer = Consumer(self.channel, self.config)

    def publish(self, event: str, payload: dict, *, source=None):
        if source is None:
            source = self.config.service_name
        self.publisher.publish(source, event, payload)

    def subscribe(self, source: str, event: str, handler):
        self.consumer.subscribe(source, event, handler)

    def run(self):
        self.consumer.start()
