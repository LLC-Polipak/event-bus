from typing import TYPE_CHECKING

from pika.exceptions import AMQPConnectionError

from .message import deserialize

if TYPE_CHECKING:
    from .bus import ConnectionManager


class Consumer:
    def __init__(
        self,
        connection_manager: 'ConnectionManager',
        exchange: str,
    ):
        self.connection_manager = connection_manager
        self.exchange = exchange
        self.subscriptions = []
        self._channel = None

    @property
    def channel(self):
        if self._channel is None or self._channel.is_closed:
            self._channel = self.connection_manager.get_channel()

        return self._channel

    def subscribe(
        self,
        source: str,
        event: str,
        handler,
    ):
        self.subscriptions.append(
            (
                source,
                event,
                handler,
            )
        )

    @staticmethod
    def _make_callback(handler):
        def callback(ch, method, _properties, body):
            try:
                message = deserialize(body)
            except Exception as e:
                print(f'Deserialize error: {e}')
                print(f'RAW: {body}')

                # 💥 съедаем битое сообщение
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            try:
                handler(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)

            except Exception as e:
                print(f'Handler error: {e}')
                # сейчас у тебя бесконечный retry
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                # если поставить True → цикл

        return callback

    def _prepare_subscriptions(self):
        for source, event, handler in self.subscriptions:
            routing_key = f'{source}.{event}'
            queue_name = (
                f'{self.connection_manager.config.service_name}.'
                f'{handler.__module__}.{handler.__qualname__}'
            )

            self.channel.queue_declare(
                queue=queue_name,
                durable=True,
            )

            self.channel.queue_bind(
                exchange=self.exchange,
                queue=queue_name,
                routing_key=routing_key,
            )

            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=self._make_callback(handler),
            )

    def start(self):
        if not self.subscriptions:
            raise RuntimeError(
                "No event consumers are configured or all consumers are disabled."
            ) from None
        
        while True:
            self._channel = None
            self._prepare_subscriptions()

            try:
                self.channel.start_consuming()
            except AMQPConnectionError:
                print('Соединение закрылось')
                continue
