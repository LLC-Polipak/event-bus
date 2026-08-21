"""Координация RabbitMQ-соединения, публикатора и consumer event bus."""

from typing import TYPE_CHECKING

from django_event_bus.event_bus.connection import create_connection
from django_event_bus.event_bus.consumer import Consumer
from django_event_bus.event_bus.publisher import Publisher

if TYPE_CHECKING:
    from pika import BlockingConnection

    from django_event_bus.event_bus.config import EventBusConfig
    from django_event_bus.event_bus.message import Event


class ConnectionManager:
    """Управляет блокирующим RabbitMQ-соединением и каналами."""

    _connection: 'BlockingConnection | None'

    def __init__(self, *, config: 'EventBusConfig'):
        self.config = config
        self._connection = None

        # NB: Первое подключение сразу после инициализации(ПРОВЕРКА СОЕДИНЕНИЯ)
        self._connection = self.connection

    @property
    def connection(self) -> 'BlockingConnection':
        """Вернуть активное RabbitMQ-соединение, пересоздав закрытое."""
        if self._connection is None or self._connection.is_closed:
            self._connection = create_connection(self.config)

        return self._connection

    def get_channel(self):
        """Создать RabbitMQ-канал и объявить в нём exchange event bus."""
        channel = self.connection.channel()

        channel.exchange_declare(
            exchange=self.config.exchange,
            exchange_type=self.config.exchange_type,
            durable=True,
        )

        return channel


class EventBus:
    """Единая точка публикации и потребления событий через RabbitMQ."""

    def __init__(self, *, config: 'EventBusConfig'):
        self.config = config
        self.connection_manager = ConnectionManager(config=config)

        self.publisher = Publisher(
            connection_manager=self.connection_manager, exchange=config.exchange
        )
        self.consumer = Consumer(
            connection_manager=self.connection_manager, exchange=config.exchange
        )

    def publish(self, event: 'Event', *, source=None):
        """Опубликовать событие от имени указанного или текущего сервиса."""
        if source is None:
            source = self.config.service_name
        self.publisher.publish(source, event)

    def subscribe(self, source: str, event: str, handler):
        """Зарегистрировать обработчик события от заданного источника."""
        self.consumer.subscribe(source, event, handler)

    def run(self):
        """Запустить блокирующее потребление зарегистрированных событий."""
        self.consumer.start()
