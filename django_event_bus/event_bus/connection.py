import time
from typing import TYPE_CHECKING

import pika

if TYPE_CHECKING:
    from django_event_bus.event_bus.config import EventBusConfig


def create_connection(config: 'EventBusConfig', retries=10, delay=5):
    """Создает соединение с RabbitMQ"""
    credentials = pika.PlainCredentials(
        config.user,
        config.password,
    )

    last_exception = None

    for attempt in range(1, retries + 1):
        try:
            print(
                f'[RabbitMQ] Connecting '
                f'{attempt}/{retries} '
                f'to {config.host}:{config.port}'
            )

            return pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=config.host,
                    port=config.port,
                    virtual_host=config.vhost,
                    credentials=credentials,
                    heartbeat=60,
                    blocked_connection_timeout=30,
                    socket_timeout=5,
                    connection_attempts=1,
                    retry_delay=0,
                )
            )

        except Exception as e:
            last_exception = e

            print(f'[RabbitMQ] Connection failed: {type(e).__name__}: {e}')

            time.sleep(delay)

    raise RuntimeError(
        f'Could not connect to RabbitMQ '
        f'after {retries} attempts '
        f'({config.host}:{config.port}, '
        f'vhost={config.vhost})'
    ) from last_exception
