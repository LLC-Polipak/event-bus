from typing import TYPE_CHECKING

from .message import build_message, serialize

if TYPE_CHECKING:
    from .bus import ConnectionManager
    from .message import Event


class Publisher:
    def __init__(self, connection_manager: 'ConnectionManager', exchange: str):
        self.exchange = exchange
        self.connection_manager = connection_manager
        self._channel = None

    @property
    def channel(self):
        if self._channel is None or self._channel.is_closed:
            self._channel = self.connection_manager.get_channel()

        return self._channel

    def publish(self, source: str, event: 'Event'):
        message = build_message(source, event)

        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=message.event,
            body=serialize(message.to_dict()),
        )
