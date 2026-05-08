import time
from typing import TYPE_CHECKING

import pika

if TYPE_CHECKING:
    from django_event_bus.event_bus.config import EventBusConfig


def create_connection(config: 'EventBusConfig', retries=5):
    credentials = pika.PlainCredentials(config.user, config.password)

    for _attempt in range(retries):
        try:
            return pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=config.host,
                    port=config.port,
                    virtual_host=config.vhost,
                    credentials=credentials,
                    heartbeat=60,
                    blocked_connection_timeout=300,
                )
            )
        except Exception:
            # print(f"Connection failed, retry {attempt + 1}/{retries}")
            time.sleep(2)

    raise Exception('Could not connect to RabbitMQ')
