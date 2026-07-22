from typing import TYPE_CHECKING

from .message import build_message, serialize

if TYPE_CHECKING:
    from .message import Event
    from .config import EventBusConfig


class Publisher:
    def __init__(self, channel, config: "EventBusConfig"):
        self.channel = channel
        self.config = config

        # declare exchange
        self.channel.exchange_declare(
            exchange=self.config.exchange,
            exchange_type=self.config.exchange_type,
            durable=True,
        )

    def publish(self, source: str, event: "Event"):
        message = build_message(source, event)

        self.channel.basic_publish(
            exchange=self.config.exchange,
            routing_key=message.event,
            body=serialize(message.to_dict()),
        )
